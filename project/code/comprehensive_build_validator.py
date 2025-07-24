#!/usr/bin/env python3
"""
Comprehensive Build Validator - Simulates compilation checks for ByteForgeFrontend
"""

import os
import re
import glob
import json
from typing import Dict, List, Set, Tuple
from collections import defaultdict

class BuildValidator:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.class_definitions = {}
        self.namespace_imports = defaultdict(set)
        
    def find_all_types(self):
        """Find all class, interface, enum, and struct definitions"""
        print("🔍 Scanning for type definitions...")
        
        cs_files = glob.glob('**/*.cs', recursive=True)
        cs_files = [f for f in cs_files if '/obj/' not in f and '/bin/' not in f]
        
        for file_path in cs_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract namespace
                namespace_match = re.search(r'namespace\s+([^\s{;]+)', content)
                current_namespace = namespace_match.group(1) if namespace_match else ""
                
                # Find type definitions
                patterns = {
                    'class': r'(?:public|internal|private)?\s*(?:abstract|sealed|static)?\s*class\s+([A-Za-z0-9_<>]+)',
                    'interface': r'(?:public|internal|private)?\s*interface\s+([A-Za-z0-9_<>]+)',
                    'enum': r'(?:public|internal|private)?\s*enum\s+([A-Za-z0-9_]+)',
                    'struct': r'(?:public|internal|private)?\s*struct\s+([A-Za-z0-9_<>]+)'
                }
                
                for type_name, pattern in patterns.items():
                    matches = re.findall(pattern, content, re.MULTILINE)
                    for match in matches:
                        # Keep both generic and non-generic versions
                        clean_name = re.sub(r'<[^>]+>', '', match)
                        full_name = f"{current_namespace}.{match}" if current_namespace else match
                        
                        # Store the clean name (without generics)
                        self.class_definitions[clean_name] = {
                            'full_name': full_name,
                            'file': file_path,
                            'type': type_name,
                            'namespace': current_namespace
                        }
                        
                        # Also store the full generic name if it has generics
                        if '<' in match:
                            self.class_definitions[match] = {
                                'full_name': full_name,
                                'file': file_path,
                                'type': type_name,
                                'namespace': current_namespace
                            }
                
                # Extract using statements
                using_matches = re.findall(r'using\s+([^;]+);', content)
                for using in using_matches:
                    self.namespace_imports[file_path].add(using.strip())
                    
            except Exception as e:
                self.errors.append(f"Error reading {file_path}: {e}")
        
        print(f"   Found {len(self.class_definitions)} type definitions")
    
    def check_service_registrations(self):
        """Check if all service registrations have corresponding implementations"""
        print("🔧 Validating service registrations...")
        
        registration_files = [
            'Extensions/AIAgentServiceExtensions.cs',
            'Extensions/InfrastructureServiceExtensions.cs',
            'Extensions/SecurityServiceExtensions.cs',
            'Extensions/ServiceCollectionExtensions.cs'
        ]
        
        for file_path in registration_files:
            if not os.path.exists(file_path):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Find service registrations
                patterns = [
                    r'AddScoped<([^,>]+),\s*([^>]+)>',
                    r'AddSingleton<([^,>]+),\s*([^>]+)>',
                    r'AddTransient<([^,>]+),\s*([^>]+)>'
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    for interface, implementation in matches:
                        # Check if both interface and implementation exist
                        interface_name = interface.split('<')[0].strip()
                        impl_name = implementation.split('<')[0].strip()
                        
                        # Skip System.IO.Abstractions types - they're from NuGet package
                        if interface_name.startswith('System.IO.Abstractions.') or impl_name.startswith('System.IO.Abstractions.'):
                            continue
                        
                        # For generic interfaces, check if a generic version exists
                        if interface_name.startswith('I') and interface_name not in self.class_definitions:
                            # Check if there's a generic version of this interface
                            generic_found = False
                            for class_name in self.class_definitions:
                                if class_name.startswith(interface_name) and '<' in self.class_definitions[class_name]['full_name']:
                                    generic_found = True
                                    break
                            
                            if not generic_found:
                                self.errors.append(f"Missing interface definition: {interface_name} in {file_path}")
                        
                        if impl_name not in self.class_definitions:
                            self.errors.append(f"Missing implementation class: {impl_name} for {interface_name} in {file_path}")
                            
            except Exception as e:
                self.errors.append(f"Error reading {file_path}: {e}")
    
    def check_controller_dependencies(self):
        """Check controller dependencies and action methods"""
        print("🎮 Validating controllers...")
        
        controller_files = glob.glob('Controllers/**/*.cs', recursive=True)
        
        for file_path in controller_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for proper controller inheritance
                if 'Controller' in content and ': Controller' not in content and ': ControllerBase' not in content:
                    self.warnings.append(f"Controller class may not inherit from Controller base: {file_path}")
                
                # Check for proper action method signatures
                action_pattern = r'public\s+(?:async\s+)?(?:Task<)?([A-Za-z0-9_<>]+)(?:>)?\s+([A-Za-z0-9_]+)\s*\([^)]*\)'
                actions = re.findall(action_pattern, content)
                
                for return_type, method_name in actions:
                    if return_type not in ['IActionResult', 'ActionResult', 'Task', 'void'] and not return_type.startswith('Task<'):
                        # Check if return type exists
                        clean_return_type = re.sub(r'<[^>]+>', '', return_type)
                        if clean_return_type not in self.class_definitions and clean_return_type not in ['string', 'int', 'bool']:
                            self.warnings.append(f"Unknown return type {return_type} in {method_name} at {file_path}")
                            
            except Exception as e:
                self.errors.append(f"Error reading {file_path}: {e}")
    
    def check_model_consistency(self):
        """Check model classes for data annotations and consistency"""
        print("📊 Validating models...")
        
        model_files = glob.glob('Models/**/*.cs', recursive=True)
        
        for file_path in model_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for proper using statements for data annotations
                if '[Required]' in content or '[StringLength' in content:
                    if 'using System.ComponentModel.DataAnnotations' not in content:
                        self.warnings.append(f"Missing DataAnnotations using statement: {file_path}")
                
                # Check for proper property definitions
                property_pattern = r'public\s+([A-Za-z0-9_<>]+(?:\?)?)\s+([A-Za-z0-9_]+)\s*{\s*get;\s*set;\s*}'
                properties = re.findall(property_pattern, content)
                
                for prop_type, prop_name in properties:
                    clean_type = re.sub(r'[<>?].*', '', prop_type)
                    if clean_type not in self.class_definitions and clean_type not in ['string', 'int', 'bool', 'DateTime', 'Guid', 'decimal', 'double', 'float']:
                        self.warnings.append(f"Unknown property type {prop_type} for {prop_name} in {file_path}")
                        
            except Exception as e:
                self.errors.append(f"Error reading {file_path}: {e}")
    
    def check_async_patterns(self):
        """Check for proper async/await patterns"""
        print("⚡ Validating async patterns...")
        
        cs_files = glob.glob('**/*.cs', recursive=True)
        cs_files = [f for f in cs_files if '/obj/' not in f and '/bin/' not in f]
        
        for file_path in cs_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for async methods without await
                async_methods = re.findall(r'public\s+async\s+Task[^{]*{([^}]*)}', content, re.DOTALL)
                for method_body in async_methods:
                    if 'await' not in method_body and 'Task.FromResult' not in method_body:
                        self.warnings.append(f"Async method without await in {file_path}")
                
                # Check for missing ConfigureAwait(false) in library code
                if '/Controllers/' not in file_path and '/Services/' in file_path:
                    awaits = re.findall(r'await\s+[^;]+', content)
                    for await_expr in awaits:
                        if 'ConfigureAwait' not in await_expr:
                            self.warnings.append(f"Missing ConfigureAwait(false) in {file_path}: {await_expr.strip()}")
                            
            except Exception as e:
                self.errors.append(f"Error reading {file_path}: {e}")
    
    def check_project_file(self):
        """Check project file for dependencies and settings"""
        print("📦 Validating project file...")
        
        project_files = glob.glob('*.csproj')
        
        for project_file in project_files:
            try:
                with open(project_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for target framework
                if '<TargetFramework>net8.0</TargetFramework>' not in content:
                    self.warnings.append(f"Project may not target .NET 8.0: {project_file}")
                
                # Check for nullable reference types
                if '<Nullable>enable</Nullable>' in content:
                    print("   ✅ Nullable reference types enabled")
                else:
                    self.warnings.append(f"Consider enabling nullable reference types: {project_file}")
                
                # Check for important packages
                required_packages = [
                    'Microsoft.AspNetCore.App',
                    'Microsoft.EntityFrameworkCore',
                    'Microsoft.Extensions.Logging'
                ]
                
                for package in required_packages:
                    if package not in content:
                        self.warnings.append(f"Missing package reference: {package} in {project_file}")
                        
            except Exception as e:
                self.errors.append(f"Error reading {project_file}: {e}")
    
    def check_configuration_files(self):
        """Check configuration files for consistency"""
        print("⚙️ Validating configuration files...")
        
        config_files = ['appsettings.json', 'appsettings.Development.json', 'appsettings.Production.json']
        
        for config_file in config_files:
            if os.path.exists(config_file):
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        config_data = json.load(f)
                    
                    # Check for connection strings
                    if 'ConnectionStrings' in config_data:
                        print(f"   ✅ Connection strings found in {config_file}")
                    
                    # Check for logging configuration
                    if 'Logging' in config_data:
                        print(f"   ✅ Logging configuration found in {config_file}")
                        
                except json.JSONDecodeError as e:
                    self.errors.append(f"Invalid JSON in {config_file}: {e}")
                except Exception as e:
                    self.errors.append(f"Error reading {config_file}: {e}")
    
    def run_comprehensive_validation(self):
        """Run all validation checks"""
        print("🏗️ COMPREHENSIVE BUILD VALIDATION")
        print("=" * 50)
        
        self.find_all_types()
        self.check_service_registrations()
        self.check_controller_dependencies()
        self.check_model_consistency()
        self.check_async_patterns()
        self.check_project_file()
        self.check_configuration_files()
        
        print("\n📊 VALIDATION RESULTS")
        print("=" * 50)
        
        if self.errors:
            print(f"🔴 ERRORS ({len(self.errors)}):")
            for i, error in enumerate(self.errors[:10], 1):
                print(f"   {i}. {error}")
            if len(self.errors) > 10:
                print(f"   ... and {len(self.errors) - 10} more errors")
        else:
            print("✅ NO CRITICAL ERRORS FOUND")
        
        if self.warnings:
            print(f"\n🟡 WARNINGS ({len(self.warnings)}):")
            for i, warning in enumerate(self.warnings[:10], 1):
                print(f"   {i}. {warning}")
            if len(self.warnings) > 10:
                print(f"   ... and {len(self.warnings) - 10} more warnings")
        else:
            print("✅ NO WARNINGS FOUND")
        
        print(f"\n📈 SUMMARY:")
        print(f"   Types found: {len(self.class_definitions)}")
        print(f"   Critical errors: {len(self.errors)}")
        print(f"   Warnings: {len(self.warnings)}")
        
        build_status = "✅ READY FOR COMPILATION" if len(self.errors) == 0 else "❌ BUILD WOULD FAIL"
        print(f"   Build status: {build_status}")
        
        return len(self.errors) == 0, len(self.errors), len(self.warnings)

if __name__ == "__main__":
    validator = BuildValidator()
    success, error_count, warning_count = validator.run_comprehensive_validation()
    
    if success:
        print("\n🎯 The application should compile successfully!")
    else:
        print(f"\n🔧 Fix {error_count} critical errors before compilation will succeed.")