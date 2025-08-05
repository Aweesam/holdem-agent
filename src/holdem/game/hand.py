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
        if self.rank != other.rank:
            return self.rank.value < other.rank.value
        if self.primary_value != other.primary_value:
            return self.primary_value < other.primary_value
        if self.secondary_value != other.secondary_value:
            return self.secondary_value < other.secondary_value
        return self.kickers < other.kickers


class Hand:
    def __init__(self, cards: List[Card]):
        if len(cards) < 5 or len(cards) > 7:
            raise ValueError("Hand must contain 5-7 cards")
        self.cards = sorted(cards, key=lambda c: c.rank.value, reverse=True)
    
    def evaluate(self) -> HandEvaluation:
        """Find the best 5-card hand from available cards."""
        if len(self.cards) == 5:
            return self._evaluate_five_cards(self.cards)
        
        # For 6 or 7 cards, check all combinations of 5
        from itertools import combinations
        best_hand = None
        
        for five_cards in combinations(self.cards, 5):
            evaluation = self._evaluate_five_cards(list(five_cards))
            if best_hand is None or evaluation > best_hand:
                best_hand = evaluation
        
        return best_hand
    
    def _evaluate_five_cards(self, cards: List[Card]) -> HandEvaluation:
        """Evaluate exactly 5 cards."""
        cards = sorted(cards, key=lambda c: c.rank.value, reverse=True)
        ranks = [card.rank.value for card in cards]
        suits = [card.suit for card in cards]
        rank_counts = Counter(ranks)
        
        is_flush = len(set(suits)) == 1
        is_straight = self._is_straight(ranks)
        
        # Check for royal flush
        if is_flush and is_straight and ranks[0] == 14:  # Ace high straight
            return HandEvaluation(HandRank.ROYAL_FLUSH, 14)
        
        # Check for straight flush
        if is_flush and is_straight:
            return HandEvaluation(HandRank.STRAIGHT_FLUSH, ranks[0])
        
        # Check for four of a kind
        if 4 in rank_counts.values():
            quad_rank = max(rank for rank, count in rank_counts.items() if count == 4)
            kicker = max(rank for rank, count in rank_counts.items() if count == 1)
            return HandEvaluation(HandRank.FOUR_OF_A_KIND, quad_rank, kickers=[kicker])
        
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
            return HandEvaluation(HandRank.STRAIGHT, ranks[0])
        
        # Check for three of a kind
        if 3 in rank_counts.values():
            trips_rank = max(rank for rank, count in rank_counts.items() if count == 3)
            kickers = sorted([rank for rank, count in rank_counts.items() if count == 1], reverse=True)
            return HandEvaluation(HandRank.THREE_OF_A_KIND, trips_rank, kickers=kickers)
        
        # Check for pairs
        pairs = [rank for rank, count in rank_counts.items() if count == 2]
        if len(pairs) == 2:
            pairs.sort(reverse=True)
            kicker = max(rank for rank, count in rank_counts.items() if count == 1)
            return HandEvaluation(HandRank.TWO_PAIR, pairs[0], pairs[1], [kicker])
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