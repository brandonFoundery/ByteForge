#!/usr/bin/env python3
"""
Watch Claude Code execution in a visible terminal
"""

import subprocess
import time
from pathlib import Path
from rich.console import Console

console = Console()


def create_visible_claude_terminal():
    """Create a new, visible terminal to watch Claude Code"""
    
    console.print("[bold blue]🔍 Creating Visible Claude Code Terminal[/bold blue]")
    
    base_path = Path.cwd().parent.parent.parent.parent  # Navigate up to get the project base path
    logs_path = base_path / "logs"
    
    # Convert paths to WSL format
    wsl_base_path = str(base_path).replace("\\", "/").replace("D:", "/mnt/d")
    wsl_log_file = str(logs_path / "visible_claude_execution.log").replace("\\", "/").replace("D:", "/mnt/d")
    
    # Create a monitoring script that shows real-time progress
    monitoring_script = f"""#!/bin/bash
clear
echo "=========================================="
echo "🚀 Claude Code Live Monitor"
echo "=========================================="
echo "Project: FY.WB.Midway Frontend Components"
echo "Time: $(date)"
echo "Log: {wsl_log_file}"
echo "=========================================="
echo ""

# Change to project directory
cd {wsl_base_path}

echo "📁 Current directory: $(pwd)"
echo "🌿 Current branch: $(git branch --show-current)"
echo ""

echo "🤖 Starting Claude Code with component creation..."
echo "⏱️  This will create React components step by step..."
echo ""

# Create log file
echo "Starting visible Claude Code execution at $(date)" > {wsl_log_file}

# Execute Claude Code with detailed component creation
claude --model sonnet --dangerously-skip-permissions -p "I need you to create React components for the FY.WB.Midway project. Please create these components one by one, showing your progress:

1. Create FrontEnd/src/components/Dashboard/DashboardLayout.tsx - A main dashboard layout
2. Create FrontEnd/src/components/Auth/RegisterForm.tsx - User registration form  
3. Create FrontEnd/src/components/LoadManagement/LoadForm.tsx - Form for creating new loads
4. Create FrontEnd/src/components/LoadManagement/LoadDetail.tsx - Detailed load view
5. Update FrontEnd/src/pages/index.tsx to use these components

For each component:
- Use TypeScript and React
- Include proper interfaces and types
- Add Tailwind CSS styling
- Include error handling and validation
- Show me the file path and a brief description when you create each one

Please work through these systematically and tell me when each component is complete." 2>&1 | tee -a {wsl_log_file}

# Check result
CLAUDE_EXIT_CODE=${{PIPESTATUS[0]}}

echo ""
echo "=========================================="
if [ $CLAUDE_EXIT_CODE -eq 0 ]; then
    echo "✅ Claude Code completed successfully!"
    echo ""
    echo "📁 Checking created files:"
    find FrontEnd/src/components -name "*.tsx" -newer {wsl_log_file} 2>/dev/null | head -10
    echo ""
    echo "🌿 Current branch: $(git branch --show-current)"
else
    echo "❌ Claude Code failed with exit code $CLAUDE_EXIT_CODE"
fi

echo "=========================================="
echo "📊 Execution completed at: $(date)"
echo "📄 Full log: {wsl_log_file}"
echo ""
echo "Press Enter to close..."
read
"""
    
    # Write the script
    script_file = logs_path / "visible_claude_monitor.sh"
    with open(script_file, 'w', encoding='utf-8', newline='\n') as f:
        f.write(monitoring_script)
    
    console.print(f"[green]✅ Created monitoring script: {script_file}[/green]")
    
    # Convert to WSL path
    wsl_script_path = str(script_file).replace("\\", "/").replace("D:", "/mnt/d")
    
    try:
        console.print("[yellow]🚀 Opening new visible terminal window...[/yellow]")
        
        # Try multiple methods to ensure visibility
        methods = [
            # Method 1: Windows Terminal with explicit window
            ["wt", "-w", "new", "new-tab", "--title", "Claude Code Live Monitor", 
             "wsl", "-d", "Ubuntu", "-e", "bash", "-c", 
             f"chmod +x {wsl_script_path} && {wsl_script_path}"],
            
            # Method 2: Start a new cmd window
            ["cmd", "/c", "start", "cmd", "/k", 
             f'title Claude Code Live Monitor && wsl -d Ubuntu -e bash -c "chmod +x {wsl_script_path} && {wsl_script_path}"'],
            
            # Method 3: PowerShell window
            ["powershell", "-Command", 
             f"Start-Process cmd -ArgumentList '/k title Claude Code Live Monitor && wsl -d Ubuntu -e bash -c \"chmod +x {wsl_script_path} && {wsl_script_path}\"'"]
        ]
        
        success = False
        for i, method in enumerate(methods, 1):
            try:
                console.print(f"[dim]Trying method {i}...[/dim]")
                subprocess.Popen(method)
                console.print(f"[green]✅ Method {i} launched successfully![/green]")
                success = True
                break
            except Exception as e:
                console.print(f"[yellow]⚠️  Method {i} failed: {e}[/yellow]")
                continue
        
        if success:
            console.print("\n[green]🎉 New terminal window should be visible![/green]")
            console.print("[cyan]Look for a window titled 'Claude Code Live Monitor'[/cyan]")
            console.print("[cyan]It will show Claude Code creating components in real-time[/cyan]")
        else:
            console.print("\n[red]❌ Could not open visible terminal[/red]")
            console.print("[yellow]💡 Manual command to run in any terminal:[/yellow]")
            console.print(f"[dim]wsl -d Ubuntu -e bash -c \"chmod +x {wsl_script_path} && {wsl_script_path}\"[/dim]")
        
        return success
        
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        return False


