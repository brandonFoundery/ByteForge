#!/usr/bin/env python3
"""
Claude Code Instruction Generator

This module generates individual instruction files for Claude Code agents,
creating a repeatable and maintainable system for AI-driven development.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


class ClaudeInstructionGenerator:
    """Generates Claude Code instruction files and orchestration documents"""
    
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.instructions_path = base_path / "generated_documents" / "design" / "claude_instructions"
        self.design_path = base_path / "generated_documents" / "design"
        
        # Agent and phase definitions
        self.agents = {
            "backend": {
                "name": "Backend Agent",
                "description": "ASP.NET Core API, data models, business logic",
                "directory": "BackEnd",
                "foundation": True  # Must complete first
            },
            "frontend": {
                "name": "Frontend Agent", 
                "description": "React/Next.js user interface components",
                "directory": "FrontEnd",
                "foundation": False
            },
            "security": {
                "name": "Security Agent",
                "description": "Authentication, authorization, audit logging", 
                "directory": "BackEnd",
                "foundation": False
            },
            "infrastructure": {
                "name": "Infrastructure Agent",
                "description": "Azure resources, CI/CD, containerization",
                "directory": "Infrastructure", 
                "foundation": False
            },
            "integration": {
                "name": "Integration Agent",
                "description": "API integration, data synchronization, external services",
                "directory": "BackEnd",
                "foundation": False
            }
        }
        
        self.phases = {
            "phase1": {
                "name": "MVP Core Features",
                "description": "Implement core functionality for minimum viable product",
                "duration_range": "30-60 minutes"
            },
            "phase2": {
                "name": "Advanced Features", 
                "description": "Add advanced functionality and business logic",
                "duration_range": "25-50 minutes"
            },
            "phase3": {
                "name": "Production Ready",
                "description": "Production hardening, performance, monitoring",
                "duration_range": "25-40 minutes"
            }
        }
        
        # Dependencies matrix
        self.dependencies = {
            "phase1": {
                "backend": [],
                "frontend": ["backend"],
                "security": ["backend"],
                "infrastructure": ["backend"],
                "integration": ["backend", "frontend", "security"]
            },
            "phase2": {
                "backend": ["backend-phase1", "integration-phase1"],
                "frontend": ["backend-phase2", "frontend-phase1"],
                "security": ["backend-phase2", "security-phase1"],
                "infrastructure": ["infrastructure-phase1"],
                "integration": ["backend-phase2", "frontend-phase2", "security-phase2", "infrastructure-phase2"]
            },
            "phase3": {
                "infrastructure": ["infrastructure-phase2"],
                "backend": ["infrastructure-phase3", "backend-phase2"],
                "frontend": ["infrastructure-phase3", "frontend-phase2"],
                "security": ["infrastructure-phase3", "security-phase2"],
                "integration": ["backend-phase3", "frontend-phase3", "security-phase3"]
            }
        }
        
        # Parallel execution opportunities
        self.parallel_groups = {
            "phase1": [
                ["frontend", "security", "infrastructure"]  # Can run parallel after backend
            ],
            "phase2": [
                ["frontend", "security", "infrastructure"]  # Can run parallel after backend-phase2
            ],
            "phase3": [
                ["backend", "frontend", "security"]  # Can run parallel after infrastructure-phase3
            ]
        }

    def generate_all_instructions(self) -> bool:
        """Generate all Claude instruction files and orchestration documents"""
        try:
            console.print("[bold blue]🚀 Generating Claude Code Instructions[/bold blue]")
            
            # Ensure directories exist
            self.instructions_path.mkdir(parents=True, exist_ok=True)
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                
                # Generate orchestration files
                task1 = progress.add_task("Creating orchestration files...", total=None)
                self._generate_execution_plan()
                self._generate_progress_tracker()
                progress.update(task1, completed=True)
                
                # Generate individual instruction files
                task2 = progress.add_task("Generating instruction files...", total=None)
                self._generate_all_instruction_files()
                progress.update(task2, completed=True)
                
                # Update executor to use new system
                task3 = progress.add_task("Updating executor system...", total=None)
                self._update_claude_executor()
                progress.update(task3, completed=True)
            
            console.print("[bold green]✅ Claude Code instruction system generated successfully![/bold green]")
            console.print(f"[green]📁 Instructions location: {self.instructions_path}[/green]")
            return True
            
        except Exception as e:
            console.print(f"[bold red]❌ Failed to generate instructions: {e}[/bold red]")
            return False

    def _generate_execution_plan(self):
        """Generate the master execution plan document"""
        execution_plan = self._create_execution_plan_content()
        
        plan_file = self.instructions_path / "execution_plan.md"
        with open(plan_file, 'w', encoding='utf-8') as f:
            f.write(execution_plan)
        
        console.print(f"[dim]📋 Created execution plan: {plan_file}[/dim]")

    def _generate_progress_tracker(self):
        """Generate the progress tracker JSON file"""
        progress_data = self._create_progress_tracker_data()
        
        tracker_file = self.instructions_path / "progress_tracker.json"
        with open(tracker_file, 'w', encoding='utf-8') as f:
            json.dump(progress_data, f, indent=2)
        
        console.print(f"[dim]📊 Created progress tracker: {tracker_file}[/dim]")

    def _generate_all_instruction_files(self):
        """Generate all individual instruction files"""
        for phase_id, phase_info in self.phases.items():
            for agent_id, agent_info in self.agents.items():
                self._generate_instruction_file(agent_id, phase_id, agent_info, phase_info)

    def _generate_instruction_file(self, agent_id: str, phase_id: str, agent_info: Dict, phase_info: Dict):
        """Generate a single instruction file for an agent/phase combination"""
        instruction_content = self._create_instruction_content(agent_id, phase_id, agent_info, phase_info)
        
        filename = f"{agent_id}-{phase_id}-{phase_info['name'].lower().replace(' ', '-')}.md"
        instruction_file = self.instructions_path / filename
        
        with open(instruction_file, 'w', encoding='utf-8') as f:
            f.write(instruction_content)
        
        console.print(f"[dim]📝 Created instruction: {filename}[/dim]")

    def _create_execution_plan_content(self) -> str:
        """Create the execution plan markdown content"""
        return f"""# Claude Code Execution Plan

