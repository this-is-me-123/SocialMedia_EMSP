# Deployment Script for SocialMedia_EMSP
# This script helps with deploying the application using Docker Compose

# Set error action preference
$ErrorActionPreference = "Stop"

# Function to write colored output
function Write-Info {
    param($message)
    Write-Host "[INFO] $message" -ForegroundColor Cyan
}

function Write-Success {
    param($message)
    Write-Host "[SUCCESS] $message" -ForegroundColor Green
}

function Write-Warning {
    param($message)
    Write-Host "[WARNING] $message" -ForegroundColor Yellow
}

function Write-Error {
    param($message)
    Write-Host "[ERROR] $message" -ForegroundColor Red
}

# Check if .env exists, if not, create from .env.example
if (-not (Test-Path .env)) {
    Write-Info "Creating .env file from .env.example..."
    try {
        Copy-Item .env.example -Destination .env -ErrorAction Stop
        Write-Success "Created .env file. Please review and update the configuration if needed."
    } catch {
        Write-Error "Failed to create .env file: $_"
        exit 1
    }
}

# Function to check if a command exists
function Test-CommandExists {
    param($command)
    return $null -ne (Get-Command $command -ErrorAction SilentlyContinue)
}

# Check for Docker and Docker Compose
Write-Info "Checking system requirements..."
$dependencies = @(
    @{ Name = "Docker"; Command = "docker" },
    @{ Name = "Docker Compose"; Command = "docker-compose" }
)

$missingDeps = @()
foreach ($dep in $dependencies) {
    if (-not (Test-CommandExists $dep.Command)) {
        $missingDeps += $dep.Name
    }
}

if ($missingDeps.Count -gt 0) {
    Write-Error "The following required dependencies are missing:`n$($missingDeps -join "`n")"
    Write-Info "Please install the missing dependencies and try again."
    exit 1
}

# Check if Docker is running
try {
    docker info | Out-Null
} catch {
    Write-Error "Docker is not running. Please start Docker Desktop and try again."
    exit 1
}

# Build and start containers
Write-Info "Building and starting containers..."
try {
    # Pull latest images
    docker-compose pull --ignore-pull-failures
    
    # Build and start services
    docker-compose up -d --build
    
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to start containers"
    }
    
    # Show container status
    Write-Info "Container status:"
    docker-compose ps
    
    # Show service URLs
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  Deployment completed successfully!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Services:" -ForegroundColor Yellow
    Write-Host "- Backend API:    http://localhost:8000"
    Write-Host "- WordPress:      http://localhost"
    Write-Host "- Database Admin: http://localhost:8080 (if enabled)"
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Complete WordPress installation at http://localhost"
    Write-Host "2. Verify backend API is running at http://localhost:8000"
    Write-Host ""
    Write-Host "Management commands:" -ForegroundColor Yellow
    Write-Host "- View logs:        docker-compose logs -f"
    Write-Host "- Stop services:    docker-compose down"
    Write-Host "- Rebuild services: docker-compose up -d --build"
    Write-Host ""
    
} catch {
    Write-Error "Deployment failed: $_"
    Write-Info "Troubleshooting steps:"
    Write-Host "1. Check if Docker is running"
    Write-Host "2. Check for port conflicts (80, 8000, 5432)"
    Write-Host "3. View logs: docker-compose logs"
    Write-Host "4. Try rebuilding: docker-compose up -d --build --force-recreate"
    Write-Host ""
    exit 1
}
