"""
Setup Script para AI Dev Workspace
Configura las variables de entorno y verifica dependencias
"""

import os
import sys
from pathlib import Path

def setup():
    print("""
╔═══════════════════════════════════════════════════════════════╗
║          ⚙️  Setup AI Dev Workspace - Llave Sagrada          ║
╚═══════════════════════════════════════════════════════════════╝
""")
    
    # Verificar .env
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists():
        if env_example.exists():
            print("📋 Copiando .env.example a .env...")
            with open(env_example, "r") as src:
                with open(env_file, "w") as dst:
                    dst.write(src.read())
        else:
            print("❌ No se encontró .env.example")
            return False
    
    # Solicitar API Key
    print("\n🔑 Necesitas una Google API Key para Gemini")
    print("📍 Obtén una en: https://aistudio.google.com/app/apikey")
    print("   (Es GRATIS y rápido - solo clic derecho)\n")
    
    api_key = input("Pega tu Google API Key: ").strip()
    
    if not api_key:
        print("❌ API Key requerida")
        return False
    
    # Guardar API Key
    with open(env_file, "r") as f:
        content = f.read()
    
    content = content.replace("your_google_api_key_here", api_key)
    
    with open(env_file, "w") as f:
        f.write(content)
    
    print(f"✅ API Key guardada en .env")
    
    # Verificar dependencias
    print("\n📦 Verificando dependencias...")
    try:
        import google.generativeai
        import colorama
        import dotenv
        print("✅ Todas las librerías están instaladas")
    except ImportError as e:
        print(f"⚠️  Falta instalar: {e}")
        return False
    
    print("""
✅ Setup completado!

🚀 Para iniciar:
   python ai_dev.py

📝 Comandos disponibles:
   /help   - Ver todos los comandos
   /status - Estado del workspace
   /files  - Listar archivos
   /clear  - Limpiar historial
   /exit   - Salir

💡 Ejemplos de uso:
   "Crea un dashboard con streamlit"
   "Refactoriza el archivo control_plane.py"
   "Debuguea este error: ..."
   "Explica cómo funciona este código"
""")
    
    return True

if __name__ == "__main__":
    if not setup():
        sys.exit(1)
