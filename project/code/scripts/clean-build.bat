@echo off
setlocal

REM Clean and rebuild the entire solution
set "SCRIPT_DIR=%~dp0"
set "PROJECT_DIR=%SCRIPT_DIR%.."

echo 🧹 Clean Build
echo ==============

cd /d "%PROJECT_DIR%"
if errorlevel 1 exit /b 1

echo Cleaning solution...
dotnet clean --verbosity minimal

echo Restoring packages...
dotnet restore --verbosity minimal

echo Building solution...
dotnet build --configuration Debug --verbosity minimal

if errorlevel 1 (
    echo ❌ Build failed!
    pause
    exit /b 1
) else (
    echo ✅ Clean build completed successfully!
)