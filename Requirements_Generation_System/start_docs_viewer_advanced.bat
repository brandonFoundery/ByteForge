@echo off
REM ============================================================================
REM FY.WB.Midway Advanced Documentation Viewer Startup Script
REM ============================================================================
REM Advanced version with options for port selection, auto-refresh, and more
REM ============================================================================

setlocal enabledelayedexpansion

title FY.WB.Midway Advanced Documentation Viewer

:main_menu
cls
echo.
echo ========================================================================
echo  FY.WB.Midway Advanced Documentation Viewer
echo ========================================================================
echo.
echo  Choose an option:
echo.
echo  1. Start Documentation Viewer (Default - Port 8000)
echo  2. Start Documentation Viewer (Custom Port)
echo  3. Update Documentation from Generated Files Only
echo  4. Start with Auto-Browser Opening
echo  5. Start in Strict Mode (Warnings as Errors)
echo  6. View Server Status
echo  7. Install/Update MkDocs Dependencies
echo  8. Exit
echo.
set /p choice="Enter your choice (1-8): "

if "%choice%"=="1" goto start_default
if "%choice%"=="2" goto start_custom_port
if "%choice%"=="3" goto update_docs_only
if "%choice%"=="4" goto start_with_browser
if "%choice%"=="5" goto start_strict
if "%choice%"=="6" goto check_status
if "%choice%"=="7" goto install_deps
if "%choice%"=="8" goto exit_script

echo Invalid choice. Please try again.
timeout /t 2 >nul
goto main_menu

:start_default
set PORT=8000
set EXTRA_ARGS=
goto start_server

:start_custom_port
echo.
set /p PORT="Enter port number (default 8000): "
if "%PORT%"=="" set PORT=8000
set EXTRA_ARGS=
goto start_server

:start_with_browser
set PORT=8000
set EXTRA_ARGS=
set OPEN_BROWSER=1
goto start_server

:start_strict
set PORT=8000
set EXTRA_ARGS=--strict
goto start_server

:update_docs_only
echo.
echo ========================================================================
echo  Updating Documentation Files
echo ========================================================================
echo.
call :update_documentation
echo.
echo Documentation update complete!
echo.
pause
goto main_menu

:check_status
echo.
echo ========================================================================
echo  Checking Server Status
echo ========================================================================
echo.
netstat -an | findstr ":8000" >nul
if errorlevel 1 (
    echo [INFO] No server running on port 8000
) else (
    echo [INFO] Server appears to be running on port 8000
)
echo.
netstat -an | findstr ":8001" >nul
if errorlevel 1 (
    echo [INFO] No server running on port 8001
) else (
    echo [INFO] Server appears to be running on port 8001
)
echo.
pause
goto main_menu

:install_deps
echo.
echo ========================================================================
echo  Installing/Updating MkDocs Dependencies
echo ========================================================================
echo.
echo Installing MkDocs and required plugins...
pip install --upgrade mkdocs mkdocs-material mkdocs-mermaid2-plugin
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies!
    pause
    goto main_menu
)
echo.
echo [SUCCESS] Dependencies installed/updated successfully!
echo.
pause
goto main_menu

:start_server
echo.
echo ========================================================================
echo  Starting Documentation Server
echo ========================================================================
echo.

REM Validate environment
call :validate_environment
if errorlevel 1 goto main_menu

REM Update documentation
call :update_documentation

REM Change to MkDocs directory
if not exist "fy-wb-midway-docs" (
    echo [ERROR] MkDocs site directory not found!
    pause
    goto main_menu
)

cd fy-wb-midway-docs

echo [INFO] Starting MkDocs server on port %PORT%...
echo.
echo ========================================================================
echo  Documentation Server Active
echo ========================================================================
echo.
echo  Server URL: http://127.0.0.1:%PORT%/
echo  Server will auto-reload when files change
echo.
echo  Press Ctrl+C to stop the server
echo  Close this window to stop the server
echo.
echo ========================================================================
echo.

REM Open browser if requested
if "%OPEN_BROWSER%"=="1" (
    echo [INFO] Opening browser...
    start "" "http://127.0.0.1:%PORT%/"
)

REM Start the server
python -m mkdocs serve --dev-addr=127.0.0.1:%PORT% %EXTRA_ARGS%

echo.
echo [INFO] Documentation server stopped.
cd ..
pause
goto main_menu

:validate_environment
REM Check if we're in the correct directory
if not exist "fy-wb-midway-docs\mkdocs.yml" (
    echo [ERROR] MkDocs configuration not found!
    echo Please run this script from the Requirements_Generation_System directory.
    pause
    exit /b 1
)

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python from https://python.org/downloads/
    pause
    exit /b 1
)

REM Check MkDocs
python -m mkdocs --version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] MkDocs not found. Installing...
    pip install mkdocs mkdocs-material mkdocs-mermaid2-plugin
    if errorlevel 1 (
        echo [ERROR] Failed to install MkDocs!
        pause
        exit /b 1
    )
)

exit /b 0

:update_documentation
echo [INFO] Updating documentation from generated files...
if exist "setup_mkdocs_site.py" (
    python setup_mkdocs_site.py
    if errorlevel 1 (
        echo [WARNING] Failed to update some documentation files.
    ) else (
        echo [SUCCESS] Documentation files updated successfully!
    )
) else (
    echo [INFO] Setup script not found, using existing files.
)
exit /b 0

:exit_script
echo.
echo Thank you for using FY.WB.Midway Documentation Viewer!
echo.
exit /b 0
