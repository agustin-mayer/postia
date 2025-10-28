@echo off
title Postia Agent - Facebook Marketplace
cd /d "%~dp0"
echo ==========================================
echo 🚀 Iniciando Postia Agent...
echo ==========================================
echo.

:: Activar entorno virtual si lo creaste (ajustá la ruta si el venv está dentro de esta carpeta)
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo ⚠️ No se encontro entorno virtual. Se usara Python global.
)

:: Definir el token del agente
set AGENT_TOKEN=un-secreto-tuyo

:: Ejecutar el servidor FastAPI
uvicorn main:app --host 127.0.0.1 --port 5050

echo.
echo ==========================================
echo 🧠 Postia Agent finalizado.
echo Presiona una tecla para cerrar...
pause >nul
