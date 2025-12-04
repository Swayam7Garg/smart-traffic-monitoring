import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

interface VehicleDistributionChartProps {
  data: {
    car?: number;
    motorcycle?: number;
    truck?: number;
    'auto-rickshaw'?: number;
  };
}

const COLORS = {
  car: '#3b82f6',
  motorcycle: '#f59e0b',
  truck: '#8b5cf6',
  'auto-rickshaw': '#eab308'
};

const LABELS = {
  car: 'Cars',
  motorcycle: 'Motorcycles',
  truck: 'Trucks',
  'auto-rickshaw': 'Auto-rickshaws'
};

export default function VehicleDistributionChart({ data }: VehicleDistributionChartProps) {
  const chartData = Object.entries(data)
    .filter(([_, value]) => value > 0)
    .map(([name, value]) => ({
      name: LABELS[name as keyof typeof LABELS] || name,
      value,
      color: COLORS[name as keyof typeof COLORS] || '#6b7280'
    }));

  const total = chartData.reduce((sum, item) => sum + item.value, 0);

  return (
    <div className="glass-card p-6">
      <h3 className="text-xl font-semibold mb-4 text-white">Vehicle Type Distribution</h3>
      {chartData.length === 0 ? (
        <div className="h-[350px] flex items-center justify-center text-gray-400">
          No vehicle data available
        </div>
      ) : (
        <>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: 'rgba(17, 24, 39, 0.95)', 
                  border: '1px solid rgba(255,255,255,0.1)',
                  borderRadius: '8px',
                  color: '#fff'
                }}
              />
            </PieChart>
          </ResponsiveContainer>
          <div className="mt-4 grid grid-cols-2 gap-3">
            {chartData.map((item, index) => (
              <div key={index} className="flex items-center justify-between p-2 rounded bg-white/5">
                <div className="flex items-center gap-2">
                  <div 
                    className="w-3 h-3 rounded-full" 
                    style={{ backgroundColor: item.color }}
                  />
                  <span className="text-sm text-gray-300">{item.name}</span>
                </div>
                <span className="text-sm font-semibold text-white">
                  {item.value} ({((item.value / total) * 100).toFixed(1)}%)
                </span>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
