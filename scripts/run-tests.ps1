# run-tests.ps1 - Comprehensive Test Execution Script
# Runs all tests for the FY.WB.Midway application

[CmdletBinding()]
param(
    [ValidateSet("unit", "integration", "e2e", "all")]
    [string]$TestType = "all",
    
    [switch]$Coverage,
    [switch]$Watch,
    [switch]$Parallel,
    [switch]$Verbose,
    [string]$Filter = "",
    [string]$Output = "results"
)

Write-Host "🧪 Running FY.WB.Midway Tests" -ForegroundColor Green
Write-Host "==============================" -ForegroundColor Green

$ErrorActionPreference = "Stop"
$testResults = @{}

# Helper function to log with timestamp
function Write-TestLog {
    param([string]$Message, [string]$Color = "White")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$timestamp] $Message" -ForegroundColor $Color
}

# Setup test environment
function Initialize-TestEnvironment {
    Write-TestLog "🔧 Setting up test environment..." "Yellow"
    
    # Create output directory
    if (-not (Test-Path $Output)) {
        New-Item -ItemType Directory -Path $Output -Force | Out-Null
    }
    
    # Set test environment variables
    $env:ASPNETCORE_ENVIRONMENT = "Testing"
    $env:ConnectionStrings__DefaultConnection = "Server=localhost,1433;Database=FYWBMidwayTest;User Id=sa;Password=StrongPassword123!;TrustServerCertificate=True;"
    $env:NODE_ENV = "test"
    
    Write-TestLog "✅ Test environment initialized" "Green"
}

# Start test infrastructure
function Start-TestInfrastructure {
    Write-TestLog "🐳 Starting test infrastructure..." "Yellow"
    
    # Start only SQL Server for tests
    docker-compose up -d sqlserver
    
    # Wait for SQL Server
    $maxAttempts = 30
    $attempt = 0
    
    do {
        $attempt++
        Start-Sleep 3
        try {
            $result = docker exec fy-wb-midway-sqlserver /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P "StrongPassword123!" -Q "SELECT 1" 2>$null
            if ($result -match "1") {
                break
            }
        } catch {
            # Continue waiting
        }
        Write-TestLog "   Waiting for SQL Server... ($attempt/$maxAttempts)" "Gray"
    } while ($attempt -lt $maxAttempts)
    
    if ($attempt -eq $maxAttempts) {
        throw "SQL Server failed to start for tests"
    }
    
    # Create test database
    Write-TestLog "   Creating test database..." "Gray"
    Push-Location BackEnd
    dotnet ef database update --project FY.WB.Midway.Infrastructure --startup-project FY.WB.Midway
    Pop-Location
    
    Write-TestLog "✅ Test infrastructure ready" "Green"
}

# Run backend unit tests
function Test-BackendUnit {
    Write-TestLog "🔍 Running backend unit tests..." "Yellow"
    
    Push-Location BackEnd
    
    $testArgs = @(
        "test",
        "FY.WB.Midway.sln",
        "--configuration", "Release",
        "--filter", "Category!=Integration"
    )
    
    if ($Coverage) {
        $testArgs += @(
            "--collect:XPlat Code Coverage",
            "--results-directory", "../$Output/backend-unit"
        )
    }
    
    if ($Verbose) {
        $testArgs += @("--verbosity", "detailed")
    } else {
        $testArgs += @("--verbosity", "normal")
    }
    
    if ($Filter) {
        $testArgs += @("--filter", "$Filter")
    }
    
    if ($Parallel) {
        $testArgs += @("--parallel")
    }
    
    $result = & dotnet $testArgs
    $success = $LASTEXITCODE -eq 0
    
    $testResults["BackendUnit"] = @{
        Success = $success
        ExitCode = $LASTEXITCODE
        Output = $result
    }
    
    Pop-Location
    
    if ($success) {
        Write-TestLog "✅ Backend unit tests passed" "Green"
    } else {
        Write-TestLog "❌ Backend unit tests failed" "Red"
    }
    
    return $success
}

# Run backend integration tests
function Test-BackendIntegration {
    Write-TestLog "🔍 Running backend integration tests..." "Yellow"
    
    Push-Location BackEnd
    
    $testArgs = @(
        "test",
        "FY.WB.Midway.sln",
        "--configuration", "Release",
        "--filter", "Category=Integration"
    )
    
    if ($Coverage) {
        $testArgs += @(
            "--collect:XPlat Code Coverage",
            "--results-directory", "../$Output/backend-integration"
        )
    }
    
    if ($Verbose) {
        $testArgs += @("--verbosity", "detailed")
    }
    
    if ($Filter) {
        $testArgs += @("--filter", "Category=Integration&$Filter")
    }
    
    $result = & dotnet $testArgs
    $success = $LASTEXITCODE -eq 0
    
    $testResults["BackendIntegration"] = @{
        Success = $success
        ExitCode = $LASTEXITCODE
        Output = $result
    }
    
    Pop-Location
    
    if ($success) {
        Write-TestLog "✅ Backend integration tests passed" "Green"
    } else {
        Write-TestLog "❌ Backend integration tests failed" "Red"
    }
    
    return $success
}

