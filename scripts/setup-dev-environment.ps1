# setup-dev-environment.ps1 - Development Environment Setup Script
# Initializes the development environment for FY.WB.Midway

[CmdletBinding()]
param(
    [switch]$SkipDocker,
    [switch]$SkipDatabase,
    [switch]$SkipFrontend,
    [switch]$Force
)

Write-Host "🚀 Setting up FY.WB.Midway Development Environment" -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Green

# Check prerequisites
function Test-Prerequisites {
    Write-Host "📋 Checking prerequisites..." -ForegroundColor Yellow
    
    $missing = @()
    
    # Check Docker
    if (-not $SkipDocker) {
        try {
            docker --version | Out-Null
        } catch {
            $missing += "Docker Desktop"
        }
    }
    
    # Check .NET SDK
    try {
        dotnet --version | Out-Null
    } catch {
        $missing += ".NET 8.0 SDK"
    }
    
    # Check Node.js
    if (-not $SkipFrontend) {
        try {
            node --version | Out-Null
        } catch {
            $missing += "Node.js 18+"
        }
    }
    
    if ($missing.Count -gt 0) {
        Write-Host "❌ Missing prerequisites:" -ForegroundColor Red
        $missing | ForEach-Object { Write-Host "   - $_" -ForegroundColor Red }
        exit 1
    }
    
    Write-Host "✅ All prerequisites found" -ForegroundColor Green
}

# Setup environment variables
function Set-EnvironmentVariables {
    Write-Host "🔧 Setting up environment variables..." -ForegroundColor Yellow
    
    $envFile = ".env"
    if (-not (Test-Path $envFile) -or $Force) {
        @"
# FY.WB.Midway Development Environment Variables
ASPNETCORE_ENVIRONMENT=Development
COMPOSE_PROJECT_NAME=fywbmidway
DOCKER_BUILDKIT=1
COMPOSE_DOCKER_CLI_BUILD=1

# Database
SA_PASSWORD=StrongPassword123!
REDIS_PASSWORD=development-redis-password

# Authentication
JWT_SECRET=development-jwt-secret-key-change-in-production-must-be-at-least-256-bits

# External Services (Optional - leave empty for development)
COSMOS_CONNECTION_STRING=
BLOB_STORAGE_CONNECTION_STRING=
SENDGRID_API_KEY=
APPLICATION_INSIGHTS_KEY=
"@ | Out-File -FilePath $envFile -Encoding UTF8
        
        Write-Host "✅ Created $envFile with default development settings" -ForegroundColor Green
    } else {
        Write-Host "ℹ️  $envFile already exists, skipping..." -ForegroundColor Blue
    }
}

# Initialize Docker environment
function Initialize-Docker {
    if ($SkipDocker) {
        Write-Host "⏭️  Skipping Docker setup" -ForegroundColor Blue
        return
    }
    
    Write-Host "🐳 Initializing Docker environment..." -ForegroundColor Yellow
    
    # Build containers
    Write-Host "   Building containers..." -ForegroundColor Gray
    docker-compose build --no-cache
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Docker build failed" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "✅ Docker containers built successfully" -ForegroundColor Green
}

# Setup database
function Initialize-Database {
    if ($SkipDatabase) {
        Write-Host "⏭️  Skipping database setup" -ForegroundColor Blue
        return
    }
    
    Write-Host "💾 Initializing database..." -ForegroundColor Yellow
    
    # Start SQL Server container
    Write-Host "   Starting SQL Server..." -ForegroundColor Gray
    docker-compose up -d sqlserver
    
    # Wait for SQL Server to be ready
    Write-Host "   Waiting for SQL Server to be ready..." -ForegroundColor Gray
    $maxAttempts = 30
    $attempt = 0
    
    do {
        $attempt++
        Start-Sleep 5
        $result = docker exec fy-wb-midway-sqlserver /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P "StrongPassword123!" -Q "SELECT 1" 2>$null
        if ($result -match "1") {
            break
        }
        Write-Host "   Attempt $attempt/$maxAttempts..." -ForegroundColor Gray
    } while ($attempt -lt $maxAttempts)
    
    if ($attempt -eq $maxAttempts) {
        Write-Host "❌ SQL Server failed to start" -ForegroundColor Red
        exit 1
    }
    
    # Run database migrations
    Write-Host "   Running database migrations..." -ForegroundColor Gray
    Push-Location BackEnd
    dotnet ef database update --project FY.WB.Midway.Infrastructure --startup-project FY.WB.Midway
    Pop-Location
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "⚠️  Database migrations may have failed - check manually" -ForegroundColor Yellow
    } else {
        Write-Host "✅ Database initialized successfully" -ForegroundColor Green
    }
}

# Setup frontend
function Initialize-Frontend {
    if ($SkipFrontend) {
        Write-Host "⏭️  Skipping frontend setup" -ForegroundColor Blue
        return
    }
    
    Write-Host "🌐 Setting up frontend..." -ForegroundColor Yellow
    
    Push-Location FrontEnd
    
    # Install dependencies
    Write-Host "   Installing npm packages..." -ForegroundColor Gray
    npm ci
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Frontend dependency installation failed" -ForegroundColor Red
        Pop-Location
        exit 1
    }
    
    # Build frontend
    Write-Host "   Building frontend..." -ForegroundColor Gray
    npm run build
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "⚠️  Frontend build failed - check manually" -ForegroundColor Yellow
    } else {
        Write-Host "✅ Frontend setup completed" -ForegroundColor Green
    }
    
    Pop-Location
}

# Create development certificates
function Create-DevCertificates {
    Write-Host "🔒 Setting up development certificates..." -ForegroundColor Yellow
    
    # .NET development certificates
    dotnet dev-certs https --trust
    
    Write-Host "✅ Development certificates configured" -ForegroundColor Green
}

# Main execution
try {
    Test-Prerequisites
    Set-EnvironmentVariables
    Create-DevCertificates
    Initialize-Docker
    Initialize-Database
    Initialize-Frontend
    
    Write-Host ""
    Write-Host "🎉 Development environment setup complete!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "  1. Run: docker-compose up -d" -ForegroundColor White
    Write-Host "  2. Navigate to: http://localhost:4000 (Frontend)" -ForegroundColor White
    Write-Host "  3. API docs: http://localhost:5002/swagger (Backend)" -ForegroundColor White
    Write-Host "  4. Database: localhost:1433 (sa/StrongPassword123!)" -ForegroundColor White
    Write-Host ""
    Write-Host "Useful commands:" -ForegroundColor Yellow
    Write-Host "  - View logs: docker-compose logs -f" -ForegroundColor White
    Write-Host "  - Stop services: docker-compose down" -ForegroundColor White
    Write-Host "  - Rebuild: docker-compose build --no-cache" -ForegroundColor White
    Write-Host ""
} catch {
    Write-Host "❌ Setup failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}