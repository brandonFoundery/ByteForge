#!/usr/bin/env python3
"""
Real-time monitoring system for Claude Code execution
Provides both web dashboard and terminal monitoring
"""
import asyncio
import json
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskID
from rich.table import Table
from rich.text import Text

console = Console()

class AgentMonitor:
    """Real-time monitoring for Claude Code agents"""
    
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.logs_path = base_path / "logs"
        self.progress_path = base_path / "project" / "design" / "claude_instructions" / "progress_tracker.json"
        self.agents_status = {}
        self.log_files = {}
        self.websocket_connections = []
        self.running = False
        
        # Ensure logs directory exists
        self.logs_path.mkdir(parents=True, exist_ok=True)
        
    def start_monitoring(self):
        """Start monitoring agents"""
        self.running = True
        
        # Start background monitoring thread
        monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        monitor_thread.start()
        
        console.print("[green]🔍 Real-time monitoring started[/green]")
        
    def stop_monitoring(self):
        """Stop monitoring"""
        self.running = False
        console.print("[yellow]⏹️ Monitoring stopped[/yellow]")
        
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                # Check progress tracker
                if self.progress_path.exists():
                    with open(self.progress_path, 'r', encoding='utf-8') as f:
                        progress_data = json.load(f)
                        self._update_agent_status(progress_data)
                
                # Check log files
                self._check_log_files()
                
                # Send updates to websockets
                self._broadcast_updates()
                
            except Exception as e:
                console.print(f"[red]Monitor error: {e}[/red]")
            
            time.sleep(1)  # Update every second
            
    def _update_agent_status(self, progress_data: Dict):
        """Update agent status from progress tracker"""
        for phase_name, phase_data in progress_data.items():
            if phase_name == "execution_metadata":
                continue
                
            if "agents" in phase_data:
                for agent_key, agent_info in phase_data["agents"].items():
                    status = agent_info.get("status", "unknown")
                    
                    if agent_key not in self.agents_status:
                        self.agents_status[agent_key] = {
                            "status": status,
                            "last_update": time.time(),
                            "started_at": agent_info.get("started_at"),
                            "completed_at": agent_info.get("completed_at"),
                            "error_log": agent_info.get("error_log"),
                            "log_content": ""
                        }
                    else:
                        # Update existing agent
                        old_status = self.agents_status[agent_key]["status"]
                        if old_status != status:
                            self.agents_status[agent_key]["status"] = status
                            self.agents_status[agent_key]["last_update"] = time.time()
                            console.print(f"[cyan]📱 Agent {agent_key} status changed: {old_status} → {status}[/cyan]")
                        
                        self.agents_status[agent_key].update({
                            "started_at": agent_info.get("started_at"),
                            "completed_at": agent_info.get("completed_at"),
                            "error_log": agent_info.get("error_log")
                        })
    
    def _check_log_files(self):
        """Check for new log content"""
        for agent_key in self.agents_status:
            # Find corresponding log file
            log_file = None
            for log_path in self.logs_path.glob(f"*{agent_key.replace('-', '_')}*.log"):
                log_file = log_path
                break
                
            if log_file and log_file.exists():
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if content != self.agents_status[agent_key]["log_content"]:
                            self.agents_status[agent_key]["log_content"] = content
                            self.agents_status[agent_key]["last_update"] = time.time()
                except Exception as e:
                    console.print(f"[red]Error reading log {log_file}: {e}[/red]")
    
    def _broadcast_updates(self):
        """Send updates to all websocket connections"""
        if self.websocket_connections:
            update_data = {
                "timestamp": datetime.now().isoformat(),
                "agents": self.agents_status
            }
            
            # Send to all connected websockets
            disconnected = []
            for ws in self.websocket_connections:
                try:
                    asyncio.create_task(ws.send_json(update_data))
                except:
                    disconnected.append(ws)
            
            # Remove disconnected websockets
            for ws in disconnected:
                self.websocket_connections.remove(ws)
    
    def add_websocket(self, websocket: WebSocket):
        """Add a websocket connection"""
        self.websocket_connections.append(websocket)
        
    def remove_websocket(self, websocket: WebSocket):
        """Remove a websocket connection"""
        if websocket in self.websocket_connections:
            self.websocket_connections.remove(websocket)
    
    def get_status_summary(self) -> Dict:
        """Get current status summary"""
        summary = {
            "total_agents": len(self.agents_status),
            "running": len([a for a in self.agents_status.values() if a["status"] == "in_progress"]),
            "completed": len([a for a in self.agents_status.values() if a["status"] == "completed"]),
            "failed": len([a for a in self.agents_status.values() if a["status"] == "failed"]),
            "pending": len([a for a in self.agents_status.values() if a["status"] in ["pending", "not_started"]])
        }
        return summary

