# 🤖 Poker Agents

AI decision-making components that determine poker strategy and actions.

## Overview

This package contains the agent framework for making poker decisions. Each agent implements different strategies, personalities, and playing styles while sharing a common interface.

## Current Agents

### **BaseAgent** (`base_agent.py`)
Abstract base class that all poker agents must extend.

**Key Methods:**
- `decide_action(game_state)` - Make decision based on current game state
- `observe_action(action, game_state)` - Learn from other players' actions  
- `hand_complete(game_state, results)` - Process hand results
- `get_valid_actions(game_state)` - Calculate legal moves

### **RandomAgent** (`random_agent.py`)  
Simple baseline agent that makes random legal moves.

**Usage:**
```python
from holdem.agents import RandomAgent

agent = RandomAgent("player_1", "TestBot")
action = agent.decide_action(game_state)
```

## Future Agent Personalities

### **GrandpaJoe42** (In Development)
- **Style**: Tight-aggressive with psychological warfare
- **Image**: Harmless elderly player that opponents underestimate
- **Strategy**: Patient value extraction, strategic bluffs
- **Timing**: Realistic human-like decision patterns

### **Planned Personalities**
- **SharkSuit88**: Aggressive high-stakes intimidation
- **TechSarah**: GTO-optimized mathematical precision
- **ChaosKid**: Unpredictable exploitative patterns
- **NitMaster**: Ultra-tight premium hands only

## Agent Architecture

```python
class PokerAgent(BaseAgent):
    def __init__(self, player_id: str, name: str):
        super().__init__(player_id, name)
        self.strategy = self._initialize_strategy()
        self.personality = self._load_personality()
    
    def decide_action(self, game_state: GameState) -> Action:
        # 1. Analyze current situation
        situation = self._analyze_game_state(game_state)
        
        # 2. Apply personality-specific strategy
        action = self.strategy.decide(situation, self.personality)
        
        # 3. Add human-like variations
        return self._humanize_action(action)
```

## Creating New Agents

### **Step 1: Extend BaseAgent**
```python
from .base_agent import BaseAgent
from ..game import Action, ActionType

class MyAgent(BaseAgent):
    def __init__(self, player_id: str, name: str = "MyBot"):
        super().__init__(player_id, name)
        # Initialize strategy, personality, etc.
    
    def decide_action(self, game_state: GameState) -> Action:
        # Implement your decision logic
        return Action(self.player_id, ActionType.CALL)
```

### **Step 2: Implement Strategy**
```python
def decide_action(self, game_state: GameState) -> Action:
    # Get valid actions
    valid_actions = self.get_valid_actions(game_state)
    
    # Analyze hand strength
    hand_strength = self._evaluate_hand(game_state.my_cards, game_state.board)
    
    # Make decision based on strategy
    if hand_strength > 0.8:
        return self._value_bet(valid_actions)
    elif hand_strength < 0.3:
        return self._fold_or_bluff(valid_actions)
    else:
        return self._play_carefully(valid_actions)
```

### **Step 3: Add Personality Traits**
```python
class AgentPersonality:
    aggression_factor: float      # 0.0-1.0 (passive to aggressive)
    tightness_factor: float       # 0.0-1.0 (loose to tight)  
    bluff_frequency: float        # 0.0-1.0 (honest to deceptive)
    image_strategy: str           # "friendly", "intimidating", "neutral"
    decision_speed: str           # "fast", "medium", "slow"
```

## Testing Agents

### **Unit Testing**
```bash
# Test individual agent logic
python -m pytest tests/test_agents.py

# Test specific agent
python -m pytest tests/test_agents.py::TestRandomAgent
```

### **Simulation Testing**
```python
from holdem.game import GameState, Player
from holdem.agents import RandomAgent

# Create test scenario
players = [Player("p1", "Agent1", 1000), Player("p2", "Agent2", 1000)]
game = GameState(players, small_blind=5, big_blind=10)

# Test agent decisions
agent = RandomAgent("p1", "TestAgent")
action = agent.decide_action(game)
print(f"Agent chose: {action.action_type}")
```

## Performance Analysis

### **Key Metrics**
- **Win Rate**: Percentage of hands won
- **VPIP**: Voluntarily Put money In Pot frequency  
- **PFR**: Pre-flop Raise frequency
- **Aggression Factor**: (Bets + Raises) / Calls
- **ROI**: Return on Investment over time

### **Agent Comparison**
```python
# Compare two agents over multiple hands
results = compare_agents(
    agent1=RandomAgent("p1", "Random"),
    agent2=TightAgent("p2", "Tight"), 
    num_hands=1000,
    blind_structure=(5, 10)
)

print(f"Random Agent ROI: {results.agent1_roi:.2%}")
print(f"Tight Agent ROI: {results.agent2_roi:.2%}")
```

## Integration with Web System

Agents can be used in two contexts:

### **1. Simulation (Pure Logic)**
```python
# Direct game engine integration
agent = MyAgent("player_1")
action = agent.decide_action(game_state)
```

### **2. Live Web Play**  
```python
# WebPokerAgent wraps base agents for live play
from holdem.web import WebPokerAgent

web_agent = WebPokerAgent(base_agent=MyAgent("player_1"))
await web_agent.start(site_url="https://clubwptgold.com/")
```

## Development Guidelines

### **Agent Design Principles**
1. **Separation of Concerns**: Strategy logic separate from web interaction
2. **Testable**: Each agent should work in simulation before live deployment
3. **Personality-Driven**: Consistent behavior that matches chosen image
4. **Adaptable**: Able to adjust to different opponents and situations
5. **Human-Like**: Realistic timing and decision patterns

### **Code Standards**
- Type hints for all public methods
- Comprehensive docstrings
- Unit tests for all decision logic  
- Performance benchmarks for strategy evaluation
- Clear separation between deterministic and random components

## Related Documentation
- [Game Engine](../game/README.md) - Poker logic and game state
- [Web Integration](../web/README.md) - Browser automation and stealth
- [Main README](../../../README.md) - Project overview and setup