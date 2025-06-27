#!/usr/bin/env python3
"""
Quick Start Script for FY.WB.Midway Requirements Generation
This script provides a simple way to test the system with minimal setup.
"""

import os
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt

console = Console()


def check_api_keys():
    """Check and set API keys if needed"""
    providers = {
        'openai': ('OPENAI_API_KEY', 'sk-...'),
        'anthropic': ('ANTHROPIC_API_KEY', 'sk-ant-...')
    }
    
    console.print("\n[cyan]Checking API keys...[/cyan]")
    
    for provider, (env_var, example) in providers.items():
        if not os.getenv(env_var):
            console.print(f"\n[yellow]{env_var} not found.[/yellow]")
            if Confirm.ask(f"Do you want to set {provider} API key now?"):
                key = Prompt.ask(f"Enter your {provider} API key", password=True)
                os.environ[env_var] = key
                console.print(f"[green]✅ {env_var} set for this session[/green]")
        else:
            console.print(f"[green]✅ {env_var} found[/green]")


def create_sample_requirements():
    """Create sample requirements for testing"""
    sample_dir = Path("sample_requirements")
    sample_dir.mkdir(exist_ok=True)
    
    # Create a sample requirement file
    sample_req = sample_dir / "FY.WB.Midway_Requirements.md"
    
    if not sample_req.exists():
        console.print("\n[cyan]Creating sample requirements for testing...[/cyan]")
        
        content = """# FY.WB.Midway System Requirements

## Executive Summary
FY.WB.Midway is an enterprise logistics and payment platform designed to streamline freight management and financial transactions.

## Business Objectives
1. Reduce freight processing time by 60%
2. Automate payment reconciliation
3. Provide real-time shipment tracking
4. Enable multi-currency transactions
5. Ensure regulatory compliance

## Key Features
- **Shipment Management**: Create, track, and manage freight shipments
- **Payment Processing**: Handle invoices, payments, and reconciliation
- **User Management**: Role-based access control and permissions
- **Reporting**: Real-time analytics and custom reports
- **Integration**: APIs for third-party systems

## Technical Requirements
- Cloud-native architecture
- Microservices design
- RESTful APIs
- Real-time data synchronization
- 99.9% uptime SLA

## Users
- Shippers
- Carriers
- Finance Teams
- Administrators
- External Partners
"""
        
        sample_req.write_text(content)
        console.print(f"[green]✅ Created sample requirements at: {sample_req}[/green]")
    
    return sample_dir


def update_config_for_quickstart(sample_dir: Path):
    """Update config to use sample requirements"""
    import yaml
    
    config_path = Path("config.yaml")
    
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Update paths
        config['paths']['requirements_dir'] = str(sample_dir.absolute())
        config['paths']['output_dir'] = str(Path("quickstart_output").absolute())
        config['paths']['status_dir'] = str(Path("quickstart_status").absolute())
        
        # Save updated config
        quickstart_config = Path("quickstart_config.yaml")
        with open(quickstart_config, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        console.print(f"[green]✅ Created quickstart config: {quickstart_config}[/green]")
        return quickstart_config
    else:
        console.print("[red]❌ config.yaml not found[/red]")
        return None


def main():
    """Run quickstart"""
    console.print(Panel.fit(
        "[bold]FY.WB.Midway Requirements Generation - Quick Start[/bold]\n"
        "This will help you test the system quickly",
        style="cyan"
    ))
    
    # Check dependencies
    console.print("\n[cyan]Checking dependencies...[/cyan]")
    try:
        import openai
        import anthropic
        import networkx
        import matplotlib
        import yaml
        console.print("[green]✅ All dependencies installed[/green]")
    except ImportError as e:
        console.print(f"[red]❌ Missing dependency: {e.name}[/red]")
        console.print("[yellow]Run: pip install -r requirements.txt[/yellow]")
        return
    
    # Check API keys
    check_api_keys()
    
    # Create sample requirements
    sample_dir = create_sample_requirements()
    
    # Update config
    config_path = update_config_for_quickstart(sample_dir)
    
    if not config_path:
        return
    
    # Options
    console.print("\n[bold]Quick Start Options:[/bold]")
    console.print("1. Run a test generation (1 document)")
    console.print("2. Run full generation (all documents)")
    console.print("3. Open monitor dashboard")
    console.print("4. View sample requirements")
    
    choice = Prompt.ask("\nSelect option", choices=["1", "2", "3", "4"])
    
    if choice == "1":
        # Test with just BRD
        console.print("\n[cyan]Running test generation (BRD only)...[/cyan]")
        console.print("[dim]This will generate just the Business Requirements Document[/dim]\n")
        
        # Modify config for single document
        import yaml
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Disable all except BRD
        for doc in config['documents']:
            config['documents'][doc]['enabled'] = (doc == 'BRD')
        
        # Save temp config
        test_config = Path("test_config.yaml")
        with open(test_config, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        # Run orchestrator
        os.system(f"{sys.executable} orchestrator.py --config {test_config}")
        
    elif choice == "2":
        console.print("\n[cyan]Running full generation...[/cyan]")
        console.print("[dim]This will generate all 10 documents[/dim]\n")
        
        os.system(f"{sys.executable} run_generation.py")
        
    elif choice == "3":
        console.print("\n[cyan]Opening monitor dashboard...[/cyan]")
        output_dir = Path("quickstart_output").absolute()
        os.system(f"start cmd /k {sys.executable} monitor.py {output_dir}")
        
    elif choice == "4":
        console.print("\n[cyan]Sample requirements:[/cyan]")
        sample_req = sample_dir / "FY.WB.Midway_Requirements.md"
        console.print(Panel(sample_req.read_text(), title="Sample Requirements"))
    
    # Show next steps
    console.print("\n[bold]Next Steps:[/bold]")
    console.print("1. Check generated documents in 'quickstart_output' folder")
    console.print("2. Run 'python utils.py analyze quickstart_output' for traceability report")
    console.print("3. Modify sample requirements and regenerate")
    console.print("4. Use your own requirements by updating config.yaml")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Quickstart interrupted[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error: {str(e)}[/red]")
        import traceback
        traceback.print_exc()