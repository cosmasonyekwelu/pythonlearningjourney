# **Day 89: API Gateway & Load Balancing Setup**

## 🎯 Objective
Implement secure API gateways, load balancers, and service meshes for trading system APIs, ensuring scalability, security, and observability in high-frequency trading environments.

## 🏗️ Architecture Overview

This implementation provides a complete API gateway and load balancing solution featuring:
- **Kong API Gateway** with advanced trading-specific plugins
- **Nginx Load Balancer** with ultra-low latency configuration
- **Istio Service Mesh** for canary deployments and traffic management
- **Redis-based rate limiting** with sliding window algorithm
- **Comprehensive monitoring** with Prometheus, Grafana, and distributed tracing

## 📦 Core Components

### **1. API Gateway Patterns**
- **Kong Enterprise** with trading-specific plugins
- **JWT authentication** with HS256/RS256 support
- **Rate limiting** by API key, IP, user, and custom attributes
- **Request/response transformation** for trading data formats
- **API versioning** with backward compatibility
- **WebSocket support** for real-time market data

### **2. Load Balancing Strategies**
- **Nginx Plus** for Layer 7 routing with microsecond latency
- **Least connections algorithm** optimized for trading workloads
- **Health checks** with trading-specific metrics
- **Session persistence** for stateful trading sessions
- **Circuit breaking** with configurable thresholds

### **3. Service Mesh Implementation**
- **Istio 1.18+** with trading-specific configurations
- **Mutual TLS** for zero-trust service communication
- **Traffic splitting** for canary deployments
- **Distributed tracing** with Jaeger integration
- **Automatic retries** with exponential backoff

### **4. Security & Performance**
- **WAF rules** specifically for trading APIs
- **DDoS protection** with rate limiting and IP filtering
- **API caching** with Redis and memory optimization
- **Request signing** for order execution APIs
- **Compliance logging** for regulatory requirements

## 🚀 Quick Start

### **Prerequisites**
```bash
# Install dependencies
pip install kong-pdk pyjwt requests redis istio-client prometheus-client
pip install nginx-config-generator python-nginx httpx

# Docker setup
docker pull kong:3.4
docker pull nginx:1.24
docker pull redis:7.2
docker pull istio/proxyv2:1.18
```

### **Basic Configuration**
```python
from day_89 import TradingAPIGateway, TradingLoadBalancer, TradingServiceMesh

# Initialize components
gateway = TradingAPIGateway(
    kong_admin_url="http://localhost:8001",
    redis_url="redis://localhost:6379"
)

load_balancer = TradingLoadBalancer(
    upstream_servers=["trading-api-1:8080", "trading-api-2:8080"],
    algorithm="least_conn"
)

service_mesh = TradingServiceMesh(
    istio_control_plane="istiod.istio-system.svc.cluster.local:15012"
)
```

## 📁 Project Structure
```
day_89/
├── __init__.py
├── api_gateway.py          # Kong API Gateway implementation
├── load_balancer.py        # Nginx load balancer with trading optimizations
├── service_mesh.py         # Istio service mesh for canary deployments
├── security.py             # WAF, rate limiting, authentication
├── monitoring.py           # Metrics, tracing, dashboards
├── deployment.py           # Blue-green, canary, zero-downtime
├── config/
│   ├── kong.yaml           # Kong declarative configuration
│   ├── nginx.conf          # Nginx load balancer config
│   ├── istio/
│   │   ├── gateway.yaml    # Istio Gateway
│   │   ├── virtualservice.yaml
│   │   └── destinationrule.yaml
│   └── security/
│       ├── waf_rules.yaml
│       └── rate_limits.yaml
├── docker-compose.yaml     # Complete deployment
└── README.md
```

## 💻 Implementation

