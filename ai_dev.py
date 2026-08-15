"""
AI Dev Workspace - CLI conversacional integrado con Google Gemini
Permite conversar con IA y que edite archivos automáticamente
"""

import os
import sys
import json
import glob
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from colorama import Fore, Style, init
from google import genai

# Inicializar colorama
init(autoreset=True)

# Cargar variables de entorno
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    print(f"{Fore.RED}❌ Error: GOOGLE_API_KEY no encontrada en .env{Style.RESET_ALL}")
    sys.exit(1)

class AIDevWorkspace:
    def __init__(self):
        self.client = genai.Client(api_key=API_KEY)
        self.model_name = "gemini-2.0-flash"
        self.workspace_root = Path.cwd()
        self.session_history = []
        self.context_files = []
        self.load_session()
        self.system_prompt = self._build_system_prompt()
        
    def _build_system_prompt(self):
        """Construye el prompt del sistema con contexto del workspace"""
        return f"""Eres un desarrollador IA experto integrado en un workspace local.

DIRECTORIO DE TRABAJO: {self.workspace_root}

TUS RESPONSABILIDADES:
1. Ayudar con código Python, debugging y arquitectura
2. EDITAR ARCHIVOS DIRECTAMENTE cuando se solicite
3. Mantener un contexto claro del proyecto
4. Proponer mejoras y refactorizaciones
5. Explicar decisiones técnicas

FORMATO DE RESPUESTAS:
- Si DEBES editar un archivo, usa el formato:
  [EDIT_FILE: ruta/del/archivo.py]
  ```python
  # código nuevo o actualizado
  ```
  [END_EDIT]

- Si necesitas crear un archivo:
  [CREATE_FILE: ruta/archivo_nuevo.py]
  ```python
  # código del nuevo archivo
  ```
  [END_CREATE]

- Explica siempre QUÉ y POR QUÉ editas

CONTEXTO DEL PROYECTO:
- Python version: 3.x
- Environment: env/ (virtualenv activo)
- Frameworks: google-generativeai, streamlit, pandas, numpy (si existen)
- Archivos clave: {', '.join(self.get_key_files()[:5])}

IMPORTANTE:
- Sé conciso pero completo
- Proporciona código listo para producción
- Comunica cambios claramente
- Pregunta si hay ambigüedades"""

    def get_key_files(self):
        """Obtiene archivos principales del workspace"""
        patterns = ["*.py", "*.json", "*.md"]
        files = []
        for pattern in patterns:
            files.extend(glob.glob(f"{self.workspace_root}/{pattern}"))
        return [Path(f).name for f in files][:10]

    def load_session(self):
        """Carga sesión anterior si existe"""
        session_file = self.workspace_root / ".ai_dev_session.json"
        if session_file.exists():
            try:
                with open(session_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.session_history = data.get("history", [])
                    print(f"{Fore.CYAN}📝 Sesión anterior cargada ({len(self.session_history)} mensajes){Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.YELLOW}⚠️  No se pudo cargar sesión anterior: {e}{Style.RESET_ALL}")

    def save_session(self):
        """Guarda la sesión actual"""
        session_file = self.workspace_root / ".ai_dev_session.json"
        try:
            with open(session_file, "w", encoding="utf-8") as f:
                json.dump({
                    "history": self.session_history,
                    "last_saved": datetime.now().isoformat()
                }, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"{Fore.YELLOW}⚠️  Error guardando sesión: {e}{Style.RESET_ALL}")

    def get_workspace_context(self):
        """Genera contexto del workspace actual"""
        try:
            context = "# Estructura actual del workspace:\n"
            for root, dirs, files in os.walk(self.workspace_root):
                # Ignorar directorios específicos
                dirs[:] = [d for d in dirs if d not in ["env", "__pycache__", ".git", "sistemas_viejos", ".pytest_cache"]]
                
                level = root.replace(str(self.workspace_root), "").count(os.sep)
                indent = "  " * level
                rel_root = os.path.basename(root)
                if level == 0:
                    rel_root = "."
                
                context += f"{indent}{rel_root}/\n"
                
                sub_indent = "  " * (level + 1)
                for file in files[:5]:  # Limitar archivos mostrados
                    if not file.startswith("."):
                        context += f"{sub_indent}{file}\n"
            
            return context[:1500]  # Limitar contexto
        except:
            return ""

    def chat(self, user_message: str):
        """Envía mensaje a Gemini y maneja respuesta"""
        # Agregar a historial
        self.session_history.append({
            "role": "user",
            "content": user_message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Construir conversación
        conversation = [self.system_prompt]
        
        # Agregar contexto del workspace
        workspace_ctx = self.get_workspace_context()
        if workspace_ctx:
            conversation.append(f"\n{workspace_ctx}")
        
        # Agregar historial reciente (últimos 5 mensajes)
        for msg in self.session_history[-10:]:
            role = "User" if msg["role"] == "user" else "Assistant"
            conversation.append(f"{role}: {msg['content']}")
        
        full_prompt = "\n".join(conversation)
        
        try:
            print(f"\n{Fore.CYAN}🤖 IA procesando...{Style.RESET_ALL}\n")
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=full_prompt
            )
            assistant_message = response.text
            
            # Guardar respuesta en historial
            self.session_history.append({
                "role": "assistant",
                "content": assistant_message,
                "timestamp": datetime.now().isoformat()
            })
            
            # Procesar respuesta (buscar ediciones)
            self._process_edits(assistant_message)
            
            # Mostrar respuesta
            print(f"{Fore.GREEN}{assistant_message}{Style.RESET_ALL}\n")
            
            # Guardar sesión
            self.save_session()
            
        except Exception as e:
            print(f"{Fore.RED}❌ Error: {str(e)}{Style.RESET_ALL}")

    def _process_edits(self, response: str):
        """Procesa comandos de edición en la respuesta"""
        # Buscar [EDIT_FILE: ...]
        import re
        
        # Editar archivos
        edit_pattern = r'\[EDIT_FILE:\s*(.+?)\]\s*```(?:python)?\s*(.*?)\s*```\s*\[END_EDIT\]'
        for match in re.finditer(edit_pattern, response, re.DOTALL):
            filepath = match.group(1).strip()
            content = match.group(2).strip()
            self._apply_edit(filepath, content)
        
        # Crear archivos
        create_pattern = r'\[CREATE_FILE:\s*(.+?)\]\s*```(?:python)?\s*(.*?)\s*```\s*\[END_CREATE\]'
        for match in re.finditer(create_pattern, response, re.DOTALL):
            filepath = match.group(1).strip()
            content = match.group(2).strip()
            self._create_file(filepath, content)

    def _apply_edit(self, filepath: str, content: str):
        """Aplica edición a un archivo"""
        try:
            full_path = self.workspace_root / filepath
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            print(f"{Fore.YELLOW}✏️  Editado: {filepath}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}❌ Error editando {filepath}: {e}{Style.RESET_ALL}")

    def _create_file(self, filepath: str, content: str):
        """Crea un nuevo archivo"""
        try:
            full_path = self.workspace_root / filepath
            if full_path.exists():
                print(f"{Fore.YELLOW}⚠️  Archivo ya existe: {filepath}{Style.RESET_ALL}")
                return
            
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            print(f"{Fore.GREEN}✅ Creado: {filepath}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}❌ Error creando {filepath}: {e}{Style.RESET_ALL}")

    def show_commands(self):
        """Muestra comandos disponibles"""
        commands = """
╔═══════════════════════════════════════════════════════════════╗
║         🤖 AI DEV WORKSPACE - Comandos Disponibles            ║
╠═══════════════════════════════════════════════════════════════╣
║ /help           - Mostrar esta ayuda                          ║
║ /status         - Estado del workspace                        ║
║ /files          - Listar archivos del proyecto                ║
║ /history        - Ver historial de sesión                     ║
║ /clear          - Limpiar historial                           ║
║ /exit o /quit   - Salir                                       ║
║                                                               ║
║ 💡 Pide a la IA que:                                          ║
║    - Edite archivos (.py, .json, .md, etc)                   ║
║    - Cree nuevos archivos                                     ║
║    - Refactorice código                                       ║
║    - Debugging y explicaciones                                ║
║    - Arquitectura y diseño                                    ║
╚═══════════════════════════════════════════════════════════════╝
"""
        print(commands)

    def show_status(self):
        """Muestra estado del workspace"""
        print(f"\n{Fore.CYAN}📊 Estado del Workspace:{Style.RESET_ALL}")
        print(f"  📁 Root: {self.workspace_root}")
        print(f"  💬 Mensajes en sesión: {len(self.session_history)}")
        print(f"  🤖 Modelo: gemini-2.0-flash")
        print(f"  ✅ API Key configurada\n")

    def show_files(self):
        """Muestra archivos del workspace"""
        print(f"\n{Fore.CYAN}📂 Archivos del proyecto:{Style.RESET_ALL}\n")
        key_files = self.get_key_files()
        for f in key_files:
            print(f"  {f}")
        print()

    def run_interactive(self):
        """Loop interactivo principal"""
        self.show_commands()
        
        while True:
            try:
                user_input = input(f"{Fore.MAGENTA}You > {Style.RESET_ALL}").strip()
                
                if not user_input:
                    continue
                
                # Comandos especiales
                if user_input.startswith("/"):
                    cmd = user_input.lower()
                    if cmd in ["/exit", "/quit"]:
                        print(f"{Fore.CYAN}👋 Sesión guardada. ¡Hasta luego!{Style.RESET_ALL}")
                        self.save_session()
                        break
                    elif cmd == "/help":
                        self.show_commands()
                    elif cmd == "/status":
                        self.show_status()
                    elif cmd == "/files":
                        self.show_files()
                    elif cmd == "/history":
                        self._show_history()
                    elif cmd == "/clear":
                        self.session_history = []
                        print(f"{Fore.GREEN}✅ Historial limpiado{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.YELLOW}Comando desconocido. Usa /help{Style.RESET_ALL}")
                    continue
                
                # Chat normal
                self.chat(user_input)
                
            except KeyboardInterrupt:
                print(f"\n{Fore.CYAN}👋 Sesión guardada. ¡Hasta luego!{Style.RESET_ALL}")
                self.save_session()
                break
            except Exception as e:
                print(f"{Fore.RED}❌ Error: {str(e)}{Style.RESET_ALL}")

    def _show_history(self):
        """Muestra historial de sesión"""
        if not self.session_history:
            print(f"{Fore.YELLOW}Sin historial{Style.RESET_ALL}")
            return
        
        print(f"\n{Fore.CYAN}📜 Historial de sesión:{Style.RESET_ALL}\n")
        for i, msg in enumerate(self.session_history[-10:], 1):
            role = "👤 User" if msg["role"] == "user" else "🤖 IA"
            content = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
            print(f"{i}. {role}: {content}")
        print()


def main():
    """Punto de entrada principal"""
    print(f"""
╔═══════════════════════════════════════════════════════════════╗
║                  🔐 LLAVE SAGRADA - AI DEV                    ║
║              Google Gemini Terminal Integration                ║
╚═══════════════════════════════════════════════════════════════╝
""")
    
    workspace = AIDevWorkspace()
    workspace.run_interactive()


if __name__ == "__main__":
    main()
