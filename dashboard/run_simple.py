#!/usr/bin/env python3
"""
Simple script to run the Requirements Generation Dashboard
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

# Get the directory of this script
SCRIPT_DIR = Path(__file__).parent.absolute()
BACKEND_DIR = SCRIPT_DIR / "backend"
FRONTEND_DIR = SCRIPT_DIR / "frontend"

# Default paths
DEFAULT_OUTPUT_DIR = Path("d:/Repository/@Clients/FY.WB.Midway/generated_documents")
DEFAULT_STATUS_DIR = Path("d:/Repository/@Clients/FY.WB.Midway/generation_status")

def main():
    """Main entry point"""
    print("Starting Requirements Generation Dashboard")
    
    # Create directories if they don't exist
    DEFAULT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    DEFAULT_STATUS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Start backend server
    print("\n1. Starting backend server...")
    backend_cmd = [
        sys.executable, "-m", "uvicorn", 
        "dashboard.backend.app:app", 
        "--host", "0.0.0.0", 
        "--port", "8001",
        "--reload"
    ]
    
    backend_env = os.environ.copy()
    backend_env["OUTPUT_PATH"] = str(DEFAULT_OUTPUT_DIR)
    backend_env["STATUS_PATH"] = str(DEFAULT_STATUS_DIR)
    
    backend_process = subprocess.Popen(
        backend_cmd,
        env=backend_env,
        cwd=str(SCRIPT_DIR.parent),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )
    
    # Wait for backend to start
    print("Waiting for backend server to start...")
    time.sleep(3)
    
    # Start frontend server
    print("\n2. Starting frontend server...")
    try:
        # Check if npm is available
        npm_check = subprocess.run(
            ["where", "npm"] if sys.platform == "win32" else ["which", "npm"],
            capture_output=True,
            text=True
        )
        
        if npm_check.returncode != 0:
            print("WARNING: npm not found in PATH. Cannot start frontend server automatically.")
            print("Please start the frontend server manually with:")
            print(f"cd {FRONTEND_DIR}")
            print("npm run dev")
            frontend_process = None
        else:
            frontend_cmd = ["npm", "run", "dev"]
            
            frontend_process = subprocess.Popen(
                frontend_cmd,
                cwd=str(FRONTEND_DIR),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
    except Exception as e:
        print(f"Error starting frontend: {str(e)}")
        print("Please start the frontend server manually with:")
        print(f"cd {FRONTEND_DIR}")
        print("npm run dev")
        frontend_process = None
    
    # Wait for backend to fully start
    print("Waiting for backend server to fully start...")
    time.sleep(3)
    
    # Open browser if frontend is running
    if frontend_process:
        print("Waiting for frontend server to start...")
        time.sleep(5)
        
        print("\n3. Opening dashboard in browser...")
        webbrowser.open("http://localhost:5173")
        
        print("\nDashboard is now running!")
        print("- Backend: http://localhost:8001")
        print("- Frontend: http://localhost:5173")
    else:
        print("\nBackend server is running at http://localhost:8001")
        print("Please start the frontend manually and then access the dashboard at http://localhost:5173")
    
    print("\nPress Ctrl+C to stop the servers")
    
    try:
        # Keep the script running and display output from both processes
        while True:
            # Check if backend process is still running
            if backend_process.poll() is not None:
                print("Backend server stopped unexpectedly")
                break
                
            # Check frontend process if it exists
            if frontend_process and frontend_process.poll() is not None:
                print("Frontend server stopped unexpectedly")
                # Continue running as long as backend is up
                frontend_process = None
                
            # Display output from backend
            backend_output = backend_process.stdout.readline()
            if backend_output:
                print(f"[Backend] {backend_output.strip()}")
                
            # Display output from frontend if it exists
            if frontend_process:
                frontend_output = frontend_process.stdout.readline()
                if frontend_output:
                    print(f"[Frontend] {frontend_output.strip()}")
                
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nShutting down servers...")
        
        # Terminate backend process
        backend_process.terminate()
        
        # Terminate frontend process if it exists
        if frontend_process:
            frontend_process.terminate()
        
        print("Servers stopped")

if __name__ == "__main__":
    main()