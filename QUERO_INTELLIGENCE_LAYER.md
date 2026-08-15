# QUERO Intelligence Layer

Esta fase agrega una capa inteligente encima del MVP DANZARIEL-QUERO.

## Objetivo

Analizar archivos que llegan a `inbox` antes de organizarlos.

El sistema sugiere una categoria y un destino, pero no mueve archivos automaticamente.

## Principio de seguridad

El sistema nunca debe modificar ni mover archivos sin una accion explicita del usuario.

Flujo obligatorio:

```text
Archivo recibido
  ↓
Analisis
  ↓
Sugerencia
  ↓
Aprobacion humana
  ↓
Movimiento
  ↓
Registro
```

## Flujo

```text
Archivo llega a inbox
  ↓
POST /api/analyze
  ↓
QUERO brain analiza nombre, tipo, metadata y texto si existe
  ↓
Devuelve sugerencia
  ↓
Usuario acepta o rechaza
  ↓
Se registra decision en bitacora
```

## Endpoint de analisis

```text
POST /api/analyze
```

Puede analizar:

- Un archivo ya guardado en `inbox`.
- Un archivo enviado directamente al endpoint.

Respuesta ejemplo:

```json
{
  "archivo": "grafico_bitcoin.png",
  "tipo": "image/png",
  "extension": ".png",
  "tamano_bytes": 12345,
  "categoria_sugerida": "trading",
  "carpeta_sugerida": "/trading/imagenes",
  "confianza": 87,
  "explicacion": "Coincidencias: bitcoin, grafico. Imagen relacionada con trading.",
  "texto_extraido": "",
  "requiere_aprobacion": true
}
```

## Memoria de decisiones

Las decisiones se guardan en:

```text
danzariel_quero_data/bitacora/analisis.jsonl
```

Ese archivo guarda observaciones del sistema:

- archivo
- senales encontradas
- clasificacion propuesta
- confianza estimada
- explicacion

Las decisiones humanas se guardan en:

```text
danzariel_quero_data/bitacora/decisiones.jsonl
```

Formato:

```json
{
  "fecha": "",
  "archivo": "",
  "decision_usuario": "aceptado",
  "categoria": "",
  "carpeta": "",
  "confianza": "",
  "explicacion": ""
}
```

Cada evento tiene un ID unico:

```json
{
  "id": "q-20260730-0001",
  "archivo": "btc_chart.png",
  "accion": "analyze",
  "resultado": "trading",
  "confianza": 87
}
```

La confianza siempre es una estimacion de reglas actuales en escala 0-100. No representa verdad absoluta.

## Preparado para IA futura

La capa `quero/brain/` separa interfaces para:

- Reglas actuales.
- Modelo local futuro.
- Vector database futura.
- Busqueda semantica futura.

Todavia no conecta modelos.

Interfaces preparadas:

```python
classifier.predict()
classifier.predict_local_model()
classifier.predict_vector_memory()
classifier.predict_llm()
```
