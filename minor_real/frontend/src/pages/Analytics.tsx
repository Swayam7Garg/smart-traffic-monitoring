import { useState, useEffect } from 'react';
import { 
  BarChart3, TrendingUp, Download, Calendar, AlertCircle, 
  MapPin, Trash2, RefreshCw, Eye, Activity, Clock,
  AlertTriangle, CheckCircle, XCircle, TrendingDown, Filter
} from 'lucide-react';
import TrafficFlowChart from '../components/charts/TrafficFlowChart';
import VehicleDistributionChart from '../components/charts/VehicleDistributionChart';
import PeakHoursChart from '../components/charts/PeakHoursChart';
import { analyticsAPI } from '../lib/api';

interface Location {
  location_id: string;
  total_videos: number;
  total_vehicles: number;
  avg_congestion: number;
  last_updated: string;
}

interface LastVideoData {
  job_id: string;
  location_id: string;
  processed_at: string;
  vehicle_count: number;
  vehicle_counts: Record<string, number>;
  congestion_level: number;
  emergency_vehicles: number;
  output_video?: string;
}

interface AnalyticsData {
  summary: {
    total_vehicles: number;
    total_videos: number;
    avg_vehicles_per_video: number;
    emergency_detections: number;
    avg_congestion?: number;
    peak_congestion?: number;
  };
  vehicle_distribution: Record<string, number>;
  timeline_data: Array<{
    timestamp: string;
    [key: string]: any;
  }>;
  peak_hours: Array<{
    hour: number;
    avg_vehicles: number;
    data_points: number;
  }>;
  location_stats: Array<{
    location_id: string;
    total_vehicles: number;
    videos: number;
    emergency: number;
  }>;
}

type ViewMode = 'all' | 'location' | 'last-video';

