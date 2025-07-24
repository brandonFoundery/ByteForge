@echo off
setlocal

REM Quick test runner - runs tests without full output
set "SCRIPT_DIR=%~dp0"
set "PROJECT_DIR=%SCRIPT_DIR%.."

echo 🚀 Quick Test Run
echo ==================

cd /d "%PROJECT_DIR%"
if errorlevel 1 exit /b 1

REM Run tests quietly and show just the summary
dotnet test --configuration Debug --verbosity quiet --no-build --logger "console;verbosity=minimal" >nul 2>&1

if errorlevel 1 (
    echo ❌ Some tests failed. Run 'scripts\run-tests.bat -v' for details.
    exit /b 1
) else (
    echo ✅ All tests passed!
    exit /b 0
)