## Overview
This document defines the execution order, dependencies, and parallel execution opportunities for Claude Code agents implementing the FY.WB.Midway project.

*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

## Agent Definitions

{self._generate_agent_definitions()}

## Execution Phases

{self._generate_phase_definitions()}

## Dependency Matrix

{self._generate_dependency_matrix()}

## Progress Tracking

Progress is tracked in `progress_tracker.json` with the following states:
- `not_started`: Agent/phase not yet begun
- `in_progress`: Agent/phase currently executing
- `completed`: Agent/phase successfully completed
- `failed`: Agent/phase failed and needs attention
- `blocked`: Agent/phase waiting for dependencies

## Execution Rules

### Pre-execution Checks
1. Verify all dependencies are in `completed` state
2. Ensure required context documents are available
3. Check that target directories exist and are accessible

### During Execution
1. Update progress tracker to `in_progress`
2. Monitor for completion signals
3. Capture all logs and outputs

### Post-execution
1. Validate completion criteria
2. Update progress tracker to `completed` or `failed`
3. Trigger dependent agents if applicable
4. Generate completion report

## Context Requirements

Each agent requires specific context documents:

### All Agents
- Project requirements (PRD, FRD, NFRD)
- Development plan (dev_plan.md)
- Database schema (db_schema.md)
- API specification (api_spec.md)

### Agent-Specific Context
{self._generate_context_requirements()}

## Completion Criteria

Each agent must provide:
1. **Code Deliverables**: All specified files created/modified
2. **Build Success**: Code compiles without errors
3. **Test Results**: All tests pass
4. **Documentation**: Updated README, API docs, etc.
5. **Completion Report**: Structured summary of work completed

## Error Handling

### Failed Executions
1. Mark agent as `failed` in progress tracker
2. Capture error logs and diagnostics
3. Block dependent agents
4. Provide retry mechanism with context

### Partial Completions
1. Allow manual intervention and resume
2. Update progress tracker with partial completion status
3. Provide rollback mechanism if needed

## Monitoring and Logging

### Log Files
- Individual agent logs: `logs/{{agent}}_{{phase}}_execution.log`
- Master execution log: `logs/execution_master.log`
- Progress updates: `logs/progress_updates.log`

