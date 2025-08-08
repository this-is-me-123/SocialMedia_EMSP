# SocialMedia_EMSP Deployment Guide

This directory contains the necessary files and instructions for deploying the SocialMedia_EMSP application using Docker Compose.

## Prerequisites

- Docker installed on your system
- Docker Compose installed
- Git (for cloning the repository)

## Getting Started

1. **Clone the repository** (if you haven't already):
   ```bash
   git clone <repository-url>
   cd SocialMedia_EMSP/deployment
   ```

2. **Set up environment variables**:
   - Copy `.env.example` to `.env`:
     ```bash
     copy .env.example .env
     ```
   - Edit the `.env` file with your configuration values

3. **Deploy the application**:
   - On Windows (PowerShell):
     ```powershell
     .\deploy.ps1
     ```
   - On Linux/macOS:
     ```bash
     chmod +x deploy.sh
     ./deploy.sh
     ```

## Accessing the Application

After successful deployment, you can access the following services:

- **Backend API**: http://localhost:8000
- **WordPress**: http://localhost
- **Frontend**: http://localhost:3000
- **Database**: localhost:5432

## Managing the Application

- **View logs**:
  ```bash
  docker-compose logs -f
  ```

- **Stop the application**:
  ```bash
  docker-compose down
  ```

- **Update the application**:
  ```bash
  git pull
  docker-compose down
  docker-compose up -d --build
  ```

## Backup and Restore

### Database Backup
```bash
docker-compose exec db pg_dump -U postgres socialmedia > backup_$(date +%Y%m%d).sql
```

### Database Restore
```bash
cat backup_file.sql | docker-compose exec -T db psql -U postgres socialmedia
```

## Troubleshooting

- **Port conflicts**: Ensure ports 80, 3000, and 8000 are available
- **Permission issues**: Run the deployment script as administrator/root if needed
- **Build failures**: Check the output for specific error messages

## Support

For support, please contact your system administrator or refer to the project documentation.
