# Live Camera Feed Integration Guide

## Overview
Complete live camera streaming system for real-time traffic monitoring and analytics delivery to authorities.

## Architecture

### Backend Components

1. **Camera Model** (`backend/app/models/cameras.py`)
   - Camera configuration storage
   - Fields: camera_id, name, rtsp_url, location_id, status, is_streaming
   - Supports RTSP, HTTP streams, and video files

2. **Camera Router** (`backend/app/routers/cameras.py`)
   - CRUD operations for camera management
   - Stream control (start/stop)
   - Live detection data retrieval

3. **WebSocket Endpoint** (`backend/app/main.py`)
   - Real-time detection broadcasting: `ws://localhost:8000/ws/live-feed`
   - Auto-reconnection support
   - Ping/pong for connection health

4. **Video Processor** (`backend/app/ml/video_processor.py`)
   - Existing `process_stream()` method for live camera processing
   - Callback-based detection storage and broadcasting
   - ~30 FPS processing rate

### Frontend Components

1. **Camera Management Page** (`frontend/src/pages/CameraManagement.tsx`)
   - Add/edit/delete cameras
   - Start/stop streams
   - Camera status monitoring
   - RTSP URL configuration

2. **Live Monitoring Page** (Enhanced `frontend/src/pages/LiveMonitoring.tsx`)
   - WebSocket connection for real-time updates
   - Live feed display with vehicle counts
   - Emergency vehicle alerts
   - Congestion level monitoring

## API Endpoints

### Camera Management

#### Get All Cameras
```http
GET /api/v1/cameras/cameras
```

#### Get Specific Camera
```http
GET /api/v1/cameras/cameras/{camera_id}
```

#### Create Camera
```http
POST /api/v1/cameras/cameras
Content-Type: application/json

{
  "camera_id": "cam_001",
  "name": "Main Intersection - North",
  "rtsp_url": "rtsp://192.168.1.100:554/stream",
  "location_id": "loc_001",
  "location_name": "MG Road Junction",
  "direction": "North-South"
}
```

#### Update Camera
```http
PUT /api/v1/cameras/cameras/{camera_id}
Content-Type: application/json

{
  "name": "Updated Name",
  "status": "active"
}
```

#### Delete Camera
```http
DELETE /api/v1/cameras/cameras/{camera_id}
```
Note: Cannot delete camera while streaming

#### Start/Stop Stream
```http
POST /api/v1/cameras/cameras/{camera_id}/stream?action=start
POST /api/v1/cameras/cameras/{camera_id}/stream?action=stop
```

#### Get Live Data
```http
GET /api/v1/cameras/cameras/{camera_id}/live-data?limit=10
```

#### Get Active Streams
```http
GET /api/v1/cameras/streams/active
```

## WebSocket Protocol

