"""
Game state management for Texas Hold'em.
"""

from enum import Enum
from typing import List, Optional, Dict
from dataclasses import dataclass, field
from uuid import uuid4

from .card import Card, Deck


class ActionType(Enum):
    FOLD = "fold"
    CHECK = "check"
    CALL = "call"
    BET = "bet"
    RAISE = "raise"
    ALL_IN = "all_in"


class GamePhase(Enum):
    PRE_FLOP = "pre_flop"
    FLOP = "flop"
    TURN = "turn"
    RIVER = "river"
    SHOWDOWN = "showdown"
    FINISHED = "finished"


@dataclass
class Action:
    player_id: str
    action_type: ActionType
    amount: int = 0
    
    def __post_init__(self):
        if self.action_type in [ActionType.BET, ActionType.RAISE, ActionType.ALL_IN] and self.amount <= 0:
            raise ValueError(f"{self.action_type} requires positive amount")


@dataclass
class Player:
    id: str
    name: str
    stack: int
    position: int
    hole_cards: List[Card] = field(default_factory=list)
    current_bet: int = 0
    is_active: bool = True
    is_all_in: bool = False
    has_acted: bool = False
    
    def can_act(self) -> bool:
        return self.is_active and not self.is_all_in
    
    def place_bet(self, amount: int) -> int:
        """Place a bet and return the actual amount bet."""
        if amount > self.stack:
            # All-in
            bet_amount = self.stack
            self.is_all_in = True
        else:
            bet_amount = amount
        
        self.stack -= bet_amount
        self.current_bet += bet_amount
        self.has_acted = True
        return bet_amount
    
    def fold(self) -> None:
        self.is_active = False
        self.has_acted = True


