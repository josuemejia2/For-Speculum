from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
from pathlib import Path
from urllib.parse import urlparse

YOUTUBE_HOSTS = {"youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be", "www.youtu.be"}
ANSI_ESCAPE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")


def ensure_ffmpeg_on_path() -> None:
    if shutil.which("ffmpeg"):
        return

    search_roots = [
        Path(os.getenv("LOCALAPPDATA", "")) / "Microsoft" / "WinGet" / "Packages",
        Path(os.getenv("ProgramFiles", "C:\\Program Files")) / "ffmpeg",
    ]
    for root in search_roots:
        if not root.exists():
            continue
        matches = list(root.glob("**/bin/ffmpeg.exe"))
        if not matches:
            continue
        os.environ["PATH"] = f"{matches[0].parent}{os.pathsep}{os.environ.get('PATH', '')}"
        return


def is_youtube_url(value: str) -> bool:
    parsed = urlparse(value.strip())
    return parsed.scheme in {"http", "https"} and parsed.hostname in YOUTUBE_HOSTS


def audio_output_dir(output_dir: Path | None = None) -> Path:
    configured_dir = os.getenv("DQ_AUDIO_OUTPUT_DIR", "").strip()
    default_dir = Path.home() / "iCloudDrive" / "sonidos"
    target = output_dir
    if target is None:
        target = Path(configured_dir).expanduser() if configured_dir else default_dir
    target.mkdir(parents=True, exist_ok=True)
    return target


def build_download_options(output_dir: Path, quality: str) -> dict[str, object]:
    options: dict[str, object] = {
        "format": "bestaudio/best",
        "outtmpl": str(output_dir / "%(title)s.%(ext)s"),
        "noplaylist": True,
        "windowsfilenames": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": quality,
            }
        ],
    }
    browser = os.getenv("YOUTUBE_COOKIES_FROM_BROWSER", "").strip()
    profile = os.getenv("YOUTUBE_COOKIES_BROWSER_PROFILE", "").strip()
    cookie_file = os.getenv("YOUTUBE_COOKIES_FILE", "").strip()
    if cookie_file and (browser or profile):
        raise ValueError("Configura solo una opcion: YOUTUBE_COOKIES_FILE o YOUTUBE_COOKIES_FROM_BROWSER.")
    if profile and not browser:
        raise ValueError("YOUTUBE_COOKIES_BROWSER_PROFILE requiere YOUTUBE_COOKIES_FROM_BROWSER.")
    if cookie_file:
        options["cookiefile"] = str(Path(cookie_file).expanduser())
    elif browser:
        options["cookiesfrombrowser"] = (browser, profile or None)
    return options


def _download_error_message(error: Exception) -> str:
    message = ANSI_ESCAPE.sub("", str(error))
    if "could not copy chrome cookie database" in message.lower():
        return (
            "yt-dlp no puede leer la base de cookies de Chrome en el PC. Cierra Chrome por completo, "
            "incluidos los procesos chrome.exe en segundo plano, y vuelve a probar. Si persiste, "
            "exporta las cookies de YouTube en formato Netscape y configura "
            "YOUTUBE_COOKIES_FILE=C:/ruta/privada/cookies.txt en .env; elimina "
            "YOUTUBE_COOKIES_FROM_BROWSER y reinicia el servidor. No compartas ese archivo."
        )
    if "sign in to confirm" in message.lower() or "not a bot" in message.lower():
        return (
            "YouTube pide verificar que no eres un bot. Configura cookies locales en .env con "
            "YOUTUBE_COOKIES_FROM_BROWSER=chrome (o edge) y reinicia el servidor. "
            "El navegador debe tener iniciada tu sesion de YouTube."
        )
    return message


def download_audio(url: str, output_dir: Path | None = None, quality: str = "128") -> Path:
    if not is_youtube_url(url):
        raise ValueError("La URL debe pertenecer a YouTube y empezar por http:// o https://.")
    ensure_ffmpeg_on_path()
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("No encuentro ffmpeg. Instalalo y vuelve a intentar.")

    try:
        import yt_dlp
    except ImportError as exc:
        raise RuntimeError("Falta yt-dlp. Ejecuta: python -m pip install yt-dlp") from exc

    target = audio_output_dir(output_dir)
    options = build_download_options(target, quality)
    with yt_dlp.YoutubeDL(options) as downloader:
        try:
            info = downloader.extract_info(url, download=True)
        except yt_dlp.utils.DownloadError as exc:
            raise RuntimeError(_download_error_message(exc)) from exc
        filename = Path(downloader.prepare_filename(info)).with_suffix(".mp3")
    return filename


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Descarga audio de un video de YouTube autorizado y lo convierte a MP3."
    )
    parser.add_argument("url", help="URL de YouTube")
    parser.add_argument(
        "--quality",
        choices=("96", "128", "160", "192", "256", "320"),
        default="128",
        help="Bitrate MP3 en kbps (por defecto: 128)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Carpeta destino (por defecto: iCloudDrive/sonidos)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        result = download_audio(args.url, args.output, args.quality)
    except (RuntimeError, ValueError) as exc:
        print(f"[!] {exc}", file=sys.stderr)
        return 1
    print(f"[+] MP3 guardado en: {result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())