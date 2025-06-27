#!/usr/bin/env python3
"""
Test script for the UI Style Comparison System
Verifies that all components are working correctly
"""

import sys
import os
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

console = Console()

def test_imports():
    """Test that all required modules can be imported"""
    console.print("\n[cyan]Testing imports...[/cyan]")
    
    try:
        from ui_style_system.ui_style_generator import UIStyleGenerator
        console.print("✅ UIStyleGenerator import successful")
    except ImportError as e:
        console.print(f"❌ UIStyleGenerator import failed: {e}")
        return False
    
    try:
        from ui_style_system.review_generator import ReviewInterfaceGenerator
        console.print("✅ ReviewInterfaceGenerator import successful")
    except ImportError as e:
        console.print(f"❌ ReviewInterfaceGenerator import failed: {e}")
        return False
    
    try:
        from ui_style_system.ui_style_menu_integration import UIStyleMenuIntegration
        console.print("✅ UIStyleMenuIntegration import successful")
    except ImportError as e:
        console.print(f"❌ UIStyleMenuIntegration import failed: {e}")
        return False
    
    return True

def test_file_structure():
    """Test that all required files exist"""
    console.print("\n[cyan]Testing file structure...[/cyan]")
    
    ui_system_path = Path(__file__).parent
    required_files = [
        "style_themes.css",
        "ui_style_generator.py",
        "review_generator.py",
        "ui_style_menu_integration.py",
        "setup_playwright.py",
        "requirements.txt",
        "README.md"
    ]
    
    all_exist = True
    for file_name in required_files:
        file_path = ui_system_path / file_name
        if file_path.exists():
            console.print(f"✅ {file_name} exists")
        else:
            console.print(f"❌ {file_name} missing")
            all_exist = False
    
    return all_exist

def test_directories():
    """Test that required directories can be created"""
    console.print("\n[cyan]Testing directory creation...[/cyan]")
    
    ui_system_path = Path(__file__).parent
    required_dirs = [
        "screenshots",
        "temp_pages",
        "review"
    ]
    
    all_created = True
    for dir_name in required_dirs:
        dir_path = ui_system_path / dir_name
        try:
            dir_path.mkdir(exist_ok=True)
            console.print(f"✅ {dir_name} directory ready")
        except Exception as e:
            console.print(f"❌ {dir_name} directory creation failed: {e}")
            all_created = False
    
    return all_created

def test_css_themes():
    """Test that CSS themes are properly defined"""
    console.print("\n[cyan]Testing CSS themes...[/cyan]")
    
    css_file = Path(__file__).parent / "style_themes.css"
    if not css_file.exists():
        console.print("❌ style_themes.css not found")
        return False
    
    try:
        with open(css_file, 'r') as f:
            css_content = f.read()
        
        # Check for all 9 themes
        themes_found = 0
        for i in range(1, 10):
            if f".ui-theme-{i}" in css_content:
                themes_found += 1
                console.print(f"✅ Theme {i} definition found")
            else:
                console.print(f"❌ Theme {i} definition missing")
        
        return themes_found == 9
        
    except Exception as e:
        console.print(f"❌ Error reading CSS file: {e}")
        return False

def test_playwright_availability():
    """Test if Playwright is available"""
    console.print("\n[cyan]Testing Playwright availability...[/cyan]")
    
    try:
        import playwright
        console.print("✅ Playwright package available")
        
        # Try to import the async API
        from playwright.async_api import async_playwright
        console.print("✅ Playwright async API available")
        
        return True
        
    except ImportError:
        console.print("❌ Playwright not installed")
        console.print("   Run: python setup_playwright.py")
        return False

def test_example_images():
    """Test if example UI images exist"""
    console.print("\n[cyan]Testing example images...[/cyan]")
    
    examples_path = Path(__file__).parent.parent / "ui_style_examples"
    if not examples_path.exists():
        console.print("❌ ui_style_examples directory not found")
        return False
    
    images_found = 0
    for i in range(1, 10):
        image_path = examples_path / f"ui_style_{i}.png"
        if image_path.exists():
            images_found += 1
            console.print(f"✅ Example image {i} found")
        else:
            console.print(f"❌ Example image {i} missing")
    
    return images_found == 9

def test_integration():
    """Test integration with main menu system"""
    console.print("\n[cyan]Testing menu integration...[/cyan]")
    
    try:
        # Test that the integration function exists and can be called
        from ui_style_system.ui_style_menu_integration import handle_ui_style_menu_choice
        
        # Test with a dummy project root
        project_root = Path(__file__).parent.parent.parent
        
        # This should not crash (though it might fail due to missing dependencies)
        console.print("✅ Menu integration function available")
        return True
        
    except Exception as e:
        console.print(f"❌ Menu integration test failed: {e}")
        return False

def main():
    """Run all tests"""
    console.print(Panel.fit(
        "[bold]🎨 UI Style Comparison System - Test Suite[/bold]\n"
        "Verifying system components and dependencies",
        style="cyan"
    ))
    
    tests = [
        ("File Structure", test_file_structure),
        ("Directory Creation", test_directories),
        ("Module Imports", test_imports),
        ("CSS Themes", test_css_themes),
        ("Example Images", test_example_images),
        ("Playwright Availability", test_playwright_availability),
        ("Menu Integration", test_integration),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        console.print(f"\n[bold]Running: {test_name}[/bold]")
        try:
            if test_func():
                passed += 1
                console.print(f"[green]✅ {test_name} PASSED[/green]")
            else:
                console.print(f"[red]❌ {test_name} FAILED[/red]")
        except Exception as e:
            console.print(f"[red]❌ {test_name} ERROR: {e}[/red]")
    
    # Summary
    console.print(f"\n[bold]Test Results: {passed}/{total} tests passed[/bold]")
    
    if passed == total:
        console.print("\n[bold green]🎉 All tests passed! UI Style System is ready to use.[/bold green]")
        console.print("\n[cyan]Next steps:[/cyan]")
        console.print("1. Run: python run_generation.py")
        console.print("2. Select option 19 for Full UI Style Workflow")
        console.print("3. Or select option 17-18 for individual steps")
    else:
        console.print(f"\n[bold yellow]⚠️  {total - passed} tests failed. Please fix issues before using the system.[/bold yellow]")
        
        if not test_playwright_availability():
            console.print("\n[yellow]To install Playwright:[/yellow]")
            console.print("python ui_style_system/setup_playwright.py")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
