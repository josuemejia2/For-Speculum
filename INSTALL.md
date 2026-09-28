# DANZARIEL-QUERO - Instalacion portable

DANZARIEL-QUERO es un servidor privado local para conectar tu telefono con tu PC y guardar conocimiento, documentos y archivos sin usar USB.

## 1. Instalar Python

Instala Python 3.11 o superior desde:

```text
https://www.python.org/downloads/windows/
```

Durante la instalacion marca:

```text
Add python.exe to PATH
```

Verifica desde PowerShell:

```powershell
python --version
```

Si `python` no responde, prueba:

```powershell
py --version
```

## 2. Instalar el proyecto

Abre PowerShell en la carpeta del proyecto y ejecuta:

```powershell
.\setup.bat
```

El instalador hace:

- Crear `.venv` si no existe.
- Instalar `requirements.txt`.
- Crear las carpetas de memoria.
- Crear `.env` si no existe.

## 3. Ejecutar el servidor

Desde la carpeta del proyecto:

```powershell
.\run_server.bat
```

El servidor mostrara:

```text
PC:
Telefono:
Puerto:
Token:
```

Abre la URL de `Telefono` desde tu celular siempre que este en la misma red Wi-Fi.

## 4. Usar inbox inteligente

Para probar QUERO Intelligence Layer:

1. Sube archivos al area `inbox`.
2. En la interfaz, usa `Analizar inbox`.
3. Escribe el nombre del archivo dentro de inbox.
4. Revisa la sugerencia.
5. Acepta o rechaza la decision.

El sistema no mueve archivos automaticamente todavia.

## 5. Entrar desde navegador

En PC:

```text
http://127.0.0.1:8000
```

En telefono:

```text
http://IP-DE-TU-PC:8000
```

La interfaz pedira el token privado. El token vive en `.env`.

## 6. Actualizar el proyecto

Si usas Git:

```powershell
git pull
.\setup.bat
.\run_server.bat
```

Si copiaste el proyecto como carpeta, reemplaza solo el codigo y conserva:

```text
.env
danzariel_quero_data/
```

## 7. Archivos que no se suben al repositorio

No subas:

```text
.env
.venv/
env/
__pycache__/
*.log
*.tmp
danzariel_quero_data/
```

La memoria principal puede subirse o no segun tu decision. Si contiene informacion privada, mantenla fuera de Git.
