import { useState, useEffect } from 'react';
import { 
  AlertTriangle, Clock, MapPin, CheckCircle, XCircle, 
  Shield, Activity, Bell, AlertOctagon, TrendingUp, Users,
  Play, Pause, SkipForward, Settings, Archive, Filter
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { emergencyAPI, trafficAPI } from '../lib/api';

interface EmergencyOverride {
  id: string;
  location_id: string;
  direction: string;
  priority_level: number;
  activated_at: string;
  expires_at: string;
  status: 'active' | 'expired' | 'cleared';
  emergency_vehicle_count: number;
  signal_state?: {
    green_time: number;
    current_phase: string;
  };
}

interface EmergencyDetection {
  id: string;
  location_id: string;
  timestamp: string;
  vehicle_type: string;
  confidence: number;
  action_taken: string;
  response_time?: number;
}

interface EmergencyStats {
  total_today: number;
  active_overrides: number;
  avg_response_time: number;
  cleared_count: number;
}

export default function Emergency() {
  const [activeOverrides, setActiveOverrides] = useState<EmergencyOverride[]>([]);
  const [emergencyHistory, setEmergencyHistory] = useState<EmergencyDetection[]>([]);
  const [stats, setStats] = useState<EmergencyStats>({
    total_today: 0,
    active_overrides: 0,
    avg_response_time: 0,
    cleared_count: 0
  });
  const [loading, setLoading] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [filterLocation, setFilterLocation] = useState<string>('all');
  const [timeFilter, setTimeFilter] = useState<number>(24);

  useEffect(() => {
    fetchEmergencyData();
    
    if (autoRefresh) {
      const interval = setInterval(fetchEmergencyData, 5000); // Refresh every 5 seconds
      return () => clearInterval(interval);
    }
  }, [autoRefresh, filterLocation, timeFilter]);

  const fetchEmergencyData = async () => {
    try {
      // Fetch active overrides
      const overrides = await emergencyAPI.getActiveOverrides();
      setActiveOverrides(Array.isArray(overrides) ? overrides : []);

      // Fetch emergency history
      const location = filterLocation === 'all' ? undefined : filterLocation;
      const history = await trafficAPI.getEmergencyHistory(location, timeFilter);
      setEmergencyHistory(Array.isArray(history) ? history : []);

      // Calculate stats
      const activeCount = Array.isArray(overrides) ? overrides.filter((o: EmergencyOverride) => o.status === 'active').length : 0;
      const clearedCount = Array.isArray(overrides) ? overrides.filter((o: EmergencyOverride) => o.status === 'cleared').length : 0;
      
      setStats({
        total_today: Array.isArray(history) ? history.length : 0,
        active_overrides: activeCount,
        avg_response_time: 2.3, // Mock for now
        cleared_count: clearedCount
      });
    } catch (error) {
      console.error('Error fetching emergency data:', error);
      // Set empty data on error so page still loads
      setActiveOverrides([]);
      setEmergencyHistory([]);
      setStats({
        total_today: 0,
        active_overrides: 0,
        avg_response_time: 0,
        cleared_count: 0
      });
    } finally {
      setLoading(false);
    }
  };

  const handleClearOverride = async (overrideId: string) => {
    if (!confirm('Are you sure you want to clear this emergency override?')) return;
    
    try {
      await emergencyAPI.clearOverride(overrideId);
      await fetchEmergencyData();
    } catch (error: any) {
      alert('Failed to clear override: ' + error.message);
    }
  };

  const handleCheckExpired = async () => {
    try {
      await emergencyAPI.checkExpired();
      await fetchEmergencyData();
    } catch (error: any) {
      alert('Failed to check expired overrides: ' + error.message);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'active':
        return <Badge variant="danger" pulse><Shield className="w-3 h-3 mr-1" />Active</Badge>;
      case 'expired':
        return <Badge variant="warning"><Clock className="w-3 h-3 mr-1" />Expired</Badge>;
      case 'cleared':
        return <Badge variant="success"><CheckCircle className="w-3 h-3 mr-1" />Cleared</Badge>;
      default:
        return <Badge variant="default">{status}</Badge>;
    }
  };

  const getPriorityBadge = (level: number) => {
    if (level >= 9) return <Badge variant="danger">Critical</Badge>;
    if (level >= 7) return <Badge variant="warning">High</Badge>;
    if (level >= 5) return <Badge variant="info">Medium</Badge>;
    return <Badge variant="default">Low</Badge>;
  };

  const formatDuration = (startTime: string) => {
    const start = new Date(startTime);
    const now = new Date();
    const diffMs = now.getTime() - start.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffSecs = Math.floor((diffMs % 60000) / 1000);
    
    if (diffMins > 0) {
      return `${diffMins}m ${diffSecs}s`;
    }
    return `${diffSecs}s`;
  };

  const getTimeRemaining = (expiresAt: string) => {
    const expires = new Date(expiresAt);
    const now = new Date();
    const diffMs = expires.getTime() - now.getTime();
    const diffSecs = Math.floor(diffMs / 1000);
    
    if (diffSecs <= 0) return 'Expired';
    if (diffSecs < 60) return `${diffSecs}s`;
    
    const diffMins = Math.floor(diffSecs / 60);
    return `${diffMins}m ${diffSecs % 60}s`;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-200px)]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-500 mx-auto mb-4"></div>
          <p className="text-gray-400">Loading emergency data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2 flex items-center gap-3">
            <AlertTriangle className="w-8 h-8 text-red-500" />
            Emergency Management
          </h1>
          <p className="text-gray-400">Real-time emergency vehicle detection and signal override control</p>
        </div>
        
        <div className="flex items-center gap-3">
          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition ${
              autoRefresh 
                ? 'bg-green-600/20 text-green-400 border border-green-500/50' 
                : 'bg-gray-600/20 text-gray-400 border border-gray-500/50'
            }`}
          >
            {autoRefresh ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
            {autoRefresh ? 'Live' : 'Paused'}
          </button>
          <button
            onClick={handleCheckExpired}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600/20 text-blue-400 border border-blue-500/50 rounded-lg hover:bg-blue-600/30 transition"
          >
            <SkipForward className="w-4 h-4" />
            Check Expired
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-400 mb-1">Detected Today</p>
                <p className="text-3xl font-bold text-white">{stats.total_today}</p>
                <p className="text-xs text-gray-500 mt-1">Last {timeFilter}h</p>
              </div>
              <div className="w-12 h-12 rounded-lg bg-blue-500/20 flex items-center justify-center">
                <Activity className="w-6 h-6 text-blue-400" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-400 mb-1">Active Overrides</p>
                <p className="text-3xl font-bold text-red-400">{stats.active_overrides}</p>
                <p className="text-xs text-gray-500 mt-1">
                  {stats.active_overrides > 0 ? 'Requires monitoring' : 'All clear'}
                </p>
              </div>
              <div className="w-12 h-12 rounded-lg bg-red-500/20 flex items-center justify-center">
                <Shield className="w-6 h-6 text-red-400" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-400 mb-1">Avg Response Time</p>
                <p className="text-3xl font-bold text-green-400">{stats.avg_response_time}s</p>
                <p className="text-xs text-green-500 mt-1 flex items-center gap-1">
                  <TrendingUp className="w-3 h-3" />
                  Excellent
                </p>
              </div>
              <div className="w-12 h-12 rounded-lg bg-green-500/20 flex items-center justify-center">
                <Clock className="w-6 h-6 text-green-400" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-400 mb-1">Cleared</p>
                <p className="text-3xl font-bold text-purple-400">{stats.cleared_count}</p>
                <p className="text-xs text-gray-500 mt-1">Successfully resolved</p>
              </div>
              <div className="w-12 h-12 rounded-lg bg-purple-500/20 flex items-center justify-center">
                <CheckCircle className="w-6 h-6 text-purple-400" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Active Emergency Overrides */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <AlertOctagon className="w-5 h-5 text-red-500" />
              Active Emergency Overrides
            </CardTitle>
            <Badge variant="danger" pulse={activeOverrides.length > 0}>
              {activeOverrides.length} Active
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          {activeOverrides.length === 0 ? (
            <div className="text-center py-12">
              <CheckCircle className="w-12 h-12 text-green-500 mx-auto mb-4" />
              <p className="text-gray-400 mb-2">No active emergency overrides</p>
              <p className="text-sm text-gray-500">All traffic signals operating normally</p>
            </div>
          ) : (
            <div className="space-y-4">
              {activeOverrides.map((override) => (
                <div
                  key={override.id}
                  className="glass rounded-lg p-4 border-l-4 border-red-500"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-3 flex-1">
                      <div className="w-10 h-10 rounded-lg bg-red-500/20 flex items-center justify-center flex-shrink-0">
                        <AlertTriangle className="w-5 h-5 text-red-400 animate-pulse" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <h4 className="font-medium text-white truncate">
                            {override.location_id}
                          </h4>
                          {getStatusBadge(override.status)}
                          {getPriorityBadge(override.priority_level)}
                        </div>
                        <div className="flex items-center gap-4 text-sm text-gray-400">
                          <span className="flex items-center gap-1">
                            <MapPin className="w-3 h-3" />
                            {override.direction} Lane
                          </span>
                          <span className="flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            Active for {formatDuration(override.activated_at)}
                          </span>
                          <span className="flex items-center gap-1">
                            <Shield className="w-3 h-3" />
                            {override.emergency_vehicle_count} vehicle(s)
                          </span>
                        </div>
                      </div>
                    </div>
                    <Button
                      onClick={() => handleClearOverride(override.id)}
                      variant="danger"
                      size="sm"
                    >
                      <XCircle className="w-4 h-4 mr-1" />
                      Clear Override
                    </Button>
                  </div>

                  {/* Override Details */}
                  <div className="grid grid-cols-3 gap-4 mt-3 pt-3 border-t border-white/10">
                    <div>
                      <p className="text-xs text-gray-500 mb-1">Time Remaining</p>
                      <p className="text-sm font-medium text-yellow-400">
                        {getTimeRemaining(override.expires_at)}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500 mb-1">Signal Phase</p>
                      <p className="text-sm font-medium text-green-400">
                        {override.signal_state?.current_phase || 'Green - Priority'}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500 mb-1">Green Time</p>
                      <p className="text-sm font-medium text-blue-400">
                        {override.signal_state?.green_time || 60}s
                      </p>
                    </div>
                  </div>

                  {/* Warning */}
                  <div className="mt-3 bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-3 flex items-center gap-2">
                    <Bell className="w-4 h-4 text-yellow-400 flex-shrink-0" />
                    <span className="text-sm text-yellow-300">
                      Signal override active - All other directions on hold
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Filters */}
      <div className="flex items-center gap-4 flex-wrap">
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-gray-400" />
          <span className="text-sm text-gray-400">Filters:</span>
        </div>
        <select
          value={timeFilter}
          onChange={(e) => setTimeFilter(Number(e.target.value))}
          className="px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value={1} className="bg-gray-900">Last 1 hour</option>
          <option value={6} className="bg-gray-900">Last 6 hours</option>
          <option value={24} className="bg-gray-900">Last 24 hours</option>
          <option value={168} className="bg-gray-900">Last 7 days</option>
        </select>
        <select
          value={filterLocation}
          onChange={(e) => setFilterLocation(e.target.value)}
          className="px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="all" className="bg-gray-900">All Locations</option>
          <option value="junction_01" className="bg-gray-900">Junction 01</option>
          <option value="junction_02" className="bg-gray-900">Junction 02</option>
          <option value="junction_03" className="bg-gray-900">Junction 03</option>
        </select>
      </div>

      {/* Emergency History */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Archive className="w-5 h-5 text-blue-500" />
            Emergency Detection History
          </CardTitle>
        </CardHeader>
        <CardContent>
          {emergencyHistory.length === 0 ? (
            <div className="text-center py-12">
              <Activity className="w-12 h-12 text-gray-600 mx-auto mb-4" />
              <p className="text-gray-400 mb-2">No emergency detections in selected time range</p>
              <p className="text-sm text-gray-500">Emergency vehicles will appear here when detected</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-white/10">
                    <th className="text-left py-3 px-4 text-gray-400 font-medium text-sm">Time</th>
                    <th className="text-left py-3 px-4 text-gray-400 font-medium text-sm">Location</th>
                    <th className="text-left py-3 px-4 text-gray-400 font-medium text-sm">Vehicle Type</th>
                    <th className="text-right py-3 px-4 text-gray-400 font-medium text-sm">Confidence</th>
                    <th className="text-left py-3 px-4 text-gray-400 font-medium text-sm">Action</th>
                    <th className="text-right py-3 px-4 text-gray-400 font-medium text-sm">Response Time</th>
                  </tr>
                </thead>
                <tbody>
                  {emergencyHistory.map((detection, index) => (
                    <tr key={detection.id || index} className="border-b border-white/5 hover:bg-white/5 transition">
                      <td className="py-3 px-4 text-sm text-gray-300">
                        {new Date(detection.timestamp).toLocaleString()}
                      </td>
                      <td className="py-3 px-4 text-sm text-white font-medium">
                        {detection.location_id}
                      </td>
                      <td className="py-3 px-4 text-sm">
                        <span className="px-2 py-1 bg-red-500/20 text-red-400 rounded text-xs">
                          {detection.vehicle_type}
                        </span>
                      </td>
                      <td className="text-right py-3 px-4 text-sm text-gray-300">
                        {(detection.confidence * 100).toFixed(1)}%
                      </td>
                      <td className="py-3 px-4 text-sm">
                        <span className={`px-2 py-1 rounded text-xs ${
                          detection.action_taken === 'override_activated' 
                            ? 'bg-green-500/20 text-green-400' 
                            : 'bg-gray-500/20 text-gray-400'
                        }`}>
                          {detection.action_taken.replace('_', ' ')}
                        </span>
                      </td>
                      <td className="text-right py-3 px-4 text-sm text-gray-300">
                        {detection.response_time ? `${detection.response_time.toFixed(1)}s` : 'N/A'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* System Information */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 rounded-lg bg-blue-500/20 flex items-center justify-center flex-shrink-0">
              <Settings className="w-4 h-4 text-blue-400" />
            </div>
            <div>
              <h4 className="font-medium text-white mb-1">Emergency System Information</h4>
              <ul className="text-sm text-gray-400 space-y-1">
                <li>• Emergency vehicles are detected using color-based detection (red/blue lights)</li>
                <li>• Signal overrides automatically activate when emergency vehicles are detected</li>
                <li>• Default override duration: 60 seconds (adjustable based on traffic density)</li>
                <li>• All overrides are logged for audit and performance analysis</li>
                <li>• System automatically clears expired overrides and restores normal signal timing</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
