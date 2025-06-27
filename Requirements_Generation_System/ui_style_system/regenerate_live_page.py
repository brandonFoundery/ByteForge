#!/usr/bin/env python3
"""
Regenerate the live comparison page with embedded status data
"""

import sys
from pathlib import Path
from rich.console import Console

# Add current directory to path
sys.path.append('.')

console = Console()

def main():
    """Regenerate the live comparison page"""
    
    console.print("🔄 Regenerating live comparison page...")
    
    try:
        from live_comparison_viewer import LiveComparisonViewer
        
        # Use current working directory as project root
        project_root = Path.cwd().parent.parent
        console.print(f"📁 Project root: {project_root}")
        
        viewer = LiveComparisonViewer(project_root)
        page_url = viewer.create_and_open_live_page()
        
        console.print(f"✅ Live page regenerated with embedded status data!")
        console.print(f"🌐 Page: {viewer.live_comparison_file}")
        
        return True
        
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        return False

if __name__ == "__main__":
    main()
