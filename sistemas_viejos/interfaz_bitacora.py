import tkinter as tk
from tkinter import messagebox

from bitacora import agregar_entrada, cargar_bitacora

def registrar_nueva():
    # Tomar los valores ingresados
    tipo = entry_tipo.get()
    intencion = entry_intencion.get()
    reaccion = entry_reaccion.get()
    decision = entry_decision.get()
    cierre = entry_cierre.get()

    # Verificar que todos los campos estén llenos
    if not all([tipo, intencion, reaccion, decision, cierre]):
        messagebox.showerror("Error", "Todos los campos deben llenarse")
        return

    try:
        cierre_val = float(cierre)
    except ValueError:
        messagebox.showerror("Error", "Cierre debe ser un número")
        return

    # Registrar en la bitácora
    agregar_entrada(
        tipo=tipo,
        intencion=intencion,
        reaccion=reaccion,
        decision=decision,
        close=cierre_val
    )

    messagebox.showinfo("Éxito", "Entrada registrada en la bitácora")

    # Limpiar campos
    entry_tipo.delete(0, tk.END)
    entry_intencion.delete(0, tk.END)
    entry_reaccion.delete(0, tk.END)
    entry_decision.delete(0, tk.END)
    entry_cierre.delete(0, tk.END)

# --- Interfaz ---
root = tk.Tk()
root.title("Registrar Evento en Bitácora")
root.geometry("450x300")

# Labels y tooltips (explicaciones)
tk.Label(root, text="Tipo de evento").grid(row=0, column=0, sticky="w")
tk.Label(root, text="Intención (Precio o valor esperado)").grid(row=1, column=0, sticky="w")
tk.Label(root, text="Reacción (Respuesta del sistema o mercado)").grid(row=2, column=0, sticky="w")
tk.Label(root, text="Decisión (Acción tomada según reacción)").grid(row=3, column=0, sticky="w")
tk.Label(root, text="Cierre (Valor final real)").grid(row=4, column=0, sticky="w")

# Entradas
entry_tipo = tk.Entry(root, width=30)
entry_intencion = tk.Entry(root, width=30)
entry_reaccion = tk.Entry(root, width=30)
entry_decision = tk.Entry(root, width=30)
entry_cierre = tk.Entry(root, width=30)

entry_tipo.grid(row=0, column=1)
entry_intencion.grid(row=1, column=1)
entry_reaccion.grid(row=2, column=1)
entry_decision.grid(row=3, column=1)
entry_cierre.grid(row=4, column=1)

# Botón para registrar
tk.Button(root, text="Registrar Entrada", command=registrar_nueva, bg="#4CAF50", fg="white").grid(row=5, column=0, columnspan=2, pady=15)

root.mainloop()