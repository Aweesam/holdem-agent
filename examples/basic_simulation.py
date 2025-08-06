#!/usr/bin/env python3
"""
Basic poker simulation example using the holdem engine.
"""

from holdem.game import Card, Deck, GameState, Player, Action, ActionType, Rank, Suit
from holdem.agents import RandomAgent


def create_test_players():
    """Create test players for simulation."""
    players = [
        Player("player1", "Alice", 1000, 0),
        Player("player2", "Bob", 1000, 1),
        Player("player3", "Charlie", 1000, 2),
    ]
    return players


def simulate_hand():
    """Simulate a single hand of poker."""
    print("=== Starting New Hand ===")
    
    players = create_test_players()
    game = GameState(players, small_blind=5, big_blind=10)
    
    # Create agents
    agents = {
        "player1": RandomAgent("player1", "Alice Agent"),
        "player2": RandomAgent("player2", "Bob Agent", aggression=0.5),
        "player3": RandomAgent("player3", "Charlie Agent", aggression=0.2),
    }
    
    print(f"Community cards: {[str(card) for card in game.community_cards]}")
    print(f"Pot: ${game.pot}")
    print(f"Current bet: ${game.current_bet}")
    print()
    
    # Play the hand
    while not game.is_hand_complete():
        current_player = game.get_current_player()
        if not current_player:
            break
            
        print(f"Player {current_player.name}'s turn:")
        print(f"  Stack: ${current_player.stack}")
        print(f"  Current bet: ${current_player.current_bet}")
        print(f"  Hole cards: {[str(card) for card in current_player.hole_cards]}")
        
        # Get agent decision
        agent = agents[current_player.id]
        action = agent.decide_action(game)
        
        print(f"  Action: {action.action_type.value}" + (f" ${action.amount}" if action.amount > 0 else ""))
        
        # Apply action
        if game.apply_action(action):
            print(f"  New pot: ${game.pot}")
        else:
            print("  Invalid action!")
            break
        
        print()
    
    print(f"Final phase: {game.phase.value}")
    print(f"Community cards: {[str(card) for card in game.community_cards]}")
    print(f"Final pot: ${game.pot}")
    
    active_players = game.get_active_players()
    print(f"Active players: {[p.name for p in active_players]}")


def test_hand_evaluation():
    """Test hand evaluation with known cards."""
    print("=== Testing Enhanced Hand Evaluation ===")
    
    from holdem.game import Hand, HandRank
    
    # Test cases including edge cases
    test_hands = [
        # Royal flush
        [Card(Rank.ACE, Suit.SPADES), Card(Rank.KING, Suit.SPADES), 
         Card(Rank.QUEEN, Suit.SPADES), Card(Rank.JACK, Suit.SPADES), Card(Rank.TEN, Suit.SPADES)],
        
        # Wheel straight flush (should be 5-high, not ace-high)
        [Card(Rank.ACE, Suit.HEARTS), Card(Rank.TWO, Suit.HEARTS), 
         Card(Rank.THREE, Suit.HEARTS), Card(Rank.FOUR, Suit.HEARTS), Card(Rank.FIVE, Suit.HEARTS)],
        
        # Four of a kind
        [Card(Rank.ACE, Suit.SPADES), Card(Rank.ACE, Suit.HEARTS), 
         Card(Rank.ACE, Suit.CLUBS), Card(Rank.ACE, Suit.DIAMONDS), Card(Rank.KING, Suit.SPADES)],
        
        # Full house
        [Card(Rank.KING, Suit.SPADES), Card(Rank.KING, Suit.HEARTS), 
         Card(Rank.KING, Suit.CLUBS), Card(Rank.QUEEN, Suit.DIAMONDS), Card(Rank.QUEEN, Suit.SPADES)],
        
        # Two pair with kicker
        [Card(Rank.ACE, Suit.SPADES), Card(Rank.ACE, Suit.HEARTS), 
         Card(Rank.KING, Suit.CLUBS), Card(Rank.KING, Suit.DIAMONDS), Card(Rank.QUEEN, Suit.SPADES)],
    ]
    
    for i, cards in enumerate(test_hands):
        hand = Hand(cards)
        evaluation = hand.evaluate()
        print(f"Hand {i+1}: {[str(card) for card in cards]}")
        print(f"  {hand.describe_best_hand()}")
        if evaluation.rank == HandRank.STRAIGHT_FLUSH and evaluation.primary_value == 5:
            print(f"  ✓ Wheel straight flush correctly valued at 5 (not 14)")
        print()
    
    # Test 7-card hand evaluation
    print("7-Card Hand Test:")
    seven_cards = [
        Card(Rank.ACE, Suit.SPADES), Card(Rank.KING, Suit.HEARTS),
        Card(Rank.QUEEN, Suit.CLUBS), Card(Rank.JACK, Suit.DIAMONDS), 
        Card(Rank.TEN, Suit.SPADES), Card(Rank.TWO, Suit.HEARTS),
        Card(Rank.THREE, Suit.CLUBS)
    ]
    seven_hand = Hand(seven_cards)
    print(f"  Cards: {[str(card) for card in seven_cards]}")
    print(f"  Best hand: {seven_hand.describe_best_hand()}")
    print()


if __name__ == "__main__":
    test_hand_evaluation()
    print("\n" + "="*50 + "\n")
    simulate_hand()