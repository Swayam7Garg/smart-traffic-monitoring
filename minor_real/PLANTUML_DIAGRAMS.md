# PlantUML Diagrams - Smart Traffic Management System

Simple, clean PlantUML diagrams for your project. Copy and paste into http://www.plantuml.com/plantuml/

---

## 1. 🔄 SEQUENCE DIAGRAM - Emergency Vehicle Detection

```plantuml
@startuml
skinparam backgroundColor #FEFEFE
skinparam sequenceArrowThickness 2
skinparam roundcorner 10

actor "Emergency\nVehicle" as EV #FFD700
participant "Camera" as Cam #FF6B6B
participant "YOLOv8\nDetector" as YOLO #EE4C2C
participant "Emergency\nSystem" as Emerg #FF4500
participant "Signal\nController" as Signal #50C878
database "MongoDB" as DB #47A248

EV -> Cam: Vehicle enters frame
activate Cam
Cam -> YOLO: Send video frame
activate YOLO

YOLO -> YOLO: Detect vehicles
YOLO -> YOLO: Check for emergency\n(white + red/blue)

alt Emergency Detected
    YOLO -> Emerg: ⚠️ Emergency vehicle found!
    activate Emerg
    
    Emerg -> Signal: Override signal\nGreen for 60s
    activate Signal
    Signal -> Signal: Set emergency\ndirection GREEN
    Signal --> Emerg: Signal changed ✅
    deactivate Signal
    
    Emerg -> DB: Log emergency event
    Emerg --> YOLO: Priority given
    deactivate Emerg
else Normal Traffic
    YOLO -> Signal: Regular traffic count
    Signal -> Signal: Calculate adaptive timing
end

YOLO --> Cam: Continue processing
deactivate YOLO
deactivate Cam

@enduml
```

---

## 2. 🔄 SEQUENCE DIAGRAM - Video Upload & Analysis

```plantuml
@startuml
skinparam backgroundColor #FEFEFE
skinparam roundcorner 10

actor "User" as User #4A90E2
participant "Frontend" as FE #61DAFB
participant "FastAPI" as API #009688
participant "Video\nProcessor" as VP #9B59B6
participant "YOLOv8" as YOLO #EE4C2C
database "MongoDB" as DB #47A248

User -> FE: Upload video file
activate FE

FE -> API: POST /upload-video
activate API

API -> API: Validate file\n(MP4/AVI)
API -> API: Create Job ID
API --> FE: Return Job ID
deactivate API

FE -> FE: Start polling\nfor status

API -> VP: Process video
activate VP

loop For each frame
    VP -> YOLO: Detect vehicles
    activate YOLO
    YOLO --> VP: Vehicle detections
    deactivate YOLO
    VP -> VP: Count & analyze
end

VP -> DB: Save results
VP --> API: ✅ Processing complete
deactivate VP

FE -> API: GET /results/{job_id}
activate API
API -> DB: Fetch results
DB --> API: Detection data
API --> FE: Results + analytics
deactivate API

FE -> User: Display charts 📊
deactivate FE

@enduml
```

---

## 3. 👥 USE CASE DIAGRAM - System Interactions

```plantuml
@startuml
skinparam backgroundColor #FEFEFE
left to right direction

actor "Traffic\nOfficer" as Officer #4A90E2
actor "System\nAdmin" as Admin #E94B3C
actor "Automated\nSystem" as System #50C878

rectangle "Smart Traffic Management System" {
  usecase UC1 as "Monitor Live\nTraffic"
  usecase UC2 as "View\nAnalytics"
  usecase UC3 as "Generate\nReports"
  usecase UC4 as "Manual Signal\nOverride"
  usecase UC5 as "Manage\nCameras"
  usecase UC6 as "Configure\nSettings"
  
  usecase UC7 as "Detect\nVehicles"
  usecase UC8 as "Control\nSignals"
  usecase UC9 as "Detect\nEmergency"
  usecase UC10 as "Emergency\nPriority"
}

' Associations
Officer --> UC1
Officer --> UC2
Officer --> UC3
Officer --> UC4

Admin --> UC5
Admin --> UC6

System --> UC7
System --> UC8
System --> UC9

' Include relationships
UC1 ..> UC7 : <<include>>
UC4 ..> UC8 : <<include>>

' Extend relationships
UC9 ..> UC10 : <<extend>>

@enduml
```

---

## 4. 📊 DATA FLOW DIAGRAM (DFD) - Level 0 (Context)

