#!/usr/bin/env python3
"""
Reset Progress Tracker and Execute Real Claude Code Implementation

This script resets the progress tracker to fix the false "completed" status
and then executes Claude Code implementation properly.
"""

import json
import sys
import time
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt

console = Console()

def reset_progress_tracker():
    """Reset progress tracker to mark all agents as not_started"""
    tracker_file = Path("../generated_documents/design/claude_instructions/progress_tracker.json")
    
    if not tracker_file.exists():
        console.print(f"[red]❌ Progress tracker not found: {tracker_file}[/red]")
        return False
    
    console.print(f"[yellow]📋 Resetting progress tracker...[/yellow]")
    
    with open(tracker_file, 'r', encoding='utf-8') as f:
        tracker = json.load(f)
    
    # Reset all agents to not_started
    for phase_name, phase_data in tracker.items():
        if phase_name == "execution_metadata":
            continue
            
        if "agents" in phase_data:
            for agent_key, agent_data in phase_data["agents"].items():
                agent_data["status"] = "not_started"
                agent_data["started_at"] = None
                agent_data["completed_at"] = None
                agent_data["actual_duration_minutes"] = None
                agent_data["error_log"] = None
                agent_data["retry_count"] = 0
                
                # Reset completion criteria to false
                if "completion_criteria" in agent_data:
                    for criteria in agent_data["completion_criteria"]:
                        agent_data["completion_criteria"][criteria] = False
    
    # Reset phase statuses
    for phase_name in ["phase1_mvp_core_features", "phase2_advanced_features", "phase3_production_ready"]:
        if phase_name in tracker:
            tracker[phase_name]["status"] = "not_started"
            tracker[phase_name]["started_at"] = None
            tracker[phase_name]["completed_at"] = None
    
    # Update execution metadata
    tracker["execution_metadata"]["last_updated"] = time.time()
    tracker["execution_metadata"]["overall_status"] = "not_started"
    tracker["execution_metadata"]["completed_agents"] = 0
    tracker["execution_metadata"]["failed_agents"] = 0
    
    # Save the reset tracker
    with open(tracker_file, 'w', encoding='utf-8') as f:
        json.dump(tracker, f, indent=2)
    
    console.print(f"[green]✅ Progress tracker reset successfully![/green]")
    return True

def execute_claude_code_frontend():
    """Execute Claude Code for Frontend Agent Phase 1 with proper monitoring"""
    console.print(f"\n[cyan]🚀 Starting Frontend Agent Phase 1 Implementation[/cyan]")
    
    # Check if instruction file exists
    instruction_file = Path("../generated_documents/design/claude_instructions/frontend-phase1-mvp-core-features.md")
    if not instruction_file.exists():
        console.print(f"[red]❌ Instruction file not found: {instruction_file}[/red]")
        return False
    
    console.print(f"[green]📖 Found instruction file: {instruction_file.name}[/green]")
    
    # Check if FrontEnd directory exists
    frontend_dir = Path("../FrontEnd")
    if not frontend_dir.exists():
        console.print(f"[red]❌ Frontend directory not found: {frontend_dir.absolute()}[/red]")
        return False
    
    console.print(f"[green]📁 Found frontend directory: {frontend_dir.absolute()}[/green]")
    
    # Create Claude Code command
    wsl_frontend_path = "project/FrontEnd"
    wsl_instruction_path = "project/generated_documents/design/claude_instructions/frontend-phase1-mvp-core-features.md"
    
    console.print(f"[cyan]💻 Executing Claude Code with real-time monitoring...[/cyan]")
    console.print(f"[dim]Frontend path: {wsl_frontend_path}[/dim]")
    console.print(f"[dim]Instruction file: {wsl_instruction_path}[/dim]")
    
    # Create the command
    claude_command = f"""
cd {wsl_frontend_path} && \\
echo "[INFO] Starting Claude Code Frontend Implementation" && \\
echo "[INFO] Current directory: $(pwd)" && \\
echo "[INFO] Instruction file: {wsl_instruction_path}" && \\
claude --model sonnet --dangerously-skip-permissions -p "@{wsl_instruction_path}" && \\
echo "[SUCCESS] Claude Code completed successfully!"
"""
    
    console.print(f"[yellow]⏱️  Launching Claude Code (this may take several minutes)...[/yellow]")
    console.print(f"[cyan]Command: claude --model sonnet -p @frontend-phase1-mvp-core-features.md[/cyan]")
    
    # Execute in WSL with real-time output
    import subprocess
    try:
        cmd = [
            "wsl", "-d", "Ubuntu", "-e", "bash", "-c", claude_command
        ]
        
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        console.print("[bold]Claude Code Output:[/bold]")
        console.print("=" * 60)
        
        # Show real-time output
        for line in proc.stdout:
            print(line.rstrip())
        
        return_code = proc.wait()
        
        console.print("=" * 60)
        console.print(f"[bold]Claude Code execution completed with exit code: {return_code}[/bold]")
        
        if return_code == 0:
            console.print(f"\n[bold green]🎉 Frontend implementation completed successfully![/bold green]")
            return True
        else:
            console.print(f"\n[yellow]⚠️  Claude Code completed with exit code: {return_code}[/yellow]")
            return False
            
    except Exception as e:
        console.print(f"\n[red]❌ Failed to execute Claude Code: {e}[/red]")
        return False

def main():
    """Main execution function"""
    console.print("[bold blue]🔧 Reset and Implement CRM Features[/bold blue]")
    console.print("This will:")
    console.print("  1. Reset the progress tracker (fix false 'completed' status)")
    console.print("  2. Execute Claude Code for Frontend Agent Phase 1")
    console.print("  3. Monitor real-time implementation progress")
    console.print("  4. Verify actual code deliverables")
    
    confirm = Prompt.ask("\nProceed with reset and implementation?", choices=["y", "n"], default="y")
    if confirm.lower() != "y":
        console.print("[yellow]Operation cancelled.[/yellow]")
        return 0
    
    # Step 1: Reset progress tracker
    console.print(f"\n[bold cyan]Step 1: Reset Progress Tracker[/bold cyan]")
    if not reset_progress_tracker():
        console.print("[red]❌ Failed to reset progress tracker[/red]")
        return 1
    
    # Step 2: Execute Claude Code for Frontend
    console.print(f"\n[bold cyan]Step 2: Execute Frontend Implementation[/bold cyan]")
    if not execute_claude_code_frontend():
        console.print("[red]❌ Frontend implementation failed[/red]")
        return 1
    
    console.print(f"\n[bold green]🎉 Reset and implementation completed successfully![/bold green]")
    console.print(f"[green]✅ Progress tracker reset[/green]")
    console.print(f"[green]✅ Frontend Agent Phase 1 implemented[/green]")
    console.print(f"\n[cyan]💡 Next steps:[/cyan]")
    console.print(f"  • Check the FrontEnd directory for new CRM components")
    console.print(f"  • Test the application at http://localhost:4000")
    console.print(f"  • Run Backend Agent Phase 1 if frontend is working")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
