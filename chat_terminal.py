from __future__ import annotations

import shutil
import sys
import json
import os
import time
import webbrowser
from datetime import datetime
from pathlib import Path
import subprocess

from danzariel_quero.services.chat import record_message, save_note_command, terminal_reply
from danzariel_quero.core.config import settings
from danzariel_quero.services.files import ensure_workspace
from quero.brain.classifier import RuleBasedClassifier

try:
    sys.stdout.reconfigure(encoding="utf-8")
except AttributeError:
    pass


class C:
    RESET = "\033[0m"
    DIM = "\033[2m"
    CYAN = "\033[96m"
    GOLD = "\033[93m"
    GREEN = "\033[92m"
    RED = "\033[91m"
    WHITE = "\033[97m"
    BLACK_BG = "\033[40m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"


VISUAL_OBJECTS = {
    "matrix": "🧬 pulso visual",
    "scan": "🔍 escaneo de areas",
    "clock": "🕒 hora local",
    "clipboard": "📋 preview clipboard",
    "images": "🖼️ indice de imagenes",
}

VISUAL_ICONS = {
    "matrix": "🧬",
    "scan": "🔍",
    "clock": "🕒",
    "clipboard": "📋",
    "images": "🖼️",
}

AREA_ICONS = {
    "inbox": "📥",
    "memoria": "🧠",
    "documentos": "📄",
    "trading": "📈",
    "knowledge": "🔑",
    "bitacora": "📓",
    "backups": "💾",
}

HEART_DOCS = [
    ("📖 ACTA", "origen y fe", "inmutable"),
    ("📓 BITACORA", "evidencia historica", "registro"),
    ("🧾 GLOSARIO", "lenguaje del sistema", "control semantico"),
    ("⚗️ INVESTIGACION", "validacion alquimica", "referencia"),
    ("🎮 LEGACY", "rama aplicada", "simulacion"),
    ("📘 MANUAL", "motor tecnico", "operativo"),
    ("🧠 METATRON", "conciencia del operador", "memoria psi"),
    ("🌌 PARADIGMA", "marco universal", "lectura"),
    ("🛠️ PROTOCOLO", "QUERO.OS", "edicion cero perdida"),
]

MODES = [
    ("🔍 LECTURA", "lee, resume y conecta documentos"),
    ("🛡️ CUSTODIA", "detecta ruido, urgencia y contradiccion"),
    ("📓 BITACORA", "registra hechos, decisiones y lecciones"),
    ("✅ VERIFICAR", "compara antes/despues y detecta perdidas"),
    ("📤 ENVIAR", "prepara bloques completos sin placeholders"),
    ("💾 BACKUP", "protege antes de cambiar"),
    ("⏮️ ROLLBACK", "restaura solo con confirmacion explicita"),
]

CUSTODY_RULES = {
    "urgencia": ["ya", "ahora", "rapido", "urgente", "de una", "no puedo esperar"],
    "miedo": ["miedo", "perder", "perdi", "panico", "ansiedad", "me hundo"],
    "euforia": ["seguro", "100%", "facil", "me forro", "garantizado", "all in"],
    "venganza": ["recuperar", "venganza", "me desquito", "doblar", "meter mas"],
    "disciplina": ["esperar", "confirmar", "bitacora", "validar", "no operar", "backup"],
}

SOS_COMMANDS = {
    "1": "/server",
    "2": "/url",
    "3": "/context",
    "4": "/diff",
    "5": "backup",
    "6": "/exit",
}

SIMULATOR_COMMANDS = {
    "1": "sim custody",
    "2": "sim classify",
    "3": "sim nodo",
    "4": "sim backup",
}

ACTIVE_MENU: str | None = None


def state_path() -> Path:
    return settings.data_dir / "memoria" / "terminal_state.json"


def default_state() -> dict[str, bool]:
    return {
        "matrix": True,
        "scan": True,
        "clock": True,
        "clipboard": True,
        "images": True,
    }


def load_visual_state() -> dict[str, bool]:
    ensure_workspace()
    path = state_path()
    if not path.exists():
        return default_state()
    try:
        raw = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except json.JSONDecodeError:
        return default_state()
    state = default_state()
    for key in state:
        if key in raw:
            state[key] = bool(raw[key])
    return state


