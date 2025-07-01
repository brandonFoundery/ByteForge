#!/usr/bin/env python3
"""
Execution Optimizer for Claude Code

This module optimizes the execution strategy for Claude Code agents,
providing intelligent scheduling, parallel execution, and dependency resolution.
"""

import asyncio
import time
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple
from pathlib import Path
import yaml

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

console = Console()


@dataclass
class AgentTask:
    """Represents a single agent execution task"""
    agent_id: str
    phase_id: str
    name: str
    priority: int = 1
    estimated_duration: int = 30  # minutes
    dependencies: List[str] = field(default_factory=list)
    status: str = "not_started"  # not_started, ready, in_progress, completed, failed
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    retry_count: int = 0
    
    @property
    def task_id(self) -> str:
        """Unique task identifier"""
        return f"{self.agent_id}-{self.phase_id}"
    
    @property
    def actual_duration(self) -> Optional[float]:
        """Actual execution duration in minutes"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time) / 60
        return None


@dataclass
class ExecutionPlan:
    """Optimized execution plan with parallel execution opportunities"""
    phases: List[str]
    tasks: Dict[str, AgentTask]
    execution_order: List[List[str]]  # List of parallel execution batches
    total_estimated_time: int  # minutes
    critical_path: List[str]


class ExecutionOptimizer:
    """Optimizes Claude Code execution strategy"""
    
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.config = self._load_config()
        self.tasks: Dict[str, AgentTask] = {}
        
    def _load_config(self) -> Dict:
        """Load configuration from config.yaml"""
        config_path = self.base_path / "Requirements_Generation_System" / "config.yaml"
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return {}
    
    def create_execution_plan(self) -> ExecutionPlan:
        """Create optimized execution plan"""
        console.print("[cyan]🚀 Creating optimized execution plan...[/cyan]")
        
        # Load tasks from configuration
        self._load_tasks_from_config()
        
        # Build dependency graph
        dependency_graph = self._build_dependency_graph()
        
        # Find critical path
        critical_path = self._find_critical_path(dependency_graph)
        
        # Create execution batches for parallel execution
        execution_order = self._create_execution_batches(dependency_graph)
        
        # Calculate total estimated time
        total_time = self._calculate_total_time(execution_order)
        
        plan = ExecutionPlan(
            phases=list(self._get_phases()),
            tasks=self.tasks,
            execution_order=execution_order,
            total_estimated_time=total_time,
            critical_path=critical_path
        )
        
        self._display_execution_plan(plan)
        return plan
    
    def _load_tasks_from_config(self):
        """Load tasks from configuration"""
        claude_config = self.config.get('claude_code_execution', {})
        agents_config = claude_config.get('agents', {})
        phases_config = claude_config.get('phases', {})
        
        for phase_id, phase_info in phases_config.items():
            for agent_id, agent_info in agents_config.items():
                # Get dependencies for this agent/phase combination
                dependencies = phase_info.get('dependencies', {}).get(agent_id, [])
                
                task = AgentTask(
                    agent_id=agent_id,
                    phase_id=phase_id,
                    name=f"{agent_info.get('name', agent_id)} - {phase_info.get('name', phase_id)}",
                    priority=agent_info.get('priority', 1),
                    estimated_duration=agent_info.get('estimated_duration', 30),
                    dependencies=dependencies
                )
                
                self.tasks[task.task_id] = task
    
    def _get_phases(self) -> List[str]:
        """Get ordered list of phases"""
        phases_config = self.config.get('claude_code_execution', {}).get('phases', {})
        return sorted(phases_config.keys(), key=lambda x: phases_config[x].get('priority', 1))
    
    def _build_dependency_graph(self) -> Dict[str, Set[str]]:
        """Build dependency graph for tasks"""
        graph = {}
        
        for task_id, task in self.tasks.items():
            graph[task_id] = set(task.dependencies)
        
        return graph
    
    def _find_critical_path(self, dependency_graph: Dict[str, Set[str]]) -> List[str]:
        """Find the critical path through the execution graph"""
        # Use topological sort with longest path calculation
        in_degree = {task_id: len(deps) for task_id, deps in dependency_graph.items()}
        distances = {task_id: 0 for task_id in self.tasks}
        queue = [task_id for task_id, degree in in_degree.items() if degree == 0]
        
        while queue:
            current = queue.pop(0)
            current_distance = distances[current] + self.tasks[current].estimated_duration
            
            # Find all tasks that depend on current task
            for task_id, deps in dependency_graph.items():
                if current in deps:
                    distances[task_id] = max(distances[task_id], current_distance)
                    in_degree[task_id] -= 1
                    if in_degree[task_id] == 0:
                        queue.append(task_id)
        
        # Find the task with maximum distance (end of critical path)
        end_task = max(distances.items(), key=lambda x: x[1])[0]
        
        # Reconstruct critical path
        critical_path = []
        current = end_task
        
        while current:
            critical_path.append(current)
            # Find the predecessor with maximum distance
            max_distance = -1
            next_task = None
            
            for dep in dependency_graph.get(current, []):
                if distances[dep] > max_distance:
                    max_distance = distances[dep]
                    next_task = dep
            
            current = next_task
        
        critical_path.reverse()
        return critical_path
    
    def _create_execution_batches(self, dependency_graph: Dict[str, Set[str]]) -> List[List[str]]:
        """Create batches of tasks that can execute in parallel"""
        completed = set()
        execution_order = []
        
        while len(completed) < len(self.tasks):
            # Find all tasks ready to execute
            ready_tasks = []
            
            for task_id, deps in dependency_graph.items():
                if task_id not in completed and deps.issubset(completed):
                    ready_tasks.append(task_id)
            
            if not ready_tasks:
                console.print("[red]❌ Circular dependency detected![/red]")
                break
            
            # Sort by priority and estimated duration
            ready_tasks.sort(key=lambda x: (self.tasks[x].priority, -self.tasks[x].estimated_duration))
            
            execution_order.append(ready_tasks)
            completed.update(ready_tasks)
        
        return execution_order
    
    def _calculate_total_time(self, execution_order: List[List[str]]) -> int:
        """Calculate total estimated execution time"""
        total_time = 0
        
        for batch in execution_order:
            # For parallel execution, take the maximum duration in the batch
            batch_time = max(self.tasks[task_id].estimated_duration for task_id in batch)
            total_time += batch_time
        
        return total_time
    
    def _display_execution_plan(self, plan: ExecutionPlan):
        """Display the execution plan"""
        console.print("\n[bold blue]📋 Optimized Execution Plan[/bold blue]")
        console.print(f"[green]Total Estimated Time: {plan.total_estimated_time} minutes[/green]")
        console.print(f"[green]Number of Parallel Batches: {len(plan.execution_order)}[/green]")
        
        console.print("\n[bold]Critical Path:[/bold]")
        critical_time = sum(self.tasks[task_id].estimated_duration for task_id in plan.critical_path)
        console.print(f"[yellow]Time: {critical_time} minutes[/yellow]")
        for task_id in plan.critical_path:
            task = self.tasks[task_id]
            console.print(f"  • {task.name} ({task.estimated_duration}m)")
        
        console.print("\n[bold]Execution Batches:[/bold]")
        for i, batch in enumerate(plan.execution_order, 1):
            batch_time = max(self.tasks[task_id].estimated_duration for task_id in batch)
            console.print(f"\n[cyan]Batch {i} (Parallel - {batch_time}m):[/cyan]")
            for task_id in batch:
                task = self.tasks[task_id]
                deps_str = ", ".join(task.dependencies) if task.dependencies else "None"
                console.print(f"  • {task.name} ({task.estimated_duration}m) - Deps: {deps_str}")
    
    def get_ready_tasks(self, completed_tasks: Set[str]) -> List[str]:
        """Get list of tasks ready for execution"""
        ready_tasks = []
        
        for task_id, task in self.tasks.items():
            if (task.status == "not_started" and 
                set(task.dependencies).issubset(completed_tasks)):
                ready_tasks.append(task_id)
        
        # Sort by priority
        ready_tasks.sort(key=lambda x: self.tasks[x].priority)
        return ready_tasks
    
    def update_task_status(self, task_id: str, status: str, start_time: Optional[float] = None, end_time: Optional[float] = None):
        """Update task status and timing"""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            task.status = status
            
            if start_time:
                task.start_time = start_time
            if end_time:
                task.end_time = end_time
    
    def get_execution_metrics(self) -> Dict[str, any]:
        """Get execution metrics and statistics"""
        completed_tasks = [task for task in self.tasks.values() if task.status == "completed"]
        failed_tasks = [task for task in self.tasks.values() if task.status == "failed"]
        in_progress_tasks = [task for task in self.tasks.values() if task.status == "in_progress"]
        
        total_estimated = sum(task.estimated_duration for task in self.tasks.values())
        total_actual = sum(task.actual_duration or 0 for task in completed_tasks)
        
        metrics = {
            "total_tasks": len(self.tasks),
            "completed": len(completed_tasks),
            "failed": len(failed_tasks),
            "in_progress": len(in_progress_tasks),
            "not_started": len(self.tasks) - len(completed_tasks) - len(failed_tasks) - len(in_progress_tasks),
            "total_estimated_time": total_estimated,
            "total_actual_time": total_actual,
            "efficiency": (total_estimated / total_actual * 100) if total_actual > 0 else 0,
            "completion_percentage": (len(completed_tasks) / len(self.tasks) * 100) if self.tasks else 0
        }
        
        return metrics


def main():
    """Test the execution optimizer"""
    base_path = Path("project")
    optimizer = ExecutionOptimizer(base_path)
    
    # Create execution plan
    plan = optimizer.create_execution_plan()
    
    # Display metrics
    metrics = optimizer.get_execution_metrics()
    console.print("\n[bold]Execution Metrics:[/bold]")
    for key, value in metrics.items():
        console.print(f"  {key}: {value}")


if __name__ == "__main__":
    main()