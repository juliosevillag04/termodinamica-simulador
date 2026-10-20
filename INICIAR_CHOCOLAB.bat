@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title ChocoLab - Simulador de Van der Waals
chcp 65001 >nul

echo ==============================================
echo       ChocoLab - Inicio en Windows
echo ==============================================
where python >nul 2>nul
if errorlevel 1 goto NO_PYTHON
python --version
if exist ".venv\Scripts\python.exe" goto CHECK_ENV
echo [ChocoLab] Creando entorno virtual...
python -m venv .venv
if errorlevel 1 goto ENV_ERROR

:CHECK_ENV
if not exist ".venv\Scripts\python.exe" goto ENV_ERROR
echo [ChocoLab] Verificando bibliotecas...
".venv\Scripts\python.exe" -c "import streamlit,numpy,pandas,plotly" >nul 2>nul
if not errorlevel 1 goto RUN_APP
echo [ChocoLab] Instalando bibliotecas. Primera ejecucion: requiere internet.
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto INSTALL_ERROR

:RUN_APP
echo.
echo [ChocoLab] Iniciando servidor...
echo Abre tu navegador en http://localhost:8501
".venv\Scripts\python.exe" -m streamlit run app.py --server.headless false
if errorlevel 1 goto APP_ERROR
goto FIN

:NO_PYTHON
echo [ERROR] Python no esta disponible en PATH.
echo Prueba: py --version, o reinstala Python habilitando Add to PATH.
goto FAIL
:ENV_ERROR
echo [ERROR] No fue posible crear o localizar el entorno virtual.
goto FAIL
:INSTALL_ERROR
echo [ERROR] No fue posible instalar las dependencias.
echo Revisa la salida de pip anterior. Algunas librerias pueden tardar en admitir Python 3.14.
goto FAIL
:APP_ERROR
echo [ERROR] Streamlit termino con un error. Revisa el mensaje anterior.
goto FAIL
:FAIL
echo.
echo La ventana permanecera abierta para que puedas copiar el error.
pause
exit /b 1
:FIN
echo.
echo [ChocoLab] Servidor cerrado.
pause
