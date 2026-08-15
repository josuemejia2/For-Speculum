# Portal Terminal en la PC

Este es el mini sistema terminal de DANZARIEL-QUERO.

## Archivos importantes

- `danzariel.bat`: entrada recomendada. Abre la terminal con pantalla inicial.
- `chat_terminal.bat`: abre la terminal sin modo wake.
- `chat_terminal.py`: logica del portal terminal.
- `TERMINAL_CHAT.md`: referencia de comandos y flujo.
- `run_server.bat`: servidor para abrir `/lab` y `/PS3`.

## Primera vez en la PC

Desde la carpeta del repo:

```powershell
.\setup.bat
```

Luego abre el portal:

```powershell
.\danzariel.bat
```

## Comandos dentro del portal

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

## Flujo recomendado

1. Ejecuta `.\run_server.bat` si quieres tener el Lab abierto.
2. Ejecuta `.\danzariel.bat` para abrir el portal terminal.
3. Dentro del portal usa `/lab` para abrir el Lab visual.
4. Usa `/PS3` para abrir el escritorio futurista.
5. Usa `/ui` para ver el centro de control terminal.

## Si no abre

Verifica que estes en el repo correcto:

```powershell
git rev-parse --short HEAD
```

Debe estar en el commit mas reciente del repo. Luego:

```powershell
git pull origin main
.\setup.bat
.\danzariel.bat
```

## Nota

`.env`, `.venv/`, `env/` y `danzariel_quero_data/` no viajan por Git. Cada PC los crea localmente.
