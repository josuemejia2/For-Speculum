from pathlib import Path
import datetime
import os
import shutil
import socket
import subprocess
import sys
import time
import unicodedata
import webbrowser


try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except AttributeError:
    pass


BUILDER_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BUILDER_DIR.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from youtube_audio import download_audio

BACKUPS_DIR = BUILDER_DIR / "backups"
PATCHES_DIR = BUILDER_DIR / "patches"
LOGS_DIR = BUILDER_DIR / "logs"

DATA_DIR = PROJECT_DIR / "danzariel_quero_data"
DATA_BACKUPS_DIR = DATA_DIR / "backups"
WEB_STATIC_DIR = PROJECT_DIR / "danzariel_quero" / "web" / "static"
LAB_HTML = WEB_STATIC_DIR / "lab.html"
XMB_HTML = PROJECT_DIR / "xmb_desktop_ui" / "index.html"

HOST = "127.0.0.1"
DEFAULT_PORT = 8000
PANEL_MIN_WIDTH = 54
PANEL_MAX_WIDTH = 88


class C:
    RESET = "\033[0m"
    DIM = "\033[2m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    CYAN = "\033[96m"
    MAGENTA = "\033[95m"
    WHITE = "\033[97m"


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

DATA_AREAS = [
    "memoria",
    "inbox",
    "trading",
    "documentos",
    "knowledge",
    "investigacion",
    "bitacora",
]

MOBILE_NOTES_DIR = DATA_DIR / "memoria" / "notas"
MOBILE_IMAGES_DIR = DATA_DIR / "imagenes"

SIMULATOR_COMMANDS = {
    "1": "sim custody",
    "2": "sim classify",
    "3": "sim nodo",
    "4": "sim backup",
}

ACTIVE_MENU = None


def enable_terminal_colors():
    if sys.platform == "win32":
        os.system("")


def color(text, tone=C.WHITE):
    return f"{tone}{text}{C.RESET}"


def visual_width(text):
    total = 0
    for char in text:
        code = ord(char)
        if unicodedata.combining(char) or 0xFE00 <= code <= 0xFE0F:
            continue
        if code > 0xFFFF or unicodedata.east_asian_width(char) in {"F", "W"}:
            total += 2
        else:
            total += 1
    return total


def shorten_visual(text, max_width):
    if visual_width(text) <= max_width:
        return text

    ellipsis = "..."
    keep_width = max(max_width - visual_width(ellipsis), 0)
    result = ""
    used = 0
    for char in text:
        char_width = visual_width(char)
        if used + char_width > keep_width:
            break
        result += char
        used += char_width
    return result + ellipsis


def frame_rule(width):
    print(color("+" + "-" * (width - 2) + "+", C.MAGENTA))


def framed_line(text="", width=PANEL_MIN_WIDTH, center=False):
    inner = width - 4
    content = shorten_visual(text, inner)
    content_width = visual_width(content)
    remaining = max(inner - content_width, 0)

    if center:
        left = remaining // 2
        right = remaining - left
        body = " " + (" " * left) + content + (" " * right) + " "
    else:
        body = " " + content + (" " * remaining) + " "

    print(color("|", C.MAGENTA) + body + color("|", C.MAGENTA))


def panel(title, lines):
    visible_widths = [visual_width(title), *(visual_width(line) for line in lines)]
    width = min(max(max(visible_widths, default=0) + 4, PANEL_MIN_WIDTH), PANEL_MAX_WIDTH)
    print()
    frame_rule(width)
    framed_line(title, width, center=True)
    frame_rule(width)
    for line in lines:
        framed_line(line, width)
    frame_rule(width)
    print()


def read_env_value(name, default):
    env_file = PROJECT_DIR / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line or line.strip().startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            if key.strip() == name:
                return value.strip()
    return os.getenv(name, default)


def server_port():
    value = read_env_value("DQ_PORT", str(DEFAULT_PORT))
    try:
        return int(value)
    except ValueError:
        return DEFAULT_PORT


def local_ip():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 80))
            return sock.getsockname()[0]
    except OSError:
        return "127.0.0.1"


def run_git(*args):
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=12,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return f"[git no disponible] {exc}"

    output = result.stdout.strip()
    if result.stderr.strip():
        output += "\n" + result.stderr.strip()
    return output.strip()


def run_git_stdout(*args):
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=12,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    return result.stdout.strip()


def get_branch():
    return run_git("branch", "--show-current") or "desconocida"


def get_python_version():
    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"


def count_files(path, recursive=False):
    if not path.exists():
        return 0
    iterator = path.rglob("*") if recursive else path.iterdir()
    return sum(1 for item in iterator if item.is_file())


def count_backups():
    return count_files(BACKUPS_DIR) + count_files(DATA_BACKUPS_DIR, recursive=True)


