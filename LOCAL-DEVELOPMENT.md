# Local Development Setup for Encompass Analytics

This guide will help you set up a local development environment for the Encompass Analytics WordPress plugin using Docker.

## Prerequisites

- Docker Desktop installed on your machine
- Docker Compose (usually comes with Docker Desktop)
- Git (optional, if cloning the repository)

## Setup Instructions

1. **Start the Docker containers**
   ```bash
   docker-compose up -d
   ```
   This will start:
   - WordPress at http://localhost:8000
   - phpMyAdmin at http://localhost:8080

2. **Complete WordPress Installation**
   - Open http://localhost:8000 in your browser
   - Follow the WordPress installation wizard
   - Remember your admin username and password

3. **Verify the Plugin**
   - Log in to WordPress admin at http://localhost:8000/wp-admin
   - Go to Plugins > Installed Plugins
   - Activate the "Encompass Analytics" plugin

4. **Test the Plugin**
   - Go to the Encompass Analytics settings page
   - Verify that all database tables were created
   - Test the plugin functionality

## Accessing the Database

- **phpMyAdmin**: http://localhost:8080
  - Username: root
  - Password: password

- **Direct MySQL Connection**:
  - Host: localhost
  - Port: 3306
  - Database: wordpress
  - Username: wordpress
  - Password: wordpress

## Stopping the Environment

```bash
docker-compose down
```

To remove all data (including the database):

```bash
docker-compose down -v
```

## Development Workflow

1. Make changes to the plugin files in the `encompass-analytics` directory
2. The changes will be reflected immediately in the Docker container
3. Test your changes in the WordPress admin or frontend
4. Commit and push your changes when ready

## Troubleshooting

- **Port conflicts**: If ports 8000 or 8080 are already in use, modify the `docker-compose.yml` file to use different ports
- **Plugin not showing up**: Make sure the plugin directory is correctly mounted in the `docker-compose.yml` file
- **Database connection issues**: Verify that the MySQL container is running and the credentials in `docker-compose.yml` match those in `wp-config.php`
