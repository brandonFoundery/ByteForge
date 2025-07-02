#!/usr/bin/env python3
"""
Run all Claude Code agents for Phase 1 MVP implementation
"""

import asyncio
import subprocess
import time
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

console = Console()

# Agent execution order based on dependencies
AGENTS = [
    ("backend", "Backend - ASP.NET Core API"),
    ("infrastructure", "Infrastructure - Azure Terraform"),
    ("frontend", "Frontend - Next.js App"),
    ("security", "Security - Auth & Protection"),
    ("integration", "Integration - External APIs")
]

BYTEFORGE_PATH = "/mnt/d/Repository/ContractLogix/LSOMitigator/ByteForge"
INSTRUCTION_PATH = "/mnt/d/Repository/ContractLogix/LSOMitigator/ByteForge/Requirements_Generation_System/project/design/claude_instructions"

async def run_agent(agent_name: str, description: str, progress: Progress, task_id):
    """Run a single Claude Code agent"""
    
    instruction_file = f"{INSTRUCTION_PATH}/{agent_name}-phase1-mvp-core-features.md"
    log_file = f"{BYTEFORGE_PATH}/Requirements_Generation_System/logs/{agent_name}_generation.log"
    
    # Update progress
    progress.update(task_id, description=f"🚀 Starting {description}")
    
    try:
        # Create the command
        cmd = f"""cd "{BYTEFORGE_PATH}" && claude --model sonnet --dangerously-skip-permissions --print "$(cat "{instruction_file}")" > "{log_file}" 2>&1"""
        
        # Run the command
        process = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        progress.update(task_id, description=f"⚙️ Generating {description}")
        
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            progress.update(task_id, description=f"✅ Completed {description}")
            return True, f"Agent {agent_name} completed successfully"
        else:
            progress.update(task_id, description=f"❌ Failed {description}")
            return False, f"Agent {agent_name} failed: {stderr.decode()}"
            
    except Exception as e:
        progress.update(task_id, description=f"❌ Error {description}")
        return False, f"Agent {agent_name} error: {str(e)}"

async def monitor_code_directory():
    """Monitor the code directory for new files"""
    code_dir = Path(f"{BYTEFORGE_PATH}/project/code")
    
    console.print(f"\n📁 Monitoring code directory: {code_dir}")
    
    while True:
        if code_dir.exists():
            files = list(code_dir.rglob("*"))
            file_count = len([f for f in files if f.is_file()])
            dir_count = len([f for f in files if f.is_dir()])
            
            console.print(f"📊 Current status: {file_count} files, {dir_count} directories", end="\r")
        
        await asyncio.sleep(5)

async def main():
    """Run all agents in sequence"""
    
    console.print("🚀 [bold green]LSOMigrator Phase 1 Code Generation[/bold green]")
    console.print("=" * 60)
    console.print(f"📁 Output Directory: {BYTEFORGE_PATH}/project/code")
    console.print(f"📝 Logs Directory: {BYTEFORGE_PATH}/Requirements_Generation_System/logs")
    console.print()
    
    # Create logs directory
    Path(f"{BYTEFORGE_PATH}/Requirements_Generation_System/logs").mkdir(parents=True, exist_ok=True)
    
    results = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        
        # Create tasks for each agent
        tasks = {}
        for agent_name, description in AGENTS:
            task_id = progress.add_task(f"⏸️ Pending {description}", total=1)
            tasks[agent_name] = task_id
        
        # Start monitoring task
        monitor_task = asyncio.create_task(monitor_code_directory())
        
        # Run agents sequentially (to avoid overwhelming the system)
        for agent_name, description in AGENTS:
            task_id = tasks[agent_name]
            
            # Run the agent
            success, message = await run_agent(agent_name, description, progress, task_id)
            results.append((agent_name, success, message))
            
            # Mark as complete
            progress.update(task_id, completed=1)
            
            # Wait a bit between agents
            await asyncio.sleep(2)
        
        # Cancel monitoring
        monitor_task.cancel()
    
    # Show final results
    console.print("\n" + "=" * 60)
    console.print("🎯 [bold]FINAL RESULTS[/bold]")
    console.print("=" * 60)
    
    successful = 0
    for agent_name, success, message in results:
        status = "✅" if success else "❌"
        console.print(f"{status} {agent_name.upper()}: {message}")
        if success:
            successful += 1
    
    console.print(f"\n📊 Summary: {successful}/{len(AGENTS)} agents completed successfully")
    
    # Show code directory contents
    code_dir = Path(f"{BYTEFORGE_PATH}/project/code")
    if code_dir.exists():
        console.print(f"\n📁 Generated files in {code_dir}:")
        for file_path in sorted(code_dir.rglob("*")):
            if file_path.is_file():
                console.print(f"   📄 {file_path.relative_to(code_dir)}")
    
    console.print(f"\n📝 Check logs in: {BYTEFORGE_PATH}/Requirements_Generation_System/logs/")

if __name__ == "__main__":
    asyncio.run(main())