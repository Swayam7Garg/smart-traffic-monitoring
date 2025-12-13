"""
Seed database with realistic demo data for presentation
Run this script to populate MongoDB with sample traffic data
"""

import asyncio
from datetime import datetime, timedelta
import random
from motor.motor_asyncio import AsyncIOMotorClient

# MongoDB connection
MONGODB_URL = "mongodb://localhost:27017"
DB_NAME = "traffic_management"


async def seed_database():
    """Populate database with realistic demo data"""
    
    print("🌱 Seeding database with demo data...")
    
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient(MONGODB_URL)
        await client.admin.command('ping')
        db = client[DB_NAME]
        print(f"✓ Connected to MongoDB: {DB_NAME}")
        
        # Clear existing data
        await db.traffic_data.delete_many({})
        await db.video_processing_jobs.delete_many({})
        await db.vehicle_detections.delete_many({})
        await db.violations.delete_many({})
        await db.cameras.delete_many({})
        await db.signals.delete_many({})
        await db.settings.delete_many({})
        print("✓ Cleared existing data")
        
        # Seed cameras
        cameras = [
            {
                "camera_id": "CAM001",
                "location_id": "MG_Road_Intersection",
                "name": "MG Road - Brigade Road Junction",
                "location_name": "MG Road Junction",
                "latitude": 12.9716,
                "longitude": 77.5946,
                "status": "active",
                "rtsp_url": "rtsp://camera1.local/stream",
                "is_streaming": false,
                "created_at": datetime.utcnow()
            },
            {
                "camera_id": "CAM002",
                "location_id": "Silk_Board_Junction",
                "name": "Silk Board Junction",
                "location_name": "Silk Board",
                "latitude": 12.9177,
                "longitude": 77.6238,
                "status": "active",
                "rtsp_url": "rtsp://camera2.local/stream",
                "is_streaming": false,
                "created_at": datetime.utcnow()
            },
            {
                "camera_id": "CAM003",
                "location_id": "Hebbal_Flyover",
                "name": "Hebbal Flyover",
                "location_name": "Hebbal",
                "latitude": 13.0358,
                "longitude": 77.5970,
                "status": "active",
                "rtsp_url": "rtsp://camera3.local/stream",
                "is_streaming": false,
                "created_at": datetime.utcnow()
            },
            {
                "camera_id": "CAM004",
                "location_id": "Koramangala_Signal",
                "name": "Koramangala 80 Feet Road",
                "location_name": "Koramangala",
                "latitude": 12.9352,
                "longitude": 77.6245,
                "status": "active",
                "rtsp_url": "rtsp://camera4.local/stream",
                "is_streaming": false,
                "created_at": datetime.utcnow()
            }
        ]
        await db.cameras.insert_many(cameras)
        print(f"✓ Seeded {len(cameras)} cameras")
        
        # Seed traffic signals
        signals = [
            {
                "signal_id": "SIG001",
                "location_id": "MG_Road_Intersection",
                "name": "MG Road Signal",
                "current_state": "GREEN",
                "green_time": 60,
                "red_time": 90,
                "yellow_time": 5,
                "last_updated": datetime.utcnow(),
                "adaptive_mode": True
            },
            {
                "signal_id": "SIG002",
                "location_id": "Silk_Board_Junction",
                "name": "Silk Board Signal",
                "current_state": "RED",
                "green_time": 90,
                "red_time": 60,
                "yellow_time": 5,
                "last_updated": datetime.utcnow(),
                "adaptive_mode": True
            },
            {
                "signal_id": "SIG003",
                "location_id": "Hebbal_Flyover",
                "name": "Hebbal Signal",
                "current_state": "GREEN",
                "green_time": 75,
                "red_time": 75,
                "yellow_time": 5,
                "last_updated": datetime.utcnow(),
                "adaptive_mode": True
            }
        ]
        await db.signals.insert_many(signals)
        print(f"✓ Seeded {len(signals)} traffic signals")
        
        # Seed traffic data (last 7 days)
        print("Generating traffic data for last 7 days...")
        traffic_data = []
        locations = ["MG_Road_Intersection", "Silk_Board_Junction", "Hebbal_Flyover", "Koramangala_Signal"]
        
        for days_ago in range(7):
            for hour in range(24):
                for location in locations:
                    timestamp = datetime.utcnow() - timedelta(days=days_ago, hours=23-hour)
                    
                    # Simulate traffic patterns (peak hours: 8-10 AM, 6-9 PM)
                    is_peak = hour in [8, 9, 10, 18, 19, 20, 21]
                    base_vehicles = 45 if is_peak else 25
                    vehicle_count = base_vehicles + random.randint(-10, 15)
                    
                    traffic_data.append({
                        "location_id": location,
                        "timestamp": timestamp,
                        "vehicle_count": vehicle_count,
                        "vehicle_counts": {
                            "car": random.randint(15, 30) if is_peak else random.randint(8, 18),
                            "motorcycle": random.randint(10, 25) if is_peak else random.randint(5, 15),
                            "auto-rickshaw": random.randint(3, 8),
                            "bus": random.randint(2, 5),
                            "truck": random.randint(1, 3)
                        },
                        "congestion_level": random.uniform(60, 85) if is_peak else random.uniform(20, 50),
                        "average_congestion": random.uniform(55, 75) if is_peak else random.uniform(25, 45),
                        "emergency_vehicles": random.randint(0, 1),
                        "source": "video_processing"
                    })
        
        await db.traffic_data.insert_many(traffic_data)
        print(f"✓ Seeded {len(traffic_data)} traffic data records")
        
        # Seed video processing jobs (recent 10)
        print("Creating video processing job history...")
        jobs = []
        for i in range(10):
            days_ago = i // 3
            timestamp = datetime.utcnow() - timedelta(days=days_ago, hours=i*2)
            location = random.choice(locations)
            
            total_vehicles = random.randint(25, 60)
            jobs.append({
                "job_id": f"job_{timestamp.strftime('%Y%m%d%H%M%S')}_{i}",
                "video_path": f"../data/videos/traffic_sample_{i+1}.mp4",
                "location_id": location,
                "status": "completed",
                "processed_at": timestamp,
                "frames": {
                    "total": random.randint(800, 1500),
                    "processed": random.randint(80, 150),
                    "skipped": random.randint(700, 1350)
                },
                "detections": {
                    "total_vehicles": total_vehicles,
                    "total_detections": total_vehicles * random.randint(8, 15),
                    "vehicle_types": {
                        "car": random.randint(10, 25),
                        "motorcycle": random.randint(8, 20),
                        "auto-rickshaw": random.randint(2, 6),
                        "bus": random.randint(1, 4),
                        "truck": random.randint(1, 3)
                    },
                    "avg_per_frame": round(random.uniform(2.5, 5.5), 2),
                    "emergency_vehicles": random.randint(0, 1),
                    "tracking_enabled": True
                },
                "analysis": {
                    "peak_congestion": round(random.uniform(40, 85), 2),
                    "avg_congestion": round(random.uniform(35, 70), 2)
                },
                "emergency_alerts": [],
                "output_video": f"../data/outputs/processed_{location}_{timestamp.strftime('%Y%m%d_%H%M%S')}.mp4"
            })
        
        await db.video_processing_jobs.insert_many(jobs)
        print(f"✓ Seeded {len(jobs)} video processing jobs")
        
        # Seed violations
        print("Creating violation records...")
        violations = []
        violation_types = [
            "Red Light Violation",
            "Speed Violation",
            "Wrong Lane",
            "No Helmet",
            "Triple Riding"
        ]
        
        for i in range(30):
            days_ago = i // 10
            timestamp = datetime.utcnow() - timedelta(days=days_ago, hours=random.randint(0, 23))
            
            violations.append({
                "violation_id": f"VIO{str(i+1).zfill(4)}",
                "location_id": random.choice(locations),
                "timestamp": timestamp,
                "violation_type": random.choice(violation_types),
                "vehicle_type": random.choice(["car", "motorcycle", "auto-rickshaw"]),
                "confidence": round(random.uniform(0.75, 0.95), 2),
                "status": random.choice(["detected", "verified", "processed"]),
                "image_path": f"violations/violation_{i+1}.jpg"
            })
        
        await db.violations.insert_many(violations)
        print(f"✓ Seeded {len(violations)} violations")
        
        # Seed system settings
        settings = {
            "system_mode": "adaptive",
            "confidence_threshold": 0.25,
            "frame_skip": 3,
            "emergency_priority_enabled": True,
            "analytics_enabled": True,
            "last_updated": datetime.utcnow()
        }
        await db.settings.insert_one(settings)
        print("✓ Seeded system settings")
        
        print("\n✅ Database seeding completed successfully!")
        print(f"   📊 Total records:")
        print(f"      - Cameras: {len(cameras)}")
        print(f"      - Signals: {len(signals)}")
        print(f"      - Traffic Data: {len(traffic_data)}")
        print(f"      - Video Jobs: {len(jobs)}")
        print(f"      - Violations: {len(violations)}")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        print(f"   Make sure MongoDB is running on {MONGODB_URL}")


if __name__ == "__main__":
    asyncio.run(seed_database())
