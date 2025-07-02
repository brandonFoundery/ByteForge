#!/usr/bin/env python3
"""
Simple script to run Claude Code generation and monitor output
"""
import asyncio
from pathlib import Path
from claude_code_executor import ClaudeCodeExecutor
from rich.console import Console

console = Console()

async def run_all_agents():
    """Run all available agents for phase 1"""
    console.print("[bold blue]🚀 Starting Claude Code Generation for All Agents[/bold blue]")
    
    try:
        # Initialize executor
        base_path = Path(".")
        executor = ClaudeCodeExecutor(base_path)
        
        console.print(f"[cyan]📂 Code output directory: {base_path / 'project' / 'code'}[/cyan]")
        console.print(f"[cyan]📝 Logs directory: {base_path / 'logs'}[/cyan]")
        
        # Get available agents
        available_agents = executor._get_available_agents("phase1")
        console.print(f"[green]📋 Available agents: {available_agents}[/green]")
        
        if not available_agents:
            console.print("[red]❌ No agents available for execution[/red]")
            return False
        
        results = []
        
        # Execute all available agents
        for agent_id in available_agents:
            # Find agent config
            agent = None
            for key, agent_config in executor.agents.items():
                if agent_config["id"] == agent_id:
                    agent = agent_config
                    break
            
            if not agent:
                console.print(f"[red]❌ Agent config not found for {agent_id}[/red]")
                continue
            
            console.print(f"\n[bold cyan]🤖 Executing: {agent['name']}[/bold cyan]")
            
            # Execute the agent
            result = await executor._execute_single_agent(agent, "phase1")
            results.append(result)
            
            if result.success:
                console.print(f"[bold green]✅ {agent['name']} completed in {result.execution_time:.2f}s[/bold green]")
                
                # Check what files were generated
                code_path = base_path / "project" / "code"
                if code_path.exists():
                    # Look for new files in the agent's directory
                    agent_dir = code_path / agent_id
                    if agent_dir.exists():
                        generated_files = list(agent_dir.rglob("*"))
                        console.print(f"[cyan]  📁 Files in {agent_id}/: {len([f for f in generated_files if f.is_file()])}[/cyan]")
                        for file in generated_files[:5]:  # Show first 5 files
                            if file.is_file():
                                size = file.stat().st_size
                                console.print(f"    📄 {file.name} ({size} bytes)")
            else:
                console.print(f"[bold red]❌ {agent['name']} failed: {result.error_message}[/bold red]")
        
        # Summary
        successful = len([r for r in results if r.success])
        total = len(results)
        
        console.print(f"\n[bold]📊 Execution Summary:[/bold]")
        console.print(f"[green]✅ Successful: {successful}/{total}[/green]")
        console.print(f"[red]❌ Failed: {total - successful}/{total}[/red]")
        
        # Check final state of project/code directory
        code_path = base_path / "project" / "code"
        if code_path.exists():
            all_files = list(code_path.rglob("*"))
            code_files = [f for f in all_files if f.is_file() and f.suffix in ['.cs', '.js', '.tsx', '.json', '.csproj', '.sln', '.yaml', '.tf']]
            console.print(f"\n[bold cyan]📁 Generated Code Files: {len(code_files)}[/bold cyan]")
            for file in code_files[:10]:  # Show first 10 code files
                rel_path = file.relative_to(code_path)
                size = file.stat().st_size
                console.print(f"  📄 {rel_path} ({size} bytes)")
        
        return successful > 0
        
    except Exception as e:
        console.print(f"[red]💥 Execution failed: {e}[/red]")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    console.print("[bold]🎯 Claude Code Generation System[/bold]")
    console.print("[dim]This will execute all available agents and generate code in project/code/[/dim]\n")
    
    success = asyncio.run(run_all_agents())
    
    if success:
        console.print("\n[bold green]🎉 Code generation completed![/bold green]")
        console.print("[cyan]Check project/code/ for generated files[/cyan]")
    else:
        console.print("\n[bold red]❌ Code generation failed![/bold red]")