# Run frontend unit tests
function Test-FrontendUnit {
    Write-TestLog "🔍 Running frontend unit tests..." "Yellow"
    
    Push-Location FrontEnd
    
    $testArgs = @("test")
    
    if (-not $Watch) {
        $testArgs += @("--watchAll=false")
    }
    
    if ($Coverage) {
        $testArgs += @("--coverage", "--coverageDirectory=../$Output/frontend-unit")
    } else {
        $testArgs += @("--coverage=false")
    }
    
    if ($Verbose) {
        $testArgs += @("--verbose")
    }
    
    $result = & npm $testArgs
    $success = $LASTEXITCODE -eq 0
    
    $testResults["FrontendUnit"] = @{
        Success = $success
        ExitCode = $LASTEXITCODE
        Output = $result
    }
    
    Pop-Location
    
    if ($success) {
        Write-TestLog "✅ Frontend unit tests passed" "Green"
    } else {
        Write-TestLog "❌ Frontend unit tests failed" "Red"
    }
    
    return $success
}

# Run E2E tests
function Test-E2E {
    Write-TestLog "🔍 Running E2E tests..." "Yellow"
    
    # Start application for E2E tests
    Write-TestLog "   Starting application for E2E tests..." "Gray"
    docker-compose up -d backend frontend
    
    # Wait for application to be ready
    Start-Sleep 30
    
    Push-Location FrontEnd
    
    $testArgs = @("run", "test:e2e")
    
    if ($Verbose) {
        $testArgs += @("--", "--headed")
    }
    
    $result = & npm $testArgs
    $success = $LASTEXITCODE -eq 0
    
    $testResults["E2E"] = @{
        Success = $success
        ExitCode = $LASTEXITCODE
        Output = $result
    }
    
    Pop-Location
    
    # Stop application
    docker-compose down
    
    if ($success) {
        Write-TestLog "✅ E2E tests passed" "Green"
    } else {
        Write-TestLog "❌ E2E tests failed" "Red"
    }
    
    return $success
}

# Generate test report
function New-TestReport {
    Write-TestLog "📊 Generating test report..." "Yellow"
    
    $reportPath = "$Output/test-report.html"
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    
    $html = @"
<!DOCTYPE html>
<html>
<head>
    <title>FY.WB.Midway Test Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background: #f5f5f5; padding: 20px; border-radius: 5px; }
        .result { margin: 10px 0; padding: 10px; border-radius: 5px; }
        .success { background: #d4edda; border: 1px solid #c3e6cb; }
        .failure { background: #f8d7da; border: 1px solid #f5c6cb; }
        .summary { margin: 20px 0; font-size: 18px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🧪 FY.WB.Midway Test Report</h1>
        <p>Generated: $timestamp</p>
        <p>Test Type: $TestType</p>
    </div>
    
    <div class="summary">
        Test Results Summary
    </div>
"@
    
    $totalTests = 0
    $passedTests = 0
    
    foreach ($test in $testResults.Keys) {
        $result = $testResults[$test]
        $totalTests++
        
        if ($result.Success) {
            $passedTests++
            $html += "<div class='result success'>✅ $test - PASSED</div>`n"
        } else {
            $html += "<div class='result failure'>❌ $test - FAILED (Exit Code: $($result.ExitCode))</div>`n"
        }
    }
    
    $html += @"
    
    <div class="summary">
        Overall Result: $passedTests/$totalTests tests passed
    </div>
    
</body>
</html>
"@
    
    $html | Out-File -FilePath $reportPath -Encoding UTF8
    Write-TestLog "✅ Test report generated: $reportPath" "Green"
}

# Cleanup test environment
function Stop-TestInfrastructure {
    Write-TestLog "🧹 Cleaning up test environment..." "Yellow"
    
    docker-compose down --volumes
    
    Write-TestLog "✅ Test environment cleaned up" "Green"
}

# Main execution
try {
    Initialize-TestEnvironment
    
    $allTestsPassed = $true
    
    # Run specified test types
    switch ($TestType) {
        "unit" {
            Start-TestInfrastructure
            $allTestsPassed = (Test-BackendUnit) -and (Test-FrontendUnit)
        }
        "integration" {
            Start-TestInfrastructure
            $allTestsPassed = Test-BackendIntegration
        }
        "e2e" {
            Start-TestInfrastructure
            $allTestsPassed = Test-E2E
        }
        "all" {
            Start-TestInfrastructure
            $backendUnitPassed = Test-BackendUnit
            $backendIntegrationPassed = Test-BackendIntegration
            $frontendUnitPassed = Test-FrontendUnit
            $e2ePassed = Test-E2E
            
            $allTestsPassed = $backendUnitPassed -and $backendIntegrationPassed -and $frontendUnitPassed -and $e2ePassed
        }
    }
    
    New-TestReport
    
    Write-TestLog ""
    if ($allTestsPassed) {
        Write-TestLog "🎉 All tests passed!" "Green"
        exit 0
    } else {
        Write-TestLog "❌ Some tests failed. Check the report for details." "Red"
        exit 1
    }
    
} catch {
    Write-TestLog "❌ Test execution failed: $($_.Exception.Message)" "Red"
    exit 1
} finally {
    if (-not $Watch) {
        Stop-TestInfrastructure
    }
}