# 🚦 Smart Traffic Management System - Complete Architecture Guide

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [Technology Stack](#technology-stack)
3. [Project Structure](#project-structure)
4. [Backend Architecture](#backend-architecture)
5. [Frontend Architecture](#frontend-architecture)
6. [Database Design](#database-design)
7. [How Technologies Work Together](#how-technologies-work-together)
8. [File-by-File Explanation](#file-by-file-explanation)
9. [Data Flow](#data-flow)
10. [Setup & Installation](#setup--installation)

---

## 🎯 Project Overview

**Smart Traffic Management System** is an AI-powered real-time traffic monitoring and control system that uses **YOLOv8** deep learning model for vehicle detection, adaptive traffic signal control, and emergency vehicle prioritization.

### Key Features
- 🚗 **Real-time Vehicle Detection** using YOLOv8
- 🚦 **Adaptive Traffic Signal Control** based on traffic density
- 🚑 **Emergency Vehicle Priority** (Ambulance, Police, Fire trucks)
- 📊 **Traffic Analytics Dashboard** with historical data
- 📹 **Multi-camera Support** for live monitoring
- 🎬 **Video Upload & Processing** for traffic analysis
- 💾 **MongoDB Database** for data persistence

---

## 🛠️ Technology Stack

### Backend Technologies

#### 1. **Python 3.10+** 
**Purpose**: Primary backend programming language  
**Why**: Rich ecosystem for AI/ML, excellent library support, async capabilities

#### 2. **FastAPI** (v0.104.1)
**Purpose**: Modern web framework for building REST APIs  
**What it does**:
- Creates HTTP endpoints (GET, POST, PUT, DELETE)
- Automatic OpenAPI documentation (Swagger UI)
- Async request handling for better performance
- WebSocket support for real-time updates
- CORS middleware for frontend integration

**Key Files**:
- `backend/app/main.py` - Application entry point
- `backend/app/routers/*.py` - API endpoints

#### 3. **Uvicorn** (v0.24.0)
**Purpose**: ASGI web server  
**What it does**: Runs the FastAPI application, handles HTTP requests

#### 4. **YOLOv8 (Ultralytics)** (v8.0.230)
**Purpose**: State-of-the-art object detection model  
**What it does**:
- Detects vehicles in video frames (30 FPS)
- Classifies 7 vehicle types: car, motorcycle, truck, bus, auto-rickshaw, bicycle, emergency vehicle
- 85%+ detection accuracy
- Real-time inference on GPU or CPU

**Key Files**:
- `backend/app/ml/detector.py` - Vehicle detection logic
- `data/models/yolov8n.pt` - Pre-trained model weights

#### 5. **OpenCV (cv2)** (v4.8.1.78)
**Purpose**: Computer vision library  
**What it does**:
- Reads video files and camera streams
- Extracts frames from videos
- Image preprocessing (resize, color conversion)
- Draws bounding boxes and annotations
- Handles RTSP streams from IP cameras

**Key Files**:
- `backend/app/ml/video_processor.py` - Video processing

#### 6. **PyTorch** (v2.2.0+)
**Purpose**: Deep learning framework  
**What it does**:
- Powers YOLOv8 model
- GPU acceleration (CUDA support)
- Tensor operations for neural networks

#### 7. **MongoDB with Motor** (pymongo v4.6.0, motor v3.3.2)
**Purpose**: NoSQL database and async driver  
**What it does**:
- Stores traffic data in JSON-like documents
- Fast reads/writes for real-time data
- Handles time-series traffic data efficiently
- Motor provides async database operations

**Key Files**:
- `backend/app/database.py` - Database connection
- Collections: `traffic_data`, `cameras`, `emergency_events`, `signal_timings`, `analytics`

#### 8. **NumPy** (v1.26.0+)
**Purpose**: Numerical computing library  
**What it does**: Array operations, mathematical functions for image processing

#### 9. **Pandas** (v2.1.0+)
**Purpose**: Data analysis library  
**What it does**: Processes traffic data, generates analytics, creates reports

#### 10. **ReportLab** (v4.0.7)
**Purpose**: PDF generation  
**What it does**: Creates PDF reports with traffic statistics and charts

---

### Frontend Technologies

#### 1. **React 19.2.0**
**Purpose**: UI library for building user interfaces  
**What it does**:
- Component-based architecture
- Virtual DOM for efficient rendering
- Hooks for state management (useState, useEffect)
- Creates interactive dashboard

**Key Files**:
- `frontend/src/App.tsx` - Main application component
- `frontend/src/pages/*.tsx` - Page components

#### 2. **TypeScript** (v5.9.3)
**Purpose**: Type-safe JavaScript  
**What it does**:
- Adds static typing to JavaScript
- Catches errors during development
- Better IDE autocomplete

#### 3. **Vite** (v7.2.2)
**Purpose**: Build tool and dev server  
**What it does**:
- Lightning-fast Hot Module Replacement (HMR)
- Optimized production builds
- Instant server startup

#### 4. **TailwindCSS** (v3.4.1)
**Purpose**: Utility-first CSS framework  
**What it does**:
- Rapid UI development with utility classes
- Responsive design out of the box
- Custom color schemes and animations

**Key Files**:
- `frontend/tailwind.config.js` - Tailwind configuration
- `frontend/src/index.css` - Global styles

#### 5. **Axios** (v1.13.2)
**Purpose**: HTTP client  
**What it does**:
- Makes API requests to backend
- Handles request/response interceptors
- Better error handling than fetch

**Key Files**:
- `frontend/src/lib/api.ts` - API configuration

#### 6. **React Query (TanStack Query)** (v5.90.10)
**Purpose**: Data fetching and state management  
**What it does**:
- Automatic caching of API responses
- Background data refetching
- Optimistic updates
- Loading/error states

#### 7. **Recharts** (v2.15.4)
**Purpose**: Charting library  
**What it does**:
- Creates line charts, bar charts, pie charts
- Interactive visualizations
- Traffic analytics graphs

**Key Files**:
- `frontend/src/components/charts/*.tsx` - Chart components

#### 8. **Lucide React** (v0.468.0)
**Purpose**: Icon library  
**What it does**: Provides beautiful icons (camera, signal, alert, etc.)

---

## 📁 Project Structure

```
minor_real/
├── backend/                    # Python FastAPI Backend
│   ├── app/
│   │   ├── __init__.py        # Package initializer
│   │   ├── main.py            # FastAPI app entry point
│   │   ├── config.py          # Configuration management
│   │   ├── database.py        # MongoDB connection
│   │   │
│   │   ├── models/            # Pydantic data models
│   │   │   ├── traffic.py     # Traffic data models
│   │   │   ├── cameras.py     # Camera models
│   │   │   ├── signals.py     # Signal control models
│   │   │   └── violations.py  # Violation models
│   │   │
│   │   ├── routers/           # API endpoints
│   │   │   ├── traffic.py     # Traffic endpoints
│   │   │   ├── cameras.py     # Camera management
│   │   │   ├── analytics.py   # Analytics endpoints
│   │   │   ├── signals.py     # Signal control
│   │   │   ├── violations.py  # Violations API
│   │   │   └── settings.py    # System settings
│   │   │
│   │   └── ml/                # Machine Learning modules
│   │       ├── detector.py    # YOLOv8 vehicle detection
│   │       ├── traffic_analyzer.py  # Traffic analysis
│   │       ├── signal_controller.py # Adaptive signals
│   │       ├── emergency_priority.py # Emergency system
│   │       ├── video_processor.py   # Video processing
│   │       └── detection_storage.py # Detection caching
│   │
│   ├── requirements.txt       # Python dependencies
│   ├── venv/                  # Virtual environment
│   └── data/                  # Data folders
│
├── frontend/                   # React TypeScript Frontend
│   ├── src/
│   │   ├── main.tsx           # App entry point
│   │   ├── App.tsx            # Main app component
│   │   ├── index.css          # Global styles
│   │   │
│   │   ├── pages/             # Page components
│   │   │   ├── Dashboard.tsx  # Live monitoring
│   │   │   ├── Analytics.tsx  # Analytics dashboard
│   │   │   ├── CameraManagement.tsx # Camera config
│   │   │   ├── LiveMonitoring.tsx   # Video analysis
│   │   │   ├── Emergency.tsx  # Emergency management
│   │   │   └── Settings.tsx   # System settings
│   │   │
│   │   ├── components/        # Reusable components
│   │   │   ├── layout/        # Header, Sidebar
│   │   │   ├── charts/        # Chart components
│   │   │   ├── ui/            # UI primitives
│   │   │   └── VideoUpload.tsx # Video upload widget
│   │   │
│   │   └── lib/
│   │       └── api.ts         # Axios API client
│   │
│   ├── package.json           # Node dependencies
│   ├── vite.config.ts         # Vite configuration
│   ├── tailwind.config.js     # Tailwind config
│   └── tsconfig.json          # TypeScript config
│
├── data/                       # Data storage
│   ├── models/
│   │   └── yolov8n.pt         # YOLO model weights
│   ├── videos/                # Input traffic videos
│   └── outputs/               # Processed outputs
│
└── docs/                       # Documentation
    ├── PROJECT_OVERVIEW.md
    ├── PLANTUML_DIAGRAMS.md
    └── PRESENTATION_README.md
```

---

## 🏗️ Backend Architecture

### 1. Application Entry (`main.py`)

**Purpose**: Initializes and runs the FastAPI application

**What happens on startup**:
```python
1. Load configuration from .env file
2. Connect to MongoDB database
3. Initialize ML components:
   - Load YOLOv8 model (yolov8n.pt)
   - Create VehicleDetector instance
   - Initialize TrafficAnalyzer
   - Setup SignalController
   - Start EmergencyPrioritySystem
4. Register API routers
5. Setup CORS middleware
6. Start Uvicorn server on port 8000
7. Create WebSocket endpoint for real-time updates
```

**Key Code**:
```python
# Lifespan event handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await Database.connect_db()
    detector = VehicleDetector(model_path, confidence=0.15)
    analyzer = TrafficAnalyzer()
    signal_controller = SignalController()
    yield
    # Shutdown
    await Database.close_db()

app = FastAPI(lifespan=lifespan)
```

---

### 2. Configuration (`config.py`)

**Purpose**: Centralized configuration management

**Settings**:
- Database URLs
- Model paths
- Thresholds (confidence, congestion)
- Signal timings (min/max green time)
- API prefixes

**Uses Pydantic Settings**:
```python
class Settings(BaseSettings):
    MONGODB_URL: str = "mongodb://localhost:27017"
    YOLO_MODEL_PATH: str = "../data/models/yolov8n.pt"
    YOLO_CONFIDENCE: float = 0.15
    MIN_GREEN_TIME: int = 15
    MAX_GREEN_TIME: int = 120
```

---

### 3. Database Layer (`database.py`)

**Purpose**: MongoDB connection and collection management

**What it does**:
- Creates async MongoDB client using Motor
- Provides database instance
- Defines collection accessors
- Handles connection lifecycle

**Collections**:
```python
- traffic_data      # Real-time vehicle counts
- cameras           # Camera configurations
- emergency_events  # Emergency vehicle logs
- signal_timings    # Signal control history
- analytics         # Aggregated statistics
- violations        # Traffic violations
```

---

### 4. ML Modules (`app/ml/`)

#### A. **detector.py** - Vehicle Detection

**Purpose**: YOLOv8 vehicle detection engine

**What it does**:
```python
1. Loads YOLOv8 model (yolov8n.pt)
2. Processes video frames
3. Detects vehicles with bounding boxes
4. Classifies vehicle types
5. Filters by confidence threshold (0.15)
6. Special logic for auto-rickshaw detection
7. Emergency vehicle detection (color analysis)
```

**Key Methods**:
```python
def detect(frame):
    # Run YOLO inference
    results = model(frame, conf=0.15, imgsz=640)
    
    # Process detections
    for box in results.boxes:
        vehicle_type = classify_vehicle(box)
        if is_emergency(box):
            mark_as_emergency()
    
    return detections
```

#### B. **traffic_analyzer.py** - Traffic Analysis

**Purpose**: Analyzes traffic patterns and congestion

**What it does**:
```python
1. Counts vehicles by type
2. Calculates traffic density
3. Determines congestion level (0-100%)
4. Classifies traffic state (light/moderate/heavy/congested)
5. Tracks vehicle flow rates
6. Generates real-time statistics
```

**Algorithm**:
```python
def calculate_congestion(vehicle_count):
    density = vehicle_count / road_capacity
    congestion_level = min(density * 100, 100)
    
    if congestion_level < 30:
        state = "light"
    elif congestion_level < 60:
        state = "moderate"
    elif congestion_level < 80:
        state = "heavy"
    else:
        state = "congested"
```

#### C. **signal_controller.py** - Adaptive Signal Control

**Purpose**: Calculates optimal traffic signal timings

**What it does**:
```python
1. Takes vehicle counts from all directions
2. Applies adaptive timing algorithm
3. Calculates green time proportional to traffic
4. Ensures min/max time constraints
5. Generates signal cycle timings
```

**Adaptive Algorithm**:
```python
def calculate_adaptive_timing(traffic_data):
    # North-South direction
    ns_vehicles = traffic_data['north_south']
    
    # East-West direction
    ew_vehicles = traffic_data['east_west']
    
    total = ns_vehicles + ew_vehicles
    
    # Proportional allocation
    ns_green = (ns_vehicles / total) * MAX_GREEN_TIME
    ew_green = (ew_vehicles / total) * MAX_GREEN_TIME
    
    # Apply constraints
    ns_green = clamp(ns_green, MIN_GREEN_TIME, MAX_GREEN_TIME)
    ew_green = clamp(ew_green, MIN_GREEN_TIME, MAX_GREEN_TIME)
    
    return {
        'north_south': ns_green,
        'east_west': ew_green
    }
```

#### D. **emergency_priority.py** - Emergency Vehicle System

**Purpose**: Detects and prioritizes emergency vehicles

**What it does**:
```python
1. Detects emergency vehicles (ambulance, police, fire)
2. Identifies direction of emergency vehicle
3. Overrides normal signal timing
4. Sets emergency direction to GREEN (60 seconds)
5. Sets all other directions to RED
6. Logs emergency event with timestamp
7. Sends real-time alert to dashboard
8. Resumes normal operation after clearance
```

**Emergency Detection**:
```python
def detect_emergency(frame, detections):
    for detection in detections:
        # Extract region
        roi = frame[y1:y2, x1:x2]
        
        # Convert to HSV color space
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        
        # Check for white vehicle with red/blue markings
        if has_emergency_colors(hsv):
            return True, get_direction(detection)
```

#### E. **video_processor.py** - Video Processing

**Purpose**: Processes uploaded videos frame-by-frame

**What it does**:
```python
1. Opens video file using OpenCV
2. Extracts frames (skips every 2nd frame for speed)
3. Runs YOLOv8 detection on each frame
4. Counts vehicles and analyzes traffic
5. Generates annotated video output
6. Creates statistics summary
7. Saves results to database
```

**Processing Pipeline**:
```python
def process_video(video_path):
    cap = cv2.VideoCapture(video_path)
    frame_count = 0
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Skip frames for performance
        if frame_count % FRAME_SKIP != 0:
            continue
        
        # Detect vehicles
        detections = detector.detect(frame)
        
        # Analyze traffic
        analysis = analyzer.analyze_frame(detections)
        
        # Draw annotations
        annotated = draw_boxes(frame, detections)
        
        frame_count += 1
    
    # Generate summary
    return statistics
```

---

### 5. API Routers (`app/routers/`)

#### A. **traffic.py** - Traffic Management API

**Endpoints**:

1. **GET `/api/v1/traffic/current`**
   - Returns real-time traffic data from all cameras
   - Used by dashboard for live monitoring

2. **POST `/api/v1/traffic/report`**
   - Submit traffic data from camera processing
   - Stores in MongoDB

3. **POST `/api/v1/traffic/upload-video`**
   - Upload video file for processing
   - Returns job ID for status tracking
   - Starts background processing

4. **GET `/api/v1/traffic/processing-status/{job_id}`**
   - Check video processing status
   - Returns: pending, processing, completed, failed

5. **GET `/api/v1/traffic/detection-results/{job_id}`**
   - Get detection results after processing
   - Returns vehicle counts, analytics, charts

#### B. **cameras.py** - Camera Management API

**Endpoints**:

1. **GET `/api/v1/cameras`**
   - List all registered cameras
   - Returns camera configs (ID, name, RTSP URL, location)

2. **POST `/api/v1/cameras`**
   - Add new camera
   - Requires: camera_id, name, rtsp_url, location

3. **PUT `/api/v1/cameras/{camera_id}`**
   - Update camera configuration

4. **DELETE `/api/v1/cameras/{camera_id}`**
   - Remove camera

5. **POST `/api/v1/cameras/start-stream/{camera_id}`**
   - Start live stream processing
   - Connects to RTSP stream, runs detection

6. **POST `/api/v1/cameras/stop-stream/{camera_id}`**
   - Stop stream processing

#### C. **analytics.py** - Analytics API

**Endpoints**:

1. **GET `/api/v1/analytics/dashboard`**
   - Dashboard statistics
   - Returns: total vehicles today, average congestion, emergency count

2. **GET `/api/v1/analytics/hourly`**
   - Hourly traffic breakdown
   - Returns chart data for last 24 hours

3. **GET `/api/v1/analytics/daily`**
   - Daily statistics
   - Vehicle counts, peak hours, congestion trends

4. **GET `/api/v1/analytics/weekly`**
   - Weekly comparison
   - Day-by-day breakdown

5. **POST `/api/v1/analytics/export-report`**
   - Generate PDF/Excel report
   - Returns downloadable file

#### D. **signals.py** - Signal Control API

**Endpoints**:

1. **GET `/api/v1/signals/{intersection_id}`**
   - Current signal status
   - Returns: green times, current phase, mode

2. **POST `/api/v1/signals/adaptive`**
   - Trigger adaptive signal calculation
   - Input: vehicle counts per direction

3. **POST `/api/v1/signals/manual-override`**
   - Manual signal control by officer
   - Set custom green times

4. **GET `/api/v1/signals/history/{intersection_id}`**
   - Signal timing history

#### E. **violations.py** - Violations API

**Endpoints**:

1. **GET `/api/v1/violations`**
   - List traffic violations
   - Filters: date range, type, status

2. **POST `/api/v1/violations`**
   - Log new violation

3. **GET `/api/v1/violations/stats`**
   - Violation statistics

---

## 🎨 Frontend Architecture

### 1. Application Entry (`main.tsx`)

**Purpose**: React application bootstrap

```typescript
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
```

---

### 2. Main App Component (`App.tsx`)

**Purpose**: Main application shell with routing

**What it does**:
```typescript
1. Manages page navigation state
2. Renders Sidebar and Header
3. Routes to different pages based on selection
4. Provides page titles and subtitles
```

**Pages**:
- Dashboard - 4-way intersection live monitor
- Live Monitoring - Video upload and processing
- Camera Management - Add/configure cameras
- Analytics - Traffic charts and reports
- Emergency - Emergency event management
- Settings - System configuration

---

### 3. Pages (`src/pages/`)

#### A. **Dashboard.tsx** - Live Traffic Monitor

**Purpose**: Real-time 4-direction traffic monitoring

**Components**:
- 4 camera grids (North, South, East, West)
- Real-time vehicle counts per direction
- Traffic signal status (Red/Yellow/Green)
- Emergency alerts
- Congestion indicators

**Data Flow**:
```typescript
1. Fetch camera list from API
2. Connect to WebSocket for real-time updates
3. Display live counts from each camera
4. Show signal timings
5. Update every 2 seconds
```

**API Calls**:
```typescript
- GET /api/v1/cameras
- GET /api/v1/traffic/current
- WebSocket: ws://localhost:8000/ws/live-feed
```

#### B. **LiveMonitoring.tsx** - Video Analysis

**Purpose**: Upload and process traffic videos

**Features**:
- File upload (drag & drop)
- Video validation (MP4, AVI)
- Processing progress bar
- Real-time status updates
- Results display with charts

**Workflow**:
```typescript
1. User selects video file
2. Upload to backend (POST /upload-video)
3. Receive job ID
4. Poll status every 2 seconds (GET /processing-status/{job_id})
5. When complete, fetch results (GET /detection-results/{job_id})
6. Display vehicle counts, congestion graph, analytics
```

#### C. **Analytics.tsx** - Traffic Analytics Dashboard

**Purpose**: Historical data visualization

**Charts**:
1. **Line Chart**: Vehicle count over time (24 hours)
2. **Bar Chart**: Peak hour traffic
3. **Pie Chart**: Vehicle type breakdown
4. **Heatmap**: Congestion levels by hour

**Filters**:
- Date range picker
- Camera selection
- Report type (hourly/daily/weekly)

**Export Options**:
- Download PDF report
- Export Excel spreadsheet

#### D. **CameraManagement.tsx** - Camera Configuration

**Purpose**: Manage traffic cameras

**Features**:
- List all cameras
- Add new camera (form with RTSP URL)
- Edit camera details
- Delete camera
- Start/stop live streams
- Test camera connection

**Form Fields**:
```typescript
- camera_id: string
- name: string
- rtsp_url: string (e.g., rtsp://192.168.1.100:554/stream)
- location: string
- direction: north | south | east | west
```

#### E. **Emergency.tsx** - Emergency Management

**Purpose**: Track emergency vehicle events

**Features**:
- Active emergencies list
- Emergency event history
- Response time statistics
- Emergency type filter (ambulance/police/fire)
- Timeline view

**Data Displayed**:
- Event ID
- Timestamp
- Vehicle type
- Direction
- Response time
- Camera that detected
- Images (original + annotated)

---

### 4. Components (`src/components/`)

#### A. **Layout Components**

**Sidebar.tsx**:
- Navigation menu
- Active page highlighting
- Icons for each section

**Header.tsx**:
- Page title
- Subtitle
- User info
- Notifications

#### B. **UI Components** (`ui/`)

**button.tsx**: Reusable button component  
**input.tsx**: Form input fields  
**label.tsx**: Form labels  
**checkbox.tsx**: Checkboxes

#### C. **Chart Components** (`charts/`)

**TrafficLineChart.tsx**: Time-series traffic data  
**VehicleBarChart.tsx**: Vehicle type comparison  
**CongestionHeatmap.tsx**: Congestion visualization

#### D. **VideoUpload.tsx**

**Purpose**: Drag-and-drop video uploader

**Features**:
- File validation
- Upload progress
- Error handling
- Preview thumbnail

---

### 5. API Client (`lib/api.ts`)

**Purpose**: Centralized Axios configuration

```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use((config) => {
  // Add auth token if exists
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle errors globally
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

export default api;
```

---

## 🗄️ Database Design

### MongoDB Collections

#### 1. **cameras**
```javascript
{
  _id: ObjectId,
  camera_id: "CAM_001",
  name: "Main Intersection - North",
  rtsp_url: "rtsp://192.168.1.100:554/stream",
  location: "Connaught Place, Delhi",
  direction: "north",
  status: "active",
  created_at: ISODate,
  updated_at: ISODate
}
```

#### 2. **traffic_data**
```javascript
{
  _id: ObjectId,
  camera_id: "CAM_001",
  timestamp: ISODate,
  vehicle_counts: {
    car: 15,
    motorcycle: 8,
    truck: 2,
    bus: 1,
    auto_rickshaw: 3,
    bicycle: 2,
    total: 31
  },
  congestion_level: 68.5,
  traffic_state: "heavy",
  detection_confidence: 0.87
}
```

#### 3. **emergency_events**
```javascript
{
  _id: ObjectId,
  event_id: "EMG_2024112801",
  camera_id: "CAM_001",
  timestamp: ISODate,
  vehicle_type: "ambulance",
  direction: "north",
  confidence: 0.92,
  priority_given: true,
  green_time_allocated: 60,
  response_time: 2.3,
  status: "completed"
}
```

#### 4. **signal_timings**
```javascript
{
  _id: ObjectId,
  timestamp: ISODate,
  cycle_type: "adaptive",
  timings: {
    north_south: {
      green_time: 65,
      yellow_time: 5,
      red_time: 45,
      vehicle_count: 25
    },
    east_west: {
      green_time: 30,
      yellow_time: 5,
      red_time: 80,
      vehicle_count: 10
    }
  },
  total_cycle_time: 120
}
```

#### 5. **analytics**
```javascript
{
  _id: ObjectId,
  date: ISODate("2024-11-28"),
  type: "daily",
  statistics: {
    total_vehicles: 15847,
    peak_hour: "18:00-19:00",
    average_congestion: 54.2,
    vehicle_breakdown: {
      car: 8456,
      motorcycle: 4231,
      truck: 892,
      bus: 453,
      auto_rickshaw: 1567,
      bicycle: 248
    },
    emergency_events: 5
  }
}
```

---

## 🔄 How Technologies Work Together

### Complete Request Flow

#### Scenario 1: **Live Camera Monitoring**

```
1. USER opens Dashboard
   └─> React renders Dashboard.tsx

2. FRONTEND fetches camera list
   └─> axios.get('/api/v1/cameras')
   
3. BACKEND receives request
   └─> cameras.py router handles request
   └─> database.py queries MongoDB
   └─> Returns camera configs
   
4. FRONTEND establishes WebSocket
   └─> WebSocket connection to ws://localhost:8000/ws/live-feed
   
5. BACKEND starts camera streams
   └─> OpenCV connects to RTSP streams
   └─> Reads frames from IP cameras
   
6. ML PROCESSING (continuous loop)
   └─> detector.py runs YOLOv8 on frames
   └─> Detects vehicles, gets bounding boxes
   └─> traffic_analyzer.py counts vehicles
   └─> Calculates congestion level
   └─> emergency_priority.py checks for emergency vehicles
   
7. SIGNAL CONTROL
   └─> signal_controller.py calculates adaptive timing
   └─> If emergency detected, override signals
   
8. DATABASE UPDATE
   └─> Save traffic_data to MongoDB
   └─> Log emergency events if any
   
9. REAL-TIME UPDATE
   └─> Backend sends WebSocket message
   └─> Frontend receives update
   └─> React re-renders with new data
   └─> Dashboard shows live counts
```

#### Scenario 2: **Video Upload & Processing**

```
1. USER selects video file
   └─> LiveMonitoring.tsx handles file

2. FRONTEND uploads video
   └─> FormData with video file
   └─> POST /api/v1/traffic/upload-video
   
3. BACKEND receives upload
   └─> traffic.py validates file (MP4/AVI)
   └─> Saves to data/videos/
   └─> Creates job ID
   └─> Returns job ID to frontend
   
4. BACKGROUND PROCESSING starts
   └─> video_processor.py opens video
   └─> Extracts frames (skip every 2nd)
   
   Loop for each frame:
   └─> detector.py runs YOLOv8 inference
   └─> Gets detections with confidence scores
   └─> traffic_analyzer.py counts vehicles
   └─> Calculates statistics
   
5. GENERATE RESULTS
   └─> Creates summary statistics
   └─> Generates charts data
   └─> Saves to MongoDB
   └─> Updates job status to "completed"
   
6. FRONTEND POLLING
   └─> Every 2 seconds: GET /processing-status/{job_id}
   └─> Shows progress to user
   
7. FETCH RESULTS
   └─> When completed: GET /detection-results/{job_id}
   └─> Backend queries MongoDB
   └─> Returns detection data
   
8. DISPLAY RESULTS
   └─> Recharts renders vehicle count graph
   └─> Shows congestion timeline
   └─> Displays vehicle type breakdown
```

#### Scenario 3: **Emergency Vehicle Detection**

```
1. CAMERA feeds video to system
   └─> RTSP stream or live camera
   
2. FRAME EXTRACTION
   └─> OpenCV reads frame
   └─> Preprocesses image
   
3. VEHICLE DETECTION
   └─> YOLOv8 detects all vehicles
   └─> Gets bounding boxes for each vehicle
   
4. EMERGENCY CHECK
   └─> emergency_priority.py analyzes each vehicle
   └─> Extracts vehicle region from frame
   └─> Converts to HSV color space
   └─> Checks for white body + red/blue markings
   
5. EMERGENCY CONFIRMED
   └─> Identifies vehicle direction (north/south/east/west)
   └─> Triggers emergency mode
   
6. SIGNAL OVERRIDE
   └─> signal_controller.py overrides normal timing
   └─> Sets emergency direction: GREEN (60 seconds)
   └─> Sets other directions: RED
   
7. DATABASE LOGGING
   └─> Saves emergency_event to MongoDB
   └─> Records: timestamp, vehicle_type, direction, response_time
   
8. REAL-TIME ALERT
   └─> Sends WebSocket message
   └─> Frontend receives alert
   └─> Shows emergency notification popup
   └─> Plays alert sound
   
9. COUNTDOWN
   └─> Waits 60 seconds for emergency vehicle to pass
   
10. RESUME NORMAL
    └─> Returns to adaptive signal control
    └─> Marks emergency event as "completed"
```

---

## 📂 File-by-File Explanation

### Backend Files

#### `backend/app/main.py`
- **Purpose**: Application entry point
- **Imports**: FastAPI, routers, ML modules
- **Lifespan events**: Startup (connect DB, load model), Shutdown (close connections)
- **Middleware**: CORS for frontend communication
- **WebSocket**: Real-time data streaming
- **Routes**: Includes all API routers

#### `backend/app/config.py`
- **Purpose**: Configuration management
- **Uses**: Pydantic Settings for type-safe config
- **Settings**: Database URLs, model paths, thresholds
- **Environment**: Loads from .env file
- **Caching**: @lru_cache for singleton pattern

#### `backend/app/database.py`
- **Purpose**: MongoDB connection
- **Motor**: Async MongoDB driver
- **Methods**: connect_db(), close_db(), get_database()
- **Collections**: Provides accessors for all collections
- **Error Handling**: Graceful degradation if DB unavailable

#### `backend/app/models/traffic.py`
- **Purpose**: Traffic data models
- **Pydantic**: Data validation
- **Models**: TrafficData, TrafficSummary, VehicleCount
- **Validation**: Type checking, required fields

#### `backend/app/routers/traffic.py`
- **Purpose**: Traffic API endpoints
- **Dependencies**: detector, analyzer, video_processor
- **Endpoints**: Current traffic, upload video, processing status
- **Background Tasks**: Async video processing
- **WebSocket**: Broadcasts live updates

#### `backend/app/ml/detector.py`
- **Purpose**: YOLOv8 vehicle detection
- **Model**: Loads yolov8n.pt
- **Classes**: 7 vehicle types
- **Methods**: detect(), detect_emergency()
- **Optimization**: Frame skipping, GPU support
- **Auto-rickshaw logic**: Size-based classification

#### `backend/app/ml/traffic_analyzer.py`
- **Purpose**: Traffic analysis
- **Calculations**: Density, congestion, flow rate
- **State**: light/moderate/heavy/congested
- **History**: Maintains sliding window of data
- **Methods**: analyze_frame(), calculate_congestion()

#### `backend/app/ml/signal_controller.py`
- **Purpose**: Adaptive signal timing
- **Algorithm**: Proportional allocation based on vehicle counts
- **Constraints**: Min/max green time (15-120 seconds)
- **Methods**: calculate_adaptive_timing(), emergency_override()

#### `backend/app/ml/emergency_priority.py`
- **Purpose**: Emergency vehicle system
- **Detection**: HSV color space analysis
- **Priority**: Overrides normal signals
- **Response**: <3 second detection to signal change
- **Logging**: Records all emergency events

#### `backend/app/ml/video_processor.py`
- **Purpose**: Video file processing
- **OpenCV**: Frame extraction
- **Pipeline**: Read → Detect → Analyze → Save
- **Output**: Annotated video, statistics
- **Performance**: Frame skipping for speed

#### `backend/requirements.txt`
- **Purpose**: Python dependencies
- **Categories**: Web, ML, Database, Utilities
- **Versions**: Pinned for reproducibility
- **Installation**: `pip install -r requirements.txt`

---

### Frontend Files

#### `frontend/src/main.tsx`
- **Purpose**: React app entry
- **ReactDOM**: Renders App component
- **StrictMode**: Development checks
- **Mounts**: To `<div id="root">`

#### `frontend/src/App.tsx`
- **Purpose**: Main app shell
- **State**: Active page navigation
- **Layout**: Sidebar + Header + Content
- **Routing**: Conditional rendering based on page
- **Page Configs**: Titles and subtitles

#### `frontend/src/pages/Dashboard.tsx`
- **Purpose**: Live 4-way traffic monitor
- **Grid Layout**: 2x2 camera grid
- **Real-time**: Vehicle counts, signals
- **WebSocket**: Live updates
- **Alerts**: Emergency notifications

#### `frontend/src/pages/LiveMonitoring.tsx`
- **Purpose**: Video upload interface
- **Upload**: File input, drag-drop
- **Progress**: Processing status
- **Results**: Charts and statistics
- **API**: Upload, poll status, fetch results

#### `frontend/src/pages/Analytics.tsx`
- **Purpose**: Analytics dashboard
- **Charts**: Line, bar, pie charts
- **Filters**: Date range, camera
- **Export**: PDF/Excel reports
- **Data**: Historical traffic data

#### `frontend/src/pages/CameraManagement.tsx`
- **Purpose**: Camera CRUD operations
- **List**: All cameras with status
- **Add**: Form with RTSP URL
- **Edit**: Update camera config
- **Delete**: Remove camera
- **Control**: Start/stop streams

#### `frontend/src/pages/Emergency.tsx`
- **Purpose**: Emergency event tracking
- **List**: Active and historical events
- **Details**: Response times, images
- **Filter**: By type, date, status
- **Timeline**: Chronological view

#### `frontend/src/components/layout/Sidebar.tsx`
- **Purpose**: Navigation menu
- **Icons**: Lucide React icons
- **Active**: Highlights current page
- **Click**: Changes active page

#### `frontend/src/components/layout/Header.tsx`
- **Purpose**: Page header
- **Title**: Dynamic based on page
- **Subtitle**: Context info
- **Actions**: User menu, notifications

#### `frontend/src/components/VideoUpload.tsx`
- **Purpose**: File upload component
- **Drag-Drop**: Drop zone
- **Validation**: File type, size
- **Progress**: Upload progress bar
- **Preview**: Video thumbnail

#### `frontend/src/lib/api.ts`
- **Purpose**: API client configuration
- **Axios**: HTTP client setup
- **Interceptors**: Request/response
- **Auth**: Token injection
- **Error**: Global error handling

#### `frontend/package.json`
- **Purpose**: Node.js dependencies
- **Scripts**: dev, build, preview
- **Dependencies**: React, Axios, Recharts
- **DevDependencies**: Vite, TypeScript, ESLint

#### `frontend/vite.config.ts`
- **Purpose**: Vite build configuration
- **Plugins**: React plugin
- **Port**: Dev server port
- **Proxy**: API proxying if needed

#### `frontend/tailwind.config.js`
- **Purpose**: Tailwind CSS configuration
- **Colors**: Custom color palette
- **Fonts**: Font family setup
- **Animations**: Custom animations

#### `frontend/tsconfig.json`
- **Purpose**: TypeScript configuration
- **Target**: ES2020
- **Module**: ESNext
- **Strict**: Strict type checking
- **Paths**: Import path aliases

---

### Data Files

#### `data/models/yolov8n.pt`
- **Purpose**: Pre-trained YOLO weights
- **Size**: ~6 MB (nano model)
- **Classes**: 80 COCO classes
- **Training**: Trained on COCO dataset
- **Usage**: Loaded by detector.py

#### `data/videos/`
- **Purpose**: Input video storage
- **Formats**: MP4, AVI
- **Source**: User uploads, camera recordings
- **Access**: Read by video_processor.py

#### `data/outputs/`
- **Purpose**: Processed video outputs
- **Contents**: Annotated videos, reports
- **Generated**: By video_processor.py
- **Download**: Accessible via API

---

## 🔗 Technology Integration

### 1. **Frontend ↔ Backend Communication**

**HTTP Requests (REST API)**:
```typescript
// Frontend (React)
import api from './lib/api';

const fetchTraffic = async () => {
  const response = await api.get('/api/v1/traffic/current');
  return response.data;
};
```

```python
# Backend (FastAPI)
@router.get("/current")
async def get_current_traffic():
    data = await database.traffic_data.find().to_list(100)
    return data
```

**WebSocket (Real-time)**:
```typescript
// Frontend
const ws = new WebSocket('ws://localhost:8000/ws/live-feed');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  updateDashboard(data);
};
```

```python
# Backend
@app.websocket("/ws/live-feed")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = get_live_data()
        await websocket.send_json(data)
```

---

### 2. **Backend ↔ Database Integration**

**Motor (Async MongoDB Driver)**:
```python
# Connect
from motor.motor_asyncio import AsyncIOMotorClient

client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client.traffic_management

# Insert
await db.traffic_data.insert_one({
    "camera_id": "CAM_001",
    "timestamp": datetime.now(),
    "vehicle_counts": {"car": 10, "motorcycle": 5}
})

# Query
data = await db.traffic_data.find({"camera_id": "CAM_001"}).to_list(100)

# Update
await db.cameras.update_one(
    {"camera_id": "CAM_001"},
    {"$set": {"status": "active"}}
)
```

---

### 3. **ML Models ↔ Backend Integration**

**YOLOv8 with FastAPI**:
```python
# Initialize once on startup
detector = VehicleDetector(model_path="yolov8n.pt", confidence=0.15)

# Use in endpoints
@router.post("/detect")
async def detect_vehicles(file: UploadFile):
    # Read image
    contents = await file.read()
    image = cv2.imdecode(np.frombuffer(contents, np.uint8), cv2.IMREAD_COLOR)
    
    # Detect
    detections = detector.detect(image)
    
    # Analyze
    analysis = analyzer.analyze_frame(detections)
    
    return {
        "detections": detections,
        "analysis": analysis
    }
```

---

### 4. **React Query for Data Fetching**

```typescript
import { useQuery } from '@tanstack/react-query';
import api from './lib/api';

function Dashboard() {
  // Auto-refetch every 2 seconds
  const { data, isLoading } = useQuery({
    queryKey: ['traffic'],
    queryFn: () => api.get('/api/v1/traffic/current'),
    refetchInterval: 2000,
  });
  
  if (isLoading) return <div>Loading...</div>;
  
  return <div>{/* Display traffic data */}</div>;
}
```

---

## 🚀 Setup & Installation

### Prerequisites
- Python 3.10+
- Node.js 18+
- MongoDB 6.0+
- Git

### Backend Setup

```bash
# 1. Navigate to backend
cd backend

# 2. Create virtual environment
python -m venv venv

# 3. Activate venv (Windows)
.\venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Create .env file
copy .env.example .env

# 6. Edit .env with your settings
# MONGODB_URL=mongodb://localhost:27017
# YOLO_MODEL_PATH=../data/models/yolov8n.pt

# 7. Download YOLO model (auto-downloads on first run)
# Or manually place yolov8n.pt in data/models/

# 8. Start backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend runs at: http://localhost:8000  
API docs at: http://localhost:8000/docs

### Frontend Setup

```bash
# 1. Navigate to frontend
cd frontend

# 2. Install dependencies
npm install

# 3. Start dev server
npm run dev
```

Frontend runs at: http://localhost:5173

### MongoDB Setup

```bash
# Install MongoDB Community Edition
# Start MongoDB service
mongod --dbpath /data/db

# Or use Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

---

## 📊 Data Flow Summary

```
Camera/Video Input
      ↓
OpenCV Frame Extraction
      ↓
YOLOv8 Vehicle Detection
      ↓
Traffic Analysis (counts, density)
      ↓
Emergency Check (color detection)
      ↓
Signal Control (adaptive/emergency)
      ↓
MongoDB Storage
      ↓
FastAPI REST Endpoints
      ↓
React Frontend Display
      ↓
User Dashboard
```

---

## 🎓 Key Concepts

### 1. **Async/Await in Python**
- Non-blocking I/O operations
- Better performance for database queries
- Concurrent request handling

### 2. **WebSocket vs REST**
- **REST**: Request-response (pull data)
- **WebSocket**: Persistent connection (push data)
- Use WebSocket for real-time updates

### 3. **Component-Based Architecture**
- React components are reusable
- Props for data passing
- State management with hooks

### 4. **YOLOv8 Inference**
- One-stage object detection
- Real-time capable (30 FPS)
- Confidence threshold filtering

### 5. **MongoDB vs SQL**
- Document-based (JSON-like)
- Schema-less flexibility
- Better for time-series data

---

## 📚 Learning Resources

### Backend
- FastAPI Docs: https://fastapi.tiangolo.com/
- YOLOv8 Docs: https://docs.ultralytics.com/
- MongoDB Tutorial: https://www.mongodb.com/docs/

### Frontend
- React Docs: https://react.dev/
- TypeScript Handbook: https://www.typescriptlang.org/docs/
- Tailwind CSS: https://tailwindcss.com/docs

---

## 🔧 Troubleshooting

### Common Issues

**1. YOLOv8 model not found**
- Ensure yolov8n.pt is in `data/models/`
- Model auto-downloads on first run if missing

**2. MongoDB connection failed**
- Check if MongoDB is running: `mongod --version`
- Verify MONGODB_URL in .env

**3. CORS errors in frontend**
- Backend CORS middleware allows localhost:5173
- Check port numbers match

**4. Video processing slow**
- Increase FRAME_SKIP in config (process every 3rd frame)
- Use GPU if available (CUDA)

**5. WebSocket disconnects**
- Check firewall settings
- Ensure backend is running

---

**Last Updated**: November 28, 2024  
**Version**: 1.0  
**Project**: Smart Traffic Management System
