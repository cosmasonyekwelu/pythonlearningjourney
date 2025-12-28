"""
Day 89: API Gateway & Load Balancing Setup
Implementation of secure API gateways, load balancers, and service meshes 
for trading system APIs with scalability, security, and observability.
"""

import asyncio
import json
import time
import hashlib
import jwt
import redis.asyncio as redis
import httpx
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
import uuid
import base64
from collections import defaultdict
import yaml
import prometheus_client
from prometheus_client import Counter, Histogram, Gauge, Summary
import opentracing
from opentracing import tracer as global_tracer
import jaeger_client
from contextlib import asynccontextmanager
import aiohttp
from aiohttp import web
import numpy as np
from decimal import Decimal
import ssl
import certifi

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus metrics registry
metrics_registry = prometheus_client.CollectorRegistry()


class TradingEnvironment(Enum):
    """Trading environment types."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    BACKTESTING = "backtesting"


class RateLimitAlgorithm(Enum):
    """Rate limiting algorithms."""
    TOKEN_BUCKET = "token_bucket"
    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW = "sliding_window"
    LEAKY_BUCKET = "leaky_bucket"


class LoadBalancingAlgorithm(Enum):
    """Load balancing algorithms."""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    IP_HASH = "ip_hash"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    RANDOM = "random"


class TradingAPIGateway:
    """
    Kong API Gateway implementation for trading systems with advanced
    rate limiting, authentication, and trading-specific plugins.
    """
    
    def __init__(self, kong_admin_url: str, redis_url: str, 
                 environment: TradingEnvironment = TradingEnvironment.DEVELOPMENT):
        self.kong_admin_url = kong_admin_url
        self.redis_url = redis_url
        self.environment = environment
        self.http_client = httpx.AsyncClient(timeout=30.0)
        self.redis_client = None
        self.services = {}
        self.routes = {}
        self.consumers = {}
        
        # Trading-specific configurations
        self.config = self._load_environment_config()
        
        # Metrics
        self.request_counter = Counter(
            'kong_requests_total',
            'Total requests through Kong',
            ['service', 'route', 'status'],
            registry=metrics_registry
        )
        
        self.latency_histogram = Histogram(
            'kong_request_duration_seconds',
            'Request latency through Kong',
            ['service', 'route'],
            buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0],
            registry=metrics_registry
        )
        
        logger.info(f"Initialized TradingAPIGateway for {environment.value}")
    
    def _load_environment_config(self) -> Dict:
        """Load configuration based on environment."""
        configs = {
            TradingEnvironment.DEVELOPMENT: {
                "rate_limits": {
                    "market_data": {"second": 100, "hour": 10000},
                    "order_execution": {"second": 10, "hour": 1000},
                    "portfolio": {"second": 50, "hour": 5000}
                },
                "security": {
                    "require_jwt": False,
                    "require_ip_whitelist": False,
                    "enable_waf": False
                },
                "timeouts": {
                    "connect": 5.0,
                    "send": 30.0,
                    "read": 30.0
                }
            },
            TradingEnvironment.STAGING: {
                "rate_limits": {
                    "market_data": {"second": 1000, "hour": 100000},
                    "order_execution": {"second": 100, "hour": 10000},
                    "portfolio": {"second": 500, "hour": 50000}
                },
                "security": {
                    "require_jwt": True,
                    "require_ip_whitelist": True,
                    "enable_waf": True,
                    "allowed_ips": ["10.0.0.0/8", "192.168.0.0/16"]
                },
                "timeouts": {
                    "connect": 2.0,
                    "send": 10.0,
                    "read": 10.0
                }
            },
            TradingEnvironment.PRODUCTION: {
                "rate_limits": {
                    "market_data": {"second": 10000, "hour": 1000000},
                    "order_execution": {"second": 1000, "hour": 100000},
                    "portfolio": {"second": 5000, "hour": 500000}
                },
                "security": {
                    "require_jwt": True,
                    "require_ip_whitelist": True,
                    "require_request_signing": True,
                    "enable_waf": True,
                    "enable_ddos_protection": True,
                    "allowed_ips": ["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"]
                },
                "performance": {
                    "connection_pool_size": 1000,
                    "keepalive_timeout": 65,
                    "buffer_size": "16k"
                },
                "timeouts": {
                    "connect": 1.0,
                    "send": 5.0,
                    "read": 5.0
                }
            }
        }
        
        return configs.get(self.environment, configs[TradingEnvironment.DEVELOPMENT])
    
    async def connect(self):
        """Connect to Kong admin API and Redis."""
        # Connect to Redis
        self.redis_client = await redis.from_url(
            self.redis_url,
            decode_responses=True,
            max_connections=100
        )
        
        # Test Kong connection
        try:
            response = await self.http_client.get(f"{self.kong_admin_url}/status")
            if response.status_code == 200:
                logger.info(f"Connected to Kong at {self.kong_admin_url}")
            else:
                logger.warning(f"Kong returned status {response.status_code}")
        except Exception as e:
            logger.error(f"Failed to connect to Kong: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from all services."""
        if self.http_client:
            await self.http_client.aclose()
        if self.redis_client:
            await self.redis_client.aclose()
        logger.info("Disconnected from TradingAPIGateway")
    
    async def setup_trading_apis(self):
        """Setup all trading API endpoints with appropriate plugins."""
        logger.info("Setting up trading APIs...")
        
        # Market Data API
        await self._create_market_data_api()
        
        # Order Execution API
        await self._create_order_execution_api()
        
        # Portfolio Management API
        await self._create_portfolio_api()
        
        # Signal Generation API
        await self._create_signal_generation_api()
        
        # WebSocket API for real-time data
        await self._create_websocket_api()
        
        # Admin/Management API
        await self._create_admin_api()
        
        logger.info("Trading APIs setup complete")
    
    async def _create_market_data_api(self):
        """Create market data API service."""
        service_config = {
            "name": "market-data-api",
            "url": "http://market-data-service:8080",
            "tags": ["trading", "market-data", self.environment.value]
        }
        
        plugins = [
            {
                "name": "rate-limiting",
                "config": {
                    "second": self.config["rate_limits"]["market_data"]["second"],
                    "hour": self.config["rate_limits"]["market_data"]["hour"],
                    "policy": "redis",
                    "redis_host": self.redis_url.split("://")[1].split(":")[0],
                    "redis_port": 6379,
                    "fault_tolerant": True,
                    "hide_client_headers": False
                }
            },
            {
                "name": "request-transformer",
                "config": {
                    "add": {
                        "headers": ["X-Trading-Environment:" + self.environment.value],
                        "querystring": ["timestamp=${timestamp}"]
                    },
                    "replace": {
                        "headers": ["Accept:application/json"]
                    }
                }
            },
            {
                "name": "correlation-id",
                "config": {
                    "header_name": "X-Request-ID",
                    "generator": "uuid#counter",
                    "echo_downstream": True
                }
            }
        ]
        
        if self.config["security"]["require_jwt"]:
            plugins.append({
                "name": "jwt",
                "config": {
                    "key_claim_name": "kid",
                    "secret_is_base64": True,
                    "run_on_preflight": True,
                    "maximum_expiration": 3600
                }
            })
        
        if self.config["security"]["enable_waf"]:
            plugins.append({
                "name": "bot-detection",
                "config": {
                    "allow": ["googlebot", "bingbot"],
                    "deny": ["badbot"]
                }
            })
        
        # Create service
        service_id = await self.create_service(**service_config)
        
        # Add plugins
        for plugin in plugins:
            await self.add_plugin_to_service(service_id, plugin)
        
        # Create routes
        routes = [
            {
                "paths": ["/api/v1/market-data"],
                "methods": ["GET"],
                "strip_path": True,
                "tags": ["market-data", "public"]
            },
            {
                "paths": ["/api/v1/market-data/historical"],
                "methods": ["GET"],
                "strip_path": True,
                "tags": ["market-data", "historical"]
            },
            {
                "paths": ["/api/v1/market-data/realtime"],
                "methods": ["GET", "POST"],
                "strip_path": True,
                "tags": ["market-data", "realtime"]
            }
        ]
        
        for route_config in routes:
            await self.create_route(service_id, **route_config)
        
        logger.info("Market Data API created")
    
    async def _create_order_execution_api(self):
        """Create order execution API with strict security."""
        service_config = {
            "name": "order-execution-api",
            "url": "http://order-execution-service:8081",
            "tags": ["trading", "order-execution", "critical", self.environment.value]
        }
        
        plugins = [
            {
                "name": "rate-limiting",
                "config": {
                    "second": self.config["rate_limits"]["order_execution"]["second"],
                    "hour": self.config["rate_limits"]["order_execution"]["hour"],
                    "policy": "redis",
                    "fault_tolerant": False,  # Stricter for orders
                    "limit_by": "consumer"  # Limit by API key/consumer
                }
            },
            {
                "name": "request-size-limiting",
                "config": {
                    "allowed_payload_size": 10240  # 10KB max
                }
            },
            {
                "name": "cors",
                "config": {
                    "origins": ["https://trading.example.com"],
                    "methods": ["POST", "PUT", "DELETE"],
                    "headers": ["Content-Type", "Authorization"],
                    "credentials": True
                }
            }
        ]
        
        # JWT authentication is required for order execution
        plugins.append({
            "name": "jwt",
            "config": {
                "key_claim_name": "kid",
                "secret_is_base64": True,
                "claims_to_verify": ["exp", "nbf"],
                "maximum_expiration": 300  # 5 minutes for order tokens
            }
        })
        
        if self.config["security"]["require_ip_whitelist"]:
            plugins.append({
                "name": "ip-restriction",
                "config": {
                    "allow": self.config["security"]["allowed_ips"],
                    "deny": []
                }
            })
        
        # Create service
        service_id = await self.create_service(**service_config)
        
        # Add plugins
        for plugin in plugins:
            await self.add_plugin_to_service(service_id, plugin)
        
        # Create routes
        routes = [
            {
                "paths": ["/api/v1/orders"],
                "methods": ["POST"],
                "strip_path": True,
                "tags": ["orders", "execute"]
            },
            {
                "paths": ["/api/v1/orders/{order_id}"],
                "methods": ["GET", "PUT", "DELETE"],
                "strip_path": True,
                "tags": ["orders", "manage"]
            },
            {
                "paths": ["/api/v1/orders/batch"],
                "methods": ["POST"],
                "strip_path": True,
                "tags": ["orders", "batch"]
            }
        ]
        
        for route_config in routes:
            await self.create_route(service_id, **route_config)
        
        logger.info("Order Execution API created")
    
    async def _create_portfolio_api(self):
        """Create portfolio management API."""
        service_config = {
            "name": "portfolio-api",
            "url": "http://portfolio-service:8082",
            "tags": ["trading", "portfolio", self.environment.value]
        }
        
        plugins = [
            {
                "name": "rate-limiting",
                "config": {
                    "second": self.config["rate_limits"]["portfolio"]["second"],
                    "hour": self.config["rate_limits"]["portfolio"]["hour"],
                    "policy": "redis"
                }
            },
            {
                "name": "acl",
                "config": {
                    "allow": ["portfolio-read", "portfolio-write"],
                    "hide_groups_header": True
                }
            }
        ]
        
        if self.config["security"]["require_jwt"]:
            plugins.append({
                "name": "jwt",
                "config": {
                    "key_claim_name": "kid",
                    "secret_is_base64": True
                }
            })
        
        # Create service
        service_id = await self.create_service(**service_config)
        
        # Add plugins
        for plugin in plugins:
            await self.add_plugin_to_service(service_id, plugin)
        
        # Create routes
        routes = [
            {
                "paths": ["/api/v1/portfolio"],
                "methods": ["GET"],
                "strip_path": True,
                "tags": ["portfolio", "read"]
            },
            {
                "paths": ["/api/v1/portfolio/positions"],
                "methods": ["GET", "POST", "PUT"],
                "strip_path": True,
                "tags": ["portfolio", "positions"]
            },
            {
                "paths": ["/api/v1/portfolio/performance"],
                "methods": ["GET"],
                "strip_path": True,
                "tags": ["portfolio", "performance"]
            }
        ]
        
        for route_config in routes:
            await self.create_route(service_id, **route_config)
        
        logger.info("Portfolio API created")
    
    async def _create_websocket_api(self):
        """Create WebSocket API for real-time market data."""
        service_config = {
            "name": "market-data-ws",
            "url": "http://market-data-ws-service:8083",
            "tags": ["trading", "websocket", "realtime", self.environment.value]
        }
        
        plugins = [
            {
                "name": "websocket",
                "config": {
                    "connect_timeout": 60000,
                    "read_timeout": 60000,
                    "write_timeout": 60000,
                    "idle_timeout": 3600000
                }
            },
            {
                "name": "rate-limiting",
                "config": {
                    "second": 100,  # Connection attempts per second
                    "hour": 10000,   # Total connections per hour
                    "policy": "redis"
                }
            }
        ]
        
        # Create service
        service_id = await self.create_service(**service_config)
        
        # Add plugins
        for plugin in plugins:
            await self.add_plugin_to_service(service_id, plugin)
        
        # Create route
        await self.create_route(
            service_id,
            paths=["/ws/v1/market-data"],
            protocols=["ws", "wss"],
            strip_path=True,
            tags=["websocket", "market-data"]
        )
        
        logger.info("WebSocket API created")
    
    async def create_service(self, name: str, url: str, **kwargs) -> str:
        """Create a service in Kong."""
        payload = {
            "name": name,
            "url": url,
            **kwargs
        }
        
        try:
            response = await self.http_client.post(
                f"{self.kong_admin_url}/services",
                json=payload
            )
            
            if response.status_code == 201:
                service_data = response.json()
                service_id = service_data["id"]
                self.services[name] = service_data
                logger.info(f"Created service: {name} (ID: {service_id})")
                return service_id
            else:
                logger.error(f"Failed to create service {name}: {response.text}")
                raise Exception(f"Failed to create service: {response.text}")
                
        except Exception as e:
            logger.error(f"Error creating service {name}: {e}")
            raise
    
    async def create_route(self, service_id: str, **kwargs) -> str:
        """Create a route for a service."""
        payload = {
            "service": {"id": service_id},
            **kwargs
        }
        
        try:
            response = await self.http_client.post(
                f"{self.kong_admin_url}/routes",
                json=payload
            )
            
            if response.status_code == 201:
                route_data = response.json()
                route_id = route_data["id"]
                self.routes[route_id] = route_data
                
                # Extract path for logging
                paths = route_data.get("paths", ["unknown"])
                logger.info(f"Created route: {paths[0]} (ID: {route_id})")
                return route_id
            else:
                logger.error(f"Failed to create route: {response.text}")
                raise Exception(f"Failed to create route: {response.text}")
                
        except Exception as e:
            logger.error(f"Error creating route: {e}")
            raise
    
    async def add_plugin_to_service(self, service_id: str, plugin_config: Dict) -> str:
        """Add a plugin to a service."""
        payload = {
            "service": {"id": service_id},
            **plugin_config
        }
        
        try:
            response = await self.http_client.post(
                f"{self.kong_admin_url}/plugins",
                json=payload
            )
            
            if response.status_code == 201:
                plugin_data = response.json()
                plugin_name = plugin_config["name"]
                logger.info(f"Added plugin {plugin_name} to service {service_id}")
                return plugin_data["id"]
            else:
                logger.error(f"Failed to add plugin {plugin_config['name']}: {response.text}")
                
        except Exception as e:
            logger.error(f"Error adding plugin: {e}")
    
    async def create_consumer(self, username: str, custom_id: str = None) -> str:
        """Create a consumer (API user) in Kong."""
        payload = {
            "username": username,
            "custom_id": custom_id or str(uuid.uuid4())
        }
        
        try:
            response = await self.http_client.post(
                f"{self.kong_admin_url}/consumers",
                json=payload
            )
            
            if response.status_code == 201:
                consumer_data = response.json()
                consumer_id = consumer_data["id"]
                self.consumers[username] = consumer_data
                logger.info(f"Created consumer: {username} (ID: {consumer_id})")
                return consumer_id
            else:
                logger.error(f"Failed to create consumer {username}: {response.text}")
                
        except Exception as e:
            logger.error(f"Error creating consumer: {e}")
    
    async def create_jwt_credential(self, consumer_id: str, 
                                   algorithm: str = "HS256") -> Dict:
        """Create JWT credentials for a consumer."""
        try:
            response = await self.http_client.post(
                f"{self.kong_admin_url}/consumers/{consumer_id}/jwt"
            )
            
            if response.status_code == 201:
                credential = response.json()
                logger.info(f"Created JWT credential for consumer {consumer_id}")
                return credential
            else:
                logger.error(f"Failed to create JWT credential: {response.text}")
                
        except Exception as e:
            logger.error(f"Error creating JWT credential: {e}")
    
    async def create_api_key(self, consumer_id: str) -> Dict:
        """Create API key for a consumer."""
        try:
            response = await self.http_client.post(
                f"{self.kong_admin_url}/consumers/{consumer_id}/key-auth"
            )
            
            if response.status_code == 201:
                api_key_data = response.json()
                logger.info(f"Created API key for consumer {consumer_id}")
                return api_key_data
            else:
                logger.error(f"Failed to create API key: {response.text}")
                
        except Exception as e:
            logger.error(f"Error creating API key: {e}")
    
    async def get_metrics(self) -> Dict:
        """Get Kong metrics."""
        try:
            # Kong metrics endpoint
            response = await self.http_client.get(
                f"{self.kong_admin_url}/metrics"
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Failed to get Kong metrics: {response.status_code}")
                return {}
                
        except Exception as e:
            logger.error(f"Error getting Kong metrics: {e}")
            return {}
    
    async def simulate_request(self, service_name: str, endpoint: str,
                              method: str = "GET", payload: Dict = None) -> Dict:
        """Simulate a request through the gateway for testing."""
        # This would normally go through the Kong proxy
        # For simulation, we'll track metrics directly
        
        start_time = time.time()
        
        try:
            # Simulate request processing
            await asyncio.sleep(0.01)  # Simulate network latency
            
            # Determine success/failure
            success = np.random.random() > 0.05  # 95% success rate
            status = 200 if success else 500
            
            # Record metrics
            self.request_counter.labels(
                service=service_name,
                route=endpoint,
                status=status
            ).inc()
            
            latency = time.time() - start_time
            self.latency_histogram.labels(
                service=service_name,
                route=endpoint
            ).observe(latency)
            
            return {
                "success": success,
                "status": status,
                "latency": latency,
                "service": service_name,
                "endpoint": endpoint
            }
            
        except Exception as e:
            logger.error(f"Error in simulated request: {e}")
            return {
                "success": False,
                "error": str(e),
                "service": service_name,
                "endpoint": endpoint
            }
    
    async def export_configuration(self, filepath: str):
        """Export Kong configuration to a file."""
        config = {
            "environment": self.environment.value,
            "timestamp": datetime.utcnow().isoformat(),
            "services": self.services,
            "routes": self.routes,
            "consumers": self.consumers,
            "config": self.config
        }
        
        with open(filepath, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        logger.info(f"Exported configuration to {filepath}")
        return config


class TradingLoadBalancer:
    """
    Nginx-based load balancer optimized for trading workloads with
    ultra-low latency and high-throughput capabilities.
    """
    
    def __init__(self, upstream_servers: List[str], 
                 algorithm: LoadBalancingAlgorithm = LoadBalancingAlgorithm.LEAST_CONNECTIONS,
                 environment: TradingEnvironment = TradingEnvironment.DEVELOPMENT):
        self.upstream_servers = upstream_servers
        self.algorithm = algorithm
        self.environment = environment
        self.active_connections = defaultdict(int)
        self.server_weights = {}
        self.health_status = {}
        
        # Initialize server weights based on capacity
        self._initialize_server_weights()
        
        # Metrics
        self.request_counter = Counter(
            'load_balancer_requests_total',
            'Total requests through load balancer',
            ['upstream', 'status'],
            registry=metrics_registry
        )
        
        self.connection_gauge = Gauge(
            'load_balancer_active_connections',
            'Active connections per upstream',
            ['upstream'],
            registry=metrics_registry
        )
        
        self.latency_histogram = Histogram(
            'load_balancer_request_duration_seconds',
            'Request latency through load balancer',
            ['upstream'],
            buckets=[0.0001, 0.0005, 0.001, 0.005, 0.01, 0.05],
            registry=metrics_registry
        )
        
        logger.info(f"Initialized TradingLoadBalancer with {len(upstream_servers)} servers")
    
    def _initialize_server_weights(self):
        """Initialize server weights based on server capacity."""
        for server in self.upstream_servers:
            # Parse server string (format: host:port:weight)
            parts = server.split(':')
            if len(parts) == 3:
                host_port = f"{parts[0]}:{parts[1]}"
                weight = int(parts[2])
            else:
                host_port = server
                weight = 1  # Default weight
            
            self.server_weights[host_port] = weight
            self.health_status[host_port] = True  # Assume healthy initially
    
    def generate_nginx_config(self) -> str:
        """Generate Nginx configuration optimized for trading."""
        
        # Trading-specific optimizations
        worker_processes = "auto"
        worker_connections = 65536
        
        if self.environment == TradingEnvironment.PRODUCTION:
            worker_processes = "4"
            worker_connections = 100000
        
        config = f"""
# Trading System Load Balancer Configuration
# Environment: {self.environment.value}
# Generated: {datetime.utcnow().isoformat()}

worker_processes {worker_processes};
worker_rlimit_nofile {worker_connections * 2};

# Thread pools for I/O operations
# thread_pool default threads=32 max_queue=65536;

error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {{
    worker_connections {worker_connections};
    use epoll;
    multi_accept on;
    accept_mutex off;  # Reduced latency
}}

http {{
    # Trading-specific TCP optimizations
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    keepalive_requests 10000;
    client_max_body_size 10m;
    
    # Fast DNS resolution
    resolver 8.8.8.8 1.1.1.1 valid=300s;
    resolver_timeout 5s;
    
    # MIME types
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    # Logging format with trading metadata
    log_format trading '$remote_addr - $remote_user [$time_local] '
                       '"$request" $status $body_bytes_sent '
                       '"$http_referer" "$http_user_agent" '
                       '"$http_x_request_id" "$upstream_addr" '
                       '$request_time $upstream_response_time';
    
    access_log /var/log/nginx/access.log trading;
    
    # Rate limiting zones
    limit_req_zone $binary_remote_addr zone=trading_api:10m rate=1000r/s;
    limit_req_zone $http_apikey zone=api_keys:10m rate=100r/s;
    
    # Trading API upstream servers
    upstream trading_api_backend {{
"""
        
        # Add load balancing algorithm
        if self.algorithm == LoadBalancingAlgorithm.LEAST_CONNECTIONS:
            config += "        least_conn;\n"
        elif self.algorithm == LoadBalancingAlgorithm.IP_HASH:
            config += "        ip_hash;\n"
        elif self.algorithm == LoadBalancingAlgorithm.WEIGHTED_ROUND_ROBIN:
            config += "        weighted;\n"
        else:  # ROUND_ROBIN or default
            config += "        round_robin;\n"
        
        config += "        zone trading_backend 64k;\n\n"
        
        # Add server definitions with weights
        for server, weight in self.server_weights.items():
            health_check = "max_fails=3 fail_timeout=30s"
            
            if self.environment == TradingEnvironment.PRODUCTION:
                health_check = "max_fails=2 fail_timeout=10s slow_start=30s"
            
            config += f"        server {server} weight={weight} {health_check};\n"
        
        config += """    }
    
    # Market data WebSocket upstream
    upstream market_data_ws {
"""
        
        # WebSocket uses ip_hash for session persistence
        if self.algorithm == LoadBalancingAlgorithm.IP_HASH:
            config += "        ip_hash;\n"
        else:
            config += "        least_conn;\n"
        
        # WebSocket servers (same as API servers for now)
        for server in self.server_weights.keys():
            config += f"        server {server};\n"
        
        config += """    }
    
    # Main trading API server block
    server {
        listen 443 ssl http2;
        server_name api.trading-system.com;
        
        # SSL Configuration
        ssl_certificate /etc/nginx/ssl/trading.crt;
        ssl_certificate_key /etc/nginx/ssl/trading.key;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers 'ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305';
        ssl_prefer_server_ciphers on;
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 10m;
        
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
            proxy_set_header X-Request-ID $http_x_request_id;
            
            # Trading-specific timeouts
            proxy_connect_timeout 1s;
            proxy_send_timeout 10s;
            proxy_read_timeout 10s;
            
            # Buffer optimizations
            proxy_buffering on;
            proxy_buffer_size 16k;
            proxy_buffers 4 32k;
            
            # Health check endpoint
            health_check interval=5s fails=2 passes=2;
        }
        
        # WebSocket endpoint for real-time market data
        location /ws/v1/market-data {
            proxy_pass http://market_data_ws;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            
            # WebSocket optimizations
            proxy_buffering off;
            proxy_read_timeout 86400s;
            proxy_send_timeout 86400s;
            
            # Enable compression for WebSocket
            proxy_set_header Sec-WebSocket-Extensions "permessage-deflate; client_max_window_bits";
        }
        
        # Order execution endpoint (stricter limits)
        location /api/v1/orders {
            limit_req zone=trading_api burst=100 nodelay;
            limit_req zone=api_keys burst=10;
            
            # Request size limit for orders
            client_max_body_size 1k;
            
            proxy_pass http://trading_api_backend;
            proxy_set_header X-Trading-API-Key $http_apikey;
            
            # Faster timeouts for orders
            proxy_connect_timeout 500ms;
            proxy_send_timeout 5s;
            proxy_read_timeout 5s;
        }
        
        # Health check endpoint
        location /health {
            access_log off;
            add_header Content-Type text/plain;
            return 200 'healthy\\n';
        }
        
        # Status endpoint for monitoring
        location /nginx_status {
            stub_status on;
            access_log off;
            allow 127.0.0.1;
            allow 10.0.0.0/8;
            deny all;
        }
    }
    
    # HTTP to HTTPS redirect
    server {
        listen 80;
        server_name api.trading-system.com;
        return 301 https://$server_name$request_uri;
    }
}
"""
        
        return config
    
    async def select_server(self, client_ip: str = None) -> str:
        """Select an upstream server based on load balancing algorithm."""
        if not self.upstream_servers:
            raise ValueError("No upstream servers configured")
        
        # Filter to healthy servers only
        healthy_servers = [
            server for server in self.server_weights.keys()
            if self.health_status.get(server, True)
        ]
        
        if not healthy_servers:
            logger.warning("No healthy servers available, using all servers")
            healthy_servers = list(self.server_weights.keys())
        
        if self.algorithm == LoadBalancingAlgorithm.LEAST_CONNECTIONS:
            # Select server with least active connections
            server = min(
                healthy_servers,
                key=lambda s: self.active_connections.get(s, 0)
            )
            
        elif self.algorithm == LoadBalancingAlgorithm.IP_HASH:
            # Hash client IP for session persistence
            if client_ip:
                hash_val = hashlib.md5(client_ip.encode()).hexdigest()
                index = int(hash_val, 16) % len(healthy_servers)
                server = healthy_servers[index]
            else:
                # Fallback to round robin
                server = healthy_servers[0]
                
        elif self.algorithm == LoadBalancingAlgorithm.WEIGHTED_ROUND_ROBIN:
            # Weighted selection based on server weights
            total_weight = sum(self.server_weights[s] for s in healthy_servers)
            r = np.random.uniform(0, total_weight)
            
            current = 0
            for server in healthy_servers:
                current += self.server_weights[server]
                if r < current:
                    break
        
        else:  # ROUND_ROBIN or RANDOM
            if self.algorithm == LoadBalancingAlgorithm.RANDOM:
                server = np.random.choice(healthy_servers)
            else:
                # Simple round robin
                server = healthy_servers[0]
                # Rotate for next request
                self.upstream_servers = self.upstream_servers[1:] + [self.upstream_servers[0]]
        
        # Update active connections
        self.active_connections[server] = self.active_connections.get(server, 0) + 1
        self.connection_gauge.labels(upstream=server).set(
            self.active_connections[server]
        )
        
        return server
    
    async def release_server(self, server: str):
        """Release a server connection."""
        if server in self.active_connections:
            self.active_connections[server] = max(0, self.active_connections[server] - 1)
            self.connection_gauge.labels(upstream=server).set(
                self.active_connections[server]
            )
    
    async def check_server_health(self, server: str) -> bool:
        """Check health of an upstream server."""
        try:
            # Extract host and port
            if '://' in server:
                # Full URL
                url = server
            else:
                # host:port
                url = f"http://{server}"
            
            # Add health endpoint
            if not url.endswith('/health'):
                url = f"{url}/health"
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=2)) as session:
                async with session.get(url) as response:
                    healthy = response.status == 200
                    self.health_status[server] = healthy
                    
                    if not healthy:
                        logger.warning(f"Server {server} is unhealthy: {response.status}")
                    
                    return healthy
                    
        except Exception as e:
            logger.error(f"Health check failed for {server}: {e}")
            self.health_status[server] = False
            return False
    
    async def check_all_servers_health(self):
        """Check health of all upstream servers."""
        tasks = [
            self.check_server_health(server)
            for server in self.server_weights.keys()
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        healthy_count = sum(1 for r in results if r is True)
        logger.info(f"Health check: {healthy_count}/{len(results)} servers healthy")
        
        return {
            server: self.health_status.get(server, False)
            for server in self.server_weights.keys()
        }
    
    async def simulate_request(self, client_ip: str = None) -> Dict:
        """Simulate a request through the load balancer."""
        start_time = time.time()
        
        try:
            # Select server
            server = await self.select_server(client_ip)
            
            # Simulate request processing
            await asyncio.sleep(np.random.exponential(0.001))  # Random latency
            
            # Determine success/failure
            success = self.health_status.get(server, True) and np.random.random() > 0.01
            status = 200 if success else 500
            
            # Record metrics
            self.request_counter.labels(
                upstream=server,
                status=status
            ).inc()
            
            latency = time.time() - start_time
            self.latency_histogram.labels(upstream=server).observe(latency)
            
            # Release server
            await self.release_server(server)
            
            return {
                "success": success,
                "server": server,
                "status": status,
                "latency": latency,
                "active_connections": self.active_connections[server]
            }
            
        except Exception as e:
            logger.error(f"Error in simulated request: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def save_config(self, filepath: str):
        """Save Nginx configuration to file."""
        config = self.generate_nginx_config()
        
        with open(filepath, 'w') as f:
            f.write(config)
        
        logger.info(f"Saved Nginx configuration to {filepath}")
        return config


class TradingServiceMesh:
    """
    Istio service mesh implementation for trading systems with
    canary deployments, traffic management, and observability.
    """
    
    def __init__(self, namespace: str = "trading",
                 istio_control_plane: str = "istiod.istio-system.svc.cluster.local:15012"):
        self.namespace = namespace
        self.control_plane = istio_control_plane
        self.virtual_services = {}
        self.destination_rules = {}
        self.gateways = {}
        
        # Tracing setup
        self.tracer = self._setup_tracing()
        
        # Metrics
        self.mesh_request_counter = Counter(
            'service_mesh_requests_total',
            'Total requests through service mesh',
            ['service', 'version', 'response_code'],
            registry=metrics_registry
        )
        
        self.mesh_latency_histogram = Histogram(
            'service_mesh_request_duration_seconds',
            'Request latency through service mesh',
            ['service', 'version'],
            buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5],
            registry=metrics_registry
        )
        
        logger.info(f"Initialized TradingServiceMesh for namespace {namespace}")
    
    def _setup_tracing(self):
        """Setup Jaeger tracing for distributed tracing."""
        config = jaeger_client.Config(
            config={
                'sampler': {
                    'type': 'const',
                    'param': 1,
                },
                'logging': True,
                'local_agent': {
                    'reporting_host': 'jaeger-agent',
                    'reporting_port': 6831,
                }
            },
            service_name='trading-service-mesh',
            validate=True,
        )
        
        return config.initialize_tracer()
    
    async def setup_canary_deployment(self, service_name: str,
                                     new_version: str,
                                     current_version: str,
                                     canary_percentage: float = 10.0,
                                     rollback_metrics: Dict = None):
        """
        Setup canary deployment with automatic rollback based on metrics.
        
        Args:
            service_name: Name of the service
            new_version: New version to deploy (canary)
            current_version: Current stable version
            canary_percentage: Percentage of traffic to send to canary
            rollback_metrics: Metrics thresholds for automatic rollback
        """
        
        if rollback_metrics is None:
            rollback_metrics = {
                "error_rate_threshold": 0.01,  # 1% error rate
                "latency_threshold_ms": 100,   # 100ms P95 latency
                "time_window_minutes": 5       # 5-minute evaluation window
            }
        
        logger.info(f"Setting up canary deployment for {service_name}: "
                   f"{canary_percentage}% to {new_version}")
        
        # Create VirtualService for traffic splitting
        virtual_service = self._create_virtual_service(
            service_name=service_name,
            new_version=new_version,
            current_version=current_version,
            canary_percentage=canary_percentage
        )
        
        # Create DestinationRule for version subsets
        destination_rule = self._create_destination_rule(
            service_name=service_name,
            new_version=new_version,
            current_version=current_version
        )
        
        # Store configurations
        self.virtual_services[service_name] = virtual_service
        self.destination_rules[service_name] = destination_rule
        
        # Setup automatic rollback monitoring
        rollback_task = asyncio.create_task(
            self._monitor_canary_rollback(
                service_name=service_name,
                new_version=new_version,
                metrics_config=rollback_metrics
            )
        )
        
        return {
            "virtual_service": virtual_service,
            "destination_rule": destination_rule,
            "rollback_monitor": rollback_task,
            "canary_percentage": canary_percentage
        }
    
    def _create_virtual_service(self, service_name: str, new_version: str,
                               current_version: str, canary_percentage: float) -> Dict:
        """Create Istio VirtualService for traffic splitting."""
        
        new_weight = canary_percentage
        current_weight = 100 - canary_percentage
        
        virtual_service = {
            "apiVersion": "networking.istio.io/v1beta1",
            "kind": "VirtualService",
            "metadata": {
                "name": service_name,
                "namespace": self.namespace,
                "labels": {
                    "app": service_name,
                    "managed-by": "trading-service-mesh"
                }
            },
            "spec": {
                "hosts": [service_name],
                "http": [
                    # Canary traffic (based on header)
                    {
                        "match": [
                            {
                                "headers": {
                                    "x-canary": {
                                        "exact": "true"
                                    }
                                }
                            }
                        ],
                        "route": [
                            {
                                "destination": {
                                    "host": service_name,
                                    "subset": new_version
                                },
                                "weight": 100
                            }
                        ]
                    },
                    # Main traffic split
                    {
                        "route": [
                            {
                                "destination": {
                                    "host": service_name,
                                    "subset": current_version
                                },
                                "weight": int(current_weight)
                            },
                            {
                                "destination": {
                                    "host": service_name,
                                    "subset": new_version
                                },
                                "weight": int(new_weight)
                            }
                        ],
                        # Retry policy for trading requests
                        "retries": {
                            "attempts": 3,
                            "retryTimeout": "2s",
                            "retryOn": "5xx,gateway-error,connect-failure"
                        },
                        # Timeout for trading requests
                        "timeout": "5s"
                    }
                ]
            }
        }
        
        return virtual_service
    
    def _create_destination_rule(self, service_name: str,
                                new_version: str, current_version: str) -> Dict:
        """Create Istio DestinationRule for version subsets."""
        
        destination_rule = {
            "apiVersion": "networking.istio.io/v1beta1",
            "kind": "DestinationRule",
            "metadata": {
                "name": service_name,
                "namespace": self.namespace
            },
            "spec": {
                "host": service_name,
                "subsets": [
                    {
                        "name": current_version,
                        "labels": {
                            "version": current_version,
                            "stable": "true"
                        }
                    },
                    {
                        "name": new_version,
                        "labels": {
                            "version": new_version,
                            "canary": "true"
                        }
                    }
                ],
                "trafficPolicy": {
                    # Connection pool settings for trading
                    "connectionPool": {
                        "tcp": {
                            "maxConnections": 1000,
                            "connectTimeout": "1s"
                        },
                        "http": {
                            "http1MaxPendingRequests": 1000,
                            "http2MaxRequests": 1000,
                            "maxRequestsPerConnection": 100,
                            "maxRetries": 3
                        }
                    },
                    # Load balancing policy
                    "loadBalancer": {
                        "simple": "LEAST_CONN"
                    },
                    # Outlier detection (circuit breaking)
                    "outlierDetection": {
                        "consecutive5xxErrors": 5,
                        "interval": "30s",
                        "baseEjectionTime": "30s",
                        "maxEjectionPercent": 100
                    },
                    # TLS settings for service-to-service communication
                    "tls": {
                        "mode": "ISTIO_MUTUAL"  # Mutual TLS
                    }
                }
            }
        }
        
        return destination_rule
    
    async def _monitor_canary_rollback(self, service_name: str,
                                      new_version: str,
                                      metrics_config: Dict):
        """
        Monitor canary deployment metrics and trigger rollback if needed.
        """
        
        error_rate_threshold = metrics_config.get("error_rate_threshold", 0.01)
        latency_threshold = metrics_config.get("latency_threshold_ms", 100) / 1000.0
        time_window = metrics_config.get("time_window_minutes", 5) * 60
        
        logger.info(f"Starting canary monitoring for {service_name} ({new_version})")
        
        error_rates = []
        latencies = []
        
        try:
            while True:
                await asyncio.sleep(30)  # Check every 30 seconds
                
                # Simulate metric collection
                # In production, this would query Prometheus
                current_error_rate = np.random.beta(1, 99)  # Simulate ~1% error rate
                current_latency = np.random.exponential(0.05)  # Simulate ~50ms latency
                
                error_rates.append(current_error_rate)
                latencies.append(current_latency)
                
                # Keep only recent data
                max_samples = time_window // 30
                error_rates = error_rates[-max_samples:]
                latencies = latencies[-max_samples:]
                
                if len(error_rates) < 5:  # Need minimum samples
                    continue
                
                # Calculate averages
                avg_error_rate = np.mean(error_rates)
                avg_latency = np.mean(latencies)
                
                # Check thresholds
                if avg_error_rate > error_rate_threshold:
                    logger.warning(f"Canary {service_name}:{new_version} exceeding error rate "
                                 f"({avg_error_rate:.3f} > {error_rate_threshold})")
                    await self.rollback_canary(service_name, new_version,
                                             reason=f"High error rate: {avg_error_rate:.3f}")
                    break
                
                if avg_latency > latency_threshold:
                    logger.warning(f"Canary {service_name}:{new_version} exceeding latency "
                                 f"({avg_latency*1000:.1f}ms > {latency_threshold*1000:.1f}ms)")
                    await self.rollback_canary(service_name, new_version,
                                             reason=f"High latency: {avg_latency*1000:.1f}ms")
                    break
                
                # Log progress
                if len(error_rates) % 10 == 0:  # Every 5 minutes
                    logger.info(f"Canary {service_name}:{new_version} monitoring - "
                              f"Error rate: {avg_error_rate:.3f}, "
                              f"Latency: {avg_latency*1000:.1f}ms")
                    
        except asyncio.CancelledError:
            logger.info(f"Cancelled canary monitoring for {service_name}")
        except Exception as e:
            logger.error(f"Error in canary monitoring: {e}")
    
    async def rollback_canary(self, service_name: str, version: str, reason: str = ""):
        """Rollback canary deployment to previous version."""
        logger.warning(f"Rolling back canary {service_name}:{version} - {reason}")
        
        if service_name in self.virtual_services:
            # Update VirtualService to send 0% traffic to canary
            vs = self.virtual_services[service_name]
            
            # Find the main route (not the header-based one)
            for http_route in vs["spec"]["http"]:
                if "match" not in http_route:  # This is the main route
                    # Set all traffic to stable version
                    http_route["route"] = [
                        {
                            "destination": {
                                "host": service_name,
                                "subset": "v1.0.0"  # Would get from config
                            },
                            "weight": 100
                        }
                    ]
                    break
            
            # In production, this would apply the updated VirtualService to Kubernetes
            logger.info(f"Rolled back {service_name} - canary traffic set to 0%")
            
            return {
                "service": service_name,
                "action": "rollback",
                "reason": reason,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def setup_blue_green_deployment(self, service_name: str,
                                         blue_version: str,
                                         green_version: str):
        """Setup blue-green deployment for zero-downtime updates."""
        
        logger.info(f"Setting up blue-green deployment for {service_name}")
        
        # Create Gateway for external traffic
        gateway = self._create_gateway(service_name)
        
        # Create VirtualService for traffic switching
        virtual_service = {
            "apiVersion": "networking.istio.io/v1beta1",
            "kind": "VirtualService",
            "metadata": {
                "name": f"{service_name}-blue-green",
                "namespace": self.namespace
            },
            "spec": {
                "hosts": [f"{service_name}.example.com"],
                "gateways": [gateway["metadata"]["name"]],
                "http": [
                    {
                        "route": [
                            {
                                "destination": {
                                    "host": service_name,
                                    "subset": blue_version
                                }
                            }
                        ]
                    }
                ]
            }
        }
        
        # Store configurations
        self.gateways[service_name] = gateway
        self.virtual_services[f"{service_name}-blue-green"] = virtual_service
        
        return {
            "gateway": gateway,
            "virtual_service": virtual_service,
            "current_traffic": "blue",
            "blue_version": blue_version,
            "green_version": green_version
        }
    
    def _create_gateway(self, service_name: str) -> Dict:
        """Create Istio Gateway for external traffic."""
        
        gateway = {
            "apiVersion": "networking.istio.io/v1beta1",
            "kind": "Gateway",
            "metadata": {
                "name": f"{service_name}-gateway",
                "namespace": self.namespace
            },
            "spec": {
                "selector": {
                    "istio": "ingressgateway"
                },
                "servers": [
                    {
                        "port": {
                            "number": 443,
                            "name": "https",
                            "protocol": "HTTPS"
                        },
                        "hosts": [f"{service_name}.example.com"],
                        "tls": {
                            "mode": "SIMPLE",
                            "credentialName": "trading-certificate"
                        }
                    }
                ]
            }
        }
        
        return gateway
    
    async def switch_traffic(self, service_name: str, to_version: str):
        """Switch traffic between blue and green deployments."""
        
        vs_name = f"{service_name}-blue-green"
        if vs_name not in self.virtual_services:
            raise ValueError(f"Blue-green deployment not found for {service_name}")
        
        virtual_service = self.virtual_services[vs_name]
        
        # Update VirtualService to route to new version
        for http_route in virtual_service["spec"]["http"]:
            http_route["route"] = [
                {
                    "destination": {
                        "host": service_name,
                        "subset": to_version
                    }
                }
            ]
        
        logger.info(f"Switched {service_name} traffic to {to_version}")
        
        return {
            "service": service_name,
            "new_version": to_version,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def simulate_mesh_request(self, service_name: str, version: str = None):
        """Simulate a request through the service mesh."""
        
        start_time = time.time()
        
        # Start trace
        with self.tracer.start_active_span(f'mesh_request_{service_name}') as scope:
            span = scope.span
            span.set_tag('service', service_name)
            span.set_tag('version', version or 'unknown')
            span.set_tag('mesh', 'istio')
            
            try:
                # Simulate request processing
                processing_time = np.random.exponential(0.02)  # ~20ms average
                await asyncio.sleep(processing_time)
                
                # Determine success
                success = np.random.random() > 0.02  # 98% success rate
                status = 200 if success else 500
                
                # Record metrics
                self.mesh_request_counter.labels(
                    service=service_name,
                    version=version or 'unknown',
                    response_code=status
                ).inc()
                
                latency = time.time() - start_time
                self.mesh_latency_histogram.labels(
                    service=service_name,
                    version=version or 'unknown'
                ).observe(latency)
                
                # Add trace information
                span.set_tag('http.status_code', status)
                span.set_tag('latency', latency)
                
                return {
                    "success": success,
                    "status": status,
                    "latency": latency,
                    "service": service_name,
                    "version": version,
                    "trace_id": span.context.trace_id
                }
                
            except Exception as e:
                span.set_tag('error', True)
                span.log_kv({'error.message': str(e)})
                
                logger.error(f"Error in mesh request simulation: {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "service": service_name,
                    "version": version
                }
    
    def export_configurations(self, directory: str):
        """Export all service mesh configurations to files."""
        
        os.makedirs(directory, exist_ok=True)
        
        exported = {}
        
        # Export VirtualServices
        vs_dir = os.path.join(directory, "virtualservices")
        os.makedirs(vs_dir, exist_ok=True)
        
        for name, vs in self.virtual_services.items():
            filename = os.path.join(vs_dir, f"{name}.yaml")
            with open(filename, 'w') as f:
                yaml.dump(vs, f, default_flow_style=False)
            exported[f"virtualservice/{name}"] = filename
        
        # Export DestinationRules
        dr_dir = os.path.join(directory, "destinationrules")
        os.makedirs(dr_dir, exist_ok=True)
        
        for name, dr in self.destination_rules.items():
            filename = os.path.join(dr_dir, f"{name}.yaml")
            with open(filename, 'w') as f:
                yaml.dump(dr, f, default_flow_style=False)
            exported[f"destinationrule/{name}"] = filename
        
        # Export Gateways
        gw_dir = os.path.join(directory, "gateways")
        os.makedirs(gw_dir, exist_ok=True)
        
        for name, gw in self.gateways.items():
            filename = os.path.join(gw_dir, f"{name}.yaml")
            with open(filename, 'w') as f:
                yaml.dump(gw, f, default_flow_style=False)
            exported[f"gateway/{name}"] = filename
        
        logger.info(f"Exported {len(exported)} service mesh configurations to {directory}")
        return exported


class TradingSecurity:
    """
    Security implementation for trading APIs including WAF, rate limiting,
    authentication, and request validation.
    """
    
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.redis_client = None
        self.waf_rules = self._load_waf_rules()
        self.rate_limit_configs = self._load_rate_limit_configs()
        self.jwt_secret = self._generate_jwt_secret()
        
        # Security metrics
        self.security_events_counter = Counter(
            'security_events_total',
            'Total security events',
            ['type', 'severity'],
            registry=metrics_registry
        )
        
        self.blocked_requests_counter = Counter(
            'security_blocked_requests_total',
            'Total blocked requests',
            ['rule_id', 'reason'],
            registry=metrics_registry
        )
        
        logger.info("Initialized TradingSecurity")
    
    def _load_waf_rules(self) -> List[Dict]:
        """Load trading-specific WAF rules."""
        return [
            # SQL injection prevention
            {
                "id": "sql_injection_1",
                "name": "SQL Injection Detection",
                "pattern": r"(union.*select|select.*from|insert.*into|delete.*from|drop.*table|truncate.*table)",
                "action": "block",
                "severity": "critical",
                "description": "Detects SQL injection attempts"
            },
            # XSS prevention
            {
                "id": "xss_1",
                "name": "Cross-Site Scripting Detection",
                "pattern": r"(<script.*?>|javascript:|onload=|onerror=)",
                "action": "block",
                "severity": "high",
                "description": "Detects XSS attempts"
            },
            # Trading-specific patterns
            {
                "id": "trading_manipulation_1",
                "name": "Suspicious Order Pattern",
                "pattern": r"quantity\s*[<>]\s*1000000|price\s*[<>]\s*[0-9]{6}",
                "action": "alert",
                "severity": "high",
                "description": "Detects suspiciously large orders or prices"
            },
            {
                "id": "trading_manipulation_2",
                "name": "Rapid Order Submission",
                "pattern": None,  # Time-based, not regex
                "action": "rate_limit",
                "severity": "medium",
                "description": "Detects rapid order submission patterns"
            },
            # API key abuse
            {
                "id": "api_key_abuse_1",
                "name": "API Key Brute Force",
                "pattern": r"apikey=.*&apikey=|apikey.*apikey",
                "action": "block",
                "severity": "high",
                "description": "Detects multiple API keys in single request"
            }
        ]
    
    def _load_rate_limit_configs(self) -> Dict:
        """Load rate limiting configurations."""
        return {
            "ip_based": {
                "window": 60,  # seconds
                "max_requests": 1000,
                "algorithm": RateLimitAlgorithm.SLIDING_WINDOW
            },
            "api_key_based": {
                "window": 60,
                "max_requests": 100,
                "algorithm": RateLimitAlgorithm.TOKEN_BUCKET
            },
            "user_based": {
                "window": 3600,  # 1 hour
                "max_requests": 10000,
                "algorithm": RateLimitAlgorithm.FIXED_WINDOW
            },
            "endpoint_based": {
                "/api/v1/orders": {
                    "window": 60,
                    "max_requests": 50
                },
                "/api/v1/market-data": {
                    "window": 1,  # per second
                    "max_requests": 100
                }
            }
        }
    
    def _generate_jwt_secret(self) -> str:
        """Generate JWT secret key."""
        # In production, this should be loaded from secure storage
        return base64.b64encode(hashlib.sha256(b"trading-jwt-secret").digest()).decode()
    
    async def connect(self):
        """Connect to Redis."""
        self.redis_client = await redis.from_url(
            self.redis_url,
            decode_responses=True,
            max_connections=50
        )
        logger.info("Connected TradingSecurity to Redis")
    
    async def disconnect(self):
        """Disconnect from Redis."""
        if self.redis_client:
            await self.redis_client.aclose()
        logger.info("Disconnected TradingSecurity")
    
    async def validate_request(self, request_data: Dict) -> Tuple[bool, str, Dict]:
        """
        Validate trading API request against security rules.
        
        Returns:
            Tuple of (is_valid, error_message, validation_details)
        """
        validation_result = {
            "waf_passed": True,
            "rate_limit_passed": True,
            "authentication_passed": True,
            "signature_passed": True,
            "rules_checked": [],
            "blocked_rules": []
        }
        
        # Extract request components
        client_ip = request_data.get("client_ip", "0.0.0.0")
        path = request_data.get("path", "")
        method = request_data.get("method", "GET")
        headers = request_data.get("headers", {})
        body = request_data.get("body", "")
        
        # 1. Check WAF rules
        waf_result = await self._check_waf_rules(
            path=path,
            headers=headers,
            body=body,
            client_ip=client_ip
        )
        
        validation_result["waf_passed"] = waf_result["passed"]
        validation_result["rules_checked"].extend(waf_result["rules_checked"])
        validation_result["blocked_rules"].extend(waf_result["blocked_rules"])
        
        if not waf_result["passed"]:
            self.blocked_requests_counter.labels(
                rule_id=waf_result["blocked_rules"][0] if waf_result["blocked_rules"] else "unknown",
                reason="waf_rule"
            ).inc()
            
            return False, f"WAF violation: {waf_result['reason']}", validation_result
        
        # 2. Check rate limits
        rate_limit_result = await self._check_rate_limits(
            client_ip=client_ip,
            api_key=headers.get("X-API-Key"),
            user_id=headers.get("X-User-ID"),
            path=path,
            method=method
        )
        
        validation_result["rate_limit_passed"] = rate_limit_result["passed"]
        
        if not rate_limit_result["passed"]:
            self.blocked_requests_counter.labels(
                rule_id="rate_limit",
                reason=f"{rate_limit_result['type']}_exceeded"
            ).inc()
            
            return False, f"Rate limit exceeded: {rate_limit_result['reason']}", validation_result
        
        # 3. Check authentication (for protected endpoints)
        if self._requires_authentication(path):
            auth_result = await self._validate_authentication(headers)
            validation_result["authentication_passed"] = auth_result["passed"]
            
            if not auth_result["passed"]:
                self.security_events_counter.labels(
                    type="authentication_failure",
                    severity="high"
                ).inc()
                
                return False, f"Authentication failed: {auth_result['reason']}", validation_result
        
        # 4. Check request signing (for order execution)
        if self._requires_request_signing(path, method):
            signature_result = await self._validate_request_signature(headers, body)
            validation_result["signature_passed"] = signature_result["passed"]
            
            if not signature_result["passed"]:
                self.security_events_counter.labels(
                    type="signature_failure",
                    severity="critical"
                ).inc()
                
                return False, f"Invalid request signature: {signature_result['reason']}", validation_result
        
        # All checks passed
        return True, "OK", validation_result
    
    async def _check_waf_rules(self, **request_data) -> Dict:
        """Check request against WAF rules."""
        result = {
            "passed": True,
            "reason": "",
            "rules_checked": [],
            "blocked_rules": []
        }
        
        # Combine all request data for pattern matching
        request_text = json.dumps(request_data, default=str)
        
        for rule in self.waf_rules:
            result["rules_checked"].append(rule["id"])
            
            if rule["pattern"]:
                # Regex-based rule
                import re
                if re.search(rule["pattern"], request_text, re.IGNORECASE):
                    result["passed"] = False
                    result["reason"] = f"Matched rule: {rule['name']}"
                    result["blocked_rules"].append(rule["id"])
                    
                    # Log security event
                    self.security_events_counter.labels(
                        type="waf_match",
                        severity=rule["severity"]
                    ).inc()
                    
                    if rule["action"] == "block":
                        break  # Immediate block
                    # else "alert" continues checking
            
            # Time-based rules would be checked here
        
        return result
    
    async def _check_rate_limits(self, **kwargs) -> Dict:
        """Check rate limits using sliding window algorithm."""
        result = {
            "passed": True,
            "reason": "",
            "type": ""
        }
        
        client_ip = kwargs.get("client_ip")
        api_key = kwargs.get("api_key")
        path = kwargs.get("path")
        
        # Check IP-based rate limiting
        ip_key = f"rate_limit:ip:{client_ip}"
        ip_passed = await self._check_sliding_window_limit(
            key=ip_key,
            window=60,
            max_requests=1000
        )
        
        if not ip_passed:
            result.update({
                "passed": False,
                "reason": "IP rate limit exceeded",
                "type": "ip"
            })
            return result
        
        # Check API key-based rate limiting
        if api_key:
            api_key_key = f"rate_limit:api_key:{api_key}"
            api_key_passed = await self._check_token_bucket_limit(
                key=api_key_key,
                capacity=100,
                refill_rate=1.67  # 100 requests per minute = 1.67 per second
            )
            
            if not api_key_passed:
                result.update({
                    "passed": False,
                    "reason": "API key rate limit exceeded",
                    "type": "api_key"
                })
                return result
        
        # Check endpoint-specific rate limiting
        if path in self.rate_limit_configs["endpoint_based"]:
            endpoint_config = self.rate_limit_configs["endpoint_based"][path]
            endpoint_key = f"rate_limit:endpoint:{path}:{client_ip}"
            
            endpoint_passed = await self._check_sliding_window_limit(
                key=endpoint_key,
                window=endpoint_config["window"],
                max_requests=endpoint_config["max_requests"]
            )
            
            if not endpoint_passed:
                result.update({
                    "passed": False,
                    "reason": f"Endpoint {path} rate limit exceeded",
                    "type": "endpoint"
                })
                return result
        
        return result
    
    async def _check_sliding_window_limit(self, key: str, window: int, max_requests: int) -> bool:
        """Check rate limit using sliding window algorithm."""
        if not self.redis_client:
            return True  # No Redis, no rate limiting
        
        current_time = time.time()
        window_start = current_time - window
        
        # Use Redis sorted set for sliding window
        pipeline = self.redis_client.pipeline()
        
        # Remove old entries
        pipeline.zremrangebyscore(key, 0, window_start)
        
        # Get current count
        pipeline.zcard(key)
        
        # Add current request
        pipeline.zadd(key, {str(current_time): current_time})
        
        # Set expiration
        pipeline.expire(key, window + 1)
        
        results = await pipeline.execute()
        current_count = results[1]
        
        return current_count < max_requests
    
    async def _check_token_bucket_limit(self, key: str, capacity: int, refill_rate: float) -> bool:
        """Check rate limit using token bucket algorithm."""
        if not self.redis_client:
            return True
        
        current_time = time.time()
        
        pipeline = self.redis_client.pipeline()
        
        # Get current token count and last update time
        pipeline.hmget(key, "tokens", "last_update")
        
        results = await pipeline.execute()
        token_data = results[0]
        
        if token_data[0] is None:
            # First request, initialize bucket
            tokens = capacity - 1
            last_update = current_time
        else:
            tokens = float(token_data[0])
            last_update = float(token_data[1])
            
            # Refill tokens based on elapsed time
            elapsed = current_time - last_update
            refill = elapsed * refill_rate
            tokens = min(capacity, tokens + refill)
            
            # Check if we have enough tokens
            if tokens < 1:
                return False
            
            tokens -= 1
        
        # Update token bucket
        update_pipeline = self.redis_client.pipeline()
        update_pipeline.hset(key, "tokens", tokens)
        update_pipeline.hset(key, "last_update", current_time)
        update_pipeline.expire(key, 3600)  # Expire after 1 hour
        
        await update_pipeline.execute()
        
        return True
    
    def _requires_authentication(self, path: str) -> bool:
        """Check if path requires authentication."""
        protected_paths = [
            "/api/v1/orders",
            "/api/v1/portfolio",
            "/api/v1/account"
        ]
        
        return any(path.startswith(p) for p in protected_paths)
    
    async def _validate_authentication(self, headers: Dict) -> Dict:
        """Validate JWT token or API key."""
        result = {
            "passed": False,
            "reason": "No authentication provided",
            "method": None
        }
        
        # Check for JWT token
        auth_header = headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            
            try:
                # Decode and verify JWT
                payload = jwt.decode(
                    token,
                    self.jwt_secret,
                    algorithms=["HS256"],
                    options={"verify_exp": True}
                )
                
                # Check required claims for trading
                required_claims = ["sub", "exp", "iat", "trading_permissions"]
                if all(claim in payload for claim in required_claims):
                    result.update({
                        "passed": True,
                        "reason": "JWT valid",
                        "method": "jwt",
                        "user_id": payload.get("sub")
                    })
                else:
                    result["reason"] = "Missing required JWT claims"
                    
            except jwt.ExpiredSignatureError:
                result["reason"] = "JWT token expired"
            except jwt.InvalidTokenError as e:
                result["reason"] = f"Invalid JWT token: {str(e)}"
        
        # Check for API key
        elif "X-API-Key" in headers:
            api_key = headers["X-API-Key"]
            
            # In production, validate against database
            # For simulation, accept any non-empty key
            if api_key and len(api_key) >= 32:  # Basic validation
                result.update({
                    "passed": True,
                    "reason": "API key valid",
                    "method": "api_key"
                })
            else:
                result["reason"] = "Invalid API key format"
        
        return result
    
    def _requires_request_signing(self, path: str, method: str) -> bool:
        """Check if request requires digital signature."""
        # Order execution requires signing
        return path.startswith("/api/v1/orders") and method in ["POST", "PUT", "DELETE"]
    
    async def _validate_request_signature(self, headers: Dict, body: str) -> Dict:
        """Validate request signature for order execution."""
        result = {
            "passed": False,
            "reason": "No signature provided"
        }
        
        signature = headers.get("X-Signature")
        timestamp = headers.get("X-Timestamp")
        api_key = headers.get("X-API-Key")
        
        if not all([signature, timestamp, api_key]):
            result["reason"] = "Missing signature components"
            return result
        
        # Check timestamp (prevent replay attacks)
        try:
            request_time = datetime.fromtimestamp(float(timestamp))
            current_time = datetime.utcnow()
            time_diff = (current_time - request_time).total_seconds()
            
            if abs(time_diff) > 300:  # 5 minutes tolerance
                result["reason"] = f"Timestamp out of range: {time_diff:.0f}s"
                return result
        except (ValueError, TypeError):
            result["reason"] = "Invalid timestamp"
            return result
        
        # In production, you would:
        # 1. Look up API key to get secret
        # 2. Recreate signature: HMAC-SHA256(timestamp + method + path + body)
        # 3. Compare with provided signature
        
        # For simulation, accept any valid base64 signature
        try:
            # Just validate it's proper base64
            base64.b64decode(signature, validate=True)
            result.update({
                "passed": True,
                "reason": "Signature valid"
            })
        except:
            result["reason"] = "Invalid signature format"
        
        return result
    
    def generate_jwt_token(self, user_id: str, permissions: List[str], 
                          expires_in: int = 3600) -> str:
        """Generate JWT token for API access."""
        
        payload = {
            "sub": user_id,
            "iat": int(time.time()),
            "exp": int(time.time()) + expires_in,
            "trading_permissions": permissions,
            "env": self.environment.value if hasattr(self, 'environment') else "development"
        }
        
        token = jwt.encode(payload, self.jwt_secret, algorithm="HS256")
        return token
    
    async def audit_request(self, request_data: Dict, validation_result: Dict):
        """Audit and log security-relevant request data."""
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": request_data.get("request_id", str(uuid.uuid4())),
            "client_ip": request_data.get("client_ip"),
            "path": request_data.get("path"),
            "method": request_data.get("method"),
            "user_agent": request_data.get("headers", {}).get("User-Agent"),
            "validation_result": validation_result,
            "environment": self.environment.value if hasattr(self, 'environment') else "development"
        }
        
        # In production, this would write to secure audit log
        logger.info(f"Security audit: {json.dumps(audit_entry, default=str)}")
        
        return audit_entry
    
    async def get_security_metrics(self) -> Dict:
        """Get security metrics summary."""
        # In production, these would be aggregated from logs/metrics
        return {
            "total_requests": 0,  # Would be actual counts
            "blocked_requests": 0,
            "waf_matches": 0,
            "authentication_failures": 0,
            "rate_limit_exceeded": 0,
            "timestamp": datetime.utcnow().isoformat()
        }


class TradingAPIMonitoring:
    """
    Comprehensive monitoring for trading APIs with metrics, tracing,
    and dashboard generation.
    """
    
    def __init__(self, prometheus_url: str = "http://localhost:9090",
                 grafana_url: str = "http://localhost:3000"):
        self.prometheus_url = prometheus_url
        self.grafana_url = grafana_url
        self.http_client = httpx.AsyncClient(timeout=30.0)
        
        # Metrics registry
        self.registry = metrics_registry
        
        # Custom trading metrics
        self._setup_trading_metrics()
        
        logger.info("Initialized TradingAPIMonitoring")
    
    def _setup_trading_metrics(self):
        """Setup trading-specific metrics."""
        
        # API performance metrics
        self.api_requests = Counter(
            'trading_api_requests_total',
            'Total trading API requests',
            ['service', 'endpoint', 'method', 'status'],
            registry=self.registry
        )
        
        self.api_latency = Histogram(
            'trading_api_request_duration_seconds',
            'Trading API request latency',
            ['service', 'endpoint', 'method'],
            buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 5.0],
            registry=self.registry
        )
        
        # Trading business metrics
        self.orders_processed = Counter(
            'trading_orders_processed_total',
            'Total orders processed',
            ['symbol', 'side', 'order_type', 'status'],
            registry=self.registry
        )
        
        self.order_execution_latency = Histogram(
            'trading_order_execution_latency_ms',
            'Order execution latency',
            ['symbol', 'order_type'],
            buckets=[1, 5, 10, 50, 100, 500, 1000],
            registry=self.registry
        )
        
        self.market_data_subscribers = Gauge(
            'trading_market_data_subscribers',
            'Active market data subscribers',
            ['symbol', 'data_type'],
            registry=self.registry
        )
        
        # System metrics
        self.active_connections = Gauge(
            'trading_active_connections',
            'Active connections',
            ['service', 'protocol'],
            registry=self.registry
        )
        
        self.error_rate = Gauge(
            'trading_error_rate',
            'Error rate percentage',
            ['service', 'error_type'],
            registry=self.registry
        )
        
        # Trading performance metrics
        self.pnl_today = Gauge(
            'trading_pnl_today',
            'Profit and loss today',
            ['portfolio', 'strategy'],
            registry=self.registry
        )
        
        self.position_count = Gauge(
            'trading_position_count',
            'Number of active positions',
            ['portfolio'],
            registry=self.registry
        )
    
    async def record_api_request(self, service: str, endpoint: str,
                                method: str, status: int, latency: float):
        """Record API request metrics."""
        self.api_requests.labels(
            service=service,
            endpoint=endpoint,
            method=method,
            status=status
        ).inc()
        
        self.api_latency.labels(
            service=service,
            endpoint=endpoint,
            method=method
        ).observe(latency)
    
    async def record_order(self, symbol: str, side: str,
                          order_type: str, status: str, latency_ms: float = None):
        """Record order execution metrics."""
        self.orders_processed.labels(
            symbol=symbol,
            side=side,
            order_type=order_type,
            status=status
        ).inc()
        
        if latency_ms is not None:
            self.order_execution_latency.labels(
                symbol=symbol,
                order_type=order_type
            ).observe(latency_ms / 1000.0)  # Convert to seconds
    
    async def update_market_data_subscribers(self, symbol: str,
                                           data_type: str, count: int):
        """Update market data subscriber count."""
        self.market_data_subscribers.labels(
            symbol=symbol,
            data_type=data_type
        ).set(count)
    
    async def query_prometheus(self, query: str, time_range: str = "5m") -> Dict:
        """Query Prometheus for metrics."""
        try:
            params = {
                "query": query,
                "time": time_range
            }
            
            response = await self.http_client.get(
                f"{self.prometheus_url}/api/v1/query",
                params=params
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Prometheus query failed: {response.status_code}")
                return {"status": "error", "data": {}}
                
        except Exception as e:
            logger.error(f"Error querying Prometheus: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_api_health_metrics(self) -> Dict:
        """Get comprehensive API health metrics."""
        
        queries = {
            "request_rate": 'rate(trading_api_requests_total[5m])',
            "error_rate": 'rate(trading_api_requests_total{status=~"5.."}[5m]) / rate(trading_api_requests_total[5m])',
            "p95_latency": 'histogram_quantile(0.95, rate(trading_api_request_duration_seconds_bucket[5m]))',
            "p99_latency": 'histogram_quantile(0.99, rate(trading_api_request_duration_seconds_bucket[5m]))',
            "active_connections": 'trading_active_connections',
            "order_rate": 'rate(trading_orders_processed_total[5m])'
        }
        
        results = {}
        for name, query in queries.items():
            result = await self.query_prometheus(query)
            results[name] = result
        
        return results
    
    def generate_grafana_dashboard(self, title: str = "Trading API Dashboard") -> Dict:
        """Generate Grafana dashboard configuration."""
        
        dashboard = {
            "dashboard": {
                "title": title,
                "tags": ["trading", "api", "monitoring"],
                "timezone": "browser",
                "panels": [
                    # Panel 1: API Request Rate
                    {
                        "title": "API Request Rate",
                        "type": "graph",
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0},
                        "targets": [
                            {
                                "expr": "rate(trading_api_requests_total[5m])",
                                "legendFormat": "{{service}} - {{endpoint}}",
                                "refId": "A"
                            }
                        ],
                        "yaxes": [
                            {"format": "reqps", "min": 0},
                            {"format": "short", "min": 0}
                        ],
                        "lines": True,
                        "fill": 1,
                        "linewidth": 2
                    },
                    
                    # Panel 2: API Error Rate
                    {
                        "title": "API Error Rate (%)",
                        "type": "graph",
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0},
                        "targets": [
                            {
                                "expr": "100 * (rate(trading_api_requests_total{status=~\"5..\"}[5m]) / rate(trading_api_requests_total[5m]))",
                                "legendFormat": "{{service}}",
                                "refId": "A"
                            }
                        ],
                        "yaxes": [
                            {"format": "percent", "min": 0, "max": 100},
                            {"format": "short", "min": 0}
                        ],
                        "thresholds": [
                            {"value": 1, "color": "yellow"},
                            {"value": 5, "color": "red"}
                        ]
                    },
                    
                    # Panel 3: API Latency (P95)
                    {
                        "title": "API Latency (95th percentile)",
                        "type": "graph",
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8},
                        "targets": [
                            {
                                "expr": "histogram_quantile(0.95, rate(trading_api_request_duration_seconds_bucket[5m]))",
                                "legendFormat": "{{service}} - {{endpoint}}",
                                "refId": "A"
                            }
                        ],
                        "yaxes": [
                            {"format": "s", "min": 0},
                            {"format": "short", "min": 0}
                        ],
                        "thresholds": [
                            {"value": 0.1, "color": "yellow"},
                            {"value": 0.5, "color": "red"}
                        ]
                    },
                    
                    # Panel 4: Order Execution Metrics
                    {
                        "title": "Order Execution Rate",
                        "type": "graph",
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8},
                        "targets": [
                            {
                                "expr": "rate(trading_orders_processed_total[5m])",
                                "legendFormat": "{{symbol}} - {{side}}",
                                "refId": "A"
                            }
                        ],
                        "yaxes": [
                            {"format": "ops", "min": 0},
                            {"format": "short", "min": 0}
                        ]
                    },
                    
                    # Panel 5: Active Connections
                    {
                        "title": "Active Connections",
                        "type": "stat",
                        "gridPos": {"h": 4, "w": 6, "x": 0, "y": 16},
                        "targets": [
                            {
                                "expr": "sum(trading_active_connections)",
                                "refId": "A",
                                "format": "short"
                            }
                        ],
                        "valueName": "current"
                    },
                    
                    # Panel 6: Market Data Subscribers
                    {
                        "title": "Market Data Subscribers",
                        "type": "stat",
                        "gridPos": {"h": 4, "w": 6, "x": 6, "y": 16},
                        "targets": [
                            {
                                "expr": "sum(trading_market_data_subscribers)",
                                "refId": "A",
                                "format": "short"
                            }
                        ],
                        "valueName": "current"
                    },
                    
                    # Panel 7: Order Execution Latency Heatmap
                    {
                        "title": "Order Execution Latency Distribution",
                        "type": "heatmap",
                        "gridPos": {"h": 8, "w": 24, "x": 0, "y": 20},
                        "targets": [
                            {
                                "expr": "rate(trading_order_execution_latency_ms_bucket[5m])",
                                "legendFormat": "{{symbol}}",
                                "refId": "A"
                            }
                        ],
                        "yAxis": {"format": "ms"}
                    }
                ],
                "time": {
                    "from": "now-1h",
                    "to": "now"
                },
                "refresh": "10s"
            },
            "overwrite": True
        }
        
        return dashboard
    
    async def setup_alerting_rules(self) -> Dict:
        """Setup Prometheus alerting rules for trading APIs."""
        
        alerting_rules = {
            "groups": [
                {
                    "name": "trading_api_alerts",
                    "rules": [
                        # High error rate alert
                        {
                            "alert": "HighAPIErrorRate",
                            "expr": """
                                sum(rate(trading_api_requests_total{status=~"5.."}[5m])) 
                                / sum(rate(trading_api_requests_total[5m])) > 0.05
                            """,
                            "for": "2m",
                            "labels": {
                                "severity": "critical",
                                "service": "trading-api"
                            },
                            "annotations": {
                                "summary": "High error rate in trading API",
                                "description": "Error rate is {{ $value }}%",
                                "runbook_url": "https://trading.example.com/runbooks/api-errors"
                            }
                        },
                        
                        # High latency alert
                        {
                            "alert": "HighAPILatency",
                            "expr": """
                                histogram_quantile(0.95, 
                                    rate(trading_api_request_duration_seconds_bucket[5m])) > 0.5
                            """,
                            "for": "3m",
                            "labels": {
                                "severity": "warning"
                            },
                            "annotations": {
                                "summary": "High latency in trading API",
                                "description": "P95 latency is {{ $value }}s"
                            }
                        },
                        
                        # Order execution failure alert
                        {
                            "alert": "OrderExecutionFailure",
                            "expr": """
                                rate(trading_orders_processed_total{status="failed"}[5m]) > 0.1
                            """,
                            "for": "1m",
                            "labels": {
                                "severity": "critical"
                            },
                            "annotations": {
                                "summary": "High order execution failure rate",
                                "description": "{{ $value }} failed orders per second"
                            }
                        },
                        
                        # Market data subscription drop
                        {
                            "alert": "MarketDataSubscriptionDrop",
                            "expr": """
                                decrease(trading_market_data_subscribers[5m]) < -100
                            """,
                            "for": "2m",
                            "labels": {
                                "severity": "warning"
                            },
                            "annotations": {
                                "summary": "Market data subscriptions dropped",
                                "description": "Lost {{ $value }} subscribers"
                            }
                        }
                    ]
                }
            ]
        }
        
        return alerting_rules
    
    async def generate_monitoring_report(self) -> Dict:
        """Generate comprehensive monitoring report."""
        
        # Get metrics
        health_metrics = await self.get_api_health_metrics()
        
        # Calculate derived metrics
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "summary": {
                "status": "healthy",  # Would be determined from metrics
                "total_services": 5,  # Would be dynamic
                "total_endpoints": 15,
                "uptime": "99.95%"  # Would be calculated
            },
            "metrics": health_metrics,
            "alerts": {
                "critical": 0,
                "warning": 0,
                "info": 0
            },
            "recommendations": []
        }
        
        # Add recommendations based on metrics
        error_rate = self._extract_metric_value(health_metrics, "error_rate")
        if error_rate and error_rate > 0.01:
            report["recommendations"].append(
                "Consider implementing circuit breaking for failing services"
            )
        
        latency = self._extract_metric_value(health_metrics, "p95_latency")
        if latency and latency > 0.1:
            report["recommendations"].append(
                "Review database queries and cache configuration for high-latency endpoints"
            )
        
        return report
    
    def _extract_metric_value(self, metrics: Dict, metric_name: str) -> Optional[float]:
        """Extract value from Prometheus query result."""
        try:
            metric_data = metrics.get(metric_name, {})
            result = metric_data.get("data", {}).get("result", [])
            if result and len(result) > 0:
                value = result[0].get("value", [])
                if len(value) > 1:
                    return float(value[1])
        except:
            pass
        return None
    
    async def export_metrics(self, format: str = "prometheus") -> str:
        """Export metrics in specified format."""
        if format == "prometheus":
            # Generate Prometheus exposition format
            output = []
            for collector in self.registry.collect():
                for metric in collector.samples:
                    line = f"{metric.name}"
                    if metric.labels:
                        labels = ",".join(
                            f'{k}="{v}"' for k, v in metric.labels.items()
                        )
                        line += f"{{{labels}}}"
                    line += f" {metric.value}"
                    output.append(line)
            
            return "\n".join(output)
        
        elif format == "json":
            # Export as JSON
            metrics_data = {}
            for collector in self.registry.collect():
                for metric in collector.samples:
                    key = metric.name
                    if key not in metrics_data:
                        metrics_data[key] = []
                    metrics_data[key].append({
                        "labels": metric.labels,
                        "value": metric.value,
                        "timestamp": metric.timestamp
                    })
            
            return json.dumps(metrics_data, indent=2)
        
        else:
            raise ValueError(f"Unsupported format: {format}")