def save_visual_state(state: dict[str, bool]) -> None:
    path = state_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def term_width(default: int = 78) -> int:
    return min(max(shutil.get_terminal_size((default, 24)).columns, 58), 96)


def fit(text: str, width: int) -> str:
    if len(text) <= width:
        return text
    return text[: max(width - 3, 0)] + "..."


def framed_line(text: str = "", color: str = C.GREEN, width: int | None = None) -> None:
    inner = (width or term_width()) - 4
    print(f"{color}|{C.RESET} {fit(text, inner):<{inner}} {color}|{C.RESET}")


def frame_rule(color: str = C.GREEN, width: int | None = None) -> None:
    print(f"{color}+{'-' * ((width or term_width()) - 2)}+{C.RESET}")


def status_chip(name: str, active: bool) -> str:
    icon = VISUAL_ICONS.get(name, "•")
    return f"{icon}{name}:{'ON' if active else 'OFF'}"


def area_count(area: str) -> int:
    base = settings.data_dir / area
    if not base.exists():
        return 0
    return len([path for path in base.rglob("*") if path.is_file()])


def clipboard_text() -> str:
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", "Get-Clipboard -Raw"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=3,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    return (result.stdout or "").strip()


def image_files() -> list[Path]:
    ensure_workspace()
    image_suffixes = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"}
    files: list[Path] = []
    for area in settings.areas:
        base = settings.data_dir / area
        if base.exists():
            files.extend(path for path in base.rglob("*") if path.is_file() and path.suffix.lower() in image_suffixes)
    return sorted(files, key=lambda path: str(path.relative_to(settings.data_dir)).lower())


def print_control_center() -> None:
    state = load_visual_state()
    width = term_width()
    now = datetime.now().strftime("%Y-%m-%d %H:%M") if state["clock"] else "clock OFF"
    frame_rule(C.GREEN, width)
    framed_line("DANZARIEL-QUERO // CENTRO DE CONTROL INICIAL", C.GREEN, width)
    framed_line(f"Modo: Speculum con custodia   Hora: {now}", C.GREEN, width)
    frame_rule(C.GREEN, width)

    if state["matrix"]:
        framed_line("00 01 10 11 23 42 :: memoria local / evidencia / bitacora / custodia", C.CYAN, width)

    chips = "  ".join(status_chip(key, state[key]) for key in VISUAL_OBJECTS)
    framed_line(f"Objetos: {chips}", C.GREEN, width)

    if state["scan"]:
        main_areas = ["inbox", "memoria", "documentos", "trading", "knowledge", "bitacora", "backups"]
        framed_line(
            "Areas: " + "  ".join(f"{AREA_ICONS.get(area, '•')}{area}:{area_count(area)}" for area in main_areas),
            C.GOLD,
            width,
        )

    if state["clipboard"]:
        clip = clipboard_text()
        preview = fit(clip.replace("\r", " ").replace("\n", " "), 58) if clip else "[clipboard vacio/no disponible]"
        framed_line(f"Clipboard: {preview}", C.MAGENTA, width)

    if state["images"]:
        framed_line(f"Imagenes indexadas: {len(image_files())}", C.BLUE, width)

    frame_rule(C.GREEN, width)
    print(f"{C.DIM}🏠 /home  ❤️ /heart  🧭 /modes  📊 /status  🧪 /simulators  🧬 /lab  🎮 /PS3  ✨ /pulse  🪞 /sigil{C.RESET}")
    print(f"{C.DIM}📋 /clip  🔍 scan  🧼 clear{C.RESET}")
    print(f"{C.DIM}🖥️ /ui  🎚️ /toggle objeto  📥 paste add  🖼️ images  📤 image send  💾 backup  ⏮️ rollback multidimensional{C.RESET}")
    print()


def print_header(wake: bool = False) -> None:
    print()
    title = "Danzariel" if wake else "[+] DANZARIEL-QUERO TERMINAL"
    subtitle = "AI Administration System" if wake else "modo hacker local // memoria privada"
    width = term_width()
    frame_rule(C.GREEN, width)
    framed_line(title, C.GREEN, width)
    framed_line(subtitle, C.GREEN, width)
    frame_rule(C.GREEN, width)
    if wake:
        print(f"{C.GREEN}AI administration system online{C.RESET}")
        print_control_center()
    else:
        print(f"{C.DIM}Comandos rapidos: /ui  /lab  /PS3  /server  /url  /start-server  /files  /note{C.RESET}")
    print(f"{C.DIM}Escribe /help para comandos. Escribe /exit para salir.{C.RESET}")
    print()


