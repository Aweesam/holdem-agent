'use client';

import { Activity, DollarSign, TrendingUp, Users, RefreshCw } from 'lucide-react';
import StatsCard from '@/components/StatsCard';
import PerformanceChart from '@/components/PerformanceChart';
import RecentHands from '@/components/RecentHands';
import LiveStats from '@/components/LiveStats';
import { useWebSocket } from '@/hooks/useWebSocket';

export default function Dashboard() {
  const { data, isConnected, error, reconnect } = useWebSocket('ws://localhost:8000/ws');

  // Use WebSocket data if available, otherwise fallback to defaults
  const stats = data ? {
    totalHands: data.stats.total_hands,
    winRate: data.stats.win_rate,
    totalProfit: data.stats.total_profit,
    currentSession: data.stats.current_session,
    hourlyRate: data.stats.hourly_rate,
    activeTables: data.stats.active_tables,
    sessionTime: data.stats.session_time,
  } : {
    totalHands: 0,
    winRate: 0,
    totalProfit: 0,
    currentSession: 0,
    hourlyRate: 0,
    activeTables: 0,
    sessionTime: 0,
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Agent Dashboard</h1>
          <p className="text-gray-600">Real-time performance monitoring</p>
          {error && (
            <p className="text-red-600 text-sm mt-1">⚠️ {error}</p>
          )}
        </div>
        <div className="flex items-center space-x-4">
          {!isConnected && (
            <button
              onClick={reconnect}
              className="flex items-center space-x-2 px-3 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              <RefreshCw className="h-4 w-4" />
              <span>Reconnect</span>
            </button>
          )}
          <div className="flex items-center space-x-2">
            <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-400' : 'bg-red-400'} animate-pulse`}></div>
            <span className="text-sm text-gray-600">
              {isConnected ? 'Connected' : 'Disconnected'}
            </span>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard
          title="Total Hands"
          value={stats.totalHands.toLocaleString()}
          icon={<Activity className="h-6 w-6 text-blue-600" />}
          trend="+2.4%"
          trendUp={true}
        />
        <StatsCard
          title="Win Rate"
          value={`${stats.winRate.toFixed(1)}%`}
          icon={<TrendingUp className="h-6 w-6 text-green-600" />}
          trend="+0.8%"
          trendUp={true}
        />
        <StatsCard
          title="Total Profit"
          value={`$${stats.totalProfit.toFixed(0)}`}
          icon={<DollarSign className="h-6 w-6 text-green-600" />}
          trend="+$125"
          trendUp={true}
        />
        <StatsCard
          title="Active Tables"
          value={stats.activeTables.toString()}
          icon={<Users className="h-6 w-6 text-purple-600" />}
          trend="Stable"
          trendUp={true}
        />
      </div>

      {/* Charts and Live Data */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Performance Chart</h2>
          <PerformanceChart />
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Live Statistics</h2>
          <LiveStats 
            hourlyRate={stats.hourlyRate}
            currentSession={stats.currentSession}
            sessionTime={stats.sessionTime}
          />
        </div>
      </div>

      {/* Recent Hands */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Recent Hands</h2>
        </div>
        <RecentHands hands={data?.recent_hands || []} />
      </div>
    </div>
  );
}
