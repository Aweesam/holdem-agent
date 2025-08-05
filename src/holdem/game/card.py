"""
Card and deck implementation for Texas Hold'em.
"""

from enum import Enum
from typing import List
import random
from dataclasses import dataclass


class Suit(Enum):
    HEARTS = "h"
    DIAMONDS = "d"
    CLUBS = "c"
    SPADES = "s"


class Rank(Enum):
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14


@dataclass(frozen=True)
class Card:
    rank: Rank
    suit: Suit
    
    def __str__(self) -> str:
        rank_str = {
            Rank.TWO: "2", Rank.THREE: "3", Rank.FOUR: "4", Rank.FIVE: "5",
            Rank.SIX: "6", Rank.SEVEN: "7", Rank.EIGHT: "8", Rank.NINE: "9",
            Rank.TEN: "T", Rank.JACK: "J", Rank.QUEEN: "Q", Rank.KING: "K", Rank.ACE: "A"
        }
        return f"{rank_str[self.rank]}{self.suit.value}"
    
    def __lt__(self, other: "Card") -> bool:
        return self.rank.value < other.rank.value


class Deck:
    def __init__(self) -> None:
        self.cards: List[Card] = []
        self._reset()
    
    def _reset(self) -> None:
        self.cards = [Card(rank, suit) for rank in Rank for suit in Suit]
        self.shuffle()
    
    def shuffle(self) -> None:
        random.shuffle(self.cards)
    
    def deal(self) -> Card:
        if not self.cards:
            raise ValueError("Cannot deal from empty deck")
        return self.cards.pop()
    
    def reset(self) -> None:
        self._reset()
    
    def __len__(self) -> int:
        return len(self.cards)