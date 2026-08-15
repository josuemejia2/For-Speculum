@echo off
setlocal
chcp 65001 > nul
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" chat_terminal.py
) else (
    python chat_terminal.py
)

pause
