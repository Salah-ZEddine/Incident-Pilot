# Log Processor Docker Deployment

This directory contains the Docker configuration for the Incident Pilot Log Processor service.

## 📋 Prerequisites

- Docker and Docker Compose installed
- All infrastructure services running (PostgreSQL, Kafka, Redis)

## 🏗️ Building the Image

### Option 1: Using Docker Compose (Recommended)
```bash
# From the project root directory
cd your/project/directory
docker-compose build log-processor
```

### Option 2: Using Docker Build
```bash
# From the log-processor directory
cd your/project/directory
docker build -t incident-pilot/log-processor:latest .
```

### Option 3: Using Helper Scripts
```bash
# Linux/Mac
./docker-run.sh build

# Windows PowerShell
.\docker-run.ps1 -Command build
```

## 🚀 Running the Service

### Option 1: Using Docker Compose (Recommended)
```bash
# Start all services including log-processor
docker-compose up -d

# Start only log-processor (dependencies must be running)
docker-compose up -d log-processor
```

### Option 2: Using Docker Run
```bash
docker run -d \
  --name incident-log-processor \
  --env-file docker.env \
  --network incident-pilot_kafka-network \
  incident-pilot/log-processor:latest
```

### Option 3: Using Helper Scripts
```bash
# Linux/Mac
./docker-run.sh run

# Windows PowerShell
.\docker-run.ps1 -Command run
```

## 📊 Monitoring

### View Logs
```bash
# Using Docker Compose
docker-compose logs -f log-processor

# Using Docker
docker logs -f incident-log-processor

# Using helper scripts
./docker-run.sh logs          # Linux/Mac
.\docker-run.ps1 -Command logs  # Windows
```

### Check Health Status
```bash
# Check container health
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Check specific health
docker inspect incident-log-processor --format='{{.State.Health.Status}}'
```

## 🔧 Configuration

### Environment Variables

The service can be configured using environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `POSTGRES_HOST` | PostgreSQL hostname | `postgres` |
| `POSTGRES_PORT` | PostgreSQL port | `5432` |
| `POSTGRES_USER` | PostgreSQL username | - |
| `POSTGRES_PASSWORD` | PostgreSQL password | - |
| `POSTGRES_DB` | PostgreSQL database | - |
| `KAFKA_BOOTSTRAP_SERVERS` | Kafka servers | `kafka:9092` |
| `KAFKA_TOPIC_INPUT` | Input topic name | `logs_raw` |
| `KAFKA_TOPIC_OUTPUT` | Output topic name | `logs_fact` |
| `KAFKA_GROUP_ID` | Consumer group ID | `log-processor-group` |
| `REDIS_HOST` | Redis hostname | `redis` |
| `REDIS_PORT` | Redis port | `6379` |
| `LOG_LEVEL` | Logging level | `INFO` |

### Configuration Files

- `docker.env` - Docker-specific environment variables
- `.env` - Local development environment variables

## 🛠️ Troubleshooting

### Common Issues

1. **Container fails to start**
   ```bash
   # Check logs for errors
   docker logs incident-log-processor
   
   # Check if dependencies are running
   docker ps | grep -E "(postgres|kafka|redis)"
   ```

2. **Cannot connect to services**
   ```bash
   # Verify network connectivity
   docker network ls
   docker network inspect incident-pilot_kafka-network
   ```

3. **Permission issues**
   ```bash
   # The container runs as non-root user 'logprocessor'
   # Check file permissions if mounting volumes
   ```

### Health Checks

The container includes health checks that verify:
- Python environment is working
- Configuration can be loaded
- Basic application startup

### Debugging

For debugging, you can run the container interactively:

```bash
docker run -it --rm \
  --env-file docker.env \
  --network incident-pilot_kafka-network \
  incident-pilot/log-processor:latest \
  /bin/bash
```

## 🔄 Management Commands

### Stop the Service
```bash
# Using Docker Compose
docker-compose stop log-processor

# Using Docker
docker stop incident-log-processor

# Using helper scripts
./docker-run.sh stop
.\docker-run.ps1 -Command stop
```

### Restart the Service
```bash
# Using Docker Compose
docker-compose restart log-processor

# Using helper scripts
./docker-run.sh restart
.\docker-run.ps1 -Command restart
```

### Remove the Service
```bash
# Using Docker Compose
docker-compose down log-processor

# Using Docker
docker stop incident-log-processor
docker rm incident-log-processor
```

## 📁 File Structure

```
log-processor/
├── app/                    # Application code
├── Dockerfile             # Docker image definition
├── .dockerignore          # Files to exclude from build
├── docker.env             # Docker environment variables
├── docker-run.sh          # Linux/Mac helper script
├── docker-run.ps1         # Windows PowerShell helper script
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

## 🏷️ Image Information

- **Base Image**: `python:3.11-slim`
- **Working Directory**: `/app`
- **User**: `logprocessor` (non-root)
- **Exposed Port**: `8000` (for future monitoring/metrics)
- **Health Check**: Every 30 seconds

## 📈 Performance

The Docker image is optimized for:
- Small size using slim base image
- Fast startup with layer caching
- Security with non-root user
- Health monitoring
- Graceful shutdown handling

## License  
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)  

This project is licensed under the **GNU General Public License v3.0**. See the [LICENSE](https://github.com/Salah-ZEddine/Incident-Pilot/blob/master/LICENSE) file for full terms.

## 🙋‍♂️ Support

- **Documentation**: [Wiki](https://github.com/Salah-ZEddine/Incident-Pilot/wiki)
- **Issues**: [GitHub Issues](https://github.com/Salah-ZEddine/Incident-Pilot/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Salah-ZEddine/Incident-Pilot/discussions)

---

**Built with ❤️ for reliable incident management**