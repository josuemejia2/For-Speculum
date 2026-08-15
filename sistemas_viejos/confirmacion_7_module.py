def run(resultados):
    """
    Filtra todas las señales según ley 7.
    """
    confirmadas = []
    for r in resultados:
        if cumple_ley_7(r):
            confirmadas.append(r)

    return {
        "modulo": "Confirmacion7",
        "señales_confirmadas": confirmadas
    }