#!/usr/bin/env python3
"""
Test script to verify the Claude Code executor fix
"""

import asyncio
import sys
from pathlib import Path
from claude_code_executor import ClaudeCodeExecutor

async def test_claude_executor():
    """Test the Claude Code executor with the fix"""
    print("🧪 Testing Claude Code Executor Fix")
    print("=" * 50)
    
    # Initialize the executor
    base_path = Path(__file__).parent
    executor = ClaudeCodeExecutor(base_path)
    
    print(f"✅ Executor initialized successfully")
    print(f"   Environment: Windows={executor.is_windows}, WSL={executor.is_wsl}, Needs WSL={executor.needs_wsl}")
    print(f"   ByteForge path: {executor.byteforge_path}")
    print(f"   Instructions path: {executor.instructions_path}")
    
    # Check if instruction files exist
    instruction_files = list(executor.instructions_path.glob("*.md"))
    print(f"📁 Found {len(instruction_files)} instruction files:")
    for file in instruction_files[:5]:  # Show first 5
        print(f"   • {file.name}")
    if len(instruction_files) > 5:
        print(f"   ... and {len(instruction_files) - 5} more")
    
    if not instruction_files:
        print("❌ No instruction files found - cannot test execution")
        return False
    
    # Test command generation (without actually executing)
    print("\n🔧 Testing command generation...")
    try:
        # Create a test agent
        test_agent = {"id": "backend", "name": "Backend Agent"}
        phase_id = "phase1"
        
        # Load an instruction file for testing
        instruction_content = executor._load_instruction_file("backend", "phase1")
        if not instruction_content:
            print("❌ Could not load backend-phase1 instruction file")
            return False
        
        print(f"✅ Loaded instruction file successfully ({len(instruction_content)} chars)")
        
        # Generate command
        command = executor._create_claude_command_from_instruction(test_agent, phase_id, instruction_content)
        print(f"✅ Command generated successfully")
        print(f"   Command: {command}")
        
        # Verify the fix - command should NOT contain nested 'wsl' calls
        if executor.needs_wsl and "wsl" in command:
            print("❌ FAILED: Command contains 'wsl' when it shouldn't (double-hop issue)")
            return False
        elif not executor.needs_wsl and "wsl" in command:
            print("⚠️  WARNING: Command contains 'wsl' but we're not in Windows->WSL mode")
        
        print("✅ Command generation test PASSED - no double-hop WSL issue detected")
        
    except Exception as e:
        print(f"❌ Command generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n🎉 All tests passed! The fix appears to be working correctly.")
    return True

if __name__ == "__main__":
    try:
        success = asyncio.run(test_claude_executor())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
