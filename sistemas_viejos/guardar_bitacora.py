import json
import os
from datetime import datetime

# Ruta del archivo maestro
BITACORA_MAESTRA = "bitacora.json"

def cargar_bitacora(ruta=BITACORA_MAESTRA):
    """Cargar bitácora existente, devuelve lista vacía si no existe"""
    if os.path.exists(ruta):
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def guardar_bitacora(datos, ruta=BITACORA_MAESTRA):
    """Guardar lista completa en la bitácora"""
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)

def agregar_entrada(tipo, intencion, reaccion, decision, close, ruta=BITACORA_MAESTRA):
    """Agrega una nueva entrada a la bitácora"""
    datos = cargar_bitacora(ruta)
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entrada = {
        "fecha": fecha,
        "tipo": tipo,
        "intencion": intencion,
        "reaccion": reaccion,
        "decision": decision,
        "close": close
    }
    datos.append(entrada)
    guardar_bitacora(datos, ruta)

def mostrar_ultimas(n=5, ruta=BITACORA_MAESTRA):
    """Muestra las últimas N entradas de la bitácora"""
    datos = cargar_bitacora(ruta)
    ultimas = datos[-n:]
    for e in ultimas:
        print(f"{e['fecha']} | Tipo: {e['tipo']} | Int: {e['intencion']} Reac: {e['reaccion']} Dec: {e['decision']} | Close: {e['close']}")

# Opcional: generar archivo mensual automático
def ruta_mensual(base="bitacora"):
    hoy = datetime.now()
    nombre = f"{base}_{hoy.year}_{hoy.month:02}.json"
    return nombre

def agregar_entrada_mensual(tipo, intencion, reaccion, decision, close):
    ruta = ruta_mensual()
    agregar_entrada(tipo, intencion, reaccion, decision, close, ruta)
    agregar_entrada(tipo, intencion, reaccion, decision, close)  # también se guarda en bitacora maestro