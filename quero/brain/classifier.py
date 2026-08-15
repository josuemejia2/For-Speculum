from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Classification:
    category: str
    folder: str
    confidence: int
    reasons: list[str]
    signals: list[str]


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".heic"}
AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".flac", ".aac", ".ogg"}
DOC_EXTENSIONS = {".md", ".txt", ".pdf", ".doc", ".docx", ".rtf"}
DATA_EXTENSIONS = {".csv", ".json", ".xlsx", ".xls"}

KEYWORDS = {
    "trading": {
        "bitcoin",
        "btc",
        "eth",
        "crypto",
        "grafico",
        "chart",
        "vela",
        "velas",
        "trade",
        "trading",
        "entrada",
        "salida",
        "precio",
        "mercado",
    },
    "investigacion": {
        "investigacion",
        "research",
        "estudio",
        "paper",
        "fuente",
        "hipotesis",
        "analisis",
    },
    "memoria": {
        "memoria",
        "bitacora",
        "diario",
        "historial",
        "decision",
        "reflexion",
    },
    "knowledge": {
        "conocimiento",
        "knowledge",
        "quero",
        "danzariel",
        "manual",
        "protocolo",
        "paradigma",
    },
}


class RuleBasedClassifier:
    def predict(self, filename: str, mime_type: str = "", extracted_text: str = "") -> Classification:
        return self._predict_rules(filename, mime_type, extracted_text)

    def predict_local_model(self, filename: str, mime_type: str = "", extracted_text: str = "") -> Classification:
        raise NotImplementedError("Modelo local todavia no conectado.")

    def predict_vector_memory(self, filename: str, mime_type: str = "", extracted_text: str = "") -> Classification:
        raise NotImplementedError("Vector memory todavia no conectada.")

    def predict_llm(self, filename: str, mime_type: str = "", extracted_text: str = "") -> Classification:
        raise NotImplementedError("LLM todavia no conectado.")

    def _predict_rules(self, filename: str, mime_type: str = "", extracted_text: str = "") -> Classification:
        name = filename.lower()
        suffix = Path(filename).suffix.lower()
        haystack = f"{name}\n{mime_type.lower()}\n{extracted_text.lower()}"

        scores = {
            "knowledge": 0,
            "documentos": 0,
            "trading": 0,
            "investigacion": 0,
            "memoria": 0,
            "imagenes": 0,
            "musica": 0,
        }
        reasons: dict[str, list[str]] = {key: [] for key in scores}
        signals: dict[str, list[str]] = {key: [] for key in scores}

        if suffix in IMAGE_EXTENSIONS or mime_type.startswith("image/"):
            scores["imagenes"] += 35
            reasons["imagenes"].append("El archivo es una imagen.")
            signals["imagenes"].append("type:image")
        elif suffix in AUDIO_EXTENSIONS or mime_type.startswith("audio/"):
            scores["musica"] += 40
            reasons["musica"].append("El archivo es audio.")
            signals["musica"].append("type:audio")
        elif suffix in DOC_EXTENSIONS or mime_type.startswith("text/"):
            scores["documentos"] += 30
            reasons["documentos"].append("El archivo parece documento o texto.")
            signals["documentos"].append("type:document")
        elif suffix in DATA_EXTENSIONS:
            scores["documentos"] += 20
            reasons["documentos"].append("El archivo contiene datos estructurados.")
            signals["documentos"].append("type:data")

        for category, words in KEYWORDS.items():
            hits = sorted(word for word in words if word in haystack)
            if hits:
                points = min(45, 15 + len(hits) * 8)
                scores[category] += points
                reasons[category].append(f"Coincidencias: {', '.join(hits[:5])}.")
                signals[category].extend(f"keyword:{hit}" for hit in hits[:10])

        if scores["trading"] and scores["imagenes"]:
            scores["trading"] += 15
            reasons["trading"].append("Imagen relacionada con trading.")
            signals["trading"].append("combined:image+trading")

        category = max(scores, key=scores.get)
        raw_score = scores[category]

        if raw_score <= 0:
            category = "documentos"
            raw_score = 35
            reasons[category].append("No hubo senales fuertes; se sugiere documentos como destino neutral.")
            signals[category].append("fallback:neutral")

        confidence = max(0, min(100, max(35, raw_score)))
        folder = suggest_folder(category, suffix, mime_type)
        return Classification(
            category=category,
            folder=folder,
            confidence=confidence,
            reasons=reasons[category],
            signals=signals[category],
        )


def classify_file(filename: str, mime_type: str = "", extracted_text: str = "") -> Classification:
    return RuleBasedClassifier().predict(filename, mime_type, extracted_text)


def suggest_folder(category: str, suffix: str, mime_type: str = "") -> str:
    if category == "trading" and (suffix in IMAGE_EXTENSIONS or mime_type.startswith("image/")):
        return "/trading/imagenes"
    if category == "trading":
        return "/trading"
    if category == "imagenes":
        return "/imagenes"
    if category == "musica":
        return "/musica"
    if category == "investigacion":
        return "/investigacion"
    if category == "memoria":
        return "/memoria"
    if category == "knowledge":
        return "/knowledge"
    return "/documentos"
