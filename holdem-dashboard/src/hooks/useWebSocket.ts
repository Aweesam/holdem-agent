'use client';

import { useState, useEffect, useCallback } from 'react';

interface AgentStats {
  total_hands: number;
  win_rate: number;
  total_profit: number;
  current_session: number;
  hourly_rate: number;
  active_tables: number;
  session_time: number;
  last_updated: string;
}

interface HandHistory {
  id: number;
  timestamp: string;
  position: string;
  hole_cards: string;
  result: string;
  profit: number;
  hand_description: string;
  table_id: string;
}

interface PerformancePoint {
  timestamp: string;
  profit: number;
  hands_played: number;
  win_rate: number;
}

interface WebSocketData {
  stats: AgentStats;
  recent_hands: HandHistory[];
  performance: PerformancePoint[];
}

interface WebSocketMessage {
  type: string;
  data?: WebSocketData;
}

interface UseWebSocketReturn {
  data: WebSocketData | null;
  isConnected: boolean;
  error: string | null;
  reconnect: () => void;
}

export function useWebSocket(url: string): UseWebSocketReturn {
  const [data, setData] = useState<WebSocketData | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [ws, setWs] = useState<WebSocket | null>(null);

  const connect = useCallback(() => {
    try {
      const websocket = new WebSocket(url);
      
      websocket.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
        setError(null);
      };

      websocket.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          
          if (message.type === 'initial_data' || message.type === 'stats_update') {
            if (message.data) {
              setData(message.data);
            }
          } else if (message.type === 'ping') {
            // Handle ping message
            console.log('Received ping from server');
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
          setError('Error parsing server message');
        }
      };

      websocket.onclose = (event) => {
        console.log('WebSocket disconnected:', event.code, event.reason);
        setIsConnected(false);
        
        // Attempt to reconnect after 3 seconds
        setTimeout(() => {
          if (!event.wasClean) {
            console.log('Attempting to reconnect...');
            connect();
          }
        }, 3000);
      };

      websocket.onerror = (error) => {
        console.error('WebSocket error:', error);
        setError('Connection error occurred');
        setIsConnected(false);
      };

      setWs(websocket);
      
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      setError('Failed to connect to server');
    }
  }, [url]);

  const reconnect = useCallback(() => {
    if (ws) {
      ws.close();
    }
    setError(null);
    connect();
  }, [ws, connect]);

  useEffect(() => {
    connect();
    
    return () => {
      if (ws) {
        ws.close();
      }
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [url]); // Only depend on url to avoid infinite reconnection loops

  return {
    data,
    isConnected,
    error,
    reconnect,
  };
}