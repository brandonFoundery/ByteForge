@echo off
echo Creating FY.WB.Midway Container Package...
echo.

REM Remove existing files
if exist "FY.WB.Midway-Container-Package.zip" del "FY.WB.Midway-Container-Package.zip"

REM Create zip file using PowerShell
powershell -NoProfile -ExecutionPolicy Bypass -Command "Compress-Archive -Path 'FrontEnd', 'BackEnd', 'Infrastructure', 'docker-compose.yml', 'docker-compose.override.yml', 'Dockerfile.backend', 'Dockerfile.frontend', 'README_DOCKER.md', 'README_STARTUP_ISSUES.md' -DestinationPath 'FY.WB.Midway-Container-Package.zip' -CompressionLevel Optimal"

if exist "FY.WB.Midway-Container-Package.zip" (
    echo.
    echo ✅ ZIP package created successfully: FY.WB.Midway-Container-Package.zip
    dir "FY.WB.Midway-Container-Package.zip"
) else (
    echo.
    echo ❌ Failed to create ZIP package
)

if exist "FY.WB.Midway-Container-Package.tar.gz" (
    echo.
    echo ✅ TAR.GZ package available: FY.WB.Midway-Container-Package.tar.gz
    dir "FY.WB.Midway-Container-Package.tar.gz"
)

echo.
echo Package creation complete!
pause