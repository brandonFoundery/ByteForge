#!/usr/bin/env python3
"""
Simple Claude Code launcher in separate terminal
"""

import subprocess
import time
from pathlib import Path
from rich.console import Console

console = Console()


def create_simple_monitoring_script():
    """Create a simple monitoring script without Unicode issues"""
    
    base_path = Path("project")
    logs_path = base_path / "logs"
    
    # Ensure logs directory exists
    logs_path.mkdir(parents=True, exist_ok=True)
    
    # Convert paths to WSL format
    wsl_base_path = str(base_path).replace("\\", "/").replace("D:", "/mnt/d")
    wsl_log_file = str(logs_path / "claude_terminal_execution.log").replace("\\", "/").replace("D:", "/mnt/d")
    
    # Create a specific implementation prompt
    implementation_prompt = """I need you to implement specific Frontend components for the FY.WB.Midway project.

CONTEXT:
- Review the design document: generated_documents/design/frontend-agent-design.md
- The FrontEnd directory already exists with a Next.js project
- Focus on creating NEW components in the existing structure

SPECIFIC TASKS:
1. Create a new authentication component: FrontEnd/src/components/Auth/LoginForm.tsx
2. Create a load management component: FrontEnd/src/components/LoadManagement/LoadList.tsx
3. Create a dashboard component: FrontEnd/src/components/Dashboard/DashboardLayout.tsx
4. Update the main page to use these components: FrontEnd/src/pages/index.tsx

REQUIREMENTS:
- Use TypeScript and React
- Follow the existing project structure
- Add proper imports and exports
- Include basic styling with Tailwind CSS
- Make components functional with proper props

Please create these specific files and show me their contents. Start with the LoginForm component.
"""
    
    # Create the monitoring script (ASCII only)
    monitoring_script = f"""#!/bin/bash
set -e

echo "=========================================="
echo "Claude Code Implementation Monitor"
echo "=========================================="
echo "Starting at: $(date)"
echo "Project: FY.WB.Midway Frontend Agent"
echo "Log file: {wsl_log_file}"
echo "=========================================="
echo ""

# Log start time
echo "Starting Claude Code execution at $(date)" >> {wsl_log_file}
echo "Implementation prompt: Frontend Agent - Specific Components" >> {wsl_log_file}
echo "========================================" >> {wsl_log_file}

# Change to project directory
cd {wsl_base_path}

echo "Current directory: $(pwd)"
echo "Current branch: $(git branch --show-current)"
echo ""

echo "Launching Claude Code..."
echo "This may take several minutes..."
echo ""

# Execute Claude Code with specific implementation
claude --model sonnet --dangerously-skip-permissions -p "{implementation_prompt}" 2>&1 | tee -a {wsl_log_file}

# Check if execution was successful
CLAUDE_EXIT_CODE=${{PIPESTATUS[0]}}

echo ""
echo "=========================================="
if [ $CLAUDE_EXIT_CODE -eq 0 ]; then
    echo "Claude Code execution completed successfully!"
    echo "Claude Code execution completed successfully at $(date)" >> {wsl_log_file}
    
    # Show what was created
    echo ""
    echo "Checking for new files in FrontEnd/src/components:"
    if [ -d "FrontEnd/src/components" ]; then
        find FrontEnd/src/components -name "*.tsx" -newer {wsl_log_file} 2>/dev/null || echo "No new .tsx files found"
    fi
    
    echo ""
    echo "Checking FrontEnd/src/pages/index.tsx:"
    if [ -f "FrontEnd/src/pages/index.tsx" ]; then
        echo "File exists - checking if modified:"
        ls -la FrontEnd/src/pages/index.tsx
    fi
    
    # Try to extract branch name
    BRANCH_NAME=$(git branch --show-current 2>/dev/null || echo "unknown")
    echo "Current branch: $BRANCH_NAME"
    
    echo "SUCCESS:$BRANCH_NAME" >> {wsl_log_file}
else
    echo "Claude Code execution failed with exit code $CLAUDE_EXIT_CODE"
    echo "Claude Code execution failed at $(date) with exit code $CLAUDE_EXIT_CODE" >> {wsl_log_file}
    echo "FAILED:Exit code $CLAUDE_EXIT_CODE" >> {wsl_log_file}
fi

echo "=========================================="
echo "Execution completed at: $(date)"
echo "Full log available at: {wsl_log_file}"
echo "=========================================="

# Keep terminal open
echo ""
echo "Press Enter to close this terminal..."
read
"""
    
    # Write the monitoring script with UTF-8 encoding
    script_file = logs_path / "claude_monitor_simple.sh"
    with open(script_file, 'w', encoding='utf-8', newline='\n') as f:
        f.write(monitoring_script)
    
    return script_file