def count_snapshots():
    return count_files(PATCHES_DIR) + count_files(LOGS_DIR)


def header():
    print()
    print(color("+------------------------------------------------+", C.GREEN))
    print(color("| DANZARIEL BUILDER // DEVELOPMENT SYSTEM        |", C.GREEN))
    print(color("+------------------------------------------------+", C.GREEN))
    print(color("| System        : Online                         |", C.GREEN))
    print(color("| Environment   : DEV                            |", C.GREEN))
    print(color("| Project       : For-Speculum_DEV               |", C.GREEN))
    print(color(f"| Python        : {get_python_version():<30}|", C.GREEN))
    print(color(f"| Branch        : {get_branch():<30}|", C.GREEN))
    print(color(f"| Backups       : {count_backups():<30}|", C.YELLOW if count_backups() == 0 else C.GREEN))
    print(color(f"| Snapshots     : {count_snapshots():<30}|", C.YELLOW if count_snapshots() == 0 else C.GREEN))
    print(color("+------------------------------------------------+", C.GREEN))
    print(
        color("ONLINE", C.GREEN)
        + " | "
        + color("DEV OK", C.GREEN)
        + " | "
        + color("PROD LOCKED", C.RED)
        + " | "
        + color("SAFE OK", C.GREEN)
    )
    print()


def quick_commands():
    print(color("QUICK COMMANDS", C.CYAN))
    print()
    print(color("  [+] builder", C.GREEN) + "              abre el panel del constructor")
    print(color("  [+] /home", C.GREEN) + "                muestra accesos principales")
    print(color("  [+] /heart", C.GREEN) + "               muestra Llave Sagrada")
    print(color("  [+] /modes", C.GREEN) + "               muestra modos operativos")
    print(color("  [+] /simulators", C.GREEN) + "          abre simuladores seguros")
    print(color("  [+] /help", C.GREEN) + "                muestra toda la ayuda")
    print(color("  [+] /lab", C.GREEN) + "                 abre la web del indicador")
    print(color("  [+] /AI", C.GREEN) + "                 abre el asistente local")
    print(color("  [+] /ps3", C.GREEN) + "                 abre la web PS3/XMB")
    print(color("  [+] /pulse", C.GREEN) + "              muestra pulso visual")
    print(color("  [+] /sigil", C.GREEN) + "              muestra sigilo terminal")
    print(color("  [+] /mp3", C.GREEN) + "                extrae audio autorizado a MP3")
    print(color("  [+] /clip", C.YELLOW) + "               inspecciona clipboard")
    print(color("  [+] /mobile", C.GREEN) + "              revisa notas/fotos del cel")
    print(color("  [+] /status", C.GREEN) + "              muestra estado Git simple")
    print(color("  [+] /diff", C.YELLOW) + "                crea reporte para AI")
    print(color("  [+] /snapshot", C.GREEN) + "            guarda estado + patch")
    print(color("  [+] /where", C.YELLOW) + "               muestra rutas protegidas")
    print(color("  [+] backup", C.YELLOW) + "              protege un bloque")
    print(color("  [-] /exit", C.RED) + "                salir del Builder")
    print()
    print("Escribe /help para comandos. Escribe /exit para salir.")


def entry_path(entry):
    return entry[3:] if len(entry) > 3 else entry


def is_automatic_path(path):
    normalized = path.replace("\\", "/").lower()
    return (
        "__pycache__/" in normalized
        or normalized.endswith(".pyc")
        or normalized.startswith("for-speculum-dev/logs/")
        or normalized.startswith("for-speculum-dev/patches/")
    )


def git_status_entries():
    output = run_git_stdout("status", "--short")
    return [line for line in output.splitlines() if line.strip()]


def visible_entries(entries):
    visible = [entry for entry in entries if not is_automatic_path(entry_path(entry))]
    hidden = len(entries) - len(visible)
    return visible, hidden


def categorize_status_entries(entries):
    groups = {"nuevos": [], "modificados": [], "borrados": [], "otros": []}
    for entry in entries:
        code = entry[:2]
        path = entry_path(entry)
        if code == "??" or "A" in code:
            groups["nuevos"].append(path)
        elif "D" in code:
            groups["borrados"].append(path)
        elif "M" in code:
            groups["modificados"].append(path)
        else:
            groups["otros"].append(path)
    return groups


def section_lines(title, lines, limit=10):
    output = [title]
    if not lines:
        output.append("  > nada")
        return output
    output.extend(f"  > {line}" for line in lines[:limit])
    hidden = len(lines) - min(len(lines), limit)
    if hidden:
        output.append(f"  > ... {hidden} mas")
    return output


