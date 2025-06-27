#!/usr/bin/env python3
"""
Test the prompt logging functionality
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from ui_style_system.llm_ui_generator import LLMUIGenerator
from rich.console import Console

console = Console()

def main():
    """Test the prompt logging functionality"""
    
    console.print("🧪 Testing prompt logging functionality...")
    
    # Get project root
    project_root = Path(__file__).parent.parent.parent
    
    # Create generator
    generator = LLMUIGenerator(project_root)
    
    # Test prompt creation and logging
    test_image = "ui_style_1.png"
    test_model = "OpenAI GPT-4o"
    
    console.print(f"\n📝 Creating prompt for {test_model} + {test_image}...")
    
    # Create the prompt
    prompt = generator.create_ui_generation_prompt(test_image)
    
    # Log the prompt details
    generator.log_prompt_details(test_model, test_image, prompt)
    
    console.print(f"\n✅ Prompt logging test complete!")
    console.print(f"📁 Check the logs/ directory for saved prompt files")
    
    # Show logs directory contents
    logs_dir = generator.ui_system_path / "logs"
    if logs_dir.exists():
        log_files = list(logs_dir.glob("*.txt"))
        console.print(f"\n📋 Log files found:")
        for log_file in log_files:
            console.print(f"   📄 {log_file.name}")
    else:
        console.print(f"\n⚠️  Logs directory not found: {logs_dir}")

if __name__ == "__main__":
    main()
