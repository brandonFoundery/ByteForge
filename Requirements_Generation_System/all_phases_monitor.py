#!/usr/bin/env python3
"""
Complete Phase Monitor - Shows ALL phases (1, 2, 3) with real-time updates
"""

import json
import time
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout

class AllPhasesMonitor:
    def __init__(self):
        self.console = Console()
        self.base_path = Path.cwd().parent if Path.cwd().name == "Requirements_Generation_System" else Path.cwd()
        self.progress_tracker_path = self.find_progress_tracker()
        self.logs_path = self.base_path / "logs"
        
    def find_progress_tracker(self):
        """Find the progress tracker file"""
        possible_paths = [
            self.base_path / "generated_documents" / "design" / "claude_instructions" / "progress_tracker.json",
            Path("../generated_documents/design/claude_instructions/progress_tracker.json"),
            Path("generated_documents/design/claude_instructions/progress_tracker.json"),
            Path("../progress_tracker.json"),
            Path("progress_tracker.json")
        ]
        
        for path in possible_paths:
            if path.exists():
                return path
        
        return None
    
    def load_progress_data(self):
        """Load progress data from tracker"""
        if not self.progress_tracker_path or not self.progress_tracker_path.exists():
            return {}
        
        try:
            with open(self.progress_tracker_path, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    
    def format_duration(self, started_at, completed_at=None):
        """Format duration from timestamps"""
        if not started_at:
            return "N/A"
        
        if completed_at:
            duration_minutes = (completed_at - started_at) / 60
            return f"{duration_minutes:.1f}m"
        else:
            current_duration = (time.time() - started_at) / 60
            return f"{current_duration:.1f}m"
    
    def get_status_display(self, status):
        """Get status display with emoji and color"""
        if status == "completed":
            return "[green]✅ Complete[/green]"
        elif status == "in_progress":
            return "[blue]🔄 Running[/blue]"
        elif status == "failed":
            return "[red]❌ Failed[/red]"
        else:
            return "[dim]⏸️ Waiting[/dim]"
    
    def create_status_table(self):
        """Create the status table showing all phases"""
        table = Table(title="🤖 All Phases Status - Real-Time Monitor")
        table.add_column("Agent", style="cyan", no_wrap=True)
        table.add_column("Phase", style="magenta")
        table.add_column("Status", style="bold")
        table.add_column("Duration", style="yellow")
        table.add_column("Progress", style="green")
        
        progress_data = self.load_progress_data()
        
        # Define phase order and display names
        phases = [
            ("phase1_mvp_core_features", "Phase 1 - MVP Core"),
            ("phase2_advanced_features", "Phase 2 - Advanced Features"),
            ("phase3_production_ready", "Phase 3 - Production Ready")
        ]
        
        # Agent order for consistent display
        agent_order = ["backend", "frontend", "security", "infrastructure", "integration"]
        
        for phase_key, phase_display in phases:
            if phase_key not in progress_data:
                continue
                
            phase_data = progress_data[phase_key]
            if not isinstance(phase_data, dict):
                continue
                
            agents = phase_data.get("agents", {})
            if not agents:
                continue
            
            # Sort agents by the standard order
            sorted_agents = []
            for base_agent in agent_order:
                for agent_id in agents.keys():
                    if base_agent in agent_id.lower():
                        sorted_agents.append(agent_id)
                        break
            
            # Add any remaining agents
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
                
                # Format duration
                duration = self.format_duration(started_at, completed_at)
                
                # Status display
                status_display = self.get_status_display(status)
                
                # Progress calculation
                if status == "completed":
                    progress = "100%"
                elif status == "in_progress" and started_at:
                    estimated = agent_data.get("estimated_duration_minutes", 60)
                    current_duration = (time.time() - started_at) / 60
                    progress_pct = min(100, (current_duration / estimated) * 100)
                    progress = f"{progress_pct:.0f}%"
                else:
                    progress = "0%"
                
                # Clean agent name
                agent_display = agent_id.replace("-", " ").title()
                
                table.add_row(
                    agent_display,
                    phase_display,
                    status_display,
                    duration,
                    progress
                )
        
        return table
    
    def get_summary_stats(self):
        """Get summary statistics"""
        progress_data = self.load_progress_data()
        
        total_agents = 0
        completed_agents = 0
        running_agents = 0
        
        phases = ["phase1_mvp_core_features", "phase2_advanced_features", "phase3_production_ready"]
        
        for phase_key in phases:
            if phase_key not in progress_data:
                continue
                
            phase_data = progress_data[phase_key]
            if not isinstance(phase_data, dict):
                continue
                
            agents = phase_data.get("agents", {})
            for agent_data in agents.values():
                if isinstance(agent_data, dict):
                    total_agents += 1
                    status = agent_data.get("status", "unknown")
                    if status == "completed":
                        completed_agents += 1
                    elif status == "in_progress":
                        running_agents += 1
        
        return {
            "total": total_agents,
            "completed": completed_agents,
            "running": running_agents,
            "waiting": total_agents - completed_agents - running_agents
        }
    
    def create_display(self):
        """Create the complete display"""
        table = self.create_status_table()
        stats = self.get_summary_stats()
        
        # Create summary panel
        summary_text = f"""
📊 **Project Progress Summary**
• Total Agents: {stats['total']}
• ✅ Completed: {stats['completed']}
• 🔄 Running: {stats['running']}
• ⏸️ Waiting: {stats['waiting']}
• 📈 Overall: {(stats['completed'] / stats['total'] * 100):.1f}% Complete

🕒 Last Updated: {datetime.now().strftime('%H:%M:%S')}
        """
        
        summary_panel = Panel(summary_text, title="📈 Summary", border_style="green")
        
        # Create layout
        layout = Layout()
        layout.split_column(
            Layout(table, name="table", size=20),
            Layout(summary_panel, name="summary", size=8)
        )
        
        return layout
    
    def run(self):
        """Run the monitor"""
        self.console.print("🚀 Starting All Phases Monitor...")
        self.console.print(f"📁 Progress Tracker: {self.progress_tracker_path}")
        self.console.print("Press Ctrl+C to stop\n")

        try:
            # Use simple clear and redraw approach
            while True:
                # Clear screen
                self.console.clear()

                # Print header
                self.console.print("🚀 All Phases Monitor - Real-Time Status")
                self.console.print(f"📁 Progress Tracker: {self.progress_tracker_path}")
                self.console.print(f"🕒 Last Updated: {datetime.now().strftime('%H:%M:%S')}")
                self.console.print("Press Ctrl+C to stop\n")

                # Print the display
                self.console.print(self.create_display())

                time.sleep(2)
        except KeyboardInterrupt:
            self.console.print("\n👋 Monitor stopped")

if __name__ == "__main__":
    monitor = AllPhasesMonitor()
    monitor.run()
