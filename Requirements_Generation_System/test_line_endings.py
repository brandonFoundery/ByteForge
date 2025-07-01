#!/usr/bin/env python3
"""
Test line endings fix
"""

import subprocess
from pathlib import Path
from rich.console import Console

console = Console()


def test_line_endings():
    """Test that we can create and execute shell scripts with proper line endings"""
    
    console.print("[bold blue]🔍 Testing Line Endings Fix[/bold blue]")
    
    base_path = Path("project")
    logs_path = base_path / "logs"
    
    # Ensure logs directory exists
    logs_path.mkdir(parents=True, exist_ok=True)
    
    # Convert paths to WSL format
    wsl_base_path = str(base_path).replace("\\", "/").replace("D:", "/mnt/d")
    wsl_log_file = str(logs_path / "test_line_endings.log").replace("\\", "/").replace("D:", "/mnt/d")
    
    # Create a test script with proper Unix line endings
    test_script = f"""#!/bin/bash
set -e

echo "Testing line endings fix at $(date)" >> {wsl_log_file}

cd {wsl_base_path}
claude --model sonnet --dangerously-skip-permissions -p "Just say hello briefly. Do not create files." 2>&1 | tee -a {wsl_log_file}

CLAUDE_EXIT_CODE=$?
echo "Claude exit code: $CLAUDE_EXIT_CODE" >> {wsl_log_file}

if [ $CLAUDE_EXIT_CODE -eq 0 ]; then
    echo "SUCCESS" >> {wsl_log_file}
else
    echo "FAILED:Exit code $CLAUDE_EXIT_CODE" >> {wsl_log_file}
fi

exit $CLAUDE_EXIT_CODE
"""
    
    # Write script with Unix line endings (newline='\n')
    script_file = logs_path / "test_line_endings.sh"
    with open(script_file, 'w', newline='\n') as f:
        f.write(test_script)
    
    console.print(f"[cyan]Created script: {script_file}[/cyan]")
    
    # Convert script path to WSL
    wsl_script_path = str(script_file).replace("\\", "/").replace("D:", "/mnt/d")
    
    try:
        # Execute the script
        console.print("[yellow]Executing script...[/yellow]")
        
        result = subprocess.run([
            "wsl", "-d", "Ubuntu", "-e", "bash", "-c", 
            f"chmod +x {wsl_script_path} && {wsl_script_path}"
        ], capture_output=True, text=True, timeout=120)
        
        console.print(f"[green]✅ Script exit code: {result.returncode}[/green]")
        
        if result.returncode == 0:
            console.print("[green]🎉 Line endings fix successful![/green]")
        else:
            console.print(f"[red]❌ Script failed with exit code: {result.returncode}[/red]")
        
        if result.stdout:
            console.print(f"[blue]Output: {result.stdout[:300]}...[/blue]")
        if result.stderr:
            console.print(f"[red]Error: {result.stderr}[/red]")
        
        # Check log file
        log_file_windows = Path(wsl_log_file.replace("/mnt/d", "D:").replace("/", "\\"))
        if log_file_windows.exists():
            with open(log_file_windows, 'r') as f:
                log_content = f.read()
            console.print(f"[blue]Log content: {log_content}[/blue]")
        else:
            console.print(f"[yellow]⚠️  Log file not found: {log_file_windows}[/yellow]")
            
    except Exception as e:
        console.print(f"[red]❌ Test failed: {e}[/red]")


if __name__ == "__main__":
    test_line_endings()
