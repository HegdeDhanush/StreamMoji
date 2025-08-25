#!/usr/bin/env python3
"""
Simple Dashboard Server for StreamMoji
Serves dashboard.html on port 8082 with proper CORS headers
"""

import http.server
import socketserver
import webbrowser
import threading
import time
import os

class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

def start_server():
    PORT = 8082
    
    print("🎯 StreamMoji Dashboard Server")
    print("=" * 40)
    print(f"📁 Starting server from: {os.getcwd()}")
    print(f"📁 Files in current directory:")
    
    for file in os.listdir('.'):
        if file.endswith('.html'):
            print(f"   📄 {file}")
    
    if os.path.exists('dashboard.html'):
        print("✅ dashboard.html found!")
    else:
        print("❌ dashboard.html not found!")
        return
    
    try:
        with socketserver.TCPServer(("", PORT), CORSHTTPRequestHandler) as httpd:
            print(f"🚀 Dashboard server started on port {PORT}")
            print(f"🌐 Open: http://localhost:{PORT}/dashboard.html")
            print("💡 Make sure your Flask API is running on port 5000")
            print("🔄 Press Ctrl+C to stop")
            print()
            
            def open_browser():
                time.sleep(2)
                webbrowser.open(f'http://localhost:{PORT}/dashboard.html')
            
            # Open browser after 2 seconds
            threading.Thread(target=open_browser, daemon=True).start()
            
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("🛑 Server stopped")
    except OSError as e:
        if e.errno == 10048:  # Port already in use
            print(f"❌ Port {PORT} is already in use!")
            print("   Try stopping other servers or use a different port")
        else:
            print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    start_server()