$pyPath = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"

if (Test-Path $pyPath) {
    Write-Host "Starting Resumez Dashboard with Python 3.12..." -ForegroundColor Cyan
    & $pyPath -m streamlit run app.py
} else {
    Write-Host "Python 3.12 path not found, trying system python..." -ForegroundColor Yellow
    python -m streamlit run app.py
}

