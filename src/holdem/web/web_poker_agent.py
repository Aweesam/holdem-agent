"""
Web-based poker agent that integrates browser automation, 
network monitoring, and poker decision-making with live dashboard reporting.
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum

from ..agents.base_agent import BaseAgent
from ..game import GameState, Action, ActionType
from .browser_manager import BrowserManager
from .human_behavior import HumanBehaviorSimulator
from .network_interceptor import ClubWPTNetworkInterceptor, GameStateParser, GameStateMessage
from .token_manager import ClubWPTTokenManager, TokenExtractor


class AgentStatus(Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    PLAYING = "playing"
    PAUSED = "paused"
    ERROR = "error"


@dataclass
class AgentStats:
    """Real-time agent statistics for dashboard reporting."""
    total_hands: int = 0
    win_rate: float = 0.0
    total_profit: float = 0.0
    current_session_profit: float = 0.0
    hourly_rate: float = 0.0
    active_tables: int = 0
    session_time: int = 0
    last_updated: str = ""
    status: AgentStatus = AgentStatus.DISCONNECTED
    last_action: str = ""
    current_position: str = ""
    current_cards: List[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "total_hands": self.total_hands,
            "win_rate": self.win_rate,
            "total_profit": self.total_profit,
            "current_session": self.current_session_profit,
            "hourly_rate": self.hourly_rate,
            "active_tables": self.active_tables,
            "session_time": self.session_time,
            "last_updated": self.last_updated,
            "status": self.status.value,
            "last_action": self.last_action,
            "current_position": self.current_position,
            "current_cards": self.current_cards or []
        }


@dataclass 
class HandRecord:
    """Record of a completed poker hand."""
    id: int
    timestamp: str
    position: str
    hole_cards: List[str]
    result: str  # "Won" or "Lost"
    profit: float
    hand_description: str
    table_id: str
    final_board: List[str] = None
    pot_size: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "position": self.position,
            "hole_cards": " ".join(self.hole_cards),
            "result": self.result,
            "profit": self.profit,
            "hand_description": self.hand_description,
            "table_id": self.table_id,
            "final_board": self.final_board or [],
            "pot_size": self.pot_size
        }


class WebPokerAgent(BaseAgent):
    """
    Complete web-based poker agent that combines:
    - Browser automation for UI interaction
    - Network monitoring for game state
    - Poker decision engine
    - Live dashboard reporting
    """
    
    def __init__(self, player_id: str = "449469", name: str = "GrandpaJoe42"):
        super().__init__(player_id, name)
        
        # Core components
        self.browser_manager: Optional[BrowserManager] = None
        self.network_interceptor: Optional[ClubWPTNetworkInterceptor] = None
        self.game_parser = GameStateParser()
        self.behavior_sim = HumanBehaviorSimulator()
        self.token_manager = ClubWPTTokenManager()
        
        # Statistics and reporting
        self.stats = AgentStats()
        self.hand_records: List[HandRecord] = []
        self.session_start_time = datetime.now()
        self.dashboard_callbacks: List[Callable] = []
        
        # Game state tracking
        self.current_game_state: Dict[str, Any] = {}
        self.is_running = False
        self.hand_count = 0
        
        # Performance tracking
        self.session_hands = 0
        self.session_profit = 0.0
        self.wins = 0
        
    def register_dashboard_callback(self, callback: Callable):
        """Register callback for dashboard updates."""
        self.dashboard_callbacks.append(callback)
    
    async def start(self, headless: bool = False, site_url: str = None, token: str = None):
        """Start the web poker agent."""
        try:
            self.stats.status = AgentStatus.CONNECTING
            self.stats.last_action = "Initializing Firefox browser..."
            self._notify_dashboard()
            
            # Initialize Firefox browser (works better with Club WPT Gold)
            self.browser_manager = BrowserManager(headless=headless, browser_type="firefox")
            
            # Handle token and URL
            game_url = await self._prepare_game_url(site_url, token)
            if not game_url:
                self.stats.status = AgentStatus.ERROR
                self.stats.last_action = "Failed to get valid game URL with token"
                self._notify_dashboard()
                return
            
            # Initialize network interceptor
            self.network_interceptor = ClubWPTNetworkInterceptor(int(self.player_id))
            self.network_interceptor.set_game_state_callback(self._handle_network_message)
            
            # Navigate to poker site
            self.stats.last_action = f"Navigating to {game_url[:50]}..."
            self._notify_dashboard()
            
            if await self._navigate_to_site(game_url):
                self.stats.status = AgentStatus.CONNECTED
                self.stats.active_tables = 1
                self.stats.last_action = "Connected to Club WPT Gold"
                self._notify_dashboard()
                
                # Start network monitoring
                asyncio.create_task(self._start_network_monitoring())
                
                # Start main game loop
                self.is_running = True
                await self._main_game_loop()
            else:
                self.stats.status = AgentStatus.ERROR
                self.stats.last_action = "Failed to navigate to poker site"
                self._notify_dashboard()
                
        except Exception as e:
            self.stats.status = AgentStatus.ERROR
            self.stats.last_action = f"Agent start error: {e}"
            print(f"Agent start error: {e}")
            self._notify_dashboard()
    
    async def _prepare_game_url(self, site_url: str = None, token: str = None) -> Optional[str]:
        """Prepare the complete game URL with token."""
        try:
            if token:
                # Token provided directly
                if self.token_manager.set_token(token):
                    return self.token_manager.get_game_url()
            
            if site_url and "token=" in site_url:
                # URL with token provided
                extracted_token = self.token_manager.extract_token_from_url(site_url)
                if extracted_token:
                    return site_url
            
            # No valid token - need to get one interactively
            print("🔐 No valid token provided. Starting manual login process...")
            
            # Navigate to login page first
            self.browser_manager.navigate_to_game("https://clubwptgold.com/login")
            
            # Wait for user to log in and get to game page
            token = TokenExtractor.wait_for_login_and_extract(self.browser_manager, timeout=300)
            
            if token:
                self.token_manager.set_token(token)
                return self.token_manager.get_game_url()
            
            return None
            
        except Exception as e:
            print(f"Error preparing game URL: {e}")
            return None
    
    async def _navigate_to_site(self, url: str) -> bool:
        """Navigate to poker site with human-like behavior."""
        try:
            return self.browser_manager.navigate_to_game(url)
        except Exception as e:
            print(f"Navigation failed: {e}")
            return False
    
    async def _start_network_monitoring(self):
        """Start monitoring network traffic."""
        try:
            await self.network_interceptor.connect()
        except Exception as e:
            print(f"Network monitoring failed: {e}")
            # Continue without network monitoring - rely on browser only
    
    async def _main_game_loop(self):
        """Main game loop for poker agent."""
        while self.is_running:
            try:
                # Update session time
                self._update_session_time()
                
                # Check if it's our turn to act
                if self._is_action_required():
                    await self._make_decision()
                
                # Take occasional human-like breaks
                if self.behavior_sim.should_take_break():
                    await self._take_break()
                
                # Update dashboard every few seconds
                self._notify_dashboard()
                
                # Brief pause before next iteration
                await asyncio.sleep(0.5)
                
            except Exception as e:
                print(f"Game loop error: {e}")
                await asyncio.sleep(1)
    
    async def _handle_network_message(self, message: GameStateMessage):
        """Handle incoming network messages and update game state."""
        try:
            # Parse message and update game state
            self.current_game_state = self.game_parser.parse_message(message)
            
            # Handle specific message types
            if message.message_type == "deal_cards":
                await self._handle_new_hand(message.data)
            elif message.message_type == "hand_result":
                await self._handle_hand_complete(message.data)
            elif message.message_type == "betting_action":
                await self._handle_betting_round(message.data)
            
            # Update status
            if self.current_game_state:
                self.stats.status = AgentStatus.PLAYING
                self.stats.last_updated = datetime.now().isoformat()
                
        except Exception as e:
            print(f"Network message handling error: {e}")
    
    async def _handle_new_hand(self, data: Dict[str, Any]):
        """Handle start of new poker hand."""
        self.hand_count += 1
        self.session_hands += 1
        self.stats.total_hands += 1
        
        # Extract hole cards if available
        if "hole_cards" in data:
            self.stats.current_cards = data["hole_cards"]
        
        # Extract position
        if "position" in data:
            self.stats.current_position = data["position"]
        
        self.stats.last_action = "New hand started"
    
    async def _handle_hand_complete(self, data: Dict[str, Any]):
        """Handle completion of poker hand."""
        # Calculate hand result
        profit = data.get("profit", 0)
        won = profit > 0
        
        if won:
            self.wins += 1
        
        # Update statistics
        self.session_profit += profit
        self.stats.total_profit += profit
        self.stats.current_session_profit += profit
        self.stats.win_rate = (self.wins / max(self.stats.total_hands, 1)) * 100
        
        # Create hand record
        hand_record = HandRecord(
            id=self.hand_count,
            timestamp=datetime.now().isoformat(),
            position=self.stats.current_position,
            hole_cards=self.stats.current_cards or [],
            result="Won" if won else "Lost",
            profit=profit,
            hand_description=data.get("hand_type", "Unknown"),
            table_id=data.get("table_id", "Table 1"),
            final_board=data.get("board", []),
            pot_size=data.get("pot_size", 0)
        )
        
        self.hand_records.insert(0, hand_record)
        
        # Keep only last 100 hands
        if len(self.hand_records) > 100:
            self.hand_records = self.hand_records[:100]
        
        self.stats.last_action = f"Hand completed: {hand_record.result} ${profit:+.2f}"
    
    async def _handle_betting_round(self, data: Dict[str, Any]):
        """Handle betting round information."""
        if "current_player" in data and data["current_player"] == int(self.player_id):
            # It's our turn to act
            self.stats.last_action = "Deciding action..."
    
    def _is_action_required(self) -> bool:
        """Check if agent needs to take action."""
        current_player = self.current_game_state.get("current_player")
        return current_player == int(self.player_id)
    
    async def _make_decision(self):
        """Make a poker decision and execute it."""
        try:
            # Simulate human thinking time
            complexity = self._assess_decision_complexity()
            self.behavior_sim.wait_decision_time(complexity)
            
            # Make decision based on current game state
            action = self._decide_action()
            
            # Execute action via browser
            if await self._execute_action(action):
                self.stats.last_action = f"Action: {action.action_type.value}"
                if hasattr(action, 'amount') and action.amount:
                    self.stats.last_action += f" ${action.amount}"
            
        except Exception as e:
            print(f"Decision making error: {e}")
            self.stats.last_action = "Decision error"
    
    def _assess_decision_complexity(self) -> str:
        """Assess complexity of current decision for timing."""
        pot = self.current_game_state.get("pot", 0)
        actions = self.current_game_state.get("available_actions", [])
        
        if pot > 1000 or len(actions) > 3:
            return "complex"
        elif pot < 100:
            return "simple"
        else:
            return "normal"
    
    def _decide_action(self) -> Action:
        """Decide what action to take (simplified logic for now)."""
        # TODO: Integrate with sophisticated poker strategy
        # For now, implement basic random strategy
        
        available_actions = self.current_game_state.get("available_actions", [])
        
        if "fold" in available_actions:
            # Simple strategy: fold 60% of hands
            if len(available_actions) > 1 and hash(str(self.stats.current_cards)) % 10 < 6:
                return Action(self.player_id, ActionType.FOLD)
        
        if "call" in available_actions:
            return Action(self.player_id, ActionType.CALL)
        elif "check" in available_actions:
            return Action(self.player_id, ActionType.CHECK)
        else:
            return Action(self.player_id, ActionType.FOLD)
    
    async def _execute_action(self, action: Action) -> bool:
        """Execute action via browser automation."""
        try:
            if not self.browser_manager:
                return False
            
            # Map action to browser clicks (canvas-based)
            # This would need to be implemented with precise coordinates
            # For now, just log the action
            print(f"Would execute: {action.action_type.value}")
            
            # TODO: Implement actual canvas clicking based on action type
            # await self._click_action_button(action.action_type)
            
            return True
            
        except Exception as e:
            print(f"Action execution error: {e}")
            return False
    
    async def _take_break(self):
        """Take a human-like break."""
        duration = self.behavior_sim.get_break_duration()
        self.stats.status = AgentStatus.PAUSED
        self.stats.last_action = f"Taking break ({duration:.0f}s)"
        self._notify_dashboard()
        
        await asyncio.sleep(duration)
        
        self.stats.status = AgentStatus.PLAYING
        self.stats.last_action = "Back from break"
    
    def _update_session_time(self):
        """Update session time and hourly rate."""
        session_duration = datetime.now() - self.session_start_time
        self.stats.session_time = int(session_duration.total_seconds())
        
        if self.stats.session_time > 0:
            self.stats.hourly_rate = (self.stats.current_session_profit / self.stats.session_time) * 3600
    
    def _notify_dashboard(self):
        """Notify all registered dashboard callbacks."""
        for callback in self.dashboard_callbacks:
            try:
                callback(self.stats, self.hand_records)
            except Exception as e:
                print(f"Dashboard callback error: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current statistics for dashboard."""
        return self.stats.to_dict()
    
    def get_recent_hands(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent hand records for dashboard."""
        return [hand.to_dict() for hand in self.hand_records[:limit]]
    
    async def stop(self):
        """Stop the poker agent."""
        self.is_running = False
        self.stats.status = AgentStatus.DISCONNECTED
        self.stats.active_tables = 0
        
        if self.browser_manager:
            self.browser_manager.close()
        
        if self.network_interceptor and self.network_interceptor.is_connected:
            await self.network_interceptor.disconnect()
        
        self._notify_dashboard()
    
    # Implement BaseAgent abstract method
    def decide_action(self, game_state: GameState) -> Action:
        """Implement BaseAgent interface (called by internal game engine)."""
        return self._decide_action()


# Example usage
if __name__ == "__main__":
    async def test_agent():
        agent = WebPokerAgent()
        
        # Register dashboard callback
        def dashboard_update(stats: AgentStats, hands: List[HandRecord]):
            print(f"Stats Update: {stats.status.value} - Hands: {stats.total_hands} - Profit: ${stats.total_profit:.2f}")
        
        agent.register_dashboard_callback(dashboard_update)
        
        # Start agent (this would normally connect to real site)
        try:
            await agent.start(headless=True)
        except KeyboardInterrupt:
            await agent.stop()
    
    asyncio.run(test_agent())