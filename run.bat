@echo off
title Resumez - AI Resume Tailoring Tool
cd /d "%~dp0"

echo ========================================================
echo     Resumez - AI Company-Tailored Resume Engine
echo ========================================================
echo.

set "PY_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"

if exist "%PY_EXE%" (
    echo Starting Streamlit App using Python 3.12...
    "%PY_EXE%" -m streamlit run app.py
) else (
    echo Python 3.12 was not found at standard location. Trying system python...
    python -m streamlit run app.py
)

pause
