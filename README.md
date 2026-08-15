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
