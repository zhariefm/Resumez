@echo off
title Resumez - AI Resume Tailoring Tool (Flask)
cd /d "%~dp0"

echo ========================================================
echo     Resumez - AI Company-Tailored Resume Engine (Flask)
echo ========================================================
echo.

set "PY_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"

if exist "%PY_EXE%" (
    echo Starting Flask Server at http://localhost:5000 using Python 3.12...
    "%PY_EXE%" app.py
) else (
    echo Python 3.12 was not found at standard location. Trying system python...
    python app.py
)

pause
