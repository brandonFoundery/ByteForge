#!/usr/bin/env python3
"""
Check actual document lengths to debug validation issues
"""

import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table

console = Console()

def check_document_lengths():
    """Check the actual content lengths of generated documents"""
    
    console.print("[bold blue]Document Length Analysis[/bold blue]")
    
    docs_dir = Path("../generated_documents")
    
    if not docs_dir.exists():
        console.print(f"[red]Documents directory not found: {docs_dir}[/red]")
        return
    
    # Create results table
    table = Table(title="Document Content Analysis")
    table.add_column("Document", style="cyan")
    table.add_column("Total Lines", style="yellow")
    table.add_column("Total Characters", style="green")
    table.add_column("Content After YAML", style="blue")
    table.add_column("Status", style="red")
    
    documents = [
        ("brd.md", "Business Requirements Document"),
        ("prd.md", "Product Requirements Document"),
        ("frd.md", "Functional Requirements Document"),
        ("nfrd.md", "Non-Functional Requirements Document"),
        ("drd.md", "Data Requirements Document"),
        ("db_schema.md", "Database Schema"),
        ("trd.md", "Technical Requirements Document"),
        ("api_spec.md", "API OpenAPI Specification"),
        ("uiux_spec.md", "UI/UX Specification"),
        ("test_plan.md", "Test Plan and Test Cases"),
        ("rtm.md", "Requirements Traceability Matrix")
    ]
    
    for filename, title in documents:
        filepath = docs_dir / filename
        
        if filepath.exists():
            try:
                content = filepath.read_text(encoding='utf-8')
                lines = content.split('\n')
                total_lines = len(lines)
                total_chars = len(content)
                
                # Find content after YAML frontmatter
                content_start = 0
                if lines and lines[0].strip() == '---':
                    for i, line in enumerate(lines[1:], 1):
                        if line.strip() == '---':
                            content_start = i + 1
                            break
                
                actual_content = '\n'.join(lines[content_start:]).strip()
                content_chars = len(actual_content)
                
                # Determine status
                if content_chars < 100:
                    status = "❌ Too Short"
                elif content_chars < 500:
                    status = "⚠️ Short"
                else:
                    status = "✅ Good"
                
                table.add_row(
                    title,
                    str(total_lines),
                    str(total_chars),
                    str(content_chars),
                    status
                )
                
                # Show first few lines of content for debugging
                if content_chars < 200:
                    console.print(f"\n[yellow]Content preview for {title}:[/yellow]")
                    preview_lines = actual_content.split('\n')[:10]
                    for i, line in enumerate(preview_lines):
                        console.print(f"  {i+1}: {line}")
                    if len(preview_lines) >= 10:
                        console.print("  ...")
                        
            except Exception as e:
                table.add_row(
                    title,
                    "Error",
                    "Error",
                    "Error",
                    f"❌ {str(e)}"
                )
        else:
            table.add_row(
                title,
                "Missing",
                "Missing", 
                "Missing",
                "❌ Not Found"
            )
    
    console.print(table)
    
    # Summary
    console.print(f"\n[bold]Analysis Summary:[/bold]")
    console.print(f"Documents with good content (>500 chars): Look for ✅ status")
    console.print(f"Documents that may need attention: Look for ⚠️ or ❌ status")
    console.print(f"The validation threshold is currently 100 characters")

if __name__ == "__main__":
    check_document_lengths()
