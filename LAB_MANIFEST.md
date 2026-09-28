# Lab Manifest

Este paquete es la parte tecnica portable de DANZARIEL-QUERO.

## Rutas principales

- `/lab`: laboratorio visual con sensores, grafica Quero EMA20/50 y Capa 3.
- `/PS3/`: interfaz modular estilo XMB.
- `/`: panel privado de documentos, inbox y memoria local.

## Capa 2 - Indicador Quero

La grafica del Lab recalcula por timeframe:

- `1m`
- `5m`
- `15m`
- `1h`

Cada timeframe crea su propio mundo:

- Serie propia agregada.
- EMA20/50 propias.
- Punto A cuando cruza EMA20/50.
- Punto B cuando el precio vuelve al nivel del Punto A.
- Linea positiva cuando el cruce EMA20/50 es negativo.
- Linea negativa cuando el cruce EMA20/50 es positivo.

## Capa 3 - Alerta Banda Bollinger

La alerta espera alineacion de:

- EMA 3/9.
- Precio sobre/bajo EMA20.
- MACD en direccion.
- Parabolica.
- Vela Inteligente como activador.

Cuando se activa, el destino es la Banda de Bollinger en la direccion del MACD.
La lectura visual usa verde, rojo o amarillo segun estado positivo, negativo o transicion.

## Datos

El codigo viaja por Git. La memoria privada no.

La carpeta `danzariel_quero_data/` se crea localmente en cada maquina y queda fuera del repositorio.
