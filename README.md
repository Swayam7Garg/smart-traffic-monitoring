# 🚦 Smart Traffic Light Monitoring System

An intelligent traffic management system using Computer Vision and AI to optimize traffic flow at intersections.

## 🎯 Project Overview

This system uses YOLOv8-based vehicle detection to analyze real-time traffic density and adaptively control traffic signal timing to reduce congestion and improve traffic flow efficiency.

**🌟 Features Web Dashboard, Real-time Analytics, Emergency Vehicle Detection, and Adaptive Signal Control!**

## ✨ Key Features

### Core Features
- **Real-time Vehicle Detection**: Uses YOLOv8 for accurate vehicle counting
- **Multi-lane Support**: Monitors multiple lanes simultaneously
- **Adaptive Signal Timing**: Dynamically adjusts green light duration based on traffic density
- **Live Dashboard**: Visual monitoring interface with statistics
- **Emergency Vehicle Priority**: Special handling for emergency vehicles
- **Data Logging**: Complete traffic analytics and reporting
- **Multi-source Support**: Works with webcam, IP cameras, or video files

### 🌟 **UNIQUE ADVANCED FEATURES** 🌟
- **🌐 Web Dashboard**: Access monitoring from any device via browser (http://localhost:5000)
- **📧 Email Alert System**: Automated alerts for congestion, emergency vehicles, and errors
- **📊 Report Generator**: Comprehensive PDF/Excel reports with beautiful visualizations
- **🚀 Integrated System**: All features working seamlessly together

> **Note**: These advanced features make this project stand out! See [UNIQUE_FEATURES.md](UNIQUE_FEATURES.md) for details.

## 🏗️ System Architecture

```
┌─────────────────┐
│  Video Input    │ (Camera/Video File)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Vehicle Detector│ (YOLOv8)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│Traffic Analyzer │ (Density Calculation)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│Signal Controller│ (Adaptive Timing)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Dashboard     │ (Real-time Display)
└─────────────────┘
```

## 📋 Requirements

### Hardware
- Webcam or IP Camera (minimum 720p recommended)
- Computer with at least 4GB RAM
- GPU (optional, for better performance)

### Software
- Python 3.8+
- OpenCV
- YOLOv8 (Ultralytics)
- NumPy, Pandas

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/smart-traffic-monitoring.git
cd smart-traffic-monitoring
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

The YOLOv8 model will download automatically on first run.

### 3. Run the System

**Option A: Web Dashboard (Recommended)**
```bash
python web_dashboard.py
```
Then open browser: **http://localhost:5000**

**Option B: Command Line with Video**
```bash
python main.py --source "data/input_videos/traffic_video_modified.mp4"
```

**Option C: Webcam**
```bash
python main.py --source 0
```

That's it! 🎉

## 📁 Project Structure

```
minor/
├── src/
│   ├── vehicle_detector.py      # YOLOv8 vehicle detection
│   ├── traffic_analyzer.py       # Traffic density analysis
│   ├── signal_controller.py      # Signal timing logic
│   ├── utils/
│   │   ├── config_manager.py     # Configuration handling
│   │   └── logger.py             # Logging utilities
│   └── __init__.py
├── config/
│   └── config.yaml               # System configuration
├── models/
│   └── yolov8n.pt               # YOLOv8 model (auto-downloaded)
├── data/
│   ├── input_videos/            # Test videos
│   └── output/                  # Results and logs
├── tests/
│   └── test_detector.py         # Unit tests
├── main.py                      # Main application
├── requirements.txt             # Dependencies
├── README.md                    # This file
└── Synopsis minor.pdf           # Project synopsis
```

## 🎮 Usage

### Method 1: Web Dashboard (Recommended) 🌐

**Step 1:** Update video source in `config/config.yaml`:
```yaml
video:
  source: "data/input_videos/traffic_video_modified.mp4"  # Your video path
```

**Step 2:** Start dashboard:
```bash
python web_dashboard.py
```

**Step 3:** Open browser:
```
http://localhost:5000
```

**Features:**
- ✅ Live video feed with vehicle detection
- ✅ Real-time statistics per lane
- ✅ Traffic signal status
- ✅ Emergency vehicle alerts
- ✅ Start/Stop controls

---

### Method 2: Command Line 💻

**With Video File:**
```bash
python main.py --source "data/input_videos/traffic_video_modified.mp4"
```

**With Webcam:**
```bash
python main.py --source 0
```

**With IP Camera:**
```bash
python main.py --source "rtsp://username:password@camera_ip:554/stream"
```

**Save Output:**
```bash
python main.py --source "data/input_videos/traffic_video_modified.mp4" --save-output
```

**Controls:**
- Press `q` to quit
- Press `s` to save screenshot
- Press `p` to pause/resume

---

### Method 3: Advanced Features (Reports + Alerts) 📊

```bash
python main_advanced.py --source "data/input_videos/traffic_video_modified.mp4"
```

This includes:
- Email alerts for congestion
- PDF/Excel report generation
- Advanced analytics

## ⚙️ Configuration

Edit `config/config.yaml` to customize:

```yaml
# Video Input
video:
  source: "data/input_videos/traffic_video_modified.mp4"  # or 0 for webcam
  
# Detection Settings
detection:
  model: "yolov8n.pt"
  confidence_threshold: 0.5
  
# Signal Control
signal:
  min_green_time: 10
  max_green_time: 60
  adaptive_mode: true
```

**Key Settings:**
- **video.source**: Path to video file, 0 for webcam, or RTSP URL
- **detection.confidence_threshold**: 0.3-0.7 (lower = more detections)
- **signal.adaptive_mode**: true/false (dynamic timing)
- **lanes.count**: Number of lanes to monitor (2-8)

## 📊 How It Works

1. **Vehicle Detection**:
   - Captures video frames from camera
   - YOLOv8 detects and classifies vehicles (car, truck, bus, motorcycle)
   - Tracks vehicle count per lane

2. **Traffic Analysis**:
   - Calculates traffic density (vehicles per lane)
   - Identifies congestion patterns
   - Detects emergency vehicles

3. **Signal Control**:
   - Determines optimal green light duration
   - Adapts timing based on real-time density
   - Implements priority for emergency vehicles
   - Ensures minimum and maximum timing limits

4. **Visualization**:
   - Live video feed with bounding boxes
   - Real-time statistics dashboard
   - Traffic density heatmap
   - Signal timing display

## 📈 Performance Metrics

The system tracks:
- Total vehicles detected per lane
- Average wait time reduction
- Traffic density over time
- Signal cycle efficiency
- Emergency vehicle response time

## 🎥 Input Video Requirements

For testing with video files:
- **Format**: MP4, AVI, MOV
- **Resolution**: Minimum 720p (1080p recommended)
- **Content**: Clear view of intersection with multiple lanes
- **Duration**: Any length (system processes in real-time)

**Sample video sources**:
- Record your own intersection footage
- Use YouTube traffic videos (download with appropriate tools)
- Use provided sample videos in `data/input_videos/`

## 🔧 Troubleshooting

### Video Issues

**Problem:** Video not loading in dashboard
```yaml
# Solution: Check config.yaml has correct path
video:
  source: "data/input_videos/traffic_video_modified.mp4"
```

**Problem:** "Video file not found"
```bash
# Solution: Check if file exists
dir data\input_videos\*.mp4

# Place your video in this folder
```

**Problem:** Webcam opening instead of video
```yaml
# Solution: Make sure config.yaml doesn't have source: 0
video:
  source: "data/input_videos/your_video.mp4"  # NOT 0
```

### Performance Issues

**Problem:** Slow FPS
```yaml
# Solution 1: Reduce resolution
video:
  resize_factor: 0.5  # Process at half size

# Solution 2: Use smaller model
detection:
  model: "yolov8n.pt"  # Fastest model
```

**Problem:** High CPU usage
```bash
# Solution: Skip frames
python main.py --source "video.mp4" --skip-frames 2
```

### Dashboard Issues

**Problem:** Port 5000 already in use
```powershell
# Solution: Kill existing process
netstat -ano | findstr :5000
taskkill /PID <process_id> /F
```

**Problem:** Dashboard not accessible
```bash
# Solution: Check firewall, or use localhost
http://localhost:5000
http://127.0.0.1:5000
```

## 📝 Future Enhancements

- [ ] Multi-intersection coordination
- [ ] Machine learning for traffic prediction
- [ ] Cloud-based monitoring dashboard
- [ ] Mobile app for traffic alerts
- [ ] Integration with existing traffic systems

## 📂 Project Structure

```
smart-traffic-monitoring/
├── config/
│   └── config.yaml              # Main configuration file
├── data/
│   ├── input_videos/           # Place your videos here
│   │   └── traffic_video_modified.mp4
│   └── output/                 # Results and logs
├── src/
│   ├── vehicle_detector.py     # YOLOv8 detection
│   ├── traffic_analyzer.py     # Traffic analysis
│   ├── signal_controller.py    # Signal control logic
│   ├── alert_system.py         # Email alerts
│   ├── report_generator.py     # PDF/Excel reports
│   └── utils/
│       ├── config_manager.py
│       └── logger.py
├── templates/
│   └── index.html              # Dashboard HTML
├── main.py                     # Main CLI application
├── main_advanced.py            # With reports & alerts
├── web_dashboard.py            # Web dashboard server
├── test_video.py               # Quick test script
├── launch_dashboard.py         # Auto launcher
├── requirements.txt            # Dependencies
├── yolov8n.pt                  # YOLO model (auto-downloads)
├── README.md                   # This file
└── PROJECT_REPORT.md           # Detailed documentation
```

## 🎓 Academic Documentation

For detailed academic documentation, see:
- **[PROJECT_REPORT.md](PROJECT_REPORT.md)** - Comprehensive 30,000+ word report
- **[INSTALL.md](INSTALL.md)** - Detailed installation guide
- **[HOW_TO_RUN_WITH_VIDEO.md](HOW_TO_RUN_WITH_VIDEO.md)** - Video processing guide

## 🚀 GitHub Push Instructions

```bash
# 1. Initialize git (if not already)
git init

# 2. Add all files
git add .

# 3. Commit
git commit -m "Initial commit: Smart Traffic Monitoring System"

# 4. Create new repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/smart-traffic-monitoring.git

# 5. Push
git branch -M main
git push -u origin main
```

## 👥 Author

Your Name - [GitHub Profile](https://github.com/YOUR_USERNAME)

## 📄 License

MIT License - Feel free to use for academic or personal projects

## 🤝 Contributing

Contributions welcome! Please open an issue or submit a pull request.

## ⭐ Show Your Support

If this project helped you, please give it a ⭐ on GitHub!

---

**Note**: This is an academic project for demonstration purposes. For production deployment, consider additional safety measures and compliance with local traffic regulations.
