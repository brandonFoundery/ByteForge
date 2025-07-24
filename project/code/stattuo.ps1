# Stattuo Lead Processing System Startup Script
# Kills existing processes and starts both backend and frontend in separate terminals

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Stattuo Lead Processing System       " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Function to kill processes on specific ports
function Kill-ProcessOnPort {
    param(
        [int]$Port
    )
    
    Write-Host "Checking for processes on port $Port..." -ForegroundColor Yellow
    
    try {
        $processes = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess
        
        if ($processes) {
            foreach ($processId in $processes) {
                $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
                if ($process) {
                    Write-Host "  Killing process: $($process.ProcessName) (PID: $processId)" -ForegroundColor Red
                    Stop-Process -Id $processId -Force
                }
            }
        } else {
            Write-Host "  No processes found on port $Port" -ForegroundColor Green
        }
    }
    catch {
        Write-Host "  No processes found on port $Port" -ForegroundColor Green
    }
}

# Kill processes on backend ports
Write-Host "Cleaning up existing processes..." -ForegroundColor Magenta
Kill-ProcessOnPort -Port 5000
Kill-ProcessOnPort -Port 7001

# Kill processes on frontend port  
Kill-ProcessOnPort -Port 3020

Write-Host ""
Write-Host "Starting applications..." -ForegroundColor Magenta

# Get current directory
$currentDir = Get-Location

# Start Backend (.NET) in new terminal
Write-Host "Starting Backend (.NET Core) on ports 5000/7001..." -ForegroundColor Green
Start-Process "wt" -ArgumentList "new-tab", "--title", "Stattuo Backend", "powershell", "-NoExit", "-Command", "cd '$currentDir'; Write-Host 'Starting .NET Backend...' -ForegroundColor Green; dotnet run"

# Wait a moment before starting frontend
Start-Sleep -Seconds 2

# Start Frontend (Next.js) in new terminal
Write-Host "Starting Frontend (Next.js) on port 3020..." -ForegroundColor Green
$frontendDir = Join-Path $currentDir "FrontEnd"
Start-Process "wt" -ArgumentList "new-tab", "--title", "Stattuo Frontend", "powershell", "-NoExit", "-Command", "cd '$frontendDir'; Write-Host 'Starting Next.js Frontend on port 3020...' -ForegroundColor Green; npm run dev -- -p 3020"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Applications starting in separate terminals:" -ForegroundColor White
Write-Host "  Backend:  http://localhost:5000" -ForegroundColor Green
Write-Host "  Frontend: http://localhost:3020" -ForegroundColor Green
Write-Host "  Hangfire: http://localhost:5000/hangfire" -ForegroundColor Yellow
Write-Host ""
Write-Host "Dashboard: http://localhost:5000/Leads/Dashboard" -ForegroundColor Magenta
Write-Host "Next.js App: http://localhost:3020" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Wait a bit and then open the applications
Write-Host ""
Write-Host "Waiting 10 seconds before opening applications..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Open both applications in default browser
Write-Host "Opening applications in browser..." -ForegroundColor Green
Start-Process "http://localhost:3020"
Start-Process "http://localhost:5000/Leads/Dashboard"

Write-Host ""
Write-Host "Setup complete! Both applications should be running in separate terminals." -ForegroundColor Green
Write-Host "Press any key to exit this script..." -ForegroundColor White
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")