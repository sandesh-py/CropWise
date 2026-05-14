@echo off
echo ========================================
echo   CropWise - Starting Servers
echo ========================================
echo.

echo Starting Backend Server (Flask) on port 8000...
start "CropWise Backend" cmd /k "cd backend && python app.py"

timeout /t 3 /nobreak > nul

echo Starting Frontend Server (Vite) on port 5174...
start "CropWise Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ========================================
echo   Servers are starting...
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5174
echo.
echo Press any key to exit this window...
echo (Servers will continue running in separate windows)
pause > nul
