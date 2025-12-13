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
            if self._matches_filter(doc, filter_dict):
                return doc
        return None
    
    def find(self, filter_dict: Dict[str, Any] = None, sort: List = None, limit: int = 0):
        """Find documents matching filter"""
        results = self.data.copy()
        
        # Apply filter
        if filter_dict:
            results = [
                doc for doc in results
                if self._matches_filter(doc, filter_dict)
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
            if self._matches_filter(doc, filter_dict):
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
            if self._matches_filter(doc, filter_dict):
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
    
    async def delete_many(self, filter_dict: Dict[str, Any] = None) -> Any:
        """Delete multiple documents matching filter"""
        if filter_dict is None or not filter_dict:
            # Delete all documents if no filter
            deleted_count = len(self.data)
            self.data = []
            logger.info(f"MockDB: Deleted all {deleted_count} documents from {self.name}")
        else:
            # Delete matching documents
            original_count = len(self.data)
            self.data = [doc for doc in self.data if not self._matches_filter(doc, filter_dict)]
            deleted_count = original_count - len(self.data)
            logger.info(f"MockDB: Deleted {deleted_count} documents from {self.name}")
        
        class DeleteResult:
            def __init__(self, count):
                self.deleted_count = count
        
        return DeleteResult(deleted_count)
    
    async def count_documents(self, filter_dict: Dict[str, Any] = None) -> int:
        """Count documents matching filter"""
        if not filter_dict:
            return len(self.data)
        
        count = sum(
            1 for doc in self.data
            if self._matches_filter(doc, filter_dict)
        )
        return count
    
    def aggregate(self, pipeline: List[Dict[str, Any]]):
        """Execute aggregation pipeline (simplified for mock)"""
        results = self.data.copy()
        
        for stage in pipeline:
            if "$match" in stage:
                # Filter documents
                match_filter = stage["$match"]
                results = [doc for doc in results if self._matches_filter(doc, match_filter)]
            
            elif "$group" in stage:
                # Group and aggregate
                group_spec = stage["$group"]
                group_id = group_spec.get("_id")
                
                # Simple grouping implementation
                grouped = {}
                for doc in results:
                    # Create group key
                    if group_id is None:
                        key = None
                    elif isinstance(group_id, str) and group_id.startswith("$"):
                        key = doc.get(group_id[1:])
                    elif isinstance(group_id, dict):
                        # Complex grouping (e.g., by hour)
                        key = str(group_id)  # Simplified
                    else:
                        key = group_id
                    
                    if key not in grouped:
                        grouped[key] = []
                    grouped[key].append(doc)
                
                # Apply aggregation functions
                results = []
                for key, docs in grouped.items():
                    result_doc = {"_id": key}
                    
                    for field, operation in group_spec.items():
                        if field == "_id":
                            continue
                        
                        if isinstance(operation, dict):
                            op_name = list(operation.keys())[0]
                            op_field = operation[op_name]
                            
                            # Handle both string field references and integer literals
                            if isinstance(op_field, str) and op_field.startswith("$"):
                                field_name = op_field[1:]
                                values = [d.get(field_name, 0) for d in docs]
                            elif isinstance(op_field, (int, float)):
                                # For literal values like {"$sum": 1}
                                values = [op_field for _ in docs]
                            else:
                                values = docs
                            
                            if op_name == "$sum":
                                result_doc[field] = sum(values) if values else 0
                            elif op_name == "$avg":
                                result_doc[field] = sum(values) / len(values) if values else 0
                            elif op_name == "$addToSet":
                                result_doc[field] = list(set(values))
                            elif op_name == "$max":
                                result_doc[field] = max(values) if values else 0
                            elif op_name == "$min":
                                result_doc[field] = min(values) if values else 0
                    
                    results.append(result_doc)
            
            elif "$sort" in stage:
                # Sort results
                sort_spec = stage["$sort"]
                for field, direction in sorted(sort_spec.items(), reverse=True):
                    results.sort(
                        key=lambda x: x.get(field, 0),
                        reverse=(direction == -1)
                    )
            
            elif "$limit" in stage:
                # Limit results
                limit = stage["$limit"]
                results = results[:limit]
        
        return MockCursor(results)
    
    def _matches_filter(self, doc: Dict[str, Any], filter_dict: Dict[str, Any]) -> bool:
        """Check if document matches filter (supports comparison operators)"""
        from datetime import datetime, timezone
        
        for key, value in filter_dict.items():
            if isinstance(value, dict):
                # Handle operators like $gte, $lte, etc.
                doc_value = doc.get(key)
                for op, op_value in value.items():
                    # Convert timezone-naive datetimes to UTC for comparison
                    if isinstance(doc_value, datetime) and isinstance(op_value, datetime):
                        if doc_value.tzinfo is None:
                            doc_value = doc_value.replace(tzinfo=timezone.utc)
                        if op_value.tzinfo is None:
                            op_value = op_value.replace(tzinfo=timezone.utc)
                    
                    if op == "$gte" and not (doc_value >= op_value):
                        return False
                    elif op == "$lte" and not (doc_value <= op_value):
                        return False
                    elif op == "$gt" and not (doc_value > op_value):
                        return False
                    elif op == "$lt" and not (doc_value < op_value):
                        return False
                    elif op == "$ne" and doc_value == op_value:
                        return False
                    elif op == "$in" and doc_value not in op_value:
                        return False
            else:
                # Direct comparison
                if doc.get(key) != value:
                    return False
        return True


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
    """Populate database with minimal configuration - no demo data"""
    
    # Only create basic cameras - no historical data
    cameras = [
        {
            "camera_id": "CAM001",
            "location_id": "location_1",
            "location_name": "Main Junction - North",
            "name": "Camera 1",
            "rtsp_url": "rtsp://camera1.local/stream",
            "latitude": 12.9716,
            "longitude": 77.5946,
            "status": "active",
            "created_at": datetime.utcnow()
        },
        {
            "camera_id": "CAM002",
            "location_id": "location_2",
            "location_name": "Main Junction - South",
            "name": "Camera 2",
            "rtsp_url": "rtsp://camera2.local/stream",
            "latitude": 12.9177,
            "longitude": 77.6238,
            "status": "active",
            "created_at": datetime.utcnow()
        }
    ]
    
    cameras_collection = db["cameras"]
    if await cameras_collection.count_documents({}) == 0:
        await cameras_collection.insert_many(cameras)
        logger.info("MockDB: Populated sample cameras")
    
    # Basic system settings only
    settings = {
        "system_mode": "adaptive",
        "confidence_threshold": 0.18,
        "frame_skip": 3,
        "emergency_priority_enabled": True,
        "analytics_enabled": True,
        "last_updated": datetime.utcnow()
    }
    
    settings_collection = db["settings"]
    if await settings_collection.count_documents({}) == 0:
        await settings_collection.insert_one(settings)
        logger.info("MockDB: Populated sample settings")
