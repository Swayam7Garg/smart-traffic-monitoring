"""
Email Alert System for Traffic Monitoring
Sends alerts when traffic exceeds threshold or emergency vehicles detected
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import yaml
from pathlib import Path

class AlertSystem:
    """Send email/SMS alerts for traffic events"""
    
    def __init__(self, config_path='config/alert_config.yaml'):
        """Initialize alert system"""
        self.config = self._load_config(config_path)
        self.enabled = self.config.get('enabled', False)
        self.email_alerts = self.config.get('email_alerts', {})
        self.thresholds = self.config.get('thresholds', {})
        
        self.last_alert_time = {}
        self.cooldown = 300  # 5 minutes between similar alerts
        
    def _load_config(self, config_path):
        """Load alert configuration"""
        config_file = Path(config_path)
        if config_file.exists():
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        return self._create_default_config(config_path)
    
    def _create_default_config(self, config_path):
        """Create default alert configuration"""
        default_config = {
            'enabled': False,  # Set to True to enable alerts
            'email_alerts': {
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'sender_email': 'your_email@gmail.com',
                'sender_password': 'your_app_password',  # Use app password for Gmail
                'recipient_emails': [
                    'admin@example.com',
                    'traffic_control@example.com'
                ]
            },
            'thresholds': {
                'congestion_threshold': 20,  # Vehicles per lane
                'emergency_alert': True,
                'system_error_alert': True
            },
            'alert_types': {
                'congestion': True,
                'emergency_vehicle': True,
                'system_error': True,
                'daily_summary': False
            }
        }
        
        # Save default config
        Path(config_path).parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False)
        
        return default_config
    
    def check_congestion(self, analysis):
        """Check if traffic is congested and send alert"""
        if not self.enabled or not self.config.get('alert_types', {}).get('congestion'):
            return
        
        threshold = self.thresholds.get('congestion_threshold', 20)
        
        for lane_idx, lane in enumerate(analysis['lanes']):
            if lane['vehicle_count'] >= threshold:
                alert_key = f'congestion_lane_{lane_idx}'
                
                if self._should_send_alert(alert_key):
                    self._send_congestion_alert(lane_idx, lane['vehicle_count'])
                    self.last_alert_time[alert_key] = datetime.now()
    
    def check_emergency(self, analysis):
        """Check for emergency vehicles and send alert"""
        if not self.enabled or not self.config.get('alert_types', {}).get('emergency_vehicle'):
            return
        
        if analysis['emergency_vehicles'] > 0:
            alert_key = 'emergency_vehicle'
            
            if self._should_send_alert(alert_key):
                self._send_emergency_alert(analysis['emergency_vehicles'])
                self.last_alert_time[alert_key] = datetime.now()
    
    def send_system_error(self, error_message):
        """Send alert for system errors"""
        if not self.enabled or not self.config.get('alert_types', {}).get('system_error'):
            return
        
        alert_key = 'system_error'
        
        if self._should_send_alert(alert_key):
            self._send_error_alert(error_message)
            self.last_alert_time[alert_key] = datetime.now()
    
    def _should_send_alert(self, alert_key):
        """Check if enough time has passed since last alert"""
        if alert_key not in self.last_alert_time:
            return True
        
        time_since_last = (datetime.now() - self.last_alert_time[alert_key]).seconds
        return time_since_last >= self.cooldown
    
    def _send_congestion_alert(self, lane_idx, vehicle_count):
        """Send congestion alert email"""
        subject = f"🚨 Traffic Congestion Alert - Lane {lane_idx + 1}"
        
        body = f"""
        <html>
        <body>
            <h2>Traffic Congestion Detected</h2>
            <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>Lane:</strong> Lane {lane_idx + 1}</p>
            <p><strong>Vehicle Count:</strong> {vehicle_count}</p>
            <p><strong>Status:</strong> High congestion detected</p>
            
            <p style="color: red;">Immediate action may be required.</p>
            
            <hr>
            <p><em>Smart Traffic Monitoring System</em></p>
        </body>
        </html>
        """
        
        self._send_email(subject, body)
    
    def _send_emergency_alert(self, count):
        """Send emergency vehicle alert email"""
        subject = "🚨 EMERGENCY VEHICLE DETECTED"
        
        body = f"""
        <html>
        <body>
            <h2 style="color: red;">Emergency Vehicle Alert</h2>
            <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>Emergency Vehicles:</strong> {count}</p>
            <p><strong>Action:</strong> Priority routing activated</p>
            
            <p style="color: red; font-size: 16px;">
                All lanes have been adjusted to prioritize emergency vehicle passage.
            </p>
            
            <hr>
            <p><em>Smart Traffic Monitoring System</em></p>
        </body>
        </html>
        """
        
        self._send_email(subject, body)
    
    def _send_error_alert(self, error_message):
        """Send system error alert email"""
        subject = "⚠️ System Error - Traffic Monitoring"
        
        body = f"""
        <html>
        <body>
            <h2 style="color: orange;">System Error Alert</h2>
            <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>Error:</strong></p>
            <pre style="background: #f4f4f4; padding: 10px;">{error_message}</pre>
            
            <p style="color: orange;">System administrator attention required.</p>
            
            <hr>
            <p><em>Smart Traffic Monitoring System</em></p>
        </body>
        </html>
        """
        
        self._send_email(subject, body)
    
    def _send_email(self, subject, body):
        """Send email alert"""
        try:
            email_config = self.email_alerts
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = email_config['sender_email']
            msg['To'] = ', '.join(email_config['recipient_emails'])
            
            html_part = MIMEText(body, 'html')
            msg.attach(html_part)
            
            # Connect to SMTP server
            server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
            server.starttls()
            server.login(email_config['sender_email'], email_config['sender_password'])
            
            # Send email
            server.send_message(msg)
            server.quit()
            
            print(f"✅ Alert sent: {subject}")
            
        except Exception as e:
            print(f"❌ Failed to send alert: {e}")


if __name__ == '__main__':
    # Test the alert system
    print("\n🔔 Alert System Test\n")
    
    alert = AlertSystem()
    
    if not alert.enabled:
        print("⚠️  Alert system is disabled.")
        print("📝 To enable:")
        print("   1. Edit config/alert_config.yaml")
        print("   2. Set 'enabled: true'")
        print("   3. Configure your email settings")
        print("\n💡 For Gmail:")
        print("   - Use App Password (not your regular password)")
        print("   - Enable 2-factor authentication")
        print("   - Generate app password: https://myaccount.google.com/apppasswords")
    else:
        print("✅ Alert system is enabled!")
        
        # Test congestion alert
        test_analysis = {
            'lanes': [
                {'vehicle_count': 25, 'density': 0.8},
                {'vehicle_count': 10, 'density': 0.3}
            ],
            'emergency_vehicles': 1
        }
        
        alert.check_congestion(test_analysis)
        alert.check_emergency(test_analysis)