async def demonstrate_trading_api_gateway():
    """Demonstrate the complete trading API gateway and load balancing setup."""
    
    print("\n" + "=" * 80)
    print("Day 89: API Gateway & Load Balancing Setup")
    print("=" * 80)
    
    # Configuration
    kong_admin_url = "http://localhost:8001"
    redis_url = "redis://localhost:6379"
    upstream_servers = [
        "trading-api-1:8080:2",  # host:port:weight
        "trading-api-2:8080:2",
        "trading-api-3:8080:1",
        "trading-api-4:8080:1"
    ]
    
    try:
        print("\n1. Setting up Trading API Gateway...")
        
        # Initialize API Gateway
        api_gateway = TradingAPIGateway(
            kong_admin_url=kong_admin_url,
            redis_url=redis_url,
            environment=TradingEnvironment.PRODUCTION
        )
        
        await api_gateway.connect()
        
        # Setup trading APIs
        await api_gateway.setup_trading_apis()
        
        # Create test consumer
        consumer_id = await api_gateway.create_consumer(
            username="quant_fund_alpha",
            custom_id="fund-alpha-001"
        )
        
        # Create JWT credentials for consumer
        jwt_credential = await api_gateway.create_jwt_credential(consumer_id)
        
        print(f"   Created consumer: {consumer_id}")
        print(f"   JWT credential: {jwt_credential.get('key', 'N/A')}")
        
        print("\n2. Setting up Load Balancer...")
        
        # Initialize Load Balancer
        load_balancer = TradingLoadBalancer(
            upstream_servers=upstream_servers,
            algorithm=LoadBalancingAlgorithm.LEAST_CONNECTIONS,
            environment=TradingEnvironment.PRODUCTION
        )
        
        # Generate Nginx configuration
        nginx_config = load_balancer.generate_nginx_config()
        print(f"   Generated Nginx configuration ({len(nginx_config)} bytes)")
        
        # Check server health
        health_status = await load_balancer.check_all_servers_health()
        healthy_servers = sum(1 for v in health_status.values() if v)
        print(f"   Server health: {healthy_servers}/{len(health_status)} healthy")
        
        print("\n3. Setting up Service Mesh for Canary Deployments...")
        
        # Initialize Service Mesh
        service_mesh = TradingServiceMesh(
            namespace="trading-production"
        )
        
        # Setup canary deployment for order service
        canary_config = await service_mesh.setup_canary_deployment(
            service_name="order-service",
            new_version="v1.1.0",
            current_version="v1.0.0",
            canary_percentage=10.0,
            rollback_metrics={
                "error_rate_threshold": 0.01,
                "latency_threshold_ms": 100,
                "time_window_minutes": 5
            }
        )
        
        print(f"   Setup canary deployment: {canary_config['canary_percentage']}% traffic")
        
        print("\n4. Setting up Security Layer...")
        
        # Initialize Security
        security = TradingSecurity(redis_url=redis_url)
        await security.connect()
        
        # Generate JWT token for testing
        jwt_token = security.generate_jwt_token(
            user_id="trader-001",
            permissions=["market_data:read", "orders:execute", "portfolio:read"]
        )
        
        print(f"   Generated JWT token: {jwt_token[:50]}...")
        
        print("\n5. Setting up Monitoring...")
        
        # Initialize Monitoring
        monitoring = TradingAPIMonitoring(
            prometheus_url="http://localhost:9090",
            grafana_url="http://localhost:3000"
        )
        
        # Generate Grafana dashboard
        dashboard = monitoring.generate_grafana_dashboard()
        print(f"   Generated Grafana dashboard with {len(dashboard['dashboard']['panels'])} panels")
        
        print("\n6. Running Simulations...")
        
        # Simulate API requests
        print("   Simulating API requests through gateway...")
        
        simulation_results = []
        for i in range(100):
            result = await api_gateway.simulate_request(
                service_name="market-data-api",
                endpoint="/api/v1/market-data/AAPL",
                method="GET"
            )
            simulation_results.append(result)
        
        success_rate = sum(1 for r in simulation_results if r['success']) / len(simulation_results)
        avg_latency = np.mean([r.get('latency', 0) for r in simulation_results])
        
        print(f"   Simulation results: {success_rate:.1%} success, {avg_latency*1000:.1f}ms avg latency")
        
        # Simulate load balancer requests
        print("   Simulating load balanced requests...")
        
        lb_results = []
        for i in range(50):
            result = await load_balancer.simulate_request(
                client_ip=f"10.0.0.{i % 256}"
            )
            lb_results.append(result)
        
        lb_success_rate = sum(1 for r in lb_results if r['success']) / len(lb_results)
        print(f"   Load balancer results: {lb_success_rate:.1%} success rate")
        
        # Simulate service mesh requests
        print("   Simulating service mesh requests...")
        
        mesh_results = []
        for i in range(30):
            result = await service_mesh.simulate_mesh_request(
                service_name="order-service",
                version="v1.0.0" if i < 27 else "v1.1.0"  # 90% to stable, 10% to canary
            )
            mesh_results.append(result)
        
        mesh_success_rate = sum(1 for r in mesh_results if r['success']) / len(mesh_results)
        print(f"   Service mesh results: {mesh_success_rate:.1%} success rate")
        
        # Test security validation
        print("   Testing security validation...")
        
        test_request = {
            "client_ip": "10.0.0.100",
            "path": "/api/v1/orders",
            "method": "POST",
            "headers": {
                "Authorization": f"Bearer {jwt_token}",
                "X-API-Key": "test-api-key-1234567890",
                "X-Signature": "test-signature",
                "X-Timestamp": str(time.time()),
                "User-Agent": "TradingClient/1.0"
            },
            "body": json.dumps({
                "symbol": "AAPL",
                "side": "buy",
                "quantity": 100,
                "price": 150.25
            })
        }
        
        is_valid, error_msg, validation_details = await security.validate_request(test_request)
        print(f"   Security validation: {'PASS' if is_valid else 'FAIL'} - {error_msg}")
        
        print("\n7. Generating Reports and Configurations...")
        
        # Export configurations
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        
        # Export API Gateway configuration
        gateway_config = await api_gateway.export_configuration(
            f"gateway_config_{timestamp}.yaml"
        )
        
        # Save load balancer configuration
        nginx_config_file = f"nginx_config_{timestamp}.conf"
        load_balancer.save_config(nginx_config_file)
        
        # Export service mesh configurations
        mesh_config_dir = f"service_mesh_config_{timestamp}"
        mesh_configs = service_mesh.export_configurations(mesh_config_dir)
        
        # Generate monitoring report
        monitoring_report = await monitoring.generate_monitoring_report()
        with open(f"monitoring_report_{timestamp}.json", 'w') as f:
            json.dump(monitoring_report, f, indent=2)
        
        print(f"   Exported configurations:")
        print(f"     - Gateway config: gateway_config_{timestamp}.yaml")
        print(f"     - Nginx config: {nginx_config_file}")
        print(f"     - Service mesh configs: {mesh_config_dir}/")
        print(f"     - Monitoring report: monitoring_report_{timestamp}.json")
        
        print("\n" + "=" * 80)
        print("DEMONSTRATION COMPLETE")
        print("=" * 80)
        
        # Summary
        summary = {
            "components_initialized": [
                "TradingAPIGateway",
                "TradingLoadBalancer", 
                "TradingServiceMesh",
                "TradingSecurity",
                "TradingAPIMonitoring"
            ],
            "apis_configured": list(api_gateway.services.keys()),
            "upstream_servers": len(upstream_servers),
            "load_balancing_algorithm": load_balancer.algorithm.value,
            "canary_deployment": "active" if canary_config else "inactive",
            "security_validation": "implemented",
            "monitoring_dashboard": "generated",
            "configurations_exported": 4
        }
        
        print("\nSummary:")
        for key, value in summary.items():
            print(f"  {key.replace('_', ' ').title()}: {value}")
        
        print("\nGenerated Files:")
        print("  • Gateway configuration YAML")
        print("  • Nginx load balancer configuration")
        print("  • Service mesh configurations (VirtualServices, DestinationRules)")
        print("  • Monitoring dashboard configuration")
        print("  • Security audit logs")
        
        print("\nKey Features Demonstrated:")
        print("  1. Kong API Gateway with trading-specific plugins")
        print("  2. Nginx load balancer with ultra-low latency optimizations")
        print("  3. Istio service mesh for canary deployments")
        print("  4. Advanced security with WAF, rate limiting, and JWT")
        print("  5. Comprehensive monitoring with Prometheus and Grafana")
        print("  6. Automatic rollback based on trading metrics")
        print("  7. Request signing for order execution security")
        
        return summary
        
    except Exception as e:
        print(f"\nError during demonstration: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}
    
    finally:
        # Cleanup
        print("\nCleaning up...")
        # Note: In production, you would properly close connections
        pass


async def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Trading API Gateway & Load Balancer')
    parser.add_argument('--demo', action='store_true', help='Run complete demonstration')
    parser.add_argument('--test-gateway', help='Test API gateway with URL')
    parser.add_argument('--test-load-balancer', help='Test load balancer with servers')
    parser.add_argument('--generate-config', help='Generate configuration for environment')
    
    args = parser.parse_args()
    
    if args.demo:
        await demonstrate_trading_api_gateway()
    
    elif args.test_gateway:
        # Test API gateway functionality
        gateway = TradingAPIGateway(
            kong_admin_url=args.test_gateway,
            redis_url="redis://localhost:6379"
        )
        await gateway.connect()
        
        # Test endpoints
        metrics = await gateway.get_metrics()
        print(f"Gateway metrics: {json.dumps(metrics, indent=2)}")
    
    elif args.test_load_balancer:
        # Test load balancer functionality
        servers = args.test_load_balancer.split(',')
        lb = TradingLoadBalancer(
            upstream_servers=servers,
            algorithm=LoadBalancingAlgorithm.LEAST_CONNECTIONS
        )
        
        config = lb.generate_nginx_config()
        print("Generated Nginx configuration:")
        print(config)
    
    elif args.generate_config:
        # Generate configuration for specific environment
        env = TradingEnvironment(args.generate_config)
        
        gateway = TradingAPIGateway(
            kong_admin_url="http://localhost:8001",
            redis_url="redis://localhost:6379",
            environment=env
        )
        
        config = gateway.config
        print(f"Configuration for {env.value}:")
        print(json.dumps(config, indent=2))
    
    else:
        # Default: run demonstration
        await demonstrate_trading_api_gateway()


if __name__ == "__main__":
    asyncio.run(main())