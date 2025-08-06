#!/usr/bin/env python3
"""
Live agent server that connects WebPokerAgent to the dashboard.
Replaces the mock data with real agent statistics and controls.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import json
import sys
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from holdem.web.web_poker_agent import WebPokerAgent, AgentStatus, AgentStats, HandRecord

app = FastAPI(title="Live Holdem Agent API", version="2.0.0")

# Enable CORS for the NextJS frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Agent control models
class AgentControlRequest(BaseModel):
    action: str  # "start", "stop", "pause", "resume"
    site_url: Optional[str] = None
    headless: Optional[bool] = True

class AgentStatusResponse(BaseModel):
    status: str
    message: str
    uptime_seconds: float

class PerformancePoint(BaseModel):
    timestamp: str
    profit: float
    hands_played: int
    win_rate: float

# Global agent state
class LiveAgentState:
    def __init__(self):
        self.agent: Optional[WebPokerAgent] = None
        self.websocket_connections: List[WebSocket] = []
        self.performance_history: List[PerformancePoint] = []
        self.is_agent_running = False
        self.start_time = datetime.now()
        
    def register_websocket(self, websocket: WebSocket):
        """Register new WebSocket connection."""
        self.websocket_connections.append(websocket)
        
    def unregister_websocket(self, websocket: WebSocket):
        """Unregister WebSocket connection."""
        if websocket in self.websocket_connections:
            self.websocket_connections.remove(websocket)
    
    async def start_agent(self, site_url: str = None, headless: bool = True):
        """Start the poker agent."""
        if self.is_agent_running:
            return False, "Agent is already running"
        
        try:
            self.agent = WebPokerAgent()
            self.agent.register_dashboard_callback(self.agent_update_callback)
            
            # Start agent in background task - simplified, no token needed
            asyncio.create_task(self.agent.start(headless=headless, site_url=site_url))
            
            self.is_agent_running = True
            self.start_time = datetime.now()
            
            await self.broadcast_update()
            return True, "Agent started - Firefox will open for manual login"
            
        except Exception as e:
            return False, f"Failed to start agent: {e}"
    
    async def stop_agent(self):
        """Stop the poker agent."""
        if not self.is_agent_running or not self.agent:
            return False, "Agent is not running"
        
        try:
            await self.agent.stop()
            self.is_agent_running = False
            
            await self.broadcast_update()
            return True, "Agent stopped successfully"
            
        except Exception as e:
            return False, f"Failed to stop agent: {e}"
    
    def agent_update_callback(self, stats: AgentStats, hands: List[HandRecord]):
        """Callback for agent updates - triggers dashboard broadcast."""
        # Add performance point
        performance_point = PerformancePoint(
            timestamp=datetime.now().isoformat(),
            profit=stats.total_profit,
            hands_played=stats.total_hands,
            win_rate=stats.win_rate
        )
        
        self.performance_history.append(performance_point)
        
        # Keep last 144 points (24 hours at 10-minute intervals)
        if len(self.performance_history) > 144:
            self.performance_history.pop(0)
        
        # Broadcast to all connected clients
        asyncio.create_task(self.broadcast_update())
    
    async def broadcast_update(self):
        """Broadcast updates to all connected WebSocket clients."""
        if not self.websocket_connections:
            return
        
        # Get current data
        stats = self.get_current_stats()
        hands = self.get_recent_hands(10)
        performance = self.get_performance_data(4)  # Last 4 hours
        
        update_data = {
            "type": "stats_update",
            "data": {
                "stats": stats,
                "recent_hands": hands,
                "performance": performance
            }
        }
        
        # Send to all connected clients
        disconnected = []
        for websocket in self.websocket_connections:
            try:
                await websocket.send_text(json.dumps(update_data))
            except:
                disconnected.append(websocket)
        
        # Remove disconnected clients
        for ws in disconnected:
            self.unregister_websocket(ws)
    
    def get_current_stats(self) -> Dict[str, Any]:
        """Get current agent statistics."""
        if self.agent:
            return self.agent.get_stats()
        else:
            return {
                "total_hands": 0,
                "win_rate": 0.0,
                "total_profit": 0.0,
                "current_session": 0.0,
                "hourly_rate": 0.0,
                "active_tables": 0,
                "session_time": int((datetime.now() - self.start_time).total_seconds()),
                "last_updated": datetime.now().isoformat(),
                "status": "disconnected",
                "last_action": "Not started",
                "current_position": "",
                "current_cards": []
            }
    
    def get_recent_hands(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent hand history."""
        if self.agent:
            return self.agent.get_recent_hands(limit)
        else:
            return []
    
    def get_performance_data(self, hours: int = 4) -> List[Dict[str, Any]]:
        """Get performance data for specified hours."""
        points_needed = min(hours * 6, len(self.performance_history))  # 6 points per hour
        recent_points = self.performance_history[-points_needed:] if points_needed > 0 else []
        return [point.dict() for point in recent_points]

