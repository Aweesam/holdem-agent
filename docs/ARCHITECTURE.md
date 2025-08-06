# 🏗️ Architecture & Development Guide

Comprehensive guide to the Holdem Agent system architecture, design decisions, and development practices.

## System Overview

The Holdem Agent ecosystem is designed as a modular, scalable system for building, testing, and deploying AI poker agents with stealth web interaction capabilities.

### **Core Design Principles**

1. **Modularity**: Clear separation between game logic, web interaction, and monitoring
2. **Testability**: Each component can be tested independently in simulation
3. **Stealth**: Human-like behavior patterns to avoid detection
4. **Scalability**: Support for multiple agents and parallel operations
5. **Observability**: Comprehensive monitoring and real-time analytics

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     HOLDEM AGENT ECOSYSTEM                     │
└─────────────────────────────────────────────────────────────────┘

┌───────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   POKER SITES     │    │  LIVE DASHBOARD  │    │  CONTROL LAYER  │
│                   │    │                  │    │                 │
│ ┌───────────────┐ │    │ ┌──────────────┐ │    │ ┌─────────────┐ │
│ │ Club WPT Gold │◄┼────┤ │ React UI     │ │    │ │ Agent Mgmt  │ │
│ │   (Canvas)    │ │    │ │ (Next.js)    │ │    │ │ (FastAPI)   │ │
│ └───────────────┘ │    │ └──────────────┘ │    │ └─────────────┘ │
│                   │    │                  │    │                 │
│ ┌───────────────┐ │    │ ┌──────────────┐ │    │ ┌─────────────┐ │
│ │ Future Sites  │ │    │ │ WebSocket    │◄┼────┤ │ Live Agent  │ │
│ │               │ │    │ │ Client       │ │    │ │ Server      │ │
│ └───────────────┘ │    │ └──────────────┘ │    │ └─────────────┘ │
└───────────────────┘    └──────────────────┘    └─────────────────┘
         ▲                         ▲                       ▲
         │                         │                       │
         ▼                         ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                      WEB POKER AGENT                           │
│                                                                 │
│ ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────┐ │
│ │   Browser   │  │  Network    │  │   Game      │  │  Human  │ │
│ │  Manager    │  │ Interceptor │  │   Parser    │  │Behavior │ │
│ │ (Selenium)  │  │(WebSocket)  │  │ (Protocol)  │  │ (Timing)│ │
│ └─────────────┘  └─────────────┘  └─────────────┘  └─────────┘ │
│         │                │                │              │     │
│         └────────────────┼────────────────┼──────────────┘     │
│                          │                │                    │
│                          ▼                ▼                    │
│              ┌─────────────────────────────────┐               │
│              │        POKER AGENT CORE         │               │
│              │                                 │               │
│              │  ┌─────────┐    ┌────────────┐  │               │
│              │  │Strategy │    │Personality │  │               │
│              │  │Engine   │    │Profile     │  │               │
│              │  └─────────┘    └────────────┘  │               │
│              │                                 │               │
│              │  ┌─────────┐    ┌────────────┐  │               │
│              │  │Decision │    │Performance │  │               │
│              │  │Logic    │    │Analytics   │  │               │
│              │  └─────────┘    └────────────┘  │               │
│              └─────────────────────────────────┘               │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    POKER GAME ENGINE                           │
│                                                                 │
│ ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────┐ │
│ │    Card     │  │    Hand     │  │    Game     │  │  Player │ │
│ │   System    │  │ Evaluation  │  │   State     │  │  Model  │ │
│ │             │  │             │  │ Management  │  │         │ │
│ └─────────────┘  └─────────────┘  └─────────────┘  └─────────┘ │
│                                                                 │
│ ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────┐ │
│ │   Action    │  │   Betting   │  │   Position  │  │  Rules  │ │
│ │  System     │  │   Rounds    │  │  Tracking   │  │ Engine  │ │
│ │             │  │             │  │             │  │         │ │
│ └─────────────┘  └─────────────┘  └─────────────┘  └─────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Component Architecture

