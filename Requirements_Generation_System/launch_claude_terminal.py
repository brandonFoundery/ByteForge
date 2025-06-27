#!/usr/bin/env python3
"""
Launch Claude Code in a separate terminal for monitoring
"""

import subprocess
import time
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

console = Console()


def create_monitoring_script():
    """Create a script that launches Claude Code with real implementation"""
    
    base_path = Path("D:/Repository/@Clients/FY.WB.Midway")
    logs_path = base_path / "logs"
    
    # Ensure logs directory exists
    logs_path.mkdir(parents=True, exist_ok=True)
    
    # Convert paths to WSL format
    wsl_base_path = str(base_path).replace("\\", "/").replace("D:", "/mnt/d")
    wsl_log_file = str(logs_path / "claude_terminal_execution.log").replace("\\", "/").replace("D:", "/mnt/d")
    
    # Create a comprehensive implementation prompt
    implementation_prompt = """I need you to implement the Frontend Agent features for Phase 1 based on the comprehensive design documents in this repository.

CONTEXT:
- Review the design document: generated_documents/design/frontend-agent-design.md
- Use the requirements documents in generated_documents/ for context
- Focus on the FrontEnd directory for implementation

IMPLEMENTATION REQUIREMENTS:
1. Follow the detailed specifications in the frontend-agent-design.md document
2. Use the specified technology stack and architecture patterns (Next.js, React, TypeScript, Tailwind)
3. Create the actual file structure and components as specified
4. Implement proper error handling and logging
5. Add comprehensive tests for all functionality
6. Create a feature branch following the naming convention from the design doc
7. Commit changes with descriptive messages

IMPORTANT: This is a real implementation task. Please create actual, working code files based on the design specifications.

SPECIFIC TASKS FOR PHASE 1:
1. Set up the basic Next.js project structure in FrontEnd/
2. Create authentication components (LoginForm, RegisterForm, AuthGuard)
3. Create load management components (LoadForm, LoadList, LoadDetail)
4. Set up routing and navigation
5. Implement basic styling with Tailwind CSS
6. Create API service layer for backend communication

Start by reading the design document and then implement the features step by step. Show me what files you're creating and their contents.
"""
    
    # Create the monitoring script
    monitoring_script = f"""#!/bin/bash
set -e

echo "=========================================="
echo "🚀 Claude Code Implementation Monitor"
echo "=========================================="
echo "Starting at: $(date)"
echo "Project: FY.WB.Midway Frontend Agent"
echo "Phase: 1 (Core Foundation)"
echo "Log file: {wsl_log_file}"
echo "=========================================="
echo ""

# Log start time
echo "Starting Claude Code execution at $(date)" >> {wsl_log_file}
echo "Implementation prompt: Frontend Agent Phase 1" >> {wsl_log_file}
echo "========================================" >> {wsl_log_file}

# Change to project directory
cd {wsl_base_path}

echo "📁 Current directory: $(pwd)"
echo "🌿 Current branch: $(git branch --show-current)"
echo "📋 Available design documents:"
ls -la generated_documents/design/

echo ""
echo "🤖 Launching Claude Code..."
echo "⏱️  This may take several minutes for a full implementation..."
echo ""

# Execute Claude Code with real implementation
claude --model sonnet --dangerously-skip-permissions -p "{implementation_prompt}" 2>&1 | tee -a {wsl_log_file}

# Check if execution was successful
CLAUDE_EXIT_CODE=${{PIPESTATUS[0]}}

echo ""
echo "=========================================="
if [ $CLAUDE_EXIT_CODE -eq 0 ]; then
    echo "✅ Claude Code execution completed successfully!"
    echo "Claude Code execution completed successfully at $(date)" >> {wsl_log_file}
    
    # Show what was created
    echo ""
    echo "📁 Checking what was created in FrontEnd directory:"
    if [ -d "FrontEnd" ]; then
        find FrontEnd -type f -name "*.tsx" -o -name "*.ts" -o -name "*.js" -o -name "*.json" | head -20
    else
        echo "⚠️  FrontEnd directory not found"
    fi
    
    echo ""
    echo "📁 Checking what was created in BackEnd directory:"
    if [ -d "BackEnd" ]; then
        find BackEnd -type f -name "*.cs" -o -name "*.json" | head -20
    else
        echo "⚠️  BackEnd directory not found"
    fi
    
    # Try to extract branch name
    BRANCH_NAME=$(git branch --show-current 2>/dev/null || echo "unknown")
    echo "🌿 Current branch: $BRANCH_NAME"
    
    echo "SUCCESS:$BRANCH_NAME" >> {wsl_log_file}
else
    echo "❌ Claude Code execution failed with exit code $CLAUDE_EXIT_CODE"
    echo "Claude Code execution failed at $(date) with exit code $CLAUDE_EXIT_CODE" >> {wsl_log_file}
    echo "FAILED:Exit code $CLAUDE_EXIT_CODE" >> {wsl_log_file}
fi

echo "=========================================="
echo "📊 Execution completed at: $(date)"
echo "📄 Full log available at: {wsl_log_file}"
echo "=========================================="

# Keep terminal open
echo ""
echo "Press Enter to close this terminal..."
read
"""
    
    # Write the monitoring script
    script_file = logs_path / "claude_monitor.sh"
    with open(script_file, 'w', newline='\n') as f:
        f.write(monitoring_script)
    
    return script_file


