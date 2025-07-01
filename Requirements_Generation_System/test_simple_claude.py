#!/usr/bin/env python3
"""
Test simple Claude Code execution
"""

import asyncio
from pathlib import Path
from claude_code_executor import ClaudeCodeExecutor
from rich.console import Console

console = Console()


async def test_simple_claude():
    """Test Claude Code with a simple, fast command"""
    
    console.print("[bold blue]🔍 Testing Simple Claude Code Execution[/bold blue]")
    
    base_path = Path("project")
    executor = ClaudeCodeExecutor(base_path)
    
    # Override the prompt creation to use a simple test prompt
    original_create_command = executor._create_claude_command
    
    def simple_create_command(agent, phase_choice):
        agent_id = agent["id"]
        wsl_base_path = str(base_path).replace("\\", "/").replace("D:", "/mnt/d")
        
        # Simple test prompt that should complete quickly
        prompt = "Just say 'Hello from Claude Code!' and confirm you can see the project. Do not create any files. Keep response brief."
        
        # Build the Claude Code command
        command = f'''cd {wsl_base_path} && claude --model sonnet --dangerously-skip-permissions -p "{prompt}"'''
        
        return command
    
    # Temporarily replace the method
    executor._create_claude_command = simple_create_command
    
    console.print("[yellow]Testing with simple prompt...[/yellow]")
    
    try:
        result = await executor.execute_implementation("1", "1")  # Frontend, Phase 1
        
        if result.success:
            console.print(f"[green]✅ Simple test successful![/green]")
            console.print(f"[green]Total time: {result.total_execution_time:.2f}s[/green]")
            
            for agent_result in result.agent_results:
                console.print(f"[green]Agent: {agent_result.agent_name}[/green]")
                console.print(f"[green]Success: {agent_result.success}[/green]")
                console.print(f"[green]Time: {agent_result.execution_time:.2f}s[/green]")
        else:
            console.print(f"[red]❌ Simple test failed[/red]")
            console.print(f"[red]Error: {result.error_summary}[/red]")
    
    except Exception as e:
        console.print(f"[red]❌ Test failed: {e}[/red]")
        import traceback
        traceback.print_exc()
    
    # Check the log file
    log_file = executor.logs_path / "frontend_claude_execution.log"
    if log_file.exists():
        console.print(f"\n[bold]Log file content:[/bold]")
        with open(log_file, 'r') as f:
            content = f.read()
        console.print(f"[blue]{content}[/blue]")
    else:
        console.print("[yellow]No log file found[/yellow]")


if __name__ == "__main__":
    asyncio.run(test_simple_claude())