### **1. Web Poker Agent Layer**

**Purpose**: Integration layer that coordinates all components for live play

**Key Components:**
- **WebPokerAgent**: Main orchestrator class
- **BrowserManager**: Stealth browser automation
- **NetworkInterceptor**: Real-time game state monitoring  
- **HumanBehaviorSimulator**: Anti-detection patterns

**Design Patterns:**
```python
class WebPokerAgent(BaseAgent):
    def __init__(self):
        # Composition pattern - inject dependencies
        self.browser = BrowserManager()
        self.network = NetworkInterceptor()  
        self.behavior = HumanBehaviorSimulator()
        self.parser = GameStateParser()
        
        # Observer pattern - register callbacks
        self.network.set_callback(self._handle_game_update)
        self.register_dashboard_callback(self._report_stats)
    
    async def start(self):
        # Orchestrate component startup sequence
        await self._initialize_browser()
        await self._connect_network_monitoring()
        await self._start_main_loop()
```

**Responsibilities:**
- Coordinate browser automation and network monitoring
- Translate web game state to internal poker representation
- Apply human behavior patterns to all actions
- Report statistics and performance to dashboard
- Handle errors and connection recovery

### **2. Poker Game Engine Layer**

**Purpose**: Pure poker logic independent of web interaction

**Key Components:**
- **Card System**: Playing cards, decks, hand evaluation
- **Game State**: Complete Texas Hold'em game state management
- **Player Model**: Player chips, position, betting status
- **Action System**: Legal moves and betting validation

**Design Patterns:**
```python
# Strategy pattern for hand evaluation
class HandEvaluator:
    def evaluate(self, cards: List[Card]) -> HandRank:
        for evaluator in self.evaluators:
            if evaluator.matches(cards):
                return evaluator.rank(cards)
                
# State pattern for betting rounds
class GameState:
    def __init__(self):
        self.current_round = PreflopRound()
    
    def advance_round(self):
        self.current_round = self.current_round.next_round()
```

**Responsibilities:**
- Enforce Texas Hold'em rules and game flow
- Evaluate hand strength and determine winners  
- Track pot, blinds, and betting action
- Provide pure functional poker logic for testing

### **3. Live Dashboard Layer**

**Purpose**: Real-time monitoring and control interface

**Key Components:**
- **React Dashboard**: Modern UI with real-time updates
- **WebSocket Client**: Live data streaming from agent server
- **Agent Control**: Start/stop/pause agent management
- **Performance Analytics**: Charts, statistics, hand history

**Design Patterns:**
```javascript
// Observer pattern with WebSocket
const useWebSocket = (url) => {
  const [data, setData] = useState(null);
  
  useEffect(() => {
    const ws = new WebSocket(url);
    ws.onmessage = (event) => {
      const update = JSON.parse(event.data);
      setData(update.data); // Reactive updates
    };
    return () => ws.close();
  }, [url]);
  
  return { data, isConnected: ws.readyState === WebSocket.OPEN };
};

// Component composition
const Dashboard = () => {
  const { data, isConnected } = useWebSocket('ws://localhost:8000/ws');
  
  return (
    <>
      <AgentControl isConnected={isConnected} />
      <StatsCards stats={data?.stats} />
      <PerformanceChart data={data?.performance} />
    </>
  );
};
```

**Responsibilities:**
- Provide real-time visibility into agent performance
- Enable remote control of poker agents
- Display live statistics, charts, and hand history
- Handle WebSocket connections and error recovery

### **4. Agent Personality System**

**Purpose**: Configurable behavior profiles for different playing styles

