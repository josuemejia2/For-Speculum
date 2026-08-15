def mostrar_ultimas():
    txt_historial.delete("1.0", tk.END)
    datos = cargar_bitacora()

    for e in datos[-10:]:
        txt_historial.insert(
            tk.END,
            f"{e.get('fecha','')} | "
            f"Tipo: {e.get('tipo','(sin tipo)')} | "
            f"Inicio: {e.get('intencion','')} | "
            f"Reacción: {e.get('reaccion','')} | "
            f"Decisión: {e.get('decision','')} | "
            f"Cierre: {e.get('close','')}\n"
        )