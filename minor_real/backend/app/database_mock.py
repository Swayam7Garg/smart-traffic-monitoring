"""
Mock Database for Testing/Demo Deployment
Provides in-memory storage when MongoDB is not available
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class MockCollection:
    """Mock MongoDB collection with in-memory storage"""
    
    def __init__(self, name: str):
        self.name = name
        self.data: List[Dict[str, Any]] = []
        self._id_counter = 1
    
    async def insert_one(self, document: Dict[str, Any]) -> Any:
        """Insert a document"""
        doc = document.copy()
        if "_id" not in doc:
            doc["_id"] = f"mock_{self.name}_{self._id_counter}"
            self._id_counter += 1
        
        if "timestamp" not in doc:
            doc["timestamp"] = datetime.now()
        
        self.data.append(doc)
        logger.debug(f"MockDB: Inserted into {self.name}: {doc.get('_id')}")
        
        class InsertResult:
            def __init__(self, inserted_id):
                self.inserted_id = inserted_id
        
        return InsertResult(doc["_id"])
    
    async def insert_many(self, documents: List[Dict[str, Any]]) -> Any:
        """Insert multiple documents"""
        inserted_ids = []
        for doc in documents:
            result = await self.insert_one(doc)
            inserted_ids.append(result.inserted_id)
        
        class InsertManyResult:
            def __init__(self, ids):
                self.inserted_ids = ids
        
        return InsertManyResult(inserted_ids)
    
    async def find_one(self, filter_dict: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Find one document matching filter"""
        if not filter_dict:
            return self.data[0] if self.data else None
        
        for doc in self.data:
            match = all(doc.get(k) == v for k, v in filter_dict.items())
            if match:
                return doc
        return None
    
    def find(self, filter_dict: Dict[str, Any] = None, sort: List = None, limit: int = 0):
        """Find documents matching filter"""
        results = self.data.copy()
        
        # Apply filter
        if filter_dict:
            results = [
                doc for doc in results
                if all(doc.get(k) == v for k, v in filter_dict.items())
            ]
        
        # Apply sort
        if sort:
            for field, direction in reversed(sort):
                results.sort(
                    key=lambda x: x.get(field, ""),
                    reverse=(direction == -1)
                )
        
        # Apply limit
        if limit > 0:
            results = results[:limit]
        
        return MockCursor(results)
    
    async def update_one(self, filter_dict: Dict[str, Any], update: Dict[str, Any]) -> Any:
        """Update one document"""
        for doc in self.data:
            match = all(doc.get(k) == v for k, v in filter_dict.items())
            if match:
                if "$set" in update:
                    doc.update(update["$set"])
                elif "$inc" in update:
                    for key, value in update["$inc"].items():
                        doc[key] = doc.get(key, 0) + value
                
                logger.debug(f"MockDB: Updated in {self.name}: {doc.get('_id')}")
                
                class UpdateResult:
                    def __init__(self, matched, modified):
                        self.matched_count = matched
                        self.modified_count = modified
                
                return UpdateResult(1, 1)
        
        class UpdateResult:
            def __init__(self, matched, modified):
                self.matched_count = matched
                self.modified_count = modified
        
        return UpdateResult(0, 0)
    
    async def delete_one(self, filter_dict: Dict[str, Any]) -> Any:
        """Delete one document"""
        for i, doc in enumerate(self.data):
            match = all(doc.get(k) == v for k, v in filter_dict.items())
            if match:
                del self.data[i]
                logger.debug(f"MockDB: Deleted from {self.name}: {doc.get('_id')}")
                
                class DeleteResult:
                    def __init__(self, count):
                        self.deleted_count = count
                
                return DeleteResult(1)
        
        class DeleteResult:
            def __init__(self, count):
                self.deleted_count = count
        
        return DeleteResult(0)
    
    async def count_documents(self, filter_dict: Dict[str, Any] = None) -> int:
        """Count documents matching filter"""
        if not filter_dict:
            return len(self.data)
        
        count = sum(
            1 for doc in self.data
            if all(doc.get(k) == v for k, v in filter_dict.items())
        )
        return count


class MockCursor:
    """Mock MongoDB cursor for iteration"""
    
    def __init__(self, data: List[Dict[str, Any]]):
        self.data = data
        self.index = 0
    
    def __aiter__(self):
        return self
    
    async def __anext__(self):
        if self.index >= len(self.data):
            raise StopAsyncIteration
        item = self.data[self.index]
        self.index += 1
        return item
    
    async def to_list(self, length: Optional[int] = None) -> List[Dict[str, Any]]:
        """Convert cursor to list"""
        if length is None:
            return self.data
        return self.data[:length]
    
    def sort(self, field: str, direction: int = 1):
        """Sort results"""
        self.data.sort(
            key=lambda x: x.get(field, ""),
            reverse=(direction == -1)
        )
        return self
    
    def limit(self, count: int):
        """Limit results"""
        self.data = self.data[:count]
        return self


