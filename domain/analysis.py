from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

CSV_PATH = Path("datos_ejemplo.csv")


@dataclass
class ResultadoAnalisis:
    symbol: str
    timeframe: str
    timestamp: str
    signal: str
    confidence: int
    tipo_vela: str
    reason: str
    detalles: dict[str, Any]


def cargar_velas(csv_path: Path = CSV_PATH) -> pd.DataFrame:
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV no encontrado: {csv_path}")

    df = pd.read_csv(csv_path)
    if df.empty:
        raise ValueError("El CSV no tiene filas para analizar.")

    df.columns = [c.strip().lower() for c in df.columns]

    required = {"open", "high", "low", "close"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Faltan columnas requeridas en CSV: {sorted(missing)}")

    for col in ("open", "high", "low", "close"):
        df[col] = pd.to_numeric(df[col], errors="coerce")

    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df = df.sort_values("timestamp")

    df = df.dropna(subset=["open", "high", "low", "close"]).reset_index(drop=True)
    if len(df) < 2:
        raise ValueError("Se requieren al menos 2 velas para evaluar entrada/salida.")

    return df


def calcular_indicadores(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    for periodo in (3, 9, 20, 50, 200):
        out[f"EMA_{periodo}"] = out["close"].ewm(span=periodo, adjust=False).mean()

    ema_fast = out["close"].ewm(span=12, adjust=False).mean()
    ema_slow = out["close"].ewm(span=26, adjust=False).mean()
    out["MACD_LINE"] = ema_fast - ema_slow
    out["MACD_SIGNAL"] = out["MACD_LINE"].ewm(span=9, adjust=False).mean()
    out["MACD_HIST"] = out["MACD_LINE"] - out["MACD_SIGNAL"]

    bb_mid = out["close"].rolling(window=20, min_periods=1).mean()
    bb_std = out["close"].rolling(window=20, min_periods=1).std(ddof=0).fillna(0.0)
    out["BB_MID"] = bb_mid
    out["BB_UPPER"] = bb_mid + (2.0 * bb_std)
    out["BB_LOWER"] = bb_mid - (2.0 * bb_std)
    out["BB_WIDTH"] = out["BB_UPPER"] - out["BB_LOWER"]

    out["PSAR"] = _calcular_psar(out["high"], out["low"], out["close"])
    out["PSAR_BULL"] = out["close"] > out["PSAR"]

    return out


def _calcular_psar(
    highs: pd.Series,
    lows: pd.Series,
    closes: pd.Series,
    step: float = 0.02,
    max_step: float = 0.2,
) -> pd.Series:
    n = len(closes)
    if n == 0:
        return pd.Series(dtype=float)

    high = highs.astype(float).tolist()
    low = lows.astype(float).tolist()
    close = closes.astype(float).tolist()

    psar = [low[0]]
    bull = True if n < 2 else close[1] >= close[0]
    ep = high[0] if bull else low[0]
    af = step

    for i in range(1, n):
        prev_psar = psar[-1]
        sar = prev_psar + af * (ep - prev_psar)

        if bull:
            if i >= 2:
                sar = min(sar, low[i - 1], low[i - 2])
            else:
                sar = min(sar, low[i - 1])

            if low[i] < sar:
                bull = False
                sar = ep
                ep = low[i]
                af = step
            else:
                if high[i] > ep:
                    ep = high[i]
                    af = min(af + step, max_step)
        else:
            if i >= 2:
                sar = max(sar, high[i - 1], high[i - 2])
            else:
                sar = max(sar, high[i - 1])

            if high[i] > sar:
                bull = True
                sar = ep
                ep = high[i]
                af = step
            else:
                if low[i] < ep:
                    ep = low[i]
                    af = min(af + step, max_step)

        psar.append(sar)

    return pd.Series(psar, index=closes.index, dtype=float)


def _pendiente(series: pd.Series, pasos: int = 3) -> float:
    tail = series.tail(max(2, pasos)).astype(float)
    if len(tail) < 2:
        return 0.0
    return float(tail.iloc[-1] - tail.iloc[0])


def _clasificar_vela(prev: pd.Series, cur: pd.Series) -> tuple[str, bool]:
    entrada_base = (
        cur["open"] > prev["open"]
        and cur["high"] > prev["high"]
        and cur["low"] > prev["low"]
    )
    salida_base = (
        cur["open"] < prev["open"]
        and cur["high"] < prev["high"]
        and cur["low"] < prev["low"]
    )

    ema3_ok = cur["close"] > cur["EMA_3"]

    if entrada_base and ema3_ok:
        return "Entrada", True
    if entrada_base and not ema3_ok:
        return "FalsaPositivaEMA3", False
    if salida_base:
        return "Salida", True
    return "Neutral", False


def _etapas_vela(cur: pd.Series) -> dict[str, float]:
    cuerpo = abs(cur["close"] - cur["open"])
    intencion = max(cur["high"] - max(cur["open"], cur["close"]), 0.0)
    reaccion = max(min(cur["open"], cur["close"]) - cur["low"], 0.0)
    return {
        "intencion": float(intencion + (0.0 if cuerpo else 0.0)),
        "reaccion": float(reaccion),
        "decision": float(cur["close"]),
    }


def _regla_capitan(df: pd.DataFrame) -> str:
    ventana = df.tail(20)
    maximo = float(ventana["high"].max())
    minimo = float(ventana["low"].min())
    cierre = float(ventana["close"].iloc[-1])
    rango = max(maximo - minimo, 1e-9)
    posicion = (cierre - minimo) / rango
    if posicion >= 0.7:
        return "cerca_maximo_busca_maximo"
    if posicion <= 0.3:
        return "cerca_minimo_busca_minimo"
    return "zona_media_sin_ventaja"


def _regla_jesus(prev: pd.Series, cur: pd.Series) -> dict[str, bool]:
    alcista = bool(cur["close"] > cur["EMA_20"] and cur["MACD_HIST"] > 0 and prev["MACD_HIST"] <= 0)
    bajista = bool(cur["close"] < cur["EMA_20"] and cur["MACD_HIST"] < 0 and prev["MACD_HIST"] >= 0)
    return {"alcista": alcista, "bajista": bajista}


def _regla_trujillo(cur: pd.Series) -> bool:
    precio = max(abs(float(cur["close"])), 1e-9)
    dist20 = abs(float(cur["open"] - cur["EMA_20"])) / precio
    dist50 = abs(float(cur["open"] - cur["EMA_50"])) / precio
    dist200 = abs(float(cur["open"] - cur["EMA_200"])) / precio
    return bool(dist20 > 0.002 and dist50 > 0.003 and dist200 > 0.004)


def _regla_distancia(cur: pd.Series) -> dict[str, Any]:
    precio = max(abs(float(cur["close"])), 1e-9)
    dist_ema20 = abs(float(cur["close"] - cur["EMA_20"])) / precio
    fuera_bandas = bool(cur["close"] > cur["BB_UPPER"] or cur["close"] < cur["BB_LOWER"])
    estirado = bool(dist_ema20 > 0.02 or fuera_bandas)
    return {"estirado": estirado, "dist_ema20_pct": round(dist_ema20 * 100, 3), "fuera_bandas": fuera_bandas}


def _ley_trina_interna(cur: pd.Series) -> dict[str, int]:
    long_score = 0
    short_score = 0

    if cur["close"] > cur["EMA_200"]:
        long_score += 1
    elif cur["close"] < cur["EMA_200"]:
        short_score += 1

    if cur["EMA_3"] > cur["EMA_9"] > cur["EMA_20"]:
        long_score += 1
    elif cur["EMA_3"] < cur["EMA_9"] < cur["EMA_20"]:
        short_score += 1

    if cur["MACD_HIST"] > 0:
        long_score += 1
    elif cur["MACD_HIST"] < 0:
        short_score += 1

    return {"long": long_score, "short": short_score}


def analizar_mercado(
    csv_path: Path = CSV_PATH,
    symbol: str = "BTC-USD",
    timeframe: str = "5m",
) -> ResultadoAnalisis:
    df = calcular_indicadores(cargar_velas(csv_path))
    prev = df.iloc[-2]
    cur = df.iloc[-1]

    tipo_vela, entrada_valida = _clasificar_vela(prev, cur)
    triada = _etapas_vela(cur)
    capitan = _regla_capitan(df)
    jesus = _regla_jesus(prev, cur)
    trujillo = _regla_trujillo(cur)
    distancia = _regla_distancia(cur)
    trina = _ley_trina_interna(cur)

    ema200_bajista = _pendiente(df["EMA_200"]) < 0
    ema200_alcista = _pendiente(df["EMA_200"]) > 0

    long_min = bool(tipo_vela == "Entrada" and entrada_valida)
    long_conf = {
        "ema3_domina_ema9": bool(cur["EMA_3"] > cur["EMA_9"]),
        "precio_sobre_ema20": bool(cur["close"] > cur["EMA_20"]),
        "macd_positivo": bool(cur["MACD_HIST"] > 0),
        "psar_alcista": bool(cur["PSAR_BULL"]),
    }
    long_invalid = {
        "contra_ema200": bool(cur["close"] < cur["EMA_200"] and ema200_bajista),
        "distancia_invalida": distancia["estirado"],
        "comprando_en_maximo": bool(cur["close"] >= cur["high"]),
    }

    short_min = bool(tipo_vela == "Salida")
    short_conf = {
        "ema3_bajo_ema9": bool(cur["EMA_3"] < cur["EMA_9"]),
        "precio_bajo_ema20": bool(cur["close"] < cur["EMA_20"]),
        "macd_negativo": bool(cur["MACD_HIST"] < 0),
        "psar_bajista": bool(not cur["PSAR_BULL"]),
    }
    short_invalid = {
        "contra_ema200": bool(cur["close"] > cur["EMA_200"] and ema200_alcista),
        "distancia_invalida": distancia["estirado"],
        "vendiendo_en_minimo": bool(cur["close"] <= cur["low"]),
    }

    long_conf_count = sum(int(v) for v in long_conf.values())
    short_conf_count = sum(int(v) for v in short_conf.values())
    long_invalid_count = sum(int(v) for v in long_invalid.values())
    short_invalid_count = sum(int(v) for v in short_invalid.values())

    signal = "NO_TRADE"
    reason = "No cumple checklist minimo"
    confidence = 10

    if (
        long_min
        and long_conf_count >= 2
        and long_invalid_count == 0
        and trina["long"] >= 2
    ):
        signal = "LONG"
        reason = "Entrada valida + confirmaciones tecnicas + confluencia"
        confidence = min(95, 40 + long_conf_count * 12 + trina["long"] * 8)
    elif (
        short_min
        and short_conf_count >= 2
        and short_invalid_count == 0
        and trina["short"] >= 2
    ):
        signal = "SHORT"
        reason = "Salida valida + confirmaciones tecnicas + confluencia"
        confidence = min(95, 40 + short_conf_count * 12 + trina["short"] * 8)
    else:
        penalty = max(long_invalid_count, short_invalid_count) * 12
        confidence = max(5, 25 + max(long_conf_count, short_conf_count) * 8 - penalty)
        if distancia["estirado"]:
            reason = "Regla de distancia invalida la operacion"
        elif tipo_vela == "FalsaPositivaEMA3":
            reason = "Falsa positiva: no cerro sobre EMA3"
        elif trina["long"] <= 1 and trina["short"] <= 1:
            reason = "Confluencia debil (1/3)"

    timestamp = (
        cur["timestamp"].isoformat()
        if "timestamp" in cur.index and pd.notna(cur["timestamp"])
        else datetime.now().isoformat(timespec="seconds")
    )

    detalles = {
        "close": float(cur["close"]),
        "emas": {
            "EMA_3": float(cur["EMA_3"]),
            "EMA_9": float(cur["EMA_9"]),
            "EMA_20": float(cur["EMA_20"]),
            "EMA_50": float(cur["EMA_50"]),
            "EMA_200": float(cur["EMA_200"]),
        },
        "macd": {
            "line": float(cur["MACD_LINE"]),
            "signal": float(cur["MACD_SIGNAL"]),
            "hist": float(cur["MACD_HIST"]),
        },
        "bollinger": {
            "mid": float(cur["BB_MID"]),
            "upper": float(cur["BB_UPPER"]),
            "lower": float(cur["BB_LOWER"]),
        },
        "psar": float(cur["PSAR"]),
        "triada_vela": triada,
        "leyes": {
            "capitan": capitan,
            "jesus": jesus,
            "trujillo": trujillo,
            "distancia": distancia,
            "trina": trina,
        },
        "checklist_long": {
            "minimo": long_min,
            "confirmaciones": long_conf,
            "invalidaciones": long_invalid,
        },
        "checklist_short": {
            "minimo": short_min,
            "confirmaciones": short_conf,
            "invalidaciones": short_invalid,
        },
    }

    return ResultadoAnalisis(
        symbol=symbol,
        timeframe=timeframe,
        timestamp=timestamp,
        signal=signal,
        confidence=int(confidence),
        tipo_vela=tipo_vela,
        reason=reason,
        detalles=detalles,
    )