def show_current_files():
    """Show what files have been created so far"""
    
    console.print("\n[bold]📁 Files Created So Far:[/bold]")
    
    base_path = Path.cwd().parent.parent.parent.parent  # Navigate up to get the project base path
    components_path = base_path / "FrontEnd" / "src" / "components"
    
    if components_path.exists():
        # Find all .tsx files
        tsx_files = list(components_path.rglob("*.tsx"))
        
        if tsx_files:
            console.print(f"[green]Found {len(tsx_files)} React components:[/green]")
            for file in sorted(tsx_files):
                rel_path = file.relative_to(components_path)
                size = file.stat().st_size
                size_kb = size / 1024
                console.print(f"  • {rel_path} ({size_kb:.1f} KB)")
        else:
            console.print("[yellow]No .tsx files found yet[/yellow]")
    else:
        console.print("[red]Components directory not found[/red]")


def main():
    """Main function"""
    
    console.print("[bold blue]🔍 Claude Code Terminal Viewer[/bold blue]")
    
    # Show current status
    show_current_files()
    
    console.print("\n[bold]What would you like to do?[/bold]")
    console.print("1. 🚀 Open new visible Claude Code terminal")
    console.print("2. 📁 Just show current files")
    console.print("3. 📊 Show file monitoring in this terminal")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        success = create_visible_claude_terminal()
        if success:
            console.print("\n[green]🎉 Watch the new terminal window for live progress![/green]")
        
    elif choice == "2":
        show_current_files()
        
    elif choice == "3":
        console.print("\n[yellow]Starting file monitoring in this terminal...[/yellow]")
        console.print("[dim]Press Ctrl+C to stop[/dim]")
        
        # Simple file monitoring loop
        try:
            last_count = 0
            while True:
                components_path = Path("project/FrontEnd/src/components")
                if components_path.exists():
                    tsx_files = list(components_path.rglob("*.tsx"))
                    if len(tsx_files) != last_count:
                        console.print(f"[green]📄 Found {len(tsx_files)} components (+{len(tsx_files) - last_count})[/green]")
                        last_count = len(tsx_files)
                
                time.sleep(2)
        except KeyboardInterrupt:
            console.print("\n[yellow]Monitoring stopped[/yellow]")
    
    else:
        console.print("[red]Invalid choice[/red]")


if __name__ == "__main__":
    main()
