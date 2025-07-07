#!/usr/bin/env python3
"""
Real-time monitoring of LSOMigrator code generation
"""

import time
import os
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

console = Console()

BYTEFORGE_PATH = "/mnt/d/Repository/ContractLogix/LSOMitigator/ByteForge"
CODE_PATH = f"{BYTEFORGE_PATH}/project/code"
LOGS_PATH = f"{BYTEFORGE_PATH}/Requirements_Generation_System/logs"

def count_files_in_directory(directory):
    """Count files recursively in a directory"""
    if not os.path.exists(directory):
        return 0, 0
    
    files = 0
    dirs = 0
    for root, dirnames, filenames in os.walk(directory):
        files += len(filenames)
        dirs += len(dirnames)
    
    return files, dirs

def get_file_size(directory):
    """Get total size of files in directory"""
    if not os.path.exists(directory):
        return 0
    
    total_size = 0
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                total_size += os.path.getsize(file_path)
            except (OSError, IOError):
                pass
    
    return total_size

def format_size(size_bytes):
    """Format size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.1f} {size_names[i]}"

def check_component_status():
    """Check which components have been generated"""
    components = {
        "Backend": f"{CODE_PATH}/LSOMigrator.Backend",
        "Frontend": f"{CODE_PATH}/LSOMigrator.Frontend", 
        "Infrastructure": f"{CODE_PATH}/terraform",
        "Security": f"{CODE_PATH}/Security",
        "Integration": f"{CODE_PATH}/Integration"
    }
    
    status = {}
    for name, path in components.items():
        if os.path.exists(path):
            files, dirs = count_files_in_directory(path)
            size = get_file_size(path)
            status[name] = {
                "exists": True,
                "files": files,
                "dirs": dirs,
                "size": format_size(size)
            }
        else:
            status[name] = {
                "exists": False,
                "files": 0,
                "dirs": 0,
                "size": "0 B"
            }
    
    return status

def create_status_table():
    """Create a status table showing component progress"""
    table = Table(title="🚀 LSOMigrator Code Generation Progress")
    
    table.add_column("Component", style="cyan", no_wrap=True)
    table.add_column("Status", style="magenta")
    table.add_column("Files", justify="right", style="green")
    table.add_column("Dirs", justify="right", style="blue")
    table.add_column("Size", justify="right", style="yellow")
    table.add_column("Description", style="white")
    
    status = check_component_status()
    
    descriptions = {
        "Backend": "ASP.NET Core Web API",
        "Frontend": "Next.js React App", 
        "Infrastructure": "Terraform Azure IaC",
        "Security": "Auth & Protection",
        "Integration": "External APIs"
    }
    
    for component, info in status.items():
        status_text = "✅ Generated" if info["exists"] else "⏳ Pending"
        table.add_row(
            component,
            status_text,
            str(info["files"]),
            str(info["dirs"]),
            info["size"],
            descriptions.get(component, "")
        )
    
    return table

def get_recent_logs():
    """Get recent log entries"""
    logs = []
    if os.path.exists(LOGS_PATH):
        for log_file in os.listdir(LOGS_PATH):
            if log_file.endswith('.log'):
                file_path = os.path.join(LOGS_PATH, log_file)
                try:
                    mtime = os.path.getmtime(file_path)
                    size = os.path.getsize(file_path)
                    logs.append((log_file, mtime, format_size(size)))
                except (OSError, IOError):
                    pass
    
    # Sort by modification time (most recent first)
    logs.sort(key=lambda x: x[1], reverse=True)
    return logs[:5]  # Return 5 most recent

def create_logs_panel():
    """Create a panel showing recent log activity"""
    logs = get_recent_logs()
    
    if not logs:
        content = "📝 No logs available yet"
    else:
        content = "📝 Recent Log Activity:\n\n"
        for log_file, mtime, size in logs:
            time_str = time.strftime("%H:%M:%S", time.localtime(mtime))
            content += f"• {log_file} ({size}) - {time_str}\n"
    
    return Panel(content, title="Log Monitor", border_style="green")

def main():
    """Main monitoring loop"""
    console.print("🔍 [bold green]LSOMigrator Generation Monitor[/bold green]")
    console.print(f"📁 Monitoring: {CODE_PATH}")
    console.print(f"📝 Logs: {LOGS_PATH}")
    console.print("⌨️  Press Ctrl+C to exit\n")
    
    with Live(console=console, refresh_per_second=2) as live:
        try:
            while True:
                # Create the main display
                status_table = create_status_table()
                logs_panel = create_logs_panel()
                
                # Get overall stats
                total_files, total_dirs = count_files_in_directory(CODE_PATH)
                total_size = format_size(get_file_size(CODE_PATH))
                
                # Create summary panel
                summary = Panel(
                    f"📊 Total Files: {total_files} | 📁 Total Directories: {total_dirs} | 💾 Total Size: {total_size}",
                    title="Summary",
                    border_style="blue"
                )
                
                # Combine all elements
                from rich.columns import Columns
                display = Columns([status_table, logs_panel], equal=True)
                
                # Create final layout
                from rich.console import Group
                layout = Group(summary, "", display)
                
                live.update(layout)
                time.sleep(2)
                
        except KeyboardInterrupt:
            console.print("\n👋 Monitoring stopped by user")

if __name__ == "__main__":
    main()