#!/usr/bin/env python3
"""
Direct test of the Application Builder system
"""

import asyncio
import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from rich.console import Console
from rich.prompt import Prompt

console = Console()

def main():
    """Test the application builder directly"""
    console.print("[bold cyan]Testing AI-Driven Application Builder Directly[/bold cyan]")
    
    try:
        # Import the application builder
        from application_builder import ApplicationBuilder
        console.print("[green]✅ ApplicationBuilder imported successfully[/green]")
        
        # Set up paths
        base_path = Path("d:/Repository/@Clients/FY.WB.Midway")
        config_path = Path(__file__).parent / "config.yaml"
        
        # Initialize the application builder
        app_builder = ApplicationBuilder("FY.WB.Midway", base_path, config_path)
        console.print("[green]✅ ApplicationBuilder initialized successfully[/green]")
        
        # Test feature specification
        feature_spec = """
        Create a simple customer notification system that allows administrators to send 
        notifications to customers about their shipment status. The system should:
        
        1. Allow admins to create notifications with title, message, and target customers
        2. Display notifications in the customer dashboard
        3. Mark notifications as read/unread
        4. Send email notifications for important updates
        
        This should integrate with the existing customer and shipment management systems.
        """
        
        feature_name = "customer_notification_system"
        
        console.print(f"\n[yellow]Testing with feature: {feature_name}[/yellow]")
        
        # Ask user if they want to proceed
        proceed = Prompt.ask("Do you want to run the full 4-pass workflow? (requires API keys)", choices=["y", "n"], default="n")
        
        if proceed.lower() == "y":
            console.print("[yellow]Starting 4-pass workflow...[/yellow]")
            
            # Run the workflow
            result = asyncio.run(app_builder.run_full_workflow(feature_spec, feature_name))
            
            # Display results
            if result.success:
                console.print(f"\n[bold green]🎉 Workflow completed successfully![/bold green]")
                console.print(f"[green]Feature branch: {result.feature_branch}[/green]")
                console.print(f"[green]Execution time: {result.total_execution_time:.2f}s[/green]")
                if result.pr_url:
                    console.print(f"[green]Pull Request: {result.pr_url}[/green]")
            else:
                console.print(f"\n[yellow]⚠️ Workflow completed with issues[/yellow]")
                console.print(f"[yellow]Error: {result.error_summary}[/yellow]")
                
            # Display pass results
            console.print(f"\n[bold]Pass Results:[/bold]")
            for pass_result in result.pass_results:
                status_color = "green" if pass_result.status.value == "completed" else "red"
                console.print(f"  [{status_color}]{pass_result.pass_type.value}: {pass_result.status.value}[/{status_color}]")
                if pass_result.execution_time:
                    console.print(f"    [dim]Execution time: {pass_result.execution_time:.2f}s, Retries: {pass_result.retry_count}[/dim]")
        else:
            console.print("[yellow]Skipping workflow execution[/yellow]")
            console.print("[green]✅ Application Builder is ready to use![/green]")
            
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
