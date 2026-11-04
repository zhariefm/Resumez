$pyPath = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"

if (Test-Path $pyPath) {
    Write-Host "Starting Resumez at http://localhost:5000 with Python 3.12..." -ForegroundColor Cyan
    & $pyPath app.py
} else {
    Write-Host "Starting Resumez at http://localhost:5000 with system python..." -ForegroundColor Cyan
    python app.py
}
