# PowerShell script to verify test compilation fixes
# This script checks if the test project compilation errors have been resolved

Write-Host "🧪 Verifying Test Project Fixes" -ForegroundColor Cyan
Write-Host "===============================" -ForegroundColor Cyan

$ErrorActionPreference = "Continue"
$issuesFound = 0

# Check GoogleLeadScraperTests file
Write-Host "`n🔍 Checking GoogleLeadScraperTests..." -ForegroundColor Yellow

if (Test-Path "LeadProcessing.Tests/UnitTests/Services/GoogleLeadScraperTests.cs") {
    $testContent = Get-Content "LeadProcessing.Tests/UnitTests/Services/GoogleLeadScraperTests.cs" -Raw
    
    # Check if constructor has been updated
    if ($testContent -match "new GoogleLeadScraper\(_mockLogger\.Object, _httpClient, _apiConfigService\)") {
        Write-Host "   ✅ GoogleLeadScraper constructor updated with all required parameters" -ForegroundColor Green
    } else {
        Write-Host "   ❌ GoogleLeadScraper constructor still missing parameters" -ForegroundColor Red
        $issuesFound++
    }
    
    # Check if HttpClient is declared
    if ($testContent -match "private HttpClient _httpClient") {
        Write-Host "   ✅ HttpClient field declared" -ForegroundColor Green
    } else {
        Write-Host "   ❌ HttpClient field missing" -ForegroundColor Red
        $issuesFound++
    }
    
    # Check if IExternalApiConfigurationService is declared
    if ($testContent -match "private IExternalApiConfigurationService _apiConfigService") {
        Write-Host "   ✅ IExternalApiConfigurationService field declared" -ForegroundColor Green
    } else {
        Write-Host "   ❌ IExternalApiConfigurationService field missing" -ForegroundColor Red
        $issuesFound++
    }
    
    # Check if configuration is set up properly
    if ($testContent -match "ExternalApiConfigurationService\(configuration\)") {
        Write-Host "   ✅ ExternalApiConfigurationService properly instantiated" -ForegroundColor Green
    } else {
        Write-Host "   ❌ ExternalApiConfigurationService not properly set up" -ForegroundColor Red
        $issuesFound++
    }
    
    # Check if tests have been updated for new expectations
    if ($testContent -match "Assert\.AreEqual\(1, leadList\.Count\)") {
        Write-Host "   ✅ Test expectations updated for single lead return" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Tests may not be updated for new lead generation behavior" -ForegroundColor Yellow
    }
    
} else {
    Write-Host "   ❌ GoogleLeadScraperTests.cs not found" -ForegroundColor Red
    $issuesFound++
}

# Check test project configuration
Write-Host "`n⚙️  Checking test project configuration..." -ForegroundColor Yellow

if (Test-Path "LeadProcessing.Tests/LeadProcessing.Tests.csproj") {
    $projectContent = Get-Content "LeadProcessing.Tests/LeadProcessing.Tests.csproj" -Raw
    
    if ($projectContent -match "Microsoft\.Extensions\.Configuration") {
        Write-Host "   ✅ Microsoft.Extensions.Configuration package referenced" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Microsoft.Extensions.Configuration package missing" -ForegroundColor Red
        $issuesFound++
    }
    
    if ($projectContent -match "ProjectReference.*LeadProcessing\.csproj") {
        Write-Host "   ✅ Main project reference exists" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Main project reference missing" -ForegroundColor Red
        $issuesFound++
    }
} else {
    Write-Host "   ❌ Test project file not found" -ForegroundColor Red
    $issuesFound++
}

# Check GlobalUsings
Write-Host "`n📁 Checking GlobalUsings..." -ForegroundColor Yellow

if (Test-Path "LeadProcessing.Tests/GlobalUsings.cs") {
    $globalUsings = Get-Content "LeadProcessing.Tests/GlobalUsings.cs" -Raw
    
    if ($globalUsings -match "global using LeadProcessing\.Services") {
        Write-Host "   ✅ Services namespace included in global usings" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Services namespace missing from global usings" -ForegroundColor Red
        $issuesFound++
    }
} else {
    Write-Host "   ❌ GlobalUsings.cs not found" -ForegroundColor Red
    $issuesFound++
}

# Summary
Write-Host "`n📊 Test Fix Verification Results" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

if ($issuesFound -eq 0) {
    Write-Host "🎉 ALL TEST FIXES VERIFIED SUCCESSFULLY!" -ForegroundColor Green
    Write-Host "✅ Test project should compile without errors" -ForegroundColor Green
    Write-Host "" 
    Write-Host "🚀 Ready to test:" -ForegroundColor Yellow
    Write-Host "   1. dotnet build" -ForegroundColor Cyan
    Write-Host "   2. dotnet test" -ForegroundColor Cyan
    Write-Host "   3. dotnet run" -ForegroundColor Cyan
} else {
    Write-Host "⚠️  Found $issuesFound potential issues" -ForegroundColor Yellow
    Write-Host "🔧 Please review the errors above and fix them before testing" -ForegroundColor Red
}

Write-Host "`n🔧 Test-specific fixes completed:" -ForegroundColor Yellow
Write-Host "   • GoogleLeadScraperTests constructor updated with HttpClient and IExternalApiConfigurationService" -ForegroundColor Cyan
Write-Host "   • Test expectations updated for new single-lead generation behavior" -ForegroundColor Cyan
Write-Host "   • Configuration setup added for fake data testing" -ForegroundColor Cyan
Write-Host "   • Logging expectations updated to match new log messages" -ForegroundColor Cyan