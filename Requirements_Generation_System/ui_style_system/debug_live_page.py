#!/usr/bin/env python3
"""
Debug the live page to see exactly what's happening
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
    llm_generated = ui_system_path / "llm_generated"
    
    # 1. Check status file
    console.print("\n📊 1. Checking status file...")
    if status_file.exists():
        with open(status_file, 'r') as f:
            status = json.load(f)
        console.print(f"   ✅ Status file exists")
        console.print(f"   📄 Results count: {len(status.get('results', []))}")
        
        # Show first few results
        if status.get('results'):
            console.print(f"   🔍 First result:")
            result = status['results'][0]
            console.print(f"      Model: {result.get('model_id')}")
            console.print(f"      Image: {result.get('reference_image')}")
            console.print(f"      Success: {result.get('success')}")
            console.print(f"      File: {result.get('output_file', 'None')}")
    else:
        console.print(f"   ❌ Status file missing: {status_file}")
        return False
    
    # 2. Check generated files
    console.print(f"\n📁 2. Checking generated files...")
    if llm_generated.exists():
        html_files = list(llm_generated.glob("*.html"))
        console.print(f"   ✅ Generated folder exists")
        console.print(f"   📄 HTML files count: {len(html_files)}")
        
        if html_files:
            console.print(f"   🔍 Sample files:")
            for i, file in enumerate(html_files[:3]):
                console.print(f"      {i+1}. {file.name}")
    else:
        console.print(f"   ❌ Generated folder missing: {llm_generated}")
        return False
    
    # 3. Check live page
    console.print(f"\n🌐 3. Checking live page...")
    if live_page.exists():
        console.print(f"   ✅ Live page exists: {live_page}")
        
        # Check if it has the updated JavaScript
        with open(live_page, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'design-${designId}' in content:
            console.print(f"   ✅ Updated JavaScript found")
        else:
            console.print(f"   ❌ Old JavaScript still present")
            
        if 'pollForUpdates' in content:
            console.print(f"   ✅ Polling function found")
        else:
            console.print(f"   ❌ Polling function missing")
    else:
        console.print(f"   ❌ Live page missing: {live_page}")
        return False
    
    # 4. Test element ID matching
    console.print(f"\n🎯 4. Testing element ID matching...")
    
    # Simulate what the JavaScript should find
    sample_result = status['results'][0] if status.get('results') else None
    if sample_result:
        model_id = sample_result['model_id']
        image_name = sample_result['reference_image']
        image_base = image_name.replace('.png', '')
        expected_design_id = f"{model_id}_{image_base}"
        expected_element_id = f"design-{expected_design_id}"
        
        console.print(f"   📋 Sample result:")
        console.print(f"      Model ID: {model_id}")
        console.print(f"      Image: {image_name}")
        console.print(f"      Expected design ID: {expected_design_id}")
        console.print(f"      Expected element ID: {expected_element_id}")
        
        # Check if this element exists in the HTML
        if expected_element_id in content:
            console.print(f"   ✅ Element ID found in HTML")
        else:
            console.print(f"   ❌ Element ID NOT found in HTML")
            
            # Look for similar IDs
            import re
            element_ids = re.findall(r'id="design-([^"]+)"', content)
            console.print(f"   🔍 Available element IDs (first 5):")
            for i, elem_id in enumerate(element_ids[:5]):
                console.print(f"      {i+1}. design-{elem_id}")
    
    # 5. Open the page with debugging
    console.print(f"\n🌐 5. Opening page for manual testing...")
    try:
        webbrowser.open(f"file://{live_page.absolute()}")
        console.print(f"✅ Page opened")
        
        console.print(f"\n🔧 Manual debugging steps:")
        console.print(f"   1. Open browser Developer Tools (F12)")
        console.print(f"   2. Go to Console tab")
        console.print(f"   3. Look for these messages:")
        console.print(f"      - 'Polling for updates...'")
        console.print(f"      - 'Status update received:'")
        console.print(f"      - 'Processing result for...'")
        console.print(f"      - 'Element not found for ID:' (this is the problem)")
        console.print(f"   4. Go to Network tab and check if generation_status.json loads")
        console.print(f"   5. Check Elements tab for actual element IDs")
        
    except Exception as e:
        console.print(f"❌ Failed to open page: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()