def print_reply(reply: str) -> None:
    lines = reply.splitlines() or [""]
    print(f"{C.GREEN}DQ://{C.RESET} {lines[0]}")
    for line in lines[1:]:
        print(f"{C.DIM}    >{C.RESET} {line}")


def print_panel(title: str, rows: list[str], color: str = C.GREEN) -> None:
    width = term_width()
    frame_rule(color, width)
    framed_line(title, color, width)
    frame_rule(color, width)
    for row in rows:
        framed_line(row, color, width)
    frame_rule(color, width)
    print()


def git_line() -> str:
    try:
        branch = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=settings.project_root,
            capture_output=True,
            text=True,
            timeout=3,
            check=False,
        ).stdout.strip() or "sin-rama"
        status = subprocess.run(
            ["git", "status", "--short"],
            cwd=settings.project_root,
            capture_output=True,
            text=True,
            timeout=3,
            check=False,
        ).stdout.splitlines()
    except (OSError, subprocess.SubprocessError):
        return "Git: no disponible"
    return f"Git: {branch}  cambios:{len(status)}"


def translate_menu_choice(message: str) -> str:
    global ACTIVE_MENU
    choice = message.strip()
    if ACTIVE_MENU == "sos" and choice in SOS_COMMANDS:
        ACTIVE_MENU = None
        return SOS_COMMANDS[choice]
    if ACTIVE_MENU == "simulators" and choice in SIMULATOR_COMMANDS:
        ACTIVE_MENU = None
        return SIMULATOR_COMMANDS[choice]
    return message


def data_files() -> list[Path]:
    ensure_workspace()
    files: list[Path] = []
    for area in settings.areas:
        base = settings.data_dir / area
        if not base.exists():
            continue
        files.extend(path for path in base.rglob("*") if path.is_file())
    return sorted(files, key=lambda path: str(path.relative_to(settings.data_dir)).lower())


def choose_area(title: str = "[+] Elige un area.") -> str | None:
    areas = ["memoria", "inbox", "trading", "documentos"]
    print_reply(title)
    for index, area in enumerate(areas, start=1):
        print(f"{C.DIM}{index}.{C.RESET} {area}")
    choice = input(f"{C.GREEN}area>{C.RESET} ").strip().lower()
    if choice in areas:
        return choice
    try:
        selected = int(choice)
    except ValueError:
        print_reply("[!] Area invalida.")
        return None
    if selected < 1 or selected > len(areas):
        print_reply("[!] Area fuera de rango.")
        return None
    return areas[selected - 1]


def choose_file(title: str, files: list[Path] | None = None) -> Path | None:
    candidates = files if files is not None else data_files()
    print_reply(title)
    if not candidates:
        print_reply("[!] No hay bloques disponibles.")
        return None

    for index, path in enumerate(candidates[:40], start=1):
        print(f"{C.DIM}{index:02}.{C.RESET} {path.relative_to(settings.data_dir)}")

    choice = input(f"{C.GREEN}bloque>{C.RESET} ").strip()
    try:
        selected = int(choice)
    except ValueError:
        print_reply("[!] Opcion invalida.")
        return None

    if selected < 1 or selected > min(len(candidates), 40):
        print_reply("[!] Opcion fuera de rango.")
        return None
    return candidates[selected - 1]


def choose_file_in_area(area: str, title: str) -> Path | None:
    base = settings.data_dir / area
    files = sorted((path for path in base.rglob("*") if path.is_file()), key=lambda path: str(path).lower())
    return choose_file(title, files)


def markdown_for_file(path: Path) -> str:
    relative = path.relative_to(settings.data_dir).as_posix()
    suffix = path.suffix.lower()
    if suffix in {".md", ".txt", ".json", ".csv", ".log"}:
        content = path.read_text(encoding="utf-8", errors="replace")
    else:
        content = f"[Archivo binario: {relative}]\nTamano: {path.stat().st_size} bytes"
    return f"# {path.name}\n\nRuta: `{relative}`\n\n```text\n{content}\n```\n"


