"""Configuration Manager Utility"""

import yaml
from pathlib import Path
from typing import Dict, Any


class ConfigManager:
    """Manage system configuration"""
    
    def __init__(self, config_path: str = 'config/config.yaml'):
        """
        Initialize config manager
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = Path(config_path)
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        if not self.config_path.exists():
            print(f"Config file not found: {self.config_path}")
            return self.get_default_config()
        
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            return config
        except Exception as e:
            print(f"Error loading config: {e}")
            return self.get_default_config()
    
    def save_config(self, config: Dict[str, Any] = None) -> bool:
        """Save configuration to YAML file"""
        if config is None:
            config = self.config
        
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    @staticmethod
    def get_default_config() -> Dict[str, Any]:
        """Return default configuration"""
        return {
            'detection': {
                'model': 'yolov8n.pt',
                'confidence_threshold': 0.5,
                'iou_threshold': 0.45,
                'device': 'cpu',
                'vehicle_classes': [2, 3, 5, 7],
                'emergency_classes': [5, 7]
            },
            'lanes': {
                'count': 4,
                'positions': {
                    'lane_1': [0, 0, 50, 50],
                    'lane_2': [50, 0, 100, 50],
                    'lane_3': [0, 50, 50, 100],
                    'lane_4': [50, 50, 100, 100]
                }
            },
            'signal': {
                'min_green_time': 10,
                'max_green_time': 60,
                'yellow_time': 3,
                'all_red_time': 2,
                'adaptive_mode': True,
                'density_thresholds': {
                    'low': 5,
                    'medium': 15,
                    'high': 30
                },
                'time_multipliers': {
                    'low': 1.0,
                    'medium': 1.5,
                    'high': 2.0
                },
                'emergency_priority': True,
                'emergency_green_time': 30
            },
            'video': {
                'source': 0,
                'frame_width': 1280,
                'frame_height': 720,
                'fps': 30,
                'skip_frames': 1,
                'resize_factor': 1.0
            },
            'output': {
                'save_video': False,
                'output_dir': 'data/output',
                'video_codec': 'mp4v',
                'show_live_feed': True,
                'show_detections': True,
                'show_statistics': True,
                'log_level': 'INFO',
                'log_file': 'data/output/traffic_log.txt'
            }
        }


if __name__ == "__main__":
    # Test config manager
    config_mgr = ConfigManager()
    
    print("Current Configuration:")
    print(f"Model: {config_mgr.get('detection.model')}")
    print(f"Lanes: {config_mgr.get('lanes.count')}")
    print(f"Min Green Time: {config_mgr.get('signal.min_green_time')}")
    
    # Test set
    config_mgr.set('signal.min_green_time', 15)
    print(f"\nUpdated Min Green Time: {config_mgr.get('signal.min_green_time')}")
