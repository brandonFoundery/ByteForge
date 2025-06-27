#!/usr/bin/env python3
"""
Debug the live comparison page to see why it's not working
"""

import json
import webbrowser
from pathlib import Path
from rich.console import Console

console = Console()

def main():
    """Debug the live comparison page step by step"""
    
    console.print("🔍 Debugging live comparison page...")
    
    # Get file paths
    ui_system_path = Path(__file__).parent
    status_file = ui_system_path / "generation_status.json"
    live_page = ui_system_path / "live_comparison.html"
    
    # 1. Check if status file exists and has data
    console.print("\n📊 1. Checking status file...")
    if status_file.exists():
        with open(status_file, 'r') as f:
            status = json.load(f)
        
        console.print(f"   ✅ Status file exists")
        console.print(f"   📄 Results count: {len(status.get('results', []))}")
        console.print(f"   ✅ Completed: {status.get('completed', 0)}")
        
        # Check first few results
        if status.get('results'):
            console.print(f"\n   🔍 First 3 results:")
            for i, result in enumerate(status['results'][:3]):
                model_id = result.get('model_id', 'unknown')
                image = result.get('reference_image', 'unknown')
                success = result.get('success', False)
                output_file = result.get('output_file', 'None')
                
                console.print(f"      {i+1}. {model_id} + {image} = {'✅' if success else '❌'}")
                console.print(f"         File: {Path(output_file).name if output_file != 'None' else 'None'}")
                
                # Check if the file actually exists
                if output_file and output_file != 'None':
                    file_path = Path(output_file)
                    if file_path.exists():
                        console.print(f"         📁 File exists: ✅")
                    else:
                        console.print(f"         📁 File exists: ❌ (Missing: {file_path})")
    else:
        console.print(f"   ❌ Status file missing: {status_file}")
        return False
    
    # 2. Check if live page exists
    console.print(f"\n🌐 2. Checking live page...")
    if live_page.exists():
        console.print(f"   ✅ Live page exists: {live_page}")
        
        # Check if it can be accessed via HTTP
        console.print(f"   🌐 Opening live page...")
        try:
            webbrowser.open(f"file://{live_page.absolute()}")
            console.print(f"   ✅ Page opened in browser")
        except Exception as e:
            console.print(f"   ❌ Failed to open page: {e}")
    else:
        console.print(f"   ❌ Live page missing: {live_page}")
        return False
    
    # 3. Test if status file is accessible via HTTP
    console.print(f"\n🔗 3. Testing HTTP access...")
    console.print(f"   📝 Manual test steps:")
    console.print(f"      1. Open browser Developer Tools (F12)")
    console.print(f"      2. Go to Console tab")
    console.print(f"      3. Look for these messages:")
    console.print(f"         - 'Polling for updates...'")
    console.print(f"         - 'Status update received:'")
    console.print(f"         - 'Processing result for...'")
    console.print(f"      4. Go to Network tab")
    console.print(f"         - Look for requests to 'generation_status.json'")
    console.print(f"         - Check if they return 200 OK or fail")
    console.print(f"      5. If Network requests fail:")
    console.print(f"         - The page needs to be served via HTTP server")
    console.print(f"         - File:// protocol can't load JSON files due to CORS")
    
    # 4. Suggest solutions
    console.print(f"\n💡 4. Potential solutions:")
    console.print(f"   🔧 Solution 1: Use HTTP server")
    console.print(f"      Run: python test_server.py")
    console.print(f"      Then access: http://localhost:8000/live_comparison.html")
    
    console.print(f"\n   🔧 Solution 2: Embed status data in HTML")
    console.print(f"      Modify live_comparison_viewer.py to embed JSON data")
    console.print(f"      Instead of loading via fetch(), use embedded JavaScript")
    
    console.print(f"\n   🔧 Solution 3: Use screenshots instead of iframes")
    console.print(f"      Generate PNG screenshots of each HTML file")
    console.print(f"      Display screenshots instead of iframes")
    
    return True

if __name__ == "__main__":
    main()
