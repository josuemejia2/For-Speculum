# Script para iniciar AI Dev Workspace en PowerShell

function Start-AIDev {
    Write-Host ""
    Write-Host "╔═══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║          🚀 AI Dev Workspace - Llave Sagrada                 ║" -ForegroundColor Cyan
    Write-Host "║           Google Gemini Terminal Integration                  ║" -ForegroundColor Cyan
    Write-Host "╚═══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    
    # Verificar que estamos en la carpeta correcta
    if (!(Test-Path "ai_dev.py")) {
        Write-Host "❌ Error: ai_dev.py no encontrado" -ForegroundColor Red
        Write-Host "   Ejecuta este script desde la carpeta raíz del proyecto" -ForegroundColor Yellow
        return $false
    }
    
    # Activar virtualenv
    if (Test-Path "env\Scripts\Activate.ps1") {
        Write-Host "🐍 Activando Python virtual environment..." -ForegroundColor Green
        & ".\env\Scripts\Activate.ps1"
    } else {
        Write-Host "⚠️  No se encontró virtualenv en env\Scripts" -ForegroundColor Yellow
    }
    
    # Verificar .env
    if (!(Test-Path ".env")) {
        Write-Host ""
        Write-Host "🔧 Primera vez? Necesitas configurar tu API Key de Google" -ForegroundColor Yellow
        Write-Host "   Ejecuta esto primero:" -ForegroundColor Yellow
        Write-Host "   python setup_ai_dev.py" -ForegroundColor Cyan
        Write-Host ""
        return $false
    }
    
    # Iniciar aplicación
    Write-Host ""
    Write-Host "▶️  Iniciando AI Dev Workspace..." -ForegroundColor Green
    Write-Host ""
    
    python ai_dev.py
    
    return $true
}

# Ejecutar función
Start-AIDev

# Pausar si es necesario
if ($LASTEXITCODE -ne 0) {
    Read-Host "Presiona Enter para salir"
}
