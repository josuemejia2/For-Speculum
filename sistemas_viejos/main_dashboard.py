def main():
    datos = cargar_datos("datos_ejemplo.csv")

    # Ejecutar módulos
    resultados = []
    resultados.append(ema_module.run(datos))
    resultados.append(macd_module.run(datos))
    resultados.append(bollinger_module.run(datos))
    resultados.append(sar_module.run(datos))
    resultados.append(vela_guia_module.run(datos))

    # Confirmación ley 7
    confirmacion = confirmacion_7_module.run(resultados)
    
    # AI supervisa
    final = ai_supervisor.run(confirmacion["señales_confirmadas"])

    # Guardar historial
    historial_module.guardar(final["señales_finales"])

    # Retornar o enviar a interfaz
    return final["señales_finales"]

if __name__ == "__main__":
    main()