#!/usr/bin/env python3
"""
Reset failed documents to trigger regeneration with enhanced auto-repair
"""

import json
import sys
from pathlib import Path
from rich.console import Console
from rich.prompt import Confirm

console = Console()

def main():
    """Reset failed documents"""
    
    console.print("[bold blue]Reset Failed Documents[/bold blue]")
    console.print("This will reset all failed documents so they can be regenerated with enhanced auto-repair.")
    
    if not Confirm.ask("Do you want to continue?"):
        console.print("[yellow]Operation cancelled.[/yellow]")
        return
    
    status_dir = Path(__file__).parent.parent / "generation_status"
    
    if not status_dir.exists():
        console.print(f"[red]Status directory not found: {status_dir}[/red]")
        return
    
    failed_docs = []
    reset_count = 0
    
    # Find all failed documents
    for status_file in status_dir.glob("status_*.json"):
        try:
            with open(status_file, 'r') as f:
                status_data = json.load(f)
            
            if status_data.get('status') == 'failed':
                failed_docs.append({
                    'file': status_file,
                    'title': status_data.get('title', 'Unknown'),
                    'error': status_data.get('error_message', 'Unknown error')
                })
        except Exception as e:
            console.print(f"[yellow]Warning: Could not read {status_file}: {e}[/yellow]")
    
    if not failed_docs:
        console.print("[green]No failed documents found![/green]")
        return
    
    console.print(f"\n[yellow]Found {len(failed_docs)} failed documents:[/yellow]")
    for doc in failed_docs:
        console.print(f"  - {doc['title']}: {doc['error']}")
    
    console.print(f"\n[blue]Resetting failed documents...[/blue]")
    
    # Reset each failed document
    for doc in failed_docs:
        try:
            # Delete the status file to trigger regeneration
            doc['file'].unlink()
            console.print(f"[green]✓ Reset {doc['title']}[/green]")
            reset_count += 1
        except Exception as e:
            console.print(f"[red]✗ Failed to reset {doc['title']}: {e}[/red]")
    
    console.print(f"\n[green]Successfully reset {reset_count} documents![/green]")
    console.print(f"[yellow]Run 'python orchestrator.py --skip-existing' to regenerate with enhanced auto-repair.[/yellow]")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user.[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]Error: {str(e)}[/red]")
        sys.exit(1)