### **API Gateway Configuration**
```python
class TradingAPIGateway:
    """Kong API Gateway implementation for trading systems."""
    
    def __init__(self, kong_admin_url: str, redis_url: str):
        self.kong_admin = kong_admin_url
        self.redis_url = redis_url
        self.services = {}
        self.routes = {}
        
    async def setup_trading_apis(self):
        """Configure trading-specific API endpoints."""
        
        # Market Data API
        await self.create_service(
            name="market-data-api",
            url="http://market-data-service:8080",
            plugins=[
                {
                    "name": "rate-limiting",
                    "config": {
                        "second": 1000,  # 1000 requests/second
                        "hour": 100000,
                        "policy": "redis",
                        "redis_host": "redis",
                        "redis_port": 6379
                    }
                },
                {
                    "name": "jwt",
                    "config": {
                        "key_claim_name": "kid",
                        "secret_is_base64": True,
                        "run_on_preflight": True
                    }
                }
            ]
        )
        
        await self.create_route(
            service_name="market-data-api",
            paths=["/api/v1/market-data"],
            methods=["GET"],
            strip_path=True
        )
        
        # Order Execution API (higher security)
        await self.create_service(
            name="order-execution-api",
            url="http://order-execution-service:8081",
            plugins=[
                {
                    "name": "rate-limiting",
                    "config": {
                        "second": 100,  # Stricter limits for orders
                        "hour": 10000,
                        "policy": "redis"
                    }
                },
                {
                    "name": "request-transformer",
                    "config": {
                        "add": {
                            "headers": ["X-Trading-API-Version:1.0"],
                            "querystring": ["timestamp=${timestamp}"]
                        }
                    }
                },
                {
                    "name": "ip-restriction",
                    "config": {
                        "allow": ["10.0.0.0/8", "192.168.0.0/16"]
                    }
                }
            ]
        )
        
        # Real-time WebSocket for market data
        await self.create_service(
            name="market-data-ws",
            url="http://market-data-ws-service:8082",
            plugins=[
                {
                    "name": "websocket",
                    "config": {
                        "connect_timeout": 60000,
                        "read_timeout": 60000,
                        "write_timeout": 60000
                    }
                }
            ]
        )
```

### **Load Balancer with Trading Optimizations**
```python
class TradingLoadBalancer:
    """Nginx load balancer optimized for trading workloads."""
    
    def generate_config(self, trading_optimized: bool = True):
        """Generate Nginx configuration for trading systems."""
        
        config = """
        # Trading System Load Balancer
        # Optimized for low-latency, high-throughput trading APIs
        
        worker_processes auto;
        worker_rlimit_nofile 100000;
        
        events {
            worker_connections 65536;
            use epoll;
            multi_accept on;
        }
        
        http {
            # Trading-specific optimizations
            sendfile on;
            tcp_nopush on;
            tcp_nodelay on;
            keepalive_timeout 65;
            keepalive_requests 10000;
            client_max_body_size 10m;
            
            # Fast DNS resolution
            resolver 8.8.8.8 1.1.1.1 valid=300s;
            resolver_timeout 5s;
            
            # Gzip compression
            gzip on;
            gzip_vary on;
            gzip_min_length 1024;
            gzip_types text/plain text/css application/json application/javascript;
            
            # Rate limiting zone
            limit_req_zone $binary_remote_addr zone=trading_api:10m rate=1000r/s;
            limit_req_zone $http_apikey zone=api_keys:10m rate=100r/s;
            
            # Trading API upstream servers
            upstream trading_api_backend {
                """
        
        if trading_optimized:
            config += """
                # Trading-optimized load balancing
                least_conn;  # Better for long-lived trading connections
                
                # Sticky sessions for trading state
                hash $http_x_session_id consistent;
                
                # Active health checks
                zone trading_backend 64k;
                
                # Server definitions with weights
                """
                
            for server in self.upstream_servers:
                config += f"server {server} max_fails=3 fail_timeout=30s;\n"
        
        config += """
            }
            
            # Market data WebSocket upstream
            upstream market_data_ws {
                """
                
        if trading_optimized:
            config += """
                ip_hash;  # Session persistence for WebSocket connections
                """
                
        for ws_server in self.ws_servers:
            config += f"server {ws_server};\n"
        
        config += """
            }
            
            # Main trading API server
            server {
                listen 443 ssl http2;
                server_name api.trading-system.com;
                
                # SSL Configuration
                ssl_certificate /etc/nginx/ssl/trading.crt;
                ssl_certificate_key /etc/nginx/ssl/trading.key;
                ssl_protocols TLSv1.2 TLSv1.3;
                ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
                ssl_session_timeout 10m;
                ssl_session_cache shared:SSL:10m;
                
                # Trading API endpoints
                location /api/v1/market-data {
                    limit_req zone=trading_api burst=2000 nodelay;
                    limit_req zone=api_keys burst=100;
                    
                    proxy_pass http://trading_api_backend;
                    proxy_http_version 1.1;
                    proxy_set_header Upgrade $http_upgrade;
                    proxy_set_header Connection 'upgrade';
                    proxy_set_header Host $host;
                    proxy_set_header X-Real-IP $remote_addr;
                    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                    proxy_set_header X-Forwarded-Proto $scheme;
                    
                    # Trading-specific timeouts
                    proxy_connect_timeout 1s;
                    proxy_send_timeout 10s;
                    proxy_read_timeout 10s;
                }
                
                # WebSocket endpoint for real-time data
                location /ws/v1/market-data {
                    proxy_pass http://market_data_ws;
                    proxy_http_version 1.1;
                    proxy_set_header Upgrade $http_upgrade;
                    proxy_set_header Connection "upgrade";
                    proxy_set_header Host $host;
                    
                    # WebSocket optimizations
                    proxy_buffering off;
                    proxy_read_timeout 86400s;
                    proxy_send_timeout 86400s;
                }
                
                # Order execution endpoint (stricter limits)
                location /api/v1/orders {
                    limit_req zone=trading_api burst=100 nodelay;
                    limit_req zone=api_keys burst=10;
                    
                    # Request signing validation
                    # (implemented in auth_request)
                    
                    proxy_pass http://trading_api_backend;
                    proxy_set_header X-Trading-API-Key $http_apikey;
                }
                
                # Health check endpoint
                location /health {
                    access_log off;
                    return 200 'healthy';
                    add_header Content-Type text/plain;
                }
            }
        }
        """
        
        return config
```