### Real-time Monitoring
- Progress dashboard showing current status
- Estimated completion times
- Dependency chain visualization
- Error alerts and notifications
"""

    def _generate_agent_definitions(self) -> str:
        """Generate agent definitions section"""
        definitions = []
        for agent_id, agent_info in self.agents.items():
            definitions.append(f"- **{agent_id}**: {agent_info['description']}")
        return "\n".join(definitions)

    def _generate_phase_definitions(self) -> str:
        """Generate phase definitions section"""
        definitions = []
        for phase_id, phase_info in self.phases.items():
            definitions.append(f"""### {phase_info['name']}
**Objective**: {phase_info['description']}
**Duration Range**: {phase_info['duration_range']}
""")
        return "\n".join(definitions)

    def _generate_dependency_matrix(self) -> str:
        """Generate dependency matrix table"""
        matrix = ["| Agent/Phase | Depends On | Can Run Parallel With |",
                 "|-------------|------------|----------------------|"]
        
        for phase_id in self.phases.keys():
            for agent_id in self.agents.keys():
                agent_phase = f"{agent_id}-{phase_id}"
                deps = self.dependencies.get(phase_id, {}).get(agent_id, [])
                deps_str = ", ".join(deps) if deps else "None"
                
                # Find parallel opportunities
                parallel = []
                for group in self.parallel_groups.get(phase_id, []):
                    if agent_id in group:
                        parallel.extend([a for a in group if a != agent_id])
                parallel_str = ", ".join(parallel) if parallel else "None"
                
                matrix.append(f"| {agent_phase} | {deps_str} | {parallel_str} |")
        
        return "\n".join(matrix)

    def _generate_context_requirements(self) -> str:
        """Generate context requirements section"""
        requirements = []
        for agent_id, agent_info in self.agents.items():
            if agent_id == "backend":
                requirements.append(f"- **{agent_id}**: Data design (DRD), business requirements (BRD)")
            elif agent_id == "frontend":
                requirements.append(f"- **{agent_id}**: UI/UX specifications, component designs")
            elif agent_id == "security":
                requirements.append(f"- **{agent_id}**: Security requirements, compliance specifications")
            elif agent_id == "infrastructure":
                requirements.append(f"- **{agent_id}**: Technical requirements, deployment specifications")
            elif agent_id == "integration":
                requirements.append(f"- **{agent_id}**: All agent outputs, API documentation")
        
        return "\n".join(requirements)

    def _create_progress_tracker_data(self) -> Dict[str, Any]:
        """Create the progress tracker JSON structure"""
        tracker = {
            "execution_metadata": {
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "current_phase": "phase1",
                "overall_status": "not_started",
                "total_agents": len(self.agents) * len(self.phases),
                "completed_agents": 0,
                "failed_agents": 0,
                "estimated_total_duration_minutes": 420
            }
        }
        
        # Add phase data
        for phase_id, phase_info in self.phases.items():
            phase_data = {
                "status": "not_started",
                "started_at": None,
                "completed_at": None,
                "agents": {}
            }
            
            for agent_id, agent_info in self.agents.items():
                agent_data = {
                    "status": "not_started",
                    "started_at": None,
                    "completed_at": None,
                    "estimated_duration_minutes": self._get_estimated_duration(agent_id, phase_id),
                    "actual_duration_minutes": None,
                    "dependencies": self.dependencies.get(phase_id, {}).get(agent_id, []),
                    "can_run_parallel_with": self._get_parallel_agents(agent_id, phase_id),
                    "outputs_required": self._get_required_outputs(agent_id, phase_id),
                    "completion_criteria": {
                        "build_success": False,
                        "tests_pass": False,
                        "code_deliverables": False,
                        "documentation_updated": False,
                        "completion_report_submitted": False
                    },
                    "error_log": None,
                    "retry_count": 0
                }
                
                phase_data["agents"][f"{agent_id}-{phase_id}"] = agent_data
            
            tracker[f"{phase_id}_{phase_info['name'].lower().replace(' ', '_')}"] = phase_data
        
        return tracker

    def _get_estimated_duration(self, agent_id: str, phase_id: str) -> int:
        """Get estimated duration for agent/phase combination"""
        durations = {
            ("backend", "phase1"): 60,
            ("frontend", "phase1"): 45,
            ("security", "phase1"): 30,
            ("infrastructure", "phase1"): 35,
            ("integration", "phase1"): 30,
            ("backend", "phase2"): 50,
            ("frontend", "phase2"): 40,
            ("security", "phase2"): 25,
            ("infrastructure", "phase2"): 30,
            ("integration", "phase2"): 35,
            ("backend", "phase3"): 35,
            ("frontend", "phase3"): 30,
            ("security", "phase3"): 25,
            ("infrastructure", "phase3"): 40,
            ("integration", "phase3"): 40
        }
        return durations.get((agent_id, phase_id), 30)

    def _get_parallel_agents(self, agent_id: str, phase_id: str) -> List[str]:
        """Get agents that can run in parallel with this agent"""
        parallel = []
        for group in self.parallel_groups.get(phase_id, []):
            if agent_id in group:
                parallel.extend([a for a in group if a != agent_id])
        return parallel

    def _get_required_outputs(self, agent_id: str, phase_id: str) -> List[str]:
        """Get required outputs for agent/phase combination"""
        # This would be expanded with specific outputs for each agent/phase
        outputs = {
            ("backend", "phase1"): [
                "Core data models created",
                "CRUD operations implemented", 
                "Database context configured",
                "Authentication infrastructure ready",
                "Basic API endpoints functional"
            ],
            ("frontend", "phase1"): [
                "Dashboard layout implemented",
                "Basic forms created",
                "Authentication UI ready",
                "Navigation system functional",
                "Core components tested"
            ]
            # Add more as needed
        }
        return outputs.get((agent_id, phase_id), [f"{agent_id.title()} {phase_id} deliverables complete"])

    def _create_instruction_content(self, agent_id: str, phase_id: str, agent_info: Dict, phase_info: Dict) -> str:
        """Create instruction content for a specific agent/phase"""
        # This is a template - would be expanded with full instruction content
        return f"""# {agent_info['name']} - {phase_info['name']}

