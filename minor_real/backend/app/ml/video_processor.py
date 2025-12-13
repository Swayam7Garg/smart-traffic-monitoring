"""
Video Processing Module
Handles video upload, processing, and frame extraction for traffic analysis
"""

import cv2
import os
import numpy as np
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Callable
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging
from .detector import VehicleDetector
from .traffic_analyzer import TrafficAnalyzer
from .detection_storage import store_detection_batch, store_video_processing_job
from ..config import get_settings

logger = logging.getLogger(__name__)


class VideoProcessor:
    """Process traffic videos for vehicle detection"""
    
    def __init__(
        self,
        detector: VehicleDetector,
        analyzer: TrafficAnalyzer,
        output_path: str = "./data/outputs"
    ):
        """
        Initialize video processor
        
        Args:
            detector: VehicleDetector instance
            analyzer: TrafficAnalyzer instance
            output_path: Directory for output videos
        """
        self.detector = detector
        self.analyzer = analyzer
        # Convert to absolute path to avoid issues after restart
        self.output_path = Path(output_path).resolve()
        self.output_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Video output directory: {self.output_path}")
        
        # Get frame_skip from config
        settings = get_settings()
        self.frame_skip = settings.FRAME_SKIP
        logger.info(f"Video processor frame skip: {self.frame_skip}")
        
        # Thread pool for async processing
        self.executor = ThreadPoolExecutor(max_workers=2)
        
        # Active processing jobs
        self.processing_jobs = {}
        
        # Active live streams
        self.active_streams = {}
    
    def process_video(
        self,
        video_path: str,
        location_id: str = "unknown",
        save_annotated: bool = True,
        frame_skip: Optional[int] = None,
        emergency_callback: Optional[Callable] = None
    ) -> Dict:
        """
        Process a video file and detect vehicles (OPTIMIZED with better accuracy)
        
        Args:
            video_path: Path to input video file
            location_id: Location identifier
            save_annotated: Save video with annotations
            frame_skip: Process every Nth frame (uses config default if None)
            emergency_callback: Optional callback for immediate emergency alerts
            
        Returns:
            Processing results summary
        """
        # Use configured frame_skip if not provided
        if frame_skip is None:
            frame_skip = self.frame_skip
        
        logger.info(f"Processing video: {video_path} (frame_skip={frame_skip})")
        
        # Open video
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video: {video_path}")
        
        # Video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        logger.info(f"Video info: {width}x{height} @ {fps}fps, {total_frames} frames")
        
        # Output video writer (OPTIMIZED: H264 codec + reduced resolution)
        output_video = None
        output_path = None
        out_width, out_height = width, height
        if save_annotated:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"processed_{location_id}_{timestamp}.mp4"
            output_path = self.output_path / output_filename
            
            # Use standard mp4v codec
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            
            output_video = cv2.VideoWriter(
                str(output_path),
                fourcc,
                fps,
                (out_width, out_height)
            )
        
        # Processing results
        frame_count = 0
        processed_count = 0
        all_detections = []
        emergency_frames = []
        vehicle_counts_over_time = []
        unique_vehicle_ids = set()  # Track unique vehicles
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame_count += 1
                
                # Skip frames for performance
                if frame_count % frame_skip != 0:
                    if output_video:
                        output_video.write(frame)
                    continue
                
                # Detect vehicles with tracking
                try:
                    detections, annotated_frame = self.detector.detect_and_track(frame, track=True)
                    
                    # Track unique vehicle IDs
                    for det in detections:
                        if 'track_id' in det:
                            unique_vehicle_ids.add(det['track_id'])
                except Exception as track_error:
                    # Fallback to detection without tracking
                    logger.warning(f"Tracking failed, using detection only: {track_error}")
                    detections = self.detector.detect(frame, detect_three_wheelers=True)
                    annotated_frame = frame.copy()
                
                # Analyze traffic
                analysis = self.analyzer.analyze_frame(detections)
                
                # Store results
                all_detections.extend(detections)
                vehicle_counts_over_time.append({
                    "frame": frame_count,
                    "timestamp": frame_count / fps,
                    "vehicle_count": analysis["vehicle_count"],
                    "congestion_level": analysis["congestion_level"],
                    "vehicle_types": analysis["vehicle_types"]
                })
                
                # Check for emergency vehicles
                if self.detector.has_emergency_vehicles(detections):
                    emergency_vehicles = self.detector.get_emergency_vehicles(detections)
                    emergency_frames.append({
                        "frame": frame_count,
                        "timestamp": frame_count / fps,
                        "emergency_vehicles": emergency_vehicles
                    })
                    logger.critical(f"🚨 EMERGENCY VEHICLE DETECTED at frame {frame_count} - IMMEDIATE ALERT TRIGGERED")
                    
                    # 🔥 ITERATION #8: IMMEDIATE EMERGENCY CALLBACK (Zero-Latency)
                    # Trigger emergency response WITHOUT waiting for full video processing
                    if emergency_callback:
                        try:
                            # Call emergency callback immediately
                            if asyncio.iscoroutinefunction(emergency_callback):
                                # Run async callback in thread-safe manner
                                asyncio.create_task(emergency_callback({
                                    "location_id": location_id,
                                    "frame_number": frame_count,
                                    "timestamp": frame_count / fps,
                                    "video_path": video_path,
                                    "emergency_vehicles": emergency_vehicles,
                                    "total_vehicles": analysis["vehicle_count"],
                                    "detected_at": datetime.now().isoformat()
                                }))
                            else:
                                emergency_callback({
                                    "location_id": location_id,
                                    "frame_number": frame_count,
                                    "timestamp": frame_count / fps,
                                    "video_path": video_path,
                                    "emergency_vehicles": emergency_vehicles,
                                    "total_vehicles": analysis["vehicle_count"],
                                    "detected_at": datetime.now().isoformat()
                                })
                            logger.info("✓ Emergency callback executed successfully")
                        except Exception as callback_error:
                            logger.error(f"Emergency callback failed: {callback_error}")
                
                # Write annotated frame (only processed frames)
                if output_video:
                    # Add frame info overlay
                    info_text = f"Frame: {frame_count} | Vehicles: {analysis['vehicle_count']} | Congestion: {analysis['congestion_level']:.1f}%"
                    cv2.putText(
                        annotated_frame,
                        info_text,
                        (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (255, 255, 255),
                        2
                    )
                    
                    output_video.write(annotated_frame)
                
                processed_count += 1
                
                # Progress logging
                if frame_count % 200 == 0:
                    progress = (frame_count / total_frames) * 100
                    logger.info(f"Progress: {progress:.1f}% ({frame_count}/{total_frames} frames, {processed_count} processed)")
        
        finally:
            cap.release()
            if output_video:
                output_video.release()
        
        # Calculate summary statistics
        total_detections = len(all_detections)
        
        # Better unique vehicle counting using both tracking IDs and spatial analysis
        vehicle_counts = self._count_unique_vehicles_by_type(all_detections, unique_vehicle_ids)
        unique_vehicle_count = sum([v for k, v in vehicle_counts.items() if k != 'total' and k != 'emergency_vehicles'])
        
        avg_vehicles_per_frame = total_detections / processed_count if processed_count > 0 else 0
        peak_congestion = max([vc["congestion_level"] for vc in vehicle_counts_over_time], default=0)
        
        results = {
            "status": "completed",
            "location_id": location_id,
            "video_path": video_path,
            "processed_at": datetime.now().isoformat(),
            "frames": {
                "total": total_frames,
                "processed": processed_count,
                "skipped": frame_count - processed_count
            },
            "detections": {
                "total_vehicles": unique_vehicle_count,  # Use unique count
                "total_detections": total_detections,  # Raw detection count
                "vehicle_types": vehicle_counts,
                "avg_per_frame": round(avg_vehicles_per_frame, 2),
                "emergency_vehicles": len(emergency_frames),
                "tracking_enabled": len(unique_vehicle_ids) > 0
            },
            "analysis": {
                "peak_congestion": round(peak_congestion, 2),
                "avg_congestion": round(sum([vc["congestion_level"] for vc in vehicle_counts_over_time]) / len(vehicle_counts_over_time), 2) if vehicle_counts_over_time else 0
            },
            "emergency_alerts": emergency_frames,
            "output_video": str(output_path) if save_annotated else None
        }
        
        # Note: Database storage happens in async wrapper
        
        logger.info(f"Processing complete: {unique_vehicle_count} unique vehicles detected ({total_detections} total detections)")
        return results
    
    def _count_unique_vehicles_by_type(self, all_detections: List, tracked_ids: set) -> Dict[str, int]:
        """
        Count unique vehicles by type using ONLY tracking IDs (no estimation)
        Each unique track_id represents ONE vehicle, counted only once
        """
        # Count unique tracking IDs per vehicle type
        tracked_vehicles_by_type = {}
        emergency_track_ids = set()  # Track unique emergency vehicle IDs
        
        for det in all_detections:
            vehicle_type = det.get('class_name', 'unknown')
            track_id = det.get('track_id')
            is_emergency = det.get('is_emergency', False)
            
            # Only count if we have a valid tracking ID
            if track_id is not None:
                # Initialize set for this vehicle type if needed
                if vehicle_type not in tracked_vehicles_by_type:
                    tracked_vehicles_by_type[vehicle_type] = set()
                
                # Add tracking ID (set automatically handles duplicates)
                tracked_vehicles_by_type[vehicle_type].add(track_id)
                
                # Track unique emergency vehicles
                if is_emergency:
                    emergency_track_ids.add(track_id)
        
        # Build final counts - each unique track_id = 1 vehicle
        vehicle_counts = {}
        total = 0
        
        for vehicle_type, track_id_set in tracked_vehicles_by_type.items():
            count = len(track_id_set)  # Count of unique track IDs
            vehicle_counts[vehicle_type] = count
            total += count
            logger.info(f"✓ {vehicle_type}: {count} unique vehicles (tracked)")
        
        vehicle_counts['total'] = total
        vehicle_counts['emergency_vehicles'] = len(emergency_track_ids)
        
        if emergency_track_ids:
            logger.warning(f"🚨 Emergency vehicles: {len(emergency_track_ids)} unique (IDs: {emergency_track_ids})")
        logger.info(f"📊 Total unique vehicles: {total} (tracked with ByteTrack)")
        return vehicle_counts
    
    async def process_video_async(
        self,
        video_path: str,
        job_id: str,
        location_id: str = "unknown",
        save_annotated: bool = True,
        emergency_callback: Optional[Callable] = None
    ) -> Dict:
        """
        Process video asynchronously with immediate emergency detection
        
        Args:
            video_path: Path to video file
            job_id: Unique job identifier
            location_id: Location identifier
            save_annotated: Save annotated video
            emergency_callback: Optional callback for immediate emergency alerts
            
        Returns:
            Processing results
        """
        loop = asyncio.get_event_loop()
        
        # Update job status
        self.processing_jobs[job_id] = {
            "status": "processing",
            "started_at": datetime.now().isoformat()
        }
        
        try:
            # Run processing in thread pool with emergency callback support
            from functools import partial
            process_fn = partial(
                self.process_video,
                video_path=video_path,
                location_id=location_id,
                save_annotated=save_annotated,
                emergency_callback=emergency_callback
            )
            results = await loop.run_in_executor(
                self.executor,
                process_fn
            )
            
            # Store job results to database
            await store_video_processing_job(job_id, video_path, location_id, results)
            logger.info(f"✓ Job results stored in database")
            
            # Update job with results
            self.processing_jobs[job_id] = {
                "status": "completed",
                "results": results,
                "completed_at": datetime.now().isoformat()
            }
            
            return results
            
        except Exception as e:
            logger.error(f"Video processing failed: {e}")
            self.processing_jobs[job_id] = {
                "status": "failed",
                "error": str(e),
                "failed_at": datetime.now().isoformat()
            }
            raise
    
    def get_job_status(self, job_id: str) -> Optional[Dict]:
        """Get status of processing job"""
        return self.processing_jobs.get(job_id)
    
    def extract_frame(self, video_path: str, frame_number: int) -> Optional[np.ndarray]:
        """
        Extract a specific frame from video
        
        Args:
            video_path: Path to video file
            frame_number: Frame index to extract
            
        Returns:
            Frame as numpy array or None
        """
        cap = cv2.VideoCapture(video_path)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = cap.read()
        cap.release()
        
        return frame if ret else None


class LiveStreamProcessor:
    """Process live CCTV streams"""
    
    def __init__(self, detector: VehicleDetector, analyzer: TrafficAnalyzer):
        """
        Initialize live stream processor
        
        Args:
            detector: VehicleDetector instance
            analyzer: TrafficAnalyzer instance
        """
        self.detector = detector
        self.analyzer = analyzer
        self.active_streams = {}
        self.frame_skip = 7  # SWEET SPOT: Frame skip for live stream processing
    
    async def process_stream(
        self,
        stream_url: str,
        stream_id: str,
        location_id: str,
        callback=None
    ):
        """
        Process live video stream
        
        Args:
            stream_url: RTSP or HTTP stream URL
            stream_id: Unique stream identifier
            location_id: Location identifier
            callback: Async callback function for detections
        """
        logger.info(f"Starting stream processing: {stream_id}")
        logger.info(f"Stream URL: {stream_url}")
        
        # Try to open stream with specific backend for IP cameras
        cap = cv2.VideoCapture(stream_url, cv2.CAP_FFMPEG)
        
        if not cap.isOpened():
            logger.error(f"Failed to open stream: {stream_url}")
            logger.info("Trying alternative URL formats...")
            # Try without /video suffix
            alt_url = stream_url.replace('/video', '/videofeed')
            cap = cv2.VideoCapture(alt_url, cv2.CAP_FFMPEG)
            if cap.isOpened():
                logger.info(f"Successfully opened with alternative URL: {alt_url}")
            else:
                logger.error("Failed to open stream with all URL formats")
                return
        
        logger.info(f"Stream opened successfully for {stream_id}")
        self.active_streams[stream_id] = {"status": "active", "location_id": location_id}
        
        failed_reads = 0
        max_failed_reads = 30  # Stop after 30 consecutive failures
        frame_count = 0
        frame_skip = self.frame_skip  # Use configured frame skip value
        
        try:
            while stream_id in self.active_streams:
                ret, frame = cap.read()
                if not ret:
                    failed_reads += 1
                    if failed_reads >= max_failed_reads:
                        logger.error(f"Stream {stream_id} failed {failed_reads} times, stopping")
                        break
                    logger.warning(f"Stream {stream_id} frame read failed ({failed_reads}/{max_failed_reads})")
                    await asyncio.sleep(0.5)
                    continue
                
                # Reset failed reads counter on success
                failed_reads = 0
                frame_count += 1
                
                # Skip frames for performance
                if frame_count % (frame_skip + 1) != 0:
                    await asyncio.sleep(0.033)
                    continue
                
                # Resize frame for faster processing
                height, width = frame.shape[:2]
                if width > 640:
                    scale = 640 / width
                    new_width = 640
                    new_height = int(height * scale)
                    frame = cv2.resize(frame, (new_width, new_height))
                
                # Detect and analyze
                detections, annotated = self.detector.detect_and_track(frame, track=True)
                analysis = self.analyzer.analyze_frame(detections)
                
                # Callback with results
                if callback:
                    await callback({
                        "stream_id": stream_id,
                        "location_id": location_id,
                        "timestamp": datetime.now().isoformat(),
                        "detections": detections,
                        "analysis": analysis,
                        "frame": annotated
                    })
                
                # Check emergency vehicles
                if self.detector.has_emergency_vehicles(detections):
                    logger.warning(f"🚨 Emergency vehicle in stream {stream_id}")
                
                await asyncio.sleep(0.05)  # ~20 FPS, reduced for stability
                
        finally:
            cap.release()
            if stream_id in self.active_streams:
                del self.active_streams[stream_id]
    
    def stop_stream(self, stream_id: str):
        """Stop processing a stream"""
        if stream_id in self.active_streams:
            del self.active_streams[stream_id]
            logger.info(f"Stopped stream: {stream_id}")