def copy_to_clipboard(text: str) -> None:
    subprocess.run(
        ["powershell", "-NoProfile", "-Command", "Set-Clipboard -Value $input"],
        input=text,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=True,
    )


def action_clip() -> None:
    clip = clipboard_text()
    if not clip:
        print_reply("[!] Clipboard vacio o no disponible.")
        return
    print_reply(f"[+] Clipboard listo: {len(clip)} caracteres.")
    for line in clip.splitlines()[:8]:
        print(f"{C.DIM}    |{C.RESET} {fit(line, term_width() - 10)}")
    if len(clip.splitlines()) > 8:
        print(f"{C.DIM}    ... preview recortado{C.RESET}")


def action_paste_add() -> None:
    clip = clipboard_text()
    if not clip:
        print_reply("[!] Clipboard vacio. Copia primero el bloque que quieres guardar.")
        return
    area = choose_area("[+] PASTE ADD: donde guardar el contenido del clipboard?")
    if not area:
        return
    title = input(f"{C.GREEN}titulo>{C.RESET} ").strip()
    if not title:
        print_reply("[!] Cancelado: falta titulo.")
        return
    safe_title = "".join(ch if ch.isalnum() or ch in "._- " else "_" for ch in title).strip() or "clipboard"
    filename = safe_title if safe_title.endswith(".md") else f"{safe_title}.md"
    target = settings.data_dir / area / filename
    if target.exists():
        print_reply(f"[!] Ya existe: {area}/{filename}")
        confirm = input(f"{C.RED}escribe SOBREESCRIBIR>{C.RESET} ").strip()
        if confirm != "SOBREESCRIBIR":
            print_reply("[!] Guardado cancelado.")
            return
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(clip.rstrip() + "\n", encoding="utf-8")
    print_reply(f"[+] Clipboard guardado en: {area}/{filename}")


def action_scan() -> None:
    ensure_workspace()
    lines = ["[+] Escaneo de areas:"]
    for area in settings.areas:
        lines.append(f"  > {area}: {area_count(area)} archivo(s)")
    print_reply("\n".join(lines))


def action_home() -> None:
    print_control_center()
    rows = [
        "❤️ [H] /heart       ver Llave Sagrada / corazon",
        "🧭 [M] /modes       modos operativos del asistente",
        "📊 [S] /status      servidor, memoria, git y entorno",
        "🧪 [X] /simulators  practicas sin tocar datos reales",
        "🧬 [L] /lab         abrir DANZARIEL LAB visual",
        "🎮 [3] /PS3         abrir escritorio futurista XMB",
        "✨ [P] /pulse       pulso animado del sistema",
        "🪞 [G] /sigil       imagen fantastica de terminal",
        "📋 [C] /clip        inspeccionar clipboard",
        "💾 [B] backup       proteger un bloque",
    ]
    print_panel("DANZARIEL-QUERO // ACCESOS PRINCIPALES", rows, C.CYAN)


def action_heart() -> None:
    rows = [f"[{code}] {role} :: {state}" for code, role, state in HEART_DOCS]
    rows.extend(
        [
            "",
            "⚖️ Regla: el simbolo orienta, la evidencia decide.",
            "🔒 Acta: inmutable. 📘 Manual: operativo. 📓 Bitacora: verdad registrada.",
        ]
    )
    print_panel("LLAVE SAGRADA // CORAZON DEL SISTEMA", rows, C.GOLD)


def action_modes() -> None:
    rows = [f"[{name}] {description}" for name, description in MODES]
    rows.extend(
        [
            "",
            "🪞 Speculum no decide por el Operador.",
            "🛡️ Speculum refleja, ordena, registra, verifica y custodia.",
        ]
    )
    print_panel("SPECULUM // MODOS OPERATIVOS", rows, C.MAGENTA)


def action_status() -> None:
    server = terminal_reply("/server").splitlines()[0].replace("[+] ", "").replace("[!] ", "")
    url = terminal_reply("/url").replace("\n", "  ")
    venv = ".venv OK" if (settings.project_root / ".venv" / "Scripts" / "python.exe").exists() else ".venv faltante"
    rows = [
        f"🖥️ Servidor: {server}",
        f"📡 URL: {url}",
        f"🐍 Entorno: {venv}",
        f"🌿 {git_line()}",
        f"🔐 Datos privados: {settings.data_dir}",
        f"🗂️ Areas activas: {len(settings.areas)}",
        f"🖼️ Imagenes indexadas: {len(image_files())}",
        f"📋 Clipboard: {'con contenido' if clipboard_text() else 'vacio/no disponible'}",
    ]
    print_panel("DANZARIEL-QUERO // ESTADO", rows, C.GREEN)


