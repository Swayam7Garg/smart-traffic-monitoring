import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api, type Stats } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Video, Activity } from 'lucide-react';

export default function App() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [updatedAt, setUpdatedAt] = useState('--:--');

  async function fetchStats() {
    try {
      const data = await api.getStats();
      setStats(data);
      setUpdatedAt(new Date().toLocaleTimeString());
    } catch (e) {
      console.warn('stats error', e);
    }
  }

  useEffect(() => {
    fetchStats();
    const t = setInterval(fetchStats, 1000);
    return () => clearInterval(t);
  }, []);

  const handleStart = async () => { try { await api.start(); setIsRunning(true); } catch(e){} };
  const handleStop  = async () => { try { await api.stop();  setIsRunning(false);} catch(e){} };

  return (
    <div className="min-h-screen">
      <header className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <h1 className="text-xl font-semibold flex items-center gap-2">🚦 Smart Traffic Monitoring</h1>
              <span className={`status-badge ${isRunning ? 'status-running':'status-stopped'}`}>{isRunning?'Running':'Stopped'}</span>
            </div>
            <nav className="flex items-center gap-4 text-sm">
              <Link to="/">Dashboard</Link>
              <a href="/analytics">Server Analytics</a>
              <a href="/logout">Logout</a>
            </nav>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto p-4">
        <div className="grid md:grid-cols-3 gap-4 mb-4">
          <div className="md:col-span-2 card">
            <h2 className="text-lg font-semibold mb-3 flex items-center gap-2"><Video className="w-5 h-5"/> Live Camera Feed</h2>
            <img src={api.getVideoFeedUrl()} alt="Video Feed" className="w-full rounded-lg border"/>
            <div className="flex gap-2 mt-3">
              <Button onClick={handleStart} disabled={isRunning}>Start</Button>
              <Button onClick={handleStop} variant="outline" disabled={!isRunning}>Stop</Button>
            </div>
          </div>

          <div className="card">
            <h2 className="text-lg font-semibold mb-3 flex items-center gap-2"><Activity className="w-5 h-5"/> Current Stats</h2>
            <div className="space-y-3">
              <div className="p-3 rounded-lg border bg-gray-50">
                <div className="text-xs text-gray-500 mb-1">Total Vehicles</div>
                <div className="text-2xl font-semibold">{stats?.total_vehicles ?? 0}</div>
              </div>
              <div className="p-3 rounded-lg border bg-gray-50">
                <div className="text-xs text-gray-500 mb-1">Emergency Vehicles</div>
                <div className="text-2xl font-semibold">{stats?.emergency_vehicles ?? 0}</div>
              </div>
              <div className="p-3 rounded-lg border bg-gray-50">
                <div className="text-xs text-gray-500 mb-1">Signal</div>
                <div className="text-sm font-medium mt-1">Active lane: {stats?.signal_status?.active_lane ?? '-'}</div>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <h2 className="text-lg font-semibold mb-3">Lane Details</h2>
          {stats?.lanes?.length ? (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="border-b">
                  <tr className="text-left">
                    <th className="py-2 px-3">Lane</th>
                    <th className="py-2 px-3">Vehicles</th>
                    <th className="py-2 px-3">Emergency</th>
                    <th className="py-2 px-3">Congestion</th>
                  </tr>
                </thead>
                <tbody>
                  {stats.lanes.map((lane) => (
                    <tr key={lane.id} className="border-b last:border-0">
                      <td className="py-2 px-3">Lane {lane.id}</td>
                      <td className="py-2 px-3">{lane.vehicles}</td>
                      <td className="py-2 px-3">{lane.emergency}</td>
                      <td className="py-2 px-3"><span className="capitalize font-medium">{lane.congestion}</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-gray-500 text-sm">No lane data yet</p>
          )}
          <div className="mt-3 text-xs text-gray-500">Updated: {updatedAt}</div>
        </div>
      </main>
    </div>
  );
}
