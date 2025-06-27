#!/usr/bin/env python3
"""
Test script to manually trigger page updates and verify the live comparison page works
"""

import json
import webbrowser
from pathlib import Path
from rich.console import Console

console = Console()

def main():
    """Test the live comparison page by manually triggering updates"""
    
    console.print("🧪 Testing live comparison page updates...")
    
    # Get paths
    ui_system_path = Path(__file__).parent
    status_file = ui_system_path / "generation_status.json"
    live_page = ui_system_path / "live_comparison.html"
    
    # Check if files exist
    if not status_file.exists():
        console.print(f"[red]❌ Status file not found: {status_file}[/red]")
        return False
        
    if not live_page.exists():
        console.print(f"[red]❌ Live page not found: {live_page}[/red]")
        return False
    
    # Read current status
    with open(status_file, 'r') as f:
        status = json.load(f)
    
    console.print(f"📊 Current status:")
    console.print(f"   Total combinations: {status.get('total_combinations', 0)}")
    console.print(f"   Completed: {status.get('completed', 0)}")
    console.print(f"   Results: {len(status.get('results', []))}")
    
    # Show some sample results
    if status.get('results'):
        console.print(f"\n📋 Sample results:")
        for i, result in enumerate(status['results'][:3]):
            console.print(f"   {i+1}. {result['model']} + {result['reference_image']} = {'✅' if result['success'] else '❌'}")
        
        if len(status['results']) > 3:
            console.print(f"   ... and {len(status['results']) - 3} more")
    
    # Open the live page
    console.print(f"\n🌐 Opening live comparison page...")
    try:
        webbrowser.open(f"file://{live_page.absolute()}")
        console.print(f"✅ Page opened: {live_page.absolute()}")
    except Exception as e:
        console.print(f"[red]❌ Failed to open page: {e}[/red]")
        return False
    
    console.print(f"\n🔍 Check the browser page:")
    console.print(f"   1. Open browser developer tools (F12)")
    console.print(f"   2. Go to Console tab")
    console.print(f"   3. Look for polling messages and element matching")
    console.print(f"   4. Check if designs are showing up instead of placeholders")
    
    return True

if __name__ == "__main__":
    main()
