#!/usr/bin/env python3
"""
Apply auto-repair to all existing documents
"""

import asyncio
import sys
import os
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, TaskID

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from orchestrator import RequirementsOrchestrator, DocumentType

console = Console()

async def repair_all_documents():
    """Apply auto-repair to all existing documents"""
    
    console.print("[bold blue]Repairing All Documents[/bold blue]")
    console.print("This will apply auto-repair to all existing documents, regardless of their current status.")
    
    # Set dummy API key for testing
    os.environ["OPENAI_API_KEY"] = "dummy-key-for-testing"
    
    # Initialize orchestrator
    project_name = "FY.WB.Midway"
    base_path = Path("project")
    orchestrator = RequirementsOrchestrator(project_name, base_path, model_provider="openai")
    
    # Load existing documents
    await orchestrator.load_existing_documents()
    
    repaired_count = 0
    failed_count = 0
    
    with Progress() as progress:
        task = progress.add_task("[cyan]Repairing documents...", total=len(DocumentType))
        
        for doc_type in DocumentType:
            progress.update(task, description=f"[cyan]Repairing {doc_type.value}...")
            
            doc = orchestrator.documents[doc_type]
            
            # Load content if not already loaded
            if not doc.content:
                doc_path = base_path / "generated_documents" / f"{doc_type.name.lower()}.md"
                if doc_path.exists():
                    doc.content = doc_path.read_text(encoding='utf-8')
            
            if doc.content:
                try:
                    # Force the document status to allow repair
                    original_status = doc.status
                    doc.status = orchestrator.documents[doc_type].status.__class__.GENERATED
                    
                    # Apply auto-repair
                    console.print(f"\n[yellow]Repairing {doc_type.value}...[/yellow]")
                    repair_success = await orchestrator.validate_and_repair_document(doc_type, max_repair_attempts=5)
                    
                    if repair_success:
                        console.print(f"[green]✓ Successfully repaired {doc_type.value}[/green]")
                        repaired_count += 1
                        
                        # Save the repaired document
                        await orchestrator.save_document(doc_type)
                    else:
                        console.print(f"[red]✗ Could not fully repair {doc_type.value}[/red]")
                        failed_count += 1
                        
                        # Still save it with improvements
                        await orchestrator.save_document(doc_type)
                        
                except Exception as e:
                    console.print(f"[red]✗ Error repairing {doc_type.value}: {str(e)}[/red]")
                    failed_count += 1
            else:
                console.print(f"[yellow]⚠ No content found for {doc_type.value}[/yellow]")
            
            progress.advance(task)
    
    console.print(f"\n[bold]Repair Summary:[/bold]")
    console.print(f"  ✅ Successfully repaired: {repaired_count}")
    console.print(f"  ❌ Failed to repair: {failed_count}")
    console.print(f"  📄 Total processed: {repaired_count + failed_count}")
    
    if repaired_count > 0:
        console.print(f"\n[green]🎉 {repaired_count} documents have been repaired![/green]")
        console.print(f"[yellow]Check the generated_documents folder for the updated files.[/yellow]")

if __name__ == "__main__":
    asyncio.run(repair_all_documents())
