from bitacora import agregar_entrada_mensual

# Ejemplo de velas simuladas, reemplaza con tu fuente de datos real
velas = [
    {"fecha": "2025-12-23 12:00:00", "tipo": "Entrada", "intencion": 20980.0, "reaccion": 20850.0, "decision": 328.2, "close": 21050.0},
    {"fecha": "2025-12-23 12:05:00", "tipo": "Entrada", "intencion": 21000.0, "reaccion": 20870.0, "decision": 330.1, "close": 21100.0},
    {"fecha": "2025-12-23 12:10:00", "tipo": "Entrada", "intencion": 21050.0, "reaccion": 20900.0, "decision": 332.0, "close": 21150.0}
]

for vela in velas:
    tipo = vela["tipo"]
    intencion = vela["intencion"]
    reaccion = vela["reaccion"]
    decision = vela["decision"]
    close = vela["close"]

    # Guardar en bitácora mensual y maestro
    agregar_entrada_mensual(tipo, intencion, reaccion, decision, close)

    print(f"Registrada vela: {vela['fecha']} | Tipo: {tipo} | Int: {intencion} Reac: {reaccion} Dec: {decision} | Close: {close}")

print("\n✅ Todas las velas han sido registradas en la bitácora.")