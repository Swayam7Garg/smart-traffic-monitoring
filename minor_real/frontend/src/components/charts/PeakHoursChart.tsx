import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

interface PeakHoursChartProps {
  data: Array<{
    hour: number;
    avg_vehicles: number;
    data_points: number;
  }>;
}

export default function PeakHoursChart({ data }: PeakHoursChartProps) {
  // Format data for display
  const chartData = data.map(item => ({
    hour: `${item.hour.toString().padStart(2, '0')}:00`,
    vehicles: Math.round(item.avg_vehicles),
    dataPoints: item.data_points
  }));

  // Find max value for color coding
  const maxVehicles = Math.max(...chartData.map(d => d.vehicles));

  // Color cells based on traffic level
  const getColor = (value: number) => {
    const ratio = value / maxVehicles;
    if (ratio > 0.7) return '#ef4444'; // High traffic - red
    if (ratio > 0.4) return '#f59e0b'; // Medium traffic - orange
    return '#10b981'; // Low traffic - green
  };

  return (
    <div className="glass-card p-6">
      <h3 className="text-xl font-semibold mb-4 text-white">Average Traffic by Hour</h3>
      <ResponsiveContainer width="100%" height={350}>
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
          <XAxis 
            dataKey="hour" 
            stroke="rgba(255,255,255,0.6)"
            style={{ fontSize: '11px' }}
          />
          <YAxis 
            stroke="rgba(255,255,255,0.6)"
            style={{ fontSize: '12px' }}
            label={{ value: 'Avg Vehicles', angle: -90, position: 'insideLeft', fill: 'rgba(255,255,255,0.6)' }}
          />
          <Tooltip 
            contentStyle={{ 
              backgroundColor: 'rgba(17, 24, 39, 0.95)', 
              border: '1px solid rgba(255,255,255,0.1)',
              borderRadius: '8px',
              color: '#fff'
            }}
            formatter={(value: number, name: string, props: any) => [
              `${value} vehicles (${props.payload.dataPoints} data points)`,
              'Average'
            ]}
          />
          <Bar dataKey="vehicles" radius={[8, 8, 0, 0]}>
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={getColor(entry.vehicles)} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <div className="mt-4 flex items-center justify-center gap-6 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-green-500" />
          <span className="text-gray-300">Low Traffic</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-orange-500" />
          <span className="text-gray-300">Medium Traffic</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-red-500" />
          <span className="text-gray-300">High Traffic</span>
        </div>
      </div>
    </div>
  );
}
