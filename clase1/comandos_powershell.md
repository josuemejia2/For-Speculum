# Comandos basicos de PowerShell

## Guias relacionadas

- `comandos_vscode_github.md`: desde instalar VS Code hasta conectar el proyecto con GitHub.

## 1. Ubicacion y listado

```powershell
Get-Location
Get-ChildItem
```

## 2. Crear carpeta y entrar

```powershell
New-Item -ItemType Directory clase1
Set-Location .\clase1
```

## 3. Crear archivo

```powershell
New-Item -ItemType File notas.txt
```

## 4. Escribir, agregar y leer

```powershell
Set-Content -Path .\notas.txt -Value 'primera linea'
Add-Content -Path .\notas.txt -Value 'segunda linea'
Get-Content .\notas.txt
```

## 5. Renombrar, copiar y borrar copia

```powershell
Rename-Item .\notas.txt apuntes.txt
Copy-Item .\apuntes.txt .\apuntes_copia.txt
Get-ChildItem
Remove-Item .\apuntes_copia.txt -WhatIf
Remove-Item .\apuntes_copia.txt
Get-ChildItem
```

## 6. Crear subcarpeta y 3 archivos

```powershell
New-Item -ItemType Directory NGM
Set-Location .\NGM
New-Item -ItemType File nota1.txt
New-Item -ItemType File nota2.txt
New-Item -ItemType File nota3.txt
```

## 7. Guardar texto en cada archivo

```powershell
Set-Content .\nota1.txt 'aprendiendo powershell'
Set-Content .\nota2.txt 'aprendiendo python'
Set-Content .\nota3.txt 'aprendiendo git'
```

## 8. Buscar texto dentro de archivos

```powershell
Select-String -Path .\*.txt -Pattern 'python'
```

## 9. Mover/copiar entre carpetas

```powershell
Set-Location ..
New-Item -ItemType Directory archivos_finales
Rename-Item .\NGM\nota1.txt powershell_basico.txt
Move-Item .\NGM\powershell_basico.txt .\archivos_finales\
Copy-Item .\NGM\nota2.txt .\archivos_finales\python_basico.txt
```

## 10. Verificar resultado final

```powershell
Get-ChildItem .\NGM
Get-ChildItem .\archivos_finales
```
