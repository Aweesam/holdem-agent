#!/usr/bin/env python3
"""
Real-time API server for holdem agent statistics.
Provides WebSocket and HTTP endpoints for the dashboard.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import json
import time
import random
from typing import List, Dict, Any
from datetime import datetime, timedelta

from holdem.utils.logging_config import setup_logger, setup_exception_logging

# Setup logging
logger = setup_logger(__name__, 'api')
setup_exception_logging(logger)

app = FastAPI(title="Holdem Agent API", version="1.0.0")

# Enable CORS for the NextJS frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class AgentStats(BaseModel):
    total_hands: int = 0
    win_rate: float = 0.0
    total_profit: float = 0.0
    current_session: float = 0.0
    hourly_rate: float = 0.0
    active_tables: int = 0
    session_time: int = 0
    last_updated: str

class HandHistory(BaseModel):
    id: int
    timestamp: str
    position: str
    hole_cards: str
    result: str
    profit: float
    hand_description: str
    table_id: str

class PerformancePoint(BaseModel):
    timestamp: str
    profit: float
    hands_played: int
    win_rate: float

# Global state
class AgentState:
    def __init__(self):
        self.stats = AgentStats(
            total_hands=1234,
            win_rate=65.8,
            total_profit=2450.0,
            current_session=245.0,
            hourly_rate=45.2,
            active_tables=3,
            session_time=7200,  # 2 hours
            last_updated=datetime.now().isoformat()
        )
        self.hand_history: List[HandHistory] = []
        self.performance_data: List[PerformancePoint] = []
        self.websocket_connections: List[WebSocket] = []
        self.session_start = datetime.now()
        
        # Generate initial performance data
        self._generate_initial_performance_data()
        self._generate_initial_hand_history()
    
    def _generate_initial_performance_data(self):
        """Generate 24 hours of mock performance data."""
        base_time = datetime.now() - timedelta(hours=24)
        cumulative_profit = 2000.0
        
        for i in range(144):  # 10-minute intervals
            timestamp = base_time + timedelta(minutes=i*10)
            profit_change = (random.random() - 0.4) * 20
            cumulative_profit += profit_change
            
            self.performance_data.append(PerformancePoint(
                timestamp=timestamp.isoformat(),
                profit=round(cumulative_profit, 2),
                hands_played=random.randint(5, 25),
                win_rate=random.uniform(60, 70)
            ))
    
    def _generate_initial_hand_history(self):
        """Generate initial hand history."""
        positions = ['BTN', 'SB', 'BB', 'UTG', 'MP', 'CO']
        hand_types = [
            'Royal Flush', 'Straight Flush', 'Four of a Kind', 'Full House',
            'Flush', 'Straight', 'Three of a Kind', 'Two Pair', 'Pair', 'High Card'
        ]
        
        for i in range(50):
            timestamp = datetime.now() - timedelta(minutes=i*2)
            profit = (random.random() - 0.4) * 100
            
            self.hand_history.append(HandHistory(
                id=i + 1,
                timestamp=timestamp.isoformat(),
                position=random.choice(positions),
                hole_cards=self._generate_hole_cards(),
                result='Won' if profit > 0 else 'Lost',
                profit=round(profit, 2),
                hand_description=random.choice(hand_types),
                table_id=f"Table {random.randint(1, 6)}"
            ))
    
    def _generate_hole_cards(self) -> str:
        """Generate random hole cards."""
        ranks = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2']
        suits = ['♠', '♥', '♦', '♣']
        
        card1 = f"{random.choice(ranks)}{random.choice(suits)}"
        card2 = f"{random.choice(ranks)}{random.choice(suits)}"
        
        return f"{card1} {card2}"
    
    async def update_stats(self):
        """Simulate real-time stats updates."""
        # Update basic stats
        self.stats.total_hands += random.randint(0, 3)
        profit_change = (random.random() - 0.4) * 15
        self.stats.total_profit += profit_change
        self.stats.current_session += profit_change * 0.5
        self.stats.win_rate += (random.random() - 0.5) * 0.5
        self.stats.win_rate = max(50.0, min(80.0, self.stats.win_rate))
        
        # Update session time
        session_duration = datetime.now() - self.session_start
        self.stats.session_time = int(session_duration.total_seconds())
        
        # Calculate hourly rate
        if self.stats.session_time > 0:
            self.stats.hourly_rate = (self.stats.current_session / self.stats.session_time) * 3600
        
        self.stats.last_updated = datetime.now().isoformat()
        
        # Add new performance point
        if len(self.performance_data) >= 144:
            self.performance_data.pop(0)
        
        self.performance_data.append(PerformancePoint(
            timestamp=datetime.now().isoformat(),
            profit=self.stats.total_profit,
            hands_played=random.randint(5, 25),
            win_rate=self.stats.win_rate
        ))
        
        # Occasionally add new hand
        if random.random() < 0.3:
            await self.add_new_hand()
    
    async def add_new_hand(self):
        """Add a new hand to history."""
        positions = ['BTN', 'SB', 'BB', 'UTG', 'MP', 'CO']
        hand_types = [
            'Royal Flush', 'Straight Flush', 'Four of a Kind', 'Full House',
            'Flush', 'Straight', 'Three of a Kind', 'Two Pair', 'Pair', 'High Card'
        ]
        
        profit = (random.random() - 0.4) * 100
        
        new_hand = HandHistory(
            id=len(self.hand_history) + 1,
            timestamp=datetime.now().isoformat(),
            position=random.choice(positions),
            hole_cards=self._generate_hole_cards(),
            result='Won' if profit > 0 else 'Lost',
            profit=round(profit, 2),
            hand_description=random.choice(hand_types),
            table_id=f"Table {random.randint(1, 6)}"
        )
        
        self.hand_history.insert(0, new_hand)
        
        # Keep only last 50 hands
        if len(self.hand_history) > 50:
            self.hand_history.pop()
    
    async def broadcast_update(self):
        """Broadcast updates to all connected WebSocket clients."""
        if not self.websocket_connections:
            return
        
        update_data = {
            "type": "stats_update",
            "data": {
                "stats": self.stats.dict(),
                "recent_hands": [hand.dict() for hand in self.hand_history[:10]],
                "performance": [point.dict() for point in self.performance_data[-24:]]  # Last 4 hours
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
            self.websocket_connections.remove(ws)

# Global agent state
agent_state = AgentState()

# Background task to update stats
async def background_stats_updater():
    """Background task to update stats and broadcast to clients."""
    while True:
        await agent_state.update_stats()
        await agent_state.broadcast_update()
        await asyncio.sleep(3)  # Update every 3 seconds

# Start background task
@app.on_event("startup")
async def startup_event():
    logger.info("Starting Holdem Agent API server")
    logger.info(f"Log level: {logger.level}")
    asyncio.create_task(background_stats_updater())
    logger.info("Background stats updater started")

# HTTP Endpoints
@app.get("/api/stats")
async def get_stats():
    """Get current agent statistics."""
    return agent_state.stats

@app.get("/api/hands")
async def get_recent_hands(limit: int = 20):
    """Get recent hand history."""
    return agent_state.hand_history[:limit]

@app.get("/api/performance")
async def get_performance_data(hours: int = 4):
    """Get performance data for the specified number of hours."""
    points_needed = hours * 6  # 6 points per hour (10-minute intervals)
    return agent_state.performance_data[-points_needed:]

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_connections": len(agent_state.websocket_connections),
        "uptime_seconds": (datetime.now() - agent_state.session_start).total_seconds()
    }

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    await websocket.accept()
    agent_state.websocket_connections.append(websocket)
    client_addr = websocket.client.host if websocket.client else "unknown"
    logger.info(f"WebSocket client connected from {client_addr}. Total connections: {len(agent_state.websocket_connections)}")
    
    try:
        # Send initial data
        initial_data = {
            "type": "initial_data",
            "data": {
                "stats": agent_state.stats.dict(),
                "recent_hands": [hand.dict() for hand in agent_state.hand_history[:10]],
                "performance": [point.dict() for point in agent_state.performance_data[-24:]]
            }
        }
        await websocket.send_text(json.dumps(initial_data))
        logger.debug(f"Sent initial data to client {client_addr}")
        
        # Keep connection alive
        while True:
            # Wait for client messages (optional)
            try:
                message = await asyncio.wait_for(websocket.receive_text(), timeout=1.0)
                logger.debug(f"Received message from {client_addr}: {message}")
            except asyncio.TimeoutError:
                # Send ping to keep connection alive
                await websocket.send_text(json.dumps({"type": "ping"}))
            
    except WebSocketDisconnect:
        agent_state.websocket_connections.remove(websocket)
        logger.info(f"WebSocket client {client_addr} disconnected. Remaining connections: {len(agent_state.websocket_connections)}")
    except Exception as e:
        logger.error(f"WebSocket error with client {client_addr}: {e}")
        if websocket in agent_state.websocket_connections:
            agent_state.websocket_connections.remove(websocket)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv('HOLDEM_API_PORT', 8000))
    logger.info(f"Starting API server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="warning")  # Set uvicorn to warning to avoid duplicate logs