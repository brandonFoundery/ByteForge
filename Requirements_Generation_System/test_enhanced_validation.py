#!/usr/bin/env python3
"""
Test the enhanced validation and auto-repair system on existing documents
"""

import asyncio
import sys
import os
from pathlib import Path
from rich.console import Console
from rich.table import Table

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from orchestrator import RequirementsOrchestrator, DocumentType

console = Console()

async def test_validation():
    """Test validation on all existing documents"""
    
    console.print("[bold blue]Testing Enhanced Validation System[/bold blue]")
    
    # Set dummy API key for testing
    os.environ["OPENAI_API_KEY"] = "dummy-key-for-testing"
    
    # Initialize orchestrator
    project_name = "FY.WB.Midway"
    base_path = Path("project")
    orchestrator = RequirementsOrchestrator(project_name, base_path, model_provider="openai")
    
    # Load existing documents
    await orchestrator.load_existing_documents()
    
    # Create results table
    table = Table(title="Document Validation Results")
    table.add_column("Document", style="cyan")
    table.add_column("Current Status", style="yellow")
    table.add_column("Validation Result", style="green")
    table.add_column("Errors Found", style="red")
    table.add_column("Can Auto-Repair", style="blue")
    
    results = []
    
    for doc_type in DocumentType:
        doc = orchestrator.documents[doc_type]
        
        # Load content if not already loaded
        if not doc.content:
            doc_path = base_path / "generated_documents" / f"{doc_type.name.lower()}.md"
            if doc_path.exists():
                doc.content = doc_path.read_text(encoding='utf-8')
        
        if doc.content:
            # Test validation
            validation_result = await orchestrator._perform_validation_checks(doc_type)
            
            # Determine if auto-repair can help
            can_repair = any(
                error_type in str(validation_result.errors) for error_type in [
                    "Missing YAML frontmatter",
                    "Document starts with YAML code block",
                    "Document missing main heading",
                    "Document content appears too short",
                    "Unmatched YAML code blocks",
                    "Missing required field",
                    "YAML frontmatter is not a valid dictionary",
                    "Missing functional requirements content",
                    "Missing API specification content",
                    "Missing UI/UX interface specifications",
                    "Missing non-functional requirements content"
                ]
            )
            
            status_icon = "✅" if validation_result.is_valid else "❌"
            repair_icon = "🔧" if can_repair and not validation_result.is_valid else "✅" if validation_result.is_valid else "❓"
            
            table.add_row(
                doc_type.value,
                doc.status.value,
                f"{status_icon} {'Valid' if validation_result.is_valid else 'Invalid'}",
                str(len(validation_result.errors)) if validation_result.errors else "0",
                f"{repair_icon} {'Yes' if can_repair else 'No' if not validation_result.is_valid else 'N/A'}"
            )
            
            results.append({
                'doc_type': doc_type,
                'valid': validation_result.is_valid,
                'errors': validation_result.errors,
                'can_repair': can_repair
            })
        else:
            table.add_row(
                doc_type.value,
                doc.status.value,
                "❓ No Content",
                "N/A",
                "N/A"
            )
    
    console.print(table)
    
    # Summary
    total_docs = len([r for r in results if r])
    valid_docs = len([r for r in results if r and r['valid']])
    invalid_docs = total_docs - valid_docs
    repairable_docs = len([r for r in results if r and not r['valid'] and r['can_repair']])
    
    console.print(f"\n[bold]Summary:[/bold]")
    console.print(f"  📄 Total Documents: {total_docs}")
    console.print(f"  ✅ Valid Documents: {valid_docs}")
    console.print(f"  ❌ Invalid Documents: {invalid_docs}")
    console.print(f"  🔧 Auto-Repairable: {repairable_docs}")
    
    if repairable_docs > 0:
        console.print(f"\n[green]Good news! {repairable_docs} documents can be auto-repaired.[/green]")
        console.print(f"[yellow]Run 'python reset_failed_documents.py' then 'python orchestrator.py --skip-existing' to fix them.[/yellow]")
    
    # Show detailed errors for invalid documents
    invalid_results = [r for r in results if r and not r['valid']]
    if invalid_results:
        console.print(f"\n[bold red]Detailed Errors:[/bold red]")
        for result in invalid_results:
            console.print(f"\n[cyan]{result['doc_type'].value}:[/cyan]")
            for error in result['errors']:
                repair_status = "🔧 Can repair" if result['can_repair'] else "❓ Manual fix needed"
                console.print(f"  - {error} ({repair_status})")

if __name__ == "__main__":
    asyncio.run(test_validation())
