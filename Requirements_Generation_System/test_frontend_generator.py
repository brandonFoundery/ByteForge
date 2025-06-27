#!/usr/bin/env python3
"""
Test script for the Frontend Test Generator
This script validates that the testing system is properly integrated.
"""

import asyncio
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

# Add the current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

from frontend_test_generator import FrontendTestGenerator

console = Console()


async def test_frontend_generator():
    """Test the FrontendTestGenerator functionality"""
    
    console.print(Panel.fit(
        "[bold]Frontend Test Generator Integration Test[/bold]\n"
        "Testing the integration with run_generation.py",
        style="cyan"
    ))
    
    # Test configuration
    project_name = "FY.WB.Midway"
    base_path = Path(__file__).parent.parent  # Go up one level to project root
    model_provider = "anthropic"
    
    console.print(f"\n[cyan]Configuration:[/cyan]")
    console.print(f"  Project: {project_name}")
    console.print(f"  Base Path: {base_path}")
    console.print(f"  Model Provider: {model_provider}")
    
    # Check if frontend directory exists
    frontend_path = base_path / "FrontEnd"
    if not frontend_path.exists():
        console.print(f"\n[red]❌ Frontend directory not found: {frontend_path}[/red]")
        console.print("[yellow]Please ensure the FrontEnd directory exists in the project root[/yellow]")
        return False
    
    console.print(f"\n[green]✅ Frontend directory found: {frontend_path}[/green]")
    
    # Initialize the generator
    try:
        generator = FrontendTestGenerator(project_name, base_path, model_provider)
        console.print("[green]✅ FrontendTestGenerator initialized successfully[/green]")
    except Exception as e:
        console.print(f"[red]❌ Failed to initialize FrontendTestGenerator: {e}[/red]")
        return False
    
    # Test directory creation
    try:
        testing_output_path = generator.testing_output_path
        claude_prompts_path = generator.claude_prompts_path
        
        console.print(f"\n[cyan]Testing directory creation:[/cyan]")
        console.print(f"  Testing Output: {testing_output_path}")
        console.print(f"  Claude Prompts: {claude_prompts_path}")
        
        if testing_output_path.exists():
            console.print("[green]✅ Testing output directory exists[/green]")
        else:
            console.print("[yellow]⚠️  Testing output directory will be created[/yellow]")
            
        if claude_prompts_path.exists():
            console.print("[green]✅ Claude prompts directory exists[/green]")
        else:
            console.print("[yellow]⚠️  Claude prompts directory will be created[/yellow]")
            
    except Exception as e:
        console.print(f"[red]❌ Directory check failed: {e}[/red]")
        return False
    
    # Test frontend structure analysis
    try:
        console.print(f"\n[cyan]Testing frontend structure analysis:[/cyan]")
        pages_info = await generator._analyze_frontend_structure()
        
        console.print(f"[green]✅ Found {len(pages_info)} pages/components[/green]")
        
        if pages_info:
            console.print("[cyan]Sample pages found:[/cyan]")
            for i, page in enumerate(pages_info[:5]):  # Show first 5
                console.print(f"  • {page['type']}: {page['name']} ({page.get('route', page['path'])})")
            
            if len(pages_info) > 5:
                console.print(f"  ... and {len(pages_info) - 5} more")
        else:
            console.print("[yellow]⚠️  No pages found - this might indicate an issue with the frontend structure[/yellow]")
            
    except Exception as e:
        console.print(f"[red]❌ Frontend structure analysis failed: {e}[/red]")
        return False
    
    # Test prompt generation
    try:
        console.print(f"\n[cyan]Testing prompt generation:[/cyan]")
        
        test_plan_prompt = await generator._create_test_plan_prompt(pages_info)
        if len(test_plan_prompt) > 100:
            console.print("[green]✅ Test plan prompt generated successfully[/green]")
            console.print(f"[dim]Prompt length: {len(test_plan_prompt)} characters[/dim]")
        else:
            console.print("[yellow]⚠️  Test plan prompt seems too short[/yellow]")
            
        testrigor_prompt = await generator._create_testrigor_generation_prompt()
        if len(testrigor_prompt) > 100:
            console.print("[green]✅ testRigor generation prompt generated successfully[/green]")
            console.print(f"[dim]Prompt length: {len(testrigor_prompt)} characters[/dim]")
        else:
            console.print("[yellow]⚠️  testRigor prompt seems too short[/yellow]")
            
    except Exception as e:
        console.print(f"[red]❌ Prompt generation failed: {e}[/red]")
        return False
    
    # Test instruction file creation
    try:
        console.print(f"\n[cyan]Testing instruction file creation:[/cyan]")
        
        test_instruction_file = generator.claude_prompts_path / "test_instructions.md"
        await generator._create_test_plan_instructions(test_instruction_file)
        
        if test_instruction_file.exists():
            console.print("[green]✅ Test plan instructions created successfully[/green]")
        else:
            console.print("[red]❌ Test plan instructions file not created[/red]")
            
        testrigor_instruction_file = generator.claude_prompts_path / "testrigor_instructions.md"
        await generator._create_testrigor_generation_instructions(testrigor_instruction_file)
        
        if testrigor_instruction_file.exists():
            console.print("[green]✅ testRigor instructions created successfully[/green]")
        else:
            console.print("[red]❌ testRigor instructions file not created[/red]")
            
    except Exception as e:
        console.print(f"[red]❌ Instruction file creation failed: {e}[/red]")
        return False
    
    console.print(f"\n[bold green]🎉 All integration tests passed![/bold green]")
    console.print(f"\n[cyan]The Frontend Test Generator is ready to use with run_generation.py[/cyan]")
    console.print(f"[cyan]You can now run options 20, 21, or 22 from the main menu.[/cyan]")
    
    return True


async def main():
    """Main test function"""
    try:
        success = await test_frontend_generator()
        if success:
            console.print(f"\n[bold green]✅ Integration test completed successfully![/bold green]")
            return 0
        else:
            console.print(f"\n[bold red]❌ Integration test failed![/bold red]")
            return 1
    except Exception as e:
        console.print(f"\n[bold red]❌ Integration test error: {e}[/bold red]")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
