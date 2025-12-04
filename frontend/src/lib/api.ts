export interface Stats {
  total_vehicles: number;
  emergency_vehicles: number;
  signal_status: { active_lane: number };
  lanes: Array<{ id: number; vehicles: number; emergency: number; congestion: 'low'|'medium'|'high' }>;
}

const API_BASE = '';

export const api = {
  async start() {
    const res = await fetch(`${API_BASE}/api/start`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to start monitoring');
    return res.json();
  },
  async stop() {
    const res = await fetch(`${API_BASE}/api/stop`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to stop monitoring');
    return res.json();
  },
  async getStats(): Promise<Stats> {
    const res = await fetch(`${API_BASE}/api/stats`);
    if (!res.ok) throw new Error('Failed to fetch stats');
    return res.json();
  },
  async getAnalytics() {
    const res = await fetch(`${API_BASE}/api/analytics/data`);
    if (!res.ok) throw new Error('Failed to fetch analytics');
    return res.json();
  },
  getVideoFeedUrl() {
    return `${API_BASE}/video_feed`;
  },
};
