@echo off
REM Script para iniciar AI Dev Workspace en Windows

setlocal enabledelayedexpansion

echo.
echo ╔═══════════════════════════════════════════════════════════════╗
echo ║          🚀 AI Dev Workspace - Llave Sagrada                 ║
echo ║           Google Gemini Terminal Integration                  ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.

REM Verificar que estamos en la carpeta correcta
if not exist "ai_dev.py" (
    echo ❌ Error: ai_dev.py no encontrado
    echo    Ejecuta este script desde la carpeta raíz del proyecto
    pause
    exit /b 1
)

REM Activar virtualenv
if exist "env\Scripts\activate.bat" (
    echo 🐍 Activando Python virtual environment...
    call env\Scripts\activate.bat
) else (
    echo ⚠️  No se encontró virtualenv en env\Scripts
)

REM Verificar .env
if not exist ".env" (
    echo.
    echo 🔧 Primera vez? Necesitas configurar tu API Key de Google
    echo    Ejecuta esto primero:
    echo    python setup_ai_dev.py
    echo.
    pause
    exit /b 1
)

REM Iniciar aplicación
echo.
echo ▶️  Iniciando AI Dev Workspace...
echo.
python ai_dev.py

pause
