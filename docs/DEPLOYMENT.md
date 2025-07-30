# Production Deployment Guide

This guide provides step-by-step instructions for deploying the Social Media Automation System in a production environment.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Server Setup](#server-setup)
3. [Configuration](#configuration)
4. [Installation](#installation)
5. [Running as a Service](#running-as-a-service)
6. [Monitoring and Maintenance](#monitoring-and-maintenance)
7. [Backup and Recovery](#backup-and-recovery)
8. [Scaling](#scaling)

## Prerequisites

- Linux server (Ubuntu 20.04/22.04 LTS recommended)
- Python 3.8+
- Redis (for job queue and caching)
- PostgreSQL (for persistent storage)
- Nginx (as reverse proxy, optional)
- Domain name with SSL certificate (recommended)

## Server Setup

### 1. Update System Packages
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv git nginx redis-server postgresql postgresql-contrib
```

### 2. Create System User
```bash
sudo adduser --system --group --no-create-home socialmedia
sudo mkdir -p /opt/socialmedia
sudo chown -R socialmedia:socialmedia /opt/socialmedia
```

### 3. Configure PostgreSQL
```bash
sudo -u postgres createuser socialmedia
sudo -u postgres createdb socialmedia
sudo -u postgres psql -c "ALTER USER socialmedia WITH PASSWORD 'your_secure_password';"
```

## Configuration

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file with your production settings:
   ```bash
   nano .env
   ```
   - Set `TESTING=false`
   - Configure all API credentials
   - Set appropriate rate limits
   - Configure notification settings

3. Set proper file permissions:
   ```bash
   chmod 600 .env
   chown socialmedia:socialmedia .env
   ```

## Installation

1. Clone the repository (or deploy your code):
   ```bash
   sudo -u socialmedia git clone <repository-url> /opt/socialmedia
   cd /opt/socialmedia
   ```

2. Create and activate virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. Initialize the database:
   ```bash
   python -m automation_stack.init_db
   ```

## Running as a Service

### 1. Create Systemd Service
Create `/etc/systemd/system/socialmedia.service`:

```ini
[Unit]
Description=Social Media Automation Service
After=network.target postgresql.service redis-server.service

[Service]
User=socialmedia
Group=socialmedia
WorkingDirectory=/opt/socialmedia
Environment="PATH=/opt/socialmedia/venv/bin"
ExecStart=/opt/socialmedia/venv/bin/python -m automation_stack.enhanced_automation run
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 2. Create Scheduler Service
Create `/etc/systemd/system/socialmedia-scheduler.service`:

```ini
[Unit]
Description=Social Media Scheduler Service
After=network.target postgresql.service redis-server.service

[Service]
User=socialmedia
Group=socialmedia
WorkingDirectory=/opt/socialmedia
Environment="PATH=/opt/socialmedia/venv/bin"
ExecStart=/opt/socialmedia/venv/bin/python -m automation_stack.enhanced_automation scheduler
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 3. Enable and Start Services
```bash
sudo systemctl daemon-reload
sudo systemctl enable socialmedia socialmedia-scheduler
sudo systemctl start socialmedia socialmedia-scheduler
```

## Monitoring and Maintenance

### 1. Logs
View logs with:
```bash
journalctl -u socialmedia -f
journalctl -u socialmedia-scheduler -f
```

### 2. Health Checks
Configure your monitoring system to check:
```
http://your-server:8000/health
```

### 3. Log Rotation
Create `/etc/logrotate.d/socialmedia`:
```
/opt/socialmedia/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 socialmedia socialmedia
    sharedscripts
    postrotate
        systemctl reload socialmedia > /dev/null 2>&1 || true
        systemctl reload socialmedia-scheduler > /dev/null 2>&1 || true
    endscript
}
```

## Backup and Recovery

### 1. Database Backups
Add to `/etc/cron.daily/backup-socialmedia`:
```bash
#!/bin/bash
BACKUP_DIR="/var/backups/socialmedia"
mkdir -p $BACKUP_DIR
sudo -u postgres pg_dump socialmedia | gzip > $BACKUP_DIR/socialmedia-$(date +%Y%m%d).sql.gz
find $BACKUP_DIR -name "socialmedia-*.sql.gz" -mtime +30 -delete
```

### 2. Media Backups
```bash
rsync -avz /opt/socialmedia/media/ backup-server:/path/to/backup/media/
```

## Scaling

### 1. Database
- Consider using Amazon RDS or Google Cloud SQL for managed PostgreSQL
- Set up read replicas for read-heavy workloads

### 2. Redis
- Use Redis Cluster for high availability
- Configure Redis persistence

### 3. Workers
- Scale worker processes based on queue length
- Consider using Celery with multiple worker nodes

## Security Considerations

1. Keep all credentials in the `.env` file with restricted permissions
2. Use a dedicated system user for running the application
3. Keep the system and dependencies up to date
4. Configure proper firewall rules
5. Use HTTPS for all API endpoints
6. Regularly rotate API tokens and credentials

## Troubleshooting

Common issues and solutions:

1. **Authentication Failures**
   - Verify API tokens are valid and have correct permissions
   - Check token expiration and refresh if needed

2. **Rate Limiting**
   - Adjust rate limits in the configuration
   - Implement exponential backoff for retries

3. **Performance Issues**
   - Monitor database queries
   - Check Redis connection pool settings
   - Review worker concurrency settings

For additional support, please refer to the project's issue tracker or contact the development team.
