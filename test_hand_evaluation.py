#!/usr/bin/env python3
"""
Comprehensive tests for hand evaluation improvements.
"""

from holdem.game import Card, Hand, HandRank, Rank, Suit, HandEvaluation


def test_wheel_straight():
    """Test that wheel straight (A-2-3-4-5) is valued correctly."""
    print("=== Testing Wheel Straight ===")
    
    # Wheel straight
    wheel_cards = [
        Card(Rank.ACE, Suit.SPADES),
        Card(Rank.TWO, Suit.HEARTS),
        Card(Rank.THREE, Suit.CLUBS),
        Card(Rank.FOUR, Suit.DIAMONDS),
        Card(Rank.FIVE, Suit.SPADES)
    ]
    wheel_hand = Hand(wheel_cards)
    wheel_eval = wheel_hand.evaluate()
    
    # Regular straight (6-7-8-9-10)
    regular_straight_cards = [
        Card(Rank.SIX, Suit.SPADES),
        Card(Rank.SEVEN, Suit.HEARTS),
        Card(Rank.EIGHT, Suit.CLUBS),
        Card(Rank.NINE, Suit.DIAMONDS),
        Card(Rank.TEN, Suit.SPADES)
    ]
    regular_hand = Hand(regular_straight_cards)
    regular_eval = regular_hand.evaluate()
    
    print(f"Wheel straight value: {wheel_eval.primary_value}")
    print(f"Regular straight (6-high) value: {regular_eval.primary_value}")
    print(f"Wheel straight should be weaker: {wheel_eval < regular_eval}")
    
    # Wheel straight flush
    wheel_flush_cards = [
        Card(Rank.ACE, Suit.SPADES),
        Card(Rank.TWO, Suit.SPADES),
        Card(Rank.THREE, Suit.SPADES),
        Card(Rank.FOUR, Suit.SPADES),
        Card(Rank.FIVE, Suit.SPADES)
    ]
    wheel_flush_hand = Hand(wheel_flush_cards)
    wheel_flush_eval = wheel_flush_hand.evaluate()
    
    print(f"Wheel straight flush rank: {wheel_flush_eval.rank.name}")
    print(f"Wheel straight flush value: {wheel_flush_eval.primary_value}")
    print()


def test_hand_comparisons():
    """Test hand comparison logic."""
    print("=== Testing Hand Comparisons ===")
    
    # Test pair comparisons with kickers
    pair_aces_king = Hand([
        Card(Rank.ACE, Suit.SPADES), Card(Rank.ACE, Suit.HEARTS),
        Card(Rank.KING, Suit.CLUBS), Card(Rank.QUEEN, Suit.DIAMONDS),
        Card(Rank.JACK, Suit.SPADES)
    ])
    
    pair_aces_queen = Hand([
        Card(Rank.ACE, Suit.CLUBS), Card(Rank.ACE, Suit.DIAMONDS),
        Card(Rank.QUEEN, Suit.SPADES), Card(Rank.JACK, Suit.HEARTS),
        Card(Rank.TEN, Suit.CLUBS)
    ])
    
    eval1 = pair_aces_king.evaluate()
    eval2 = pair_aces_queen.evaluate()
    
    print(f"Pair of Aces with King kicker: {eval1.kickers}")
    print(f"Pair of Aces with Queen kicker: {eval2.kickers}")
    print(f"King kicker beats Queen kicker: {eval1 > eval2}")
    
    # Test two pair comparisons
    two_pair_aces_kings = Hand([
        Card(Rank.ACE, Suit.SPADES), Card(Rank.ACE, Suit.HEARTS),
        Card(Rank.KING, Suit.CLUBS), Card(Rank.KING, Suit.DIAMONDS),
        Card(Rank.QUEEN, Suit.SPADES)
    ])
    
    two_pair_aces_queens = Hand([
        Card(Rank.ACE, Suit.CLUBS), Card(Rank.ACE, Suit.DIAMONDS),
        Card(Rank.QUEEN, Suit.HEARTS), Card(Rank.QUEEN, Suit.CLUBS),
        Card(Rank.KING, Suit.SPADES)
    ])
    
    eval3 = two_pair_aces_kings.evaluate()
    eval4 = two_pair_aces_queens.evaluate()
    
    print(f"Two pair A/K: primary={eval3.primary_value}, secondary={eval3.secondary_value}")
    print(f"Two pair A/Q: primary={eval4.primary_value}, secondary={eval4.secondary_value}")
    print(f"Aces and Kings beats Aces and Queens: {eval3 > eval4}")
    print()


