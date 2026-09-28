from __future__ import annotations

import mimetypes
from dataclasses import asdict, dataclass
from pathlib import Path

from quero.brain.classifier import RuleBasedClassifier


@dataclass(frozen=True)
class FileAnalysis:
    id: str
    archivo: str
    accion: str
    tipo: str
    extension: str
    tamano_bytes: int
    categoria_sugerida: str
    carpeta_sugerida: str
    confianza: int
    explicacion: str
    senales: list[str]
    texto_extraido: str
    requiere_aprobacion: bool = True

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


TEXT_EXTENSIONS = {".md", ".txt", ".json", ".csv", ".log"}


def analyze_path(path: Path, event_id: str = "") -> FileAnalysis:
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"Archivo no encontrado: {path}")

    mime_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    suffix = path.suffix.lower()
    extracted = extract_text(path)
    classification = RuleBasedClassifier().predict(path.name, mime_type, extracted)
    explanation = " ".join(classification.reasons) or "Clasificacion generada por reglas basicas."

    return FileAnalysis(
        id=event_id,
        archivo=path.name,
        accion="analyze",
        tipo=mime_type,
        extension=suffix or "",
        tamano_bytes=path.stat().st_size,
        categoria_sugerida=classification.category,
        carpeta_sugerida=classification.folder,
        confianza=classification.confidence,
        explicacion=explanation,
        senales=classification.signals,
        texto_extraido=extracted[:1000],
    )


def analyze_upload_metadata(
    filename: str,
    mime_type: str = "",
    size: int = 0,
    sample_text: str = "",
    event_id: str = "",
) -> FileAnalysis:
    guessed_mime = mime_type or mimetypes.guess_type(filename)[0] or "application/octet-stream"
    suffix = Path(filename).suffix.lower()
    classification = RuleBasedClassifier().predict(filename, guessed_mime, sample_text)
    explanation = " ".join(classification.reasons) or "Clasificacion generada por reglas basicas."

    return FileAnalysis(
        id=event_id,
        archivo=filename,
        accion="analyze",
        tipo=guessed_mime,
        extension=suffix or "",
        tamano_bytes=size,
        categoria_sugerida=classification.category,
        carpeta_sugerida=classification.folder,
        confianza=classification.confidence,
        explicacion=explanation,
        senales=classification.signals,
        texto_extraido=sample_text[:1000],
    )


def extract_text(path: Path, max_chars: int = 4000) -> str:
    if path.suffix.lower() not in TEXT_EXTENSIONS:
        return ""

    try:
        return path.read_text(encoding="utf-8", errors="replace")[:max_chars]
    except OSError:
        return ""