def action_lab() -> None:
    port = 8000
    url_text = terminal_reply("/url")
    for line in url_text.splitlines():
        if line.startswith("PC: http://127.0.0.1:"):
            try:
                port = int(line.rsplit(":", 1)[1])
            except ValueError:
                port = 8000

    if "Servidor apagado" in terminal_reply("/server"):
        print_reply("🧬 DANZARIEL LAB: servidor apagado, iniciando...")
        print_reply(terminal_reply("/start-server"))
        time.sleep(1.2)

    lab_url = f"http://127.0.0.1:{port}/lab"
    webbrowser.open(lab_url)
    rows = [
        f"🧬 URL: {lab_url}",
        "🛡️ Terminal queda limpia; simuladores viven en la app.",
        "🎮 Modulos: Custodia, Nodo Quero, Calculadoras, Juegos.",
    ]
    print_panel("DANZARIEL LAB // ABIERTO", rows, C.CYAN)


def action_ps3() -> None:
    port = 8000
    url_text = terminal_reply("/url")
    for line in url_text.splitlines():
        if line.startswith("PC: http://127.0.0.1:"):
            try:
                port = int(line.rsplit(":", 1)[1])
            except ValueError:
                port = 8000

    if "Servidor apagado" in terminal_reply("/server"):
        print_reply("🎮 PS3 XMB: servidor apagado, iniciando...")
        print_reply(terminal_reply("/start-server"))
        time.sleep(1.2)

    ps3_url = f"http://127.0.0.1:{port}/PS3/"
    webbrowser.open(ps3_url)
    rows = [
        f"🎮 URL: {ps3_url}",
        "🕹️ Escritorio modular futurista inspirado en XMB.",
        "⬅️➡️ Categorias horizontales  ↑↓ Submenu vertical  Enter abre modulo.",
    ]
    print_panel("PS3 XMB OS // ABIERTO", rows, C.MAGENTA)


def action_pulse() -> None:
    width = term_width()
    frames = [
        "🧬 memoria local",
        "🧬 memoria local  →  📓 bitacora",
        "🧬 memoria local  →  📓 bitacora  →  🛡️ custodia",
        "🧬 memoria local  →  📓 bitacora  →  🛡️ custodia  →  ✅ verificacion",
        "🧬 memoria local  →  📓 bitacora  →  🛡️ custodia  →  ✅ verificacion  →  🔑 llave",
        "🧬 memoria local  →  📓 bitacora  →  🛡️ custodia  →  ✅ verificacion  →  🔑 llave  →  ✨ pulso",
    ]
    print()
    for _ in range(2):
        for frame in frames:
            sys.stdout.write("\r" + C.CYAN + fit(frame, width - 2).ljust(width - 2) + C.RESET)
            sys.stdout.flush()
            time.sleep(0.12)
    sys.stdout.write("\r" + " " * (width - 2) + "\r")
    sys.stdout.flush()
    rows = [
        "✨ Pulso completo.",
        "🧬 Memoria: activa",
        "📓 Bitacora: lista",
        "🛡️ Custodia: vigilante",
        "✅ Verificacion: disponible",
        "🔑 Llave: bajo control del Operador",
    ]
    print_panel("DANZARIEL-QUERO // PULSO VISUAL", rows, C.CYAN)


def action_sigil() -> None:
    rows = [
        "                 ✦",
        "              ◇  │  ◇",
        "        ╔════════════════════╗",
        "        ║    DANZARIEL       ║",
        "        ║   SPECULUM  OS     ║",
        "        ╚════════════════════╝",
        "              ◇  │  ◇",
        "                 ✦",
        "",
        "        🧬────📓────🛡️────✅────🔑",
        "        memoria  evidencia  custodia",
        "",
        "🪞 Imagen de terminal: no es foto real, es sigilo visual.",
        "🖼️ Para fotos reales conviene usar la web local o abrir imagen desde archivo.",
    ]
    print_panel("DANZARIEL-QUERO // SIGILO TERMINAL", rows, C.MAGENTA)


