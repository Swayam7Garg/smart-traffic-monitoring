import React, { useState, useEffect } from 'react';
import { 
  Settings as SettingsIcon, 
  Save, 
  RefreshCw, 
  AlertCircle, 
  CheckCircle,
  Clock,
  MapPin,
  ScanSearch,
  Sliders,
  Plus,
  Trash2,
  X
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { settingsAPI } from '';

// Types
interface SignalTiming {
  location_id: string;
  location_name: string;
  vehicle_type: string;
  green_duration: number;
  red_duration: number;
  time_period: 'peak' | 'normal' | 'night';
}

interface Location {
  id: string;
  name: string;
  latitude: number;
  longitude: number;
  camera_id: string;
  status: 'active' | 'inactive';
}

interface DetectionConfig {
  confidence_threshold: number;
  iou_threshold: number;
  emergency_color_threshold: number;
  autorickshaw_size_threshold: number;
  frame_skip: number;
}

interface SystemSettings {
  auto_refresh_interval: number;
  max_video_size_mb: number;
  enable_notifications: boolean;
  dark_mode: boolean;
  language: string;
}

const Settings: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'signals' | 'locations' | 'detection' | 'system'>('signals');
  const [loading, setLoading] = useState(false);
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'success' | 'error'>('idle');
  const [statusMessage, setStatusMessage] = useState('');

  // Signal Timing State
  const [signalTimings, setSignalTimings] = useState<SignalTiming[]>([]);

  // Location State
  const [locations, setLocations] = useState<Location[]>([]);
  const [showAddLocation, setShowAddLocation] = useState(false);
  const [newLocation, setNewLocation] = useState<Partial<Location>>({
    name: '',
    latitude: 0,
    longitude: 0,
    camera_id: '',
    status: 'active'
  });

  // Detection Config State
  const [detectionConfig, setDetectionConfig] = useState<DetectionConfig>({
    confidence_threshold: 0.2,
    iou_threshold: 0.4,
    emergency_color_threshold: 50,
    autorickshaw_size_threshold: 25000,
    frame_skip: 2
  });

  // System Settings State
  const [systemSettings, setSystemSettings] = useState<SystemSettings>({
    auto_refresh_interval: 5000,
    max_video_size_mb: 500,
    enable_notifications: true,
    dark_mode: false,
    language: 'en'
  });

  useEffect(() => {
    loadSettings();
  }, [activeTab]);

  const loadSettings = async () => {
    setLoading(true);
    try {
      // Load data based on active tab
      if (activeTab === 'signals') {
        await loadSignalTimings();
      } else if (activeTab === 'locations') {
        await loadLocations();
      } else if (activeTab === 'detection') {
        await loadDetectionConfig();
      } else if (activeTab === 'system') {
        await loadSystemSettings();
      }
    } catch (error) {
      console.error('Error loading settings:', error);
      setStatusMessage('Failed to load settings');
      setSaveStatus('error');
      // Set default values on error
      if (activeTab === 'signals') setSignalTimings([]);
      if (activeTab === 'locations') setLocations([]);
    } finally {
      setLoading(false);
    }
  };

  const loadSignalTimings = async () => {
    try {
      const response = await settingsAPI.getSignalTimings();
      setSignalTimings(response);
    } catch (error) {
      console.error('Error loading signal timings:', error);
      setSignalTimings([]);
    }
  };

  const loadLocations = async () => {
    try {
      const response = await settingsAPI.getLocations();
      setLocations(response);
    } catch (error) {
      console.error('Error loading locations:', error);
      setLocations([]);
    }
  };

  const loadDetectionConfig = async () => {
    try {
      const response = await settingsAPI.getDetectionConfig();
      setDetectionConfig({
        confidence_threshold: response.confidence_threshold,
        iou_threshold: response.iou_threshold,
        emergency_color_threshold: response.emergency_color_threshold,
        autorickshaw_size_threshold: response.autorickshaw_size_threshold,
        frame_skip: response.frame_skip
      });
    } catch (error) {
      console.error('Error loading detection config:', error);
      setDetectionConfig({
        confidence_threshold: 0.2,
        iou_threshold: 0.4,
        emergency_color_threshold: 50,
        autorickshaw_size_threshold: 25000,
        frame_skip: 2
      });
    }
  };

  const loadSystemSettings = async () => {
    try {
      const response = await settingsAPI.getSystemSettings();
      setSystemSettings({
        auto_refresh_interval: response.auto_refresh_interval,
        max_video_size_mb: response.max_video_size_mb,
        enable_notifications: response.enable_notifications,
        dark_mode: response.dark_mode,
        language: response.language
      });
    } catch (error) {
      console.error('Error loading system settings:', error);
      setSystemSettings({
        auto_refresh_interval: 5000,
        max_video_size_mb: 500,
        enable_notifications: true,
        dark_mode: false,
        language: 'en'
      });
    }
  };

  const saveSettings = async () => {
    setSaveStatus('saving');
    setStatusMessage('Saving changes...');
    
    try {
      if (activeTab === 'signals') {
        await settingsAPI.updateSignalTimings(signalTimings);
      } else if (activeTab === 'locations') {
        // Note: locations are updated individually on add/edit/delete
        // This just confirms the current state
        setStatusMessage('Locations are saved automatically');
      } else if (activeTab === 'detection') {
        await settingsAPI.updateDetectionConfig(detectionConfig);
      } else if (activeTab === 'system') {
        await settingsAPI.updateSystemSettings(systemSettings);
      }
      
      setSaveStatus('success');
      setStatusMessage('Settings saved successfully!');
      
      // Reset status after 3 seconds
      setTimeout(() => {
        setSaveStatus('idle');
        setStatusMessage('');
      }, 3000);
    } catch (error) {
      console.error('Error saving settings:', error);
      setSaveStatus('error');
      setStatusMessage('Failed to save settings');
      setTimeout(() => {
        setSaveStatus('idle');
        setStatusMessage('');
      }, 5000);
    }
  };

  const resetToDefaults = async () => {
    if (window.confirm('Are you sure you want to reset to default settings? This cannot be undone.')) {
      setSaveStatus('saving');
      setStatusMessage('Resetting to defaults...');
      
      try {
        if (activeTab === 'detection') {
          const response = await settingsAPI.resetDetectionConfig();
          setDetectionConfig({
            confidence_threshold: response.config.confidence_threshold,
            iou_threshold: response.config.iou_threshold,
            emergency_color_threshold: response.config.emergency_color_threshold,
            autorickshaw_size_threshold: response.config.autorickshaw_size_threshold,
            frame_skip: response.config.frame_skip
          });
        } else if (activeTab === 'system') {
          const response = await settingsAPI.resetSystemSettings();
          setSystemSettings({
            auto_refresh_interval: response.settings.auto_refresh_interval,
            max_video_size_mb: response.settings.max_video_size_mb,
            enable_notifications: response.settings.enable_notifications,
            dark_mode: response.settings.dark_mode,
            language: response.settings.language
          });
        }
        
        setStatusMessage('Reset to default values');
        setSaveStatus('success');
        setTimeout(() => {
          setSaveStatus('idle');
          setStatusMessage('');
        }, 3000);
      } catch (error) {
        console.error('Error resetting settings:', error);
        setSaveStatus('error');
        setStatusMessage('Failed to reset settings');
        setTimeout(() => {
          setSaveStatus('idle');
          setStatusMessage('');
        }, 5000);
      }
    }
  };

  // Signal Timing Handlers
  const updateSignalTiming = (index: number, field: keyof SignalTiming, value: any) => {
    const updated = [...signalTimings];
    updated[index] = { ...updated[index], [field]: value };
    setSignalTimings(updated);
  };

  // Location Handlers
  const addLocation = async () => {
    if (!newLocation.name || !newLocation.camera_id) {
      alert('Please fill in all required fields');
      return;
    }
    
    try {
      const location = await settingsAPI.createLocation({
        name: newLocation.name || '',
        latitude: newLocation.latitude || 0,
        longitude: newLocation.longitude || 0,
        camera_id: newLocation.camera_id || '',
        status: newLocation.status || 'active'
      });
      
      setLocations([...locations, location]);
      setShowAddLocation(false);
      setNewLocation({ name: '', latitude: 0, longitude: 0, camera_id: '', status: 'active' });
      
      setStatusMessage('Location added successfully');
      setSaveStatus('success');
      setTimeout(() => {
        setSaveStatus('idle');
        setStatusMessage('');
      }, 3000);
    } catch (error) {
      console.error('Error adding location:', error);
      alert('Failed to add location');
    }
  };

  const deleteLocation = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this location?')) {
      try {
        await settingsAPI.deleteLocation(id);
        setLocations(locations.filter(loc => loc.id !== id));
        
        setStatusMessage('Location deleted successfully');
        setSaveStatus('success');
        setTimeout(() => {
          setSaveStatus('idle');
          setStatusMessage('');
        }, 3000);
      } catch (error) {
        console.error('Error deleting location:', error);
        alert('Failed to delete location');
      }
    }
  };

  const toggleLocationStatus = async (id: string) => {
    const location = locations.find(loc => loc.id === id);
    if (!location) return;
    
    const newStatus = location.status === 'active' ? 'inactive' : 'active';
    
    try {
      await settingsAPI.updateLocation(id, { status: newStatus });
      setLocations(locations.map(loc => 
        loc.id === id ? { ...loc, status: newStatus } : loc
      ));
      
      setStatusMessage(`Location ${newStatus === 'active' ? 'activated' : 'deactivated'}`);
      setSaveStatus('success');
      setTimeout(() => {
        setSaveStatus('idle');
        setStatusMessage('');
      }, 3000);
    } catch (error) {
      console.error('Error updating location:', error);
      alert('Failed to update location status');
    }
  };

  // Render Tab Content
  const renderSignalTimings = () => (
    <Card className="bg-gradient-to-br from-slate-800 to-slate-900 border-slate-700">
      <CardHeader>
        <CardTitle className="text-slate-100">Signal Timing Configuration</CardTitle>
        <p className="text-sm text-slate-400">Adjust traffic signal durations based on vehicle type and time period</p>
      </CardHeader>
      <CardContent>
        <div className="bg-slate-900/50 rounded-xl border border-slate-700 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-700">
              <thead className="bg-slate-800/50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                  Location
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Vehicle Type
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Time Period
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Green Duration (s)
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Red Duration (s)
                </th>
              </tr>
            </thead>
              <tbody className="bg-slate-900/30 divide-y divide-slate-700">
                {signalTimings.map((timing, index) => (
                  <tr key={index} className="hover:bg-slate-800/50 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-slate-200">
                    {timing.location_name}
                  </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-300">
                      <span className="capitalize">{timing.vehicle_type}</span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium capitalize
                        ${timing.time_period === 'peak' ? 'bg-red-500/20 text-red-400 border border-red-500/30' : 
                          timing.time_period === 'normal' ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30' : 
                          'bg-purple-500/20 text-purple-400 border border-purple-500/30'}`}>
                        {timing.time_period}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <input
                        type="number"
                        value={timing.green_duration}
                        onChange={(e) => updateSignalTiming(index, 'green_duration', parseInt(e.target.value))}
                        className="w-20 px-3 py-1.5 bg-slate-800 border border-slate-700 text-slate-200 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                        min="10"
                        max="120"
                      />
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <input
                        type="number"
                        value={timing.red_duration}
                        onChange={(e) => updateSignalTiming(index, 'red_duration', parseInt(e.target.value))}
                        className="w-20 px-3 py-1.5 bg-slate-800 border border-slate-700 text-slate-200 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500"
                        min="10"
                        max="120"
                      />
                    </td>
                </tr>
              ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="bg-blue-500/10 border border-blue-500/30 rounded-xl p-4 mt-4">
          <div className="flex">
            <AlertCircle className="h-5 w-5 text-blue-400 mr-2 flex-shrink-0" />
            <div className="text-sm text-blue-300">
              <p className="font-medium">Signal Timing Guidelines:</p>
              <ul className="list-disc list-inside mt-1 space-y-1 text-blue-400/90">
                <li>Peak hours: 7-10 AM, 5-8 PM (higher traffic volume)</li>
                <li>Normal hours: 10 AM-5 PM (moderate traffic)</li>
                <li>Night hours: 8 PM-7 AM (low traffic volume)</li>
                <li>Adjust durations based on real-time analytics data</li>
              </ul>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );

  const renderLocations = () => (
    <Card className="bg-gradient-to-br from-slate-800 to-slate-900 border-slate-700">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-slate-100">Location Management</CardTitle>
            <p className="text-sm text-slate-400 mt-1">Manage traffic monitoring locations and camera assignments</p>
          </div>
          <button
            onClick={() => setShowAddLocation(true)}
            className="flex items-center gap-2 px-4 py-2.5 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-xl hover:from-blue-700 hover:to-blue-800 transition-all shadow-lg"
          >
            <Plus className="h-4 w-4" />
            Add Location
          </button>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">

      {showAddLocation && (
        <div className="bg-white rounded-lg border-2 border-blue-500 p-6 mb-4">
          <div className="flex items-center justify-between mb-4">
            <h4 className="text-lg font-semibold text-gray-900">Add New Location</h4>
            <button
              onClick={() => setShowAddLocation(false)}
              className="text-gray-400 hover:text-gray-600"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Location Name *</label>
              <input
                type="text"
                value={newLocation.name}
                onChange={(e) => setNewLocation({ ...newLocation, name: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="e.g., Main Junction"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Camera ID *</label>
              <input
                type="text"
                value={newLocation.camera_id}
                onChange={(e) => setNewLocation({ ...newLocation, camera_id: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="e.g., CAM001"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Latitude</label>
              <input
                type="number"
                step="0.0001"
                value={newLocation.latitude}
                onChange={(e) => setNewLocation({ ...newLocation, latitude: parseFloat(e.target.value) })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="28.7041"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Longitude</label>
              <input
                type="number"
                step="0.0001"
                value={newLocation.longitude}
                onChange={(e) => setNewLocation({ ...newLocation, longitude: parseFloat(e.target.value) })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="77.1025"
              />
            </div>
          </div>
          <div className="mt-4 flex gap-2">
            <button
              onClick={addLocation}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Add Location
            </button>
            <button
              onClick={() => setShowAddLocation(false)}
              className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      <div className="grid gap-4">
        {locations.map((location) => (
          <div
            key={location.id}
            className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-3">
                  <h4 className="text-lg font-semibold text-gray-900">{location.name}</h4>
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
                    ${location.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                    {location.status}
                  </span>
                </div>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600">Location ID:</span>
                    <span className="ml-2 font-mono text-gray-900">{location.id}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Camera ID:</span>
                    <span className="ml-2 font-mono text-gray-900">{location.camera_id}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Coordinates:</span>
                    <span className="ml-2 text-gray-900">
                      {location.latitude.toFixed(4)}, {location.longitude.toFixed(4)}
                    </span>
                  </div>
                </div>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => toggleLocationStatus(location.id)}
                  className={`p-2 rounded-lg transition-colors ${
                    location.status === 'active'
                      ? 'bg-yellow-100 text-yellow-700 hover:bg-yellow-200'
                      : 'bg-green-100 text-green-700 hover:bg-green-200'
                  }`}
                  title={location.status === 'active' ? 'Deactivate' : 'Activate'}
                >
                  <RefreshCw className="h-4 w-4" />
                </button>
                <button
                  onClick={() => deleteLocation(location.id)}
                  className="p-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors"
                  title="Delete location"
                >
                  <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );

  const renderDetectionConfig = () => (
    <Card className="bg-gradient-to-br from-slate-800 to-slate-900 border-slate-700">
      <CardHeader>
        <CardTitle className="text-slate-100">Detection Configuration</CardTitle>
        <p className="text-sm text-slate-400">Fine-tune vehicle detection parameters for optimal accuracy</p>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Confidence Threshold */}
        <div className="p-4 bg-slate-900/50 rounded-xl border border-slate-700">
          <div className="flex items-center justify-between mb-3">
            <label className="text-sm font-medium text-slate-300">Confidence Threshold</label>
            <span className="text-sm font-semibold text-blue-400 bg-blue-500/20 px-3 py-1 rounded-lg">
              {detectionConfig.confidence_threshold.toFixed(2)}
            </span>
          </div>
          <input
            type="range"
            min="0.1"
            max="0.9"
            step="0.05"
            value={detectionConfig.confidence_threshold}
            onChange={(e) => setDetectionConfig({ ...detectionConfig, confidence_threshold: parseFloat(e.target.value) })}
            className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-blue-500"
          />
          <p className="text-xs text-slate-500 mt-2">
            Minimum confidence score for vehicle detection (lower = more detections but more false positives)
          </p>
        </div>

        {/* IOU Threshold */}
        <div className="p-4 bg-slate-900/50 rounded-xl border border-slate-700">
          <div className="flex items-center justify-between mb-3">
            <label className="text-sm font-medium text-slate-300">IOU Threshold</label>
            <span className="text-sm font-semibold text-blue-400 bg-blue-500/20 px-3 py-1 rounded-lg">
              {detectionConfig.iou_threshold.toFixed(2)}
            </span>
          </div>
          <input
            type="range"
            min="0.1"
            max="0.9"
            step="0.05"
            value={detectionConfig.iou_threshold}
            onChange={(e) => setDetectionConfig({ ...detectionConfig, iou_threshold: parseFloat(e.target.value) })}
            className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-blue-500"
          />
          <p className="text-xs text-slate-500 mt-2">
            Intersection over Union for non-maximum suppression (lower = better for overlapping vehicles)
          </p>
        </div>

        {/* Emergency Color Threshold */}
        <div className="p-4 bg-slate-900/50 rounded-xl border border-slate-700">
          <div className="flex items-center justify-between mb-3">
            <label className="text-sm font-medium text-slate-300">Emergency Vehicle Color Threshold (%)</label>
            <span className="text-sm font-semibold text-red-400 bg-red-500/20 px-3 py-1 rounded-lg">
              {detectionConfig.emergency_color_threshold}%
            </span>
          </div>
          <input
            type="range"
            min="20"
            max="80"
            step="5"
            value={detectionConfig.emergency_color_threshold}
            onChange={(e) => setDetectionConfig({ ...detectionConfig, emergency_color_threshold: parseInt(e.target.value) })}
            className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-red-500"
          />
          <p className="text-xs text-slate-500 mt-2">
            Percentage of red/blue pixels required to classify as emergency vehicle
          </p>
        </div>

        {/* Auto-rickshaw Size Threshold */}
        <div className="p-4 bg-slate-900/50 rounded-xl border border-slate-700">
          <div className="flex items-center justify-between mb-3">
            <label className="text-sm font-medium text-slate-300">Auto-rickshaw Size Threshold (pixels)</label>
            <span className="text-sm font-semibold text-green-400 bg-green-500/20 px-3 py-1 rounded-lg">
              {detectionConfig.autorickshaw_size_threshold.toLocaleString()}
            </span>
          </div>
          <input
            type="range"
            min="10000"
            max="50000"
            step="1000"
            value={detectionConfig.autorickshaw_size_threshold}
            onChange={(e) => setDetectionConfig({ ...detectionConfig, autorickshaw_size_threshold: parseInt(e.target.value) })}
            className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-green-500"
          />
          <p className="text-xs text-slate-500 mt-2">
            Maximum bounding box size for auto-rickshaw classification
          </p>
        </div>

        {/* Frame Skip */}
        <div className="p-4 bg-slate-900/50 rounded-xl border border-slate-700">
          <div className="flex items-center justify-between mb-3">
            <label className="text-sm font-medium text-slate-300">Frame Skip Rate</label>
            <span className="text-sm font-semibold text-purple-400 bg-purple-500/20 px-3 py-1 rounded-lg">
              {detectionConfig.frame_skip}
            </span>
          </div>
          <input
            type="range"
            min="1"
            max="10"
            step="1"
            value={detectionConfig.frame_skip}
            onChange={(e) => setDetectionConfig({ ...detectionConfig, frame_skip: parseInt(e.target.value) })}
            className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-purple-500"
          />
          <p className="text-xs text-slate-500 mt-2">
            Process every Nth frame (higher = faster processing but less accuracy)
          </p>
        </div>

        <div className="bg-amber-500/10 border border-amber-500/30 rounded-xl p-4 mt-6">
          <div className="flex">
            <AlertCircle className="h-5 w-5 text-amber-400 mr-2 flex-shrink-0" />
            <div className="text-sm text-amber-300">
              <p className="font-medium">Current Optimized Settings:</p>
              <ul className="list-disc list-inside mt-1 space-y-1 text-amber-400/90">
                <li>Confidence: 0.20 (optimized for motorcycle detection)</li>
                <li>IOU: 0.40 (handles overlapping vehicles in Indian traffic)</li>
                <li>Emergency threshold: 50% (balanced sensitivity)</li>
                <li>Frame skip: 2 (balance between speed and accuracy)</li>
              </ul>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );

  const renderSystemSettings = () => (
    <Card className="bg-gradient-to-br from-slate-800 to-slate-900 border-slate-700">
      <CardHeader>
        <CardTitle className="text-slate-100">System Settings</CardTitle>
        <p className="text-sm text-slate-400">Configure system-wide preferences and behavior</p>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Auto Refresh Interval */}
        <div className="p-4 bg-slate-900/50 rounded-xl border border-slate-700">
          <div className="flex items-center justify-between mb-3">
            <label className="text-sm font-medium text-slate-300">Auto-refresh Interval (seconds)</label>
            <span className="text-sm font-semibold text-blue-400 bg-blue-500/20 px-3 py-1 rounded-lg">
              {(systemSettings.auto_refresh_interval / 1000).toFixed(0)}s
            </span>
          </div>
          <input
            type="range"
            min="1000"
            max="30000"
            step="1000"
            value={systemSettings.auto_refresh_interval}
            onChange={(e) => setSystemSettings({ ...systemSettings, auto_refresh_interval: parseInt(e.target.value) })}
            className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-blue-500"
          />
          <p className="text-xs text-slate-500 mt-2">
            How often to refresh data on dashboard and monitoring pages
          </p>
        </div>

        {/* Max Video Size */}
        <div className="p-4 bg-slate-900/50 rounded-xl border border-slate-700">
          <div className="flex items-center justify-between mb-3">
            <label className="text-sm font-medium text-slate-300">Max Video Upload Size (MB)</label>
            <span className="text-sm font-semibold text-green-400 bg-green-500/20 px-3 py-1 rounded-lg">
              {systemSettings.max_video_size_mb} MB
            </span>
          </div>
          <input
            type="range"
            min="100"
            max="2000"
            step="100"
            value={systemSettings.max_video_size_mb}
            onChange={(e) => setSystemSettings({ ...systemSettings, max_video_size_mb: parseInt(e.target.value) })}
            className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-green-500"
          />
          <p className="text-xs text-slate-500 mt-2">
            Maximum allowed file size for video uploads
          </p>
        </div>

        {/* Enable Notifications */}
        <div className="flex items-center justify-between p-4 bg-slate-900/50 rounded-xl border border-slate-700">
          <div>
            <label className="text-sm font-medium text-slate-300">Enable Notifications</label>
            <p className="text-xs text-slate-500 mt-1">
              Receive alerts for emergency vehicles and system events
            </p>
          </div>
          <label className="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={systemSettings.enable_notifications}
              onChange={(e) => setSystemSettings({ ...systemSettings, enable_notifications: e.target.checked })}
              className="sr-only peer"
            />
            <div className="w-11 h-6 bg-slate-700 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-500/30 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-slate-300 after:border-slate-700 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
          </label>
        </div>

        {/* Dark Mode */}
        <div className="flex items-center justify-between p-4 bg-slate-900/50 rounded-xl border border-green-500/30">
          <div>
            <label className="text-sm font-medium text-green-400">Dark Mode</label>
            <p className="text-xs text-green-500/70 mt-1">
              Currently enabled (looks great!)
            </p>
          </div>
          <label className="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={systemSettings.dark_mode}
              onChange={(e) => setSystemSettings({ ...systemSettings, dark_mode: e.target.checked })}
              className="sr-only peer"
            />
            <div className="w-11 h-6 bg-slate-700 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-green-500/30 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-slate-300 after:border-slate-700 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-green-600"></div>
          </label>
        </div>

        {/* Language */}
        <div className="p-4 bg-slate-900/50 rounded-xl border border-slate-700">
          <label className="block text-sm font-medium text-slate-300 mb-3">Language</label>
          <select
            value={systemSettings.language}
            onChange={(e) => setSystemSettings({ ...systemSettings, language: e.target.value })}
            className="w-full px-4 py-3 bg-slate-800 border border-slate-700 text-slate-100 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="en">English</option>
            <option value="hi">हिन्दी (Hindi)</option>
            <option value="mr">मराठी (Marathi)</option>
            <option value="ta">தமிழ் (Tamil)</option>
            <option value="te">తెలుగు (Telugu)</option>
          </select>
          <p className="text-xs text-slate-500 mt-2">
            Select your preferred interface language
          </p>
        </div>
      </CardContent>
    </Card>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-3 bg-blue-500/20 rounded-xl">
              <SettingsIcon className="h-8 w-8 text-blue-400" />
            </div>
            <h1 className="text-3xl font-bold text-slate-100">Settings</h1>
          </div>
          <p className="text-slate-400">Configure system parameters and preferences</p>
        </div>

        {/* Status Message */}
        {statusMessage && (
          <div className={`mb-6 p-4 rounded-xl border flex items-center gap-3 ${
            saveStatus === 'success' ? 'bg-green-500/10 border-green-500/30 text-green-400' :
            saveStatus === 'error' ? 'bg-red-500/10 border-red-500/30 text-red-400' :
            'bg-blue-500/10 border-blue-500/30 text-blue-400'
          }`}>
            {saveStatus === 'success' && <CheckCircle className="h-5 w-5" />}
            {saveStatus === 'error' && <AlertCircle className="h-5 w-5" />}
            {saveStatus === 'saving' && <RefreshCw className="h-5 w-5 animate-spin" />}
            <span className="font-medium">{statusMessage}</span>
          </div>
        )}

        {/* Tabs */}
        <Card className="mb-6 bg-gradient-to-br from-slate-800 to-slate-900 border-slate-700">
          <CardContent className="p-2">
            <div className="flex gap-2">
              <button
                onClick={() => setActiveTab('signals')}
                className={`flex items-center gap-2 px-4 py-3 rounded-xl font-medium transition-all ${
                  activeTab === 'signals'
                    ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                }`}
              >
                <Clock className="h-4 w-4" />
                Signal Timing
              </button>
              <button
                onClick={() => setActiveTab('locations')}
                className={`flex items-center gap-2 px-4 py-3 rounded-xl font-medium transition-all ${
                  activeTab === 'locations'
                    ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                }`}
              >
                <MapPin className="h-4 w-4" />
                Locations
              </button>
              <button
                onClick={() => setActiveTab('detection')}
                className={`flex items-center gap-2 px-4 py-3 rounded-xl font-medium transition-all ${
                  activeTab === 'detection'
                    ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                }`}
              >
                <ScanSearch className="h-4 w-4" />
                Detection
              </button>
              <button
                onClick={() => setActiveTab('system')}
                className={`flex items-center gap-2 px-4 py-3 rounded-xl font-medium transition-all ${
                  activeTab === 'system'
                    ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                }`}
              >
                <Sliders className="h-4 w-4" />
                System
              </button>
            </div>
          </CardContent>
        </Card>

        {/* Tab Content */}
        {loading ? (
          <Card className="bg-gradient-to-br from-slate-800 to-slate-900 border-slate-700">
            <CardContent>
              <div className="flex items-center justify-center py-12">
                <RefreshCw className="h-8 w-8 text-blue-400 animate-spin" />
              </div>
            </CardContent>
          </Card>
        ) : (
          <>
            {activeTab === 'signals' && renderSignalTimings()}
            {activeTab === 'locations' && renderLocations()}
            {activeTab === 'detection' && renderDetectionConfig()}
            {activeTab === 'system' && renderSystemSettings()}
          </>
        )}

        {/* Action Buttons */}
        <Card className="mt-8 bg-gradient-to-br from-slate-800 to-slate-900 border-slate-700">
          <CardContent>
            <div className="flex items-center justify-between">
              <button
                onClick={resetToDefaults}
                disabled={activeTab === 'signals' || activeTab === 'locations'}
                className="flex items-center gap-2 px-4 py-2.5 text-slate-300 bg-slate-800/50 rounded-xl hover:bg-slate-800 border border-slate-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <RefreshCw className="h-4 w-4" />
                Reset to Defaults
              </button>
              <button
                onClick={saveSettings}
                disabled={saveStatus === 'saving'}
                className="flex items-center gap-2 px-6 py-2.5 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-xl hover:from-blue-700 hover:to-blue-800 transition-all shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {saveStatus === 'saving' ? (
                  <>
                    <RefreshCw className="h-4 w-4 animate-spin" />
                    Saving...
                  </>
                ) : (
                  <>
                    <Save className="h-4 w-4" />
                    Save Changes
                  </>
                )}
              </button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Settings;