def stat_summary_lines(title, raw_stat, limit=8):
    output = [title]
    if not raw_stat:
        output.append("  > nada")
        return output
    lines = [
        line.strip()
        for line in raw_stat.splitlines()
        if "__pycache__" not in line and ".pyc" not in line
    ]
    if not lines:
        output.append("  > solo cambios automaticos ocultados")
        return output
    output.extend(f"  > {line}" for line in lines[:limit])
    hidden = len(lines) - min(len(lines), limit)
    if hidden:
        output.append(f"  > ... {hidden} lineas mas ocultas")
    return output


def status():
    raw_entries = git_status_entries()
    entries, hidden_auto = visible_entries(raw_entries)
    groups = categorize_status_entries(entries)
    lines = [
        f"🌿 Rama actual : {get_branch()}",
        f"📊 Cambios     : {len(entries)}",
    ]
    if hidden_auto:
        lines.append(f"🧹 Automaticos : {hidden_auto} ocultos")
    if not raw_entries:
        lines.append("🟢 Laboratorio limpio. No hay cambios pendientes.")
    else:
        lines.append("")
        lines.extend(section_lines("🟢 Nuevos:", groups["nuevos"], limit=10))
        lines.extend(section_lines("🟡 Modificados:", groups["modificados"], limit=10))
        lines.extend(section_lines("🔴 Borrados:", groups["borrados"], limit=10))
        lines.extend(section_lines("⚪ Otros:", groups["otros"], limit=8))
    panel("DQ:// ESTADO GIT SIMPLE", lines)


def latest_file(directory, pattern):
    if not directory.exists():
        return None
    files = [path for path in directory.glob(pattern) if path.is_file()]
    if not files:
        return None
    return max(files, key=lambda path: path.stat().st_mtime)


def diff():
    raw_entries = git_status_entries()
    entries, hidden_auto = visible_entries(raw_entries)
    groups = categorize_status_entries(entries)
    latest_patch = latest_file(PATCHES_DIR, "*.patch")
    latest_status = latest_file(LOGS_DIR, "status_*.txt")
    port = server_port()
    lines = [
        "🧠 Estado para Codex/ChatGPT",
        f"📁 Proyecto : {PROJECT_DIR}",
        f"🌿 Rama     : {get_branch()}",
        f"🧬 /lab     : http://127.0.0.1:{port}/lab",
        f"🎮 /ps3     : http://127.0.0.1:{port}/PS3/",
        f"📊 Cambios  : {len(entries)} archivo(s) visibles",
    ]
    if hidden_auto:
        lines.append(f"🧹 Ruido    : {hidden_auto} automaticos ocultos")
    if not raw_entries:
        lines.append("🟢 Sin cambios pendientes. Estado limpio.")
        panel("DQ:// REPORTE PARA AI", lines)
        return
    lines.extend(
        [
            "",
            "🧭 Resumen para la siguiente AI:",
            "  > Proyecto: portal Danzariel-Quero.",
            "  > La web del indicador se abre con /lab.",
            "  > PS3/XMB se abre con /ps3.",
            "  > No tocar PROD ni borrar sin confirmacion humana.",
            "  > Para detalle exacto: usar /snapshot.",
            "",
        ]
    )
    lines.extend(section_lines("🟢 Archivos nuevos:", groups["nuevos"], limit=12))
    lines.extend(section_lines("🟡 Archivos modificados:", groups["modificados"], limit=12))
    lines.extend(section_lines("🔴 Archivos borrados:", groups["borrados"], limit=12))
    lines.extend(section_lines("⚪ Otros estados:", groups["otros"], limit=8))
    lines.append("")
    lines.extend(stat_summary_lines("📐 Cambio tracked sin stage:", run_git_stdout("diff", "--stat")))
    lines.append("")
    lines.extend(stat_summary_lines("📦 Cambio preparado/staged:", run_git_stdout("diff", "--cached", "--stat")))
    lines.append("")
    if latest_status or latest_patch:
        lines.append("💾 Ultimo snapshot disponible:")
        if latest_status:
            lines.append(f"  > Status: {latest_status}")
        if latest_patch:
            lines.append(f"  > Patch : {latest_patch}")
    else:
        lines.append("🟡 No hay snapshot guardado todavia. Usa /snapshot.")
    panel("DQ:// REPORTE PARA AI", lines)


def snapshot():
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    PATCHES_DIR.mkdir(exist_ok=True)
    LOGS_DIR.mkdir(exist_ok=True)
    status_file = LOGS_DIR / f"status_{timestamp}.txt"
    diff_file = PATCHES_DIR / f"changes_{timestamp}.patch"
    status_file.write_text(run_git("status"), encoding="utf-8")
    diff_file.write_text(run_git("diff"), encoding="utf-8")
    panel(
        "DQ:// SNAPSHOT SEGURO CREADO",
        [
            f"💾 Status : {status_file}",
            f"📦 Patch  : {diff_file}",
            "🟢 Evidencia lista para Codex/ChatGPT.",
        ],
    )