def action_simulators() -> None:
    global ACTIVE_MENU
    ACTIVE_MENU = "simulators"
    rows = [
        "1. 🛡️ sim custody   detectar ruido en una frase",
        "2. 🗂️ sim classify  sugerir carpeta para un archivo",
        "3. 📈 sim nodo      visualizar Nodo Quero en ASCII",
        "4. 💾 sim backup    practicar flujo backup/rollback",
        "",
        "Escribe 1-4 o el comando completo.",
    ]
    print_panel("LABORATORIO // SIMULADORES SEGUROS", rows, C.BLUE)


def custody_scan(text: str) -> tuple[str, list[str], list[str]]:
    normalized = text.lower()
    alerts: list[str] = []
    discipline: list[str] = []
    for label, words in CUSTODY_RULES.items():
        hits = [word for word in words if word in normalized]
        if not hits:
            continue
        if label == "disciplina":
            discipline.extend(hits)
        else:
            alerts.append(f"{label}: {', '.join(hits[:3])}")

    if alerts:
        state = "🛡️ CUSTODIA ACTIVA: pausar, registrar, no ejecutar por impulso"
    elif discipline:
        state = "✅ DISCIPLINA DETECTADA: puede pasar a verificacion"
    else:
        state = "🟡 NEUTRAL: falta evidencia, pedir contexto o bitacora"
    return state, alerts, discipline


def action_sim_custody(raw_text: str = "") -> None:
    text = raw_text.strip()
    if not text:
        print_reply("[+] SIM CUSTODIA: escribe una frase para evaluar.")
        text = input(f"{C.GREEN}custodia>{C.RESET} ").strip()
    if not text:
        print_reply("[!] Simulador cancelado.")
        return
    state, alerts, discipline = custody_scan(text)
    rows = [
        f"📝 Entrada: {fit(text, term_width() - 14)}",
        f"🧭 Resultado: {state}",
        f"🚨 Alertas: {', '.join(alerts) if alerts else 'ninguna'}",
        f"✅ Disciplina: {', '.join(discipline) if discipline else 'no detectada'}",
        "📓 Accion segura: registrar antes de operar si aparece ruido.",
    ]
    print_panel("SIMULADOR // CUSTODIA", rows, C.RED if alerts else C.GREEN)


def action_sim_classify(raw_name: str = "") -> None:
    filename = raw_name.strip()
    if not filename:
        print_reply("[+] SIM CLASIFICACION: escribe un nombre de archivo.")
        filename = input(f"{C.GREEN}archivo>{C.RESET} ").strip()
    if not filename:
        print_reply("[!] Simulador cancelado.")
        return
    extracted = input(f"{C.GREEN}contexto opcional>{C.RESET} ").strip()
    result = RuleBasedClassifier().predict(filename, extracted_text=extracted)
    rows = [
        f"📄 Archivo: {filename}",
        f"🗂️ Categoria: {result.category}",
        f"📁 Carpeta: {result.folder}",
        f"📊 Confianza: {result.confidence}%",
        f"📡 Senales: {', '.join(result.signals) if result.signals else 'ninguna'}",
        f"🧠 Razon: {' '.join(result.reasons) if result.reasons else 'reglas basicas'}",
    ]
    print_panel("SIMULADOR // CLASIFICACION", rows, C.CYAN)


def action_sim_nodo() -> None:
    rows = [
        "📈 Precio",
        "  ^",
        "  |                 revisita",
        "  |                    v",
        "  |  EMA3/9 rotan  ----*----------------",
        "  |       * Nodo Quero fijo",
        "  |        \\",
        "  |         \\____ swing ____ rechazo ____",
        "  +--------------------------------------> tiempo",
        "",
        "📌 Regla: el nodo no se mueve con las EMAs.",
        "🛡️ Lectura: memoria estructural, no entrada automatica.",
    ]
    print_panel("SIMULADOR // NODO QUERO", rows, C.GOLD)


def action_sim_backup() -> None:
    rows = [
        "📄 A = documento actual que manda",
        "🧠 BUFFER = cambios pendientes",
        "1. 📤 ENVIAR: reconstruir A + BUFFER completo",
        "2. 💾 BACKUP: crear snapshot antes de guardar",
        "3. ✅ VERIFICAR: comparar A contra propuesta B",
        "4. 🔒 GUARDAR: solo si no hay perdidas",
        "5. ⏮️ ROLLBACK: restaurar snapshot con confirmacion",
        "",
        "🧪 Este simulador no modifica archivos reales.",
    ]
    print_panel("SIMULADOR // BACKUP / ROLLBACK", rows, C.MAGENTA)


