#!/usr/bin/env python3
"""
Comprehensive validation script to verify all compilation errors have been resolved
"""

import os
import glob
import re
from collections import defaultdict

def check_namespace_consistency():
    """Check that all namespaces are consistent"""
    print("🔍 Checking namespace consistency...")
    issues = []
    
    cs_files = glob.glob("**/*.cs", recursive=True)
    namespace_pattern = re.compile(r'namespace\s+([^;\s{]+)')
    using_pattern = re.compile(r'using\s+([^;\s]+);')
    
    for file in cs_files:
        if '/obj/' in file or '/bin/' in file:
            continue
            
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Check for old LeadProcessing references
                if 'LeadProcessing' in content:
                    issues.append(f"❌ {file}: Still contains 'LeadProcessing' references")
                
                # Check namespace declarations
                namespaces = namespace_pattern.findall(content)
                for ns in namespaces:
                    if not ns.startswith('ByteForgeFrontend'):
                        issues.append(f"❌ {file}: Non-standard namespace '{ns}'")
                        
        except Exception as e:
            issues.append(f"❌ {file}: Error reading file - {e}")
    
    if not issues:
        print("✅ All namespaces are consistent")
    else:
        for issue in issues[:5]:  # Show first 5 issues
            print(f"  {issue}")
            
    return len(issues)

def check_model_definitions():
    """Check that all required models are defined"""
    print("\n🏗️ Checking model definitions...")
    issues = []
    
    required_models = [
        'AnalyticsData',
        'SystemStatus', 
        'BRDGenerationRequest',
        'PRDGenerationRequest',
        'DocumentGenerationAnalytics',
        'AgentPerformanceAnalytics'
    ]
    
    found_models = set()
    cs_files = glob.glob("**/*.cs", recursive=True)
    
    for file in cs_files:
        if '/obj/' in file or '/bin/' in file:
            continue
            
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                for model in required_models:
                    if f'class {model}' in content:
                        found_models.add(model)
        except:
            continue
    
    missing_models = set(required_models) - found_models
    if missing_models:
        for model in missing_models:
            issues.append(f"❌ Missing model class: {model}")
    else:
        print("✅ All required models are defined")
        
    return len(issues)

def check_service_interfaces():
    """Check that all service interfaces are properly defined"""
    print("\n🔧 Checking service interfaces...")
    issues = []
    
    # Check if key service methods exist
    interface_methods = {
        'IMonitoringService': ['GetSystemStatus', 'GetAnalyticsAsync'],
        'ILLMService': ['GenerateAsync'],
        'IProjectService': ['GetProjectDocumentsAsync'],
        'IAgentRegistry': ['GetAllAgents', 'GetAgentStatus']
    }
    
    for interface_name, methods in interface_methods.items():
        interface_files = glob.glob(f"**/*{interface_name}.cs", recursive=True)
        if not interface_files:
            issues.append(f"❌ Interface {interface_name} not found")
            continue
            
        try:
            interface_file = interface_files[0]
            with open(interface_file, 'r', encoding='utf-8') as f:
                content = f.read()
                for method in methods:
                    if method not in content:
                        issues.append(f"❌ {interface_name}: Missing method {method}")
        except Exception as e:
            issues.append(f"❌ Error reading {interface_name}: {e}")
    
    if not issues:
        print("✅ All service interfaces are properly defined")
    else:
        for issue in issues:
            print(f"  {issue}")
            
    return len(issues)

