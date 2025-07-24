#!/usr/bin/env python3
"""
Run the Requirements Generation System for LSOMigrator
This script orchestrates the entire document generation process.

Supports multiple LLM providers:
- OpenAI o3-mini (with reasoning)
- Anthropic Claude 4 Opus
- Google Gemini 2.5 Pro (with thinking)
"""

import os
import sys
import yaml
import json
import subprocess
import getpass
import asyncio
from pathlib import Path
from datetime import datetime
from typing import List
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm

# Local imports
from orchestrator import RequirementsOrchestrator
from change_manager import ChangeManager, ChangeRequest, ChangeType

# UI Style System imports
try:
    from ui_style_system.ui_style_menu_integration import handle_ui_style_menu_choice
except ImportError:
    # Fallback if UI style system is not available
    def handle_ui_style_menu_choice(choice: str, project_root: Path) -> bool:
        console.print("[red]UI Style System not available. Please ensure ui_style_system module is properly installed.[/red]")
        return False

# Initialize console with Windows encoding fix
import platform
if platform.system() == "Windows":
    try:
        import os
        os.system("chcp 65001 > nul")
        console = Console(force_terminal=True, legacy_windows=False)
    except:
        console = Console(force_terminal=True, legacy_windows=True)
else:
    console = Console()


def load_config(config_path: Path) -> dict:
    """Load configuration from YAML file"""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def get_universal_base_path() -> Path:
    """Get the universal base path (ByteForge directory) for cross-platform compatibility"""
    script_dir = Path(__file__).parent.resolve()  # Requirements_Generation_System directory
    return script_dir.parent  # ByteForge directory


def check_environment(config: dict, model_provider: str = None, prompt_for_keys: bool = True) -> bool:
    """Check if environment is properly configured"""
    console.print("\n[cyan]Checking environment...[/cyan]")
    
    issues = []
    
    # Check API keys based on selected model provider or config
    provider = model_provider or config['llm']['provider']
    
    # Check for API key (environment variable or saved)
    key_info = get_api_key_info(provider)
    if key_info:
        # First check if key exists in environment or saved keys
        env_key = os.getenv(key_info["env_var"])
        saved_keys = load_api_keys()
        
        if not env_key and provider not in saved_keys:
            if prompt_for_keys:
                # Prompt for key
                console.print(f"[yellow]No API key found for {key_info['name']}[/yellow]")
                api_key = get_api_key(provider, force_prompt=True)
                
                if not api_key:
                    issues.append(f"No API key provided for {key_info['name']}")
            else:
                issues.append(f"No API key found for {key_info['name']}")
    
    # Check paths - Universal Path Structure (Cross-platform)
    script_dir = Path(__file__).parent.resolve()  # Requirements_Generation_System directory (absolute)
    byteforge_path = script_dir.parent  # ByteForge directory

    # Handle relative paths in config (remove ../ prefix for cross-platform compatibility)
    requirements_dir = config['paths']['requirements_dir']
    if requirements_dir.startswith('../'):
        requirements_dir = requirements_dir[3:]  # Remove '../'

    prompts_dir = config['paths']['prompts_dir']

    paths_to_check = [
        ('Requirements Directory', byteforge_path / requirements_dir),
        ('Prompts Directory', script_dir / prompts_dir)
    ]

    for name, path in paths_to_check:
        if not path.exists():
            issues.append(f"{name} not found: {path}")
    
    # Check Python packages
    required_packages = [
        ('openai', 'openai'),
        ('networkx', 'networkx'),
        ('rich', 'rich'),
        ('yaml', 'pyyaml')
    ]

    # Optional packages based on provider
    optional_packages = []
    if provider == "anthropic":
        optional_packages.append(('anthropic', 'anthropic'))
    elif provider == "gemini":
        optional_packages.append(('google.generativeai', 'google-generativeai'))

    # Check required packages
    for package_name, pip_name in required_packages:
        try:
            __import__(package_name)
        except ImportError:
            issues.append(f"Missing required Python package: {pip_name}")

    # Check optional packages for selected provider
    for package_name, pip_name in optional_packages:
        try:
            __import__(package_name)
        except ImportError:
            issues.append(f"Missing Python package for {provider}: {pip_name}")
    
    if issues:
        console.print("\n[red]Environment issues found:[/red]")
        for issue in issues:
            console.print(f"  [ERROR] {issue}")
        return False
    else:
        console.print("[green]Environment check passed![/green]")
        return True


def get_api_key_info(provider: str):
    """Get API key information for a provider"""
    if provider == "openai":
        return {
            "env_var": "OPENAI_API_KEY",
            "url": "https://platform.openai.com/api-keys",
            "name": "OpenAI"
        }
    elif provider == "anthropic":
        return {
            "env_var": "ANTHROPIC_API_KEY",
            "url": "https://console.anthropic.com/",
            "name": "Anthropic"
        }
    elif provider == "gemini":
        return {
            "env_var": "GOOGLE_API_KEY",
            "url": "https://makersuite.google.com/app/apikey",
            "name": "Google"
        }
    elif provider == "grok":
        return {
            "env_var": "GROK_API_KEY",
            "url": "https://x.ai/api",
            "name": "Grok (xAI)"
        }
    return None


def get_keys_file_path():
    """Get the path to the API keys file"""
    script_dir = Path(__file__).parent
    return script_dir / "api_keys.json"


def load_api_keys():
    """Load API keys from file"""
    keys_file = get_keys_file_path()
    if not keys_file.exists():
        return {}
    
    try:
        with open(keys_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        console.print(f"[yellow]Warning: Could not load API keys file: {str(e)}[/yellow]")
        return {}


def save_api_keys(keys: dict):
    """Save API keys to file"""
    keys_file = get_keys_file_path()
    
    try:
        with open(keys_file, 'w') as f:
            json.dump(keys, f, indent=2)
        
        # Set restrictive permissions on the file
        if sys.platform != "win32":
            os.chmod(keys_file, 0o600)  # Read/write for owner only
            
    except Exception as e:
        console.print(f"[yellow]Warning: Could not save API keys: {str(e)}[/yellow]")


def get_api_key(provider: str, force_prompt: bool = False):
    """Get API key for a provider, prompting if necessary"""
    key_info = get_api_key_info(provider)
    if not key_info:
        return None

    # Check environment variable first
    env_key = os.getenv(key_info["env_var"])
    if env_key and not force_prompt:
        return env_key

    # Check saved keys
    saved_keys = load_api_keys()
    if provider in saved_keys and not force_prompt:
        return saved_keys[provider]

    # Prompt for key
    console.print(f"\n[bold]Enter {key_info['name']} API Key[/bold]")
    console.print(f"You can get an API key from: {key_info['url']}")

    while True:
        key = getpass.getpass(f"{key_info['name']} API Key: ")

        if not key.strip():
            console.print("[yellow]No key entered. Try again or press Ctrl+C to cancel.[/yellow]")
            continue

        # Show a preview of the key for verification
        if len(key) >= 8:
            preview = f"{key[:4]}...{key[-4:]}"
        elif len(key) >= 4:
            preview = f"{key[:2]}...{key[-2:]}"
        elif len(key) == 3:
            preview = f"{key[0]}...{key[-1]}"
        else:
            preview = "***"

        console.print(f"[dim]Key preview: {preview}[/dim]")

        # Ask for confirmation
        if Confirm.ask("Is this key correct?"):
            # Ask if user wants to save the key
            save_key = Confirm.ask("Save this API key for future use?")
            if save_key:
                saved_keys[provider] = key
                save_api_keys(saved_keys)

            return key
        else:
            console.print("[yellow]Please re-enter the API key.[/yellow]")

    return None


def display_api_key_instructions(provider: str):
    """Display instructions for setting up API keys"""
    key_info = get_api_key_info(provider)
    if not key_info:
        return
    
    console.print("\n[bold yellow]API Key Setup Instructions:[/bold yellow]")
    console.print(f"  1. Get an API key from {key_info['url']}")
    console.print("  2. Set the environment variable:")
    console.print(f"     [dim]Windows:[/dim] set {key_info['env_var']}=your_key_here")
    console.print(f"     [dim]Linux/Mac:[/dim] export {key_info['env_var']}=your_key_here")
    
    console.print("\n[dim]For persistent setup, add the environment variable to your system settings.[/dim]")
    console.print("[dim]Alternatively, you can enter your API key when prompted by this script.[/dim]")


def create_directories(config: dict):
    """Create necessary directories"""
    directories = [
        config['paths']['output_dir'],
        config['paths']['status_dir']
    ]
    
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        console.print(f"[dim]Created directory: {dir_path}[/dim]")


def run_orchestrator(config_path: Path, model_provider: str = "openai"):
    """Run the main orchestrator"""
    console.print(f"\n[bold cyan]Starting Requirements Generation Orchestrator using {model_provider.upper()}[/bold cyan]")
    
    # Get API key for the selected provider
    key_info = get_api_key_info(model_provider)
    api_key = get_api_key(model_provider)
    
    if not api_key:
        console.print(f"[bold red]Error: No API key available for {key_info['name']}[/bold red]")
        return
    
    # Get the script directory
    script_dir = Path(__file__).parent
    orchestrator_path = script_dir / "orchestrator.py"
    
    # Run orchestrator with config and model provider
    cmd = [sys.executable, str(orchestrator_path), "--config", str(config_path), "--model", model_provider]
    
    try:
        # Create environment with API key
        env = os.environ.copy()
        if key_info and api_key:
            env[key_info["env_var"]] = api_key
            console.print(f"[dim]Using {key_info['name']} API key[/dim]")
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1,
            env=env
        )
        
        # Stream output
        for line in process.stdout:
            print(line, end='')
        
        process.wait()
        
        if process.returncode == 0:
            console.print("\n[bold green][COMPLETE] Generation completed successfully![/bold green]")
        else:
            console.print(f"\n[bold red][ERROR] Generation failed with code {process.returncode}[/bold red]")
            
    except KeyboardInterrupt:
        console.print("\n[yellow]Generation interrupted by user[/yellow]")
        process.terminate()
    except Exception as e:
        console.print(f"\n[bold red]Error running orchestrator: {str(e)}[/bold red]")


def run_orchestrator_selective(config_path: Path, model_provider: str = "openai", selected_documents: List[str] = None):
    """Run the orchestrator with selected documents"""
    if not selected_documents:
        console.print("[red]No documents specified for selective generation[/red]")
        return
        
    console.print(f"\n[bold cyan]Starting Selective Requirements Generation using {model_provider.upper()}[/bold cyan]")
    console.print(f"[dim]Documents to generate: {', '.join(selected_documents)}[/dim]")
    
    # Get API key for the selected provider
    key_info = get_api_key_info(model_provider)
    api_key = get_api_key(model_provider)
    
    if not api_key:
        console.print(f"[bold red]Error: No API key available for {key_info['name']}[/bold red]")
        return
    
    # Get the script directory
    script_dir = Path(__file__).parent
    orchestrator_path = script_dir / "orchestrator.py"
    
    # Run orchestrator with config, model provider, and selected documents
    documents_param = ",".join(selected_documents)
    cmd = [sys.executable, str(orchestrator_path), "--config", str(config_path), "--model", model_provider, "--documents", documents_param]
    
    try:
        # Create environment with API key
        env = os.environ.copy()
        if key_info and api_key:
            env[key_info["env_var"]] = api_key
            console.print(f"[dim]Using {key_info['name']} API key[/dim]")
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            env=env
        )
        
        # Stream output in real-time
        for line in iter(process.stdout.readline, ''):
            if line:
                print(line.rstrip())
        
        process.wait()
        
        if process.returncode == 0:
            console.print(f"\n[bold green]Selective generation completed successfully![/bold green]")
        else:
            console.print(f"\n[bold red]Selective generation failed with return code {process.returncode}[/bold red]")
            
    except Exception as e:
        console.print(f"[bold red]Error running selective generation: {str(e)}[/bold red]")