### **Service Mesh for Canary Deployments**
```python
class TradingServiceMesh:
    """Istio service mesh implementation for trading systems."""
    
    async def setup_canary_deployment(self, service_name: str, 
                                     new_version: str, 
                                     current_version: str,
                                     metrics_config: Dict):
        """Setup canary deployment with automatic rollback based on metrics."""
        
        # VirtualService for traffic splitting
        virtual_service = f"""
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: {service_name}
spec:
  hosts:
  - {service_name}
  http:
  - match:
    - headers:
        x-canary:
          exact: "true"
    route:
    - destination:
        host: {service_name}
        subset: {new_version}
      weight: 100
  - route:
    - destination:
        host: {service_name}
        subset: {current_version}
      weight: 90
    - destination:
        host: {service_name}
        subset: {new_version}
      weight: 10
    retries:
      attempts: 3
      retryTimeout: 2s
    timeout: 5s
"""
        
        # DestinationRule for subsets
        destination_rule = f"""
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: {service_name}
spec:
  host: {service_name}
  subsets:
  - name: {current_version}
    labels:
      version: {current_version}
  - name: {new_version}
    labels:
      version: {new_version}
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 1000
      http:
        http1MaxPendingRequests: 1000
        http2MaxRequests: 1000
    outlierDetection:
      consecutive5xxErrors: 5
      interval: 30s
      baseEjectionTime: 30s
      maxEjectionPercent: 100
"""
        
        # Deploy configurations
        await self.apply_istio_config(virtual_service, "virtualservice")
        await self.apply_istio_config(destination_rule, "destinationrule")
        
        # Setup metrics-based rollback
        await self.setup_rollback_monitoring(
            service_name,
            new_version,
            metrics_config
        )
    
    async def setup_rollback_monitoring(self, service_name: str, 
                                       version: str,
                                       metrics_config: Dict):
        """Setup Prometheus alerts and automatic rollback triggers."""
        
        prometheus_rules = {
            "groups": [{
                "name": f"{service_name}_canary_rules",
                "rules": [
                    {
                        "alert": f"{service_name}_HighErrorRate",
                        "expr": f"""
                            sum(rate(istio_requests_total{{
                                destination_service="{service_name}",
                                destination_version="{version}",
                                response_code=~"5.."
                            }}[5m])) / 
                            sum(rate(istio_requests_total{{
                                destination_service="{service_name}",
                                destination_version="{version}"
                            }}[5m])) > {metrics_config.get('error_rate_threshold', 0.01)}
                        """,
                        "for": "2m",
                        "annotations": {
                            "summary": f"High error rate in {service_name} {version}",
                            "action": "Rollback to previous version"
                        },
                        "labels": {
                            "severity": "critical",
                            "service": service_name
                        }
                    },
                    {
                        "alert": f"{service_name}_HighLatency",
                        "expr": f"""
                            histogram_quantile(0.99,
                                sum(rate(istio_request_duration_milliseconds_bucket{{
                                    destination_service="{service_name}",
                                    destination_version="{version}"
                                }}[5m])) by (le)) > {metrics_config.get('latency_threshold_ms', 100)}
                        """,
                        "for": "3m",
                        "annotations": {
                            "summary": f"High latency in {service_name} {version}",
                            "action": "Consider rollback"
                        }
                    }
                ]
            }]
        }
        
        # Apply Prometheus rules
        await self.apply_prometheus_rules(prometheus_rules)
        
        # Setup automatic rollback action
        await self.setup_rollback_action(service_name, version)
```

