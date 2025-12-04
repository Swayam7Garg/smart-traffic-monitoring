"""
Configuration management for the Traffic Management System
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = "Traffic Management System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    
    # MongoDB
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "traffic_management"
    USE_MOCK_DB: bool = False  # Set to True to use in-memory database (no MongoDB required)
    
    # YOLO Model
    YOLO_MODEL_PATH: str = "../data/models/yolov8n.pt"
    YOLO_CONFIDENCE: float = 0.15  # Lowered to 0.15 for better bike/scooter/auto detection
    
    # Video Processing
    VIDEO_INPUT_PATH: str = "../data/videos"
    VIDEO_OUTPUT_PATH: str = "../data/outputs"
    FRAME_SKIP: int = 2  # Process every Nth frame
    
    # Traffic Signal Simulation
    MIN_GREEN_TIME: int = 15  # seconds
    MAX_GREEN_TIME: int = 120  # seconds
    DEFAULT_GREEN_TIME: int = 30  # seconds
    
    # Alerts
    CONGESTION_THRESHOLD: int = 20  # vehicles
    VIOLATION_THRESHOLD: int = 5  # violations per minute
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS (Comma-separated list of allowed origins)
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:5174,http://localhost:3000"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    def get_allowed_origins(self) -> list[str]:
        """Parse ALLOWED_ORIGINS string into list"""
        if self.ALLOWED_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
