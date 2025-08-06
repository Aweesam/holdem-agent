# Holdem - AI Poker Agent Ecosystem

An advanced toolkit for building, testing, and deploying Texas Hold'em poker agents with stealth web interaction, real-time monitoring, and multi-personality agent framework.

## 🚀 Features

### **Live Agent System**
- **WebPokerAgent**: Production-ready agent for Club WPT Gold
- **Real-time Dashboard**: Modern React interface with live statistics and controls
- **Agent Control**: Start/stop/pause agents remotely via web interface
- **Multi-Agent Framework**: Support for different personalities and play styles

### **Stealth Technology**
- **Browser Automation**: Human-like interaction with anti-detection measures
- **Network Monitoring**: WebSocket interception for real-time game state
- **Human Behavior Simulation**: Realistic timing, breaks, and decision patterns
- **Canvas Integration**: Works with HTML5 canvas-based poker sites

### **Poker Intelligence**
- **Complete Game Engine**: Full Texas Hold'em logic and hand evaluation
- **Strategy Framework**: Extensible system for different playing styles
- **Performance Analytics**: Detailed tracking of win rates, profit, and patterns
- **Hand History**: Complete records with position, cards, and results

## 📁 Project Architecture

```
holdem/                           # 🏠 Main project directory
├── 🎮 LIVE AGENT SYSTEM
│   ├── live_agent_server.py      # Live agent API with real-time dashboard
│   ├── start_live_dashboard.py   # Launch live monitoring system
│   └── network_traffic_sample.har # Captured Club WPT Gold traffic
│
├── 🎲 POKER GAME ENGINE 
│   └── src/holdem/
│       ├── game/                 # Core poker logic [see src/holdem/game/README.md]
│       ├── agents/               # AI decision makers [see src/holdem/agents/README.md]
│       └── web/                  # Stealth web interaction [see src/holdem/web/README.md]
│
├── 📊 DASHBOARD & MONITORING
│   ├── holdem-dashboard/         # React frontend [see holdem-dashboard/README.md]
│   ├── api_server.py            # Mock data server (legacy)
│   └── start_dashboard.py       # Mock dashboard launcher (legacy)
│
├── 🧪 EXAMPLES & TESTING
│   ├── examples/                # Demo scripts and usage examples
│   ├── tests/                   # Unit tests and validation
│   └── docs/                    # Detailed documentation
│
└── 📚 DOCUMENTATION
    ├── README.md               # This overview (you are here)
    ├── DASHBOARD_README.md     # Dashboard setup and features
    └── [Package READMEs]       # Focused docs in each subdirectory
```

> 💡 **Tip**: Each major component has its own README with detailed documentation to avoid information overload.

## Installation

```bash
cd holdem
pip install -e .
```

### Dependencies

- Python 3.9+
- Node.js and npm (for dashboard)
- Selenium WebDriver
- Chrome/Chromium browser
- ChromeDriver

## 🚀 Quick Start

### 1. Live Agent Dashboard (Recommended)

Launch the complete live agent system with real-time monitoring:

```bash
# Install dependencies
pip install -e .
cd holdem-dashboard && npm install && cd ..

# Start live system (agent + dashboard)
python start_live_dashboard.py

# Access dashboard at http://localhost:3000
```

**Features:**
- 🎮 **Agent Control**: Start/stop/pause poker agents remotely
- 📊 **Live Statistics**: Real-time win rates, profit tracking, hand history  
- 🎯 **GrandpaJoe42**: Our first agent (User ID: 449469) ready for Club WPT Gold
- 🤖 **Human Behavior**: Realistic timing, breaks, and anti-detection measures

### 2. Development Dashboard (Testing)

For development with mock data:

```bash
# Mock data dashboard for testing UI
python start_dashboard.py
```

### 3. Component Testing

Test individual components:

```bash
# Test network monitoring
python examples/network_monitoring_demo.py

# Test browser automation  
python examples/web_agent_demo.py

# Test poker game engine
python examples/basic_simulation.py
```

### Basic Poker Simulation

```python
from src.holdem.game import GameState, Player
from src.holdem.agents import RandomAgent

# Create players
players = [
    Player("p1", "Alice", 1000, 0),
    Player("p2", "Bob", 1000, 1),
]

# Start game
game = GameState(players, small_blind=5, big_blind=10)

# Create agents
agents = {
    "p1": RandomAgent("p1", "Alice"),
    "p2": RandomAgent("p2", "Bob"),
}

# Play hand
while not game.is_hand_complete():
    current_player = game.get_current_player()
    if current_player:
        agent = agents[current_player.id]
        action = agent.decide_action(game)
        game.apply_action(action)
```

