# Simple user registration script
$baseUrl = "http://localhost:5002"

# User 1: user@example.com
Write-Host "Registering user@example.com..." -ForegroundColor Cyan
$user1 = @{
    email = "user@example.com"
    password = "Test123!"
    companyName = "Example Corp"
    companyUrl = "https://example.com"
} | ConvertTo-Json

try {
    $response1 = Invoke-RestMethod -Uri "$baseUrl/api/Auth/register" -Method POST -Body $user1 -ContentType "application/json"
    Write-Host "✓ user@example.com registered successfully!" -ForegroundColor Green
    Write-Host $response1
} catch {
    Write-Host "Registration failed or user exists. Trying login..." -ForegroundColor Yellow
    $loginBody1 = @{
        email = "user@example.com"
        password = "Test123!"
    } | ConvertTo-Json
    
    try {
        $loginResponse1 = Invoke-RestMethod -Uri "$baseUrl/api/Auth/login" -Method POST -Body $loginBody1 -ContentType "application/json"
        Write-Host "✓ user@example.com login successful!" -ForegroundColor Green
    } catch {
        Write-Host "✗ user@example.com login failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host ""

# User 2: client1@example.com
Write-Host "Registering client1@example.com..." -ForegroundColor Cyan
$user2 = @{
    email = "client1@example.com"
    password = "Test123!"
    companyName = "Client Solutions LLC"
    companyUrl = "https://clientsolutions.com"
} | ConvertTo-Json

try {
    $response2 = Invoke-RestMethod -Uri "$baseUrl/api/Auth/register" -Method POST -Body $user2 -ContentType "application/json"
    Write-Host "✓ client1@example.com registered successfully!" -ForegroundColor Green
    Write-Host $response2
} catch {
    Write-Host "Registration failed or user exists. Trying login..." -ForegroundColor Yellow
    $loginBody2 = @{
        email = "client1@example.com"
        password = "Test123!"
    } | ConvertTo-Json
    
    try {
        $loginResponse2 = Invoke-RestMethod -Uri "$baseUrl/api/Auth/login" -Method POST -Body $loginBody2 -ContentType "application/json"
        Write-Host "✓ client1@example.com login successful!" -ForegroundColor Green
    } catch {
        Write-Host "✗ client1@example.com login failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "User registration process completed!" -ForegroundColor Blue
