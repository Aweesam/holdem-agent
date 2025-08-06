#!/usr/bin/env python3
"""
Demo script for monitoring Club WPT Gold network traffic.
This script shows how to intercept and analyze game communications.
"""

import asyncio
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from holdem.web.network_interceptor import ClubWPTNetworkInterceptor, GameStateParser, GameStateMessage


class PokerNetworkMonitor:
    """Monitors Club WPT Gold network traffic for game state."""
    
    def __init__(self):
        self.interceptor = ClubWPTNetworkInterceptor()
        self.parser = GameStateParser()
        self.message_count = 0
    
    async def start_monitoring(self):
        """Start monitoring network traffic."""
        print("🎰 Club WPT Gold Network Monitor")
        print("=" * 50)
        print(f"Target WebSocket: {self.interceptor.WEBSOCKET_URL}")
        print(f"Monitoring for User ID: {self.interceptor.user_id} (GrandpaJoe42)")
        print("=" * 50)
        
        # Register handlers for different message types
        self.interceptor.register_handler("player_action", self.handle_player_action)
        self.interceptor.register_handler("deal_cards", self.handle_deal_cards)
        self.interceptor.register_handler("betting_action", self.handle_betting_action)
        self.interceptor.register_handler("pot_update", self.handle_pot_update)
        self.interceptor.register_handler("board_update", self.handle_board_update)
        self.interceptor.register_handler("hand_result", self.handle_hand_result)
        
        # Set general message callback
        self.interceptor.set_game_state_callback(self.handle_any_message)
        
        try:
            print("🔌 Attempting to connect to WebSocket...")
            await self.interceptor.connect()
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            print("\nℹ️  This is expected without proper authentication.")
            print("To get real data, we need to:")
            print("1. Extract authentication token from browser session")
            print("2. Use authenticated WebSocket connection")
            print("3. Or implement browser-based monitoring")
    
    async def handle_any_message(self, message: GameStateMessage):
        """Handle any incoming message."""
        self.message_count += 1
        print(f"\n📨 Message #{self.message_count} [{message.message_type}]")
        print(f"⏰ Time: {message.timestamp.strftime('%H:%M:%S.%f')[:-3]}")
        
        # Show first 200 characters of raw data
        preview = message.raw_data[:200]
        if len(message.raw_data) > 200:
            preview += "..."
        print(f"📄 Data: {preview}")
        
        # Parse and show game state if relevant
        if message.message_type in ["deal_cards", "betting_action", "pot_update", "board_update"]:
            game_state = self.parser.parse_message(message)
            self.show_game_state(game_state)
    
    async def handle_player_action(self, message: GameStateMessage):
        """Handle player action messages."""
        print(f"🎮 Player Action: {message.data}")
    
    async def handle_deal_cards(self, message: GameStateMessage):
        """Handle card dealing messages."""
        print(f"🃏 Cards Dealt: {message.data}")
    
    async def handle_betting_action(self, message: GameStateMessage):
        """Handle betting action messages."""
        print(f"💰 Betting Action: {message.data}")
    
    async def handle_pot_update(self, message: GameStateMessage):
        """Handle pot update messages."""
        print(f"🎯 Pot Update: {message.data}")
    
    async def handle_board_update(self, message: GameStateMessage):
        """Handle community card updates."""
        print(f"🎴 Board Update: {message.data}")
    
    async def handle_hand_result(self, message: GameStateMessage):
        """Handle hand result messages."""
        print(f"🏆 Hand Result: {message.data}")
    
    def show_game_state(self, game_state):
        """Display current game state in readable format."""
        print("┌─ GAME STATE ─────────────────────────────────┐")
        print(f"│ Pot: ${game_state.get('pot', 0):,}")
        print(f"│ My Cards: {game_state.get('my_cards', 'Unknown')}")
        print(f"│ Board: {game_state.get('community_cards', [])}")
        print(f"│ Current Player: {game_state.get('current_player', 'Unknown')}")
        print(f"│ Round: {game_state.get('betting_round', 'Unknown')}")
        print(f"│ Available Actions: {game_state.get('available_actions', [])}")
        print("└──────────────────────────────────────────────┘")


async def main():
    """Main demo function."""
    monitor = PokerNetworkMonitor()
    
    try:
        await monitor.start_monitoring()
    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped by user")
    except Exception as e:
        print(f"❌ Monitor error: {e}")
    finally:
        if monitor.interceptor.is_connected:
            await monitor.interceptor.disconnect()


def test_message_parsing():
    """Test message parsing with sample data."""
    print("\n🧪 Testing Message Parsing")
    print("=" * 30)
    
    parser = GameStateParser()
    
    # Test sample messages (based on common poker protocols)
    test_messages = [
        {
            "type": "deal_cards",
            "data": {"hole_cards": ["As", "Kd"], "player_id": 449469}
        },
        {
            "type": "pot_update", 
            "data": {"pot": 150, "side_pots": []}
        },
        {
            "type": "board_update",
            "data": {"community_cards": ["Jh", "Tc", "9s"]}
        },
        {
            "type": "betting_action",
            "data": {"current_player": 449469, "actions": ["fold", "call", "raise"]}
        }
    ]
    
    for i, test in enumerate(test_messages, 1):
        print(f"\n📝 Test Message {i}:")
        message = GameStateMessage(
            message_type=test["type"],
            timestamp=asyncio.get_event_loop().time(),
            data=test["data"],
            raw_data=str(test["data"])
        )
        
        game_state = parser.parse_message(message)
        print(f"Result: {game_state}")


if __name__ == "__main__":
    print("Choose an option:")
    print("1. Live Network Monitoring (requires auth)")
    print("2. Test Message Parsing")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "2":
        test_message_parsing()
    else:
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")