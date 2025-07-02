#!/usr/bin/env python3
"""
Watch the progress tracker in real-time
"""

import json
import time
import os
from pathlib import Path
from datetime import datetime

def format_duration(seconds):
    """Format duration in human readable format"""
    if seconds is None:
        return "N/A"
    if seconds < 60:
        return f"{seconds:.1f}s"
    else:
        return f"{seconds/60:.1f}m"

def get_status_emoji(status):
    """Get emoji for status"""
    emoji_map = {
        "not_started": "⏸️",
        "in_progress": "🔄",
        "completed": "✅", 
        "failed": "❌"
    }
    return emoji_map.get(status, "❓")

def watch_progress():
    """Watch progress tracker and display updates"""
    tracker_file = Path(__file__).parent.parent / "project" / "design" / "claude_instructions" / "progress_tracker.json"
    
    if not tracker_file.exists():
        print(f"❌ Progress tracker not found: {tracker_file}")
        return
    
    last_modified = 0
    
    print("🔍 Watching Claude Code execution progress...")
    print("Press Ctrl+C to stop\n")
    
    while True:
        try:
            # Check if file was modified
            current_modified = os.path.getmtime(tracker_file)
            
            if current_modified > last_modified:
                last_modified = current_modified
                
                # Clear screen and show updated status
                os.system('clear' if os.name == 'posix' else 'cls')
                
                with open(tracker_file, 'r', encoding='utf-8') as f:
                    tracker = json.load(f)
                
                print(f"🚀 Claude Code Execution Monitor - {datetime.now().strftime('%H:%M:%S')}")
                print("=" * 60)
                
                # Phase 1 status
                phase1 = tracker.get("phase1_mvp_core_features", {})
                print(f"\n📋 Phase 1 MVP Core Features")
                print("-" * 30)
                
                for agent_key, agent_data in phase1.get("agents", {}).items():
                    status = agent_data.get("status", "unknown")
                    emoji = get_status_emoji(status)
                    
                    duration = None
                    if agent_data.get("started_at") and agent_data.get("completed_at"):
                        duration = agent_data["completed_at"] - agent_data["started_at"]
                    elif agent_data.get("started_at"):
                        duration = time.time() - agent_data["started_at"]
                    
                    print(f"{emoji} {agent_key:<20} {status:<12} {format_duration(duration):>8}")
                
                print(f"\n📊 Overall Progress")
                print("-" * 20)
                total_agents = len(phase1.get("agents", {}))
                completed = sum(1 for a in phase1.get("agents", {}).values() if a.get("status") == "completed")
                in_progress = sum(1 for a in phase1.get("agents", {}).values() if a.get("status") == "in_progress")
                
                print(f"✅ Completed: {completed}/{total_agents}")
                print(f"🔄 In Progress: {in_progress}")
                print(f"📈 Progress: {completed/total_agents*100:.1f}%")
                
            time.sleep(2)
            
        except KeyboardInterrupt:
            print("\n👋 Monitoring stopped")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    watch_progress()