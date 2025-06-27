#!/usr/bin/env python3
"""
Quick test script for the Frontend Testing System
This script helps diagnose and fix common issues.
"""

import subprocess
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

console = Console()


def check_frontend_server():
    """Check if frontend server is running"""
    console.print("\n[cyan]Checking frontend server status...[/cyan]")
    
    try:
        import requests
        response = requests.get("http://localhost:4001", timeout=5)
        if response.status_code == 200:
            console.print("[green]✅ Frontend server is running on http://localhost:4001[/green]")
            return True
        else:
            console.print(f"[yellow]⚠️  Frontend server responded with status {response.status_code}[/yellow]")
            return False
    except ImportError:
        console.print("[yellow]⚠️  requests library not available, using curl instead[/yellow]")
        try:
            result = subprocess.run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "http://localhost:4001"], 
                                  capture_output=True, text=True, timeout=5)
            if result.stdout.strip() == "200":
                console.print("[green]✅ Frontend server is running on http://localhost:4001[/green]")
                return True
            else:
                console.print(f"[yellow]⚠️  Frontend server status: {result.stdout.strip()}[/yellow]")
                return False
        except Exception:
            console.print("[red]❌ Cannot check frontend server status[/red]")
            return False
    except Exception as e:
        console.print(f"[red]❌ Frontend server not accessible: {e}[/red]")
        return False


def check_claude_code():
    """Check if Claude Code is available"""
    console.print("\n[cyan]Checking Claude Code availability...[/cyan]")
    
    try:
        if sys.platform == "win32":
            result = subprocess.run([
                "wsl", "-d", "Ubuntu", "-e", "bash", "-c", "claude --version"
            ], capture_output=True, text=True, timeout=10)
        else:
            result = subprocess.run(["claude", "--version"], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            console.print("[green]✅ Claude Code is available[/green]")
            return True
        else:
            console.print("[red]❌ Claude Code not available[/red]")
            return False
    except Exception as e:
        console.print(f"[red]❌ Error checking Claude Code: {e}[/red]")
        return False


def check_frontend_structure():
    """Check frontend directory structure"""
    console.print("\n[cyan]Checking frontend directory structure...[/cyan]")
    
    base_path = Path(__file__).parent.parent
    frontend_path = base_path / "FrontEnd"
    
    if not frontend_path.exists():
        console.print(f"[red]❌ Frontend directory not found: {frontend_path}[/red]")
        return False
    
    console.print(f"[green]✅ Frontend directory found: {frontend_path}[/green]")
    
    # Check for pages
    pages_path = frontend_path / "src" / "pages"
    if pages_path.exists():
        page_files = list(pages_path.rglob("*.tsx"))
        console.print(f"[green]✅ Found {len(page_files)} page files[/green]")
    else:
        console.print("[yellow]⚠️  Pages directory not found[/yellow]")
    
    # Check for components
    components_path = frontend_path / "src" / "components"
    if components_path.exists():
        component_files = list(components_path.rglob("*.tsx"))
        console.print(f"[green]✅ Found {len(component_files)} component files[/green]")
    else:
        console.print("[yellow]⚠️  Components directory not found[/yellow]")
    
    return True


def check_output_directories():
    """Check if output directories exist"""
    console.print("\n[cyan]Checking output directories...[/cyan]")
    
    base_path = Path(__file__).parent.parent
    testing_dir = base_path / "generated_documents" / "testing"
    prompts_dir = base_path / "Development_Prompts" / "claude_code_prompts"
    
    if not testing_dir.exists():
        console.print(f"[yellow]⚠️  Testing directory will be created: {testing_dir}[/yellow]")
        testing_dir.mkdir(parents=True, exist_ok=True)
        console.print("[green]✅ Testing directory created[/green]")
    else:
        console.print(f"[green]✅ Testing directory exists: {testing_dir}[/green]")
    
    if not prompts_dir.exists():
        console.print(f"[yellow]⚠️  Prompts directory will be created: {prompts_dir}[/yellow]")
        prompts_dir.mkdir(parents=True, exist_ok=True)
        console.print("[green]✅ Prompts directory created[/green]")
    else:
        console.print(f"[green]✅ Prompts directory exists: {prompts_dir}[/green]")
    
    return True


def start_frontend_server():
    """Help start the frontend server"""
    console.print("\n[cyan]Frontend server startup help...[/cyan]")
    
    base_path = Path(__file__).parent.parent
    frontend_path = base_path / "FrontEnd"
    
    console.print(f"[yellow]To start the frontend server:[/yellow]")
    console.print(f"1. Open a new terminal")
    console.print(f"2. Navigate to: {frontend_path}")
    console.print(f"3. Run: npx next dev -p 4001")
    console.print(f"4. Wait for 'Ready in X.Xs' message")
    console.print(f"5. Verify at: http://localhost:4001")


def install_claude_code():
    """Help install Claude Code"""
    console.print("\n[cyan]Claude Code installation help...[/cyan]")
    
    if sys.platform == "win32":
        console.print("[yellow]For Windows (WSL):[/yellow]")
        console.print("1. Open WSL Ubuntu terminal")
        console.print("2. Install Node.js: curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -")
        console.print("3. Install Node.js: sudo apt-get install -y nodejs")
        console.print("4. Install Claude Code: npm install -g @anthropic/claude-cli")
        console.print("5. Configure API key: claude auth")
    else:
        console.print("[yellow]For Linux/Mac:[/yellow]")
        console.print("1. Install Node.js (if not installed)")
        console.print("2. Install Claude Code: npm install -g @anthropic/claude-cli")
        console.print("3. Configure API key: claude auth")


def main():
    """Main diagnostic function"""
    
    console.print(Panel.fit(
        "[bold]Frontend Testing System - Quick Diagnostic[/bold]\n"
        "This will check if your system is ready for frontend testing",
        style="cyan"
    ))
    
    issues = []
    
    # Check frontend server
    if not check_frontend_server():
        issues.append("frontend_server")
    
    # Check Claude Code
    if not check_claude_code():
        issues.append("claude_code")
    
    # Check frontend structure
    if not check_frontend_structure():
        issues.append("frontend_structure")
    
    # Check output directories
    check_output_directories()
    
    # Summary
    console.print("\n" + "="*60)
    
    if not issues:
        console.print("[bold green]🎉 All checks passed! Your system is ready for frontend testing.[/bold green]")
        console.print("\n[cyan]You can now run:[/cyan]")
        console.print("python run_generation.py")
        console.print("Then select option 20, 21, or 22")
    else:
        console.print("[bold red]❌ Issues found that need to be resolved:[/bold red]")
        
        if "frontend_server" in issues:
            console.print("\n[red]Frontend Server Issue:[/red]")
            start_frontend_server()
        
        if "claude_code" in issues:
            console.print("\n[red]Claude Code Issue:[/red]")
            install_claude_code()
        
        if "frontend_structure" in issues:
            console.print("\n[red]Frontend Structure Issue:[/red]")
            console.print("Ensure the FrontEnd directory exists with src/pages and src/components")
    
    return 0 if not issues else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
