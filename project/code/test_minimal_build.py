#!/usr/bin/env python3
"""
Minimal test to see what compilation errors we still have by checking key files
"""

import os
import subprocess
import glob

def check_cs_files():
    """Check C# files for obvious syntax errors"""
    print("=== Checking C# files for basic syntax ===")
    
    cs_files = glob.glob("**/*.cs", recursive=True)
    issues = []
    
    for file in cs_files[:10]:  # Check first 10 files
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Check for basic issues
                if 'using LeadProcessing' in content:
                    issues.append(f"{file}: Still contains 'using LeadProcessing' references")
                    
                if 'namespace LeadProcessing' in content:
                    issues.append(f"{file}: Still contains 'namespace LeadProcessing' declarations")
                    
                # Count braces to check for basic syntax
                open_braces = content.count('{')
                close_braces = content.count('}')
                if open_braces != close_braces:
                    issues.append(f"{file}: Mismatched braces - {open_braces} open, {close_braces} close")
                    
        except Exception as e:
            issues.append(f"{file}: Error reading file - {e}")
    
    return issues

def check_project_file():
    """Check the project file"""
    print("=== Checking project file ===")
    
    project_files = glob.glob("*.csproj")
    if not project_files:
        return ["No .csproj file found"]
        
    issues = []
    for proj_file in project_files:
        try:
            with open(proj_file, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"Project file: {proj_file}")
                
                # Check for EF versions
                if 'Microsoft.EntityFrameworkCore' in content:
                    print("✓ Entity Framework packages found")
                else:
                    issues.append(f"{proj_file}: No Entity Framework packages found")
                    
                # Check for consistent versions
                if '8.0.12' in content:
                    print("✓ Version 8.0.12 found (consistent versioning)")
                else:
                    issues.append(f"{proj_file}: No version 8.0.12 found")
                    
        except Exception as e:
            issues.append(f"{proj_file}: Error reading - {e}")
            
    return issues

def check_database():
    """Check database file"""
    print("=== Checking database ===")
    
    db_files = glob.glob("*.db")
    if not db_files:
        return ["No .db files found - may need to create database"]
        
    issues = []
    for db_file in db_files:
        if os.path.exists(db_file):
            size = os.path.getsize(db_file)
            print(f"✓ Database file: {db_file} ({size} bytes)")
        else:
            issues.append(f"Database file {db_file} does not exist")
            
    return issues

def main():
    print("ByteForge Frontend - Minimal Build Check")
    print("=" * 50)
    
    all_issues = []
    
    # Check C# files
    cs_issues = check_cs_files()
    all_issues.extend(cs_issues)
    
    # Check project file
    proj_issues = check_project_file()
    all_issues.extend(proj_issues)
    
    # Check database
    db_issues = check_database()
    all_issues.extend(db_issues)
    
    print("\n=== SUMMARY ===")
    if all_issues:
        print("❌ Issues found:")
        for issue in all_issues:
            print(f"  - {issue}")
    else:
        print("✅ No obvious issues found!")
        
    print(f"\n📊 Total issues: {len(all_issues)}")
    return len(all_issues)

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)