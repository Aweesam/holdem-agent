"""
Human behavior simulation for stealth poker play.
"""

import random
import time
from typing import Tuple, Optional
from dataclasses import dataclass


@dataclass
class HumanTimingProfile:
    """Configuration for human-like timing patterns."""
    decision_time_range: Tuple[float, float] = (1.5, 8.0)  # seconds
    quick_decision_prob: float = 0.15  # probability of fast decision
    long_think_prob: float = 0.08  # probability of long think
    mouse_movement_delay: Tuple[float, float] = (0.1, 0.4)
    typing_speed_wpm: Tuple[int, int] = (35, 65)  # words per minute range


class HumanBehaviorSimulator:
    """Simulates human-like behavior patterns for stealth play."""
    
    def __init__(self, profile: Optional[HumanTimingProfile] = None):
        self.profile = profile or HumanTimingProfile()
        self.session_start_time = time.time()
        self.hands_played = 0
        self.recent_decisions = []  # Track recent decision times for pattern variation
    
    def get_decision_time(self, action_complexity: str = "normal") -> float:
        """
        Calculate human-like decision time based on situation complexity.
        
        Args:
            action_complexity: "simple", "normal", "complex"
        """
        base_min, base_max = self.profile.decision_time_range
        
        # Adjust based on complexity
        if action_complexity == "simple":
            base_min *= 0.5
            base_max *= 0.7
        elif action_complexity == "complex":
            base_min *= 1.5
            base_max *= 2.0
        
        # Random decision patterns
        if random.random() < self.profile.quick_decision_prob:
            # Quick decision (strong hand or obvious fold)
            return random.uniform(0.3, 1.2)
        elif random.random() < self.profile.long_think_prob:
            # Long think (marginal decision)
            return random.uniform(base_max, base_max * 1.8)
        else:
            # Normal decision time with slight randomness
            decision_time = random.uniform(base_min, base_max)
            
            # Add slight correlation to recent decisions (humans have patterns)
            if len(self.recent_decisions) >= 3:
                avg_recent = sum(self.recent_decisions[-3:]) / 3
                decision_time = decision_time * 0.7 + avg_recent * 0.3
            
            return decision_time
    
    def wait_decision_time(self, action_complexity: str = "normal") -> None:
        """Wait for a human-like decision time."""
        wait_time = self.get_decision_time(action_complexity)
        self.recent_decisions.append(wait_time)
        if len(self.recent_decisions) > 10:
            self.recent_decisions.pop(0)
        
        # Add micro-pauses during wait to simulate thinking
        self._simulate_thinking_pauses(wait_time)
    
    def _simulate_thinking_pauses(self, total_time: float) -> None:
        """Add small pauses during decision time to simulate human thinking."""
        elapsed = 0
        while elapsed < total_time:
            # Sleep in chunks with slight variations
            chunk_time = min(random.uniform(0.1, 0.5), total_time - elapsed)
            time.sleep(chunk_time)
            elapsed += chunk_time
            
            # Occasionally add a slightly longer pause (like re-reading cards)
            if random.random() < 0.3 and elapsed < total_time * 0.8:
                time.sleep(random.uniform(0.1, 0.3))
                elapsed += 0.2
    
    def get_mouse_movement_delay(self) -> float:
        """Get delay for mouse movement to simulate human cursor movement."""
        return random.uniform(*self.profile.mouse_movement_delay)
    
    def get_typing_delay(self, text_length: int) -> float:
        """Calculate typing time based on human typing speed."""
        wpm = random.uniform(*self.profile.typing_speed_wpm)
        # Average word length is ~5 characters
        words = text_length / 5
        minutes = words / wpm
        return minutes * 60
    
    def should_take_break(self) -> bool:
        """Determine if agent should take a human-like break."""
        session_time = time.time() - self.session_start_time
        
        # Probability increases with session length
        if session_time > 3600:  # After 1 hour
            return random.random() < 0.1  # 10% chance per hand
        elif session_time > 1800:  # After 30 minutes
            return random.random() < 0.05  # 5% chance per hand
        
        return False
    
    def get_break_duration(self) -> float:
        """Get duration for a human-like break."""
        break_type = random.choice(["short", "medium", "long"])
        
        if break_type == "short":
            return random.uniform(10, 30)  # 10-30 seconds
        elif break_type == "medium":
            return random.uniform(60, 180)  # 1-3 minutes
        else:
            return random.uniform(300, 900)  # 5-15 minutes
    
    def add_random_micro_behavior(self) -> bool:
        """Randomly decide if agent should perform micro-behaviors."""
        behaviors = {
            "hover_cards": 0.05,  # Hover over cards briefly
            "scroll_slight": 0.03,  # Small scroll movements
            "window_focus_check": 0.02,  # Brief tab switches or window checks
        }
        
        for behavior, probability in behaviors.items():
            if random.random() < probability:
                return behavior
        
        return None
    
    def vary_click_position(self, base_x: int, base_y: int, variation: int = 5) -> Tuple[int, int]:
        """Add slight variation to click positions to appear more human."""
        x_offset = random.randint(-variation, variation)
        y_offset = random.randint(-variation, variation)
        return base_x + x_offset, base_y + y_offset