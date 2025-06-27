"""
Application Template Manager

This module manages application templates and provides initialization
capabilities for new AI-driven application development projects.
"""

import shutil
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import yaml
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.panel import Panel

console = Console()

class TemplateManager:
    """Manages application templates for AI-driven development."""
    
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.templates_path = base_path / "Application_Templates"
        self.artifacts_path = base_path / "Requirements_Artifacts"
        
    def list_available_templates(self) -> List[Dict[str, Any]]:
        """List all available application templates."""
        templates = []
        
        if not self.templates_path.exists():
            return templates
            
        for template_dir in self.templates_path.iterdir():
            if template_dir.is_dir() and template_dir.name != "__pycache__":
                template_info = self._load_template_info(template_dir)
                templates.append(template_info)
                
        return templates
    
    def display_template_catalog(self):
        """Display available templates in a formatted table."""
        templates = self.list_available_templates()
        
        if not templates:
            console.print("[yellow]No application templates found.[/yellow]")
            console.print("Create templates in the Application_Templates directory.")
            return
            
        console.print("\n[bold cyan]📋 Available Application Templates[/bold cyan]")
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID", style="cyan", width=8)
        table.add_column("Template", style="green", width=20)
        table.add_column("Description", style="white", width=50)
        table.add_column("Features", style="yellow", width=30)
        
        for i, template in enumerate(templates, 1):
            features = ", ".join(template.get("features", [])[:3])
            if len(template.get("features", [])) > 3:
                features += "..."
                
            table.add_row(
                str(i),
                template["name"],
                template["description"][:47] + "..." if len(template["description"]) > 50 else template["description"],
                features
            )
            
        console.print(table)
        
    def initialize_project_from_template(self, template_name: str, project_name: str) -> bool:
        """Initialize a new project from a template."""
        template_path = self.templates_path / template_name
        
        if not template_path.exists():
            console.print(f"[red]❌ Template '{template_name}' not found.[/red]")
            return False
            
        console.print(f"\n[cyan]🚀 Initializing project '{project_name}' from template '{template_name}'...[/cyan]")
        
        # Create project directory structure
        project_path = self.base_path.parent / project_name
        if project_path.exists():
            if not Confirm.ask(f"Project directory '{project_name}' already exists. Overwrite?"):
                return False
            shutil.rmtree(project_path)
            
        project_path.mkdir(parents=True)
        
        # Copy template structure
        self._copy_template_structure(template_path, project_path)
        
        # Copy and customize requirements artifacts
        self._initialize_requirements_artifacts(template_path, project_path, project_name)
        
        # Create project configuration
        self._create_project_config(project_path, project_name, template_name)
        
        console.print(f"[green]✅ Project '{project_name}' initialized successfully![/green]")
        console.print(f"[dim]Project location: {project_path}[/dim]")
        
        return True
    
    def interactive_template_selection(self) -> Optional[str]:
        """Interactive template selection process."""
        templates = self.list_available_templates()
        
        if not templates:
            console.print("[red]❌ No templates available.[/red]")
            return None
            
        self.display_template_catalog()
        
        while True:
            try:
                choice = Prompt.ask("\nSelect template by ID", default="1")
                template_id = int(choice) - 1
                
                if 0 <= template_id < len(templates):
                    selected_template = templates[template_id]
                    
                    # Show template details
                    self._display_template_details(selected_template)
                    
                    if Confirm.ask(f"Use template '{selected_template['name']}'?"):
                        return selected_template["name"]
                else:
                    console.print("[red]Invalid selection. Please try again.[/red]")
                    
            except ValueError:
                console.print("[red]Please enter a valid number.[/red]")
            except KeyboardInterrupt:
                console.print("\n[yellow]Template selection cancelled.[/yellow]")
                return None
                
    def _load_template_info(self, template_dir: Path) -> Dict[str, Any]:
        """Load template information from directory."""
        template_info = {
            "name": template_dir.name,
            "path": str(template_dir),
            "description": "No description available",
            "features": [],
            "industry_variations": [],
            "complexity": "Medium"
        }
        
        # Try to load template metadata
        metadata_file = template_dir / "template_metadata.yaml"
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = yaml.safe_load(f)
                    template_info.update(metadata)
            except Exception as e:
                console.print(f"[yellow]Warning: Could not load metadata for {template_dir.name}: {e}[/yellow]")
                
        # Extract features from requirements if metadata not available
        if not template_info["features"]:
            template_info["features"] = self._extract_features_from_template(template_dir)
            
        return template_info
    
    def _extract_features_from_template(self, template_dir: Path) -> List[str]:
        """Extract features from template requirements."""
        features = []
        
        # Look for functional requirements
        req_files = list((template_dir / "requirements_template" / "detailed_specs").glob("*.md"))
        
        for req_file in req_files:
            try:
                with open(req_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Extract feature names from FR- lines
                lines = content.split('\n')
                for line in lines:
                    if '| FR-' in line or '| REQ-FUNC-' in line:
                        parts = [part.strip() for part in line.split('|')]
                        if len(parts) >= 3:
                            feature_name = parts[2].replace('**', '').strip()
                            if feature_name and feature_name not in features:
                                features.append(feature_name)
                                
            except Exception:
                continue
                
        return features[:10]  # Limit to first 10 features
    
    def _copy_template_structure(self, template_path: Path, project_path: Path):
        """Copy template directory structure to project."""
        # Copy core application structure
        for item in template_path.iterdir():
            if item.name not in ["requirements_template"]:  # Skip requirements, we'll handle separately
                if item.is_dir():
                    shutil.copytree(item, project_path / item.name)
                else:
                    shutil.copy2(item, project_path / item.name)
                    
        # Create standard project directories
        (project_path / "Requirements_Generation_System").mkdir(exist_ok=True)
        (project_path / "generated_documents").mkdir(exist_ok=True)
        (project_path / "logs").mkdir(exist_ok=True)
        
    def _initialize_requirements_artifacts(self, template_path: Path, project_path: Path, project_name: str):
        """Initialize requirements artifacts from template."""
        template_req_path = template_path / "requirements_template"
        project_req_path = project_path / "Requirements_Artifacts"
        
        if template_req_path.exists():
            shutil.copytree(template_req_path, project_req_path)
            
            # Customize template files with project name
            self._customize_template_files(project_req_path, project_name)
            
    def _customize_template_files(self, req_path: Path, project_name: str):
        """Customize template files with project-specific information."""
        # Find all markdown files and replace placeholders
        for md_file in req_path.rglob("*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Replace common placeholders
                content = content.replace("{PROJECT_NAME}", project_name)
                content = content.replace("{APP_NAME}", project_name)
                content = content.replace("[Your App Name]", project_name)
                
                with open(md_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
            except Exception as e:
                console.print(f"[yellow]Warning: Could not customize {md_file}: {e}[/yellow]")
                
    def _create_project_config(self, project_path: Path, project_name: str, template_name: str):
        """Create project configuration file."""
        config = {
            "project": {
                "name": project_name,
                "template": template_name,
                "created_at": str(Path().cwd()),
                "version": "1.0.0"
            },
            "ai_generation": {
                "enhanced_artifacts": True,
                "template_based": True,
                "fidelity_mode": "high"
            }
        }
        
        config_file = project_path / "project_config.yaml"
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, indent=2)
            
    def _display_template_details(self, template: Dict[str, Any]):
        """Display detailed template information."""
        details = f"""
[bold]Template:[/bold] {template['name']}
[bold]Description:[/bold] {template['description']}
[bold]Complexity:[/bold] {template.get('complexity', 'Medium')}

[bold]Key Features:[/bold]
{chr(10).join(f"• {feature}" for feature in template.get('features', [])[:8])}

[bold]Industry Variations:[/bold]
{chr(10).join(f"• {variation}" for variation in template.get('industry_variations', [])[:5]) if template.get('industry_variations') else '• Standard implementation'}
"""
        
        console.print(Panel(details, title="Template Details", border_style="cyan"))

def create_new_project_interactive(base_path: Path) -> Optional[str]:
    """Interactive new project creation process."""
    console.print("\n[bold cyan]🚀 AI-Driven Application Builder[/bold cyan]")
    console.print("Create a new application using proven templates and AI generation.")
    
    template_manager = TemplateManager(base_path)
    
    # Select template
    template_name = template_manager.interactive_template_selection()
    if not template_name:
        return None
        
    # Get project name
    while True:
        project_name = Prompt.ask("\nEnter project name")
        if project_name and project_name.replace('_', '').replace('-', '').isalnum():
            break
        console.print("[red]Please enter a valid project name (alphanumeric, hyphens, underscores only).[/red]")
        
    # Initialize project
    if template_manager.initialize_project_from_template(template_name, project_name):
        console.print(f"\n[green]🎉 Project '{project_name}' is ready for AI-driven development![/green]")
        console.print(f"[dim]Next steps:[/dim]")
        console.print(f"[dim]1. cd {project_name}[/dim]")
        console.print(f"[dim]2. Customize requirements in Requirements_Artifacts/[/dim]")
        console.print(f"[dim]3. Run python Requirements_Generation_System/run_generation.py[/dim]")
        return project_name
    
    return None