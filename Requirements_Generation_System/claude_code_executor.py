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
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


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

    async def _execute_single_agent(self, agent: Dict, phase_id: str) -> AgentResult:
        """Execute Claude Code for a single agent using instruction file"""
        start_time = time.time()
        agent_name = agent["name"]
        agent_id = agent["id"]

        console.print(f"[cyan]🤖 Starting {agent_name} implementation for {phase_id}...[/cyan]")

        # Update status to in_progress
        self._update_agent_status(agent_id, phase_id, "in_progress")

        try:
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
        """Create Claude Code command using instruction file content"""
        wsl_base_path = self._convert_to_wsl_path(str(self.base_path))

        # Create a shorter, focused prompt that references the instruction file
        agent_name = agent.get('name', 'Unknown Agent')
        instruction_file_path = f"generated_documents/design/claude_instructions/{agent['id']}-{phase_id}.md"

        short_prompt = f"""I need you to implement the {agent_name} for {phase_id}.

Please read and follow the detailed instructions in the file: {instruction_file_path}

This file contains:
- Complete mission statement and objectives
- Detailed deliverables and requirements
- Build and test procedures
- Completion criteria
- Error handling guidelines

Please implement all requirements specified in that instruction file. Focus on:
1. Following the exact deliverables listed
2. Building and testing the implementation
3. Providing a completion report as specified
4. Ensuring all dependencies are properly handled

Start by reading the instruction file and then proceed with the implementation."""

        # Escape the short prompt for shell safety
        escaped_prompt = short_prompt.replace('"', '\\"').replace('`', '\\`')
        command = f'cd {wsl_base_path} && claude --model sonnet --dangerously-skip-permissions -p "{escaped_prompt}"'

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

            # Execute the wrapper script
            result = await asyncio.to_thread(
                subprocess.run,
                ["wsl", "-d", "Ubuntu", "-e", "bash", "-c", wrapper_script],
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
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
