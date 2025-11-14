# Installation and Setup Guide

## Quick Installation (Windows PowerShell)

### Step 1: Install Dependencies

```powershell
# Navigate to project directory
cd c:\Users\swaya\OneDrive\Desktop\minor

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate

# Install all dependencies
pip install -r requirements.txt
```

### Step 2: Run Quick Start

```powershell
# Test with webcam
python quick_start.py
```

### Step 3: Run Main Application

```powershell
# With webcam
python main.py

# With video file
python main.py --source data/input_videos/traffic.mp4

# With IP camera
python main.py --source "rtsp://camera_ip:port/stream"

# Save output video
python main.py --save-output
```

## Troubleshooting

### Error: "Import could not be resolved"
This is just a linting warning. The packages will work once installed with pip.

### Error: "Cannot open video source"
- Check if webcam is connected
- Try different camera index: `python main.py --source 1`
- Test with video file instead

### Error: "Model not found"
YOLOv8 will automatically download the model on first run.

### Slow Performance
- Use smaller model: Change 'yolov8n.pt' to 'yolov8n.pt' in config.yaml (already default)
- Reduce frame resolution
- Enable GPU if available (change 'device: cpu' to 'device: cuda' in config.yaml)

## What You Need

### For Testing Without Video Files
✅ **Webcam** - Built-in or USB webcam (most computers have one)

### For Testing With Video Files
📹 **Traffic videos** - Download or record traffic intersection videos

**Where to get videos:**
1. **YouTube**: Search "traffic intersection" and download using yt-dlp
2. **Your phone**: Record traffic at nearby intersection
3. **Stock footage**: Pexels.com, Pixabay.com (search: traffic)

### Example Download (using yt-dlp):
```powershell
# Install yt-dlp
pip install yt-dlp

# Download a traffic video
yt-dlp "https://www.youtube.com/watch?v=YOUR_VIDEO_ID" -o data/input_videos/traffic.mp4
```

## System Requirements

- **OS**: Windows 10/11, Linux, or macOS
- **Python**: 3.8 or higher
- **RAM**: Minimum 4GB (8GB recommended)
- **GPU**: Optional (CPU works fine for testing)
- **Camera**: Webcam or IP camera (optional, can use video files)

## Project Files Created

```
minor/
├── main.py                    # Main application ✓
├── quick_start.py             # Quick test script ✓
├── requirements.txt           # Dependencies ✓
├── README.md                  # Documentation ✓
├── config/
│   └── config.yaml           # Configuration ✓
├── src/
│   ├── vehicle_detector.py   # YOLO detection ✓
│   ├── traffic_analyzer.py   # Traffic analysis ✓
│   ├── signal_controller.py  # Signal control ✓
│   └── utils/
│       ├── config_manager.py # Config utilities ✓
│       └── logger.py         # Logging ✓
├── data/
│   ├── input_videos/         # Put test videos here
│   └── output/               # Results saved here
└── tests/
    └── test_detector.py      # Unit tests ✓
```

## Next Steps

1. **Install dependencies**: `pip install -r requirements.txt`
2. **Test with webcam**: `python quick_start.py`
3. **Add test videos** to `data/input_videos/`
4. **Run with video**: `python main.py --source data/input_videos/your_video.mp4`
5. **Customize config**: Edit `config/config.yaml` for your needs

## Features Working

✅ Real-time vehicle detection (YOLOv8)
✅ Multi-lane traffic analysis
✅ Adaptive signal timing
✅ Emergency vehicle priority
✅ Live visualization dashboard
✅ Statistics and logging
✅ Video recording
✅ Configurable parameters

## Need Help?

Check the main README.md for detailed documentation and usage examples.