def launch_separate_terminal():
    """Launch Claude Code in a separate terminal window"""
    
    console.print(Panel.fit(
        "[bold blue]🚀 Launching Claude Code in Separate Terminal[/bold blue]\n"
        "This will open a new terminal window where you can monitor the implementation in real-time",
        border_style="blue"
    ))
    
    # Create the monitoring script
    script_file = create_monitoring_script()
    console.print(f"[green]✅ Created monitoring script: {script_file}[/green]")
    
    # Convert script path to WSL
    wsl_script_path = str(script_file).replace("\\", "/").replace("D:", "/mnt/d")
    
    try:
        # Launch in a new Windows Terminal window
        console.print("[yellow]🚀 Launching new terminal window...[/yellow]")
        
        # Try Windows Terminal first, then fall back to cmd
        try:
            subprocess.Popen([
                "wt", "new-tab", "--title", "Claude Code Monitor", 
                "wsl", "-d", "Ubuntu", "-e", "bash", "-c", 
                f"chmod +x {wsl_script_path} && {wsl_script_path}"
            ])
            console.print("[green]✅ Launched in Windows Terminal[/green]")
        except FileNotFoundError:
            # Fall back to cmd if Windows Terminal not available
            subprocess.Popen([
                "cmd", "/c", "start", "cmd", "/k", 
                f"wsl -d Ubuntu -e bash -c \"chmod +x {wsl_script_path} && {wsl_script_path}\""
            ])
            console.print("[green]✅ Launched in Command Prompt[/green]")
        
        console.print("\n[cyan]📺 A new terminal window should have opened with Claude Code running.[/cyan]")
        console.print("[cyan]You can watch the implementation progress in real-time![/cyan]")
        
        # Wait a moment for the terminal to start
        time.sleep(2)
        
        console.print("\n[yellow]⏱️  Claude Code is now running in the separate terminal.[/yellow]")
        console.print("[yellow]This may take several minutes for a full implementation.[/yellow]")
        
        return True
        
    except Exception as e:
        console.print(f"[red]❌ Failed to launch separate terminal: {e}[/red]")
        console.print("[yellow]💡 You can manually run the script in WSL:[/yellow]")
        console.print(f"[dim]wsl -d Ubuntu -e bash -c \"chmod +x {wsl_script_path} && {wsl_script_path}\"[/dim]")
        return False


