#!/usr/bin/env python3
"""
Test Claude Code command to verify it works correctly
"""

import subprocess
import sys
from pathlib import Path
from rich.console import Console

console = Console()


def test_claude_command():
    """Test if Claude Code is available and working"""
    
    console.print("[bold cyan]Testing Claude Code Command[/bold cyan]")
    
    try:
        # Test basic claude command
        console.print("\n[cyan]Testing basic claude command...[/cyan]")
        
        if sys.platform == "win32":
            # Test WSL and claude command
            result = subprocess.run([
                "wsl", "-d", "Ubuntu", "-e", "bash", "-c", "claude --version"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                console.print(f"[green]✅ Claude Code is available[/green]")
                console.print(f"[dim]Version: {result.stdout.strip()}[/dim]")
            else:
                console.print(f"[red]❌ Claude Code not available[/red]")
                console.print(f"[red]Error: {result.stderr}[/red]")
                return False
                
        else:
            # Test on Unix systems
            result = subprocess.run(["claude", "--version"], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                console.print(f"[green]✅ Claude Code is available[/green]")
                console.print(f"[dim]Version: {result.stdout.strip()}[/dim]")
            else:
                console.print(f"[red]❌ Claude Code not available[/red]")
                console.print(f"[red]Error: {result.stderr}[/red]")
                return False
        
        # Test help command
        console.print("\n[cyan]Testing claude help command...[/cyan]")
        
        if sys.platform == "win32":
            result = subprocess.run([
                "wsl", "-d", "Ubuntu", "-e", "bash", "-c", "claude --help"
            ], capture_output=True, text=True, timeout=10)
        else:
            result = subprocess.run(["claude", "--help"], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            console.print("[green]✅ Claude Code help command works[/green]")
            
            # Check for -p option
            if "-p" in result.stdout or "--prompt" in result.stdout:
                console.print("[green]✅ Claude Code supports -p/--prompt option[/green]")
            else:
                console.print("[yellow]⚠️  -p/--prompt option not found in help[/yellow]")
                console.print("[dim]Available options:[/dim]")
                console.print(result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout)
        else:
            console.print(f"[red]❌ Claude Code help command failed[/red]")
            console.print(f"[red]Error: {result.stderr}[/red]")
            return False
        
        # Test working directory
        console.print("\n[cyan]Testing working directory access...[/cyan]")
        
        project_root = "/mnt/d/Repository/@Clients/FY.WB.Midway"
        
        if sys.platform == "win32":
            result = subprocess.run([
                "wsl", "-d", "Ubuntu", "-e", "bash", "-c", f"ls -la {project_root}"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                console.print(f"[green]✅ Can access project directory: {project_root}[/green]")
            else:
                console.print(f"[red]❌ Cannot access project directory: {project_root}[/red]")
                console.print(f"[red]Error: {result.stderr}[/red]")
                return False
        
        console.print("\n[bold green]🎉 All Claude Code tests passed![/bold green]")
        return True
        
    except subprocess.TimeoutExpired:
        console.print("[red]❌ Command timed out[/red]")
        return False
    except Exception as e:
        console.print(f"[red]❌ Error testing Claude Code: {e}[/red]")
        return False


def show_manual_commands():
    """Show manual commands for testing Claude Code"""
    
    console.print("\n[bold yellow]Manual Testing Commands[/bold yellow]")
    console.print("\nYou can manually test Claude Code with these commands:")
    
    if sys.platform == "win32":
        console.print("\n[cyan]In Windows Command Prompt or PowerShell:[/cyan]")
        console.print("wsl -d Ubuntu")
        console.print("claude --version")
        console.print("claude --help")
        console.print("cd /mnt/d/Repository/@Clients/FY.WB.Midway")
        console.print("ls -la FrontEnd/src/pages/")
    else:
        console.print("\n[cyan]In Terminal:[/cyan]")
        console.print("claude --version")
        console.print("claude --help")
        console.print("cd /path/to/FY.WB.Midway")
        console.print("ls -la FrontEnd/src/pages/")
    
    console.print("\n[yellow]If Claude Code is not installed:[/yellow]")
    console.print("1. Install Node.js in WSL Ubuntu (if on Windows)")
    console.print("2. Install Claude Code: npm install -g @anthropic/claude-cli")
    console.print("3. Configure your Anthropic API key")


def main():
    """Main test function"""
    
    console.print("[bold]Claude Code Command Test[/bold]")
    console.print("This will test if Claude Code is properly installed and accessible.\n")
    
    success = test_claude_command()
    
    if success:
        console.print("\n[bold green]✅ Claude Code is ready to use![/bold green]")
        console.print("[green]You can now run the Frontend Testing System (options 20-22)[/green]")
    else:
        console.print("\n[bold red]❌ Claude Code setup issues detected![/bold red]")
        console.print("[yellow]Please fix the issues above before using the Frontend Testing System[/yellow]")
        show_manual_commands()
    
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
