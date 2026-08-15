def run(datos):
    """
    Calcula Parabólica SAR y fase de cambio.
    """
    sar = calcular_sar(datos)
    cambio_fase = datos['close'][-1] > sar[-1]

    return {
        "modulo": "SAR",
        "señal": cambio_fase,
        "detalle": {
            "SAR": sar[-1],
            "fase_cambio": cambio_fase
        }
    }