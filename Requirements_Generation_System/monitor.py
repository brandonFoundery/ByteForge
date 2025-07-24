import time
import json
import os
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

def load_config(config_path: Path = None) -> dict:
    """Load configuration from YAML file"""
    if config_path is None:
        config_path = Path(__file__).parent / "config.yaml"
    
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        console.print(f"[red]Error loading config: {e}[/red]")
        return {}


class GenerationMonitor:
    """Real-time monitor for document generation progress"""
    
    def __init__(self, output_path: Path = None, status_path: Path = None):
        # Load config to get correct paths
        self.config = load_config()
        
        # Use provided paths or get from config
        if output_path is None:
            script_dir = Path(__file__).parent
            output_dir = self.config.get('paths', {}).get('output_dir', '../project/requirements')
            if output_dir.startswith('../'):
                output_dir = output_dir[3:]  # Remove '../'
            self.output_path = script_dir.parent / output_dir
        else:
            self.output_path = output_path
            
        if status_path is None:
            script_dir = Path(__file__).parent
            status_dir = self.config.get('paths', {}).get('status_dir', '../project/generation_status')
            if status_dir.startswith('../'):
                status_dir = status_dir[3:]  # Remove '../'
            self.status_path = script_dir.parent / status_dir
        else:
            self.status_path = status_path
            
        self.history = deque(maxlen=100)
        
        # Create directories if they don't exist
        self.output_path.mkdir(parents=True, exist_ok=True)
        self.status_path.mkdir(parents=True, exist_ok=True)
        
        console.print(f"[dim]Monitoring output: {self.output_path}[/dim]")
        console.print(f"[dim]Monitoring status: {self.status_path}[/dim]")
        
    def get_status(self):
        """Get current status of all documents from both status files and document metadata"""
        status = {}
        
        # First, try to read from JSON status files
        for status_file in self.status_path.glob("status_*.json"):
            try:
                with open(status_file, 'r', encoding='utf-8') as f:
                    status_data = json.load(f)
                    doc_id = status_data.get('document_type', status_file.stem.replace('status_', '').upper())
                    
                    # Get corresponding document file for size
                    doc_file = self.output_path / f"{doc_id.lower()}.md"
                    file_size = doc_file.stat().st_size if doc_file.exists() else 0
                    
                    status[doc_id] = {
                        "title": status_data.get('document_type', doc_id),
                        "status": status_data.get('status', 'unknown'),
                        "generated_at": status_data.get('generated_at', 'N/A'),
                        "refined_count": status_data.get('refined_count', 0),
                        "file_size": file_size
                    }
            except Exception as e:
                console.print(f"[yellow]Warning: Could not read status file {status_file}: {e}[/yellow]")
        
        # Then, read from document metadata (fallback or supplement)
        if self.output_path.exists():
            for doc_file in self.output_path.glob("*.md"):
                if doc_file.name == "status_report.txt":
                    continue
                    
                try:
                    # Read metadata from file
                    content = doc_file.read_text(encoding="utf-8", errors="ignore")
                    if content.startswith("---"):
                        metadata_end = content.find("---", 3)
                        if metadata_end > 0:
                            metadata = yaml.safe_load(content[3:metadata_end])
                            doc_id = metadata.get("id", doc_file.stem.upper())
                            
                            # Only add if not already from status file (status files are more authoritative)
                            if doc_id not in status:
                                status[doc_id] = {
                                    "title": metadata.get("title", "Unknown"),
                                    "status": metadata.get("status", "unknown"),
                                    "generated_at": metadata.get("generated_at", "N/A"),
                                    "refined_count": metadata.get("refined_count", 0),
                                    "file_size": doc_file.stat().st_size
                                }
                except Exception as e:
                    console.print(f"[yellow]Warning: Could not read document {doc_file}: {e}[/yellow]")
        
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
                
                generated_at = info["generated_at"]
                if generated_at and generated_at != "N/A":
                    generated_at_display = generated_at[:19] if len(generated_at) > 19 else generated_at
                else:
                    generated_at_display = "N/A"
                
                table.add_row(
                    info["title"],
                    f"{status_emoji} {info['status']}",
                    f"{size_kb:.1f} KB",
                    str(info["refined_count"]),
                    generated_at_display
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
                
                generated_at = info["generated_at"]
                if generated_at and generated_at != "N/A":
                    generated_at_display = generated_at[:19] if len(generated_at) > 19 else generated_at
                else:
                    generated_at_display = "N/A"
                
                table.add_row(
                    info["title"],
                    f"{status_emoji} {info['status']}",
                    f"{size_kb:.1f} KB",
                    str(info["refined_count"]),
                    generated_at_display
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
        console.print(f"Monitoring output: {self.output_path}")
        console.print(f"Monitoring status: {self.status_path}")
        console.print("Press Ctrl+C to stop monitoring\n")
        
        last_status_hash = None
        
        try:
            with Live(console=console, refresh_per_second=1/refresh_rate, vertical_overflow="visible") as live:
                while True:
                    try:
                        # Get current status
                        current_status = self.get_status()
                        current_status_hash = hash(str(sorted(current_status.items())))
                        
                        # Only update display if status has actually changed or it's the first run
                        if current_status_hash != last_status_hash:
                            table = self.create_status_table()
                            summary = self.create_progress_summary()
                            
                            # Create combined display
                            combined_output = table
                            live.update(combined_output)
                            
                            # Print summary below the table (not in live update to avoid conflicts)
                            if last_status_hash is not None:  # Don't print on first run
                                console.print(summary)
                            
                            last_status_hash = current_status_hash
                        
                        # Check for completion
                        if len(current_status) >= 10:  # All documents present
                            if all(info["status"] in ["validated", "failed"] for info in current_status.values()):
                                live.stop()
                                console.print("\n[bold green]All documents processed![/bold green]")
                                
                                # Final summary
                                validated = sum(1 for info in current_status.values() if info["status"] == "validated")
                                failed = sum(1 for info in current_status.values() if info["status"] == "failed")
                                
                                console.print(f"\n[bold]Final Results:[/bold]")
                                console.print(f"  ✨ Validated: {validated}")
                                console.print(f"  ❌ Failed: {failed}")
                                break
                        
                        time.sleep(refresh_rate)
                        
                    except KeyboardInterrupt:
                        live.stop()
                        console.print("\n[yellow]Monitor stopped by user[/yellow]")
                        break
                    except Exception as e:
                        console.print(f"[red]Monitor error: {str(e)}[/red]")
                        time.sleep(5)  # Wait before retrying
                        
        except Exception as e:
            console.print(f"[red]Fatal monitor error: {str(e)}[/red]")
            import traceback
            traceback.print_exc()


def main():
    """Run the monitor"""
    import sys
    
    # Allow custom path as argument
    if len(sys.argv) > 1:
        output_path = Path(sys.argv[1])
        monitor = GenerationMonitor(output_path)
    else:
        # Use config-based paths (auto-detected)
        monitor = GenerationMonitor()
    
    # Check if directories exist, create them if needed
    if not monitor.output_path.exists():
        console.print(f"[yellow]Output directory does not exist, creating: {monitor.output_path}[/yellow]")
        monitor.output_path.mkdir(parents=True, exist_ok=True)
    
    if not monitor.status_path.exists():
        console.print(f"[yellow]Status directory does not exist, creating: {monitor.status_path}[/yellow]")
        monitor.status_path.mkdir(parents=True, exist_ok=True)
    
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