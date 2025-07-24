#!/usr/bin/env python3
"""
Comprehensive build diagnostics to identify compilation errors
"""

import os
import glob
import re
from collections import defaultdict

def analyze_cs_files():
    """Analyze C# files for potential compilation issues"""
    print("🔍 Analyzing C# files for compilation issues...")
    
    issues = []
    cs_files = glob.glob("**/*.cs", recursive=True)
    
    # Skip build artifacts
    cs_files = [f for f in cs_files if '/obj/' not in f and '/bin/' not in f]
    
    for file_path in cs_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
                # Check for basic syntax issues
                open_braces = content.count('{')
                close_braces = content.count('}')
                if open_braces != close_braces:
                    issues.append(f"❌ {file_path}: Mismatched braces ({open_braces} open, {close_braces} close)")
                
                # Check for missing using statements patterns
                if 'Task<' in content and 'using System.Threading.Tasks;' not in content:
                    issues.append(f"⚠️  {file_path}: Missing 'using System.Threading.Tasks;'")
                
                if 'Dictionary<' in content and 'using System.Collections.Generic;' not in content:
                    issues.append(f"⚠️  {file_path}: Missing 'using System.Collections.Generic;'")
                
                if 'ILogger<' in content and 'using Microsoft.Extensions.Logging;' not in content:
                    issues.append(f"⚠️  {file_path}: Missing 'using Microsoft.Extensions.Logging;'")
                
                # Check for undefined classes/interfaces being used
                undefined_references = []
                
                # Look for class instantiations that might be undefined
                class_instantiation_pattern = re.compile(r'new\s+([A-Z][A-Za-z0-9_]+)')
                interface_usage_pattern = re.compile(r':\s*I([A-Z][A-Za-z0-9_]+)')
                
                for match in class_instantiation_pattern.finditer(content):
                    class_name = match.group(1)
                    if class_name not in ['List', 'Dictionary', 'StringBuilder', 'DateTime', 'Guid', 'TimeSpan']:
                        if f'class {class_name}' not in content and f'public {class_name}(' not in content:
                            undefined_references.append(class_name)
                
                if undefined_references:
                    for ref in set(undefined_references[:3]):  # Limit to 3 per file
                        issues.append(f"⚠️  {file_path}: Potentially undefined class '{ref}'")
                        
        except Exception as e:
            issues.append(f"❌ {file_path}: Error reading file - {e}")
    
    return issues

def check_missing_implementations():
    """Check for missing interface implementations"""
    print("\n🔧 Checking for missing interface implementations...")
    
    issues = []
    interface_files = glob.glob("**/I*.cs", recursive=True)
    interface_files = [f for f in interface_files if '/obj/' not in f and '/bin/' not in f]
    
    interfaces_and_methods = {}
    
    # Extract interface definitions
    for file_path in interface_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Find interface names
                interface_pattern = re.compile(r'public interface (I[A-Za-z0-9_]+)')
                method_pattern = re.compile(r'^\s*(Task<[^>]+>|Task|[A-Za-z0-9_<>]+)\s+([A-Za-z0-9_]+)\s*\([^)]*\);', re.MULTILINE)
                
                for interface_match in interface_pattern.finditer(content):
                    interface_name = interface_match.group(1)
                    
                    # Find methods in this interface
                    methods = []
                    for method_match in method_pattern.finditer(content):
                        method_name = method_match.group(2)
                        if method_name not in ['get', 'set']:  # Skip property accessors
                            methods.append(method_name)
                    
                    interfaces_and_methods[interface_name] = methods
                    
        except Exception as e:
            issues.append(f"❌ Error reading interface file {file_path}: {e}")
    
    # Check for implementations
    implementation_files = glob.glob("**/*.cs", recursive=True)
    implementation_files = [f for f in implementation_files if '/obj/' not in f and '/bin/' not in f and not f.endswith('/I*.cs')]
    
    for interface_name, methods in interfaces_and_methods.items():
        implementation_class = interface_name[1:]  # Remove 'I' prefix
        
        found_implementation = False
        for file_path in implementation_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    if f'class {implementation_class}' in content and f': {interface_name}' in content:
                        found_implementation = True
                        
                        # Check if all methods are implemented
                        for method in methods:
                            if f'public async Task' in content or f'public Task' in content:
                                # Look for method implementations
                                method_impl_pattern = re.compile(rf'public\s+(?:async\s+)?(?:Task<?[^>]*>?|[A-Za-z0-9_<>]+)\s+{method}\s*\(')
                                if not method_impl_pattern.search(content):
                                    issues.append(f"⚠️  {file_path}: Missing implementation for {interface_name}.{method}")
                        break
                        
            except Exception:
                continue
        
        if not found_implementation:
            issues.append(f"❌ Missing implementation class for interface {interface_name}")
    
    return issues

