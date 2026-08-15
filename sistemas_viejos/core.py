import pandas as pd
from datetime import datetime
from guardar_conocimiento import agregar_conocimiento, cargar_conocimientos, guardar_todo

# Archivo CSV de velas
CSV_FILE = "datos_ejemplo.csv"

# -----------------------------
# Leyes del Sistema Quero
# -----------------------------
leyes = {
    "Quero": "El precio siempre vuelve a rotación de EMAs. EMA3/9 es la rotación más fuerte.",
    "Capitan": "Cerca del máximo → busca máximo. Cerca del mínimo → busca mínimo. Define dirección, no repetición.",
    "Maximos": "Un máximo tocado tiende a repetirse hasta que sea roto.",
    "Minimos": "Un mínimo tocado tiende a repetirse mientras no sea roto.",
    "Jesus": "Precio sobre EMA20 + primer histograma MACD positivo → tocará banda de Bollinger. EMA50 actúa si la banda está lejos.",
    "Trujillo": "Para continuidad, la vela debe abrir lejos de EMA20/50/200.",
    "52Semanas": "Toque o rechazo de EMA50 → tendencia sin límite."
}

# -----------------------------
# Funciones para el sistema
# -----------------------------
def leer_datos_csv():
    """Leer CSV de velas"""
    try:
        df = pd.read_csv(CSV_FILE)
        return df
    except FileNotFoundError:
        print(f"{CSV_FILE} no encontrado. Crea el archivo con datos de ejemplo.")
        return pd.DataFrame()

def tipo_vela(fila, fila_ant):
    """Determina tipo de vela: Entrada, Salida o Neutral"""
    if fila_ant.empty:
        return "Neutral"
    
    if (fila["open"] > fila_ant["open"] and
        fila["high"] > fila_ant["high"] and
        fila["low"] > fila_ant["low"]):
        return "Entrada"
    
    elif (fila["open"] < fila_ant["open"] and
          fila["high"] < fila_ant["high"] and
          fila["low"] < fila_ant["low"]):
        return "Salida"
    
    else:
        return "Neutral"

def etapas_vela(fila, fila_ant):
    """Calcula Intención, Reacción y Decisión de la vela"""
    intencion = abs(fila["high"] - fila["open"])
    reaccion = abs(fila["low"] - fila["open"])
    decision = fila["close"]
    return intencion, reaccion, decision

def panel_lateral(df):
    """Muestra panel lateral y registra en conocimientos.json"""
    if df.empty:
        print("No hay datos para mostrar.")
        return

    datos_conocimiento = cargar_conocimientos()
    
    print("\n🔹 PANEL LATERAL - Llave 2-3-6-7-10-12-8")
    
    fila_ant = pd.Series()
    for index, fila in df.iterrows():
        tipo = tipo_vela(fila, fila_ant)
        intencion, reaccion, decision = etapas_vela(fila, fila_ant)
        
        print(f"{fila['timestamp']} | Tipo: {tipo} | Int: {intencion:.2f} Reac: {reaccion:.2f} Dec: {decision:.2f} | Close: {fila['close']}")
        
        # Registrar automáticamente en conocimientos.json
        registro = (f"{fila['timestamp']} | Tipo: {tipo} | Int: {intencion:.2f} "
                    f"Reac: {reaccion:.2f} Dec: {decision:.2f} | Close: {fila['close']}")
        agregar_conocimiento("Notas_Sistema", registro)
        
        fila_ant = fila

def mostrar_leyes():
    print("\n📜 Leyes activas del Sistema Quero:")
    for nombre, desc in leyes.items():
        print(f"- {nombre}: {desc}")

# -----------------------------
# Función principal
# -----------------------------
def main():
    print("🔑 SISTEMA QUERO - Llave 2-3-6-7-10-12-8 activa ✅")
    
    mostrar_leyes()
    
    df = leer_datos_csv()
    panel_lateral(df)
    
    print("\n✅ Análisis completado.")

# -----------------------------
if __name__ == "__main__":
    main()