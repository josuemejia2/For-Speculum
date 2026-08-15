import streamlit as st
import pandas as pd

# -----------------------------
# Título del Dashboard
# -----------------------------
st.title("💡 Dashboard Híbrido Sistema Universal")

# -----------------------------
# Cargar CSV con velas
# -----------------------------
CSV_FILE = "datos_ejemplo.csv"
df = pd.read_csv(CSV_FILE)

# -----------------------------
# Detectar tipo de vela y columnas simples
# -----------------------------
df["tipo_vela"] = ["Entrada 🔥" if c > o else "Salida ❄️" for c,o in zip(df["close"], df["open"])]
df["tendencia"] = df["EMA3"] if "EMA3" in df.columns else 0
df["momento"] = df["EMA9"] if "EMA9" in df.columns else 0
df["senal"] = df["MACD"] if "MACD" in df.columns else 0
df["mensaje"] = df["tipo_vela"].apply(lambda x: "🔥 Entrada" if "Entrada" in x else "❄️ Salida")

# -----------------------------
# Panel lateral para pegar URL
# -----------------------------
st.sidebar.header("📌 Configurar Gráfico GoCharting")
url_input = st.sidebar.text_input(
    "Pega aquí tu URL de GoCharting",
    "https://www.gocharting.com/chart?symbol=BTCUSD&interval=15"
)

# -----------------------------
# Mostrar tabla de velas
# -----------------------------
st.subheader("📊 Tabla de Velas Interpretadas")
st.dataframe(df[["timestamp","tipo_vela","tendencia","momento","senal","close","mensaje"]])

# -----------------------------
# Mostrar iframe con URL pegado
# -----------------------------
st.subheader("📈 Gráfico Interactivo GoCharting")
# Botón para actualizar el iframe
if st.sidebar.button("Actualizar gráfico"):
    st.components.v1.iframe(url_input, height=600, scrolling=True)
