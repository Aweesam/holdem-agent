"""
Base agent interface for poker decision making.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any

from ..game import GameState, Action, Player, ActionType


class BaseAgent(ABC):
    """Base class for all poker agents."""
    
    def __init__(self, player_id: str, name: str = None):
        self.player_id = player_id
        self.name = name or f"Agent_{player_id[:8]}"
        self.hand_history: List[Dict[str, Any]] = []
    
    @abstractmethod
    def decide_action(self, game_state: GameState) -> Action:
        """
        Decide what action to take given the current game state.
        
        Args:
            game_state: Current state of the poker game
            
        Returns:
            Action to take
        """
        pass
    
    def observe_action(self, action: Action, game_state: GameState) -> None:
        """
        Observe an action taken by any player (including self).
        
        Args:
            action: The action that was taken
            game_state: Game state after the action
        """
        pass
    
    def hand_complete(self, game_state: GameState, results: Dict[str, Any]) -> None:
        """
        Called when a hand is complete.
        
        Args:
            game_state: Final game state
            results: Hand results including winners, amounts won, etc.
        """
        self.hand_history.append({
            'game_state': game_state,
            'results': results
        })
    
    def get_valid_actions(self, game_state: GameState) -> List[Action]:
        """
        Get list of valid actions for the current game state.
        
        Args:
            game_state: Current game state
            
        Returns:
            List of valid actions
        """
        current_player = game_state.get_current_player()
        if not current_player or current_player.id != self.player_id:
            return []
        
        valid_actions = []
        
        # Can always fold (unless already all-in)
        if current_player.can_act():
            valid_actions.append(Action(self.player_id, ActionType.FOLD))
        
        # Check if can check
        if game_state.current_bet == current_player.current_bet:
            valid_actions.append(Action(self.player_id, ActionType.CHECK))
        
        # Check if can call
        call_amount = game_state.current_bet - current_player.current_bet
        if call_amount > 0 and call_amount <= current_player.stack:
            valid_actions.append(Action(self.player_id, ActionType.CALL))
        
        # All-in if call amount exceeds stack
        if call_amount > 0 and call_amount >= current_player.stack:
            valid_actions.append(Action(self.player_id, ActionType.ALL_IN))
        
        # Betting/raising options
        if current_player.stack > 0:
            min_bet = max(game_state.big_blind, game_state.current_bet * 2 - current_player.current_bet)
            
            if game_state.current_bet == 0:
                # Can bet
                if current_player.stack >= min_bet:
                    valid_actions.append(Action(self.player_id, ActionType.BET, min_bet))
            else:
                # Can raise
                if current_player.stack >= min_bet:
                    valid_actions.append(Action(self.player_id, ActionType.RAISE, min_bet))
        
        return valid_actions