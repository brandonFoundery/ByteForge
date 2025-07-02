@echo off
echo ╭─────────────────────────────────────────────────╮
echo │ ByteForge App Generation System                 │
echo │ Automated Code Generation with Claude Code     │
echo ╰─────────────────────────────────────────────────╯
echo.

REM Check if we're in the right directory
if not exist "config.yaml" (
    echo ERROR: config.yaml not found
    echo Please run this script from the Requirements_Generation_System directory
    pause
    exit /b 1
)

REM Try to run the Python script
python run_generation_simple.py

REM If python command fails, try python3
if %errorlevel% neq 0 (
    echo Trying python3...
    python3 run_generation_simple.py
)

REM If still fails, try py
if %errorlevel% neq 0 (
    echo Trying py...
    py run_generation_simple.py
)

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Could not run Python script
    echo Please ensure Python is installed and available in PATH
    echo.
    echo You can also run manually:
    echo   python run_generation_simple.py
    echo   or
    echo   python3 run_generation_simple.py
    echo   or  
    echo   py run_generation_simple.py
    pause
)