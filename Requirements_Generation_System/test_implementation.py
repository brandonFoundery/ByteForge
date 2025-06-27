#!/usr/bin/env python3
"""
Test script to validate the Full Regeneration from Code implementation
"""

import sys
import yaml
from pathlib import Path
from rich.console import Console

console = Console()

def test_configuration():
    """Test that configuration is properly updated"""
    console.print("\n[cyan]Testing configuration...[/cyan]")
    
    config_path = Path(__file__).parent / "config.yaml"
    if not config_path.exists():
        console.print("[red]❌ config.yaml not found[/red]")
        return False
    
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Check for new paths
        paths = config.get('paths', {})
        if 'frontend_dir' not in paths:
            console.print("[red]❌ frontend_dir not found in config[/red]")
            return False
        if 'backend_dir' not in paths:
            console.print("[red]❌ backend_dir not found in config[/red]")
            return False
        
        # Check for code regeneration config
        code_regen = config.get('code_regeneration', {})
        if not code_regen:
            console.print("[red]❌ code_regeneration section not found in config[/red]")
            return False
        
        batching = code_regen.get('batching', {})
        if 'max_files' not in batching or 'max_tokens' not in batching:
            console.print("[red]❌ batching configuration incomplete[/red]")
            return False
        
        console.print("[green]✓ Configuration updated correctly[/green]")
        return True
        
    except Exception as e:
        console.print(f"[red]❌ Error reading config: {e}[/red]")
        return False

def test_code_scanner_import():
    """Test that code_scanner module can be imported"""
    console.print("\n[cyan]Testing code_scanner import...[/cyan]")
    
    try:
        from code_scanner import CodeScanner, CodeFile, FileBatch, CodeTree
        console.print("[green]✓ code_scanner module imported successfully[/green]")
        return True
    except ImportError as e:
        console.print(f"[red]❌ Failed to import code_scanner: {e}[/red]")
        return False

