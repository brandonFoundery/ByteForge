#!/usr/bin/env python3
"""
Downstream Resume Manager

Detects when new requirements were added but downstream documents (UI/UX, Test Plans, RTM)
weren't properly updated, and provides functionality to resume and complete the generation.
"""

import re
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Tuple, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from orchestrator import RequirementsOrchestrator, DocumentType

console = Console()

class DownstreamResumeManager:
    """Manages detection and resumption of incomplete downstream document updates"""
    
    def __init__(self, base_path: Path, orchestrator: RequirementsOrchestrator):
        self.base_path = base_path
        self.orchestrator = orchestrator
        self.docs_path = base_path / "fy-wb-midway-docs" / "docs"
        self.requirements_path = self.docs_path / "requirements"
        self.uiux_path = self.docs_path / "uiux"
        self.testing_path = self.docs_path / "testing"
        self.management_path = self.docs_path / "management"
        
    def detect_incomplete_downstream_updates(self) -> Dict[str, any]:
        """
        Detect which downstream documents are missing updates after new requirements were added
        
        Returns:
            Dict with analysis results including missing requirements and outdated documents
        """
        console.print("\n[cyan]🔍 Analyzing downstream document synchronization...[/cyan]")
        
        # Extract requirement IDs from source documents
        frd_requirements = self._extract_requirement_ids_from_file(self.requirements_path / "frd.md")
        nfrd_requirements = self._extract_requirement_ids_from_file(self.requirements_path / "nfrd.md")
        drd_requirements = self._extract_requirement_ids_from_file(self.requirements_path / "drd.md")
        
        all_source_requirements = frd_requirements | nfrd_requirements | drd_requirements
        
        # Extract requirement IDs referenced in downstream documents
        uiux_references = self._extract_requirement_references_from_uiux()
        test_references = self._extract_requirement_references_from_testing()
        rtm_references = self._extract_requirement_references_from_rtm()
        
        # Find missing requirements in each downstream document type
        missing_in_uiux = all_source_requirements - uiux_references
        missing_in_testing = all_source_requirements - test_references
        missing_in_rtm = all_source_requirements - rtm_references
        
        # Check modification times
        source_mod_times = self._get_source_document_mod_times()
        downstream_mod_times = self._get_downstream_document_mod_times()
        
        # Determine which documents need regeneration
        # Primary check: missing requirements (more reliable than timestamps)
        outdated_documents = []

        if missing_in_uiux:
            outdated_documents.append('UI/UX Specifications')

        if missing_in_testing:
            outdated_documents.append('Test Plans')

        if missing_in_rtm:
            outdated_documents.append('Requirements Traceability Matrix')

        # Secondary check: timestamp comparison (only if no missing requirements detected)
        if not outdated_documents:
            if self._is_outdated(source_mod_times, downstream_mod_times.get('uiux', 0)):
                outdated_documents.append('UI/UX Specifications')

            if self._is_outdated(source_mod_times, downstream_mod_times.get('testing', 0)):
                outdated_documents.append('Test Plans')

            if self._is_outdated(source_mod_times, downstream_mod_times.get('rtm', 0)):
                outdated_documents.append('Requirements Traceability Matrix')
        
        return {
            'total_requirements': len(all_source_requirements),
            'missing_in_uiux': missing_in_uiux,
            'missing_in_testing': missing_in_testing,
            'missing_in_rtm': missing_in_rtm,
            'outdated_documents': outdated_documents,
            'source_mod_times': source_mod_times,
            'downstream_mod_times': downstream_mod_times,
            'needs_update': len(outdated_documents) > 0
        }
    
    def _extract_requirement_ids_from_file(self, file_path: Path) -> Set[str]:
        """Extract all requirement IDs from a requirements document"""
        if not file_path.exists():
            return set()
            
        try:
            content = file_path.read_text(encoding='utf-8')
            # Match patterns like REQ-FUNC-020, FRD-3.1.2, etc.
            patterns = [
                r'REQ-FUNC-\d+',
                r'REQ-NFR-\d+', 
                r'REQ-DATA-\d+',
                r'FRD-\d+\.\d+\.\d+',
                r'NFRD-\d+\.\d+\.\d+',
                r'DRD-\d+\.\d+\.\d+'
            ]
            
            requirement_ids = set()
            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                requirement_ids.update(matches)
                
            return requirement_ids
            
        except Exception as e:
            console.print(f"[red]Error reading {file_path}: {e}[/red]")
            return set()
    
    def _extract_requirement_references_from_uiux(self) -> Set[str]:
        """Extract requirement IDs referenced in UI/UX documents"""
        references = set()
        
        if not self.uiux_path.exists():
            return references
            
        for uiux_file in self.uiux_path.glob("*.md"):
            file_refs = self._extract_requirement_ids_from_file(uiux_file)
            references.update(file_refs)
            
        return references
    
    def _extract_requirement_references_from_testing(self) -> Set[str]:
        """Extract requirement IDs referenced in testing documents"""
        references = set()
        
        if not self.testing_path.exists():
            return references
            
        for test_file in self.testing_path.glob("*.md"):
            file_refs = self._extract_requirement_ids_from_file(test_file)
            references.update(file_refs)
            
        return references
    
    def _extract_requirement_references_from_rtm(self) -> Set[str]:
        """Extract requirement IDs referenced in RTM document"""
        rtm_file = self.management_path / "rtm.md"
        return self._extract_requirement_ids_from_file(rtm_file)
    
    def _get_source_document_mod_times(self) -> float:
        """Get the latest modification time of source requirement documents"""
        latest_time = 0
        
        for doc_file in [self.requirements_path / "frd.md", 
                        self.requirements_path / "nfrd.md",
                        self.requirements_path / "drd.md"]:
            if doc_file.exists():
                mod_time = doc_file.stat().st_mtime
                latest_time = max(latest_time, mod_time)
                
        return latest_time
    
    def _get_downstream_document_mod_times(self) -> Dict[str, float]:
        """Get modification times of downstream documents"""
        times = {}
        
        # UI/UX documents
        if self.uiux_path.exists():
            uiux_times = [f.stat().st_mtime for f in self.uiux_path.glob("*.md") if f.exists()]
            times['uiux'] = max(uiux_times) if uiux_times else 0
            
        # Testing documents  
        if self.testing_path.exists():
            test_times = [f.stat().st_mtime for f in self.testing_path.glob("*.md") if f.exists()]
            times['testing'] = max(test_times) if test_times else 0
            
        # RTM document
        rtm_file = self.management_path / "rtm.md"
        times['rtm'] = rtm_file.stat().st_mtime if rtm_file.exists() else 0
        
        return times
    
    def _is_outdated(self, source_time: float, downstream_time: float) -> bool:
        """Check if downstream document is outdated compared to source"""
        return source_time > downstream_time
    
    def display_analysis_results(self, analysis: Dict[str, any]) -> None:
        """Display the analysis results in a formatted table"""
        
        if not analysis['needs_update']:
            console.print("\n[green]✅ All downstream documents are up to date![/green]")
            return
            
        console.print(f"\n[yellow]⚠️  Found {len(analysis['outdated_documents'])} downstream document(s) that need updating[/yellow]")
        
        # Create summary table
        table = Table(title="Downstream Document Analysis")
        table.add_column("Document Type", style="cyan")
        table.add_column("Status", style="magenta")
        table.add_column("Missing Requirements", style="red")
        
        if 'UI/UX Specifications' in analysis['outdated_documents']:
            missing_count = len(analysis['missing_in_uiux'])
            table.add_row("UI/UX Specifications", "❌ Outdated", f"{missing_count} requirements")
            
        if 'Test Plans' in analysis['outdated_documents']:
            missing_count = len(analysis['missing_in_testing'])
            table.add_row("Test Plans", "❌ Outdated", f"{missing_count} requirements")
            
        if 'Requirements Traceability Matrix' in analysis['outdated_documents']:
            missing_count = len(analysis['missing_in_rtm'])
            table.add_row("RTM", "❌ Outdated", f"{missing_count} requirements")
        
        console.print(table)
        
        # Show some example missing requirements
        if analysis['missing_in_uiux']:
            console.print(f"\n[red]Missing in UI/UX:[/red] {', '.join(list(analysis['missing_in_uiux'])[:5])}")
            if len(analysis['missing_in_uiux']) > 5:
                console.print(f"[dim]... and {len(analysis['missing_in_uiux']) - 5} more[/dim]")

    async def resume_downstream_generation(self, analysis: Dict[str, any], model_provider: str = "openai") -> bool:
        """
        Resume generation of outdated downstream documents

        Args:
            analysis: Results from detect_incomplete_downstream_updates()
            model_provider: LLM provider to use for generation

        Returns:
            True if successful, False otherwise
        """
        if not analysis['needs_update']:
            console.print("[green]No updates needed - all documents are current[/green]")
            return True

        console.print(f"\n[cyan]🔄 Resuming generation of {len(analysis['outdated_documents'])} downstream document(s)...[/cyan]")

        success_count = 0
        total_count = len(analysis['outdated_documents'])

        try:
            # Regenerate UI/UX Specifications
            if 'UI/UX Specifications' in analysis['outdated_documents']:
                console.print("\n[yellow]Regenerating UI/UX Specifications...[/yellow]")
                try:
                    await self.orchestrator.generate_document(DocumentType.UIUX_SPEC, model_provider)
                    console.print("[green]✓ UI/UX Specifications updated successfully[/green]")
                    success_count += 1
                except Exception as e:
                    console.print(f"[red]✗ Failed to update UI/UX Specifications: {e}[/red]")

            # Regenerate Test Plans
            if 'Test Plans' in analysis['outdated_documents']:
                console.print("\n[yellow]Regenerating Test Plans...[/yellow]")
                try:
                    await self.orchestrator.generate_document(DocumentType.TEST_PLAN, model_provider)
                    console.print("[green]✓ Test Plans updated successfully[/green]")
                    success_count += 1
                except Exception as e:
                    console.print(f"[red]✗ Failed to update Test Plans: {e}[/red]")

            # Regenerate Requirements Traceability Matrix
            if 'Requirements Traceability Matrix' in analysis['outdated_documents']:
                console.print("\n[yellow]Regenerating Requirements Traceability Matrix...[/yellow]")
                try:
                    await self.orchestrator.generate_document(DocumentType.RTM, model_provider)
                    console.print("[green]✓ RTM updated successfully[/green]")
                    success_count += 1
                except Exception as e:
                    console.print(f"[red]✗ Failed to update RTM: {e}[/red]")

            # Summary
            if success_count == total_count:
                console.print(f"\n[green]🎉 Successfully updated all {success_count} downstream documents![/green]")
                return True
            else:
                console.print(f"\n[yellow]⚠️  Updated {success_count}/{total_count} documents. Some updates failed.[/yellow]")
                return False

        except Exception as e:
            console.print(f"\n[red]❌ Resume operation failed: {e}[/red]")
            return False

    async def interactive_resume(self, model_provider: str = "openai") -> bool:
        """
        Interactive resume process with user confirmation

        Args:
            model_provider: LLM provider to use for generation

        Returns:
            True if successful, False otherwise
        """
        console.print(Panel.fit(
            "[bold cyan]Downstream Document Resume Manager[/bold cyan]\n"
            "Checking for incomplete updates after new requirements were added...",
            title="🔄 Resume Analysis"
        ))

        # Perform analysis
        analysis = self.detect_incomplete_downstream_updates()

        # Display results
        self.display_analysis_results(analysis)

        if not analysis['needs_update']:
            return True

        # Ask for confirmation
        console.print(f"\n[yellow]The following documents will be regenerated:[/yellow]")
        for doc in analysis['outdated_documents']:
            console.print(f"  • {doc}")

        from rich.prompt import Confirm
        if not Confirm.ask("\nProceed with regeneration?", default=True):
            console.print("[yellow]Resume cancelled by user[/yellow]")
            return False

        # Perform the resume
        return await self.resume_downstream_generation(analysis, model_provider)


# Standalone function for easy integration
async def run_downstream_resume(base_path: Path, config_path: Path, model_provider: str = "openai") -> bool:
    """
    Standalone function to run the downstream resume process

    Args:
        base_path: Base path of the project
        config_path: Path to config.yaml
        model_provider: LLM provider to use

    Returns:
        True if successful, False otherwise
    """
    try:
        # Initialize orchestrator
        from orchestrator import RequirementsOrchestrator
        orchestrator = RequirementsOrchestrator("FY.WB.Midway", base_path, config_path, model_provider)

        # Create resume manager
        resume_manager = DownstreamResumeManager(base_path / "Requirements_Generation_System", orchestrator)

        # Run interactive resume
        return await resume_manager.interactive_resume(model_provider)

    except Exception as e:
        console.print(f"[red]Error running downstream resume: {e}[/red]")
        return False


if __name__ == "__main__":
    import asyncio
    import sys
    from pathlib import Path

    # Default paths
    base_path = Path("d:/Repository/@Clients/FY.WB.Midway")
    config_path = base_path / "Requirements_Generation_System" / "config.yaml"

    # Run the resume process
    asyncio.run(run_downstream_resume(base_path, config_path, "openai"))
