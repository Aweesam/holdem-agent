# 🧪 Examples & Demos

Collection of scripts and examples demonstrating different aspects of the Holdem Agent system.

## Overview

This directory contains practical examples for testing, learning, and demonstrating the various components of the poker agent ecosystem. Each example is self-contained with clear documentation.

## Available Examples

### **🎮 Live Agent Demos**

**`network_monitoring_demo.py`**
Demonstrates WebSocket network monitoring for Club WPT Gold.
```bash
python examples/network_monitoring_demo.py
```
- **Purpose**: Show how to intercept and parse poker site communications
- **Features**: Real-time message analysis, game state parsing, message classification  
- **Use Case**: Understanding site protocols before agent development

**`web_agent_demo.py`**  
Browser automation and stealth behavior demonstration.
```bash
python examples/web_agent_demo.py
```
- **Purpose**: Test browser automation and human behavior simulation
- **Features**: Stealth browser setup, human-like interactions, timing patterns
- **Use Case**: Validate browser automation before live deployment

### **🎲 Game Engine Demos**

**`basic_simulation.py`**
Core poker game simulation with multiple agents.
```bash
python examples/basic_simulation.py
```
- **Purpose**: Demonstrate pure poker game logic and agent decision-making
- **Features**: Multi-player games, hand evaluation, betting rounds, results tracking
- **Use Case**: Testing agent strategies without web interaction

### **📊 Dashboard Demos**

**Live Dashboard Integration**
```bash
# Start complete live system
python start_live_dashboard.py

# Access dashboard: http://localhost:3000
# Monitor live agent performance
```

**Mock Dashboard (Development)**
```bash
# Start development dashboard with mock data  
python start_dashboard.py

# Test UI components without live agents
```

## Detailed Examples

### **Network Monitoring Demo**

**Purpose**: Monitor and analyze Club WPT Gold network traffic

**Key Features:**
- WebSocket connection to `wss://gate.clubwptgold.com/`
- Real-time message interception and parsing
- Game state reconstruction from network data
- Message type classification (cards, bets, actions)

**Sample Output:**
```
🎰 Club WPT Gold Network Monitor
==============================================
Target WebSocket: wss://gate.clubwptgold.com/
Monitoring for User ID: 449469 (GrandpaJoe42)
==============================================

📨 Message #1 [deal_cards]
⏰ Time: 14:23:15.421
📄 Data: {"type":"deal_cards","hole_cards":["As","Kd"],"player_id":449469}

┌─ GAME STATE ─────────────────────────────────┐
│ Pot: $0
│ My Cards: ['As', 'Kd']  
│ Board: []
│ Current Player: 449469
│ Round: preflop
│ Available Actions: ['fold', 'call', 'raise']
└──────────────────────────────────────────────┘
```

**Usage Scenarios:**
1. **Protocol Analysis**: Understand site communication patterns
2. **Message Format**: Learn JSON/binary message structures  
3. **Timing Analysis**: Study real-time update frequencies
4. **Error Testing**: Test connection recovery and error handling

### **Web Agent Demo**

**Purpose**: Demonstrate browser automation and stealth capabilities

**Key Components:**
1. **Stealth Browser Setup**
   ```python
   # Anti-detection browser configuration
   options.add_argument("--disable-blink-features=AutomationControlled")
   options.add_experimental_option("excludeSwitches", ["enable-automation"])
   options.add_argument(f"--user-agent={random_user_agent()}")
   ```

2. **Human Behavior Simulation**
   ```python
   # Realistic decision timing
   behavior_sim = HumanBehaviorSimulator()
   decision_time = behavior_sim.get_decision_time("complex")  # 4-12 seconds
   
   # Human-like mouse movement
   browser.human_click(element, offset_variation=5)
   ```

3. **Navigation Patterns**
   ```python
   # Natural browsing behavior
   browser.get("https://google.com")      # Visit normal site first
   time.sleep(random.uniform(1, 3))       # Human pause
   browser.get("https://clubwptgold.com") # Then poker site
   ```

**Sample Output:**
```
=== Stealth Behavior Demo ===
Decision timing examples:
  simple: 0.87 seconds
  normal: 3.42 seconds  
  complex: 7.91 seconds

Micro-behavior examples:
  Would perform: hover_cards
  Would perform: scroll_slight

=== Browser Automation Demo ===  
Browser initialized successfully
Navigating to https://example.com
Navigation successful
Demo completed successfully
```

### **Basic Simulation Demo**

**Purpose**: Pure poker game simulation without web components

**Game Flow:**
```python
from holdem.game import GameState, Player
from holdem.agents import RandomAgent

# Setup 6-player game
players = [
    Player(f"p{i}", f"Player{i}", 1000, i) 
    for i in range(6)
]

game = GameState(players, small_blind=5, big_blind=10)

# Create agents with different personalities
agents = {
    "p0": RandomAgent("p0", "Randomizer"),
    "p1": TightAgent("p1", "NitMaster"), 
    "p2": AggressiveAgent("p2", "SharkAttack"),
    # ... more agents
}

# Play complete hand
while not game.is_hand_complete():
    current_player = game.get_current_player()
    if current_player:
        agent = agents[current_player.id]
        action = agent.decide_action(game)
        game.apply_action(action)
        
print(f"Winner: {game.get_winners()}")
print(f"Final pot: ${game.pot}")
```