# Global monitor instance
monitor = None

def create_web_app():
    """Create FastAPI web application"""
    app = FastAPI(title="Claude Code Agent Monitor")
    
    @app.get("/", response_class=HTMLResponse)
    async def dashboard():
        """Main dashboard"""
        html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Claude Code Agent Monitor</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #1a1a1a; color: #fff; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px; margin-bottom: 20px; }
        .header h1 { margin: 0; color: white; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px; }
        .stat-card { background: #2d2d2d; padding: 15px; border-radius: 8px; text-align: center; }
        .stat-number { font-size: 2em; font-weight: bold; margin-bottom: 5px; }
        .stat-label { color: #aaa; }
        .running { color: #4CAF50; }
        .completed { color: #2196F3; }
        .failed { color: #f44336; }
        .pending { color: #ff9800; }
        .agents-grid { display: grid; gap: 15px; }
        .agent-card { background: #2d2d2d; border-radius: 8px; padding: 15px; }
        .agent-header { display: flex; justify-content: between; align-items: center; margin-bottom: 10px; }
        .agent-name { font-weight: bold; }
        .agent-status { padding: 4px 8px; border-radius: 4px; font-size: 0.8em; }
        .status-running { background: #4CAF50; }
        .status-completed { background: #2196F3; }
        .status-failed { background: #f44336; }
        .status-pending { background: #ff9800; }
        .log-content { background: #1a1a1a; padding: 10px; border-radius: 4px; font-family: monospace; font-size: 0.8em; max-height: 200px; overflow-y: auto; margin-top: 10px; }
        .timestamp { color: #aaa; font-size: 0.8em; }
        .auto-refresh { margin-bottom: 20px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 Claude Code Agent Monitor</h1>
        <p>Real-time monitoring of AI agent execution</p>
    </div>
    
    <div class="auto-refresh">
        <label>
            <input type="checkbox" id="autoRefresh" checked> Auto-refresh every 2 seconds
        </label>
        <button onclick="location.reload()">🔄 Refresh Now</button>
    </div>
    
    <div class="stats" id="stats">
        <!-- Stats will be populated by JavaScript -->
    </div>
    
    <div class="agents-grid" id="agents">
        <!-- Agents will be populated by JavaScript -->
    </div>
    
    <script>
        const ws = new WebSocket(`ws://${window.location.host}/ws`);
        
        ws.onmessage = function(event) {
            const data = JSON.parse(event.data);
            updateDashboard(data);
        };
        
        ws.onopen = function() {
            console.log('WebSocket connected');
        };
        
        ws.onclose = function() {
            console.log('WebSocket disconnected');
            setTimeout(() => location.reload(), 3000);
        };
        
        function updateDashboard(data) {
            updateStats(data.agents);
            updateAgents(data.agents);
            document.getElementById('lastUpdate').textContent = new Date(data.timestamp).toLocaleTimeString();
        }
        
        function updateStats(agents) {
            const stats = {
                total: Object.keys(agents).length,
                running: Object.values(agents).filter(a => a.status === 'in_progress').length,
                completed: Object.values(agents).filter(a => a.status === 'completed').length,
                failed: Object.values(agents).filter(a => a.status === 'failed').length,
                pending: Object.values(agents).filter(a => ['pending', 'not_started'].includes(a.status)).length
            };
            
            document.getElementById('stats').innerHTML = `
                <div class="stat-card">
                    <div class="stat-number">${stats.total}</div>
                    <div class="stat-label">Total Agents</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number running">${stats.running}</div>
                    <div class="stat-label">Running</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number completed">${stats.completed}</div>
                    <div class="stat-label">Completed</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number failed">${stats.failed}</div>
                    <div class="stat-label">Failed</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number pending">${stats.pending}</div>
                    <div class="stat-label">Pending</div>
                </div>
            `;
        }
        
        function updateAgents(agents) {
            const agentsHtml = Object.entries(agents).map(([agentKey, agent]) => {
                const logContent = agent.log_content ? agent.log_content.slice(-1000) : 'No log data';
                const statusClass = `status-${agent.status.replace('_', '-')}`;
                
                return `
                    <div class="agent-card">
                        <div class="agent-header">
                            <div class="agent-name">${agentKey}</div>
                            <div class="agent-status ${statusClass}">${agent.status}</div>
                        </div>
                        <div class="timestamp">Last update: ${new Date(agent.last_update * 1000).toLocaleTimeString()}</div>
                        ${agent.error_log ? `<div style="color: #f44336; margin-top: 5px;">Error: ${agent.error_log}</div>` : ''}
                        <div class="log-content">${logContent}</div>
                    </div>
                `;
            }).join('');
            
            document.getElementById('agents').innerHTML = agentsHtml;
        }
        
        // Auto-refresh functionality
        setInterval(() => {
            if (document.getElementById('autoRefresh').checked && ws.readyState !== WebSocket.OPEN) {
                location.reload();
            }
        }, 2000);
    </script>
    
    <div style="margin-top: 20px; text-align: center; color: #aaa;">
        Last update: <span id="lastUpdate">-</span>
    </div>
</body>
</html>
        """
        return HTMLResponse(content=html_content)
    
    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        """WebSocket endpoint for real-time updates"""
        await websocket.accept()
        
        if monitor:
            monitor.add_websocket(websocket)
            
            try:
                while True:
                    # Keep connection alive
                    await asyncio.sleep(1)
            except WebSocketDisconnect:
                monitor.remove_websocket(websocket)
    
    @app.get("/api/status")
    async def get_status():
        """API endpoint for status"""
        if monitor:
            return {
                "status": "running",
                "summary": monitor.get_status_summary(),
                "agents": monitor.agents_status
            }
        return {"status": "not_running"}
    
    return app

def start_web_monitor(base_path: Path, port: int = 8001):
    """Start web monitoring dashboard"""
    global monitor
    
    if not monitor:
        monitor = AgentMonitor(base_path)
        monitor.start_monitoring()
    
    app = create_web_app()
    
    console.print(f"[green]🌐 Starting web monitor on http://localhost:{port}[/green]")
    console.print("[dim]Press Ctrl+C to stop[/dim]")
    
    # Run server
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="error")

def start_terminal_monitor(base_path: Path):
    """Start terminal-based monitoring"""
    global monitor
    
    if not monitor:
        monitor = AgentMonitor(base_path)
        monitor.start_monitoring()
    
    def create_layout():
        """Create Rich layout for terminal"""
        layout = Layout()
        
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main", ratio=1),
            Layout(name="footer", size=3)
        )
        
        layout["main"].split_row(
            Layout(name="agents", ratio=2),
            Layout(name="logs", ratio=3)
        )
        
        return layout
    
    def update_display():
        """Update the display with current data"""
        layout = create_layout()
        
        # Header
        layout["header"].update(Panel(
            "[bold blue]🤖 Claude Code Agent Monitor[/bold blue]\n"
            f"Monitoring: {monitor.logs_path}",
            style="cyan"
        ))
        
        # Agents table
        agents_table = Table(title="Agent Status")
        agents_table.add_column("Agent", style="cyan")
        agents_table.add_column("Status", style="magenta")
        agents_table.add_column("Last Update", style="green")
        
        for agent_key, agent_info in monitor.agents_status.items():
            status = agent_info["status"]
            last_update = datetime.fromtimestamp(agent_info["last_update"]).strftime("%H:%M:%S")
            
            # Color status
            if status == "in_progress":
                status_text = f"[yellow]{status}[/yellow]"
            elif status == "completed":
                status_text = f"[green]{status}[/green]"
            elif status == "failed":
                status_text = f"[red]{status}[/red]"
            else:
                status_text = f"[dim]{status}[/dim]"
            
            agents_table.add_row(agent_key, status_text, last_update)
        
        layout["agents"].update(Panel(agents_table, title="Agents"))
        
        # Logs
        logs_text = ""
        for agent_key, agent_info in monitor.agents_status.items():
            if agent_info["log_content"]:
                logs_text += f"[bold]{agent_key}:[/bold]\n"
                logs_text += agent_info["log_content"][-500:] + "\n\n"
        
        if not logs_text:
            logs_text = "[dim]No log data available[/dim]"
        
        layout["logs"].update(Panel(logs_text, title="Recent Logs", wrap=True))
        
        # Footer
        summary = monitor.get_status_summary()
        layout["footer"].update(Panel(
            f"Total: {summary['total']} | "
            f"[yellow]Running: {summary['running']}[/yellow] | "
            f"[green]Completed: {summary['completed']}[/green] | "
            f"[red]Failed: {summary['failed']}[/red] | "
            f"[dim]Pending: {summary['pending']}[/dim]",
            style="blue"
        ))
        
        return layout
    
    try:
        with Live(update_display(), refresh_per_second=2, screen=True) as live:
            while True:
                live.update(update_display())
                time.sleep(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Monitoring stopped.[/yellow]")
    finally:
        if monitor:
            monitor.stop_monitoring()

if __name__ == "__main__":
    import sys
    
    base_path = Path(__file__).parent
    
    if len(sys.argv) > 1 and sys.argv[1] == "web":
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 8001
        start_web_monitor(base_path, port)
    else:
        start_terminal_monitor(base_path)