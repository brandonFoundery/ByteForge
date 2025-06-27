#!/usr/bin/env python3
"""
Backup and restore custom UI style reference images
"""

import shutil
from pathlib import Path
from datetime import datetime
from rich.console import Console

console = Console()

def backup_custom_images():
    """Backup existing custom reference images"""
    
    project_root = Path(__file__).parent.parent.parent
    examples_dir = project_root / "Requirements_Generation_System" / "ui_style_examples"
    backup_dir = project_root / "Requirements_Generation_System" / "ui_style_examples_backup"
    
    if not examples_dir.exists():
        console.print("[yellow]No ui_style_examples directory found to backup[/yellow]")
        return False
    
    # Create backup directory with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    timestamped_backup = backup_dir / f"backup_{timestamp}"
    timestamped_backup.mkdir(parents=True, exist_ok=True)
    
    # Copy all PNG files
    png_files = list(examples_dir.glob("*.png"))
    
    if not png_files:
        console.print("[yellow]No PNG files found to backup[/yellow]")
        return False
    
    for png_file in png_files:
        shutil.copy2(png_file, timestamped_backup / png_file.name)
    
    console.print(f"[green]✅ Backed up {len(png_files)} images to:[/green]")
    console.print(f"[green]   {timestamped_backup}[/green]")
    
    # Also create a "latest" backup
    latest_backup = backup_dir / "latest"
    if latest_backup.exists():
        shutil.rmtree(latest_backup)
    shutil.copytree(examples_dir, latest_backup)
    
    console.print(f"[green]✅ Latest backup also saved to: {latest_backup}[/green]")
    return True

def restore_custom_images(backup_name="latest"):
    """Restore custom reference images from backup"""
    
    project_root = Path(__file__).parent.parent.parent
    examples_dir = project_root / "Requirements_Generation_System" / "ui_style_examples"
    backup_dir = project_root / "Requirements_Generation_System" / "ui_style_examples_backup"
    
    # Determine backup source
    if backup_name == "latest":
        source_dir = backup_dir / "latest"
    else:
        source_dir = backup_dir / f"backup_{backup_name}"
    
    if not source_dir.exists():
        console.print(f"[red]❌ Backup not found: {source_dir}[/red]")
        list_backups()
        return False
    
    # Create examples directory if it doesn't exist
    examples_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy files from backup
    png_files = list(source_dir.glob("*.png"))
    
    if not png_files:
        console.print(f"[red]❌ No PNG files found in backup: {source_dir}[/red]")
        return False
    
    for png_file in png_files:
        shutil.copy2(png_file, examples_dir / png_file.name)
    
    console.print(f"[green]✅ Restored {len(png_files)} images from backup[/green]")
    console.print(f"[green]   Source: {source_dir}[/green]")
    console.print(f"[green]   Target: {examples_dir}[/green]")
    return True

def list_backups():
    """List all available backups"""
    
    project_root = Path(__file__).parent.parent.parent
    backup_dir = project_root / "Requirements_Generation_System" / "ui_style_examples_backup"
    
    if not backup_dir.exists():
        console.print("[yellow]No backup directory found[/yellow]")
        return
    
    backups = []
    
    # Check for latest backup
    latest_backup = backup_dir / "latest"
    if latest_backup.exists():
        png_count = len(list(latest_backup.glob("*.png")))
        backups.append(f"  📁 latest ({png_count} images)")
    
    # Check for timestamped backups
    for backup_folder in sorted(backup_dir.glob("backup_*")):
        png_count = len(list(backup_folder.glob("*.png")))
        timestamp = backup_folder.name.replace("backup_", "")
        # Format timestamp for readability
        try:
            dt = datetime.strptime(timestamp, "%Y%m%d_%H%M%S")
            readable_time = dt.strftime("%Y-%m-%d %H:%M:%S")
            backups.append(f"  📁 {timestamp} ({readable_time}) - {png_count} images")
        except:
            backups.append(f"  📁 {timestamp} - {png_count} images")
    
    if backups:
        console.print("[cyan]Available backups:[/cyan]")
        for backup in backups:
            console.print(backup)
    else:
        console.print("[yellow]No backups found[/yellow]")

def main():
    """Main function for command line usage"""
    import sys
    
    if len(sys.argv) < 2:
        console.print("[bold]UI Style Image Backup Tool[/bold]")
        console.print("\nUsage:")
        console.print("  python backup_custom_images.py backup")
        console.print("  python backup_custom_images.py restore [backup_name]")
        console.print("  python backup_custom_images.py list")
        console.print("\nExamples:")
        console.print("  python backup_custom_images.py backup")
        console.print("  python backup_custom_images.py restore latest")
        console.print("  python backup_custom_images.py restore 20250619_143022")
        return
    
    command = sys.argv[1].lower()
    
    if command == "backup":
        backup_custom_images()
    elif command == "restore":
        backup_name = sys.argv[2] if len(sys.argv) > 2 else "latest"
        restore_custom_images(backup_name)
    elif command == "list":
        list_backups()
    else:
        console.print(f"[red]Unknown command: {command}[/red]")
        console.print("Use: backup, restore, or list")

if __name__ == "__main__":
    main()
