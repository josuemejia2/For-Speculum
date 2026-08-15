from __future__ import annotations

import json
import os
import socket
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

from danzariel_quero.core.config import settings
from danzariel_quero.services.files import ensure_workspace, list_area_files, search_files


def chat_log_path() -> Path:
    ensure_workspace()
    path = settings.data_dir / "memoria" / "chat.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def record_message(role: str, content: str) -> dict[str, Any]:
    entry = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "role": role,
        "content": content,
    }
    with chat_log_path().open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


def recent_messages(limit: int = 20) -> list[dict[str, Any]]:
    path = chat_log_path()
    if not path.exists():
        return []

    messages: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines()[-limit:]:
        try:
            messages.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return messages


def project_root() -> Path:
    return settings.project_root


def venv_python() -> Path:
    return project_root() / ".venv" / "Scripts" / "python.exe"


def environment_status() -> str:
    python_path = venv_python()
    if python_path.exists():
        return (
            "[+] Entorno listo.\n"
            f"- Python: {python_path}\n"
            "- Para activar manualmente:\n"
            "  .\\.venv\\Scripts\\Activate.ps1"
        )

    return (
        "[!] No encontre .venv.\n"
        "- Para crearlo e instalar dependencias:\n"
        "  .\\setup.bat"
    )


def local_ip() -> str:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 80))
            return sock.getsockname()[0]
    except OSError:
        return "127.0.0.1"


def server_port() -> int:
    return int(os.getenv("DQ_PORT", "8000"))


def server_status() -> str:
    port = server_port()
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=1):
            return (
                "[+] Servidor activo.\n"
                f"- PC: http://127.0.0.1:{port}\n"
                f"- Telefono: http://{local_ip()}:{port}"
            )
    except OSError:
        return (
            "[!] Servidor apagado.\n"
            "- Para iniciarlo desde este chat:\n"
            "  /start-server\n"
            "- O manualmente:\n"
            "  .\\run_server.bat"
        )


def run_git(args: list[str], max_lines: int = 40) -> str:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=project_root(),
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return "[git no disponible]"

    output = (result.stdout or result.stderr).strip()
    if not output:
        return "[sin salida]"

    lines = output.splitlines()
    if len(lines) <= max_lines:
        return output
    visible = "\n".join(lines[:max_lines])
    return f"{visible}\n... [{len(lines) - max_lines} linea(s) ocultas para mantener el reporte legible]"


def area_counts() -> list[str]:
    lines: list[str] = []
    ensure_workspace()
    for area in settings.areas:
        base = settings.data_dir / area
        count = len([path for path in base.rglob("*") if path.is_file()]) if base.exists() else 0
        lines.append(f"- {area}: {count} archivo(s)")
    return lines


def ai_context_report() -> str:
    port = server_port()
    python_path = venv_python()
    status = run_git(["status", "--short"], max_lines=35)
    branch = run_git(["branch", "--show-current"])
    diff_stat = run_git(["diff", "--stat"], max_lines=20)
    staged_stat = run_git(["diff", "--cached", "--stat"], max_lines=25)

    return "\n".join(
        [
            "# DANZARIEL-QUERO AI CONTEXT",
            "",
            "## Identidad",
            "- Sistema: DANZARIEL-QUERO",
            "- Modo: PC local como servidor privado para telefono, archivos y memoria",
            f"- Proyecto: {project_root()}",
            f"- Datos privados: {settings.data_dir}",
            "",
            "## Servidor",
            f"- PC: http://127.0.0.1:{port}",
            f"- Telefono: http://{local_ip()}:{port}",
            f"- Estado: {'activo' if 'Servidor activo' in server_status() else 'apagado'}",
            "",
            "## Entorno",
            f"- Python venv: {'listo' if python_path.exists() else 'faltante'}",
            "- Inicio terminal: .\\danzariel.bat",
            "- Inicio servidor: .\\run_server.bat o /start-server",
            "",
            "## Areas de conocimiento",
            *area_counts(),
            "",
            "## Git",
            f"- Rama: {branch}",
            "### Archivos cambiados",
            status,
            "",
            "### Diff de trabajo",
            diff_stat,
            "",
            "### Diff preparado",
            staged_stat,
            "",
            "## Seguridad",
            "- No mostrar tokens ni secretos.",
            "- No mover, borrar ni restaurar archivos sin confirmacion humana.",
            "- Runtime privado en danzariel_quero_data/ no debe subirse al repo.",
        ]
    )


