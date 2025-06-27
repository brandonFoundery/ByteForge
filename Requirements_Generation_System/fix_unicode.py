#!/usr/bin/env python3
"""
Fix Unicode characters in Python files for Windows compatibility
"""

import re
from pathlib import Path

def fix_unicode_in_file(file_path: Path):
    """Replace Unicode characters with ASCII equivalents"""
    
    # Unicode to ASCII mappings
    replacements = {
        '✓': '[OK]',
        '✅': '[OK]',
        '❌': '[ERROR]',
        '⚠️': '[WARNING]',
        '🎉': '[SUCCESS]',
        '✨': '[COMPLETE]',
        '📄': '[FILE]',
        '📁': '[FOLDER]',
        '📋': '[INFO]',
        '🔧': '[TOOL]',
        '💡': '[TIP]',
        '⏱️': '[TIME]',
        '📺': '[DISPLAY]',
        '⏸️': '[PAUSE]',
        '🔍': '[SEARCH]',
        '⏭': '[SKIP]',
        '✗': '[FAIL]'
    }
    
    try:
        # Read the file
        content = file_path.read_text(encoding='utf-8')
        
        # Apply replacements
        modified = False
        for unicode_char, ascii_replacement in replacements.items():
            if unicode_char in content:
                content = content.replace(unicode_char, ascii_replacement)
                modified = True
                print(f"Replaced '{unicode_char}' with '{ascii_replacement}' in {file_path.name}")
        
        # Write back if modified
        if modified:
            file_path.write_text(content, encoding='utf-8')
            print(f"Updated {file_path.name}")
        else:
            print(f"No changes needed in {file_path.name}")
            
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

def main():
    """Fix Unicode characters in key Python files"""
    
    current_dir = Path(__file__).parent
    files_to_fix = [
        current_dir / "run_generation.py",
        current_dir / "orchestrator.py"
    ]
    
    for file_path in files_to_fix:
        if file_path.exists():
            print(f"\nProcessing {file_path.name}...")
            fix_unicode_in_file(file_path)
        else:
            print(f"File not found: {file_path}")
    
    print("\nUnicode fix completed!")

if __name__ == "__main__":
    main()
