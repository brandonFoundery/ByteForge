#!/usr/bin/env python3
"""
Direct test of Claude Code execution without run_generation.py dependencies
"""
import asyncio
from pathlib import Path
from claude_code_executor import ClaudeCodeExecutor
from rich.console import Console

console = Console()

async def test_direct_claude_execution():
    """Test Claude Code execution directly"""
    console.print("[bold blue]🚀 Testing Direct Claude Code Execution[/bold blue]")
    
    try:
        # Initialize executor
        base_path = Path(".")
        executor = ClaudeCodeExecutor(base_path)
        
        console.print(f"[cyan]📂 Base path: {base_path.absolute()}[/cyan]")
        console.print(f"[cyan]📂 Instructions path: {executor.instructions_path}[/cyan]")
        
        # Test available agents
        available_agents = executor._get_available_agents("phase1")
        console.print(f"[cyan]🤖 Available agents: {available_agents}[/cyan]")
        
        if not available_agents:
            console.print("[red]❌ No agents available[/red]")
            return False
        
        # Get first available agent
        agent_id = available_agents[0]
        agent = None
        
        # Find agent config
        for key, agent_config in executor.agents.items():
            if agent_config["id"] == agent_id:
                agent = agent_config
                break
        
        if not agent:
            console.print(f"[red]❌ Agent config not found for {agent_id}[/red]")
            return False
        
        console.print(f"[bold green]🎯 Executing: {agent['name']}[/bold green]")
        console.print(f"[dim]Agent ID: {agent['id']}[/dim]")
        
        # Test instruction file loading
        instruction_content = executor._load_instruction_file(agent_id, "phase1")
        if not instruction_content:
            console.print(f"[red]❌ Could not load instruction file[/red]")
            return False
        
        console.print(f"[green]✅ Loaded instruction file ({len(instruction_content)} chars)[/green]")
        
        # Test command generation
        try:
            command = executor._create_claude_command_from_instruction(agent, "phase1", instruction_content)
            console.print(f"[cyan]🔨 Generated command:[/cyan]")
            console.print(f"[dim]{command}[/dim]")
            
            if "--dangerously-skip-permissions" in command:
                console.print("[green]✅ Command includes bypass permissions flag[/green]")
            else:
                console.print("[yellow]⚠️ Command missing bypass permissions flag[/yellow]")
        
        except Exception as e:
            console.print(f"[red]❌ Command generation failed: {e}[/red]")
            return False
        
        # Execute the agent
        console.print(f"[bold cyan]🚀 Executing Claude Code for {agent['name']}...[/bold cyan]")
        
        result = await executor._execute_single_agent(agent, "phase1")
        
        if result.success:
            console.print(f"[bold green]🎉 SUCCESS: {agent['name']} completed![/bold green]")
            console.print(f"[green]⏱️ Execution time: {result.execution_time:.2f}s[/green]")
            
            # Check what was generated
            code_path = base_path / "project" / "code"
            if code_path.exists():
                generated_files = list(code_path.rglob("*"))
                console.print(f"[cyan]📁 Files in project/code: {len(generated_files)}[/cyan]")
                for file in generated_files[:10]:  # Show first 10 files
                    if file.is_file():
                        console.print(f"  📄 {file.relative_to(code_path)}")
            
            return True
        else:
            console.print(f"[bold red]❌ FAILED: {result.error_message}[/bold red]")
            return False
            
    except Exception as e:
        console.print(f"[red]💥 Execution failed: {e}[/red]")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    console.print("[bold]🧪 Direct Claude Code Execution Test[/bold]")
    success = asyncio.run(test_direct_claude_execution())
    
    if success:
        console.print("[bold green]✅ Test completed successfully![/bold green]")
    else:
        console.print("[bold red]❌ Test failed![/bold red]")