class MockDatabase:
    """
    Mock database for testing without MongoDB
    Provides same interface as Motor AsyncIOMotorDatabase
    """
    
    def __init__(self, name: str = "mock_traffic_management"):
        self.name = name
        self.collections: Dict[str, MockCollection] = {}
        logger.info(f"✓ Mock Database initialized: {name}")
    
    def __getitem__(self, collection_name: str) -> MockCollection:
        """Get or create collection"""
        if collection_name not in self.collections:
            self.collections[collection_name] = MockCollection(collection_name)
            logger.debug(f"MockDB: Created collection '{collection_name}'")
        return self.collections[collection_name]
    
    def __getattr__(self, collection_name: str) -> MockCollection:
        """Get or create collection via attribute access (e.g., db.my_collection)"""
        if collection_name.startswith('_'):
            # Avoid infinite recursion for private attributes
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{collection_name}'")
        return self[collection_name]
    
    def get_collection(self, collection_name: str) -> MockCollection:
        """Get or create collection (alternative method)"""
        return self[collection_name]
    
    async def list_collection_names(self) -> List[str]:
        """List all collection names"""
        return list(self.collections.keys())
    
    async def drop_collection(self, collection_name: str):
        """Drop a collection"""
        if collection_name in self.collections:
            del self.collections[collection_name]
            logger.info(f"MockDB: Dropped collection '{collection_name}'")


class MockClient:
    """Mock MongoDB client"""
    
    def __init__(self, uri: str = None):
        self.databases: Dict[str, MockDatabase] = {}
        logger.info("✓ Mock MongoDB Client initialized (in-memory mode)")
    
    def __getitem__(self, db_name: str) -> MockDatabase:
        """Get or create database"""
        if db_name not in self.databases:
            self.databases[db_name] = MockDatabase(db_name)
        return self.databases[db_name]
    
    async def server_info(self) -> Dict[str, Any]:
        """Return mock server info"""
        return {
            "version": "mock-1.0.0",
            "ok": 1,
            "mode": "in-memory"
        }
    
    def close(self):
        """Close connection (no-op for mock)"""
        logger.info("MockDB: Connection closed")


async def get_mock_database(db_name: str = "traffic_management") -> MockDatabase:
    """
    Get mock database instance
    
    Args:
        db_name: Database name
        
    Returns:
        MockDatabase instance
    """
    client = MockClient()
    db = client[db_name]
    
    # Pre-populate with some sample data
    await _populate_sample_data(db)
    
    return db


async def _populate_sample_data(db: MockDatabase):
    """Populate database with sample data for demo"""
    
    # Sample cameras
    cameras = [
        {
            "camera_id": "CAM001",
            "location": "North Junction",
            "latitude": 22.7196,
            "longitude": 75.8577,
            "status": "active",
            "stream_url": "rtsp://demo-camera-1",
            "direction": "north"
        },
        {
            "camera_id": "CAM002",
            "location": "South Junction",
            "latitude": 22.7186,
            "longitude": 75.8577,
            "status": "active",
            "stream_url": "rtsp://demo-camera-2",
            "direction": "south"
        },
        {
            "camera_id": "CAM003",
            "location": "East Junction",
            "latitude": 22.7196,
            "longitude": 75.8587,
            "status": "active",
            "stream_url": "rtsp://demo-camera-3",
            "direction": "east"
        },
        {
            "camera_id": "CAM004",
            "location": "West Junction",
            "latitude": 22.7196,
            "longitude": 75.8567,
            "status": "active",
            "stream_url": "rtsp://demo-camera-4",
            "direction": "west"
        }
    ]
    
    cameras_collection = db["cameras"]
    if await cameras_collection.count_documents({}) == 0:
        await cameras_collection.insert_many(cameras)
        logger.info("MockDB: Populated sample cameras")
    
    # Sample settings
    settings = {
        "system_name": "Traffic Management System",
        "min_green_time": 15,
        "max_green_time": 120,
        "default_green_time": 30,
        "congestion_threshold": 20,
        "emergency_priority": True,
        "auto_adapt_signals": True
    }
    
    settings_collection = db["settings"]
    if await settings_collection.count_documents({}) == 0:
        await settings_collection.insert_one(settings)
        logger.info("MockDB: Populated sample settings")