def where():
    port = server_port()
    panel(
        "DQ:// MAPA DE SEGURIDAD",
        [
            f"🧪 DEV       : {PROJECT_DIR}",
            f"🛠️ Builder   : {BUILDER_DIR}",
            f"📜 Logs      : {LOGS_DIR}",
            f"📦 Patches   : {PATCHES_DIR}",
            f"💾 Backups   : {BACKUPS_DIR}",
            f"🧠 Data      : {DATA_DIR}",
            f"🧬 /lab      : http://127.0.0.1:{port}/lab",
            f"🎮 /ps3      : http://127.0.0.1:{port}/PS3/",
            f"📄 Web file  : {LAB_HTML}",
            f"🕹️ XMB file  : {XMB_HTML}",
            "🔴 PROD NO ES MODIFICADO POR ESTE BUILDER.",
        ],
    )


def home():
    panel(
        "DANZARIEL-QUERO // ACCESOS PRINCIPALES",
        [
            "❤️ [H] /heart       ver Llave Sagrada / corazon",
            "🧭 [M] /modes       modos operativos del asistente",
            "📊 [S] /status      servidor, memoria, git y entorno",
            "🧪 [X] /simulators  practicas sin tocar datos reales",
            "🧬 [L] /lab         abrir DANZARIEL LAB visual",
            "🤖 [A] /AI          abrir asistente local ChatGPT-like",
            "🎮 [3] /ps3         abrir escritorio futurista XMB",
            "✨ [P] /pulse       pulso animado del sistema",
            "🪞 [G] /sigil       imagen fantastica de terminal",
            "📋 [C] /clip        inspeccionar clipboard",
            "💾 [B] backup       proteger un bloque",
        ],
    )


def heart():
    panel(
        "LLAVE SAGRADA // CORAZON DEL SISTEMA",
        [
            "[📖 ACTA] origen y fe :: inmutable",
            "[📓 BITACORA] evidencia historica :: registro",
            "[🧾 GLOSARIO] lenguaje del sistema :: control semantico",
            "[⚗️ INVESTIGACION] validacion alquimica :: referencia",
            "[🎮 LEGACY] rama aplicada :: simulacion",
            "[📘 MANUAL] motor tecnico :: operativo",
            "[🧠 METATRON] conciencia del operador :: memoria psi",
            "[🌌 PARADIGMA] marco universal :: lectura",
            "[🛠️ PROTOCOLO] QUERO.OS :: edicion cero perdida",
            "",
            "⚖️ Regla: el simbolo orienta, la evidencia decide.",
            "🔒 Acta: inmutable. 📘 Manual: operativo.",
            "📓 Bitacora: verdad registrada.",
        ],
    )


def modes():
    lines = [f"[{name}] {description}" for name, description in MODES]
    lines.extend(
        [
            "",
            "🪞 Speculum no decide por el Operador.",
            "🛡️ Speculum refleja, ordena, registra, verifica y custodia.",
        ]
    )
    panel("SPECULUM // MODOS OPERATIVOS", lines)


def clipboard_text():
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


def clip():
    text = clipboard_text()
    if not text:
        panel("DQ:// CLIPBOARD", ["🟡 Clipboard vacio o no disponible."])
        return
    lines = [f"📋 Clipboard listo: {len(text)} caracteres.", ""]
    preview = text.replace("\r", "").splitlines()
    lines.extend(f"  | {line}" for line in preview[:8])
    if len(preview) > 8:
        lines.append("  | ... preview recortado")
    panel("DQ:// CLIPBOARD", lines)


def latest_mobile_files(directory, limit=6):
    if not directory.exists():
        return []
    files = [path for path in directory.rglob("*") if path.is_file()]
    return sorted(files, key=lambda path: path.stat().st_mtime, reverse=True)[:limit]


def mobile():
    MOBILE_NOTES_DIR.mkdir(parents=True, exist_ok=True)
    MOBILE_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    notes = latest_mobile_files(MOBILE_NOTES_DIR)
    images = latest_mobile_files(MOBILE_IMAGES_DIR)
    lines = [
        "📱 Bandeja movil conectada.",
        f"📝 Notas  : {MOBILE_NOTES_DIR}",
        f"🖼️ Fotos  : {MOBILE_IMAGES_DIR}",
        "",
        f"📝 Notas guardadas : {count_files(MOBILE_NOTES_DIR, recursive=True)}",
        f"🖼️ Fotos guardadas : {count_files(MOBILE_IMAGES_DIR, recursive=True)}",
        "",
        "🟢 Ultimas notas:",
    ]
    if notes:
        lines.extend(f"  > {path.relative_to(DATA_DIR)}" for path in notes)
    else:
        lines.append("  > nada todavia")
    lines.append("")
    lines.append("🟢 Ultimas fotos:")
    if images:
        lines.extend(f"  > {path.relative_to(DATA_DIR)}" for path in images)
    else:
        lines.append("  > nada todavia")
    lines.extend(
        [
            "",
            "🟡 Evaluacion pendiente: luego podemos crear /evaluar-mobile.",
        ]
    )
    panel("DQ:// BANDEJA MOVIL", lines)


