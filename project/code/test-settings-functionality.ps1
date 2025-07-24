# Test script for Settings page functionality
# Run this after starting the application to verify the settings page works

Write-Host "🧪 Testing Settings Page Functionality" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan

# Test database connection and settings
Write-Host "`n1. Testing database connection..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/debug/test-database" -Method POST -UseBasicParsing
    $result = $response.Content | ConvertFrom-Json
    
    if ($result.success) {
        Write-Host "   ✅ Database connection successful" -ForegroundColor Green
        Write-Host "   📊 Current leads in database: $($result.currentCount)" -ForegroundColor Cyan
    } else {
        Write-Host "   ❌ Database connection failed: $($result.error)" -ForegroundColor Red
    }
} catch {
    Write-Host "   ⚠️  Could not connect to application. Make sure it's running on http://localhost:5000" -ForegroundColor Yellow
}

# Test settings page accessibility
Write-Host "`n2. Testing Settings page accessibility..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/Settings" -UseBasicParsing
    
    if ($response.StatusCode -eq 200) {
        Write-Host "   ✅ Settings page is accessible" -ForegroundColor Green
        
        # Check if page contains expected elements
        if ($response.Content -match "Workflow Configuration") {
            Write-Host "   ✅ Workflow Configuration tab found" -ForegroundColor Green
        }
        
        if ($response.Content -match "API Keys") {
            Write-Host "   ✅ API Keys tab found" -ForegroundColor Green
        }
        
        if ($response.Content -match "enrichmentProcessCount") {
            Write-Host "   ✅ Enrichment process count field found" -ForegroundColor Green
        }
        
        if ($response.Content -match "googleApiKey") {
            Write-Host "   ✅ Google API key field found" -ForegroundColor Green
        }
    } else {
        Write-Host "   ❌ Settings page returned status: $($response.StatusCode)" -ForegroundColor Red
    }
} catch {
    if ($_.Exception.Message -match "401") {
        Write-Host "   ⚠️  Settings page requires authentication. Please log in first." -ForegroundColor Yellow
        Write-Host "   💡 Navigate to http://localhost:5000 and log in, then access http://localhost:5000/Settings" -ForegroundColor Cyan
    } else {
        Write-Host "   ❌ Could not access Settings page: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Test API endpoints
Write-Host "`n3. Testing Settings API endpoints..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/Settings/GetCurrentSettings" -UseBasicParsing
    $result = $response.Content | ConvertFrom-Json
    
    if ($result.success) {
        Write-Host "   ✅ GetCurrentSettings API working" -ForegroundColor Green
        Write-Host "   📊 Current workflow settings:" -ForegroundColor Cyan
        Write-Host "      • Enrichment processes: $($result.workflowSettings.enrichmentProcessCount)" -ForegroundColor Cyan
        Write-Host "      • Vetting processes: $($result.workflowSettings.vettingProcessCount)" -ForegroundColor Cyan
        Write-Host "      • Scoring processes: $($result.workflowSettings.scoringProcessCount)" -ForegroundColor Cyan
        Write-Host "      • CRM update processes: $($result.workflowSettings.crmUpdateProcessCount)" -ForegroundColor Cyan
        Write-Host "   🔧 API configuration:" -ForegroundColor Cyan
        Write-Host "      • Using fake data: $($result.apiConfiguration.useFakeData)" -ForegroundColor Cyan
        Write-Host "      • Google API configured: $($result.apiConfiguration.google.isConfigured)" -ForegroundColor Cyan
        Write-Host "      • Facebook API configured: $($result.apiConfiguration.facebook.isConfigured)" -ForegroundColor Cyan
    } else {
        Write-Host "   ❌ GetCurrentSettings API failed: $($result.message)" -ForegroundColor Red
    }
} catch {
    if ($_.Exception.Message -match "401") {
        Write-Host "   ⚠️  API requires authentication" -ForegroundColor Yellow
    } else {
        Write-Host "   ❌ Could not access API: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "`n🏁 Testing completed!" -ForegroundColor Cyan
Write-Host "💡 To fully test the settings functionality:" -ForegroundColor Yellow
Write-Host "   1. Start the application: dotnet run" -ForegroundColor Cyan
Write-Host "   2. Navigate to http://localhost:5000" -ForegroundColor Cyan
Write-Host "   3. Log in or register an account" -ForegroundColor Cyan
Write-Host "   4. Click the '🔧 Settings' link in the navigation" -ForegroundColor Cyan
Write-Host "   5. Test both Workflow Configuration and API Keys tabs" -ForegroundColor Cyan