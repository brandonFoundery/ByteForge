#!/usr/bin/env python3
"""
Debug script to check if Claude Code hooks are working.
This will log when hooks are called.
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path

def log_hook_call(hook_name, data):
    """Log hook calls to a debug file."""
    debug_file = Path("hook-debug.log")
    
    with open(debug_file, "a") as f:
        f.write(f"\n[{datetime.now().isoformat()}] {hook_name} called\n")
        f.write(f"Data: {json.dumps(data, indent=2)}\n")
        f.write("-" * 50 + "\n")

if __name__ == "__main__":
    # This script can be used to test if hooks are being called
    hook_name = sys.argv[1] if len(sys.argv) > 1 else "unknown"
    
    try:
        # Read JSON input from stdin
        input_data = json.load(sys.stdin)
        log_hook_call(hook_name, input_data)
        
        # Send to observability server
        import urllib.request
        import urllib.error
        
        event_data = {
            'source_app': 'claude-code-debug',
            'session_id': input_data.get('session_id', 'debug-session'),
            'hook_event_type': f'Debug{hook_name}',
            'payload': input_data,
            'timestamp': int(datetime.now().timestamp() * 1000)
        }
        
        try:
            req = urllib.request.Request(
                'http://localhost:4000/events',
                data=json.dumps(event_data).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    print(f"Debug: {hook_name} event sent successfully", file=sys.stderr)
                
        except Exception as e:
            print(f"Debug: Failed to send {hook_name} event: {e}", file=sys.stderr)
            
        sys.exit(0)
        
    except Exception as e:
        log_hook_call(hook_name, {"error": str(e)})
        sys.exit(0)