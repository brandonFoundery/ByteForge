#!/usr/bin/env python3
"""
Simple monitoring system to track Claude Code execution and generated files
"""
import time
import threading
from pathlib import Path
from datetime import datetime

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()

class CodeGenerationMonitor:
    """Monitor for tracking code generation in project/code directory"""
    
    def __init__(self, base_path: Path):
        self.base_path = base_path
        
        # CORRECTED: Monitor the actual ByteForge project code directory
        if base_path.name == "Requirements_Generation_System":
            # We're in Requirements_Generation_System, so ByteForge project is parent
            self.byteforge_path = base_path.parent
        else:
            self.byteforge_path = base_path
            
        self.code_path = self.byteforge_path / "project" / "code"  # CORRECT path
        self.logs_path = base_path / "logs"
        
        # Ensure directories exist
        self.code_path.mkdir(parents=True, exist_ok=True)
        self.logs_path.mkdir(parents=True, exist_ok=True)
        
        # Track generated files and changes
        self.generated_files = {}
        self.log_files = {}
        self.start_time = datetime.now()
        self.running = False
        
    def start_monitoring(self):
        """Start monitoring code generation"""
        self.running = True
        console.print("[green]🔍 Starting code generation monitoring...[/green]")
        console.print(f"[cyan]📁 Watching: {self.code_path}[/cyan]")
        console.print(f"[cyan]📝 Logs: {self.logs_path}[/cyan]")
        
        # Start monitoring thread
        monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        monitor_thread.start()
        
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                # Scan for generated code files
                self._scan_generated_files()
                
                # Check log files for progress
                self._check_log_files()
                
            except Exception as e:
                console.print(f"[red]Monitor error: {e}[/red]")
            
            time.sleep(2)  # Check every 2 seconds
    
    def _scan_generated_files(self):
        """Scan for newly generated code files"""
        if not self.code_path.exists():
            return
            
        # Find all files in code directory
        for file_path in self.code_path.rglob("*"):
            if file_path.is_file():
                rel_path = file_path.relative_to(self.code_path)
                
                # Check if this is a new file or changed file
                current_mtime = file_path.stat().st_mtime
                
                if str(rel_path) not in self.generated_files:
                    # New file detected
                    self.generated_files[str(rel_path)] = {
                        "path": file_path,
                        "created": datetime.fromtimestamp(current_mtime),
                        "size": file_path.stat().st_size,
                        "agent": self._guess_agent_from_path(str(rel_path))
                    }
                    console.print(f"[green]📄 New file: {rel_path}[/green]")
                
                elif self.generated_files[str(rel_path)].get("mtime", 0) != current_mtime:
                    # File was modified
                    self.generated_files[str(rel_path)]["modified"] = datetime.fromtimestamp(current_mtime)
                    self.generated_files[str(rel_path)]["size"] = file_path.stat().st_size
                    self.generated_files[str(rel_path)]["mtime"] = current_mtime
                    console.print(f"[yellow]✏️ Modified: {rel_path}[/yellow]")
    
    def _guess_agent_from_path(self, path: str) -> str:
        """Guess which agent generated the file based on path"""
        if "backend" in path.lower():
            return "Backend Agent"
        elif "frontend" in path.lower():
            return "Frontend Agent"
        elif "infrastructure" in path.lower():
            return "Infrastructure Agent"
        elif "security" in path.lower():
            return "Security Agent"
        elif "integration" in path.lower():
            return "Integration Agent"
        else:
            return "Unknown Agent"
    
    def _check_log_files(self):
        """Check Claude Code execution logs"""
        if not self.logs_path.exists():
            return
            
        for log_file in self.logs_path.glob("*claude_execution.log"):
            try:
                if log_file.name not in self.log_files:
                    self.log_files[log_file.name] = {
                        "path": log_file,
                        "last_size": 0
                    }
                
                current_size = log_file.stat().st_size
                if current_size > self.log_files[log_file.name]["last_size"]:
                    # Log file grew - read new content
                    with open(log_file, 'r', encoding='utf-8') as f:
                        f.seek(self.log_files[log_file.name]["last_size"])
                        new_content = f.read()
                        if new_content.strip():
                            console.print(f"[dim]📝 {log_file.name}: {new_content.strip()[-100:]}[/dim]")
                    
                    self.log_files[log_file.name]["last_size"] = current_size
                    
            except Exception as e:
                console.print(f"[red]Error reading log {log_file}: {e}[/red]")
    
    def create_display(self):
        """Create Rich display layout"""
        layout = Layout()
        
        layout.split_column(
            Layout(name="header", size=5),
            Layout(name="main", ratio=1),
            Layout(name="footer", size=3)
        )
        
        layout["main"].split_row(
            Layout(name="files", ratio=2),
            Layout(name="stats", ratio=1)
        )
        
        # Header
        elapsed = datetime.now() - self.start_time
        layout["header"].update(Panel(
            f"[bold blue]🤖 Claude Code Generation Monitor[/bold blue]\n"
            f"[cyan]Started: {self.start_time.strftime('%H:%M:%S')}[/cyan] | "
            f"[green]Elapsed: {str(elapsed).split('.')[0]}[/green]\n"
            f"[dim]Watching: {self.code_path}[/dim]",
            style="cyan"
        ))
        
        # Generated files table
        files_table = Table(title="Generated Code Files")
        files_table.add_column("File", style="cyan")
        files_table.add_column("Agent", style="magenta")
        files_table.add_column("Size", style="green") 
        files_table.add_column("Created", style="yellow")
        
        for rel_path, file_info in self.generated_files.items():
            size_str = f"{file_info['size']:,} bytes"
            created_str = file_info['created'].strftime('%H:%M:%S')
            
            files_table.add_row(
                rel_path,
                file_info['agent'],
                size_str,
                created_str
            )
        
        if not self.generated_files:
            files_table.add_row("[dim]No files generated yet[/dim]", "", "", "")
        
        layout["files"].update(Panel(files_table, title="Generated Files"))
        
        # Stats
        stats_text = Text()
        stats_text.append(f"Total Files: {len(self.generated_files)}\n", style="green")
        
        # Count by agent
        agent_counts = {}
        for file_info in self.generated_files.values():
            agent = file_info['agent']
            agent_counts[agent] = agent_counts.get(agent, 0) + 1
        
        for agent, count in agent_counts.items():
            stats_text.append(f"{agent}: {count}\n", style="cyan")
        
        # Log file count
        stats_text.append(f"\nLog Files: {len(self.log_files)}\n", style="yellow")
        
        layout["stats"].update(Panel(stats_text, title="Statistics"))
        
        # Footer
        layout["footer"].update(Panel(
            "[dim]Press Ctrl+C to stop monitoring[/dim]",
            style="blue"
        ))
        
        return layout
    
    def stop(self):
        """Stop monitoring"""
        self.running = False
        console.print("[yellow]⏹️ Monitoring stopped[/yellow]")

def monitor_code_generation(base_path: Path):
    """Start real-time monitoring of code generation"""
    monitor = CodeGenerationMonitor(base_path)
    monitor.start_monitoring()
    
    try:
        with Live(monitor.create_display(), refresh_per_second=2, screen=True) as live:
            while monitor.running:
                live.update(monitor.create_display())
                time.sleep(0.5)
    except KeyboardInterrupt:
        console.print("\n[yellow]Monitoring stopped by user[/yellow]")
    finally:
        monitor.stop()

if __name__ == "__main__":
    base_path = Path(__file__).parent
    monitor_code_generation(base_path)