def check_dependency_issues():
    """Check for dependency and package reference issues"""
    print("\n📦 Checking dependency issues...")
    
    issues = []
    
    # Check project file
    project_files = glob.glob("*.csproj")
    if not project_files:
        issues.append("❌ No .csproj file found")
        return issues
    
    try:
        with open(project_files[0], 'r', encoding='utf-8') as f:
            project_content = f.read()
            
            # Check for version conflicts
            ef_versions = re.findall(r'Microsoft\.EntityFrameworkCore[^"]*" Version="([^"]+)"', project_content)
            if len(set(ef_versions)) > 1:
                issues.append(f"❌ Entity Framework version conflict: {set(ef_versions)}")
            
            # Check for required packages
            required_packages = [
                'Microsoft.EntityFrameworkCore.Design',
                'Microsoft.EntityFrameworkCore.SqlServer',
                'Microsoft.EntityFrameworkCore.Sqlite',
                'Microsoft.AspNetCore.Identity.EntityFrameworkCore',
                'StackExchange.Redis'
            ]
            
            for package in required_packages:
                if package not in project_content:
                    issues.append(f"⚠️  Missing package reference: {package}")
                    
    except Exception as e:
        issues.append(f"❌ Error reading project file: {e}")
    
    return issues

def check_configuration_issues():
    """Check for configuration and startup issues"""
    print("\n⚙️ Checking configuration issues...")
    
    issues = []
    
    # Check Program.cs
    program_files = glob.glob("**/Program.cs", recursive=True)
    if not program_files:
        issues.append("❌ Program.cs not found")
        return issues
    
    try:
        with open(program_files[0], 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for common startup issues
            if 'AddDbContext' not in content:
                issues.append("⚠️  Program.cs: Missing AddDbContext call")
            
            if 'AddIdentity' not in content and 'AddDefaultIdentity' not in content:
                issues.append("⚠️  Program.cs: Missing Identity configuration")
            
            # Check for undefined service registrations
            undefined_services = []
            service_pattern = re.compile(r'services\.Add\w*<([^,>]+)')
            
            for match in service_pattern.finditer(content):
                service_name = match.group(1)
                if service_name.startswith('I') and service_name not in ['IConfiguration', 'ILogger', 'IServiceCollection']:
                    # Check if this interface exists
                    if not glob.glob(f"**/{service_name}.cs", recursive=True):
                        undefined_services.append(service_name)
            
            if undefined_services:
                for service in set(undefined_services[:3]):
                    issues.append(f"⚠️  Program.cs: Potentially undefined service interface '{service}'")
                    
    except Exception as e:
        issues.append(f"❌ Error reading Program.cs: {e}")
    
    return issues

def check_database_issues():
    """Check for database-related issues"""
    print("\n🗄️ Checking database configuration...")
    
    issues = []
    
    # Check if database file exists
    db_files = glob.glob("*.db")
    if not db_files:
        issues.append("⚠️  No database files found - may need to run migrations")
    
    # Check ApplicationDbContext
    dbcontext_files = glob.glob("**/ApplicationDbContext.cs", recursive=True)
    if not dbcontext_files:
        issues.append("❌ ApplicationDbContext.cs not found")
        return issues
    
    try:
        with open(dbcontext_files[0], 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for entity configurations
            if 'DbSet<' not in content:
                issues.append("⚠️  ApplicationDbContext: No DbSet properties defined")
            
            # Check for old entity references
            old_entities = ['Lead>', 'ExternalServices', 'Nppes']
            for entity in old_entities:
                if entity in content:
                    issues.append(f"⚠️  ApplicationDbContext: Still contains old entity reference '{entity}'")
                    
    except Exception as e:
        issues.append(f"❌ Error reading ApplicationDbContext: {e}")
    
    return issues

def main():
    print("ByteForge Frontend - Build Diagnostics")
    print("=" * 60)
    
    all_issues = []
    
    # Run all diagnostic checks
    all_issues.extend(analyze_cs_files())
    all_issues.extend(check_missing_implementations())
    all_issues.extend(check_dependency_issues())
    all_issues.extend(check_configuration_issues())
    all_issues.extend(check_database_issues())
    
    # Categorize issues
    critical_issues = [issue for issue in all_issues if issue.startswith('❌')]
    warning_issues = [issue for issue in all_issues if issue.startswith('⚠️')]
    
    print("\n" + "=" * 60)
    print("📊 BUILD DIAGNOSTICS SUMMARY")
    print("=" * 60)
    
    print(f"\n🔴 Critical Issues: {len(critical_issues)}")
    for issue in critical_issues[:10]:  # Show first 10 critical issues
        print(f"  {issue}")
    
    if len(critical_issues) > 10:
        print(f"  ... and {len(critical_issues) - 10} more critical issues")
    
    print(f"\n🟡 Warnings: {len(warning_issues)}")
    for issue in warning_issues[:10]:  # Show first 10 warnings
        print(f"  {issue}")
    
    if len(warning_issues) > 10:
        print(f"  ... and {len(warning_issues) - 10} more warnings")
    
    print(f"\n📈 Total Issues: {len(all_issues)}")
    
    if len(critical_issues) == 0:
        print("✅ No critical compilation blockers found!")
        print("🎉 Project should compile successfully")
        return 0
    else:
        print("❌ Critical issues found that will prevent compilation")
        print("🔧 These issues must be resolved before the project will build")
        return len(critical_issues)

if __name__ == "__main__":
    exit_code = main()
    exit(min(exit_code, 1))