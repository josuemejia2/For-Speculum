from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from danzariel_quero.core.config import settings
from danzariel_quero.core.security import require_token
from danzariel_quero.services.files import (
    create_or_update_markdown,
    dashboard_summary,
    ensure_workspace,
    list_area_files,
    read_markdown,
    resolve_existing_file,
    save_upload,
    search_files,
)
from quero.brain.analyzer import analyze_path, analyze_upload_metadata
from quero.brain.events import next_event_id
from quero.brain.memory import AnalysisMemory, DecisionMemory

app = FastAPI(title="DANZARIEL-QUERO", version="0.1.0")

STATIC_DIR = Path(__file__).resolve().parents[1] / "web" / "static"
XMB_DIR = Path(__file__).resolve().parents[2] / "xmb_desktop_ui"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/PS3", StaticFiles(directory=XMB_DIR, html=True), name="ps3")


@app.on_event("startup")
def startup() -> None:
    ensure_workspace()


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/lab")
def lab() -> FileResponse:
    return FileResponse(STATIC_DIR / "lab.html")


@app.get("/ps3")
def ps3_lowercase() -> RedirectResponse:
    return RedirectResponse(url="/PS3/")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "name": "DANZARIEL-QUERO"}


@app.get("/api/market/btc")
def market_btc(symbol: str = "BTC-USD") -> dict[str, object]:
    safe_symbol = "".join(ch for ch in symbol.upper() if ch.isalnum() or ch == "-")[:20] or "BTC-USD"
    url = f"https://api.exchange.coinbase.com/products/{quote(safe_symbol, safe='')}/candles?granularity=3600"
    request = Request(url, headers={"User-Agent": "DANZARIEL-QUERO local lab"})

    try:
        with urlopen(request, timeout=7) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (OSError, ValueError) as exc:
        raise HTTPException(status_code=502, detail=f"No pude leer API de mercado: {exc}") from exc

    if not isinstance(payload, list):
        raise HTTPException(status_code=502, detail="Respuesta de mercado invalida")

    points: list[dict[str, float | int]] = []
    for row in payload:
        if not isinstance(row, list) or len(row) < 5:
            continue
        try:
            timestamp, low, high, open_, close = row[:5]
            points.append(
                {
                    "time": int(timestamp),
                    "open": float(open_),
                    "high": float(high),
                    "low": float(low),
                    "close": float(close),
                }
            )
        except (TypeError, ValueError):
            continue

    points.sort(key=lambda point: point["time"])
    if len(points) < 40:
        raise HTTPException(status_code=502, detail="La API devolvio pocos puntos")

    return {"symbol": safe_symbol, "source": "coinbase", "points": points[-170:]}


@app.get("/api/areas", dependencies=[Depends(require_token)])
def areas() -> dict[str, list[str]]:
    return {"areas": settings.areas}


@app.get("/api/files", dependencies=[Depends(require_token)])
def files(area: str = "knowledge") -> dict[str, object]:
    return {"area": area, "files": list_area_files(area)}


@app.get("/api/dashboard", dependencies=[Depends(require_token)])
def dashboard() -> dict[str, object]:
    return dashboard_summary()


@app.get("/api/search", dependencies=[Depends(require_token)])
def search(q: str = "") -> dict[str, object]:
    return {"query": q, "results": search_files(q)}


@app.get("/api/files/download", dependencies=[Depends(require_token)])
def download_file(area: str, path: str) -> FileResponse:
    target = resolve_existing_file(area, path)
    return FileResponse(target, filename=target.name)


@app.post("/api/upload", dependencies=[Depends(require_token)])
async def upload_file(area: str = Form("documentos"), file: UploadFile = File(...)) -> dict[str, str]:
    saved = save_upload(area, file)
    return {"status": "saved", "path": saved}


@app.post("/api/analyze", dependencies=[Depends(require_token)])
async def analyze_file(
    area: str = Form("inbox"),
    path: str = Form(""),
    file: UploadFile | None = File(default=None),
) -> dict[str, object]:
    event_id = next_event_id(settings.data_dir / "bitacora" / "event_counter.txt")

    if file is not None:
        content = await file.read()
        sample_text = ""
        if (file.content_type or "").startswith("text/") or file.filename.lower().endswith((".md", ".txt", ".json", ".csv")):
            sample_text = content[:4000].decode("utf-8", errors="replace")
        analysis = analyze_upload_metadata(
            filename=file.filename or "archivo",
            mime_type=file.content_type or "",
            size=len(content),
            sample_text=sample_text,
            event_id=event_id,
        )
        payload = analysis.to_dict()
        AnalysisMemory(settings.data_dir / "bitacora" / "analisis.jsonl").record(payload)
        return payload

    if not path:
        raise HTTPException(status_code=400, detail="Envia un archivo o path en inbox")

    target = resolve_existing_file(area, path)
    payload = analyze_path(target, event_id=event_id).to_dict()
    AnalysisMemory(settings.data_dir / "bitacora" / "analisis.jsonl").record(payload)
    return payload


@app.post("/api/decisions", dependencies=[Depends(require_token)])
def record_decision(
    analysis_id: str = Form(""),
    archivo: str = Form(...),
    decision_usuario: str = Form(...),
    categoria: str = Form(""),
    carpeta: str = Form(""),
    confianza: str = Form(""),
    explicacion: str = Form(""),
) -> dict[str, object]:
    event_id = next_event_id(settings.data_dir / "bitacora" / "event_counter.txt")
    memory = DecisionMemory(settings.data_dir / "bitacora" / "decisiones.jsonl")
    entry = memory.record(
        {
            "id": event_id,
            "analysis_id": analysis_id,
            "archivo": archivo,
            "decision_usuario": decision_usuario,
            "categoria": categoria,
            "carpeta": carpeta,
            "confianza": confianza,
            "explicacion": explicacion,
        }
    )
    return {"status": "recorded", "decision": entry}


@app.get("/api/decisions", dependencies=[Depends(require_token)])
def recent_decisions(limit: int = 50) -> dict[str, object]:
    memory = DecisionMemory(settings.data_dir / "bitacora" / "decisiones.jsonl")
    return {"decisions": memory.list_recent(limit=limit)}


@app.get("/api/docs", dependencies=[Depends(require_token)])
def get_doc(area: str = "knowledge", path: str = "") -> dict[str, str]:
    if not path:
        raise HTTPException(status_code=400, detail="path es requerido")
    return {"area": area, "path": path, "content": read_markdown(area, path)}


@app.post("/api/docs", dependencies=[Depends(require_token)])
def save_doc(area: str = Form("knowledge"), path: str = Form(...), content: str = Form("")) -> dict[str, str]:
    saved = create_or_update_markdown(area, path, content)
    return {"status": "saved", "path": saved}
