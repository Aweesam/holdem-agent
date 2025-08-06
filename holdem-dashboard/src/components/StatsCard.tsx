import React from 'react';
import { ArrowUpIcon, ArrowDownIcon } from 'lucide-react';

interface StatsCardProps {
  title: string;
  value: string;
  icon: React.ReactNode;
  trend?: string;
  trendUp?: boolean;
}

export default function StatsCard({ title, value, icon, trend, trendUp }: StatsCardProps) {
  return (
    <div className="bg-white overflow-hidden shadow rounded-lg">
      <div className="p-5">
        <div className="flex items-center">
          <div className="flex-shrink-0">
            {icon}
          </div>
          <div className="ml-5 w-0 flex-1">
            <dl>
              <dt className="text-sm font-medium text-gray-500 truncate">
                {title}
              </dt>
              <dd className="text-lg font-medium text-gray-900">
                {value}
              </dd>
            </dl>
          </div>
        </div>
        {trend && (
          <div className="mt-3 flex items-center">
            <div className={`flex items-center ${trendUp ? 'text-green-600' : 'text-red-600'}`}>
              {trendUp ? (
                <ArrowUpIcon className="h-4 w-4" />
              ) : (
                <ArrowDownIcon className="h-4 w-4" />
              )}
              <span className="text-sm font-medium ml-1">
                {trend}
              </span>
            </div>
            <span className="text-xs text-gray-500 ml-2">
              vs last period
            </span>
          </div>
        )}
      </div>
    </div>
  );
}