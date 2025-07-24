# Startup Script for Lead Processing System
# Kills existing processes and starts both backend and frontend

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Lead Processing System Startup       " -ForegroundColor Cyan
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

# Kill existing processes
Write-Host "Cleaning up existing processes..." -ForegroundColor Magenta
Kill-ProcessOnPort -Port 5000  # Backend HTTP
Kill-ProcessOnPort -Port 7001  # Backend HTTPS  
Kill-ProcessOnPort -Port 3020  # Frontend

Write-Host ""
Write-Host "Starting applications..." -ForegroundColor Magenta

# Get current directory
$currentDir = Get-Location

# Start Backend (.NET) in new terminal
Write-Host "Starting Backend (.NET Core)..." -ForegroundColor Green
Start-Process "powershell" -ArgumentList "-NoExit", "-Command", "cd '$currentDir'; Write-Host 'Starting .NET Backend...' -ForegroundColor Green; dotnet run" -WindowStyle Normal

# Wait before starting frontend
Start-Sleep -Seconds 3

# Start Frontend (Next.js) in new terminal with full npm path
Write-Host "Starting Frontend (Next.js)..." -ForegroundColor Green
$frontendDir = Join-Path $currentDir "FrontEnd"
$npmPath = "C:\Program Files\nodejs\npm.cmd"
Start-Process "powershell" -ArgumentList "-NoExit", "-Command", "cd '$frontendDir'; Write-Host 'Starting Next.js Frontend on port 3020...' -ForegroundColor Green; & '$npmPath' run dev -- -p 3020" -WindowStyle Normal

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Applications starting:" -ForegroundColor White
Write-Host "  Backend:  http://localhost:5000" -ForegroundColor Green
Write-Host "  Frontend: http://localhost:3020" -ForegroundColor Green
Write-Host "  Dashboard: http://localhost:5000/Leads/Dashboard" -ForegroundColor Magenta
Write-Host "========================================" -ForegroundColor Cyan

Write-Host ""
Write-Host "Setup complete! Applications are starting in separate terminals." -ForegroundColor Green