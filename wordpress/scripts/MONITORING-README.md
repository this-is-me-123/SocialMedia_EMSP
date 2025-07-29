# Marketing Automation Monitoring System

This directory contains the monitoring and alerting system for the Encompass MSP marketing automation platform. The system provides real-time monitoring of critical services, resource usage, and website availability.

## Features

- **Service Monitoring**: Tracks status of critical services (Apache, MySQL, PHP-FPM, Redis)
- **Resource Monitoring**: Monitors disk, memory, and CPU usage
- **Website Uptime**: Checks website availability and response codes
- **Alerting**: Sends email notifications for critical issues
- **Logging**: Maintains detailed logs of all checks and alerts
- **Scheduled Checks**: Runs automatically every 5 minutes

## Prerequisites

- Linux server with systemd
- Python 3.6+
- Required Python packages (will be installed automatically):
  - requests
  - python-dotenv
  - psutil
  - mysql-connector-python (optional, for future database checks)
- SMTP server access for email alerts

## Installation

1. **Clone the repository** to your server

2. **Run the setup script** (as root):
   ```bash
   chmod +x scripts/setup_monitoring.sh
   sudo ./scripts/setup_monitoring.sh
   ```

3. **Configure the environment** by editing:
   ```bash
   sudo nano /etc/marketing-automation/.env
   ```
   Update the following settings:
   - `ALERT_EMAILS`: Comma-separated list of email addresses to receive alerts
   - `FROM_EMAIL`: Sender email address
   - SMTP server details
   - Website URL to monitor

4. **Start the monitoring service**:
   ```bash
   sudo systemctl start marketing-monitoring.timer
   sudo systemctl enable marketing-monitoring.timer
   ```

## Configuration

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `ALERT_EMAILS` | Comma-separated list of email recipients | `"admin@example.com,team@example.com"` |
| `FROM_EMAIL` | Sender email address | `alerts@encompass-msp.com` |
| `SMTP_SERVER` | SMTP server for sending alerts | `smtp.office365.com` |
| `SMTP_PORT` | SMTP server port | `587` |
| `SMTP_USERNAME` | SMTP username | `alerts@encompass-msp.com` |
| `SMTP_PASSWORD` | SMTP password | `your-password` |
| `SITE_URL` | Website URL to monitor | `https://www.encompass-msp.com` |
| `DISK_THRESHOLD` | Disk usage threshold (percentage) | `80` |
| `MEMORY_THRESHOLD` | Memory usage threshold (percentage) | `85` |
| `CPU_THRESHOLD` | CPU usage threshold (percentage) | `90` |

### Critical Services

By default, the following services are monitored:
- Apache web server
- MySQL database
- PHP-FPM
- Redis cache

To modify the list of monitored services, edit the `CRITICAL_SERVICES` list in the configuration.

## Usage

### Manual Checks

Run a manual health check:
```bash
sudo /usr/local/bin/check_marketing_health.py
```

### Viewing Logs

Check the monitoring logs:
```bash
sudo tail -f /var/log/marketing-monitoring/status.log
```

### Service Management

Start/stop/restart the monitoring service:
```bash
sudo systemctl start marketing-monitoring.service  # Run checks now
sudo systemctl status marketing-monitoring.timer   # Check timer status
sudo systemctl restart marketing-monitoring.timer  # Restart timer
```

## Alert Types

The system monitors for the following conditions and sends alerts when thresholds are exceeded:

1. **High Disk Usage**: When disk usage exceeds the configured threshold
2. **High Memory Usage**: When memory usage exceeds the configured threshold
3. **High CPU Usage**: When CPU usage exceeds the configured threshold
4. **Service Outages**: When any critical service is not running
5. **Website Errors**: When the website returns an error status code or is unreachable

## Log Rotation

Logs are automatically rotated daily and kept for 30 days. The log rotation configuration can be found at:
```
/etc/logrotate.d/marketing-monitoring
```

## Troubleshooting

### Common Issues

#### Emails Not Sending
1. Verify SMTP settings in the `.env` file
2. Check the mail server logs
3. Test SMTP connectivity:
   ```bash
   telnet your-smtp-server.com 587
   ```

#### False Alerts
1. Adjust threshold values in the configuration
2. Check for resource-intensive processes
3. Verify service dependencies

#### Service Not Starting
1. Check the systemd journal:
   ```bash
   journalctl -u marketing-monitoring.service
   ```
2. Verify Python dependencies:
   ```bash
   /opt/marketing-monitoring/bin/pip list
   ```

## Security Considerations

- The `.env` file contains sensitive information and should be kept secure
- Use a dedicated email account for sending alerts
- Regularly rotate SMTP credentials
- Monitor the monitoring system itself for failures

## Maintenance

### Updating the Monitoring Script
1. Make changes to the script
2. Test manually
3. Restart the service:
   ```bash
   sudo systemctl restart marketing-monitoring.service
   ```

### Updating Dependencies
```bash
source /opt/marketing-monitoring/bin/activate
pip install -r /path/to/updated-requirements.txt
```

## Support

For assistance with the monitoring system, contact the IT team at [it-support@encompass-msp.com](mailto:it-support@encompass-msp.com).

---
*Last updated: July 2025*  
*Version: 1.0.0*
