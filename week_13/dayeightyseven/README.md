# Day 87: Containerization with Docker & Docker Compose

## Objective
Package trading applications as Docker containers for consistency, portability, and efficient deployment across development and production environments.

## Core Concepts
* Docker Fundamentals: Images, containers, volumes, networks, registries, multi-stage builds, layer caching optimization, security best practices, multi-architecture builds
* Dockerfile Best Practices: Choosing base images (Alpine vs. Debian Slim vs. Ubuntu), Python dependency management (pip vs. poetry vs. pipenv), binary dependencies optimization, GPU-enabled containers, environment variable management
* Docker Compose for Development & Staging: Local environment with all dependencies, service dependencies and health checks, volume mounts for persistent data, environment variable management, hot-reload capabilities
* Container Optimization for Trading Workloads: Minimal base images, dependency pruning, resource constraints configuration, log aggregation, health checks and probes
* Orchestration Patterns: Service discovery and networking, shared volumes for model artifacts, resource constraints and limits, container networking modes
* Production Transition: Pushing to container registries, image tagging strategies, vulnerability scanning, image signing and verification, preparation for Kubernetes

## Tutorial: Multi-Service Trading System with Docker Compose

This tutorial creates a complete trading system with four microservices using Docker Compose, with health checks, dependency management, and persistent volumes.