def start_server() -> str:
    port = server_port()
    if "Servidor activo" in server_status():
        return server_status()

    python_path = venv_python()
    if not python_path.exists():
        return "[!] No puedo iniciar servidor porque falta .venv. Ejecuta /setup o .\\setup.bat."

    subprocess.Popen(
        [
            str(python_path),
            "-m",
            "uvicorn",
            "danzariel_quero.app.main:app",
            "--host",
            "0.0.0.0",
            "--port",
            str(port),
        ],
        cwd=project_root(),
        creationflags=subprocess.CREATE_NEW_CONSOLE,
    )
    return (
        "[+] Servidor iniciando.\n"
        f"- PC: http://127.0.0.1:{port}\n"
        f"- Telefono: http://{local_ip()}:{port}"
    )


def magic_key_reply() -> str:
    return (
        "[+] DANZARIEL activado.\n"
        "Elige una accion:\n"
        "\n"
        "  🏠 /home                    centro principal extendido\n"
        "  🖥️ /ui                      mostrar centro de control visual\n"
        "  ❤️ /heart                   mostrar Llave Sagrada / corazon\n"
        "  🧭 /modes                   mostrar modos Speculum\n"
        "  📊 /status                  resumen visual del sistema\n"
        "  🧪 /simulators              laboratorio seguro\n"
        "  🧬 /lab                     abrir DANZARIEL LAB visual\n"
        "  🎮 /PS3                     abrir escritorio futurista XMB\n"
        "  ✨ /pulse                   pulso animado del sistema\n"
        "  🪞 /sigil                   imagen fantastica de terminal\n"
        "  🎚️ /toggle objeto           encender/apagar objetos visuales\n"
        "  ➕ add                      agregar informacion\n"
        "  📥 paste add                guardar clipboard como bloque\n"
        "  📤 send                     enviar bloque como Markdown al clipboard\n"
        "  📋 /clip                    ver preview del clipboard\n"
        "  🖼️ images                   listar imagenes indexadas\n"
        "  🖼️ image send               copiar referencia Markdown de imagen\n"
        "  🔍 scan                     escanear areas\n"
        "  ⏮️ rollback multidimensional restaurar desde backup con confirmacion\n"
        "  💾 backup                   crear copia protegida\n"
        "\n"
        "Emergencia:\n"
        "  sos"
    )


