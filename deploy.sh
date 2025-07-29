#!/bin/bash
# Deployment script for Social Media Automation System
# Usage: ./deploy.sh [environment]

set -euo pipefail

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
ENV=${1:-staging}
DEPLOY_USER="socialmedia"
APP_DIR="/opt/socialmedia"
BACKUP_DIR="/var/backups/socialmedia"
LOG_DIR="/var/log/socialmedia"

# Validate environment
if [[ ! "$ENV" =~ ^(staging|production)$ ]]; then
  echo -e "${RED}Error: Invalid environment. Use 'staging' or 'production'.${NC}"
  exit 1
fi

# Check if running as root
if [ "$(id -u)" -ne 0 ]; then
  echo -e "${RED}Error: This script must be run as root${NC}"
  exit 1
fi

# Load environment specific settings
load_environment() {
  echo -e "${YELLOW}Loading $ENV environment settings...${NC}"
  
  if [ "$ENV" = "production" ]; then
    # Production settings
    GIT_BRANCH="main"
    PORT=8000
  else
    # Staging settings
    GIT_BRANCH="develop"
    PORT=8001
  fi
  
  echo -e "  Branch: ${GREEN}$GIT_BRANCH${NC}"
  echo -e "  Port: ${GREEN}$PORT${NC}"
}

# Create required directories
create_directories() {
  echo -e "${YELLOW}Creating directories...${NC}"
  
  for dir in "$APP_DIR" "$BACKUP_DIR" "$LOG_DIR"; do
    if [ ! -d "$dir" ]; then
      echo "Creating directory: $dir"
      mkdir -p "$dir"
      chown -R $DEPLOY_USER:$DEPLOY_USER "$dir"
      chmod 750 "$dir"
    else
      echo "Directory exists: $dir"
    fi
  done
}

# Setup Python virtual environment
setup_venv() {
  echo -e "${YELLOW}Setting up Python virtual environment...${NC}"
  
  if [ ! -d "$APP_DIR/venv" ]; then
    echo "Creating virtual environment..."
    sudo -u $DEPLOY_USER python3 -m venv "$APP_DIR/venv"
  fi
  
  # Activate virtual environment
  source "$APP_DIR/venv/bin/activate"
  
  # Upgrade pip and install requirements
  echo "Installing dependencies..."
  pip install --upgrade pip
  pip install -r "$APP_DIR/requirements.txt"
  
  deactivate
}

# Configure systemd services
setup_services() {
  echo -e "${YELLOW}Configuring systemd services...${NC}"
  
  # Copy service files
  cp "$APP_DIR/deployment/socialmedia-health.service" "/etc/systemd/system/socialmedia-health.service"
  
  # Replace placeholders
  sed -i "s|{{APP_DIR}}|$APP_DIR|g" "/etc/systemd/system/socialmedia-health.service"
  sed -i "s|{{PORT}}|$PORT|g" "/etc/systemd/system/socialmedia-health.service"
  
  # Reload systemd
  systemctl daemon-reload
  
  # Enable and start services
  for service in socialmedia-health; do
    echo "Enabling and starting $service..."
    systemctl enable $service
    systemctl restart $service
  done
}

# Setup log rotation
setup_logrotate() {
  echo -e "${YELLOW}Configuring log rotation...${NC}"
  
  cp "$APP_DIR/deployment/socialmedia-logrotate" "/etc/logrotate.d/socialmedia"
  chmod 644 "/etc/logrotate.d/socialmedia"
  
  # Test logrotate configuration
  if logrotate -d "/etc/logrotate.d/socialmedia" >/dev/null 2>&1; then
    echo "Log rotation configured successfully"
  else
    echo -e "${RED}Error in logrotate configuration${NC}"
    exit 1
  fi
}

# Setup cron jobs
setup_cron() {
  echo -e "${YELLOW}Configuring scheduled tasks...${NC}"
  
  # Copy cron configuration
  cp "$APP_DIR/deployment/backup-cron" "/etc/cron.d/socialmedia-backup"
  chmod 644 "/etc/cron.d/socialmedia-backup"
  
  echo "Scheduled tasks configured"
}

# Setup monitoring
setup_monitoring() {
  echo -e "${YELLOW}Configuring monitoring...${NC}"
  
  # Copy alert rules
  mkdir -p "/etc/prometheus/rules.d"
  cp "$APP_DIR/monitoring/alerts.yml" "/etc/prometheus/rules.d/socialmedia.yml"
  
  # Restart Prometheus if installed
  if systemctl is-active --quiet prometheus; then
    systemctl restart prometheus
    echo "Prometheus configuration updated"
  else
    echo -e "${YELLOW}Prometheus not running, alerts will be active after Prometheus is configured${NC}"
  fi
}

# Verify deployment
verify_deployment() {
  echo -e "${YELLOW}Verifying deployment...${NC}"
  
  # Check services
  for service in socialmedia-health; do
    if systemctl is-active --quiet $service; then
      echo -e "  ${GREEN}✓${NC} $service is running"
    else
      echo -e "  ${RED}✗${NC} $service is not running"
      exit 1
    fi
  done
  
  # Run verification script
  echo "Running deployment verification..."
  if sudo -u $DEPLOY_USER "$APP_DIR/venv/bin/python" "$APP_DIR/scripts/verify_deployment.py"; then
    echo -e "${GREEN}✓ Deployment verification passed${NC}"
  else
    echo -e "${RED}✗ Deployment verification failed${NC}"
    exit 1
  fi
}

# Main deployment function
deploy() {
  echo -e "${GREEN}Starting $ENV deployment...${NC}"
  
  load_environment
  create_directories
  
  # Clone or update code
  if [ -d "$APP_DIR/.git" ]; then
    echo -e "${YELLOW}Updating code from $GIT_BRANCH...${NC}"
    cd "$APP_DIR"
    sudo -u $DEPLOY_USER git fetch origin
    sudo -u $DEPLOY_USER git checkout "$GIT_BRANCH"
    sudo -u $DEPLOY_USER git pull origin "$GIT_BRANCH"
  else
    echo -e "${RED}Git repository not found in $APP_DIR${NC}"
    exit 1
  fi
  
  # Set permissions
  chown -R $DEPLOY_USER:$DEPLOY_USER "$APP_DIR"
  find "$APP_DIR" -type d -exec chmod 750 {} \;
  find "$APP_DIR" -type f -exec chmod 640 {} \;
  chmod 750 "$APP_DIR/scripts/"*.py
  chmod 750 "$APP_DIR/automation_stack/"*.py
  
  setup_venv
  setup_services
  setup_logrotate
  setup_cron
  setup_monitoring
  
  # Restart services
  systemctl daemon-reload
  systemctl restart socialmedia-*
  
  verify_deployment
  
  echo -e "${GREEN}Deployment to $ENV completed successfully!${NC}"
  echo -e "\nNext steps:"
  echo "1. Verify services: systemctl status socialmedia-"*
  echo "2. Check logs: journalctl -u socialmedia-health -f"
  echo "3. Access health check: http://localhost:$PORT/health"
}

# Run deployment
echo -e "${YELLOW}=== Social Media Automation System Deployment ===${NC}"
echo -e "Environment: ${GREEN}$ENV${NC}"
echo -e "Running as: ${GREEN}$(whoami)${NC}"

read -p "Proceed with deployment? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
  deploy
else
  echo -e "${YELLOW}Deployment cancelled${NC}"
  exit 0
fi