```dockerfile
# Dockerfile for Trading System Components
# Multi-stage builds for optimized production images

# ============================================================================
# Base Image with Common Dependencies
# ============================================================================

# Stage 1: Builder for Python dependencies
FROM python:3.9-slim as builder

WORKDIR /app

# Install system dependencies needed for Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt


# ============================================================================
# Market Data Service
# ============================================================================

FROM python:3.9-slim as market-data

LABEL maintainer="trading-team@quantflow.com"
LABEL version="1.0.0"
LABEL description="Market Data Ingestion Service"

# Create non-root user for security
RUN groupadd -r trading && useradd -r -g trading -m -d /app trading

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /home/trading/.local
ENV PATH=/home/trading/.local/bin:$PATH

# Copy application code
COPY src/market_data/ .

# Create necessary directories with correct permissions
RUN mkdir -p /app/data /app/logs && \
    chown -R trading:trading /app && \
    chmod -R 755 /app

# Switch to non-root user
USER trading

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import socket; socket.create_connection(('localhost', 8000), timeout=2)" || exit 1

# Expose port
EXPOSE 8000

# Command to run
CMD ["python", "market_data_service.py"]


# ============================================================================
# Signal Generation Service (ML-Optimized with GPU support)
# ============================================================================

# Base image with CUDA for GPU support (optional)
ARG BASE_IMAGE=python:3.9-slim
FROM ${BASE_IMAGE} as signal-generator

LABEL maintainer="trading-team@quantflow.com"
LABEL version="1.0.0"
LABEL description="ML Signal Generation Service with GPU support"

# Install system dependencies including CUDA if needed
RUN apt-get update && apt-get install -y \
    wget \
    && rm -rf /var/lib/apt/lists/*

# For GPU support, uncomment these lines:
# ENV NVIDIA_VISIBLE_DEVICES all
# ENV NVIDIA_DRIVER_CAPABILITIES compute,utility

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY src/signal_generator/ .

# Create model directory
RUN mkdir -p /app/models && chmod 755 /app/models

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD python -c "import socket; socket.create_connection(('localhost', 8001), timeout=2)" || exit 1

# Expose port
EXPOSE 8001

# Command to run
CMD ["python", "signal_generator_service.py"]


# ============================================================================
# Order Execution Service (Security Hardened)
# ============================================================================

FROM python:3.9-alpine as order-execution

LABEL maintainer="trading-team@quantflow.com"
LABEL version="1.0.0"
LABEL description="Order Execution Service (Security Hardened)"

# Alpine specific dependencies
RUN apk add --no-cache \
    gcc \
    musl-dev \
    linux-headers \
    libffi-dev \
    openssl-dev

WORKDIR /app

# Copy Python dependencies from builder (need to rebuild for Alpine)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/order_execution/ .

# Create non-root user
RUN addgroup -S trading && adduser -S trading -G trading
USER trading

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import socket; socket.create_connection(('localhost', 8002), timeout=2)" || exit 1

# Expose port
EXPOSE 8002

# Command to run
CMD ["python", "order_execution_service.py"]


# ============================================================================
# Monitoring Service
# ============================================================================

FROM python:3.9-slim as monitoring

LABEL maintainer="trading-team@quantflow.com"
LABEL version="1.0.0"
LABEL description="Monitoring and Dashboard Service"

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY src/monitoring/ .

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import socket; socket.create_connection(('localhost', 8003), timeout=2)" || exit 1

# Expose ports for monitoring dashboard
EXPOSE 8003 9090

# Command to run
CMD ["python", "monitoring_service.py"]


# ============================================================================
# Development Image (with hot-reload)
# ============================================================================

FROM python:3.9-slim as development

LABEL maintainer="trading-team@quantflow.com"
LABEL version="1.0.0"
LABEL description="Development Environment with Hot Reload"

WORKDIR /app

# Install development dependencies
COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt

# Copy entire source for development
COPY . .

# Create volume for development
VOLUME /app

# Command for development with hot reload
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]

# docker-compose.yml - Complete Trading System Orchestration
version: '3.8'

# Networks for service isolation
networks:
  trading-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
  monitoring-network:
    driver: bridge
  data-network:
    driver: bridge

# Volumes for persistent data
volumes:
  postgres-data:
    driver: local
  redis-data:
    driver: local
  market-data:
    driver: local
  model-storage:
    driver: local
  logs:
    driver: local

# Shared configuration
x-trading-config: &trading-config
  TZ: America/New_York
  LOG_LEVEL: INFO
  ENVIRONMENT: ${ENVIRONMENT:-development}

x-database-config: &database-config
  POSTGRES_DB: trading
  POSTGRES_USER: trading_user
  POSTGRES_PASSWORD: ${DB_PASSWORD:-changeme123}
  POSTGRES_HOST_AUTH_METHOD: md5

x-redis-config: &redis-config
  REDIS_PASSWORD: ${REDIS_PASSWORD:-redispass123}
  REDIS_PORT: 6379

services:
  # Database Services
  postgres:
    image: postgres:14-alpine
    container_name: trading-postgres
    networks:
      - data-network
    environment:
      <<: *database-config
      POSTGRES_INITDB_ARGS: "--encoding=UTF-8 --locale=C"
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./database/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U trading_user -d trading"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s
    deploy:
      resources:
        limits:
          memory: 1G
        reservations:
          memory: 512M
    restart: unless-stopped

  timescaledb:
    image: timescale/timescaledb:2.8-pg14
    container_name: trading-timescaledb
    networks:
      - data-network
    environment:
      <<: *database-config
      POSTGRES_DB: market_data
    volumes:
      - timescale-data:/var/lib/postgresql/data
      - ./database/timescale-init.sql:/docker-entrypoint-initdb.d/timescale-init.sql
    ports:
      - "5433:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U trading_user -d market_data"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s
    deploy:
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    container_name: trading-redis
    command: redis-server --requirepass $${REDIS_PASSWORD} --appendonly yes
    networks:
      - data-network
    environment:
      <<: *redis-config
    volumes:
      - redis-data:/data
      - ./redis/redis.conf:/usr/local/etc/redis/redis.conf
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M
    restart: unless-stopped

  # Message Queue
  rabbitmq:
    image: rabbitmq:3.11-management-alpine
    container_name: trading-rabbitmq
    networks:
      - data-network
    environment:
      RABBITMQ_DEFAULT_USER: trading
      RABBITMQ_DEFAULT_PASS: ${RABBITMQ_PASSWORD:-rabbitpass123}
      RABBITMQ_DEFAULT_VHOST: /trading
    volumes:
      - rabbitmq-data:/var/lib/rabbitmq
      - ./rabbitmq/definitions.json:/etc/rabbitmq/definitions.json
      - ./rabbitmq/rabbitmq.conf:/etc/rabbitmq/rabbitmq.conf
    ports:
      - "5672:5672"   # AMQP
      - "15672:15672" # Management UI
    healthcheck:
      test: ["CMD", "rabbitmq-diagnostics", "ping"]
      interval: 30s
      timeout: 10s
      retries: 5
    restart: unless-stopped

  # Trading Services
  market-data:
    build:
      context: .
      dockerfile: Dockerfile.market-data
      target: market-data
    container_name: trading-market-data
    networks:
      - trading-network
      - data-network
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      rabbitmq:
        condition: service_healthy
    environment:
      <<: *trading-config
      SERVICE_NAME: market-data
      DB_HOST: postgres
      REDIS_HOST: redis
      RABBITMQ_HOST: rabbitmq
      MARKET_DATA_SOURCES: ${MARKET_DATA_SOURCES:-alpaca,polygon}
    volumes:
      - market-data:/app/data
      - logs:/app/logs
      - ./config/market-data.yaml:/app/config.yaml:ro
      - ./src/market_data:/app:ro
    ports:
      - "8000:8000"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 512M
    restart: unless-stopped

  signal-generator:
    build:
      context: .
      dockerfile: Dockerfile.signal-generator
      target: signal-generator
      args:
        BASE_IMAGE: ${GPU_IMAGE:-python:3.9-slim}
    container_name: trading-signal-generator
    networks:
      - trading-network
      - data-network
    depends_on:
      market-data:
        condition: service_healthy
      redis:
        condition: service_healthy
      timescaledb:
        condition: service_healthy
    environment:
      <<: *trading-config
      SERVICE_NAME: signal-generator
      DB_HOST: timescaledb
      REDIS_HOST: redis
      MARKET_DATA_HOST: market-data
      MODEL_STORAGE_PATH: /app/models
      USE_GPU: ${USE_GPU:-false}
    volumes:
      - model-storage:/app/models
      - logs:/app/logs
      - ./config/signal-generator.yaml:/app/config.yaml:ro
      - ./src/signal_generator:/app:ro
    ports:
      - "8001:8001"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 120s
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 1G
    restart: unless-stopped

  order-execution:
    build:
      context: .
      dockerfile: Dockerfile.order-execution
      target: order-execution
    container_name: trading-order-execution
    networks:
      - trading-network
      - data-network
    depends_on:
      signal-generator:
        condition: service_healthy
      redis:
        condition: service_healthy
      rabbitmq:
        condition: service_healthy
    environment:
      <<: *trading-config
      SERVICE_NAME: order-execution
      REDIS_HOST: redis
      RABBITMQ_HOST: rabbitmq
      SIGNAL_GENERATOR_HOST: signal-generator
      BROKER_API_KEY: ${BROKER_API_KEY}
      BROKER_API_SECRET: ${BROKER_API_SECRET}
    volumes:
      - logs:/app/logs
      - ./config/order-execution.yaml:/app/config.yaml:ro
      - ./src/order_execution:/app:ro
      - ./secrets:/app/secrets:ro
    ports:
      - "8002:8002"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8002/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 512M
    restart: unless-stopped

  # Monitoring Stack
  monitoring:
    build:
      context: .
      dockerfile: Dockerfile.monitoring
      target: monitoring
    container_name: trading-monitoring
    networks:
      - trading-network
      - monitoring-network
      - data-network
    depends_on:
      - market-data
      - signal-generator
      - order-execution
    environment:
      <<: *trading-config
      SERVICE_NAME: monitoring
      PROMETHEUS_MULTIPROC_DIR: /tmp
      GRAFANA_ADMIN_PASSWORD: ${GRAFANA_PASSWORD:-grafana123}
    volumes:
      - prometheus-data:/prometheus
      - grafana-data:/var/lib/grafana
      - logs:/app/logs
      - ./config/monitoring.yaml:/app/config.yaml:ro
      - ./monitoring/dashboards:/etc/grafana/provisioning/dashboards:ro
      - ./monitoring/datasources:/etc/grafana/provisioning/datasources:ro
    ports:
      - "8003:8003"   # Monitoring API
      - "3000:3000"   # Grafana
      - "9090:9090"   # Prometheus
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8003/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 2G
        reservations:
          cpus: '0.25'
          memory: 512M
    restart: unless-stopped

  prometheus:
    image: prom/prometheus:v2.45.0
    container_name: trading-prometheus
    networks:
      - monitoring-network
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=30d'
      - '--web.enable-lifecycle'
    volumes:
      - prometheus-data:/prometheus
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - ./monitoring/alerts.yml:/etc/prometheus/alerts.yml:ro
    ports:
      - "9091:9090"
    restart: unless-stopped

  grafana:
    image: grafana/grafana:9.5.2
    container_name: trading-grafana
    networks:
      - monitoring-network
    environment:
      GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_PASSWORD:-grafana123}
      GF_INSTALL_PLUGINS: grafana-clock-panel,grafana-simple-json-datasource
    volumes:
      - grafana-data:/var/lib/grafana
      - ./monitoring/dashboards:/etc/grafana/provisioning/dashboards:ro
      - ./monitoring/datasources:/etc/grafana/provisioning/datasources:ro
    ports:
      - "3001:3000"
    restart: unless-stopped

  # Development Services
  dev-environment:
    build:
      context: .
      dockerfile: Dockerfile.development
      target: development
    container_name: trading-dev
    networks:
      - trading-network
    depends_on:
      - postgres
      - redis
      - rabbitmq
    environment:
      <<: *trading-config
      ENVIRONMENT: development
      PYTHONPATH: /app
      PYTHONUNBUFFERED: 1
    volumes:
      - ./src:/app/src
      - ./tests:/app/tests
      - ./config:/app/config
      - ./notebooks:/app/notebooks
      - ./data:/app/data
    ports:
      - "8080:8080"
      - "8888:8888"   # Jupyter notebook
    command: >
      sh -c "python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8080 --reload &
             jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root --NotebookApp.token='' --NotebookApp.password=''"
    restart: unless-stopped

  # Testing Services
  test-runner:
    build:
      context: .
      dockerfile: Dockerfile.testing
    container_name: trading-test-runner
    networks:
      - trading-network
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    environment:
      <<: *trading-config
      ENVIRONMENT: test
      PYTHONPATH: /app
      TEST_DB_HOST: postgres
      TEST_REDIS_HOST: redis
    volumes:
      - ./tests:/app/tests
      - ./src:/app/src
      - ./test-reports:/app/test-reports
    command: >
      sh -c "pytest tests/ --cov=src --cov-report=xml:test-reports/coverage.xml
             --cov-report=html:test-reports/coverage_html
             --junitxml=test-reports/junit.xml -v"
    restart: "no"

  # Utilities
  pgadmin:
    image: dpage/pgadmin4:latest
    container_name: trading-pgadmin
    networks:
      - data-network
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@trading.local
      PGADMIN_DEFAULT_PASSWORD: ${PGADMIN_PASSWORD:-admin123}
    volumes:
      - pgadmin-data:/var/lib/pgadmin
    ports:
      - "5050:80"
    restart: unless-stopped

  redis-commander:
    image: rediscommander/redis-commander:latest
    container_name: trading-redis-commander
    networks:
      - data-network
    environment:
      REDIS_HOSTS: local:redis:6379
      REDIS_PASSWORD: ${REDIS_PASSWORD:-redispass123}
    ports:
      - "8081:8081"
    restart: unless-stopped

# Profiles for different environments
profiles:
  development:
    - dev-environment
    - pgadmin
    - redis-commander
  
  production:
    - market-data
    - signal-generator
    - order-execution
    - monitoring
    - prometheus
    - grafana
  
  testing:
    - test-runner
  
  minimal:
    - market-data
    - signal-generator
    - order-execution
  
  monitoring-only:
    - monitoring
    - prometheus
    - grafana