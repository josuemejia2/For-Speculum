def run(datos):
    """
    Calcula MACD y fuerza del impulso.
    """
    macd_linea, señal_linea = calcular_macd(datos)
    impulso = macd_linea[-1] - señal_linea[-1]

    return {
        "modulo": "MACD",
        "señal": impulso > 0,  # True si impulso positivo
        "detalle": {
            "MACD": macd_linea[-1],
            "señal": señal_linea[-1],
            "impulso": impulso
        }
    }