def run_orchestrator_resume(config_path: Path, model_provider: str = "openai"):
    """Run the orchestrator in resume mode"""
    console.print(f"\n[bold cyan]Resuming Requirements Generation using {model_provider.upper()}[/bold cyan]")

    # Get API key for the selected provider
    key_info = get_api_key_info(model_provider)
    api_key = get_api_key(model_provider)

    if not api_key:
        console.print(f"[bold red]Error: No API key available for {key_info['name']}[/bold red]")
        return

    # Get the script directory
    script_dir = Path(__file__).parent
    orchestrator_path = script_dir / "orchestrator.py"

    # Run orchestrator with config, model provider, and resume flag
    cmd = [sys.executable, str(orchestrator_path), "--config", str(config_path), "--model", model_provider, "--resume"]

    try:
        # Create environment with API key
        env = os.environ.copy()
        if key_info and api_key:
            env[key_info["env_var"]] = api_key
            console.print(f"[dim]Using {key_info['name']} API key[/dim]")

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1,
            env=env
        )

        # Stream output
        for line in process.stdout:
            print(line, end='')

        process.wait()

        if process.returncode == 0:
            console.print("\n[bold green][COMPLETE] Resume completed successfully![/bold green]")
        else:
            console.print(f"\n[bold red][ERROR] Resume failed with code {process.returncode}[/bold red]")

    except KeyboardInterrupt:
        console.print("\n[yellow]Resume interrupted by user[/yellow]")
        process.terminate()
    except Exception as e:
        console.print(f"\n[bold red]Error running orchestrator in resume mode: {str(e)}[/bold red]")


def run_monitor(output_dir: str):
    """Run the monitor in a separate process"""
    console.print("\n[cyan]Starting monitor in separate window...[/cyan]")

    script_dir = Path(__file__).parent
    monitor_path = script_dir / "monitor.py"

    # Start monitor in new window
    if sys.platform == "win32":
        subprocess.Popen([
            "start", "cmd", "/k",
            sys.executable, str(monitor_path), output_dir
        ], shell=True)
    else:
        subprocess.Popen([
            "gnome-terminal", "--",
            sys.executable, str(monitor_path), output_dir
        ])


def launch_dashboard():
    """Launch the dashboard backend and open the HTML page in browser"""
    console.print("\n[cyan]Starting dashboard...[/cyan]")

    script_dir = Path(__file__).parent
    dashboard_backend_dir = script_dir.parent / "dashboard" / "backend"
    dashboard_html_path = script_dir.parent / "dashboard" / "simple_dashboard.html"

    # Start the dashboard backend in a separate process
    try:
        if sys.platform == "win32":
            # Start backend in a new window (minimized)
            subprocess.Popen([
                "start", "/min", "cmd", "/c",
                sys.executable, "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"
            ], shell=True, cwd=str(dashboard_backend_dir))
        else:
            # Start backend in background for Unix systems
            subprocess.Popen([
                sys.executable, "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"
            ], cwd=str(dashboard_backend_dir))

        console.print("[dim]Dashboard backend starting on http://localhost:8000[/dim]")

        # Wait a moment for the backend to start
        import time
        time.sleep(2)

        # Open the HTML dashboard in the default browser
        dashboard_url = f"file:///{dashboard_html_path.as_posix()}"

        if sys.platform == "win32":
            subprocess.Popen(["start", dashboard_url], shell=True)
        elif sys.platform == "darwin":  # macOS
            subprocess.Popen(["open", dashboard_url])
        else:  # Linux
            subprocess.Popen(["xdg-open", dashboard_url])

        console.print(f"[green][OK] Dashboard opened in browser: {dashboard_url}[/green]")

    except Exception as e:
        console.print(f"[yellow]Warning: Could not start dashboard: {str(e)}[/yellow]")
        console.print("[dim]You can manually open the dashboard by running:[/dim]")
        console.print(f"[dim]cd {dashboard_backend_dir} && python -m uvicorn app:app --host 0.0.0.0 --port 8000[/dim]")
        console.print(f"[dim]Then open: {dashboard_html_path}[/dim]")


def manage_api_keys():
    """Manage all API keys"""
    console.print("\n[bold]API Key Management[/bold]")
    console.print("This will help you set up API keys for all supported LLM providers.")

    providers = ["openai", "anthropic", "gemini", "grok"]
    saved_keys = load_api_keys()

    for provider in providers:
        key_info = get_api_key_info(provider)

        # Check if key exists
        env_key = os.getenv(key_info["env_var"])
        has_saved_key = provider in saved_keys

        if env_key:
            # Show preview of environment key
            if len(env_key) >= 8:
                preview = f"{env_key[:4]}...{env_key[-4:]}"
            elif len(env_key) >= 4:
                preview = f"{env_key[:2]}...{env_key[-2:]}"
            elif len(env_key) == 3:
                preview = f"{env_key[0]}...{env_key[-1]}"
            else:
                preview = "***"
            status = f"[green]Set in environment ({preview})[/green]"
        elif has_saved_key:
            # Show preview of saved key
            saved_key = saved_keys[provider]
            if len(saved_key) >= 8:
                preview = f"{saved_key[:4]}...{saved_key[-4:]}"
            elif len(saved_key) >= 4:
                preview = f"{saved_key[:2]}...{saved_key[-2:]}"
            elif len(saved_key) == 3:
                preview = f"{saved_key[0]}...{saved_key[-1]}"
            else:
                preview = "***"
            status = f"[green]Saved in key file ({preview})[/green]"
        else:
            status = f"[yellow]Not set[/yellow]"

        console.print(f"\n{key_info['name']} API Key: {status}")

        # Ask if user wants to update this key
        update = Confirm.ask(f"Update {key_info['name']} API key?")
        if update:
            api_key = get_api_key(provider, force_prompt=True)
            if api_key:
                console.print(f"[green][OK] {key_info['name']} API key updated[/green]")
            else:
                console.print(f"[yellow]No key provided for {key_info['name']}[/yellow]")

    console.print("\n[green]API key management completed[/green]")


def get_multiline_input(prompt_message: str) -> str:
    """Gets multi-line input from the user."""
    console.print(f"[bold cyan]{prompt_message}[/bold cyan]")
    console.print("[dim](Type 'END' on a new line and press Enter when you are finished)[/dim]")

    lines = []
    while True:
        try:
            line = input()
            if line.strip().upper() == 'END':
                break
            lines.append(line)
        except EOFError:
            break
    return "\n".join(lines)