### **Security Implementation**
```python
class TradingSecurity:
    """Security implementation for trading APIs."""
    
    def __init__(self):
        self.waf_rules = self.load_waf_rules()
        self.rate_limiters = {}
        
    def load_waf_rules(self) -> List[Dict]:
        """Load trading-specific WAF rules."""
        return [
            # SQL injection prevention
            {
                "id": "trading_sql_injection",
                "rule": r"(union.*select|select.*from|insert.*into|delete.*from|drop.*table)",
                "action": "block",
                "severity": "critical"
            },
            # Trading-specific patterns
            {
                "id": "suspicious_order_pattern",
                "rule": r"quantity\s*[<>]\s*1000000|price\s*[<>]\s*[0-9]{6}",
                "action": "alert",
                "severity": "high"
            },
            # API key brute force
            {
                "id": "api_key_bruteforce",
                "rule": r"apikey=.*&apikey=|apikey.*apikey",
                "action": "block",
                "severity": "high"
            },
            # WebSocket abuse
            {
                "id": "websocket_flood",
                "rule": r"Sec-WebSocket-Version:\s*13.*Sec-WebSocket-Version:\s*13",
                "action": "rate_limit",
                "severity": "medium"
            }
        ]
    
    async def validate_request(self, request: Request) -> Tuple[bool, str]:
        """Validate trading API request against security rules."""
        
        # Check rate limits
        if not await self.check_rate_limit(request):
            return False, "Rate limit exceeded"
        
        # Validate JWT token for order execution
        if request.path.startswith("/api/v1/orders"):
            if not await self.validate_jwt(request):
                return False, "Invalid or expired token"
        
        # Check WAF rules
        waf_result = await self.check_waf_rules(request)
        if not waf_result[0]:
            return False, f"Security violation: {waf_result[1]}"
        
        # Validate request signing for sensitive endpoints
        if request.path.startswith("/api/v1/execute"):
            if not await self.validate_request_signature(request):
                return False, "Invalid request signature"
        
        return True, "OK"
    
    async def check_rate_limit(self, request: Request) -> bool:
        """Advanced rate limiting with sliding window algorithm."""
        
        identifier = self.get_rate_limit_identifier(request)
        window_size = 60  # seconds
        max_requests = self.get_rate_limit_for_endpoint(request.path)
        
        # Use Redis sorted sets for sliding window
        current_time = time.time()
        window_start = current_time - window_size
        
        pipeline = self.redis.pipeline()
        pipeline.zremrangebyscore(identifier, 0, window_start)
        pipeline.zcard(identifier)
        pipeline.zadd(identifier, {str(current_time): current_time})
        pipeline.expire(identifier, window_size)
        
        results = await pipeline.execute()
        current_count = results[1]
        
        return current_count < max_requests
```