def action_toggle(message: str) -> None:
    parts = message.split(maxsplit=1)
    state = load_visual_state()
    if len(parts) == 1:
        lines = ["[+] Objetos visuales:"]
        for key, label in VISUAL_OBJECTS.items():
            lines.append(f"  > {key}: {'ON' if state[key] else 'OFF'} - {label}")
        lines.append("Uso: /toggle matrix")
        print_reply("\n".join(lines))
        return
    key = parts[1].strip().lower()
    if key not in VISUAL_OBJECTS:
        print_reply(f"[!] Objeto desconocido: {key}. Usa /toggle para ver opciones.")
        return
    state[key] = not state[key]
    save_visual_state(state)
    print_reply(f"[+] {key} -> {'ON' if state[key] else 'OFF'}")
    print_control_center()


def action_images() -> None:
    files = image_files()
    if not files:
        print_reply("[!] No hay imagenes indexadas en danzariel_quero_data.")
        return
    print_reply("[+] Imagenes disponibles:")
    for index, path in enumerate(files[:40], start=1):
        print(f"{C.DIM}{index:02}.{C.RESET} {path.relative_to(settings.data_dir)}")


def action_image_send() -> None:
    files = image_files()
    selected = choose_file("[+] IMAGE SEND: elige imagen para copiar referencia Markdown.", files)
    if not selected:
        return
    relative = selected.relative_to(settings.data_dir).as_posix()
    payload = f"![{selected.stem}]({relative})\n\nRuta local: `{selected}`\n"
    copy_to_clipboard(payload)
    print_reply(f"[+] Referencia de imagen copiada al clipboard: {relative}")


def action_send() -> None:
    area = choose_area("[+] SEND: elige el area del bloque.")
    if not area:
        return
    selected = choose_file_in_area(area, "[+] SEND: elige el bloque que deseas enviar como Markdown.")
    if not selected:
        return
    copy_to_clipboard(markdown_for_file(selected))
    print_reply(f"[+] Copiado al clipboard como Markdown: {selected.relative_to(settings.data_dir)}")


def action_add() -> None:
    area = choose_area("[+] ADD: donde quieres guardar?")
    if not area:
        return
    title = input(f"{C.GREEN}titulo>{C.RESET} ").strip()
    if not title:
        print_reply("[!] Cancelado: falta titulo.")
        return
    print_reply("Escribe el contenido. Termina con una linea que diga: .")
    lines: list[str] = []
    while True:
        line = input(f"{C.GREEN}add>{C.RESET} ")
        if line.strip() == ".":
            break
        lines.append(line)
    content = "\n".join(lines).strip()
    if not content:
        print_reply("[!] Cancelado: contenido vacio.")
        return

    safe_title = "".join(ch if ch.isalnum() or ch in "._- " else "_" for ch in title).strip() or "nota"
    filename = safe_title if safe_title.endswith(".md") else f"{safe_title}.md"
    target = settings.data_dir / area / filename
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content + "\n", encoding="utf-8")
    print_reply(f"[+] Informacion agregada: {area}/{filename}")


def action_backup() -> None:
    area = choose_area("[+] BACKUP: elige el area del bloque.")
    if not area:
        return
    selected = choose_file_in_area(area, "[+] BACKUP: elige el bloque que quieres proteger.")
    if not selected:
        return
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    relative = selected.relative_to(settings.data_dir)
    target = settings.data_dir / "backups" / relative.parent / f"{selected.stem}__{stamp}{selected.suffix}"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(selected, target)
    print_reply(f"[+] Backup creado: {target.relative_to(settings.data_dir)}")


