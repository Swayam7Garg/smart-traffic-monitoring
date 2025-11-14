"""
Test Vehicle Detector
Run this to test if vehicle detection is working properly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.vehicle_detector import VehicleDetector
import cv2
import pytest


def test_detector_initialization():
    """Test if detector initializes correctly"""
    detector = VehicleDetector(model_path='yolov8n.pt')
    assert detector is not None
    assert detector.model is not None
    print("✓ Detector initialization test passed")


def test_detector_with_sample_image():
    """Test detection with a sample image"""
    detector = VehicleDetector(model_path='yolov8n.pt')
    
    # Create a blank test image
    test_image = cv2.imread('data/input_videos/test_frame.jpg')
    if test_image is None:
        # Create dummy image if file doesn't exist
        test_image = cv2.imread(0) * 255
    
    detections = detector.detect(test_image)
    assert isinstance(detections, list)
    print(f"✓ Detection test passed - Found {len(detections)} vehicles")


def test_count_by_type():
    """Test vehicle counting by type"""
    detector = VehicleDetector(model_path='yolov8n.pt')
    
    # Mock detections
    mock_detections = [
        {'vehicle_type': 'car', 'is_emergency': False},
        {'vehicle_type': 'car', 'is_emergency': False},
        {'vehicle_type': 'truck', 'is_emergency': True},
    ]
    
    counts = detector.count_by_type(mock_detections)
    assert counts['car'] == 2
    assert counts['truck'] == 1
    assert counts['emergency'] == 1
    assert counts['total'] == 3
    print("✓ Count by type test passed")


if __name__ == "__main__":
    print("\nRunning Vehicle Detector Tests...")
    print("="*50)
    
    try:
        test_detector_initialization()
        # test_detector_with_sample_image()
        test_count_by_type()
        
        print("="*50)
        print("All tests passed! ✓\n")
    except Exception as e:
        print(f"\n✗ Test failed: {e}\n")
        raise