## Agent Information
- **Agent ID**: {agent_id}-{phase_id}
- **Phase**: {phase_info['name']}
- **Estimated Duration**: {self._get_estimated_duration(agent_id, phase_id)} minutes
- **Dependencies**: {', '.join(self.dependencies.get(phase_id, {}).get(agent_id, [])) or 'None'}
- **Can Run Parallel With**: {', '.join(self._get_parallel_agents(agent_id, phase_id)) or 'None'}

## Mission Statement
{self._get_mission_statement(agent_id, phase_id, agent_info, phase_info)}

## Context Documents Required
You have access to the following context documents in the repository:

### Primary Requirements
- `generated_documents/prd.md` - Product Requirements Document
- `generated_documents/FRD.md` - Functional Requirements Document  
- `generated_documents/NFRD.md` - Non-Functional Requirements Document

### Technical Specifications
- `generated_documents/dev_plan.md` - Development Plan
- `generated_documents/db_schema.md` - Database Schema
- `generated_documents/api_spec.md` - API Specification

### Design Documents
- `generated_documents/design/{agent_id}-agent-design.md` - Your specific design document
- `CLAUDE.md` - Project structure and development guidelines

{self._get_dependency_context(agent_id, phase_id)}

## Specific Deliverables

{self._get_deliverables(agent_id, phase_id)}

## Build, Test, and Fix Process

{self._get_build_process(agent_id, phase_id)}

## Completion Criteria

{self._get_completion_criteria(agent_id, phase_id)}

## Completion Report Template

When you complete this phase, provide a structured report:

```markdown
# {agent_info['name']} {phase_info['name']} Completion Report

## Summary
[Brief summary of work completed]

## Deliverables Completed
{self._get_completion_checklist(agent_id, phase_id)}

## Build Results
- Build Status: SUCCESS/FAILED
- Test Results: X/Y tests passed

## Known Issues
[List any known issues or limitations]

## Next Steps for Dependent Agents
[What other agents can now proceed]

## Files Created/Modified
[List of all files created or modified]
```

## Error Handling and Recovery

{self._get_error_handling(agent_id, phase_id)}

