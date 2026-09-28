from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


class JsonlMemory:
    def __init__(self, log_path: Path):
        self.log_path = log_path

    def ensure(self) -> None:
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.log_path.exists():
            self.log_path.touch()

    def append(self, entry: dict[str, Any]) -> dict[str, Any]:
        self.ensure()
        with self.log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return entry

    def list_recent(self, limit: int = 50) -> list[dict[str, Any]]:
        self.ensure()
        lines = self.log_path.read_text(encoding="utf-8", errors="replace").splitlines()
        recent = []
        for line in lines[-limit:]:
            try:
                recent.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return recent


class AnalysisMemory(JsonlMemory):
    def record(self, analysis: dict[str, Any]) -> dict[str, Any]:
        entry = {
            "fecha": datetime.now().isoformat(timespec="seconds"),
            "id": analysis.get("id", ""),
            "archivo": analysis.get("archivo", ""),
            "accion": "analyze",
            "tipo": analysis.get("tipo", ""),
            "senales": analysis.get("senales", []),
            "clasificacion_propuesta": analysis.get("categoria_sugerida", ""),
            "carpeta_sugerida": analysis.get("carpeta_sugerida", ""),
            "confianza": analysis.get("confianza", 0),
            "explicacion": analysis.get("explicacion", ""),
        }
        return self.append(entry)


class DecisionMemory(JsonlMemory):
    def record(self, decision: dict[str, Any]) -> dict[str, Any]:
        entry = {
            "fecha": datetime.now().isoformat(timespec="seconds"),
            "id": decision.get("id", ""),
            "analysis_id": decision.get("analysis_id", ""),
            "archivo": decision.get("archivo", ""),
            "accion": "decision",
            "decision_usuario": decision.get("decision_usuario", "pendiente"),
            "categoria": decision.get("categoria", ""),
            "carpeta": decision.get("carpeta", ""),
            "confianza": decision.get("confianza", ""),
            "explicacion": decision.get("explicacion", ""),
        }
        return self.append(entry)
