import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface TrafficFlowChartProps {
  data: Array<{
    timestamp: string;
    car?: number;
    motorcycle?: number;
    truck?: number;
    'auto-rickshaw'?: number;
    total: number;
  }>;
}

export default function TrafficFlowChart({ data }: TrafficFlowChartProps) {
  // Format timestamp for display
  const formattedData = data.map(item => ({
    ...item,
    time: new Date(item.timestamp).toLocaleString('en-US', { 
      month: 'short', 
      day: 'numeric', 
      hour: '2-digit' 
    })
  }));

  return (
    <div className="glass-card p-6">
      <h3 className="text-xl font-semibold mb-4 text-white">Traffic Flow Over Time</h3>
      <ResponsiveContainer width="100%" height={350}>
        <LineChart data={formattedData}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
          <XAxis 
            dataKey="time" 
            stroke="rgba(255,255,255,0.6)"
            style={{ fontSize: '12px' }}
          />
          <YAxis 
            stroke="rgba(255,255,255,0.6)"
            style={{ fontSize: '12px' }}
          />
          <Tooltip 
            contentStyle={{ 
              backgroundColor: 'rgba(17, 24, 39, 0.95)', 
              border: '1px solid rgba(255,255,255,0.1)',
              borderRadius: '8px',
              color: '#fff'
            }}
          />
          <Legend 
            wrapperStyle={{ color: '#fff' }}
          />
          <Line 
            type="monotone" 
            dataKey="car" 
            stroke="#3b82f6" 
            strokeWidth={2}
            name="Cars"
            dot={false}
          />
          <Line 
            type="monotone" 
            dataKey="motorcycle" 
            stroke="#f59e0b" 
            strokeWidth={2}
            name="Motorcycles"
            dot={false}
          />
          <Line 
            type="monotone" 
            dataKey="truck" 
            stroke="#8b5cf6" 
            strokeWidth={2}
            name="Trucks"
            dot={false}
          />
          <Line 
            type="monotone" 
            dataKey="auto-rickshaw" 
            stroke="#eab308" 
            strokeWidth={2}
            name="Auto-rickshaws"
            dot={false}
          />
          <Line 
            type="monotone" 
            dataKey="total" 
            stroke="#10b981" 
            strokeWidth={3}
            name="Total"
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

