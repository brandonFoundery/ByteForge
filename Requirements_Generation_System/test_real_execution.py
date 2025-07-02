#!/usr/bin/env python3
"""
Test real Claude Code execution to verify it generates files
"""

import asyncio
import sys
from pathlib import Path
from claude_code_executor import ClaudeCodeExecutor

async def test_real_execution():
    """Test real Claude Code execution with a simple backend agent"""
    print("🚀 Testing Real Claude Code Execution")
    print("=" * 60)
    
    # Initialize the executor
    base_path = Path(__file__).parent
    executor = ClaudeCodeExecutor(base_path)
    
    print(f"✅ Executor initialized")
    print(f"   Working directory will be: {executor.code_output_path}")
    
    # Reset backend-phase1 status first
    print("\n🔄 Resetting backend-phase1 status...")
    try:
        if "phase1_mvp_core_features" in executor.progress_tracker:
            if "backend-phase1" in executor.progress_tracker["phase1_mvp_core_features"]["agents"]:
                backend_agent = executor.progress_tracker["phase1_mvp_core_features"]["agents"]["backend-phase1"]
                backend_agent["status"] = "not_started"
                backend_agent["started_at"] = None
                backend_agent["completed_at"] = None
                backend_agent["actual_duration_minutes"] = None
                backend_agent["error_log"] = None
                backend_agent["retry_count"] = 0
                
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
    
    # Test single backend agent execution
    print("\n🧪 Testing backend agent execution...")
    try:
        # Execute just the backend agent for phase1
        result = await executor.execute_implementation("2", "1")  # agent_choice="2" (backend), phase_choice="1" (phase1)
        
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
        
        # Check if files were generated
        print(f"\n📁 Checking for generated files in {executor.code_output_path}...")
        if executor.code_output_path.exists():
            generated_files = list(executor.code_output_path.rglob("*"))
            generated_files = [f for f in generated_files if f.is_file()]
            
            if generated_files:
                print(f"✅ Found {len(generated_files)} generated files:")
                for file in generated_files[:10]:  # Show first 10 files
                    rel_path = file.relative_to(executor.code_output_path)
                    print(f"   • {rel_path}")
                if len(generated_files) > 10:
                    print(f"   ... and {len(generated_files) - 10} more files")
            else:
                print("⚠️  No files found in code output directory")
        else:
            print("❌ Code output directory does not exist")
        
        if result.success:
            print("\n🎉 SUCCESS! Claude Code executed and completed successfully!")
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
        success = asyncio.run(test_real_execution())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
