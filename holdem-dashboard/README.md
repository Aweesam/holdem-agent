# 📊 Holdem Agent Dashboard

Modern React-based dashboard for real-time monitoring and control of poker agents.

## Overview

The dashboard provides a comprehensive interface for managing poker agents, monitoring their performance, and analyzing their play in real-time. Built with Next.js, React, and WebSocket technology for live updates.

## Features

### **🎮 Agent Control**
- **Start/Stop/Pause**: Remote control of poker agents
- **Configuration**: Browser settings, site URLs, headless mode
- **Status Monitoring**: Real-time agent status and connection health
- **Error Handling**: Automatic reconnection and error reporting

### **📈 Performance Analytics**  
- **Live Statistics**: Win rate, profit/loss, hourly rate tracking
- **Interactive Charts**: Profit curves, performance over time
- **Session Analytics**: Current session profit, uptime, hands played
- **Historical Data**: Long-term performance trends and analysis

### **🃏 Hand History**
- **Real-time Updates**: Live hand results as they happen
- **Detailed Records**: Position, hole cards, final results, pot size
- **Hand Analysis**: Hand strength, action sequence, profit per hand
- **Filtering/Search**: Find specific hands or patterns

### **🔄 Live Updates**
- **WebSocket Integration**: 3-second real-time updates
- **Connection Status**: Visual indicators for dashboard/agent connectivity  
- **Auto-Reconnection**: Automatic reconnection on connection loss
- **Error Notifications**: Alert system for issues and status changes

## Technology Stack

### **Frontend**
- **Next.js 15**: React framework with App Router
- **React 19**: Component-based UI with hooks
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Modern, responsive styling
- **Lucide Icons**: Clean, consistent iconography

### **Data Visualization**
- **Recharts**: Interactive charts and graphs
- **Real-time Updates**: Live data streaming via WebSocket
- **Responsive Design**: Mobile-friendly layouts
- **Performance Optimized**: Efficient re-rendering and updates

### **Backend Integration**
- **WebSocket Client**: Real-time communication with agent server
- **REST API**: HTTP endpoints for agent control and data fetching
- **Error Handling**: Robust error boundaries and recovery
- **State Management**: React state with custom hooks

## Quick Start

### **1. Install Dependencies**
```bash
cd holdem-dashboard
npm install
```

### **2. Development Mode**  
```bash
# Start Next.js dev server
npm run dev

# Dashboard available at http://localhost:3000
```

### **3. Production Build**
```bash  
# Build optimized version
npm run build
npm start
```

## Component Architecture

### **Main Dashboard** (`src/app/page.tsx`)
Central dashboard layout with all major components.

```tsx
export default function Dashboard() {
  const { data, isConnected, error, reconnect } = useWebSocket('ws://localhost:8000/ws');
  
  return (
    <div className="space-y-6">
      <StatsCards stats={data?.stats} />
      <AgentControl isConnected={isConnected} />
      <PerformanceChart data={data?.performance} />
      <RecentHands hands={data?.recent_hands} />
    </div>
  );
}
```

### **Core Components**

**AgentControl** (`src/components/AgentControl.tsx`)
- Agent start/stop/pause controls
- Configuration settings (headless mode, site URL)
- Real-time status display and error handling

**StatsCard** (`src/components/StatsCard.tsx`)  
- Individual metric displays (win rate, profit, hands played)
- Trend indicators and visual formatting
- Responsive grid layout

**PerformanceChart** (`src/components/PerformanceChart.tsx`)
- Interactive profit/loss chart over time
- Recharts integration with smooth animations
- Hover tooltips and zoom functionality

**RecentHands** (`src/components/RecentHands.tsx`)
- Live-updating hand history table
- Detailed hand information with cards and results
- Profit highlighting and position indicators

**LiveStats** (`src/components/LiveStats.tsx`)
- Session-specific metrics (hourly rate, session time)
- Real-time counters and progress indicators
- Break tracking and status monitoring

### **Custom Hooks**

**useWebSocket** (`src/hooks/useWebSocket.ts`)
Real-time WebSocket connection management.

```tsx
const { data, isConnected, error, reconnect } = useWebSocket(url);

// Features:
// - Automatic reconnection on disconnect
// - Message parsing and error handling  
// - Connection status tracking
// - Data caching and state management
```

## Data Flow

### **Real-time Updates**
```
WebPokerAgent → LiveAgentServer → WebSocket → Dashboard
     ↓               ↓              ↓           ↓
- Hand results    - Statistics   - JSON msgs  - UI updates
- Agent status    - Performance  - Broadcasts - Live charts  
- Profit/loss     - Hand history - Real-time  - Notifications
```

### **Agent Control**
```
Dashboard → HTTP POST → LiveAgentServer → WebPokerAgent
    ↓           ↓             ↓               ↓
- Start/Stop  - API calls  - Agent control - Browser automation
- Settings    - Validation - Status updates - Poker gameplay
- Config      - Responses  - Error handling - Live monitoring
```

## Configuration

### **Environment Variables**
```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
```

