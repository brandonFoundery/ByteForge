@echo off
echo Starting FY.WB.Midway Upload Service with Docker...
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)

echo Creating network if it doesn't exist...
docker network create fy-wb-network 2>nul

echo.
echo Starting Upload Service and dependencies...
echo This will start:
echo - Upload Service API (Port 5003)
echo - MinIO Object Storage (Port 9000, Console: 9001)
echo - SQL Server Database (Port 1433)
echo - Redis Cache (Port 6379)
echo.

REM Start the main services first
echo Starting main infrastructure...
docker-compose up -d sqlserver redis

REM Wait a moment for services to initialize
echo Waiting for services to initialize...
timeout /t 10 /nobreak >nul

REM Start the upload service
echo Starting Upload Service...
docker-compose -f docker-compose.upload.yml up --build

echo.
echo Upload Service is now running!
echo.
echo Access points:
echo - Upload API: http://localhost:5003
echo - Swagger Documentation: http://localhost:5003
echo - MinIO Console: http://localhost:9001 (admin/minioadmin123)
echo - Health Check: http://localhost:5003/health
echo.
echo Press Ctrl+C to stop the services
pause
