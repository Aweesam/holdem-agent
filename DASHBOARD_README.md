# 🎰 Holdem Agent Dashboard

A real-time web dashboard for monitoring Texas Hold'em poker agent performance, built with Next.js and Python FastAPI.

## 🚀 Quick Start

### Prerequisites
- Python 3.9+ with venv activated
- Node.js and npm installed
- All project dependencies installed

### Starting the Dashboard

1. **Auto-start both servers:**
   ```bash
   cd /home/envy/holdem
   python start_dashboard.py
   ```

2. **Manual start:**
   ```bash
   # Terminal 1 - API Server
   cd /home/envy/holdem
   source venv/bin/activate
   python api_server.py
   
   # Terminal 2 - Frontend
   cd /home/envy/holdem/holdem-dashboard  
   npm run dev
   ```

### Access the Dashboard
- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000  
- **API Documentation**: http://localhost:8000/docs

## 📊 Features

### Real-Time Statistics
- **Live Updates**: WebSocket connection provides 3-second updates
- **Performance Metrics**: Win rate, profit/loss, hourly rate
- **Session Tracking**: Current session time and profitability

### Interactive Dashboard
- **Stats Cards**: Key metrics with trend indicators
- **Performance Chart**: Real-time profit visualization
- **Recent Hands**: Live hand history with results
- **Connection Status**: Visual connection indicator with reconnect button

### API Endpoints
- `GET /api/stats` - Current agent statistics
- `GET /api/hands?limit=20` - Recent hand history
- `GET /api/performance?hours=4` - Performance data points
- `GET /api/health` - System health check
- `WS /ws` - WebSocket for real-time updates

## 🎯 Key Metrics Tracked

### Agent Performance
- **Total Hands Played**: Lifetime hand count
- **Win Rate**: Percentage of hands won
- **Total Profit**: Cumulative profit/loss
- **Active Tables**: Number of concurrent tables

### Session Analytics  
- **Session Time**: Current session duration
- **Session Profit**: Current session P&L
- **Hourly Rate**: Profit per hour calculation

### Hand History
- **Recent Hands**: Last 50 hands with details
- **Position**: Seat position (BTN, SB, BB, etc.)
- **Hole Cards**: Starting hand cards
- **Result**: Win/Loss with profit amount
- **Hand Strength**: Final hand ranking

## 🔧 Technical Architecture

### Backend (FastAPI)
- **Real-time Updates**: Background task updates stats every 3 seconds
- **WebSocket Support**: Live data broadcasting to all connected clients
- **Mock Data**: Simulated poker game data for demonstration
- **CORS Enabled**: Allows frontend connections

### Frontend (Next.js)
- **React Components**: Modular, reusable dashboard components
- **WebSocket Integration**: Custom hook for real-time connectivity
- **Responsive Design**: Mobile-friendly Tailwind CSS styling
- **Charts**: Recharts for performance visualization

### Data Flow
1. API server generates/updates mock agent data
2. WebSocket broadcasts updates to connected clients
3. Frontend receives updates via useWebSocket hook
4. React components re-render with new data
5. Dashboard shows live statistics and charts

## 🎮 Demo Data

The system includes realistic mock data:
- **Simulated Hands**: Random poker hands with realistic outcomes
- **Performance Metrics**: Fluctuating win rates and profit margins  
- **Session Tracking**: Live session timer and statistics
- **Hand Evaluations**: Uses actual poker hand rankings

## 🛠 Development

### Adding New Metrics
1. Update `AgentStats` model in `api_server.py`
2. Add UI component in dashboard
3. Update WebSocket data flow

### Custom Styling
- Tailwind CSS classes in components
- Responsive breakpoints included
- Dark mode ready (toggle not implemented)

### Real Agent Integration
Replace mock data generation in `api_server.py` with actual agent statistics from your poker bot implementation.

## 🚨 Notes

- **Demo Mode**: Currently uses simulated data
- **Port Usage**: API (8000), Frontend (3000)
- **Auto-Reconnect**: Frontend automatically reconnects on WebSocket disconnect
- **Performance**: Optimized for real-time updates with minimal CPU usage

## 🔄 Real-Time Features

The dashboard automatically updates:
- Statistics every 3 seconds
- New hands as they're played
- Performance charts with sliding window
- Connection status with visual indicators

---

**Ready to monitor your poker agent in real-time!** 🎲