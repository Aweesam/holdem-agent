"""
Network traffic interceptor for Club WPT Gold poker site.
Monitors WebSocket and HTTP communications to extract game state.
"""

import json
import asyncio
import websockets
import logging
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class GameStateMessage:
    """Represents a parsed game state message."""
    message_type: str
    timestamp: datetime
    data: Dict[str, Any]
    raw_data: str


class ClubWPTNetworkInterceptor:
    """Intercepts and parses Club WPT Gold network communications."""
    
    # Known endpoints from HAR analysis
    WEBSOCKET_URL = "wss://gate.clubwptgold.com/"
    API_BASE = "https://apigate.clubwptgold.com/authserver"
    USER_ID = 449469  # GrandpaJoe42
    
    def __init__(self, user_id: int = USER_ID):
        self.user_id = user_id
        self.websocket = None
        self.is_connected = False
        self.message_handlers: Dict[str, Callable] = {}
        self.game_state_callback: Optional[Callable] = None
        
    def register_handler(self, message_type: str, handler: Callable):
        """Register a handler for specific message types."""
        self.message_handlers[message_type] = handler
        logger.info(f"Registered handler for message type: {message_type}")
    
    def set_game_state_callback(self, callback: Callable):
        """Set callback for game state updates."""
        self.game_state_callback = callback
        
    async def connect(self, auth_token: str = None):
        """Connect to Club WPT Gold WebSocket gateway."""
        try:
            logger.info(f"Connecting to {self.WEBSOCKET_URL}")
            
            # Add authentication headers if available
            extra_headers = {}
            if auth_token:
                extra_headers["Authorization"] = f"Bearer {auth_token}"
            
            self.websocket = await websockets.connect(
                self.WEBSOCKET_URL,
                extra_headers=extra_headers,
                ping_interval=30,
                ping_timeout=10
            )
            
            self.is_connected = True
            logger.info("WebSocket connected successfully")
            
            # Start message processing loop
            await self._message_loop()
            
        except Exception as e:
            logger.error(f"WebSocket connection failed: {e}")
            self.is_connected = False
            raise
    
    async def _message_loop(self):
        """Main message processing loop."""
        try:
            async for message in self.websocket:
                await self._process_message(message)
        except websockets.exceptions.ConnectionClosed:
            logger.info("WebSocket connection closed")
            self.is_connected = False
        except Exception as e:
            logger.error(f"Message loop error: {e}")
            self.is_connected = False
    
    async def _process_message(self, raw_message: str):
        """Process incoming WebSocket message."""
        try:
            timestamp = datetime.now()
            logger.debug(f"Received message: {raw_message[:200]}...")
            
            # Try to parse as JSON
            try:
                data = json.loads(raw_message)
                message_type = self._identify_message_type(data)
            except json.JSONDecodeError:
                # Handle binary or non-JSON messages
                message_type = "binary"
                data = {"raw": raw_message}
            
            # Create structured message
            game_message = GameStateMessage(
                message_type=message_type,
                timestamp=timestamp,
                data=data,
                raw_data=raw_message
            )
            
            # Route to specific handler
            if message_type in self.message_handlers:
                await self.message_handlers[message_type](game_message)
            
            # Always call general game state callback if set
            if self.game_state_callback:
                await self.game_state_callback(game_message)
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    def _identify_message_type(self, data: Dict[str, Any]) -> str:
        """Identify the type of message based on content."""
        # Common poker game message patterns
        if "action" in data:
            return "player_action"
        elif "cards" in data or "hole_cards" in data:
            return "deal_cards"
        elif "pot" in data:
            return "pot_update"
        elif "board" in data or "community_cards" in data:
            return "board_update"
        elif "blinds" in data:
            return "blinds_update"
        elif "winner" in data or "showdown" in data:
            return "hand_result"
        elif "seat" in data or "player" in data:
            return "player_update"
        elif "bet" in data or "raise" in data or "call" in data or "fold" in data:
            return "betting_action"
        elif "game_state" in data:
            return "game_state"
        else:
            return "unknown"
    
    async def send_action(self, action_data: Dict[str, Any]):
        """Send action to the poker server."""
        if not self.is_connected or not self.websocket:
            raise ConnectionError("WebSocket not connected")
        
        try:
            message = json.dumps(action_data)
            await self.websocket.send(message)
            logger.info(f"Sent action: {action_data}")
        except Exception as e:
            logger.error(f"Failed to send action: {e}")
            raise
    
    async def disconnect(self):
        """Close WebSocket connection."""
        if self.websocket:
            await self.websocket.close()
            self.is_connected = False
            logger.info("WebSocket disconnected")


class GameStateParser:
    """Parses Club WPT Gold game messages into standardized format."""
    
    def __init__(self):
        self.current_game_state = {
            "pot": 0,
            "community_cards": [],
            "players": {},
            "current_player": None,
            "betting_round": "preflop",
            "small_blind": 0,
            "big_blind": 0,
            "my_cards": [],
            "my_position": None,
            "available_actions": []
        }
    
    def parse_message(self, message: GameStateMessage) -> Dict[str, Any]:
        """Parse a game message and update internal state."""
        if message.message_type == "deal_cards":
            return self._parse_deal_cards(message.data)
        elif message.message_type == "betting_action":
            return self._parse_betting_action(message.data)
        elif message.message_type == "pot_update":
            return self._parse_pot_update(message.data)
        elif message.message_type == "board_update":
            return self._parse_board_update(message.data)
        else:
            return self._parse_generic(message.data)
    
    def _parse_deal_cards(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse card dealing messages."""
        # Extract hole cards if present
        if "hole_cards" in data:
            self.current_game_state["my_cards"] = data["hole_cards"]
        
        return self.current_game_state
    
    def _parse_betting_action(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse betting action messages."""
        # Update current player and available actions
        if "current_player" in data:
            self.current_game_state["current_player"] = data["current_player"]
        
        if "actions" in data:
            self.current_game_state["available_actions"] = data["actions"]
        
        return self.current_game_state
    
    def _parse_pot_update(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse pot size updates."""
        if "pot" in data:
            self.current_game_state["pot"] = data["pot"]
        
        return self.current_game_state
    
    def _parse_board_update(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse community card updates."""
        if "board" in data:
            self.current_game_state["community_cards"] = data["board"]
        elif "community_cards" in data:
            self.current_game_state["community_cards"] = data["community_cards"]
        
        return self.current_game_state
    
    def _parse_generic(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse any other message types."""
        # Update any matching fields in current state
        for key in ["pot", "players", "blinds"]:
            if key in data:
                self.current_game_state[key] = data[key]
        
        return self.current_game_state
    
    def get_current_state(self) -> Dict[str, Any]:
        """Get current parsed game state."""
        return self.current_game_state.copy()


# Example usage and testing
if __name__ == "__main__":
    async def test_connection():
        """Test WebSocket connection to Club WPT Gold."""
        interceptor = ClubWPTNetworkInterceptor()
        parser = GameStateParser()
        
        # Register message handler
        async def handle_game_message(message: GameStateMessage):
            print(f"Message Type: {message.message_type}")
            print(f"Data: {message.data}")
            
            # Parse and update game state
            game_state = parser.parse_message(message)
            print(f"Current Game State: {game_state}")
            print("-" * 50)
        
        interceptor.set_game_state_callback(handle_game_message)
        
        try:
            await interceptor.connect()
        except Exception as e:
            print(f"Connection test failed: {e}")
            print("This is expected without proper authentication")
    
    # Run test
    asyncio.run(test_connection())