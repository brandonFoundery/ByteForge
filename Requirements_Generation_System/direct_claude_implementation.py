#!/usr/bin/env python3
"""
Direct Claude Code Implementation with File Content

This script directly executes Claude Code with the instruction file content
to ensure proper implementation of CRM features.
"""

import subprocess
import sys
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt

console = Console()

def execute_claude_with_file_content():
    """Execute Claude Code with the actual instruction file content"""
    console.print(f"\n[cyan]🚀 Direct Claude Code Implementation[/cyan]")
    
    # Read the instruction file content
    instruction_file = Path("../generated_documents/design/claude_instructions/frontend-phase1-mvp-core-features.md")
    if not instruction_file.exists():
        console.print(f"[red]❌ Instruction file not found: {instruction_file}[/red]")
        return False
    
    console.print(f"[green]📖 Reading instruction file: {instruction_file.name}[/green]")
    
    with open(instruction_file, 'r', encoding='utf-8') as f:
        instruction_content = f.read()
    
    console.print(f"[green]✅ Loaded {len(instruction_content)} characters of instructions[/green]")
    
    # Check if FrontEnd directory exists
    frontend_dir = Path("../FrontEnd")
    if not frontend_dir.exists():
        console.print(f"[red]❌ Frontend directory not found: {frontend_dir.absolute()}[/red]")
        return False
    
    console.print(f"[green]📁 Found frontend directory: {frontend_dir.absolute()}[/green]")
    
    # Create a focused prompt that tells Claude to implement the CRM features
    focused_prompt = f"""You are implementing the Frontend Agent Phase 1 for the FY.WB.Midway CRM system.

CRITICAL: You must IMPLEMENT the code, not just discuss it. This is a real implementation task.

Here are your complete instructions:

{instruction_content}

IMPLEMENTATION REQUIREMENTS:
1. You MUST create all the components and files listed in the deliverables
2. You MUST implement the CRM features: Lead capture, Contact management, Deal pipeline, Activity tracking
3. You MUST build working React/Next.js components with proper TypeScript
4. You MUST integrate with the backend APIs
5. You MUST create a completion report when finished

START IMPLEMENTING NOW. Do not ask questions - implement the code according to the specifications.

Focus on creating the CRM customer management system with:
- Customer/Client list and detail views
- Customer creation and editing forms
- Search and filtering capabilities
- Integration with backend APIs
- Professional UI using Tailwind CSS

Begin implementation immediately."""
    
    # Convert to WSL path
    wsl_frontend_path = "/mnt/d/Repository/@Clients/FY.WB.Midway/FrontEnd"
    
    console.print(f"[cyan]💻 Executing Claude Code with direct instructions...[/cyan]")
    console.print(f"[dim]Frontend path: {wsl_frontend_path}[/dim]")
    console.print(f"[dim]Instruction length: {len(focused_prompt)} characters[/dim]")
    
    # Escape the prompt for shell safety
    escaped_prompt = focused_prompt.replace('"', '\\"').replace('`', '\\`').replace('$', '\\$')
    
    # Create the command
    claude_command = f'cd {wsl_frontend_path} && claude --model sonnet --dangerously-skip-permissions -p "{escaped_prompt}"'
    
    console.print(f"[yellow]⏱️  Launching Claude Code (this may take several minutes)...[/yellow]")
    console.print(f"[cyan]This will implement the actual CRM components in the FrontEnd directory[/cyan]")
    
    # Execute in WSL with real-time output
    try:
        cmd = [
            "wsl", "-d", "Ubuntu", "-e", "bash", "-c", claude_command
        ]
        
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        console.print("[bold]Claude Code Output:[/bold]")
        console.print("=" * 60)
        
        # Show real-time output
        for line in proc.stdout:
            print(line.rstrip())
        
        return_code = proc.wait()
        
        console.print("=" * 60)
        console.print(f"[bold]Claude Code execution completed with exit code: {return_code}[/bold]")
        
        if return_code == 0:
            console.print(f"\n[bold green]🎉 Frontend implementation completed successfully![/bold green]")
            return True
        else:
            console.print(f"\n[yellow]⚠️  Claude Code completed with exit code: {return_code}[/yellow]")
            return False
            
    except Exception as e:
        console.print(f"\n[red]❌ Failed to execute Claude Code: {e}[/red]")
        return False

