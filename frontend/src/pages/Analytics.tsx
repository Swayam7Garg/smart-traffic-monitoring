import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { BarChart3, TrendingUp } from 'lucide-react';

export default function Analytics() {
  const [data, setData] = useState<any>(null);

  async function fetchAnalytics() {
    try {
      const res = await api.getAnalytics();
      setData(res);
    } catch (e) {
      console.warn('analytics error', e);
    }
  }

  useEffect(() => {
    fetchAnalytics();
    const id = setInterval(fetchAnalytics, 10000);
    return () => clearInterval(id);
  }, []);

  return (
    <div className="min-h-screen">
      <header className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-xl font-semibold">📊 Analytics</h1>
            <nav className="flex items-center gap-4 text-sm">
              <a href="/app">Dashboard</a>
              <a href="/app/analytics">Analytics</a>
              <a href="/logout">Logout</a>
            </nav>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto p-4">
        <div className="grid md:grid-cols-3 gap-4 mb-4">
          <div className="md:col-span-2 card">
            <h2 className="text-lg font-semibold mb-3 flex items-center gap-2"><TrendingUp className="w-5 h-5"/> Traffic Trend (last hour)</h2>
            {data ? (
              <div className="h-64 flex items-center justify-center text-gray-500 text-sm">Chart placeholder - integrate Chart.js</div>
            ) : (
              <div className="h-64 flex items-center justify-center text-gray-500 text-sm">No data yet</div>
            )}
          </div>

          <div className="space-y-3">
            <div className="card">
              <div className="text-xs text-gray-500 mb-1">Total Vehicles Today</div>
              <div className="text-2xl font-semibold">{data?.total_vehicles ?? 0}</div>
            </div>
            <div className="card">
              <div className="text-xs text-gray-500 mb-1">Peak Hour</div>
              <div className="text-sm">{data?.peak_hour ?? '--:--'} · {data?.peak_vehicles ?? 0} vehicles</div>
            </div>
            <div className="card">
              <div className="text-xs text-gray-500 mb-1">Jams Detected</div>
              <div className="text-sm">{data?.total_jams ?? 0} total · avg {data?.avg_duration ?? 0} min</div>
            </div>
            <div className="card">
              <div className="text-xs text-gray-500 mb-1">System Uptime</div>
              <div className="text-sm">{data?.uptime ?? '0h 0m'}</div>
            </div>
          </div>
        </div>

        <div className="card">
          <h2 className="text-lg font-semibold mb-3 flex items-center gap-2"><BarChart3 className="w-5 h-5"/> Lane Comparison</h2>
          {data ? (
            <div className="h-48 flex items-center justify-center text-gray-500 text-sm">Chart placeholder - integrate Chart.js</div>
          ) : (
            <div className="h-48 flex items-center justify-center text-gray-500 text-sm">No data yet</div>
          )}
        </div>
      </main>
    </div>
  );
}