def check_current_directories():
    """Check what currently exists in FrontEnd and BackEnd directories"""
    
    console.print("\n" + "="*60)
    console.print("[bold]📁 Current Directory Analysis[/bold]")
    
    base_path = Path("D:/Repository/@Clients/FY.WB.Midway")
    
    # Check FrontEnd directory
    frontend_path = base_path / "FrontEnd"
    console.print(f"\n[bold]🎨 FrontEnd Directory: {frontend_path}[/bold]")
    
    if frontend_path.exists():
        console.print("[green]✅ FrontEnd directory exists[/green]")
        
        # List files
        files = list(frontend_path.rglob("*"))
        if files:
            console.print(f"[blue]📄 Found {len(files)} items:[/blue]")
            for file in files[:10]:  # Show first 10
                rel_path = file.relative_to(frontend_path)
                file_type = "📁" if file.is_dir() else "📄"
                console.print(f"  {file_type} {rel_path}")
            if len(files) > 10:
                console.print(f"  ... and {len(files) - 10} more items")
        else:
            console.print("[yellow]⚠️  FrontEnd directory is empty[/yellow]")
    else:
        console.print("[red]❌ FrontEnd directory does not exist[/red]")
    
    # Check BackEnd directory
    backend_path = base_path / "BackEnd"
    console.print(f"\n[bold]🔧 BackEnd Directory: {backend_path}[/bold]")
    
    if backend_path.exists():
        console.print("[green]✅ BackEnd directory exists[/green]")
        
        # List files
        files = list(backend_path.rglob("*"))
        if files:
            console.print(f"[blue]📄 Found {len(files)} items:[/blue]")
            for file in files[:10]:  # Show first 10
                rel_path = file.relative_to(backend_path)
                file_type = "📁" if file.is_dir() else "📄"
                console.print(f"  {file_type} {rel_path}")
            if len(files) > 10:
                console.print(f"  ... and {len(files) - 10} more items")
        else:
            console.print("[yellow]⚠️  BackEnd directory is empty[/yellow]")
    else:
        console.print("[red]❌ BackEnd directory does not exist[/red]")
    
    # Check if directories need to be created
    console.print(f"\n[bold]💡 Analysis:[/bold]")
    if not frontend_path.exists():
        console.print("[yellow]• FrontEnd directory needs to be created[/yellow]")
    if not backend_path.exists():
        console.print("[yellow]• BackEnd directory needs to be created[/yellow]")
    
    if frontend_path.exists() and not list(frontend_path.rglob("*.tsx")):
        console.print("[yellow]• FrontEnd directory exists but has no React components[/yellow]")
    
    if backend_path.exists() and not list(backend_path.rglob("*.cs")):
        console.print("[yellow]• BackEnd directory exists but has no C# files[/yellow]")


def main():
    """Main function"""
    
    console.print("[bold blue]🔍 Claude Code Terminal Launcher & Directory Analyzer[/bold blue]")
    
    # First, analyze current directories
    check_current_directories()
    
    # Ask user what they want to do
    console.print("\n[bold]What would you like to do?[/bold]")
    console.print("1. 🚀 Launch Claude Code in separate terminal (with real implementation)")
    console.print("2. 📁 Just analyze directories (no execution)")
    console.print("3. 🧪 Launch simulation mode in separate terminal")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        success = launch_separate_terminal()
        if success:
            console.print("\n[green]🎉 Claude Code is now running in a separate terminal![/green]")
            console.print("[cyan]You can monitor the progress and see files being created in real-time.[/cyan]")
    elif choice == "2":
        console.print("\n[blue]📊 Directory analysis complete.[/blue]")
    elif choice == "3":
        console.print("\n[yellow]🧪 Simulation mode would be launched here (not implemented in this script)[/yellow]")
    else:
        console.print("\n[red]Invalid choice.[/red]")


if __name__ == "__main__":
    main()
