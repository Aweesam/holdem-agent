# 🎲 Poker Game Engine

Core Texas Hold'em game logic, hand evaluation, and game state management.

## Overview

This package contains the fundamental poker game mechanics that power both simulations and live agent decision-making. All poker rules, hand rankings, and game flow are implemented here.

## Core Components

### **Card System** (`card.py`)
Handles playing cards, decks, and card operations.

**Classes:**
- `Card`: Individual playing card (rank, suit)
- `Deck`: 52-card deck with shuffling and dealing
- `Hand`: Collection of cards with evaluation methods

**Usage:**
```python
from holdem.game import Card, Deck

# Create cards
card = Card('A', 'spades')
print(card)  # "A♠"

# Create and shuffle deck
deck = Deck()
deck.shuffle()
hole_cards = deck.deal(2)
```

### **Hand Evaluation** (`hand.py`)
Advanced poker hand evaluation with tie-breaking and ranking.

**Hand Rankings** (Highest to Lowest):
1. **Royal Flush**: A♠ K♠ Q♠ J♠ T♠
2. **Straight Flush**: 9♥ 8♥ 7♥ 6♥ 5♥  
3. **Four of a Kind**: K♠ K♥ K♦ K♣ A♠
4. **Full House**: Q♠ Q♥ Q♦ 7♣ 7♠
5. **Flush**: A♠ J♠ 9♠ 6♠ 4♠
6. **Straight**: A♠ K♥ Q♦ J♣ T♠
7. **Three of a Kind**: J♠ J♥ J♦ A♠ 9♣
8. **Two Pair**: A♠ A♥ 8♦ 8♣ K♠
9. **One Pair**: K♠ K♥ A♦ Q♣ J♠
10. **High Card**: A♠ K♥ Q♦ J♣ 9♠

**Usage:**
```python
from holdem.game import Hand, Card

# Evaluate 7-card hand (hole cards + board)
cards = [
    Card('A', 'spades'), Card('K', 'spades'),     # Hole cards
    Card('Q', 'spades'), Card('J', 'spades'),    # Board
    Card('T', 'spades'), Card('9', 'hearts'),
    Card('8', 'clubs')
]

hand = Hand(cards)
hand_rank = hand.evaluate()
print(f"Hand: {hand_rank.name}")  # "ROYAL_FLUSH"
print(f"Strength: {hand_rank.value}")  # 10 (highest)
```

### **Game State Management** (`game_state.py`) 
Complete Texas Hold'em game state and rules enforcement.

**Key Classes:**
- `Player`: Player with chips, position, and current bet
- `GameState`: Complete game state with betting rounds
- `Action`: Player actions (fold, call, bet, raise, check)
- `ActionType`: Enumeration of possible actions

**Game Flow:**
1. **Pre-flop**: Deal 2 hole cards, betting round
2. **Flop**: Deal 3 community cards, betting round  
3. **Turn**: Deal 1 more community card, betting round
4. **River**: Deal final community card, betting round
5. **Showdown**: Determine winner(s)

**Usage:**
```python
from holdem.game import GameState, Player, Action, ActionType

# Setup game
players = [
    Player("p1", "Alice", chips=1000, position=0),
    Player("p2", "Bob", chips=1500, position=1)
]

game = GameState(players, small_blind=5, big_blind=10)

# Play a hand
while not game.is_hand_complete():
    current_player = game.get_current_player()
    if current_player:
        # Get valid actions for current player
        valid_actions = game.get_valid_actions(current_player.id)
        
        # Make decision (would use agent here)
        action = Action(current_player.id, ActionType.CALL)
        
        # Apply action
        game.apply_action(action)
```

## Advanced Features

### **Hand Strength Calculation**
```python
def calculate_hand_strength(hole_cards, board_cards):
    """Calculate relative hand strength (0.0 to 1.0)"""
    
    # Monte Carlo simulation
    wins = 0
    total_trials = 1000
    
    for trial in range(total_trials):
        # Complete random board if needed
        full_board = complete_board(board_cards)
        
        # Generate random opponent hand
        opponent_hand = generate_random_hand(exclude=hole_cards + full_board)
        
        # Compare hands
        our_hand = Hand(hole_cards + full_board)
        their_hand = Hand(opponent_hand + full_board)
        
        if our_hand.evaluate() > their_hand.evaluate():
            wins += 1
    
    return wins / total_trials
```

### **Pot Odds Calculation**
```python
def calculate_pot_odds(pot_size, bet_to_call):
    """Calculate pot odds for decision making"""
    total_pot = pot_size + bet_to_call
    pot_odds = bet_to_call / total_pot
    return pot_odds

# Example: $100 pot, $20 to call = 20/120 = 0.167 (16.7%)
odds = calculate_pot_odds(100, 20)
print(f"Need {odds:.1%} equity to call")
```

### **Betting Round Management**
```python
class BettingRound:
    PREFLOP = "preflop"
    FLOP = "flop"
    TURN = "turn"  
    RIVER = "river"

def advance_betting_round(game_state):
    """Progress to next betting round"""
    current_round = game_state.betting_round
    
    if current_round == BettingRound.PREFLOP:
        # Deal flop
        game_state.board.extend(game_state.deck.deal(3))
        game_state.betting_round = BettingRound.FLOP
        
    elif current_round == BettingRound.FLOP:
        # Deal turn
        game_state.board.append(game_state.deck.deal(1)[0])
        game_state.betting_round = BettingRound.TURN
        
    # etc...
```

