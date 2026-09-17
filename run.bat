@echo off
setlocal
cd /d "%~dp0"

echo.
echo ========================================
echo   Tokyo Revengers Reader - Startup
echo ========================================
echo.

if exist ".venv\Scripts\python.exe" goto install

echo [1/3] Creating virtual environment...
where py >nul 2>nul
if errorlevel 1 goto use_python

py -m venv .venv
goto check_venv

:use_python
python -m venv .venv

:check_venv
if errorlevel 1 goto error

:install
echo [2/3] Installing/updating dependencies...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto error

echo.
echo [3/3] Starting application...
echo.
echo Open this address in your browser:
echo http://127.0.0.1:8000
echo.
echo Press CTRL+C in this window to stop the server.
echo.

".venv\Scripts\python.exe" -m uvicorn app.main:app --reload
exit /b 0

:error
echo.
echo ERROR: The application could not be started.
echo Make sure Python is installed and available as either "py" or "python".
echo.
pause
exit /b 1
