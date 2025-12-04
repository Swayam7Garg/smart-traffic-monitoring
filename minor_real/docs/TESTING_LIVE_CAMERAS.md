# Quick Test Guide: Live Camera Integration

## Verify Installation

✅ All components created and installed:
- Backend camera model and router
- WebSocket endpoint
- Frontend Camera Management page
- Frontend Live Monitoring enhancements

## Testing Steps

### 1. Verify Backend Auto-Reload
Backend should have automatically reloaded with new endpoints. Check terminal for:
```
INFO:     Application startup complete.
```

If not showing, restart backend manually.

### 2. Access Camera Management Page

1. Open frontend: http://localhost:5173
2. Click **"Cameras"** in sidebar (new menu item)
3. You should see the Camera Management page

### 3. Add Test Camera with Video File

Click "Add Camera" and fill in:

```
Camera ID: cam_test_001
Camera Name: Test Camera - Sample Video
RTSP/HTTP URL: C:\Users\swaya\OneDrive\Desktop\minor\minor_real\data\videos\[YOUR_VIDEO_FILE].mp4
Location ID: loc_test_001
Location Name: Test Location
Direction: North-South
```

Click "Add Camera"

### 4. Start Stream

1. Camera card appears with status "Offline"
2. Click green "Start" button
3. Status changes to "🔴 LIVE"
4. Backend terminal shows:
   ```
   INFO - Starting stream processing: stream_cam_test_001_...
   INFO - ✓ Motorcycle detected: area=575px, ratio=0.61
   ```

### 5. Monitor Live Feed

1. Go to **Live Monitoring** page
2. Top banner shows "Live feed connected" (green WiFi icon)
3. "Live Camera Feeds" section appears with your camera
4. Real-time vehicle counts update continuously
5. Watch for emergency vehicle alerts if any detected

### 6. Stop Stream

1. Return to **Cameras** page
2. Click red "Stop" button on active camera
3. Status changes to "Offline"
4. Live feed disappears from Live Monitoring

## Expected Behavior

### Camera Management Page
- ✅ Add/edit/delete cameras
- ✅ Start/stop streams with single click
- ✅ Real-time status updates (LIVE/Offline)
- ✅ Last active timestamp
- ✅ Cannot delete camera while streaming

### Live Monitoring Page
- ✅ WebSocket auto-connect
- ✅ Multiple camera grid view
- ✅ Real-time vehicle counts per camera
- ✅ Emergency vehicle badges
- ✅ Congestion level display
- ✅ Auto-reconnect if disconnected

### Backend Processing
- ✅ ~30 FPS detection rate
- ✅ MongoDB storage of detections
- ✅ WebSocket broadcasting
- ✅ GPU-accelerated processing
- ✅ Emergency vehicle priority triggering

## Testing with RTSP Camera

If you have an RTSP camera:

```
RTSP URL format:
rtsp://username:password@IP_ADDRESS:554/stream

Example:
rtsp://admin:admin123@192.168.1.100:554/stream
```

1. Test RTSP URL first with VLC player
2. Add camera with RTSP URL
3. Start stream
4. Monitor live feed

## Troubleshooting

### Backend Not Loading Camera Routes
**Solution**: Restart backend manually
```powershell
cd C:\Users\swaya\OneDrive\Desktop\minor\minor_real\backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Camera Page Not Found
**Solution**: Rebuild frontend
```powershell
cd C:\Users\swaya\OneDrive\Desktop\minor\minor_real\frontend
npm run dev
```

### WebSocket Not Connecting
**Check**:
1. Backend running on port 8000
2. Browser console for errors
3. CORS settings in backend

### Stream Not Starting
**Check**:
1. Video file path is correct and absolute
2. File is readable (not in use)
3. Backend logs for specific error
4. GPU memory available

## API Test with curl

### Add Camera
```bash
curl -X POST http://localhost:8000/api/v1/cameras/cameras \
  -H "Content-Type: application/json" \
  -d '{
    "camera_id": "cam_001",
    "name": "Test Camera",
    "rtsp_url": "C:\\path\\to\\video.mp4",
    "location_id": "loc_001",
    "location_name": "Test Location"
  }'
```

### Start Stream
```bash
curl -X POST "http://localhost:8000/api/v1/cameras/cameras/cam_001/stream?action=start"
```

### Get Active Streams
```bash
curl http://localhost:8000/api/v1/cameras/streams/active
```

### Stop Stream
```bash
curl -X POST "http://localhost:8000/api/v1/cameras/cameras/cam_001/stream?action=stop"
```

## Success Criteria

✅ Camera Management page loads without errors
✅ Can add camera successfully
✅ Stream starts and shows LIVE status
✅ Live Monitoring page shows WebSocket connected
✅ Real-time vehicle counts update
✅ Backend logs show detections
✅ Can stop stream successfully
✅ MongoDB stores live_detections collection

## Next Steps After Testing

1. **Production RTSP Setup**: Add real traffic cameras
2. **Multi-Camera Testing**: Add 3-5 cameras simultaneously
3. **Performance Monitoring**: Check GPU usage with multiple streams
4. **Authority Dashboard**: Create dedicated view for traffic control center
5. **Alert System**: Add email/SMS notifications for emergencies

---

**Status**: Ready for Testing
**Date**: 2024-01-15