## Game Variants

### **No-Limit Hold'em** (Default)
- Players can bet any amount up to their chip stack
- All-in betting allowed
- Most common tournament and cash game format

### **Limit Hold'em**
```python
class LimitGameState(GameState):
    def __init__(self, players, small_bet, big_bet):
        super().__init__(players, small_bet//2, small_bet)
        self.small_bet = small_bet  # Preflop/flop bet size
        self.big_bet = big_bet      # Turn/river bet size
        
    def get_valid_bet_sizes(self, player):
        if self.betting_round in [BettingRound.PREFLOP, BettingRound.FLOP]:
            return [self.small_bet]
        else:
            return [self.big_bet]
```

### **Tournament Structure**
```python
class TournamentGameState(GameState):
    def __init__(self, players, blind_schedule):
        self.blind_schedule = blind_schedule
        self.tournament_level = 0
        super().__init__(players, blind_schedule[0][0], blind_schedule[0][1])
    
    def increase_blinds(self):
        """Increase blinds according to tournament schedule"""
        if self.tournament_level < len(self.blind_schedule) - 1:
            self.tournament_level += 1
            sb, bb = self.blind_schedule[self.tournament_level]
            self.small_blind = sb
            self.big_blind = bb
```

## Testing and Validation

### **Hand Evaluation Tests**
```python
def test_royal_flush():
    cards = [Card('A','♠'), Card('K','♠'), Card('Q','♠'), 
             Card('J','♠'), Card('T','♠'), Card('9','♥'), Card('8','♣')]
    hand = Hand(cards)
    assert hand.evaluate().name == "ROYAL_FLUSH"

def test_tie_breaking():
    # Test that A♠ A♥ K♦ beats A♦ A♣ Q♠ (same pair, better kicker)
    hand1 = Hand([Card('A','♠'), Card('A','♥'), Card('K','♦'), 
                  Card('7','♣'), Card('3','♠')])
    hand2 = Hand([Card('A','♦'), Card('A','♣'), Card('Q','♠'),
                  Card('7','♥'), Card('3','♦')])
    assert hand1.evaluate() > hand2.evaluate()
```

### **Game Logic Tests**
```python
def test_betting_sequence():
    players = [Player(f"p{i}", f"Player{i}", 1000, i) for i in range(3)]
    game = GameState(players, 5, 10)
    
    # Preflop betting
    game.apply_action(Action("p0", ActionType.CALL))  # Small blind calls
    game.apply_action(Action("p1", ActionType.RAISE, 30))  # Big blind raises
    game.apply_action(Action("p2", ActionType.CALL))  # Button calls
    game.apply_action(Action("p0", ActionType.FOLD))  # Small blind folds
    game.apply_action(Action("p1", ActionType.CALL))  # Big blind calls raise
    
    assert game.pot == 90  # 5 + 30 + 30 + 30 - 5 (folded)
    assert len(game.active_players) == 2
```

### **Performance Benchmarks**
```bash
# Benchmark hand evaluation speed
python -m pytest tests/test_performance.py

# Results: ~50,000 hand evaluations per second
# Monte Carlo simulations: ~1,000 trials per second
```

## Integration with Agents

### **Agent Decision Support**
```python
class GameStateAnalyzer:
    @staticmethod
    def get_hand_strength(hole_cards, board_cards, num_opponents):
        """Calculate hand strength against N opponents"""
        return monte_carlo_simulation(hole_cards, board_cards, num_opponents)
    
    @staticmethod  
    def get_pot_odds(game_state, player_id):
        """Calculate current pot odds for player"""
        player = game_state.get_player(player_id)
        call_amount = game_state.current_bet - player.current_bet
        return call_amount / (game_state.pot + call_amount)
    
    @staticmethod
    def get_position_info(game_state, player_id):
        """Get position information (early/middle/late)"""
        player = game_state.get_player(player_id)
        total_players = len(game_state.active_players)
        position_pct = player.position / total_players
        
        if position_pct < 0.33:
            return "early"
        elif position_pct < 0.67:
            return "middle"
        else:
            return "late"
```

### **Strategy Integration**
```python
# Agent uses game engine for decision making
class PokerAgent(BaseAgent):
    def decide_action(self, game_state: GameState) -> Action:
        # Use game engine analysis
        hand_strength = GameStateAnalyzer.get_hand_strength(
            game_state.get_player_hole_cards(self.player_id),
            game_state.board,
            len(game_state.active_players) - 1
        )
        
        pot_odds = GameStateAnalyzer.get_pot_odds(game_state, self.player_id)
        position = GameStateAnalyzer.get_position_info(game_state, self.player_id)
        
        # Make decision based on analysis
        return self.strategy.decide(hand_strength, pot_odds, position)
```

## Performance Considerations

### **Optimization Techniques**
- **Hand Evaluation**: Optimized lookup tables for 5-card combinations
- **Monte Carlo**: Parallelized simulations for hand strength calculation  
- **Memory Management**: Efficient card and game state representations
- **Caching**: Memoized results for repeated calculations

### **Scalability**
- Support for 2-10 players per table
- Multiple simultaneous game instances
- Tournament bracket management
- Database integration for hand history

## Related Documentation
- [Agents](../agents/README.md) - AI decision-making using game engine
- [Web Integration](../web/README.md) - Live play with game state sync
- [Examples](../../../examples/README.md) - Usage examples and demos  
- [Main README](../../../README.md) - Project overview and setup