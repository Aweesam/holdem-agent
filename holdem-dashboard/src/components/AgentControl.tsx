'use client';

import { useState, useEffect } from 'react';
import { Play, Square, Pause, Settings, Wifi, WifiOff } from 'lucide-react';

interface AgentControlProps {
  isConnected: boolean;
}

interface AgentStatus {
  status: string;
  message: string;
  uptime_seconds: number;
}

export default function AgentControl({ isConnected }: AgentControlProps) {
  const [agentStatus, setAgentStatus] = useState<AgentStatus>({
    status: 'stopped',
    message: 'Agent not started',
    uptime_seconds: 0
  });
  const [isLoading, setIsLoading] = useState(false);
  const [siteUrl, setSiteUrl] = useState('https://clubwptgold.com/');
  const [headless, setHeadless] = useState(false); // False for manual login
  const [token] = useState('');
  const [showSettings, setShowSettings] = useState(false);

  // Poll agent status
  useEffect(() => {
    const pollStatus = async () => {
      if (!isConnected) return;
      
      try {
        const response = await fetch('http://localhost:8000/api/agent/status');
        if (response.ok) {
          const status = await response.json();
          setAgentStatus(status);
        }
      } catch (error) {
        console.error('Failed to fetch agent status:', error);
      }
    };

    const interval = setInterval(pollStatus, 2000);
    pollStatus(); // Initial call
    
    return () => clearInterval(interval);
  }, [isConnected]);

  const controlAgent = async (action: string) => {
    setIsLoading(true);
    
    try {
      const response = await fetch('http://localhost:8000/api/agent/control', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          action,
          site_url: siteUrl || null,
          headless: headless,
          token: token || null
        }),
      });

      if (response.ok) {
        const result = await response.json();
        console.log(`Agent ${action}:`, result.message);
        
        // Update status immediately
        setAgentStatus(prev => ({
          ...prev,
          status: result.status,
          message: result.message
        }));
      } else {
        console.error(`Failed to ${action} agent`);
      }
    } catch (error) {
      console.error(`Error ${action}ing agent:`, error);
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'started':
      case 'running':
      case 'playing':
        return 'text-green-600';
      case 'connecting':
      case 'paused':
        return 'text-yellow-600';
      case 'error':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'started':
      case 'running':
      case 'playing':
        return <Wifi className="w-4 h-4 text-green-600" />;
      case 'connecting':
        return <Wifi className="w-4 h-4 text-yellow-600 animate-pulse" />;
      case 'paused':
        return <Pause className="w-4 h-4 text-yellow-600" />;
      case 'error':
        return <WifiOff className="w-4 h-4 text-red-600" />;
      default:
        return <WifiOff className="w-4 h-4 text-gray-600" />;
    }
  };

  const formatUptime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    
    if (hours > 0) {
      return `${hours}h ${minutes}m ${secs}s`;
    } else if (minutes > 0) {
      return `${minutes}m ${secs}s`;
    } else {
      return `${secs}s`;
    }
  };

  const isAgentRunning = ['started', 'running', 'playing', 'connecting'].includes(agentStatus.status);

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold text-gray-800">Agent Control</h2>
        <button
          onClick={() => setShowSettings(!showSettings)}
          className="p-2 text-gray-600 hover:text-gray-800 rounded-lg hover:bg-gray-100 transition-colors"
          title="Agent Settings"
        >
          <Settings className="w-5 h-5" />
        </button>
      </div>

      {/* Agent Status */}
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-2">
          {getStatusIcon(agentStatus.status)}
          <span className={`font-medium ${getStatusColor(agentStatus.status)}`}>
            {agentStatus.status.charAt(0).toUpperCase() + agentStatus.status.slice(1)}
          </span>
        </div>
        <p className="text-sm text-gray-600 mb-2">{agentStatus.message}</p>
        {agentStatus.uptime_seconds > 0 && (
          <p className="text-sm text-gray-500">
            Uptime: {formatUptime(agentStatus.uptime_seconds)}
          </p>
        )}
      </div>

      {/* Settings Panel */}
      {showSettings && (
        <div className="mb-6 p-4 bg-gray-50 rounded-lg border">
          <h3 className="font-medium text-gray-700 mb-3">Agent Settings</h3>
          
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-600 mb-1">
                Poker Site URL
              </label>
              <input
                type="text"
                value={siteUrl}
                onChange={(e) => setSiteUrl(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="https://clubwptgold.com/"
                disabled={isAgentRunning}
              />
              <p className="text-xs text-gray-500 mt-1">
                Website where agent will open Firefox for you to log in manually.
              </p>
            </div>
            
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="headless"
                checked={headless}
                onChange={(e) => setHeadless(e.target.checked)}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                disabled={isAgentRunning}
              />
              <label htmlFor="headless" className="text-sm text-gray-600">
                Run in headless mode (turn OFF to see browser window)
              </label>
            </div>
          </div>
        </div>
      )}

      {/* Control Buttons */}
      <div className="flex gap-3">
        {!isAgentRunning ? (
          <button
            onClick={() => controlAgent('start')}
            disabled={isLoading || !isConnected}
            className="flex-1 flex items-center justify-center gap-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-md font-medium transition-colors"
          >
            {isLoading ? (
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
            ) : (
              <Play className="w-4 h-4" />
            )}
            {isLoading ? 'Starting...' : 'Start Agent'}
          </button>
        ) : (
          <>
            <button
              onClick={() => controlAgent('pause')}
              disabled={isLoading}
              className="flex-1 flex items-center justify-center gap-2 bg-yellow-600 hover:bg-yellow-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-md font-medium transition-colors"
            >
              <Pause className="w-4 h-4" />
              Pause
            </button>
            
            <button
              onClick={() => controlAgent('stop')}
              disabled={isLoading}
              className="flex-1 flex items-center justify-center gap-2 bg-red-600 hover:bg-red-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-md font-medium transition-colors"
            >
              {isLoading ? (
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <Square className="w-4 h-4" />
              )}
              {isLoading ? 'Stopping...' : 'Stop Agent'}
            </button>
          </>
        )}
      </div>

      {/* Instructions and Warnings */}
      {!isAgentRunning && (
        <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-md">
          <p className="text-sm text-blue-700 font-medium mb-2">
            🎯 How GrandpaJoe42 Works:
          </p>
          <ol className="text-sm text-blue-700 space-y-1">
            <li>1. <strong>Agent opens Firefox</strong> and navigates to Club WPT Gold</li>
            <li>2. <strong>You log in manually</strong> (SMS verification, etc.)</li>
            <li>3. <strong>You select a poker table</strong> to play</li>
            <li>4. <strong>Agent detects table</strong> and takes over gameplay automatically</li>
            <li>5. <strong>Dashboard shows live stats</strong> as GrandpaJoe42 plays</li>
          </ol>
          <p className="text-sm text-blue-600 mt-2">
            💡 <strong>Tip:</strong> Keep headless mode OFF to see the browser window
          </p>
        </div>
      )}
      
      {/* Connection Warning */}
      {!isConnected && (
        <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-md">
          <p className="text-sm text-yellow-700">
            ⚠️ Dashboard not connected to API server. Agent control disabled.
          </p>
        </div>
      )}
    </div>
  );
}