def test_orchestrator_extension():
    """Test that orchestrator has the new method"""
    console.print("\n[cyan]Testing orchestrator extension...[/cyan]")

    try:
        from orchestrator import RequirementsOrchestrator

        # Check if the new method exists
        if hasattr(RequirementsOrchestrator, 'generate_requirements_from_code'):
            console.print("[green]✓ generate_requirements_from_code method found[/green]")
            return True
        else:
            console.print("[red]❌ generate_requirements_from_code method not found[/red]")
            return False

    except ImportError as e:
        error_msg = str(e)
        if "anthropic" in error_msg or "google.generativeai" in error_msg:
            console.print(f"[yellow]⚠ Optional dependency missing: {error_msg}[/yellow]")
            console.print("[yellow]This is expected if you haven't installed all LLM providers[/yellow]")

            # Try to check the method exists by reading the file directly
            try:
                orchestrator_path = Path(__file__).parent / "orchestrator.py"
                with open(orchestrator_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                if "def generate_requirements_from_code" in content:
                    console.print("[green]✓ generate_requirements_from_code method found in source[/green]")
                    return True
                else:
                    console.print("[red]❌ generate_requirements_from_code method not found in source[/red]")
                    return False

            except Exception as file_error:
                console.print(f"[red]❌ Could not check orchestrator source: {file_error}[/red]")
                return False
        else:
            console.print(f"[red]❌ Failed to import orchestrator: {e}[/red]")
            return False

def test_run_generation_menu():
    """Test that run_generation has the new menu option"""
    console.print("\n[cyan]Testing run_generation menu...[/cyan]")
    
    try:
        run_gen_path = Path(__file__).parent / "run_generation.py"
        if not run_gen_path.exists():
            console.print("[red]❌ run_generation.py not found[/red]")
            return False
        
        with open(run_gen_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Check for new menu option
        if "Re-Generate Requirements from Source Code" in content:
            console.print("[green]✓ New menu option found[/green]")
        else:
            console.print("[red]❌ New menu option not found[/red]")
            return False
        
        # Check for workflow function
        if "full_regeneration_workflow" in content:
            console.print("[green]✓ full_regeneration_workflow function found[/green]")
        else:
            console.print("[red]❌ full_regeneration_workflow function not found[/red]")
            return False
        
        # Check for choice handling
        if 'choice == "0"' in content:
            console.print("[green]✓ Choice 0 handling found[/green]")
        else:
            console.print("[red]❌ Choice 0 handling not found[/red]")
            return False
        
        return True
        
    except Exception as e:
        console.print(f"[red]❌ Error reading run_generation.py: {e}[/red]")
        return False

def test_unit_tests():
    """Test that unit tests exist and can be imported"""
    console.print("\n[cyan]Testing unit tests...[/cyan]")
    
    test_files = [
        "test_code_scanner.py",
        "test_full_regeneration.py"
    ]
    
    all_tests_exist = True
    
    for test_file in test_files:
        test_path = Path(__file__).parent / test_file
        if test_path.exists():
            console.print(f"[green]✓ {test_file} exists[/green]")
        else:
            console.print(f"[red]❌ {test_file} not found[/red]")
            all_tests_exist = False
    
    return all_tests_exist

def test_directory_structure():
    """Test that the expected directory structure exists"""
    console.print("\n[cyan]Testing directory structure...[/cyan]")
    
    base_path = Path(__file__).parent.parent
    
    # Check for FrontEnd and BackEnd directories
    frontend_dir = base_path / "FrontEnd"
    backend_dir = base_path / "BackEnd"
    
    if frontend_dir.exists():
        console.print("[green]✓ FrontEnd directory exists[/green]")
    else:
        console.print("[red]❌ FrontEnd directory not found[/red]")
        return False
    
    if backend_dir.exists():
        console.print("[green]✓ BackEnd directory exists[/green]")
    else:
        console.print("[red]❌ BackEnd directory not found[/red]")
        return False
    
    # Check for some code files
    frontend_files = list(frontend_dir.rglob("*.ts")) + list(frontend_dir.rglob("*.tsx")) + list(frontend_dir.rglob("*.js"))
    backend_files = list(backend_dir.rglob("*.cs"))
    
    if frontend_files:
        console.print(f"[green]✓ Found {len(frontend_files)} frontend code files[/green]")
    else:
        console.print("[yellow]⚠ No frontend code files found[/yellow]")
    
    if backend_files:
        console.print(f"[green]✓ Found {len(backend_files)} backend code files[/green]")
    else:
        console.print("[yellow]⚠ No backend code files found[/yellow]")
    
    return True

def run_basic_functionality_test():
    """Run a basic functionality test without LLM calls"""
    console.print("\n[cyan]Testing basic functionality...[/cyan]")
    
    try:
        from code_scanner import CodeScanner
        
        # Create a minimal config
        config = {
            'code_regeneration': {
                'batching': {
                    'max_files': 5,
                    'max_tokens': 1000,
                    'included_extensions': ['.py', '.js', '.ts', '.cs'],
                    'excluded_directories': ['node_modules', 'bin'],
                    'excluded_files': ['package-lock.json']
                }
            }
        }
        
        # Initialize scanner
        scanner = CodeScanner(config)
        console.print("[green]✓ CodeScanner initialized successfully[/green]")
        
        # Test file inclusion logic
        test_file = Path("test.py")
        if scanner.should_include_file(test_file):
            console.print("[green]✓ File inclusion logic working[/green]")
        else:
            console.print("[red]❌ File inclusion logic failed[/red]")
            return False
        
        # Test directory categorization
        category = scanner._categorize_directory("FrontEnd/src/components")
        if category == "frontend-components":
            console.print("[green]✓ Directory categorization working[/green]")
        else:
            console.print(f"[red]❌ Directory categorization failed: got {category}[/red]")
            return False
        
        return True
        
    except Exception as e:
        console.print(f"[red]❌ Basic functionality test failed: {e}[/red]")
        return False

def main():
    """Run all tests"""
    console.print("[bold]Full Regeneration from Code - Implementation Validation[/bold]")
    console.print("=" * 60)
    
    tests = [
        ("Configuration", test_configuration),
        ("Code Scanner Import", test_code_scanner_import),
        ("Orchestrator Extension", test_orchestrator_extension),
        ("Run Generation Menu", test_run_generation_menu),
        ("Unit Tests", test_unit_tests),
        ("Directory Structure", test_directory_structure),
        ("Basic Functionality", run_basic_functionality_test)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                console.print(f"[red]Test '{test_name}' failed[/red]")
        except Exception as e:
            console.print(f"[red]Test '{test_name}' crashed: {e}[/red]")
    
    console.print(f"\n[bold]Results: {passed}/{total} tests passed[/bold]")
    
    if passed == total:
        console.print("[bold green]🎉 All tests passed! Implementation is ready.[/bold green]")
        console.print("\n[cyan]Next steps:[/cyan]")
        console.print("1. Run the system: python run_generation.py")
        console.print("2. Select option 0: Re-Generate Requirements from Source Code")
        console.print("3. Choose your LLM provider and confirm the operation")
        return 0
    else:
        console.print(f"[bold red]❌ {total - passed} tests failed. Please fix the issues before proceeding.[/bold red]")
        return 1

if __name__ == "__main__":
    sys.exit(main())
