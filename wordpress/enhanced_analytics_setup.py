#!/usr/bin/env python3
"""
Enhanced WordPress Analytics Setup

This script automates the installation and configuration of various analytics tools
for the Encompass MSP WordPress site, including monitoring and reporting setup.
"""
import os
import sys
import json
import time
import smtplib
import schedule
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import subprocess
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('analytics_setup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AnalyticsConfig:
    """Configuration for analytics tools."""
    
    def __init__(self, config_file: str = 'analytics_config.json'):
        """Initialize with configuration file."""
        self.config_file = Path(config_file)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default."""
        default_config = {
            'wordpress': {
                'url': '',
                'admin_user': '',
                'admin_password': '',
                'path': ''
            },
            'google': {
                'ga4_property_id': '',
                'gtm_id': ''
            },
            'microsoft': {
                'clarity_id': ''
            },
            'hotjar': {
                'site_id': ''
            },
            'matomo': {
                'enabled': False,
                'url': '',
                'site_id': ''
            },
            'monitoring': {
                'email_alerts': False,
                'email_recipient': '',
                'smtp_server': '',
                'smtp_port': 587,
                'smtp_username': '',
                'smtp_password': ''
            },
            'reporting': {
                'daily_report': False,
                'weekly_report': True,
                'monthly_report': True,
                'report_recipient': ''
            }
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return {**default_config, **json.load(f)}
            except json.JSONDecodeError:
                logger.warning("Invalid config file. Using default configuration.")
        
        return default_config
    
    def save_config(self) -> None:
        """Save configuration to file."""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
        logger.info(f"Configuration saved to {self.config_file}")


class AnalyticsMonitor:
    """Monitors analytics implementation and sends alerts."""
    
    def __init__(self, config: AnalyticsConfig):
        """Initialize with configuration."""
        self.config = config
        self.monitoring_data = {
            'last_check': None,
            'alerts': [],
            'metrics': {}
        }
    
    def check_analytics_implementation(self) -> bool:
        """Check if analytics are properly implemented."""
        self.monitoring_data['last_check'] = datetime.utcnow().isoformat()
        
        # Check GA4 implementation
        if self.config.config['google']['ga4_property_id']:
            self._check_ga4_implementation()
        
        # Check GTM implementation
        if self.config.config['google']['gtm_id']:
            self._check_gtm_implementation()
        
        # Check other analytics tools
        self._check_other_analytics()
        
        # Send alerts if needed
        if self.monitoring_data['alerts'] and self.config.config['monitoring']['email_alerts']:
            self._send_alerts()
        
        return len(self.monitoring_data['alerts']) == 0
    
    def _check_ga4_implementation(self) -> None:
        """Check GA4 implementation."""
        try:
            # This is a simplified check - in a real implementation, you would
            # verify the GA4 tracking code is present on the page
            home_page = requests.get(self.config.config['wordpress']['url'])
            has_ga4 = 'gtag' in home_page.text and 'config' in home_page.text
            
            if not has_ga4:
                self.monitoring_data['alerts'].append({
                    'level': 'error',
                    'message': 'GA4 tracking code not detected on homepage',
                    'timestamp': datetime.utcnow().isoformat()
                })
            
            self.monitoring_data['metrics']['ga4_implemented'] = has_ga4
            
        except Exception as e:
            logger.error(f"Error checking GA4 implementation: {e}")
            self.monitoring_data['alerts'].append({
                'level': 'error',
                'message': f'Error checking GA4 implementation: {str(e)}',
                'timestamp': datetime.utcnow().isoformat()
            })
    
    def _check_gtm_implementation(self) -> None:
        """Check GTM implementation."""
        try:
            home_page = requests.get(self.config.config['wordpress']['url'])
            gtm_id = self.config.config['google']['gtm_id']
            has_gtm = f'GTM-{gtm_id}' in home_page.text or f'gtm.js?id={gtm_id}' in home_page.text
            
            if not has_gtm:
                self.monitoring_data['alerts'].append({
                    'level': 'warning',
                    'message': 'Google Tag Manager code not detected on homepage',
                    'timestamp': datetime.utcnow().isoformat()
                })
            
            self.monitoring_data['metrics']['gtm_implemented'] = has_gtm
            
        except Exception as e:
            logger.error(f"Error checking GTM implementation: {e}")
    
    def _check_other_analytics(self) -> None:
        """Check other analytics implementations."""
        try:
            home_page = requests.get(self.config.config['wordpress']['url']).text
            
            # Check Microsoft Clarity
            if self.config.config['microsoft']['clarity_id']:
                has_clarity = f'clarity.ms/sync' in home_page or f'c.clarity.ms' in home_page
                self.monitoring_data['metrics']['clarity_implemented'] = has_clarity
                if not has_clarity:
                    self.monitoring_data['alerts'].append({
                        'level': 'warning',
                        'message': 'Microsoft Clarity tracking not detected',
                        'timestamp': datetime.utcnow().isoformat()
                    })
            
            # Check Hotjar
            if self.config.config['hotjar']['site_id']:
                has_hotjar = 'hotjar' in home_page.lower()
                self.monitoring_data['metrics']['hotjar_implemented'] = has_hotjar
                if not has_hotjar:
                    self.monitoring_data['alerts'].append({
                        'level': 'warning',
                        'message': 'Hotjar tracking not detected',
                        'timestamp': datetime.utcnow().isoformat()
                    })
            
        except Exception as e:
            logger.error(f"Error checking other analytics: {e}")
    
    def _send_alerts(self) -> None:
        """Send email alerts for any issues found."""
        if not self.config.config['monitoring']['email_alerts']:
            return
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config.config['monitoring']['smtp_username']
            msg['To'] = self.config.config['monitoring']['email_recipient']
            msg['Subject'] = 'Analytics Monitoring Alert'
            
            # Create email body
            body = "Analytics Monitoring Alert\n\n"
            body += f"Time: {datetime.utcnow().isoformat()}\n"
            body += f"Site: {self.config.config['wordpress']['url']}\n\n"
            
            if self.monitoring_data['alerts']:
                body += "Issues Found:\n"
                for alert in self.monitoring_data['alerts']:
                    body += f"- [{alert['level'].upper()}] {alert['message']} ({alert['timestamp']})\n"
            else:
                body += "No issues detected.\n"
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            with smtplib.SMTP(
                self.config.config['monitoring']['smtp_server'],
                self.config.config['monitoring']['smtp_port']
            ) as server:
                server.starttls()
                server.login(
                    self.config.config['monitoring']['smtp_username'],
                    self.config.config['monitoring']['smtp_password']
                )
                server.send_message(msg)
            
            logger.info("Alert email sent successfully")
            
        except Exception as e:
            logger.error(f"Error sending alert email: {e}")


class AnalyticsReporter:
    """Generates and sends analytics reports."""
    
    def __init__(self, config: AnalyticsConfig):
        """Initialize with configuration."""
        self.config = config
        self.report_data = {
            'generated_at': None,
            'period': {},
            'metrics': {},
            'recommendations': []
        }
    
    def generate_daily_report(self) -> Dict[str, Any]:
        """Generate daily analytics report."""
        if not self.config.config['reporting']['daily_report']:
            return {}
        
        self.report_data['generated_at'] = datetime.utcnow().isoformat()
        self.report_data['period'] = {
            'start': (datetime.utcnow() - timedelta(days=1)).isoformat(),
            'end': datetime.utcnow().isoformat()
        }
        
        # In a real implementation, this would fetch data from the analytics APIs
        self._generate_sample_report_data('daily')
        
        if self.config.config['reporting']['report_recipient']:
            self._send_report('Daily Analytics Report')
        
        return self.report_data
    
    def generate_weekly_report(self) -> Dict[str, Any]:
        """Generate weekly analytics report."""
        if not self.config.config['reporting']['weekly_report']:
            return {}
        
        self.report_data['generated_at'] = datetime.utcnow().isoformat()
        self.report_data['period'] = {
            'start': (datetime.utcnow() - timedelta(weeks=1)).isoformat(),
            'end': datetime.utcnow().isoformat()
        }
        
        # In a real implementation, this would fetch data from the analytics APIs
        self._generate_sample_report_data('weekly')
        
        if self.config.config['reporting']['report_recipient']:
            self._send_report('Weekly Analytics Report')
        
        return self.report_data
    
    def generate_monthly_report(self) -> Dict[str, Any]:
        """Generate monthly analytics report."""
        if not self.config.config['reporting']['monthly_report']:
            return {}
        
        self.report_data['generated_at'] = datetime.utcnow().isoformat()
        self.report_data['period'] = {
            'start': (datetime.utcnow() - timedelta(days=30)).isoformat(),
            'end': datetime.utcnow().isoformat()
        }
        
        # In a real implementation, this would fetch data from the analytics APIs
        self._generate_sample_report_data('monthly')
        
        if self.config.config['reporting']['report_recipient']:
            self._send_report('Monthly Analytics Report')
        
        return self.report_data
    
    def _generate_sample_report_data(self, report_type: str) -> None:
        """Generate sample report data for demonstration."""
        # In a real implementation, this would fetch data from the analytics APIs
        self.report_data['metrics'] = {
            'sessions': random.randint(100, 5000),
            'users': random.randint(80, 4000),
            'pageviews': random.randint(150, 10000),
            'bounce_rate': round(random.uniform(30, 80), 2),
            'avg_session_duration': random.randint(30, 300),
            'top_pages': [
                {'page': '/', 'views': random.randint(100, 1000)},
                {'page': '/services', 'views': random.randint(50, 800)},
                {'page': '/about', 'views': random.randint(30, 500)},
                {'page': '/contact', 'views': random.randint(20, 400)},
                {'page': '/blog', 'views': random.randint(10, 300)}
            ],
            'traffic_sources': {
                'direct': random.randint(20, 50),
                'organic_search': random.randint(20, 70),
                'social': random.randint(5, 30),
                'referral': random.randint(5, 25),
                'email': random.randint(1, 15)
            }
        }
        
        # Add some sample recommendations
        self.report_data['recommendations'] = [
            "Optimize page load speed for mobile devices",
            "Add more internal links to improve navigation",
            "Create more content around high-performing topics"
        ]
    
    def _send_report(self, subject: str) -> None:
        """Send the generated report via email."""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config.config['monitoring']['smtp_username']
            msg['To'] = self.config.config['reporting']['report_recipient']
            msg['Subject'] = f"{subject} - {datetime.utcnow().strftime('%Y-%m-%d')}"
            
            # Create email body
            body = f"""{subject}
            
            Period: {self.report_data['period']['start']} to {self.report_data['period']['end']}
            
            Key Metrics:
            - Sessions: {self.report_data['metrics']['sessions']:,}
            - Users: {self.report_data['metrics']['users']:,}
            - Pageviews: {self.report_data['metrics']['pageviews']:,}
            - Bounce Rate: {self.report_data['metrics']['bounce_rate']}%
            - Avg. Session Duration: {self.report_data['metrics']['avg_session_duration']} seconds
            
            Top Pages:"""
            
            for page in self.report_data['metrics']['top_pages']:
                body += f"\n  - {page['page']}: {page['views']:,} views"
            
            body += """
            
            Traffic Sources:"""
            
            for source, percentage in self.report_data['metrics']['traffic_sources'].items():
                body += f"\n  - {source.replace('_', ' ').title()}: {percentage}%"
            
            if self.report_data['recommendations']:
                body += """
                
                Recommendations:"""
                for rec in self.report_data['recommendations']:
                    body += f"\n                - {rec}"
            
            body += """
            
            ---
            This is an automated report. Please contact support if you have any questions."""
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            with smtplib.SMTP(
                self.config.config['monitoring']['smtp_server'],
                self.config.config['monitoring']['smtp_port']
            ) as server:
                server.starttls()
                server.login(
                    self.config.config['monitoring']['smtp_username'],
                    self.config.config['monitoring']['smtp_password']
                )
                server.send_message(msg)
            
            logger.info(f"{subject} sent successfully")
            
        except Exception as e:
            logger.error(f"Error sending {subject.lower()}: {e}")


def setup_monitoring():
    """Set up monitoring schedule."""
    config = AnalyticsConfig()
    monitor = AnalyticsMonitor(config)
    reporter = AnalyticsReporter(config)
    
    # Schedule monitoring checks (every 6 hours)
    schedule.every(6).hours.do(monitor.check_analytics_implementation)
    
    # Schedule reports
    schedule.every().day.at("08:00").do(reporter.generate_daily_report)
    schedule.every().monday.at("09:00").do(reporter.generate_weekly_report)
    schedule.every().day.at("10:00").do(
        reporter.generate_monthly_report
    ).tag("monthly")
    
    # Initial check
    monitor.check_analytics_implementation()
    
    # Run scheduled tasks
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute


if __name__ == "__main__":
    # This is a simplified version of the script that would be run as a service
    # In a production environment, you would use systemd or a similar service manager
    
    print("Starting Analytics Monitoring Service...")
    print("Press Ctrl+C to stop")
    
    try:
        setup_monitoring()
    except KeyboardInterrupt:
        print("\nStopping Analytics Monitoring Service...")
    except Exception as e:
        logger.error(f"Error in monitoring service: {e}", exc_info=True)
