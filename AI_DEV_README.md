# 🤖 AI Dev Workspace - Google Gemini Terminal Integration

Un workspace donde conversás con una IA (Google Gemini) directamente en el terminal y ella edita tus archivos automáticamente.

## ✨ Características

- 💬 **Chat conversacional** en terminal con Google Gemini
- ✏️ **Edición automática** de archivos Python, JSON, Markdown, etc.
- 📁 **Contexto completo** del workspace (entiende tu estructura)
- 💾 **Historial persistente** de sesiones
- 🔄 **Integración fluida** con tu proyecto actual
- 🎨 **Interfaz coloreada** y amigable

## 🚀 Quick Start

### 1. Obtén tu Google API Key (GRATIS)

```
1. Abre: https://aistudio.google.com/app/apikey
2. Haz clic en "Crear API key"
3. Cópiala
```

**¿Es realmente gratis?** Sí, Google te da:
- 🆓 **50 requests/minuto** de forma GRATUITA
- 🆓 Suficiente para desarrollo y testing
- 💰 Luego pagas solo si excedes el límite

### 2. Setup Inicial

En PowerShell (en la carpeta del proyecto):

```powershell
# Activar venv si no está activo
.\env\Scripts\Activate.ps1

# Ejecutar setup
python setup_ai_dev.py
```

Sigue los pasos (solo pedir la API Key).

### 3. ¡Inicia!

```powershell
python ai_dev.py
```

## 💬 Cómo Usar

### Ejemplos de Comandos

```
👤 You > Crea un archivo llamado utils.py con funciones útiles

👤 You > Refactoriza control_plane.py para mejorar rendimiento

👤 You > Debug: cuando ejecuto robot_quero.py me da este error...
          [pegar error aquí]

👤 You > Crea un dashboard con Streamlit que muestre estadísticas

👤 You > Explica cómo funciona el módulo bollinger_module.py
```

### Comandos Especiales

```
/help      → Ver todos los comandos
/status    → Estado del workspace y sesión
/files     → Listar archivos del proyecto
/history   → Ver últimos 10 mensajes
/clear     → Limpiar historial de sesión
/exit      → Salir (guarda sesión automáticamente)
```

## 🎯 Casos de Uso

### 📝 Crear Nuevo Código
```
👤 You > Crea un script que lea datos_ejemplo.csv y haga análisis estadístico
```

### 🔧 Refactorizar Existente
```
👤 You > Mejora el código de control_plane.py:
         - Añade type hints
         - Organiza mejor las funciones
         - Agrega docstrings
```

### 🐛 Debugging
```
👤 You > No entiendo este error:
         [copiar/pegar error completo]
         Archivo: robot_quero.py línea 45
```

### 📚 Explicaciones
```
👤 You > ¿Qué hace el módulo de Bollinger Bands?
👤 You > Explica la lógica del dashboard_tradingview.py
```

## 📂 Archivos Generados

```
ai_dev.py              → Aplicación principal (lanzar esta!)
setup_ai_dev.py        → Script de setup único
.env                   → Tus credenciales (NO COMMITEAR)
.env.example          → Template de .env
.ai_dev_session.json  → Historial persistente de sesiones
```

## ⚙️ Configuración Avanzada

### Editar `.env`

```bash
# Google Gemini API
GOOGLE_API_KEY=tu_api_key_aqui

# Carpetas a ignorar
IGNORE_PATHS=env,__pycache__,.git,sistemas_viejos

# Root del workspace
PROJECT_ROOT=.
```

### Modelos disponibles en Gemini

```python
# En ai_dev.py línea 32, puedes cambiar:
self.model = genai.GenerativeModel("gemini-2.0-flash")  # Actual
# A alternativas:
genai.GenerativeModel("gemini-2.0-pro")        # Más potente, más lento
genai.GenerativeModel("gemini-1.5-pro")        # Muy capaz, recomendado
```

## 🔐 Seguridad

- ✅ Tu API Key se guarda en `.env` (agrégalo a `.gitignore`)
- ✅ La sesión se guarda localmente (`.ai_dev_session.json`)
- ✅ No subes datos a ningún lado excepto a Google Gemini
- ✅ La IA **NO** edita archivos sin pedirte permiso

## 📋 Requisitos

- Python 3.8+
- Google Account (para la API Key)
- Conexión a Internet (para Gemini)

## 🐛 Troubleshooting

### Error: "GOOGLE_API_KEY no encontrada"
```
Solución: Ejecuta setup_ai_dev.py de nuevo
```

### Error: "Failed to import google.generativeai"
```
Solución: pip install google-generativeai
```

### La IA no edita mis archivos
```
Verifica que hayas pedido explícitamente:
"Edita el archivo X para que..."
"Crea un archivo nuevo llamado..."
```

### Limitar contexto (para sesiones muy largas)
```
Usa /clear para limpiar historial
O abre una nueva terminal (nueva sesión)
```

## 🎓 Tips y Trucos

### 1. **Contexto es Todo**
Cuanta más información des a la IA, mejores respuestas:
```
MÁS ESPECÍFICO: "Refactoriza control_plane.py para que use async/await"
MENOS ESPECÍFICO: "Mejora control_plane.py"
```

### 2. **Paso a Paso**
Para tareas complejas, divide en pasos:
```
👤 You > 1. Primero, crea una clase ConfigManager en utils.py
👤 You > 2. Ahora integra esa clase en control_plane.py
👤 You > 3. Prueba que funcione correctamente
```

### 3. **Revisar Antes de Ejecutar**
Siempre lee el código que la IA genera antes de usarlo.

### 4. **Reutilizar Sesiones**
Tu historial se guarda automáticamente, así que puedes:
```
Sesión 1: "Crea archivo X"
[Al día siguiente]
Sesión 2: "Mejora el archivo X que creaste ayer"
```

## 🚀 Próximos Pasos

### Después del primer setup:

1. **Prueba simple:**
   ```
   You > Di "hola" en español
   ```

2. **Prueba de edición:**
   ```
   You > Crea un archivo test.py con una función que diga hola
   ```

3. **Prueba real:**
   ```
   You > [Tu tarea real de desarrollo]
   ```

## 📞 Soporte

Si algo no funciona:
1. Verifica que tengas Internet
2. Verifica que la API Key sea correcta
3. Prueba `/status` para ver configuración
4. Limpia con `/clear` y reinicia

## 🎯 Casos de Uso del Proyecto Actual

**Para tu proyecto de trading/bots:**

```
👤 You > Mejora robot_quero.py para que sea más eficiente

👤 You > Crea un módulo nuevo llamado notificaciones.py 
         que envíe alertas cuando se cumplan ciertas condiciones

👤 You > Refactoriza dashboard_tradingview.py para usar Streamlit

👤 You > Documenta todos los módulos con docstrings

👤 You > Crea tests unitarios para las funciones más críticas
```

---

**Hecho con ❤️ para tu workspace**

¿Preguntas? Lee `/help` dentro de la aplicación.
