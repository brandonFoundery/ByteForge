"""
Claude Code Executor for AI Agent Implementation (Updated)

This module executes Claude Code in WSL terminals to implement features based on
individual instruction files. It manages dependencies, progress tracking, and
parallel execution according to the execution plan.
"""

import asyncio
import json
import subprocess
import time
import yaml
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


class SecurityError(Exception):
    """Security validation error"""
    pass


try:
    from execution_optimizer import ExecutionOptimizer, ExecutionPlan
    from performance_monitor import PerformanceMonitor
    from security_manager import SecurityManager
except ImportError:
    ExecutionOptimizer = None
    ExecutionPlan = None
    PerformanceMonitor = None
    SecurityManager = None


@dataclass
class AgentResult:
    """Result of a single agent implementation"""
    agent_name: str
    success: bool
    branch_name: Optional[str] = None
    pr_url: Optional[str] = None
    execution_time: float = 0.0
    error_message: Optional[str] = None


@dataclass
class ExecutionResult:
    """Result of the entire execution process"""
    success: bool
    total_execution_time: float
    agent_results: List[AgentResult]
    errors: List[str]
    error_summary: Optional[str] = None


class ClaudeCodeExecutor:
    """Enhanced Claude Code executor using instruction files"""

    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.instructions_path = base_path / "generated_documents" / "design" / "claude_instructions"
        self.logs_path = base_path / "logs"

        # Ensure directories exist
        self.logs_path.mkdir(parents=True, exist_ok=True)

        # Load execution plan and progress tracker
        self.execution_plan = self._load_execution_plan()
        self.progress_tracker = self._load_progress_tracker()

        # Agent configurations
        self.agents = {
            "1": {"id": "backend", "name": "Backend Agent", "dir": "BackEnd"},
            "2": {"id": "frontend", "name": "Frontend Agent", "dir": "FrontEnd"},
            "3": {"id": "infrastructure", "name": "Infrastructure Agent", "dir": "Infrastructure"},
            "4": {"id": "security", "name": "Security Agent", "dir": "BackEnd"},
            "5": {"id": "integration", "name": "Integration Agent", "dir": "BackEnd"}
        }

        # Phase configurations
        self.phases = {
            "1": {"id": "phase1", "name": "MVP Core Features"},
            "2": {"id": "phase2", "name": "Advanced Features"},
            "3": {"id": "phase3", "name": "Production Ready"}
        }

        # Load configuration
        self.config = self._load_claude_config()
        
        # Initialize execution optimizer
        if ExecutionOptimizer:
            self.optimizer = ExecutionOptimizer(base_path)
            self.execution_plan = None
        else:
            self.optimizer = None
            self.execution_plan = None
        
        # Initialize performance monitor
        if PerformanceMonitor:
            self.performance_monitor = PerformanceMonitor(base_path)
        else:
            self.performance_monitor = None
        
        # Initialize security manager
        if SecurityManager:
            self.security_manager = SecurityManager(base_path)
        else:
            self.security_manager = None

    def _load_claude_config(self) -> Dict:
        """Load Claude Code configuration from config.yaml"""
        try:
            config_path = self.base_path / "Requirements_Generation_System" / "config.yaml"
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                return config.get('llm', {}).get('claude_code', {})
            else:
                console.print(f"[yellow]⚠️ Config file not found: {config_path}[/yellow]")
        except Exception as e:
            console.print(f"[red]❌ Error loading config: {e}[/red]")
        
        # Return default configuration
        return {
            'model': 'claude-sonnet-4-20250514',
            'temperature': 0.1,
            'timeout': 600,
            'max_retries': 3,
            'retry_delay': 10
        }

    def _load_execution_plan(self) -> Dict:
        """Load the execution plan"""
        plan_file = self.instructions_path / "execution_plan.md"
        if not plan_file.exists():
            console.print(f"[yellow]⚠️ Execution plan not found: {plan_file}[/yellow]")
            return {}
        return {"loaded": True}  # Would parse markdown if needed

    def _load_progress_tracker(self) -> Dict:
        """Load the progress tracker"""
        tracker_file = self.instructions_path / "progress_tracker.json"
        if not tracker_file.exists():
            console.print(f"[yellow]⚠️ Progress tracker not found: {tracker_file}[/yellow]")
            return {}

        with open(tracker_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save_progress_tracker(self):
        """Save the progress tracker"""
        tracker_file = self.instructions_path / "progress_tracker.json"
        with open(tracker_file, 'w', encoding='utf-8') as f:
            json.dump(self.progress_tracker, f, indent=2)

    def _update_agent_status(self, agent_id: str, phase_id: str, status: str, error_message: str = None):
        """Update agent status in progress tracker"""
        phase_key = f"{phase_id}_mvp_core_features" if phase_id == "phase1" else f"{phase_id}_advanced_features" if phase_id == "phase2" else f"{phase_id}_production_ready"
        agent_key = f"{agent_id}-{phase_id}"

        console.print(f"[dim]Updating status: {phase_key} -> {agent_key} -> {status}[/dim]")

        if phase_key in self.progress_tracker and agent_key in self.progress_tracker[phase_key]["agents"]:
            agent_data = self.progress_tracker[phase_key]["agents"][agent_key]
            agent_data["status"] = status

            if status == "in_progress":
                agent_data["started_at"] = time.time()
            elif status in ["completed", "failed"]:
                agent_data["completed_at"] = time.time()
                if agent_data["started_at"]:
                    agent_data["actual_duration_minutes"] = (agent_data["completed_at"] - agent_data["started_at"]) / 60

            if error_message:
                agent_data["error_log"] = error_message
                agent_data["retry_count"] = agent_data.get("retry_count", 0) + 1

            self._save_progress_tracker()
        else:
            console.print(f"[yellow]⚠️ Could not find {phase_key} -> {agent_key} in progress tracker[/yellow]")

    def _check_dependencies(self, agent_id: str, phase_id: str) -> bool:
        """Check if all dependencies for an agent are completed"""
        phase_key = f"{phase_id}_mvp_core_features" if phase_id == "phase1" else f"{phase_id}_advanced_features" if phase_id == "phase2" else f"{phase_id}_production_ready"
        agent_key = f"{agent_id}-{phase_id}"

        console.print(f"[dim]Checking dependencies for {agent_key} in {phase_key}[/dim]")

        if phase_key not in self.progress_tracker or agent_key not in self.progress_tracker[phase_key]["agents"]:
            console.print(f"[yellow]⚠️ Agent {agent_key} not found in {phase_key}[/yellow]")
            return False

        agent_data = self.progress_tracker[phase_key]["agents"][agent_key]
        dependencies = agent_data.get("dependencies", [])

        console.print(f"[dim]Dependencies for {agent_key}: {dependencies}[/dim]")

        # If no dependencies, agent can run
        if not dependencies:
            console.print(f"[green]✅ {agent_key} has no dependencies, can run[/green]")
            return True

        for dep in dependencies:
            # Convert simple dependency name to full agent-phase format
            if "-" not in dep:
                dep_full = f"{dep}-{phase_id}"
            else:
                dep_full = dep

            # Check if dependency is completed - search across all phases
            found = False
            for phase_name, phase_data in self.progress_tracker.items():
                if phase_name == "execution_metadata":
                    continue

                if "agents" in phase_data and dep_full in phase_data["agents"]:
                    dep_status = phase_data["agents"][dep_full]["status"]
                    if dep_status != "completed":
                        console.print(f"[yellow]⏳ {agent_id}-{phase_id} waiting for dependency: {dep_full} (status: {dep_status})[/yellow]")
                        return False
                    else:
                        console.print(f"[green]✅ Dependency {dep_full} is completed[/green]")
                    found = True
                    break

            if not found:
                console.print(f"[red]❌ Dependency {dep_full} not found in progress tracker[/red]")
                return False

        console.print(f"[green]✅ All dependencies satisfied for {agent_key}[/green]")
        return True

    def _get_available_agents(self, phase_id: str) -> List[str]:
        """Get list of agents that can be executed (dependencies satisfied)"""
        available = []
        phase_key = f"{phase_id}_mvp_core_features" if phase_id == "phase1" else f"{phase_id}_advanced_features" if phase_id == "phase2" else f"{phase_id}_production_ready"

        console.print(f"[cyan]🔍 Checking available agents for {phase_key}[/cyan]")

        for agent_id in ["backend", "frontend", "security", "infrastructure", "integration"]:
            agent_key = f"{agent_id}-{phase_id}"

            if phase_key in self.progress_tracker and agent_key in self.progress_tracker[phase_key]["agents"]:
                status = self.progress_tracker[phase_key]["agents"][agent_key]["status"]
                console.print(f"[dim]Agent {agent_key} status: {status}[/dim]")

                if status == "not_started" and self._check_dependencies(agent_id, phase_id):
                    available.append(agent_id)
                    console.print(f"[green]✅ {agent_id} is available[/green]")
            else:
                console.print(f"[yellow]⚠️ Agent {agent_key} not found in {phase_key}[/yellow]")

        console.print(f"[cyan]📋 Available agents: {available}[/cyan]")
        return available

    async def execute_implementation(self, agent_choice: str, phase_choice: str) -> ExecutionResult:
        """Execute Claude Code implementation using instruction files"""
        start_time = time.time()
        agent_results = []
        errors = []

        phase_id = self.phases.get(phase_choice, self.phases["1"])["id"]

        console.print(f"[cyan]🚀 Starting Claude Code execution for {phase_id}[/cyan]")

        if agent_choice == "6":  # All agents
            # Execute in dependency order
            agent_results = await self._execute_dependency_order(phase_id)
        else:
            # Execute single agent
            selected_agent = self.agents.get(agent_choice)
            if selected_agent:
                agent_results = [await self._execute_single_agent(selected_agent, phase_id)]

        total_time = time.time() - start_time
        success = all(result.success for result in agent_results)

        # Create error summary if there were failures
        error_summary = None
        if not success:
            failed_agents = [r.agent_name for r in agent_results if not r.success]
            error_summary = f"Failed agents: {', '.join(failed_agents)}"

        return ExecutionResult(
            success=success,
            total_execution_time=total_time,
            agent_results=agent_results,
            errors=errors,
            error_summary=error_summary
        )

    async def _execute_dependency_order(self, phase_id: str) -> List[AgentResult]:
        """Execute agents in dependency order with parallel opportunities"""
        results = []

        while True:
            available_agents = self._get_available_agents(phase_id)
            if not available_agents:
                break

            console.print(f"[cyan]📋 Available agents: {', '.join(available_agents)}[/cyan]")

            # Execute available agents in parallel
            tasks = []
            for agent_id in available_agents:
                agent_info = {"id": agent_id, "name": f"{agent_id.title()} Agent"}
                tasks.append(self._execute_single_agent(agent_info, phase_id))

            if tasks:
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                for result in batch_results:
                    if isinstance(result, AgentResult):
                        results.append(result)
                    else:
                        console.print(f"[red]❌ Agent execution error: {result}[/red]")
            else:
                break

        return results

    async def execute_optimized_implementation(self, agent_choice: str, phase_choice: str) -> ExecutionResult:
        """Execute Claude Code implementation using optimized execution plan with performance monitoring"""
        if not self.optimizer:
            console.print("[yellow]⚠️ Execution optimizer not available, falling back to standard execution[/yellow]")
            return await self.execute_implementation(agent_choice, phase_choice)
        
        start_time = time.time()
        
        # Create optimized execution plan
        if not self.execution_plan:
            console.print("[cyan]🚀 Creating optimized execution plan...[/cyan]")
            self.execution_plan = self.optimizer.create_execution_plan()
        
        # Start performance monitoring
        if self.performance_monitor:
            total_agents = 1 if agent_choice != "6" else len(self.agents)
            total_estimated_time = self.execution_plan.total_estimated_time if agent_choice == "6" else 30
            self.performance_monitor.start_session(total_agents, total_estimated_time)
            self.performance_monitor.start_real_time_monitoring()
        
        phase_id = self.phases.get(phase_choice, self.phases["1"])["id"]
        agent_results = []
        errors = []
        
        if agent_choice == "6":  # All agents
            agent_results = await self._execute_optimized_plan(phase_id)
        else:
            # Execute single agent with optimization
            selected_agent = self.agents.get(agent_choice)
            if selected_agent:
                task_id = f"{selected_agent['id']}-{phase_id}"
                if task_id in self.execution_plan.tasks:
                    agent_results = [await self._execute_optimized_agent(selected_agent, phase_id)]
                else:
                    # Fallback to standard execution
                    agent_results = [await self._execute_single_agent(selected_agent, phase_id)]
        
        total_time = time.time() - start_time
        success = all(result.success for result in agent_results)
        
        # Stop performance monitoring and generate report
        if self.performance_monitor:
            self.performance_monitor.stop_real_time_monitoring()
            performance_report = self.performance_monitor.generate_performance_report()
            console.print("[green]📊 Performance report generated[/green]")
        
        # Create error summary if there were failures
        error_summary = None
        if not success:
            failed_agents = [r.agent_name for r in agent_results if not r.success]
            error_summary = f"Failed agents: {', '.join(failed_agents)}"
        
        return ExecutionResult(
            success=success,
            total_execution_time=total_time,
            agent_results=agent_results,
            errors=errors,
            error_summary=error_summary
        )

    async def _execute_optimized_plan(self, phase_id: str) -> List[AgentResult]:
        """Execute agents using optimized execution plan"""
        results = []
        completed_tasks = set()
        
        # Filter execution order for the specified phase
        phase_batches = []
        for batch in self.execution_plan.execution_order:
            phase_batch = [task_id for task_id in batch if task_id.endswith(f"-{phase_id}")]
            if phase_batch:
                phase_batches.append(phase_batch)
        
        console.print(f"[cyan]📋 Executing {len(phase_batches)} optimized batches for {phase_id}[/cyan]")
        
        for batch_num, batch in enumerate(phase_batches, 1):
            console.print(f"[cyan]🔄 Executing batch {batch_num}/{len(phase_batches)} ({len(batch)} agents in parallel)[/cyan]")
            
            # Execute batch in parallel
            batch_tasks = []
            for task_id in batch:
                agent_id = task_id.split('-')[0]
                agent_info = next((agent for agent in self.agents.values() if agent['id'] == agent_id), None)
                if agent_info:
                    batch_tasks.append(self._execute_optimized_agent(agent_info, phase_id))
            
            if batch_tasks:
                batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
                for i, result in enumerate(batch_results):
                    if isinstance(result, AgentResult):
                        results.append(result)
                        if result.success:
                            completed_tasks.add(batch[i])
                        # Update optimizer with completion status
                        self.optimizer.update_task_status(
                            batch[i], 
                            "completed" if result.success else "failed",
                            end_time=time.time()
                        )
                    else:
                        console.print(f"[red]❌ Batch execution error: {result}[/red]")
        
        return results

    async def _execute_optimized_agent(self, agent: Dict, phase_id: str) -> AgentResult:
        """Execute single agent with optimization and performance monitoring"""
        task_id = f"{agent['id']}-{phase_id}"
        agent_id = agent['id']
        
        # Get estimated duration from execution plan
        estimated_duration = 30
        if self.execution_plan and task_id in self.execution_plan.tasks:
            estimated_duration = self.execution_plan.tasks[task_id].estimated_duration
        
        # Start performance monitoring
        if self.performance_monitor:
            self.performance_monitor.start_agent_monitoring(agent_id, phase_id, estimated_duration)
        
        # Update optimizer with start status
        if self.optimizer:
            self.optimizer.update_task_status(task_id, "in_progress", start_time=time.time())
        
        # Execute using standard method but with enhanced monitoring
        result = await self._execute_single_agent(agent, phase_id)
        
        # Complete performance monitoring
        if self.performance_monitor:
            error_count = 1 if not result.success else 0
            self.performance_monitor.complete_agent_monitoring(agent_id, phase_id, result.success, error_count)
        
        # Update optimizer with completion status
        if self.optimizer:
            self.optimizer.update_task_status(
                task_id, 
                "completed" if result.success else "failed",
                end_time=time.time()
            )
        
        return result

    async def _execute_single_agent(self, agent: Dict, phase_id: str) -> AgentResult:
        """Execute Claude Code for a single agent using instruction file"""
        start_time = time.time()
        agent_name = agent["name"]
        agent_id = agent["id"]

        console.print(f"[cyan]🤖 Starting {agent_name} implementation for {phase_id}...[/cyan]")

        # Update status to in_progress
        self._update_agent_status(agent_id, phase_id, "in_progress")

        try:
            # Check rate limits
            if self.security_manager:
                if not self.security_manager.check_rate_limit("claude_api", agent_id):
                    error_msg = f"Rate limit exceeded for {agent_id}"
                    self._update_agent_status(agent_id, phase_id, "failed", error_msg)
                    return AgentResult(agent_name, False, error_message=error_msg)
            
            # Load instruction file
            instruction_content = self._load_instruction_file(agent_id, phase_id)
            if not instruction_content:
                error_msg = f"Instruction file not found for {agent_id}-{phase_id}"
                self._update_agent_status(agent_id, phase_id, "failed", error_msg)
                return AgentResult(agent_name, False, error_message=error_msg)

            # Create the Claude Code command
            command = self._create_claude_command_from_instruction(agent, phase_id, instruction_content)

            # Create log file for this execution
            log_file = self.logs_path / f"{agent_id}_{phase_id}_claude_execution.log"

            # Convert Windows path to WSL path properly
            wsl_log_file = self._convert_to_wsl_path(str(log_file))

            # Ensure log directory exists in WSL
            wsl_logs_dir = self._convert_to_wsl_path(str(self.logs_path))
            console.print(f"[dim]Creating log directory: {wsl_logs_dir}[/dim]")

            # Execute Claude Code in WSL
            result = await self._run_claude_code_wsl(command, wsl_log_file)

            execution_time = time.time() - start_time

            if result.get("success", False):
                console.print(f"[green]✅ {agent_name} completed successfully![/green]")
                self._update_agent_status(agent_id, phase_id, "completed")
                return AgentResult(agent_name, True, execution_time=execution_time)
            else:
                error_msg = result.get("error", "Unknown error")
                console.print(f"[red]❌ {agent_name} failed: {error_msg}[/red]")
                self._update_agent_status(agent_id, phase_id, "failed", error_msg)
                return AgentResult(agent_name, False, error_message=error_msg, execution_time=execution_time)

        except SecurityError as e:
            execution_time = time.time() - start_time
            error_msg = f"Security violation: {str(e)}"
            console.print(f"[red]🚨 {agent_name} execution blocked by security: {error_msg}[/red]")
            self._update_agent_status(agent_id, phase_id, "failed", error_msg)
            return AgentResult(agent_name, False, error_message=error_msg, execution_time=execution_time)
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = str(e)
            console.print(f"[red]❌ {agent_name} execution failed: {error_msg}[/red]")
            self._update_agent_status(agent_id, phase_id, "failed", error_msg)
            return AgentResult(agent_name, False, error_message=error_msg, execution_time=execution_time)

    def _load_instruction_file(self, agent_id: str, phase_id: str) -> Optional[str]:
        """Load instruction file for agent/phase combination"""
        phase_name = "mvp-core-features" if phase_id == "phase1" else "advanced-features" if phase_id == "phase2" else "production-ready"
        instruction_file = self.instructions_path / f"{agent_id}-{phase_id}-{phase_name}.md"

        if not instruction_file.exists():
            # Try fallback without -features suffix
            phase_name_fallback = "mvp-core" if phase_id == "phase1" else "advanced-features" if phase_id == "phase2" else "production-ready"
            instruction_file = self.instructions_path / f"{agent_id}-{phase_id}-{phase_name_fallback}.md"

            if not instruction_file.exists():
                console.print(f"[red]❌ Instruction file not found: {instruction_file}[/red]")
                console.print(f"[red]❌ Also tried: {self.instructions_path / f'{agent_id}-{phase_id}-{phase_name}.md'}[/red]")
                return None

        console.print(f"[green]📖 Loading instruction file: {instruction_file.name}[/green]")
        with open(instruction_file, 'r', encoding='utf-8') as f:
            return f.read()

    def _create_claude_command_from_instruction(self, agent: Dict, phase_id: str, instruction_content: str) -> str:
        """Create Claude Code command using instruction file reference with security validation"""
        wsl_base_path = self._convert_to_wsl_path(str(self.base_path))
        
        # Load configuration
        config = self.config
        
        # Create instruction file path
        instruction_file_path = f"generated_documents/design/claude_instructions/{agent['id']}-{phase_id}.md"
        wsl_instruction_path = self._convert_to_wsl_path(str(self.base_path / instruction_file_path))
        
        # Validate file access
        if self.security_manager:
            if not self.security_manager.validate_file_access(str(self.base_path / instruction_file_path), "read"):
                raise SecurityError(f"File access denied: {instruction_file_path}")
        
        # Use file-based prompting to avoid shell escaping
        model_flag = config.get('model', 'sonnet').replace('claude-', '').replace('-20250514', '')
        
        command = f'cd {wsl_base_path} && claude --model {model_flag} --dangerously-skip-permissions --file {wsl_instruction_path}'
        
        # Validate command security
        if self.security_manager:
            if not self.security_manager.validate_command(command):
                raise SecurityError(f"Command blocked by security policy: {command}")
            
            # Sanitize command for WSL
            command = self.security_manager.sanitize_command_for_wsl(command)
        
        return command

    def _convert_to_wsl_path(self, windows_path: str) -> str:
        """Convert Windows path to WSL path format"""
        # Convert backslashes to forward slashes
        wsl_path = windows_path.replace("\\", "/")

        # Convert drive letters (e.g., D: -> /mnt/d)
        if len(wsl_path) >= 2 and wsl_path[1] == ':':
            drive_letter = wsl_path[0].lower()
            wsl_path = f"/mnt/{drive_letter}" + wsl_path[2:]

        return wsl_path

    async def _run_claude_code_wsl(self, command: str, wsl_log_file: str) -> Dict:
        """Run Claude Code command in WSL and capture results"""
        try:
            # Create a wrapper script that includes notification
            wrapper_script = f"""
#!/bin/bash
set -e

# Create log directory if it doesn't exist
mkdir -p "$(dirname "{wsl_log_file}")"

echo "Starting Claude Code execution at $(date)" >> {wsl_log_file}

{command} 2>&1 | tee -a {wsl_log_file}

CLAUDE_EXIT_CODE=${{PIPESTATUS[0]}}
echo "Claude exit code: $CLAUDE_EXIT_CODE" >> {wsl_log_file}

if [ $CLAUDE_EXIT_CODE -eq 0 ]; then
    echo "SUCCESS" >> {wsl_log_file}
    exit 0
else
    echo "FAILED:Exit code $CLAUDE_EXIT_CODE" >> {wsl_log_file}
    exit $CLAUDE_EXIT_CODE
fi
"""

            # Execute the wrapper script with configurable timeout
            timeout_seconds = self.config.get('timeout', 600)
            result = await asyncio.to_thread(
                subprocess.run,
                ["wsl", "-d", "Ubuntu", "-e", "bash", "-c", wrapper_script],
                capture_output=True,
                text=True,
                timeout=timeout_seconds
            )

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "error": result.stderr if result.returncode != 0 else None
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "returncode": -1
            }
