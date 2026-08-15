from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    project_root: Path = field(default_factory=lambda: Path(__file__).resolve().parents[2])
    secret_token: str = field(default_factory=lambda: os.getenv("DQ_SECRET_TOKEN", "cambia-este-token"))
    data_dir: Path = field(
        default_factory=lambda: Path(os.getenv("DQ_DATA_DIR", Path(__file__).resolve().parents[2] / "danzariel_quero_data"))
    )
    areas: list[str] = field(
        default_factory=lambda: [
            "inbox",
            "knowledge",
            "documentos",
            "trading",
            "investigacion",
            "memoria",
            "imagenes",
            "musica",
            "backups",
            "bitacora",
        ]
    )


settings = Settings()
