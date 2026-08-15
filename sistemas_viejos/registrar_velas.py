import pandas as pd
from ema_module import calcular_emas
from bitacora import agregar_entrada, agregar_entrada_mensual

CSV_FILE = "datos_ejemplo.csv"

def registrar_velas():
    """
    Lee cada fila del CSV y registra la vela en la bitácora maestro y mensual.
    Detecta velas de entrada/salida según tu sistema:
      - Vela de entrada: open, low, high > vela anterior + cierre > EMA_3
      - Vela de salida: open, low, high < vela anterior
    Calcula intención, reacción y decisión usando EMA_3, EMA_9 y MACD.
    Convierte los valores a tipos nativos Python para evitar errores JSON.
    """

    # Cargar CSV en DataFrame
    df = pd.read_csv(CSV_FILE)
    
    # Calcular EMAs
    df = calcular_emas(df)

    # Columna para tipo de vela
    df["tipo_vela"] = "ninguna"

    # Recorrer velas
    for i in range(1, len(df)):
        anterior = df.iloc[i-1]
        actual = df.iloc[i]

        # Detectar vela de entrada
        if (
            actual["open"] > anterior["open"] and
            actual["high"] > anterior["high"] and
            actual["low"] > anterior["low"] and
            actual["close"] > actual["EMA_3"]  # confirmación EMA3
        ):
            tipo = "Entrada"
        
        # Detectar vela de salida
        elif (
            actual["open"] < anterior["open"] and
            actual["high"] < anterior["high"] and
            actual["low"] < anterior["low"]
        ):
            tipo = "Salida"
        
        else:
            tipo = "ninguna"

        df.at[i, "tipo_vela"] = tipo