def verify_implementation():
    """Verify that the implementation actually created files"""
    console.print(f"\n[cyan]🔍 Verifying Implementation Results[/cyan]")
    
    frontend_src = Path("../FrontEnd/src")
    if not frontend_src.exists():
        console.print(f"[red]❌ Frontend src directory not found[/red]")
        return False
    
    # Check for key directories that should be created
    expected_dirs = [
        "components/Layout",
        "components/Auth", 
        "components/Dashboard",
        "components/LoadManagement",
        "components/ClientManagement",
        "components/CustomerManagement",  # CRM specific
        "services"
    ]
    
    created_dirs = []
    missing_dirs = []
    
    for dir_path in expected_dirs:
        full_path = frontend_src / dir_path
        if full_path.exists():
            created_dirs.append(dir_path)
            console.print(f"[green]✅ Found: {dir_path}[/green]")
        else:
            missing_dirs.append(dir_path)
            console.print(f"[yellow]⚠️  Missing: {dir_path}[/yellow]")
    
    # Check for key files
    expected_files = [
        "components/CustomerManagement/CustomerList.tsx",
        "components/CustomerManagement/CustomerForm.tsx",
        "components/CustomerManagement/CustomerDetail.tsx",
        "services/customerService.ts",
        "services/api.ts"
    ]
    
    created_files = []
    missing_files = []
    
    for file_path in expected_files:
        full_path = frontend_src / file_path
        if full_path.exists():
            created_files.append(file_path)
            console.print(f"[green]✅ Found: {file_path}[/green]")
        else:
            missing_files.append(file_path)
            console.print(f"[yellow]⚠️  Missing: {file_path}[/yellow]")
    
    console.print(f"\n[bold]Implementation Summary:[/bold]")
    console.print(f"[green]✅ Created directories: {len(created_dirs)}/{len(expected_dirs)}[/green]")
    console.print(f"[green]✅ Created files: {len(created_files)}/{len(expected_files)}[/green]")
    
    if len(created_dirs) > 0 or len(created_files) > 0:
        console.print(f"[green]🎉 Implementation successful - files were created![/green]")
        return True
    else:
        console.print(f"[red]❌ Implementation failed - no files were created[/red]")
        return False

def main():
    """Main execution function"""
    console.print("[bold blue]🚀 Direct Claude Code CRM Implementation[/bold blue]")
    console.print("This will:")
    console.print("  1. Read the complete instruction file content")
    console.print("  2. Execute Claude Code with direct implementation instructions")
    console.print("  3. Monitor real-time implementation progress")
    console.print("  4. Verify that actual CRM components were created")
    
    confirm = Prompt.ask("\nProceed with direct Claude Code implementation?", choices=["y", "n"], default="y")
    if confirm.lower() != "y":
        console.print("[yellow]Operation cancelled.[/yellow]")
        return 0
    
    # Execute Claude Code with file content
    console.print(f"\n[bold cyan]Step 1: Execute Claude Code Implementation[/bold cyan]")
    if not execute_claude_with_file_content():
        console.print("[red]❌ Claude Code implementation failed[/red]")
        return 1
    
    # Verify implementation results
    console.print(f"\n[bold cyan]Step 2: Verify Implementation Results[/bold cyan]")
    if not verify_implementation():
        console.print("[red]❌ Implementation verification failed[/red]")
        return 1
    
    console.print(f"\n[bold green]🎉 Direct implementation completed successfully![/bold green]")
    console.print(f"[green]✅ Claude Code executed with full instructions[/green]")
    console.print(f"[green]✅ CRM components created and verified[/green]")
    console.print(f"\n[cyan]💡 Next steps:[/cyan]")
    console.print(f"  • Check the FrontEnd/src directory for new CRM components")
    console.print(f"  • Test the application at http://localhost:4000")
    console.print(f"  • Verify the customer management features work")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
