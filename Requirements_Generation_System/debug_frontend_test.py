#!/usr/bin/env python3
"""
Debug script for Frontend Test Generator
This script will help identify the exact issue causing the failure.
"""

import asyncio
import sys
import logging
from pathlib import Path
from rich.console import Console

# Add the current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

console = Console()

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug_frontend_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


async def debug_frontend_test_generator():
    """Debug the FrontendTestGenerator step by step"""
    
    console.print("[bold cyan]🔍 Debug Frontend Test Generator[/bold cyan]")
    
    try:
        # Step 1: Import the module
        console.print("\n[cyan]Step 1: Importing FrontendTestGenerator...[/cyan]")
        logger.info("Importing FrontendTestGenerator")
        
        from frontend_test_generator import FrontendTestGenerator
        console.print("[green]✅ Import successful[/green]")
        
        # Step 2: Initialize the generator
        console.print("\n[cyan]Step 2: Initializing FrontendTestGenerator...[/cyan]")
        logger.info("Initializing FrontendTestGenerator")
        
        project_name = "FY.WB.Midway"
        base_path = Path(__file__).parent.parent  # Go up one level to project root
        model_provider = "anthropic"
        
        console.print(f"  Project: {project_name}")
        console.print(f"  Base Path: {base_path}")
        console.print(f"  Model Provider: {model_provider}")
        
        generator = FrontendTestGenerator(project_name, base_path, model_provider)
        console.print("[green]✅ Initialization successful[/green]")
        
        # Step 3: Test frontend structure analysis
        console.print("\n[cyan]Step 3: Testing frontend structure analysis...[/cyan]")
        logger.info("Testing frontend structure analysis")
        
        pages_info = await generator._analyze_frontend_structure()
        console.print(f"[green]✅ Found {len(pages_info)} pages/components[/green]")
        
        if pages_info:
            console.print("[cyan]Sample pages found:[/cyan]")
            for i, page in enumerate(pages_info[:3]):  # Show first 3
                console.print(f"  • {page['type']}: {page['name']} ({page.get('route', page['path'])})")
        
        # Step 4: Test prompt generation
        console.print("\n[cyan]Step 4: Testing prompt generation...[/cyan]")
        logger.info("Testing prompt generation")
        
        test_plan_prompt = await generator._create_test_plan_prompt(pages_info)
        console.print(f"[green]✅ Generated prompt with {len(test_plan_prompt)} characters[/green]")
        
        # Step 5: Test directory creation
        console.print("\n[cyan]Step 5: Testing directory creation...[/cyan]")
        logger.info("Testing directory creation")
        
        testing_output_path = generator.testing_output_path
        claude_prompts_path = generator.claude_prompts_path
        
        console.print(f"  Testing Output: {testing_output_path}")
        console.print(f"  Claude Prompts: {claude_prompts_path}")
        
        if testing_output_path.exists():
            console.print("[green]✅ Testing output directory exists[/green]")
        else:
            console.print("[yellow]⚠️  Creating testing output directory[/yellow]")
            testing_output_path.mkdir(parents=True, exist_ok=True)
            console.print("[green]✅ Testing output directory created[/green]")
            
        if claude_prompts_path.exists():
            console.print("[green]✅ Claude prompts directory exists[/green]")
        else:
            console.print("[yellow]⚠️  Creating claude prompts directory[/yellow]")
            claude_prompts_path.mkdir(parents=True, exist_ok=True)
            console.print("[green]✅ Claude prompts directory created[/green]")
        
        # Step 6: Test file writing
        console.print("\n[cyan]Step 6: Testing file writing...[/cyan]")
        logger.info("Testing file writing")
        
        # Save the prompt for Claude Code
        prompt_file = claude_prompts_path / "debug_test_plan_prompt.md"
        with open(prompt_file, 'w', encoding='utf-8') as f:
            f.write(test_plan_prompt)
        
        console.print(f"[green]✅ Prompt saved to: {prompt_file}[/green]")
        
        # Step 7: Test instruction file creation
        console.print("\n[cyan]Step 7: Testing instruction file creation...[/cyan]")
        logger.info("Testing instruction file creation")
        
        instruction_file = claude_prompts_path / "debug_test_plan_instructions.md"
        await generator._create_test_plan_instructions(instruction_file)
        
        if instruction_file.exists():
            console.print(f"[green]✅ Instructions saved to: {instruction_file}[/green]")
        else:
            console.print("[red]❌ Instructions file not created[/red]")
            return False
        
        console.print("\n[bold green]🎉 All debug tests passed![/bold green]")
        console.print("[green]The FrontendTestGenerator is working correctly up to file generation.[/green]")
        console.print("[yellow]The issue might be in the complete workflow or terminal launching.[/yellow]")
        
        return True
        
    except Exception as e:
        console.print(f"\n[bold red]❌ Debug test failed at step: {e}[/bold red]")
        logger.error(f"Debug test failed: {str(e)}")
        
        import traceback
        console.print(f"[red]Full traceback:[/red]")
        console.print(traceback.format_exc())
        
        return False


async def test_complete_workflow():
    """Test the complete workflow to see where it fails"""
    
    console.print("\n[bold cyan]🔍 Testing Complete Workflow[/bold cyan]")
    
    try:
        from frontend_test_generator import FrontendTestGenerator
        
        project_name = "FY.WB.Midway"
        base_path = Path(__file__).parent.parent
        model_provider = "anthropic"
        
        generator = FrontendTestGenerator(project_name, base_path, model_provider)
        
        console.print("[cyan]Testing generate_test_plan method...[/cyan]")
        result = await generator.generate_test_plan()
        
        if result.success:
            console.print("[green]✅ generate_test_plan completed successfully[/green]")
            console.print(f"  Pages analyzed: {result.pages_analyzed}")
            console.print(f"  Execution time: {result.execution_time:.2f}s")
        else:
            console.print("[red]❌ generate_test_plan failed[/red]")
            console.print(f"  Error: {result.error_summary}")
            return False
        
        return True
        
    except Exception as e:
        console.print(f"[red]❌ Complete workflow test failed: {e}[/red]")
        import traceback
        console.print(traceback.format_exc())
        return False


async def main():
    """Main debug function"""
    
    console.print("[bold]Frontend Test Generator Debug Session[/bold]")
    console.print("This will help identify the exact issue causing the failure.\n")
    
    # Run step-by-step debug
    step_by_step_success = await debug_frontend_test_generator()
    
    if step_by_step_success:
        console.print("\n" + "="*60)
        
        # Run complete workflow test
        workflow_success = await test_complete_workflow()
        
        if workflow_success:
            console.print("\n[bold green]🎉 All tests passed! The system should be working.[/bold green]")
        else:
            console.print("\n[bold red]❌ Complete workflow failed. Check the logs above.[/bold red]")
    else:
        console.print("\n[bold red]❌ Step-by-step debug failed. Fix the issues above first.[/bold red]")
    
    console.print(f"\n[cyan]Debug log saved to: debug_frontend_test.log[/cyan]")
    console.print(f"[cyan]System log saved to: frontend_test_generator.log[/cyan]")


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(0)
