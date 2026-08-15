@echo off
setlocal enabledelayedexpansion
chcp 65001 > nul

cd /d "%~dp0"

if not exist ".venv\Scripts\activate.bat" (
    echo ERROR: No existe .venv. Ejecuta setup.bat primero.
    pause
    exit /b 1
)

call ".venv\Scripts\activate.bat"

if exist ".env" (
    for /f "usebackq tokens=1,* delims==" %%A in (".env") do (
        if "%%A"=="DQ_PORT" set DQ_PORT=%%B
        if "%%A"=="DQ_SECRET_TOKEN" set DQ_SECRET_TOKEN=%%B
    )
)

if "%DQ_PORT%"=="" set DQ_PORT=8000
if "%DQ_SECRET_TOKEN%"=="" set DQ_SECRET_TOKEN=cambia-este-token

for /f "tokens=2 delims=:" %%A in ('ipconfig ^| findstr /c:"IPv4"') do (
    set LOCAL_IP=%%A
    set LOCAL_IP=!LOCAL_IP: =!
    goto :found_ip
)

:found_ip
if "%LOCAL_IP%"=="" set LOCAL_IP=127.0.0.1

echo.
echo ==========================================
echo  DANZARIEL-QUERO - Servidor local
echo ==========================================
echo PC:       http://127.0.0.1:%DQ_PORT%
echo Telefono: http://%LOCAL_IP%:%DQ_PORT%
echo Puerto:   %DQ_PORT%
echo Token:    %DQ_SECRET_TOKEN%
echo.
echo Mantén esta ventana abierta mientras uses el servidor.
echo.

python -m uvicorn danzariel_quero.app.main:app --host 0.0.0.0 --port %DQ_PORT%
