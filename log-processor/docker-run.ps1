# Log Processor Docker Build and Run Script (PowerShell)

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("build", "run", "stop", "restart", "logs", "help")]
    [string]$Command
)

# Function to print colored output
function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Build the Docker image
function Build-Image {
    Write-Status "Building log processor Docker image..."
    docker build -t incident-pilot/log-processor:latest .
    if ($LASTEXITCODE -eq 0) {
        Write-Status "Docker image built successfully!"
    } else {
        Write-Error "Failed to build Docker image!"
        exit 1
    }
}

# Run the container
function Start-Container {
    Write-Status "Running log processor container..."
    docker run -d `
        --name incident-log-processor `
        --env-file docker.env `
        --network incident-pilot_kafka-network `
        incident-pilot/log-processor:latest
    if ($LASTEXITCODE -eq 0) {
        Write-Status "Container started successfully!"
    } else {
        Write-Error "Failed to start container!"
        exit 1
    }
}

# Stop and remove the container
function Stop-Container {
    Write-Status "Stopping log processor container..."
    docker stop incident-log-processor 2>$null
    docker rm incident-log-processor 2>$null
    Write-Status "Container stopped and removed!"
}

# Show logs
function Show-Logs {
    Write-Status "Showing container logs..."
    docker logs -f incident-log-processor
}

# Show help
function Show-Help {
    Write-Host "Log Processor Docker Management Script"
    Write-Host ""
    Write-Host "Usage: .\docker-run.ps1 -Command [COMMAND]"
    Write-Host ""
    Write-Host "Commands:"
    Write-Host "  build     Build the Docker image"
    Write-Host "  run       Run the container"
    Write-Host "  stop      Stop and remove the container"
    Write-Host "  restart   Stop and start the container"
    Write-Host "  logs      Show container logs"
    Write-Host "  help      Show this help message"
    Write-Host ""
}

# Main script
switch ($Command) {
    "build" {
        Build-Image
    }
    "run" {
        Start-Container
    }
    "stop" {
        Stop-Container
    }
    "restart" {
        Stop-Container
        Start-Container
    }
    "logs" {
        Show-Logs
    }
    "help" {
        Show-Help
    }
    default {
        Write-Error "Unknown command: $Command"
        Show-Help
        exit 1
    }
}
