'use client';

import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface DataPoint {
  time: string;
  profit: number;
  hands: number;
}

export default function PerformanceChart() {
  const [data, setData] = useState<DataPoint[]>([]);

  useEffect(() => {
    // Generate initial mock data
    const generateInitialData = () => {
      const points: DataPoint[] = [];
      let cumulativeProfit = 1000;
      
      for (let i = 23; i >= 0; i--) {
        const time = new Date();
        time.setHours(time.getHours() - i);
        
        cumulativeProfit += (Math.random() - 0.4) * 50;
        
        points.push({
          time: time.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
          profit: Math.round(cumulativeProfit),
          hands: Math.floor(Math.random() * 20) + 10,
        });
      }
      return points;
    };

    setData(generateInitialData());

    // Simulate real-time updates
    const interval = setInterval(() => {
      setData(prev => {
        const newData = [...prev];
        const lastProfit = newData[newData.length - 1].profit;
        const newTime = new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
        
        // Add new point
        newData.push({
          time: newTime,
          profit: lastProfit + (Math.random() - 0.4) * 30,
          hands: Math.floor(Math.random() * 20) + 10,
        });

        // Keep only last 24 points
        if (newData.length > 24) {
          newData.shift();
        }

        return newData;
      });
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
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
}