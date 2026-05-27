@echo off
chcp 65001 >nul
title Sistema de Gestion de Proyectos OATI
color 0A

echo.
echo  ============================================================
echo   SISTEMA DE GESTION DE PROYECTOS - OATI
echo   Universidad Distrital Francisco Jose de Caldas
echo  ============================================================
echo.

cd /d "%~dp0"

:: Verificar Node.js
where node >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Node.js no esta instalado. Descarguelo de https://nodejs.org
    pause
    exit /b 1
)

:: Verificar Python
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python no esta instalado. Descarguelo de https://python.org
    pause
    exit /b 1
)

echo [1/4] Instalando dependencias del backend...
cd backend
if not exist ".env" (
    copy .env.example .env >nul 2>&1
)
python -m pip install -r requirements.txt -q
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Fallo la instalacion de dependencias Python.
    pause
    exit /b 1
)
:: Pillow para logos (opcional; en Python 3.14+ usar version 12+)
python -m pip install "Pillow>=12.0.0" -q 2>nul
cd ..

echo [2/4] Instalando dependencias del frontend...
cd frontend
if not exist "node_modules\" (
    call npm install
)
cd ..

echo [3/4] Iniciando servidor backend (puerto 8000)...
:: Cerrar instancias anteriores del backend (incluye workers huérfanos de uvicorn)
powershell -NoProfile -Command "Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }; Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | Where-Object { $_.CommandLine -match 'uvicorn.*--port 8000' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }"
timeout /t 2 /nobreak >nul
start "OATI Backend" cmd /k "cd /d %~dp0backend && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

echo [4/4] Iniciando servidor frontend (puerto 4200)...
timeout /t 3 /nobreak >nul
start "OATI Frontend" cmd /k "cd /d %~dp0frontend && npm start"

echo.
echo  ============================================================
echo   Sistema iniciado correctamente!
echo.
echo   Frontend:  http://localhost:4200
echo   Backend:   http://localhost:8000
echo   Swagger:   http://localhost:8000/api/docs
echo.
echo   Usuarios de prueba:
echo     Admin:   admin / admin123
echo     General: general / general123
echo  ============================================================
echo.

timeout /t 5 /nobreak >nul
start http://localhost:4200

echo Presione cualquier tecla para cerrar esta ventana...
echo (Los servidores seguiran ejecutandose en ventanas separadas)
pause >nul
