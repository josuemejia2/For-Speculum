# Guia para Codex PC - atraer el Lab

Este repositorio lleva el Lab visual de DANZARIEL-QUERO para correrlo en otra PC.
La informacion verdadera y privada vive fuera de Git, en iCloud/archivos locales.

## Objetivo

Traer el codigo del Lab a la PC y ejecutarlo localmente.

Incluye:

- `danzariel_quero/`: servidor FastAPI, `/lab`, API local y UI principal.
- `quero/`: logica de clasificacion, memoria y sensores.
- `xmb_desktop_ui/`: interfaz `/PS3` que el servidor monta al iniciar.
- `setup.bat`: crea `.venv`, instala dependencias y prepara carpetas.
- `run_server.bat`: inicia el servidor local.
- `danzariel.bat` y `chat_terminal.py`: terminal bonito del sistema.
- `tests/`: pruebas utiles para verificar que la logica base responde.

## En la PC nueva

Si aun no existe la carpeta:

```powershell
git clone https://github.com/josuemejia2/For-Speculum.git
cd For-Speculum
```

Si ya existe:

```powershell
cd RUTA\A\For-Speculum
git pull
```

Luego instala:

```powershell
.\setup.bat
```

Y ejecuta:

```powershell
.\run_server.bat
```

Abre:

```text
http://127.0.0.1:8000/lab
```

Opcional:

```text
http://127.0.0.1:8000/PS3/
```

## Portal terminal

Para abrir el mini sistema terminal:

```powershell
.\danzariel.bat
```

Dentro del portal puedes usar:

```text
/ui
/lab
/PS3
/server
/start-server
/url
/files
/note
/help
```

Guia especifica:

```text
PORTAL_TERMINAL_PC.md
```

## Para Codex PC

Despues de `git pull`, verifica:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_ema20_sensor tests.test_quero_brain_classifier
```

Si falta `.env`, ejecuta `setup.bat` o copia `.env.example` como `.env`.
Cambia `DQ_SECRET_TOKEN` en la PC si vas a usar funciones privadas.

## No subir a Git

Mantener fuera del repo:

```text
.env
.venv/
env/
__pycache__/
*.log
danzariel_quero_data/
document_backups/
```

## Nota

El Lab puede funcionar con datos simulados. La API de mercado es opcional y puede fallar si no hay internet.
