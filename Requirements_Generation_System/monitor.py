import time
import json
from pathlib import Path
from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
import yaml

console = Console()


class GenerationMonitor:
    """Real-time monitor for document generation progress"""
    
    def __init__(self, output_path: Path):
        self.output_path = output_path
        self.history = deque(maxlen=100)
        
    def get_status(self):
        """Get current status of all documents"""
        status = {}
        
        for doc_file in self.output_path.glob("*.md"):
            if doc_file.name == "status_report.txt":
                continue
                
            # Read metadata from file
            # Attempt to read using UTF-8 and ignore any undecodable bytes to prevent UnicodeDecodeError
            content = doc_file.read_text(encoding="utf-8", errors="ignore")
            if content.startswith("---"):
                metadata_end = content.find("---", 3)
                if metadata_end > 0:
                    metadata = yaml.safe_load(content[3:metadata_end])
                    status[metadata.get("id", doc_file.stem)] = {
                        "title": metadata.get("title", "Unknown"),
                        "status": metadata.get("status", "unknown"),
                        "generated_at": metadata.get("generated_at", "N/A"),
                        "refined_count": metadata.get("refined_count", 0),
                        "file_size": doc_file.stat().st_size
                    }
        
        return status
    
    def create_status_table(self):
        """Create a rich table showing current status"""
        table = Table(title=f"Document Generation Progress - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        table.add_column("Document", style="cyan", no_wrap=True)
        table.add_column("Status", style="magenta")
        table.add_column("Size", style="green")
        table.add_column("Refined", style="yellow")
        table.add_column("Generated At", style="blue")
        
        status = self.get_status()
        
        # Define document order
        doc_order = ["BRD", "PRD", "FRD", "NFRD", "DRD", "DB_SCHEMA", "TRD", "API_SPEC", "TEST_PLAN", "RTM"]
        
        # Add rows in order, then any remaining
        processed = set()
        
        for doc_id in doc_order:
            if doc_id in status:
                info = status[doc_id]
                processed.add(doc_id)
                
                status_emoji = {
                    "not_started": "⏸️",
                    "in_progress": "🔄",
                    "generated": "✅",
                    "refined": "🔧",
                    "validated": "✨",
                    "failed": "❌"
                }.get(info["status"], "❓")
                
                size_kb = info["file_size"] / 1024
                
                table.add_row(
                    info["title"],
                    f"{status_emoji} {info['status']}",
                    f"{size_kb:.1f} KB",
                    str(info["refined_count"]),
                    info["generated_at"][:19] if info["generated_at"] != "N/A" else "N/A"
                )
        
        # Add any remaining documents not in the order
        for doc_id, info in sorted(status.items()):
            if doc_id not in processed:
                status_emoji = {
                    "not_started": "⏸️",
                    "in_progress": "🔄",
                    "generated": "✅",
                    "refined": "🔧",
                    "validated": "✨",
                    "failed": "❌"
                }.get(info["status"], "❓")
                
                size_kb = info["file_size"] / 1024
                
                table.add_row(
                    info["title"],
                    f"{status_emoji} {info['status']}",
                    f"{size_kb:.1f} KB",
                    str(info["refined_count"]),
                    info["generated_at"][:19] if info["generated_at"] != "N/A" else "N/A"
                )
        
        return table
    
    def create_progress_summary(self):
        """Create a summary of overall progress"""
        status = self.get_status()
        
        total_docs = 10  # Expected number of documents
        completed = sum(1 for info in status.values() if info["status"] in ["validated", "refined", "generated"])
        failed = sum(1 for info in status.values() if info["status"] == "failed")
        in_progress = sum(1 for info in status.values() if info["status"] == "in_progress")
        
        progress_bar = Progress(
            TextColumn("[bold blue]Overall Progress"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TextColumn(f"{completed}/{total_docs} documents")
        )
        
        with progress_bar:
            task = progress_bar.add_task("Progress", total=total_docs)
            progress_bar.update(task, completed=completed)
        
        summary = f"\n[bold]Summary:[/bold]\n"
        summary += f"  ✅ Completed: {completed}\n"
        summary += f"  🔄 In Progress: {in_progress}\n"
        summary += f"  ❌ Failed: {failed}\n"
        summary += f"  ⏸️  Not Started: {total_docs - completed - failed - in_progress}\n"
        
        return summary
    
    def monitor_live(self, refresh_rate: int = 2):
        """Live monitoring with auto-refresh"""
        console.print("[bold cyan]Starting Document Generation Monitor[/bold cyan]")
        console.print(f"Monitoring: {self.output_path}\n")
        console.print("Press Ctrl+C to stop monitoring\n")
        
        with Live(self.create_status_table(), refresh_per_second=1/refresh_rate, vertical_overflow="visible") as live:
            while True:
                try:
                    time.sleep(refresh_rate)
                    
                    # Update the display
                    table = self.create_status_table()
                    summary = self.create_progress_summary()
                    
                    # Combine table and summary
                    console.clear()
                    live.update(table)
                    console.print(summary)
                    
                    # Check for completion
                    status = self.get_status()
                    if len(status) >= 10:  # All documents present
                        if all(info["status"] in ["validated", "failed"] for info in status.values()):
                            console.print("\n[bold green]All documents processed![/bold green]")
                            
                            # Final summary
                            validated = sum(1 for info in status.values() if info["status"] == "validated")
                            failed = sum(1 for info in status.values() if info["status"] == "failed")
                            
                            console.print(f"\n[bold]Final Results:[/bold]")
                            console.print(f"  ✨ Validated: {validated}")
                            console.print(f"  ❌ Failed: {failed}")
                            
                            break
                except KeyboardInterrupt:
                    console.print("\n[yellow]Monitor stopped by user[/yellow]")
                    break
                except Exception as e:
                    console.print(f"[red]Error: {str(e)}[/red]")
                    time.sleep(5)  # Wait before retrying


def main():
    """Run the monitor"""
    import sys
    
    # Allow custom path as argument
    if len(sys.argv) > 1:
        output_path = Path(sys.argv[1])
    else:
        output_path = Path("project/generated_documents")
    
    if not output_path.exists():
        console.print(f"[red]Output directory not found: {output_path}[/red]")
        console.print("\nUsage: python monitor.py [output_directory]")
        return
    
    monitor = GenerationMonitor(output_path)
    
    try:
        monitor.monitor_live()
    except KeyboardInterrupt:
        console.print("\n[yellow]Monitor stopped by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Monitor error: {str(e)}[/red]")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()