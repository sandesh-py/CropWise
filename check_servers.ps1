# Check if CropWise servers are running
Write-Host "Checking CropWise servers..." -ForegroundColor Cyan
Write-Host ""

# Check Backend (port 8000)
try {
    $backend = Test-NetConnection -ComputerName localhost -Port 8000 -WarningAction SilentlyContinue
    if ($backend.TcpTestSucceeded) {
        Write-Host "✅ Backend Server: RUNNING on port 8000" -ForegroundColor Green
        Write-Host "   URL: http://localhost:8000" -ForegroundColor Gray
    } else {
        Write-Host "❌ Backend Server: NOT RUNNING" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Backend Server: NOT RUNNING" -ForegroundColor Red
}

# Check Frontend (port 5174)
try {
    $frontend = Test-NetConnection -ComputerName localhost -Port 5174 -WarningAction SilentlyContinue
    if ($frontend.TcpTestSucceeded) {
        Write-Host "✅ Frontend Server: RUNNING on port 5174" -ForegroundColor Green
        Write-Host "   URL: http://localhost:5174" -ForegroundColor Gray
    } else {
        Write-Host "❌ Frontend Server: NOT RUNNING" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Frontend Server: NOT RUNNING" -ForegroundColor Red
}

Write-Host ""
Write-Host "To start servers, run: .\start_servers.ps1" -ForegroundColor Yellow

