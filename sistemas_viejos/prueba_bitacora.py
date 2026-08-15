import pandas as pd
from ema_module import calcular_emas

# Cargar datos de ejemplo
df = pd.read_csv("datos_ejemplo.csv")

# Calcular EMAs
df = calcular_emas(df)

# Mostrar últimas filas
print(df.tail())
