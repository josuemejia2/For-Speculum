def run(datos):
    """
    Detecta velas de entrada y salida y las 3 etapas: intención, reacción, decisión.
    """
    ultima = datos[-1]
    anterior = datos[-2]

    entrada = (ultima['open'] > anterior['open'] and
               ultima['high'] > anterior['high'] and
               ultima['low'] > anterior['low'])

    salida = (ultima['open'] < anterior['open'] and
              ultima['high'] < anterior['high'] and
              ultima['low'] < anterior['low'])

    return {
        "modulo": "VelaGuia",
        "entrada": entrada,
        "salida": salida,
        "detalle": {
            "intencion": ultima['high'] - ultima['close'],
            "reaccion": ultima['close'] - ultima['low'],
            "decision": ultima['close']
        }
    }