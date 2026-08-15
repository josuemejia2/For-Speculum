import json
import os
import matplotlib.pyplot as plt

# Ruta del archivo maestro
BITACORA_MAESTRA = "bitacora.json"

def cargar_bitacora(ruta=BITACORA_MAESTRA):
    if os.path.exists(ruta):
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def mostrar_bitacora(n=5, ruta=BITACORA_MAESTRA):
    datos = cargar_bitacora(ruta)
    ultimas = datos[-n:]
    print("\n🔹 BITÁCORA")
    for entry in ultimas:
        print(f"{entry['fecha']} | Tipo: {entry['tipo']} | Int: {entry['intencion']} Reac: {entry['reaccion']} Dec: {entry['decision']} | Close: {entry['close']}")

def graficar_velas(ruta=BITACORA_MAESTRA):
    datos = cargar_bitacora(ruta)
    if not datos:
        print("No hay datos para graficar.")
        return

    fechas = [d["fecha"] for d in datos]
    closes = [d["close"] for d in datos]

    plt.figure(figsize=(10,5))
    plt.plot(fechas, closes, marker='o', linestyle='-', color='blue', label='Close')
    plt.xticks(rotation=45)
    plt.xlabel("Fecha")
    plt.ylabel("Close")
    plt.title("Cierre de velas")
    plt.legend()
    plt.tight_layout()
    plt.show()

# Ejecutar funciones
mostrar_bitacora()
graficar_velas()