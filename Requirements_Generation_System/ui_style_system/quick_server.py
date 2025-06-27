#!/usr/bin/env python3
"""
Quick HTTP server for live comparison page
"""

import http.server
import socketserver
import webbrowser
import threading
import time
from pathlib import Path
from rich.console import Console

console = Console()

def start_server(port=8001):
    """Start a simple HTTP server on a different port"""
    
    try:
        with socketserver.TCPServer(("", port), http.server.SimpleHTTPRequestHandler) as httpd:
            console.print(f"🌐 Server started at http://localhost:{port}")
            
            # Open the live page in browser
            def open_browser():
                time.sleep(1)
                webbrowser.open(f"http://localhost:{port}/live_comparison.html")
                console.print(f"🌐 Opened: http://localhost:{port}/live_comparison.html")
            
            browser_thread = threading.Thread(target=open_browser)
            browser_thread.daemon = True
            browser_thread.start()
            
            console.print(f"⏹️  Press Ctrl+C to stop")
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        console.print(f"\n🛑 Server stopped")
    except OSError as e:
        if "Address already in use" in str(e):
            console.print(f"[red]❌ Port {port} in use. Trying {port + 1}...[/red]")
            start_server(port + 1)
        else:
            console.print(f"[red]❌ Server error: {e}[/red]")

if __name__ == "__main__":
    start_server()
