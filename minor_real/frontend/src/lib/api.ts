import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Traffic API
export const trafficAPI = {
  getCurrentTraffic: async (locationId?: string) => {
    const params = locationId ? { location_id: locationId } : {};
    const response = await api.get('/traffic/current', { params });
    return response.data;
  },

  getDetectionHistory: async (locationId: string, hours: number = 24) => {
    const response = await api.get(`/traffic/detection-history/${locationId}`, {
      params: { hours },
    });
    return response.data;
  },

  getDetectionStatistics: async (locationId: string, hours: number = 24) => {
    const response = await api.get(`/traffic/detection-statistics/${locationId}`, {
      params: { hours },
    });
    return response.data;
  },

  getEmergencyHistory: async (locationId?: string, hours: number = 24) => {
    const params = { hours, ...(locationId && { location_id: locationId }) };
    const response = await api.get('/traffic/emergency-history', { params });
    return response.data;
  },

  uploadVideo: async (formData: FormData, locationId: string = 'junction_01') => {
    const response = await api.post('/traffic/upload-video', formData, {
      params: { location_id: locationId },
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  getJobStatus: async (jobId: string) => {
    const response = await api.get(`/traffic/processing-status/${jobId}`);
    return response.data;
  },

  getRecentJobs: async (limit: number = 10) => {
    const response = await api.get('/traffic/recent-jobs', {
      params: { limit },
    });
    return response.data;
  },

  downloadProcessedVideo: (jobId: string) => {
    window.open(`${API_BASE_URL}/traffic/download-processed-video/${jobId}`, '_blank');
  },
};

// Emergency API
export const emergencyAPI = {
  getActiveOverrides: async () => {
    const response = await api.get('/traffic/emergency/active');
    return response.data;
  },

  clearOverride: async (overrideId: string) => {
    const response = await api.post(`/traffic/emergency/clear/${overrideId}`);
    return response.data;
  },

  checkExpired: async () => {
    const response = await api.post('/traffic/emergency/check-expired');
    return response.data;
  },
};

// Signals API
export const signalsAPI = {
  getAllSignals: async () => {
    const response = await api.get('/signals/');
    return response.data;
  },

  getSignalById: async (signalId: string) => {
    const response = await api.get(`/signals/${signalId}`);
    return response.data;
  },

  updateSignal: async (signalId: string, data: any) => {
    const response = await api.put(`/signals/${signalId}`, data);
    return response.data;
  },
};

// Analytics API
export const analyticsAPI = {
  getOverview: async (startDate?: string, endDate?: string) => {
    const params: any = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;
    const response = await api.get('/analytics/overview', { params });
    return response.data;
  },

  getDashboardStats: async (hours: number = 24) => {
    const response = await api.get('/analytics/dashboard', {
      params: { hours },
    });
    return response.data;
  },

  getTrafficTrends: async (locationId: string, days: number = 7) => {
    const response = await api.get(`/analytics/trends/${locationId}`, {
      params: { days },
    });
    return response.data;
  },

  getPeakHours: async (locationId: string) => {
    const response = await api.get(`/analytics/peak-hours/${locationId}`);
    return response.data;
  },

  generateReport: async (locationId?: string, startDate?: string, endDate?: string) => {
    const params: any = {};
    if (locationId) params.location_id = locationId;
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;
    const response = await api.get('/analytics/report', { params });
    return response.data;
  },

  exportCSV: async (startDate?: string, endDate?: string) => {
    const params: any = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;
    const response = await api.get('/analytics/export/csv', {
      params,
      responseType: 'blob',
    });
    
    // Create download link
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `traffic_analytics_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  },

  getLastVideo: async () => {
    const response = await api.get('/analytics/last-video');
    return response.data;
  },

  getAllLocations: async () => {
    const response = await api.get('/analytics/locations');
    return response.data;
  },

  getLocationAnalytics: async (locationId: string, startDate?: string, endDate?: string) => {
    const params: any = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;
    const response = await api.get(`/analytics/location/${locationId}`, { params });
    return response.data;
  },

  clearHistory: async (locationId?: string) => {
    const params: any = { confirm: true };
    if (locationId) params.location_id = locationId;
    const response = await api.delete('/analytics/clear-history', { params });
    return response.data;
  },
};

// Settings API
export const settingsAPI = {
  // Signal Timings
  getSignalTimings: async () => {
    const response = await api.get('/settings/signal-timings');
    return response.data;
  },

  updateSignalTimings: async (timings: any[]) => {
    const response = await api.put('/settings/signal-timings', timings);
    return response.data;
  },

  updateSignalTiming: async (
    locationId: string,
    vehicleType: string,
    timePeriod: string,
    update: { green_duration?: number; red_duration?: number }
  ) => {
    const response = await api.put(
      `/settings/signal-timings/${locationId}/${vehicleType}/${timePeriod}`,
      update
    );
    return response.data;
  },

  // Locations
  getLocations: async () => {
    const response = await api.get('/settings/locations');
    return response.data;
  },

  createLocation: async (location: {
    name: string;
    latitude: number;
    longitude: number;
    camera_id: string;
    status: 'active' | 'inactive';
  }) => {
    const response = await api.post('/settings/locations', location);
    return response.data;
  },

  updateLocation: async (locationId: string, update: any) => {
    const response = await api.put(`/settings/locations/${locationId}`, update);
    return response.data;
  },

  deleteLocation: async (locationId: string) => {
    const response = await api.delete(`/settings/locations/${locationId}`);
    return response.data;
  },

  // Detection Config
  getDetectionConfig: async () => {
    const response = await api.get('/settings/detection-config');
    return response.data;
  },

  updateDetectionConfig: async (config: {
    confidence_threshold?: number;
    iou_threshold?: number;
    emergency_color_threshold?: number;
    autorickshaw_size_threshold?: number;
    frame_skip?: number;
  }) => {
    const response = await api.put('/settings/detection-config', config);
    return response.data;
  },

  resetDetectionConfig: async () => {
    const response = await api.post('/settings/detection-config/reset');
    return response.data;
  },

  // System Settings
  getSystemSettings: async () => {
    const response = await api.get('/settings/system');
    return response.data;
  },

  updateSystemSettings: async (settings: {
    auto_refresh_interval?: number;
    max_video_size_mb?: number;
    enable_notifications?: boolean;
    dark_mode?: boolean;
    language?: string;
  }) => {
    const response = await api.put('/settings/system', settings);
    return response.data;
  },

  resetSystemSettings: async () => {
    const response = await api.post('/settings/system/reset');
    return response.data;
  },
};
