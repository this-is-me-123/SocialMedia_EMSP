#!/bin/bash

# Marketing Automation Monitoring Setup Script
# This script sets up monitoring for the Encompass MSP marketing automation system

# Configuration
MONITORING_DIR="/var/log/marketing-monitoring"
CONFIG_DIR="/etc/marketing-automation"
SERVICE_USER="marketing"
LOG_FILE="/var/log/marketing-monitoring/setup.log"

# Create necessary directories
mkdir -p "$MONITORING_DIR" "$CONFIG_DIR"
touch "$LOG_FILE"

# Function to log messages
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Check if running as root
if [ "$(id -u)" -ne 0 ]; then
    log "This script must be run as root"
    exit 1
fi

log "Starting marketing automation monitoring setup..."

# Install required packages
log "Installing required packages..."
apt-get update
apt-get install -y python3-pip python3-venv cron curl jq

# Create virtual environment
log "Setting up Python virtual environment..."
python3 -m venv /opt/marketing-monitoring
source /opt/marketing-monitoring/bin/activate

# Install Python dependencies
log "Installing Python dependencies..."
cat > /tmp/requirements.txt << EOL
requests>=2.28.1
python-dotenv>=0.19.2
psutil>=5.9.0
python-dateutil>=2.8.2
mysql-connector-python>=8.0.31
EOL

pip install -r /tmp/requirements.txt
rm /tmp/requirements.txt

# Create monitoring script
log "Creating monitoring script..."
cat > /usr/local/bin/check_marketing_health.py << 'EOL'
#!/usr/bin/env python3

import os
import sys
import json
import smtplib
import socket
import subprocess
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import psutil
import mysql.connector
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/etc/marketing-automation/.env')

# Configuration
CONFIG = {
    'log_file': '/var/log/marketing-monitoring/status.log',
    'alert_emails': os.getenv('ALERT_EMAILS', '').split(','),
    'smtp_server': os.getenv('SMTP_SERVER', 'smtp.office365.com'),
    'smtp_port': int(os.getenv('SMTP_PORT', 587)),
    'smtp_username': os.getenv('SMTP_USERNAME', ''),
    'smtp_password': os.getenv('SMTP_PASSWORD', ''),
    'from_email': os.getenv('FROM_EMAIL', 'alerts@encompass-msp.com'),
    'site_url': os.getenv('SITE_URL', 'https://www.encompass-msp.com'),
    'critical_services': ['apache2', 'mysql', 'php-fpm', 'redis'],
    'disk_threshold': 80,  # Percentage
    'memory_threshold': 85,  # Percentage
    'cpu_threshold': 90,  # Percentage
}

