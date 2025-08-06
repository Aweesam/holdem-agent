# 🌐 Web Integration & Stealth

Browser automation and network monitoring for live poker site interaction.

## Overview

This package handles all web-based interactions for live poker play, including stealth browser automation, human behavior simulation, and real-time game state monitoring.

## Core Components

### **BrowserManager** (`browser_manager.py`)
Manages stealth browser instances with anti-detection measures.

**Features:**
- Randomized user agents and viewports
- Human-like mouse movements and clicking  
- Realistic typing speeds and timing
- Anti-automation detection measures
- Session management and cookie handling

**Usage:**
```python
from holdem.web import BrowserManager

with BrowserManager(headless=False) as browser:
    success = browser.navigate_to_game("https://clubwptgold.com/game/")
    element = browser.wait_for_element(By.ID, "call-button")
    browser.human_click(element)
```

### **HumanBehaviorSimulator** (`human_behavior.py`)  
Simulates realistic human behavior patterns to avoid detection.

**Behavior Types:**
- **Decision Timing**: Variable think times based on situation complexity
- **Mouse Movement**: Natural cursor paths with micro-adjustments
- **Typing Patterns**: Realistic WPM with occasional corrections
- **Break Patterns**: Human-like pauses and session management
- **Micro-behaviors**: Random scrolls, hovers, window focus checks

**Usage:**
```python
from holdem.web import HumanBehaviorSimulator

behavior_sim = HumanBehaviorSimulator()

# Wait realistic time for complex decision
behavior_sim.wait_decision_time("complex")

# Get natural typing delay
delay = behavior_sim.get_typing_delay(len("raise 100"))
```

### **NetworkInterceptor** (`network_interceptor.py`)
Monitors WebSocket and HTTP traffic to extract real-time game state.

**Capabilities:**
- WebSocket message interception
- Protocol parsing (JSON/binary)
- Real-time game state reconstruction
- Message type classification
- Error handling and reconnection

**Usage:**
```python
from holdem.web import ClubWPTNetworkInterceptor

interceptor = ClubWPTNetworkInterceptor(user_id=449469)
interceptor.set_game_state_callback(handle_game_update)
await interceptor.connect()
```

### **WebPokerAgent** (`web_poker_agent.py`)
Complete integration of browser automation + poker intelligence.

**Features:**
- Combines all web components into unified agent
- Real-time dashboard reporting  
- Live statistics and performance tracking
- Agent control (start/stop/pause)
- Error recovery and session management

## Club WPT Gold Integration

### **Site Architecture Analysis**
- **Rendering**: Cocos2d-js HTML5 canvas (not traditional DOM)
- **Communication**: WebSocket to `wss://gate.clubwptgold.com/`
- **Authentication**: Token-based via `https://apigate.clubwptgold.com/authserver`
- **Game State**: Binary/JSON mixed protocol over WebSocket

### **Interaction Strategy**
```python
# 1. Stealth browser connection
browser = BrowserManager(headless=True)
browser.navigate_to_game("https://clubwptgold.com/game/")

# 2. Network monitoring for game state
interceptor = ClubWPTNetworkInterceptor()  
await interceptor.connect()

# 3. Canvas-based action execution
def execute_action(action_type):
    # Calculate precise canvas coordinates
    coords = get_action_button_coords(action_type)
    
    # Human-like click with variations
    browser.human_click_canvas(coords[0], coords[1])
```

