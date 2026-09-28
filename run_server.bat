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
        if "%%A"=="DQ_HOST" set DQ_HOST=%%B
        if "%%A"=="DQ_PORT" set DQ_PORT=%%B
        if "%%A"=="DQ_SECRET_TOKEN" set DQ_SECRET_TOKEN=%%B
    )
)

if "%DQ_HOST%"=="" set DQ_HOST=0.0.0.0
if "%DQ_PORT%"=="" set DQ_PORT=8000
if "%DQ_SECRET_TOKEN%"=="" (
    echo ERROR: Falta DQ_SECRET_TOKEN en .env. Ejecuta setup.bat o define un token privado.
    pause
    exit /b 1
)
if "%DQ_SECRET_TOKEN%"=="cambia-este-token" (
    echo ERROR: DQ_SECRET_TOKEN todavia usa el valor temporal. Ejecuta setup.bat o cambialo en .env.
    pause
    exit /b 1
)

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
if "%DQ_HOST%"=="127.0.0.1" (
    echo Telefono: desactivado ^(DQ_HOST local^)
) else (
    echo Telefono: http://%LOCAL_IP%:%DQ_PORT%
)
echo Puerto:   %DQ_PORT%
echo Host:     %DQ_HOST%
echo Token:    configurado
echo.
echo Mantén esta ventana abierta mientras uses el servidor.
echo.

python -m uvicorn danzariel_quero.app.main:app --host %DQ_HOST% --port %DQ_PORT%
