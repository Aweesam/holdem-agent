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

### Prerequisites
- Python 3.9+
- Node.js 18+ and npm (for dashboard)
- Chrome/Chromium browser
- ChromeDriver (automatically managed by Selenium 4.15+)

### Setup Instructions

```bash
# 1. Clone and navigate to project
cd holdem

# 2. Install Python package in editable mode
pip install -e .

# 3. Install dashboard dependencies
cd holdem-dashboard
npm install
cd ..

# 4. Verify installation
python -c "from holdem.game import Card, Hand, GameState; from holdem.agents import RandomAgent; print('✓ Core modules imported successfully')"
python examples/basic_simulation.py | head -10
echo "✓ Installation verified successfully"
```

### Dependencies

**Python Dependencies:**
- numpy>=1.20.0 (numerical computing)
- fastapi>=0.104.0 (web API framework)  
- uvicorn>=0.24.0 (ASGI server)
- websockets>=12.0 (real-time communication)
- selenium>=4.15.0 (browser automation)
- beautifulsoup4>=4.12.0 (HTML parsing)
- requests>=2.31.0 (HTTP client)
- pydantic>=2.0.0 (data validation)
- python-dotenv>=1.0.0 (environment variables)

**Node.js Dependencies:**
- Next.js 15+ (React framework)
- React 19+ (UI components)
- TypeScript (type safety)
- Tailwind CSS (styling)
- Lucide Icons (iconography)
- Recharts (data visualization)

## 🚀 Quick Start

### 1. **holdemctl** - One Command Launch (Recommended) 🎯

The simplest way to start the complete holdem stack with automatic port management and health checks:

```bash
# Install dependencies (one-time setup)
pip install -e .
cd holdem-dashboard && npm install && cd ..

# Start everything with one command
python holdemctl.py up
```

**What happens:**
- ✅ **Port Management**: Automatically finds free ports for API (8000+) and dashboard (3000+)
- ✅ **Health Checks**: Waits for services to be ready before starting dependents
- ✅ **Startup Sequence**: API → Dashboard → Agent (in correct order)
- ✅ **Browser Launch**: Opens dashboard automatically  
- ✅ **Clear Logging**: Real-time status with colored output

**Commands:**
```bash
python holdemctl.py up       # Start all services
python holdemctl.py down     # Stop all services  
python holdemctl.py status   # Show service status

# Or use the shell wrapper:
./holdemctl up               # Same as above
./holdemctl down
./holdemctl status
```

**Environment Variables:**
```bash
HOLDEM_API_PORT=8080           # Custom API port
HOLDEM_DASHBOARD_PORT=3001     # Custom dashboard port
HOLDEM_AGENT_HEADLESS=false    # Show browser for agent
HOLDEM_AGENT_SITE_URL=...      # Override poker site URL
```

**Troubleshooting:**
- If ports are busy, holdemctl automatically finds alternatives
- Use `Ctrl+C` for graceful shutdown of all services
- Check `python holdemctl.py status` if services seem stuck
- Dashboard takes ~15-20 seconds to start (NextJS compilation)

## 📋 Logging & Troubleshooting

The holdem project includes comprehensive logging with rotating file management for debugging and monitoring.

### Log Structure
```
logs/
├── api/              # API server logs with rotation (10MB, 5 backups)
├── agent/            # Poker agent logs with rotation  
├── dashboard/        # Next.js dashboard logs (daily rotation, 14 days)
└── holdemctl/        # Service management logs + stdout/stderr capture
```

### Quick Commands
```bash
# View logs for specific service
holdemctl logs api              # Show recent API logs
holdemctl logs dashboard        # Show dashboard logs  
holdemctl logs agent           # Show agent logs
holdemctl logs holdemctl       # Show service management logs

# Follow logs in real-time (like tail -f)
holdemctl logs api --follow
holdemctl logs dashboard --follow

# Start with different log levels
LOG_LEVEL=DEBUG holdemctl up           # Debug Python services
DASH_LOG_LEVEL=debug holdemctl up      # Debug dashboard
LOG_FORMAT=json holdemctl up           # Structured JSON logs
```

### Log Levels & Environment Variables

**Python Services (API & Agent):**
- `LOG_LEVEL`: DEBUG, INFO, WARNING, ERROR, CRITICAL (default: INFO)
- `LOG_FORMAT`: standard, json (default: standard)

**Dashboard (Next.js):**  
- `DASH_LOG_LEVEL`: error, warn, info, debug (default: info)

### Log Features

**🔄 Automatic Rotation:**
- Python services: 10MB files, 5 backups each
- Dashboard: Daily rotation, keeps 14 days, gzipped
- Error logs kept longer (30 days)

**🎯 Structured Logging:**
- JSON format available for log analysis
- Contextual metadata (component, operation, performance)
- Error tracking with stack traces

**💥 Fatal Error Surfacing:**
- Critical errors appear in both logs AND console
- WebSocket connection issues logged with retry attempts
- Dashboard component lifecycle tracking

### Common Log Patterns

**Check if services started correctly:**
```bash
holdemctl logs api | grep "Starting\|ready\|healthy"
holdemctl logs dashboard | grep "server\|ready\|compiled"
```

**Monitor WebSocket connections:**
```bash
holdemctl logs dashboard --follow | grep -i websocket
holdemctl logs api --follow | grep -i websocket
```

**Debug performance issues:**
```bash
# See timing and performance data
LOG_LEVEL=DEBUG holdemctl up
holdemctl logs api | grep -i performance
```

**Find errors across all services:**
```bash
find logs/ -name "*.log" -exec grep -l "ERROR\|FATAL\|Exception" {} \;
```

### Docker Log Persistence

When using Docker, logs persist on the host:
```bash
# Mount logs directory for persistence
docker run -v $(pwd)/logs:/app/logs holdem-api
```

Logs are automatically archived in CI/CD failures for debugging.

---

### 2. Manual Launch (Alternative)

For manual control or troubleshooting, you can use the original launch scripts:

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
# Install test dependencies
pip install -e ".[dev]"

# Run all tests
pytest tests/

# Run specific test files
python test_hand_evaluation.py
python test_tie_breaking.py
python test_grandpajoe42.py

# Run basic functionality tests
python examples/basic_simulation.py
python examples/network_monitoring_demo.py
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