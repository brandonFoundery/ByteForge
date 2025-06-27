#!/usr/bin/env python3
"""
Simple HTTP Server for Live UI Generation
Serves the live comparison page and allows AJAX requests to work properly
"""

import http.server
import socketserver
import webbrowser
import threading
import time
from pathlib import Path

def start_server(port=8000):
    """Start a simple HTTP server"""
    
    # Change to the ui_style_system directory
    ui_system_path = Path(__file__).parent
    print(f"📁 Serving from: {ui_system_path}")
    
    # Create server
    handler = http.server.SimpleHTTPRequestHandler
    
    try:
        with socketserver.TCPServer(("", port), handler) as httpd:
            print(f"🌐 Server started at: http://localhost:{port}")
            print(f"📱 Live page URL: http://localhost:{port}/live_comparison.html")
            
            # Open browser after a short delay
            def open_browser():
                time.sleep(1)
                webbrowser.open(f"http://localhost:{port}/live_comparison.html")
            
            browser_thread = threading.Thread(target=open_browser)
            browser_thread.daemon = True
            browser_thread.start()
            
            print("🔄 Server running... Press Ctrl+C to stop")
            httpd.serve_forever()
            
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ Port {port} is already in use. Trying port {port + 1}...")
            start_server(port + 1)
        else:
            print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    start_server()