### **Current Agent: GrandpaJoe42**
- **User ID**: 449469
- **Avatar**: Elderly gentleman (#17)
- **Personality**: Tight-aggressive with "harmless grandpa" image
- **Target Site**: Club WPT Gold (https://clubwptgold.com/)

## Stealth Technology

### **Anti-Detection Measures**

**Browser Fingerprinting:**
```python
# Randomized browser fingerprint
options.add_argument(f"--user-agent={random_user_agent()}")
options.add_argument(f"--window-size={random_viewport()}")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
```

**Human Behavior:**
```python
# Realistic decision timing based on situation
def get_decision_time(complexity):
    if complexity == "simple":   # Obvious fold/call
        return random.uniform(0.3, 1.2)  
    elif complexity == "complex": # Difficult river decision
        return random.uniform(4.0, 12.0)
    else:
        return random.uniform(1.5, 8.0)
```

**Traffic Patterns:**
```python
# Human-like navigation patterns
browser.get("https://google.com")      # Visit normal site first
time.sleep(random.uniform(1, 3))       # Human pause
browser.get("https://clubwptgold.com") # Then poker site
```

### **Detection Avoidance**
- **No DOM Manipulation**: Use canvas clicking only
- **Variable Timing**: Realistic decision speeds with human variance
- **Session Patterns**: Natural break times and session lengths  
- **Error Handling**: Graceful failures that mimic human confusion
- **Traffic Analysis**: Avoid suspicious request patterns

## Development Workflow

### **1. Site Analysis**
```bash
# Capture network traffic for analysis
python examples/network_monitoring_demo.py

# Test browser automation  
python examples/web_agent_demo.py
```

### **2. Agent Development**
```python
from holdem.web import WebPokerAgent

# Create and configure agent
agent = WebPokerAgent(player_id="449469", name="GrandpaJoe42")
agent.register_dashboard_callback(dashboard_update)

# Test in simulation first
await agent.start(headless=True, site_url="https://clubwptgold.com/game/")
```

### **3. Live Testing**
```bash  
# Launch live dashboard for monitoring
python start_live_dashboard.py

# Use dashboard to start/stop agent safely
# Monitor performance in real-time
```

## Canvas Interaction

### **Coordinate Mapping**
Since Club WPT Gold uses HTML5 canvas, we need precise coordinate mapping:

```python
# Action button coordinates (approximate)
ACTION_BUTTONS = {
    "fold": (x1, y1),
    "check": (x2, y2), 
    "call": (x3, y3),
    "bet": (x4, y4),
    "raise": (x5, y5)
}

def click_action_button(action_type):
    base_x, base_y = ACTION_BUTTONS[action_type]
    
    # Add human-like coordinate variation
    x, y = behavior_sim.vary_click_position(base_x, base_y, variation=5)
    
    # Execute click with realistic timing
    time.sleep(behavior_sim.get_mouse_movement_delay())
    browser.click_canvas_coordinate(x, y)
```

### **Bet Input Handling**
```python
def input_bet_amount(amount):
    # Find bet input field
    bet_input = browser.wait_for_element(By.CLASS_NAME, "cocosEditBox")
    
    # Clear and type with human speed
    bet_input.clear()
    browser.human_type(bet_input, str(amount))
    
    # Confirm bet
    confirm_button = get_confirm_button_coords()
    browser.human_click_canvas(*confirm_button)
```

## Error Handling

### **Connection Issues**
```python
async def handle_disconnect():
    self.stats.status = AgentStatus.ERROR
    self.stats.last_action = "Connection lost - attempting reconnect"
    
    # Wait human-like time before reconnecting
    await asyncio.sleep(random.uniform(10, 30))
    
    # Attempt graceful reconnection
    await self.reconnect_with_backoff()
```

### **Site Changes**
```python
def detect_layout_change():
    # Take screenshot for analysis
    screenshot = browser.get_screenshot()
    
    # Compare with known good state
    if not verify_expected_elements(screenshot):
        # Fallback to manual intervention
        self.request_human_assistance("Site layout changed")
```

## Performance Optimization

### **Resource Management**
- Disable images and ads for faster loading
- Use headless mode for production
- Implement connection pooling for multiple agents
- Monitor memory usage and browser cleanup

### **Network Efficiency** 
- Cache static resources locally
- Minimize unnecessary requests  
- Use WebSocket keep-alive efficiently
- Implement smart reconnection strategies

## Security Considerations

### **Account Safety**
- Never log sensitive authentication data
- Use secure credential storage
- Implement rate limiting for actions
- Monitor for unusual detection patterns

### **Traffic Analysis**
- Avoid predictable timing patterns
- Randomize session characteristics
- Use realistic break patterns
- Monitor for site countermeasures

## Testing

### **Unit Tests**
```bash
# Test individual components
python -m pytest tests/test_web_components.py
```

### **Integration Tests**
```bash
# Test full web agent workflow  
python -m pytest tests/test_web_agent.py
```

### **Live Testing**
```bash
# Safe testing with monitoring
python examples/safe_live_test.py
```

## Related Documentation
- [Agents](../agents/README.md) - AI decision-making logic
- [Game Engine](../game/README.md) - Poker game mechanics  
- [Dashboard](../../holdem-dashboard/README.md) - Monitoring interface
- [Main README](../../../README.md) - Project overview