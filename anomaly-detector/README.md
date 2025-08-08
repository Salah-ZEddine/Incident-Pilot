# 🚨 Incident Pilot - Anomaly Detector

A sophisticated real-time anomaly detection service that analyzes log facts and generates intelligent alerts for incident management.

## 📋 Overview

The Anomaly Detector is a critical component of the Incident Pilot system that:

- 📥 **Consumes** processed facts from Kafka topic `logs_fact`
- 🔍 **Analyzes** facts using configurable rule-based detection engine
- 🚨 **Generates** actionable alerts for detected anomalies
- 💾 **Stores** alerts in PostgreSQL database for incident management
- ⚡ **Processes** facts in real-time with sub-second latency

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Kafka Topic   │───▶│ Anomaly Detector │───▶│   PostgreSQL    │
│   (logs_fact)   │    │     Service      │    │   (alerts)      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │   Rules Engine   │
                       │  (JSON Rules)    │
                       └──────────────────┘
```

### Components

- **🎯 FactHandler**: Core anomaly processing engine
- **🔧 Rules Engine**: JSON-based configurable rule system
- **💾 Database Service**: PostgreSQL integration for alert storage
- **📡 Kafka Service**: Message consumption and processing
- **🏷️ Alert Generation**: Intelligent alert creation with context

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ 
- PostgreSQL database
- Kafka cluster
- Redis (for caching)

### Installation

```bash
# Clone and navigate
cd your\path\to\anomaly-detector

# Install dependencies
npm install

# Set up environment
cp .env.example .env
# Edit .env with your configuration

# Build TypeScript
npm run build

# Start the service
npm start
```

### Development Mode

```bash
# Run in development with hot reload
npm run dev

# Run tests
npm test

# Lint code
npm run lint
```

## 🐳 Docker Deployment

### Build Docker Image

```bash
# Build the image
docker build -t incident-pilot/anomaly-detector:latest .

# Or use Docker Compose
docker-compose build anomaly-detector
```

### Run with Docker

```bash
# Standalone container
docker run -d \
  --name anomaly-detector \
  --env-file .env \
  --network incident-pilot_network \
  incident-pilot/anomaly-detector:latest

# Or with Docker Compose
docker-compose up -d anomaly-detector
```

### Docker Compose Integration

```yaml
services:
  anomaly-detector:
    build:
      context: ./anomaly-detector
      dockerfile: Dockerfile
    container_name: incident-anomaly-detector
    depends_on:
      - postgres
      - kafka
      - redis
    environment:
      - POSTGRES_HOST=postgres
      - POSTGRES_PORT=5432
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=${POSTGRES_DB}
      - KAFKA_BOOTSTRAP_SERVERS=kafka:9092
      - KAFKA_FACT_TOPIC=logs_fact
      - REDIS_HOST=redis
      - REDIS_PORT=6379
    networks:
      - incident-pilot_network
    restart: unless-stopped
```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `POSTGRES_HOST` | PostgreSQL hostname | `localhost` | ✅ |
| `POSTGRES_PORT` | PostgreSQL port | `5432` | ✅ |
| `POSTGRES_USER` | PostgreSQL username | - | ✅ |
| `POSTGRES_PASSWORD` | PostgreSQL password | - | ✅ |
| `POSTGRES_DB` | PostgreSQL database | - | ✅ |
| `KAFKA_BOOTSTRAP_SERVERS` | Kafka brokers | `localhost:9092` | ✅ |
| `KAFKA_FACT_TOPIC` | Input topic name | `logs_fact` | ✅ |
| `KAFKA_GROUP_ID` | Consumer group ID | `anomaly-detector-group` | ❌ |
| `LOG_LEVEL` | Logging level | `info` | ❌ |
| `NODE_ENV` | Environment | `development` | ❌ |

### Sample .env File

```bash
# Database Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=incident_user
POSTGRES_PASSWORD=incident_pass
POSTGRES_DB=incident_db

# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_FACT_TOPIC=logs_fact
KAFKA_GROUP_ID=anomaly-detector-group



