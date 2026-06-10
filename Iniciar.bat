@echo off
setlocal
REM Doble clic para arrancar la app en Windows.
cd /d "%~dp0"

REM Detecta Python: primero el lanzador "py", luego "python".
set "PY="
py -3 --version >nul 2>nul && set "PY=py -3"
if not defined PY (
  python --version >nul 2>nul && set "PY=python"
)

if not defined PY (
  echo.
  echo [ERROR] No se encontro Python.
  echo Instalalo desde https://www.python.org/downloads/
  echo IMPORTANTE: marca "Add Python to PATH" en el instalador.
  echo.
  pause
  exit /b 1
)

echo Usando Python: %PY%
%PY% --version

if not exist ".venv\Scripts\python.exe" (
  echo Creando entorno e instalando dependencias (solo la primera vez)...
  %PY% -m venv .venv
  if errorlevel 1 ( echo [ERROR] No se pudo crear el entorno virtual. & pause & exit /b 1 )
  call ".venv\Scripts\activate.bat"
  python -m pip install --upgrade pip
  pip install -r requirements.txt
  if errorlevel 1 ( echo [ERROR] Fallo instalando dependencias. & pause & exit /b 1 )
) else (
  call ".venv\Scripts\activate.bat"
)

echo.
echo Arrancando la app...
python app.py
echo.
echo [La app se cerro. Codigo de salida: %errorlevel%]
pause
