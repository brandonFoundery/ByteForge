#!/usr/bin/env python3
"""
Test script for ClaudeCodeExecutor to verify the fixes work correctly
"""

import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_claude_executor():
    """Test the ClaudeCodeExecutor initialization"""
    try:
        from claude_code_executor import ClaudeCodeExecutor
        
        print("Testing ClaudeCodeExecutor initialization...")
        
        # Test with current project path
        base_path = Path(__file__).parent / "project"
        executor = ClaudeCodeExecutor(base_path)
        
        print(f"✅ ClaudeCodeExecutor initialized successfully!")
        print(f"✅ Loaded {len(executor.agents)} agents")
        print(f"✅ Loaded {len(executor.phases)} phases")
        print(f"✅ Progress tracker loaded/generated")
        
        # Print loaded agents
        print("\n📋 Loaded Agents:")
        for key, agent in executor.agents.items():
            print(f"  {key}: {agent['name']} ({agent['id']})")
        
        # Print loaded phases  
        print("\n📋 Loaded Phases:")
        for key, phase in executor.phases.items():
            print(f"  {key}: {phase['name']} ({phase['id']})")
            
        # Check if progress tracker has proper structure
        print("\n📋 Progress Tracker Structure:")
        for key in executor.progress_tracker.keys():
            if key.startswith("phase"):
                agents_count = len(executor.progress_tracker[key].get("agents", {}))
                print(f"  {key}: {agents_count} agents")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing ClaudeCodeExecutor: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_claude_executor()
    sys.exit(0 if success else 1)