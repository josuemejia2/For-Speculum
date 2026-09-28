import json
import re
from pathlib import Path
from typing import Any, List, Tuple

import pandas as pd


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def doc_stats(path: Path) -> dict:
    if not path.exists():
        return {"exists": False, "lines": 0, "chars": 0, "headings": 0}
    text = read_text(path)
    lines = text.splitlines()
    return {
        "exists": True,
        "lines": len(lines),
        "chars": len(text),
        "headings": sum(1 for line in lines if line.strip().startswith("#")),
    }


def _safe_name(value: str) -> str:
    clean = re.sub(r"[^A-Za-z0-9_.-]+", "_", value.strip())
    return clean.strip("_") or "documento"


def backup_document(path: Path, target_dir: Path) -> Path:
    stamp = pd.Timestamp.now().strftime("%Y%m%d__%H%M%S")
    target_dir.mkdir(parents=True, exist_ok=True)
    suffix = path.suffix or ".txt"
    target = target_dir / f"{_safe_name(path.stem)}__{stamp}{suffix}"
    target.write_text(read_text(path), encoding="utf-8")
    return target


def split_sections(md_text: str) -> List[Tuple[str, str]]:
    lines = md_text.splitlines()
    sections: List[Tuple[str, str]] = []
    current_title = "Resumen"
    current_lines: List[str] = []

    for line in lines:
        if re.match(r"^\s*#{1,4}\s+", line):
            if current_lines:
                sections.append((current_title, "\n".join(current_lines).strip()))
                current_lines = []
            current_title = re.sub(r"^\s*#{1,4}\s+", "", line).strip()
        else:
            current_lines.append(line)

    if current_lines:
        sections.append((current_title, "\n".join(current_lines).strip()))

    return [(title, body) for title, body in sections if title or body]


class DocLayer:
    def __init__(self, index: int, title: str, start: int, end: int, level: int, kind: str):
        self.index = index
        self.title = title
        self.start = start
        self.end = end
        self.level = level
        self.kind = kind


def split_layers(text: str) -> List[DocLayer]:
    lines = text.splitlines()
    heading_hits: list[tuple[int, int, str]] = []

    for idx, line in enumerate(lines):
        match = re.match(r"^(#{1,4})\s+(.+?)\s*$", line)
        if match:
            heading_hits.append((idx, len(match.group(1)), match.group(2).strip()))

    if heading_hits:
        layers: list[DocLayer] = []
        for layer_index, (start, level, title) in enumerate(heading_hits):
            end = heading_hits[layer_index + 1][0] if layer_index + 1 < len(heading_hits) else len(lines)
            layers.append(DocLayer(layer_index, title, start, end, level, "heading"))
        return layers

    tree_hits: list[tuple[int, str]] = []
    for idx, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith(("\u251c\u2500\u2500", "\u2514\u2500\u2500")):
            title = stripped[3:].strip() or "Rama"
            tree_hits.append((idx, title))

    if tree_hits:
        layers = []
        if tree_hits[0][0] > 0:
            layers.append(DocLayer(0, "Raiz", 0, tree_hits[0][0], 0, "root"))
        for hit_index, (start, title) in enumerate(tree_hits):
            end = tree_hits[hit_index + 1][0] if hit_index + 1 < len(tree_hits) else len(lines)
            layers.append(DocLayer(len(layers), title, start, end, 1, "tree"))
        return layers

    separator_hits = [
        idx
        for idx, line in enumerate(lines)
        if line.strip() and len(line.strip()) <= 8 and not any(ch.isalnum() for ch in line.strip())
    ]
    boundaries = [-1] + separator_hits + [len(lines)]
    layers = []

    for idx in range(len(boundaries) - 1):
        start = boundaries[idx] + 1
        end = boundaries[idx + 1]
        if start >= end:
            continue
        block = lines[start:end]
        title = next((line.strip() for line in block if line.strip()), "Capa sin titulo")
        if len(title) > 76:
            title = title[:73] + "..."
        layers.append(DocLayer(len(layers), title, start, end, 0, "block"))
    return layers


def layer_text(text: str, layer: DocLayer) -> str:
    lines = text.splitlines()
    return "\n".join(lines[layer.start : layer.end])


def replace_layer(text: str, layer: DocLayer, new_layer_text: str) -> str:
    lines = text.splitlines()
    replacement = new_layer_text.splitlines()
    output = lines[: layer.start] + replacement + lines[layer.end :]
    return "\n".join(output).rstrip() + "\n"


def load_raw_df(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=["timestamp", "open", "high", "low", "close"])
    df = pd.read_csv(path)
    if df.empty:
        return pd.DataFrame(columns=["timestamp", "open", "high", "low", "close"])
    return df


def load_json_list(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []

    raw = path.read_text(encoding="utf-8").strip()
    if not raw:
        return []

    try:
        parsed = json.loads(raw)
        return parsed if isinstance(parsed, list) else []
    except json.JSONDecodeError:
        repaired = raw
        while repaired.count("]") > repaired.count("["):
            repaired = repaired[:-1]
        try:
            parsed = json.loads(repaired)
            return parsed if isinstance(parsed, list) else []
        except json.JSONDecodeError:
            return []


def append_json_entry(path: Path, entry: dict[str, Any]) -> None:
    data = load_json_list(path)
    data.append(entry)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def append_candle(open_v: float, high_v: float, low_v: float, close_v: float, path: Path) -> None:
    df = load_raw_df(path)
    row = {
        "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
        "open": float(open_v),
        "high": float(high_v),
        "low": float(low_v),
        "close": float(close_v),
    }

    if df.empty:
        out = pd.DataFrame([row])
    else:
        out = df.copy()
        for col in out.columns:
            if col not in row:
                row[col] = pd.NA
        for col in row:
            if col not in out.columns:
                out[col] = pd.NA
        out = pd.concat([out, pd.DataFrame([row], columns=out.columns)], ignore_index=True)

    out.to_csv(path, index=False)


def prepare_df_for_table(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy()
    normalized_columns = [c.strip().lower() for c in df.columns]
    if len(set(normalized_columns)) != len(normalized_columns):
        unique_columns: list[str] = []
        seen: dict[str, int] = {}
        for col in normalized_columns:
            if col not in seen:
                seen[col] = 0
                unique_columns.append(col)
            else:
                seen[col] += 1
                unique_columns.append(f"{col}_{seen[col]}")
        df.columns = unique_columns
    else:
        df.columns = normalized_columns

    for col in ("open", "high", "low", "close"):
        if col not in df.columns:
            df[col] = pd.NA
        df[col] = pd.to_numeric(df[col], errors="coerce")
    if "timestamp" not in df.columns:
        df["timestamp"] = pd.Timestamp.now()

    timestamp_series = df.loc[:, "timestamp"]
    if isinstance(timestamp_series, pd.DataFrame):
        timestamp_series = timestamp_series.iloc[:, 0]
    df["timestamp"] = pd.to_datetime(timestamp_series, errors="coerce")
    df = df.dropna(subset=["open", "high", "low", "close"]).reset_index(drop=True)
    if df.empty:
        return df

    df["tipo_vela"] = df.apply(lambda r: "Entrada" if r["close"] > r["open"] else "Salida", axis=1)
    return df
