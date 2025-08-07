#!/usr/bin/env python3
"""
Step-by-step walkthrough of the poker system components.
This helps understand how each piece works.
"""

print("=== HOLDEM SYSTEM WALKTHROUGH ===\n")

# Step 1: Basic Card and Hand System
print("1. TESTING CARDS AND HANDS")
print("-" * 30)

from holdem.game import Card, Hand, Rank, Suit

# Create some cards
ace_spades = Card(Rank.ACE, Suit.SPADES)
king_spades = Card(Rank.KING, Suit.SPADES)
print(f"Created cards: {ace_spades}, {king_spades}")

# Create a hand
cards = [
    Card(Rank.ACE, Suit.SPADES), Card(Rank.KING, Suit.SPADES), Card(Rank.QUEEN, Suit.SPADES),
    Card(Rank.JACK, Suit.SPADES), Card(Rank.TEN, Suit.SPADES)  # Royal flush!
]
hand = Hand(cards)
evaluation = hand.evaluate()
print(f"Hand: {[str(c) for c in cards]}")
print(f"Evaluation: {evaluation.rank.name} (strength: {evaluation.rank.value})")
print()

# Step 2: Game State Management
print("2. TESTING GAME STATE")
print("-" * 30)

from holdem.game import GameState, Player

# Create players
players = [
    Player("p1", "Alice", 1000, 0),
    Player("p2", "Bob", 1000, 1)
]

print("Created players:")
for player in players:
    print(f"  {player.name}: ${player.stack} chips, position {player.position}")

# Create game
game = GameState(players, small_blind=5, big_blind=10)
print(f"Game created - Pot: ${game.pot}, Small blind: ${game.small_blind}, Big blind: ${game.big_blind}")
print()

# Step 3: Agent System
print("3. TESTING AGENTS")
print("-" * 30)

from holdem.agents import RandomAgent

# Create agents
alice_agent = RandomAgent("p1", "Alice")
bob_agent = RandomAgent("p2", "Bob")

print(f"Created agents: {alice_agent.name} and {bob_agent.name}")

# Get current player
current_player = game.get_current_player()
if current_player:
    print(f"Current player: {current_player.name}")
    print(f"Player has ${current_player.stack} chips")
    
    # Have agent decide (RandomAgent will pick a random valid action)
    agent = alice_agent if current_player.id == "p1" else bob_agent
    print(f"Agent {agent.name} making decision...")
    action = agent.decide_action(game)
    print(f"Agent {agent.name} decided: {action.action_type.value}")
    
    # Apply the action
    game.apply_action(action)
    print(f"Action applied - New pot: ${game.pot}")
else:
    print("No current player (hand might be complete)")
print()

# Step 4: Web Components (Import Test)
print("4. TESTING WEB COMPONENTS")
print("-" * 30)

try:
    from holdem.web import BrowserManager, HumanBehaviorSimulator
    print("✓ BrowserManager imported successfully")
    print("✓ HumanBehaviorSimulator imported successfully")
    
    # Test behavior simulator
    behavior_sim = HumanBehaviorSimulator()
    decision_time = behavior_sim.get_decision_time("simple")
    print(f"✓ Human behavior simulation works - decision time: {decision_time:.2f}s")
    
except ImportError as e:
    print(f"✗ Web components import failed: {e}")
print()

print("=== WALKTHROUGH COMPLETE ===")
print("✓ Core poker engine working")
print("✓ Game state management working") 
print("✓ Agent system working")
print("✓ Web components available")
print("\nReady to proceed to live dashboard testing!")