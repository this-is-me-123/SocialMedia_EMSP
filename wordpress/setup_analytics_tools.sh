#!/bin/bash
# WordPress Analytics Tools Setup Script
# This script installs and configures various analytics tools for WordPress

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== WordPress Analytics Tools Setup ===${NC}\n"

# Check if running as root
if [ "$(id -u)" -ne 0 ]; then
    echo -e "${YELLOW}Please run as root or with sudo.${NC}"
    exit 1
fi

# Install required system packages
echo -e "${GREEN}Installing required system packages...${NC}"
apt-get update
apt-get install -y python3-pip python3-venv git unzip

# Install required Python packages
echo -e "\n${GREEN}Installing Python packages...${NC}"
pip3 install requests schedule

# Create a directory for analytics tools
ANALYTICS_DIR="/opt/wordpress-analytics"
mkdir -p "$ANALYTICS_DIR"
cd "$ANALYTICS_DIR"

# Clone the analytics tools repository (if needed)
if [ ! -d "$ANALYTICS_DIR/wordpress-analytics-tools" ]; then
    echo -e "\n${GREEN}Downloading analytics tools...${NC}"
    git clone https://github.com/your-repo/wordpress-analytics-tools.git
else
    echo -e "\n${YELLOW}Analytics tools directory already exists. Updating...${NC}"
    cd "$ANALYTICS_DIR/wordpress-analytics-tools"
    git pull
fi

# Install WordPress CLI if not already installed
if ! command -v wp &> /dev/null; then
    echo -e "\n${GREEN}Installing WP-CLI...${NC}"
    curl -O https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar
    chmod +x wp-cli.phar
    mv wp-cli.phar /usr/local/bin/wp
fi

# Configure the analytics tools
echo -e "\n${GREEN}Configuring analytics tools...${NC}"

# Create a configuration file if it doesn't exist
CONFIG_FILE="$ANALYTICS_DIR/config.json"
if [ ! -f "$CONFIG_FILE" ]; then
    cat > "$CONFIG_FILE" << EOL
{
    "wordpress_path": "/var/www/wordpress",
    "analytics_tools": {
        "google_analytics": {
            "enabled": true,
            "tracking_id": ""
        },
        "microsoft_clarity": {
            "enabled": true,
            "project_id": ""
        },
        "hotjar": {
            "enabled": true,
            "site_id": ""
        },
        "matomo": {
            "enabled": false,
            "url": "",
            "site_id": ""
        },
        "plausible": {
            "enabled": false,
            "domain": ""
        },
        "fathom": {
            "enabled": false,
            "site_id": ""
        },
        "pirsch": {
            "enabled": false,
            "client_id": "",
            "client_secret": ""
        }
    },
    "monitoring": {
        "enabled": true,
        "check_interval": 3600,
        "email_alerts": {
            "enabled": true,
            "smtp_server": "smtp.example.com",
            "smtp_port": 587,
            "smtp_username": "alerts@example.com",
            "smtp_password": "your-password",
            "recipient": "admin@example.com"
        }
    },
    "reporting": {
        "daily": true,
        "weekly": true,
        "monthly": true,
        "email_recipient": "reports@example.com"
    }
}
EOL
    
    echo -e "${YELLOW}Please edit $CONFIG_FILE to configure your analytics tools.${NC}"
    echo -e "Run 'nano $CONFIG_FILE' to edit the configuration.${NC}"
    read -p "Press Enter to continue after you've edited the configuration..."
fi

# Install and configure the monitoring service
echo -e "\n${GREEN}Setting up monitoring service...${NC}"
cp "$ANALYTICS_DIR/wordpress-analytics-tools/analytics-monitor.service" /etc/systemd/system/
systemctl daemon-reload
systemctl enable analytics-monitor.service
systemctl start analytics-monitor.service

# Install WordPress plugins
echo -e "\n${GREEN}Installing WordPress plugins...${NC}"
WP_CLI="sudo -u www-data -- wp --path=/var/www/wordpress"

# Required plugins
PLUGINS=(
    "google-site-kit"
    "monsterinsights"
    "wordpress-seo"
    "wp-mail-smtp"
    "hotjar"
    "microsoft-clarity"
    "matomo-analytics"
    "plausible-analytics"
    "fathom-analytics"
    "pirsch-analytics"
)

for plugin in "${PLUGINS[@]}"; do
    echo -e "\n${GREEN}Installing $plugin...${NC}"
    $WP_CLI plugin install $plugin --activate
    
    # Configure specific plugins
    case $plugin in
        "google-site-kit")
            echo -e "${YELLOW}Please configure Google Site Kit in the WordPress admin panel.${NC}"
            ;;
        "monsterinsights")
            $WP_CLI option set monsterinsights_license ""
            $WP_CLI option set monsterinsights_license_type "plus"
            echo -e "${YELLOW}Please configure MonsterInsights in the WordPress admin panel.${NC}"
            ;;
        "hotjar")
            $WP_CLI option update hotjar_site_id ""
            echo -e "${YELLOW}Please enter your Hotjar Site ID in the WordPress admin panel.${NC}"
            ;;
    esac
done

# Set up cron jobs for reporting
echo -e "\n${GREEN}Setting up cron jobs...${NC}"
(crontab -l 2>/dev/null; echo "0 8 * * * /usr/bin/python3 $ANALYTICS_DIR/wordpress-analytics-tools/generate_report.py --daily") | crontab -
(crontab -l 2>/dev/null; echo "0 9 * * 1 /usr/bin/python3 $ANALYTICS_DIR/wordpress-analytics-tools/generate_report.py --weekly") | crontab -
(crontab -l 2>/dev/null; echo "0 10 1 * * /usr/bin/python3 $ANALYTICS_DIR/wordpress-analytics-tools/generate_report.py --monthly") | crontab -

# Set permissions
echo -e "\n${GREEN}Setting permissions...${NC}"
chown -R www-data:www-data "$ANALYTICS_DIR"
chmod -R 750 "$ANALYTICS_DIR"

# Restart services
echo -e "\n${GREEN}Restarting services...${NC}"
systemctl restart apache2
systemctl restart analytics-monitor.service

echo -e "\n${GREEN}=== Setup Complete ===${NC}"
echo -e "\nNext steps:"
echo "1. Complete the configuration in $CONFIG_FILE"
echo "2. Configure each analytics tool in the WordPress admin panel"
echo "3. Verify the monitoring service is running: systemctl status analytics-monitor"
echo -e "\n${YELLOW}Note: Some tools require additional setup in their respective dashboards.${NC}"