**Architecture:**
```python
@dataclass
class PersonalityProfile:
    # Playing style parameters
    aggression: float       # 0.0-1.0 (passive to aggressive)
    tightness: float        # 0.0-1.0 (loose to tight)  
    deception: float        # 0.0-1.0 (honest to deceptive)
    
    # Image management
    image_strategy: str     # "harmless", "intimidating", "professional"
    avatar_choice: int      # Consistent avatar selection
    name_pattern: str       # Naming convention for the persona
    
    # Behavioral patterns
    decision_speed: str     # "fast", "normal", "slow" 
    break_frequency: float  # How often to take breaks
    tilt_resistance: float  # Response to bad beats
    
    # Advanced features
    opponent_modeling: bool # Track opponent patterns
    meta_game: bool         # Adjust image based on results

class PersonalityEngine:
    def __init__(self, profile: PersonalityProfile):
        self.profile = profile
        self.decision_modifier = self._create_decision_modifier()
        self.timing_modifier = self._create_timing_modifier()
    
    def modify_decision(self, base_action: Action, context: GameContext) -> Action:
        # Apply personality-specific modifications
        return self.decision_modifier.apply(base_action, context, self.profile)
    
    def get_decision_timing(self, situation_complexity: str) -> float:
        base_time = self._base_decision_time(situation_complexity)
        return self.timing_modifier.apply(base_time, self.profile)
```

## Data Flow Architecture

### **Real-Time Game State Pipeline**

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Poker Site  │───▶│ Network     │───▶│ Game State  │───▶│ Agent       │
│ (WebSocket) │    │ Interceptor │    │ Parser      │    │ Decision    │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                            │                   │                │
                            ▼                   ▼                ▼
                   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
                   │ Raw Message │    │ Structured  │    │ Poker       │
                   │ Queue       │    │ Game State  │    │ Action      │
                   └─────────────┘    └─────────────┘    └─────────────┘
                            │                   │                │
                            ▼                   ▼                ▼
                   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
                   │ Dashboard   │    │ Statistics  │    │ Browser     │
                   │ Updates     │    │ Tracking    │    │ Execution   │
                   └─────────────┘    └─────────────┘    └─────────────┘
```

### **Statistical Aggregation Pipeline**

```python
class StatisticsAggregator:
    def __init__(self):
        self.raw_events = []
        self.session_stats = SessionStats()
        self.long_term_stats = LongTermStats()
    
    def process_hand_completion(self, hand_result: HandResult):
        # Update immediate statistics
        self.session_stats.add_hand(hand_result)
        self.long_term_stats.add_hand(hand_result)
        
        # Calculate derived metrics
        win_rate = self.long_term_stats.calculate_win_rate()
        hourly_rate = self.session_stats.calculate_hourly_rate()
        
        # Broadcast to dashboard
        self.notify_dashboard({
            'win_rate': win_rate,
            'hourly_rate': hourly_rate,
            'session_profit': self.session_stats.total_profit,
            'total_hands': self.long_term_stats.total_hands
        })
```

## Security & Stealth Architecture

### **Anti-Detection Layers**

**Layer 1: Browser Fingerprinting**
```python
class BrowserFingerprint:
    @staticmethod
    def randomize_fingerprint():
        return {
            'user_agent': random.choice(REALISTIC_USER_AGENTS),
            'viewport': random.choice(COMMON_RESOLUTIONS),
            'timezone': random.choice(US_TIMEZONES),
            'language': 'en-US,en;q=0.9',
            'plugins': generate_realistic_plugin_list()
        }
```

**Layer 2: Behavioral Patterns**
```python  
class HumanBehaviorEngine:
    def __init__(self):
        self.decision_patterns = DecisionTimingModel()
        self.mouse_patterns = MouseMovementModel()
        self.session_patterns = SessionManagementModel()
    
    def generate_decision_time(self, complexity: str, recent_history: List[float]) -> float:
        base_time = self.decision_patterns.get_base_time(complexity)
        variance = self._calculate_human_variance(recent_history)
        return base_time + variance
