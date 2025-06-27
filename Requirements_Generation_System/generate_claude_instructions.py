#!/usr/bin/env python3
"""
Generate Claude Code Instructions

This script generates the complete Claude Code instruction system including:
- Individual instruction files for each agent/phase combination
- Master execution plan with dependencies
- Progress tracker for monitoring execution
- Updated Claude executor that uses instruction files

Usage:
    python generate_claude_instructions.py
"""

import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from claude_instruction_generator import ClaudeInstructionGenerator
from rich.console import Console

console = Console()


def main():
    """Generate the complete Claude Code instruction system"""
    console.print("[bold blue]🚀 Generating Claude Code Instruction System[/bold blue]")
    console.print("[dim]This will create a repeatable, maintainable system for AI-driven development[/dim]\n")
    
    # Get base path
    base_path = Path(__file__).parent.parent
    console.print(f"[dim]Base path: {base_path}[/dim]")
    
    # Create generator
    generator = ClaudeInstructionGenerator(base_path)
    
    # Generate all instructions
    success = generator.generate_all_instructions()
    
    if success:
        console.print("\n[bold green]🎉 Claude Code instruction system generated successfully![/bold green]")
        console.print("\n[green]What was created:[/green]")
        console.print("📁 generated_documents/design/claude_instructions/")
        console.print("   ├── execution_plan.md - Master orchestration document")
        console.print("   ├── progress_tracker.json - Progress tracking")
        console.print("   ├── backend-phase1-mvp-core.md - Backend Phase 1 instructions")
        console.print("   ├── frontend-phase1-mvp-core.md - Frontend Phase 1 instructions")
        console.print("   ├── security-phase1-mvp-core.md - Security Phase 1 instructions")
        console.print("   ├── infrastructure-phase1-mvp-core.md - Infrastructure Phase 1 instructions")
        console.print("   ├── integration-phase1-mvp-core.md - Integration Phase 1 instructions")
        console.print("   └── ... (all phase 2 and phase 3 instructions)")
        console.print("\n🔄 Requirements_Generation_System/claude_code_executor.py - Updated executor")
        
        console.print("\n[green]Next steps:[/green]")
        console.print("1. Review the generated instruction files")
        console.print("2. Run the updated orchestrator system")
        console.print("3. Execute Claude Code agents using the new instruction-based system")
        
        console.print("\n[yellow]Benefits of this system:[/yellow]")
        console.print("✅ Repeatable - All instructions are generated programmatically")
        console.print("✅ Maintainable - Easy to update and modify instructions")
        console.print("✅ Trackable - Progress tracking and dependency management")
        console.print("✅ Parallel - Automatic parallel execution where possible")
        console.print("✅ Context-aware - Each agent gets all necessary context")
        console.print("✅ Self-documenting - Clear completion reports and error handling")
        
    else:
        console.print("\n[bold red]❌ Failed to generate instruction system.[/bold red]")
        console.print("[red]Check the error messages above for details.[/red]")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
