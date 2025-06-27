#!/usr/bin/env python3
"""
Open the simple HTML dashboard in a web browser
"""

import os
import sys
import webbrowser
from pathlib import Path

def main():
    """Open the dashboard in a web browser"""
    # Get the directory of this script
    script_dir = Path(__file__).parent.absolute()
    
    # Path to the simple dashboard HTML file
    dashboard_path = script_dir / "simple_dashboard.html"
    
    if not dashboard_path.exists():
        print(f"Error: Dashboard file not found at {dashboard_path}")
        return 1
    
    # Convert to file URL
    dashboard_url = f"file://{dashboard_path.absolute()}"
    
    print(f"Opening dashboard at: {dashboard_url}")
    
    # Open in default browser
    webbrowser.open(dashboard_url)
    
    print("\nDashboard opened in your web browser.")
    print("Make sure the backend server is running with:")
    print("python run_simple.py")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())