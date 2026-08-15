import pandas as pd

PERIODOS_EMA = [3, 9, 20, 50, 200]

def calcular_emas(df, columna_precio="close"):
    if columna_precio not in df.columns:
        raise ValueError(f"No existe la columna '{columna_precio}'")

    for periodo in PERIODOS_EMA:
        df[f"EMA_{periodo}"] = df[columna_precio].ewm(
            span=periodo,
            adjust=False
        ).mean()

    return df