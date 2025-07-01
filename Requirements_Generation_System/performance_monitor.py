#!/usr/bin/env python3
"""
Performance Monitor for Claude Code Execution

This module provides real-time monitoring, performance analytics, and
comprehensive reporting for Claude Code execution sessions.
"""

import json
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import threading

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn, SpinnerColumn, TimeElapsedColumn
from rich.live import Live
from rich.layout import Layout

console = Console()


@dataclass
class PerformanceMetrics:
    """Performance metrics for a single execution"""
    agent_id: str
    phase_id: str
    start_time: float
    end_time: Optional[float] = None
    estimated_duration: int = 30  # minutes
    actual_duration: Optional[float] = None  # minutes
    success: bool = False
    error_count: int = 0
    retry_count: int = 0
    cpu_usage: Optional[float] = None
    memory_usage: Optional[float] = None
    
    @property
    def is_completed(self) -> bool:
        return self.end_time is not None
    
    @property
    def duration_minutes(self) -> float:
        if self.end_time:
            return (self.end_time - self.start_time) / 60
        return (time.time() - self.start_time) / 60
    
    @property
    def efficiency_ratio(self) -> float:
        """Ratio of estimated to actual duration"""
        if self.actual_duration and self.actual_duration > 0:
            return self.estimated_duration / self.actual_duration
        return 1.0


@dataclass
class SessionMetrics:
    """Overall session performance metrics"""
    session_id: str
    start_time: float
    total_agents: int
    completed_agents: int = 0
    failed_agents: int = 0
    total_estimated_time: int = 0  # minutes
    total_actual_time: float = 0  # minutes
    overall_efficiency: float = 0.0
    critical_path_time: float = 0.0
    parallel_efficiency: float = 0.0


class PerformanceMonitor:
    """Real-time performance monitoring and analytics"""
    
    def __init__(self, base_path: Path, session_id: Optional[str] = None):
        self.base_path = base_path
        self.session_id = session_id or f"session_{int(time.time())}"
        self.logs_path = base_path / "logs"
        self.metrics_path = self.logs_path / "performance_metrics"
        
        # Ensure directories exist
        self.metrics_path.mkdir(parents=True, exist_ok=True)
        
        # Performance data
        self.agent_metrics: Dict[str, PerformanceMetrics] = {}
        self.session_metrics: Optional[SessionMetrics] = None
        self.monitoring_thread: Optional[threading.Thread] = None
        self.is_monitoring = False
        
        # Real-time display
        self.live_display: Optional[Live] = None
        
        console.print(f"[green]📊 Performance Monitor initialized - Session: {self.session_id}[/green]")
    
    def start_session(self, total_agents: int, total_estimated_time: int):
        """Start a new monitoring session"""
        self.session_metrics = SessionMetrics(
            session_id=self.session_id,
            start_time=time.time(),
            total_agents=total_agents,
            total_estimated_time=total_estimated_time
        )
        
        console.print(f"[cyan]🚀 Performance monitoring started for {total_agents} agents[/cyan]")
        self._save_session_metrics()
    
    def start_agent_monitoring(self, agent_id: str, phase_id: str, estimated_duration: int = 30):
        """Start monitoring a specific agent"""
        task_id = f"{agent_id}-{phase_id}"
        
        self.agent_metrics[task_id] = PerformanceMetrics(
            agent_id=agent_id,
            phase_id=phase_id,
            start_time=time.time(),
            estimated_duration=estimated_duration
        )
        
        console.print(f"[blue]📈 Started monitoring: {task_id} (est. {estimated_duration}m)[/blue]")
        self._save_agent_metrics(task_id)
    
    def complete_agent_monitoring(self, agent_id: str, phase_id: str, success: bool = True, error_count: int = 0):
        """Complete monitoring for a specific agent"""
        task_id = f"{agent_id}-{phase_id}"
        
        if task_id in self.agent_metrics:
            metrics = self.agent_metrics[task_id]
            metrics.end_time = time.time()
            metrics.actual_duration = metrics.duration_minutes
            metrics.success = success
            metrics.error_count = error_count
            
            if self.session_metrics:
                if success:
                    self.session_metrics.completed_agents += 1
                else:
                    self.session_metrics.failed_agents += 1
                
                self.session_metrics.total_actual_time += metrics.actual_duration
                self._update_session_efficiency()
            
            status = "SUCCESS" if success else "FAILED"
            console.print(f"[green]✅ {status}: {task_id} completed in {metrics.actual_duration:.1f}m[/green]")
            
            self._save_agent_metrics(task_id)
            self._save_session_metrics()
    
    def start_real_time_monitoring(self):
        """Start real-time monitoring display"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        console.print("[cyan]📱 Real-time monitoring started[/cyan]")
    
    def stop_real_time_monitoring(self):
        """Stop real-time monitoring"""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=2)
        
        if self.live_display:
            self.live_display.stop()
        
        console.print("[yellow]📱 Real-time monitoring stopped[/yellow]")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=5)
        )
        
        layout["main"].split_row(
            Layout(name="agents", ratio=2),
            Layout(name="metrics", ratio=1)
        )
        
        with Live(layout, refresh_per_second=2, screen=True) as live:
            self.live_display = live
            while self.is_monitoring:
                try:
                    layout["header"].update(self._create_header_panel())
                    layout["agents"].update(self._create_agents_table())
                    layout["metrics"].update(self._create_metrics_panel())
                    layout["footer"].update(self._create_footer_panel())
                    time.sleep(0.5)
                except Exception as e:
                    console.print(f"[red]Monitoring error: {e}[/red]")
                    break
    
    def _create_header_panel(self) -> Panel:
        """Create header panel with session info"""
        if not self.session_metrics:
            return Panel("No active session", title="Performance Monitor")
        
        session_duration = (time.time() - self.session_metrics.start_time) / 60
        completion_rate = (self.session_metrics.completed_agents / self.session_metrics.total_agents * 100) if self.session_metrics.total_agents > 0 else 0
        
        header_text = f"""
