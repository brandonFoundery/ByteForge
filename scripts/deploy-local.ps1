# deploy-local.ps1 - Local Deployment Script
# Deploys the application to local Docker environment

[CmdletBinding()]
param(
    [switch]$Fresh,
    [switch]$SkipBuild,
    [switch]$SkipTest,
    [string]$Environment = "Development",
    [string[]]$Services = @()
)

Write-Host "🚀 Deploying FY.WB.Midway Locally" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Green

$ErrorActionPreference = "Stop"

# Helper function to log with timestamp
function Write-LogMessage {
    param([string]$Message, [string]$Color = "White")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$timestamp] $Message" -ForegroundColor $Color
}

# Clean up existing deployment
function Remove-ExistingDeployment {
    if ($Fresh) {
        Write-LogMessage "🧹 Cleaning up existing deployment..." "Yellow"
        
        # Stop and remove containers
        docker-compose down --volumes --remove-orphans
        
        # Remove unused images
        docker system prune -f
        
        Write-LogMessage "✅ Cleanup completed" "Green"
    }
}

# Build application
function Build-Application {
    if ($SkipBuild) {
        Write-LogMessage "⏭️  Skipping build phase" "Blue"
        return
    }
    
    Write-LogMessage "🔨 Building application..." "Yellow"
    
    # Build backend
    Write-LogMessage "   Building backend..." "Gray"
    Push-Location BackEnd
    dotnet build FY.WB.Midway.sln --configuration Release --verbosity minimal
    if ($LASTEXITCODE -ne 0) {
        throw "Backend build failed"
    }
    Pop-Location
    
    # Build frontend
    Write-LogMessage "   Building frontend..." "Gray"
    Push-Location FrontEnd
    npm run build
    if ($LASTEXITCODE -ne 0) {
        throw "Frontend build failed"
    }
    Pop-Location
    
    Write-LogMessage "✅ Application built successfully" "Green"
}

# Run tests
function Test-Application {
    if ($SkipTest) {
        Write-LogMessage "⏭️  Skipping tests" "Blue"
        return
    }
    
    Write-LogMessage "🧪 Running tests..." "Yellow"
    
    # Backend tests
    Write-LogMessage "   Running backend tests..." "Gray"
    Push-Location BackEnd
    dotnet test FY.WB.Midway.sln --configuration Release --verbosity minimal --no-build
    if ($LASTEXITCODE -ne 0) {
        Write-LogMessage "⚠️  Backend tests failed - continuing deployment" "Yellow"
    }
    Pop-Location
    
    # Frontend tests
    Write-LogMessage "   Running frontend tests..." "Gray"
    Push-Location FrontEnd
    npm test -- --watchAll=false --coverage=false
    if ($LASTEXITCODE -ne 0) {
        Write-LogMessage "⚠️  Frontend tests failed - continuing deployment" "Yellow"
    }
    Pop-Location
    
    Write-LogMessage "✅ Tests completed" "Green"
}

# Build Docker images
function Build-DockerImages {
    Write-LogMessage "🐳 Building Docker images..." "Yellow"
    
    if ($Services.Count -gt 0) {
        $serviceArgs = $Services -join " "
        docker-compose build $serviceArgs
    } else {
        docker-compose build
    }
    
    if ($LASTEXITCODE -ne 0) {
        throw "Docker build failed"
    }
    
    Write-LogMessage "✅ Docker images built successfully" "Green"
}

# Deploy services
function Deploy-Services {
    Write-LogMessage "📦 Deploying services..." "Yellow"
    
    # Set environment variables
    $env:ASPNETCORE_ENVIRONMENT = $Environment
    $env:COMPOSE_PROJECT_NAME = "fywbmidway"
    
    # Start infrastructure services first
    Write-LogMessage "   Starting infrastructure services..." "Gray"
    docker-compose up -d sqlserver redis
    
    # Wait for database
    Write-LogMessage "   Waiting for database to be ready..." "Gray"
    $maxAttempts = 30
    $attempt = 0
    
    do {
        $attempt++
        Start-Sleep 3
        $result = docker exec fy-wb-midway-sqlserver /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P "StrongPassword123!" -Q "SELECT 1" 2>$null
        if ($result -match "1") {
            break
        }
        Write-LogMessage "   Database startup attempt $attempt/$maxAttempts..." "Gray"
    } while ($attempt -lt $maxAttempts)
    
    if ($attempt -eq $maxAttempts) {
        throw "Database failed to start"
    }
    
    # Run database migrations
    Write-LogMessage "   Running database migrations..." "Gray"
    Push-Location BackEnd
    $connectionString = "Server=localhost,1433;Database=FYWBMidway;User Id=sa;Password=StrongPassword123!;TrustServerCertificate=True;"
    $env:ConnectionStrings__DefaultConnection = $connectionString
    dotnet ef database update --project FY.WB.Midway.Infrastructure --startup-project FY.WB.Midway
    Pop-Location
    
    # Start application services
    Write-LogMessage "   Starting application services..." "Gray"
    if ($Services.Count -gt 0) {
        $serviceArgs = $Services -join " "
        docker-compose up -d $serviceArgs
    } else {
        docker-compose up -d backend frontend nginx
    }
    
    if ($LASTEXITCODE -ne 0) {
        throw "Service deployment failed"
    }
    
    Write-LogMessage "✅ Services deployed successfully" "Green"
}