def action_rollback() -> None:
    backups = sorted((settings.data_dir / "backups").rglob("*"), key=lambda path: path.stat().st_mtime, reverse=True)
    backups = [path for path in backups if path.is_file()]
    backup = choose_file("[!] ROLLBACK MULTIDIMENSIONAL: elige backup origen.", backups)
    if not backup:
        return
    target = choose_file("[!] Elige bloque destino que sera reemplazado.")
    if not target:
        return
    print_reply(f"[!] Esto reemplazara: {target.relative_to(settings.data_dir)}")
    confirm = input(f"{C.RED}escribe RESTAURAR>{C.RESET} ").strip()
    if confirm != "RESTAURAR":
        print_reply("[!] Rollback cancelado.")
        return
    shutil.copy2(backup, target)
    print_reply(f"[+] Rollback aplicado desde: {backup.relative_to(settings.data_dir)}")


def handle_magic_action(message: str) -> bool:
    normalized = message.strip().lower()
    if normalized in {"/home", "home"}:
        action_home()
        return True
    if normalized in {"/ui", "ui"}:
        print_control_center()
        return True
    if normalized in {"/heart", "heart"}:
        action_heart()
        return True
    if normalized in {"/modes", "modes"}:
        action_modes()
        return True
    if normalized in {"/status", "status"}:
        action_status()
        return True
    if normalized in {"/lab", "lab"}:
        action_lab()
        return True
    if normalized in {"/ps3", "ps3"}:
        action_ps3()
        return True
    if normalized in {"/pulse", "pulse"}:
        action_pulse()
        return True
    if normalized in {"/sigil", "sigil", "/sello", "sello"}:
        action_sigil()
        return True
    if normalized in {"/simulators", "simulators", "simuladores"}:
        action_simulators()
        return True
    if normalized.startswith("sim custody") or normalized.startswith("/sim custody"):
        raw = message.split("custody", 1)[1] if "custody" in message else ""
        action_sim_custody(raw)
        return True
    if normalized.startswith("sim classify") or normalized.startswith("/sim classify"):
        raw = message.split("classify", 1)[1] if "classify" in message else ""
        action_sim_classify(raw)
        return True
    if normalized in {"sim nodo", "/sim nodo"}:
        action_sim_nodo()
        return True
    if normalized in {"sim backup", "/sim backup"}:
        action_sim_backup()
        return True
    if normalized.startswith("/toggle"):
        action_toggle(normalized)
        return True
    if normalized in {"/clip", "clip"}:
        action_clip()
        return True
    if normalized == "paste add":
        action_paste_add()
        return True
    if normalized in {"scan", "/scan"}:
        action_scan()
        return True
    if normalized == "clear":
        os.system("cls")
        print_header(wake="--wake" in sys.argv)
        return True
    if normalized in {"images", "/images"}:
        action_images()
        return True
    if normalized == "image send":
        action_image_send()
        return True
    if normalized == "add":
        action_add()
        return True
    if normalized == "send":
        action_send()
        return True
    if normalized == "backup":
        action_backup()
        return True
    if normalized == "rollback multidimensional":
        action_rollback()
        return True
    if normalized == "sos":
        global ACTIVE_MENU
        ACTIVE_MENU = "sos"
        print_reply(
            "🚨 SOS:\n"
            "  1. 🖥️ /server - revisar servidor\n"
            "  2. 📡 /url - ver URL del telefono\n"
            "  3. 🧾 /context - mostrar sistema para ChatGPT/Codex\n"
            "  4. 🔎 /diff - alias rapido de /context\n"
            "  5. 💾 backup - proteger bloque\n"
            "  6. 🚪 /exit - salir"
        )
        return True
    return False


def should_log_command(message: str) -> bool:
    normalized = message.strip().lower()
    return (
        normalized.startswith("/note ")
        or normalized in {"add", "backup", "rollback multidimensional", "paste add", "image send"}
    )


def main() -> None:
    ensure_workspace()
    wake = "--wake" in sys.argv
    print_header(wake=wake)

    while True:
        try:
            message = input(f"{C.GREEN}user@quero>{C.RESET} ").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{C.DIM}Cerrando chat.{C.RESET}")
            break

        if not message:
            continue

        message = translate_menu_choice(message)

        if message == "/exit":
            print_reply("Conversacion guardada. Hasta luego.")
            break

        if message.lower() == "danzariel":
            message = "/danzariel"

        if handle_magic_action(message):
            continue

        if message.startswith("/note "):
            reply = save_note_command(message)
        else:
            reply = terminal_reply(message)
        if should_log_command(message):
            record_message("user", message)
            record_message("assistant", reply)
        print_reply(reply)


if __name__ == "__main__":
    main()
