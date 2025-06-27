@echo off
REM ============================================================================
REM FY.WB.Midway Documentation Viewer Startup Script
REM ============================================================================
REM This script starts the MkDocs documentation server for viewing generated
REM requirements and technical documentation in a professional web interface.
REM ============================================================================

title FY.WB.Midway Documentation Viewer

echo.
echo ========================================================================
echo  FY.WB.Midway Documentation Viewer
echo ========================================================================
echo.
echo  Starting professional documentation server...
echo.

REM Check if we're in the correct directory
if not exist "fy-wb-midway-docs\mkdocs.yml" (
    echo [ERROR] MkDocs configuration not found!
    echo.
    echo Please ensure you're running this script from the Requirements_Generation_System directory.
    echo Expected file: fy-wb-midway-docs\mkdocs.yml
    echo.
    pause
    exit /b 1
)

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH!
    echo.
    echo Please install Python and ensure it's added to your system PATH.
    echo Download from: https://python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM Check if MkDocs is installed
python -m mkdocs --version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] MkDocs is not installed!
    echo.
    echo Installing MkDocs and required dependencies...
    echo.
    pip install mkdocs mkdocs-material mkdocs-mermaid2-plugin
    if errorlevel 1 (
        echo [ERROR] Failed to install MkDocs dependencies!
        echo.
        echo Please install manually:
        echo   pip install mkdocs mkdocs-material mkdocs-mermaid2-plugin
        echo.
        pause
        exit /b 1
    )
    echo.
    echo [SUCCESS] MkDocs installed successfully!
    echo.
)

REM Update documentation from generated files
echo [INFO] Updating documentation from generated files...
echo.
if exist "setup_mkdocs_site.py" (
    python setup_mkdocs_site.py
    if errorlevel 1 (
        echo [WARNING] Failed to update documentation files.
        echo Continuing with existing files...
        echo.
    ) else (
        echo [SUCCESS] Documentation files updated!
        echo.
    )
) else (
    echo [INFO] Setup script not found, using existing documentation files.
    echo.
)

REM Change to MkDocs directory
cd fy-wb-midway-docs

REM Start the MkDocs server
echo [INFO] Starting MkDocs development server...
echo.
echo ========================================================================
echo  Documentation Server Starting
echo ========================================================================
echo.
echo  Server URL: http://127.0.0.1:8000/
echo  Server will auto-reload when files change
echo.
echo  Press Ctrl+C to stop the server
echo  Close this window to stop the server
echo.
echo ========================================================================
echo.

REM Start MkDocs server and automatically open browser
start "" "http://127.0.0.1:8000/"
python -m mkdocs serve --dev-addr=127.0.0.1:8000

REM If we get here, the server was stopped
echo.
echo ========================================================================
echo  Documentation Server Stopped
echo ========================================================================
echo.
echo The documentation server has been stopped.
echo.
pause