def check_database_context():
    """Check ApplicationDbContext is clean"""
    print("\n🗄️ Checking database context...")
    issues = []
    
    dbcontext_files = glob.glob("**/ApplicationDbContext.cs", recursive=True)
    if not dbcontext_files:
        issues.append("❌ ApplicationDbContext.cs not found")
        return 1
        
    try:
        with open(dbcontext_files[0], 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for old lead processing entities
            old_entities = ['DbSet<Lead>', 'DbSet<ExternalServicesConfiguration>', 
                          'DbSet<NppesFilterConfiguration>', 'DbSet<JobScheduleSettings>']
            
            for entity in old_entities:
                if entity in content:
                    issues.append(f"❌ ApplicationDbContext still contains: {entity}")
                    
            # Check for ByteForge entities
            required_entities = ['DbSet<Project>', 'DbSet<ProjectDocument>', 'DbSet<ApiKey>']
            for entity in required_entities:
                if entity not in content:
                    issues.append(f"❌ ApplicationDbContext missing: {entity}")
                    
    except Exception as e:
        issues.append(f"❌ Error reading ApplicationDbContext: {e}")
    
    if not issues:
        print("✅ ApplicationDbContext is properly configured")
    else:
        for issue in issues:
            print(f"  {issue}")
            
    return len(issues)

def check_service_registrations():
    """Check service registration extensions"""
    print("\n📦 Checking service registrations...")
    issues = []
    
    extension_files = glob.glob("**/InfrastructureServiceExtensions.cs", recursive=True)
    if not extension_files:
        issues.append("❌ InfrastructureServiceExtensions.cs not found")
        return 1
        
    try:
        with open(extension_files[0], 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for key service registrations
            required_services = [
                'ILLMService',
                'IMonitoringService', 
                'IProjectService',
                'IDocumentGenerationService'
            ]
            
            for service in required_services:
                if service not in content:
                    issues.append(f"❌ Missing service registration: {service}")
                    
    except Exception as e:
        issues.append(f"❌ Error reading service extensions: {e}")
    
    if not issues:
        print("✅ Service registrations are complete")
    else:
        for issue in issues:
            print(f"  {issue}")
            
    return len(issues)

def check_project_file():
    """Check project file configuration"""
    print("\n📄 Checking project file...")
    issues = []
    
    project_files = glob.glob("*.csproj")
    if not project_files:
        issues.append("❌ No .csproj file found")
        return 1
        
    try:
        with open(project_files[0], 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for consistent EF versions
            if '8.0.12' not in content:
                issues.append("❌ Entity Framework version not consistent (should be 8.0.12)")
                
            # Check for required packages
            required_packages = [
                'Microsoft.EntityFrameworkCore',
                'StackExchange.Redis',
                'Microsoft.AspNetCore.Identity'
            ]
            
            for package in required_packages:
                if package not in content:
                    issues.append(f"❌ Missing package: {package}")
                    
    except Exception as e:
        issues.append(f"❌ Error reading project file: {e}")
    
    if not issues:
        print("✅ Project file is properly configured")
    else:
        for issue in issues:
            print(f"  {issue}")
            
    return len(issues)

def main():
    print("ByteForge Frontend - Build Validation")
    print("=" * 50)
    
    total_issues = 0
    
    # Run all checks
    total_issues += check_namespace_consistency()
    total_issues += check_model_definitions() 
    total_issues += check_service_interfaces()
    total_issues += check_database_context()
    total_issues += check_service_registrations()
    total_issues += check_project_file()
    
    print("\n" + "=" * 50)
    print("📊 VALIDATION SUMMARY")
    print("=" * 50)
    
    if total_issues == 0:
        print("🎉 SUCCESS: All validation checks passed!")
        print("✅ The project should now compile without major errors")
        print("\n🚀 Next steps:")
        print("  1. Run 'dotnet build' to verify compilation")
        print("  2. Run 'dotnet ef database update' for database setup")
        print("  3. Run 'dotnet run' to start the application")
    else:
        print(f"⚠️  ISSUES FOUND: {total_issues} issues need to be resolved")
        print("❌ The project may still have compilation errors")
        print("\n🔧 Please review and fix the issues listed above")
    
    return total_issues

if __name__ == "__main__":
    exit_code = main()
    exit(min(exit_code, 1))  # Return 0 for success, 1 for any issues