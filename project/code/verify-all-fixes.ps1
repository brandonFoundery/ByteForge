# PowerShell script to verify all compilation fixes
# This script checks if all compilation errors have been resolved

Write-Host "🔍 Verifying All Build Fixes" -ForegroundColor Cyan
Write-Host "============================" -ForegroundColor Cyan

$ErrorActionPreference = "Continue"
$issuesFound = 0

# Check Lead model property usage in scrapers
Write-Host "`n👤 Checking Lead model property usage..." -ForegroundColor Yellow

$scraperFiles = @(
    "Services/GoogleLeadScraper.cs",
    "Services/FacebookLeadScraper.cs", 
    "Services/LinkedInLeadScraper.cs",
    "Services/YellowPagesLeadScraper.cs"
)

foreach ($file in $scraperFiles) {
    if (Test-Path $file) {
        $content = Get-Content $file -Raw
        
        if ($content -match "FirstName|LastName") {
            Write-Host "   ❌ $file still contains FirstName/LastName references" -ForegroundColor Red
            $issuesFound++
        } else {
            Write-Host "   ✅ $file - Lead properties correct" -ForegroundColor Green
        }
        
        if ($content -match "Name\s*=\s*") {
            Write-Host "   ✅ $file - Uses Name property correctly" -ForegroundColor Green
        } else {
            Write-Host "   ⚠️  $file - May not be setting Name property" -ForegroundColor Yellow
        }
    } else {
        Write-Host "   ❌ $file - MISSING" -ForegroundColor Red
        $issuesFound++
    }
}

# Check test project configuration
Write-Host "`n🧪 Checking test project configuration..." -ForegroundColor Yellow

if (Test-Path "LeadProcessing.Tests/GlobalUsings.cs") {
    $globalUsings = Get-Content "LeadProcessing.Tests/GlobalUsings.cs" -Raw
    if ($globalUsings -match "LeadProcessing.Services") {
        Write-Host "   ✅ Global usings include Services namespace" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Global usings missing Services namespace" -ForegroundColor Red
        $issuesFound++
    }
} else {
    Write-Host "   ❌ GlobalUsings.cs missing" -ForegroundColor Red
    $issuesFound++
}

# Check ExternalApiConfigurationService interface
Write-Host "`n🔧 Checking ExternalApiConfigurationService..." -ForegroundColor Yellow

if (Test-Path "Services/ExternalApiConfigurationService.cs") {
    $serviceContent = Get-Content "Services/ExternalApiConfigurationService.cs" -Raw
    
    if ($serviceContent -match "public ExternalServicesConfiguration GetConfiguration") {
        Write-Host "   ✅ GetConfiguration method implemented" -ForegroundColor Green
    } else {
        Write-Host "   ❌ GetConfiguration method missing" -ForegroundColor Red
        $issuesFound++
    }
    
    if ($serviceContent -match "ExternalServicesConfiguration GetConfiguration\(\);") {
        Write-Host "   ✅ GetConfiguration method in interface" -ForegroundColor Green
    } else {
        Write-Host "   ❌ GetConfiguration method missing from interface" -ForegroundColor Red
        $issuesFound++
    }
} else {
    Write-Host "   ❌ ExternalApiConfigurationService.cs missing" -ForegroundColor Red
    $issuesFound++
}

# Check SettingsViewModels
Write-Host "`n📋 Checking SettingsViewModels..." -ForegroundColor Yellow

if (Test-Path "Models/SettingsViewModels.cs") {
    $viewModelsContent = Get-Content "Models/SettingsViewModels.cs" -Raw
    
    if ($viewModelsContent -match "public class SettingsViewModel") {
        Write-Host "   ✅ SettingsViewModel class exists" -ForegroundColor Green
    } else {
        Write-Host "   ❌ SettingsViewModel class missing" -ForegroundColor Red
        $issuesFound++
    }
    
    if ($viewModelsContent -match "namespace LeadProcessing.Models") {
        Write-Host "   ✅ Correct namespace" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Incorrect namespace" -ForegroundColor Red
        $issuesFound++
    }
} else {
    Write-Host "   ❌ SettingsViewModels.cs missing" -ForegroundColor Red
    $issuesFound++
}

# Check database migration files
Write-Host "`n💾 Checking database migration..." -ForegroundColor Yellow

if (Test-Path "Migrations/20250721173800_AddWorkflowSettings.cs") {
    Write-Host "   ✅ WorkflowSettings migration file exists" -ForegroundColor Green
} else {
    Write-Host "   ❌ WorkflowSettings migration file missing" -ForegroundColor Red
    $issuesFound++
}

if (Test-Path "add-workflow-settings-table.sql") {
    Write-Host "   ✅ Manual SQL migration script exists" -ForegroundColor Green
} else {
    Write-Host "   ❌ Manual SQL migration script missing" -ForegroundColor Red
    $issuesFound++
}

# Summary
Write-Host "`n📊 Verification Results" -ForegroundColor Cyan
Write-Host "=======================" -ForegroundColor Cyan

if ($issuesFound -eq 0) {
    Write-Host "🎉 ALL FIXES VERIFIED SUCCESSFULLY!" -ForegroundColor Green
    Write-Host "✅ No compilation errors expected" -ForegroundColor Green
    Write-Host "" 
    Write-Host "🚀 Ready to build and deploy:" -ForegroundColor Yellow
    Write-Host "   1. dotnet build" -ForegroundColor Cyan
    Write-Host "   2. dotnet ef database update (or run add-workflow-settings-table.sql)" -ForegroundColor Cyan
    Write-Host "   3. dotnet run" -ForegroundColor Cyan
    Write-Host "   4. Navigate to http://localhost:5000/Settings" -ForegroundColor Cyan
} else {
    Write-Host "⚠️  Found $issuesFound potential issues" -ForegroundColor Yellow
    Write-Host "🔧 Please review the errors above and fix them before building" -ForegroundColor Red
}

Write-Host "`n🔧 Quick build test command:" -ForegroundColor Yellow
Write-Host "   dotnet build --no-restore --verbosity quiet" -ForegroundColor Cyan