```

**Layer 3: Traffic Analysis**
```python
class TrafficAnalyzer:
    def __init__(self):
        self.request_patterns = []
        self.timing_patterns = []
    
    def analyze_suspicion_level(self) -> float:
        # Check for bot-like patterns
        if self._has_too_regular_timing():
            return 0.8  # High suspicion
        elif self._has_unusual_request_patterns():
            return 0.6  # Medium suspicion
        else:
            return 0.2  # Low suspicion
```

## Performance & Scalability

### **Component Performance Characteristics**

| Component | CPU Usage | Memory Usage | Network I/O | Scaling Factor |
|-----------|-----------|--------------|-------------|----------------|
| Browser Manager | Medium | High | Low | 1 per agent |
| Network Interceptor | Low | Low | Medium | 1 per agent |
| Game Engine | Low | Low | None | Shared |
| Dashboard | Low | Medium | Medium | 1 per system |
| Agent Logic | Medium | Low | None | 1 per agent |

### **Scaling Architecture**

```python
class MultiAgentManager:
    def __init__(self, max_agents: int = 4):
        self.agent_pool = []
        self.resource_monitor = ResourceMonitor()
        self.load_balancer = AgentLoadBalancer()
    
    async def spawn_agent(self, personality: PersonalityProfile) -> WebPokerAgent:
        if self.resource_monitor.can_spawn_agent():
            agent = WebPokerAgent(personality=personality)
            await agent.start()
            self.agent_pool.append(agent)
            return agent
        else:
            raise ResourceExhaustedException("Cannot spawn more agents")
    
    async def balance_load(self):
        # Distribute agents across available resources
        for agent in self.agent_pool:
            optimal_resources = self.load_balancer.calculate_optimal_allocation(agent)
            await agent.migrate_resources(optimal_resources)
```

## Error Handling & Recovery

### **Error Categories & Strategies**

**1. Network Errors**
```python
class NetworkErrorHandler:
    async def handle_connection_lost(self, agent: WebPokerAgent):
        # Exponential backoff reconnection
        for attempt in range(5):
            delay = 2 ** attempt
            await asyncio.sleep(delay)
            
            try:
                await agent.reconnect()
                return True
            except ConnectionError:
                continue
        
        # Escalate to human intervention
        await self.request_manual_intervention(agent)
```

**2. Site Changes**
```python
class SiteChangeDetector:
    def detect_layout_change(self, screenshot: bytes) -> bool:
        current_hash = self._calculate_visual_hash(screenshot)
        if current_hash not in self.known_layouts:
            self.log_potential_site_change(current_hash)
            return True
        return False
    
    async def adapt_to_changes(self, agent: WebPokerAgent):
        # Attempt automatic adaptation
        if await self._try_automatic_adaptation():
            return True
        
        # Fall back to manual recalibration
        await self._request_recalibration()
```

**3. Detection Events**  
```python
class DetectionResponseSystem:
    def __init__(self):
        self.threat_levels = {
            'low': self._handle_low_threat,
            'medium': self._handle_medium_threat,  
            'high': self._handle_high_threat
        }
    
    async def _handle_high_threat(self, agent: WebPokerAgent):
        # Immediate shutdown and cooldown period
        await agent.emergency_shutdown()
        await self._initiate_cooldown_period(hours=24)
        await self._rotate_fingerprint()
```

## Testing Architecture

### **Test Pyramid Structure**

```
                ┌─────────────────┐
                │   End-to-End    │  ◄─ Full system integration
                │      Tests      │     Live site interaction
                └─────────────────┘
              ┌─────────────────────┐
              │  Integration Tests  │  ◄─ Component interaction
              │                     │     API contracts
              └─────────────────────┘
            ┌─────────────────────────┐
            │     Unit Tests          │  ◄─ Individual functions
            │                         │     Pure logic testing
            └─────────────────────────┘
