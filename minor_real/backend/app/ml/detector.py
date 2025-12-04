"""
YOLOv8 Vehicle Detection Module
Handles real-time vehicle detection from video footage
"""

import cv2
import numpy as np
from ultralytics import YOLO
from typing import List, Tuple, Dict
import logging

logger = logging.getLogger(__name__)


class VehicleDetector:
    """YOLOv8-based vehicle detector with Indian vehicle support"""
    
    # Standard COCO vehicle class IDs
    VEHICLE_CLASSES = {
        2: "car",
        3: "motorcycle",
        5: "bus",
        7: "truck",
        1: "bicycle"
    }
    
    # Emergency vehicle detection keywords (from license plate or visual features)
    EMERGENCY_KEYWORDS = ["ambulance", "police", "fire", "emergency"]
    
    # Indian-specific vehicle mapping (can be trained with custom dataset)
    INDIAN_VEHICLE_MAPPING = {
        "motorcycle": ["bike", "scooter", "two-wheeler"],
        "car": ["car", "sedan", "suv", "hatchback"],
        "truck": ["truck", "lorry", "tempo"],
        "auto-rickshaw": ["auto", "rickshaw", "three-wheeler", "tuk-tuk"],
        "bicycle": ["bicycle", "cycle"]
    }
    
    def __init__(self, model_path: str = "yolov8n.pt", confidence: float = 0.2, detect_emergency: bool = True):
        """
        Initialize vehicle detector
        
        Args:
            model_path: Path to YOLOv8 model weights
            confidence: Confidence threshold for detections (default 0.2 for better bike/scooter detection)
            detect_emergency: Enable emergency vehicle detection
        """
        try:
            self.model = YOLO(model_path)
            self.confidence = confidence
            self.detect_emergency = detect_emergency
            self.emergency_vehicles_detected = []
            logger.info(f"✓ YOLOv8 model loaded: {model_path}")
            logger.info(f"✓ Confidence threshold: {confidence} (optimized for motorcycles)")
            logger.info(f"Emergency vehicle detection: {'enabled' if detect_emergency else 'disabled'}")
        except Exception as e:
            logger.error(f"Failed to load YOLO model: {e}")
            raise
    
    def detect(self, frame: np.ndarray, detect_three_wheelers: bool = True) -> List[Dict]:
        """
        Detect vehicles in a frame including Indian vehicles
        
        Args:
            frame: Input image/frame (numpy array)
            detect_three_wheelers: Attempt to classify 3-wheelers (auto-rickshaws)
            
        Returns:
            List of detection dictionaries containing:
                - class_id: Vehicle class ID
                - class_name: Vehicle type name
                - confidence: Detection confidence score
                - bbox: Bounding box [x, y, w, h]
                - is_emergency: Boolean indicating emergency vehicle
        """
        # OPTIMIZED: Use imgsz=640 for 4x faster detection (still accurate for traffic)
        # Lower IOU threshold for better detection of overlapping vehicles (especially bikes)
        results = self.model(frame, conf=self.confidence, iou=0.4, imgsz=640, verbose=False)
        
        detections = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                class_id = int(box.cls[0])
                
                # Filter only vehicles
                if class_id in self.VEHICLE_CLASSES:
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    confidence = float(box.conf[0])
                    vehicle_type = self.VEHICLE_CLASSES[class_id]
                    
                    # Attempt to classify auto-rickshaws (3-wheelers)
                    # They often get detected as motorcycles but are larger
                    if detect_three_wheelers and class_id == 3:  # motorcycle
                        bbox_area = (x2 - x1) * (y2 - y1)
                        # Auto-rickshaws are significantly larger than bikes/scooters
                        # Typical sizes: Bike/Scooter: 3000-12000px, Auto: 20000-40000px
                        if bbox_area > 25000:  # Increased threshold to avoid false positives
                            vehicle_type = "auto-rickshaw"
                    
                    # Check for emergency vehicles (basic color/shape heuristics)
                    is_emergency = False
                    if self.detect_emergency:
                        is_emergency = self._check_emergency_vehicle(frame, x1, y1, x2, y2, vehicle_type)
                    
                    detections.append({
                        "class_id": class_id,
                        "class_name": vehicle_type,
                        "confidence": confidence,
                        "bbox": [int(x1), int(y1), int(x2 - x1), int(y2 - y1)],
                        "is_emergency": is_emergency
                    })
        
        return detections
    
    def _check_emergency_vehicle(self, frame: np.ndarray, x1: float, y1: float, x2: float, y2: float, vehicle_type: str) -> bool:
        """
        ENHANCED emergency vehicle detection with multiple validation layers
        Uses color patterns, vehicle size, shape, and spatial features
        
        Args:
            frame: Full frame
            x1, y1, x2, y2: Bounding box coordinates
            vehicle_type: Detected vehicle type
            
        Returns:
            True if emergency vehicle detected with high confidence
        """
        # Only check cars, buses, and trucks
        if vehicle_type not in ["car", "bus", "truck"]:
            return False
        
        try:
            # Extract vehicle region
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            vehicle_roi = frame[y1:y2, x1:x2]
            h, w = vehicle_roi.shape[:2]
            
            # Minimum size check - emergency vehicles are typically larger
            # Reduced threshold to catch smaller ambulances
            if h < 50 or w < 50:
                return False
            
            # Vehicle size and aspect ratio analysis
            bbox_area = h * w
            aspect_ratio = w / h if h > 0 else 0
            
            # Convert to HSV and BGR for multi-spectrum analysis
            hsv = cv2.cvtColor(vehicle_roi, cv2.COLOR_BGR2HSV)
            
            # Split vehicle into strategic regions
            top_h = int(h * 0.25)      # Top 25% - light bars, roof
            mid_h = int(h * 0.5)       # Middle 50% - body, markings
            upper_h = int(h * 0.4)     # Top 40% - upper body area
            
            top_region = hsv[:top_h, :]
            mid_region = hsv[top_h:mid_h, :]
            upper_region = hsv[:upper_h, :]
            full_region = hsv
            
            # === RED DETECTION (Ambulances, Fire Trucks) ===
            # Very bright red (emergency lights and markings)
            lower_red_bright1 = np.array([0, 120, 120])   # Lowered threshold for detection
            upper_red_bright1 = np.array([10, 255, 255])
            lower_red_bright2 = np.array([170, 120, 120])
            upper_red_bright2 = np.array([180, 255, 255])
            
            mask_red_top = cv2.bitwise_or(
                cv2.inRange(top_region, lower_red_bright1, upper_red_bright1),
                cv2.inRange(top_region, lower_red_bright2, upper_red_bright2)
            )
            mask_red_upper = cv2.bitwise_or(
                cv2.inRange(upper_region, lower_red_bright1, upper_red_bright1),
                cv2.inRange(upper_region, lower_red_bright2, upper_red_bright2)
            )
            mask_red_full = cv2.bitwise_or(
                cv2.inRange(full_region, lower_red_bright1, upper_red_bright1),
                cv2.inRange(full_region, lower_red_bright2, upper_red_bright2)
            )
            
            # === BLUE DETECTION (Police vehicles) ===
            lower_blue_bright = np.array([95, 100, 100])
            upper_blue_bright = np.array([135, 255, 255])
            mask_blue_top = cv2.inRange(top_region, lower_blue_bright, upper_blue_bright)
            mask_blue_full = cv2.inRange(full_region, lower_blue_bright, upper_blue_bright)
            
            # === WHITE DETECTION (Ambulances base color) ===
            lower_white = np.array([0, 0, 180])    # Slightly darker whites
            upper_white = np.array([180, 50, 255])
            mask_white_full = cv2.inRange(full_region, lower_white, upper_white)
            
            # === YELLOW/ORANGE DETECTION (Fire trucks, warning stripes) ===
            lower_orange = np.array([8, 120, 120])
            upper_orange = np.array([28, 255, 255])
            mask_orange = cv2.inRange(full_region, lower_orange, upper_orange)
            
            # Calculate color percentages
            top_pixels = top_region.shape[0] * top_region.shape[1]
            upper_pixels = upper_region.shape[0] * upper_region.shape[1]
            total_pixels = h * w
            
            red_top_pct = (cv2.countNonZero(mask_red_top) / top_pixels) * 100 if top_pixels > 0 else 0
            red_upper_pct = (cv2.countNonZero(mask_red_upper) / upper_pixels) * 100 if upper_pixels > 0 else 0
            red_full_pct = (cv2.countNonZero(mask_red_full) / total_pixels) * 100
            blue_top_pct = (cv2.countNonZero(mask_blue_top) / top_pixels) * 100 if top_pixels > 0 else 0
            blue_full_pct = (cv2.countNonZero(mask_blue_full) / total_pixels) * 100
            white_full_pct = (cv2.countNonZero(mask_white_full) / total_pixels) * 100
            orange_pct = (cv2.countNonZero(mask_orange) / total_pixels) * 100
            
            # Confidence scoring system (0-100)
            confidence_score = 0
            detection_reasons = []
            
            # === DETECTION CRITERIA (Multi-layered approach) ===
            
            # 1. LIGHT BAR DETECTION - Strongest indicator (roof-mounted lights)
            if red_top_pct > 6:
                confidence_score += 40
                detection_reasons.append(f"Red light bar ({red_top_pct:.1f}%)")
            elif red_top_pct > 4:
                confidence_score += 25
                detection_reasons.append(f"Red lights top ({red_top_pct:.1f}%)")
            
            if blue_top_pct > 6:
                confidence_score += 40
                detection_reasons.append(f"Blue light bar ({blue_top_pct:.1f}%)")
            elif blue_top_pct > 3:
                confidence_score += 25
                detection_reasons.append(f"Blue lights top ({blue_top_pct:.1f}%)")
            
            # 2. AMBULANCE PATTERN - White vehicle with red markings
            if white_full_pct > 55 and red_upper_pct > 2.5:
                confidence_score += 35
                detection_reasons.append(f"Ambulance pattern (W:{white_full_pct:.1f}% R:{red_upper_pct:.1f}%)")
            elif white_full_pct > 50 and (red_full_pct > 8 or red_top_pct > 2):
                confidence_score += 28
                detection_reasons.append(f"White+Red ({white_full_pct:.1f}%/{red_full_pct:.1f}%)")
            
            # 3. FIRE TRUCK PATTERN - Red body or orange/yellow
            if vehicle_type in ["truck", "bus"]:
                if red_full_pct > 30:
                    confidence_score += 35
                    detection_reasons.append(f"Red fire truck ({red_full_pct:.1f}%)")
                elif orange_pct > 12:
                    confidence_score += 30
                    detection_reasons.append(f"Yellow fire truck ({orange_pct:.1f}%)")
            elif red_full_pct > 40 and aspect_ratio > 1.2:  # Large red vehicle
                confidence_score += 30
                detection_reasons.append(f"Red emergency ({red_full_pct:.1f}%)")
            
            # 4. POLICE VEHICLE - Blue with lights
            if blue_full_pct > 15 or (blue_top_pct > 2 and vehicle_type in ["car", "truck"]):
                confidence_score += 30
                detection_reasons.append(f"Police blue ({blue_full_pct:.1f}%)")
            
            # 5. SIZE FACTOR - Emergency vehicles are usually bigger
            if vehicle_type == "truck" or vehicle_type == "bus":
                confidence_score += 10
                detection_reasons.append("Large vehicle")
            elif bbox_area > 15000:  # Large car/van
                confidence_score += 8
                detection_reasons.append("Large size")
            
            # 6. ORANGE/YELLOW WARNING MARKINGS
            if orange_pct > 15:
                confidence_score += 25
                detection_reasons.append(f"Warning stripes ({orange_pct:.1f}%)")
            elif orange_pct > 8 and (red_full_pct > 5 or white_full_pct > 40):
                confidence_score += 15
                detection_reasons.append(f"Yellow marks ({orange_pct:.1f}%)")
            
            # 7. COMBINATION PATTERNS (Bonus scoring)
            if red_top_pct > 3 and white_full_pct > 40:  # Classic ambulance
                confidence_score += 15
                detection_reasons.append("Classic ambulance combo")
            
            if (red_full_pct > 20 or orange_pct > 10) and vehicle_type == "truck":  # Fire truck
                confidence_score += 12
                detection_reasons.append("Fire truck combo")
            
            # === DECISION THRESHOLD ===
            # Require confidence score >= 50 to classify as emergency vehicle
            if confidence_score >= 50:
                reasons_str = " + ".join(detection_reasons)
                logger.info(f"🚨 EMERGENCY VEHICLE DETECTED: {vehicle_type} | Score: {confidence_score} | {reasons_str}")
                return True
                
        except Exception as e:
            logger.debug(f"Emergency detection error: {e}")
        
        return False
    
    def detect_and_track(
        self,
        frame: np.ndarray,
        track: bool = True
    ) -> Tuple[List[Dict], np.ndarray]:
        """
        Detect vehicles and optionally track them
        
        Args:
            frame: Input frame
            track: Enable object tracking
            
        Returns:
            Tuple of (detections, annotated_frame)
        """
        # Use imgsz=640 for faster detection
        if track:
            results = self.model.track(
                frame,
                conf=self.confidence,
                iou=0.4,
                imgsz=640,
                persist=True,
                tracker="bytetrack.yaml",
                verbose=False
            )
        else:
            results = self.model(frame, conf=self.confidence, iou=0.4, imgsz=640, verbose=False)
        
        detections = []
        annotated_frame = frame.copy()
        
        for result in results:
            boxes = result.boxes
            for box in boxes:
                class_id = int(box.cls[0])
                
                if class_id in self.VEHICLE_CLASSES:
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    confidence = float(box.conf[0])
                    vehicle_type = self.VEHICLE_CLASSES[class_id]
                    
                    # Get tracking ID if available
                    track_id = int(box.id[0]) if box.id is not None else None
                    
                    # Calculate bbox dimensions
                    bbox_width = x2 - x1
                    bbox_height = y2 - y1
                    bbox_area = bbox_width * bbox_height
                    aspect_ratio = bbox_width / bbox_height if bbox_height > 0 else 0
                    
                    # Classify two-wheelers and three-wheelers
                    if class_id == 1:  # bicycle
                        vehicle_type = "bicycle"
                        logger.info(f"✓ Bicycle detected: area={bbox_area:.0f}px")
                    
                    elif class_id == 3:  # motorcycle class
                        # Auto-rickshaws: larger area (6000+) and square aspect ratio (1.0-1.8)
                        # Motorcycles/bikes: smaller area (<6000) or narrow/tall aspect
                        if bbox_area > 6000 and 1.0 <= aspect_ratio <= 1.8:
                            vehicle_type = "auto-rickshaw"
                            logger.info(f"✓ Auto-rickshaw detected: area={bbox_area:.0f}px, ratio={aspect_ratio:.2f}")
                        else:
                            vehicle_type = "motorcycle"
                            logger.info(f"✓ Motorcycle detected: area={bbox_area:.0f}px, ratio={aspect_ratio:.2f}")
                    
                    # Check small cars - might be auto-rickshaws detected as cars
                    elif class_id == 2:  # car class
                        # Small square vehicles could be autos (3000-12000 pixels)
                        # Auto-rickshaws have distinctive square/compact shape
                        if 3000 <= bbox_area <= 12000 and 0.9 <= aspect_ratio <= 1.7:
                            vehicle_type = "auto-rickshaw"
                            logger.info(f"✓ Auto (from car): area={bbox_area:.0f}px, ratio={aspect_ratio:.2f}")
                        # Log all vehicle detections to see what's being found
                    
                    logger.info(f"Detected: {vehicle_type} (class {class_id}, conf={confidence:.2f}, area={bbox_area:.0f}, ratio={aspect_ratio:.2f})")
                    
                    # Check emergency status
                    is_emergency = False
                    if self.detect_emergency:
                        is_emergency = self._check_emergency_vehicle(frame, x1, y1, x2, y2, vehicle_type)
                    
                    detection = {
                        "class_id": class_id,
                        "class_name": vehicle_type,
                        "confidence": confidence,
                        "bbox": [int(x1), int(y1), int(x2 - x1), int(y2 - y1)],
                        "track_id": track_id,
                        "is_emergency": is_emergency
                    }
                    detections.append(detection)
                    
                    # Draw bounding box (red for emergency, green for normal)
                    color = (0, 0, 255) if is_emergency else (0, 255, 0)  # Red or Green
                    thickness = 3 if is_emergency else 2
                    
                    cv2.rectangle(
                        annotated_frame,
                        (int(x1), int(y1)),
                        (int(x2), int(y2)),
                        color,
                        thickness
                    )
                    
                    # Add label
                    label = f"{detection['class_name']} {confidence:.2f}"
                    if track_id:
                        label = f"ID{track_id} {label}"
                    if is_emergency:
                        label = f"🚨 EMERGENCY - {label}"
                    
                    cv2.putText(
                        annotated_frame,
                        label,
                        (int(x1), int(y1) - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        color,
                        2
                    )
        
        return detections, annotated_frame
    
    def count_vehicles(self, detections: List[Dict]) -> Dict[str, int]:
        """
        Count vehicles by type including emergency vehicles
        
        Args:
            detections: List of detection dictionaries
            
        Returns:
            Dictionary with vehicle counts by type and emergency count
        """
        counts = {}
        emergency_count = 0
        
        for detection in detections:
            vehicle_type = detection["class_name"]
            counts[vehicle_type] = counts.get(vehicle_type, 0) + 1
            
            if detection.get("is_emergency", False):
                emergency_count += 1
        
        counts["total"] = len(detections)
        counts["emergency_vehicles"] = emergency_count
        
        return counts
    
    def has_emergency_vehicles(self, detections: List[Dict]) -> bool:
        """
        Check if any emergency vehicles detected
        
        Args:
            detections: List of detection dictionaries
            
        Returns:
            True if emergency vehicle present
        """
        return any(d.get("is_emergency", False) for d in detections)
    
    def get_emergency_vehicles(self, detections: List[Dict]) -> List[Dict]:
        """
        Get only emergency vehicle detections
        
        Args:
            detections: List of detection dictionaries
            
        Returns:
            List of emergency vehicle detections
        """
        return [d for d in detections if d.get("is_emergency", False)]
