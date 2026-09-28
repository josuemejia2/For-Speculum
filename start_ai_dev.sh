#!/bin/bash
# Script para iniciar AI Dev Workspace en Linux/Mac

echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║          🚀 AI Dev Workspace - Llave Sagrada                 ║"
echo "║           Google Gemini Terminal Integration                  ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Verificar que estamos en la carpeta correcta
if [ ! -f "ai_dev.py" ]; then
    echo "❌ Error: ai_dev.py no encontrado"
    echo "   Ejecuta este script desde la carpeta raíz del proyecto"
    exit 1
fi

# Activar virtualenv
if [ -f "env/bin/activate" ]; then
    echo "🐍 Activando Python virtual environment..."
    source env/bin/activate
else
    echo "⚠️  No se encontró virtualenv en env/bin"
fi

# Verificar .env
if [ ! -f ".env" ]; then
    echo ""
    echo "🔧 Primera vez? Necesitas configurar tu API Key de Google"
    echo "   Ejecuta esto primero:"
    echo "   python setup_ai_dev.py"
    echo ""
    exit 1
fi

# Iniciar aplicación
echo ""
echo "▶️  Iniciando AI Dev Workspace..."
echo ""

python ai_dev.py
