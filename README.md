# Llave Sagrada / Sistema Quero

## Sistema actual

Estos archivos son los que quedaron activos en la raiz del proyecto:

- `danzariel_quero/`: servidor local FastAPI, panel privado y Lab visual en `/lab`.
- `quero/`: nucleo de clasificacion, memoria y sensores del sistema.
- `xmb_desktop_ui/`: interfaz modular tipo PS3/XMB disponible en `/PS3/`.
- `chat_terminal.py` y `danzariel.bat`: terminal bonito del sistema.
- `robot_quero.py`: motor principal del robot, reglas, indicadores y guardado en bitacora.
- `dashboard_tradingview.py`: dashboard Streamlit del robot con grafica embebida.
- `control_plane.py`: entrada Streamlit para navegar entre Inicio, Robot y Paradigma.
- `control_plane_app.py`: app de escritorio PySide6 del control plane.
- `abrir_control_panel.bat`: launcher para abrir el panel como ventana de app.

## Arranque portable en otra PC

Primero crea el entorno:

```powershell
.\setup.bat
```

Luego inicia el servidor:

```powershell
.\run_server.bat
```

Abre el Lab:

```text
http://127.0.0.1:8000/lab
```

### Usar el Lab desde el telefono

1. Conecta el telefono y el PC a la misma red Wi-Fi.
2. Inicia el servidor con `run_server.bat` y deja esa ventana abierta. La consola muestra la URL de acceso desde el telefono, por ejemplo `http://192.168.1.25:8000`.
3. En el telefono abre esa URL, introduce el valor `DQ_SECRET_TOKEN` de `.env` en el campo de token y pulsa `Entrar`.
4. Abre `Lab` y usa `YouTube a MP3`. Las canciones se guardan en `iCloudDrive/sonidos` en el PC.

Usalo solo en una red de confianza y no compartas el token. Si Windows pregunta, permite el acceso de Python solo en redes privadas. Si no carga desde el telefono, revisa que ambos dispositivos esten en la misma Wi-Fi y que el Firewall de Windows permita el puerto configurado en redes privadas.

Abre el XMB:

```text
http://127.0.0.1:8000/PS3/
```

Para la terminal:

```powershell
.\danzariel.bat
```

## Datos activos

- `datos_ejemplo.csv`: velas de prueba.
- `leyes.json`: leyes del sistema.
- `bitacora.json`: bitacora principal.
- `bitacoras_historicas/`: bitacoras por mes.
- `conocimientos.json`: memoria/conocimiento guardado.

## Carpetas

- `clase1/`: notas y practica de PowerShell.
- `.venv/`: entorno virtual generado por `setup.bat` en cada maquina. No se sube a Git.
- `sistemas_viejos/`: versiones anteriores, pruebas, dashboards viejos y modulos que ya no forman parte del sistema actual.

## Comandos utiles

### Audio offline de YouTube

Para contenido propio, con licencia o cuya descarga tengas autorizada, instala `ffmpeg` y las dependencias del proyecto. Luego ejecuta:

```powershell
.\extraer_youtube_mp3.bat "https://www.youtube.com/watch?v=ID"
```

El MP3 se guarda en `~/iCloudDrive/sonidos`, para que iCloud Drive lo sincronice con tus dispositivos. Para una voz o clase larga, `128` kbps suele ser suficiente:

```powershell
.\extraer_youtube_mp3.bat "https://youtu.be/ID" --quality 192
```

Si iCloud Drive esta en otra ubicacion, configura `DQ_AUDIO_OUTPUT_DIR` como variable de entorno o pasa la carpeta con `--output` al comando.

El proceso admite vídeos largos; asegúrate de tener espacio libre suficiente. `ffmpeg` debe estar instalado y disponible en `PATH`.

Si YouTube muestra “Sign in to confirm you're not a bot” desde `/lab`, configura cookies de un navegador donde ya tengas iniciada tu sesión de YouTube. Agrega esto al `.env` del proyecto y reinicia el servidor:

```dotenv
YOUTUBE_COOKIES_FROM_BROWSER=chrome
```

Si aparece `Could not copy Chrome cookie database`, el servidor del PC no puede leer la base de cookies del navegador; el iPhone solo envía la solicitud y no aporta sus cookies. Cierra Chrome por completo en el PC, incluidos los procesos `chrome.exe` que sigan activos, y vuelve a probar.

Si el error persiste, exporta las cookies de YouTube en formato Netscape (no copies el archivo SQLite del perfil) y configura `YOUTUBE_COOKIES_FILE=C:/ruta/privada/cookies.txt` en `.env`. Quita `YOUTUBE_COOKIES_FROM_BROWSER` y `YOUTUBE_COOKIES_BROWSER_PROFILE`, y reinicia el servidor. Mantén el archivo privado y no lo compartas ni lo subas al repositorio. La cuenta exportada debe poder ver el video. También puedes seleccionar un perfil distinto con `YOUTUBE_COOKIES_BROWSER_PROFILE=Profile 1`, pero esto sigue leyendo la base de datos del navegador.

```powershell
.\.venv\Scripts\python.exe robot_quero.py analizar --json
```

```powershell
.\.venv\Scripts\python.exe -m streamlit run control_plane.py
```

```powershell
.\.venv\Scripts\python.exe control_plane_app.py
```

```powershell
.\abrir_control_panel.bat
```

## Control Panel

El panel principal usa una navegacion tipo XMB:

- `Control`: categorias principales del sistema.
- `Robot`: tablero operativo de mercado.
- `Documentos`: lectura por secciones de documentos maestros.
- `Editor`: edicion por capas con backup automatico.
- `Paradigma`: acceso rapido al marco universal.

Documentos maestros integrados: Acta, Paradigma, Root Architecture, Protocolo, Manual, Legacy y Botones iOS.

El editor bloquea el Acta de Origen y Fe como solo lectura. Los demas documentos se guardan con copia previa en `document_backups/`.
