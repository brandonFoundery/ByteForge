# backup-data.ps1 - Data Backup and Restore Utility
# Handles database and blob storage backups for FY.WB.Midway

[CmdletBinding()]
param(
    [ValidateSet("backup", "restore", "list", "cleanup")]
    [string]$Action = "backup",
    
    [ValidateSet("database", "blobs", "all")]
    [string]$Type = "all",
    
    [string]$BackupName = "",
    [string]$BackupPath = "./backups",
    [switch]$Compress,
    [int]$RetentionDays = 30,
    [switch]$Force
)

Write-Host "💾 FY.WB.Midway Data Backup Utility" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green

$ErrorActionPreference = "Stop"

# Helper function to log with timestamp
function Write-BackupLog {
    param([string]$Message, [string]$Color = "White")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$timestamp] $Message" -ForegroundColor $Color
}

# Initialize backup environment
function Initialize-BackupEnvironment {
    Write-BackupLog "🔧 Initializing backup environment..." "Yellow"
    
    # Create backup directory
    if (-not (Test-Path $BackupPath)) {
        New-Item -ItemType Directory -Path $BackupPath -Force | Out-Null
        Write-BackupLog "   Created backup directory: $BackupPath" "Gray"
    }
    
    # Create subdirectories
    $subdirs = @("database", "blobs", "logs")
    foreach ($subdir in $subdirs) {
        $path = Join-Path $BackupPath $subdir
        if (-not (Test-Path $path)) {
            New-Item -ItemType Directory -Path $path -Force | Out-Null
        }
    }
    
    # Generate backup name if not provided
    if (-not $BackupName) {
        $script:BackupName = "backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    }
    
    Write-BackupLog "✅ Backup environment ready" "Green"
}

# Check if SQL Server container is running
function Test-SqlServerConnection {
    try {
        $result = docker exec fy-wb-midway-sqlserver /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P "StrongPassword123!" -Q "SELECT 1" 2>$null
        return $result -match "1"
    } catch {
        return $false
    }
}

# Backup database
function Backup-Database {
    Write-BackupLog "💾 Backing up database..." "Yellow"
    
    if (-not (Test-SqlServerConnection)) {
        Write-BackupLog "❌ SQL Server container is not running" "Red"
        return $false
    }
    
    $backupFile = "$BackupName.bak"
    $backupPath = Join-Path $BackupPath "database" $backupFile
    
    # Create backup inside container
    Write-BackupLog "   Creating database backup..." "Gray"
    $containerBackupPath = "/var/opt/mssql/backup/$backupFile"
    
    # Ensure backup directory exists in container
    docker exec fy-wb-midway-sqlserver mkdir -p /var/opt/mssql/backup
    
    # Create backup
    $sqlCmd = "BACKUP DATABASE [FYWBMidway] TO DISK = '$containerBackupPath' WITH FORMAT, INIT, NAME = 'FYWBMidway-Full Database Backup', SKIP, NOREWIND, NOUNLOAD, STATS = 10"
    $result = docker exec fy-wb-midway-sqlserver /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P "StrongPassword123!" -Q "$sqlCmd"
    
    if ($LASTEXITCODE -ne 0) {
        Write-BackupLog "❌ Database backup failed" "Red"
        return $false
    }
    
    # Copy backup from container to host
    Write-BackupLog "   Copying backup to host..." "Gray"
    docker cp "fy-wb-midway-sqlserver:$containerBackupPath" $backupPath
    
    if ($LASTEXITCODE -ne 0) {
        Write-BackupLog "❌ Failed to copy backup from container" "Red"
        return $false
    }
    
    # Compress if requested
    if ($Compress) {
        Write-BackupLog "   Compressing backup..." "Gray"
        $compressedPath = "$backupPath.zip"
        Compress-Archive -Path $backupPath -DestinationPath $compressedPath -Force
        Remove-Item $backupPath -Force
        $backupPath = $compressedPath
    }
    
    $fileSize = (Get-Item $backupPath).Length / 1MB
    Write-BackupLog "✅ Database backup completed: $backupPath ($([Math]::Round($fileSize, 2)) MB)" "Green"
    
    return $true
}

# Backup blob storage (development storage)
function Backup-BlobStorage {
    Write-BackupLog "📁 Backing up blob storage..." "Yellow"
    
    # In development, we're using local storage or Azure Storage Emulator
    # For now, we'll backup any local file uploads if they exist
    
    $uploadsPath = "./uploads"
    if (Test-Path $uploadsPath) {
        $blobBackupPath = Join-Path $BackupPath "blobs" "$BackupName-blobs"
        
        Write-BackupLog "   Copying blob files..." "Gray"
        Copy-Item -Path $uploadsPath -Destination $blobBackupPath -Recurse -Force
        
        if ($Compress) {
            Write-BackupLog "   Compressing blob backup..." "Gray"
            $compressedPath = "$blobBackupPath.zip"
            Compress-Archive -Path $blobBackupPath -DestinationPath $compressedPath -Force
            Remove-Item $blobBackupPath -Recurse -Force
        }
        
        Write-BackupLog "✅ Blob storage backup completed" "Green"
        return $true
    } else {
        Write-BackupLog "ℹ️  No blob storage to backup (uploads directory not found)" "Blue"
        return $true
    }
}

# Restore database
function Restore-Database {
    param([string]$RestoreBackupName)
    
    Write-BackupLog "🔄 Restoring database..." "Yellow"
    
    if (-not (Test-SqlServerConnection)) {
        Write-BackupLog "❌ SQL Server container is not running" "Red"
        return $false
    }
    
    # Find backup file
    $backupFile = "$RestoreBackupName.bak"
    $backupPath = Join-Path $BackupPath "database" $backupFile
    
    # Check for compressed version
    if (-not (Test-Path $backupPath)) {
        $backupPath = "$backupPath.zip"
        if (Test-Path $backupPath) {
            Write-BackupLog "   Extracting compressed backup..." "Gray"
            $extractPath = Join-Path $BackupPath "database" "temp"
            Expand-Archive -Path $backupPath -DestinationPath $extractPath -Force
            $backupPath = Join-Path $extractPath "$RestoreBackupName.bak"
        }
    }
    
    if (-not (Test-Path $backupPath)) {
        Write-BackupLog "❌ Backup file not found: $backupPath" "Red"
        return $false
    }
    
    # Copy backup to container
    Write-BackupLog "   Copying backup to container..." "Gray"
    $containerBackupPath = "/var/opt/mssql/backup/$backupFile"
    docker cp $backupPath "fy-wb-midway-sqlserver:$containerBackupPath"
    
    # Stop any connections to the database
    Write-BackupLog "   Preparing database for restore..." "Gray"
    $killConnectionsCmd = "ALTER DATABASE [FYWBMidway] SET SINGLE_USER WITH ROLLBACK IMMEDIATE"
    docker exec fy-wb-midway-sqlserver /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P "StrongPassword123!" -Q "$killConnectionsCmd"
    
    # Restore database
    Write-BackupLog "   Restoring database..." "Gray"
    $restoreCmd = "RESTORE DATABASE [FYWBMidway] FROM DISK = '$containerBackupPath' WITH REPLACE, STATS = 10"
    $result = docker exec fy-wb-midway-sqlserver /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P "StrongPassword123!" -Q "$restoreCmd"
    
    # Return database to multi-user mode
    $multiUserCmd = "ALTER DATABASE [FYWBMidway] SET MULTI_USER"
    docker exec fy-wb-midway-sqlserver /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P "StrongPassword123!" -Q "$multiUserCmd"
    
    if ($LASTEXITCODE -eq 0) {
        Write-BackupLog "✅ Database restore completed" "Green"
        return $true
    } else {
        Write-BackupLog "❌ Database restore failed" "Red"
        return $false
    }
}

# List available backups
function Get-BackupList {
    Write-BackupLog "📋 Available backups:" "Yellow"
    
    $databaseBackups = Get-ChildItem -Path (Join-Path $BackupPath "database") -Filter "*.bak*" | Sort-Object LastWriteTime -Descending
    $blobBackups = Get-ChildItem -Path (Join-Path $BackupPath "blobs") -Filter "*blobs*" | Sort-Object LastWriteTime -Descending
    
    Write-BackupLog ""
    Write-BackupLog "Database Backups:" "Cyan"
    if ($databaseBackups.Count -eq 0) {
        Write-BackupLog "  No database backups found" "Gray"
    } else {
        foreach ($backup in $databaseBackups) {
            $size = [Math]::Round($backup.Length / 1MB, 2)
            Write-BackupLog "  📁 $($backup.BaseName) - $($backup.LastWriteTime) ($size MB)" "White"
        }
    }
    
    Write-BackupLog ""
    Write-BackupLog "Blob Storage Backups:" "Cyan"
    if ($blobBackups.Count -eq 0) {
        Write-BackupLog "  No blob storage backups found" "Gray"
    } else {
        foreach ($backup in $blobBackups) {
            if ($backup.PSIsContainer) {
                $size = "Directory"
            } else {
                $size = "$([Math]::Round($backup.Length / 1MB, 2)) MB"
            }
            Write-BackupLog "  📁 $($backup.Name) - $($backup.LastWriteTime) ($size)" "White"
        }
    }
}

# Cleanup old backups
function Remove-OldBackups {
    Write-BackupLog "🧹 Cleaning up old backups..." "Yellow"
    
    $cutoffDate = (Get-Date).AddDays(-$RetentionDays)
    $deletedCount = 0
    
    # Cleanup database backups
    $databaseBackups = Get-ChildItem -Path (Join-Path $BackupPath "database") -Filter "*.bak*"
    foreach ($backup in $databaseBackups) {
        if ($backup.LastWriteTime -lt $cutoffDate) {
            Write-BackupLog "   Deleting old database backup: $($backup.Name)" "Gray"
            Remove-Item $backup.FullName -Force
            $deletedCount++
        }
    }
    
    # Cleanup blob backups
    $blobBackups = Get-ChildItem -Path (Join-Path $BackupPath "blobs")
    foreach ($backup in $blobBackups) {
        if ($backup.LastWriteTime -lt $cutoffDate) {
            Write-BackupLog "   Deleting old blob backup: $($backup.Name)" "Gray"
            if ($backup.PSIsContainer) {
                Remove-Item $backup.FullName -Recurse -Force
            } else {
                Remove-Item $backup.FullName -Force
            }
            $deletedCount++
        }
    }
    
    Write-BackupLog "✅ Cleanup completed. Deleted $deletedCount old backups" "Green"
}

# Main execution
try {
    Initialize-BackupEnvironment
    
    switch ($Action) {
        "backup" {
            $success = $true
            
            if ($Type -in @("database", "all")) {
                $success = $success -and (Backup-Database)
            }
            
            if ($Type -in @("blobs", "all")) {
                $success = $success -and (Backup-BlobStorage)
            }
            
            if ($success) {
                Write-BackupLog ""
                Write-BackupLog "🎉 Backup completed successfully!" "Green"
                Write-BackupLog "   Backup name: $BackupName" "White"
                Write-BackupLog "   Backup path: $BackupPath" "White"
            } else {
                Write-BackupLog "❌ Backup failed" "Red"
                exit 1
            }
        }
        
        "restore" {
            if (-not $BackupName) {
                Write-BackupLog "❌ Backup name required for restore operation" "Red"
                exit 1
            }
            
            if (-not $Force) {
                $confirmation = Read-Host "⚠️  This will overwrite the current database. Continue? (y/N)"
                if ($confirmation -ne "y" -and $confirmation -ne "Y") {
                    Write-BackupLog "Restore cancelled by user" "Yellow"
                    exit 0
                }
            }
            
            $success = Restore-Database -RestoreBackupName $BackupName
            
            if ($success) {
                Write-BackupLog "🎉 Restore completed successfully!" "Green"
            } else {
                Write-BackupLog "❌ Restore failed" "Red"
                exit 1
            }
        }
        
        "list" {
            Get-BackupList
        }
        
        "cleanup" {
            Remove-OldBackups
        }
    }
    
} catch {
    Write-BackupLog "❌ Operation failed: $($_.Exception.Message)" "Red"
    exit 1
}