### Connection
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/live-feed');
```

### Message Types

#### Connection Confirmation
```json
{
  "type": "connection",
  "status": "connected",
  "message": "Live feed connected"
}
```

#### Live Detection Data
```json
{
  "type": "live_detection",
  "camera_id": "cam_001",
  "timestamp": "2024-01-15T10:30:45",
  "data": {
    "camera_id": "cam_001",
    "stream_id": "stream_cam_001_1234567890",
    "location_id": "loc_001",
    "timestamp": "2024-01-15T10:30:45",
    "vehicle_counts": {
      "car": 15,
      "motorcycle": 8,
      "truck": 2,
      "bus": 1,
      "auto-rickshaw": 5,
      "bicycle": 3
    },
    "congestion_level": "moderate",
    "average_speed": 25.5,
    "emergency_vehicles": [],
    "total_detections": 34
  }
}
```

#### Keep-Alive Messages
```json
{
  "type": "ping"
}
```
```json
{
  "type": "pong",
  "received": "client_message"
}
```

## Database Collections

### cameras
```javascript
{
  "_id": ObjectId,
  "camera_id": "cam_001",
  "name": "Main Intersection - North",
  "rtsp_url": "rtsp://192.168.1.100:554/stream",
  "location_id": "loc_001",
  "location_name": "MG Road Junction",
  "direction": "North-South",
  "status": "active",
  "is_streaming": true,
  "stream_id": "stream_cam_001_1234567890",
  "created_at": ISODate,
  "updated_at": ISODate,
  "last_active": ISODate
}
```

### live_detections
```javascript
{
  "_id": ObjectId,
  "camera_id": "cam_001",
  "stream_id": "stream_cam_001_1234567890",
  "location_id": "loc_001",
  "timestamp": ISODate,
  "vehicle_counts": {
    "car": 15,
    "motorcycle": 8,
    "truck": 2,
    "bus": 1,
    "auto-rickshaw": 5,
    "bicycle": 3
  },
  "congestion_level": "moderate",
  "average_speed": 25.5,
  "emergency_vehicles": [
    {
      "vehicle_type": "ambulance",
      "confidence": 0.92,
      "bbox": [100, 200, 300, 400]
    }
  ],
  "total_detections": 34
}
```

## Usage Instructions

### 1. Add a Camera

Navigate to **Cameras** page in the frontend:

1. Click "Add Camera" button
2. Fill in camera details:
   - Camera ID: Unique identifier (e.g., `cam_001`)
   - Camera Name: Descriptive name (e.g., `Main Intersection - North`)
   - RTSP/HTTP URL: Camera stream URL or video file path
   - Location ID: Location identifier (e.g., `loc_001`)
   - Location Name: Human-readable location (e.g., `MG Road Junction`)
   - Direction: Optional traffic direction (e.g., `North-South`)
3. Click "Add Camera"

### 2. Start Live Stream

On the Camera Management page:

1. Find your camera in the grid
2. Click the green "Start" button
3. Camera status changes to "🔴 LIVE"
4. Stream processing begins immediately

### 3. Monitor Live Feed

Navigate to **Live Monitoring** page:

1. WebSocket automatically connects (green "Live feed connected" indicator)
2. Active camera feeds appear in the "Live Camera Feeds" section
3. Real-time vehicle counts update every frame (~30 FPS)
4. Emergency vehicles trigger immediate alerts
5. Congestion levels update continuously

### 4. Stop Stream

On the Camera Management page:

1. Find the active camera
2. Click the red "Stop" button
3. Stream processing stops
4. Camera status changes to "Offline"

## RTSP Camera Examples

### Common RTSP URL Formats

```
# Generic RTSP
rtsp://username:password@192.168.1.100:554/stream

# Hikvision
rtsp://admin:password@192.168.1.100:554/Streaming/Channels/101

# Dahua
rtsp://admin:password@192.168.1.100:554/cam/realmonitor?channel=1&subtype=0

# Axis
rtsp://admin:password@192.168.1.100:554/axis-media/media.amp

# Foscam
rtsp://admin:password@192.168.1.100:554/videoMain

