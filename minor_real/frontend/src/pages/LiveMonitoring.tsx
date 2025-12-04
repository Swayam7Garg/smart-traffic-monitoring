import React, { useEffect, useState, useRef } from 'react';
import { Video, Activity, Clock, AlertTriangle, Download, CheckCircle, XCircle, Loader, Wifi, WifiOff } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { VideoUpload } from '../components/VideoUpload';
import { trafficAPI } from '../lib/api.ts';

interface ProcessedVideo {
  id: string;
  location_id: string;
  status: string;
  timestamp: string;
  vehicle_count: number;
  vehicle_types: {
    car?: number;
    motorcycle?: number;
    truck?: number;
    bus?: number;
    bicycle?: number;
    'auto-rickshaw'?: number;
  };
  emergency_vehicles: number;
  congestion_level: number;
  output_video: string | null;
  frames: {
    total?: number;
    processed?: number;
    skipped?: number;
  };
}

interface LiveFeedData {
  camera_id: string;
  timestamp: string;
  vehicle_counts: {
    car?: number;
    motorcycle?: number;
    truck?: number;
    bus?: number;
    'auto-rickshaw'?: number;
    bicycle?: number;
  };
  congestion_level: string;
  emergency_vehicles: any[];
  total_detections: number;
}

export const LiveMonitoring: React.FC = () => {
  const [recentVideos, setRecentVideos] = useState<ProcessedVideo[]>([]);
  const [loading, setLoading] = useState(true);
  const [liveFeeds, setLiveFeeds] = useState<Record<string, LiveFeedData>>({});
  const [wsConnected, setWsConnected] = useState(false);
  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    fetchRecentVideos();
    const interval = setInterval(fetchRecentVideos, 5000); // Refresh every 5 seconds
    
    // WebSocket connection for live feeds
    connectWebSocket();
    
    return () => {
      clearInterval(interval);
      if (ws.current) {
        ws.current.close();
      }
    };
  }, []);

  const connectWebSocket = () => {
    try {
      ws.current = new WebSocket('ws://localhost:8000/ws/live-feed');
      
      ws.current.onopen = () => {
        console.log('WebSocket connected');
        setWsConnected(true);
      };
      
      ws.current.onmessage = (event) => {
        const message = JSON.parse(event.data);
        
        if (message.type === 'live_detection') {
          // Update live feeds with latest detection data
          setLiveFeeds(prev => ({
            ...prev,
            [message.camera_id]: message.data
          }));
        }
      };
      
      ws.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        setWsConnected(false);
      };
      
      ws.current.onclose = () => {
        console.log('WebSocket disconnected');
        setWsConnected(false);
        // Reconnect after 5 seconds
        setTimeout(connectWebSocket, 5000);
      };
    } catch (error) {
      console.error('Failed to connect WebSocket:', error);
      setWsConnected(false);
    }
  };

  const fetchRecentVideos = async () => {
    try {
      const data = await trafficAPI.getRecentJobs(10);
      setRecentVideos(data);
    } catch (error) {
      console.error('Failed to fetch recent videos:', error);
    } finally {
      setLoading(false);
    }
  };

  const getCongestionLevel = (level: number) => {
    if (level >= 75) return { label: 'Critical', color: 'text-red-400', bg: 'bg-red-500/20' };
    if (level >= 50) return { label: 'High', color: 'text-orange-400', bg: 'bg-orange-500/20' };
    if (level >= 25) return { label: 'Moderate', color: 'text-yellow-400', bg: 'bg-yellow-500/20' };
    return { label: 'Low', color: 'text-green-400', bg: 'bg-green-500/20' };
  };

  const getCongestionBadge = (level: number) => {
    const congestion = getCongestionLevel(level);
    if (level >= 75) return <Badge variant="danger">{congestion.label}</Badge>;
    if (level >= 50) return <Badge variant="warning">{congestion.label}</Badge>;
    if (level >= 25) return <Badge variant="warning">{congestion.label}</Badge>;
    return <Badge variant="success">{congestion.label}</Badge>;
  };

  const getStatusBadge = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed':
        return <Badge variant="success"><CheckCircle className="w-3 h-3 mr-1" />Completed</Badge>;
      case 'processing':
        return <Badge variant="info"><Loader className="w-3 h-3 mr-1 animate-spin" />Processing</Badge>;
      case 'failed':
        return <Badge variant="danger"><XCircle className="w-3 h-3 mr-1" />Failed</Badge>;
      default:
        return <Badge variant="default">{status}</Badge>;
    }
  };

  const handleDownload = (jobId: string) => {
    trafficAPI.downloadProcessedVideo(jobId);
  };

  const totalVehicles = recentVideos.reduce((sum, v) => sum + (v.vehicle_count || 0), 0);
  const totalEmergencies = recentVideos.reduce((sum, v) => sum + (v.emergency_vehicles || 0), 0);
  const avgCongestion = recentVideos.length > 0 
    ? recentVideos.reduce((sum, v) => sum + (v.congestion_level || 0), 0) / recentVideos.length 
    : 0;

  return (
    <div className="space-y-6">
      {/* WebSocket Status */}
      <div className="flex items-center justify-between bg-slate-800/50 rounded-lg p-3">
        <div className="flex items-center gap-2">
          {wsConnected ? (
            <>
              <Wifi className="w-5 h-5 text-green-400" />
              <span className="text-sm text-green-400">Live feed connected</span>
            </>
          ) : (
            <>
              <WifiOff className="w-5 h-5 text-red-400" />
              <span className="text-sm text-red-400">Live feed disconnected</span>
            </>
          )}
        </div>
        <span className="text-xs text-slate-500">
          {Object.keys(liveFeeds).length} active camera(s)
        </span>
      </div>

      {/* Live Camera Feeds */}
      {Object.keys(liveFeeds).length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <span className="relative flex h-3 w-3">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-red-500"></span>
              </span>
              Live Camera Feeds
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {Object.entries(liveFeeds).map(([cameraId, data]) => (
                <div key={cameraId} className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-medium text-slate-200">{cameraId}</h4>
                    <Badge variant="danger" pulse>LIVE</Badge>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="text-xs text-slate-400">
                      Last Update: {new Date(data.timestamp).toLocaleTimeString()}
                    </div>
                    
                    <div className="grid grid-cols-3 gap-2">
                      {data.vehicle_counts.car !== undefined && (
                        <div className="bg-slate-700/50 rounded p-2">
                          <div className="text-xs text-slate-400">Cars</div>
                          <div className="text-lg font-bold text-blue-400">{data.vehicle_counts.car}</div>
                        </div>
                      )}
                      {data.vehicle_counts.motorcycle !== undefined && (
                        <div className="bg-slate-700/50 rounded p-2">
                          <div className="text-xs text-slate-400">Bikes</div>
                          <div className="text-lg font-bold text-orange-400">{data.vehicle_counts.motorcycle}</div>
                        </div>
                      )}
                      {data.vehicle_counts['auto-rickshaw'] !== undefined && (
                        <div className="bg-slate-700/50 rounded p-2">
                          <div className="text-xs text-slate-400">Autos</div>
                          <div className="text-lg font-bold text-yellow-400">{data.vehicle_counts['auto-rickshaw']}</div>
                        </div>
                      )}
                    </div>
                    
                    <div className="flex items-center justify-between pt-2">
                      <span className="text-xs text-slate-400">
                        Congestion: <span className="font-medium text-slate-200">{data.congestion_level}</span>
                      </span>
                      {data.emergency_vehicles.length > 0 && (
                        <Badge variant="danger">
                          <AlertTriangle className="w-3 h-3 mr-1" />
                          {data.emergency_vehicles.length} Emergency
                        </Badge>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Video Upload Section */}
      <VideoUpload />

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400 mb-1">Total Vehicles Processed</p>
                <p className="text-3xl font-bold text-slate-100">{totalVehicles}</p>
                <p className="text-xs text-slate-500 mt-1">Across {recentVideos.length} videos</p>
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
                <p className="text-sm text-slate-400 mb-1">Emergency Detections</p>
                <p className="text-3xl font-bold text-red-400">{totalEmergencies}</p>
                <p className="text-xs text-slate-500 mt-1">
                  {totalEmergencies > 0 ? 'Requires attention' : 'All clear'}
                </p>
              </div>
              <div className="w-12 h-12 rounded-lg bg-red-500/20 flex items-center justify-center">
                <AlertTriangle className="w-6 h-6 text-red-400" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400 mb-1">Avg. Congestion</p>
                <p className={`text-3xl font-bold ${getCongestionLevel(avgCongestion).color}`}>
                  {avgCongestion.toFixed(0)}%
                </p>
                <p className="text-xs text-slate-500 mt-1">
                  {getCongestionLevel(avgCongestion).label} traffic
                </p>
              </div>
              <div className={`w-12 h-12 rounded-lg ${getCongestionLevel(avgCongestion).bg} flex items-center justify-center`}>
                <Clock className={`w-6 h-6 ${getCongestionLevel(avgCongestion).color}`} />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Processed Videos */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Recent Processed Videos</CardTitle>
            <Badge variant="info" pulse>
              <Activity className="w-3 h-3 mr-1" />
              Auto-refresh (5s)
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-12">
              <div className="inline-block w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mb-4" />
              <p className="text-slate-400">Loading processed videos...</p>
            </div>
          ) : recentVideos.length === 0 ? (
            <div className="text-center py-12">
              <Video className="w-12 h-12 text-slate-600 mx-auto mb-4" />
              <p className="text-slate-400 mb-2">No videos processed yet</p>
              <p className="text-sm text-slate-500">Upload a video above to start analyzing traffic</p>
            </div>
          ) : (
            <div className="space-y-4">
              {recentVideos.map((video, index) => (
                <div
                  key={video.id || index}
                  className="glass rounded-lg p-4 hover:bg-slate-700/50 transition-all"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-3 flex-1">
                      <div className="w-10 h-10 rounded-lg bg-blue-500/20 flex items-center justify-center flex-shrink-0">
                        <Video className="w-5 h-5 text-blue-400" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <h4 className="font-medium text-slate-200 truncate">
                            {video.location_id || 'Unknown Location'}
                          </h4>
                          {getStatusBadge(video.status)}
                        </div>
                        <p className="text-sm text-slate-400 flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {new Date(video.timestamp).toLocaleString()}
                        </p>
                        {video.frames && (
                          <p className="text-xs text-slate-500 mt-1">
                            Processed {video.frames.processed || 0} / {video.frames.total || 0} frames
                            {video.frames.skipped ? ` (${video.frames.skipped} skipped)` : ''}
                          </p>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center gap-2 flex-shrink-0">
                      {getCongestionBadge(video.congestion_level)}
                      {video.output_video && video.status === 'completed' && (
                        <button
                          onClick={() => handleDownload(video.id)}
                          className="p-2 rounded-lg bg-green-500/20 hover:bg-green-500/30 text-green-400 transition-colors"
                          title="Download processed video"
                        >
                          <Download className="w-4 h-4" />
                        </button>
                      )}
                    </div>
                  </div>

                  {/* Vehicle Statistics */}
                  <div className="grid grid-cols-2 md:grid-cols-6 gap-3">
                    <div className="bg-slate-800/50 rounded-lg p-3">
                      <p className="text-xs text-slate-400 mb-1">Total</p>
                      <p className="text-lg font-bold text-slate-100">
                        {video.vehicle_count || 0}
                      </p>
                    </div>
                    
                    <div className="bg-slate-800/50 rounded-lg p-3">
                      <p className="text-xs text-slate-400 mb-1">🚗 Cars</p>
                      <p className="text-lg font-bold text-blue-400">
                        {video.vehicle_types?.car || 0}
                      </p>
                    </div>
                    
                    <div className="bg-slate-800/50 rounded-lg p-3">
                      <p className="text-xs text-slate-400 mb-1">🏍️ Bikes</p>
                      <p className="text-lg font-bold text-orange-400">
                        {video.vehicle_types?.motorcycle || 0}
                      </p>
                    </div>
                    
                    <div className="bg-slate-800/50 rounded-lg p-3">
                      <p className="text-xs text-slate-400 mb-1">🚛 Trucks</p>
                      <p className="text-lg font-bold text-purple-400">
                        {video.vehicle_types?.truck || 0}
                      </p>
                    </div>
                    
                    <div className="bg-slate-800/50 rounded-lg p-3">
                      <p className="text-xs text-slate-400 mb-1">🚌 Buses</p>
                      <p className="text-lg font-bold text-green-400">
                        {video.vehicle_types?.bus || 0}
                      </p>
                    </div>
                    
                    <div className="bg-slate-800/50 rounded-lg p-3">
                      <p className="text-xs text-slate-400 mb-1">🛺 Autos</p>
                      <p className="text-lg font-bold text-yellow-400">
                        {video.vehicle_types?.['auto-rickshaw'] || 0}
                      </p>
                    </div>
                  </div>

                  {/* Emergency Alert */}
                  {video.emergency_vehicles > 0 && (
                    <div className="mt-3 bg-red-500/10 border border-red-500/30 rounded-lg p-3 flex items-center gap-2">
                      <AlertTriangle className="w-4 h-4 text-red-400 flex-shrink-0" />
                      <span className="text-sm text-red-300">
                        🚨 {video.emergency_vehicles} emergency vehicle(s) detected - Priority clearance recommended
                      </span>
                    </div>
                  )}

                  {/* Congestion Info */}
                  <div className="mt-3 flex items-center gap-2">
                    <div className="flex-1 bg-slate-800/30 rounded-full h-2 overflow-hidden">
                      <div
                        className={`h-full transition-all ${
                          video.congestion_level >= 75 ? 'bg-red-500' :
                          video.congestion_level >= 50 ? 'bg-orange-500' :
                          video.congestion_level >= 25 ? 'bg-yellow-500' :
                          'bg-green-500'
                        }`}
                        style={{ width: `${Math.min(video.congestion_level, 100)}%` }}
                      />
                    </div>
                    <span className={`text-sm font-medium ${getCongestionLevel(video.congestion_level).color}`}>
                      {video.congestion_level.toFixed(0)}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Info Card */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 rounded-lg bg-blue-500/20 flex items-center justify-center flex-shrink-0">
              <Activity className="w-4 h-4 text-blue-400" />
            </div>
            <div>
              <h4 className="font-medium text-slate-200 mb-1">How Live Monitoring Works</h4>
              <ul className="text-sm text-slate-400 space-y-1">
                <li>• Upload traffic videos to process with AI-powered vehicle detection</li>
                <li>• GPU-accelerated processing detects cars, bikes, trucks, buses, and auto-rickshaws</li>
                <li>• Emergency vehicles are flagged for priority signal management</li>
                <li>• Download processed videos with bounding boxes and annotations</li>
                <li>• View detailed analytics in the Analytics page for traffic insights</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

