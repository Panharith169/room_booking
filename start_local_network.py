#!/usr/bin/env python
"""
Local Network Server Starter for Room Booking System
This script helps you run the Django server accessible from phones on the same WiFi network
"""

import socket
import subprocess
import sys
import os
from pathlib import Path

def get_local_ip():
    """Get the local IP address"""
    try:
        # Connect to a remote server to get local IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
        return local_ip
    except Exception:
        return "127.0.0.1"

def check_port_available(port):
    """Check if a port is available"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('', port))
            return True
        except socket.error:
            return False

def main():
    print("🚀 RUPP Room Booking System - Local Network Server")
    print("=" * 60)
    
    # Get local IP
    local_ip = get_local_ip()
    port = 8000
    
    # Check if port is available
    if not check_port_available(port):
        print(f"⚠️  Port {port} is already in use. Trying port 8001...")
        port = 8001
        if not check_port_available(port):
            print(f"❌ Port {port} is also in use. Please close other Django servers.")
            return
    
    print(f"🌐 Local IP Address: {local_ip}")
    print(f"🔗 Server will run on: http://{local_ip}:{port}")
    print()
    print("⚠️  IMPORTANT REQUIREMENTS:")
    print("   • Your computer must stay ON and running this server")
    print("   • Phone and computer must be on the SAME WiFi network")
    print("   • This only works on LOCAL network (not internet)")
    print()
    print("📱 Phone Access Instructions:")
    print(f"   1. Make sure your phone is on the same WiFi network as this computer")
    print(f"   2. Keep this computer ON and this server running")
    print(f"   3. Open browser on your phone")
    print(f"   4. Go to: http://{local_ip}:{port}")
    print()
    print("💻 Computer Access:")
    print(f"   Local: http://localhost:{port}")
    print(f"   Network: http://{local_ip}:{port}")
    print()
    print("🔄 When server stops working:")
    print("   • If you close this window, phone access stops")
    print("   • If computer goes to sleep, phone access stops")
    print("   • If you disconnect from WiFi, phone access stops")
    print()
    print("🔥 Starting Django development server...")
    print("   Press Ctrl+C to stop the server")
    print("=" * 60)
    
    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    # Start Django server
    try:
        subprocess.run([
            sys.executable, 
            "manage.py", 
            "runserver", 
            f"0.0.0.0:{port}"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    main()