def pulse():
    frames = [
        "🧬 memoria local",
        "🧬 memoria local  ->  📓 bitacora",
        "🧬 memoria local  ->  📓 bitacora  ->  🛡️ custodia",
        "🧬 memoria local  ->  📓 bitacora  ->  🛡️ custodia  ->  ✅ verificacion",
        "🧬 memoria local  ->  📓 bitacora  ->  🛡️ custodia  ->  ✅ verificacion  ->  🔑 llave",
    ]
    print()
    for _ in range(2):
        for frame in frames:
            sys.stdout.write("\r" + color(shorten_visual(frame, 78).ljust(78), C.CYAN))
            sys.stdout.flush()
            time.sleep(0.12)
    sys.stdout.write("\r" + " " * 78 + "\r")
    sys.stdout.flush()
    panel(
        "DANZARIEL-QUERO // PULSO VISUAL",
        [
            "✨ Pulso completo.",
            "🧬 Memoria: activa",
            "📓 Bitacora: lista",
            "🛡️ Custodia: vigilante",
            "✅ Verificacion: disponible",
            "🔑 Llave: bajo control del Operador",
        ],
    )


def sigil():
    panel(
        "DANZARIEL-QUERO // SIGILO TERMINAL",
        [
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
            "🪞 Imagen de terminal: sigilo visual, no foto real.",
            "🖼️ Para imagenes reales conviene abrir archivo o web local.",
        ],
    )


def simulators():
    global ACTIVE_MENU
    ACTIVE_MENU = "simulators"
    panel(
        "LABORATORIO // SIMULADORES SEGUROS",
        [
            "1. 🛡️ sim custody   detectar ruido en una frase",
            "2. 🗂️ sim classify  sugerir carpeta para un archivo",
            "3. 📈 sim nodo      visualizar Nodo Quero en ASCII",
            "4. 💾 sim backup    practicar flujo backup/rollback",
            "",
            "Escribe 1-4 o el comando completo.",
        ],
    )


def custody_scan(text):
    normalized = text.lower()
    alerts = []
    discipline = []
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


def sim_custody(raw_text=""):
    text = raw_text.strip()
    if not text:
        panel("SIMULADOR // CUSTODIA", ["🛡️ Escribe una frase para evaluar."])
        text = input(color("custodia> ", C.GREEN)).strip()
    if not text:
        panel("SIMULADOR // CUSTODIA", ["🟡 Simulador cancelado."])
        return
    state, alerts, discipline = custody_scan(text)
    panel(
        "SIMULADOR // CUSTODIA",
        [
            f"📝 Entrada: {text}",
            f"🧭 Resultado: {state}",
            f"🚨 Alertas: {', '.join(alerts) if alerts else 'ninguna'}",
            f"✅ Disciplina: {', '.join(discipline) if discipline else 'no detectada'}",
            "📓 Accion segura: registrar antes de operar si aparece ruido.",
        ],
    )


def sim_classify(raw_name=""):
    filename = raw_name.strip()
    if not filename:
        panel("SIMULADOR // CLASIFICACION", ["🗂️ Escribe un nombre de archivo."])
        filename = input(color("archivo> ", C.GREEN)).strip()
    if not filename:
        panel("SIMULADOR // CLASIFICACION", ["🟡 Simulador cancelado."])
        return
    extracted = input(color("contexto opcional> ", C.GREEN)).strip()
    try:
        from quero.brain.classifier import RuleBasedClassifier

        result = RuleBasedClassifier().predict(filename, extracted_text=extracted)
        lines = [
            f"📄 Archivo: {filename}",
            f"🗂️ Categoria: {result.category}",
            f"📁 Carpeta: {result.folder}",
            f"📊 Confianza: {result.confidence}%",
            f"📡 Senales: {', '.join(result.signals) if result.signals else 'ninguna'}",
            f"🧠 Razon: {' '.join(result.reasons) if result.reasons else 'reglas basicas'}",
        ]
    except Exception as exc:
        lines = [
            f"📄 Archivo: {filename}",
            "🟡 Clasificador no disponible.",
            f"⚠️ Detalle: {exc}",
        ]
    panel("SIMULADOR // CLASIFICACION", lines)


def sim_nodo():
    panel(
        "SIMULADOR // NODO QUERO",
        [
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
        ],
    )


