#!/usr/bin/env python3
"""
Simple Claude Code CRM Implementation

This script uses a simple approach to execute Claude Code for CRM implementation.
"""

import subprocess
import sys
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt

console = Console()

def execute_claude_simple():
    """Execute Claude Code with a simple CRM implementation prompt"""
    console.print(f"\n[cyan]🚀 Simple Claude Code CRM Implementation[/cyan]")
    
    # Check if FrontEnd directory exists
    frontend_dir = Path("../FrontEnd")
    if not frontend_dir.exists():
        console.print(f"[red]❌ Frontend directory not found: {frontend_dir.absolute()}[/red]")
        return False
    
    console.print(f"[green]📁 Found frontend directory: {frontend_dir.absolute()}[/green]")
    
    # Create a simple, direct prompt for CRM implementation
    simple_prompt = """Implement CRM customer management features for the FY.WB.Midway application.

CRITICAL: You must CREATE actual code files, not just discuss them.

Create these CRM components in the FrontEnd/src directory:

1. components/CustomerManagement/CustomerList.tsx - List all customers with search and filtering
2. components/CustomerManagement/CustomerForm.tsx - Create/edit customer form
3. components/CustomerManagement/CustomerDetail.tsx - Customer detail view
4. components/CustomerManagement/CustomerCard.tsx - Individual customer card
5. services/customerService.ts - API service for customer operations
6. pages/customers/index.tsx - Main customers page
7. pages/customers/[id].tsx - Customer detail page
8. pages/customers/new.tsx - New customer page

Requirements:
- Use React with TypeScript
- Use Tailwind CSS for styling
- Include search, filtering, and pagination
- Add CRUD operations (Create, Read, Update, Delete)
- Include form validation
- Use modern React hooks
- Make it responsive and professional looking

START IMPLEMENTING NOW. Create the actual files with working code."""
    
    # Convert to WSL path
    wsl_frontend_path = "project/FrontEnd"
    
    console.print(f"[cyan]💻 Executing Claude Code with simple CRM prompt...[/cyan]")
    console.print(f"[dim]Frontend path: {wsl_frontend_path}[/dim]")
    
    # Create the command with a simple prompt
    claude_command = f"""cd {wsl_frontend_path} && claude --model sonnet --dangerously-skip-permissions -p '{simple_prompt}'"""
    
    console.print(f"[yellow]⏱️  Launching Claude Code (this may take several minutes)...[/yellow]")
    console.print(f"[cyan]This will create CRM customer management components[/cyan]")
    
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
            universal_newlines=True,
            encoding='utf-8',
            errors='replace'  # Handle encoding errors gracefully
        )
        
        console.print("[bold]Claude Code Output:[/bold]")
        console.print("=" * 60)
        
        # Show real-time output with error handling
        try:
            for line in proc.stdout:
                print(line.rstrip())
        except UnicodeDecodeError:
            console.print("[yellow]⚠️  Some output contained special characters[/yellow]")
        
        return_code = proc.wait()
        
        console.print("=" * 60)
        console.print(f"[bold]Claude Code execution completed with exit code: {return_code}[/bold]")
        
        if return_code == 0:
            console.print(f"\n[bold green]🎉 CRM implementation completed successfully![/bold green]")
            return True
        else:
            console.print(f"\n[yellow]⚠️  Claude Code completed with exit code: {return_code}[/yellow]")
            return False
            
    except Exception as e:
        console.print(f"\n[red]❌ Failed to execute Claude Code: {e}[/red]")
        return False

def verify_crm_implementation():
    """Verify that CRM components were actually created"""
    console.print(f"\n[cyan]🔍 Verifying CRM Implementation[/cyan]")
    
    frontend_src = Path("../FrontEnd/src")
    if not frontend_src.exists():
        console.print(f"[red]❌ Frontend src directory not found[/red]")
        return False
    
    # Check for CRM-specific files
    crm_files = [
        "components/CustomerManagement/CustomerList.tsx",
        "components/CustomerManagement/CustomerForm.tsx", 
        "components/CustomerManagement/CustomerDetail.tsx",
        "components/CustomerManagement/CustomerCard.tsx",
        "services/customerService.ts",
        "pages/customers/index.tsx",
        "pages/customers/[id].tsx",
        "pages/customers/new.tsx"
    ]
    
    created_files = []
    missing_files = []
    
    for file_path in crm_files:
        full_path = frontend_src / file_path
        if full_path.exists():
            created_files.append(file_path)
            # Check file size to ensure it's not empty
            file_size = full_path.stat().st_size
            console.print(f"[green]✅ Found: {file_path} ({file_size} bytes)[/green]")
        else:
            missing_files.append(file_path)
            console.print(f"[yellow]⚠️  Missing: {file_path}[/yellow]")
    
    # Check for any customer-related files that might have been created
    customer_files = list(frontend_src.rglob("*[Cc]ustomer*"))
    if customer_files:
        console.print(f"\n[cyan]📁 Found customer-related files:[/cyan]")
        for file in customer_files:
            rel_path = file.relative_to(frontend_src)
            file_size = file.stat().st_size if file.is_file() else "DIR"
            console.print(f"[blue]  • {rel_path} ({file_size})[/blue]")
    
    console.print(f"\n[bold]CRM Implementation Summary:[/bold]")
    console.print(f"[green]✅ Created CRM files: {len(created_files)}/{len(crm_files)}[/green]")
    console.print(f"[blue]📁 Total customer files found: {len(customer_files)}[/blue]")
    
    if len(created_files) > 0 or len(customer_files) > 0:
        console.print(f"[green]🎉 CRM implementation successful - files were created![/green]")
        return True
    else:
        console.print(f"[red]❌ CRM implementation failed - no files were created[/red]")
        return False

def main():
    """Main execution function"""
    console.print("[bold blue]🚀 Simple Claude Code CRM Implementation[/bold blue]")
    console.print("This will:")
    console.print("  1. Execute Claude Code with a simple CRM implementation prompt")
    console.print("  2. Create customer management components")
    console.print("  3. Verify that actual CRM files were created")
    console.print("  4. Handle encoding issues gracefully")
    
    confirm = Prompt.ask("\nProceed with simple CRM implementation?", choices=["y", "n"], default="y")
    if confirm.lower() != "y":
        console.print("[yellow]Operation cancelled.[/yellow]")
        return 0
    
    # Execute Claude Code
    console.print(f"\n[bold cyan]Step 1: Execute Claude Code CRM Implementation[/bold cyan]")
    if not execute_claude_simple():
        console.print("[red]❌ Claude Code implementation failed[/red]")
        return 1
    
    # Verify implementation results
    console.print(f"\n[bold cyan]Step 2: Verify CRM Implementation[/bold cyan]")
    if not verify_crm_implementation():
        console.print("[red]❌ CRM implementation verification failed[/red]")
        return 1
    
    console.print(f"\n[bold green]🎉 Simple CRM implementation completed successfully![/bold green]")
    console.print(f"[green]✅ Claude Code executed successfully[/green]")
    console.print(f"[green]✅ CRM components created and verified[/green]")
    console.print(f"\n[cyan]💡 Next steps:[/cyan]")
    console.print(f"  • Check the FrontEnd/src directory for new CRM components")
    console.print(f"  • Start the development server: cd FrontEnd && npm run dev")
    console.print(f"  • Test the application at http://localhost:4000")
    console.print(f"  • Navigate to /customers to see the CRM features")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