# Global state
live_agent_state = LiveAgentState()

# Background task for periodic updates
async def background_updater():
    """Background task for periodic dashboard updates."""
    while True:
        if live_agent_state.is_agent_running:
            await live_agent_state.broadcast_update()
        await asyncio.sleep(3)  # Update every 3 seconds

# Start background task
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(background_updater())

# HTTP Endpoints
@app.get("/api/stats")
async def get_stats():
    """Get current agent statistics."""
    return live_agent_state.get_current_stats()

@app.get("/api/hands")
async def get_recent_hands(limit: int = 20):
    """Get recent hand history."""
    return live_agent_state.get_recent_hands(limit)

@app.get("/api/performance")
async def get_performance_data(hours: int = 4):
    """Get performance data for the specified number of hours."""
    return live_agent_state.get_performance_data(hours)

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    agent_status = "running" if live_agent_state.is_agent_running else "stopped"
    return {
        "status": "healthy",
        "agent_status": agent_status,
        "timestamp": datetime.now().isoformat(),
        "active_connections": len(live_agent_state.websocket_connections),
        "uptime_seconds": (datetime.now() - live_agent_state.start_time).total_seconds()
    }

@app.post("/api/agent/control")
async def control_agent(request: AgentControlRequest):
    """Control agent (start/stop/pause/resume)."""
    if request.action == "start":
        success, message = await live_agent_state.start_agent(request.site_url, request.headless)
        status = "started" if success else "error"
    elif request.action == "stop":
        success, message = await live_agent_state.stop_agent()
        status = "stopped" if success else "error"
    else:
        success, message = False, f"Unknown action: {request.action}"
        status = "error"
    
    return AgentStatusResponse(
        status=status,
        message=message,
        uptime_seconds=(datetime.now() - live_agent_state.start_time).total_seconds()
    )

@app.get("/api/agent/status")
async def get_agent_status():
    """Get current agent status."""
    if live_agent_state.agent:
        agent_stats = live_agent_state.agent.get_stats()
        status = agent_stats.get("status", "unknown")
        last_action = agent_stats.get("last_action", "Unknown")
    else:
        status = "stopped"
        last_action = "Agent not initialized"
    
    return AgentStatusResponse(
        status=status,
        message=last_action,
        uptime_seconds=(datetime.now() - live_agent_state.start_time).total_seconds()
    )

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    await websocket.accept()
    live_agent_state.register_websocket(websocket)
    
    try:
        # Send initial data
        initial_data = {
            "type": "initial_data",
            "data": {
                "stats": live_agent_state.get_current_stats(),
                "recent_hands": live_agent_state.get_recent_hands(10),
                "performance": live_agent_state.get_performance_data(4)
            }
        }
        await websocket.send_text(json.dumps(initial_data))
        
        # Keep connection alive
        while True:
            try:
                message = await asyncio.wait_for(websocket.receive_text(), timeout=1.0)
                # Handle client messages if needed (like agent control commands)
                try:
                    data = json.loads(message)
                    if data.get("type") == "agent_control":
                        action = data.get("action")
                        if action == "start":
                            await live_agent_state.start_agent()
                        elif action == "stop":
                            await live_agent_state.stop_agent()
                except json.JSONDecodeError:
                    pass
            except asyncio.TimeoutError:
                # Send ping to keep connection alive
                await websocket.send_text(json.dumps({"type": "ping"}))
            
    except WebSocketDisconnect:
        live_agent_state.unregister_websocket(websocket)

if __name__ == "__main__":
    import uvicorn
    print("🎰 Starting Live Holdem Agent Server")
    print("=" * 50)
    print("🚀 API Server: http://localhost:8000")
    print("📊 Dashboard: http://localhost:3000") 
    print("📡 WebSocket: ws://localhost:8000/ws")
    print("🎮 Agent Control: POST /api/agent/control")
    print("=" * 50)
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")