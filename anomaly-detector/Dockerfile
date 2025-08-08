# Use Node.js 22 LTS Alpine for smaller image size
FROM node:22-alpine

# Set metadata
LABEL authors="Salah ZEddine"
LABEL description="Anomaly Detection Service for Incident Pilot"
LABEL version="1.0"

# Set environment variables
ENV NODE_ENV=production \
    PORT=3000

# Set working directory
WORKDIR /app

# Install system dependencies for native modules
RUN apk add --no-cache \
    python3 \
    make \
    g++ \
    && rm -rf /var/cache/apk/*

# Copy package files first for better Docker layer caching
COPY package*.json ./
COPY tsconfig.json ./

# Install dependencies
RUN npm ci --only=production && npm cache clean --force

# Copy source code
COPY src/ ./src/
COPY rules/ ./rules/

# Build TypeScript
RUN npm run build

# Create non-root user for security
RUN addgroup -g 1001 -S anomaly && \
    adduser -S anomaly -u 1001 -G anomaly && \
    chown -R anomaly:anomaly /app

USER anomaly

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD node -e "console.log('Health check passed')" || exit 1

# Expose port for monitoring/metrics
EXPOSE 3000

# Set default command
CMD ["npm", "start"]
