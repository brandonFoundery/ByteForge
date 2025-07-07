#!/usr/bin/env python3
"""
Test script for the fixed Claude Code executor
"""
import asyncio
import sys
from pathlib import Path

from claude_code_executor import ClaudeCodeExecutor
from rich.console import Console

console = Console()

async def test_fixed_executor():
    """Test the fixed Claude Code executor"""
    console.print("[bold blue]🧪 Testing Fixed Claude Code Executor[/bold blue]")
    
    try:
        # Initialize executor
        console.print("[cyan]📋 Initializing ClaudeCodeExecutor...[/cyan]")
        base_path = Path(__file__).parent
        executor = ClaudeCodeExecutor(base_path)
        
        # Test agent detection
        console.print("[cyan]🔍 Testing agent detection for phase1...[/cyan]")
        available_agents = executor._get_available_agents("phase1")
        console.print(f"[green]✅ Found {len(available_agents)} available agents: {available_agents}[/green]")
        
        if not available_agents:
            console.print("[red]❌ No agents available - checking progress tracker...[/red]")
            
            # Show progress tracker contents
            phase_key = "phase1_mvp_core_features"
            if phase_key in executor.progress_tracker:
                agents_status = executor.progress_tracker[phase_key]["agents"]
                console.print(f"[dim]Progress tracker agents: {list(agents_status.keys())}[/dim]")
                for agent_key, agent_data in agents_status.items():
                    status = agent_data.get("status", "unknown")
                    console.print(f"  {agent_key}: {status}")
            return False
        
        # Test instruction file loading
        console.print("[cyan]📖 Testing instruction file loading...[/cyan]")
        for agent_id in available_agents[:1]:  # Test just one agent
            console.print(f"[dim]Testing agent: {agent_id}[/dim]")
            instruction_content = executor._load_instruction_file(agent_id, "phase1")
            if instruction_content:
                console.print(f"[green]✅ Loaded instruction file for {agent_id} ({len(instruction_content)} chars)[/green]")
            else:
                console.print(f"[red]❌ Failed to load instruction file for {agent_id}[/red]")
                return False
        
        # Test command generation
        console.print("[cyan]🔨 Testing Claude Code command generation...[/cyan]")
        agent = executor.agents["1"]  # Backend agent
        try:
            command = executor._create_claude_command_from_instruction(agent, "phase1", "test content")
            console.print(f"[green]✅ Generated command: {command[:100]}...[/green]")
            
            # Check if it has the bypass permissions flag
            if "--dangerously-skip-permissions" in command:
                console.print("[green]✅ Command includes --dangerously-skip-permissions flag[/green]")
            else:
                console.print("[red]❌ Command missing --dangerously-skip-permissions flag[/red]")
                
        except Exception as e:
            console.print(f"[red]❌ Command generation failed: {e}[/red]")
            return False
        
        console.print("[bold green]🎉 All tests passed! The executor should now work properly.[/bold green]")
        return True
        
    except Exception as e:
        console.print(f"[red]💥 Test failed with error: {e}[/red]")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_fixed_executor())
    sys.exit(0 if success else 1)