### **Monitoring and Observability**
```python
class TradingMonitoring:
    """Comprehensive monitoring for trading APIs."""
    
    def __init__(self):
        self.metrics_registry = CollectorRegistry()
        self.setup_metrics()
        self.tracing_exporter = setup_tracing()
        
    def setup_metrics(self):
        """Setup trading-specific metrics."""
        
        # API request metrics
        self.request_counter = Counter(
            'trading_api_requests_total',
            'Total trading API requests',
            ['method', 'endpoint', 'status'],
            registry=self.metrics_registry
        )
        
        # Latency histogram (microsecond precision)
        self.request_latency = Histogram(
            'trading_api_request_duration_seconds',
            'Trading API request latency',
            ['method', 'endpoint'],
            buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0],
            registry=self.metrics_registry
        )
        
        # Trading-specific metrics
        self.order_execution_latency = Histogram(
            'trading_order_execution_latency_ms',
            'Order execution latency in milliseconds',
            ['symbol', 'order_type'],
            buckets=[1, 5, 10, 50, 100, 500],
            registry=self.metrics_registry
        )
        
        self.market_data_subscribers = Gauge(
            'trading_market_data_subscribers',
            'Number of active market data subscribers',
            ['symbol'],
            registry=self.metrics_registry
        )
        
        # Business metrics
        self.orders_processed = Counter(
            'trading_orders_processed_total',
            'Total orders processed',
            ['symbol', 'side', 'status'],
            registry=self.metrics_registry
        )
    
    def generate_dashboard(self) -> Dict:
        """Generate Grafana dashboard configuration."""
        
        return {
            "dashboard": {
                "title": "Trading API Dashboard",
                "panels": [
                    {
                        "title": "API Request Rate",
                        "targets": [
                            {
                                "expr": "rate(trading_api_requests_total[5m])",
                                "legendFormat": "{{method}} {{endpoint}}"
                            }
                        ],
                        "type": "graph",
                        "yaxes": [{"format": "reqps"}]
                    },
                    {
                        "title": "API Latency (99th percentile)",
                        "targets": [
                            {
                                "expr": "histogram_quantile(0.99, rate(trading_api_request_duration_seconds_bucket[5m]))",
                                "legendFormat": "{{endpoint}}"
                            }
                        ],
                        "type": "graph",
                        "yaxes": [{"format": "s"}]
                    },
                    {
                        "title": "Order Execution Latency",
                        "targets": [
                            {
                                "expr": "histogram_quantile(0.95, rate(trading_order_execution_latency_ms_bucket[1m]))",
                                "legendFormat": "{{symbol}} {{order_type}}"
                            }
                        ],
                        "type": "heatmap"
                    },
                    {
                        "title": "Active Market Data Subscribers",
                        "targets": [
                            {
                                "expr": "trading_market_data_subscribers",
                                "legendFormat": "{{symbol}}"
                            }
                        ],
                        "type": "stat"
                    }
                ]
            }
        }
```

## 🚀 Deployment Examples

### **Docker Compose Setup**
```yaml
version: '3.8'

services:
  # Kong API Gateway
  kong:
    image: kong:3.4
    environment:
      KONG_DATABASE: postgres
      KONG_PG_HOST: postgres
      KONG_PG_USER: kong
      KONG_PG_PASSWORD: kong
      KONG_PROXY_ACCESS_LOG: /dev/stdout
      KONG_ADMIN_ACCESS_LOG: /dev/stdout
      KONG_PROXY_ERROR_LOG: /dev/stderr
      KONG_ADMIN_ERROR_LOG: /dev/stderr
      KONG_ADMIN_LISTEN: 0.0.0.0:8001
    ports:
      - "8000:8000"  # Proxy
      - "8443:8443"  # SSL Proxy
      - "8001:8001"  # Admin API
    depends_on:
      - postgres
      - redis
  
  # Nginx Load Balancer
  nginx:
    image: nginx:1.24-alpine
    volumes:
      - ./config/nginx/trading.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - kong
  
  # Redis for rate limiting
  redis:
    image: redis:7.2-alpine
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
  
  # PostgreSQL for Kong
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: kong
      POSTGRES_PASSWORD: kong
      POSTGRES_DB: kong
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  # Prometheus for metrics
  prometheus:
    image: prom/prometheus:v2.45.0
    volumes:
      - ./config/prometheus:/etc/prometheus:ro
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
  
  # Grafana for dashboards
  grafana:
    image: grafana/grafana:9.5.2
    environment:
      GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_PASSWORD}
    volumes:
      - grafana_data:/var/lib/grafana
      - ./config/grafana/dashboards:/etc/grafana/provisioning/dashboards:ro
    ports:
      - "3000:3000"
  
  # Jaeger for distributed tracing
  jaeger:
    image: jaegertracing/all-in-one:1.46
    environment:
      COLLECTOR_OTLP_ENABLED: true
    ports:
      - "16686:16686"  # UI
      - "4317:4317"    # OTLP gRPC
      - "4318:4318"    # OTLP HTTP

volumes:
  postgres_data:
  redis_data:
  prometheus_data:
  grafana_data:
```