Session: {self.session_id} | Duration: {session_duration:.1f}m | Completion: {completion_rate:.1f}%
Agents: {self.session_metrics.completed_agents}/{self.session_metrics.total_agents} | Efficiency: {self.session_metrics.overall_efficiency:.1f}%
        """.strip()
        
        return Panel(header_text, title="📊 Claude Code Performance Monitor", style="bold blue")
    
    def _create_agents_table(self) -> Table:
        """Create agents performance table"""
        table = Table(title="Agent Performance")
        table.add_column("Agent", style="cyan")
        table.add_column("Phase", style="magenta")
        table.add_column("Status", style="green")
        table.add_column("Duration", justify="right")
        table.add_column("Estimated", justify="right")
        table.add_column("Efficiency", justify="right")
        table.add_column("Errors", justify="right")
        
        for task_id, metrics in self.agent_metrics.items():
            status = "✅ DONE" if metrics.is_completed else "🔄 RUNNING"
            if metrics.is_completed and not metrics.success:
                status = "❌ FAILED"
            
            duration = f"{metrics.duration_minutes:.1f}m"
            estimated = f"{metrics.estimated_duration}m"
            efficiency = f"{metrics.efficiency_ratio:.1f}x"
            errors = str(metrics.error_count)
            
            table.add_row(
                metrics.agent_id,
                metrics.phase_id,
                status,
                duration,
                estimated,
                efficiency,
                errors
            )
        
        return table
    
    def _create_metrics_panel(self) -> Panel:
        """Create metrics summary panel"""
        if not self.session_metrics:
            return Panel("No metrics available", title="Metrics")
        
        # Calculate performance metrics
        total_efficiency = self.session_metrics.overall_efficiency
        time_saved = self.session_metrics.total_estimated_time - self.session_metrics.total_actual_time
        
        # Get current running agents
        running_agents = sum(1 for m in self.agent_metrics.values() if not m.is_completed)
        
        metrics_text = f"""
Total Efficiency: {total_efficiency:.1f}%
Time Saved: {time_saved:.1f}m
Running Agents: {running_agents}
Failed Agents: {self.session_metrics.failed_agents}

