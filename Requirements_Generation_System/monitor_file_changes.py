#!/usr/bin/env python3
"""
Real-time file change monitor for Claude Code execution
"""

import time
import os
from pathlib import Path
from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from datetime import datetime

console = Console()


class FileMonitor:
    """Monitor file changes in FrontEnd and BackEnd directories"""
    
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.frontend_path = base_path / "FrontEnd"
        self.backend_path = base_path / "BackEnd"
        self.log_file = base_path / "logs" / "claude_terminal_execution.log"
        
        # Track initial state
        self.initial_files = self._get_current_files()
        self.start_time = time.time()
        
    def _get_current_files(self):
        """Get current file list with timestamps"""
        files = {}
        
        # Check FrontEnd
        if self.frontend_path.exists():
            for file in self.frontend_path.rglob("*"):
                if file.is_file() and file.suffix in ['.tsx', '.ts', '.js', '.json', '.css']:
                    try:
                        files[str(file)] = file.stat().st_mtime
                    except:
                        pass
        
        # Check BackEnd
        if self.backend_path.exists():
            for file in self.backend_path.rglob("*"):
                if file.is_file() and file.suffix in ['.cs', '.json', '.csproj']:
                    try:
                        files[str(file)] = file.stat().st_mtime
                    except:
                        pass
        
        return files
    
    def _get_log_status(self):
        """Get current status from log file"""
        if not self.log_file.exists():
            return "Log file not found", "yellow"
        
        try:
            with open(self.log_file, 'r') as f:
                content = f.read()
            
            if "SUCCESS:" in content:
                return "Execution completed successfully", "green"
            elif "FAILED:" in content:
                return "Execution failed", "red"
            elif "Launching Claude Code" in content:
                return "Claude Code is running...", "blue"
            elif "Starting Claude Code execution" in content:
                return "Execution started", "yellow"
            else:
                return "Waiting for execution to start", "dim"
        except:
            return "Could not read log file", "red"
    
    def get_changes(self):
        """Get file changes since monitoring started"""
        current_files = self._get_current_files()
        
        new_files = []
        modified_files = []
        
        for file_path, mtime in current_files.items():
            if file_path not in self.initial_files:
                # New file
                new_files.append({
                    'path': file_path,
                    'time': datetime.fromtimestamp(mtime).strftime("%H:%M:%S"),
                    'size': self._get_file_size(file_path)
                })
            elif mtime > self.initial_files[file_path]:
                # Modified file
                modified_files.append({
                    'path': file_path,
                    'time': datetime.fromtimestamp(mtime).strftime("%H:%M:%S"),
                    'size': self._get_file_size(file_path)
                })
        
        return new_files, modified_files
    
    def _get_file_size(self, file_path):
        """Get human-readable file size"""
        try:
            size = os.path.getsize(file_path)
            if size < 1024:
                return f"{size} B"
            elif size < 1024 * 1024:
                return f"{size // 1024} KB"
            else:
                return f"{size // (1024 * 1024)} MB"
        except:
            return "Unknown"
    
    def _shorten_path(self, file_path, max_length=60):
        """Shorten file path for display"""
        if len(file_path) <= max_length:
            return file_path
        
        # Try to show relative path from base
        try:
            rel_path = str(Path(file_path).relative_to(self.base_path))
            if len(rel_path) <= max_length:
                return rel_path
        except:
            pass
        
        # Truncate from the middle
        if len(file_path) > max_length:
            start = file_path[:max_length//2-2]
            end = file_path[-(max_length//2-2):]
            return f"{start}...{end}"
        
        return file_path
    
    def create_status_table(self):
        """Create status table for display"""
        new_files, modified_files = self.get_changes()
        log_status, log_color = self._get_log_status()
        
        # Main status panel
        elapsed = int(time.time() - self.start_time)
        status_text = f"""
[bold]Claude Code File Monitor[/bold]

[{log_color}]Status: {log_status}[/{log_color}]
[dim]Elapsed: {elapsed}s[/dim]
[dim]Monitoring: FrontEnd & BackEnd directories[/dim]

[green]New files: {len(new_files)}[/green]
[yellow]Modified files: {len(modified_files)}[/yellow]
"""
        
        # Files table
        table = Table(title="File Changes", show_header=True, header_style="bold magenta")
        table.add_column("Type", style="cyan", width=8)
        table.add_column("File", style="white", width=50)
        table.add_column("Time", style="green", width=8)
        table.add_column("Size", style="yellow", width=8)
        
        # Add new files
        for file_info in new_files[-10:]:  # Show last 10
            short_path = self._shorten_path(file_info['path'], 45)
            table.add_row("NEW", short_path, file_info['time'], file_info['size'])
        
        # Add modified files
        for file_info in modified_files[-10:]:  # Show last 10
            short_path = self._shorten_path(file_info['path'], 45)
            table.add_row("MODIFIED", short_path, file_info['time'], file_info['size'])
        
        if len(new_files) == 0 and len(modified_files) == 0:
            table.add_row("", "[dim]No changes detected yet...[/dim]", "", "")
        
        return Panel(status_text, title="Status"), table


def monitor_files():
    """Monitor file changes in real-time"""
    
    base_path = Path("D:/Repository/@Clients/FY.WB.Midway")
    monitor = FileMonitor(base_path)
    
    console.print("[bold blue]Starting Real-time File Monitor[/bold blue]")
    console.print("[dim]Monitoring FrontEnd and BackEnd directories for changes...[/dim]")
    console.print("[dim]Press Ctrl+C to stop[/dim]\n")
    
    try:
        with Live(console=console, refresh_per_second=2) as live:
            while True:
                status_panel, files_table = monitor.create_status_table()
                
                # Create combined display
                from rich.columns import Columns
                display = Columns([status_panel, files_table], equal=False, expand=True)
                
                live.update(display)
                time.sleep(1)
                
    except KeyboardInterrupt:
        console.print("\n[yellow]Monitoring stopped by user[/yellow]")
        
        # Final summary
        new_files, modified_files = monitor.get_changes()
        console.print(f"\n[bold]Final Summary:[/bold]")
        console.print(f"[green]New files created: {len(new_files)}[/green]")
        console.print(f"[yellow]Files modified: {len(modified_files)}[/yellow]")
        
        if new_files:
            console.print(f"\n[bold green]New files:[/bold green]")
            for file_info in new_files:
                rel_path = monitor._shorten_path(file_info['path'], 80)
                console.print(f"  • {rel_path} ({file_info['size']})")
        
        if modified_files:
            console.print(f"\n[bold yellow]Modified files:[/bold yellow]")
            for file_info in modified_files:
                rel_path = monitor._shorten_path(file_info['path'], 80)
                console.print(f"  • {rel_path} ({file_info['size']})")


if __name__ == "__main__":
    monitor_files()
