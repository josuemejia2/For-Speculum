# ⚡ QUICK START - AI Dev Workspace

## En 3 pasos estás listo

### 📌 Paso 1: Obtén tu Google API Key (GRATIS - 2 minutos)

```
1. Abre en tu navegador:
   https://aistudio.google.com/app/apikey

2. Haz clic en "Create API key"

3. Haz clic en "Create API key in new Google Cloud project"

4. ✅ Copia la clave (te aparece en pantalla)
```

**¿Por qué es gratis?**
- Google te da 50 requests/minuto **SIN PAGAR**
- Solo pagas si lo usas comercialmente o excedes muchísimo el límite
- Para desarrollo es perfecto

---

### 🔧 Paso 2: Setup (Windows - PowerShell)

En la carpeta del proyecto, abre PowerShell y corre:

```powershell
# Activar entorno virtual (si no está activo)
.\env\Scripts\Activate.ps1

# Ejecutar setup
python setup_ai_dev.py
```

Te pedirá:
- Tu Google API Key (la que copiaste arriba)
- **¡Listo!**

---

### 🚀 Paso 3: ¡Inicia!

Opción A (PowerShell):
```powershell
python ai_dev.py
```

Opción B (Doble clic - fácil):
```
start_ai_dev.bat
```

Opción C (PowerShell mejorado):
```powershell
.\start_ai_dev.ps1
```

---

## 💬 Tu primer comando

Una vez iniciado, ves un prompt como:

```
You > 
```

Escribe algo como:

```
You > Di hola en español
```

O más útil:

```
You > Crea un archivo test.py que imprima "Hola mundo"
```

---

## 🎯 Ejemplos Listos para Copiar/Pegar

### Crear un archivo nuevo
```
You > Crea un archivo utils.py con estas funciones:
      - suma(a, b)
      - resta(a, b)
      - multiplica(a, b)
```

### Refactorizar código existente
```
You > Refactoriza control_plane.py:
      - Añade type hints a todas las funciones
      - Mejora la documentación
      - Optimiza la lógica de conexión
```

### Debugging
```
You > Me da este error cuando ejecuto robot_quero.py:
      [COPIAR Y PEGAR EL ERROR AQUÍ]
      
      ¿Cómo lo arreglo?
```

### Crear módulo completo
```
You > Crea un módulo alertas.py que:
      1. Lee datos de bitacora.json
      2. Si hay cambios importantes, guarda una alerta
      3. Exporta función get_ultimas_alertas()
```

---

## ⌨️ Comandos útiles dentro de la app

```
/help      →  Ver todos los comandos
/status    →  Ver config actual
/files     →  Listar archivos del proyecto
/history   →  Ver últimos 10 mensajes
/clear     →  Limpiar historial
/exit      →  Salir (guarda todo automáticamente)
```

---

## ❓ Preguntas Comunes

### "¿Es realmente gratis?"
✅ Sí, **completamente gratis** para desarrollo
- 50 requests/minuto sin pagar
- Suficiente para trabajar normalmente

### "¿Dónde va mi API Key?"
✅ En el archivo `.env` en tu carpeta (NO se sube a GitHub)
- Nunca compartir el `.env`
- Es solo local en tu PC

### "¿Y si me equivoco y la IA edita mal?"
✅ La IA NO edita sin permiso
- Solo edita si le pides explícitamente
- El historial se guarda, puedes ver qué cambió
- Usa `/clear` si necesitas empezar limpio

### "¿Tengo conexión a Internet?"
✅ SÍ, necesita Internet
- Se conecta a Google Gemini API
- Una vez descargado el código, funciona offline (pero sin IA)

### "¿Puedo cambiar de modelo?"
✅ Sí, en `ai_dev.py` línea 32:
```python
self.model = genai.GenerativeModel("gemini-2.0-pro")  # Más potente
```

---

## 🎬 Demo en 1 minuto

```
You > Crea un script que lea bitacora.json y muestre estadísticas

[IA crea el archivo y explica qué hace]

You > Ahora integra eso en un dashboard con streamlit

[IA crea dashboard_automatico.py]

You > ¿Puedes refactorizar control_plane.py?

[IA edita el archivo y muestra cambios]

You > /exit

[Sesión guardada]
```

---

## 📂 Archivos que se crean

```
ai_dev.py              ← EJECUTA ESTO
setup_ai_dev.py        ← Ejecuta una sola vez
start_ai_dev.bat       ← Atajo para Windows
start_ai_dev.ps1       ← Atajo PowerShell
start_ai_dev.sh        ← Atajo Linux/Mac
.env                   ← Tus credenciales (NO commitear)
.env.example          ← Plantilla
.ai_dev_session.json  ← Historial automático
ai_dev_config.json    ← Configuración avanzada
AI_DEV_README.md      ← Documentación completa
QUICK_START.md        ← Este archivo
```

---

## 🆘 Si algo falla

### Error: "GOOGLE_API_KEY no encontrada"
```
Solución:
1. python setup_ai_dev.py
2. Ingresa tu API Key correctamente
```

### Error: "Módulo no encontrado"
```
Solución:
pip install google-generativeai python-dotenv colorama
```

### La IA no me edita archivos
```
Verifica que:
1. Hayas pedido explícitamente "Edita el archivo X"
2. El nombre del archivo sea correcto
3. El archivo exista
```

---

## 🎓 Tips Pro

1. **Sé específico**: 
   - ❌ "Mejora el código"
   - ✅ "Refactoriza para usar async/await y agrega type hints"

2. **Divide tareas grandes**:
   ```
   You > Primero, crea la clase Database en db.py
   You > Luego, integra Database en control_plane.py
   You > Finalmente, crea tests para ambos
   ```

3. **Usa el contexto**:
   La IA ve tu estructura de proyecto, úsalo:
   ```
   You > El bitacora.json guarda datos así: [pegar ejemplo]
         Quiero un script que analice esos datos
   ```

4. **Historial persistente**:
   El historial se guarda automáticamente
   ```
   Sesión 1: Creas algo
   Sesión 2: "Mejora lo que hicimos ayer"
   [IA lo recuerda!]
   ```

---

## ✅ Checklist Final

Antes de empezar:
- [ ] Tengo Google API Key (obtenida de aistudio.google.com/app/apikey)
- [ ] Ejecuté `python setup_ai_dev.py` 
- [ ] Tengo Internet (para conectar a Gemini)
- [ ] Estoy en la carpeta correcta (donde está `ai_dev.py`)

¡Listo?

```
python ai_dev.py
```

---

**¡Que disfrutes tu AI Dev Workspace! 🚀**

Si tienes dudas, lee AI_DEV_README.md para documentación completa.
