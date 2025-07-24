#!/usr/bin/env python3
"""
Simple script to start the document generation monitor
"""

from monitor import GenerationMonitor
from rich.console import Console

console = Console()

def main():
    """Start the monitor with improved error handling"""
    try:
        console.print("[bold cyan]ByteForge Document Generation Monitor[/bold cyan]")
        console.print("=" * 50)
        
        # Create monitor with auto-detected paths
        monitor = GenerationMonitor()
        
        # Show configuration
        console.print(f"[dim]Output directory: {monitor.output_path}[/dim]")
        console.print(f"[dim]Status directory: {monitor.status_path}[/dim]")
        
        # Check if directories exist
        if not monitor.output_path.exists():
            console.print(f"[yellow]Warning: Output directory does not exist: {monitor.output_path}[/yellow]")
            console.print("[yellow]The monitor will create it and wait for documents to be generated.[/yellow]")
        
        if not monitor.status_path.exists():
            console.print(f"[yellow]Warning: Status directory does not exist: {monitor.status_path}[/yellow]")
            console.print("[yellow]The monitor will create it and wait for status files to be generated.[/yellow]")
            
        console.print()
        
        # Start monitoring
        monitor.monitor_live()
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Monitor stopped by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Monitor error: {str(e)}[/red]")
        console.print("\n[dim]If this error persists, please check:[/dim]")
        console.print("[dim]1. That config.yaml exists and is valid[/dim]")
        console.print("[dim]2. That the project directory structure is correct[/dim]")
        console.print("[dim]3. That you have proper permissions to create directories[/dim]")
        
        # Optionally show traceback in debug mode
        import os
        if os.getenv("DEBUG", "").lower() in ("1", "true", "yes"):
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()