export default function Analytics() {
  const [viewMode, setViewMode] = useState<ViewMode>('all');
  const [selectedLocation, setSelectedLocation] = useState<string>('');
  const [locations, setLocations] = useState<Location[]>([]);
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [lastVideo, setLastVideo] = useState<LastVideoData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showClearModal, setShowClearModal] = useState(false);
  const [clearingData, setClearingData] = useState(false);
  
  const [dateRange, setDateRange] = useState(() => {
    const now = new Date();
    const sevenDaysAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
    return {
      start: sevenDaysAgo.toISOString().split('T')[0],
      end: now.toISOString().split('T')[0]
    };
  });

  // Fetch locations on mount
  useEffect(() => {
    fetchLocations();
  }, []);

  // Fetch data when view mode, location, or date range changes
  useEffect(() => {
    fetchData();
  }, [viewMode, selectedLocation, dateRange]);

  const fetchLocations = async () => {
    try {
      const result = await analyticsAPI.getAllLocations();
      setLocations(result);
      if (result.length > 0 && !selectedLocation) {
        setSelectedLocation(result[0].location_id);
      }
    } catch (err: any) {
      console.error('Error fetching locations:', err);
    }
  };

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      if (viewMode === 'last-video') {
        console.log('Fetching last video data...');
        const lastVideoData = await analyticsAPI.getLastVideo();
        console.log('Last video data:', lastVideoData);
        setLastVideo(lastVideoData);
        setData(null);
      } else if (viewMode === 'location' && selectedLocation) {
        console.log(`Fetching location analytics for ${selectedLocation}...`);
        const locationData = await analyticsAPI.getLocationAnalytics(
          selectedLocation,
          `${dateRange.start}T00:00:00Z`,
          `${dateRange.end}T23:59:59Z`
        );
        console.log('Location data:', locationData);
        setData(locationData);
        setLastVideo(null);
      } else {
        console.log('Fetching overview analytics...');
        const overviewData = await analyticsAPI.getOverview(
          `${dateRange.start}T00:00:00Z`,
          `${dateRange.end}T23:59:59Z`
        );
        console.log('Overview data:', overviewData);
        setData(overviewData);
        setLastVideo(null);
      }
    } catch (err: any) {
      console.error('Error fetching analytics:', err);
      console.error('Error details:', err.response?.data);
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to load analytics data';
      setError(`${errorMsg}. Check browser console for details.`);
    } finally {
      setLoading(false);
    }
  };

  const handleClearHistory = async () => {
    try {
      setClearingData(true);
      const locationToClear = viewMode === 'location' ? selectedLocation : undefined;
      await analyticsAPI.clearHistory(locationToClear);
      setShowClearModal(false);
      await fetchData();
      await fetchLocations();
      alert(`Successfully cleared ${locationToClear ? `data for ${locationToClear}` : 'all data'}`);
    } catch (err: any) {
      alert('Failed to clear data: ' + err.message);
    } finally {
      setClearingData(false);
    }
  };

  const handleExportCSV = async () => {
    try {
      await analyticsAPI.exportCSV(
        `${dateRange.start}T00:00:00Z`,
        `${dateRange.end}T23:59:59Z`
      );
    } catch (err: any) {
      alert('Failed to export data: ' + err.message);
    }
  };

  const getCongestionColor = (level: number) => {
    if (level < 30) return 'text-green-400 bg-green-500/20';
    if (level < 60) return 'text-yellow-400 bg-yellow-500/20';
    return 'text-red-400 bg-red-500/20';
  };

  const getCongestionLabel = (level: number) => {
    if (level < 30) return 'Low';
    if (level < 60) return 'Moderate';
    return 'High';
  };

  const getTrafficRecommendation = (congestion: number, emergencyCount: number) => {
    if (emergencyCount > 0) {
      return {
        icon: AlertTriangle,
        color: 'text-red-400',
        title: 'Emergency Priority',
        message: `${emergencyCount} emergency vehicle(s) detected. Prioritize green signals.`
      };
    }
    if (congestion > 85) {
      return {
        icon: AlertCircle,
        color: 'text-orange-400',
        title: 'High Congestion Alert',
        message: 'Consider extending signal timing or activating alternative routes.'
      };
    }
    if (congestion < 40) {
      return {
        icon: CheckCircle,
        color: 'text-green-400',
        title: 'Traffic Flowing Smoothly',
        message: 'Current signal timing is optimal for traffic flow.'
      };
    }
    return {
      icon: Activity,
      color: 'text-blue-400',
      title: 'Moderate Traffic',
      message: 'Monitor traffic patterns. No immediate action required.'
    };
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-200px)]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-400">Loading analytics...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-200px)]">
        <div className="glass-card p-8 max-w-md text-center">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-white mb-2">Error Loading Analytics</h3>
          <p className="text-gray-400 mb-4">{error}</p>
          <button
            onClick={fetchData}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  const recommendation = data ? getTrafficRecommendation(
    data.summary.avg_congestion || data.summary.peak_congestion || 0,
    data.summary.emergency_detections
  ) : null;

  return (
    <div className="space-y-6">
      {/* Header with View Mode Selector */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Traffic Analytics Dashboard</h1>
          <p className="text-gray-400">Real-world traffic insights and management tools</p>
        </div>
        
        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowClearModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-red-600/20 text-red-400 border border-red-500/50 rounded-lg hover:bg-red-600/30 transition"
          >
            <Trash2 className="w-4 h-4" />
            Clear Data
          </button>
          <button
            onClick={handleExportCSV}
            className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition"
          >
            <Download className="w-4 h-4" />
            Export CSV
          </button>
        </div>
      </div>

      {/* View Mode Tabs */}
      <div className="glass-card p-4">
        <div className="flex items-center gap-4 flex-wrap">
          <button
            onClick={() => setViewMode('all')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition ${
              viewMode === 'all'
                ? 'bg-blue-600 text-white'
                : 'bg-white/5 text-gray-400 hover:bg-white/10'
            }`}
          >
            <Activity className="w-4 h-4" />
            All Locations
          </button>
          <button
            onClick={() => setViewMode('location')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition ${
              viewMode === 'location'
                ? 'bg-blue-600 text-white'
                : 'bg-white/5 text-gray-400 hover:bg-white/10'
            }`}
          >
            <MapPin className="w-4 h-4" />
            By Location
          </button>
          <button
            onClick={() => setViewMode('last-video')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition ${
              viewMode === 'last-video'
                ? 'bg-blue-600 text-white'
                : 'bg-white/5 text-gray-400 hover:bg-white/10'
            }`}
          >
            <Eye className="w-4 h-4" />
            Last Video
          </button>

          {/* Location Selector */}
          {viewMode === 'location' && locations.length > 0 && (
            <>
              <div className="h-8 w-px bg-white/20"></div>
              <select
                value={selectedLocation}
                onChange={(e) => setSelectedLocation(e.target.value)}
                className="px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {locations.map((loc) => {
                  const junctionName = loc.location_id.replace('junction_0', 'Junction ').replace('junction_', 'Junction ');
                  return (
                    <option key={loc.location_id} value={loc.location_id} className="bg-gray-900">
                      {junctionName} ({loc.total_videos} videos, {loc.total_vehicles} vehicles)
                    </option>
                  );
                })}
              </select>
            </>
          )}
        </div>
      </div>

      {/* Date Range Selector - Only for all/location views */}
      {viewMode !== 'last-video' && (
        <div className="glass-card p-4">
          <div className="flex items-center gap-4 flex-wrap">
            <Calendar className="w-5 h-5 text-blue-400" />
            <span className="text-white font-medium">Date Range:</span>
            <input
              type="date"
              value={dateRange.start}
              onChange={(e) => setDateRange({ ...dateRange, start: e.target.value })}
              className="px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <span className="text-gray-400">to</span>
            <input
              type="date"
              value={dateRange.end}
              onChange={(e) => setDateRange({ ...dateRange, end: e.target.value })}
              className="px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={fetchData}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600/20 text-blue-400 border border-blue-500/50 rounded-lg hover:bg-blue-600/30 transition"
            >
              <RefreshCw className="w-4 h-4" />
              Refresh
            </button>
          </div>
        </div>
      )}

      {/* Last Video View */}
      {viewMode === 'last-video' && lastVideo && (
        <div className="space-y-6">
          <div className="glass-card p-6">
            <div className="flex items-start justify-between mb-6">
              <div>
                <h2 className="text-2xl font-bold text-white mb-2">Latest Processed Video</h2>
                <p className="text-gray-400">Most recent traffic analysis</p>
              </div>
              <div className="text-right">
                <div className="text-sm text-gray-400">Location</div>
                <div className="text-lg font-semibold text-white">
                  {lastVideo.location_id.replace('junction_0', 'Junction ').replace('junction_', 'Junction ')}
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  {new Date(lastVideo.processed_at).toLocaleString()}
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-4">
                <div className="text-sm text-blue-400 mb-1">Total Vehicles</div>
                <div className="text-3xl font-bold text-white">{lastVideo.vehicle_count}</div>
              </div>
              <div className={`border rounded-lg p-4 ${getCongestionColor(lastVideo.congestion_level)}`}>
                <div className="text-sm mb-1">Congestion Level</div>
                <div className="text-3xl font-bold">{lastVideo.congestion_level.toFixed(1)}%</div>
                <div className="text-xs mt-1">{getCongestionLabel(lastVideo.congestion_level)}</div>
              </div>
              <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4">
                <div className="text-sm text-red-400 mb-1">Emergency Vehicles</div>
                <div className="text-3xl font-bold text-white">{lastVideo.emergency_vehicles}</div>
              </div>
              <div className="bg-purple-500/10 border border-purple-500/30 rounded-lg p-4">
                <div className="text-sm text-purple-400 mb-1">Job ID</div>
                <div className="text-xs font-mono text-white break-all">{lastVideo.job_id.slice(0, 13)}...</div>
              </div>
            </div>

            <div className="bg-white/5 rounded-lg p-4">
              <h3 className="text-white font-semibold mb-3">Vehicle Breakdown</h3>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                {Object.entries(lastVideo.vehicle_counts).map(([type, count]) => {
                  if (type === 'total' || type === 'emergency_vehicles') return null;
                  return (
                    <div key={type} className="bg-white/5 rounded p-3">
                      <div className="text-xs text-gray-400 capitalize">{type.replace('-', ' ')}</div>
                      <div className="text-2xl font-bold text-white mt-1">{count}</div>
                    </div>
                  );
                })}
              </div>
            </div>

            {lastVideo.output_video && (
              <div className="mt-4">
                <a
                  href={`http://localhost:8000${lastVideo.output_video}`}
                  download
                  className="inline-flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition"
                >
                  <Download className="w-4 h-4" />
                  Download Processed Video
                </a>
              </div>
            )}
          </div>

          {/* Traffic Recommendation for Last Video */}
          {(() => {
            const rec = getTrafficRecommendation(lastVideo.congestion_level, lastVideo.emergency_vehicles);
            return (
              <div className={`glass-card p-6 border-l-4 ${
                rec.color === 'text-red-400' ? 'border-red-500' :
                rec.color === 'text-orange-400' ? 'border-orange-500' :
                rec.color === 'text-green-400' ? 'border-green-500' : 'border-blue-500'
              }`}>
                <div className="flex items-start gap-4">
                  <rec.icon className={`w-8 h-8 ${rec.color} flex-shrink-0`} />
                  <div>
                    <h3 className="text-xl font-bold text-white mb-2">{rec.title}</h3>
                    <p className="text-gray-300">{rec.message}</p>
                  </div>
                </div>
              </div>
            );
          })()}
        </div>
      )}

      {/* Standard Analytics View */}
      {viewMode !== 'last-video' && data && (
        <div className="space-y-6">
          {/* Traffic Recommendation */}
          {recommendation && data.summary.total_videos > 0 && (
            <div className={`glass-card p-6 border-l-4 ${
              recommendation.color === 'text-red-400' ? 'border-red-500' :
              recommendation.color === 'text-orange-400' ? 'border-orange-500' :
              recommendation.color === 'text-green-400' ? 'border-green-500' : 'border-blue-500'
            }`}>
              <div className="flex items-start gap-4">
                <recommendation.icon className={`w-8 h-8 ${recommendation.color} flex-shrink-0`} />
                <div className="flex-1">
                  <h3 className="text-xl font-bold text-white mb-2">{recommendation.title}</h3>
                  <p className="text-gray-300 mb-3">{recommendation.message}</p>
                  {viewMode === 'location' && (
                    <div className="text-sm text-gray-400">
                      Analyzing <span className="text-white font-semibold">{selectedLocation}</span> · 
                      {data.summary.total_videos} video(s) · 
                      {data.summary.total_vehicles} vehicles detected
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="glass-card p-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-gray-400 text-sm">Total Vehicles</span>
                <BarChart3 className="w-5 h-5 text-blue-400" />
              </div>
              <p className="text-3xl font-bold text-white">{data.summary.total_vehicles.toLocaleString()}</p>
              <p className="text-sm text-gray-500 mt-1">
                {viewMode === 'location' ? `At ${selectedLocation}` : 'Across all locations'}
              </p>
            </div>

            <div className="glass-card p-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-gray-400 text-sm">Videos Analyzed</span>
                <TrendingUp className="w-5 h-5 text-green-400" />
              </div>
              <p className="text-3xl font-bold text-white">{data.summary.total_videos}</p>
              <p className="text-sm text-gray-500 mt-1">In selected period</p>
            </div>

            <div className="glass-card p-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-gray-400 text-sm">Avg Congestion</span>
                <Activity className="w-5 h-5 text-yellow-400" />
              </div>
              <p className="text-3xl font-bold text-white">
                {(data.summary.avg_congestion || 0).toFixed(1)}%
              </p>
              <p className="text-sm text-gray-500 mt-1">
                {getCongestionLabel(data.summary.avg_congestion || 0)} traffic
              </p>
            </div>

            <div className="glass-card p-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-gray-400 text-sm">Emergency Alerts</span>
                <AlertCircle className="w-5 h-5 text-red-400" />
              </div>
              <p className="text-3xl font-bold text-white">{data.summary.emergency_detections}</p>
              <p className="text-sm text-gray-500 mt-1">Requires attention</p>
            </div>
          </div>

          {/* Charts */}
          {data.summary.total_videos > 0 ? (
            <>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <TrafficFlowChart data={data.timeline_data} />
                <VehicleDistributionChart data={data.vehicle_distribution} />
              </div>

              {data.peak_hours.length > 0 && (
                <PeakHoursChart data={data.peak_hours} />
              )}

              {/* Location Comparison Table - Only in 'all' view */}
              {viewMode === 'all' && data.location_stats.length > 0 && (
                <div className="glass-card p-6">
                  <h3 className="text-xl font-semibold mb-4 text-white flex items-center gap-2">
                    <MapPin className="w-5 h-5" />
                    Location Comparison
                  </h3>
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead>
                        <tr className="border-b border-white/10">
                          <th className="text-left py-3 px-4 text-gray-400 font-medium">Location</th>
                          <th className="text-right py-3 px-4 text-gray-400 font-medium">Vehicles</th>
                          <th className="text-right py-3 px-4 text-gray-400 font-medium">Videos</th>
                          <th className="text-right py-3 px-4 text-gray-400 font-medium">Avg/Video</th>
                          <th className="text-right py-3 px-4 text-gray-400 font-medium">Emergency</th>
                          <th className="text-right py-3 px-4 text-gray-400 font-medium">Action</th>
                        </tr>
                      </thead>
                      <tbody>
                        {data.location_stats.map((location, index) => (
                          <tr key={index} className="border-b border-white/5 hover:bg-white/5 transition">
                            <td className="py-3 px-4 text-white font-medium">
                              {location.location_id.replace('junction_0', 'Junction ').replace('junction_', 'Junction ')}
                            </td>
                            <td className="text-right py-3 px-4 text-white">{location.total_vehicles.toLocaleString()}</td>
                            <td className="text-right py-3 px-4 text-gray-300">{location.videos}</td>
                            <td className="text-right py-3 px-4 text-gray-300">
                              {(location.total_vehicles / location.videos).toFixed(1)}
                            </td>
                            <td className="text-right py-3 px-4">
                              <span className={`px-2 py-1 rounded text-sm ${
                                location.emergency > 0 ? 'bg-red-500/20 text-red-400' : 'bg-gray-500/20 text-gray-400'
                              }`}>
                                {location.emergency}
                              </span>
                            </td>
                            <td className="text-right py-3 px-4">
                              <button
                                onClick={() => {
                                  setSelectedLocation(location.location_id);
                                  setViewMode('location');
                                }}
                                className="px-3 py-1 bg-blue-600/20 text-blue-400 text-sm rounded hover:bg-blue-600/30 transition"
                              >
                                View Details
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="glass-card p-12 text-center">
              <BarChart3 className="w-16 h-16 text-gray-600 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-white mb-2">No Data Available</h3>
              <p className="text-gray-400 mb-4">
                {viewMode === 'location' 
                  ? `No traffic data found for ${selectedLocation} in the selected date range.`
                  : 'No traffic data found for the selected date range.'}
                <br />
                Upload and process videos to see analytics.
              </p>
            </div>
          )}
        </div>
      )}

      {/* Clear History Modal */}
      {showClearModal && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
          <div className="glass-card p-6 max-w-md w-full">
            <div className="flex items-center gap-3 mb-4">
              <AlertTriangle className="w-8 h-8 text-red-400" />
              <h3 className="text-xl font-bold text-white">Clear Analytics History</h3>
            </div>
            <p className="text-gray-300 mb-6">
              {viewMode === 'location'
                ? `This will permanently delete all analytics data for ${selectedLocation}. This action cannot be undone.`
                : 'This will permanently delete ALL analytics data for ALL locations. This action cannot be undone.'}
            </p>
            <div className="flex gap-3">
              <button
                onClick={() => setShowClearModal(false)}
                disabled={clearingData}
                className="flex-1 px-4 py-2 bg-white/10 text-white rounded-lg hover:bg-white/20 transition disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                onClick={handleClearHistory}
                disabled={clearingData}
                className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {clearingData ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    Clearing...
                  </>
                ) : (
                  <>
                    <Trash2 className="w-4 h-4" />
                    Clear Data
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

