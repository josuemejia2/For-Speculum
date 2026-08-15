import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.title("💡 Panel Avanzado Sistema Universal")

# -----------------------------
# Cargar CSV
# -----------------------------
CSV_FILE = "datos_ejemplo.csv"
df = pd.read_csv(CSV_FILE)

# -----------------------------
# Asegurarse de que existan columnas necesarias
# -----------------------------
for col in ["EMA3","EMA9","EMA20","MACD"]:
    if col not in df.columns:
        df[col] = 0

# -----------------------------
# Detectar tipo de vela
# -----------------------------
tipos = []
for i in range(1, len(df)):
    anterior = df.iloc[i-1]
    actual = df.iloc[i]
    if actual["close"] > anterior["close"]:
        tipo = "Entrada 🔥"
    elif actual["close"] < anterior["close"]:
        tipo = "Salida ❄️"
    else:
        tipo = "Ninguna ⚪"
    tipos.append(tipo)

df = df.iloc[1:]
df["tipo_vela"] = tipos

# -----------------------------
# Crear columnas intencion/reaccion/decision
# -----------------------------
df["intencion"] = df["EMA3"]
df["reaccion"] = df["EMA9"]
df["decision"] = df["MACD"]
df["mensaje"] = df["tipo_vela"].apply(lambda x: "🔥 Entrada" if "Entrada" in x else "❄️ Salida" if "Salida" in x else "⚪ Sin señal")

# -----------------------------
# Gráfica Plotly de velas
# -----------------------------
fig = go.Figure(data=[go.Candlestick(
    x=df["timestamp"],
    open=df["open"],
    high=df["high"],
    low=df["low"],
    close=df["close"]
)])

# EMAs
fig.add_trace(go.Scatter(x=df["timestamp"], y=df["EMA3"], mode="lines", name="EMA3", line=dict(color="blue")))
fig.add_trace(go.Scatter(x=df["timestamp"], y=df["EMA9"], mode="lines", name="EMA9", line=dict(color="orange")))
fig.add_trace(go.Scatter(x=df["timestamp"], y=df["EMA20"], mode="lines", name="EMA20", line=dict(color="green")))

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Mostrar tabla
# -----------------------------
st.subheader("Tabla de Velas Interpretadas")
st.dataframe(df[["timestamp","tipo_vela","intencion","reaccion","decision","close","mensaje"]])