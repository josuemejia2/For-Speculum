@echo off
setlocal
chcp 65001 > nul
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" youtube_audio.py %*
) else if exist "env\Scripts\python.exe" (
    "env\Scripts\python.exe" youtube_audio.py %*
) else (
    python youtube_audio.py %*
)

pause