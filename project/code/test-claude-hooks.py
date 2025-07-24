#!/usr/bin/env python3
"""
Test script to verify Claude Code hooks are working.
Run this from your FY.WB.Bird2 project directory.
"""

import subprocess
import time
import urllib.request
import json

def get_recent_events(limit=5):
    """Get recent events from observability server."""
    try:
        with urllib.request.urlopen(f'http://localhost:4000/events/recent?limit={limit}') as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"Error getting events: {e}")
        return []

def test_hooks():
    print("🔍 Testing Claude Code hooks integration...")
    print("=" * 50)
    
    # Get current event count
    initial_events = get_recent_events(1)
    initial_count = len(initial_events)
    
    print(f"📊 Current event count: {initial_count}")
    print("\n🚀 Now run a Claude Code command in your FY.WB.Bird2 project:")
    print("   Example: claude code 'list files in current directory'")
    print("\n⏳ Waiting for new events (press Ctrl+C to stop)...")
    
    try:
        while True:
            time.sleep(2)
            current_events = get_recent_events(5)
            
            # Look for new events
            new_events = [e for e in current_events if e['source_app'] == 'claude-code-fy-bird']
            
            if new_events:
                print(f"\n✅ Found {len(new_events)} events from FY.WB.Bird2!")
                for event in new_events[:3]:  # Show first 3
                    print(f"   - {event['hook_event_type']}: {event['session_id']}")
                    if 'tool_name' in event['payload']:
                        print(f"     Tool: {event['payload']['tool_name']}")
                print("\n🎉 Hooks are working! Check dashboard: http://localhost:5173")
                break
            else:
                print(".", end="", flush=True)
                
    except KeyboardInterrupt:
        print("\n\n❌ No events detected from FY.WB.Bird2")
        print("   This might mean:")
        print("   1. Claude Code isn't calling the hooks")
        print("   2. Python environment issues in the project")
        print("   3. Hook permissions or path problems")
        
        # Show all recent events for debugging
        all_events = get_recent_events(10)
        if all_events:
            print(f"\n📝 Recent events from other sources:")
            for event in all_events[:5]:
                print(f"   - {event['source_app']}: {event['hook_event_type']}")

if __name__ == "__main__":
    test_hooks()