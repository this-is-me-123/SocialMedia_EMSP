# Social Media Automation System - Deployment Guide

This guide provides step-by-step instructions for deploying the Social Media Automation System in both development and production environments.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Detailed Deployment](#detailed-deployment)
   - [Server Setup](#server-setup)
   - [Database Setup](#database-setup)
   - [Application Setup](#application-setup)
   - [Monitoring Setup](#monitoring-setup)
4. [Configuration](#configuration)
5. [Maintenance](#maintenance)
6. [Troubleshooting](#troubleshooting)

## Prerequisites

### Hardware Requirements
- CPU: 2+ cores
- RAM: 4GB+ (8GB recommended for production)
- Storage: 20GB+ (SSD recommended)

### Software Requirements
- Ubuntu 20.04/22.04 LTS (recommended)
- Python 3.8+
- PostgreSQL 13+
- Redis 6+
- Nginx (for production)
- Docker (optional, for containerized deployment)

### Network Requirements
- Port 80/443 (HTTP/HTTPS)
- Port 8000 (Application)
- Port 5432 (PostgreSQL)
- Port 6379 (Redis)
- Port 9090 (Prometheus)
- Port 3000 (Grafana, if using)

## Quick Start

For a quick deployment on a fresh Ubuntu server:

```bash
# Clone the repository
sudo apt update && sudo apt install -y git
sudo mkdir -p /opt/socialmedia
sudo chown -R $USER:$USER /opt/socialmedia
git clone https://github.com/your-org/socialmedia-automation.git /opt/socialmedia

# Run the deployment script
cd /opt/socialmedia
chmod +x deploy.sh
sudo ./deploy.sh production
```

## Detailed Deployment

### Server Setup

1. **Update System Packages**
   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo apt install -y software-properties-common
   ```

2. **Install Required Packages**
   ```bash
   # Python and build dependencies
   sudo apt install -y python3-pip python3-venv python3-dev build-essential \
       libpq-dev redis-server nginx postgresql postgresql-contrib
   ```

3. **Create System User**
   ```bash
   sudo useradd -r -s /bin/false socialmedia
   sudo mkdir -p /var/log/socialmedia
   sudo chown -R socialmedia:socialmedia /var/log/socialmedia
   ```

### Database Setup

1. **Configure PostgreSQL**
   ```bash
   sudo -u postgres createuser -P socialmedia
   sudo -u postgres createdb -O socialmedia socialmedia
   
   # Allow connections from localhost (update pg_hba.conf for production)
   echo "host    socialmedia    socialmedia    127.0.0.1/32    md5" | sudo tee -a /etc/postgresql/*/main/pg_hba.conf
   sudo systemctl restart postgresql
   ```

2. **Initialize Database**
   ```bash
   cd /opt/socialmedia
   sudo -u socialmedia python3 -m automation_stack.init_db
   ```

### Application Setup

1. **Install Dependencies**
   ```bash
   cd /opt/socialmedia
   python3 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   nano .env
   ```

3. **Set Up Systemd Services**
   ```bash
   sudo cp deployment/socialmedia-health.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable socialmedia-health
   sudo systemctl start socialmedia-health
   ```

4. **Set Up Log Rotation**
   ```bash
   sudo cp deployment/socialmedia-logrotate /etc/logrotate.d/socialmedia
   ```

### Monitoring Setup

1. **Install Prometheus and Node Exporter**
   ```bash
   wget https://github.com/prometheus/prometheus/releases/download/v2.30.3/prometheus-2.30.3.linux-amd64.tar.gz
   tar xvfz prometheus-*.tar.gz
   sudo cp prometheus-*.linux-amd64/prometheus /usr/local/bin/
   sudo cp prometheus-*.linux-amd64/promtool /usr/local/bin/
   sudo mkdir -p /etc/prometheus
   sudo mkdir -p /var/lib/prometheus
   
   # Configure Prometheus
   sudo cp monitoring/prometheus.yml /etc/prometheus/
   sudo cp monitoring/alerts.yml /etc/prometheus/rules.d/
   ```

2. **Set Up Prometheus Service**
   ```bash
   sudo cp monitoring/prometheus.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable prometheus
   sudo systemctl start prometheus
   ```

3. **Install Grafana (Optional)**
   ```bash
   sudo apt-get install -y apt-transport-https
   sudo apt-get install -y software-properties-common wget
   wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
   echo "deb https://packages.grafana.com/oss/deb stable main" | sudo tee -a /etc/apt/sources.list.d/grafana.list
   sudo apt-get update
   sudo apt-get install -y grafana
   
   # Import dashboard
   sudo cp monitoring/grafana-dashboard.json /var/lib/grafana/dashboards/
   
   sudo systemctl daemon-reload
   sudo systemctl enable grafana-server
   sudo systemctl start grafana-server
   ```

## Configuration

### Environment Variables

Create a `.env` file in the application root with the following variables:

```ini
# Application
DEBUG=False
SECRET_KEY=your-secret-key
TIMEZONE=UTC

# Database
DB_NAME=socialmedia
DB_USER=socialmedia
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# Storage
STORAGE_PATH=/var/lib/socialmedia

# Social Media API Keys
INSTAGRAM_API_KEY=your-instagram-key
FACEBOOK_API_KEY=your-facebook-key
TWITTER_API_KEY=your-twitter-key
TIKTOK_API_KEY=your-tiktok-key

# Monitoring
PROMETHEUS_ENABLED=True
PROMETHEUS_PORT=8001
```

## Maintenance

### Backups

Automatic daily backups are configured via cron. To perform a manual backup:

```bash
sudo -u socialmedia python3 /opt/socialmedia/scripts/backup_restore.py backup
```

### Updates

To update the application:

```bash
cd /opt/socialmedia
sudo -u socialmedia git pull
sudo systemctl restart socialmedia-*
```

### Logs

View application logs:
```bash
sudo journalctl -u socialmedia-health -f
```

## Troubleshooting

### Common Issues

1. **Service Fails to Start**
   - Check logs: `journalctl -u socialmedia-health -n 50`
   - Verify database connection
   - Check environment variables in `.env`

2. **Database Connection Issues**
   - Verify PostgreSQL is running: `sudo systemctl status postgresql`
   - Check connection settings in `.env`
   - Verify user permissions in PostgreSQL

3. **High Resource Usage**
   - Check running processes: `htop`
   - Review logs for errors
   - Adjust resource limits if needed

### Getting Help

For additional support, please open an issue in the project repository or contact the development team.

## Security Considerations

- Always use HTTPS in production
- Keep system packages up to date
- Use strong passwords for all services
- Regularly rotate API keys and credentials
- Monitor system logs for suspicious activity

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