```

**Unit Test Strategy:**
```python
class TestPokerGameEngine:
    def test_hand_evaluation(self):
        # Test pure poker logic
        royal_flush = Hand([Card('A','♠'), Card('K','♠'), ...])
        assert royal_flush.evaluate().name == "ROYAL_FLUSH"
    
    def test_betting_validation(self):
        # Test game rules enforcement
        game = GameState(players, blinds=(5, 10))
        invalid_action = Action("p1", ActionType.BET, amount=-10)
        assert not game.is_valid_action(invalid_action)

class TestHumanBehavior:
    def test_decision_timing_variance(self):
        # Test behavioral patterns
        behavior = HumanBehaviorSimulator()
        times = [behavior.get_decision_time("normal") for _ in range(100)]
        assert statistics.stdev(times) > 0.5  # Should have variance
```

**Integration Test Strategy:**
```python
class TestWebAgentIntegration:
    @pytest.mark.asyncio
    async def test_network_to_game_state_pipeline(self):
        # Test message flow from network to game state
        interceptor = NetworkInterceptor()
        parser = GameStateParser()
        
        mock_message = create_mock_deal_cards_message()
        game_state = parser.parse_message(mock_message)
        
        assert len(game_state['my_cards']) == 2
        assert game_state['betting_round'] == 'preflop'
```

## Monitoring & Observability

### **Metrics Collection**

```python
class MetricsCollector:
    def __init__(self):
        self.counters = defaultdict(int)
        self.timers = defaultdict(list)
        self.gauges = defaultdict(float)
    
    def increment(self, metric: str, value: int = 1):
        self.counters[metric] += value
    
    def time_operation(self, operation: str):
        return Timer(operation, self.timers)
    
    def set_gauge(self, metric: str, value: float):
        self.gauges[metric] = value

# Usage throughout system
metrics = MetricsCollector()

@metrics.time_operation('hand_evaluation')
def evaluate_hand(cards):
    return hand_evaluator.evaluate(cards)

metrics.increment('hands_played')
metrics.set_gauge('current_profit', agent.session_profit)
```

### **Logging Strategy**

```python
import structlog

# Structured logging for better analysis
logger = structlog.get_logger()

# Agent decision logging
logger.info("agent_decision", 
           agent_id="GrandpaJoe42",
           action="raise", 
           amount=50,
           hand_strength=0.73,
           pot_odds=0.25,
           position="button")

# Performance logging  
logger.info("performance_update",
           session_duration=3600,
           hands_played=45, 
           win_rate=0.67,
           profit=125.50)
```

## Deployment Architecture

### **Development Environment**
```bash
# Local development setup
python start_live_dashboard.py

# Components:
# - Live Agent Server (localhost:8000)
# - React Dashboard (localhost:3000) 
# - WebSocket connections for real-time updates
```

### **Production Environment**
```bash
# Containerized deployment
docker-compose up

# Components:
# - Agent containers with resource limits
# - Dashboard with SSL/HTTPS
# - Monitoring and logging infrastructure
# - Database for persistent statistics
```

### **Scaling Configuration**
```yaml
# docker-compose.yml
version: '3.8'
services:
  agent-manager:
    image: holdem-agent:latest
    environment:
      - MAX_AGENTS=4
      - HEADLESS_MODE=true
    resources:
      limits:
        memory: 4G
        cpus: '2.0'
  
  dashboard:
    image: holdem-dashboard:latest
    ports:
      - "3000:3000"
    environment:
      - API_URL=http://agent-manager:8000
```

## Related Documentation
- [Game Engine](../src/holdem/game/README.md) - Poker logic implementation
- [Web Integration](../src/holdem/web/README.md) - Browser automation details  
- [Agents](../src/holdem/agents/README.md) - AI decision-making components
- [Dashboard](../holdem-dashboard/README.md) - Monitoring interface
- [Examples](../examples/README.md) - Usage examples and demos
- [Main README](../README.md) - Project overview and quick start