async def full_regeneration_workflow(config_path: Path, model_provider: str = "openai"):
    """Full regeneration workflow that wipes old outputs and regenerates from source code"""
    console.print(f"\n[bold green]♻️ Full Requirements Regeneration from Source Code[/bold green]")
    console.print(f"[yellow]Using {model_provider.upper()} for analysis[/yellow]")

    try:
        # Load configuration
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        # Get paths - Universal Path Structure
        script_dir = Path(__file__).parent.resolve()  # Requirements_Generation_System directory
        byteforge_path = script_dir.parent  # ByteForge directory
        byteforge_project_path = byteforge_path / "project"  # ByteForgeProjectPath

        base_path = byteforge_path  # For compatibility with existing code
        frontend_dir = Path(config['paths']['frontend_dir'])
        backend_dir = Path(config['paths']['backend_dir'])
        output_dir = byteforge_project_path / "requirements"
        status_dir = byteforge_project_path / "generation_status"

        # Resolve relative paths
        if not frontend_dir.is_absolute():
            frontend_dir = base_path / frontend_dir
        if not backend_dir.is_absolute():
            backend_dir = base_path / backend_dir
        if not output_dir.is_absolute():
            output_dir = base_path / output_dir
        if not status_dir.is_absolute():
            status_dir = base_path / status_dir

        console.print(f"\n[cyan]Step A: Purging old outputs...[/cyan]")

        # Step A: Purge old outputs
        purge_dirs = config.get('code_regeneration', {}).get('purge_directories', [
            'generated_documents',
            'generation_status',
            'Requirements/consolidated-requirements',
            'Requirements/invoice-requirements',
            'Requirements/logistics-requirements',
            'Requirements_Generation_System/build_passes'
        ])

        for purge_dir in purge_dirs:
            purge_path = base_path / purge_dir
            if purge_path.exists():
                try:
                    import shutil
                    shutil.rmtree(purge_path)
                    console.print(f"[dim]Removed: {purge_path}[/dim]")
                except Exception as e:
                    console.print(f"[yellow]Warning: Could not remove {purge_path}: {e}[/yellow]")

        # Recreate essential directories
        output_dir.mkdir(parents=True, exist_ok=True)
        status_dir.mkdir(parents=True, exist_ok=True)
        cumulative_docs_dir = output_dir / "code_generated_requirements"
        cumulative_docs_dir.mkdir(parents=True, exist_ok=True)

        console.print(f"[green][OK] Purged old outputs and recreated directories[/green]")

        console.print(f"\n[cyan]Step B: Discovering code files...[/cyan]")

        # Step B: Discover code files
        try:
            from code_scanner import CodeScanner
        except ImportError:
            console.print("[red]Error: code_scanner module not found. Please ensure code_scanner.py is in the same directory.[/red]")
            return False

        scanner = CodeScanner(config)
        code_tree = scanner.build_code_tree(frontend_dir, backend_dir)

        # Save code tree for transparency
        tree_path = output_dir / "code_tree.json"
        scanner.save_code_tree(code_tree, tree_path)

        console.print(f"[green][OK] Discovered {code_tree.total_files} code files[/green]")
        console.print(f"[dim]Code tree saved to: {tree_path}[/dim]")

        console.print(f"\n[cyan]Step C: Creating file batches...[/cyan]")

        # Step C: Create batches
        batches = scanner.create_batches(code_tree)
        console.print(f"[green][OK] Created {len(batches)} batches for processing[/green]")

        # Display batch summary
        for i, batch in enumerate(batches[:5], 1):  # Show first 5 batches
            console.print(f"[dim]  Batch {i}: {batch.total_files} files, {batch.total_tokens} tokens ({batch.category})[/dim]")
        if len(batches) > 5:
            console.print(f"[dim]  ... and {len(batches) - 5} more batches[/dim]")

        console.print(f"\n[cyan]Step D: Processing batches with LLM...[/cyan]")

        # Step D: LLM interaction
        # Get API key and set environment
        key_info = get_api_key_info(model_provider)
        api_key = get_api_key(model_provider)

        if not api_key:
            console.print(f"[bold red]Error: No API key available for {key_info['name']}[/bold red]")
            return False

        # Set environment variable
        os.environ[key_info["env_var"]] = api_key

        # Initialize orchestrator
        orchestrator = RequirementsOrchestrator(config['project']['name'], base_path, config_path, model_provider=model_provider)

        # Check for existing status files (resume support)
        processed_batches = set()
        if status_dir.exists():
            for status_file in status_dir.glob("status_batch_*.json"):
                try:
                    with open(status_file, 'r', encoding='utf-8') as f:
                        status_data = json.load(f)
                        if status_data.get('success', False):
                            processed_batches.add(status_data['batch_id'])
                except Exception as e:
                    console.print(f"[yellow]Warning: Could not read status file {status_file}: {e}[/yellow]")

        if processed_batches:
            console.print(f"[cyan]Found {len(processed_batches)} previously processed batches - resuming...[/cyan]")

        # Process batches
        successful_batches = len(processed_batches)  # Count previously successful batches
        failed_batches = 0
        skipped_batches = 0

        # Save overall progress status
        progress_file = status_dir / "regeneration_progress.json"

        for i, batch in enumerate(batches, 1):
            # Skip already processed batches
            if batch.batch_id in processed_batches:
                skipped_batches += 1
                console.print(f"[dim]Skipping batch {i}/{len(batches)}: {batch.batch_id} (already processed)[/dim]")
                continue

            console.print(f"\n[yellow]Processing batch {i}/{len(batches)}: {batch.batch_id}[/yellow]")
            console.print(f"[dim]Category: {batch.category}, Files: {batch.total_files}, Tokens: {batch.total_tokens}[/dim]")

            # Extract file paths from batch
            file_paths = [Path(f.path) for f in batch.files]

            try:
                success = await orchestrator.generate_requirements_from_code(
                    file_paths, cumulative_docs_dir, batch.batch_id
                )

                if success:
                    successful_batches += 1
                    console.print(f"[green][OK] Batch {i} completed successfully[/green]")
                else:
                    failed_batches += 1
                    console.print(f"[red][FAIL] Batch {i} failed[/red]")

                # Save batch status
                status_file = status_dir / f"status_batch_{batch.batch_id}.json"
                status_data = {
                    "batch_id": batch.batch_id,
                    "processed_at": datetime.now().isoformat(),
                    "success": success,
                    "files_processed": [str(p) for p in file_paths],
                    "category": batch.category,
                    "total_files": batch.total_files,
                    "total_tokens": batch.total_tokens,
                    "error": None
                }

                with open(status_file, 'w', encoding='utf-8') as f:
                    json.dump(status_data, f, indent=2)

                # Update overall progress
                progress_data = {
                    "total_batches": len(batches),
                    "processed_batches": successful_batches + failed_batches,
                    "successful_batches": successful_batches,
                    "failed_batches": failed_batches,
                    "skipped_batches": skipped_batches,
                    "last_updated": datetime.now().isoformat(),
                    "model_provider": model_provider,
                    "can_resume": True
                }

                with open(progress_file, 'w', encoding='utf-8') as f:
                    json.dump(progress_data, f, indent=2)

            except KeyboardInterrupt:
                console.print(f"\n[yellow]Processing interrupted by user at batch {i}[/yellow]")
                console.print(f"[cyan]Progress saved. You can resume by running this option again.[/cyan]")

                # Save interruption status
                status_file = status_dir / f"status_batch_{batch.batch_id}.json"
                status_data = {
                    "batch_id": batch.batch_id,
                    "processed_at": datetime.now().isoformat(),
                    "success": False,
                    "files_processed": [str(p) for p in file_paths],
                    "category": batch.category,
                    "total_files": batch.total_files,
                    "total_tokens": batch.total_tokens,
                    "error": "Interrupted by user"
                }

                with open(status_file, 'w', encoding='utf-8') as f:
                    json.dump(status_data, f, indent=2)

                return False

            except Exception as e:
                failed_batches += 1
                console.print(f"[red][FAIL] Batch {i} failed with error: {e}[/red]")

                # Save error status
                status_file = status_dir / f"status_batch_{batch.batch_id}.json"
                status_data = {
                    "batch_id": batch.batch_id,
                    "processed_at": datetime.now().isoformat(),
                    "success": False,
                    "files_processed": [str(p) for p in file_paths],
                    "category": batch.category,
                    "total_files": batch.total_files,
                    "total_tokens": batch.total_tokens,
                    "error": str(e)
                }

                with open(status_file, 'w', encoding='utf-8') as f:
                    json.dump(status_data, f, indent=2)

                continue

        console.print(f"\n[cyan]Step E: Processing complete![/cyan]")
        console.print(f"[green][OK] Successful batches: {successful_batches}[/green]")
        console.print(f"[red][FAIL] Failed batches: {failed_batches}[/red]")
        if skipped_batches > 0:
            console.print(f"[dim][SKIP] Skipped batches (already processed): {skipped_batches}[/dim]")

        if successful_batches > 0:
            console.print(f"\n[green][SUCCESS] Requirements regeneration completed![/green]")
            console.print(f"[green]Generated requirements saved to: {cumulative_docs_dir}[/green]")
            console.print(f"[green]Processing status saved to: {status_dir}[/green]")

            # Step F: Post-processing (optional validation)
            console.print(f"\n[cyan]Step F: Post-processing...[/cyan]")
            console.print(f"[dim]You can now run option 4 (Validate existing documents) to check the generated requirements[/dim]")

            return True
        else:
            console.print(f"\n[red][ERROR] No batches were processed successfully[/red]")
            return False

    except Exception as e:
        console.print(f"[red]Error in full regeneration workflow: {e}[/red]")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main entry point"""
    # Banner
    console.print(Panel.fit(
        "[bold]ByteForge App Generation System[/bold]\n"
        "Automated Document Generation with Traceability",
        style="cyan"
    ))
    
    # Load configuration
    script_dir = Path(__file__).parent
    config_path = script_dir / "config.yaml"
    
    if not config_path.exists():
        console.print(f"[red]Configuration file not found: {config_path}[/red]")
        return 1
    
    try:
        config = load_config(config_path)
    except Exception as e:
        console.print(f"[red]Error loading configuration: {str(e)}[/red]")
        return 1
    
    # Check environment
    if not check_environment(config):
        console.print("\n[yellow]Please fix the environment issues before running.[/yellow]")
        # Display instructions for the default provider
        display_api_key_instructions(config['llm']['provider'])
        return 1
    
    # Create directories
    create_directories(config)
    
    # Ask user for run mode
    console.print("\n[bold]Select run mode:[/bold]")
    console.print("  0. [bold green]Re-Generate Requirements from Source Code[/bold green]")
    console.print("  1. Full generation (all documents)")
    console.print("  2. Resume from last checkpoint")
    console.print("  3. Generate specific documents")
    console.print("  4. Validate existing documents")
    console.print("  5. Generate traceability report")
    console.print("  6. Manage API keys")
    console.print("  7. [bold yellow]Modify Existing Requirement[/bold yellow]")
    console.print("  8. [bold yellow]Introduce New Requirement(s)[/bold yellow]")
    console.print("  9. [bold orange]Resume Downstream Document Generation[/bold orange]")
    console.print("")
    console.print("  [bold yellow]Quick AI Build (Rapid Prototyping):[/bold yellow]")
    console.print("  10. [bold magenta]Build Application (AI-Driven 4-Pass System)[/bold magenta]")
    console.print("")
    console.print("  [bold yellow]Controlled Development (Production Apps):[/bold yellow]")
    console.print("  11. [bold green]Generate AI Agent Design Documents[/bold green]")
    console.print("  12. [bold cyan]Generate Development Plan[/bold cyan]")
    console.print("  13. [bold blue]Execute Claude Code Implementation[/bold blue]")
    console.print("")
    console.print("  [bold cyan]Quick Phase Launch:[/bold cyan]")
    console.print("  14. [bold cyan]Phase 1 - All Agents[/bold cyan]")
    console.print("  15. [bold cyan]Phase 2 - All Agents[/bold cyan]")
    console.print("  16. [bold cyan]Phase 3 - All Agents[/bold cyan]")
    console.print("  17. [bold cyan]Next Available Phase[/bold cyan]")
    console.print("")
    console.print("  [bold magenta]UI Style Comparison:[/bold magenta]")
    console.print("  18. [bold magenta]Generate UI Style Screenshots[/bold magenta]")
    console.print("  19. [bold cyan]View UI Style Comparison[/bold cyan]")
    console.print("  20. [bold yellow]Full UI Style Workflow[/bold yellow]")
    console.print("")
    console.print("  [bold red]Frontend Testing System:[/bold red]")
    console.print("  21. [bold red]Generate Frontend Test Plan[/bold red]")
    console.print("  22. [bold red]Execute testRigor Test Generation[/bold red]")
    console.print("  23. [bold red]Complete Testing Workflow[/bold red]")
    console.print("  24. [bold red]Fix E2E Test Issues with Claude Code[/bold red]")
    console.print("")
    console.print("  [bold green]Application Templates:[/bold green]")
    console.print("  25. [bold green]Browse Application Templates[/bold green]")
    console.print("  26. [bold green]Create New Project from Template[/bold green]")
    console.print("")
    console.print("  [bold red]Troubleshooting:[/bold red]")
    console.print("  27. [bold red]Reset Failed Claude Code Agents[/bold red]")

    choice = input("\nEnter choice (1-27): ").strip()

    # Model selection for generation modes (UI style options don't need LLM)
    model_provider = None
    if choice in ["0", "1", "2", "3", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "21", "22", "23", "24"]:
        console.print("\n[bold]Select LLM provider:[/bold]")
        console.print("  0. OpenAI o3 with reasoning")
        console.print("  1. OpenAI o3-mini with reasoning (Default)")
        console.print("  2. Anthropic Claude 4 Opus")
        console.print("  3. Google Gemini 2.5 Pro with thinking")
        console.print("  4. Grok (xAI) with reasoning")

        model_choice = input("\nEnter choice (0-4) or press Enter for default: ").strip()

        if model_choice == "0":
            model_provider = "openai"
            # Set specific model for o3
            os.environ["OPENAI_MODEL_OVERRIDE"] = "o3"
        elif model_choice == "2":
            model_provider = "anthropic"
        elif model_choice == "3":
            model_provider = "gemini"
        elif model_choice == "4":
            model_provider = "grok"
        else:
            model_provider = "openai"  # Default or explicit choice 1 (o3-mini)

        # Check environment for selected model
        if not check_environment(config, model_provider):
            console.print(f"\n[yellow]API key for {model_provider.upper()} is not set.[/yellow]")
            display_api_key_instructions(model_provider)
            return 1

    if choice == "0":
        # Full regeneration from source code
        console.print("\n[bold green]♻️ Full Requirements Regeneration from Source Code[/bold green]")
        console.print("This will:")
        console.print("  [cyan]1. Wipe all previously generated requirements[/cyan]")
        console.print("  [cyan]2. Scan the complete FrontEnd and BackEnd codebases[/cyan]")
        console.print("  [cyan]3. Feed code files to LLM in coherent batches[/cyan]")
        console.print("  [cyan]4. Iteratively rebuild BRD/PRD/FRD/NFRD documents[/cyan]")

        confirm = Prompt.ask("\n[bold red][WARNING] This will DELETE all existing generated requirements. Continue?[/bold red]", choices=["y", "n"], default="n")
        if confirm.lower() != "y":
            console.print("[yellow]Full regeneration cancelled.[/yellow]")
            return 0

        try:
            import asyncio
            success = asyncio.run(full_regeneration_workflow(config_path, model_provider))

            if success:
                console.print("\n[bold green][SUCCESS] Full regeneration completed successfully![/bold green]")
                console.print("[green]You can now run other options to validate or further process the generated requirements.[/green]")
            else:
                console.print("\n[bold red][ERROR] Full regeneration failed[/bold red]")
                return 1

        except Exception as e:
            console.print(f"\n[bold red]Error during full regeneration: {e}[/bold red]")
            import traceback
            traceback.print_exc()
            return 1

    elif choice == "1":
        # Full generation workflow: Requirements -> AI Agent Design -> Development Plan
        console.print("\n[bold cyan]Full Generation Workflow[/bold cyan]")
        console.print("This will run the complete end-to-end generation process:")
        console.print("  [cyan]1. Generate all requirements documents (BRD, PRD, FRD, etc.)[/cyan]")
        console.print("  [cyan]2. Generate AI Agent Design Documents[/cyan]")
        console.print("  [cyan]3. Generate Development Plan[/cyan]")

        confirm = Prompt.ask("\nProceed with full generation workflow?", choices=["y", "n"], default="y")
        if confirm.lower() != "y":
            console.print("[yellow]Full generation cancelled.[/yellow]")
            return 0

        # Start monitor if enabled
        if config['monitoring']['enabled']:
            run_monitor(config['paths']['output_dir'])

        # Launch dashboard in browser
        launch_dashboard()

        try:
            # Step 1: Generate all requirements documents
            console.print("\n[bold]Step 1/3: Generating Requirements Documents[/bold]")
            run_orchestrator(config_path, model_provider)
            console.print("[green][OK] Requirements documents generated successfully![/green]")

            # Step 2: Generate AI Agent Design Documents
            console.print("\n[bold]Step 2/3: Generating AI Agent Design Documents[/bold]")

            # Get API key and set environment
            key_info = get_api_key_info(model_provider)
            api_key = get_api_key(model_provider)

            if not api_key:
                console.print(f"[bold red]Error: No API key available for {key_info['name']}[/bold red]")
                return 1

            os.environ[key_info["env_var"]] = api_key

            from design_document_generator import DesignDocumentGenerator
            base_path = get_universal_base_path()  # Universal Path Structure
            design_generator = DesignDocumentGenerator(config['project']['name'], base_path, model_provider)

            import asyncio
            result = asyncio.run(design_generator.generate_all_agent_designs())

            if result.success:
                console.print(f"[green][OK] AI Agent Design Documents generated successfully![/green]")
                console.print(f"[green]Generated {len(result.generated_documents)} design documents in {result.total_execution_time:.2f} seconds[/green]")
            else:
                console.print(f"[red][ERROR] Design document generation failed: {result.error_summary}[/red]")
                return 1

            # Step 3: Generate Development Plan
            console.print("\n[bold]Step 3/3: Generating Development Plan[/bold]")

            from orchestrator import DocumentType
            orchestrator = RequirementsOrchestrator(config['project']['name'], base_path, config_path, model_provider=model_provider)

            result = asyncio.run(orchestrator.generate_document(DocumentType.DEV_PLAN, model_provider))
            validation_success = asyncio.run(orchestrator.validate_and_repair_document(DocumentType.DEV_PLAN))

            if validation_success:
                console.print("[green][OK] Development Plan generated and validated successfully![/green]")
            else:
                console.print("[yellow][WARNING] Development Plan generated but validation failed.[/yellow]")

            # Final success message
            console.print(f"\n[bold green]🎉 Full Generation Workflow Completed Successfully! 🎉[/bold green]")
            console.print("[green]All documents have been generated in the correct order:[/green]")
            console.print("[green]  ✅ Requirements Documents[/green]")
            console.print("[green]  ✅ AI Agent Design Documents[/green]")
            console.print("[green]  ✅ Development Plan[/green]")

        except Exception as e:
            console.print(f"[red]Error in full generation workflow: {e}[/red]")
            import traceback
            traceback.print_exc()
            return 1
        
    elif choice == "2":
        # Resume from last checkpoint
        console.print("\n[cyan]Checking for previous generation state...[/cyan]")

        # Check if there's anything to resume
        output_dir = Path(config['paths']['output_dir'])
        status_dir = Path(config['paths']['status_dir'])

        has_documents = any(output_dir.glob("*.md"))
        has_status_files = any(status_dir.glob("status_*.json"))

        if not has_documents and not has_status_files:
            console.print("[yellow]No previous generation found to resume from.[/yellow]")
            console.print("[cyan]Starting fresh generation instead...[/cyan]")

            # Start monitor if enabled
            if config['monitoring']['enabled']:
                run_monitor(config['paths']['output_dir'])

            # Run full generation
            run_orchestrator(config_path, model_provider)
        else:
            console.print("[green]Previous generation state detected![/green]")

            # Start monitor if enabled
            if config['monitoring']['enabled']:
                run_monitor(config['paths']['output_dir'])

            # Launch dashboard in browser
            launch_dashboard()

            # Run orchestrator in resume mode
            run_orchestrator_resume(config_path, model_provider)
        
    elif choice == "3":
        # Selective generation - generate specific documents
        console.print("\n[bold cyan]Selective Document Generation[/bold cyan]")
        console.print("Choose specific documents to generate:")
        
        # Show available document types
        console.print("\n[bold]Available document types:[/bold]")
        document_types = [
            ("BRD", "Business Requirements Document"),
            ("PRD", "Product Requirements Document"), 
            ("FRD", "Functional Requirements Document"),
            ("NFRD", "Non-Functional Requirements Document"),
            ("DRD", "Data Requirements Document"),
            ("DB_SCHEMA", "Database Schema Document"),
            ("API_SPEC", "API Specifications (OpenAPI)"),
            ("TRD", "Technical Requirements Document"),
            ("TEST_PLAN", "Test Plan Document"),
            ("RTM", "Requirements Traceability Matrix"),
            ("UIUX_SPEC", "UI/UX Specifications Document"),
            ("DEV_PLAN", "Development Plan Document")
        ]
        
        for i, (code, description) in enumerate(document_types, 1):
            console.print(f"  {i:2d}. {code:10} - {description}")
        
        console.print("\nEnter document types (comma-separated, e.g., 'BRD,PRD,API_SPEC' or numbers '1,2,7'):")
        selected_input = input("> ").strip()
        
        if not selected_input:
            console.print("[yellow]No documents selected. Cancelled.[/yellow]")
            return 0
        
        # Parse input - support both codes and numbers
        selected_docs = []
        for item in selected_input.split(','):
            item = item.strip().upper()
            
            # Check if it's a number (1-based index)
            if item.isdigit():
                index = int(item) - 1
                if 0 <= index < len(document_types):
                    selected_docs.append(document_types[index][0])
                else:
                    console.print(f"[yellow]Warning: Invalid number '{item}'. Valid range is 1-{len(document_types)}[/yellow]")
            else:
                # Check if it's a valid document code
                valid_codes = [code for code, _ in document_types]
                if item in valid_codes:
                    selected_docs.append(item)
                else:
                    console.print(f"[yellow]Warning: Invalid document type '{item}'. Valid types: {', '.join(valid_codes)}[/yellow]")
        
        if not selected_docs:
            console.print("[red]No valid documents selected. Cancelled.[/red]")
            return 0
        
        console.print(f"\n[green]Selected documents: {', '.join(selected_docs)}[/green]")
        
        confirm = Prompt.ask("Proceed with selective generation?", choices=["y", "n"], default="y")
        if confirm.lower() != "y":
            console.print("[yellow]Selective generation cancelled.[/yellow]")
            return 0
        
        # Start monitor if enabled
        if config['monitoring']['enabled']:
            run_monitor(config['paths']['output_dir'])

        # Launch dashboard in browser
        launch_dashboard()
        
        # Run orchestrator with selected documents
        run_orchestrator_selective(config_path, model_provider, selected_docs)
        
    elif choice == "4":
        # Run validation
        script_dir = Path(__file__).parent
        utils_path = script_dir / "utils.py"
        
        subprocess.run([
            sys.executable, str(utils_path),
            "analyze", config['paths']['output_dir']
        ])
        
    elif choice == "5":
        # Generate traceability report
        script_dir = Path(__file__).parent
        utils_path = script_dir / "utils.py"
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True
        ) as progress:
            task = progress.add_task("Generating traceability report...", total=None)
            
            # Export matrix
            subprocess.run([
                sys.executable, str(utils_path),
                "export", config['paths']['output_dir']
            ])
            
            # Generate graph
            subprocess.run([
                sys.executable, str(utils_path),
                "graph", config['paths']['output_dir']
            ])
            
        console.print("[green][OK] Traceability report generated![/green]")
        
    elif choice == "6":
        # Manage API keys
        manage_api_keys()

    elif choice == "7":
        # Modify an existing requirement
        console.print("\n[bold yellow]Modify Existing Requirement[/bold yellow]")
        target_id = Prompt.ask("Enter the Requirement ID to modify (e.g., REQ-LOAD-002)")
        reason = Prompt.ask("Enter the reason for this change")
        requestor = Prompt.ask("Enter your name/role (Requestor)", default=getpass.getuser())

        # Get API key and set environment before creating orchestrator
        key_info = get_api_key_info(model_provider)
        api_key = get_api_key(model_provider)
        
        if not api_key:
            console.print(f"[bold red]Error: No API key available for {key_info['name']}[/bold red]")
            return 1
        
        # Set environment variable
        os.environ[key_info["env_var"]] = api_key

        # Initialize orchestrator and change manager
        base_path = get_universal_base_path()  # Universal Path Structure
        orchestrator = RequirementsOrchestrator(config['project']['name'], base_path, config_path, model_provider=model_provider)
        change_manager = ChangeManager(base_path, orchestrator)

        # Create and process the change request
        change_request = ChangeRequest(
            change_id=change_manager._generate_change_id(),
            change_type=ChangeType.MODIFICATION,
            target_requirement_id=target_id,
            reason=reason,
            requestor=requestor
        )
        
        # This will be an async call in the future, for now, we call it directly
        # Note: The process_change_request is not yet async, but we're preparing for it
        try:
            import asyncio
            asyncio.run(change_manager.process_change_request(change_request))
        except Exception as e:
            console.print(f"[red]Error processing change request: {e}[/red]")

    elif choice == "8":
        # Introduce new requirement(s) from text
        console.print("\n[bold yellow]Introduce New Requirement(s)[/bold yellow]")

        raw_text = get_multiline_input("Paste the raw text containing new requirements:")
        if not raw_text.strip():
            console.print("[yellow]No input provided. Aborting.[/yellow]")
            return 1

        requestor = Prompt.ask("Enter your name/role (Requestor)", default=getpass.getuser())

        # Get API key and set environment before creating orchestrator
        key_info = get_api_key_info(model_provider)
        api_key = get_api_key(model_provider)

        if not api_key:
            console.print(f"[bold red]Error: No API key available for {key_info['name']}[/bold red]")
            return 1

        # Set environment variable
        os.environ[key_info["env_var"]] = api_key

        # Initialize orchestrator and change manager
        base_path = get_universal_base_path()  # Universal Path Structure
        orchestrator = RequirementsOrchestrator(config['project']['name'], base_path, config_path, model_provider=model_provider)
        change_manager = ChangeManager(base_path, orchestrator)

        # This will be an async call
        try:
            import asyncio
            asyncio.run(change_manager.process_new_requirements_from_text(raw_text, requestor, model_provider))
        except Exception as e:
            console.print(f"[red]Error processing new requirements: {e}[/red]")

    elif choice == "9":
        # Resume downstream document generation after new requirements were added
        console.print("\n[bold cyan]Resume Downstream Document Generation[/bold cyan]")
        console.print("This will check for and regenerate UI/UX specs, Test Plans, and RTM that may be outdated after new requirements were added.")

        # Get API key and set environment
        key_info = get_api_key_info(model_provider)
        api_key = get_api_key(model_provider)

        if not api_key:
            console.print(f"[bold red]Error: No API key available for {key_info['name']}[/bold red]")
            return 1

        # Set environment variable
        os.environ[key_info["env_var"]] = api_key

        # Run the downstream resume process
        try:
            from downstream_resume_manager import run_downstream_resume
            import asyncio

            base_path = get_universal_base_path()  # Universal Path Structure
            success = asyncio.run(run_downstream_resume(base_path, config_path, model_provider))

            if success:
                console.print("\n[green][OK] Downstream document resume completed successfully![/green]")
            else:
                console.print("\n[yellow][WARNING]  Downstream document resume completed with some issues.[/yellow]")

        except Exception as e:
            console.print(f"[red]Error running downstream resume: {e}[/red]")

    elif choice == "12":
        # Generate Development Plan
        console.print("\n[bold cyan]Generate Development Plan[/bold cyan]")
        console.print("This will analyze all existing requirements documents and create a comprehensive development plan.")
        console.print("The plan will include feature dependencies, parallel work streams, and feature branch strategies.")

        confirm = Prompt.ask("\nProceed with development plan generation?", choices=["y", "n"], default="y")
        if confirm.lower() != "y":
            console.print("[yellow]Development plan generation cancelled.[/yellow]")
            return 0

        # Get API key and set environment before creating orchestrator
        key_info = get_api_key_info(model_provider)
        api_key = get_api_key(model_provider)

        if not api_key:
            console.print(f"[bold red]Error: No API key available for {key_info['name']}[/bold red]")
            return 1

        # Set environment variable
        os.environ[key_info["env_var"]] = api_key

        # Initialize orchestrator
        base_path = get_universal_base_path()  # Universal Path Structure
        orchestrator = RequirementsOrchestrator(config['project']['name'], base_path, config_path, model_provider=model_provider)

        try:
            import asyncio
            from orchestrator import DocumentType

            console.print("\n[yellow]Generating Development Plan...[/yellow]")

            # Generate the development plan document
            result = asyncio.run(orchestrator.generate_document(DocumentType.DEV_PLAN, model_provider))

            # Validate the generated document
            validation_success = asyncio.run(orchestrator.validate_and_repair_document(DocumentType.DEV_PLAN))

            if validation_success:
                console.print("[green][OK] Development Plan generated and validated successfully![/green]")
                console.print("[green][OK] Development Plan saved to generated_documents/dev_plan.md[/green]")
            else:
                console.print("[yellow][WARNING] Development Plan generated but validation failed. Please review manually.[/yellow]")

        except Exception as e:
            console.print(f"[red]Error generating development plan: {e}[/red]")
            import traceback
            traceback.print_exc()

    elif choice == "11":
        # Generate AI Agent Design Documents
        console.print("\n[bold green]Generate AI Agent Design Documents[/bold green]")
        console.print("This will create detailed design documents for each AI agent based on your development plan:")
        console.print("  [cyan]• Frontend Agent:[/cyan] Next.js/React/Tailwind UI implementation")
        console.print("  [cyan]• Backend Agent:[/cyan] ASP.NET Core API, CQRS, business logic")
        console.print("  [cyan]• Infrastructure Agent:[/cyan] Azure resources, CI/CD, database schema")
        console.print("  [cyan]• Security Agent:[/cyan] Authentication, authorization, audit trails")
        console.print("  [cyan]• Integration Agent:[/cyan] Third-party integrations, payment gateway")

        # Check if dev_plan.md exists
        dev_plan_path = Path(config['paths']['output_dir']) / "dev_plan.md"
        if not dev_plan_path.exists():
            console.print(f"[red]Development plan not found: {dev_plan_path}[/red]")
            console.print("[red]Please generate the development plan first (option 12)[/red]")
            return 1

        console.print(f"\n[green][OK] Found development plan: {dev_plan_path}[/green]")

        confirm = Prompt.ask("\nProceed with AI agent design document generation?", choices=["y", "n"], default="y")
        if confirm.lower() != "y":
            console.print("[yellow]Design document generation cancelled.[/yellow]")
            return 0

        # Get API key and set environment
        key_info = get_api_key_info(model_provider)
        api_key = get_api_key(model_provider)

        if not api_key:
            console.print(f"[bold red]Error: No API key available for {key_info['name']}[/bold red]")
            return 1

        # Set environment variable
        os.environ[key_info["env_var"]] = api_key

        try:
            from design_document_generator import DesignDocumentGenerator

            base_path = get_universal_base_path()  # Universal Path Structure
            design_generator = DesignDocumentGenerator(config['project']['name'], base_path, model_provider)

            console.print(f"\n[yellow]Generating AI agent design documents...[/yellow]")

            # Generate all design documents
            import asyncio
            result = asyncio.run(design_generator.generate_all_agent_designs())

            if result.success:
                console.print(f"\n[bold green][SUCCESS] All AI agent design documents generated successfully![/bold green]")
                console.print(f"[green][OK] Documents saved to: design/[/green]")
                console.print(f"[green][OK] Total execution time: {result.total_execution_time:.2f} seconds[/green]")

                # List generated files
                design_dir = base_path / "design"
                if design_dir.exists():
                    design_files = list(design_dir.glob("*.md"))
                    console.print(f"\n[bold]Generated design documents:[/bold]")
                    for design_file in sorted(design_files):
                        console.print(f"  • {design_file.name}")
            else:
                console.print(f"\n[bold red][ERROR] Design document generation failed[/bold red]")
                if result.error_summary:
                    console.print(f"[red]Error summary: {result.error_summary}[/red]")

        except ImportError as e:
            console.print(f"[red]Error: Could not import DesignDocumentGenerator: {e}[/red]")
            console.print(f"[yellow]Make sure design_document_generator.py is properly implemented[/yellow]")
            return 1
        except Exception as e:
            console.print(f"[red]Error generating design documents: {e}[/red]")
            import traceback
            traceback.print_exc()
            return 1

    elif choice == "13":
        # Execute Claude Code Implementation
        console.print("\n[bold blue]Execute Claude Code Implementation[/bold blue]")
        console.print("Choose implementation method:")
        console.print("  1. 🚀 Real Claude Code (requires permissions)")
        console.print("  2. 🧪 Simulation Mode (demonstration)")

        impl_choice = input("\nEnter choice (1-2): ").strip()

        if impl_choice == "1":
            # Real Claude Code Implementation
            console.print("\n[bold yellow]🚀 Real Claude Code Implementation[/bold yellow]")
            console.print("This will launch Claude Code in WSL terminals to implement features based on design documents:")
            console.print("  [cyan]• Uses design documents as context[/cyan]")
            console.print("  [cyan]• Launches separate WSL terminals for each agent[/cyan]")
            console.print("  [cyan]• Implements real application code[/cyan]")
            console.print("  [cyan]• Creates pull requests automatically[/cyan]")

            # Check if design documents exist - Universal Path Structure (Cross-platform)
            script_dir = Path(__file__).parent.resolve()  # Requirements_Generation_System directory (absolute)
            byteforge_path = script_dir.parent  # ByteForge directory
            byteforge_project_path = byteforge_path / "project"  # ByteForgeProjectPath
            design_dir = byteforge_project_path / "design"
            if not design_dir.exists():
                console.print(f"[red]Design documents directory not found: {design_dir}[/red]")
                console.print("[red]Please generate design documents first (option 11)[/red]")
                return 1

            design_files = list(design_dir.glob("*-agent-design.md"))
            if not design_files:
                console.print(f"[red]No agent design documents found in {design_dir}[/red]")
                console.print("[red]Please generate design documents first (option 11)[/red]")
                return 1

            console.print(f"\n[green][OK] Found {len(design_files)} agent design documents:[/green]")
            for design_file in sorted(design_files):
                agent_name = design_file.stem.replace("-agent-design", "").replace("-", " ").title()
                console.print(f"  • {agent_name} Agent")

            # Agent selection
            console.print("\n[bold]Select agents to implement:[/bold]")
            console.print("  1. Frontend Agent only")
            console.print("  2. Backend Agent only")
            console.print("  3. Infrastructure Agent only")
            console.print("  4. Security Agent only")
            console.print("  5. Integration Agent only")
            console.print("  6. All agents (parallel execution)")
            console.print("  7. Custom selection")

            agent_choice = input("\nEnter choice (1-7): ").strip()

            # Phase selection
            console.print("\n[bold]Select implementation phase:[/bold]")
            console.print("  1. Phase 1 (Core foundation)")
            console.print("  2. Phase 2 (Core business features)")
            console.print("  3. Phase 3 (Advanced features)")
            console.print("  4. Phase 4 (Final optimization)")
            console.print("  5. All phases (sequential)")

            phase_choice = input("\nEnter choice (1-5): ").strip()

            confirm = Prompt.ask("\nProceed with Claude Code implementation?", choices=["y", "n"], default="n")
            if confirm.lower() != "y":
                console.print("[yellow]Claude Code implementation cancelled.[/yellow]")
                return 0

            try:
                from claude_code_executor import ClaudeCodeExecutor

                # Universal Path Structure - Use Requirements_Generation_System as base
                script_dir = Path(__file__).parent.resolve()  # Requirements_Generation_System directory
                claude_executor = ClaudeCodeExecutor(script_dir)

                console.print(f"\n[yellow]Launching Claude Code implementation...[/yellow]")

                # Execute Claude Code based on selections
                import asyncio
                result = asyncio.run(claude_executor.execute_implementation(agent_choice, phase_choice))

                if result.success:
                    console.print(f"\n[bold green][SUCCESS] Claude Code implementation completed successfully![/bold green]")
                    console.print(f"[green][OK] Total execution time: {result.total_execution_time:.2f} seconds[/green]")

                    # Display results for each agent
                    for agent_result in result.agent_results:
                        status_color = "green" if agent_result.success else "red"
                        console.print(f"  [{status_color}]{agent_result.agent_name}: {'Success' if agent_result.success else 'Failed'}[/{status_color}]")
                        if agent_result.branch_name:
                            console.print(f"    [dim]Branch: {agent_result.branch_name}[/dim]")
                        if agent_result.pr_url:
                            console.print(f"    [dim]PR: {agent_result.pr_url}[/dim]")
                else:
                    console.print(f"\n[bold red][ERROR] Claude Code implementation failed[/bold red]")
                    if result.error_summary:
                        console.print(f"[red]Error summary: {result.error_summary}[/red]")

            except ImportError as e:
                console.print(f"[red]Error: Could not import ClaudeCodeExecutor: {e}[/red]")
                console.print(f"[yellow]Make sure claude_code_executor.py is properly implemented[/yellow]")
                return 1
            except Exception as e:
                console.print(f"[red]Error executing Claude Code: {e}[/red]")
                import traceback
                traceback.print_exc()
                return 1

        elif impl_choice == "2":
            # Simulation Mode
            console.print("\n[bold blue]🧪 Claude Code Simulation Mode[/bold blue]")
            console.print("This demonstrates what would happen during real Claude Code implementation:")
            console.print("  [cyan]• Shows realistic implementation progress[/cyan]")
            console.print("  [cyan]• Simulates file creation and modification[/cyan]")
            console.print("  [cyan]• Demonstrates branch creation and testing[/cyan]")
            console.print("  [cyan]• Safe demonstration mode (no actual changes)[/cyan]")

            # Check if design documents exist - Universal Path Structure (Cross-platform)
            script_dir = Path(__file__).parent.resolve()  # Requirements_Generation_System directory (absolute)
            byteforge_path = script_dir.parent  # ByteForge directory
            byteforge_project_path = byteforge_path / "project"  # ByteForgeProjectPath
            design_dir = byteforge_project_path / "design"
            if not design_dir.exists():
                console.print(f"[red]Design documents directory not found: {design_dir}[/red]")
                console.print("[red]Please generate design documents first (option 11)[/red]")
                return 1

            design_files = list(design_dir.glob("*-agent-design.md"))
            if not design_files:
                console.print(f"[red]No agent design documents found in {design_dir}[/red]")
                console.print("[red]Please generate design documents first (option 11)[/red]")
                return 1

            console.print(f"\n[green][OK] Found {len(design_files)} agent design documents[/green]")

            # Agent selection for simulation
            console.print("\n[bold]Select agents to simulate:[/bold]")
            console.print("  1. Frontend Agent only")
            console.print("  2. Backend Agent only")
            console.print("  3. Infrastructure Agent only")
            console.print("  4. Security Agent only")
            console.print("  5. Integration Agent only")
            console.print("  6. All agents")
            console.print("  7. Custom selection (Frontend + Backend)")

            agent_choice = input("\nEnter choice (1-7): ").strip()

            # Map choices to agent IDs
            agent_map = {
                "1": ["frontend"],
                "2": ["backend"],
                "3": ["infrastructure"],
                "4": ["security"],
                "5": ["integration"],
                "6": ["frontend", "backend", "infrastructure", "security", "integration"],
                "7": ["frontend", "backend"]
            }

            selected_agents = agent_map.get(agent_choice, ["frontend"])

            # Phase selection
            console.print("\n[bold]Select implementation phase:[/bold]")
            console.print("  1. Phase 1 (Core foundation)")
            console.print("  2. Phase 2 (Core business features)")
            console.print("  3. Phase 3 (Advanced features)")
            console.print("  4. Phase 4 (Final optimization)")
            console.print("  5. All phases")

            phase_choice = input("\nEnter choice (1-5): ").strip()
            phase_name = {
                "1": "Phase 1",
                "2": "Phase 2",
                "3": "Phase 3",
                "4": "Phase 4",
                "5": "All Phases"
            }.get(phase_choice, "Phase 1")

            confirm = Prompt.ask(f"\nProceed with simulation of {len(selected_agents)} agent(s)?", choices=["y", "n"], default="y")
            if confirm.lower() != "y":
                console.print("[yellow]Simulation cancelled.[/yellow]")
                return 0

            try:
                from claude_code_simulator import ClaudeCodeSimulator

                base_path = get_universal_base_path()  # Universal Path Structure
                simulator = ClaudeCodeSimulator(base_path)

                console.print(f"\n[cyan]🧪 Starting Claude Code simulation...[/cyan]")

                # Execute simulation
                import asyncio
                results = asyncio.run(simulator.simulate_multiple_agents(selected_agents, phase_name))

                # Show results
                successful = [r for r in results if r.success]
                console.print(f"\n[bold green][SUCCESS] Simulation Complete![/bold green]")
                console.print(f"[green][OK] Successful: {len(successful)}/{len(results)} agents[/green]")

                total_files = sum(len(r.files_created or []) + len(r.files_modified or []) for r in successful)
                console.print(f"[green][FILE] Total files that would be affected: {total_files}[/green]")

                # Show detailed results for first successful agent
                if successful:
                    first_result = successful[0]
                    console.print(f"\n[blue][INFO] Sample Implementation Summary ({first_result.agent_name}):[/blue]")
                    if first_result.implementation_summary:
                        console.print(first_result.implementation_summary)

            except ImportError as e:
                console.print(f"[red]Error: Could not import ClaudeCodeSimulator: {e}[/red]")
                console.print(f"[yellow]Make sure claude_code_simulator.py is properly implemented[/yellow]")
                return 1
            except Exception as e:
                console.print(f"[red]Error running simulation: {e}[/red]")
                import traceback
                traceback.print_exc()
                return 1

        else:
            console.print("[red]Invalid choice. Please select 1 or 2.[/red]")
            return 1

    elif choice == "10":
        # AI-Driven Application Builder
        console.print("\n[bold magenta]🚀 AI-Driven Application Builder[/bold magenta]")
        console.print("This will use a 4-pass AI system to build your application based on existing requirements:")
        console.print("  [cyan]Pass 1:[/cyan] OpenAI o3 - System Design (uses BRD, PRD, FRD, NFRD)")
        console.print("  [cyan]Pass 2:[/cyan] Gemini 2.5 - Design Review (uses Pass 1 output + TRD, API specs)")
        console.print("  [cyan]Pass 3:[/cyan] Claude Sonnet 4 - Implementation (uses Pass 2 output + all technical docs)")
        console.print("  [cyan]Pass 4:[/cyan] Automated Build System - Code Generation & Compilation")

        console.print("\n[yellow][WARNING]  This will automatically build based on your existing requirements documents:[/yellow]")
        console.print("  • Create a new Git feature branch")
        console.print("  • Generate and modify code files")
        console.print("  • Run build and test commands")
        console.print("  • Create a Pull Request if successful")

        # Check if requirements documents exist
        requirements_dir = Path(config['paths']['requirements_dir'])
        if not requirements_dir.exists():
            console.print(f"[red]Requirements directory not found: {requirements_dir}[/red]")
            console.print("[red]Please generate requirements documents first (option 1)[/red]")
            return 1

        # List available requirements documents
        req_files = list(requirements_dir.glob("*.md"))
        if not req_files:
            console.print(f"[red]No requirements documents found in {requirements_dir}[/red]")
            console.print("[red]Please generate requirements documents first (option 1)[/red]")
            return 1

        console.print(f"\n[green]Found {len(req_files)} requirements documents:[/green]")
        for req_file in sorted(req_files):
            console.print(f"  • {req_file.name}")

        confirm = Prompt.ask("\nProceed with AI-driven application build using these requirements?", choices=["y", "n"], default="n")
        if confirm.lower() != "y":
            console.print("[yellow]Application build cancelled.[/yellow]")
            return 0

        # Get optional feature name for the branch
        feature_name = Prompt.ask("Enter a name for this implementation (for Git branch)", default="requirements_implementation")
        if not feature_name:
            feature_name = "requirements_implementation"

        # Get API keys for all models (since we use multiple models)
        console.print("\n[yellow]Setting up API keys for multi-model workflow...[/yellow]")

        # Check all required API keys
        required_models = ["openai", "gemini", "anthropic"]
        api_keys = {}

        for model in required_models:
            key_info = get_api_key_info(model)
            api_key = get_api_key(model)

            if not api_key:
                console.print(f"[bold red]Error: No API key available for {key_info['name']}[/bold red]")
                console.print(f"[yellow]Please set up API keys using option 6 (Manage API keys) first.[/yellow]")
                return 1

            # Set environment variable
            os.environ[key_info["env_var"]] = api_key
            api_keys[model] = api_key

        console.print("[green][OK] All API keys configured successfully[/green]")

        # Initialize ApplicationBuilder
        try:
            from application_builder import ApplicationBuilder

            base_path = get_universal_base_path()  # Universal Path Structure
            app_builder = ApplicationBuilder(config['project']['name'], base_path, config_path)

            console.print(f"\n[yellow]Starting 4-pass AI workflow...[/yellow]")
            console.print(f"[dim]Logs will be written to: {base_path}/logs/[/dim]")

            # Run the complete workflow using existing requirements documents
            import asyncio
            result = asyncio.run(app_builder.run_full_workflow_from_requirements(requirements_dir, feature_name))

            # Display results
            if result.success:
                console.print(f"\n[bold green][SUCCESS] Application build completed successfully![/bold green]")
                if result.feature_branch:
                    console.print(f"[green][OK] Feature branch: {result.feature_branch}[/green]")
                if result.pr_url:
                    console.print(f"[green][OK] Pull Request: {result.pr_url}[/green]")
                console.print(f"[green][OK] Total execution time: {result.total_execution_time:.2f} seconds[/green]")
            else:
                console.print(f"\n[bold red][ERROR] Application build failed[/bold red]")
                if result.error_summary:
                    console.print(f"[red]Error summary: {result.error_summary}[/red]")
                console.print(f"[yellow]Check logs in {base_path}/logs/ for detailed error information[/yellow]")

            # Display pass results
            console.print(f"\n[bold]Pass Results Summary:[/bold]")
            for pass_result in result.pass_results:
                status_color = "green" if pass_result.status.value == "completed" else "red"
                console.print(f"  [{status_color}]{pass_result.pass_type.value.title()}: {pass_result.status.value}[/{status_color}]")
                if pass_result.execution_time:
                    console.print(f"    [dim]Execution time: {pass_result.execution_time:.2f}s, Retries: {pass_result.retry_count}[/dim]")

        except ImportError as e:
            console.print(f"[red]Error: Could not import ApplicationBuilder: {e}[/red]")
            console.print(f"[yellow]Make sure application_builder.py is properly implemented[/yellow]")
            return 1
        except Exception as e:
            console.print(f"[red]Error running application builder: {e}[/red]")
            import traceback
            traceback.print_exc()
            return 1

    elif choice in ["14", "15", "16", "17"]:
        # Quick Phase Launch
        phase_map = {
            "14": "1",  # Phase 1
            "15": "2",  # Phase 2
            "16": "3",  # Phase 3
            "17": "auto"  # Next Available Phase
        }

        phase_names = {
            "14": "Phase 1 (Core foundation)",
            "15": "Phase 2 (Core business features)",
            "16": "Phase 3 (Advanced features)",
            "17": "Next Available Phase"
        }

        console.print(f"\n[bold cyan]⚡ Quick Launch: {phase_names[choice]}[/bold cyan]")
        console.print("This will automatically launch Claude Code implementation with:")
        console.print("  [cyan]• All agents selected[/cyan]")
        console.print("  [cyan]• Real Claude Code execution[/cyan]")
        console.print("  [cyan]• Automatic dependency resolution[/cyan]")

        # Check if design documents exist - Universal Path Structure (Cross-platform)
        script_dir = Path(__file__).parent.resolve()  # Requirements_Generation_System directory (absolute)
        byteforge_path = script_dir.parent  # ByteForge directory
        byteforge_project_path = byteforge_path / "project"  # ByteForgeProjectPath
        design_dir = byteforge_project_path / "design"
        if not design_dir.exists():
            console.print(f"[red]Design documents directory not found: {design_dir}[/red]")
            console.print("[red]Please generate design documents first (option 10)[/red]")
            return 1

        design_files = list(design_dir.glob("*-agent-design.md"))
        if not design_files:
            console.print(f"[red]No agent design documents found in {design_dir}[/red]")
            console.print("[red]Please generate design documents first (option 10)[/red]")
            return 1

        console.print(f"\n[green][OK] Found {len(design_files)} agent design documents[/green]")

        # Determine which phase to run
        target_phase = phase_map[choice]
        if target_phase == "auto":
            # Auto-detect next available phase
            try:
                from claude_code_executor import ClaudeCodeExecutor
                script_dir = Path(__file__).parent.resolve()  # Requirements_Generation_System directory
                claude_executor = ClaudeCodeExecutor(script_dir)

                # Check which phases are completed
                progress_tracker = claude_executor.progress_tracker

                if progress_tracker.get("phase1_mvp_core_features", {}).get("status") != "completed":
                    target_phase = "1"
                    console.print("[cyan]Auto-detected: Phase 1 needs to be completed[/cyan]")
                elif progress_tracker.get("phase2_advanced_features", {}).get("status") != "completed":
                    target_phase = "2"
                    console.print("[cyan]Auto-detected: Phase 2 is next[/cyan]")
                elif progress_tracker.get("phase3_production_ready", {}).get("status") != "completed":
                    target_phase = "3"
                    console.print("[cyan]Auto-detected: Phase 3 is next[/cyan]")
                else:
                    console.print("[green]All phases completed! Nothing to do.[/green]")
                    return 0

            except Exception as e:
                console.print(f"[yellow]Could not auto-detect phase, defaulting to Phase 1: {e}[/yellow]")
                target_phase = "1"

        confirm = Prompt.ask(f"\nProceed with Phase {target_phase} implementation?", choices=["y", "n"], default="y")
        if confirm.lower() != "y":
            console.print("[yellow]Quick launch cancelled.[/yellow]")
            return 0

        try:
            from claude_code_executor import ClaudeCodeExecutor

            script_dir = Path(__file__).parent.resolve()  # Requirements_Generation_System directory
            claude_executor = ClaudeCodeExecutor(script_dir)

            console.print(f"\n[yellow]🚀 Quick launching Phase {target_phase} with all agents...[/yellow]")

            # Execute Claude Code: agent_choice="6" (all agents), phase_choice=target_phase
            import asyncio
            result = asyncio.run(claude_executor.execute_implementation("6", target_phase))

            if result.success:
                console.print(f"\n[bold green][SUCCESS] Phase {target_phase} implementation completed successfully![/bold green]")
                console.print(f"[green][OK] Total execution time: {result.total_execution_time:.2f} seconds[/green]")

                # Display results for each agent
                for agent_result in result.agent_results:
                    status_color = "green" if agent_result.success else "red"
                    console.print(f"  [{status_color}]{agent_result.agent_name}: {'Success' if agent_result.success else 'Failed'}[/{status_color}]")
                    if agent_result.branch_name:
                        console.print(f"    [dim]Branch: {agent_result.branch_name}[/dim]")
                    if agent_result.pr_url:
                        console.print(f"    [dim]PR: {agent_result.pr_url}[/dim]")
            else:
                console.print(f"\n[bold red][ERROR] Phase {target_phase} implementation failed[/bold red]")
                if result.error_summary:
                    console.print(f"[red]Error summary: {result.error_summary}[/red]")

        except ImportError as e:
            console.print(f"[red]Error: Could not import ClaudeCodeExecutor: {e}[/red]")
            console.print(f"[yellow]Make sure claude_code_executor.py is properly implemented[/yellow]")
            return 1
        except Exception as e:
            console.print(f"[red]Error executing quick launch: {e}[/red]")
            import traceback
            traceback.print_exc()
            return 1

    elif choice in ["18", "19", "20"]:
        # UI Style Comparison System
        console.print("\n[bold magenta]🎨 UI Style Comparison System[/bold magenta]")

        try:
            # Get the project root path
            base_path = get_universal_base_path()  # Universal Path Structure

            # Handle the UI style choice
            success = handle_ui_style_menu_choice(choice, base_path)

            if success:
                console.print("\n[bold green][OK] UI Style operation completed successfully![/bold green]")
            else:
                console.print("\n[bold red][ERROR] UI Style operation failed![/bold red]")
                return 1

        except Exception as e:
            console.print(f"[red]Error in UI Style System: {e}[/red]")
            import traceback
            traceback.print_exc()
            return 1

    elif choice in ["21", "22", "23", "24"]:
        # Frontend Testing System
        console.print("\n[bold red]🧪 Frontend Testing System[/bold red]")

        try:
            from frontend_test_generator import FrontendTestGenerator

            base_path = get_universal_base_path()  # Universal Path Structure

            # Get API key and set environment
            key_info = get_api_key_info(model_provider)
            api_key = get_api_key(model_provider)

            if not api_key:
                console.print(f"[bold red]Error: No API key available for {key_info['name']}[/bold red]")
                return 1

            # Set environment variable
            os.environ[key_info["env_var"]] = api_key

            test_generator = FrontendTestGenerator(config['project']['name'], base_path, model_provider)

            if choice == "20":
                # Generate Frontend Test Plan
                console.print("\n[bold red][INFO] Generate Frontend Test Plan[/bold red]")
                console.print("This will analyze the frontend codebase and create a comprehensive test plan:")
                console.print("  [cyan]• Scan all frontend pages and components[/cyan]")
                console.print("  [cyan]• Identify interactive elements and controls[/cyan]")
                console.print("  [cyan]• Create test tasks for each page and modal[/cyan]")
                console.print("  [cyan]• Generate markdown task list for manual review[/cyan]")

                # Check if frontend directory exists
                frontend_dir = base_path / "FrontEnd"
                if not frontend_dir.exists():
                    console.print(f"[red]Frontend directory not found: {frontend_dir}[/red]")
                    console.print("[red]Please ensure the FrontEnd directory exists[/red]")
                    return 1

                confirm = Prompt.ask("\nProceed with frontend test plan generation?", choices=["y", "n"], default="y")
                if confirm.lower() != "y":
                    console.print("[yellow]Test plan generation cancelled.[/yellow]")
                    return 0

                console.print(f"\n[yellow]Analyzing frontend codebase and generating test plan...[/yellow]")

                import asyncio
                result = asyncio.run(test_generator.generate_test_plan())

                if result.success:
                    console.print(f"\n[bold green][SUCCESS] Frontend test plan generated successfully![/bold green]")
                    console.print(f"[green][OK] Test plan saved to: {result.test_plan_path}[/green]")
                    console.print(f"[green][OK] Total pages analyzed: {result.pages_analyzed}[/green]")
                    console.print(f"[green][OK] Total test tasks created: {result.test_tasks_created}[/green]")
                else:
                    console.print(f"\n[bold red][ERROR] Test plan generation failed[/bold red]")
                    if result.error_summary:
                        console.print(f"[red]Error summary: {result.error_summary}[/red]")

            elif choice == "21":
                # Execute testRigor Test Generation
                console.print("\n[bold red]🤖 Execute testRigor Test Generation[/bold red]")
                console.print("This will read the test plan and generate testRigor tests:")
                console.print("  [cyan]• Read the generated test plan markdown[/cyan]")
                console.print("  [cyan]• Create testRigor tests for each task[/cyan]")
                console.print("  [cyan]• Store tests in organized directory structure[/cyan]")
                console.print("  [cyan]• Generate execution reports[/cyan]")

                # Check if test plan exists
                test_plan_path = base_path / "generated_documents" / "testing" / "frontend_test_plan.md"
                if not test_plan_path.exists():
                    console.print(f"[red]Test plan not found: {test_plan_path}[/red]")
                    console.print("[red]Please generate the test plan first (option 20)[/red]")
                    return 1

                console.print(f"\n[green][OK] Found test plan: {test_plan_path}[/green]")

                confirm = Prompt.ask("\nProceed with testRigor test generation?", choices=["y", "n"], default="y")
                if confirm.lower() != "y":
                    console.print("[yellow]Test generation cancelled.[/yellow]")
                    return 0

                console.print(f"\n[yellow]Reading test plan and generating testRigor tests...[/yellow]")

                import asyncio
                result = asyncio.run(test_generator.generate_testrigor_tests())

                if result.success:
                    console.print(f"\n[bold green][SUCCESS] testRigor tests generated successfully![/bold green]")
                    console.print(f"[green][OK] Tests saved to: {result.tests_directory}[/green]")
                    console.print(f"[green][OK] Total tests generated: {result.tests_generated}[/green]")
                    console.print(f"[green][OK] Test execution time: {result.execution_time:.2f} seconds[/green]")
                else:
                    console.print(f"\n[bold red][ERROR] Test generation failed[/bold red]")
                    if result.error_summary:
                        console.print(f"[red]Error summary: {result.error_summary}[/red]")

            elif choice == "22":
                # Complete Testing Workflow
                console.print("\n[bold red]🚀 Complete Testing Workflow[/bold red]")
                console.print("This will run the complete testing workflow:")
                console.print("  [cyan]Step 1:[/cyan] Generate frontend test plan")
                console.print("  [cyan]Step 2:[/cyan] Generate testRigor tests")
                console.print("  [cyan]Step 3:[/cyan] Create execution summary")

                confirm = Prompt.ask("\nProceed with complete testing workflow?", choices=["y", "n"], default="y")
                if confirm.lower() != "y":
                    console.print("[yellow]Testing workflow cancelled.[/yellow]")
                    return 0

                console.print(f"\n[yellow]Starting complete testing workflow...[/yellow]")

                import asyncio
                result = asyncio.run(test_generator.run_complete_workflow())

                if result.success:
                    console.print(f"\n[bold green][SUCCESS] Complete testing workflow completed successfully![/bold green]")
                    console.print(f"[green][OK] Test plan: {result.test_plan_path}[/green]")
                    console.print(f"[green][OK] Tests directory: {result.tests_directory}[/green]")
                    console.print(f"[green][OK] Total execution time: {result.total_execution_time:.2f} seconds[/green]")
                    console.print(f"[green][OK] Pages analyzed: {result.pages_analyzed}[/green]")
                    console.print(f"[green][OK] Tests generated: {result.tests_generated}[/green]")
                else:
                    console.print(f"\n[bold red][ERROR] Testing workflow failed[/bold red]")
                    if result.error_summary:
                        console.print(f"[red]Error summary: {result.error_summary}[/red]")

            elif choice == "23":
                # Fix E2E Test Issues with Claude Code
                console.print("\n[bold red][TOOL] Fix E2E Test Issues with Claude Code[/bold red]")
                console.print("This will use Claude Code to fix frontend issues identified by E2E test results:")
                console.print("  [cyan]• Analyze current E2E test results and failures[/cyan]")
                console.print("  [cyan]• Fix form field mapping issues[/cyan]")
                console.print("  [cyan]• Add missing required attributes to forms[/cyan]")
                console.print("  [cyan]• Improve form workflows and error handling[/cyan]")
                console.print("  [cyan]• Implement missing search functionality[/cyan]")

                # Check if frontend directory exists
                frontend_dir = base_path / "FrontEnd"
                if not frontend_dir.exists():
                    console.print(f"[red]Frontend directory not found: {frontend_dir}[/red]")
                    console.print("[red]Please ensure the FrontEnd directory exists[/red]")
                    return 1

                # Check if Claude Code instructions exist
                instructions_file = frontend_dir / "claude_code_instructions_e2e_fixes.md"
                if not instructions_file.exists():
                    console.print(f"[red]Claude Code instructions not found: {instructions_file}[/red]")
                    console.print("[red]Instructions file should have been created automatically[/red]")
                    return 1

                console.print(f"\n[green][OK] Found Claude Code instructions: {instructions_file}[/green]")
                console.print(f"[green][OK] Found frontend directory: {frontend_dir}[/green]")

                confirm = Prompt.ask("\nProceed with Claude Code E2E fixes?", choices=["y", "n"], default="y")
                if confirm.lower() != "y":
                    console.print("[yellow]E2E fixes cancelled.[/yellow]")
                    return 0

                console.print(f"\n[yellow]Launching Claude Code to fix E2E test issues...[/yellow]")

                try:
                    import subprocess
                    import tempfile

                    console.print("[cyan]🚀 Launching Claude Code in a new visible terminal window...[/cyan]")
                    console.print("[dim]This will open a new terminal window where you can watch Claude Code work[/dim]")

                    # Create a temporary script file to avoid command line issues
                    diagnostic_script_content = '''#!/bin/bash
echo "[SEARCH] === Claude Code E2E Fixes Diagnostic ==="
echo "📅 $(date)"
echo ""

echo "[TOOL] Step 1: Checking WSL environment..."
echo "[FOLDER] Current directory: $(pwd)"
echo "🐧 WSL Distribution: $(cat /etc/os-release | grep PRETTY_NAME)"
echo ""

echo "[TOOL] Step 2: Checking target directory..."
TARGET_DIR="/mnt/d/Repository/ContractLogix/LSOMitigator/ByteForge/project/FrontEnd"
if [ -d "$TARGET_DIR" ]; then
    echo "[OK] Target directory exists: $TARGET_DIR"
    cd "$TARGET_DIR"
    echo "[FOLDER] Changed to: $(pwd)"
else
    echo "[ERROR] Target directory not found: $TARGET_DIR"
    echo "📂 Available directories in /mnt/d/Repository/@Clients/:"
    ls -la /mnt/d/Repository/@Clients/ 2>/dev/null || echo "[ERROR] Parent directory not accessible"
    echo ""
    echo "[PAUSE]  Press Enter to continue anyway or Ctrl+C to exit..."
    read
fi

echo ""
echo "[TOOL] Step 3: Checking instruction file..."
INSTRUCTION_FILE="claude_code_instructions_e2e_fixes.md"
if [ -f "$INSTRUCTION_FILE" ]; then
    echo "[OK] Instruction file found: $INSTRUCTION_FILE"
    echo "[FILE] File size: $(wc -c < "$INSTRUCTION_FILE") bytes"
    echo "📝 First few lines:"
    head -5 "$INSTRUCTION_FILE"
else
    echo "[ERROR] Instruction file not found: $INSTRUCTION_FILE"
    echo "📂 Available files:"
    ls -la *.md 2>/dev/null || echo "[ERROR] No .md files found"
    echo ""
    echo "[PAUSE]  Press Enter to continue anyway or Ctrl+C to exit..."
    read
fi

echo ""
echo "[TOOL] Step 4: Checking Claude Code installation..."
if command -v claude >/dev/null 2>&1; then
    echo "[OK] Claude Code is installed"
    echo "[INFO] Claude version: $(claude --version 2>/dev/null || echo 'Version check failed')"
else
    echo "[ERROR] Claude Code is not installed or not in PATH"
    echo "[SEARCH] Checking common installation locations..."
    ls -la ~/.local/bin/claude 2>/dev/null && echo "Found in ~/.local/bin/" || echo "Not in ~/.local/bin/"
    ls -la /usr/local/bin/claude 2>/dev/null && echo "Found in /usr/local/bin/" || echo "Not in /usr/local/bin/"
    echo ""
    echo "[TIP] To install Claude Code, run:"
    echo "   curl -sSL https://claude.ai/install.sh | bash"
    echo ""
    echo "[PAUSE]  Press Enter to continue anyway or Ctrl+C to exit..."
    read
fi

echo ""
echo "🚀 Step 5: Attempting to run Claude Code..."
if [ -f "$INSTRUCTION_FILE" ] && command -v claude >/dev/null 2>&1; then
    echo "▶️  Executing: claude --model sonnet -p \\"$(cat $INSTRUCTION_FILE)\\""
    echo ""
    claude --model sonnet -p "$(cat $INSTRUCTION_FILE)"
    CLAUDE_EXIT_CODE=$?
    echo ""
    if [ $CLAUDE_EXIT_CODE -eq 0 ]; then
        echo "[OK] Claude Code completed successfully!"
    else
        echo "[ERROR] Claude Code failed with exit code: $CLAUDE_EXIT_CODE"
    fi
else
    echo "[WARNING]  Skipping Claude Code execution due to missing requirements"
fi

echo ""
echo "🏁 === Diagnostic Complete ==="
echo "[PAUSE]  Press Enter to close this window..."
read
'''

                    # Create temporary script file
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as temp_script:
                        temp_script.write(diagnostic_script_content)
                        temp_script_path = temp_script.name

                    # Convert Windows path to WSL path
                    wsl_script_path = temp_script_path.replace('\\', '/').replace('C:', '/mnt/c')

                    # Try multiple methods to ensure a visible terminal window opens
                    success = False

                    # Method 1: Try Windows Terminal first
                    try:
                        subprocess.Popen([
                            "wt", "new-tab", "--title", "Claude Code E2E Fixes - Diagnostic",
                            "wsl", "-d", "Ubuntu", "-e", "bash", wsl_script_path
                        ])
                        console.print("[green][OK] Launched diagnostic terminal in Windows Terminal[/green]")
                        success = True
                    except FileNotFoundError:
                        # Method 2: Fall back to cmd if Windows Terminal not available
                        try:
                            subprocess.Popen([
                                "cmd", "/c", "start", "cmd", "/k",
                                f'title Claude Code E2E Fixes - Diagnostic && wsl -d Ubuntu -e bash {wsl_script_path}'
                            ])
                            console.print("[green][OK] Launched diagnostic terminal in Command Prompt[/green]")
                            success = True
                        except Exception as cmd_error:
                            # Method 3: Try PowerShell as final fallback
                            try:
                                subprocess.Popen([
                                    "powershell", "-Command",
                                    f'Start-Process cmd -ArgumentList "/k title Claude Code E2E Fixes - Diagnostic && wsl -d Ubuntu -e bash {wsl_script_path}"'
                                ])
                                console.print("[green][OK] Launched diagnostic terminal via PowerShell[/green]")
                                success = True
                            except Exception as ps_error:
                                console.print(f"[red][ERROR] All terminal launch methods failed[/red]")
                                console.print(f"[red]Windows Terminal error: FileNotFoundError[/red]")
                                console.print(f"[red]CMD error: {cmd_error}[/red]")
                                console.print(f"[red]PowerShell error: {ps_error}[/red]")

                    if success:
                        console.print(f"\n[bold green][SUCCESS] Claude Code diagnostic terminal launched successfully![/bold green]")
                        console.print(f"[green][OK] A new terminal window should have opened with comprehensive diagnostics[/green]")
                        console.print(f"[green][OK] The terminal will stay open so you can see exactly what's happening[/green]")
                        console.print(f"\n[cyan][DISPLAY] In the diagnostic terminal window, you'll see:[/cyan]")
                        console.print(f"  • WSL environment verification")
                        console.print(f"  • Directory and file existence checks")
                        console.print(f"  • Claude Code installation status")
                        console.print(f"  • Step-by-step execution progress")
                        console.print(f"  • Detailed error messages if anything fails")
                        console.print(f"\n[cyan]The terminal will pause at each step if there are issues,[/cyan]")
                        console.print(f"[cyan]so you can see exactly what needs to be fixed.[/cyan]")

                        # Give the terminal time to start
                        import time
                        time.sleep(2)

                        console.print(f"\n[yellow][TIME]  Diagnostic terminal is now running.[/yellow]")
                        console.print(f"[yellow]Check the terminal window to see what's happening![/yellow]")
                    else:
                        console.print(f"\n[bold red][ERROR] Failed to launch visible terminal window[/bold red]")
                        console.print(f"[yellow][TIP] You can manually run the diagnostic script with:[/yellow]")
                        console.print(f"[dim]wsl -d Ubuntu -e bash {wsl_script_path}[/dim]")

                    # Clean up temporary file after a delay (let the terminal start first)
                    import threading
                    def cleanup_temp_file():
                        time.sleep(10)  # Wait 10 seconds for terminal to start
                        try:
                            os.unlink(temp_script_path)
                        except:
                            pass  # Ignore cleanup errors

                    threading.Thread(target=cleanup_temp_file, daemon=True).start()

                except Exception as e:
                    console.print(f"\n[bold red][ERROR] Error launching Claude Code: {e}[/bold red]")
                    console.print(f"[yellow][TIP] You can manually run Claude Code with:[/yellow]")
                    console.print(f"[dim]cd FrontEnd && claude --model sonnet -p \"$(cat claude_code_instructions_e2e_fixes.md)\"[/dim]")

                    # Clean up temp file on error
                    try:
                        os.unlink(temp_script_path)
                    except:
                        pass

        except ImportError as e:
            console.print(f"[red]Error: Could not import FrontendTestGenerator: {e}[/red]")
            console.print(f"[yellow]Make sure frontend_test_generator.py is properly implemented[/yellow]")
            return 1
        except Exception as e:
            console.print(f"[red]Error in Frontend Testing System: {e}[/red]")
            import traceback
            traceback.print_exc()
            return 1

    elif choice == "25":
        # Browse Application Templates
        from template_manager import TemplateManager
        template_manager = TemplateManager(get_universal_base_path())  # Universal Path Structure
        template_manager.display_template_catalog()

    elif choice == "26":
        # Create New Project from Template
        from template_manager import create_new_project_interactive
        project_name = create_new_project_interactive(get_universal_base_path())  # Universal Path Structure
        if project_name:
            console.print(f"\n[green][OK] Project '{project_name}' created successfully![/green]")
            console.print("[dim]You can now navigate to the project directory and run the AI generation system.[/dim]")

    elif choice == "27":
        # Reset Failed Claude Code Agents
        console.print("\n[bold red]Reset Failed Claude Code Agents[/bold red]")
        console.print("This will reset all failed Claude Code agents back to 'not_started' status,")
        console.print("allowing them to be retried in the next execution.")

        # Check if progress tracker exists
        script_dir = Path(__file__).parent.resolve()
        byteforge_path = script_dir.parent
        byteforge_project_path = byteforge_path / "project"
        progress_tracker_path = byteforge_project_path / "design" / "claude_instructions" / "progress_tracker.json"

        if not progress_tracker_path.exists():
            console.print(f"[yellow]No progress tracker found: {progress_tracker_path}[/yellow]")
            console.print("[yellow]Nothing to reset.[/yellow]")
            return 0

        try:
            # Load progress tracker
            with open(progress_tracker_path, 'r', encoding='utf-8') as f:
                progress_data = json.load(f)

            # Count all non-not_started agents (failed, completed, in_progress)
            resetable_agents = []
            for phase_name, phase_data in progress_data.items():
                if phase_name == "execution_metadata":
                    continue
                
                if "agents" in phase_data:
                    for agent_key, agent_data in phase_data["agents"].items():
                        status = agent_data.get("status")
                        if status in ["failed", "completed", "in_progress"]:
                            resetable_agents.append((agent_key, status))

            if not resetable_agents:
                console.print("[green]All agents are already in 'not_started' status. Nothing to reset.[/green]")
                return 0

            console.print(f"\n[yellow]Found {len(resetable_agents)} agents that can be reset:[/yellow]")
            for agent, status in resetable_agents:
                status_color = "red" if status == "failed" else "green" if status == "completed" else "yellow"
                console.print(f"  • {agent}: [{status_color}]{status}[/{status_color}]")

            console.print(f"\n[cyan]This will reset all agents back to 'not_started' so they can run again.[/cyan]")
            console.print(f"[cyan]This is useful when agents completed but didn't actually generate code.[/cyan]")

            confirm = Prompt.ask(f"\nReset {len(resetable_agents)} agents to 'not_started' status?", choices=["y", "n"], default="y")
            if confirm.lower() != "y":
                console.print("[yellow]Reset cancelled.[/yellow]")
                return 0

            # Reset all non-not_started agents
            reset_count = 0
            for phase_name, phase_data in progress_data.items():
                if phase_name == "execution_metadata":
                    continue
                
                if "agents" in phase_data:
                    for agent_key, agent_data in phase_data["agents"].items():
                        status = agent_data.get("status")
                        if status in ["failed", "completed", "in_progress"]:
                            agent_data["status"] = "not_started"
                            agent_data["started_at"] = None
                            agent_data["completed_at"] = None
                            agent_data["actual_duration_minutes"] = None
                            agent_data["error_log"] = None
                            agent_data["retry_count"] = 0
                            reset_count += 1

            # Save updated progress tracker
            with open(progress_tracker_path, 'w', encoding='utf-8') as f:
                json.dump(progress_data, f, indent=2, ensure_ascii=False)

            console.print(f"\n[bold green][SUCCESS] Reset {reset_count} failed agents![/bold green]")
            console.print("[green]All failed agents have been reset to 'not_started' status.[/green]")
            console.print("[green]You can now run Claude Code implementation again (option 13).[/green]")

        except Exception as e:
            console.print(f"[red]Error resetting failed agents: {e}[/red]")
            import traceback
            traceback.print_exc()
            return 1

    else:
        console.print("[red]Invalid choice[/red]")
        return 1
    
    console.print("\n[bold green]Process completed![/bold green]")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[bold red]Unexpected error: {str(e)}[/bold red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)
