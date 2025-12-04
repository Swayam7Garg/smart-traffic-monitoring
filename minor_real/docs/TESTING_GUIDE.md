# Iteration 2 - Quick Start & Testing Guide

## 🚀 Quick Start

### 1. Start the Backend Server

```powershell
cd C:\Users\swaya\OneDrive\Desktop\minor\minor_real\backend
.\venv\Scripts\activate
uvicorn app.main:app --reload
```

Server will start at: `http://localhost:8000`

### 2. Test API Health

```powershell
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "ml_components": {
    "detector": true,
    "analyzer": true,
    "signal_controller": true,
    "video_processor": true,
    "emergency_system": true
  }
}
```

---

## 🧪 Testing Iteration 2 Features

### Test 1: Video Upload & Processing

#### Using PowerShell (curl)
```powershell
# Upload a video file
$videoPath = "C:\path\to\your\traffic_video.mp4"

curl -X POST "http://localhost:8000/api/traffic/upload-video?location_id=junction_01" `
  -F "file=@$videoPath" `
  -H "accept: application/json"
```

Response:
```json
{
  "job_id": "abc123",
  "status": "processing",
  "message": "Video uploaded successfully"
}
```

#### Check Processing Status
```powershell
curl http://localhost:8000/api/traffic/processing-status/abc123
```

Response:
```json
{
  "job_id": "abc123",
  "status": "completed",
  "started_at": "2025-01-15T10:30:00",
  "completed_at": "2025-01-15T10:32:30",
  "results": {
    "total_frames": 3000,
    "detections": 250,
    "emergency_vehicles": 2,
    "output_video": "./outputs/processed_abc123.mp4"
  }
}
```

---

### Test 2: Real-time Frame Detection

#### Using Python Script
```python
# test_realtime_detection.py
import requests
import cv2
import base64

# Read a frame from video
cap = cv2.VideoCapture("traffic_video.mp4")
ret, frame = cap.read()

# Encode frame to base64
_, buffer = cv2.imencode('.jpg', frame)
frame_base64 = base64.b64encode(buffer).decode()

# Send to API
response = requests.post(
    "http://localhost:8000/api/traffic/process-realtime",
    json={
        "location_id": "junction_01",
        "frame_data": frame_base64,
        "trigger_emergency": True
    }
)

print(response.json())
```

Expected Response:
```json
{
  "detections": [
    {
      "class_name": "car",
      "confidence": 0.92,
      "bbox": [100, 150, 300, 400],
      "is_emergency": false
    }
  ],
  "analysis": {
    "vehicle_count": 15,
    "congestion_level": 45.5,
    "vehicle_types": {"car": 10, "bike": 3, "auto-rickshaw": 2}
  },
  "emergency_override": null
}
```

---

### Test 3: Detection History

#### Get Location History
```powershell
curl "http://localhost:8000/api/traffic/detection-history/junction_01?hours=24&vehicle_type=car"
```

#### Get Statistics
```powershell
curl "http://localhost:8000/api/traffic/detection-statistics/junction_01?hours=24"
```

Expected Response:
```json
{
  "location_id": "junction_01",
  "time_range_hours": 24,
  "vehicle_types": {
    "car": 1200,
    "bike": 450,
    "auto-rickshaw": 150,
    "bus": 80,
    "truck": 50
  },
  "total_vehicles": 1930,
  "emergency_vehicles": 8
}
```

---

### Test 4: Emergency Vehicle Detection

#### Simulate Emergency Detection
```python
# test_emergency.py
import requests
import cv2
import numpy as np
import base64

# Create a frame with a red vehicle (simulated ambulance)
frame = np.zeros((720, 1280, 3), dtype=np.uint8)
# Draw a red rectangle (ambulance)
cv2.rectangle(frame, (400, 300), (600, 500), (0, 0, 255), -1)

# Encode frame
_, buffer = cv2.imencode('.jpg', frame)
frame_base64 = base64.b64encode(buffer).decode()

# Send to API
response = requests.post(
    "http://localhost:8000/api/traffic/process-realtime",
    json={
        "location_id": "junction_01",
        "frame_data": frame_base64,
        "trigger_emergency": True
    }
)

result = response.json()
if result.get("emergency_override"):
    print("✓ Emergency detected! Signal override activated")
    print(f"Override ID: {result['emergency_override']['override_id']}")
else:
    print("No emergency detected")
```

---

### Test 5: Emergency Override Management

#### List Active Overrides
```powershell
curl http://localhost:8000/api/traffic/emergency/active
```

Response:
```json
{
  "active_count": 2,
  "overrides": [
    {
      "override_id": "override_xyz",
      "location_id": "junction_01",
      "emergency_type": "ambulance",
      "emergency_lane": "lane_2",
      "created_at": "2025-01-15T10:30:00",
      "expires_at": "2025-01-15T10:31:00",
      "remaining_seconds": 45
    }
  ]
}
```