class GameState:
    def __init__(self, players: List[Player], small_blind: int = 1, big_blind: int = 2):
        if len(players) < 2 or len(players) > 10:
            raise ValueError("Game requires 2-10 players")
        
        self.players = players
        self.small_blind = small_blind
        self.big_blind = big_blind
        self.deck = Deck()
        
        # Game state
        self.phase = GamePhase.PRE_FLOP
        self.community_cards: List[Card] = []
        self.pot = 0
        self.current_bet = 0
        self.dealer_position = 0
        self.action_position = 0
        
        # Round tracking
        self.actions: List[Action] = []
        self.side_pots: List[Dict] = []
        
        self._setup_hand()
    
    def _setup_hand(self) -> None:
        """Initialize a new hand."""
        self.deck.reset()
        self.community_cards = []
        self.pot = 0
        self.current_bet = 0
        self.actions = []
        
        # Reset player states
        for player in self.players:
            player.hole_cards = []
            player.current_bet = 0
            player.is_active = True
            player.is_all_in = False
            player.has_acted = False
        
        # Deal hole cards
        for _ in range(2):
            for player in self.players:
                if player.stack > 0:  # Only deal to players with chips
                    player.hole_cards.append(self.deck.deal())
        
        # Post blinds
        self._post_blinds()
    
    def _post_blinds(self) -> None:
        """Post small and big blinds."""
        num_players = len([p for p in self.players if p.stack > 0])
        if num_players < 2:
            return
        
        sb_pos = (self.dealer_position + 1) % len(self.players)
        bb_pos = (self.dealer_position + 2) % len(self.players)
        
        # Small blind
        sb_player = self.players[sb_pos]
        sb_amount = sb_player.place_bet(self.small_blind)
        self.pot += sb_amount
        self.actions.append(Action(sb_player.id, ActionType.BET, sb_amount))
        
        # Big blind
        bb_player = self.players[bb_pos]
        bb_amount = bb_player.place_bet(self.big_blind)
        self.pot += bb_amount
        self.current_bet = bb_amount
        self.actions.append(Action(bb_player.id, ActionType.BET, bb_amount))
        
        # Set action position (UTG or small blind in heads-up)
        self.action_position = (bb_pos + 1) % len(self.players) if num_players > 2 else sb_pos
    
    def get_current_player(self) -> Optional[Player]:
        """Get the player whose turn it is to act."""
        if self.phase == GamePhase.FINISHED:
            return None
        
        # Find next active player who can act
        start_pos = self.action_position
        for _ in range(len(self.players)):
            player = self.players[self.action_position]
            if player.can_act() and (not player.has_acted or player.current_bet < self.current_bet):
                return player
            self.action_position = (self.action_position + 1) % len(self.players)
        
        return None
    
    def apply_action(self, action: Action) -> bool:
        """Apply an action to the game state."""
        current_player = self.get_current_player()
        if not current_player or current_player.id != action.player_id:
            return False
        
        if action.action_type == ActionType.FOLD:
            current_player.fold()
        elif action.action_type == ActionType.CHECK:
            if self.current_bet > current_player.current_bet:
                return False  # Can't check when there's a bet to call
            current_player.has_acted = True
        elif action.action_type == ActionType.CALL:
            call_amount = self.current_bet - current_player.current_bet
            actual_amount = current_player.place_bet(call_amount)
            self.pot += actual_amount
        elif action.action_type in [ActionType.BET, ActionType.RAISE]:
            if action.action_type == ActionType.BET and self.current_bet > 0:
                return False  # Can't bet when there's already a bet
            if action.action_type == ActionType.RAISE and self.current_bet == 0:
                return False  # Can't raise when there's no bet
            
            total_bet = action.amount
            if action.action_type == ActionType.RAISE:
                total_bet += self.current_bet
            
            bet_amount = total_bet - current_player.current_bet
            actual_amount = current_player.place_bet(bet_amount)
            self.pot += actual_amount
            self.current_bet = current_player.current_bet
            
            # Reset has_acted for other players
            for player in self.players:
                if player != current_player and player.can_act():
                    player.has_acted = False
        
        self.actions.append(action)
        self.action_position = (self.action_position + 1) % len(self.players)
        
        # Check if betting round is complete
        if self._is_betting_round_complete():
            self._advance_phase()
        
        return True
    
    def _is_betting_round_complete(self) -> bool:
        """Check if the current betting round is complete."""
        active_players = [p for p in self.players if p.is_active]
        if len(active_players) <= 1:
            return True
        
        # All active players have acted and either:
        # 1. All have the same current_bet, or
        # 2. All but one are all-in
        players_can_act = [p for p in active_players if p.can_act()]
        if not players_can_act:
            return True
        
        for player in players_can_act:
            if not player.has_acted or player.current_bet < self.current_bet:
                return False
        
        return True
    
    def _advance_phase(self) -> None:
        """Advance to the next phase of the game."""
        # Reset betting for next round
        for player in self.players:
            player.current_bet = 0
            player.has_acted = False
        self.current_bet = 0
        
        if self.phase == GamePhase.PRE_FLOP:
            self._deal_flop()
            self.phase = GamePhase.FLOP
        elif self.phase == GamePhase.FLOP:
            self._deal_turn()
            self.phase = GamePhase.TURN
        elif self.phase == GamePhase.TURN:
            self._deal_river()
            self.phase = GamePhase.RIVER
        elif self.phase == GamePhase.RIVER:
            self.phase = GamePhase.SHOWDOWN
        else:
            self.phase = GamePhase.FINISHED
        
        # Set action to first active player after dealer
        if self.phase not in [GamePhase.SHOWDOWN, GamePhase.FINISHED]:
            self.action_position = (self.dealer_position + 1) % len(self.players)
            while not self.players[self.action_position].can_act():
                self.action_position = (self.action_position + 1) % len(self.players)
    
    def _deal_flop(self) -> None:
        """Deal the flop (3 community cards)."""
        self.deck.deal()  # Burn card
        for _ in range(3):
            self.community_cards.append(self.deck.deal())
    
    def _deal_turn(self) -> None:
        """Deal the turn (4th community card)."""
        self.deck.deal()  # Burn card
        self.community_cards.append(self.deck.deal())
    
    def _deal_river(self) -> None:
        """Deal the river (5th community card)."""
        self.deck.deal()  # Burn card
        self.community_cards.append(self.deck.deal())
    
    def get_active_players(self) -> List[Player]:
        """Get all active players."""
        return [p for p in self.players if p.is_active]
    
    def is_hand_complete(self) -> bool:
        """Check if the hand is complete."""
        return self.phase == GamePhase.FINISHED or len(self.get_active_players()) <= 1