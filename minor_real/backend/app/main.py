"""
FastAPI Application - Traffic Management System
Main entry point for the backend API
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import json
import asyncio
from typing import List

from .config import get_settings
from .database import Database
from .routers import traffic, signals, analytics, violations, cameras
from .routers import settings as settings_router
from .ml.detector import VehicleDetector
from .ml.traffic_analyzer import TrafficAnalyzer
from .ml.signal_controller import SignalController
from .ml.video_processor import VideoProcessor
from .ml.emergency_priority import EmergencyPrioritySystem

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()

# Initialize ML components (will be set up on startup)
detector = None
analyzer = None
signal_controller = None
video_processor = None
emergency_system = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    global detector, analyzer, signal_controller, video_processor
    
    # Startup
    logger.info("Starting Traffic Management System API...")
    
    # Connect to MongoDB
    await Database.connect_db()
    logger.info("✓ MongoDB connected")
    
    # Initialize ML components
    try:
        logger.info("Initializing ML components...")
        
        # Vehicle detector
        detector = VehicleDetector(
            model_path=settings.YOLO_MODEL_PATH,
            confidence=settings.YOLO_CONFIDENCE,
            detect_emergency=True
        )
        logger.info("✓ Vehicle Detector initialized")
        
        # Traffic analyzer
        analyzer = TrafficAnalyzer(history_size=30)
        logger.info("✓ Traffic Analyzer initialized")
        
        # Signal controller
        signal_controller = SignalController(
            min_green_time=settings.MIN_GREEN_TIME,
            max_green_time=settings.MAX_GREEN_TIME,
            default_green_time=settings.DEFAULT_GREEN_TIME
        )
        logger.info("✓ Signal Controller initialized")
        
        # Video processor
        video_processor = VideoProcessor(
            detector=detector,
            analyzer=analyzer,
            output_path=settings.VIDEO_OUTPUT_PATH
        )
        logger.info("✓ Video Processor initialized")
        
        # Emergency priority system
        emergency_system = EmergencyPrioritySystem(
            signal_controller=signal_controller,
            priority_duration=60,
            clear_time=10
        )
        logger.info("✓ Emergency Priority System initialized")
        
        # Set global instances for routers
        traffic.detector = detector
        traffic.analyzer = analyzer
        traffic.video_processor = video_processor
        traffic.emergency_system = emergency_system
        
        logger.info("✓ Application started successfully")
        logger.info("=" * 60)
        logger.info("🚦 Traffic Management System Ready")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Failed to initialize ML components: {e}")
        logger.warning("API will run in limited mode without ML features")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    await Database.close_db()
    logger.info("Application shutdown complete")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Real-time traffic management and monitoring system",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:5175", "http://localhost:5176", "http://localhost:3000"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(traffic.router, prefix=f"{settings.API_V1_PREFIX}/traffic", tags=["Traffic"])
app.include_router(signals.router, prefix=f"{settings.API_V1_PREFIX}/signals", tags=["Signals"])
app.include_router(analytics.router, prefix=f"{settings.API_V1_PREFIX}/analytics", tags=["Analytics"])
app.include_router(violations.router, prefix=f"{settings.API_V1_PREFIX}/violations", tags=["Violations"])
app.include_router(cameras.router, prefix=f"{settings.API_V1_PREFIX}/cameras", tags=["Cameras"])
app.include_router(settings_router.router, tags=["Settings"])


@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "Traffic Management System API",
        "version": settings.APP_VERSION,
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to client: {e}")
    
    async def broadcast_json(self, message: dict):
        """Alias for broadcast method"""
        await self.broadcast(message)


manager = ConnectionManager()


@app.websocket("/ws/live-feed")
async def websocket_live_feed(websocket: WebSocket):
    """
    WebSocket endpoint for live traffic detection data
    Sends real-time updates to connected clients
    """
    await manager.connect(websocket)
    try:
        # Send initial connection success
        await websocket.send_json({
            "type": "connection",
            "status": "connected",
            "message": "Live feed connected"
        })
        
        # Keep connection alive and listen for messages
        while True:
            # Wait for client messages (ping/pong)
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                # Echo back to confirm connection is alive
                await websocket.send_json({"type": "pong", "received": data})
            except asyncio.TimeoutError:
                # Send ping to keep connection alive
                await websocket.send_json({"type": "ping"})
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


async def broadcast_live_detection(camera_id: str, detection_data: dict):
    """
    Broadcast live detection data to all WebSocket clients
    Called from camera stream processing
    """
    message = {
        "type": "live_detection",
        "camera_id": camera_id,
        "timestamp": detection_data.get("timestamp"),
        "data": detection_data
    }
    await manager.broadcast(message)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
