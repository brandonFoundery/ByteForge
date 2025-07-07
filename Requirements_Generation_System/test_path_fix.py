#!/usr/bin/env python3
"""
Test if the path fix resolved the instruction file issue
"""
import asyncio
from pathlib import Path
from claude_code_executor import ClaudeCodeExecutor
from rich.console import Console

console = Console()

async def test_path_fix():
    """Test if instruction files can now be found"""
    console.print("[bold blue]🧪 Testing Path Fix[/bold blue]")
    
    try:
        # Initialize executor with fixed paths
        base_path = Path(".")  # Current directory (Requirements_Generation_System)
        executor = ClaudeCodeExecutor(base_path)
        
        console.print(f"[cyan]📂 Base path: {base_path.absolute()}[/cyan]")
        console.print(f"[cyan]📂 Instructions path: {executor.instructions_path.absolute()}[/cyan]")
        console.print(f"[cyan]📂 Instructions exists: {executor.instructions_path.exists()}[/cyan]")
        
        if executor.instructions_path.exists():
            console.print("[green]✅ Instructions directory found[/green]")
            
            # List instruction files
            instruction_files = list(executor.instructions_path.glob("*.md"))
            console.print(f"[cyan]📄 Found {len(instruction_files)} instruction files:[/cyan]")
            for file in instruction_files:
                console.print(f"  • {file.name}")
        else:
            console.print("[red]❌ Instructions directory not found[/red]")
            return False
        
        # Test agent detection
        available_agents = executor._get_available_agents("phase1")
        console.print(f"[cyan]🤖 Available agents: {available_agents}[/cyan]")
        
        if available_agents:
            # Test instruction file loading for first agent
            agent_id = available_agents[0]
            instruction_content = executor._load_instruction_file(agent_id, "phase1")
            
            if instruction_content:
                console.print(f"[green]✅ Successfully loaded instruction file for {agent_id}[/green]")
                console.print(f"[dim]Content length: {len(instruction_content)} characters[/dim]")
                return True
            else:
                console.print(f"[red]❌ Failed to load instruction file for {agent_id}[/red]")
                return False
        else:
            console.print("[yellow]⚠️ No agents available[/yellow]")
            return False
            
    except Exception as e:
        console.print(f"[red]💥 Test failed: {e}[/red]")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_path_fix())
    if success:
        console.print("[bold green]🎉 Path fix successful! Agents should now work.[/bold green]")
    else:
        console.print("[bold red]❌ Path fix failed. More debugging needed.[/bold red]")