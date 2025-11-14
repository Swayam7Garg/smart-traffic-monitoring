"""
Traffic Report Generator
Generates detailed PDF and Excel reports with statistics and visualizations
"""

import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import json

try:
    from fpdf import FPDF
    FPDF_AVAILABLE = True
except ImportError:
    FPDF_AVAILABLE = False
    print("⚠️  fpdf not installed. PDF reports disabled.")
    print("   Install with: pip install fpdf2")


class TrafficReportGenerator:
    """Generate comprehensive traffic reports"""
    
    def __init__(self, output_dir='data/reports'):
        """Initialize report generator"""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.session_data = {
            'timestamps': [],
            'total_vehicles': [],
            'lane_counts': [[], [], [], []],
            'emergency_vehicles': [],
            'active_lanes': []
        }
    
    def log_frame_data(self, analysis, signal_status):
        """Log data from each frame for reporting"""
        timestamp = datetime.now()
        
        self.session_data['timestamps'].append(timestamp)
        self.session_data['total_vehicles'].append(analysis['total_vehicles'])
        self.session_data['emergency_vehicles'].append(analysis['emergency_vehicles'])
        self.session_data['active_lanes'].append(signal_status['active_lane'])
        
        for i, lane in enumerate(analysis['lanes']):
            self.session_data['lane_counts'][i].append(lane['vehicle_count'])
    
    def generate_excel_report(self, filename=None):
        """Generate Excel report with statistics"""
        if not self.session_data['timestamps']:
            print("⚠️  No data to generate report")
            return None
        
        if filename is None:
            filename = f"traffic_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        filepath = self.output_dir / filename
        
        # Create dataframe
        df = pd.DataFrame({
            'Timestamp': self.session_data['timestamps'],
            'Total_Vehicles': self.session_data['total_vehicles'],
            'Lane_1': self.session_data['lane_counts'][0],
            'Lane_2': self.session_data['lane_counts'][1],
            'Lane_3': self.session_data['lane_counts'][2],
            'Lane_4': self.session_data['lane_counts'][3],
            'Emergency_Vehicles': self.session_data['emergency_vehicles'],
            'Active_Lane': self.session_data['active_lanes']
        })
        
        # Calculate statistics
        stats_df = pd.DataFrame({
            'Metric': [
                'Total Frames',
                'Total Vehicles Detected',
                'Average Vehicles per Frame',
                'Max Vehicles (Single Frame)',
                'Emergency Vehicles',
                'Peak Lane (Most Traffic)',
                'Session Duration (minutes)'
            ],
            'Value': [
                len(df),
                df['Total_Vehicles'].sum(),
                df['Total_Vehicles'].mean(),
                df['Total_Vehicles'].max(),
                df['Emergency_Vehicles'].sum(),
                f"Lane {df[['Lane_1', 'Lane_2', 'Lane_3', 'Lane_4']].sum().idxmax().split('_')[1]}",
                (df['Timestamp'].iloc[-1] - df['Timestamp'].iloc[0]).seconds / 60
            ]
        })
        
        # Write to Excel with multiple sheets
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            stats_df.to_excel(writer, sheet_name='Summary', index=False)
            df.to_excel(writer, sheet_name='Detailed_Data', index=False)
            
            # Lane statistics
            lane_stats = pd.DataFrame({
                'Lane': ['Lane 1', 'Lane 2', 'Lane 3', 'Lane 4'],
                'Total_Vehicles': [sum(self.session_data['lane_counts'][i]) for i in range(4)],
                'Average': [sum(self.session_data['lane_counts'][i])/len(self.session_data['lane_counts'][i]) if self.session_data['lane_counts'][i] else 0 for i in range(4)],
                'Max': [max(self.session_data['lane_counts'][i]) if self.session_data['lane_counts'][i] else 0 for i in range(4)]
            })
            lane_stats.to_excel(writer, sheet_name='Lane_Statistics', index=False)
        
        print(f"✅ Excel report saved: {filepath}")
        return str(filepath)
    
    def generate_charts(self):
        """Generate visualization charts"""
        if not self.session_data['timestamps']:
            return []
        
        chart_files = []
        
        # Chart 1: Total vehicles over time
        plt.figure(figsize=(12, 6))
        plt.plot(self.session_data['timestamps'], self.session_data['total_vehicles'], 
                linewidth=2, color='#667eea')
        plt.title('Total Vehicles Over Time', fontsize=16, fontweight='bold')
        plt.xlabel('Time')
        plt.ylabel('Vehicle Count')
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        chart1 = self.output_dir / 'chart_vehicles_timeline.png'
        plt.savefig(chart1, dpi=300, bbox_inches='tight')
        plt.close()
        chart_files.append(str(chart1))
        
        # Chart 2: Lane comparison
        plt.figure(figsize=(10, 6))
        lane_totals = [sum(self.session_data['lane_counts'][i]) for i in range(4)]
        colors = ['#667eea', '#764ba2', '#f59e0b', '#10b981']
        bars = plt.bar(['Lane 1', 'Lane 2', 'Lane 3', 'Lane 4'], lane_totals, color=colors)
        plt.title('Total Vehicles per Lane', fontsize=16, fontweight='bold')
        plt.ylabel('Vehicle Count')
        plt.grid(axis='y', alpha=0.3)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        chart2 = self.output_dir / 'chart_lane_comparison.png'
        plt.savefig(chart2, dpi=300, bbox_inches='tight')
        plt.close()
        chart_files.append(str(chart2))
        
        # Chart 3: Lane distribution over time
        plt.figure(figsize=(12, 6))
        for i in range(4):
            plt.plot(self.session_data['timestamps'], self.session_data['lane_counts'][i],
                    label=f'Lane {i+1}', linewidth=2, color=colors[i])
        plt.title('Lane Distribution Over Time', fontsize=16, fontweight='bold')
        plt.xlabel('Time')
        plt.ylabel('Vehicle Count')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        chart3 = self.output_dir / 'chart_lane_distribution.png'
        plt.savefig(chart3, dpi=300, bbox_inches='tight')
        plt.close()
        chart_files.append(str(chart3))
        
        print(f"✅ Generated {len(chart_files)} charts")
        return chart_files
    
    def generate_pdf_report(self, filename=None):
        """Generate comprehensive PDF report"""
        if not FPDF_AVAILABLE:
            print("⚠️  PDF generation not available. Install fpdf2: pip install fpdf2")
            return None
        
        if not self.session_data['timestamps']:
            print("⚠️  No data to generate report")
            return None
        
        # Generate charts first
        charts = self.generate_charts()
        
        if filename is None:
            filename = f"traffic_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        filepath = self.output_dir / filename
        
        # Create PDF
        pdf = FPDF()
        pdf.add_page()
        
        # Title
        pdf.set_font('Arial', 'B', 24)
        pdf.cell(0, 20, 'Smart Traffic Monitoring Report', 0, 1, 'C')
        
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1, 'C')
        pdf.ln(10)
        
        # Summary Statistics
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'Summary Statistics', 0, 1)
        pdf.ln(5)
        
        total_vehicles = sum(self.session_data['total_vehicles'])
        avg_vehicles = total_vehicles / len(self.session_data['total_vehicles']) if self.session_data['total_vehicles'] else 0
        emergency_total = sum(self.session_data['emergency_vehicles'])
        duration = (self.session_data['timestamps'][-1] - self.session_data['timestamps'][0]).seconds / 60
        
        pdf.set_font('Arial', '', 12)
        stats = [
            f"Total Frames Analyzed: {len(self.session_data['timestamps'])}",
            f"Total Vehicles Detected: {total_vehicles}",
            f"Average Vehicles per Frame: {avg_vehicles:.2f}",
            f"Emergency Vehicles: {emergency_total}",
            f"Session Duration: {duration:.2f} minutes"
        ]
        
        for stat in stats:
            pdf.cell(0, 8, stat, 0, 1)
        
        pdf.ln(10)
        
        # Lane Statistics
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'Lane Statistics', 0, 1)
        pdf.ln(5)
        
        pdf.set_font('Arial', '', 12)
        for i in range(4):
            lane_total = sum(self.session_data['lane_counts'][i])
            lane_avg = lane_total / len(self.session_data['lane_counts'][i]) if self.session_data['lane_counts'][i] else 0
            pdf.cell(0, 8, f"Lane {i+1}: {lane_total} vehicles (avg: {lane_avg:.2f})", 0, 1)
        
        # Add charts
        if charts:
            pdf.add_page()
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, 'Visualization Charts', 0, 1)
            pdf.ln(5)
            
            for chart in charts:
                if Path(chart).exists():
                    pdf.image(chart, x=10, w=190)
                    pdf.ln(5)
        
        # Save PDF
        pdf.output(str(filepath))
        print(f"✅ PDF report saved: {filepath}")
        
        return str(filepath)
    
    def generate_all_reports(self):
        """Generate all report types"""
        print("\n📊 Generating Traffic Reports...\n")
        
        reports = {}
        
        # Excel report
        excel_file = self.generate_excel_report()
        if excel_file:
            reports['excel'] = excel_file
        
        # PDF report
        pdf_file = self.generate_pdf_report()
        if pdf_file:
            reports['pdf'] = pdf_file
        
        print(f"\n✅ Generated {len(reports)} reports in: {self.output_dir}")
        return reports


if __name__ == '__main__':
    # Test report generation with dummy data
    print("\n📊 Testing Report Generator\n")
    
    generator = TrafficReportGenerator()
    
    # Generate some test data
    from datetime import datetime, timedelta
    import random
    
    start_time = datetime.now()
    for i in range(100):
        analysis = {
            'total_vehicles': random.randint(5, 30),
            'lanes': [
                {'vehicle_count': random.randint(0, 10)},
                {'vehicle_count': random.randint(0, 10)},
                {'vehicle_count': random.randint(0, 10)},
                {'vehicle_count': random.randint(0, 10)}
            ],
            'emergency_vehicles': random.randint(0, 2)
        }
        signal_status = {'active_lane': random.randint(0, 3)}
        
        generator.log_frame_data(analysis, signal_status)
        generator.session_data['timestamps'][-1] = start_time + timedelta(seconds=i)
    
    # Generate reports
    generator.generate_all_reports()
    
    print("\n✅ Test complete! Check data/reports/ folder")
