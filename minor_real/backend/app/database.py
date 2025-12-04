"""
MongoDB database connection and operations
"""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure
from .config import get_settings
import logging

logger = logging.getLogger(__name__)

settings = get_settings()


class Database:
    """MongoDB database manager"""
    
    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None
    
    @classmethod
    async def connect_db(cls):
        """Connect to MongoDB database"""
        try:
            # Add timeout settings
            cls.client = AsyncIOMotorClient(
                settings.MONGODB_URL,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000,
                socketTimeoutMS=10000
            )
            # Test connection with timeout
            await cls.client.admin.command('ping')
            cls.db = cls.client[settings.MONGODB_DB_NAME]
            logger.info(f"✓ Connected to MongoDB: {settings.MONGODB_DB_NAME}")
        except Exception as e:
            logger.warning(f"MongoDB connection failed: {e}")
            logger.warning("Running in limited mode without database")
            # Don't raise - allow app to start without DB
            cls.db = None
    
    @classmethod
    async def close_db(cls):
        """Close MongoDB connection"""
        if cls.client:
            cls.client.close()
            logger.info("Closed MongoDB connection")
    
    @classmethod
    def get_database(cls) -> AsyncIOMotorDatabase:
        """Get database instance"""
        if cls.db is None:
            logger.warning("Database not available - running in limited mode")
            return None
        return cls.db


# Collections
async def get_traffic_collection():
    """Get traffic data collection"""
    db = Database.get_database()
    return db.traffic_data


async def get_violations_collection():
    """Get violations collection"""
    db = Database.get_database()
    return db.violations


async def get_signals_collection():
    """Get signals collection"""
    db = Database.get_database()
    return db.signals


async def get_analytics_collection():
    """Get analytics collection"""
    db = Database.get_database()
    return db.analytics