# Verify deployment
function Test-Deployment {
    Write-LogMessage "🔍 Verifying deployment..." "Yellow"
    
    # Health check URLs
    $healthChecks = @(
        @{ Name = "Backend API"; Url = "http://localhost:5002/health"; Timeout = 60 }
        @{ Name = "Frontend"; Url = "http://localhost:4000"; Timeout = 30 }
        @{ Name = "Nginx Proxy"; Url = "http://localhost:80"; Timeout = 30 }
    )
    
    foreach ($check in $healthChecks) {
        Write-LogMessage "   Checking $($check.Name)..." "Gray"
        $maxAttempts = [Math]::Ceiling($check.Timeout / 5)
        $attempt = 0
        $success = $false
        
        do {
            $attempt++
            try {
                $response = Invoke-WebRequest -Uri $check.Url -TimeoutSec 5 -UseBasicParsing -ErrorAction SilentlyContinue
                if ($response.StatusCode -eq 200) {
                    $success = $true
                    break
                }
            } catch {
                # Ignore errors and retry
            }
            
            if ($attempt -lt $maxAttempts) {
                Start-Sleep 5
            }
        } while ($attempt -lt $maxAttempts)
        
        if ($success) {
            Write-LogMessage "   ✅ $($check.Name) is healthy" "Green"
        } else {
            Write-LogMessage "   ⚠️  $($check.Name) health check failed" "Yellow"
        }
    }
}

# Display deployment info
function Show-DeploymentInfo {
    Write-LogMessage ""
    Write-LogMessage "🎉 Deployment completed!" "Green"
    Write-LogMessage ""
    Write-LogMessage "Application URLs:" "Yellow"
    Write-LogMessage "  🌐 Frontend:     http://localhost:4000" "White"
    Write-LogMessage "  🌐 Frontend:     http://localhost:80 (via Nginx)" "White"
    Write-LogMessage "  🔧 Backend API:  http://localhost:5002" "White"
    Write-LogMessage "  📚 API Docs:     http://localhost:5002/swagger" "White"
    Write-LogMessage "  💾 Database:     localhost:1433 (sa/StrongPassword123!)" "White"
    Write-LogMessage "  🗃️  Redis:        localhost:6379" "White"
    Write-LogMessage ""
    Write-LogMessage "Useful commands:" "Yellow"
    Write-LogMessage "  📊 View logs:    docker-compose logs -f [service]" "White"
    Write-LogMessage "  🔄 Restart:      docker-compose restart [service]" "White"
    Write-LogMessage "  🛑 Stop:         docker-compose down" "White"
    Write-LogMessage "  🔧 Debug:        docker exec -it [container] /bin/bash" "White"
    Write-LogMessage ""
    Write-LogMessage "Container status:" "Yellow"
    docker-compose ps
}

# Main execution
try {
    Remove-ExistingDeployment
    Build-Application
    Test-Application
    Build-DockerImages
    Deploy-Services
    Test-Deployment
    Show-DeploymentInfo
} catch {
    Write-LogMessage "❌ Deployment failed: $($_.Exception.Message)" "Red"
    Write-LogMessage ""
    Write-LogMessage "Troubleshooting:" "Yellow"
    Write-LogMessage "  1. Check logs: docker-compose logs" "White"
    Write-LogMessage "  2. Check status: docker-compose ps" "White"
    Write-LogMessage "  3. Clean up: docker-compose down --volumes" "White"
    exit 1
}