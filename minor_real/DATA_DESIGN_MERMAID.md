# Data Design Diagrams - Mermaid Format

## 3.6.1 Entity-Relationship Diagram (Simplified)

```mermaid
erDiagram
    CAMERA ||--o{ TRAFFIC_DATA : generates
    CAMERA ||--o{ EMERGENCY_EVENT : detects
    CAMERA ||--o{ VIOLATION : captures
    INTERSECTION ||--o{ CAMERA : monitors
    INTERSECTION ||--o{ SIGNAL_TIMING : controls
    EMERGENCY_EVENT }o--|| SIGNAL_TIMING : triggers
    USER ||--o{ ANALYTICS : creates
    ANALYTICS }o--o{ TRAFFIC_DATA : aggregates

    CAMERA {
        string camera_id PK
        string name
        string direction
        string rtsp_url
        string status
        boolean is_active
        datetime created_at
    }

    TRAFFIC_DATA {
        objectId _id PK
        string camera_id FK
        datetime timestamp
        json vehicle_counts
        int total_vehicles
        float congestion_level
        string traffic_state
    }

    EMERGENCY_EVENT {
        string event_id PK
        string camera_id FK
        datetime timestamp
        float confidence
        int priority_level
        string status
        float response_time
    }

    SIGNAL_TIMING {
        string timing_id PK
        string intersection_id FK
        datetime timestamp
        string mode
        json signals
        int cycle_length
    }

    ANALYTICS {
        string report_id PK
        string report_type
        datetime start_date
        datetime end_date
        json aggregated_data
        string generated_by FK
    }

    VIOLATION {
        string violation_id PK
        string camera_id FK
        datetime timestamp
        string violation_type
        string vehicle_plate
        float fine_amount
    }

    INTERSECTION {
        string intersection_id PK
        string name
        json location
        int num_directions
        boolean is_active
    }

    USER {
        string user_id PK
        string username
        string email
        string role
        datetime created_at
    }
```

---

## 3.6.2 Class Diagram (Simplified)

```mermaid
classDiagram
    class VehicleDetector {
        -model: YOLO
        -confidence: float
        +detect(frame) List~Detection~
        +preprocess(frame) ndarray
    }

    class Detection {
        +bbox: Tuple
        +class_name: str
        +confidence: float
        +get_area() int
    }

    class TrafficAnalyzer {
        -congestion_threshold: int
        +analyze(detections) TrafficStats
        +calculate_density(count) float
        +get_traffic_state(density) str
    }

    class EmergencyDetector {
        -confidence_threshold: float
        +detect_emergency(frame) bool
        +check_color_pattern(hsv) bool
    }

    class SignalController {
        -min_green: int
        -max_green: int
        +calculate_timing(traffic) Dict
        +handle_emergency(direction) Dict
    }

    class Camera {
        +camera_id: str
        +direction: str
        +rtsp_url: str
        +connect() bool
        +get_frame() ndarray
    }

    class TrafficData {
        +camera_id: str
        +timestamp: datetime
        +vehicle_counts: Dict
        +save_to_db() void
    }

    class VideoProcessor {
        -detector: VehicleDetector
        -analyzer: TrafficAnalyzer
        +process_video(path) Result
        +process_frame(frame) FrameResult
    }

    class DatabaseService {
        -client: AsyncIOMotorClient
        +insert_traffic_data(data) ObjectId
        +get_camera(camera_id) Camera
        +aggregate_analytics(filters) Dict
    }

    VehicleDetector "1" --> "*" Detection : creates
    VideoProcessor "1" --> "1" VehicleDetector : uses
    VideoProcessor "1" --> "1" TrafficAnalyzer : uses
    VideoProcessor "1" --> "1" EmergencyDetector : uses
    TrafficAnalyzer "1" --> "1" TrafficData : generates
    SignalController "1" --> "*" TrafficData : reads
    Camera "1" --> "*" TrafficData : generates
    VideoProcessor "1" --> "1" DatabaseService : uses
```

---

## 3.6.3 Data Flow Diagram (Level 0 - Context)

```mermaid
flowchart TB
    subgraph External
        C[IP Cameras]
        U[User/Officer]
        S[Traffic Signals]
    end

    subgraph System["Smart Traffic Management System"]
        Core[Traffic Management<br/>Core System]
    end

    C -->|Video Streams| Core
    U -->|Manual Override| Core
    Core -->|Signal Commands| S
    Core -->|Real-time Data| U
    Core -->|Analytics Reports| U
```

---

## 3.6.4 Data Flow Diagram (Level 1 - Detailed)

```mermaid
flowchart LR
    subgraph Input
        CAM[4 IP Cameras]
        VID[Video Upload]
    end

    subgraph Processing
        FE[Frame<br/>Extraction]
        YOLO[YOLOv8<br/>Detection]
    end

    subgraph Intelligence
        TA[Traffic<br/>Analyzer]
        ED[Emergency<br/>Detector]
        SC[Signal<br/>Controller]
    end

    subgraph Storage
        DB[(MongoDB)]
    end

    subgraph Output
        API[FastAPI<br/>Backend]
        WS[WebSocket]
        UI[React<br/>Dashboard]
    end

    CAM --> FE
    VID --> FE
    FE --> YOLO
    YOLO --> TA
    YOLO --> ED
    TA --> SC
    ED --> SC
    SC --> API
    TA --> API
    ED --> API
    API --> DB
    API --> WS
    WS --> UI
```

