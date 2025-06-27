#!/usr/bin/env python3
"""
Test current Claude Code executor
"""

import asyncio
from pathlib import Path
from claude_code_executor import ClaudeCodeExecutor
from rich.console import Console

console = Console()


async def test_current_executor():
    """Test the current Claude Code executor"""
    
    console.print("[bold blue]🔍 Testing Current Claude Code Executor[/bold blue]")
    
    base_path = Path("D:/Repository/@Clients/FY.WB.Midway")
    executor = ClaudeCodeExecutor(base_path)
    
    console.print(f"[cyan]Base path: {base_path}[/cyan]")
    console.print(f"[cyan]Logs path: {executor.logs_path}[/cyan]")
    
    # Test single agent execution
    console.print("\n[yellow]Testing Frontend Agent execution...[/yellow]")
    
    try:
        result = await executor.execute_implementation("1", "1")  # Frontend, Phase 1
        
        if result.success:
            console.print(f"[green]✅ Execution successful![/green]")
            console.print(f"[green]Total time: {result.total_execution_time:.2f}s[/green]")
            
            for agent_result in result.agent_results:
                console.print(f"[green]Agent: {agent_result.agent_name}[/green]")
                console.print(f"[green]Success: {agent_result.success}[/green]")
                console.print(f"[green]Time: {agent_result.execution_time:.2f}s[/green]")
                if agent_result.branch_name:
                    console.print(f"[green]Branch: {agent_result.branch_name}[/green]")
        else:
            console.print(f"[red]❌ Execution failed[/red]")
            console.print(f"[red]Error: {result.error_summary}[/red]")
            
            for agent_result in result.agent_results:
                if not agent_result.success:
                    console.print(f"[red]Failed agent: {agent_result.agent_name}[/red]")
                    console.print(f"[red]Error: {agent_result.error_message}[/red]")
    
    except Exception as e:
        console.print(f"[red]❌ Test failed: {e}[/red]")
        import traceback
        traceback.print_exc()
    
    # Check log files
    console.print("\n[bold]Checking log files...[/bold]")
    
    log_files = list(executor.logs_path.glob("*claude_execution.log"))
    if log_files:
        for log_file in log_files:
            console.print(f"[blue]Found log: {log_file.name}[/blue]")
            try:
                with open(log_file, 'r') as f:
                    content = f.read()
                console.print(f"[blue]Content: {content[:200]}...[/blue]")
            except Exception as e:
                console.print(f"[red]Could not read log: {e}[/red]")
    else:
        console.print("[yellow]No log files found[/yellow]")
    
    # Check wrapper script
    wrapper_script = executor.logs_path / "claude_wrapper.sh"
    if wrapper_script.exists():
        console.print(f"\n[bold]Wrapper script content (first 10 lines):[/bold]")
        with open(wrapper_script, 'r') as f:
            lines = f.readlines()[:10]
            for i, line in enumerate(lines, 1):
                console.print(f"[dim]{i:2d}: {line.rstrip()}[/dim]")


if __name__ == "__main__":
    asyncio.run(test_current_executor())
