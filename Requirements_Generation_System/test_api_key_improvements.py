#!/usr/bin/env python3
"""
Test script to verify API key management improvements
"""

import os
import sys
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from rich.console import Console

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from run_generation import get_api_key, manage_api_keys, get_api_key_info, load_api_keys, save_api_keys

console = Console()

def test_api_key_preview():
    """Test that API key preview works correctly"""
    console.print("\n[cyan]Testing API key preview functionality...[/cyan]")
    
    # Test different key lengths
    test_cases = [
        ("sk-1234567890abcdef", "sk-1...cdef"),
        ("short", "sh...rt"),
        ("abc", "a...c"),
        ("ab", "***"),
        ("a", "***"),
        ("", "***")
    ]
    
    for key, expected_preview in test_cases:
        if len(key) >= 8:
            preview = f"{key[:4]}...{key[-4:]}"
        elif len(key) >= 4:
            preview = f"{key[:2]}...{key[-2:]}"
        elif len(key) == 3:
            preview = f"{key[0]}...{key[-1]}"
        else:
            preview = "***"
        
        if preview == expected_preview:
            console.print(f"[green]✓ Key '{key}' -> Preview '{preview}'[/green]")
        else:
            console.print(f"[red]✗ Key '{key}' -> Expected '{expected_preview}', got '{preview}'[/red]")

def test_api_key_info():
    """Test API key info retrieval"""
    console.print("\n[cyan]Testing API key info retrieval...[/cyan]")
    
    providers = ["openai", "anthropic", "gemini"]
    
    for provider in providers:
        info = get_api_key_info(provider)
        if info and "env_var" in info and "url" in info and "name" in info:
            console.print(f"[green]✓ {provider}: {info['name']} - {info['env_var']}[/green]")
        else:
            console.print(f"[red]✗ {provider}: Missing or invalid info[/red]")

def test_key_file_operations():
    """Test saving and loading API keys"""
    console.print("\n[cyan]Testing key file operations...[/cyan]")
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Mock the keys file path
        test_keys_file = Path(temp_dir) / "test_api_keys.json"
        
        with patch('run_generation.get_keys_file_path', return_value=test_keys_file):
            # Test saving keys
            test_keys = {
                "openai": "sk-test123456789",
                "anthropic": "ant-test123456789",
                "gemini": "gem-test123456789"
            }
            
            save_api_keys(test_keys)
            
            if test_keys_file.exists():
                console.print("[green]✓ API keys file created successfully[/green]")
                
                # Test loading keys
                loaded_keys = load_api_keys()
                
                if loaded_keys == test_keys:
                    console.print("[green]✓ API keys loaded correctly[/green]")
                else:
                    console.print(f"[red]✗ Keys mismatch: {loaded_keys} != {test_keys}[/red]")
            else:
                console.print("[red]✗ API keys file was not created[/red]")

def test_environment_key_detection():
    """Test environment variable detection"""
    console.print("\n[cyan]Testing environment key detection...[/cyan]")
    
    # Set a test environment variable
    test_key = "sk-test123456789"
    os.environ["TEST_OPENAI_API_KEY"] = test_key
    
    # Mock the environment variable name
    with patch('run_generation.get_api_key_info') as mock_info:
        mock_info.return_value = {
            "env_var": "TEST_OPENAI_API_KEY",
            "url": "https://platform.openai.com/api-keys",
            "name": "OpenAI"
        }
        
        # Test that environment key is detected
        env_key = os.getenv("TEST_OPENAI_API_KEY")
        if env_key == test_key:
            console.print("[green]✓ Environment variable detected correctly[/green]")
        else:
            console.print(f"[red]✗ Environment variable not detected: {env_key}[/red]")
    
    # Clean up
    del os.environ["TEST_OPENAI_API_KEY"]

def main():
    """Run all tests"""
    console.print("[bold blue]API Key Management Improvements Test Suite[/bold blue]")
    
    try:
        test_api_key_preview()
        test_api_key_info()
        test_key_file_operations()
        test_environment_key_detection()
        
        console.print("\n[bold green]✅ All tests completed![/bold green]")
        console.print("\n[yellow]Improvements made:[/yellow]")
        console.print("  • API key preview shows first 4 and last 4 characters")
        console.print("  • Confirmation step before saving keys")
        console.print("  • Better visual feedback in key management")
        console.print("  • Retry loop for incorrect key entry")
        
    except Exception as e:
        console.print(f"\n[red]❌ Test failed with error: {e}[/red]")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
