import { useEffect, useState, useRef } from 'react';
import { Car, Bike, Truck, Activity, AlertTriangle, TrendingUp, TrendingDown, Video, VideoOff, Camera, Clock, ArrowUp, ArrowDown, ArrowLeft, ArrowRight } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Alert } from '../components/ui/Alert';
import { analyticsAPI } from '../lib/api';

interface VehicleCount {
  car: number;
  truck: number;
  bus: number;
  motorcycle: number;
  bicycle: number;
  'auto-rickshaw': number;
}

interface CameraFeed {
  camera_id: string;
  direction: 'north' | 'south' | 'east' | 'west';
  frame: string | null;
  vehicle_count: number;
  vehicle_types: VehicleCount;
  congestion_level: number;
  fps: number;
  emergency_detected: boolean;
  signal_state: 'green' | 'red' | 'yellow';
  recommended_green_time: number;
  is_connected: boolean;
}

export const DashboardPage: React.FC = () => {
  const [cameras, setCameras] = useState<CameraFeed[]>([
    { 
      camera_id: 'north', 
      direction: 'north', 
      frame: null, 
      vehicle_count: 0, 
      vehicle_types: {car:0,truck:0,bus:0,motorcycle:0,bicycle:0,'auto-rickshaw':0}, 
      congestion_level: 0, 
      fps: 0, 
      emergency_detected: false, 
      signal_state: 'red', 
      recommended_green_time: 30, 
      is_connected: false 
    },
    { 
      camera_id: 'south', 
      direction: 'south', 
      frame: null, 
      vehicle_count: 0, 
      vehicle_types: {car:0,truck:0,bus:0,motorcycle:0,bicycle:0,'auto-rickshaw':0}, 
      congestion_level: 0, 
      fps: 0, 
      emergency_detected: false, 
      signal_state: 'red', 
      recommended_green_time: 30, 
      is_connected: false 
    },
    { 
      camera_id: 'east', 
      direction: 'east', 
      frame: null, 
      vehicle_count: 0, 
      vehicle_types: {car:0,truck:0,bus:0,motorcycle:0,bicycle:0,'auto-rickshaw':0}, 
      congestion_level: 0, 
      fps: 0, 
      emergency_detected: false, 
      signal_state: 'red', 
      recommended_green_time: 30, 
      is_connected: false 
    },
    { 
      camera_id: 'west', 
      direction: 'west', 
      frame: null, 
      vehicle_count: 0, 
      vehicle_types: {car:0,truck:0,bus:0,motorcycle:0,bicycle:0,'auto-rickshaw':0}, 
      congestion_level: 0, 
      fps: 0, 
      emergency_detected: false, 
      signal_state: 'red', 
      recommended_green_time: 30, 
      is_connected: false 
    }
  ]);

  const [totalVehicles, setTotalVehicles] = useState(0);
  const [emergencyActive, setEmergencyActive] = useState(false);
  const [currentGreenDirection, setCurrentGreenDirection] = useState<'north' | 'south' | 'east' | 'west'>('north');
  const wsRef = useRef<WebSocket | null>(null);

  // WebSocket connection for multi-camera live feed
  useEffect(() => {
    const connectWebSocket = () => {
      const ws = new WebSocket('ws://localhost:8000/ws/live-feed');
      wsRef.current = ws;

      ws.onopen = () => {
        // WebSocket connected
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          // Update camera feed based on direction or camera_id
          setCameras(prevCameras => {
            const updatedCameras = [...prevCameras];
            
            // Priority 1: Use direction from backend if provided
            let cameraIndex = -1;
            if (data.direction) {
              cameraIndex = updatedCameras.findIndex(c => c.direction === data.direction);
            }
            
            // Priority 2: Match by camera_id
            if (cameraIndex === -1) {
              cameraIndex = updatedCameras.findIndex(c => c.camera_id === data.camera_id);
            }
            
            // Priority 3: Assign to first disconnected camera
            if (cameraIndex === -1) {
              cameraIndex = updatedCameras.findIndex(c => !c.is_connected);
            }
            
            if (cameraIndex !== -1) {
              const vehicleTypes = data.analysis?.vehicle_types || {};
              const vehicleCount = Object.values(vehicleTypes).reduce((sum: number, count) => sum + (count as number), 0);
              
              updatedCameras[cameraIndex] = {
                ...updatedCameras[cameraIndex],
                frame: data.frame || null,
                vehicle_count: vehicleCount,
                vehicle_types: vehicleTypes,
                congestion_level: calculateCongestion(vehicleCount),
                fps: 20,
                emergency_detected: data.detections?.some((d: any) => d.is_emergency) || false,
                is_connected: true,
                camera_id: data.camera_id || updatedCameras[cameraIndex].camera_id
              };
            }
            
            return updatedCameras;
          });

          // Check for emergency
          if (data.detections?.some((d: any) => d.is_emergency)) {
            setEmergencyActive(true);
          }
        } catch (error) {
          console.error('Error parsing WebSocket data:', error);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      ws.onclose = () => {
        console.log('WebSocket disconnected, reconnecting...');
        setCameras(prev => prev.map(cam => ({ ...cam, is_connected: false })));
        setTimeout(connectWebSocket, 5000);
      };
    };

    connectWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  // Calculate intelligent signal timing
  useEffect(() => {
    const interval = setInterval(() => {
      // Calculate which direction has most traffic
      const trafficDensity = cameras.map(cam => ({
        direction: cam.direction,
        count: cam.vehicle_count,
        emergency: cam.emergency_detected
      }));

      // Priority: Emergency > Highest traffic
      const emergencyDir = trafficDensity.find(d => d.emergency);
      if (emergencyDir) {
        setCurrentGreenDirection(emergencyDir.direction);
        setEmergencyActive(true);
      } else {
        const maxTraffic = trafficDensity.reduce((max, curr) => 
          curr.count > max.count ? curr : max
        );
        setCurrentGreenDirection(maxTraffic.direction);
        setEmergencyActive(false);
      }

      // Update signal states and green times
      setCameras(prev => prev.map(cam => ({
        ...cam,
        signal_state: cam.direction === currentGreenDirection ? 'green' : 'red',
        recommended_green_time: calculateGreenTime(cam.vehicle_count)
      })));

      // Update total vehicles
      const total = cameras.reduce((sum, cam) => sum + cam.vehicle_count, 0);
      setTotalVehicles(total);

    }, 5000); // Update every 5 seconds

    return () => clearInterval(interval);
  }, [cameras, currentGreenDirection]);

  const calculateCongestion = (count: number): number => {
    if (count < 5) return 20;
    if (count < 10) return 40;
    if (count < 15) return 60;
    if (count < 20) return 80;
    return 100;
  };

  const calculateGreenTime = (vehicleCount: number): number => {
    return Math.min(30 + Math.floor(vehicleCount / 5) * 5, 90);
  };

  const getDirectionIcon = (direction: string) => {
    switch(direction) {
      case 'north': return <ArrowUp className="w-5 h-5" />;
      case 'south': return <ArrowDown className="w-5 h-5" />;
      case 'east': return <ArrowRight className="w-5 h-5" />;
      case 'west': return <ArrowLeft className="w-5 h-5" />;
      default: return <Camera className="w-5 h-5" />;
    }
  };

  const getSignalColor = (state: string) => {
    switch(state) {
      case 'green': return 'bg-green-500';
      case 'red': return 'bg-red-500';
      case 'yellow': return 'bg-yellow-500';
      default: return 'bg-gray-500';
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Smart Traffic Control Dashboard</h1>
          <p className="text-gray-400 mt-1">4-Way Intersection Monitoring & Intelligent Signal Control</p>
        </div>
        {emergencyActive && (
          <div className="flex items-center gap-2 bg-red-500/20 border border-red-500 px-4 py-2 rounded-lg animate-pulse">
            <AlertTriangle className="w-5 h-5 text-red-500" />
            <span className="text-red-500 font-semibold">EMERGENCY VEHICLE DETECTED</span>
          </div>
        )}
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-xl p-6 border border-slate-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Total Vehicles</p>
              <p className="text-3xl font-bold text-white mt-1">{totalVehicles}</p>
            </div>
            <Activity className="w-10 h-10 text-blue-500" />
          </div>
        </div>

        <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-xl p-6 border border-slate-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Current Green</p>
              <p className="text-2xl font-bold text-green-500 mt-1 uppercase">{currentGreenDirection}</p>
            </div>
            <div className={`w-10 h-10 rounded-full ${getSignalColor('green')} animate-pulse`} />
          </div>
        </div>

        <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-xl p-6 border border-slate-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Active Cameras</p>
              <p className="text-3xl font-bold text-white mt-1">
                {cameras.filter(c => c.is_connected).length}/4
              </p>
            </div>
            <Camera className="w-10 h-10 text-purple-500" />
          </div>
        </div>

        <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-xl p-6 border border-slate-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">System Status</p>
              <p className="text-2xl font-bold text-green-500 mt-1">ACTIVE</p>
            </div>
            <TrendingUp className="w-10 h-10 text-green-500" />
          </div>
        </div>
      </div>

      {/* 4-Way Camera Grid */}
      <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-xl border border-slate-700 p-6">
        <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
          <Camera className="w-6 h-6 text-blue-500" />
          4-Direction Traffic Monitoring
        </h2>

        <div className="grid grid-cols-2 gap-4">
          {cameras.map((camera) => (
            <div
              key={camera.direction}
              className={`relative bg-slate-900/50 rounded-lg overflow-hidden border-2 transition-all ${
                camera.signal_state === 'green' 
                  ? 'border-green-500 shadow-lg shadow-green-500/50' 
                  : camera.emergency_detected
                  ? 'border-red-500 shadow-lg shadow-red-500/50 animate-pulse'
                  : 'border-slate-700'
              }`}
            >
              {/* Direction Header */}
              <div className={`absolute top-0 left-0 right-0 z-10 px-4 py-2 flex items-center justify-between ${
                camera.signal_state === 'green' ? 'bg-green-500/90' : 'bg-slate-800/90'
              }`}>
                <div className="flex items-center gap-2">
                  {getDirectionIcon(camera.direction)}
                  <span className="font-bold uppercase text-white">{camera.direction}</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className={`w-3 h-3 rounded-full ${getSignalColor(camera.signal_state)}`} />
                  <span className="text-white text-sm font-semibold uppercase">{camera.signal_state}</span>
                </div>
              </div>

              {/* Video Feed */}
              <div className="aspect-video bg-slate-950 relative">
                {camera.is_connected && camera.frame ? (
                  <img
                    src={`data:image/jpeg;base64,${camera.frame}`}
                    alt={`${camera.direction} camera feed`}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="w-full h-full flex flex-col items-center justify-center text-gray-500">
                    <Camera className="w-12 h-12 mb-2 opacity-50" />
                    <p className="text-sm">Camera Offline</p>
                    <p className="text-xs text-gray-600 mt-1">Waiting for stream...</p>
                  </div>
                )}

                {/* Emergency Overlay */}
                {camera.emergency_detected && (
                  <div className="absolute inset-0 bg-red-500/20 border-4 border-red-500 flex items-center justify-center animate-pulse">
                    <div className="bg-red-500 text-white px-4 py-2 rounded-lg font-bold flex items-center gap-2">
                      <AlertTriangle className="w-5 h-5" />
                      EMERGENCY VEHICLE
                    </div>
                  </div>
                )}
              </div>

              {/* Stats Overlay */}
              <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-slate-900 via-slate-900/95 to-transparent p-4">
                <div className="grid grid-cols-3 gap-2 text-center">
                  <div>
                    <p className="text-gray-400 text-xs">Vehicles</p>
                    <p className="text-white font-bold text-lg">{camera.vehicle_count}</p>
                  </div>
                  <div>
                    <p className="text-gray-400 text-xs">Congestion</p>
                    <p className={`font-bold text-lg ${
                      camera.congestion_level > 70 ? 'text-red-500' : 
                      camera.congestion_level > 40 ? 'text-yellow-500' : 'text-green-500'
                    }`}>
                      {camera.congestion_level}%
                    </p>
                  </div>
                  <div>
                    <p className="text-gray-400 text-xs flex items-center justify-center gap-1">
                      <Clock className="w-3 h-3" />
                      Green
                    </p>
                    <p className="text-white font-bold text-lg">{camera.recommended_green_time}s</p>
                  </div>
                </div>

                {/* Vehicle Type Breakdown */}
                {camera.is_connected && Object.values(camera.vehicle_types).some(v => v > 0) && (
                  <div className="mt-2 flex flex-wrap gap-1 text-xs">
                    {Object.entries(camera.vehicle_types).map(([type, count]) => (
                      count > 0 && (
                        <span key={type} className="bg-slate-800 px-2 py-1 rounded text-gray-300">
                          {type}: {count}
                        </span>
                      )
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Signal Control Logic Explanation */}
      <div className="bg-gradient-to-br from-blue-900/20 to-slate-900 rounded-xl border border-blue-500/30 p-6">
        <h3 className="text-lg font-bold text-white mb-3 flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-blue-500" />
          Intelligent Signal Control Logic
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
          <div className="bg-slate-800/50 p-4 rounded-lg">
            <p className="text-red-400 font-semibold mb-2">🚨 Priority 1: Emergency</p>
            <p className="text-gray-300">If emergency vehicle detected, immediate green signal to that direction</p>
          </div>
          <div className="bg-slate-800/50 p-4 rounded-lg">
            <p className="text-green-400 font-semibold mb-2">📊 Priority 2: Traffic Density</p>
            <p className="text-gray-300">Direction with most vehicles gets longer green time (30-90 seconds)</p>
          </div>
          <div className="bg-slate-800/50 p-4 rounded-lg">
            <p className="text-purple-400 font-semibold mb-2">⚖️ Priority 3: Fair Rotation</p>
            <p className="text-gray-300">All directions get minimum 30s green time for fairness</p>
          </div>
        </div>
      </div>
    </div>
  );
};

