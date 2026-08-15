import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from bitacora import agregar_entrada, cargar_bitacora

# --- Funciones ---
def registrar_entrada():
    try:
        tipo = tipo_var.get()
        intencion = float(int_var.get())
        reaccion = float(reac_var.get())
        decision = float(dec_var.get())
        close = float(close_var.get())
        
        agregar_entrada(tipo, intencion, reaccion, decision, close)
        messagebox.showinfo("Éxito", "Vela registrada en la bitácora.")
        limpiar_campos()
        actualizar_tabla()
    except ValueError:
        messagebox.showerror("Error", "Valores numéricos inválidos.")

def limpiar_campos():
    int_var.set("")
    reac_var.set("")
    dec_var.set("")
    close_var.set("")

def actualizar_tabla():
    for row in tabla.get_children():
        tabla.delete(row)
    datos = cargar_bitacora()
    ultimas = datos[-10:]  # mostrar últimas 10 entradas
    for e in ultimas:
        tabla.insert("", "end", values=(
            e["fecha"], e["tipo"], e["intencion"], e["reaccion"], e["decision"], e["close"]
        ))

def graficar():
    datos = cargar_bitacora()
    if not datos:
        messagebox.showwarning("Atención", "No hay datos para graficar.")
        return
    fechas = [datetime.fromisoformat(d["fecha"]) for d in datos]
    closes = [d["close"] for d in datos]

    fig, ax = plt.subplots(figsize=(6,4))
    ax.plot(fechas, closes, marker='o', linestyle='-')
    ax.set_title("Precio Close Histórico")
    ax.set_xlabel("Fecha")
    ax.set_ylabel("Close")
    fig.autofmt_xdate()

    # Integrar matplotlib en Tkinter
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().grid(row=10, column=0, columnspan=4)
    canvas.draw()

# --- Interfaz ---
root = tk.Tk()
root.title("Sistema Universal 2-3-6-7-10-12-8")

# Variables
tipo_var = tk.StringVar(value="Entrada")
int_var = tk.StringVar()
reac_var = tk.StringVar()
dec_var = tk.StringVar()
close_var = tk.StringVar()

# Campos
tk.Label(root, text="Tipo:").grid(row=0, column=0)
ttk.Combobox(root, textvariable=tipo_var, values=["Entrada", "Salida"]).grid(row=0, column=1)

tk.Label(root, text="Intención:").grid(row=1, column=0)
tk.Entry(root, textvariable=int_var).grid(row=1, column=1)

tk.Label(root, text="Reacción:").grid(row=2, column=0)
tk.Entry(root, textvariable=reac_var).grid(row=2, column=1)

tk.Label(root, text="Decisión:").grid(row=3, column=0)
tk.Entry(root, textvariable=dec_var).grid(row=3, column=1)

tk.Label(root, text="Close:").grid(row=4, column=0)
tk.Entry(root, textvariable=close_var).grid(row=4, column=1)

tk.Button(root, text="Registrar Vela", command=registrar_entrada).grid(row=5, column=0, columnspan=2, pady=5)
tk.Button(root, text="Graficar Close", command=graficar).grid(row=5, column=2, columnspan=2, pady=5)

# Tabla de últimas entradas
columns = ("fecha", "tipo", "intencion", "reaccion", "decision", "close")
tabla = ttk.Treeview(root, columns=columns, show="headings", height=10)
for col in columns:
    tabla.heading(col, text=col.capitalize())
tabla.grid(row=6, column=0, columnspan=4)

# Inicializar tabla
actualizar_tabla()

root.mainloop()