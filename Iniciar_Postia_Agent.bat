@echo off
title Postia Agent - Facebook Marketplace
cd /d "%~dp0"
echo ==========================================
echo 🚀 Iniciando Postia Agent...
echo ==========================================
echo.

:: Detectar comando Python disponible
set PYTHON_CMD=
where py >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=py
    goto :python_found
)
where python3 >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python3
    goto :python_found
)
where python >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python
    goto :python_found
)

:: Si no se encuentra Python
echo ❌ Python no esta instalado o no esta en el PATH.
echo.
echo 📥 Por favor instala Python desde: https://www.python.org/downloads/
echo    Durante la instalacion, marca la opcion "Add Python to PATH"
echo.
pause
exit /b 1

:python_found
echo ✅ Python encontrado: %PYTHON_CMD%

:: Verificar si existe el entorno virtual
if not exist "venv\Scripts\activate.bat" (
    echo 📦 Creando entorno virtual...
    %PYTHON_CMD% -m venv venv
    if errorlevel 1 (
        echo ❌ Error al crear entorno virtual.
        pause
        exit /b 1
    )
    echo ✅ Entorno virtual creado.
)

:: Activar entorno virtual
echo 🔧 Activando entorno virtual...
call venv\Scripts\activate.bat

:: Verificar si uvicorn está instalado
%PYTHON_CMD% -c "import uvicorn" 2>nul
if errorlevel 1 (
    echo 📥 Instalando dependencias...
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Error al instalar dependencias.
        pause
        exit /b 1
    )
    echo ✅ Dependencias instaladas correctamente.
)

:: Definir el token del agente
set AGENT_TOKEN=un-secreto-tuyo

echo.
echo ==========================================
echo 🌐 Servidor iniciando en http://127.0.0.1:5050
echo ==========================================
echo.

:: Ejecutar el servidor FastAPI
uvicorn main:app --host 127.0.0.1 --port 5050

echo.
echo ==========================================
echo 🧠 Postia Agent finalizado.
echo Presiona una tecla para cerrar...
pause >nul
