# DANZARIEL-QUERO - Portability Report

## Cambios realizados

- Se creo un modulo nuevo y aislado en `danzariel_quero/`.
- Se agrego un servidor FastAPI privado.
- Se agrego una interfaz web movil en `danzariel_quero/web/static/`.
- Se agrego almacenamiento portable en `danzariel_quero_data/`.
- Se agrego autenticacion por token usando `.env`.
- Se agrego registro de cambios en `danzariel_quero_data/memoria/change_log.jsonl`.
- Se agrego QUERO Intelligence Layer en `quero/brain/`.
- Se agrego analizador de inbox con `POST /api/analyze`.
- Se separo memoria de observaciones y decisiones:
  - `danzariel_quero_data/bitacora/analisis.jsonl`
  - `danzariel_quero_data/bitacora/decisiones.jsonl`
- Se agrego identidad unica de eventos tipo `q-YYYYMMDD-0001`.
- Se agrego principio de seguridad: nada se mueve sin aprobacion humana.
- Se agrego memoria de decisiones en `danzariel_quero_data/bitacora/decisiones.jsonl`.
- Se agregaron scripts Windows:
  - `setup.bat`
  - `run_server.bat`
- Se agrego `requirements.txt`.
- Se agrego `INSTALL.md`.

## Rutas corregidas o evitadas

El codigo no fija rutas del perfil de usuario. Los documentos externos del panel se configuran mediante variables locales `DQ_*_PATH` o `PARADIGMA_MD_PATH`; por defecto se buscan dentro de `documentos/` en la carpeta del proyecto. Los datos del servidor se guardan bajo `DQ_DATA_DIR`.

## Que falta para portabilidad completa

- Decidir si la memoria `danzariel_quero_data/` se sincronizara con Git, disco externo, nube privada o backups.
- Agregar usuarios multiples si mas personas entraran al servidor.
- Agregar HTTPS si se expone fuera de la red local.
- Agregar chat con IA conectado a documentos.
- Agregar base vectorial para busqueda semantica.
- Migrar documentos viejos de iCloud a `danzariel_quero_data/`.
- Agregar aprobacion que mueva archivos automaticamente cuando el usuario lo confirme.