# Application Configuration
LOG_LEVEL=info
NODE_ENV=development
```

## 📋 Anomaly Detection Rules

### Rule Structure

Rules are defined in JSON format in the `rules/` directory:

```json
{
  "name": "high-error-rate",
  "conditions": {
    "all": [
      {
        "fact": "repeated_error_count",
        "operator": "greaterThan",
        "value": 10
      }
    ]
  },
  "event": {
    "type": "high-error-rate",
    "params": {
      "severity": "high",
      "description": "High error rate detected"
    }
  }
}
```

### Built-in Rules

| Rule Name | Condition | Severity | Description |
|-----------|-----------|----------|-------------|
| **High Error Rate** | `repeated_error_count > 10` | High | Detects elevated error frequencies |
| **Potential Scraper** | `potential_scraper = true` | Medium | Identifies web scraping activity |
| **Silence Detection** | `is_silent = true` | Medium | Detects service outages |
| **Failed System Calls** | `failed_syscall = true` | Critical | System-level operation failures |
| **Unauthorized Access** | `unauthorized_count > 3` | Critical | Security breach attempts |

### Custom Rules

Add custom rules by creating JSON files in the `rules/` directory:

```bash
# Create a new rule
echo '{
  "name": "custom-rule",
  "conditions": {
    "all": [
      { "fact": "your_fact_field", "operator": "greaterThan", "value": 5 }
    ]
  },
  "event": {
    "type": "custom-anomaly",
    "params": { "severity": "medium" }
  }
}' > rules/custom-rule.json
```

## 🚨 Alert Schema

Generated alerts follow this structure:

```typescript
interface Alert {
  alert_id?: string;           // Auto-generated UUID
  timestamp: Date;             // Detection timestamp
  rule_name: string;           // Human-readable rule name
  description: string;         // Detailed description
  severity: 'low'|'medium'|'high'|'critical';
  log_reference_ids: string[]; // Referenced log entries
  tags: string[];              // Categorization tags
  detected_by: string;         // Detection service identifier
  suggested_action: string;    // Recommended response
  facts: Record<string, any>;  // Context data
}
```

### Sample Alert

```json
{
  "alert_id": "123e4567-e89b-12d3-a456-426614174000",
  "timestamp": "2025-08-08T10:30:00Z",
  "rule_name": "High Error Rate Detection",
  "description": "High error rate detected from web-server-01: 15 errors in 2-minute timeframe (75% error rate)",
  "severity": "high",
  "log_reference_ids": ["web-server-01-2025-08-08T10:30:00Z"],
  "tags": ["anomaly-detection", "performance", "errors", "source:web-server-01", "severity:high"],
  "detected_by": "anomaly-detector-service",
  "suggested_action": "Investigate error logs, check system resources, review recent deployments",
  "facts": {
    "source": "web-server-01",
    "anomaly_type": "high-error-rate",
    "error_count": 15,
    "timestamp": "2025-08-08T10:30:00Z"
  }
}
```

## 📊 Monitoring & Observability

### Health Checks

```bash
# Check service health
curl http://localhost:3000/health

# Check database connectivity
curl http://localhost:3000/health/database

# Check Kafka connectivity  
curl http://localhost:3000/health/kafka
```

### Metrics

The service exposes metrics for monitoring:

- **Facts Processed**: Total facts analyzed
- **Anomalies Detected**: Total anomalies found
- **Alerts Generated**: Total alerts created
- **Processing Latency**: Average fact processing time
- **Rule Execution Time**: Rule engine performance
- **Database Operations**: Insert/query performance

### Logs

```bash
# View service logs
docker logs -f anomaly-detector

# Filter by log level
docker logs anomaly-detector 2>&1 | grep "ERROR"

# Real-time monitoring
tail -f logs/anomaly-detector.log
```

## 🧪 Testing

### Unit Tests

```bash
# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run specific test file
npm test -- FactHandler.test.ts
```

### Integration Tests

```bash
# End-to-end testing
npm run test:e2e

# Database integration tests
npm run test:db

# Kafka integration tests
npm run test:kafka
```

### Load Testing

```bash
# Generate test facts
npm run generate-test-facts

