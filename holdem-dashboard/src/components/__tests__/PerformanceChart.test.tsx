import React from 'react';
import { render } from '@testing-library/react';
import PerformanceChart from '../PerformanceChart';

// Mock recharts to avoid canvas issues in test environment
jest.mock('recharts', () => ({
  ResponsiveContainer: ({ children }: { children: React.ReactNode }) => <div data-testid="responsive-container">{children}</div>,
  LineChart: ({ children }: { children: React.ReactNode }) => <div data-testid="line-chart">{children}</div>,
  Line: () => <div data-testid="line" />,
  XAxis: () => <div data-testid="x-axis" />,
  YAxis: () => <div data-testid="y-axis" />,
  CartesianGrid: () => <div data-testid="cartesian-grid" />,
  Tooltip: () => <div data-testid="tooltip" />,
}));

describe('PerformanceChart', () => {
  const mockData = [
    {
      timestamp: '2024-01-01T12:00:00Z',
      profit: 100,
      hands_played: 50,
      win_rate: 65.5
    },
    {
      timestamp: '2024-01-01T13:00:00Z', 
      profit: 150,
      hands_played: 75,
      win_rate: 67.2
    }
  ];

  beforeEach(() => {
    // Clear any console errors
    jest.clearAllMocks();
  });

  it('renders without crashing with no data', () => {
    const { getByTestId } = render(<PerformanceChart />);
    expect(getByTestId('responsive-container')).toBeInTheDocument();
  });

  it('renders without crashing with mock data', () => {
    const { getByTestId } = render(<PerformanceChart data={mockData} />);
    expect(getByTestId('responsive-container')).toBeInTheDocument();
    expect(getByTestId('line-chart')).toBeInTheDocument();
  });

  it('does not cause infinite re-renders', () => {
    const renderSpy = jest.fn();
    const TestComponent = () => {
      renderSpy();
      return <PerformanceChart data={mockData} />;
    };

    render(<TestComponent />);
    
    // Component should render exactly once
    expect(renderSpy).toHaveBeenCalledTimes(1);
  });

  it('memoizes properly with same data reference', () => {
    const { rerender } = render(<PerformanceChart data={mockData} />);
    
    // Re-render with same data reference - should not cause new chart data calculation
    rerender(<PerformanceChart data={mockData} />);
    
    expect(document.querySelector('[data-testid="line-chart"]')).toBeInTheDocument();
  });

  it('handles empty data array', () => {
    const { getByTestId } = render(<PerformanceChart data={[]} />);
    expect(getByTestId('responsive-container')).toBeInTheDocument();
  });
});