# Holdem - Stealth Poker Agent Toolkit

A Python toolkit for building Texas Hold'em poker agents with stealth web interaction capabilities.

## Features

- **Complete Poker Engine**: Full Texas Hold'em game logic with hand evaluation, betting rounds, and game state management
- **Real-time Dashboard**: Modern web interface for monitoring agent performance with live statistics and charts
- **Stealth Web Automation**: Human-like browser interaction to avoid detection
- **Agent Framework**: Extensible agent system for different poker strategies
- **Human Behavior Simulation**: Realistic timing, mouse movements, and decision patterns

## Project Structure

```
holdem/
├── src/holdem/
│   ├── game/           # Core poker game logic
│   │   ├── card.py     # Card and deck implementation
│   │   ├── hand.py     # Hand evaluation and ranking
│   │   └── game_state.py # Game state management
│   ├── agents/         # Poker decision-making agents
│   │   ├── base_agent.py    # Base agent interface
│   │   └── random_agent.py  # Random baseline agent
│   └── web/            # Stealth web interaction
│       ├── browser_manager.py    # Browser automation
│       ├── human_behavior.py     # Human behavior simulation
│       └── stealth_agent.py      # Web-based poker agent
├── holdem-dashboard/   # Real-time monitoring dashboard
│   ├── src/           # Next.js frontend components
│   └── package.json   # Frontend dependencies
├── api_server.py      # FastAPI backend for dashboard
├── start_dashboard.py # Auto-start script for dashboard
├── examples/          # Demo and test scripts
├── tests/            # Unit tests
└── docs/             # Documentation
```

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

## Quick Start

### Dashboard Monitoring

Launch the real-time dashboard to monitor agent performance:

```bash
# Auto-start both API server and frontend
python start_dashboard.py

# Access dashboard at http://localhost:3000
```

Features:
- Real-time statistics and performance metrics
- Live hand history and results
- Interactive profit/loss charts
- WebSocket updates every 3 seconds

See [DASHBOARD_README.md](DASHBOARD_README.md) for detailed setup instructions.

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

## Roadmap

- [x] Real-time dashboard with performance monitoring
- [ ] Advanced poker agents (GTO, exploitative)
- [ ] Site-specific game state parsers
- [ ] Machine learning integration
- [ ] Advanced anti-detection measures
- [ ] Performance optimization
- [ ] Comprehensive test coverage