## Success Metrics
{self._get_success_metrics(agent_id, phase_id)}

**IMPORTANT**: {self._get_important_notes(agent_id, phase_id)}
"""

    def _get_mission_statement(self, agent_id: str, phase_id: str, agent_info: Dict, phase_info: Dict) -> str:
        """Get mission statement for agent/phase"""
        return f"Implement the {agent_info['description']} for {phase_info['description']}."

    def _get_dependency_context(self, agent_id: str, phase_id: str) -> str:
        """Get dependency context section"""
        deps = self.dependencies.get(phase_id, {}).get(agent_id, [])
        if not deps:
            return ""
        
        context = "\n### Backend Context (Dependencies)\n"
        for dep in deps:
            context += f"- {dep} outputs and APIs\n"
        return context

    def _get_deliverables(self, agent_id: str, phase_id: str) -> str:
        """Get deliverables section"""
        return f"### {agent_id.title()} {phase_id.title()} Deliverables\n[Specific deliverables would be defined here]"

    def _get_build_process(self, agent_id: str, phase_id: str) -> str:
        """Get build process section"""
        if agent_id == "backend":
            return """### 1. Build Process
```bash
cd BackEnd
dotnet restore
dotnet build
```"""
        elif agent_id == "frontend":
            return """### 1. Build Process
```bash
cd FrontEnd
npm install
npm run build
```"""
        else:
            return "### 1. Build Process\n[Build instructions specific to this agent]"

    def _get_completion_criteria(self, agent_id: str, phase_id: str) -> str:
        """Get completion criteria section"""
        return """### Code Deliverables ✓
- [ ] All required files created/modified
- [ ] Code follows project standards

### Build Success ✓
- [ ] No compilation errors
- [ ] All dependencies resolve

### Test Results ✓
- [ ] All tests pass
- [ ] Integration tests successful"""

    def _get_completion_checklist(self, agent_id: str, phase_id: str) -> str:
        """Get completion checklist"""
        outputs = self._get_required_outputs(agent_id, phase_id)
        checklist = []
        for output in outputs:
            checklist.append(f"- [x] {output}")
        return "\n".join(checklist)

    def _get_error_handling(self, agent_id: str, phase_id: str) -> str:
        """Get error handling section"""
        return """### Common Issues and Solutions
1. **Build Issues**: Check dependencies and configuration
2. **Integration Issues**: Verify dependent services are running
3. **Test Issues**: Check test data and environment setup