### Stealth Web Interaction

```python
from src.holdem.web import BrowserManager, HumanBehaviorSimulator

# Initialize stealth browser
with BrowserManager(headless=False) as browser:
    # Navigate with human-like behavior
    browser.navigate_to_game("https://friendsimulatedholdem.com/game/?token=&profile=pg")
    
    # Simulate human decision-making
    behavior_sim = HumanBehaviorSimulator()
    behavior_sim.wait_decision_time("complex")  # Think time for difficult decision
    
    # Perform human-like interactions
    element = browser.wait_for_element(By.ID, "call-button")
    browser.human_click(element)
```

## Development

### Running Examples

```bash
# Launch dashboard for real-time monitoring
python start_dashboard.py

# Basic poker simulation
python examples/basic_simulation.py

# Web automation demo
python examples/web_agent_demo.py
```

### Testing

```bash
pytest tests/
```

### Code Formatting

```bash
black src/ tests/ examples/
isort src/ tests/ examples/
```

## Architecture Goals

This toolkit is designed for:

1. **Research**: Exploring AI poker strategies and game theory
2. **Stealth Operation**: Undetectable interaction with web-based poker games
3. **Extensibility**: Easy to add new agents, strategies, and behaviors
4. **Human-like Patterns**: Sophisticated behavior simulation to avoid detection

## Security & Ethics

This project is intended for:
- Educational and research purposes
- Personal skill development
- Understanding game theory and AI decision-making

Please use responsibly and in accordance with applicable terms of service and regulations.

## 🔮 Multi-Agent Vision

### **Agent Personality Framework (Future)**

The system is designed to support multiple agents with different personalities and play styles for A/B testing and strategy comparison:

**Planned Agent Personalities:**
- 🧓 **GrandpaJoe42** *(Current)*: Tight-aggressive, psychological warfare, "harmless" image
- 🕴️ **SharkSuit88**: Loose-aggressive, high-stakes player, intimidation tactics  
- 👩‍💻 **TechSarah**: GTO-optimized, mathematical precision, minimal tells
- 🎭 **ChaosKid**: Unpredictable patterns, exploitative adjustments, wild image
- 🎯 **NitMaster**: Ultra-tight, premium hands only, patient value extraction

**Agent Comparison System:**
- **Parallel Testing**: Run multiple agents simultaneously on different tables
- **Performance Analytics**: Compare win rates, profit curves, variance
- **Strategy Effectiveness**: A/B test different approaches against same player pools
- **Meta-Game Analysis**: Study how different personalities affect table dynamics

**Implementation Design:**
```python
class AgentPersonality:
    playing_style: PlayingStyle     # Tight/Loose, Aggressive/Passive
    image_strategy: ImageStrategy   # Deceptive/Honest, Friendly/Intimidating  
    timing_profile: TimingProfile   # Decision speeds, break patterns
    bet_sizing: BetSizingStrategy   # Value/bluff ratios, sizing tells
    adaptability: AdaptationLevel   # Static/Dynamic opponent modeling
```

This allows testing hypotheses like "Does a 'grandpa' image extract more value?" or "Are mathematical agents more profitable than exploitative ones?"

## 🗺️ Development Roadmap

### **Current Status** ✅
- [x] **GrandpaJoe42**: First production agent with stealth capabilities
- [x] **Live Dashboard**: Real-time monitoring and control system  
- [x] **Club WPT Gold Integration**: Network monitoring and browser automation
- [x] **Human Behavior Simulation**: Realistic timing and anti-detection

### **Phase 1: Enhanced Intelligence** 🔄
- [ ] **Advanced Poker Strategy**: GTO solver integration, exploitative adjustments
- [ ] **Canvas Action Execution**: Precise clicking and bet input for Club WPT Gold
- [ ] **Authentication Management**: Token extraction and session management
- [ ] **Error Recovery**: Robust handling of disconnections and site changes

### **Phase 2: Multi-Agent System** 📋
- [ ] **Agent Personality Framework**: Multiple playing styles and images
- [ ] **Parallel Agent Management**: Run multiple agents simultaneously
- [ ] **A/B Testing Infrastructure**: Compare agent performance scientifically
- [ ] **Meta-Game Analysis**: Study how different styles affect table dynamics

### **Phase 3: Advanced Features** 🔮
- [ ] **Machine Learning**: Opponent modeling and adaptive strategies
- [ ] **Multi-Site Support**: Expand beyond Club WPT Gold
- [ ] **Advanced Anti-Detection**: Computer vision, behavioral randomization
- [ ] **Bankroll Management**: Automated stake selection and risk management