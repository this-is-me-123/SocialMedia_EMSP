# PowerShell deployment script for Dockerized Social Media Backend (Windows)
# Usage: Run from the backend directory in an elevated PowerShell terminal

Write-Host "Starting deployment for Social Media Backend..." -ForegroundColor Cyan

# 1. Check Docker
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "Docker is not installed. Please install Docker Desktop for Windows and try again." -ForegroundColor Red
    exit 1
}

# 2. Ensure Docker Desktop is running
$dockerStatus = docker info 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Docker Desktop is not running. Please start Docker Desktop and try again." -ForegroundColor Red
    exit 1
}

# 3. Check for .env file
if (-not (Test-Path .env)) {
    Write-Host ".env file not found! Please create and configure your .env file before deploying." -ForegroundColor Red
    exit 1
}

# 4. Build and start containers
Write-Host "Building and starting Docker containers..." -ForegroundColor Yellow
docker-compose up --build -d
if ($LASTEXITCODE -ne 0) {
    Write-Host "Docker Compose failed! Check your Dockerfile, docker-compose.yml, and logs for errors." -ForegroundColor Red
    exit 1
}

# 5. Show running containers
Write-Host "Deployment successful! Running containers:" -ForegroundColor Green
docker-compose ps

# 6. Show app logs (optional, comment out if not needed)
Write-Host "Showing application logs (press Ctrl+C to exit)..." -ForegroundColor Cyan
docker-compose logs -f app
