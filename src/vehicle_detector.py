"""
Vehicle Detector Module
Uses YOLOv8 for real-time vehicle detection and tracking
"""

import cv2
import numpy as np
from ultralytics import YOLO
from typing import List, Dict, Tuple
import logging


class VehicleDetector:
    """
    Vehicle detection using YOLOv8 model
    """
    
    def __init__(self, model_path: str = 'yolov8n.pt', conf_threshold: float = 0.5):
        """
        Initialize the vehicle detector
        
        Args:
            model_path: Path to YOLOv8 model weights
            conf_threshold: Confidence threshold for detections
        """
        self.logger = logging.getLogger(__name__)
        self.conf_threshold = conf_threshold
        
        try:
            self.model = YOLO(model_path)
            self.logger.info(f"YOLOv8 model loaded: {model_path}")
        except Exception as e:
            self.logger.error(f"Failed to load model: {e}")
            raise
        
        # COCO dataset vehicle class IDs
        self.vehicle_classes = {
            2: 'car',
            3: 'motorcycle',
            5: 'bus',
            7: 'truck'
        }
        
        # Emergency vehicle classes
        self.emergency_classes = [5, 7]  # bus, truck (can represent ambulance, fire truck)
        
        # Colors for different vehicle types
        self.colors = {
            'car': (0, 255, 0),        # Green
            'motorcycle': (255, 255, 0),  # Yellow
            'bus': (255, 0, 0),        # Blue
            'truck': (0, 0, 255)       # Red
        }
    
    def detect(self, frame: np.ndarray) -> List[Dict]:
        """
        Detect vehicles in a frame
        
        Args:
            frame: Input image frame (BGR format)
            
        Returns:
            List of detected vehicles with bounding boxes and metadata
        """
        detections = []
        
        try:
            # Run YOLOv8 inference
            results = self.model(frame, conf=self.conf_threshold, verbose=False)
            
            # Process results
            for result in results:
                boxes = result.boxes
                
                for box in boxes:
                    # Get class ID
                    cls_id = int(box.cls[0])
                    
                    # Filter only vehicles
                    if cls_id in self.vehicle_classes:
                        # Get bounding box coordinates
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        
                        # Get confidence score
                        confidence = float(box.conf[0])
                        
                        # Vehicle type
                        vehicle_type = self.vehicle_classes[cls_id]
                        
                        # Check if emergency vehicle
                        is_emergency = cls_id in self.emergency_classes
                        
                        detection = {
                            'bbox': (x1, y1, x2, y2),
                            'confidence': confidence,
                            'class_id': cls_id,
                            'vehicle_type': vehicle_type,
                            'is_emergency': is_emergency,
                            'center': ((x1 + x2) // 2, (y1 + y2) // 2)
                        }
                        
                        detections.append(detection)
            
            self.logger.debug(f"Detected {len(detections)} vehicles")
            
        except Exception as e:
            self.logger.error(f"Detection error: {e}")
        
        return detections
    
    def draw_detections(self, frame: np.ndarray, detections: List[Dict]) -> np.ndarray:
        """
        Draw bounding boxes and labels on frame
        
        Args:
            frame: Input frame
            detections: List of detections from detect()
            
        Returns:
            Frame with drawn detections
        """
        annotated_frame = frame.copy()
        
        for detection in detections:
            x1, y1, x2, y2 = detection['bbox']
            vehicle_type = detection['vehicle_type']
            confidence = detection['confidence']
            is_emergency = detection['is_emergency']
            
            # Choose color
            color = (0, 0, 255) if is_emergency else self.colors.get(vehicle_type, (255, 255, 255))
            
            # Draw bounding box
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
            
            # Create label
            label = f"{vehicle_type}: {confidence:.2f}"
            if is_emergency:
                label = f"EMERGENCY {label}"
            
            # Draw label background
            label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            cv2.rectangle(annotated_frame, 
                         (x1, y1 - label_size[1] - 10), 
                         (x1 + label_size[0], y1), 
                         color, -1)
            
            # Draw label text
            cv2.putText(annotated_frame, label, 
                       (x1, y1 - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 
                       0.5, (255, 255, 255), 1)
        
        return annotated_frame
    
    def count_by_type(self, detections: List[Dict]) -> Dict[str, int]:
        """
        Count vehicles by type
        
        Args:
            detections: List of detections
            
        Returns:
            Dictionary with counts for each vehicle type
        """
        counts = {
            'car': 0,
            'motorcycle': 0,
            'bus': 0,
            'truck': 0,
            'emergency': 0,
            'total': 0
        }
        
        for detection in detections:
            vehicle_type = detection['vehicle_type']
            counts[vehicle_type] += 1
            counts['total'] += 1
            
            if detection['is_emergency']:
                counts['emergency'] += 1
        
        return counts


if __name__ == "__main__":
    """
    Test the vehicle detector with webcam or video file
    """
    import argparse
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Parse arguments
    parser = argparse.ArgumentParser(description='Test Vehicle Detector')
    parser.add_argument('--source', type=str, default='0', 
                       help='Video source (0 for webcam or path to video file)')
    parser.add_argument('--model', type=str, default='yolov8n.pt',
                       help='Path to YOLOv8 model')
    args = parser.parse_args()
    
    # Initialize detector
    detector = VehicleDetector(model_path=args.model)
    
    # Open video source
    source = int(args.source) if args.source.isdigit() else args.source
    cap = cv2.VideoCapture(source)
    
    if not cap.isOpened():
        print(f"Error: Could not open video source {args.source}")
        exit()
    
    print("Press 'q' to quit")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("End of video or cannot read frame")
            break
        
        # Detect vehicles
        detections = detector.detect(frame)
        
        # Draw detections
        annotated_frame = detector.draw_detections(frame, detections)
        
        # Get counts
        counts = detector.count_by_type(detections)
        
        # Display counts
        info_text = f"Total: {counts['total']} | Cars: {counts['car']} | " \
                   f"Bikes: {counts['motorcycle']} | Bus: {counts['bus']} | " \
                   f"Truck: {counts['truck']}"
        
        cv2.putText(annotated_frame, info_text, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        if counts['emergency'] > 0:
            cv2.putText(annotated_frame, f"EMERGENCY VEHICLES: {counts['emergency']}", 
                       (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        # Show frame
        cv2.imshow('Vehicle Detection', annotated_frame)
        
        # Break on 'q' press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
