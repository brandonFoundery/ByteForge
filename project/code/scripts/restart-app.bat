@echo off
setlocal enabledelayedexpansion

REM Colors for output (Windows)
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "NC=[0m"

REM Get script directory
set "SCRIPT_DIR=%~dp0"
set "PROJECT_DIR=%SCRIPT_DIR%.."

echo =========================================
echo      Lead Processing App Restart
echo =========================================
echo.

echo %BLUE%[%date% %time%]%NC% Project directory: %PROJECT_DIR%
echo %BLUE%[%date% %time%]%NC% Stopping any existing LeadProcessing processes...

REM Kill existing processes
taskkill /F /IM "LeadProcessing.exe" >nul 2>&1
taskkill /F /FI "IMAGENAME eq dotnet.exe" /FI "COMMANDLINE eq *LeadProcessing*" >nul 2>&1

REM Kill processes using our ports
for /f "tokens=5" %%a in ('netstat -ano ^| find ":5000 " 2^>nul') do (
    if not "%%a"=="0" (
        echo %YELLOW%[%date% %time%]%NC% Killing process %%a using port 5000
        taskkill /F /PID %%a >nul 2>&1
    )
)

for /f "tokens=5" %%a in ('netstat -ano ^| find ":7001 " 2^>nul') do (
    if not "%%a"=="0" (
        echo %YELLOW%[%date% %time%]%NC% Killing process %%a using port 7001
        taskkill /F /PID %%a >nul 2>&1
    )
)

echo %GREEN%[%date% %time%]%NC% Process cleanup completed
echo.

REM Change to project directory
cd /d "%PROJECT_DIR%"
if errorlevel 1 (
    echo %RED%[%date% %time%]%NC% Failed to change to project directory: %PROJECT_DIR%
    pause
    exit /b 1
)

REM Build the application
echo %BLUE%[%date% %time%]%NC% Building the application...
dotnet build --configuration Debug --verbosity minimal
if errorlevel 1 (
    echo %RED%[%date% %time%]%NC% Build failed!
    pause
    exit /b 1
)
echo %GREEN%[%date% %time%]%NC% Build completed successfully
echo.

REM Update database
echo %BLUE%[%date% %time%]%NC% Updating database...
dotnet ef database update --verbosity minimal
if errorlevel 1 (
    echo %YELLOW%[%date% %time%]%NC% Database update failed or no migrations needed
) else (
    echo %GREEN%[%date% %time%]%NC% Database updated successfully
)
echo.

REM Start the application
echo %BLUE%[%date% %time%]%NC% Starting the application...
echo %BLUE%[%date% %time%]%NC% The application will be available at:
echo %BLUE%[%date% %time%]%NC%   - HTTP:  http://localhost:5000
echo %BLUE%[%date% %time%]%NC%   - HTTPS: https://localhost:7001
echo %BLUE%[%date% %time%]%NC%   - Hangfire Dashboard: https://localhost:7001/hangfire
echo.
echo %BLUE%[%date% %time%]%NC% Press Ctrl+C to stop the application
echo %BLUE%[%date% %time%]%NC% Starting in 3 seconds...

timeout /t 3 /nobreak >nul

REM Start the application
dotnet run --configuration Debug