def sim_backup():
    panel(
        "SIMULADOR // BACKUP / ROLLBACK",
        [
            "📄 A = documento actual que manda",
            "🧠 BUFFER = cambios pendientes",
            "1. 📤 ENVIAR: reconstruir A + BUFFER completo",
            "2. 💾 BACKUP: crear snapshot antes de guardar",
            "3. ✅ VERIFICAR: comparar A contra propuesta B",
            "4. 🔒 GUARDAR: solo si no hay perdidas",
            "5. ⏮️ ROLLBACK: restaurar snapshot con confirmacion",
            "",
            "🧪 Este simulador no modifica archivos reales.",
        ],
    )


def area_files(area):
    base = DATA_DIR / area
    if not base.exists():
        return []
    return sorted([path for path in base.rglob("*") if path.is_file()], key=lambda path: str(path).lower())


def choose_area():
    lines = ["💾 BACKUP: elige el area del bloque."]
    for index, area in enumerate(DATA_AREAS, start=1):
        lines.append(f"{index}. {area}")
    panel("BACKUP // AREA", lines)
    choice = input(color("area> ", C.GREEN)).strip().lower()
    if choice in DATA_AREAS:
        return choice
    try:
        selected = int(choice)
    except ValueError:
        panel("BACKUP // CANCELADO", ["🟡 Area invalida."])
        return None
    if selected < 1 or selected > len(DATA_AREAS):
        panel("BACKUP // CANCELADO", ["🟡 Area fuera de rango."])
        return None
    return DATA_AREAS[selected - 1]


def choose_file(area):
    files = area_files(area)
    if not files:
        panel("BACKUP // CANCELADO", [f"🟡 No hay archivos en {area}."])
        return None
    lines = [f"💾 BACKUP: elige archivo en {area}."]
    for index, path in enumerate(files[:30], start=1):
        lines.append(f"{index:02}. {path.relative_to(DATA_DIR)}")
    if len(files) > 30:
        lines.append(f"... {len(files) - 30} archivos mas ocultos")
    panel("BACKUP // ARCHIVO", lines)
    choice = input(color("archivo> ", C.GREEN)).strip()
    try:
        selected = int(choice)
    except ValueError:
        panel("BACKUP // CANCELADO", ["🟡 Opcion invalida."])
        return None
    if selected < 1 or selected > min(len(files), 30):
        panel("BACKUP // CANCELADO", ["🟡 Opcion fuera de rango."])
        return None
    return files[selected - 1]


def backup():
    area = choose_area()
    if not area:
        return
    selected = choose_file(area)
    if not selected:
        return
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    relative = selected.relative_to(DATA_DIR)
    target = DATA_BACKUPS_DIR / relative.parent / f"{selected.stem}__{stamp}{selected.suffix}"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(selected, target)
    panel(
        "BACKUP // BLOQUE PROTEGIDO",
        [
            f"💾 Origen : {relative}",
            f"📦 Backup : {target.relative_to(DATA_DIR)}",
            "🟢 Copia protegida creada.",
        ],
    )


def mp3():
    panel(
        "AUDIO OFFLINE // YOUTUBE A MP3",
        [
            "Usa solo contenido propio, con licencia o cuya descarga tengas autorizada.",
            "El audio se guarda en iCloud Drive/sonidos.",
            "Escribe cancelar para salir.",
        ],
    )
    url = input(color("URL de YouTube> ", C.GREEN)).strip()
    if not url or url.lower() in {"cancelar", "cancel", "salir"}:
        panel("MP3 // CANCELADO", ["🟡 Extraccion cancelada."])
        return

    quality = input(color("Calidad MP3 en kbps [128]> ", C.GREEN)).strip() or "128"
    if quality not in {"96", "128", "160", "192", "256", "320"}:
        panel("MP3 // CANCELADO", ["🟡 Calidad invalida. Usa 96, 128, 160, 192, 256 o 320."])
        return

    panel("MP3 // PROCESANDO", ["🟢 Descargando y convirtiendo; un video largo puede tardar varios minutos."])
    try:
        result = download_audio(url, quality=quality)
    except (RuntimeError, ValueError) as exc:
        panel("MP3 // ERROR", [f"🔴 {exc}"])
        return
    panel("MP3 // LISTO", [f"🎧 Archivo: {result}"])