### **Kubernetes Deployment**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: trading-api-gateway
  namespace: trading
spec:
  replicas: 3
  selector:
    matchLabels:
      app: trading-gateway
  template:
    metadata:
      labels:
        app: trading-gateway
        version: v1.0.0
    spec:
      containers:
      - name: kong
        image: kong:3.4
        env:
        - name: KONG_DATABASE
          value: "off"
        - name: KONG_DECLARATIVE_CONFIG
          value: "/etc/kong/kong.yaml"
        - name: KONG_PROXY_LISTEN
          value: "0.0.0.0:8000"
        - name: KONG_ADMIN_LISTEN
          value: "0.0.0.0:8001"
        ports:
        - containerPort: 8000
          name: proxy
        - containerPort: 8001
          name: admin
        volumeMounts:
        - name: kong-config
          mountPath: /etc/kong
        resources:
          limits:
            memory: "512Mi"
            cpu: "500m"
          requests:
            memory: "256Mi"
            cpu: "250m"
        livenessProbe:
          httpGet:
            path: /status
            port: admin
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /status/ready
            port: admin
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: trading-gateway
  namespace: trading
spec:
  selector:
    app: trading-gateway
  ports:
  - name: proxy
    port: 80
    targetPort: 8000
  - name: admin
    port: 8001
    targetPort: 8001
  type: LoadBalancer
```

## 📊 Monitoring Setup

### **Prometheus Configuration**
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'kong'
    static_configs:
      - targets: ['kong:8001']
    metrics_path: /metrics
    
  - job_name: 'nginx'
    static_configs:
      - targets: ['nginx:9113']
    metrics_path: /metrics
    
  - job_name: 'trading-apis'
    static_configs:
      - targets: 
        - 'market-data-service:8080'
        - 'order-execution-service:8081'
        - 'signal-service:8082'
    metrics_path: /metrics
    
  - job_name: 'redis'
    static_configs:
      - targets: ['redis:9121']
      
  - job_name: 'kubernetes-pods'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
```

### **Alerting Rules**
```yaml
groups:
  - name: trading_api_alerts
    rules:
      - alert: HighAPIErrorRate
        expr: |
          sum(rate(http_requests_total{status=~"5.."}[5m])) 
          / sum(rate(http_requests_total[5m])) > 0.05
        for: 2m
        labels:
          severity: critical
          service: trading-api
        annotations:
          summary: "High error rate in trading API"
          description: "Error rate is {{ $value }}%"
          
      - alert: APILatencySpike
        expr: |
          histogram_quantile(0.99, 
            rate(http_request_duration_seconds_bucket[5m])) > 0.5
        for: 3m
        labels:
          severity: warning
        annotations:
          summary: "High latency in trading API"
          
      - alert: RateLimitExceeded
        expr: |
          increase(kong_http_status{code="429"}[5m]) > 100
        for: 1m
        labels:
          severity: warning
        annotations:
          summary: "High rate limiting activity"
```

## 🔧 Configuration Management

