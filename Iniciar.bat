@echo off
setlocal
REM Doble clic para arrancar la app en Windows.
cd /d "%~dp0"

REM Detecta Python: primero el lanzador "py", luego "python".
set "PY="
py -3 --version >nul 2>nul && set "PY=py -3"
if not defined PY py --version >nul 2>nul && set "PY=py"
if not defined PY python --version >nul 2>nul && set "PY=python"

if not defined PY goto NOPYTHON

echo Usando Python: %PY%
%PY% --version

if exist ".venv\Scripts\python.exe" goto ACTIVATE

echo Creando entorno e instalando dependencias. Solo la primera vez, tarda un poco...
%PY% -m venv .venv
if errorlevel 1 goto VENVERR
call ".venv\Scripts\activate.bat"
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 goto PIPERR
goto RUN

:ACTIVATE
call ".venv\Scripts\activate.bat"

:RUN
echo.
echo Arrancando la app...
python app.py
echo.
echo La app se cerro. Codigo de salida: %errorlevel%
pause
exit /b 0

:NOPYTHON
echo.
echo [ERROR] No se encontro Python.
echo Instalalo desde https://www.python.org/downloads/
echo IMPORTANTE: marca "Add Python to PATH" en el instalador.
echo.
pause
exit /b 1

:VENVERR
echo.
echo [ERROR] No se pudo crear el entorno virtual .venv
echo.
pause
exit /b 1

:PIPERR
echo.
echo [ERROR] Fallo instalando dependencias de requirements.txt
echo.
pause
exit /b 1