def log_message(message, level='INFO'):
    """Log messages to file."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] [{level}] {message}"
    
    with open(CONFIG['log_file'], 'a') as f:
        f.write(log_entry + '\n')
    
    if level in ['ERROR', 'CRITICAL']:
        print(log_entry, file=sys.stderr)
    else:
        print(log_entry)

def send_alert(subject, message):
    """Send alert email."""
    if not CONFIG['alert_emails'] or not CONFIG['smtp_username']:
        log_message(f"Alert not sent - missing email configuration", 'WARNING')
        return False
    
    try:
        msg = MIMEMultipart()
        msg['From'] = CONFIG['from_email']
        msg['To'] = ', '.join(CONFIG['alert_emails'])
        msg['Subject'] = f"[Marketing Automation Alert] {subject}"
        msg.attach(MIMEText(message, 'plain'))
        
        with smtplib.SMTP(CONFIG['smtp_server'], CONFIG['smtp_port']) as server:
            server.starttls()
            server.login(CONFIG['smtp_username'], CONFIG['smtp_password'])
            server.send_message(msg)
        
        log_message(f"Alert sent: {subject}")
        return True
    except Exception as e:
        log_message(f"Failed to send alert: {str(e)}", 'ERROR')
        return False

def check_disk_usage():
    """Check disk usage."""
    try:
        disk = psutil.disk_usage('/')
        usage_percent = disk.percent
        if usage_percent > CONFIG['disk_threshold']:
            message = f"Disk usage is at {usage_percent}% (threshold: {CONFIG['disk_threshold']}%)"
            log_message(message, 'WARNING')
            send_alert("High Disk Usage", message)
            return False
        return True
    except Exception as e:
        log_message(f"Error checking disk usage: {str(e)}", 'ERROR')
        return False

def check_memory_usage():
    """Check memory usage."""
    try:
        memory = psutil.virtual_memory()
        usage_percent = memory.percent
        if usage_percent > CONFIG['memory_threshold']:
            message = f"Memory usage is at {usage_percent}% (threshold: {CONFIG['memory_threshold']}%)"
            log_message(message, 'WARNING')
            send_alert("High Memory Usage", message)
            return False
        return True
    except Exception as e:
        log_message(f"Error checking memory usage: {str(e)}", 'ERROR')
        return False

def check_cpu_usage():
    """Check CPU usage."""
    try:
        usage_percent = psutil.cpu_percent(interval=1)
        if usage_percent > CONFIG['cpu_threshold']:
            message = f"CPU usage is at {usage_percent}% (threshold: {CONFIG['cpu_threshold']}%)"
            log_message(message, 'WARNING')
            send_alert("High CPU Usage", message)
            return False
        return True
    except Exception as e:
        log_message(f"Error checking CPU usage: {str(e)}", 'ERROR')
        return False

def check_services():
    """Check if required services are running."""
    failed_services = []
    
    for service in CONFIG['critical_services']:
        try:
            result = subprocess.run(
                ['systemctl', 'is-active', '--quiet', service],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                failed_services.append(service)
        except Exception as e:
            log_message(f"Error checking service {service}: {str(e)}", 'ERROR')
            failed_services.append(service)
    
    if failed_services:
        message = f"Critical services not running: {', '.join(failed_services)}"
        log_message(message, 'CRITICAL')
        send_alert("Critical Services Down", message)
        return False
    
    return True

def check_website():
    """Check if website is accessible."""
    try:
        import requests
        response = requests.get(CONFIG['site_url'], timeout=10)
        
        if response.status_code != 200:
            message = f"Website returned status code: {response.status_code}"
            log_message(message, 'ERROR')
            send_alert("Website Error", message)
            return False
        return True
    except Exception as e:
        message = f"Website check failed: {str(e)}"
        log_message(message, 'ERROR')
        send_alert("Website Down", message)
        return False

def main():
    """Main function to run all checks."""
    log_message("Starting marketing automation health check...")
    
    # Run all checks
    checks = {
        'disk': check_disk_usage(),
        'memory': check_memory_usage(),
        'cpu': check_cpu_usage(),
        'services': check_services(),
        'website': check_website()
    }
    
    # Log summary
    failed_checks = [name for name, passed in checks.items() if not passed]
    
    if failed_checks:
        message = f"Health check failed for: {', '.join(failed_checks)}"
        log_message(message, 'ERROR')
        send_alert("Marketing Automation Health Check Failed", message)
        return 1
    
    log_message("All health checks passed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main())
EOL

# Make the script executable
chmod +x /usr/local/bin/check_marketing_health.py

# Create environment file template
log "Creating environment file template..."
cat > "$CONFIG_DIR/.env.example" << 'EOL'
# Email Configuration
ALERT_EMAILS="admin@example.com,team@example.com"
FROM_EMAIL="alerts@encompass-msp.com"
SMTP_SERVER="smtp.office365.com"
SMTP_PORT=587
SMTP_USERNAME=""
SMTP_PASSWORD=""

# Website URL
SITE_URL="https://www.encompass-msp.com"

# Database Configuration (for future use)
DB_HOST="localhost"
DB_NAME="wordpress"
DB_USER="wordpress"
DB_PASSWORD=""
EOL

# Create actual environment file if it doesn't exist
if [ ! -f "$CONFIG_DIR/.env" ]; then
    cp "$CONFIG_DIR/.env.example" "$CONFIG_DIR/.env"
    log "Please edit $CONFIG_DIR/.env with your configuration"
else
    log "Environment file already exists, skipping creation"
fi

# Set up log rotation
log "Configuring log rotation..."
cat > /etc/logrotate.d/marketing-monitoring << 'EOL'
/var/log/marketing-monitoring/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 marketing marketing
    sharedscripts
    postrotate
        systemctl reload rsyslog >/dev/null 2>&1 || true
    endscript
}
EOL

# Create systemd service
log "Creating systemd service..."
cat > /etc/systemd/system/marketing-monitoring.service << 'EOL'
[Unit]
Description=Marketing Automation Monitoring
After=network.target

[Service]
Type=oneshot
User=root
ExecStart=/usr/local/bin/check_marketing_health.py
EnvironmentFile=/etc/marketing-automation/.env

[Install]
WantedBy=multi-user.target
EOL

# Create systemd timer
cat > /etc/systemd/system/marketing-monitoring.timer << 'EOL'
[Unit]
Description=Run marketing monitoring every 5 minutes

[Timer]
OnBootSec=5min
OnUnitActiveSec=5min
Unit=marketing-monitoring.service

[Install]
WantedBy=timers.target
EOL

# Set permissions
chown -R $SERVICE_USER:$SERVICE_USER "$MONITORING_DIR"
chmod 755 /usr/local/bin/check_marketing_health.py
chmod 600 "$CONFIG_DIR/.env"
chmod 644 "$CONFIG_DIR/.env.example"

# Reload systemd and enable services
systemctl daemon-reload
systemctl enable marketing-monitoring.timer
systemctl start marketing-monitoring.timer

log "Marketing automation monitoring setup complete!"
log "Please configure $CONFIG_DIR/.env with your settings"
log "Monitoring logs can be found in $MONITORING_DIR"