### **Environment-Specific Configs**
```python
class TradingAPIConfig:
    """Configuration manager for trading API gateway."""
    
    CONFIGS = {
        "development": {
            "rate_limits": {
                "market_data": {"second": 100, "hour": 10000},
                "order_execution": {"second": 10, "hour": 1000}
            },
            "security": {
                "require_authentication": False,
                "enable_waf": False
            }
        },
        "staging": {
            "rate_limits": {
                "market_data": {"second": 1000, "hour": 100000},
                "order_execution": {"second": 100, "hour": 10000}
            },
            "security": {
                "require_authentication": True,
                "enable_waf": True
            }
        },
        "production": {
            "rate_limits": {
                "market_data": {"second": 10000, "hour": 1000000},
                "order_execution": {"second": 1000, "hour": 100000}
            },
            "security": {
                "require_authentication": True,
                "enable_waf": True,
                "require_request_signing": True,
                "enable_ddos_protection": True
            },
            "performance": {
                "connection_pool_size": 1000,
                "keepalive_timeout": 65,
                "proxy_buffer_size": "16k"
            }
        }
    }
```

## 🎯 Testing

### **Load Testing Script**
```python
async def load_test_trading_api():
    """Load test trading APIs with realistic trading patterns."""
    
    # Test market data API
    market_data_results = await asyncio.gather(*[
        test_market_data_request(symbol)
        for symbol in ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA']
        for _ in range(1000)
    ])
    
    # Test order execution with realistic patterns
    order_patterns = generate_realistic_order_patterns()
    order_results = await asyncio.gather(*[
        test_order_execution(order)
        for order in order_patterns
    ])
    
    # Test WebSocket connections
    ws_results = await test_websocket_connections(
        symbol='AAPL',
        num_connections=100,
        duration=300  # 5 minutes
    )
    
    return {
        'market_data': analyze_results(market_data_results),
        'order_execution': analyze_results(order_results),
        'websocket': analyze_ws_results(ws_results)
    }
```

### **Security Testing**
```python
async def security_test_trading_api():
    """Run security tests on trading APIs."""
    
    tests = [
        # Rate limiting tests
        test_rate_limiting_violation(),
        
        # Authentication bypass tests
        test_jwt_authentication(),
        test_api_key_validation(),
        
        # WAF rule tests
        test_sql_injection_prevention(),
        test_xss_prevention(),
        
        # Trading-specific attacks
        test_order_manipulation(),
        test_price_manipulation(),
        
        # DDoS simulation
        test_ddos_protection()
    ]
    
    results = await asyncio.gather(*tests)
    return generate_security_report(results)
```

## 📈 Performance Optimization

### **Nginx Tuning for Trading**
```nginx
# Trading-specific Nginx optimizations
events {
    # Use epoll for Linux
    use epoll;
    
    # Increase worker connections
    worker_connections 100000;
    
    # Multi-accept for better performance
    multi_accept on;
}

http {
    # TCP optimizations
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    
    # Keepalive optimizations
    keepalive_timeout 65;
    keepalive_requests 10000;
    
    # Buffer optimizations
    client_body_buffer_size 16k;
    client_header_buffer_size 1k;
    large_client_header_buffers 4 8k;
    
    # Timeout optimizations
    client_body_timeout 12;
    client_header_timeout 12;
    send_timeout 10;
    
    # Gzip optimizations
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css application/json application/javascript;
}
```

### **Kong Performance Tuning**
```yaml
# kong.conf - Performance tuning
nginx_worker_processes = auto
nginx_worker_rlimit_nofile = 100000

# Memory optimizations
mem_cache_size = 128m
ssl_session_cache_size = 10m
ssl_session_timeout = 1d

# Connection pool
nginx_upstream_keepalive = 60
nginx_upstream_keepalive_requests = 10000
nginx_upstream_keepalive_timeout = 60s

# Buffer optimizations
client_body_buffer_size = 8k
client_header_buffer_size = 4k
large_client_header_buffers 4 8k
```

## 🔄 CI/CD Integration