def terminal_reply(message: str) -> str:
    text = message.strip()
    if not text:
        return "Te escucho. Escribe algo o usa /help."

    if text == "/danzariel":
        return magic_key_reply()

    if text.startswith("/search "):
        query = text.removeprefix("/search ").strip()
        results = search_files(query)
        if not results:
            return f"[!] Sin coincidencias para: {query}"
        lines = [f"[+] Resultados para '{query}':"]
        for item in results[:8]:
            lines.append(f"  > {item['area']}/{item['path']}")
        return "\n".join(lines)

    if text == "/history":
        messages = recent_messages(10)
        if not messages:
            return "[!] No hay historial todavia."
        return "\n".join(f"{m['role']}: {m['content']}" for m in messages)

    if text == "/files":
        summary = []
        for area in settings.areas:
            count = len(list_area_files(area))
            if count:
                summary.append(f"  > {area}: {count} archivo(s)")
        return "\n".join(summary) if summary else "[!] Todavia no hay archivos guardados."

    if text == "/env":
        return environment_status()

    if text == "/server":
        return server_status()

    if text == "/start-server":
        return start_server()

    if text == "/url":
        port = server_port()
        return f"PC: http://127.0.0.1:{port}\nTelefono: http://{local_ip()}:{port}"

    if text.lower() == "/ps3":
        port = server_port()
        return (
            "[+] PS3 XMB disponible.\n"
            f"- PC: http://127.0.0.1:{port}/PS3/\n"
            f"- Telefono: http://{local_ip()}:{port}/PS3/"
        )

    if text in {"/context", "/diff"}:
        return ai_context_report()

    if text == "/setup":
        return (
            "[+] Setup local:\n"
            "  1. Ejecuta: .\\setup.bat\n"
            "  2. Luego abre: .\\danzariel.bat\n"
            "  3. Para servidor: /start-server"
        )

    if text == "/help":
        return (
            "[+] Comandos principales:\n"
            "  🔑 danzariel      activar llave magica\n"
            "  🔑 /danzariel     mostrar acciones esenciales\n"
            "  🏠 /home          centro principal extendido\n"
            "  🖥️ /ui            centro de control visual\n"
            "  ❤️ /heart         mostrar Llave Sagrada / corazon\n"
            "  🧭 /modes         mostrar LECTURA, CUSTODIA, BITACORA, VERIFICAR...\n"
            "  📊 /status        servidor, memoria, git y entorno\n"
            "  🧪 /simulators    laboratorio seguro de practica\n"
            "  🧬 /lab           abrir DANZARIEL LAB visual\n"
            "  🎮 /PS3           abrir escritorio futurista XMB\n"
            "  ✨ /pulse         pulso animado del sistema\n"
            "  🪞 /sigil         imagen fantastica de terminal\n"
            "  🛡️ sim custody    detectar ruido en una frase\n"
            "  🗂️ sim classify   sugerir carpeta para un archivo\n"
            "  📈 sim nodo       explicar Nodo Quero en ASCII\n"
            "  💾 sim backup     practicar flujo backup/rollback\n"
            "  🎚️ /toggle objeto encender/apagar: matrix, scan, clock, clipboard, images\n"
            "  ➕ add            agregar informacion\n"
            "  📥 paste add      guardar contenido del clipboard como nota\n"
            "  📤 send           copiar bloque como Markdown al clipboard\n"
            "  📋 /clip          ver preview del clipboard\n"
            "  🖼️ images         listar imagenes guardadas\n"
            "  🖼️ image send     copiar referencia Markdown de una imagen\n"
            "  🔍 scan           ver conteo de areas\n"
            "  🧼 clear          limpiar pantalla y redibujar entorno\n"
            "  💾 backup         crear backup de un bloque\n"
            "  ⏮️ rollback multidimensional restaurar desde backup\n"
            "  🚨 sos            menu de emergencia\n"
            "\n"
            "Sistema:\n"
            "  🖥️ /server        estado del servidor\n"
            "  🚀 /start-server  activar servidor local\n"
            "  📡 /url           URL para PC y telefono\n"
            "  🗂️ /files         contar archivos por area\n"
            "  🔎 /search texto  buscar en archivos\n"
            "  🧾 /context       reporte seguro para ChatGPT/Codex\n"
            "  🔎 /diff          alias de /context\n"
            "  📝 /note t | c    guardar nota rapida\n"
            "  🕒 /history       ver ultimos mensajes\n"
            "  🐍 /env           ver entorno Python\n"
            "  ⚙️ /setup         preparar entorno\n"
            "  🚪 /exit          salir"
        )

    if text.startswith("/note "):
        return "[!] Usa: /note titulo | contenido"

    return "[!] Comando no reconocido. Escribe danzariel para ver las 4 acciones."


def save_note_command(text: str) -> str:
    from danzariel_quero.services.files import create_or_update_markdown

    body = text.removeprefix("/note ").strip()
    if "|" not in body:
        return "[!] Formato: /note titulo | contenido"

    title, content = [part.strip() for part in body.split("|", 1)]
    if not title or not content:
        return "[!] La nota necesita titulo y contenido."

    filename = title if title.endswith(".md") else f"{title}.md"
    saved = create_or_update_markdown("memoria", filename, content)
    return f"[+] Nota guardada en memoria/{saved}"
