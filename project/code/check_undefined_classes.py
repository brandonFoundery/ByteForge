#!/usr/bin/env python3
"""
Script to check if 'potentially undefined' classes actually exist in the codebase
"""

import os
import re
import glob
from typing import Dict, List, Set

def find_all_class_definitions() -> Dict[str, str]:
    """Find all class definitions in the codebase"""
    class_definitions = {}
    
    cs_files = glob.glob('**/*.cs', recursive=True)
    cs_files = [f for f in cs_files if '/obj/' not in f and '/bin/' not in f]
    
    for file_path in cs_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find class definitions
            class_pattern = r'(?:public|internal|private)?\s*(?:abstract|sealed|static)?\s*class\s+([A-Za-z0-9_<>]+)'
            matches = re.findall(class_pattern, content, re.MULTILINE)
            
            for class_name in matches:
                # Remove generic type parameters for simpler matching
                clean_name = re.sub(r'<[^>]+>', '', class_name)
                class_definitions[clean_name] = file_path
            
            # Also find enums and interfaces
            enum_pattern = r'(?:public|internal|private)?\s*enum\s+([A-Za-z0-9_]+)'
            interface_pattern = r'(?:public|internal|private)?\s*interface\s+([A-Za-z0-9_<>]+)'
            
            enum_matches = re.findall(enum_pattern, content, re.MULTILINE)
            interface_matches = re.findall(interface_pattern, content, re.MULTILINE)
            
            for enum_name in enum_matches:
                class_definitions[enum_name] = file_path
                
            for interface_name in interface_matches:
                clean_name = re.sub(r'<[^>]+>', '', interface_name)
                class_definitions[clean_name] = file_path
        
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
    
    return class_definitions

def analyze_undefined_classes():
    """Analyze potentially undefined classes and check if they exist"""
    print("🔍 Finding all class definitions in the codebase...")
    class_definitions = find_all_class_definitions()
    
    print(f"Found {len(class_definitions)} class/interface/enum definitions")
    
    # List of potentially undefined classes from the diagnostics
    potentially_undefined = [
        'Uri', 'DefaultAzureCredential', 'InvalidOperationException',
        'ClaudeAgentConfig', 'ArgumentException', 'AgentProjectContext',
        'SettingsViewModel', 'ExternalServicesConfiguration', 'WorkflowSettings',
        'ApiResponse', 'HealthCheckResponse', 'DocumentGenerationRequest',
        'DocumentGenerationResponse', 'LLMGenerationRequest', 'LLMGenerationResponse',
        'Project', 'CreateProjectRequest', 'ProjectStatus', 'ProjectTemplate',
        'JobScheduleViewModel', 'JobScheduleUpdateModel', 'MonitoringResponse',
        'RequirementsGenerationRequest', 'RequirementsGenerationResponse',
        'TemplateGenerationRequest', 'TemplateGenerationResponse',
        'WorkflowHealthStatus', 'WorkflowExecution'
    ]
    
    print("\\n📊 ANALYSIS RESULTS")
    print("=" * 60)
    
    defined_classes = []
    truly_undefined = []
    system_classes = ['Uri', 'InvalidOperationException', 'ArgumentException', 'DefaultAzureCredential']
    
    for class_name in potentially_undefined:
        if class_name in system_classes:
            print(f"🔷 {class_name}: System class (should be available via using statements)")
            continue
            
        if class_name in class_definitions:
            defined_classes.append((class_name, class_definitions[class_name]))
            print(f"✅ {class_name}: Found in {class_definitions[class_name]}")
        else:
            truly_undefined.append(class_name)
            print(f"❌ {class_name}: Not found in codebase")
    
    print(f"\\n📈 SUMMARY:")
    print(f"   Total analyzed: {len(potentially_undefined)}")
    print(f"   Found in codebase: {len(defined_classes)}")
    print(f"   System classes: {len(system_classes)}")
    print(f"   Truly undefined: {len(truly_undefined)}")
    
    if truly_undefined:
        print(f"\\n❗ TRULY UNDEFINED CLASSES:")
        for class_name in truly_undefined:
            print(f"   - {class_name}")
            
            # Check if there are similar named classes
            similar = [name for name in class_definitions.keys() 
                      if name.lower().find(class_name.lower()) != -1 or 
                         class_name.lower().find(name.lower()) != -1]
            if similar:
                print(f"     Similar classes found: {', '.join(similar[:3])}")
    
    return defined_classes, truly_undefined

def check_specific_missing_classes():
    """Check for common missing model classes that should exist"""
    print("\\n🔍 Checking for missing model classes...")
    
    # Check if common model classes exist
    model_dirs = ['Models/', 'Models/Api/', 'Models/ProjectManagement/', 'Models/Monitoring/']
    
    for model_dir in model_dirs:
        if os.path.exists(model_dir):
            print(f"✅ Directory exists: {model_dir}")
            files = os.listdir(model_dir)
            cs_files = [f for f in files if f.endswith('.cs')]
            print(f"   Contains {len(cs_files)} C# files: {', '.join(cs_files[:5])}")
        else:
            print(f"❌ Directory missing: {model_dir}")

if __name__ == "__main__":
    analyze_undefined_classes()
    check_specific_missing_classes()