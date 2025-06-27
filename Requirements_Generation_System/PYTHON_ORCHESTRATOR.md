# Requirements Generation System - Python Orchestrator

This document contains the complete Python code for automating the requirements document generation process using LLMs.

## Installation Requirements

Create a `requirements.txt` file with:

```txt
# Core dependencies
openai>=1.0.0
anthropic>=0.7.0
pyyaml>=6.0
jinja2>=3.1.0
pydantic>=2.0.0
rich>=13.0.0
asyncio>=3.4.3
aiofiles>=23.0.0
python-dotenv>=1.0.0
networkx>=3.0
matplotlib>=3.8.0
tqdm>=4.65.0
```

## Main Orchestrator Code

Create `orchestrator.py`:

```python
import os
import yaml
import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging

from openai import OpenAI
from anthropic import Anthropic
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree
from jinja2 import Template
from pydantic import BaseModel, Field
import networkx as nx
import matplotlib.pyplot as plt
from tqdm import tqdm
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize rich console for beautiful output
console = Console()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('requirements_generation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DocumentStatus(Enum):
    """Status of document generation"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    GENERATED = "generated"
    REFINED = "refined"
    VALIDATED = "validated"
    FAILED = "failed"


class DocumentType(Enum):
    """Types of documents in the system"""
    BRD = "Business Requirements Document"
    PRD = "Product Requirements Document"
    FRD = "Functional Requirements Document"
    NFRD = "Non-Functional Requirements Document"
    DRD = "Data Requirements Document"
    DB_SCHEMA = "Database Schema"
    TRD = "Technical Requirements Document"
    API_SPEC = "API OpenAPI Specification"
    TEST_PLAN = "Test Plan and Test Cases"
    RTM = "Requirements Traceability Matrix"


@dataclass
class Document:
    """Represents a requirements document"""
    doc_type: DocumentType
    status: DocumentStatus = DocumentStatus.NOT_STARTED
    content: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[DocumentType] = field(default_factory=list)
    prompt_template: Optional[str] = None
    generated_at: Optional[datetime] = None
    refined_count: int = 0
    validation_errors: List[str] = field(default_factory=list)


class RequirementsOrchestrator:
    """Main orchestrator for requirements generation"""
    
    def __init__(self, project_name: str, base_path: Path):
        self.project_name = project_name
        self.base_path = base_path
        self.output_path = base_path / "generated_documents"
        self.prompts_path = base_path / "Requirements_Generation_Prompts"
        self.requirements_path = base_path / "Requirements"
        
        # Initialize LLM clients
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
        # Document registry
        self.documents: Dict[DocumentType, Document] = {}
        self._initialize_documents()
        
        # Dependency graph
        self.dependency_graph = self._build_dependency_graph()
        
        # Create output directory
        self.output_path.mkdir(parents=True, exist_ok=True)
        
    def _initialize_documents(self):
        """Initialize document registry with dependencies"""
        doc_configs = [
            (DocumentType.BRD, [], "01_BRD.md"),
            (DocumentType.PRD, [DocumentType.BRD], "02_PRD.md"),
            (DocumentType.FRD, [DocumentType.PRD, DocumentType.BRD], "04_FRD.md"),
            (DocumentType.NFRD, [DocumentType.PRD, DocumentType.FRD, DocumentType.BRD], "05_NFRD.md"),
            (DocumentType.DRD, [DocumentType.FRD, DocumentType.PRD], "07_DRD.md"),
            (DocumentType.DB_SCHEMA, [DocumentType.DRD, DocumentType.TRD], "08_DB_Schema.md"),
            (DocumentType.TRD, [DocumentType.FRD, DocumentType.NFRD, DocumentType.DRD], "09_TRD.md"),
            (DocumentType.API_SPEC, [DocumentType.FRD, DocumentType.DRD, DocumentType.TRD], "10_API_OpenAPI.md"),
            (DocumentType.TEST_PLAN, [DocumentType.FRD, DocumentType.NFRD, DocumentType.PRD], "20_Test_Plan.md"),
            (DocumentType.RTM, [DocumentType.BRD, DocumentType.PRD, DocumentType.FRD, 
                               DocumentType.NFRD, DocumentType.TRD, DocumentType.TEST_PLAN], "24_RTM.md"),
        ]
        
        for doc_type, deps, prompt_file in doc_configs:
            prompt_path = self.prompts_path / prompt_file
            prompt_template = prompt_path.read_text() if prompt_path.exists() else None
            
            self.documents[doc_type] = Document(
                doc_type=doc_type,
                dependencies=deps,
                prompt_template=prompt_template
            )
    
    def _build_dependency_graph(self) -> nx.DiGraph:
        """Build directed graph of document dependencies"""
        G = nx.DiGraph()
        
        for doc_type, doc in self.documents.items():
            G.add_node(doc_type.name)
            for dep in doc.dependencies:
                G.add_edge(dep.name, doc_type.name)
        
        return G
    
    def visualize_dependencies(self, output_file: str = "dependency_graph.png"):
        """Visualize document dependencies"""
        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(self.dependency_graph, k=2, iterations=50)
        
        # Color nodes by status
        node_colors = []
        for node in self.dependency_graph.nodes():
            doc_type = DocumentType[node]
            status = self.documents[doc_type].status
            if status == DocumentStatus.VALIDATED:
                node_colors.append('#90EE90')  # Light green
            elif status == DocumentStatus.GENERATED:
                node_colors.append('#87CEEB')  # Sky blue
            elif status == DocumentStatus.IN_PROGRESS:
                node_colors.append('#FFD700')  # Gold
            elif status == DocumentStatus.FAILED:
                node_colors.append('#FF6B6B')  # Light red
            else:
                node_colors.append('#D3D3D3')  # Light gray
        
        nx.draw(self.dependency_graph, pos, 
                node_color=node_colors,
                node_size=3000,
                font_size=10,
                font_weight='bold',
                arrows=True,
                edge_color='gray',
                with_labels=True)
        
        plt.title(f"Document Generation Dependencies - {self.project_name}")
        plt.tight_layout()
        plt.savefig(self.output_path / output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        console.print(f"[green]Dependency graph saved to {self.output_path / output_file}[/green]")
    
    def get_generation_order(self) -> List[DocumentType]:
        """Get topological order for document generation"""
        try:
            order = list(nx.topological_sort(self.dependency_graph))
            return [DocumentType[name] for name in order]
        except nx.NetworkXUnfeasible:
            logger.error("Circular dependency detected in document dependencies")
            raise
    
    async def gather_context(self, doc_type: DocumentType) -> Dict[str, str]:
        """Gather context from existing requirements and generated documents"""
        context = {
            "project_name": self.project_name,
            "generation_date": datetime.now().strftime("%Y-%m-%d"),
        }
        
        # Add dependency documents
        for dep_type in self.documents[doc_type].dependencies:
            dep_doc = self.documents[dep_type]
            if dep_doc.status in [DocumentStatus.GENERATED, DocumentStatus.REFINED, DocumentStatus.VALIDATED]:
                context[dep_type.name.lower()] = dep_doc.content
        
        # Add existing requirements based on document type
        if doc_type == DocumentType.BRD:
            # Load master PRD and other business context
            master_prd_path = self.requirements_path / "consolidated-requirements" / "master-prd.md"
            if master_prd_path.exists():
                context["master_prd"] = master_prd_path.read_text()
            
            # Load video annotations
            video_path = self.requirements_path / "Video Annotations"
            if video_path.exists():
                annotations = []
                for file in video_path.glob("*.markdown"):
                    annotations.append(f"## {file.stem}\n{file.read_text()}")
                context["video_annotations"] = "\n\n".join(annotations)
        
        elif doc_type == DocumentType.DRD:
            # Load existing database schemas
            db_schemas = []
            for schema_path in self.requirements_path.rglob("DB-SCHEMA.sql"):
                db_schemas.append(f"-- From {schema_path.relative_to(self.requirements_path)}\n{schema_path.read_text()}")
            context["existing_schemas"] = "\n\n".join(db_schemas)
        
        return context
    
    async def generate_document(self, doc_type: DocumentType, use_anthropic: bool = True) -> str:
        """Generate a document using LLM"""
        doc = self.documents[doc_type]
        
        if not doc.prompt_template:
            raise ValueError(f"No prompt template found for {doc_type.value}")
        
        # Update status
        doc.status = DocumentStatus.IN_PROGRESS
        console.print(f"\n[yellow]Generating {doc_type.value}...[/yellow]")
        
        # Gather context
        context = await self.gather_context(doc_type)
        
        # Extract the main prompt from template
        prompt_parts = doc.prompt_template.split("```markdown")
        if len(prompt_parts) > 1:
            main_prompt = prompt_parts[1].split("```")[0]
        else:
            main_prompt = doc.prompt_template
        
        # Build the full prompt
        full_prompt = f"""
{main_prompt}

## Context Provided:

Project Name: {context.get('project_name', 'Unknown Project')}
Generation Date: {context.get('generation_date', 'Unknown')}

"""
        
        # Add dependency documents
        for key, value in context.items():
            if key not in ['project_name', 'generation_date'] and value:
                full_prompt += f"\n### {key.upper().replace('_', ' ')}:\n{value[:5000]}...\n"
        
        try:
            if use_anthropic:
                response = await self._generate_with_anthropic(full_prompt)
            else:
                response = await self._generate_with_openai(full_prompt)
            
            doc.content = response
            doc.status = DocumentStatus.GENERATED
            doc.generated_at = datetime.now()
            
            # Save document
            await self.save_document(doc_type)
            
            console.print(f"[green]✓ Generated {doc_type.value}[/green]")
            return response
            
        except Exception as e:
            logger.error(f"Failed to generate {doc_type.value}: {str(e)}")
            doc.status = DocumentStatus.FAILED
            doc.validation_errors.append(str(e))
            raise
    
    async def _generate_with_anthropic(self, prompt: str) -> str:
        """Generate content using Anthropic Claude"""
        message = self.anthropic_client.messages.create(
            model="claude-opus-4",
            max_tokens=4000,
            temperature=0.7,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return message.content[0].text
    
    async def _generate_with_openai(self, prompt: str) -> str:
        """Generate content using OpenAI GPT"""
        response = self.openai_client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are an expert requirements analyst and technical writer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4000
        )
        return response.choices[0].message.content
    
    async def refine_document(self, doc_type: DocumentType, refinement_round: int = 1):
        """Refine a generated document"""
        doc = self.documents[doc_type]
        
        if doc.status not in [DocumentStatus.GENERATED, DocumentStatus.REFINED]:
            raise ValueError(f"Document {doc_type.value} must be generated before refinement")
        
        console.print(f"\n[yellow]Refining {doc_type.value} (Round {refinement_round})...[/yellow]")
        
        # Get refinement prompt from template
        refinement_prompts = []
        if "Refinement Round" in doc.prompt_template:
            parts = doc.prompt_template.split("### Refinement Round")
            for i in range(1, len(parts)):
                if str(refinement_round) in parts[i][:5]:
                    refinement_prompts.append(parts[i].split("```")[0])
        
        if not refinement_prompts:
            console.print(f"[yellow]No refinement prompt found for round {refinement_round}[/yellow]")
            return
        
        refinement_prompt = f"""
Please refine the following {doc_type.value}:

{doc.content}

{refinement_prompts[0]}
"""
        
        try:
            refined_content = await self._generate_with_anthropic(refinement_prompt)
            doc.content = refined_content
            doc.refined_count += 1
            doc.status = DocumentStatus.REFINED
            
            await self.save_document(doc_type)
            console.print(f"[green]✓ Refined {doc_type.value} (Round {refinement_round})[/green]")
            
        except Exception as e:
            logger.error(f"Failed to refine {doc_type.value}: {str(e)}")
            raise
    
    async def validate_document(self, doc_type: DocumentType) -> bool:
        """Validate a generated document"""
        doc = self.documents[doc_type]
        
        if doc.status not in [DocumentStatus.GENERATED, DocumentStatus.REFINED]:
            return False
        
        console.print(f"\n[yellow]Validating {doc_type.value}...[/yellow]")
        
        validation_errors = []
        
        # Check for required sections based on document type
        if doc_type == DocumentType.BRD:
            required_sections = ["Executive Summary", "Business Context", "Business Requirements"]
            for section in required_sections:
                if section not in doc.content:
                    validation_errors.append(f"Missing required section: {section}")
        
        # Check for traceability IDs
        if doc_type != DocumentType.BRD:  # BRD is the root
            id_prefix = doc_type.name.replace("_", "-")
            if f"{id_prefix}-" not in doc.content:
                validation_errors.append(f"No traceability IDs found (expected {id_prefix}-XXX)")
        
        # Check for upstream references
        for dep_type in doc.dependencies:
            dep_id_prefix = dep_type.name.replace("_", "-")
            if dep_id_prefix not in doc.content:
                validation_errors.append(f"No references to upstream document {dep_type.value}")
        
        doc.validation_errors = validation_errors
        
        if not validation_errors:
            doc.status = DocumentStatus.VALIDATED
            console.print(f"[green]✓ Validated {doc_type.value}[/green]")
            return True
        else:
            console.print(f"[red]✗ Validation failed for {doc_type.value}:[/red]")
            for error in validation_errors:
                console.print(f"  [red]- {error}[/red]")
            return False
    
    async def save_document(self, doc_type: DocumentType):
        """Save document to file"""
        doc = self.documents[doc_type]
        
        if not doc.content:
            return
        
        filename = f"{doc_type.name.lower()}.md"
        filepath = self.output_path / filename
        
        # Add metadata header
        metadata = {
            "id": doc_type.name,
            "title": doc_type.value,
            "version": "1.0",
            "status": doc.status.value,
            "generated_at": doc.generated_at.isoformat() if doc.generated_at else None,
            "refined_count": doc.refined_count,
            "dependencies": [dep.name for dep in doc.dependencies]
        }
        
        content = f"""---
{yaml.dump(metadata, default_flow_style=False)}---

{doc.content}
"""
        
        filepath.write_text(content)
        logger.info(f"Saved {doc_type.value} to {filepath}")
    
    def generate_status_report(self) -> str:
        """Generate a status report of all documents"""
        table = Table(title=f"Requirements Generation Status - {self.project_name}")
        
        table.add_column("Document", style="cyan", no_wrap=True)
        table.add_column("Status", style="magenta")
        table.add_column("Generated At", style="green")
        table.add_column("Refined", style="yellow")
        table.add_column("Errors", style="red")
        
        for doc_type, doc in self.documents.items():
            status_emoji = {
                DocumentStatus.NOT_STARTED: "⏸️",
                DocumentStatus.IN_PROGRESS: "🔄",
                DocumentStatus.GENERATED: "✅",
                DocumentStatus.REFINED: "🔧",
                DocumentStatus.VALIDATED: "✨",
                DocumentStatus.FAILED: "❌"
            }
            
            status = f"{status_emoji.get(doc.status, '')} {doc.status.value}"
            generated_at = doc.generated_at.strftime("%Y-%m-%d %H:%M") if doc.generated_at else "N/A"
            refined = f"{doc.refined_count} times" if doc.refined_count > 0 else "No"
            errors = len(doc.validation_errors)
            
            table.add_row(
                doc_type.value,
                status,
                generated_at,
                refined,
                str(errors) if errors > 0 else "None"
            )
        
        console.print(table)
        
        # Save status report
        report_path = self.output_path / "status_report.txt"
        with open(report_path, "w") as f:
            from rich.console import Console
            file_console = Console(file=f)
            file_console.print(table)
        
        return str(table)
    
    def generate_rtm_data(self) -> Dict[str, Any]:
        """Generate data structure for RTM"""
        rtm_data = {
            "project_name": self.project_name,
            "generated_at": datetime.now().isoformat(),
            "documents": {},
            "traceability_links": []
        }
        
        for doc_type, doc in self.documents.items():
            if doc.status in [DocumentStatus.GENERATED, DocumentStatus.REFINED, DocumentStatus.VALIDATED]:
                # Extract requirement IDs from content
                import re
                id_pattern = rf"{doc_type.name.replace('_', '-')}-\d+"
                ids = re.findall(id_pattern, doc.content) if doc.content else []
                
                rtm_data["documents"][doc_type.name] = {
                    "title": doc_type.value,
                    "status": doc.status.value,
                    "requirement_ids": list(set(ids)),
                    "dependencies": [dep.name for dep in doc.dependencies]
                }
        
        return rtm_data
    
    async def run(self, skip_existing: bool = False, max_refinements: int = 2):
        """Run the complete document generation process"""
        console.print(Panel.fit(
            f"[bold cyan]Requirements Generation System[/bold cyan]\n"
            f"Project: {self.project_name}\n"
            f"Output: {self.output_path}",
            title="Starting Generation Process"
        ))
        
        # Visualize initial state
        self.visualize_dependencies("initial_state.png")
        
        # Get generation order
        generation_order = self.get_generation_order()
        console.print(f"\n[cyan]Generation order: {' → '.join([dt.name for dt in generation_order])}[/cyan]\n")
        
        # Generate documents in order
        for doc_type in generation_order:
            doc = self.documents[doc_type]
            
            # Skip if already generated and skip_existing is True
            if skip_existing and doc.status != DocumentStatus.NOT_STARTED:
                console.print(f"[yellow]Skipping {doc_type.value} (already generated)[/yellow]")
                continue
            
            try:
                # Generate document
                await self.generate_document(doc_type)
                
                # Refine document
                for i in range(1, max_refinements + 1):
                    await self.refine_document(doc_type, i)
                
                # Validate document
                await self.validate_document(doc_type)
                
                # Update visualization after each document
                self.visualize_dependencies(f"state_after_{doc_type.name.lower()}.png")
                
            except Exception as e:
                console.print(f"[red]Failed to process {doc_type.value}: {str(e)}[/red]")
                logger.error(f"Document generation failed for {doc_type.value}", exc_info=True)
                
                # Ask user if they want to continue
                if input(f"\nContinue with remaining documents? (y/n): ").lower() != 'y':
                    break
        
        # Generate final status report
        console.print("\n" + "="*80 + "\n")
        self.generate_status_report()
        
        # Generate RTM data
        rtm_data = self.generate_rtm_data()
        rtm_path = self.output_path / "rtm_data.json"
        rtm_path.write_text(json.dumps(rtm_data, indent=2))
        console.print(f"\n[green]RTM data saved to {rtm_path}[/green]")
        
        # Final visualization
        self.visualize_dependencies("final_state.png")
        
        console.print(Panel.fit(
            "[bold green]Generation Process Complete![/bold green]\n"
            f"Documents saved to: {self.output_path}",
            title="Success"
        ))