def port_is_open(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        return sock.connect_ex((host, port)) == 0


def python_executable():
    venv_python = PROJECT_DIR / ".venv" / "Scripts" / "python.exe"
    if venv_python.exists():
        return str(venv_python)
    return sys.executable


def start_danzariel_server(port):
    creation_flags = 0
    if sys.platform == "win32":
        creation_flags = subprocess.CREATE_NEW_CONSOLE
    subprocess.Popen(
        [
            python_executable(),
            "-m",
            "uvicorn",
            "danzariel_quero.app.main:app",
            "--host",
            "0.0.0.0",
            "--port",
            str(port),
        ],
        cwd=PROJECT_DIR,
        creationflags=creation_flags,
    )


def wait_for_server(port):
    for _ in range(40):
        if port_is_open(HOST, port):
            return True
        time.sleep(0.25)
    return False


def ensure_server_panel(title, port):
    if port_is_open(HOST, port):
        panel(title, ["🟢 Servidor online."])
        return
    start_danzariel_server(port)
    lines = [
        "🟡 Servidor apagado, iniciando...",
        "🟢 [+] Servidor iniciando.",
        f"🖥️ PC: http://127.0.0.1:{port}",
        f"📱 Telefono: http://{local_ip()}:{port}",
    ]
    if not wait_for_server(port):
        lines.append("🟡 Todavia arrancando. Abro la ruta de todos modos.")
    panel(title, lines)


def start_lab():
    port = server_port()
    url = f"http://{HOST}:{port}/lab"
    phone_url = f"http://{local_ip()}:{port}/lab"
    panel("DQ:// LAB", ["🧬 Abriendo web del indicador..."])
    if not LAB_HTML.exists():
        panel("DQ:// LAB // ERROR", ["🔴 Web del indicador no encontrada.", f"🟡 Ruta esperada: {LAB_HTML}"])
        return
    ensure_server_panel("DQ:// LAB // SERVIDOR", port)
    panel(
        "LAB DEL INDICADOR // ABIERTO",
        [
            f"🧬 PC: {url}",
            f"📱 Telefono: {phone_url}",
            "📈 Indicador, sensores, calculadoras y laboratorio.",
            "🟢 Verde = avance/positivo  🟡 amarillo = revisar",
        ],
    )
    webbrowser.open(url)
    panel("DQ:// NAVEGADOR", ["🌐 Navegador abierto."])


def local_ai_python():
    env_python = PROJECT_DIR / "env" / "Scripts" / "python.exe"
    if env_python.exists():
        return str(env_python)
    return python_executable()


def start_ai():
    port = 5000
    url = f"http://{HOST}:{port}/"
    app_script = PROJECT_DIR / "local_chatgpt_app.py"
    if not app_script.exists():
        panel("DQ:// AI // ERROR", ["🔴 Asistente local no encontrado.", f"🟡 Ruta esperada: {app_script}"])
        return

    if not port_is_open(HOST, port):
        creation_flags = getattr(subprocess, "CREATE_NO_WINDOW", 0) if sys.platform == "win32" else 0
        subprocess.Popen(
            [local_ai_python(), str(app_script)],
            cwd=PROJECT_DIR,
            creationflags=creation_flags,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        time.sleep(1.2)

    online = port_is_open(HOST, port)
    panel(
        "ASISTENTE LOCAL // AI",
        [
            f"🤖 PC: {url}",
            "🧠 ChatGPT local con memoria y contexto de tus archivos.",
            "🟢 Servidor online." if online else "🟡 Servidor iniciando; abro la ruta de todos modos.",
        ],
    )
    webbrowser.open(url)
    panel("DQ:// NAVEGADOR", ["🌐 Asistente local abierto."])


def start_ps3():
    port = server_port()
    url = f"http://{HOST}:{port}/PS3/"
    phone_url = f"http://{local_ip()}:{port}/PS3/"
    if not XMB_HTML.exists():
        panel("DQ:// PS3 XMB // ERROR", ["🔴 Web PS3/XMB no encontrada.", f"🟡 Ruta esperada: {XMB_HTML}"])
        return
    ensure_server_panel("DQ:// PS3 XMB // SERVIDOR", port)
    panel(
        "PS3 XMB OS // ABIERTO",
        [
            f"🧬 PC: {url}",
            f"📱 Telefono: {phone_url}",
            "🕹️ Escritorio modular futurista inspirado en XMB.",
            "⬅️➡️ Horizontal  ↑↓ Vertical  Enter abre modulo.",
        ],
    )
    webbrowser.open(url)
    panel("DQ:// NAVEGADOR", ["🌐 Navegador abierto."])


def help_menu():
    panel(
        "DANZARIEL BUILDER // HELP",
        [
            "🟢 builder      redibuja el panel del constructor",
            "🏠 /home        accesos principales del sistema",
            "❤️ /heart       ver Llave Sagrada / corazon",
            "🧬 /lab         abre la web del indicador",
            "🎮 /ps3         abre la web PS3/XMB",
            "📊 /status      estado Git simple con semaforo",
            "🧠 /diff        reporte claro para Codex/ChatGPT",
            "💾 /snapshot    crear snapshot del estado actual",
            "🛡️ /where       mostrar entorno y rutas protegidas",
            "📘 /help        mostrar esta ayuda",
            "🔴 /exit        cerrar Builder",
            "",
            "🟢 verde    = avanzar / positivo / OK",
            "🟡 amarillo = intermedio / advertencia / revisar",
            "🔴 rojo     = negativo / parar / salir / prod bloqueado",
            "",
            "MODO ACTUAL: SOLO LECTURA + SNAPSHOTS + LAB",
        ],
    )


def help_menu():
    panel(
        "DANZARIEL BUILDER // HELP",
        [
            "🟢 builder      redibuja el panel del constructor",
            "🏠 /home        accesos principales del sistema",
            "❤️ /heart       ver Llave Sagrada / corazon",
            "🧭 /modes       modos operativos del asistente",
            "🧪 /simulators  practicas sin tocar datos reales",
            "🧬 /lab         abre la web del indicador",
            "🤖 /AI          abre el asistente local",
            "🎮 /ps3         abre la web PS3/XMB",
            "✨ /pulse       pulso animado del sistema",
            "🪞 /sigil       imagen fantastica de terminal",
            "🎧 /mp3         extraer audio autorizado de YouTube a MP3",
            "📋 /clip        inspeccionar clipboard",
            "📱 /mobile      revisar notas/fotos del telefono",
            "📊 /status      estado Git simple con semaforo",
            "🧠 /diff        reporte claro para Codex/ChatGPT",
            "💾 /snapshot    crear snapshot del estado actual",
            "🛡️ /where       mostrar entorno y rutas protegidas",
            "💾 backup       proteger un bloque",
            "🛡️ sim custody  detectar ruido en una frase",
            "🗂️ sim classify sugerir carpeta para un archivo",
            "📈 sim nodo     visualizar Nodo Quero en ASCII",
            "💾 sim backup   practicar flujo backup/rollback",
            "📘 /help        mostrar esta ayuda",
            "🔴 /exit        cerrar Builder",
            "",
            "🟢 verde    = avanzar / positivo / OK",
            "🟡 amarillo = intermedio / advertencia / revisar",
            "🔴 rojo     = negativo / parar / salir / prod bloqueado",
            "",
            "MODO ACTUAL: SOLO LECTURA + SNAPSHOTS + LAB",
        ],
    )


def main():
    global ACTIVE_MENU
    enable_terminal_colors()
    BACKUPS_DIR.mkdir(exist_ok=True)
    PATCHES_DIR.mkdir(exist_ok=True)
    LOGS_DIR.mkdir(exist_ok=True)
    header()
    quick_commands()

    while True:
        try:
            command = input(color("\nDanzariel> ", C.GREEN)).strip()
            if ACTIVE_MENU == "simulators" and command in SIMULATOR_COMMANDS:
                command = SIMULATOR_COMMANDS[command]
                ACTIVE_MENU = None
            command_lower = command.lower()

            if command_lower in ("builder", "danzariel"):
                header()
                quick_commands()
            elif command_lower == "/home":
                home()
            elif command_lower == "/heart":
                heart()
            elif command_lower == "/modes":
                modes()
            elif command_lower == "/simulators":
                simulators()
            elif command_lower == "/pulse":
                pulse()
            elif command_lower == "/sigil":
                sigil()
            elif command_lower == "/mp3":
                mp3()
            elif command_lower == "/clip":
                clip()
            elif command_lower in ("/mobile", "/capturas"):
                mobile()
            elif command_lower in ("/lab", "/playground"):
                start_lab()
            elif command_lower in ("/ai", "/assistant"):
                start_ai()
            elif command_lower == "/ps3":
                start_ps3()
            elif command_lower == "/status":
                status()
            elif command_lower == "/diff":
                diff()
            elif command_lower == "/snapshot":
                snapshot()
            elif command_lower == "/where":
                where()
            elif command_lower == "/help":
                help_menu()
            elif command_lower == "backup":
                backup()
            elif command_lower.startswith("sim custody"):
                sim_custody(command.split("custody", 1)[1] if "custody" in command else "")
            elif command_lower.startswith("sim classify"):
                sim_classify(command.split("classify", 1)[1] if "classify" in command else "")
            elif command_lower == "sim nodo":
                sim_nodo()
            elif command_lower == "sim backup":
                sim_backup()
            elif command_lower == "/exit":
                panel("DQ:// BUILDER CERRADO", ["🔴 Salir del Builder.", "🟢 DEV permanece seguro."])
                break
            elif not command:
                continue
            else:
                panel("DQ:// COMANDO DESCONOCIDO", ["🟡 Escribe /help para ver comandos disponibles."])
        except KeyboardInterrupt:
            panel("DQ:// BUILDER CERRADO", ["🔴 Interrupcion recibida."])
            break


if __name__ == "__main__":
    main()

