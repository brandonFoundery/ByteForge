#!/usr/bin/env python3
"""
Script to automatically add missing using statements to C# files
"""

import os
import re
import glob
from typing import Dict, List, Set

# Common missing using statements and their typical indicators
COMMON_USINGS = {
    'System': ['Uri', 'InvalidOperationException', 'ArgumentException', 'ArgumentNullException', 'Exception', 'DateTime', 'TimeSpan', 'Guid'],
    'System.Threading.Tasks': ['Task'],
    'System.Collections.Generic': ['Dictionary', 'List', 'IEnumerable'],
    'System.Linq': ['Any', 'FirstOrDefault', 'Where', 'Select'],
    'Microsoft.Extensions.Logging': ['ILogger', 'LogInformation', 'LogError', 'LogWarning'],
    'Microsoft.AspNetCore.Mvc': ['Controller', 'IActionResult', 'ActionResult'],
    'Microsoft.AspNetCore.Authorization': ['Authorize'],
    'Microsoft.EntityFrameworkCore': ['DbContext', 'DbSet'],
    'System.ComponentModel.DataAnnotations': ['Required', 'StringLength', 'Display'],
    'Azure.Core': ['DefaultAzureCredential'],
    'Azure.Identity': ['DefaultAzureCredential'],
    'System.Text.Json': ['JsonSerializer'],
    'Newtonsoft.Json': ['JsonConvert'],
}

def has_using_statement(content: str, using_namespace: str) -> bool:
    """Check if the file already has a specific using statement"""
    pattern = rf'^\s*using\s+{re.escape(using_namespace)}\s*;'
    return bool(re.search(pattern, content, re.MULTILINE))

def needs_using_statement(content: str, namespace: str, indicators: List[str]) -> bool:
    """Check if the file needs a specific using statement based on indicators"""
    if has_using_statement(content, namespace):
        return False
    
    # Check if any of the indicators are used in the code
    for indicator in indicators:
        # Look for class usage, method calls, etc.
        patterns = [
            rf'\b{re.escape(indicator)}\b',  # Direct usage
            rf'new\s+{re.escape(indicator)}\s*\(',  # Constructor calls
            rf'{re.escape(indicator)}\.',  # Static method calls
        ]
        
        for pattern in patterns:
            if re.search(pattern, content):
                return True
    
    return False

def get_existing_usings(content: str) -> List[str]:
    """Extract existing using statements from the file"""
    pattern = r'^\s*using\s+([^;]+)\s*;'
    matches = re.findall(pattern, content, re.MULTILINE)
    return [match.strip() for match in matches]

def add_using_statements(file_path: str, new_usings: List[str]) -> bool:
    """Add new using statements to a C# file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        existing_usings = get_existing_usings(content)
        
        # Filter out usings that already exist
        usings_to_add = [using for using in new_usings if using not in existing_usings]
        
        if not usings_to_add:
            return False
        
        # Find the location to insert using statements
        # Look for existing using statements or namespace declaration
        using_pattern = r'((?:^\s*using\s+[^;]+;\s*\n)*)'
        namespace_pattern = r'(^\s*namespace\s+[^;\n{]+[{\n])'
        
        # Try to find existing using statements first
        using_match = re.search(using_pattern, content, re.MULTILINE)
        namespace_match = re.search(namespace_pattern, content, re.MULTILINE)
        
        if using_match and using_match.group(1).strip():
            # Insert after existing using statements
            insert_pos = using_match.end()
            new_using_block = ''.join(f'using {using};\n' for using in sorted(usings_to_add))
        elif namespace_match:
            # Insert before namespace declaration
            insert_pos = namespace_match.start()
            new_using_block = ''.join(f'using {using};\n' for using in sorted(usings_to_add)) + '\n'
        else:
            # Insert at the beginning of the file
            insert_pos = 0
            new_using_block = ''.join(f'using {using};\n' for using in sorted(usings_to_add)) + '\n'
        
        # Insert the new using statements
        new_content = content[:insert_pos] + new_using_block + content[insert_pos:]
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ Added {len(usings_to_add)} using statements to {file_path}")
        for using in usings_to_add:
            print(f"   + using {using};")
        
        return True
        
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False

def fix_using_statements():
    """Fix missing using statements in all C# files"""
    print("🔧 Fixing missing using statements in C# files...")
    
    # Find all C# files except in obj/bin directories
    cs_files = glob.glob('**/*.cs', recursive=True)
    cs_files = [f for f in cs_files if '/obj/' not in f and '/bin/' not in f]
    
    files_modified = 0
    total_usings_added = 0
    
    for file_path in cs_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            usings_to_add = []
            
            # Check each namespace/using combination
            for namespace, indicators in COMMON_USINGS.items():
                if needs_using_statement(content, namespace, indicators):
                    usings_to_add.append(namespace)
            
            if usings_to_add:
                if add_using_statements(file_path, usings_to_add):
                    files_modified += 1
                    total_usings_added += len(usings_to_add)
        
        except Exception as e:
            print(f"❌ Error reading {file_path}: {e}")
    
    print(f"\n📊 SUMMARY:")
    print(f"   Files processed: {len(cs_files)}")
    print(f"   Files modified: {files_modified}")
    print(f"   Using statements added: {total_usings_added}")

if __name__ == "__main__":
    fix_using_statements()