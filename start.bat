@echo off
title Dead Time B2B — Enterprise Launcher
color 0B
cls

echo.
echo  ================================================================
echo   D E A D   T I M E   B 2 B
echo   Workflow Intelligence ^& Automation Engine  v4.0
echo  ================================================================
echo.
echo  [1/3] Starting Backend API (Port 8002)...
echo.

:: Start the FastAPI backend
cd /d "%~dp0backend"
start "Dead Time Backend" cmd /k "python -m uvicorn main:app --host 0.0.0.0 --port 8002 --reload"

echo  [OK] Backend starting on http://localhost:8002
echo.

:: Wait for backend to boot
timeout /t 3 /nobreak > nul

echo  [2/3] Starting Frontend Dashboard (Port 3000)...
echo.

:: Start the Next.js frontend
cd /d "%~dp0frontend"
start "Dead Time Frontend" cmd /k "npm.cmd run dev"

echo  [OK] Frontend starting on http://localhost:3000
echo.

:: Wait for frontend to boot
timeout /t 5 /nobreak > nul

echo  [3/3] Opening Dashboard in Browser...
echo.

:: Open the dashboard
start "" "http://localhost:3000"

echo.
echo  ================================================================
echo   READY! Dead Time B2B is running.
echo  ================================================================
echo.
echo   Dashboard:    http://localhost:3000
echo   API Docs:     http://localhost:8002/docs
echo   Backend API:  http://localhost:8002
echo.
echo   TIP: Click "Seed Demo Data" in the header to load
echo        a realistic enterprise demonstration dataset.
echo.
echo   Press any key to stop all services...
echo.
pause > nul

:: Kill both servers
taskkill /FI "WINDOWTITLE eq Dead Time Backend*" /F > nul 2>&1
taskkill /FI "WINDOWTITLE eq Dead Time Frontend*" /F > nul 2>&1
echo  Services stopped. Goodbye!
timeout /t 2 /nobreak > nul
