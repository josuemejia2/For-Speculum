from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

from fastapi import HTTPException, UploadFile

from danzariel_quero.core.config import settings


def ensure_workspace() -> None:
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    for area in settings.areas:
        (settings.data_dir / area).mkdir(parents=True, exist_ok=True)
    (settings.data_dir / "trading" / "imagenes").mkdir(parents=True, exist_ok=True)


def _safe_area(area: str) -> Path:
    if area not in settings.areas:
        raise HTTPException(status_code=400, detail=f"Area no permitida: {area}")
    return settings.data_dir / area


def _safe_relative_path(raw_path: str, default_suffix: str = "") -> Path:
    cleaned = raw_path.strip().replace("\\", "/")
    if not cleaned:
        raise HTTPException(status_code=400, detail="Ruta vacia")

    parts = [p for p in cleaned.split("/") if p and p not in (".", "..")]
    if not parts:
        raise HTTPException(status_code=400, detail="Ruta invalida")

    safe_parts = [re.sub(r"[^A-Za-z0-9_. -]+", "_", part).strip() for part in parts]
    safe_parts = [part or "archivo" for part in safe_parts]
    path = Path(*safe_parts)

    if default_suffix and not path.suffix:
        path = path.with_suffix(default_suffix)

    return path


def _resolve(area: str, raw_path: str, default_suffix: str = "") -> Path:
    base = _safe_area(area).resolve()
    relative = _safe_relative_path(raw_path, default_suffix)
    target = (base / relative).resolve()

    if base not in target.parents and target != base:
        raise HTTPException(status_code=400, detail="Ruta fuera del area permitida")

    return target


def _log_change(action: str, area: str, path: str) -> None:
    ensure_workspace()
    log_path = settings.data_dir / "memoria" / "change_log.jsonl"
    entry = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "action": action,
        "area": area,
        "path": path,
    }
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def list_area_files(area: str) -> list[dict[str, object]]:
    ensure_workspace()
    base = _safe_area(area)
    files: list[dict[str, object]] = []

    for path in sorted(base.rglob("*")):
        if path.is_file():
            files.append(
                {
                    "path": path.relative_to(base).as_posix(),
                    "size": path.stat().st_size,
                    "modified": datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds"),
                }
            )

    return files


def dashboard_summary() -> dict[str, object]:
    ensure_workspace()
    summary: dict[str, object] = {
        "version": "v0.4-mobile-files",
        "total_size": 0,
        "areas": {},
        "recent": [],
    }
    recent: list[dict[str, object]] = []

    for area in settings.areas:
        base = _safe_area(area)
        count = 0
        size = 0
        for path in base.rglob("*"):
            if not path.is_file():
                continue
            stat = path.stat()
            count += 1
            size += stat.st_size
            recent.append(
                {
                    "area": area,
                    "path": path.relative_to(base).as_posix(),
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds"),
                }
            )
        summary["areas"][area] = {"count": count, "size": size}
        summary["total_size"] = int(summary["total_size"]) + size

    summary["recent"] = sorted(recent, key=lambda item: str(item["modified"]), reverse=True)[:20]
    return summary


def search_files(query: str) -> list[dict[str, object]]:
    ensure_workspace()
    needle = query.strip().lower()
    if not needle:
        return []

    results: list[dict[str, object]] = []
    for area in settings.areas:
        base = _safe_area(area)
        for path in base.rglob("*"):
            if not path.is_file():
                continue
            relative = path.relative_to(base).as_posix()
            haystack = relative.lower()
            text_hit = False
            if path.suffix.lower() in (".md", ".txt", ".json", ".csv", ".log"):
                text_hit = needle in path.read_text(encoding="utf-8", errors="replace").lower()
            if needle in haystack or text_hit:
                stat = path.stat()
                results.append(
                    {
                        "area": area,
                        "path": relative,
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds"),
                        "match": "content" if text_hit else "name",
                    }
                )

    return sorted(results, key=lambda item: str(item["modified"]), reverse=True)[:50]


def save_upload(area: str, upload: UploadFile) -> str:
    ensure_workspace()
    filename = upload.filename or "archivo"
    target = _resolve(area, filename)
    target.parent.mkdir(parents=True, exist_ok=True)

    with target.open("wb") as f:
        while chunk := upload.file.read(1024 * 1024):
            f.write(chunk)

    relative = target.relative_to(_safe_area(area)).as_posix()
    _log_change("upload", area, relative)
    return relative


def read_markdown(area: str, raw_path: str) -> str:
    target = _resolve(area, raw_path, ".md")
    if target.suffix.lower() not in (".md", ".txt"):
        raise HTTPException(status_code=400, detail="Solo se pueden leer documentos .md o .txt")
    if not target.exists():
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    return target.read_text(encoding="utf-8", errors="replace")


def create_or_update_markdown(area: str, raw_path: str, content: str) -> str:
    ensure_workspace()
    target = _resolve(area, raw_path, ".md")
    if target.suffix.lower() not in (".md", ".txt"):
        raise HTTPException(status_code=400, detail="Solo se pueden guardar documentos .md o .txt")

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8", newline="\n")
    relative = target.relative_to(_safe_area(area)).as_posix()
    _log_change("write_doc", area, relative)
    return relative


def resolve_existing_file(area: str, raw_path: str) -> Path:
    target = _resolve(area, raw_path)
    if not target.exists() or not target.is_file():
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    return target