**Sample Output:**
```
🎲 Texas Hold'em Simulation
===========================
Players: 6 | Blinds: $5/$10 | Starting Stack: $1000

Hand #1
-------
Dealer: Player5 (Button)
Small Blind: Player0 ($5)
Big Blind: Player1 ($10)

Preflop:
Player2 folds
Player3 calls $10  
Player4 raises to $30
Player5 calls $30
Player0 folds
Player1 calls $20

Flop: [Jh][Tc][9s]
Player1 checks
Player3 bets $50
Player4 calls $50
Player5 folds
Player1 folds

Turn: [7d]
Player3 checks  
Player4 bets $100
Player3 calls $100

River: [2c]
Player3 checks
Player4 bets $200
Player3 calls $200

Showdown:
Player3: [Qs][Kh] (Straight, K high)
Player4: [Ah][Jd] (Pair of Jacks)

Winner: Player3 (+$765)
```

## Testing Scenarios

### **Agent Strategy Testing**
```python
# Compare two strategies over 1000 hands
def compare_strategies():
    tight_agent = TightAgent("p1", "Conservative")
    loose_agent = LooseAgent("p2", "Aggressive")
    
    results = simulate_heads_up(
        agent1=tight_agent,
        agent2=loose_agent, 
        num_hands=1000,
        starting_chips=1000,
        blinds=(1, 2)
    )
    
    print(f"Tight Agent ROI: {results.agent1_roi:.2%}")
    print(f"Loose Agent ROI: {results.agent2_roi:.2%}")
```

### **Performance Benchmarking**
```python
# Benchmark hand evaluation speed
def benchmark_hand_evaluation():
    import time
    from holdem.game import Hand, Card
    
    hands = generate_random_hands(10000)
    
    start_time = time.time()
    for hand in hands:
        hand.evaluate()
    end_time = time.time()
    
    hands_per_second = len(hands) / (end_time - start_time)
    print(f"Hand evaluation speed: {hands_per_second:,.0f} hands/sec")
```

### **Network Latency Testing**
```python
# Test WebSocket connection stability
async def test_connection_stability():
    interceptor = ClubWPTNetworkInterceptor()
    
    connection_times = []
    for i in range(10):
        start = time.time()
        await interceptor.connect()
        connection_times.append(time.time() - start)
        await interceptor.disconnect()
        
    avg_time = sum(connection_times) / len(connection_times)
    print(f"Average connection time: {avg_time:.3f} seconds")
```

## Development Workflow

### **1. Component Testing**
```bash  
# Test individual components before integration
python examples/web_agent_demo.py        # Browser automation
python examples/network_monitoring_demo.py  # Network interception  
python examples/basic_simulation.py      # Game engine logic
```

### **2. Integration Testing**
```bash
# Test complete system integration
python start_live_dashboard.py
# Use dashboard to start agent and monitor performance
```

### **3. Performance Analysis**
```bash
# Profile agent performance
python -m cProfile examples/performance_test.py

# Memory usage analysis
python -m memory_profiler examples/memory_test.py
```

## Creating New Examples

### **Example Template**
```python
#!/usr/bin/env python3
"""
Brief description of what this example demonstrates.
"""

import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

def main():
    """Main example function."""
    print("🎯 Example: [Name]")
    print("=" * 40)
    
    try:
        # Example code here
        demonstrate_feature()
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        cleanup_resources()

def demonstrate_feature():
    """Core demonstration logic."""
    pass

def cleanup_resources():
    """Clean up any resources used.""" 
    pass

if __name__ == "__main__":
    main()
```

### **Documentation Requirements**
1. **Clear Purpose**: What does this example demonstrate?
2. **Prerequisites**: What needs to be installed or configured?
3. **Usage Instructions**: How to run the example
4. **Expected Output**: What should users expect to see?
5. **Error Handling**: How to troubleshoot common issues

### **Testing Guidelines**
1. **Self-Contained**: Examples should run independently
2. **Error Recovery**: Handle failures gracefully with clear messages
3. **Resource Cleanup**: Always clean up connections, files, processes
4. **Documentation**: Include inline comments explaining key concepts
5. **Cross-Platform**: Test on different operating systems where possible

## Related Documentation
- [Web Integration](../src/holdem/web/README.md) - Web automation components
- [Game Engine](../src/holdem/game/README.md) - Core poker logic
- [Agents](../src/holdem/agents/README.md) - AI decision-making
- [Dashboard](../holdem-dashboard/README.md) - Monitoring interface
- [Main README](../README.md) - Project overview and setup