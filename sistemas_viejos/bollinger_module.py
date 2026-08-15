def run(datos):
    """
    Calcula Bandas de Bollinger y rango de velas.
    """
    media, upper, lower = calcular_bollinger(datos)

    # Ver si la vela toca límite
    toca_limite = datos['close'][-1] > upper or datos['close'][-1] < lower

    return {
        "modulo": "Bollinger",
        "señal": toca_limite,
        "detalle": {
            "media": media[-1],
            "upper": upper[-1],
            "lower": lower[-1]
        }
    }
