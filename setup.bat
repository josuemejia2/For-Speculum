@echo off
setlocal
chcp 65001 > nul

cd /d "%~dp0"

echo.
echo ==========================================
echo  DANZARIEL-QUERO - Setup portable
echo ==========================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo [1/5] Creando entorno virtual .venv...
    python -m venv .venv
    if errorlevel 1 (
        echo ERROR: No se pudo crear .venv. Verifica que Python este instalado.
        pause
        exit /b 1
    )
) else (
    echo [1/5] .venv ya existe.
)

echo [2/5] Activando entorno...
call ".venv\Scripts\activate.bat"

echo [3/5] Actualizando pip...
python -m pip install --upgrade pip

echo [4/5] Instalando dependencias...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: No se pudieron instalar las dependencias.
    pause
    exit /b 1
)

echo [5/5] Creando carpetas necesarias...
python -m danzariel_quero.tools.ensure_workspace

if not exist ".env" (
    echo DQ_SECRET_TOKEN=cambia-este-token > .env
    echo DQ_HOST=0.0.0.0>> .env
    echo DQ_PORT=8000>> .env
    echo.
    echo Se creo .env con un token temporal.
    echo Edita DQ_SECRET_TOKEN para usar una clave privada.
) else (
    findstr /b /c:"DQ_SECRET_TOKEN=" ".env" > nul || echo DQ_SECRET_TOKEN=cambia-este-token>> .env
    findstr /b /c:"DQ_HOST=" ".env" > nul || echo DQ_HOST=0.0.0.0>> .env
    findstr /b /c:"DQ_PORT=" ".env" > nul || echo DQ_PORT=8000>> .env
    echo .env revisado: variables DQ listas.
)

echo.
echo Setup completado.
echo Para iniciar el servidor:
echo run_server.bat
echo.
pause
