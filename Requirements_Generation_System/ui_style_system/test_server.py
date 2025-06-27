#!/usr/bin/env python3
"""
Simple HTTP server to test the live page without CORS issues
"""

import http.server
import socketserver
import webbrowser
import threading
import time
from pathlib import Path
from rich.console import Console

console = Console()

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

def start_server(port=8000):
    """Start a simple HTTP server"""
    
    # Change to the ui_style_system directory
    ui_system_path = Path(__file__).parent
    import os
    os.chdir(ui_system_path)
    
    try:
        with socketserver.TCPServer(("", port), CustomHTTPRequestHandler) as httpd:
            console.print(f"🌐 Server started at http://localhost:{port}")
            console.print(f"📁 Serving from: {ui_system_path}")
            
            # Open the live page in browser
            def open_browser():
                time.sleep(1)  # Wait for server to start
                webbrowser.open(f"http://localhost:{port}/live_comparison.html")
                console.print(f"🌐 Opened live page: http://localhost:{port}/live_comparison.html")
                
                # Also open the direct test
                time.sleep(1)
                webbrowser.open(f"http://localhost:{port}/test_direct.html")
                console.print(f"🧪 Opened test page: http://localhost:{port}/test_direct.html")
            
            # Start browser opening in a separate thread
            browser_thread = threading.Thread(target=open_browser)
            browser_thread.daemon = True
            browser_thread.start()
            
            console.print(f"\n🔧 Testing URLs:")
            console.print(f"   Live Page: http://localhost:{port}/live_comparison.html")
            console.print(f"   Test Page: http://localhost:{port}/test_direct.html")
            console.print(f"   Status JSON: http://localhost:{port}/generation_status.json")
            console.print(f"\n⏹️  Press Ctrl+C to stop the server")
            
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        console.print(f"\n🛑 Server stopped")
    except OSError as e:
        if "Address already in use" in str(e):
            console.print(f"[red]❌ Port {port} is already in use. Trying port {port + 1}...[/red]")
            start_server(port + 1)
        else:
            console.print(f"[red]❌ Server error: {e}[/red]")

def main():
    """Start the test server"""
    console.print("🚀 Starting test server for live page debugging...")
    start_server()

if __name__ == "__main__":
    main()
