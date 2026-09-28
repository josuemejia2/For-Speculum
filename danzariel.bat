@echo off
setlocal
chcp 65001 > nul
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" for-speculum-dev\builder.py
) else (
    python for-speculum-dev\builder.py
)

pause
