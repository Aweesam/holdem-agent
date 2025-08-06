'use client';

import React, { useState, useEffect } from 'react';
import { Clock, TrendingUp } from 'lucide-react';

interface LiveStatsProps {
  hourlyRate: number;
  currentSession: number;
  sessionTime?: number;
}

export default function LiveStats({ hourlyRate, currentSession, sessionTime: propSessionTime }: LiveStatsProps) {
  const [localSessionTime, setLocalSessionTime] = useState(0);
  const [currentHourlyRate, setCurrentHourlyRate] = useState(hourlyRate);

  useEffect(() => {
    // Use prop session time if available, otherwise increment local time
    if (propSessionTime !== undefined) {
      setLocalSessionTime(propSessionTime);
    } else {
      const timer = setInterval(() => {
        setLocalSessionTime(prev => prev + 1);
      }, 1000);
      return () => clearInterval(timer);
    }
  }, [propSessionTime]);

  useEffect(() => {
    setCurrentHourlyRate(hourlyRate);
  }, [hourlyRate]);

  const formatTime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const sessionStats = [
    {
      label: 'Session Time',
      value: formatTime(localSessionTime),
      icon: <Clock className="h-5 w-5 text-blue-500" />,
    },
    {
      label: 'Session Profit',
      value: `$${currentSession.toFixed(0)}`,
      icon: <TrendingUp className="h-5 w-5 text-green-500" />,
    },
    {
      label: 'Hourly Rate',
      value: `$${currentHourlyRate.toFixed(1)}/hr`,
      icon: <TrendingUp className="h-5 w-5 text-purple-500" />,
    },
  ];

  return (
    <div className="space-y-4">
      {sessionStats.map((stat, index) => (
        <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
          <div className="flex items-center space-x-3">
            {stat.icon}
            <span className="text-sm font-medium text-gray-700">{stat.label}</span>
          </div>
          <span className="text-lg font-semibold text-gray-900">{stat.value}</span>
        </div>
      ))}
      
      <div className="mt-6 p-4 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg text-white">
        <div className="text-sm opacity-90">Current Status</div>
        <div className="text-xl font-bold">
          {currentSession > 0 ? '🟢 Winning Session' : '🔴 Losing Session'}
        </div>
        <div className="text-sm opacity-90 mt-1">
          {currentSession > 0 ? 'Keep up the good work!' : 'Stay focused, variance is normal'}
        </div>
      </div>
    </div>
  );
}