```plantuml
@startuml
skinparam backgroundColor #FEFEFE
skinparam rectangleBackgroundColor #4A90E2
skinparam rectangleBorderColor #2C5F8D

rectangle "Traffic Cameras\n📹" as cameras #FF6B6B
rectangle "Traffic Officers\n👮" as officers #50C878
rectangle "Emergency Vehicles\n🚑" as emergency #FFD700
rectangle "Traffic Signals\n🚦" as signals #FF4500

rectangle "Smart Traffic\nManagement\nSystem" as system #4A90E2 {
}

cameras -down-> system : Video Stream
emergency -down-> system : Vehicle Presence
officers -down-> system : Commands\nView Data

system -down-> signals : Signal Control
system -up-> officers : Analytics\nAlerts
system -up-> emergency : Green Priority

@enduml
```

---

## 5. 📊 DATA FLOW DIAGRAM (DFD) - Level 1

```plantuml
@startuml
skinparam backgroundColor #FEFEFE

rectangle "Cameras\n📹" as cameras #FF6B6B
rectangle "Officers\n👮" as officers #50C878

' Processes
rectangle "P1\nDetect\nVehicles\n🧠" as P1 #EE4C2C
rectangle "P2\nAnalyze\nTraffic\n📊" as P2 #4A90E2
rectangle "P3\nCheck\nEmergency\n🚨" as P3 #FFD700
rectangle "P4\nAdaptive\nSignal\n🚦" as P4 #50C878
rectangle "P5\nEmergency\nPriority\n⚡" as P5 #FF4500
rectangle "P6\nStore\nData\n💾" as P6 #9B59B6

' Data Stores
database "D1\nYOLO Model" as D1 #F5F5F5
database "D2\nMongoDB" as D2 #47A248

cameras --> P1 : Video Frames
P1 <--> D1 : Model Weights
P1 --> P2 : Detections

P2 --> P3 : Traffic Stats

P3 --> P4 : Normal Traffic
P3 --> P5 : Emergency Found

P4 --> P6 : Signal Timings
P5 --> P6 : Emergency Data

P6 <--> D2 : Read/Write

D2 --> officers : Dashboard Data
officers --> P4 : Manual Override

@enduml
```

---

## 6. 📦 BLOCK DIAGRAM - System Architecture

```plantuml
@startuml
skinparam backgroundColor #FEFEFE
skinparam componentStyle rectangle

package "INPUT LAYER" #FFE6E6 {
    [📹 Camera 1\nNorth] as Cam1
    [📹 Camera 2\nSouth] as Cam2
    [📹 Camera 3\nEast] as Cam3
    [📹 Camera 4\nWest] as Cam4
}

package "AI PROCESSING" #FFE6CC {
    [🧠 YOLOv8\nDetector] as YOLO
    [⚙️ OpenCV\nProcessor] as OpenCV
}

package "INTELLIGENCE" #E6F2FF {
    [📊 Traffic\nAnalyzer] as Analyzer
    [🚨 Emergency\nDetector] as Emergency
    [🚦 Signal\nController] as Signal
}

package "BACKEND" #E6FFE6 {
    [🔌 FastAPI\nServer] as API
    [🔄 WebSocket] as WS
}

package "FRONTEND" #F0E6FF {
    [⚛️ React\nDashboard] as React
}

database "💾 MongoDB" as DB #F5F5F5

Cam1 --> OpenCV
Cam2 --> OpenCV
Cam3 --> OpenCV
Cam4 --> OpenCV

OpenCV --> YOLO
YOLO --> Analyzer
YOLO --> Emergency

Analyzer --> Signal
Emergency --> Signal

Signal --> API
Analyzer --> API
Emergency --> API

API --> DB
API --> WS
WS --> React
DB --> React

@enduml
```

---

## 7. 🗄️ DATABASE DIAGRAM (Simplified ER)

```plantuml
@startuml
skinparam backgroundColor #FEFEFE
skinparam linetype ortho

entity "cameras" as cam #FF6B6B {
  * camera_id : string <<PK>>
  --
  name : string
  rtsp_url : string
  location : string
  direction : string
  status : string
}

entity "traffic_data" as traffic #4A90E2 {
  * _id : ObjectId <<PK>>
  --
  camera_id : string <<FK>>
  timestamp : datetime
  car : int
  motorcycle : int
  truck : int
  bus : int
  auto_rickshaw : int
  total : int
  congestion_level : float
}

entity "emergency_events" as emerg #FFD700 {
  * event_id : string <<PK>>
  --
  camera_id : string <<FK>>
  timestamp : datetime
  vehicle_type : string
  direction : string
  confidence : float
  response_time : float
}

entity "signal_timings" as signal #50C878 {
  * _id : ObjectId <<PK>>
  --
  timestamp : datetime
  ns_green_time : int
  ew_green_time : int
  cycle_type : string
  total_cycle : int
}

entity "analytics" as analytics #9B59B6 {
  * _id : ObjectId <<PK>>
  --
  date : date
  type : string
  total_vehicles : int
  peak_hour : string
  avg_congestion : float
}

cam ||--o{ traffic : "generates"
cam ||--o{ emerg : "detects"
traffic }o--|| analytics : "aggregates to"

@enduml
```

