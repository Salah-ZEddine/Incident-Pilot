# Use Python 3.11 slim image for smaller size and better performance
FROM python:3.11-slim

# Set metadata
LABEL authors="Salah ZEddine"
LABEL description="Log Processor Service for Incident Pilot"
LABEL version="1.0"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY .env .

# Create non-root user for security
RUN groupadd -r logprocessor && useradd -r -g logprocessor logprocessor
RUN chown -R logprocessor:logprocessor /app
USER logprocessor

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "from app.config import settings; print('Health check passed')" || exit 1

# Expose port (if needed for monitoring/metrics)
EXPOSE 8000

# Set default command
CMD ["python", "app/main.py"]