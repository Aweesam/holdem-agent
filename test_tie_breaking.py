#!/usr/bin/env python3
"""
Test tie-breaking and hand comparison utilities.
"""

from holdem.game import Card, Hand, Rank, Suit


def test_tie_breaking():
    """Test the tie-breaking mechanisms."""
    print("=== Testing Tie-Breaking ===")
    
    # Create hands for testing
    hands = [
        # Hand 0: Pair of Aces with King kicker
        Hand([
            Card(Rank.ACE, Suit.SPADES), Card(Rank.ACE, Suit.HEARTS),
            Card(Rank.KING, Suit.CLUBS), Card(Rank.QUEEN, Suit.DIAMONDS),
            Card(Rank.JACK, Suit.SPADES)
        ]),
        
        # Hand 1: Pair of Aces with Queen kicker (should lose)
        Hand([
            Card(Rank.ACE, Suit.CLUBS), Card(Rank.ACE, Suit.DIAMONDS),
            Card(Rank.QUEEN, Suit.SPADES), Card(Rank.JACK, Suit.HEARTS),
            Card(Rank.TEN, Suit.CLUBS)
        ]),
        
        # Hand 2: Pair of Kings (should lose to both Aces)
        Hand([
            Card(Rank.KING, Suit.SPADES), Card(Rank.KING, Suit.HEARTS),
            Card(Rank.ACE, Suit.CLUBS), Card(Rank.QUEEN, Suit.DIAMONDS),
            Card(Rank.JACK, Suit.SPADES)
        ]),
        
        # Hand 3: Another Pair of Aces with King kicker (should tie with Hand 0)
        Hand([
            Card(Rank.ACE, Suit.DIAMONDS), Card(Rank.ACE, Suit.CLUBS),
            Card(Rank.KING, Suit.SPADES), Card(Rank.QUEEN, Suit.HEARTS),
            Card(Rank.JACK, Suit.DIAMONDS)
        ])
    ]
    
    # Test compare_hands
    winners = Hand.compare_hands(hands)
    print(f"Winners (should be hands 0 and 3): {winners}")
    
    # Test rank_hands
    rankings = Hand.rank_hands(hands)
    print("Hand rankings:")
    for i, (hand_idx, evaluation) in enumerate(rankings):
        print(f"  {i+1}. Hand {hand_idx}: {hands[hand_idx].describe_best_hand()}")
    
    print()


def test_hand_descriptions():
    """Test hand description functionality."""
    print("=== Testing Hand Descriptions ===")
    
    test_hands = [
        # Royal Flush
        Hand([
            Card(Rank.ACE, Suit.SPADES), Card(Rank.KING, Suit.SPADES),
            Card(Rank.QUEEN, Suit.SPADES), Card(Rank.JACK, Suit.SPADES),
            Card(Rank.TEN, Suit.SPADES)
        ]),
        
        # Straight Flush (wheel)
        Hand([
            Card(Rank.FIVE, Suit.HEARTS), Card(Rank.FOUR, Suit.HEARTS),
            Card(Rank.THREE, Suit.HEARTS), Card(Rank.TWO, Suit.HEARTS),
            Card(Rank.ACE, Suit.HEARTS)
        ]),
        
        # Four of a Kind
        Hand([
            Card(Rank.KING, Suit.SPADES), Card(Rank.KING, Suit.HEARTS),
            Card(Rank.KING, Suit.CLUBS), Card(Rank.KING, Suit.DIAMONDS),
            Card(Rank.ACE, Suit.SPADES)
        ]),
        
        # Full House
        Hand([
            Card(Rank.ACE, Suit.SPADES), Card(Rank.ACE, Suit.HEARTS),
            Card(Rank.ACE, Suit.CLUBS), Card(Rank.KING, Suit.DIAMONDS),
            Card(Rank.KING, Suit.SPADES)
        ]),
        
        # Flush
        Hand([
            Card(Rank.ACE, Suit.SPADES), Card(Rank.JACK, Suit.SPADES),
            Card(Rank.NINE, Suit.SPADES), Card(Rank.SEVEN, Suit.SPADES),
            Card(Rank.FIVE, Suit.SPADES)
        ]),
        
        # Straight
        Hand([
            Card(Rank.TEN, Suit.SPADES), Card(Rank.NINE, Suit.HEARTS),
            Card(Rank.EIGHT, Suit.CLUBS), Card(Rank.SEVEN, Suit.DIAMONDS),
            Card(Rank.SIX, Suit.SPADES)
        ]),
        
        # Two Pair
        Hand([
            Card(Rank.ACE, Suit.SPADES), Card(Rank.ACE, Suit.HEARTS),
            Card(Rank.KING, Suit.CLUBS), Card(Rank.KING, Suit.DIAMONDS),
            Card(Rank.QUEEN, Suit.SPADES)
        ]),
        
        # Pair
        Hand([
            Card(Rank.ACE, Suit.SPADES), Card(Rank.ACE, Suit.HEARTS),
            Card(Rank.KING, Suit.CLUBS), Card(Rank.QUEEN, Suit.DIAMONDS),
            Card(Rank.JACK, Suit.SPADES)
        ])
    ]
    
    for i, hand in enumerate(test_hands):
        print(f"Hand {i+1}: {hand.describe_best_hand()}")
    
    print()


def test_complex_scenarios():
    """Test complex tie-breaking scenarios."""
    print("=== Testing Complex Scenarios ===")
    
    # Test multiple pairs with different kickers
    hands = [
        # Pair of 8s with A-K-Q kickers
        Hand([
            Card(Rank.EIGHT, Suit.SPADES), Card(Rank.EIGHT, Suit.HEARTS),
            Card(Rank.ACE, Suit.CLUBS), Card(Rank.KING, Suit.DIAMONDS),
            Card(Rank.QUEEN, Suit.SPADES)
        ]),
        
        # Pair of 8s with A-K-J kickers (should lose on 3rd kicker)
        Hand([
            Card(Rank.EIGHT, Suit.CLUBS), Card(Rank.EIGHT, Suit.DIAMONDS),
            Card(Rank.ACE, Suit.SPADES), Card(Rank.KING, Suit.HEARTS),
            Card(Rank.JACK, Suit.CLUBS)
        ]),
        
        # Pair of 8s with A-Q-J kickers (should lose on 2nd kicker)
        Hand([
            Card(Rank.EIGHT, Suit.HEARTS), Card(Rank.EIGHT, Suit.CLUBS),
            Card(Rank.ACE, Suit.DIAMONDS), Card(Rank.QUEEN, Suit.CLUBS),
            Card(Rank.JACK, Suit.DIAMONDS)
        ])
    ]
    
    rankings = Hand.rank_hands(hands)
    print("Pair with kicker comparisons:")
    for i, (hand_idx, evaluation) in enumerate(rankings):
        print(f"  {i+1}. Hand {hand_idx}: {hands[hand_idx].describe_best_hand()}")
        print(f"      Kickers: {evaluation.kickers}")
    
    print()


def run_all_tests():
    """Run all tie-breaking tests."""
    print("Running tie-breaking and comparison tests...\n")
    
    test_tie_breaking()
    test_hand_descriptions()
    test_complex_scenarios()
    
    print("All tie-breaking tests completed!")


if __name__ == "__main__":
    run_all_tests()