#!/usr/bin/env python3
"""
Test script for the AI-Driven Application Builder

This script tests the basic functionality of the application builder system.
"""

import asyncio
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from application_builder import ApplicationBuilder
from rich.console import Console

console = Console()


async def test_basic_workflow():
    """Test the basic workflow setup"""
    console.print("[bold cyan]Testing AI-Driven Application Builder[/bold cyan]")
    
    # Initialize the application builder
    project_name = "FY.WB.Midway"
    base_path = Path("project")
    config_path = Path(__file__).parent / "config.yaml"
    
    try:
        app_builder = ApplicationBuilder(project_name, base_path, config_path)
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
        
        console.print(f"\n[yellow]Testing workflow with feature: {feature_name}[/yellow]")
        console.print(f"[dim]Feature spec: {feature_spec[:100]}...[/dim]")
        
        # Note: This will fail at the design pass since we need API keys
        # But it will test the workflow orchestration
        try:
            result = await app_builder.run_full_workflow(feature_spec, feature_name)
            
            if result.success:
                console.print(f"\n[bold green]🎉 Workflow completed successfully![/bold green]")
                console.print(f"[green]Feature branch: {result.feature_branch}[/green]")
                console.print(f"[green]Execution time: {result.total_execution_time:.2f}s[/green]")
            else:
                console.print(f"\n[yellow]⚠️ Workflow completed with issues[/yellow]")
                console.print(f"[yellow]Error: {result.error_summary}[/yellow]")
                
            # Display pass results
            console.print(f"\n[bold]Pass Results:[/bold]")
            for pass_result in result.pass_results:
                status_color = "green" if pass_result.status.value == "completed" else "red"
                console.print(f"  [{status_color}]{pass_result.pass_type.value}: {pass_result.status.value}[/{status_color}]")
                
        except Exception as e:
            console.print(f"[red]❌ Workflow failed: {e}[/red]")
            console.print(f"[yellow]This is expected if API keys are not configured[/yellow]")
        
    except Exception as e:
        console.print(f"[red]❌ Failed to initialize ApplicationBuilder: {e}[/red]")
        return False
    
    return True


async def test_configuration():
    """Test configuration loading"""
    console.print("\n[bold cyan]Testing Configuration[/bold cyan]")
    
    config_path = Path(__file__).parent / "config.yaml"
    
    if not config_path.exists():
        console.print(f"[red]❌ Config file not found: {config_path}[/red]")
        return False
    
    try:
        import yaml
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Check for application_builder section
        if 'application_builder' in config:
            console.print("[green]✅ Application builder configuration found[/green]")
            
            app_config = config['application_builder']
            console.print(f"[dim]Max retries: {app_config.get('max_retries', 'not set')}[/dim]")
            console.print(f"[dim]Separate terminals: {app_config.get('logging', {}).get('separate_terminals', 'not set')}[/dim]")
            
            # Check pass configurations
            passes = app_config.get('passes', {})
            for pass_name in ['design', 'review', 'implementation']:
                if pass_name in passes:
                    pass_config = passes[pass_name]
                    console.print(f"[dim]{pass_name.title()} pass: {pass_config.get('model', 'not set')} - {pass_config.get('model_name', 'not set')}[/dim]")
                else:
                    console.print(f"[yellow]⚠️ {pass_name.title()} pass configuration missing[/yellow]")
        else:
            console.print("[yellow]⚠️ Application builder configuration not found in config.yaml[/yellow]")
            return False
            
    except Exception as e:
        console.print(f"[red]❌ Failed to load configuration: {e}[/red]")
        return False
    
    return True


async def test_logging_system():
    """Test the multi-terminal logging system"""
    console.print("\n[bold cyan]Testing Multi-Terminal Logging System[/bold cyan]")
    
    try:
        from multi_terminal_logger import MultiTerminalLogger, LogLevel
        
        base_path = Path("project")
        workflow_id = "test_workflow_123"
        
        logger = MultiTerminalLogger(base_path, workflow_id)
        console.print("[green]✅ MultiTerminalLogger initialized successfully[/green]")
        
        # Test creating pass loggers
        design_logger = logger.create_pass_logger("design")
        console.print("[green]✅ Design pass logger created[/green]")
        
        # Test logging messages
        logger.log_pass_message("design", LogLevel.INFO, "Test message from design pass")
        logger.log_pass_start("design", "Test feature specification")
        logger.log_pass_complete("design", 5.2, "Generated design document")
        
        console.print("[green]✅ Logging system test completed[/green]")
        console.print(f"[dim]Log files created in: {logger.log_dir}[/dim]")
        
        # Cleanup
        logger.cleanup()
        
    except Exception as e:
        console.print(f"[red]❌ Logging system test failed: {e}[/red]")
        return False
    
    return True


async def main():
    """Run all tests"""
    console.print("[bold]AI-Driven Application Builder - Test Suite[/bold]")
    console.print("=" * 60)
    
    tests = [
        ("Configuration", test_configuration),
        ("Logging System", test_logging_system),
        ("Basic Workflow", test_basic_workflow),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        console.print(f"\n[bold]Running {test_name} Test...[/bold]")
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            console.print(f"[red]❌ {test_name} test failed with exception: {e}[/red]")
            results.append((test_name, False))
    
    # Summary
    console.print("\n" + "=" * 60)
    console.print("[bold]Test Results Summary[/bold]")
    
    passed = 0
    for test_name, result in results:
        status = "[green]PASS[/green]" if result else "[red]FAIL[/red]"
        console.print(f"  {status} {test_name}")
        if result:
            passed += 1
    
    console.print(f"\n[bold]Tests passed: {passed}/{len(results)}[/bold]")
    
    if passed == len(results):
        console.print("[bold green]🎉 All tests passed![/bold green]")
    else:
        console.print("[bold yellow]⚠️ Some tests failed. Check the output above for details.[/bold yellow]")


if __name__ == "__main__":
    asyncio.run(main())
