import tkinter as tk
from bitacora import cargar_bitacora

# --------------------
# INTERFAZ PRINCIPAL
# --------------------
root = tk.Tk()
root.title("Dashboard del Sistema")

# --------------------
# TEXTO BITÁCORA
# --------------------
txt_ultimas = tk.Text(root, width=80, height=25)
txt_ultimas.pack(padx=10, pady=10)

# --------------------
# FUNCIÓN MOSTRAR
# --------------------
def mostrar_ultimas():
    txt_ultimas.delete("1.0", tk.END)

    try:
        registros = cargar_bitacora()
    except Exception as e:
        txt_ultimas.insert(tk.END, f"Error cargando bitácora: {e}\n")
        return

    if not registros:
        txt_ultimas.insert(tk.END, "No hay registros aún.\n")
        return

    for e in registros[-10:]:
        fecha = e.get("fecha", "—")
        tipo = e.get("tipo") or e.get("accion") or e.get("evento", "—")
        intencion = e.get("intencion", "—")
        reaccion = e.get("reaccion", "—")
        decision = e.get("decision", "—")
        cierre = e.get("close", e.get("cierre", "—"))

        txt_ultimas.insert(
            tk.END,
            f"{fecha}\n"
            f"  Tipo: {tipo}\n"
            f"  Intención: {intencion}\n"
            f"  Reacción: {reaccion}\n"
            f"  Decisión: {decision}\n"
            f"  Cierre: {cierre}\n"
            f"{'-'*40}\n"
        )

# --------------------
# BOTÓN
# --------------------
btn = tk.Button(root, text="Mostrar últimas entradas", command=mostrar_ultimas)
btn.pack(pady=5)

# Mostrar al iniciar
mostrar_ultimas()

root.mainloop()