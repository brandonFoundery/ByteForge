#!/usr/bin/env python3
"""
LLM UI Generation Orchestrator
Main script to run the complete LLM UI generation process:
1. Create reference images
2. Generate UIs with all LLM models in parallel
3. Create comparison viewer
4. Open results in browser
"""

import os
import sys
import asyncio
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

console = Console()

async def main():
    """Main orchestrator function"""
    
    console.print(Panel.fit(
        "[bold cyan]🚀 LLM UI Generation System[/bold cyan]\n"
        "Generating 45 unique dashboard designs (9 styles × 5 models)\n"
        "• OpenAI GPT-4o, GPT-4.1, o3\n"
        "• Google Gemini 2.5\n"
        "• Anthropic Claude 4\n"
        "• Each model creates designs for all 9 reference styles",
        style="cyan"
    ))
    
    project_root = Path(__file__).parent.parent.parent
    
    # Step 1: Check/Create reference images
    console.print("\n[bold]Step 1: Checking Reference Images[/bold]")

    # Check if reference images already exist
    examples_dir = project_root / "Requirements_Generation_System" / "ui_style_examples"
    existing_images = list(examples_dir.glob("*.png")) if examples_dir.exists() else []

    if len(existing_images) >= 9:
        console.print(f"[green]✅ Found {len(existing_images)} existing reference images - skipping recreation[/green]")
        console.print("[dim]   (To recreate images, delete the ui_style_examples folder first)[/dim]")
    else:
        console.print(f"[yellow]⚠️  Only found {len(existing_images)} reference images, creating missing ones...[/yellow]")
        try:
            from create_reference_images import create_reference_images
            create_reference_images()
            console.print("[green]✅ Reference images created successfully[/green]")
        except Exception as e:
            console.print(f"[red]❌ Failed to create reference images: {e}[/red]")
            return False
    
    # Step 2: Check API keys
    console.print("\n[bold]Step 2: Checking API Keys[/bold]")
    api_keys = {
        'OpenAI': os.getenv('OPENAI_API_KEY'),
        'Google': os.getenv('GOOGLE_API_KEY'), 
        'Anthropic': os.getenv('ANTHROPIC_API_KEY')
    }
    
    missing_keys = [provider for provider, key in api_keys.items() if not key]
    if missing_keys:
        console.print(f"[yellow]⚠️  Missing API keys for: {', '.join(missing_keys)}[/yellow]")
        console.print("[yellow]Some models may fail to generate. Set environment variables:[/yellow]")
        for provider in missing_keys:
            console.print(f"[yellow]  - {provider.upper()}_API_KEY[/yellow]")
    else:
        console.print("[green]✅ All API keys found[/green]")
    
    # Step 3: Create and open live comparison page
    console.print("\n[bold]Step 3: Creating Live Comparison Page[/bold]")

    try:
        from live_comparison_viewer import LiveComparisonViewer

        live_viewer = LiveComparisonViewer(project_root)
        live_viewer.create_and_open_live_page()

        console.print("[green]✅ Live comparison page opened - will update as designs complete[/green]")

    except Exception as e:
        console.print(f"[red]❌ Failed to create live page: {e}[/red]")
        return False

    # Step 4: Generate UIs with all LLMs in parallel
    console.print("\n[bold]Step 4: Generating UIs with LLM Models[/bold]")

    try:
        from llm_ui_generator import LLMUIGenerator

        generator = LLMUIGenerator(project_root)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Generating UIs in parallel...", total=None)

            results = await generator.generate_all_llm_uis()

            progress.update(task, description="✅ LLM generation complete!")

        successful_count = len([r for r in results if r.get("success")])
        console.print(f"[green]✅ Generated {successful_count}/{len(results)} UIs successfully[/green]")

    except Exception as e:
        console.print(f"[red]❌ Failed to generate UIs: {e}[/red]")
        return False
    
    # Step 5: Create final static comparison viewer
    console.print("\n[bold]Step 5: Creating Final Comparison Viewer[/bold]")

    try:
        from llm_comparison_viewer import LLMComparisonViewer

        viewer = LLMComparisonViewer(project_root)
        viewer.save_and_open_comparison(results)

        console.print("[green]✅ Final comparison viewer created[/green]")

    except Exception as e:
        console.print(f"[yellow]⚠️  Could not create final viewer: {e}[/yellow]")
        console.print("[green]✅ Live viewer is still available and functional[/green]")
    
    # Summary
    console.print(Panel.fit(
        f"[bold green]🎉 LLM UI Generation Complete![/bold green]\n\n"
        f"📊 Results Summary:\n"
        f"• Total Combinations: {len(results)} (9 styles × 5 models)\n"
        f"• Successful: {successful_count}\n"
        f"• Failed: {len(results) - successful_count}\n\n"
        f"🌐 Live comparison page opened in your browser\n"
        f"📱 Page updates automatically as designs complete\n"
        f"📁 Files saved in: ui_style_system/llm_generated/",
        style="green"
    ))
    
    return True

def check_dependencies():
    """Check if required dependencies are installed"""
    
    required_packages = [
        ('PIL', 'Pillow'),
        ('rich', 'rich'),
        ('openai', 'openai'),
        ('google.generativeai', 'google-generativeai'),
        ('anthropic', 'anthropic')
    ]
    
    missing_packages = []
    
    for import_name, package_name in required_packages:
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(package_name)
    
    if missing_packages:
        console.print(Panel.fit(
            f"[bold red]❌ Missing Dependencies[/bold red]\n\n"
            f"Please install the following packages:\n"
            f"pip install {' '.join(missing_packages)}",
            style="red"
        ))
        return False
    
    return True

if __name__ == "__main__":
    console.print("[bold]🔍 Checking dependencies...[/bold]")
    
    if not check_dependencies():
        sys.exit(1)
    
    console.print("[green]✅ All dependencies found[/green]")
    
    # Run the main orchestrator
    success = asyncio.run(main())
    
    if not success:
        console.print("\n[red]❌ Process completed with errors[/red]")
        sys.exit(1)
    else:
        console.print("\n[green]✅ Process completed successfully![/green]")
        
        # Keep the script running briefly to show final message
        import time
        time.sleep(2)
