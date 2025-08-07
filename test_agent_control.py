#!/usr/bin/env python3
"""
Test script to demonstrate agent control and monitoring capabilities.
"""

import requests
import json
import time

API_BASE = "http://localhost:8000"

def print_stats():
    """Print current agent statistics."""
    try:
        response = requests.get(f"{API_BASE}/api/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"📊 AGENT STATS:")
            print(f"   Status: {stats['status']}")
            print(f"   Last Action: {stats['last_action']}")
            print(f"   Total Hands: {stats['total_hands']}")
            print(f"   Win Rate: {stats['win_rate']:.1%}")
            print(f"   Total Profit: ${stats['total_profit']:.2f}")
            print(f"   Session Time: {stats['session_time']}s")
            print(f"   Active Tables: {stats['active_tables']}")
            print()
        else:
            print(f"❌ Failed to get stats: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting stats: {e}")

def control_agent(action, site_url=None, headless=True):
    """Send control command to agent."""
    payload = {
        "action": action,
        "site_url": site_url,
        "headless": headless
    }
    
    try:
        response = requests.post(f"{API_BASE}/api/agent/control", 
                               json=payload,
                               headers={"Content-Type": "application/json"})
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Agent {action}: {result['message']}")
            return True
        else:
            print(f"❌ Failed to {action} agent: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error controlling agent: {e}")
        return False

def main():
    print("=== AGENT CONTROL DEMO ===\\n")
    
    # Check system health
    try:
        response = requests.get(f"{API_BASE}/api/health")
        if response.status_code == 200:
            health = response.json()
            print(f"🏥 SYSTEM HEALTH:")
            print(f"   Status: {health['status']}")
            print(f"   Agent Status: {health['agent_status']}")
            print(f"   Uptime: {health['uptime_seconds']:.0f}s")
            print(f"   Active Connections: {health['active_connections']}")
            print()
        else:
            print(f"❌ System unhealthy: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Cannot connect to API server: {e}")
        print("Make sure to run: python start_live_dashboard.py")
        return
    
    # Show initial stats
    print_stats()
    
    # Demonstrate agent control
    print("🎮 DEMONSTRATING AGENT CONTROL\\n")
    
    print("1. Attempting to start agent (will fail gracefully - no browser)...")
    if control_agent("start", site_url="https://clubwptgold.com/", headless=True):
        print("   Agent start initiated!")
        
        # Wait a moment for status to update
        print("   Waiting for status update...")
        time.sleep(2)
        
        # Check stats again
        print_stats()
        
        print("2. Attempting to stop agent...")
        if control_agent("stop"):
            print("   Agent stop initiated!")
            
            # Wait a moment
            time.sleep(1)
            print_stats()
    
    print("🔍 CHECKING AVAILABLE DATA\\n")
    
    # Check hand history
    try:
        response = requests.get(f"{API_BASE}/api/hands?limit=5")
        if response.status_code == 200:
            hands = response.json()
            print(f"📋 RECENT HANDS: {len(hands)} hands")
            if hands:
                for hand in hands[:3]:  # Show first 3
                    print(f"   Hand {hand['id']}: {hand['result']} - ${hand['profit']:.2f}")
            else:
                print("   No hands played yet")
            print()
    except Exception as e:
        print(f"❌ Error getting hands: {e}")
    
    # Check performance data
    try:
        response = requests.get(f"{API_BASE}/api/performance?hours=1")
        if response.status_code == 200:
            performance = response.json()
            print(f"📈 PERFORMANCE DATA: {len(performance)} data points")
            if performance:
                latest = performance[-1]
                print(f"   Latest: ${latest['profit']:.2f} profit, {latest['hands_played']} hands")
            else:
                print("   No performance data yet")
            print()
    except Exception as e:
        print(f"❌ Error getting performance: {e}")
    
    print("=== DEMO COMPLETE ===\\n")
    print("🌐 Dashboard Access:")
    print(f"   API Server: {API_BASE}")
    print(f"   React Dashboard: http://localhost:3000")
    print(f"   API Docs: {API_BASE}/docs")
    print("\\n🎯 Next Steps:")
    print("   1. Open http://localhost:3000 in your browser")
    print("   2. Use the dashboard to control agents")
    print("   3. Watch real-time updates via WebSocket")
    print("   4. Monitor agent performance and statistics")

if __name__ == "__main__":
    main()