---

## 8. 🎨 UI FLOWCHART - User Navigation

```plantuml
@startuml
skinparam backgroundColor #FEFEFE
skinparam activityDiamondBackgroundColor #E6F2FF

start

:🌐 Open Browser;
:Load React App;

:📱 Dashboard Home;

repeat
  :Choose Menu Option;
  
  if (Which page?) then (Dashboard)
    :📺 **Live Monitoring**\n- 4 Camera Grid\n- Real-time Counts\n- Signal Status;
    
  elseif (Video) then
    :📹 **Video Analysis**\n- Upload Video\n- Process File\n- View Results;
    :Select Video File;
    :⏳ Upload & Process;
    :📊 Show Detection Results;
    
  elseif (Cameras) then
    :🎥 **Camera Management**\n- Add/Edit Cameras\n- Configure RTSP\n- Control Streams;
    
  elseif (Analytics) then
    :📈 **Analytics Dashboard**\n- Traffic Charts\n- Peak Hours\n- Export Reports;
    :Filter Date Range;
    :Display Charts;
    if (Export?) then (yes)
      :💾 Download PDF/Excel;
    endif
    
  elseif (Emergency) then
    :🚨 **Emergency Page**\n- Active Emergencies\n- Event History\n- Response Times;
    
  else (Settings)
    :⚙️ **Settings**\n- System Config\n- Thresholds\n- Timings;
  endif
  
repeat while (Continue using?) is (yes)
->no;

stop

@enduml
```

---

## 9. 🏗️ CLASS DIAGRAM - Core Models

```plantuml
@startuml
skinparam backgroundColor #FEFEFE
skinparam classAttributeIconSize 0

class VehicleDetector {
  - model: YOLO
  - confidence: float
  + __init__(model_path: str)
  + detect(frame): List[Detection]
  + detect_emergency(): bool
}

class TrafficAnalyzer {
  - vehicle_counts: dict
  - congestion_threshold: int
  + analyze_frame(detections): dict
  + calculate_congestion(): float
  + get_traffic_state(): string
}

class SignalController {
  - min_green: int
  - max_green: int
  + calculate_timing(counts): dict
  + adaptive_control(): int
  + emergency_override(): void
}

class EmergencySystem {
  - priority_duration: int
  + detect_emergency(frame): bool
  + trigger_priority(direction): void
  + clear_priority(): void
}

class Camera {
  + camera_id: string
  + name: string
  + rtsp_url: string
  + location: string
  + status: string
}

class TrafficData {
  + camera_id: string
  + timestamp: datetime
  + vehicle_counts: dict
  + congestion_level: float
  + traffic_state: string
}

VehicleDetector --> TrafficAnalyzer : provides detections
VehicleDetector --> EmergencySystem : checks emergency
TrafficAnalyzer --> SignalController : sends traffic data
EmergencySystem --> SignalController : overrides signals
Camera --> VehicleDetector : video stream
Camera --> TrafficData : generates

@enduml
```

---

## 10. 🔀 ACTIVITY DIAGRAM - Traffic Processing Flow

```plantuml
@startuml
skinparam backgroundColor #FEFEFE
skinparam activityDiamondBackgroundColor #FFE6CC

start

:📹 Read Camera Frame;

:🧠 YOLOv8 Detection;

if (Vehicles detected?) then (yes)
  :📊 Count Vehicles by Type;
  
  if (Emergency vehicle?) then (yes)
    :🔴 **EMERGENCY MODE**;
    :Get vehicle direction;
    :Override signals\nGreen: 60s;
    :💾 Log emergency event;
    :🔔 Send alert;
    :Wait 60 seconds;
    :Resume normal mode;
  else (no)
    :Calculate traffic density;
    :Run adaptive algorithm;
    :Update signal timings;
    :💾 Save traffic data;
  endif
else (no)
  :Wait for next frame;
endif

:Continue monitoring;

stop

@enduml
```

---

## 11. 🚀 DEPLOYMENT DIAGRAM (Simplified)

