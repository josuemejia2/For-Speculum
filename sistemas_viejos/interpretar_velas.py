def interpretar_vela(fila, simbolo="BTC-USD", timeframe="5m"):
    """
    Devuelve un resumen simbólico de una vela:
    - Intención (mecha) = EMA_3
    - Reacción (rechazo / absorción) = EMA_9
    - Decisión (cierre) = MACD
    """
    interpretacion = {
        "simbolo": simbolo,
        "timeframe": timeframe,
        "tipo_vela": fila.get("tipo_vela", "ninguna"),
        "intencion": fila.get("EMA_3", 0),
        "reaccion": fila.get("EMA_9", 0),
        "decision": fila.get("MACD", 0)
    }

    # Interpretación simbólica
    if interpretacion["tipo_vela"] == "Entrada 🔥":
        interpretacion["mensaje"] = "🔥 Vela de entrada confirmada"
    elif interpretacion["tipo_vela"] == "Salida ❄️":
        interpretacion["mensaje"] = "❄️ Vela de salida detectada"
    else:
        interpretacion["mensaje"] = "⚪ Sin señal"

    return interpretacion