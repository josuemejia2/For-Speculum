# Comandos desde VS Code hasta GitHub

Esta guia sirve para preparar una computadora Windows, abrir este proyecto en VS Code y conectarlo con GitHub.

## 1. Instalar programas necesarios

Opcion A: instalar desde PowerShell con winget.

```powershell
winget install Microsoft.VisualStudioCode
winget install Git.Git
winget install GitHub.cli
winget install Python.Python.3.13
```

Opcion B: si winget no funciona, instalar manualmente desde el navegador.

```text
VS Code:
https://code.visualstudio.com/

Git for Windows:
https://git-scm.com/download/win

GitHub CLI:
https://cli.github.com/

Python:
https://www.python.org/downloads/windows/
```

Despues de instalar, cerrar PowerShell y abrirlo de nuevo.

## 2. Verificar instalaciones

```powershell
code --version
git --version
gh --version
python --version
```

Si `python` no responde, probar:

```powershell
py --version
```

## 3. Configurar Git por primera vez

Cambiar nombre y correo por los tuyos.

```powershell
git config --global user.name "Tu Nombre"
git config --global user.email "tu-correo@example.com"
git config --global init.defaultBranch main
```

Verificar configuracion:

```powershell
git config --global --list
```

## 4. Entrar al proyecto

```powershell
Set-Location "C:\Users\jonat\OneDrive\Desktop\llave_sagrada"
Get-Location
Get-ChildItem
```

Abrir el proyecto en VS Code:

```powershell
code .
```

## 5. Crear o activar entorno virtual

Si el entorno `env` ya existe:

```powershell
.\env\Scripts\Activate.ps1
```

Si PowerShell bloquea la activacion:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
.\env\Scripts\Activate.ps1
```

Si necesitas crear el entorno desde cero:

```powershell
python -m venv env
.\env\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

## 6. Instalar librerias principales del proyecto

```powershell
pip install pandas streamlit plotly PySide6 python-dotenv colorama google-genai google-generativeai
```

Ver librerias instaladas:

```powershell
pip freeze
```

Guardar dependencias en un archivo:

```powershell
pip freeze > requirements.txt
```

Instalar desde `requirements.txt` en otra computadora:

```powershell
pip install -r requirements.txt
```

## 7. Probar el sistema local

Ejecutar pruebas:

```powershell
.\env\Scripts\python.exe -m unittest discover -s tests -v
```

Compilar archivos Python para revisar sintaxis:

```powershell
.\env\Scripts\python.exe -m compileall -q -x "env|__pycache__|\.git" .
```

Ejecutar robot:

```powershell
.\env\Scripts\python.exe robot_quero.py analizar --json
```

Abrir panel Streamlit:

```powershell
.\env\Scripts\python.exe -m streamlit run control_plane.py
```

Abrir app de escritorio:

```powershell
.\env\Scripts\python.exe control_plane_app.py
```

## 8. Preparar archivos que no se suben a GitHub

Crear o revisar `.gitignore`:

```powershell
Get-Content .\.gitignore
```

Debe ignorar cosas como:

```text
.env
env/
__pycache__/
*.log
document_backups/
.ai_dev_session.json
```

Nunca subir claves privadas ni API keys.

## 9. Revisar estado de Git

```powershell
git status
git branch
git remote -v
```

Si no existe repositorio Git local:

```powershell
git init
```

## 10. Conectarse a GitHub

Iniciar sesion con GitHub CLI:

```powershell
gh auth login
```

Seleccionar normalmente:

```text
GitHub.com
HTTPS
Login with a web browser
```

Verificar sesion:

```powershell
gh auth status
```

## 11. Crear repositorio en GitHub desde la terminal

Opcion recomendada: crear repo privado.

```powershell
gh repo create llave_sagrada --private --source=. --remote=origin
```

Si lo quieres publico:

```powershell
gh repo create llave_sagrada --public --source=. --remote=origin
```

Verificar remoto:

```powershell
git remote -v
```

## 12. Primer commit y primer push

```powershell
git status
git add .
git commit -m "Initial project setup"
git push -u origin main
```

Si la rama no se llama `main`:

```powershell
git branch -M main
git push -u origin main
```

## 13. Flujo diario de trabajo

Antes de trabajar:

```powershell
git pull
```

Ver cambios:

```powershell
git status
git diff
```

Guardar cambios:

```powershell
git add .
git commit -m "Describe el cambio"
git push
```

## 14. Descargar el proyecto en otra computadora