```plantuml
@startuml
skinparam backgroundColor #FEFEFE

node "Client Browser" as client #E6F2FF {
  component [React\nDashboard] as react #61DAFB
}

node "Application Server" as server #FFE6E6 {
  component [FastAPI\nBackend] as api #009688
  component [YOLOv8\nEngine] as yolo #EE4C2C
  component [OpenCV\nProcessor] as cv #FF6B6B
}

node "Database Server" as dbserver #E6FFE6 {
  database [MongoDB] as db #47A248
}

node "Camera Network" as cameras #FFF4E6 {
  artifact [IP Camera 1] as cam1
  artifact [IP Camera 2] as cam2
  artifact [IP Camera 3] as cam3
  artifact [IP Camera 4] as cam4
}

client -down-> api : HTTPS\nPort 8000
api -down-> db : MongoDB\nPort 27017
api -right-> yolo : Detections
yolo -right-> cv : Frames
cv -down-> cam1 : RTSP
cv -down-> cam2 : RTSP
cv -down-> cam3 : RTSP
cv -down-> cam4 : RTSP

@enduml
```

---

## 12. 📊 COMPONENT DIAGRAM - System Components

```plantuml
@startuml
skinparam backgroundColor #FEFEFE

package "Frontend Layer" {
  [Dashboard UI] as ui
  [Camera Grid] as grid
  [Analytics View] as charts
}

package "API Layer" {
  [Traffic Router] as traffic
  [Camera Router] as camera
  [Analytics Router] as analytics
}

package "ML Layer" {
  [Vehicle Detector] as detector
  [Traffic Analyzer] as analyzer
  [Emergency System] as emergency
}

package "Data Layer" {
  database [MongoDB] as db
  folder [File Storage] as files
}

ui --> traffic : REST API
ui --> camera : REST API
ui --> analytics : REST API

traffic --> detector
traffic --> analyzer
traffic --> emergency

camera --> detector

detector --> db
analyzer --> db
emergency --> db

traffic --> files
camera --> files

@enduml
```

---

## 13. 🎯 STATE DIAGRAM - Traffic Signal States

```plantuml
@startuml
skinparam backgroundColor #FEFEFE

[*] --> Normal

Normal : 🟢 Normal Operation
Normal : Adaptive timing active

Normal --> Emergency : Emergency\nVehicle Detected

Emergency : 🔴 Emergency Mode
Emergency : Priority override
Emergency : Fixed 60s green

Emergency --> ClearTime : Emergency\nCleared

ClearTime : ⏳ Clear Time
ClearTime : 10 second buffer

ClearTime --> Normal : Resume\nAdaptive

Normal --> Manual : Officer\nOverride

Manual : 👮 Manual Control
Manual : Officer sets timing

Manual --> Normal : Release\nControl

@enduml
```

---

## 🚀 HOW TO USE

### **Online (Easiest)**
1. Go to: http://www.plantuml.com/plantuml/
2. Copy any diagram code above
3. Paste into the text box
4. Click "Submit"
5. Download as PNG or SVG

### **VS Code**
1. Install extension: "PlantUML"
2. Create a `.puml` file
3. Paste diagram code
4. Press `Alt+D` to preview
5. Right-click → Export to PNG/SVG

### **Command Line**
```bash
# Install PlantUML
npm install -g node-plantuml

# Generate diagram
puml generate diagram.puml -o output.png
```

### **Python Script**
```python
from plantuml import PlantUML

server = PlantUML(url='http://www.plantuml.com/plantuml/img/')
server.processes_file('diagram.puml')
```

---

## 📝 CUSTOMIZATION TIPS

### Change Colors
```plantuml
skinparam backgroundColor #FEFEFE
skinparam componentStyle rectangle
participant "Name" as alias #FF0000  ' Red background
```

### Add Notes
```plantuml
note right of Component
  This is an important
  component that handles
  vehicle detection
end note
```

### Style Arrows
```plantuml
skinparam sequenceArrowThickness 2
skinparam roundcorner 10
A -> B : normal
A ->> B : async
A --> B : return
A ..> B : dotted
```

---

## 📊 DIAGRAM SUMMARY

| Diagram | Purpose | Complexity |
|---------|---------|------------|
| Sequence (Emergency) | Emergency flow | ⭐⭐ Simple |
| Sequence (Upload) | Video processing | ⭐⭐ Simple |
| Use Case | Actor interactions | ⭐ Very Simple |
| DFD Level 0 | Context diagram | ⭐ Very Simple |
| DFD Level 1 | Process flows | ⭐⭐ Simple |
| Block Diagram | System architecture | ⭐⭐ Simple |
| Database ER | Data structure | ⭐⭐ Simple |
| UI Flowchart | User navigation | ⭐⭐⭐ Medium |
| Class Diagram | Code structure | ⭐⭐ Simple |
| Activity Diagram | Process flow | ⭐⭐ Simple |
| Deployment | Infrastructure | ⭐⭐ Simple |
| Component | System parts | ⭐⭐ Simple |
| State Diagram | Signal states | ⭐ Very Simple |

All diagrams are simplified for clarity and easy understanding! 🎨

---

**Created**: November 27, 2024  
**Format**: PlantUML  
**Render**: http://www.plantuml.com/plantuml/