### **API Endpoints**
```typescript
// Dashboard connects to these agent server endpoints
const API_ENDPOINTS = {
  stats: '/api/stats',              // Get current statistics  
  hands: '/api/hands',              // Get recent hand history
  performance: '/api/performance',   // Get performance data
  control: '/api/agent/control',    // Start/stop agent
  status: '/api/agent/status',      // Get agent status
  health: '/api/health',            // System health check
  websocket: '/ws'                  // Real-time updates
};
```

### **WebSocket Messages**
```typescript
// Message types the dashboard handles
interface WebSocketMessage {
  type: 'initial_data' | 'stats_update' | 'ping';
  data?: {
    stats: AgentStats;
    recent_hands: HandRecord[];
    performance: PerformancePoint[];
  };
}
```

## Styling and Design

### **Design System**
- **Colors**: Tailwind CSS color palette with custom poker-themed accents
- **Typography**: Clean, readable fonts with proper hierarchy
- **Spacing**: Consistent spacing system using Tailwind utilities
- **Icons**: Lucide React icons for consistency and performance

### **Responsive Breakpoints**
```css
/* Mobile-first responsive design */
sm: '640px',   /* Small devices */
md: '768px',   /* Medium devices */ 
lg: '1024px',  /* Large devices */
xl: '1280px',  /* Extra large devices */
2xl: '1536px'  /* 2X large devices */
```

### **Component Patterns**
```tsx
// Consistent card layout pattern
<div className="bg-white rounded-lg shadow-md p-6">
  <h2 className="text-xl font-semibold text-gray-800 mb-4">Title</h2>
  <div className="space-y-4">
    {/* Content */}
  </div>
</div>

// Status indicator pattern  
<div className={`w-3 h-3 rounded-full ${
  isConnected ? 'bg-green-400' : 'bg-red-400'
} animate-pulse`} />
```

## Development

### **Code Structure**
```
holdem-dashboard/
├── src/
│   ├── app/              # Next.js App Router pages
│   │   ├── page.tsx      # Main dashboard page
│   │   ├── layout.tsx    # Root layout
│   │   └── globals.css   # Global styles
│   ├── components/       # Reusable React components
│   │   ├── AgentControl.tsx
│   │   ├── StatsCard.tsx
│   │   ├── PerformanceChart.tsx
│   │   └── RecentHands.tsx
│   └── hooks/            # Custom React hooks
│       └── useWebSocket.ts
├── public/               # Static assets
├── package.json          # Dependencies and scripts
└── tailwind.config.js    # Tailwind CSS configuration
```

### **Development Scripts**
```bash
# Development server with hot reload
npm run dev

# Type checking
npm run type-check  

# Linting
npm run lint

# Production build
npm run build

# Start production server
npm start
```

### **Code Quality**
- **TypeScript**: Full type safety with strict mode
- **ESLint**: Code linting with Next.js recommended rules
- **Prettier**: Consistent code formatting
- **Component Testing**: React Testing Library for component tests

## Deployment

### **Development Deployment**
```bash
# Start with live agent server
cd /home/envy/holdem
python start_live_dashboard.py

# Dashboard: http://localhost:3000
# API: http://localhost:8000
```

### **Production Deployment**  
```bash
# Build optimized version
npm run build

# Deploy to hosting provider
# Configure environment variables
# Set up SSL/HTTPS for WebSocket connections
```

### **Docker Deployment**
```dockerfile
# Dockerfile example
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

## Monitoring and Analytics

### **Performance Metrics**
- **Component Render Times**: React DevTools profiling
- **WebSocket Connection Health**: Connection uptime tracking  
- **API Response Times**: Network request monitoring
- **Real-time Update Latency**: WebSocket message timing

### **User Experience**
- **Loading States**: Skeleton screens and loading indicators
- **Error States**: Graceful error handling with recovery options
- **Connection States**: Clear status indicators and reconnection  
- **Responsive Design**: Optimal experience on all device sizes

## Troubleshooting

### **Common Issues**

**WebSocket Connection Failed**
```bash
# Check if agent server is running
curl http://localhost:8000/api/health

# Verify WebSocket endpoint
wscat -c ws://localhost:8000/ws
```

**Dashboard Not Updating**
```bash
# Check browser console for errors
# Verify API server is responding
# Check WebSocket connection status in dashboard
```

**Agent Control Not Working**
```bash
# Verify agent server API endpoints
curl -X POST http://localhost:8000/api/agent/control \
  -H "Content-Type: application/json" \
  -d '{"action": "status"}'
```

### **Debug Mode**
```bash
# Start with debug logging
DEBUG=* npm run dev

# Enable WebSocket debug
DEBUG=socket.io* npm run dev
```

## Related Documentation
- [Live Agent Server](../live_agent_server.py) - Backend API integration
- [Web Poker Agent](../src/holdem/web/README.md) - Agent system being monitored
- [Main README](../README.md) - Project overview and complete setup
- [Dashboard Features](../DASHBOARD_README.md) - Detailed feature documentation