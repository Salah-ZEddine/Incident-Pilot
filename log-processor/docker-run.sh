#!/bin/bash

# Log Processor Docker Build and Run Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Build the Docker image
build_image() {
    print_status "Building log processor Docker image..."
    docker build -t incident-pilot/log-processor:latest .
    print_status "Docker image built successfully!"
}

# Run the container
run_container() {
    print_status "Running log processor container..."
    docker run -d \
        --name incident-log-processor \
        --env-file docker.env \
        --network incident-pilot_kafka-network \
        incident-pilot/log-processor:latest
    print_status "Container started successfully!"
}

# Stop and remove the container
stop_container() {
    print_status "Stopping log processor container..."
    docker stop incident-log-processor 2>/dev/null || true
    docker rm incident-log-processor 2>/dev/null || true
    print_status "Container stopped and removed!"
}

# Show logs
show_logs() {
    print_status "Showing container logs..."
    docker logs -f incident-log-processor
}

# Show help
show_help() {
    echo "Log Processor Docker Management Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  build     Build the Docker image"
    echo "  run       Run the container"
    echo "  stop      Stop and remove the container"
    echo "  restart   Stop and start the container"
    echo "  logs      Show container logs"
    echo "  help      Show this help message"
    echo ""
}

# Main script
case "$1" in
    build)
        build_image
        ;;
    run)
        run_container
        ;;
    stop)
        stop_container
        ;;
    restart)
        stop_container
        run_container
        ;;
    logs)
        show_logs
        ;;
    help)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