### **GitHub Actions Workflow**
```yaml
name: Trading API Gateway CI/CD

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      redis:
        image: redis:7.2
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Run API tests
      run: |
        python -m pytest tests/api_gateway_test.py -v
        python -m pytest tests/load_balancer_test.py -v
        python -m pytest tests/security_test.py -v
    
    - name: Run performance tests
      run: |
        python tests/performance_test.py --requests 10000 --concurrent 100
    
    - name: Run security scans
      run: |
        python tests/security_scan.py --api-endpoint http://localhost:8000

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - name: Deploy to staging
      run: |
        python deploy.py --environment staging --canary 10%
        
    - name: Run canary tests
      run: |
        python tests/canary_test.py --duration 300
        
    - name: Promote to production
      if: success()
      run: |
        python deploy.py --environment production --rollout 25%
        sleep 300  # Wait 5 minutes
        python deploy.py --environment production --rollout 100%
```

## 📚 API Documentation

### **OpenAPI Specification**
```yaml
openapi: 3.0.0
info:
  title: Trading System API
  version: 1.0.0
  description: High-performance trading API with real-time market data and order execution

servers:
  - url: https://api.trading-system.com
    description: Production server
  - url: https://staging.api.trading-system.com
    description: Staging server

paths:
  /api/v1/market-data/{symbol}:
    get:
      summary: Get market data for symbol
      parameters:
        - name: symbol
          in: path
          required: true
          schema:
            type: string
          example: AAPL
      responses:
        '200':
          description: Market data retrieved successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/MarketData'
        '429':
          description: Rate limit exceeded
      
  /api/v1/orders:
    post:
      summary: Execute a trading order
      security:
        - BearerAuth: []
        - ApiKeyAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Order'
      responses:
        '201':
          description: Order executed successfully
        '400':
          description: Invalid order parameters
        '401':
          description: Unauthorized

components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
    ApiKeyAuth:
      type: apiKey
      in: header
      name: X-API-Key
```

## 🚀 Getting Started

### **1. Clone and Setup**
```bash
git clone https://github.com/your-org/trading-api-gateway.git
cd trading-api-gateway

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your configuration
```

### **2. Start Services**
```bash
# Using Docker Compose
docker-compose up -d

# Or using Kubernetes
kubectl apply -f kubernetes/
```

### **3. Configure APIs**
```python
from day_89 import TradingAPIGateway

gateway = TradingAPIGateway(
    kong_admin_url="http://localhost:8001",
    redis_url="redis://localhost:6379"
)

# Setup trading APIs
await gateway.setup_trading_apis()

# Setup monitoring
await gateway.setup_monitoring()
```

### **4. Run Tests**
```bash
# Unit tests
pytest tests/

# Performance tests
python tests/performance_test.py --requests 10000

# Security tests
python tests/security_test.py --api-endpoint http://localhost:8000
```

## 🆘 Troubleshooting

### **Common Issues**

1. **Kong not starting**
   ```bash
   # Check Kong logs
   docker logs kong
   
   # Check PostgreSQL connection
   docker exec -it postgres psql -U kong -d kong
   ```

2. **Rate limiting not working**
   ```bash
   # Check Redis connection
   docker exec -it redis redis-cli ping
   
   # Check Kong plugins
   curl http://localhost:8001/plugins
   ```

3. **High latency**
   ```nginx
   # Adjust Nginx timeouts
   proxy_connect_timeout 1s;
   proxy_send_timeout 5s;
   proxy_read_timeout 5s;
   ```

### **Performance Monitoring**
```bash
# Monitor API performance
curl http://localhost:8001/metrics

# Check Nginx status
curl http://localhost:8080/nginx_status

# Monitor Redis memory
docker exec -it redis redis-cli info memory
```

## 📈 Scaling Recommendations

### **Horizontal Scaling**
```yaml
# Scale Kong horizontally
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: kong-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: kong
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### **Database Scaling**
```sql
-- PostgreSQL read replicas for Kong
-- In kong.conf:
pg_host = host1,host2,host3
pg_port = 5432,5432,5432
```

## 🔮 Future Enhancements

1. **AI-based rate limiting** using request pattern analysis
2. **Predictive scaling** based on market volatility
3. **Blockchain integration** for order immutability
4. **Quantum-safe cryptography** for future-proof security
5. **Edge computing** for ultra-low latency order execution

---

**Next Steps**: Deploy this API gateway solution, integrate with your existing trading services, and customize the security rules and rate limits based on your specific trading patterns and regulatory requirements.