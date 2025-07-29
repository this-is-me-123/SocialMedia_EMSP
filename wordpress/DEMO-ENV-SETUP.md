# Demo Environment Setup Guide

This guide provides instructions for setting up a local demo environment for the Encompass MSP marketing automation system. This environment is ideal for training, testing, and demonstrations.

## Prerequisites

- Docker and Docker Compose installed
- At least 8GB RAM available
- 20GB free disk space
- Git
- Node.js 14+ (for theme development)
- Composer (for PHP dependencies)

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/encompass-msp/marketing-automation-demo.git
cd marketing-automation-demo
```

### 2. Configure Environment

Copy the example environment file and update with your settings:

```bash
cp .env.example .env
```

Edit the `.env` file with your preferred settings:

```env
# WordPress
WP_HOME=https://demo.encompass-msp.local
WP_SITEURL=${WP_HOME}/wp

# Database
DB_NAME=wordpress
DB_USER=wordpress
DB_PASSWORD=password

# WordPress Security Keys
# Generate at: https://api.wordpress.org/secret-key/1.1/salt/

# Development
WP_ENV=development
WP_DEBUG=true
WP_DEBUG_LOG=true
```

### 3. Start the Environment

```bash
docker-compose up -d
```

### 4. Install WordPress

1. Open `https://demo.encompass-msp.local` in your browser
2. Complete the WordPress installation:
   - Site Title: Encompass MSP Demo
   - Username: admin
   - Password: Use a strong password
   - Email: your.email@encompass-msp.com

### 5. Import Demo Content

```bash
# Import sample data
./bin/import-sample-data.sh
```

## Detailed Setup

### System Requirements

| Component | Requirement |
|-----------|-------------|
| OS | Linux/macOS/Windows 10+ with WSL2 |
| Docker | 20.10.0+ |
| Docker Compose | 1.29.0+ |
| RAM | 8GB+ (4GB minimum) |
| CPU | 2+ cores |
| Disk Space | 20GB+ |

### Directory Structure

```
marketing-automation-demo/
├── .docker/             # Docker configuration
├── config/             # WordPress configuration
├── content/            # Themes and plugins
│   ├── plugins/        # Custom plugins
│   └── themes/         # Custom themes
├── scripts/            # Utility scripts
├── .env                # Environment configuration
├── docker-compose.yml  # Docker Compose configuration
└── README.md           # Project documentation
```

### Services

The demo environment includes:

- **WordPress** - Latest version with debug enabled
- **MySQL** - Database server
- **phpMyAdmin** - Database management
- **MailHog** - Email testing
- **Redis** - Object caching
- **Nginx** - Web server
- **Certbot** - SSL certificates

### Configuration

#### WordPress Configuration

Edit `config/application.php` to modify WordPress settings:

```php
define('WP_DEBUG', true);
define('WP_DEBUG_LOG', true);
define('WP_DEBUG_DISPLAY', false);

// Development environment
if (WP_ENV === 'development') {
    define('SAVEQUERIES', true);
    define('SCRIPT_DEBUG', true);
    define('WP_CACHE', false);
}
```

#### Plugin Configuration

Configure plugins in `content/plugins/`:

1. **Advanced Custom Fields** - Custom fields
2. **Yoast SEO** - SEO optimization
3. **Gravity Forms** - Form builder
4. **WP Rocket** - Caching (disabled in dev)
5. **Query Monitor** - Debugging

### Development Workflow

#### Starting the Environment

```bash
docker-compose up -d
```

#### Stopping the Environment

```bash
docker-compose down
```

#### Accessing Containers

```bash
# WordPress container
docker-compose exec wordpress bash

# Database container
docker-compose exec db bash
```

#### Viewing Logs

```bash
# WordPress logs
docker-compose logs wordpress

# Database logs
docker-compose logs db
```

### Demo Data

Sample data includes:
- Pages (Home, About, Services, Contact)
- Blog posts with categories
- Test products
- Form submissions
- User accounts with different roles

### Email Testing

Access MailHog at `http://localhost:8025` to view all outgoing emails.

## Training Scenarios

### Scenario 1: Email Campaign

1. Create a new email campaign
2. Design the email
3. Set up automation rules
4. Test email delivery

### Scenario 2: Lead Generation

1. Create a landing page
2. Set up a form
3. Configure lead capture
4. Test form submission

### Scenario 3: Analytics Review

1. Generate sample traffic
2. Review analytics dashboard
3. Export reports
4. Set up custom segments

## Troubleshooting

### Common Issues

#### Port Conflicts
If you get port conflicts, update the ports in `docker-compose.yml`.

#### File Permissions
If you encounter permission issues:

```bash
sudo chown -R $USER:$USER .
```

#### Database Connection Issues
Verify the database is running:

```bash
docker-compose ps
docker-compose logs db
```

### Resetting the Environment

To completely reset the demo environment:

```bash
# Stop and remove containers
docker-compose down -v

# Remove all volumes
docker volume prune

# Remove all images
docker rmi $(docker images -q)

# Start fresh
docker-compose up -d
```

## Security Considerations

- Never use default credentials in production
- Keep the demo environment isolated
- Regularly update dependencies
- Use strong passwords
- Enable SSL in production

## Support

For assistance with the demo environment:

- **Email**: support@encompass-msp.com
- **Slack**: #marketing-demo-support
- **Documentation**: [docs.encompass-msp.com](https://docs.encompass-msp.com)

## License

This demo environment is for training and evaluation purposes only. All rights reserved © Encompass MSP.

---
*Last updated: July 2025*  
*Version: 1.0.0*
