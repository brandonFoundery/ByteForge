#!/usr/bin/env python3
"""
UI Style System Menu Integration
Adds UI style comparison options to the main menu system
"""

import os
import sys
import subprocess
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

console = Console()

class UIStyleMenuIntegration:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.ui_system_path = project_root / "Requirements_Generation_System" / "ui_style_system"
        
    def setup_ui_style_system(self) -> bool:
        """Setup the UI style system (install dependencies, etc.)"""
        
        console.print("\n[cyan]🎨 Setting up UI Style Comparison System...[/cyan]")
        
        try:
            # Check if Playwright is installed
            result = subprocess.run([sys.executable, "-c", "import playwright"], 
                                  capture_output=True, text=True)
            
            if result.returncode != 0:
                console.print("[yellow]📦 Playwright not found. Installing...[/yellow]")
                
                # Run the setup script
                setup_script = self.ui_system_path / "setup_playwright.py"
                if setup_script.exists():
                    result = subprocess.run([sys.executable, str(setup_script)], 
                                          cwd=str(self.project_root))
                    if result.returncode != 0:
                        console.print("[red]❌ Failed to setup Playwright[/red]")
                        return False
                else:
                    console.print("[red]❌ Setup script not found[/red]")
                    return False
            else:
                console.print("[green]✅ Playwright already installed[/green]")
            
            console.print("[green]✅ UI Style System ready![/green]")
            return True
            
        except Exception as e:
            console.print(f"[red]❌ Error setting up UI Style System: {e}[/red]")
            return False
    
    def generate_llm_ui_designs(self) -> bool:
        """Generate UI designs using LLM models and start results monitor"""

        console.print("\n[cyan]🤖 Generating LLM UI Designs...[/cyan]")
        console.print("[dim]This will generate 45 unique designs using 5 AI models × 9 reference styles[/dim]")

        try:
            # Check if LLM generation script exists
            llm_script = self.ui_system_path / "run_llm_ui_generation.py"
            if not llm_script.exists():
                console.print(f"[red]❌ LLM generation script not found: {llm_script}[/red]")
                return False

            # Check API keys
            api_keys = {
                'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
                'GOOGLE_API_KEY': os.getenv('GOOGLE_API_KEY'),
                'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY')
            }

            missing_keys = [key for key, value in api_keys.items() if not value]
            if missing_keys:
                console.print(f"[yellow]⚠️  Missing API keys: {', '.join(missing_keys)}[/yellow]")
                console.print("[yellow]Some models may fail. Set environment variables and try again.[/yellow]")

                proceed = console.input("\n[bold]Continue anyway? (y/N): [/bold]").lower()
                if proceed != 'y':
                    return False
            else:
                console.print("[green]✅ All API keys found[/green]")

            # Start the results monitor in a separate process
            console.print("\n[cyan]🌐 Starting results monitor...[/cyan]")
            monitor_url = self.start_results_monitor()

            if monitor_url:
                console.print(f"[green]✅ Results monitor started: {monitor_url}[/green]")
                console.print("[dim]The page will update automatically as designs are generated[/dim]")

            # Run the LLM generation
            console.print("\n[cyan]🚀 Starting LLM generation process...[/cyan]")
            result = subprocess.run([sys.executable, str(llm_script)],
                                  cwd=str(self.ui_system_path),
                                  text=True, encoding='utf-8', errors='replace')

            if result.returncode == 0:
                console.print("\n[green]✅ LLM generation completed successfully![/green]")
                console.print("[cyan]Check the results monitor for generated designs[/cyan]")
                return True
            else:
                console.print("\n[red]❌ LLM generation failed[/red]")
                console.print("Check the console output above for details")
                return False

        except Exception as e:
            console.print(f"[red]❌ Error running LLM generation: {e}[/red]")
            return False

    def start_results_monitor(self) -> str:
        """Start the live results monitor and return the URL"""

        try:
            # Create live comparison viewer
            from live_comparison_viewer import LiveComparisonViewer

            live_viewer = LiveComparisonViewer(self.project_root)
            live_viewer.create_and_open_live_page()

            # Return the URL
            live_page_path = self.ui_system_path / "live_comparison.html"
            if live_page_path.exists():
                return f"file:///{live_page_path.absolute()}"
            else:
                return "http://localhost:8000"  # Fallback

        except Exception as e:
            console.print(f"[yellow]⚠️  Could not start results monitor: {e}[/yellow]")
            console.print("[dim]You can manually open the results page later[/dim]")
            return None
    
    def create_review_interface(self) -> Path:
        """Create the HTML review interface"""
        
        console.print("\n[cyan]🌐 Creating Review Interface...[/cyan]")
        
        try:
            review_script = self.ui_system_path / "review_generator.py"
            if not review_script.exists():
                console.print(f"[red]❌ Review generator not found: {review_script}[/red]")
                return None
            
            # Run the review generator
            result = subprocess.run([sys.executable, str(review_script)],
                                  cwd=str(self.project_root),
                                  capture_output=True, text=True, encoding='utf-8', errors='replace')
            
            if result.returncode == 0:
                # Extract the path from the output
                output_lines = result.stdout.strip().split('\n')
                for line in output_lines:
                    if "Review interface generated:" in line:
                        path_str = line.split("Review interface generated: ")[1]
                        review_path = Path(path_str)
                        console.print(f"[green]✅ Review interface created: {review_path.name}[/green]")
                        return review_path
                
                # Fallback - assume standard path
                review_path = self.ui_system_path / "review" / "ui_style_comparison.html"
                if review_path.exists():
                    console.print(f"[green]✅ Review interface created: {review_path.name}[/green]")
                    return review_path
                else:
                    console.print("[yellow]⚠️  Review interface may have been created but path not found[/yellow]")
                    return None
            else:
                console.print("[red]❌ Failed to create review interface[/red]")
                console.print(f"Error: {result.stderr}")
                return None
                
        except Exception as e:
            console.print(f"[red]❌ Error creating review interface: {e}[/red]")
            return None
    
    def open_review_interface(self, review_path: Path = None) -> bool:
        """Open the review interface in the default browser"""
        
        if review_path is None:
            review_path = self.ui_system_path / "review" / "ui_style_comparison.html"
        
        if not review_path.exists():
            console.print(f"[red]❌ Review interface not found: {review_path}[/red]")
            return False
        
        try:
            # Open in default browser
            if sys.platform.startswith('win'):
                os.startfile(str(review_path.absolute()))
            elif sys.platform.startswith('darwin'):  # macOS
                subprocess.run(['open', str(review_path.absolute())])
            else:  # Linux
                subprocess.run(['xdg-open', str(review_path.absolute())])
            
            console.print(f"[green]🌐 Review interface opened in browser![/green]")
            console.print(f"[dim]File: {review_path.absolute()}[/dim]")
            return True
            
        except Exception as e:
            console.print(f"[red]❌ Error opening review interface: {e}[/red]")
            console.print(f"[yellow]You can manually open: {review_path.absolute()}[/yellow]")
            return False
    
    def run_full_ui_style_workflow(self) -> bool:
        """Run the complete UI style comparison workflow"""
        
        console.print(Panel.fit(
            "[bold]🎨 UI Style Comparison Workflow[/bold]\n"
            "Generate 9 different UI themes and create a review interface",
            style="cyan"
        ))
        
        # Step 1: Setup
        if not self.setup_ui_style_system():
            return False
        
        # Step 2: Generate LLM designs
        if not self.generate_llm_ui_designs():
            console.print("[yellow]⚠️  LLM generation failed, but continuing with review interface...[/yellow]")
        
        # Step 3: Create review interface
        review_path = self.create_review_interface()
        if review_path is None:
            console.print("[red]❌ Failed to create review interface[/red]")
            return False
        
        # Step 4: Open review interface
        if Confirm.ask("\n🌐 Open review interface in browser?", default=True):
            self.open_review_interface(review_path)
        
        console.print("\n[bold green]🎉 UI Style Comparison Workflow Complete![/bold green]")
        console.print(f"[dim]Review interface: {review_path.absolute()}[/dim]")
        
        return True