#### Clear Override Manually
```powershell
curl -X POST http://localhost:8000/api/traffic/emergency/clear/override_xyz
```

#### Cleanup Expired Overrides
```powershell
curl -X POST http://localhost:8000/api/traffic/emergency/check-expired
```

---

### Test 6: Emergency History

```powershell
curl "http://localhost:8000/api/traffic/emergency-history?location_id=junction_01&hours=24"
```

Response:
```json
{
  "total": 8,
  "emergencies": [
    {
      "location_id": "junction_01",
      "timestamp": "2025-01-15T10:30:00",
      "vehicle_type": "car",
      "is_emergency": true,
      "confidence": 0.88
    }
  ]
}
```

---

## 🎥 Sample Video Testing

### Download Sample Traffic Videos
```powershell
# Use YouTube-DL or download from free video sites
# Example: Pexels, Pixabay

# Download from Pexels (free)
# Visit: https://www.pexels.com/search/videos/traffic/
# Download: Traffic intersection video (MP4)
```

### Recommended Test Videos
1. **Traffic Junction**: 30-60 seconds, multiple vehicles
2. **Highway Traffic**: Cars, trucks, bikes
3. **Emergency Vehicle**: Ambulance/police car (red/blue)

### Process Test Video
```powershell
# Upload video
curl -X POST "http://localhost:8000/api/traffic/upload-video?location_id=test_junction" `
  -F "file=@C:\Videos\traffic_test.mp4"

# Wait 30-60 seconds for processing...

# Check results
curl http://localhost:8000/api/traffic/processing-status/{job_id}

# View processed video
# Location: C:\Users\swaya\OneDrive\Desktop\minor\minor_real\data\outputs\processed_{job_id}.mp4
```

---

## 📊 Verify Database Storage

### Using MongoDB Compass or CLI

```javascript
// Connect to MongoDB
mongodb://localhost:27017/traffic_management

// Check collections
db.vehicle_detections.countDocuments()
db.video_processing_jobs.countDocuments()

// View recent detections
db.vehicle_detections.find().sort({timestamp: -1}).limit(10)

// View emergency events
db.vehicle_detections.find({is_emergency: true})

// View processing jobs
db.video_processing_jobs.find()
```

---

## ✅ Testing Checklist

### Core Functionality
- [ ] Backend server starts without errors
- [ ] All ML components initialized (check logs)
- [ ] Health endpoint returns all systems healthy
- [ ] MongoDB connection successful

### Video Processing
- [ ] Video upload accepts MP4 files
- [ ] Processing job creates job_id
- [ ] Status endpoint tracks progress
- [ ] Processed video saved to outputs folder
- [ ] Detections stored in database

### Detection Accuracy
- [ ] Cars detected correctly
- [ ] Bikes detected correctly
- [ ] Auto-rickshaws classified (large motorcycles)
- [ ] Trucks and buses detected
- [ ] Detection confidence >0.5

### Emergency Detection
- [ ] Red vehicles flagged as emergency
- [ ] Blue vehicles flagged as emergency
- [ ] Signal override triggered automatically
- [ ] Override expires after 60 seconds
- [ ] Manual clear works correctly

### Database Operations
- [ ] Detections stored every 10 frames
- [ ] Job results stored after processing
- [ ] History queries return data
- [ ] Statistics calculations accurate
- [ ] Emergency history tracked

---

## 🐛 Troubleshooting

### Issue: Video processing hangs
**Solution**: Check video format (MP4), reduce frame skip, check logs

### Issue: No detections found
**Solution**: Verify YOLOv8 model downloaded, check video quality, adjust confidence threshold

### Issue: Emergency not detected
**Solution**: Check vehicle color (must be solid red/blue), adjust HSV thresholds in detector.py

### Issue: Database errors
**Solution**: Verify MongoDB running, check connection string, ensure collections created

### Issue: Out of memory
**Solution**: Reduce frame skip, process smaller videos, increase system RAM

---

## 📝 Expected Log Output

```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     ✓ Vehicle Detector initialized
INFO:     ✓ Traffic Analyzer initialized  
INFO:     ✓ Signal Controller initialized
INFO:     ✓ Video Processor initialized
INFO:     ✓ Emergency Priority System initialized
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

---

## 🎯 Success Criteria

Iteration 2 is successful when:
1. ✅ All ML components initialize without errors
2. ✅ Video processing completes with detections
3. ✅ Emergency vehicles detected and logged
4. ✅ Signal override triggers automatically
5. ✅ Database stores all detections
6. ✅ API endpoints return valid responses
7. ✅ No Python/MongoDB errors in logs

---

**Ready for testing! 🚀**
