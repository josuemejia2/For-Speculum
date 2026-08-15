import streamlit as st
import pandas as pd

# -----------------------------
# Función de interpretación de velas
# -----------------------------
def interpretar_vela(fila, simbolo="BTC-USD", timeframe="5m"):
    interpretacion = {
        "simbolo": simbolo,
        "timeframe": timeframe,
        "tipo_vela": fila.get("tipo_vela", "ninguna"),
        "intencion": fila.get("EMA_3", 0),
        "reaccion": fila.get("EMA_9", 0),
        "decision": fila.get("MACD", 0)
    }

    if interpretacion["tipo_vela"] == "Entrada 🔥":
        interpretacion["mensaje"] = "🔥 Vela de entrada confirmada"
    elif interpretacion["tipo_vela"] == "Salida ❄️":
        interpretacion["mensaje"] = "❄️ Vela de salida detectada"
    else:
        interpretacion["mensaje"] = "⚪ Sin señal"

    return interpretacion

# -----------------------------
# Cargar datos
# -----------------------------
CSV_FILE = "datos_ejemplo.csv"
df = pd.read_csv(CSV_FILE)

# Asegurarse de que existan EMAs y MACD
for col in ["EMA3", "EMA9", "EMA20", "EMA_3", "EMA_9", "EMA_20", "MACD"]:
    if col not in df.columns:
        df[col] = 0

# -----------------------------
# Detectar tipo de vela
# -----------------------------
tipos = []
for i in range(1, len(df)):
    anterior = df.iloc[i-1]
    actual = df.iloc[i]
    if (actual["open"] > anterior["open"] and
        actual["high"] > anterior["high"] and
        actual["low"] > anterior["low"] and
        actual["close"] > actual.get("EMA_3", actual.get("EMA3", 0))):
        tipo = "Entrada 🔥"
    elif (actual["open"] < anterior["open"] and
          actual["high"] < anterior["high"] and
          actual["low"] < anterior["low"]):
        tipo = "Salida ❄️"
    else:
        tipo = "Ninguna ⚪"
    tipos.append(tipo)

df = df.iloc[1:]
df["tipo_vela"] = tipos

# -----------------------------
# Crear columnas intencion/reaccion/decision
# -----------------------------
df["intencion"] = df["EMA_3"] if "EMA_3" in df.columns else df["EMA3"]
df["reaccion"] = df["EMA_9"] if "EMA_9" in df.columns else df["EMA9"]
df["decision"] = df["MACD"] if "MACD" in df.columns else 0

# -----------------------------
# Interpretar velas y agregar mensaje
# -----------------------------
df["mensaje"] = df.apply(lambda row: interpretar_vela(row)["mensaje"], axis=1)

# -----------------------------
# Panel lateral filtros
# -----------------------------
st.sidebar.header("Filtros")
symbol = st.sidebar.selectbox("Símbolo", ["BTC-USD"])
timeframe = st.sidebar.selectbox("Timeframe", ["5m", "15m", "1h"])
st.sidebar.button("Actualizar")

# -----------------------------
# Mostrar tabla principal
# -----------------------------
st.title("💡 Panel de Control Sistema Universal")
st.subheader(f"Velas recientes - {symbol} ({timeframe})")
st.dataframe(df[["timestamp", "tipo_vela", "intencion", "reaccion", "decision", "close", "mensaje"]])