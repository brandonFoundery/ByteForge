#!/usr/bin/env python3
"""
Simplified ByteForge App Generation System
Cross-platform compatible version without external dependencies
"""

import os
import sys
from pathlib import Path
import json

def print_banner():
    print("╭─────────────────────────────────────────────────╮")
    print("│ ByteForge App Generation System                 │")
    print("│ Automated Code Generation with Claude Code     │")
    print("╰─────────────────────────────────────────────────╯")
    print()

def check_environment():
    """Check if the environment is properly set up"""
    print("Checking environment...")
    print()
    
    issues = []
    
    # Check if we're in the right directory
    if not os.path.exists("config.yaml"):
        issues.append("config.yaml not found - run from Requirements_Generation_System directory")
    
    # Check requirements directory (relative path)
    requirements_dir = "../project/requirements"
    if not os.path.exists(requirements_dir):
        issues.append(f"Requirements Directory not found: {os.path.abspath(requirements_dir)}")
    
    # Check if code was already generated
    code_dir = "../project/code"
    if os.path.exists(code_dir):
        files = []
        for root, dirs, filenames in os.walk(code_dir):
            files.extend(filenames)
        print(f"✅ Code directory found with {len(files)} files")
    else:
        print("📁 Code directory not found - ready for generation")
    
    if issues:
        print("Environment issues found:")
        for issue in issues:
            print(f"  [ERROR] {issue}")
        print()
        return False
    else:
        print("✅ Environment looks good!")
        print()
        return True

def show_main_menu():
    """Show the main generation menu"""
    print("🚀 Code Generation Options:")
    print()
    print("  1. View Generated Code Status")
    print("  2. Monitor Code Generation")
    print("  3. Build and Test Generated Code")
    print("  4. Instructions for Manual Generation")
    print("  5. Claude Code Integration Guide")
    print("  0. Exit")
    print()

def show_code_status():
    """Show the status of generated code"""
    print("📊 Generated Code Status:")
    print("="*50)
    
    code_dir = "../project/code"
    if not os.path.exists(code_dir):
        print("❌ No code generated yet")
        return
    
    components = {
        "Backend": "LSOMigrator.Backend",
        "Frontend": "LSOMigrator.Frontend", 
        "Infrastructure": "terraform",
        "Security": "Security",
        "Integration": "Integration"
    }
    
    for name, subdir in components.items():
        path = os.path.join(code_dir, subdir)
        if os.path.exists(path):
            files = []
            for root, dirs, filenames in os.walk(path):
                files.extend(filenames)
            print(f"✅ {name}: {len(files)} files")
        else:
            print(f"❌ {name}: Not generated")
    
    print()

def show_manual_instructions():
    """Show instructions for manual code generation"""
    print("📋 Manual Code Generation Instructions:")
    print("="*50)
    print()
    print("The LSOMigrator application code has been successfully generated!")
    print("Here's how to work with it:")
    print()
    print("🔧 Backend (ASP.NET Core):")
    print("  cd ../project/code/LSOMigrator.Backend")
    print("  dotnet restore")
    print("  dotnet build")
    print("  dotnet run --project LSOMigrator.Api")
    print()
    print("🌐 Frontend (Next.js):")
    print("  cd ../project/code/LSOMigrator.Frontend")
    print("  npm install")
    print("  npm run dev")
    print()
    print("☁️ Infrastructure (Terraform):")
    print("  cd ../project/code/terraform")
    print("  terraform init")
    print("  terraform plan")
    print("  terraform apply")
    print()

def show_claude_guide():
    """Show Claude Code integration guide"""
    print("🤖 Claude Code Integration Guide:")
    print("="*50)
    print()
    print("The code generation system uses Claude Code for automated development.")
    print("Here's how to use it:")
    print()
    print("💡 Basic Claude Commands:")
    print("  claude --model sonnet --dangerously-skip-permissions --print \"Your prompt here\"")
    print()
    print("📁 Working Directory:")
    print("  Always run from: D:\\Repository\\ContractLogix\\LSOMitigator\\ByteForge")
    print("  Code outputs to: project/code/")
    print()
    print("🎯 Example Generation Commands:")
    print("  # Generate more backend features")
    print("  claude --model sonnet --dangerously-skip-permissions --print \\")
    print("    \"Add user management features to the LSOMigrator backend in project/code/\"")
    print()
    print("  # Generate frontend pages")
    print("  claude --model sonnet --dangerously-skip-permissions --print \\")
    print("    \"Create dashboard and reports pages for LSOMigrator frontend in project/code/\"")
    print()

def monitor_generation():
    """Show how to monitor generation"""
    print("👀 Monitoring Code Generation:")
    print("="*50)
    print()
    print("Use these methods to monitor generation progress:")
    print()
    print("🔍 Real-time Monitor:")
    print("  python3 monitor_generation.py")
    print()
    print("📝 Check Logs:")
    print("  ls -la logs/*.log")
    print("  tail -f logs/backend_generation.log")
    print()
    print("📁 View Generated Files:")
    print("  find ../project/code -name \"*.cs\" -o -name \"*.tsx\" -o -name \"*.ts\"")
    print()

def build_test_code():
    """Show how to build and test the generated code"""
    print("🔨 Build and Test Instructions:")
    print("="*50)
    print()
    
    backend_path = "../project/code/LSOMigrator.Backend"
    frontend_path = "../project/code/LSOMigrator.Frontend"
    
    if os.path.exists(backend_path):
        print("🔧 Backend Build:")
        print(f"  cd {backend_path}")
        print("  dotnet restore")
        print("  dotnet build")
        print("  dotnet test  # if tests exist")
        print()
    
    if os.path.exists(frontend_path):
        print("🌐 Frontend Build:")
        print(f"  cd {frontend_path}")
        print("  npm install")
        print("  npm run build")
        print("  npm run lint")
        print()
    
    print("🚀 To run the application:")
    print("  Backend: dotnet run --project LSOMigrator.Api")
    print("  Frontend: npm run dev")
    print()

def main():
    """Main application loop"""
    print_banner()
    
    if not check_environment():
        print("Please fix the environment issues before running.")
        return 1
    
    while True:
        show_main_menu()
        
        try:
            choice = input("Select an option: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            return 0
        
        print()
        
        if choice == "0":
            print("Goodbye!")
            return 0
        elif choice == "1":
            show_code_status()
        elif choice == "2":
            monitor_generation()
        elif choice == "3":
            build_test_code()
        elif choice == "4":
            show_manual_instructions()
        elif choice == "5":
            show_claude_guide()
        else:
            print("Invalid option. Please try again.")
        
        print()
        input("Press Enter to continue...")
        print()

if __name__ == "__main__":
    sys.exit(main())