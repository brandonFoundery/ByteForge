#!/usr/bin/env python3
"""
Debug Claude Code Execution
"""

import asyncio
import subprocess
from pathlib import Path
from rich.console import Console

console = Console()


async def debug_claude_execution():
    """Debug the Claude Code execution issue"""
    
    console.print("[bold blue]🔍 Debugging Claude Code Execution[/bold blue]")
    
    base_path = Path("project")
    logs_path = base_path / "logs"
    
    # Ensure logs directory exists
    logs_path.mkdir(parents=True, exist_ok=True)
    
    # Convert paths to WSL format
    wsl_base_path = str(base_path).replace("\\", "/").replace("D:", "/mnt/d")
    wsl_log_file = str(logs_path / "debug_claude_execution.log").replace("\\", "/").replace("D:", "/mnt/d")
    
    console.print(f"[cyan]Base path (Windows): {base_path}[/cyan]")
    console.print(f"[cyan]Base path (WSL): {wsl_base_path}[/cyan]")
    console.print(f"[cyan]Log file (WSL): {wsl_log_file}[/cyan]")
    
    # Create a simple test prompt
    prompt = "Just say hello and confirm you can see the project files. Do not create any files."
    
    # Test 1: Direct Claude Code execution
    console.print("\n[bold]Test 1: Direct Claude Code execution[/bold]")
    
    try:
        command = f'cd {wsl_base_path} && claude --model sonnet --dangerously-skip-permissions -p "{prompt}"'
        console.print(f"[dim]Command: {command}[/dim]")
        
        result = subprocess.run([
            "wsl", "-d", "Ubuntu", "-e", "bash", "-c", command
        ], capture_output=True, text=True, timeout=60)
        
        console.print(f"[green]✅ Exit code: {result.returncode}[/green]")
        if result.stdout:
            console.print(f"[green]Output: {result.stdout[:200]}...[/green]")
        if result.stderr:
            console.print(f"[red]Error: {result.stderr}[/red]")
            
    except Exception as e:
        console.print(f"[red]❌ Test 1 failed: {e}[/red]")
    
    # Test 2: Wrapper script execution
    console.print("\n[bold]Test 2: Wrapper script execution[/bold]")
    
    try:
        # Create a simple wrapper script
        wrapper_script = f"""#!/bin/bash
set -e

echo "Starting debug execution at $(date)" >> {wsl_log_file}

cd {wsl_base_path}
claude --model sonnet --dangerously-skip-permissions -p "{prompt}" 2>&1 | tee -a {wsl_log_file}

CLAUDE_EXIT_CODE=$?
echo "Claude exit code: $CLAUDE_EXIT_CODE" >> {wsl_log_file}

if [ $CLAUDE_EXIT_CODE -eq 0 ]; then
    echo "SUCCESS" >> {wsl_log_file}
else
    echo "FAILED:Exit code $CLAUDE_EXIT_CODE" >> {wsl_log_file}
fi

exit $CLAUDE_EXIT_CODE
"""
        
        # Write wrapper script
        script_file = logs_path / "debug_wrapper.sh"
        with open(script_file, 'w') as f:
            f.write(wrapper_script)
        
        # Convert script path to WSL
        wsl_script_path = str(script_file).replace("\\", "/").replace("D:", "/mnt/d")
        
        console.print(f"[dim]Script path (WSL): {wsl_script_path}[/dim]")
        
        # Execute wrapper script
        result = subprocess.run([
            "wsl", "-d", "Ubuntu", "-e", "bash", "-c", 
            f"chmod +x {wsl_script_path} && {wsl_script_path}"
        ], capture_output=True, text=True, timeout=60)
        
        console.print(f"[green]✅ Wrapper exit code: {result.returncode}[/green]")
        if result.stdout:
            console.print(f"[green]Wrapper output: {result.stdout[:200]}...[/green]")
        if result.stderr:
            console.print(f"[red]Wrapper error: {result.stderr}[/red]")
        
        # Check log file
        log_file_windows = Path(wsl_log_file.replace("/mnt/d", "D:").replace("/", "\\"))
        if log_file_windows.exists():
            with open(log_file_windows, 'r') as f:
                log_content = f.read()
            console.print(f"[blue]Log content: {log_content}[/blue]")
        else:
            console.print(f"[yellow]⚠️  Log file not found: {log_file_windows}[/yellow]")
            
    except Exception as e:
        console.print(f"[red]❌ Test 2 failed: {e}[/red]")
    
    # Test 3: Async subprocess execution (like our real code)
    console.print("\n[bold]Test 3: Async subprocess execution[/bold]")
    
    try:
        # Create async wrapper script
        async_script = f"""#!/bin/bash
set -e

echo "Starting async execution at $(date)" >> {wsl_log_file}

cd {wsl_base_path}
claude --model sonnet --dangerously-skip-permissions -p "{prompt}" 2>&1 | tee -a {wsl_log_file}

CLAUDE_EXIT_CODE=$?
echo "Async Claude exit code: $CLAUDE_EXIT_CODE" >> {wsl_log_file}

if [ $CLAUDE_EXIT_CODE -eq 0 ]; then
    echo "ASYNC_SUCCESS" >> {wsl_log_file}
else
    echo "ASYNC_FAILED:Exit code $CLAUDE_EXIT_CODE" >> {wsl_log_file}
fi

exit $CLAUDE_EXIT_CODE
"""
        
        # Write async script
        async_script_file = logs_path / "debug_async_wrapper.sh"
        with open(async_script_file, 'w') as f:
            f.write(async_script)
        
        # Convert script path to WSL
        wsl_async_script_path = str(async_script_file).replace("\\", "/").replace("D:", "/mnt/d")
        
        # Execute with asyncio (like our real code)
        process = await asyncio.create_subprocess_shell(
            f'wsl -d Ubuntu -e bash -c "chmod +x {wsl_async_script_path} && {wsl_async_script_path}"',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        console.print(f"[green]✅ Async exit code: {process.returncode}[/green]")
        if stdout:
            console.print(f"[green]Async output: {stdout.decode()[:200]}...[/green]")
        if stderr:
            console.print(f"[red]Async error: {stderr.decode()}[/red]")
        
        # Check log file again
        log_file_windows = Path(wsl_log_file.replace("/mnt/d", "D:").replace("/", "\\"))
        if log_file_windows.exists():
            with open(log_file_windows, 'r') as f:
                log_content = f.read()
            console.print(f"[blue]Final log content: {log_content[-500:]}[/blue]")
            
    except Exception as e:
        console.print(f"[red]❌ Test 3 failed: {e}[/red]")
    
    console.print("\n[bold green]🔍 Debug completed![/bold green]")


if __name__ == "__main__":
    asyncio.run(debug_claude_execution())
