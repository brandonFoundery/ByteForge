@echo off
REM ============================================================================
REM FY.WB.Midway Documentation Viewer - Quick Start
REM ============================================================================
REM Simple and reliable script to start the MkDocs documentation server
REM ============================================================================

title FY.WB.Midway Documentation Viewer

echo.
echo ========================================================================
echo  FY.WB.Midway Documentation Viewer
echo ========================================================================
echo.
echo  Starting documentation server...
echo.

REM Store the original directory
set "ORIGINAL_DIR=%CD%"

REM Navigate to the Requirements_Generation_System directory
cd /d "%~dp0Requirements_Generation_System"

REM Check if we can find the MkDocs configuration
if not exist "fy-wb-midway-docs\mkdocs.yml" (
    echo [ERROR] MkDocs configuration not found!
    echo.
    echo Expected location: %CD%\fy-wb-midway-docs\mkdocs.yml
    echo.
    echo Please ensure the documentation files are properly set up.
    echo.
    pause
    exit /b 1
)

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH!
    echo.
    echo Please install Python from: https://python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo [INFO] Python found: 
python --version

REM Check if MkDocs is installed
python -m mkdocs --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo [WARNING] MkDocs is not installed!
    echo [INFO] Installing MkDocs and required dependencies...
    echo.
    
    pip install mkdocs mkdocs-material mkdocs-mermaid2-plugin pymdown-extensions
    
    if errorlevel 1 (
        echo.
        echo [ERROR] Failed to install MkDocs dependencies!
        echo.
        echo Please try installing manually:
        echo   pip install mkdocs mkdocs-material mkdocs-mermaid2-plugin pymdown-extensions
        echo.
        pause
        exit /b 1
    )
    
    echo.
    echo [SUCCESS] MkDocs installed successfully!
)

echo.
echo [INFO] MkDocs version:
python -m mkdocs --version

REM Change to the MkDocs directory
cd fy-wb-midway-docs

echo.
echo [INFO] Starting MkDocs development server...
echo.
echo ========================================================================
echo  Documentation Server Active
echo ========================================================================
echo.
echo  Server URL: http://127.0.0.1:8000/
echo  Auto-reload: Enabled (changes will be reflected automatically)
echo.
echo  Press Ctrl+C to stop the server
echo  Close this window to stop the server
echo.
echo ========================================================================
echo.

REM Start MkDocs server and automatically open browser
echo [INFO] Opening browser...
start "" "http://127.0.0.1:8000/"

echo [INFO] Starting server...
python -m mkdocs serve --dev-addr=127.0.0.1:8000

REM If we get here, the server was stopped
echo.
echo ========================================================================
echo  Documentation Server Stopped
echo ========================================================================
echo.
echo The documentation server has been stopped.
echo You can restart it by running this script again.
echo.
pause

REM Return to original directory
cd /d "%ORIGINAL_DIR%"
