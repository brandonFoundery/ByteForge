@echo off
REM ============================================================================
REM FY.WB.Midway Documentation Quick Start
REM ============================================================================
REM Quick launcher for the documentation viewer from project root
REM ============================================================================

title FY.WB.Midway Documentation Quick Start

echo.
echo ========================================================================
echo  FY.WB.Midway Documentation Quick Start
echo ========================================================================
echo.
echo  Launching documentation viewer...
echo.

REM Check if we're in the project root
if not exist "Requirements_Generation_System" (
    echo [ERROR] This script must be run from the FY.WB.Midway project root directory.
    echo.
    echo Expected directory structure:
    echo   FY.WB.Midway\
    echo   ├── Requirements_Generation_System\
    echo   ├── generated_documents\
    echo   └── start_documentation.bat (this file)
    echo.
    pause
    exit /b 1
)

REM Change to the Requirements_Generation_System directory
cd Requirements_Generation_System

REM Check if the documentation viewer script exists
if not exist "start_docs_viewer.bat" (
    echo [ERROR] Documentation viewer script not found!
    echo Expected: Requirements_Generation_System\start_docs_viewer.bat
    echo.
    pause
    exit /b 1
)

REM Launch the documentation viewer
echo [INFO] Starting documentation viewer...
echo.
call start_docs_viewer.bat

REM Return to original directory when done
cd ..

echo.
echo Documentation viewer session ended.
pause