### Recovery Process
If critical errors occur:
1. Document the error in detail
2. Check dependency completion status
3. Attempt automated fixes
4. Mark as failed with detailed error log if unable to resolve"""

    def _get_success_metrics(self, agent_id: str, phase_id: str) -> str:
        """Get success metrics"""
        return f"- All {agent_id} {phase_id} deliverables completed\n- Clean build with no errors\n- All tests passing\n- Ready for dependent agents"

    def _get_important_notes(self, agent_id: str, phase_id: str) -> str:
        """Get important notes"""
        if self.agents[agent_id].get("foundation"):
            return "This is a foundation agent. Other agents depend on your successful completion."
        else:
            return "Ensure all dependencies are completed before starting your work."

    def _update_claude_executor(self):
        """Update the Claude executor to use the new instruction system"""
        executor_path = self.base_path / "Requirements_Generation_System" / "claude_code_executor.py"

        # Create the updated executor code
        updated_executor = self._create_updated_executor_code()

        # Backup original executor
        backup_path = executor_path.with_suffix('.py.backup')
        if executor_path.exists():
            import shutil
            shutil.copy2(executor_path, backup_path)
            console.print(f"[dim]💾 Backed up original executor to {backup_path}[/dim]")

        # Write updated executor
        with open(executor_path, 'w', encoding='utf-8') as f:
            f.write(updated_executor)

        console.print(f"[dim]🔄 Updated Claude executor to use instruction files[/dim]")

    def _create_updated_executor_code(self) -> str:
        """Create the updated executor code that uses instruction files"""
        return '''"""
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
        phase_key = f"{phase_id}_mvp_core" if phase_id == "phase1" else f"{phase_id}_advanced" if phase_id == "phase2" else f"{phase_id}_production"
        agent_key = f"{agent_id}-{phase_id}"

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

    def _check_dependencies(self, agent_id: str, phase_id: str) -> bool:
        """Check if all dependencies for an agent are completed"""
        phase_key = f"{phase_id}_mvp_core" if phase_id == "phase1" else f"{phase_id}_advanced" if phase_id == "phase2" else f"{phase_id}_production"
        agent_key = f"{agent_id}-{phase_id}"

        if phase_key not in self.progress_tracker or agent_key not in self.progress_tracker[phase_key]["agents"]:
            return False

        agent_data = self.progress_tracker[phase_key]["agents"][agent_key]
        dependencies = agent_data.get("dependencies", [])

        for dep in dependencies:
            # Check if dependency is completed
            dep_phase_key = f"{dep.split('-')[1]}_mvp_core" if dep.split('-')[1] == "phase1" else f"{dep.split('-')[1]}_advanced" if dep.split('-')[1] == "phase2" else f"{dep.split('-')[1]}_production"
            if dep_phase_key in self.progress_tracker and dep in self.progress_tracker[dep_phase_key]["agents"]:
                dep_status = self.progress_tracker[dep_phase_key]["agents"][dep]["status"]
                if dep_status != "completed":
                    console.print(f"[yellow]⏳ {agent_id}-{phase_id} waiting for dependency: {dep} (status: {dep_status})[/yellow]")
                    return False

        return True

    def _get_available_agents(self, phase_id: str) -> List[str]:
        """Get list of agents that can be executed (dependencies satisfied)"""
        available = []
        for agent_id in ["backend", "frontend", "security", "infrastructure", "integration"]:
            if self._check_dependencies(agent_id, phase_id):
                phase_key = f"{phase_id}_mvp_core" if phase_id == "phase1" else f"{phase_id}_advanced" if phase_id == "phase2" else f"{phase_id}_production"
                agent_key = f"{agent_id}-{phase_id}"

                if phase_key in self.progress_tracker and agent_key in self.progress_tracker[phase_key]["agents"]:
                    status = self.progress_tracker[phase_key]["agents"][agent_key]["status"]
                    if status == "not_started":
                        available.append(agent_id)

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

        return ExecutionResult(
            success=success,
            total_execution_time=total_time,
            agent_results=agent_results,
            errors=errors
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
            wsl_log_file = str(log_file).replace("\\\\", "/").replace("D:", "/mnt/d")

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
        phase_name = "mvp-core" if phase_id == "phase1" else "advanced-features" if phase_id == "phase2" else "production-ready"
        instruction_file = self.instructions_path / f"{agent_id}-{phase_id}-{phase_name}.md"

        if not instruction_file.exists():
            console.print(f"[red]❌ Instruction file not found: {instruction_file}[/red]")
            return None

        with open(instruction_file, 'r', encoding='utf-8') as f:
            return f.read()

    def _create_claude_command_from_instruction(self, agent: Dict, phase_id: str, instruction_content: str) -> str:
        """Create Claude Code command using instruction file content"""
        wsl_base_path = str(self.base_path).replace("\\\\", "/").replace("D:", "/mnt/d")

        # Use the instruction content directly as the prompt
        # Escape quotes in instruction content for shell safety
        escaped_content = instruction_content.replace('"', '\\"').replace('`', '\\`')
        command = f'cd {wsl_base_path} && claude --model sonnet --dangerously-skip-permissions -p "{escaped_content}"'

        return command

    async def _run_claude_code_wsl(self, command: str, wsl_log_file: str) -> Dict:
        """Run Claude Code command in WSL and capture results"""
        try:
            # Create a wrapper script that includes notification
            wrapper_script = f"""
#!/bin/bash
set -e

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
'''


def main():
    """Main function to generate Claude instructions"""
    base_path = Path("D:/Repository/@Clients/FY.WB.Midway")
    generator = ClaudeInstructionGenerator(base_path)
    
    success = generator.generate_all_instructions()
    if success:
        console.print("\n[bold green]🎉 Claude Code instruction system ready![/bold green]")
        console.print("[green]Run the updated orchestrator to use the new system.[/green]")
    else:
        console.print("\n[bold red]❌ Failed to generate instruction system.[/bold red]")


if __name__ == "__main__":
    main()
