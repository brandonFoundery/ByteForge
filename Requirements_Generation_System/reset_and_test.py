#!/usr/bin/env python3
"""
Reset backend agent status and test the Claude Code executor fix
"""

import asyncio
import json
import sys
from pathlib import Path
from claude_code_executor import ClaudeCodeExecutor

async def reset_and_test():
    """Reset backend agent status and test execution"""
    print("🔄 Resetting Backend Agent Status and Testing Fix")
    print("=" * 60)
    
    # Initialize the executor
    base_path = Path(__file__).parent
    executor = ClaudeCodeExecutor(base_path)
    
    print(f"✅ Executor initialized")
    print(f"   Environment: Windows={executor.is_windows}, WSL={executor.is_wsl}, Needs WSL={executor.needs_wsl}")
    
    # Reset backend-phase1 status
    print("\n🔄 Resetting backend-phase1 status...")
    try:
        # Update the progress tracker to reset backend-phase1
        if "phase1_mvp_core_features" in executor.progress_tracker:
            if "backend-phase1" in executor.progress_tracker["phase1_mvp_core_features"]["agents"]:
                backend_agent = executor.progress_tracker["phase1_mvp_core_features"]["agents"]["backend-phase1"]
                backend_agent["status"] = "not_started"
                backend_agent["started_at"] = None
                backend_agent["completed_at"] = None
                backend_agent["actual_duration_minutes"] = None
                backend_agent["error_log"] = None
                backend_agent["retry_count"] = 0
                
                # Save the updated progress tracker
                executor._save_progress_tracker()
                print("✅ Backend-phase1 status reset to 'not_started'")
            else:
                print("❌ Backend-phase1 not found in progress tracker")
                return False
        else:
            print("❌ Phase1 not found in progress tracker")
            return False
            
    except Exception as e:
        print(f"❌ Failed to reset status: {e}")
        return False
    
    # Test single agent execution (backend only)
    print("\n🧪 Testing backend agent execution with fix...")
    try:
        # Execute just the backend agent for phase1
        result = await executor.execute_implementation("1", "1")  # agent_choice="1" (backend), phase_choice="1" (phase1)
        
        print(f"\n📊 Execution Results:")
        print(f"   Success: {result.success}")
        print(f"   Total time: {result.total_execution_time:.2f}s")
        print(f"   Agent results: {len(result.agent_results)}")
        
        for agent_result in result.agent_results:
            status = "✅ SUCCESS" if agent_result.success else "❌ FAILED"
            print(f"   • {agent_result.agent_name}: {status}")
            if agent_result.error_message:
                print(f"     Error: {agent_result.error_message}")
            print(f"     Execution time: {agent_result.execution_time:.2f}s")
        
        if result.success:
            print("\n🎉 SUCCESS! The fix is working - backend agent executed without WSL double-hop error!")
            return True
        else:
            print(f"\n❌ FAILED: {result.error_summary}")
            print("Check the logs for detailed error information:")
            log_file = base_path / "logs" / "backend_phase1_claude_execution.log"
            print(f"   Log file: {log_file}")
            return False
            
    except Exception as e:
        print(f"❌ Execution test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(reset_and_test())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
