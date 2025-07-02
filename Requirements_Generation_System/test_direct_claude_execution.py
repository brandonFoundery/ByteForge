#!/usr/bin/env python3
"""
Direct test of Claude Code execution without dependencies
"""
import asyncio
import sys
from pathlib import Path

from claude_code_executor import ClaudeCodeExecutor
from rich.console import Console

console = Console()

async def test_direct_execution():
    """Test direct Claude Code execution"""
    console.print("[bold blue]🚀 Testing Direct Claude Code Execution[/bold blue]")
    
    try:
        # Initialize executor
        base_path = Path(__file__).parent
        executor = ClaudeCodeExecutor(base_path)
        
        console.print("[cyan]🔍 Available agents for execution:[/cyan]")
        available_agents = executor._get_available_agents("phase1")
        
        if not available_agents:
            console.print("[red]❌ No agents available for execution[/red]")
            return False
        
        # Select first available agent
        agent_id = available_agents[0]
        agent = None
        
        # Find the agent config
        for key, agent_config in executor.agents.items():
            if agent_config["id"] == agent_id:
                agent = agent_config
                break
        
        if not agent:
            console.print(f"[red]❌ Could not find agent config for {agent_id}[/red]")
            return False
        
        console.print(f"[cyan]🤖 Executing agent: {agent['name']} ({agent_id})[/cyan]")
        
        # Execute the agent
        result = await executor._execute_single_agent(agent, "phase1")
        
        if result.success:
            console.print(f"[bold green]✅ SUCCESS: {agent['name']} completed in {result.execution_time:.2f}s[/bold green]")
            return True
        else:
            console.print(f"[bold red]❌ FAILED: {agent['name']} - {result.error_message}[/bold red]")
            return False
        
    except Exception as e:
        console.print(f"[red]💥 Execution failed: {e}[/red]")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    console.print("[bold]Starting direct Claude Code execution test...[/bold]")
    success = asyncio.run(test_direct_execution())
    sys.exit(0 if success else 1)