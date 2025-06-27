#!/usr/bin/env python3
"""
Simple Phase 2 Status Checker
Shows real-time status of Phase 2 agents
"""

import json
import time
from pathlib import Path
from datetime import datetime

def load_progress_data():
    """Load progress tracker data"""
    # Try multiple possible paths
    possible_paths = [
        Path("../generated_documents/design/claude_instructions/progress_tracker.json"),
        Path("generated_documents/design/claude_instructions/progress_tracker.json"),
        Path("../progress_tracker.json"),
        Path("progress_tracker.json")
    ]

    for progress_file in possible_paths:
        if progress_file.exists():
            try:
                with open(progress_file, 'r') as f:
                    data = json.load(f)
                    print(f"📁 Found progress data at: {progress_file}")
                    return data
            except Exception as e:
                print(f"Error loading progress data from {progress_file}: {e}")
                continue

    print("❌ Could not find progress tracker file in any expected location")
    return {}

def format_duration(started_at, completed_at=None):
    """Format duration from timestamps"""
    if not started_at:
        return "N/A"
    
    if completed_at:
        duration_minutes = (completed_at - started_at) / 60
        return f"{duration_minutes:.1f}m"
    else:
        current_duration = (time.time() - started_at) / 60
        return f"{current_duration:.1f}m"

def get_status_emoji(status):
    """Get emoji for status"""
    if status == "completed":
        return "✅"
    elif status == "in_progress":
        return "🔄"
    elif status == "failed":
        return "❌"
    else:
        return "⏸️"

def show_all_phases_status():
    """Show status for all phases"""
    progress_data = load_progress_data()

    print("=" * 80)
    print("🚀 ALL PHASES STATUS - REAL-TIME")
    print("=" * 80)
    print(f"📅 Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Check all phases
    phases = {
        "phase1_mvp_core_features": "🎯 PHASE 1 - MVP CORE FEATURES",
        "phase2_advanced_features": "🚀 PHASE 2 - ADVANCED FEATURES",
        "phase3_production_ready": "🏭 PHASE 3 - PRODUCTION READY"
    }

    for phase_key, phase_title in phases.items():
        print(phase_title)
        print("-" * 80)

        phase_data = progress_data.get(phase_key, {})
        if not phase_data:
            print(f"❌ No {phase_key} data found")
            print()
            continue

        agents = phase_data.get("agents", {})
        if not agents:
            print(f"❌ No {phase_key} agents found")
            print()
            continue

        for agent_id, agent_data in agents.items():
            if not isinstance(agent_data, dict):
                continue

            status = agent_data.get("status", "unknown")
            started_at = agent_data.get("started_at")
            completed_at = agent_data.get("completed_at")
            duration = format_duration(started_at, completed_at)

            emoji = get_status_emoji(status)
            agent_name = agent_id.replace("-", " ").title()

            print(f"{emoji} {agent_name:<25} | {status.upper():<12} | {duration:<8}")

            # Show dependencies if waiting
            if status == "not_started":
                deps = agent_data.get("dependencies", [])
                if deps:
                    print(f"   └─ Waiting for: {', '.join(deps)}")

        # Show completion summary for this phase
        completed_count = sum(1 for agent in agents.values()
                             if isinstance(agent, dict) and agent.get("status") == "completed")
        in_progress_count = sum(1 for agent in agents.values()
                               if isinstance(agent, dict) and agent.get("status") == "in_progress")
        total_count = len(agents)

        progress_pct = (completed_count / total_count) * 100 if total_count > 0 else 0
        print(f"📈 Progress: {completed_count}/{total_count} complete ({progress_pct:.1f}%)")
        print()

if __name__ == "__main__":
    try:
        show_all_phases_status()
    except KeyboardInterrupt:
        print("\n👋 Status check stopped")
    except Exception as e:
        print(f"❌ Error: {e}")