def launch_in_new_terminal():
    """Launch Claude Code in a new terminal"""
    
    console.print("[blue]Creating monitoring script...[/blue]")
    script_file = create_simple_monitoring_script()
    console.print(f"[green]Created: {script_file}[/green]")
    
    # Convert script path to WSL
    wsl_script_path = str(script_file).replace("\\", "/").replace("D:", "/mnt/d")
    
    try:
        console.print("[yellow]Launching new terminal window...[/yellow]")
        
        # Try Windows Terminal first
        try:
            subprocess.Popen([
                "wt", "new-tab", "--title", "Claude Code Monitor", 
                "wsl", "-d", "Ubuntu", "-e", "bash", "-c", 
                f"chmod +x {wsl_script_path} && {wsl_script_path}"
            ])
            console.print("[green]Launched in Windows Terminal[/green]")
        except FileNotFoundError:
            # Fall back to cmd
            subprocess.Popen([
                "cmd", "/c", "start", "cmd", "/k", 
                f"wsl -d Ubuntu -e bash -c \"chmod +x {wsl_script_path} && {wsl_script_path}\""
            ])
            console.print("[green]Launched in Command Prompt[/green]")
        
        console.print("\n[cyan]A new terminal window should have opened![/cyan]")
        console.print("[cyan]You can watch Claude Code create specific components.[/cyan]")
        
        return True
        
    except Exception as e:
        console.print(f"[red]Failed to launch: {e}[/red]")
        console.print(f"[yellow]Manual command:[/yellow]")
        console.print(f"[dim]wsl -d Ubuntu -e bash -c \"chmod +x {wsl_script_path} && {wsl_script_path}\"[/dim]")
        return False


def analyze_existing_structure():
    """Analyze the existing project structure"""
    
    console.print("\n[bold]Analyzing existing project structure...[/bold]")
    
    base_path = Path("project")
    frontend_path = base_path / "FrontEnd"
    
    if frontend_path.exists():
        console.print(f"[green]FrontEnd directory exists[/green]")
        
        # Check for src directory
        src_path = frontend_path / "src"
        if src_path.exists():
            console.print(f"[green]src directory exists[/green]")
            
            # Check for components
            components_path = src_path / "components"
            if components_path.exists():
                console.print(f"[green]components directory exists[/green]")
                existing_components = list(components_path.rglob("*.tsx"))
                console.print(f"[blue]Found {len(existing_components)} existing .tsx components[/blue]")
            else:
                console.print(f"[yellow]components directory does not exist - will be created[/yellow]")
            
            # Check for pages
            pages_path = src_path / "pages"
            if pages_path.exists():
                console.print(f"[green]pages directory exists[/green]")
                index_file = pages_path / "index.tsx"
                if index_file.exists():
                    console.print(f"[green]index.tsx exists[/green]")
                else:
                    console.print(f"[yellow]index.tsx does not exist[/yellow]")
            else:
                console.print(f"[yellow]pages directory does not exist[/yellow]")
        else:
            console.print(f"[yellow]src directory does not exist[/yellow]")
    
    # Check package.json for dependencies
    package_json = frontend_path / "package.json"
    if package_json.exists():
        console.print(f"[green]package.json exists[/green]")
        try:
            import json
            with open(package_json, 'r') as f:
                package_data = json.load(f)
            
            if 'dependencies' in package_data:
                deps = package_data['dependencies']
                has_react = 'react' in deps
                has_next = 'next' in deps
                has_typescript = '@types/react' in deps or 'typescript' in deps
                has_tailwind = 'tailwindcss' in deps
                
                console.print(f"[blue]React: {'✅' if has_react else '❌'}[/blue]")
                console.print(f"[blue]Next.js: {'✅' if has_next else '❌'}[/blue]")
                console.print(f"[blue]TypeScript: {'✅' if has_typescript else '❌'}[/blue]")
                console.print(f"[blue]Tailwind: {'✅' if has_tailwind else '❌'}[/blue]")
        except Exception as e:
            console.print(f"[red]Could not read package.json: {e}[/red]")


def main():
    """Main function"""
    
    console.print("[bold blue]Claude Code Terminal Launcher (Simple)[/bold blue]")
    
    # Analyze existing structure
    analyze_existing_structure()
    
    console.print("\n[bold]Ready to launch Claude Code in separate terminal?[/bold]")
    console.print("[yellow]This will create specific React components in the existing FrontEnd project.[/yellow]")
    
    proceed = input("\nProceed? [y/n]: ").strip().lower()
    
    if proceed == 'y':
        success = launch_in_new_terminal()
        if success:
            console.print("\n[green]Claude Code is now running in a separate terminal![/green]")
            console.print("[cyan]Watch the terminal to see components being created.[/cyan]")
            
            # Monitor the log file
            console.print("\n[yellow]Monitoring log file for updates...[/yellow]")
            log_file = Path("project/logs/claude_terminal_execution.log")
            
            for i in range(30):  # Monitor for 30 seconds
                if log_file.exists():
                    try:
                        with open(log_file, 'r') as f:
                            content = f.read()
                        if "SUCCESS:" in content or "FAILED:" in content:
                            console.print("[green]Execution completed! Check the terminal window.[/green]")
                            break
                    except:
                        pass
                
                time.sleep(1)
                if i % 5 == 0:
                    console.print(f"[dim]Monitoring... ({i}s)[/dim]")
        else:
            console.print("[red]Failed to launch terminal[/red]")
    else:
        console.print("[yellow]Cancelled[/yellow]")


if __name__ == "__main__":
    main()
