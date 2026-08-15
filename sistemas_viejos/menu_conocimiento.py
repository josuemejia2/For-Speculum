import json
from guardar_conocimiento import agregar_conocimiento, mostrar_conocimientos, guardar_todo

CONOCIMIENTO_FILE = "conocimientos.json"

# Cargar conocimientos
def cargar_conocimientos():
    try:
        with open(CONOCIMIENTO_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
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

# Menú principal
def menu():
    datos = cargar_conocimientos()
    while True:
        print("\n📚 SECCIONES DISPONIBLES:")
        for i, seccion in enumerate(datos.keys(), start=1):
            print(f"{i}. {seccion} ({len(datos[seccion])})")
        print("0. Salir")

        try:
            opcion = int(input("Selecciona sección: "))
        except ValueError:
            print("Ingresa un número válido.")
            continue

        if opcion == 0:
            print("Saliendo del menú. ✅")
            break
        elif 1 <= opcion <= len(datos):
            seccion = list(datos.keys())[opcion-1]
            menu_seccion(seccion, datos)
        else:
            print("Opción inválida.")

# Menú de cada sección
def menu_seccion(seccion, datos):
    while True:
        print(f"\n📂 {seccion}")
        entradas = datos[seccion]
        if not entradas:
            print("— Sin entradas —")
        else:
            for i, e in enumerate(entradas, start=1):
                print(f"{i}. {e['contenido']} (agregado: {e['fecha']})")

        print("\nAcciones:")
        print("1. Agregar")
        print("2. Editar")
        print("3. Eliminar")
        print("0. Volver")

        try:
            accion = int(input("Selecciona acción: "))
        except ValueError:
            print("Ingresa un número válido.")
            continue

        if accion == 0:
            guardar_todo(datos)
            break
        elif accion == 1:
            texto = input("Ingresa contenido: ")
            agregar_conocimiento(seccion, texto)
            datos = cargar_conocimientos()  # recargar
        elif accion == 2:
            if not entradas:
                print("No hay entradas para editar.")
                continue
            try:
                num = int(input(f"Ingresa el número de la entrada a editar (1-{len(entradas)}): "))
                nuevo = input("Ingresa el nuevo contenido: ")
                datos[seccion][num-1]['contenido'] = nuevo
                datos[seccion][num-1]['fecha'] = datetime.now().isoformat()
                guardar_todo(datos)
                print("Contenido editado ✅")
            except (ValueError, IndexError):
                print("Número inválido.")
        elif accion == 3:
            if not entradas:
                print("No hay entradas para eliminar.")
                continue
            try:
                num = int(input(f"Ingresa el número de la entrada a eliminar (1-{len(entradas)}): "))
                eliminado = datos[seccion].pop(num-1)
                guardar_todo(datos)
                print(f"Entrada eliminada: {eliminado['contenido']}")
            except (ValueError, IndexError):
                print("Número inválido.")
        else:
            print("Acción inválida.")

if __name__ == "__main__":
    from datetime import datetime
    menu()