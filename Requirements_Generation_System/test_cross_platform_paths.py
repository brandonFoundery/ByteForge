#!/usr/bin/env python3
"""
Test Cross-Platform Path Compatibility
Tests the universal path structure from both Windows and WSL environments.
"""

import platform
from pathlib import Path
import sys

def test_universal_paths():
    """Test the universal path structure"""
    print("🧪 Testing Universal Path Structure")
    print(f"Platform: {platform.system()}")
    print(f"Python: {sys.version}")
    
    # Universal Path Structure - ALWAYS relative to Requirements_Generation_System
    base_path = Path(__file__).parent.resolve()  # Requirements_Generation_System directory (absolute)
    print(f"Base Path (Requirements_Generation_System): {base_path}")
    
    # ByteForgePath = {relative_path}\ByteForge
    byteforge_path = base_path.parent  # ByteForge directory (parent of Requirements_Generation_System)
    print(f"ByteForge Path: {byteforge_path}")
    
    # ByteForgeProjectPath = {ByteForgePath}\project  
    byteforge_project_path = byteforge_path / "project"
    print(f"ByteForge Project Path: {byteforge_project_path}")
    
    # All generated content goes under ByteForgeProjectPath
    paths_to_test = {
        "Instructions": byteforge_project_path / "design" / "claude_instructions",
        "Code Output": byteforge_project_path / "code",
        "Design": byteforge_project_path / "design",
        "Requirements": byteforge_project_path / "requirements",
        "Requirements Artifacts": byteforge_project_path / "requirements_artifacts",
        "Generation Status": byteforge_project_path / "generation_status",
    }
    
    print("\n📁 Testing Path Existence:")
    all_good = True
    for name, path in paths_to_test.items():
        exists = path.exists()
        status = "✅" if exists else "❌"
        print(f"  {status} {name}: {path}")
        if not exists and name in ["Design", "Requirements Artifacts"]:
            all_good = False
    
    # Test cross-platform path conversion
    print("\n🔄 Testing Cross-Platform Path Conversion:")
    
    # Simulate WSL path conversion
    def convert_to_wsl_path(windows_path: str) -> str:
        """Convert Windows path to WSL path format"""
        wsl_path = windows_path.replace("\\", "/")
        if len(wsl_path) >= 2 and wsl_path[1] == ":":
            drive_letter = wsl_path[0].lower()
            wsl_path = f"/mnt/{drive_letter}" + wsl_path[2:]
        return wsl_path
    
    for name, path in paths_to_test.items():
        windows_path = str(path)
        wsl_path = convert_to_wsl_path(windows_path)
        print(f"  {name}:")
        print(f"    Windows: {windows_path}")
        print(f"    WSL:     {wsl_path}")
    
    print(f"\n🎯 Universal Path Structure Test: {'✅ PASSED' if all_good else '❌ FAILED'}")
    return all_good

if __name__ == "__main__":
    test_universal_paths()
