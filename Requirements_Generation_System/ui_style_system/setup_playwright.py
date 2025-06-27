#!/usr/bin/env python3
"""
Setup script for Playwright installation
"""

import subprocess
import sys
import os
from pathlib import Path

def install_playwright():
    """Install Playwright and its dependencies"""
    
    print("🎭 Setting up Playwright for UI Style Screenshots...")
    
    try:
        # Install playwright package
        print("📦 Installing Playwright package...")
        subprocess.run([sys.executable, "-m", "pip", "install", "playwright"], check=True)
        
        # Install browser binaries
        print("🌐 Installing browser binaries...")
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
        
        print("✅ Playwright setup complete!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error setting up Playwright: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_playwright():
    """Test Playwright installation"""
    
    print("\n🧪 Testing Playwright installation...")
    
    test_script = '''
import asyncio
from playwright.async_api import async_playwright

async def test():
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto("data:text/html,<h1>Playwright Test</h1>")
            title = await page.title()
            await browser.close()
            print(f"Playwright test successful! Page title: {title}")
            return True
    except Exception as e:
        print(f"Playwright test failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test())
'''
    
    try:
        # Write test script to temporary file
        test_file = Path(__file__).parent / "test_playwright.py"
        with open(test_file, 'w') as f:
            f.write(test_script)
        
        # Run test
        result = subprocess.run([sys.executable, str(test_file)], 
                              capture_output=True, text=True)
        
        # Clean up test file
        test_file.unlink()
        
        if result.returncode == 0:
            print(result.stdout)
            return True
        else:
            print(f"Test failed: {result.stderr}")
            return False

    except Exception as e:
        print(f"Error running test: {e}")
        return False

def main():
    """Main setup function"""

    print("UI Style System - Playwright Setup")
    print("=" * 50)

    # Install Playwright
    if not install_playwright():
        print("\nSetup failed!")
        return False

    # Test installation
    if not test_playwright():
        print("\nInstallation completed but test failed!")
        print("You may need to run: python -m playwright install chromium")
        return False

    print("\nSetup completed successfully!")
    print("\nYou can now run the UI style generator:")
    print("python ui_style_generator.py")

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