# For testing with local video file
/path/to/video.mp4
```

## Testing with Sample Video

For testing without RTSP camera:

1. Add camera with video file path:
   ```
   RTSP URL: C:\Users\swaya\OneDrive\Desktop\minor\minor_real\data\videos\sample.mp4
   ```

2. Start stream - processor will read from file as if it's a live feed

3. Monitor Live Monitoring page for real-time updates

## System Capabilities

### Detection Features
- ✅ Cars, motorcycles, trucks, buses, bicycles, auto-rickshaws
- ✅ Emergency vehicle detection (ambulance, fire truck, police)
- ✅ Confidence threshold: 0.15 (optimized for Indian traffic)
- ✅ ByteTrack tracking for vehicle counting
- ✅ Smart counting with estimation for untracked vehicles

### Real-Time Features
- ✅ ~30 FPS processing rate
- ✅ WebSocket broadcasting to all connected clients
- ✅ MongoDB storage for historical analysis
- ✅ Emergency vehicle priority signaling
- ✅ Congestion level calculation
- ✅ Multi-camera support

### Frontend Features
- ✅ Live camera grid view
- ✅ Real-time vehicle counts
- ✅ Emergency alerts with visual indicators
- ✅ WebSocket auto-reconnection
- ✅ Camera status monitoring (online/offline)
- ✅ Start/stop stream controls

## Production Deployment

### Backend Requirements
1. CUDA-capable GPU (NVIDIA RTX 3050+ recommended)
2. Python 3.13.4+
3. MongoDB 3.3.2+
4. PyTorch 2.7.1+cu118
5. FastAPI 0.104.1+

### Network Requirements
1. RTSP camera access on local network
2. Port 8000 for API
3. WebSocket support
4. Low latency network (<100ms)

### Security Considerations
1. Add camera authentication (username/password)
2. Secure RTSP URLs in database (encrypt)
3. Add API key authentication for camera management
4. Implement rate limiting for stream control
5. Add user roles (admin, viewer)

### Performance Optimization
1. **Multi-Camera Scaling**:
   - Each stream runs in separate asyncio task
   - GPU shared across all streams
   - Batch processing for multiple frames

2. **Bandwidth Optimization**:
   - Adjust frame skip for slower connections
   - Lower resolution for distant cameras
   - Use H.264 compression for RTSP

3. **Storage Management**:
   - Auto-delete old live_detections (keep last 7 days)
   - Index timestamp field for fast queries
   - Archive critical events (emergencies)

## Monitoring & Maintenance

### Health Checks
```http
GET /health
# Response: {"status": "healthy"}

GET /api/v1/cameras/streams/active
# Response: List of active streams
```

### Error Handling
- **Stream Connection Failed**: Check RTSP URL and network
- **GPU Out of Memory**: Reduce concurrent streams or lower resolution
- **WebSocket Disconnected**: Auto-reconnect after 5 seconds
- **Detection Lag**: Check GPU utilization, reduce imgsz or confidence

### Logs
```bash
# Backend logs show:
INFO - Starting stream processing: stream_cam_001_1234567890
INFO - ✓ Motorcycle detected: area=575px, ratio=0.61
WARNING - 🚨 Emergency vehicle in stream cam_001
INFO - Stored and broadcasted live detection for cam_001
```

## Troubleshooting

### Camera Not Streaming
1. Verify RTSP URL is correct
2. Check camera is accessible on network
3. Test with VLC: `vlc rtsp://...`
4. Check backend logs for connection errors

### No Live Updates in Frontend
1. Check WebSocket connection (green indicator)
2. Open browser console for WebSocket errors
3. Verify backend is running and accessible
4. Check CORS settings in backend

### Poor Detection Accuracy
1. Adjust confidence threshold in Settings
2. Check camera angle and lighting
3. Ensure camera covers all lanes
4. Verify GPU is being used (check logs)

### High CPU/GPU Usage
1. Reduce number of concurrent streams
2. Lower imgsz (1280 → 640)
3. Increase frame skip (process every 2nd frame)
4. Check for memory leaks in long-running streams

## Future Enhancements

### Planned Features
- [ ] Multi-camera grid view with video frames
- [ ] Heat map overlay for congestion zones
- [ ] Traffic flow predictions using historical data
- [ ] Automatic incident detection (accidents, stalled vehicles)
- [ ] License plate recognition for violations
- [ ] Cloud recording and playback
- [ ] Mobile app for authorities
- [ ] SMS/email alerts for emergencies
- [ ] Integration with traffic signal controllers
- [ ] API for third-party integrations

## Support

For issues or questions:
1. Check logs in backend terminal
2. Review error messages in frontend console
3. Verify MongoDB connection
4. Test with sample video before RTSP cameras
5. Ensure GPU is accessible (nvidia-smi)

---

**System Status**: ✅ Operational
**Last Updated**: 2024-01-15
**Version**: 1.0.0