def test_seven_card_hands():
    """Test 7-card hand evaluation."""
    print("=== Testing 7-Card Hand Evaluation ===")
    
    # 7 cards that should make a flush
    seven_cards = [
        Card(Rank.ACE, Suit.SPADES),
        Card(Rank.KING, Suit.SPADES),
        Card(Rank.QUEEN, Suit.SPADES),
        Card(Rank.JACK, Suit.SPADES),
        Card(Rank.TEN, Suit.SPADES),  # Royal flush!
        Card(Rank.TWO, Suit.HEARTS),
        Card(Rank.THREE, Suit.CLUBS)
    ]
    
    seven_card_hand = Hand(seven_cards)
    evaluation = seven_card_hand.evaluate()
    
    print(f"7-card hand evaluation: {evaluation.rank.name}")
    print(f"Should be Royal Flush: {evaluation.rank == HandRank.ROYAL_FLUSH}")
    
    # 7 cards with full house possibilities
    seven_cards_fh = [
        Card(Rank.ACE, Suit.SPADES),
        Card(Rank.ACE, Suit.HEARTS),
        Card(Rank.ACE, Suit.CLUBS),
        Card(Rank.KING, Suit.SPADES),
        Card(Rank.KING, Suit.HEARTS),
        Card(Rank.QUEEN, Suit.DIAMONDS),
        Card(Rank.JACK, Suit.SPADES)
    ]
    
    seven_card_fh = Hand(seven_cards_fh)
    eval_fh = seven_card_fh.evaluate()
    
    print(f"7-card full house: {eval_fh.rank.name}")
    print(f"Primary (trips): {eval_fh.primary_value}, Secondary (pair): {eval_fh.secondary_value}")
    print()


def test_edge_cases():
    """Test edge cases and complex scenarios."""
    print("=== Testing Edge Cases ===")
    
    # Test royal flush vs straight flush
    royal_flush = Hand([
        Card(Rank.ACE, Suit.HEARTS),
        Card(Rank.KING, Suit.HEARTS),
        Card(Rank.QUEEN, Suit.HEARTS),
        Card(Rank.JACK, Suit.HEARTS),
        Card(Rank.TEN, Suit.HEARTS)
    ])
    
    straight_flush_9 = Hand([
        Card(Rank.NINE, Suit.SPADES),
        Card(Rank.EIGHT, Suit.SPADES),
        Card(Rank.SEVEN, Suit.SPADES),
        Card(Rank.SIX, Suit.SPADES),
        Card(Rank.FIVE, Suit.SPADES)
    ])
    
    royal_eval = royal_flush.evaluate()
    sf9_eval = straight_flush_9.evaluate()
    
    print(f"Royal flush rank: {royal_eval.rank.name}")
    print(f"9-high straight flush rank: {sf9_eval.rank.name}")
    print(f"Royal flush beats 9-high straight flush: {royal_eval > sf9_eval}")
    
    # Test equal hands
    pair1 = Hand([
        Card(Rank.ACE, Suit.SPADES), Card(Rank.ACE, Suit.HEARTS),
        Card(Rank.KING, Suit.CLUBS), Card(Rank.QUEEN, Suit.DIAMONDS),
        Card(Rank.JACK, Suit.SPADES)
    ])
    
    pair2 = Hand([
        Card(Rank.ACE, Suit.CLUBS), Card(Rank.ACE, Suit.DIAMONDS),
        Card(Rank.KING, Suit.SPADES), Card(Rank.QUEEN, Suit.HEARTS),
        Card(Rank.JACK, Suit.CLUBS)
    ])
    
    eval_pair1 = pair1.evaluate()
    eval_pair2 = pair2.evaluate()
    
    print(f"Equal hands test: {eval_pair1 == eval_pair2}")
    print(f"Neither should be greater than the other: {not (eval_pair1 > eval_pair2) and not (eval_pair2 > eval_pair1)}")
    print()


def test_performance():
    """Test performance improvements."""
    print("=== Testing Performance ===")
    import time
    
    # Create a 7-card hand for performance testing
    seven_cards = [
        Card(Rank.ACE, Suit.SPADES),
        Card(Rank.KING, Suit.HEARTS),
        Card(Rank.QUEEN, Suit.CLUBS),
        Card(Rank.JACK, Suit.DIAMONDS),
        Card(Rank.TEN, Suit.SPADES),
        Card(Rank.NINE, Suit.HEARTS),
        Card(Rank.EIGHT, Suit.CLUBS)
    ]
    
    # Time multiple evaluations
    start_time = time.time()
    for _ in range(1000):
        hand = Hand(seven_cards)
        evaluation = hand.evaluate()
    end_time = time.time()
    
    print(f"1000 seven-card evaluations took: {end_time - start_time:.4f} seconds")
    print(f"Average per evaluation: {(end_time - start_time) * 1000:.4f} ms")
    print()


def run_all_tests():
    """Run all test suites."""
    print("Running comprehensive hand evaluation tests...\n")
    
    test_wheel_straight()
    test_hand_comparisons()
    test_seven_card_hands()
    test_edge_cases()
    test_performance()
    
    print("All tests completed!")


if __name__ == "__main__":
    run_all_tests()