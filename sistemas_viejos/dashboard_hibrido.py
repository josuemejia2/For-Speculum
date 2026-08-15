import streamlit as st
import pandas as pd

# -----------------------------
# Título
# -----------------------------
st.title("💡 Dashboard Híbrido Sistema Universal")

# -----------------------------
# Cargar CSV con datos de velas
# -----------------------------
CSV_FILE = "datos_ejemplo.csv"
df = pd.read_csv(CSV_FILE)

# Asegurarse de que existan columnas necesarias
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
# Columnas simples: Tendencia, Momento, Señal
# -----------------------------
df["tendencia"] = df["EMA3"]
df["momento"] = df["EMA9"]
df["senal"] = df["MACD"]
df["mensaje"] = df["tipo_vela"].apply(
    lambda x: "🔥 Entrada" if "Entrada" in x else "❄️ Salida" if "Salida" in x else "⚪ Sin señal"
)

# -----------------------------
# Panel lateral con selectores
# -----------------------------
st.sidebar.header("Filtros y Controles")
symbol = st.sidebar.selectbox("Símbolo", ["BTCUSD", "ETHUSD", "LTCUSD"])
interval = st.sidebar.selectbox("Intervalo (min)", ["5", "15", "60", "240", "1440"])
st.sidebar.button("Actualizar")

# -----------------------------
# Mostrar tabla de velas
# -----------------------------
st.subheader("📊 Tabla de Velas Interpretadas")
st.dataframe(df[["timestamp","tipo_vela","tendencia","momento","senal","close","mensaje"]])

# -----------------------------
# Gráfico embebido GoCharting
# -----------------------------
st.subheader("📈 Gráfico Interactivo GoCharting")
url = f"https://www.gocharting.com/chart?symbol={symbol}&interval={interval}"
st.components.v1.iframe(url, height=600, scrolling=True)