---

## 3.6.5 Database Schema (MongoDB Collections)

```mermaid
graph TB
    subgraph MongoDB["MongoDB Database: traffic_management"]
        TC[("traffic_data<br/>────────<br/>camera_id<br/>timestamp<br/>vehicle_counts<br/>congestion_level")]
        
        CAM[("cameras<br/>────────<br/>camera_id<br/>direction<br/>rtsp_url<br/>status")]
        
        EM[("emergency_events<br/>────────<br/>event_id<br/>camera_id<br/>confidence<br/>priority_level")]
        
        SIG[("signal_timings<br/>────────<br/>timing_id<br/>mode<br/>signals<br/>cycle_length")]
        
        AN[("analytics<br/>────────<br/>report_id<br/>report_type<br/>aggregated_data")]
        
        VIO[("violations<br/>────────<br/>violation_id<br/>camera_id<br/>vehicle_plate<br/>fine_amount")]
    end

    style TC fill:#E8F5E9
    style CAM fill:#E3F2FD
    style EM fill:#FFF3E0
    style SIG fill:#F3E5F5
    style AN fill:#E0F2F1
    style VIO fill:#FCE4EC
```

---

## 3.6.6 System Component Diagram

```mermaid
graph TD
    subgraph Frontend["Frontend Layer"]
        R[React App<br/>Port: 5173]
    end

    subgraph Backend["Backend Layer"]
        FA[FastAPI Server<br/>Port: 8000]
        WS[WebSocket<br/>Manager]
    end

    subgraph ML["ML/AI Layer"]
        Y[YOLOv8<br/>Detector]
        TA[Traffic<br/>Analyzer]
        ED[Emergency<br/>Detector]
    end

    subgraph Data["Data Layer"]
        M[(MongoDB<br/>Port: 27017)]
        F[File Storage<br/>videos/outputs/]
    end

    R <-->|HTTP/WS| FA
    FA <--> WS
    FA --> Y
    Y --> TA
    Y --> ED
    FA <--> M
    FA <--> F

    style R fill:#E3F2FD
    style FA fill:#E8F5E9
    style Y fill:#FFE0B2
    style M fill:#F3E5F5
```

---

## 3.6.7 Emergency Priority Flow

```mermaid
sequenceDiagram
    participant C as Camera
    participant Y as YOLOv8
    participant ED as Emergency Detector
    participant SC as Signal Controller
    participant DB as MongoDB
    participant UI as Dashboard

    C->>Y: Video Frame
    Y->>ED: Vehicle Detections
    ED->>ED: Check Color Pattern<br/>(White + Red/Blue)
    alt Emergency Detected
        ED->>SC: Emergency Override<br/>Priority: Critical
        SC->>SC: Calculate Green Time<br/>(60s for emergency dir)
        SC->>DB: Save Signal Timing
        SC->>UI: Broadcast Signal Update
        ED->>DB: Save Emergency Event
        ED->>UI: Alert Notification
        Note over SC,UI: Response Time < 3 sec
    else Normal Traffic
        ED->>SC: Normal Traffic Data
        SC->>SC: Adaptive Algorithm<br/>Green = (Count/Total) × Max
        SC->>DB: Save Signal Timing
    end
```

---

## 3.6.8 MongoDB Schema Validation Structure

```mermaid
graph LR
    subgraph Schema["Schema Validation Rules"]
        direction TB
        
        subgraph TC[traffic_data]
            TC1[Required:<br/>camera_id, timestamp,<br/>vehicle_counts]
            TC2[Constraints:<br/>congestion_level: 0-100<br/>traffic_state: enum]
        end
        
        subgraph EM[emergency_events]
            EM1[Required:<br/>event_id, camera_id,<br/>confidence]
            EM2[Constraints:<br/>confidence: 0-1<br/>priority_level: 1-5]
        end
        
        subgraph CAM[cameras]
            CAM1[Required:<br/>camera_id, direction,<br/>rtsp_url]
            CAM2[Constraints:<br/>direction: enum<br/>fps: 1-60]
        end
    end

    style TC fill:#E8F5E9
    style EM fill:#FFF3E0
    style CAM fill:#E3F2FD
```

---

## How to Use These Diagrams

### For Presentations:
1. **ER Diagram (3.6.1)** - Shows database relationships
2. **Class Diagram (3.6.2)** - Shows code architecture
3. **DFD Level 0 (3.6.3)** - Shows system context
4. **DFD Level 1 (3.6.4)** - Shows internal data flow

### For Documentation:
1. **Component Diagram (3.6.6)** - System layers overview
2. **Emergency Flow (3.6.7)** - Critical feature explanation
3. **Schema Validation (3.6.8)** - Database constraints

### For Development:
1. **Class Diagram** - Implementation reference
2. **MongoDB Collections (3.6.5)** - Database structure

### Rendering Options:
- **Online**: [Mermaid Live Editor](https://mermaid.live)
- **VS Code**: Install "Markdown Preview Mermaid Support" extension
- **GitHub**: Renders natively in markdown files
- **Documentation**: GitBook, Docusaurus support Mermaid

### Export:
```bash
# Using Mermaid CLI
npm install -g @mermaid-js/mermaid-cli
mmdc -i DATA_DESIGN_MERMAID.md -o diagrams.pdf
```
