#!/usr/bin/env python3
"""
Setup MkDocs site with generated documents
"""

import shutil
import sys
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, TaskID

console = Console()

def setup_mkdocs_site():
    """Copy generated documents to MkDocs site structure"""
    
    console.print("[bold blue]Setting up MkDocs Professional Documentation Site[/bold blue]")
    
    # Define paths
    generated_docs_dir = Path("../generated_documents")
    mkdocs_site_dir = Path("./fy-wb-midway-docs")
    docs_dir = mkdocs_site_dir / "docs"
    
    if not generated_docs_dir.exists():
        console.print(f"[red]Generated documents directory not found: {generated_docs_dir}[/red]")
        return False
    
    if not mkdocs_site_dir.exists():
        console.print(f"[red]MkDocs site directory not found: {mkdocs_site_dir}[/red]")
        return False
    
    # Document mapping: source_file -> destination_path
    document_mapping = {
        # Requirements Documentation
        "brd.md": "requirements/brd.md",
        "prd.md": "requirements/prd.md", 
        "frd.md": "requirements/frd.md",
        "nfrd.md": "requirements/nfrd.md",
        "drd.md": "requirements/drd.md",
        
        # Technical Documentation
        "trd.md": "technical/trd.md",
        "trd_architecture.md": "technical/trd_architecture.md",
        "trd_technology_stack.md": "technical/trd_technology_stack.md",
        "trd_security.md": "technical/trd_security.md",
        "trd_infrastructure.md": "technical/trd_infrastructure.md",
        "trd_performance.md": "technical/trd_performance.md",
        "trd_operations.md": "technical/trd_operations.md",
        "db_schema.md": "technical/db_schema.md",
        
        # API Documentation
        "api_spec.md": "api/api_spec.md",
        "api_spec_security.md": "api/api_spec_security.md",
        "api_spec_components.md": "api/api_spec_components.md",
        "api_spec_errors.md": "api/api_spec_errors.md",
        "api_spec_common.md": "api/api_spec_common.md",
        "api_spec_customers.md": "api/api_spec_customers.md",
        "api_spec_payments.md": "api/api_spec_payments.md",
        "api_spec_loads.md": "api/api_spec_loads.md",
        "api_spec_invoices.md": "api/api_spec_invoices.md",
        "api_spec_carriers.md": "api/api_spec_carriers.md",
        
        # UI/UX Documentation
        "uiux_spec.md": "uiux/uiux_spec.md",
        "uiux_spec_architecture.md": "uiux/uiux_spec_architecture.md",
        "uiux_spec_components.md": "uiux/uiux_spec_components.md",
        "uiux_spec_interactions.md": "uiux/uiux_spec_interactions.md",
        "uiux_spec_dashboard.md": "uiux/uiux_spec_dashboard.md",
        "uiux_spec_customer_mgt.md": "uiux/uiux_spec_customer_mgt.md",
        "uiux_spec_payment_proc.md": "uiux/uiux_spec_payment_proc.md",
        "uiux_spec_load_mgt.md": "uiux/uiux_spec_load_mgt.md",
        "uiux_spec_invoice_proc.md": "uiux/uiux_spec_invoice_proc.md",
        "uiux_spec_carrier_mgt.md": "uiux/uiux_spec_carrier_mgt.md",
        
        # Testing Documentation
        "test_plan.md": "testing/test_plan.md",
        "test_strategy.md": "testing/test_strategy.md",
        "test_cases_functional.md": "testing/test_cases_functional.md",
        "test_cases_performance.md": "testing/test_cases_performance.md",
        "test_cases_security.md": "testing/test_cases_security.md",
        "test_automation.md": "testing/test_automation.md",
        
        # Project Management
        "rtm.md": "management/rtm.md",
        "dev_plan.md": "management/dev_plan.md"
    }
    
    copied_count = 0
    missing_count = 0
    
    with Progress() as progress:
        task = progress.add_task("[cyan]Copying documents...", total=len(document_mapping))
        
        for source_file, dest_path in document_mapping.items():
            source_path = generated_docs_dir / source_file
            dest_full_path = docs_dir / dest_path
            
            # Ensure destination directory exists
            dest_full_path.parent.mkdir(parents=True, exist_ok=True)
            
            if source_path.exists():
                try:
                    # Copy and clean up the document
                    content = source_path.read_text(encoding='utf-8')

                    # Clean up the document content
                    import re

                    # Remove YAML frontmatter (everything between first --- and second ---)
                    frontmatter_pattern = r'^---\n.*?\n---\n'
                    content = re.sub(frontmatter_pattern, '', content, flags=re.DOTALL)

                    # Remove YAML code blocks that wrap the entire content
                    # Pattern: ```yaml at start, then optional metadata, then content, then ``` at end
                    yaml_block_pattern = r'^```yaml\n(?:.*?\n---\n)?(.*?)```\s*$'
                    match = re.search(yaml_block_pattern, content, flags=re.DOTALL)

                    if match:
                        # Extract just the markdown content from inside the YAML block
                        content = match.group(1)
                    else:
                        # Fallback: remove any remaining ```yaml and ``` lines
                        lines = content.split('\n')
                        cleaned_lines = []
                        skip_yaml_metadata = False

                        for line in lines:
                            # Skip ```yaml line
                            if line.strip() == '```yaml':
                                skip_yaml_metadata = True
                                continue

                            # Skip YAML metadata until we hit markdown content
                            if skip_yaml_metadata:
                                if line.strip().startswith('#') or (line.strip() == '' and not skip_yaml_metadata):
                                    skip_yaml_metadata = False
                                elif ':' in line and not line.strip().startswith('#'):
                                    continue
                                elif line.strip() == '---':
                                    continue

                            # Skip closing ``` at the end
                            if line.strip() == '```':
                                continue

                            cleaned_lines.append(line)

                        content = '\n'.join(cleaned_lines)

                    # Clean up excessive whitespace
                    content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
                    content = content.strip()

                    # Remove multiple consecutive blank lines
                    import re
                    content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
                    content = content.strip()

                    # Write cleaned content
                    dest_full_path.write_text(content, encoding='utf-8')
                    copied_count += 1
                    
                except Exception as e:
                    console.print(f"[red]Error copying {source_file}: {str(e)}[/red]")
                    missing_count += 1
            else:
                console.print(f"[yellow]Missing: {source_file}[/yellow]")
                missing_count += 1
            
            progress.advance(task)
    
    console.print(f"\n[bold]Copy Summary:[/bold]")
    console.print(f"  ✅ Successfully copied: {copied_count} documents")
    console.print(f"  ❌ Missing/Failed: {missing_count} documents")
    console.print(f"  📄 Total processed: {len(document_mapping)} documents")
    
    if copied_count > 0:
        console.print(f"\n[green]🎉 MkDocs site setup complete![/green]")
        console.print(f"[yellow]Site location: {mkdocs_site_dir.absolute()}[/yellow]")
        console.print(f"\n[bold]Next steps:[/bold]")
        console.print(f"1. cd {mkdocs_site_dir}")
        console.print(f"2. python -m mkdocs serve")
        console.print(f"3. Open http://127.0.0.1:8000 in your browser")
        return True
    else:
        console.print(f"\n[red]❌ No documents were copied. Check the generated_documents directory.[/red]")
        return False

if __name__ == "__main__":
    try:
        success = setup_mkdocs_site()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Setup cancelled by user.[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]Error during setup: {str(e)}[/red]")
        sys.exit(1)