def handle_ui_style_menu_choice(choice: str, project_root: Path) -> bool:
    """Handle UI style menu choices"""

    try:
        integration = UIStyleMenuIntegration(project_root)
    except Exception as e:
        console.print(f"[red]Error creating UIStyleMenuIntegration: {e}[/red]")
        return False

    if choice == "17":  # Generate LLM UI Designs
        console.print(Panel.fit(
            "[bold]🤖 Generate LLM UI Designs[/bold]\n"
            "Generate 45 unique designs using AI models with automatic results monitoring",
            style="blue"
        ))

        if not integration.setup_ui_style_system():
            return False

        return integration.generate_llm_ui_designs()
    
    elif choice == "18":  # View UI Style Comparison
        console.print(Panel.fit(
            "[bold]🌐 View UI Style Comparison[/bold]\n"
            "Open the review interface to compare all UI styles",
            style="green"
        ))
        
        # Try to create/update review interface first
        review_path = integration.create_review_interface()
        
        # Open the interface
        return integration.open_review_interface(review_path)
    
    elif choice == "19":  # Full UI Style Workflow
        return integration.run_full_ui_style_workflow()
    
    return False

def get_ui_style_menu_options() -> str:
    """Get the UI style menu options to add to the main menu"""

    return """  17. [bold magenta]🤖 Generate LLM UI Designs[/bold magenta]
  18. [bold cyan]🌐 View UI Style Comparison[/bold cyan]
  19. [bold yellow]🎯 Full UI Style Workflow[/bold yellow]"""

def main():
    """Test the UI style menu integration"""
    
    project_root = Path(__file__).parent.parent.parent
    
    console.print(Panel.fit(
        "[bold]🎨 UI Style System - Menu Integration Test[/bold]\n"
        "Testing the UI style comparison system",
        style="cyan"
    ))
    
    console.print("\n[bold]Available Options:[/bold]")
    console.print(get_ui_style_menu_options())
    
    choice = console.input("\n[bold]Select option (17-19): [/bold]")

    if choice in ["17", "18", "19"]:
        success = handle_ui_style_menu_choice(choice, project_root)
        if success:
            console.print("\n[green]✅ Operation completed successfully![/green]")
        else:
            console.print("\n[red]❌ Operation failed![/red]")
    else:
        console.print("[red]Invalid choice[/red]")

if __name__ == "__main__":
    main()
