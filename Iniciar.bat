@echo off
REM Doble clic para arrancar la app en Windows.
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
  echo Python no esta instalado. Instalalo desde https://www.python.org/downloads/
  echo IMPORTANTE: marca "Add Python to PATH" en el instalador.
  pause
  exit /b 1
)

if not exist ".venv\" (
  echo Creando entorno e instalando dependencias (solo la primera vez)...
  python -m venv .venv
  call .venv\Scripts\activate.bat
  python -m pip install --upgrade pip
  pip install -r requirements.txt
) else (
  call .venv\Scripts\activate.bat
)

python app.py
pause
