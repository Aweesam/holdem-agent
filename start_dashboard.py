#!/usr/bin/env python3
"""
Start script for the Holdem Agent Dashboard system.
This script starts both the API server and NextJS development server.
"""

import subprocess
import sys
import os
import time
import signal
import webbrowser
from pathlib import Path

def start_api_server():
    """Start the Live Agent FastAPI server."""
    print("🚀 Starting Live Agent server on port 8000...")
    cmd = ["python", "live_agent_server.py"]
    return subprocess.Popen(cmd, cwd="/home/envy/holdem")

def start_nextjs_server():
    """Start the NextJS development server."""
    print("🚀 Starting NextJS dashboard...")
    cmd = ["npm", "run", "dev"]
    return subprocess.Popen(cmd, cwd="/home/envy/holdem/holdem-dashboard", 
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                          universal_newlines=True, bufsize=1)

def main():
    print("🎰 Starting Holdem Agent Dashboard System")
    print("=" * 50)
    
    processes = []
    
    try:
        # Start API server
        api_process = start_api_server()
        processes.append(api_process)
        time.sleep(3)  # Give API server time to start
        
        # Start NextJS server
        nextjs_process = start_nextjs_server()
        processes.append(nextjs_process)
        
        # Monitor Next.js output to find the actual port
        frontend_url = None
        print("⏳ Waiting for Next.js to start...")
        
        # Read Next.js output to find the port
        start_time = time.time()
        while time.time() - start_time < 30:  # 30 second timeout
            if nextjs_process.poll() is not None:
                print("❌ NextJS server failed to start")
                break
                
            line = nextjs_process.stdout.readline()
            if line:
                print(f"   {line.strip()}")
                if "Local:" in line and "http://localhost:" in line:
                    # Extract the URL from the line
                    import re
                    match = re.search(r'http://localhost:(\d+)', line)
                    if match:
                        port = match.group(1)
                        frontend_url = f"http://localhost:{port}"
                        break
                        
        if not frontend_url:
            frontend_url = "http://localhost:3000"  # fallback
            
        print("\n✅ Both servers started successfully!")
        print("\n📊 Dashboard URLs:")
        print(f"   - Frontend: {frontend_url}")
        print("   - API: http://localhost:8000")
        print("   - API Docs: http://localhost:8000/docs")
        print("\n🔄 Real-time updates via WebSocket: ws://localhost:8000/ws")
        print("\n💡 Press Ctrl+C to stop all servers")
        
        # Open Firefox with the correct URL
        time.sleep(2)
        print("\n🌐 Opening dashboard in Firefox...")
        try:
            # Set Firefox as the preferred browser and open the dashboard
            webbrowser.register('firefox', webbrowser.BackgroundBrowser('/usr/bin/firefox'))
            webbrowser.get('firefox').open(frontend_url)
            print(f"✅ Opened {frontend_url} in Firefox")
        except Exception as e:
            print(f"⚠️  Could not open Firefox automatically: {e}")
            print(f"   Please manually open {frontend_url} in your browser")
        
        # Wait for processes
        while True:
            time.sleep(1)
            # Check if any process has died
            for i, process in enumerate(processes):
                if process.poll() is not None:
                    print(f"❌ Process {i} has stopped unexpectedly")
                    return
                    
    except KeyboardInterrupt:
        print("\n🛑 Shutting down servers...")
        for process in processes:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
        print("✅ All servers stopped")
        
    except Exception as e:
        print(f"❌ Error starting servers: {e}")
        for process in processes:
            process.terminate()
        sys.exit(1)

if __name__ == "__main__":
    main()