Estimated Total: {self.session_metrics.total_estimated_time}m
Actual Total: {self.session_metrics.total_actual_time:.1f}m
        """.strip()
        
        return Panel(metrics_text, title="📈 Performance Metrics", style="green")
    
    def _create_footer_panel(self) -> Panel:
        """Create footer with recent activity"""
        recent_completions = []
        
        # Get last 3 completed agents
        completed_agents = [m for m in self.agent_metrics.values() if m.is_completed]
        completed_agents.sort(key=lambda x: x.end_time or 0, reverse=True)
        
        for metrics in completed_agents[:3]:
            status = "✅" if metrics.success else "❌"
            recent_completions.append(f"{status} {metrics.agent_id}-{metrics.phase_id} ({metrics.actual_duration:.1f}m)")
        
        footer_text = "Recent: " + " | ".join(recent_completions) if recent_completions else "Waiting for completions..."
        return Panel(footer_text, title="Recent Activity", style="dim")
    
    def _update_session_efficiency(self):
        """Update overall session efficiency metrics"""
        if not self.session_metrics:
            return
        
        total_estimated = sum(m.estimated_duration for m in self.agent_metrics.values())
        total_actual = sum(m.actual_duration or 0 for m in self.agent_metrics.values() if m.actual_duration)
        
        if total_actual > 0:
            self.session_metrics.overall_efficiency = (total_estimated / total_actual) * 100
        
        self.session_metrics.total_actual_time = total_actual
    
    def generate_performance_report(self) -> Dict:
        """Generate comprehensive performance report"""
        report = {
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "session_metrics": asdict(self.session_metrics) if self.session_metrics else None,
            "agent_metrics": {k: asdict(v) for k, v in self.agent_metrics.items()},
            "summary": self._generate_summary_stats(),
            "recommendations": self._generate_recommendations()
        }
        
        # Save report to file
        report_file = self.metrics_path / f"performance_report_{self.session_id}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        console.print(f"[green]📊 Performance report saved: {report_file}[/green]")
        return report
    
    def _generate_summary_stats(self) -> Dict:
        """Generate summary statistics"""
        if not self.agent_metrics:
            return {}
        
        completed_metrics = [m for m in self.agent_metrics.values() if m.is_completed]
        
        if not completed_metrics:
            return {"message": "No completed agents yet"}
        
        durations = [m.actual_duration for m in completed_metrics if m.actual_duration]
        efficiencies = [m.efficiency_ratio for m in completed_metrics]
        
        return {
            "total_agents": len(self.agent_metrics),
            "completed_agents": len(completed_metrics),
            "success_rate": sum(1 for m in completed_metrics if m.success) / len(completed_metrics) * 100,
            "average_duration": sum(durations) / len(durations) if durations else 0,
            "average_efficiency": sum(efficiencies) / len(efficiencies) if efficiencies else 0,
            "fastest_agent": min(durations) if durations else 0,
            "slowest_agent": max(durations) if durations else 0,
            "total_errors": sum(m.error_count for m in completed_metrics)
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate performance improvement recommendations"""
        recommendations = []
        
        if not self.agent_metrics:
            return recommendations
        
        completed_metrics = [m for m in self.agent_metrics.values() if m.is_completed]
        
        if not completed_metrics:
            return recommendations
        
        # Analyze efficiency
        avg_efficiency = sum(m.efficiency_ratio for m in completed_metrics) / len(completed_metrics)
        if avg_efficiency < 0.8:
            recommendations.append("Consider increasing time estimates - agents are taking longer than expected")
        elif avg_efficiency > 1.5:
            recommendations.append("Consider reducing time estimates - agents are completing faster than expected")
        
        # Analyze error rates
        error_rate = sum(m.error_count for m in completed_metrics) / len(completed_metrics)
        if error_rate > 2:
            recommendations.append("High error rate detected - review instruction quality and dependency management")
        
        # Analyze failure rate
        failure_rate = sum(1 for m in completed_metrics if not m.success) / len(completed_metrics)
        if failure_rate > 0.2:
            recommendations.append("High failure rate - consider improving error handling and retry logic")
        
        return recommendations
    
    def _save_agent_metrics(self, task_id: str):
        """Save agent metrics to file"""
        if task_id in self.agent_metrics:
            metrics_file = self.metrics_path / f"agent_{task_id}_{self.session_id}.json"
            with open(metrics_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.agent_metrics[task_id]), f, indent=2)
    
    def _save_session_metrics(self):
        """Save session metrics to file"""
        if self.session_metrics:
            session_file = self.metrics_path / f"session_{self.session_id}.json"
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.session_metrics), f, indent=2)


def main():
    """Test the performance monitor"""
    import asyncio
    
    async def test_monitoring():
        base_path = Path("project")
        monitor = PerformanceMonitor(base_path)
        
        # Start session
        monitor.start_session(total_agents=3, total_estimated_time=90)
        
        # Start real-time monitoring
        monitor.start_real_time_monitoring()
        
        # Simulate agent execution
        agents = ["backend", "frontend", "security"]
        for i, agent in enumerate(agents):
            monitor.start_agent_monitoring(agent, "phase1", 30)
            await asyncio.sleep(2)  # Simulate work
            monitor.complete_agent_monitoring(agent, "phase1", success=True)
        
        # Generate report
        await asyncio.sleep(2)
        report = monitor.generate_performance_report()
        
        # Stop monitoring
        monitor.stop_real_time_monitoring()
        
        console.print("\n[bold green]Performance monitoring test completed![/bold green]")
    
    asyncio.run(test_monitoring())


if __name__ == "__main__":
    main()