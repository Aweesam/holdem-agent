"""
Random agent for testing and baseline comparison.
"""

import random
from typing import List

from .base_agent import BaseAgent
from ..game import GameState, Action, ActionType


class RandomAgent(BaseAgent):
    """Agent that makes random valid decisions."""
    
    def __init__(self, player_id: str, name: str = None, aggression: float = 0.3):
        super().__init__(player_id, name)
        self.aggression = aggression  # Probability of betting/raising vs checking/calling
    
    def decide_action(self, game_state: GameState) -> Action:
        """Make a random valid decision."""
        valid_actions = self.get_valid_actions(game_state)
        
        if not valid_actions:
            return Action(self.player_id, ActionType.FOLD)
        
        # Separate passive and aggressive actions
        passive_actions = [
            a for a in valid_actions 
            if a.action_type in [ActionType.FOLD, ActionType.CHECK, ActionType.CALL]
        ]
        aggressive_actions = [
            a for a in valid_actions 
            if a.action_type in [ActionType.BET, ActionType.RAISE, ActionType.ALL_IN]
        ]
        
        # Choose based on aggression level
        if aggressive_actions and random.random() < self.aggression:
            return random.choice(aggressive_actions)
        elif passive_actions:
            # Prefer check/call over fold
            non_fold_actions = [a for a in passive_actions if a.action_type != ActionType.FOLD]
            if non_fold_actions and random.random() > 0.1:  # 90% chance to not fold
                return random.choice(non_fold_actions)
            return random.choice(passive_actions)
        else:
            return random.choice(valid_actions)