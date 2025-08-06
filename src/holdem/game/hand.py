"""
Hand evaluation and ranking for Texas Hold'em.
"""

from enum import Enum
from typing import List, Tuple, Optional
from collections import Counter
from dataclasses import dataclass

from .card import Card, Rank


class HandRank(Enum):
    HIGH_CARD = 1
    PAIR = 2
    TWO_PAIR = 3
    THREE_OF_A_KIND = 4
    STRAIGHT = 5
    FLUSH = 6
    FULL_HOUSE = 7
    FOUR_OF_A_KIND = 8
    STRAIGHT_FLUSH = 9
    ROYAL_FLUSH = 10


@dataclass
class HandEvaluation:
    rank: HandRank
    primary_value: int
    secondary_value: int = 0
    kickers: List[int] = None
    
    def __post_init__(self):
        if self.kickers is None:
            self.kickers = []
    
    def __lt__(self, other: "HandEvaluation") -> bool:
        """Compare two hand evaluations. Returns True if self is weaker than other."""
        if self.rank != other.rank:
            return self.rank.value < other.rank.value
        if self.primary_value != other.primary_value:
            return self.primary_value < other.primary_value
        if self.secondary_value != other.secondary_value:
            return self.secondary_value < other.secondary_value
        # Compare kickers element by element
        for my_kicker, other_kicker in zip(self.kickers, other.kickers):
            if my_kicker != other_kicker:
                return my_kicker < other_kicker
        return False  # Hands are equal
    
    def __eq__(self, other: "HandEvaluation") -> bool:
        """Check if two hand evaluations are equal."""
        return (self.rank == other.rank and 
                self.primary_value == other.primary_value and
                self.secondary_value == other.secondary_value and
                self.kickers == other.kickers)
    
    def __gt__(self, other: "HandEvaluation") -> bool:
        """Returns True if self is stronger than other."""
        return not self.__lt__(other) and not self.__eq__(other)
    
    def __le__(self, other: "HandEvaluation") -> bool:
        """Returns True if self is weaker than or equal to other."""
        return self.__lt__(other) or self.__eq__(other)
    
    def __ge__(self, other: "HandEvaluation") -> bool:
        """Returns True if self is stronger than or equal to other."""
        return self.__gt__(other) or self.__eq__(other)


