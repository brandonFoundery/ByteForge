@echo off
echo ========================================
echo   Claude Code Log Monitor
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Check if rich is installed, install if not
python -c "import rich" >nul 2>&1
if errorlevel 1 (
    echo Installing required dependencies...
    pip install rich
    if errorlevel 1 (
        echo ERROR: Failed to install rich library
        echo Please run: pip install rich
        pause
        exit /b 1
    )
)

echo Starting log monitor...
echo Press Ctrl+C to stop monitoring
echo.

REM Run the log monitor
python log_monitor.py

pause
