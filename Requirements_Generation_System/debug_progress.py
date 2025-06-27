#!/usr/bin/env python3
"""
Debug script to see what's in the progress tracker
"""

import json
from pathlib import Path

def debug_progress_tracker():
    """Debug the progress tracker contents"""
    
    # Try multiple possible paths
    possible_paths = [
        Path("../generated_documents/design/claude_instructions/progress_tracker.json"),
        Path("generated_documents/design/claude_instructions/progress_tracker.json"),
        Path("../progress_tracker.json"),
        Path("progress_tracker.json")
    ]
    
    progress_file = None
    for path in possible_paths:
        if path.exists():
            progress_file = path
            break
    
    if not progress_file:
        print("❌ Could not find progress tracker file")
        return
    
    print(f"📁 Found progress tracker at: {progress_file}")
    print("=" * 80)
    
    try:
        with open(progress_file, 'r') as f:
            data = json.load(f)
        
        print("📊 PROGRESS TRACKER CONTENTS:")
        print("-" * 80)
        
        # Show top-level keys
        print("🔑 Top-level keys:")
        for key in data.keys():
            print(f"  - {key}")
        
        print()
        
        # Show each phase in detail
        for phase_name, phase_data in data.items():
            if phase_name == "execution_metadata":
                continue
                
            print(f"📋 {phase_name.upper()}:")
            print(f"   Type: {type(phase_data)}")
            
            if isinstance(phase_data, dict):
                print(f"   Keys: {list(phase_data.keys())}")
                
                agents = phase_data.get("agents", {})
                if agents:
                    print(f"   Agents ({len(agents)}):")
                    for agent_id, agent_data in agents.items():
                        if isinstance(agent_data, dict):
                            status = agent_data.get("status", "unknown")
                            print(f"     - {agent_id}: {status}")
                        else:
                            print(f"     - {agent_id}: {type(agent_data)}")
                else:
                    print("   No agents found")
            
            print()
        
    except Exception as e:
        print(f"❌ Error reading progress tracker: {e}")

if __name__ == "__main__":
    debug_progress_tracker()
