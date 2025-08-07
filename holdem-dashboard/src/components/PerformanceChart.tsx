'use client';

import React, { useMemo, memo } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface DataPoint {
  time: string;
  profit: number;
  hands: number;
}

interface PerformancePoint {
  timestamp: string;
  profit: number;
  hands_played: number;
  win_rate: number;
}

interface PerformanceChartProps {
  data?: PerformancePoint[];
}

const PerformanceChart = memo(function PerformanceChart({ data: externalData }: PerformanceChartProps) {
  const chartData = useMemo<DataPoint[]>(() => {
    // If external data is provided, convert and use it
    if (externalData && externalData.length > 0) {
      return externalData.map(point => ({
        time: new Date(point.timestamp).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
        profit: Math.round(point.profit),
        hands: point.hands_played
      }));
    }

    // Otherwise, generate static mock data (no timers, no random values)
    // Use a stable seed for consistent mock data to prevent unnecessary re-renders
    const points: DataPoint[] = [];
    let cumulativeProfit = 1000;
    const baseTime = new Date('2024-01-01T12:00:00Z'); // Fixed base time
    
    for (let i = 23; i >= 0; i--) {
      const time = new Date(baseTime);
      time.setHours(time.getHours() - i);
      
      // Use deterministic profit changes instead of Math.random()
      const profitChange = ((i % 3) - 1) * 25; // Predictable pattern
      cumulativeProfit += profitChange;
      
      points.push({
        time: time.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
        profit: Math.round(cumulativeProfit),
        hands: 10 + (i % 20), // Deterministic hands count
      });
    }
    return points;
  }, [externalData]);

  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey="time" 
            tick={{ fontSize: 12 }}
            interval="preserveStartEnd"
          />
          <YAxis tick={{ fontSize: 12 }} />
          <Tooltip 
            labelFormatter={(label) => `Time: ${label}`}
            formatter={(value: number, name: string) => [
              name === 'profit' ? `$${value}` : value,
              name === 'profit' ? 'Profit' : 'Hands'
            ]}
          />
          <Line 
            type="monotone" 
            dataKey="profit" 
            stroke="#2563eb" 
            strokeWidth={2}
            dot={{ fill: '#2563eb', strokeWidth: 2, r: 3 }}
            activeDot={{ r: 5 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
});

export default PerformanceChart;