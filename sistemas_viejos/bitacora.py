import json
import os
from datetime import datetime

BITACORA_FILE = "bitacora.json"

def cargar_bitacora(ruta=BITACORA_FILE):
    if os.path.exists(ruta):
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def guardar_bitacora(datos, ruta=BITACORA_FILE):
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=2, ensure_ascii=False)

def agregar_entrada(tipo, intencion, reaccion, decision, close, ruta=BITACORA_FILE):
    entrada = {
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "tipo": tipo,
        "intencion": intencion,
        "reaccion": reaccion,
        "decision": decision,
        "close": close
    }
    datos = cargar_bitacora(ruta)
    datos.append(entrada)
    guardar_bitacora(datos, ruta)

# Función para generar archivo mensual automáticamente
def ruta_mensual(base="bitacora"):
    hoy = datetime.now()
    nombre = f"{base}_{hoy.year}_{hoy.month:02}.json"
    return os.path.join("bitacoras_historicas", nombre)

def agregar_entrada_mensual(tipo, intencion, reaccion, decision, close):
    # Guardar en el archivo mensual
    ruta = ruta_mensual()
    os.makedirs("bitacoras_historicas", exist_ok=True)
    agregar_entrada(tipo, intencion, reaccion, decision, close, ruta)
    # Guardar también en el bitacora principal
    agregar_entrada(tipo, intencion, reaccion, decision, close)