@echo off
echo Stopping Lead Processing Application...
echo.

REM Kill processes on common ports
echo Killing processes on ports 7001, 5000, 3000...

REM Kill ASP.NET Core backend (typically runs on 7001 or 5000)
for /f "tokens=5" %%a in ('netstat -aon ^| find ":7001" ^| find "LISTENING"') do (
    echo Killing process %%a on port 7001
    taskkill /f /pid %%a >nul 2>&1
)

for /f "tokens=5" %%a in ('netstat -aon ^| find ":5000" ^| find "LISTENING"') do (
    echo Killing process %%a on port 5000
    taskkill /f /pid %%a >nul 2>&1
)

REM Kill Next.js frontend (typically runs on 3000)
for /f "tokens=5" %%a in ('netstat -aon ^| find ":3000" ^| find "LISTENING"') do (
    echo Killing process %%a on port 3000
    taskkill /f /pid %%a >nul 2>&1
)

REM Also kill any node.exe and dotnet.exe processes
echo Killing any remaining node.exe and dotnet.exe processes...
taskkill /f /im node.exe >nul 2>&1
taskkill /f /im dotnet.exe >nul 2>&1

echo.
echo All application processes have been stopped.
echo.
pause