```powershell
Set-Location "C:\Users\jonat\OneDrive\Desktop"
git clone https://github.com/TU_USUARIO/llave_sagrada.git
Set-Location .\llave_sagrada
code .
```

Crear entorno e instalar dependencias:

```powershell
python -m venv env
.\env\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 15. Entrar al repo For-Speculum

Este es el repo limpio conectado a GitHub:

```text
https://github.com/josuemejia2/For-Speculum.git
```

Carpeta local:

```text
C:\Users\jonat\OneDrive\Desktop\For-Speculum
```

Abrir desde PowerShell:

```powershell
cd C:\Users\jonat\OneDrive\Desktop\For-Speculum
code .
```

Abrir el panel terminal:

```powershell
.\control.ps1
```

O abrir con doble clic desde el Escritorio:

```text
Entrar_For-Speculum.cmd
```

## 16. Leer el estado del panel For-Speculum

Si el panel muestra esto:

```text
## main...origin/main
```

Significa:

```text
Estas en la rama main.
La rama local esta conectada con origin/main en GitHub.
```

Si ves archivos con `??`:

```text
?? archivo.md
```

Significa:

```text
Git ve el archivo, pero todavia no esta agregado al commit.
```

Si ves archivos con `A`:

```text
A  archivo.md
```

Significa:

```text
El archivo ya esta agregado y listo para crear commit.
```

Si ves archivos con `M`:

```text
M  archivo.md
```

Significa:

```text
El archivo ya existia y fue modificado.
```

Si ves la sesion GitHub asi:

```text
Logged in to github.com account josuemejia2
Git operations protocol: https
Token scopes: repo
```

Significa:

```text
Ya entraste a GitHub y tienes permiso para subir cambios.
```

## 17. Guardar y subir cambios desde el panel

Flujo recomendado:

```text
1. Abrir Entrar_For-Speculum.cmd
2. Elegir opcion 1 para revisar estado
3. Elegir opcion 5 para guardar cambios y subir
4. Escribir un mensaje de commit
```

Mensaje recomendado para el panel:

```text
Add terminal control panel
```

La opcion 5 hace por ti estos comandos:

```powershell
git add -A
git commit -m "Add terminal control panel"
git push
```

Verificar despues:

```powershell
git status
```

Si todo quedo subido, deberias ver algo parecido a:

```text
Your branch is up to date with 'origin/main'.
nothing to commit, working tree clean
```

## 18. Botones importantes del panel

```text
1  Estado del repo y GitHub
2  Entrar a GitHub
3  Abrir este repo en VS Code
4  Actualizar desde GitHub
5  Guardar cambios y subir
6  Crear documento nuevo
10 Enviar archivo por Clipboard
11 Pegar Clipboard sobre archivo
12 Backup de archivo
13 Rollback desde historial
14 Abrir historial
```

Nota importante sobre la opcion 11:

```text
Pegar Clipboard sobre archivo reemplaza TODO el contenido del archivo.
Antes de usarla, conviene usar la opcion 12 para crear un backup.
```

## 19. Comandos manuales para For-Speculum

Si no quieres usar el panel, estos son los comandos manuales:

```powershell
cd C:\Users\jonat\OneDrive\Desktop\For-Speculum
git status
git add -A
git commit -m "Describe el cambio"
git push
```

Actualizar antes de trabajar:

```powershell
cd C:\Users\jonat\OneDrive\Desktop\For-Speculum
git pull --ff-only
```

Ver conexion con GitHub:

```powershell
git remote -v
gh auth status
```

## 20. Comandos de emergencia

Ver archivos modificados:

```powershell
git status
```

Ver historial:

```powershell
git log --oneline --max-count=10
```

Deshacer cambios de un archivo antes de commit:

```powershell
git restore nombre_del_archivo
```

Quitar un archivo del area de commit sin borrarlo:

```powershell
git restore --staged nombre_del_archivo
```

Ver remotos:

```powershell
git remote -v
```

Cambiar remoto origin:

```powershell
git remote set-url origin https://github.com/TU_USUARIO/llave_sagrada.git
```

## 21. Checklist final

```text
[ ] VS Code instalado
[ ] Git instalado
[ ] GitHub CLI instalado
[ ] Python instalado
[ ] Proyecto abierto con code .
[ ] Entorno env activado
[ ] Tests pasando
[ ] .gitignore revisado
[ ] gh auth login completado
[ ] Repo creado en GitHub
[ ] git push completado
```
