import json
from datetime import datetime

CONOCIMIENTO_FILE = "conocimientos.json"

# Agregar conocimiento
def agregar_conocimiento(seccion, contenido):
    datos = cargar_conocimientos()
    
    # Cada entrada ahora es un diccionario con contenido y fecha
    entrada = {
        "contenido": contenido,
        "fecha": datetime.now().isoformat()
    }

    if seccion not in datos:
        datos[seccion] = []
    datos[seccion].append(entrada)
    guardar_todo(datos)
    print("Conocimiento agregado y registrado en la bitácora ✅")

# Mostrar todos los conocimientos
def mostrar_conocimientos():
    return cargar_conocimientos()

# Guardar todo el diccionario completo en conocimientos.json
def guardar_todo(datos):
    with open(CONOCIMIENTO_FILE, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)

# Cargar conocimientos
def cargar_conocimientos():
    try:
        with open(CONOCIMIENTO_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        # Crear estructura base
        return {
            "Paradigma": [],
            "Mandala_de_Singularidad": [],
            "Manual": [],
            "Leyes": [],
            "Reflexiones": [],
            "Proyectos": [],
            "ADN": [],
            "Danzariel": [],
            "Codigos": [],
            "Notas_Sistema": []
        }