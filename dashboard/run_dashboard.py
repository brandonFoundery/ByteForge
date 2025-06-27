#!/usr/bin/env python3
"""
Run the Requirements Generation Dashboard
This script starts both the backend FastAPI server and the frontend development server.
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path
import signal
import argparse

# Get the directory of this script
SCRIPT_DIR = Path(__file__).parent.absolute()
BACKEND_DIR = SCRIPT_DIR / "backend"
FRONTEND_DIR = SCRIPT_DIR / "frontend"

# Default paths
DEFAULT_OUTPUT_DIR = Path("d:/Repository/@Clients/FY.WB.Midway/generated_documents")
DEFAULT_STATUS_DIR = Path("d:/Repository/@Clients/FY.WB.Midway/generation_status")

# Process handles
backend_process = None
frontend_process = None

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Run the Requirements Generation Dashboard")
    parser.add_argument("--output-dir", type=str, default=str(DEFAULT_OUTPUT_DIR),
                        help="Directory containing generated documents")
    parser.add_argument("--status-dir", type=str, default=str(DEFAULT_STATUS_DIR),
                        help="Directory containing status files")
    parser.add_argument("--backend-only", action="store_true",
                        help="Run only the backend server")
    parser.add_argument("--frontend-only", action="store_true",
                        help="Run only the frontend server")
    parser.add_argument("--port", type=int, default=8000,
                        help="Port for the backend server (default: 8000)")
    parser.add_argument("--no-open", action="store_true",
                        help="Don't automatically open browser")
    
    return parser.parse_args()

def start_backend(output_dir, status_dir, port):
    """Start the FastAPI backend server"""
    print(f"Starting backend server on port {port}...")
    
    # Create directories if they don't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    Path(status_dir).mkdir(parents=True, exist_ok=True)
    
    # Set environment variables for the backend
    env = os.environ.copy()
    env["OUTPUT_PATH"] = str(output_dir)
    env["STATUS_PATH"] = str(status_dir)
    env["PORT"] = str(port)
    
    # Start the backend server
    cmd = [
        sys.executable, "-m", "uvicorn", 
        "dashboard.backend.app:app", 
        "--host", "0.0.0.0", 
        "--port", str(port),
        "--reload"
    ]
    
    process = subprocess.Popen(
        cmd,
        env=env,
        cwd=str(SCRIPT_DIR.parent),  # Run from parent directory
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )
    
    # Wait for server to start
    for line in process.stdout:
        print(f"[Backend] {line.strip()}")
        if "Application startup complete" in line:
            print("Backend server started successfully!")
            break
    
    return process

def start_frontend():
    """Start the React frontend development server"""
    print("Starting frontend development server...")
    
    # Check if node_modules exists, if not run npm install
    if not (FRONTEND_DIR / "node_modules").exists():
        print("Installing frontend dependencies...")
        subprocess.run(
            ["npm", "install"],
            cwd=str(FRONTEND_DIR),
            check=True
        )
    
    # Start the frontend server
    cmd = ["npm", "run", "dev"]
    
    process = subprocess.Popen(
        cmd,
        cwd=str(FRONTEND_DIR),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )
    
    # Wait for server to start
    frontend_url = None
    for line in process.stdout:
        print(f"[Frontend] {line.strip()}")
        
        # Extract the local URL
        if "Local:" in line:
            frontend_url = line.split("Local:")[1].strip()
            print(f"Frontend server started at {frontend_url}")
            break
    
    return process, frontend_url

def cleanup(signum=None, frame=None):
    """Clean up processes on exit"""
    print("\nShutting down servers...")
    
    if backend_process:
        backend_process.terminate()
        print("Backend server stopped")
    
    if frontend_process:
        frontend_process.terminate()
        print("Frontend server stopped")
    
    print("Cleanup complete")
    sys.exit(0)

def main():
    """Main entry point"""
    global backend_process, frontend_process
    
    # Parse arguments
    args = parse_args()
    
    # Register signal handlers for clean shutdown
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)
    
    try:
        # Start backend if requested
        if not args.frontend_only:
            backend_process = start_backend(args.output_dir, args.status_dir, args.port)
        
        # Start frontend if requested
        frontend_url = None
        if not args.backend_only:
            frontend_process, frontend_url = start_frontend()
        
        # Open browser if requested
        if frontend_url and not args.no_open:
            print(f"Opening browser at {frontend_url}")
            webbrowser.open(frontend_url)
        
        # Keep the script running
        print("\nPress Ctrl+C to stop the servers")
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if backend_process and backend_process.poll() is not None:
                print("Backend server stopped unexpectedly")
                cleanup()
            
            if frontend_process and frontend_process.poll() is not None:
                print("Frontend server stopped unexpectedly")
                cleanup()
    
    except KeyboardInterrupt:
        cleanup()
    except Exception as e:
        print(f"Error: {e}")
        cleanup()

if __name__ == "__main__":
    main()