# Stress test
npm run stress-test
```

## 🔧 Development

### Project Structure

```
anomaly-detector/
├── src/
│   ├── index.ts              # Main application entry
│   ├── services/
│   │   ├── FactHandler.ts    # Core anomaly processing
│   │   └── KafkaService.ts   # Kafka integration
│   ├── db/
│   │   ├── Idatabase.ts      # Database interface
│   │   └── postgres.databse.ts # PostgreSQL implementation
│   ├── types/
│   │   ├── Alert.ts          # Alert type definitions
│   │   └── Fact.ts           # Fact type definitions
│   └── config/
│       └── postgres.config.ts # Database configuration
├── rules/                    # Anomaly detection rules
├── tests/                    # Test files
├── dist/                     # Compiled JavaScript
├── Dockerfile               # Docker configuration
├── package.json             # Node.js dependencies
├── tsconfig.json            # TypeScript configuration
└── README.md                # This file
```

### Adding New Rules

1. **Create Rule File**: Add JSON rule to `rules/` directory
2. **Test Rule**: Verify rule logic with test facts
3. **Update Documentation**: Document rule in README
4. **Deploy**: Restart service to load new rules

### Database Schema

```sql
CREATE TABLE alerts (
  alert_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
  rule_name VARCHAR(255) NOT NULL,
  description TEXT NOT NULL,
  severity VARCHAR(50) NOT NULL CHECK (severity IN ('low', 'medium', 'high', 'critical')),
  log_reference_ids TEXT[] DEFAULT '{}',
  tags TEXT[] DEFAULT '{}',
  detected_by VARCHAR(255) NOT NULL,
  suggested_action TEXT NOT NULL,
  facts JSONB DEFAULT '{}',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## 🚨 Troubleshooting

### Common Issues

#### 1. **Service Won't Start**
```bash
# Check configuration
npm run config:validate

# Verify dependencies
docker-compose ps

# Check logs
docker logs anomaly-detector
```

#### 2. **No Facts Being Processed**
```bash
# Check Kafka connectivity
npm run kafka:test

# Verify topic exists
kafka-topics --list --bootstrap-server localhost:9092

# Check consumer group
kafka-consumer-groups --bootstrap-server localhost:9092 --group anomaly-detector-group --describe
```

#### 3. **Database Connection Issues**
```bash
# Test database connection
npm run db:test

# Check PostgreSQL logs
docker logs postgres

# Verify credentials
psql -h localhost -U incident_user -d incident_db
```

#### 4. **Rules Not Loading**
```bash
# Validate rule syntax
npm run rules:validate

# Check rules directory
ls -la rules/

# Test rule execution
npm run rules:test
```

### Performance Tuning

- **Increase Kafka Partitions**: For higher throughput
- **Optimize Database Indexes**: On alert timestamp and severity
- **Rule Engine Caching**: Cache compiled rules
- **Batch Processing**: Process multiple facts together

## 📈 Scaling

### Horizontal Scaling

```yaml
# Multiple instances
deploy:
  replicas: 3
  strategy:
    type: RollingUpdate
```

### Kafka Partitioning

```bash
# Increase topic partitions
kafka-topics --alter --topic logs_fact --partitions 6 --bootstrap-server localhost:9092
```

### Database Optimization

```sql
-- Add indexes for performance
CREATE INDEX idx_alerts_timestamp ON alerts(timestamp);
CREATE INDEX idx_alerts_severity ON alerts(severity);
CREATE INDEX idx_alerts_source ON alerts((facts->>'source'));
```

## 🤝 Contributing

1. **Fork** the repository
2. **Create** feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** changes (`git commit -m 'Add amazing feature'`)
4. **Push** to branch (`git push origin feature/amazing-feature`)
5. **Open** Pull Request

### Development Guidelines

- Follow TypeScript best practices
- Write comprehensive tests
- Update documentation
- Use conventional commits
- Ensure CI/CD passes

## License  
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)  

This project is licensed under the **GNU General Public License v3.0**. See the [LICENSE](https://github.com/Salah-ZEddine/Incident-Pilot/blob/master/LICENSE) file for full terms.

## 🙋‍♂️ Support

- **Documentation**: [Wiki](https://github.com/Salah-ZEddine/Incident-Pilot/wiki)
- **Issues**: [GitHub Issues](https://github.com/Salah-ZEddine/Incident-Pilot/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Salah-ZEddine/Incident-Pilot/discussions)

---

**Built with ❤️ for reliable incident management**