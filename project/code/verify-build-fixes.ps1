# PowerShell script to verify build fixes
# This script checks if the compilation errors have been resolved

Write-Host "🔍 Verifying Build Fixes" -ForegroundColor Cyan
Write-Host "========================" -ForegroundColor Cyan

$ErrorActionPreference = "Continue"
$issuesFound = 0

# Check if required files exist
Write-Host "`n📁 Checking file structure..." -ForegroundColor Yellow

$requiredFiles = @(
    "Models/SettingsViewModels.cs",
    "Models/WorkflowSettings.cs", 
    "Services/ISettingsService.cs",
    "Services/SettingsService.cs",
    "Services/ExternalApiConfigurationService.cs",
    "Controllers/SettingsController.cs",
    "Views/Settings/Index.cshtml"
)

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "   ✅ $file" -ForegroundColor Green
    } else {
        Write-Host "   ❌ $file - MISSING" -ForegroundColor Red
        $issuesFound++
    }
}

# Check for proper namespace usage
Write-Host "`n🏷️  Checking namespace issues..." -ForegroundColor Yellow

# Check SettingsViewModel in View
$viewContent = Get-Content "Views/Settings/Index.cshtml" -Raw
if ($viewContent -match "@model SettingsViewModel") {
    Write-Host "   ✅ SettingsViewModel properly referenced in view" -ForegroundColor Green
} else {
    Write-Host "   ❌ SettingsViewModel not found in view" -ForegroundColor Red
    $issuesFound++
}

# Check if Models/SettingsViewModels.cs has proper namespace
$viewModelsContent = Get-Content "Models/SettingsViewModels.cs" -Raw
if ($viewModelsContent -match "namespace LeadProcessing.Models") {
    Write-Host "   ✅ SettingsViewModels has correct namespace" -ForegroundColor Green
} else {
    Write-Host "   ❌ SettingsViewModels namespace issue" -ForegroundColor Red
    $issuesFound++
}

# Check ExternalApiConfigurationService interface
$serviceContent = Get-Content "Services/ExternalApiConfigurationService.cs" -Raw
if ($serviceContent -match "ExternalServicesConfiguration GetConfiguration") {
    Write-Host "   ✅ GetConfiguration method exists in interface" -ForegroundColor Green
} else {
    Write-Host "   ❌ GetConfiguration method missing from interface" -ForegroundColor Red
    $issuesFound++
}

# Check test project references
Write-Host "`n🧪 Checking test project..." -ForegroundColor Yellow

if (Test-Path "LeadProcessing.Tests/LeadProcessing.Tests.csproj") {
    $testProject = Get-Content "LeadProcessing.Tests/LeadProcessing.Tests.csproj" -Raw
    if ($testProject -match "Microsoft.Extensions.Configuration") {
        Write-Host "   ✅ Test project has Configuration package reference" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Test project missing Configuration package" -ForegroundColor Red
        $issuesFound++
    }
    
    if ($testProject -match "ProjectReference.*LeadProcessing.csproj") {
        Write-Host "   ✅ Test project references main project" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Test project missing main project reference" -ForegroundColor Red
        $issuesFound++
    }
}

# Check Program.cs registration
Write-Host "`n⚙️  Checking service registration..." -ForegroundColor Yellow

$programContent = Get-Content "Program.cs" -Raw
if ($programContent -match "AddScoped<ISettingsService, SettingsService>") {
    Write-Host "   ✅ SettingsService registered in DI container" -ForegroundColor Green
} else {
    Write-Host "   ❌ SettingsService not registered in Program.cs" -ForegroundColor Red
    $issuesFound++
}

# Summary
Write-Host "`n📊 Build Fix Verification Results" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan

if ($issuesFound -eq 0) {
    Write-Host "🎉 All build fixes verified successfully!" -ForegroundColor Green
    Write-Host "✅ No compilation errors expected" -ForegroundColor Green
    Write-Host "" 
    Write-Host "📋 Next steps:" -ForegroundColor Yellow
    Write-Host "   1. Build the solution: dotnet build" -ForegroundColor Cyan
    Write-Host "   2. Apply database migration: dotnet ef database update" -ForegroundColor Cyan
    Write-Host "   3. Run the application: dotnet run" -ForegroundColor Cyan
    Write-Host "   4. Test settings page: http://localhost:5000/Settings" -ForegroundColor Cyan
} else {
    Write-Host "⚠️  Found $issuesFound potential issues" -ForegroundColor Yellow
    Write-Host "🔧 Please review the errors above and fix them before building" -ForegroundColor Red
}

Write-Host "`n🔧 Manual verification steps:" -ForegroundColor Yellow
Write-Host "   • Check that SettingsViewModel is accessible from Views" -ForegroundColor Cyan
Write-Host "   • Verify ExternalApiConfigurationService compiles correctly" -ForegroundColor Cyan  
Write-Host "   • Ensure test project can find all referenced types" -ForegroundColor Cyan
Write-Host "   • Confirm database migration file is properly structured" -ForegroundColor Cyan