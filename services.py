from datetime import datetime
from pathlib import Path
from typing import Any, List

from domain.analysis import ResultadoAnalisis, calcular_indicadores
from infra import repositories


def read_document(path: Path) -> str:
    return repositories.read_text(path)


def write_document(path: Path, text: str) -> None:
    return repositories.write_text(path, text)


def document_stats(path: Path) -> dict:
    return repositories.doc_stats(path)


def split_document_sections(md_text: str) -> List[tuple[str, str]]:
    return repositories.split_sections(md_text)


def split_document_layers(text: str) -> List[repositories.DocLayer]:
    return repositories.split_layers(text)


def load_document_layers(path: Path) -> List[repositories.DocLayer]:
    text = repositories.read_text(path)
    return repositories.split_layers(text)


def layer_text(text: str, layer: repositories.DocLayer) -> str:
    return repositories.layer_text(text, layer)


def replace_document_layer(text: str, layer: repositories.DocLayer, new_text: str) -> str:
    return repositories.replace_layer(text, layer, new_text)


def backup_document(path: Path, backup_dir: Path) -> Path:
    return repositories.backup_document(path, backup_dir)


def load_market_df(path: Path):
    return repositories.load_raw_df(path)


def add_candle(open_v: float, high_v: float, low_v: float, close_v: float, path: Path) -> None:
    return repositories.append_candle(open_v, high_v, low_v, close_v, path)


def append_json_entry(path: Path, entry: dict[str, Any]) -> None:
    return repositories.append_json_entry(path, entry)


def _to_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def save_analysis_to_bitacora(
    resultado: ResultadoAnalisis,
    bitacora_path: Path = Path("bitacora.json"),
    bitacora_dir: Path = Path("bitacoras_historicas"),
) -> list[Path]:
    triada = resultado.detalles.get("triada_vela", {})
    macd_hist = _to_float(resultado.detalles.get("macd", {}).get("hist"))
    close = _to_float(resultado.detalles.get("close"))

    tipo = "Entrada" if resultado.signal == "LONG" else "Salida" if resultado.signal == "SHORT" else "NoTrade"
    entry = {
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "tipo": tipo,
        "intencion": _to_float(triada.get("intencion")),
        "reaccion": _to_float(triada.get("reaccion")),
        "decision": macd_hist,
        "close": close,
        "senal": resultado.signal,
        "confianza": resultado.confidence,
        "motivo": resultado.reason,
        "symbol": resultado.symbol,
        "timeframe": resultado.timeframe,
    }

    month_file = bitacora_dir / f"bitacora_{datetime.now().year}_{datetime.now().month:02}.json"
    append_json_entry(bitacora_path, entry)
    append_json_entry(month_file, entry)
    return [bitacora_path, month_file]


def prepare_table_df(df):
    if df is None or df.empty:
        return df

    prepared = repositories.prepare_df_for_table(df)
    if prepared.empty:
        return prepared

    prepared = calcular_indicadores(prepared)
    prepared["tipo_vela"] = prepared.apply(lambda r: "Entrada" if r["close"] > r["open"] else "Salida", axis=1)
    return prepared