class Hand:
    def __init__(self, cards: List[Card]):
        if len(cards) < 5 or len(cards) > 7:
            raise ValueError("Hand must contain 5-7 cards")
        self.cards = sorted(cards, key=lambda c: c.rank.value, reverse=True)
    
    def evaluate(self) -> HandEvaluation:
        """Find the best 5-card hand from available cards."""
        if len(self.cards) == 5:
            return self._evaluate_five_cards(self.cards)
        
        # For 6 or 7 cards, use optimized evaluation
        return self._evaluate_best_hand(self.cards)
    
    def _evaluate_five_cards(self, cards: List[Card]) -> HandEvaluation:
        """Evaluate exactly 5 cards."""
        cards = sorted(cards, key=lambda c: c.rank.value, reverse=True)
        ranks = [card.rank.value for card in cards]
        suits = [card.suit for card in cards]
        rank_counts = Counter(ranks)
        
        is_flush = len(set(suits)) == 1
        is_straight = self._is_straight(ranks)
        
        # Check for royal flush (ace-high straight flush)
        if is_flush and is_straight:
            straight_high = self._get_straight_high_card(ranks)
            if straight_high == 14:  # Ace high straight
                return HandEvaluation(HandRank.ROYAL_FLUSH, 14)
        
        # Check for straight flush
        if is_flush and is_straight:
            straight_high = self._get_straight_high_card(ranks)
            return HandEvaluation(HandRank.STRAIGHT_FLUSH, straight_high)
        
        # Check for four of a kind
        if 4 in rank_counts.values():
            quad_rank = max(rank for rank, count in rank_counts.items() if count == 4)
            kickers = sorted([rank for rank, count in rank_counts.items() if count == 1], reverse=True)
            return HandEvaluation(HandRank.FOUR_OF_A_KIND, quad_rank, kickers=kickers)
        
        # Check for full house
        if 3 in rank_counts.values() and 2 in rank_counts.values():
            trips_rank = max(rank for rank, count in rank_counts.items() if count == 3)
            pair_rank = max(rank for rank, count in rank_counts.items() if count == 2)
            return HandEvaluation(HandRank.FULL_HOUSE, trips_rank, pair_rank)
        
        # Check for flush
        if is_flush:
            return HandEvaluation(HandRank.FLUSH, 0, kickers=ranks)
        
        # Check for straight
        if is_straight:
            straight_high = self._get_straight_high_card(ranks)
            return HandEvaluation(HandRank.STRAIGHT, straight_high)
        
        # Check for three of a kind
        if 3 in rank_counts.values():
            trips_rank = max(rank for rank, count in rank_counts.items() if count == 3)
            kickers = sorted([rank for rank, count in rank_counts.items() if count == 1], reverse=True)
            return HandEvaluation(HandRank.THREE_OF_A_KIND, trips_rank, kickers=kickers)
        
        # Check for pairs
        pairs = [rank for rank, count in rank_counts.items() if count == 2]
        if len(pairs) == 2:
            pairs.sort(reverse=True)
            kickers = sorted([rank for rank, count in rank_counts.items() if count == 1], reverse=True)
            return HandEvaluation(HandRank.TWO_PAIR, pairs[0], pairs[1], kickers)
        elif len(pairs) == 1:
            pair_rank = pairs[0]
            kickers = sorted([rank for rank, count in rank_counts.items() if count == 1], reverse=True)
            return HandEvaluation(HandRank.PAIR, pair_rank, kickers=kickers)
        
        # High card
        return HandEvaluation(HandRank.HIGH_CARD, 0, kickers=ranks)
    
    def _is_straight(self, ranks: List[int]) -> bool:
        """Check if ranks form a straight."""
        unique_ranks = sorted(set(ranks), reverse=True)
        if len(unique_ranks) != 5:
            return False
        
        # Check for regular straight
        if unique_ranks[0] - unique_ranks[4] == 4:
            return True
        
        # Check for wheel straight (A-2-3-4-5)
        if unique_ranks == [14, 5, 4, 3, 2]:
            return True
        
        return False
    
    def _get_straight_high_card(self, ranks: List[int]) -> int:
        """Get the high card value for a straight, handling wheel correctly."""
        unique_ranks = sorted(set(ranks), reverse=True)
        
        # Check for wheel straight (A-2-3-4-5) - high card is 5, not Ace
        if unique_ranks == [14, 5, 4, 3, 2]:
            return 5
        
        # Regular straight - return highest card
        return unique_ranks[0]
    
    def _evaluate_best_hand(self, cards: List[Card]) -> HandEvaluation:
        """Efficiently find the best 5-card hand from 6 or 7 cards."""
        # For small numbers of cards, still use combinations approach
        # but optimized for common cases
        from itertools import combinations
        best_hand = None
        
        # Sort cards by rank (highest first) for optimization
        cards = sorted(cards, key=lambda c: c.rank.value, reverse=True)
        
        # Try combinations in a smarter order - prioritize higher cards
        for five_cards in combinations(cards, 5):
            evaluation = self._evaluate_five_cards(list(five_cards))
            if best_hand is None or evaluation > best_hand:
                best_hand = evaluation
                # Early termination for high-ranking hands
                if best_hand.rank.value >= HandRank.STRAIGHT_FLUSH.value:
                    break
        
        return best_hand
    
    @staticmethod
    def compare_hands(hands: List["Hand"]) -> List[int]:
        """
        Compare multiple hands and return indices of winning hands.
        Returns a list of indices - if multiple hands tie, multiple indices are returned.
        """
        if not hands:
            return []
        
        evaluations = [hand.evaluate() for hand in hands]
        best_eval = max(evaluations)
        
        # Find all hands that are tied for best
        winners = []
        for i, evaluation in enumerate(evaluations):
            if evaluation == best_eval:
                winners.append(i)
        
        return winners
    
    @staticmethod
    def rank_hands(hands: List["Hand"]) -> List[Tuple[int, "HandEvaluation"]]:
        """
        Rank multiple hands from best to worst.
        Returns list of (index, evaluation) tuples sorted by hand strength.
        """
        evaluations = [(i, hand.evaluate()) for i, hand in enumerate(hands)]
        return sorted(evaluations, key=lambda x: x[1], reverse=True)
    
    def __str__(self) -> str:
        """String representation of the hand."""
        return f"Hand({[str(card) for card in self.cards]})"
    
    def describe_best_hand(self) -> str:
        """Return a human-readable description of the best 5-card hand."""
        evaluation = self.evaluate()
        rank_names = {
            HandRank.HIGH_CARD: "High Card",
            HandRank.PAIR: "Pair",
            HandRank.TWO_PAIR: "Two Pair", 
            HandRank.THREE_OF_A_KIND: "Three of a Kind",
            HandRank.STRAIGHT: "Straight",
            HandRank.FLUSH: "Flush",
            HandRank.FULL_HOUSE: "Full House",
            HandRank.FOUR_OF_A_KIND: "Four of a Kind",
            HandRank.STRAIGHT_FLUSH: "Straight Flush",
            HandRank.ROYAL_FLUSH: "Royal Flush"
        }
        
        rank_symbols = {14: "A", 13: "K", 12: "Q", 11: "J", 10: "T", 
                       9: "9", 8: "8", 7: "7", 6: "6", 5: "5", 4: "4", 3: "3", 2: "2"}
        
        base_name = rank_names[evaluation.rank]
        
        if evaluation.rank in [HandRank.ROYAL_FLUSH]:
            return f"{base_name}"
        elif evaluation.rank in [HandRank.STRAIGHT_FLUSH, HandRank.STRAIGHT]:
            high_card = rank_symbols.get(evaluation.primary_value, str(evaluation.primary_value))
            return f"{base_name}, {high_card} high"
        elif evaluation.rank == HandRank.FOUR_OF_A_KIND:
            quad_rank = rank_symbols.get(evaluation.primary_value, str(evaluation.primary_value))
            return f"{base_name}, {quad_rank}s"
        elif evaluation.rank == HandRank.FULL_HOUSE:
            trips_rank = rank_symbols.get(evaluation.primary_value, str(evaluation.primary_value))
            pair_rank = rank_symbols.get(evaluation.secondary_value, str(evaluation.secondary_value))
            return f"{base_name}, {trips_rank}s over {pair_rank}s"
        elif evaluation.rank == HandRank.FLUSH:
            high_card = rank_symbols.get(evaluation.kickers[0], str(evaluation.kickers[0]))
            return f"{base_name}, {high_card} high"
        elif evaluation.rank == HandRank.THREE_OF_A_KIND:
            trips_rank = rank_symbols.get(evaluation.primary_value, str(evaluation.primary_value))
            return f"{base_name}, {trips_rank}s"
        elif evaluation.rank == HandRank.TWO_PAIR:
            high_pair = rank_symbols.get(evaluation.primary_value, str(evaluation.primary_value))
            low_pair = rank_symbols.get(evaluation.secondary_value, str(evaluation.secondary_value))
            return f"{base_name}, {high_pair}s and {low_pair}s"
        elif evaluation.rank == HandRank.PAIR:
            pair_rank = rank_symbols.get(evaluation.primary_value, str(evaluation.primary_value))
            return f"{base_name} of {pair_rank}s"
        else:  # HIGH_CARD
            high_card = rank_symbols.get(evaluation.kickers[0], str(evaluation.kickers[0]))
            return f"{base_name}, {high_card} high"