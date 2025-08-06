#!/usr/bin/env python3
"""
Start script for the Live Holdem Agent Dashboard system.
This script starts the live agent API server and NextJS development server.
"""

import subprocess
import sys
import os
import time
import signal
from pathlib import Path

def start_live_api_server():
    """Start the live agent FastAPI server."""
    print("🚀 Starting Live Agent API server on port 8000...")
    cmd = ["python", "live_agent_server.py"]
    return subprocess.Popen(cmd, cwd="/home/envy/holdem")

def start_nextjs_server():
    """Start the NextJS development server."""
    print("🚀 Starting NextJS dashboard on port 3000...")
    cmd = ["npm", "run", "dev"]
    return subprocess.Popen(cmd, cwd="/home/envy/holdem/holdem-dashboard")

def main():
    print("🎰 Starting Live Holdem Agent Dashboard System")
    print("=" * 60)
    print("🤖 This version connects to REAL poker agents!")
    print("=" * 60)
    
    processes = []
    
    try:
        # Start Live Agent API server
        api_process = start_live_api_server()
        processes.append(api_process)
        time.sleep(3)  # Give API server time to start
        
        # Start NextJS server
        nextjs_process = start_nextjs_server()
        processes.append(nextjs_process)
        
        print("\n✅ Both servers started successfully!")
        print("\n📊 Dashboard URLs:")
        print("   - Frontend: http://localhost:3000")
        print("   - Live API: http://localhost:8000")
        print("   - API Docs: http://localhost:8000/docs")
        print("\n🔄 Real-time updates via WebSocket: ws://localhost:8000/ws")
        print("\n🎮 Agent Control Features:")
        print("   - Start/Stop poker agent")
        print("   - Real-time statistics")
        print("   - Live hand history")
        print("   - Browser automation settings")
        print("\n💡 Press Ctrl+C to stop all servers")
        print("\n🎯 Ready for GrandpaJoe42 to play poker!")
        
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