#!/usr/bin/env python3
"""
Force update the live comparison page with the latest JavaScript fixes
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from ui_style_system.live_comparison_viewer import LiveComparisonViewer
from rich.console import Console

console = Console()

def main():
    """Force regenerate the live comparison page"""
    
    console.print("🔄 Force updating live comparison page...")
    
    # Get project root
    project_root = Path(__file__).parent.parent.parent
    
    # Create viewer and regenerate page
    viewer = LiveComparisonViewer(project_root)
    
    # Delete existing page first
    live_page = viewer.live_comparison_file
    if live_page.exists():
        live_page.unlink()
        console.print(f"🗑️  Deleted old page: {live_page}")
    
    # Regenerate with updated JavaScript
    page_url = viewer.create_and_open_live_page()
    
    console.print(f"✅ Live page regenerated with updated JavaScript!")
    console.print(f"🌐 URL: {page_url}")
    console.print("📱 The page should now properly display completed designs")
    
    return page_url

if __name__ == "__main__":
    main()
