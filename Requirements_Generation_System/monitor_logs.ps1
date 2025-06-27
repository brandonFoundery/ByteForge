# Claude Code Log Monitor - PowerShell Version
param(
    [string]$Action = "monitor",
    [string]$ExportFile = "",
    [switch]$NoFollow,
    [double]$Interval = 2.0
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Claude Code Log Monitor" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python and try again" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if rich is installed
try {
    python -c "import rich" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "📦 Installing required dependencies..." -ForegroundColor Yellow
        pip install rich
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ ERROR: Failed to install rich library" -ForegroundColor Red
            Write-Host "Please run: pip install rich" -ForegroundColor Yellow
            Read-Host "Press Enter to exit"
            exit 1
        }
        Write-Host "✅ Dependencies installed successfully" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ ERROR: Failed to check dependencies" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Build command arguments
$args = @()

if ($Action -eq "export") {
    $args += "--export"
    if ($ExportFile) {
        $args += $ExportFile
    } else {
        $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        $args += "claude_logs_export_$timestamp.html"
    }
    Write-Host "📄 Exporting logs to file..." -ForegroundColor Blue
} else {
    Write-Host "🔍 Starting real-time log monitor..." -ForegroundColor Blue
    Write-Host "Press Ctrl+C to stop monitoring" -ForegroundColor Yellow
    Write-Host ""
    
    if ($NoFollow) {
        $args += "--no-follow"
    }
    
    $args += "--interval", $Interval
}

# Run the log monitor
try {
    python log_monitor.py @args
} catch {
    Write-Host "❌ ERROR: Failed to run log monitor" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}

if ($Action -eq "export") {
    Write-Host ""
    Write-Host "✅ Export completed!" -ForegroundColor Green
    Read-Host "Press Enter to exit"
}