async def main():
    """Main entry point"""
    # Configuration
    project_name = "FY.WB.Midway"
    base_path = Path("d:/Repository/@Clients/FY.WB.Midway")
    
    # Create orchestrator
    orchestrator = RequirementsOrchestrator(project_name, base_path)
    
    # Run the generation process
    await orchestrator.run(skip_existing=False, max_refinements=2)


if __name__ == "__main__":
    asyncio.run(main())
```

## Progress Monitor Script

Create `monitor.py`:

```python
import time
import json
from pathlib import Path
from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque

console = Console()


class GenerationMonitor:
    """Real-time monitor for document generation progress"""
    
    def __init__(self, output_path: Path):
        self.output_path = output_path
        self.history = deque(maxlen=100)
        
    def get_status(self):
        """Get current status of all documents"""
        status = {}
        
        for doc_file in self.output_path.glob("*.md"):
            if doc_file.name == "status_report.txt":
                continue
                
            # Read metadata from file
            content = doc_file.read_text()
            if content.startswith("---"):
                metadata_end = content.find("---", 3)
                if metadata_end > 0:
                    import yaml
                    metadata = yaml.safe_load(content[3:metadata_end])
                    status[metadata.get("id", doc_file.stem)] = {
                        "title": metadata.get("title", "Unknown"),
                        "status": metadata.get("status", "unknown"),
                        "generated_at": metadata.get("generated_at", "N/A"),
                        "refined_count": metadata.get("refined_count", 0),
                        "file_size": doc_file.stat().st_size
                    }
        
        return status
    
    def create_status_table(self):
        """Create a rich table showing current status"""
        table = Table(title=f"Document Generation Progress - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        table.add_column("Document", style="cyan", no_wrap=True)
        table.add_column("Status", style="magenta")
        table.add_column("Size", style="green")
        table.add_column("Refined", style="yellow")
        table.add_column("Generated At", style="blue")
        
        status = self.get_status()
        
        for doc_id, info in sorted(status.items()):
            status_emoji = {
                "not_started": "⏸️",
                "in_progress": "🔄",
                "generated": "✅",
                "refined": "🔧",
                "validated": "✨",
                "failed": "❌"
            }.get(info["status"], "❓")
            
            size_kb = info["file_size"] / 1024
            
            table.add_row(
                info["title"],
                f"{status_emoji} {info['status']}",
                f"{size_kb:.1f} KB",
                str(info["refined_count"]),
                info["generated_at"][:19] if info["generated_at"] != "N/A" else "N/A"
            )
        
        return table
    
    def monitor_live(self, refresh_rate: int = 2):
        """Live monitoring with auto-refresh"""
        with Live(self.create_status_table(), refresh_per_second=1/refresh_rate) as live:
            while True:
                time.sleep(refresh_rate)
                live.update(self.create_status_table())
                
                # Check for completion
                status = self.get_status()
                if all(info["status"] in ["validated", "failed"] for info in status.values()):
                    console.print("\n[bold green]All documents processed![/bold green]")
                    break


def main():
    """Run the monitor"""
    output_path = Path("d:/Repository/@Clients/FY.WB.Midway/generated_documents")
    
    if not output_path.exists():
        console.print(f"[red]Output directory not found: {output_path}[/red]")
        return
    
    monitor = GenerationMonitor(output_path)
    
    console.print("[bold cyan]Starting Document Generation Monitor[/bold cyan]")
    console.print(f"Monitoring: {output_path}\n")
    
    try:
        monitor.monitor_live()
    except KeyboardInterrupt:
        console.print("\n[yellow]Monitor stopped by user[/yellow]")


if __name__ == "__main__":
    main()
```

## Configuration File

Create `config.yaml`:

```yaml
# Requirements Generation System Configuration

project:
  name: "FY.WB.Midway"
  description: "Enterprise Logistics and Payment Platform"
  version: "1.0"

paths:
  base: "d:/Repository/@Clients/FY.WB.Midway"
  prompts: "Requirements_Generation_Prompts"
  requirements: "Requirements"
  output: "generated_documents"

llm:
  primary: "anthropic"  # or "openai"
  models:
    anthropic: "claude-opus-4"
    openai: "o3-mini"
    gemini: "gemini-2.5-pro-preview-06-05"
  
  parameters:
    temperature: 0.7
    max_tokens: 4000
    
generation:
  skip_existing: false
  max_refinements: 2
  validate_after_generation: true
  
  order_override: []  # Leave empty to use dependency order
  
monitoring:
  enable_visualization: true
  refresh_rate: 2  # seconds
  
  export_formats:
    - markdown
    - json
    - pdf  # requires additional dependencies
    
traceability:
  id_patterns:
    BRD: "BRD-{:03d}"
    PRD: "PRD-{:03d}"
    FRD: "FRD-{:03d}"
    NFRD: "NFR-{:03d}"
    DRD: "DRD-{:03d}"
    TRD: "TRD-{:03d}"
    
  link_validation: true
  orphan_detection: true
```

## Utility Scripts

Create `utils.py`:

```python
"""Utility functions for the requirements generation system"""

import re
from typing import List, Dict, Set, Tuple
from pathlib import Path
import yaml
import json
from collections import defaultdict
import networkx as nx
from rich.console import Console

console = Console()


class TraceabilityAnalyzer:
    """Analyze traceability between documents"""
    
    def __init__(self, documents_path: Path):
        self.documents_path = documents_path
        self.id_patterns = {
            "BRD": r"BRD-\d{3}",
            "PRD": r"PRD-\d{3}",
            "FRD": r"FRD-\d{3}",
            "NFRD": r"NFR-\d{3}",
            "DRD": r"DRD-\d{3}",
            "TRD": r"TRD-\d{3}",
            "TC": r"TC-\d{3}"
        }
        
    def extract_ids(self, content: str) -> Dict[str, Set[str]]:
        """Extract all requirement IDs from content"""
        ids = defaultdict(set)
        
        for doc_type, pattern in self.id_patterns.items():
            matches = re.findall(pattern, content)
            ids[doc_type].update(matches)
        
        return dict(ids)
    
    def analyze_document(self, doc_path: Path) -> Dict[str, Any]:
        """Analyze a single document for traceability"""
        content = doc_path.read_text()
        
        # Extract metadata
        metadata = {}
        if content.startswith("---"):
            metadata_end = content.find("---", 3)
            if metadata_end > 0:
                metadata = yaml.safe_load(content[3:metadata_end])
        
        # Extract IDs
        ids = self.extract_ids(content)
        
        # Count references to other documents
        references = defaultdict(int)
        for doc_type, id_set in ids.items():
            if doc_type != metadata.get("id", doc_path.stem).upper():
                references[doc_type] = len(id_set)
        
        return {
            "path": doc_path,
            "metadata": metadata,
            "ids": ids,
            "references": dict(references),
            "total_requirements": sum(len(id_set) for id_set in ids.values())
        }
    
    def build_traceability_graph(self) -> nx.DiGraph:
        """Build a graph of requirement traceability"""
        G = nx.DiGraph()
        
        # Analyze all documents
        analyses = {}
        for doc_path in self.documents_path.glob("*.md"):
            if doc_path.stem not in ["status_report", "README"]:
                analysis = self.analyze_document(doc_path)
                analyses[doc_path.stem] = analysis
        
        # Add nodes
        for doc_name, analysis in analyses.items():
            for doc_type, id_set in analysis["ids"].items():
                for req_id in id_set:
                    G.add_node(req_id, doc_type=doc_type, document=doc_name)
        
        # Add edges based on references
        for doc_name, analysis in analyses.items():
            doc_type = analysis["metadata"].get("id", doc_name).upper()
            doc_ids = analysis["ids"].get(doc_type, set())
            
            for other_type, other_ids in analysis["ids"].items():
                if other_type != doc_type:
                    # Create edges from referenced IDs to this document's IDs
                    for other_id in other_ids:
                        for doc_id in doc_ids:
                            G.add_edge(other_id, doc_id)
        
        return G
    
    def find_orphans(self) -> Dict[str, List[str]]:
        """Find requirements without upstream or downstream links"""
        G = self.build_traceability_graph()
        
        orphans = {
            "no_upstream": [],
            "no_downstream": []
        }
        
        for node in G.nodes():
            if G.in_degree(node) == 0 and not node.startswith("BRD"):
                orphans["no_upstream"].append(node)
            
            if G.out_degree(node) == 0 and not node.startswith("TC"):
                orphans["no_downstream"].append(node)
        
        return orphans
    
    def generate_traceability_report(self) -> str:
        """Generate a comprehensive traceability report"""
        report = ["# Traceability Analysis Report\n"]
        
        # Document analysis
        report.append("## Document Analysis\n")
        
        total_reqs = 0
        for doc_path in sorted(self.documents_path.glob("*.md")):
            if doc_path.stem not in ["status_report", "README"]:
                analysis = self.analyze_document(doc_path)
                report.append(f"### {analysis['metadata'].get('title', doc_path.stem)}")
                report.append(f"- Total requirements: {analysis['total_requirements']}")
                report.append(f"- References: {dict(analysis['references'])}")
                report.append("")
                total_reqs += analysis['total_requirements']
        
        report.append(f"\n**Total requirements across all documents: {total_reqs}**\n")
        
        # Orphan analysis
        orphans = self.find_orphans()
        report.append("## Orphan Analysis\n")
        
        if orphans["no_upstream"]:
            report.append("### Requirements without upstream traceability:")
            for req in sorted(orphans["no_upstream"]):
                report.append(f"- {req}")
            report.append("")
        
        if orphans["no_downstream"]:
            report.append("### Requirements without downstream traceability:")
            for req in sorted(orphans["no_downstream"]):
                report.append(f"- {req}")
            report.append("")
        
        # Graph statistics
        G = self.build_traceability_graph()
        report.append("## Traceability Graph Statistics\n")
        report.append(f"- Total nodes (requirements): {G.number_of_nodes()}")
        report.append(f"- Total edges (traceability links): {G.number_of_edges()}")
        report.append(f"- Average degree: {sum(dict(G.degree()).values()) / G.number_of_nodes():.2f}")
        
        # Find longest paths
        if nx.is_directed_acyclic_graph(G):
            report.append(f"- Graph is acyclic (no circular dependencies)")
            
            # Find longest path
            longest_path = nx.dag_longest_path(G)
            if longest_path:
                report.append(f"- Longest traceability chain: {' → '.join(longest_path)}")
        else:
            report.append(f"- WARNING: Graph contains cycles!")
        
        return "\n".join(report)


def validate_yaml_metadata(file_path: Path) -> List[str]:
    """Validate YAML metadata in a document"""
    errors = []
    content = file_path.read_text()
    
    if not content.startswith("---"):
        errors.append("Missing YAML frontmatter")
        return errors
    
    metadata_end = content.find("---", 3)
    if metadata_end < 0:
        errors.append("Unclosed YAML frontmatter")
        return errors
    
    try:
        metadata = yaml.safe_load(content[3:metadata_end])
        
        # Check required fields
        required_fields = ["id", "title", "version", "status"]
        for field in required_fields:
            if field not in metadata:
                errors.append(f"Missing required field: {field}")
        
        # Validate status
        valid_statuses = ["not_started", "in_progress", "generated", "refined", "validated", "failed"]
        if metadata.get("status") not in valid_statuses:
            errors.append(f"Invalid status: {metadata.get('status')}")
        
    except yaml.YAMLError as e:
        errors.append(f"Invalid YAML: {str(e)}")
    
    return errors


def merge_documents(doc_paths: List[Path], output_path: Path):
    """Merge multiple documents into a single file"""
    merged_content = [
        "# Merged Requirements Documentation",
        f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
        "---\n"
    ]
    
    for doc_path in doc_paths:
        content = doc_path.read_text()
        
        # Extract title from metadata
        title = doc_path.stem
        if content.startswith("---"):
            metadata_end = content.find("---", 3)
            if metadata_end > 0:
                metadata = yaml.safe_load(content[3:metadata_end])
                title = metadata.get("title", title)
                content = content[metadata_end + 3:].strip()
        
        merged_content.append(f"\n\n# {title}\n")
        merged_content.append(content)
    
    output_path.write_text("\n".join(merged_content))
    console.print(f"[green]Merged {len(doc_paths)} documents into {output_path}[/green]")


if __name__ == "__main__":
    # Example usage
    docs_path = Path("generated_documents")
    
    analyzer = TraceabilityAnalyzer(docs_path)
    report = analyzer.generate_traceability_report()
    
    report_path = docs_path / "traceability_report.md"
    report_path.write_text(report)
    console.print(f"[green]Traceability report saved to {report_path}[/green]")
```

## Usage Instructions

1. **Setup Environment**:
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
echo "OPENAI_API_KEY=your-key-here" > .env
echo "ANTHROPIC_API_KEY=your-key-here" >> .env
```

2. **Run the Orchestrator**:
```bash
# Generate all documents
python orchestrator.py

# Monitor progress in another terminal
python monitor.py
```

3. **Analyze Traceability**:
```bash
# Generate traceability report
python utils.py
```

4. **Customize Generation**:
- Edit `config.yaml` to change settings
- Modify document dependencies in `orchestrator.py`
- Add custom validation rules

## Features

1. **Automated Document Generation**:
   - Respects dependencies between documents
   - Handles context gathering from existing requirements
   - Supports both OpenAI and Anthropic APIs

2. **Progress Monitoring**:
   - Real-time status updates
   - Visual dependency graphs
   - Progress tracking with rich console output

3. **Traceability Analysis**:
   - Automatic ID extraction
   - Orphan detection
   - Traceability graph visualization

4. **Quality Assurance**:
   - Document validation
   - Iterative refinement
   - Error handling and recovery

5. **Flexible Configuration**:
   - YAML-based configuration
   - Customizable generation order
   - Skip existing documents option

This system provides a complete automation solution for generating traceable requirements documentation using the prompts we created earlier.