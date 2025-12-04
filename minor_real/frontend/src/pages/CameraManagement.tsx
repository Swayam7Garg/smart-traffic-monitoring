import { useState, useEffect } from 'react';
import { Plus, Video, Trash2, Play, Square, Camera, MapPin, Radio, CheckCircle, AlertCircle } from 'lucide-react';
import { Card, CardContent } from '../components/ui/Card';

interface Camera {
  camera_id: string;
  name: string;
  rtsp_url: string;
  location_id: string;
  location_name: string;
  direction?: string;
  status: string;
  is_streaming: boolean;
  created_at: string;
  last_active?: string;
}

interface CameraForm {
  camera_id: string;
  name: string;
  rtsp_url: string;
  location_id: string;
  location_name: string;
  direction: string;
}

export default function CameraManagement() {
  const [cameras, setCameras] = useState<Camera[]>([]);
  const [showAddModal, setShowAddModal] = useState(false);
  const [loading, setLoading] = useState(false);
  const [statusMessage, setStatusMessage] = useState('');
  const [statusType, setStatusType] = useState<'success' | 'error' | 'info'>('info');
  const [formData, setFormData] = useState<CameraForm>({
    camera_id: '',
    name: '',
    rtsp_url: '',
    location_id: '',
    location_name: '',
    direction: ''
  });

  const showStatus = (message: string, type: 'success' | 'error' | 'info' = 'info') => {
    setStatusMessage(message);
    setStatusType(type);
    setTimeout(() => setStatusMessage(''), 4000);
  };

  // Fetch cameras
  const fetchCameras = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/cameras/cameras');
      const data = await response.json();
      setCameras(data);
    } catch (error) {
      console.error('Error fetching cameras:', error);
      showStatus('Failed to fetch cameras', 'error');
    }
  };

  useEffect(() => {
    fetchCameras();
    // Auto-refresh every 5 seconds
    const interval = setInterval(fetchCameras, 5000);
    return () => clearInterval(interval);
  }, []);

  // Add camera
  const handleAddCamera = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/v1/cameras/cameras', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        setShowAddModal(false);
        setFormData({
          camera_id: '',
          name: '',
          rtsp_url: '',
          location_id: '',
          location_name: '',
          direction: ''
        });
        fetchCameras();
        showStatus('Camera added successfully!', 'success');
      } else {
        const error = await response.json();
        showStatus(error.detail || 'Failed to add camera', 'error');
      }
    } catch (error) {
      console.error('Error adding camera:', error);
      showStatus('Failed to add camera', 'error');
    } finally {
      setLoading(false);
    }
  };

  // Start/Stop stream
  const handleStreamControl = async (cameraId: string, action: 'start' | 'stop') => {
    try {
      const response = await fetch(
        `http://localhost:8000/api/v1/cameras/cameras/${cameraId}/stream?action=${action}`,
        { method: 'POST' }
      );

      if (response.ok) {
        fetchCameras();
        const result = await response.json();
        showStatus(result.message, 'success');
      } else {
        const error = await response.json();
        showStatus(error.detail || `Failed to ${action} stream`, 'error');
      }
    } catch (error) {
      console.error('Error controlling stream:', error);
      showStatus(`Failed to ${action} stream`, 'error');
    }
  };

  // Delete camera
  const handleDeleteCamera = async (cameraId: string) => {
    if (!confirm('Are you sure you want to delete this camera?')) return;

    try {
      const response = await fetch(
        `http://localhost:8000/api/v1/cameras/cameras/${cameraId}`,
        { method: 'DELETE' }
      );

      if (response.ok) {
        fetchCameras();
        showStatus('Camera deleted successfully', 'success');
      } else {
        const error = await response.json();
        showStatus(error.detail || 'Failed to delete camera', 'error');
      }
    } catch (error) {
      console.error('Error deleting camera:', error);
      showStatus('Failed to delete camera', 'error');
    }
  };

  const activeCameras = cameras.filter(c => c.is_streaming).length;
  const totalCameras = cameras.length;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <div className="p-3 bg-blue-500/20 rounded-xl">
                  <Camera className="h-8 w-8 text-blue-400" />
                </div>
                <h1 className="text-3xl font-bold text-slate-100">Camera Management</h1>
              </div>
              <p className="text-slate-400">Manage traffic monitoring cameras and live streams</p>
            </div>
            <button
              onClick={() => setShowAddModal(true)}
              className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-xl hover:from-blue-700 hover:to-blue-800 transition-all shadow-lg hover:shadow-blue-500/50"
            >
              <Plus className="w-5 h-5" />
              Add Camera
            </button>
          </div>
        </div>

        {/* Multi-Camera Info Box */}
        <div className="mb-6 p-5 rounded-xl border border-blue-500/30 bg-gradient-to-r from-blue-500/10 to-purple-500/10">
          <div className="flex items-start gap-3">
            <AlertCircle className="h-5 w-5 text-blue-400 mt-0.5 flex-shrink-0" />
            <div className="flex-1">
              <h3 className="text-blue-400 font-semibold mb-2">📹 Multi-Camera Dashboard Integration</h3>
              <div className="text-sm text-slate-300 space-y-1">
                <p>• <strong>1 Camera:</strong> Shows in one direction (North/South/East/West) on Dashboard</p>
                <p>• <strong>2-4 Cameras:</strong> Each fills next available direction automatically</p>
                <p>• <strong>Direction Control:</strong> Include "North", "South", "East", or "West" in camera name</p>
                <p>• <strong>Example:</strong> Camera named "North Junction" will appear in North direction on Dashboard</p>
              </div>
            </div>
          </div>
        </div>

        {/* Status Message */}
        {statusMessage && (
          <div className={`mb-6 p-4 rounded-xl border flex items-center gap-3 ${
            statusType === 'success' ? 'bg-green-500/10 border-green-500/30 text-green-400' :
            statusType === 'error' ? 'bg-red-500/10 border-red-500/30 text-red-400' :
            'bg-blue-500/10 border-blue-500/30 text-blue-400'
          }`}>
            {statusType === 'success' && <CheckCircle className="h-5 w-5" />}
            {statusType === 'error' && <AlertCircle className="h-5 w-5" />}
            {statusType === 'info' && <AlertCircle className="h-5 w-5" />}
            <span className="font-medium">{statusMessage}</span>
          </div>
        )}

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card hover className="bg-gradient-to-br from-slate-800 to-slate-900 border-slate-700">
            <CardContent>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-400 mb-1">Total Cameras</p>
                  <p className="text-3xl font-bold text-slate-100">{totalCameras}</p>
                </div>
                <div className="p-4 bg-blue-500/20 rounded-xl">
                  <Camera className="h-8 w-8 text-blue-400" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card hover className="bg-gradient-to-br from-slate-800 to-slate-900 border-slate-700">
            <CardContent>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-400 mb-1">Active Streams</p>
                  <p className="text-3xl font-bold text-green-400">{activeCameras}</p>
                </div>
                <div className="p-4 bg-green-500/20 rounded-xl">
                  <Radio className="h-8 w-8 text-green-400" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card hover className="bg-gradient-to-br from-slate-800 to-slate-900 border-slate-700">
            <CardContent>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-400 mb-1">Offline</p>
                  <p className="text-3xl font-bold text-slate-400">{totalCameras - activeCameras}</p>
                </div>
                <div className="p-4 bg-slate-700/50 rounded-xl">
                  <Video className="h-8 w-8 text-slate-400" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Camera Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {cameras.length === 0 ? (
            <div className="col-span-full">
              <Card className="bg-gradient-to-br from-slate-800 to-slate-900 border-slate-700">
                <CardContent>
                  <div className="text-center py-12">
                    <div className="inline-flex p-4 bg-slate-700/50 rounded-full mb-4">
                      <Camera className="h-12 w-12 text-slate-400" />
                    </div>
                    <h3 className="text-xl font-semibold text-slate-100 mb-2">No Cameras Added</h3>
                    <p className="text-slate-400 mb-4">Add your first camera to start live monitoring</p>
                    <button
                      onClick={() => setShowAddModal(true)}
                      className="px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-xl hover:from-blue-700 hover:to-blue-800 transition-all shadow-lg"
                    >
                      <Plus className="inline w-5 h-5 mr-2" />
                      Add Camera
                    </button>
                  </div>
                </CardContent>
              </Card>
            </div>
          ) : (
            cameras.map((camera) => (
              <Card key={camera.camera_id} hover className="bg-gradient-to-br from-slate-800 to-slate-900 border-slate-700">
                <CardContent>
                  <div className="space-y-4">
                    {/* Header */}
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold text-slate-100 mb-1">{camera.name}</h3>
                        <div className="flex items-center gap-2 text-sm text-slate-400">
                          <MapPin className="w-4 h-4" />
                          <span>{camera.location_name}</span>
                        </div>
                        {camera.direction && (
                          <p className="text-xs text-slate-500 mt-1">{camera.direction}</p>
                        )}
                      </div>
                      <span className={`flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium ${
                        camera.is_streaming
                          ? 'bg-green-500/20 text-green-400 border border-green-500/30'
                          : 'bg-slate-700/50 text-slate-400 border border-slate-600'
                      }`}>
                        {camera.is_streaming && (
                          <span className="flex h-2 w-2">
                            <span className="animate-ping absolute inline-flex h-2 w-2 rounded-full bg-green-400 opacity-75"></span>
                            <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
                          </span>
                        )}
                        {camera.is_streaming ? 'Live' : 'Offline'}
                      </span>
                    </div>

                    {/* Camera Info */}
                    <div className="space-y-3 pt-3 border-t border-slate-700">
                      <div className="flex items-center gap-2 text-sm">
                        <div className="p-2 bg-blue-500/10 rounded-lg">
                          <Video className="w-4 h-4 text-blue-400" />
                        </div>
                        <span className="text-slate-300 font-mono truncate">{camera.camera_id}</span>
                      </div>
                      <div className="p-3 bg-slate-900/50 rounded-lg">
                        <p className="text-xs text-slate-500 font-mono break-all">
                          {camera.rtsp_url}
                        </p>
                      </div>
                      {camera.last_active && (
                        <div className="text-xs text-slate-500">
                          Last active: {new Date(camera.last_active).toLocaleString()}
                        </div>
                      )}
                    </div>

                    {/* Actions */}
                    <div className="flex gap-2 pt-3">
                      {camera.is_streaming ? (
                        <button
                          onClick={() => handleStreamControl(camera.camera_id, 'stop')}
                          className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl font-medium transition-all bg-red-500/20 text-red-400 hover:bg-red-500/30 border border-red-500/30"
                        >
                          <Square className="w-4 h-4" />
                          Stop Stream
                        </button>
                      ) : (
                        <button
                          onClick={() => handleStreamControl(camera.camera_id, 'start')}
                          className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl font-medium transition-all bg-green-500/20 text-green-400 hover:bg-green-500/30 border border-green-500/30"
                        >
                          <Play className="w-4 h-4" />
                          Start Stream
                        </button>
                      )}
                      <button
                        onClick={() => handleDeleteCamera(camera.camera_id)}
                        disabled={camera.is_streaming}
                        className={`p-2.5 rounded-xl transition-all ${
                          camera.is_streaming
                            ? 'text-slate-600 bg-slate-800 border border-slate-700 cursor-not-allowed'
                            : 'text-red-400 hover:bg-red-500/20 border border-red-500/30'
                        }`}
                        title="Delete Camera"
                      >
                        <Trash2 className="w-5 h-5" />
                      </button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>

        {/* Add Camera Modal */}
        {showAddModal && (
          <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl p-6 w-full max-w-md border border-slate-700 shadow-2xl">
              <div className="flex items-center gap-3 mb-6">
                <div className="p-3 bg-blue-500/20 rounded-xl">
                  <Camera className="h-6 w-6 text-blue-400" />
                </div>
                <h2 className="text-2xl font-bold text-slate-100">Add New Camera</h2>
              </div>
              
              <form onSubmit={handleAddCamera} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Camera ID *
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.camera_id}
                    onChange={(e) => setFormData({ ...formData, camera_id: e.target.value })}
                    className="w-full px-4 py-3 bg-slate-900/50 border border-slate-700 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-slate-100 placeholder-slate-500"
                    placeholder="cam_001"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Camera Name * 
                    <span className="text-xs text-blue-400 ml-2">
                      (Use "North", "South", "East", or "West" for dashboard direction)
                    </span>
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="w-full px-4 py-3 bg-slate-900/50 border border-slate-700 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-slate-100 placeholder-slate-500"
                    placeholder="North Junction Camera"
                  />
                  <p className="text-xs text-slate-500 mt-1">
                    💡 Tip: Name contains "North" → Shows in North direction on Dashboard
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    RTSP/HTTP URL *
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.rtsp_url}
                    onChange={(e) => setFormData({ ...formData, rtsp_url: e.target.value })}
                    className="w-full px-4 py-3 bg-slate-900/50 border border-slate-700 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-slate-100 placeholder-slate-500 font-mono text-sm"
                    placeholder="rtsp://192.168.1.100:554/stream"
                  />
                  <p className="text-xs text-slate-500 mt-1">Supports RTSP, HTTP, or local video files</p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Location ID *
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.location_id}
                    onChange={(e) => setFormData({ ...formData, location_id: e.target.value })}
                    className="w-full px-4 py-3 bg-slate-900/50 border border-slate-700 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-slate-100 placeholder-slate-500"
                    placeholder="loc_001"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Location Name *
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.location_name}
                    onChange={(e) => setFormData({ ...formData, location_name: e.target.value })}
                    className="w-full px-4 py-3 bg-slate-900/50 border border-slate-700 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-slate-100 placeholder-slate-500"
                    placeholder="MG Road Junction"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Direction (Optional)
                  </label>
                  <input
                    type="text"
                    value={formData.direction}
                    onChange={(e) => setFormData({ ...formData, direction: e.target.value })}
                    className="w-full px-4 py-3 bg-slate-900/50 border border-slate-700 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-slate-100 placeholder-slate-500"
                    placeholder="North-South"
                  />
                </div>

                <div className="flex gap-3 pt-4">
                  <button
                    type="button"
                    onClick={() => setShowAddModal(false)}
                    className="flex-1 px-4 py-3 border border-slate-600 text-slate-300 rounded-xl hover:bg-slate-800 transition-all"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={loading}
                    className="flex-1 px-4 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-xl hover:from-blue-700 hover:to-blue-800 disabled:from-slate-700 disabled:to-slate-800 disabled:text-slate-500 transition-all shadow-lg"
                  >
                    {loading ? 'Adding...' : 'Add Camera'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
