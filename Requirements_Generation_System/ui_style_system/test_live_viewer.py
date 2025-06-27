#!/usr/bin/env python3
"""
Test script for the live comparison viewer
Creates the live page and opens it immediately to test the interface
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from live_comparison_viewer import LiveComparisonViewer

def main():
    """Test the live comparison viewer"""
    
    print("🧪 Testing Live Comparison Viewer...")
    
    project_root = Path(__file__).parent.parent.parent
    viewer = LiveComparisonViewer(project_root)
    
    # Create and open the live page
    page_url = viewer.create_and_open_live_page()
    
    print(f"✅ Live page created and opened!")
    print(f"📂 URL: {page_url}")
    print("\n📱 The page shows:")
    print("   • Tabs for each AI model")
    print("   • Placeholders for all 45 designs")
    print("   • Live status indicators")
    print("   • Auto-updating counters")
    print("\n🔄 When you run the full generation:")
    print("   • Page will update automatically as designs complete")
    print("   • No need to refresh manually")
    print("   • Each design appears as soon as it's generated")

if __name__ == "__main__":
    main()
