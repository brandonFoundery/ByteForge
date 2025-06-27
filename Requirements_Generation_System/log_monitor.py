#!/usr/bin/env python3
"""
Claude Code Log Monitor
Real-time monitoring and color-coded display of Claude Code execution logs
"""

import os
import time
import json
import re
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import argparse

try:
    from rich.console import Console
    from rich.live import Live
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    from rich.layout import Layout
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
    from rich.syntax import Syntax
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("Rich not available. Install with: pip install rich")

class LogMonitor:
    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path) if base_path else Path.cwd().parent
        self.logs_path = self.base_path / "logs"
        self.progress_tracker_path = self.base_path / "generated_documents" / "design" / "claude_instructions" / "progress_tracker.json"
        
        if RICH_AVAILABLE:
            self.console = Console()
        
        # Color coding patterns
        self.patterns = {
            'success': [
                r'✅', r'SUCCESS', r'completed successfully', r'BUILD SUCCEEDED',
                r'All tests passed', r'Migration applied successfully'
            ],
            'error': [
                r'❌', r'ERROR', r'FAILED', r'Exception', r'BUILD FAILED',
                r'Test failed', r'Migration failed'
            ],
            'warning': [
                r'⚠️', r'WARNING', r'WARN', r'deprecated', r'obsolete'
            ],
            'info': [
                r'ℹ️', r'INFO', r'Starting', r'Loading', r'Creating',
                r'Updating', r'Processing'
            ],
            'progress': [
                r'🚀', r'🔍', r'📖', r'🤖', r'⏳', r'📋',
                r'Building', r'Testing', r'Implementing'
            ],
            'file_ops': [
                r'Created file:', r'Modified file:', r'Deleted file:',
                r'\.cs$', r'\.tsx?$', r'\.json$'
            ],
            'commands': [
                r'dotnet', r'npm', r'yarn', r'git', r'claude'
            ]
        }
    
    def get_log_files(self) -> List[Path]:
        """Get all Claude execution log files"""
        if not self.logs_path.exists():
            return []

        log_files = []
        # Get all Claude execution log files including phase-specific ones
        patterns = [
            "*_claude_execution.log",
            "*_phase*_claude_execution.log"
        ]

        for pattern in patterns:
            for file in self.logs_path.glob(pattern):
                if file not in log_files:
                    log_files.append(file)

        return sorted(log_files, key=lambda x: x.stat().st_mtime, reverse=True)
    
    def get_progress_status(self) -> Dict:
        """Get current progress from progress tracker"""
        if not self.progress_tracker_path.exists():
            # Try alternative paths
            alternative_paths = [
                self.base_path.parent / "generated_documents" / "design" / "claude_instructions" / "progress_tracker.json",
                Path("../generated_documents/design/claude_instructions/progress_tracker.json"),
                Path("generated_documents/design/claude_instructions/progress_tracker.json")
            ]

            for alt_path in alternative_paths:
                if alt_path.exists():
                    self.progress_tracker_path = alt_path
                    break
            else:
                return {}

        try:
            with open(self.progress_tracker_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading progress data: {e}")
            return {}
    
    def colorize_line(self, line: str) -> Text:
        """Apply color coding to a log line"""
        if not RICH_AVAILABLE:
            return line
        
        text = Text(line)
        
        # Check patterns and apply colors
        for category, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    if category == 'success':
                        text.stylize("bold green")
                    elif category == 'error':
                        text.stylize("bold red")
                    elif category == 'warning':
                        text.stylize("bold yellow")
                    elif category == 'info':
                        text.stylize("cyan")
                    elif category == 'progress':
                        text.stylize("bold blue")
                    elif category == 'file_ops':
                        text.stylize("magenta")
                    elif category == 'commands':
                        text.stylize("bold white")
                    break
        
        return text
    
    def create_status_table(self, progress_data: Dict) -> Table:
        """Create a status table showing agent progress"""
        table = Table(title="🤖 Claude Code Agent Status", show_header=True, header_style="bold magenta")
        table.add_column("Agent", style="cyan", no_wrap=True)
        table.add_column("Phase", style="blue")
        table.add_column("Status", style="bold")
        table.add_column("Duration", style="green")
        table.add_column("Progress", style="yellow")
        
        if not progress_data:
            table.add_row("No data", "N/A", "N/A", "N/A", "N/A")
            return table
        
        # Extract agent information from progress data - handle all phases
        phase_order = ["phase1_mvp_core_features", "phase2_advanced_features", "phase3_production_ready"]

        for phase_name in phase_order:
            if phase_name not in progress_data:
                continue

            phase_data = progress_data[phase_name]
            if not isinstance(phase_data, dict):
                continue

            agents = phase_data.get("agents", {})
            if not agents:
                continue

            # Sort agents for consistent display
            agent_order = ["backend", "frontend", "security", "infrastructure", "integration"]
            sorted_agents = []

            for base_agent in agent_order:
                for agent_id in agents.keys():
                    if base_agent in agent_id.lower():
                        sorted_agents.append(agent_id)
                        break

            # Add any remaining agents not in the standard order
            for agent_id in agents.keys():
                if agent_id not in sorted_agents:
                    sorted_agents.append(agent_id)

            for agent_id in sorted_agents:
                agent_data = agents[agent_id]
                if not isinstance(agent_data, dict):
                    continue

                status = agent_data.get("status", "unknown")
                started_at = agent_data.get("started_at")
                completed_at = agent_data.get("completed_at")

                # Calculate duration
                duration = "N/A"
                if started_at:
                    if completed_at:
                        duration = f"{agent_data.get('actual_duration_minutes', 0):.1f}m"
                    else:
                        current_duration = (time.time() - started_at) / 60
                        duration = f"{current_duration:.1f}m"

                # Status styling
                if status == "completed":
                    status_text = "[green]✅ Complete[/green]"
                elif status == "in_progress":
                    status_text = "[blue]🔄 Running[/blue]"
                elif status == "failed":
                    status_text = "[red]❌ Failed[/red]"
                else:
                    status_text = "[dim]⏸️ Waiting[/dim]"

                # Progress indicator
                estimated = agent_data.get("estimated_duration_minutes", 60)
                if status == "in_progress" and started_at:
                    current_duration = (time.time() - started_at) / 60
                    progress_pct = min(100, (current_duration / estimated) * 100)
                    progress_text = f"{progress_pct:.0f}%"
                elif status == "completed":
                    progress_text = "100%"
                else:
                    progress_text = "0%"

                # Clean up display names
                agent_display = agent_id.replace("-", " ").replace("phase", "Phase").title()

                # Create better phase display names
                phase_display_map = {
                    "phase1_mvp_core_features": "Phase 1 - MVP Core",
                    "phase2_advanced_features": "Phase 2 - Advanced Features",
                    "phase3_production_ready": "Phase 3 - Production Ready"
                }
                phase_display = phase_display_map.get(phase_name, phase_name.replace("_", " ").title())

                table.add_row(
                    agent_display,
                    phase_display,
                    status_text,
                    duration,
                    progress_text
                )
        
        return table
    
    def monitor_logs(self, follow: bool = True, refresh_interval: float = 2.0):
        """Monitor logs in real-time"""
        if not RICH_AVAILABLE:
            print("Rich library required for monitoring. Install with: pip install rich")
            return
        
        log_files = self.get_log_files()
        if not log_files:
            self.console.print("[red]No Claude execution log files found![/red]")
            return
        
        # Track file positions for tailing
        file_positions = {file: 0 for file in log_files}
        
        with Live(console=self.console, refresh_per_second=1/refresh_interval) as live:
            while True:
                try:
                    # Create layout
                    layout = Layout()
                    layout.split_column(
                        Layout(name="status", size=10),
                        Layout(name="logs")
                    )
                    
                    # Get progress status
                    progress_data = self.get_progress_status()
                    status_table = self.create_status_table(progress_data)
                    layout["status"].update(Panel(status_table, title="📊 Execution Status"))
                    
                    # Read new log content
                    log_content = []
                    for log_file in log_files:
                        if log_file.exists():
                            try:
                                with open(log_file, 'r', encoding='utf-8') as f:
                                    f.seek(file_positions[log_file])
                                    new_lines = f.readlines()
                                    file_positions[log_file] = f.tell()
                                    
                                    if new_lines:
                                        log_content.append(f"\n📁 {log_file.name}:")
                                        for line in new_lines:
                                            log_content.append(self.colorize_line(line.rstrip()))
                            except Exception as e:
                                log_content.append(Text(f"Error reading {log_file}: {e}", style="red"))
                    
                    # Display logs
                    if log_content:
                        log_text = Text()
                        for item in log_content[-50:]:  # Show last 50 lines
                            if isinstance(item, str):
                                log_text.append(item + "\n", style="bold cyan")
                            else:
                                log_text.append_text(item)
                                log_text.append("\n")
                    else:
                        log_text = Text("Waiting for log output...", style="dim")
                    
                    layout["logs"].update(Panel(log_text, title="📋 Live Logs", border_style="blue"))
                    
                    live.update(layout)
                    
                    if not follow:
                        break
                    
                    time.sleep(refresh_interval)
                    
                except KeyboardInterrupt:
                    self.console.print("\n[yellow]Monitoring stopped by user[/yellow]")
                    break
                except Exception as e:
                    self.console.print(f"[red]Error during monitoring: {e}[/red]")
                    time.sleep(refresh_interval)
    
    def export_logs(self, output_file: str = None):
        """Export all logs to a formatted file"""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"claude_logs_export_{timestamp}.html"
        
        log_files = self.get_log_files()
        progress_data = self.get_progress_status()
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Claude Code Execution Logs - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</title>
    <style>
        body {{ font-family: 'Consolas', 'Monaco', monospace; background: #1e1e1e; color: #d4d4d4; margin: 20px; }}
        .header {{ background: #2d2d30; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
        .log-section {{ background: #252526; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #007acc; }}
        .success {{ color: #4ec9b0; font-weight: bold; }}
        .error {{ color: #f44747; font-weight: bold; }}
        .warning {{ color: #ffcc02; font-weight: bold; }}
        .info {{ color: #9cdcfe; }}
        .progress {{ color: #569cd6; font-weight: bold; }}
        .file-ops {{ color: #c586c0; }}
        .commands {{ color: #dcdcaa; font-weight: bold; }}
        .timestamp {{ color: #6a9955; font-size: 0.9em; }}
        pre {{ white-space: pre-wrap; word-wrap: break-word; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 Claude Code Execution Logs</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Base Path: {self.base_path}</p>
    </div>
"""
        
        # Add progress status
        if progress_data:
            html_content += "<div class='log-section'><h2>📊 Execution Status</h2><pre>"
            html_content += json.dumps(progress_data, indent=2)
            html_content += "</pre></div>"
        
        # Add log files
        for log_file in log_files:
            if log_file.exists():
                html_content += f"<div class='log-section'><h2>📁 {log_file.name}</h2><pre>"
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Apply basic HTML escaping and color coding
                        content = content.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                        
                        # Apply color coding
                        for category, patterns in self.patterns.items():
                            for pattern in patterns:
                                content = re.sub(
                                    f'({pattern})',
                                    f'<span class="{category}">\\1</span>',
                                    content,
                                    flags=re.IGNORECASE
                                )
                        
                        html_content += content
                except Exception as e:
                    html_content += f"Error reading file: {e}"
                html_content += "</pre></div>"
        
        html_content += "</body></html>"
        
        # Write to file
        output_path = Path(output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        if RICH_AVAILABLE:
            self.console.print(f"[green]✅ Logs exported to: {output_path.absolute()}[/green]")
        else:
            print(f"✅ Logs exported to: {output_path.absolute()}")

def main():
    parser = argparse.ArgumentParser(description="Monitor Claude Code execution logs")
    parser.add_argument("--path", "-p", help="Base path to monitor (default: current directory parent)")
    parser.add_argument("--export", "-e", help="Export logs to file instead of monitoring")
    parser.add_argument("--no-follow", action="store_true", help="Don't follow logs in real-time")
    parser.add_argument("--interval", "-i", type=float, default=2.0, help="Refresh interval in seconds")
    
    args = parser.parse_args()
    
    monitor = LogMonitor(args.path)
    
    if args.export:
        monitor.export_logs(args.export)
    else:
        monitor.monitor_logs(follow=not args.no_follow, refresh_interval=args.interval)

if __name__ == "__main__":
    main()
