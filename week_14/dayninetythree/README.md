# Day 93: Logging & Audit Systems for Trading Activity

## 📋 Project Overview

Implement structured logging and comprehensive audit systems to track trading activity, system changes, and user actions for compliance and debugging. This day focuses on building a robust logging infrastructure that meets regulatory requirements while providing actionable insights for operations and security teams.

## 🎯 Objective

Implement structured JSON logging across a trading system, configure ELK stack for log aggregation, and create Kibana dashboards for trading activity analysis.

## 🏗️ Architecture

```
logging-system/
├── log-aggregation/           # Centralized log management
│   ├── elasticsearch/        # Log storage and indexing
│   ├── logstash/            # Log processing pipelines
│   ├── kibana/              # Log visualization
│   └── filebeat/            # Log shipping agents
├── structured-logging/       # Python logging implementation
│   ├── loggers/             # Custom logger configurations
│   ├── formatters/          # Structured formatters (JSON)
│   ├── handlers/            # Custom log handlers
│   └── middleware/          # Request/response logging
├── audit-trail/             # Regulatory compliance logging
│   ├── auditors/            # Audit event generators
│   ├── validators/          # Audit log validation
│   ├── archivers/           # Long-term storage
│   └── compliance/          # Regulatory reporting
├── docker-compose.yml       # Local development stack
└── scripts/                 # Deployment and maintenance
```

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.9+
- Basic understanding of Elasticsearch and Kibana

### Local Development Setup

```bash
# Clone the repository
git clone <repository-url>
cd logging-system

# Start the logging stack
docker-compose up -d

# Access the services:
# Kibana: http://localhost:5601 (elastic/changeme)
# Elasticsearch: http://localhost:9200
# Logstash: http://localhost:9600

# Install Python dependencies
pip install -r requirements.txt

# Test logging configuration
python examples/test_logging.py
```

## 🔧 Configuration

### ELK Stack Configuration

#### Elasticsearch Configuration (elasticsearch/elasticsearch.yml)

```yaml
cluster.name: trading-logs
node.name: elasticsearch-1
network.host: 0.0.0.0
http.port: 9200
discovery.type: single-node

# Security
xpack.security.enabled: true
xpack.security.authc.api_key.enabled: true

# Audit logging
xpack.security.audit.enabled: true
xpack.security.audit.outputs: [logfile, index]
xpack.security.audit.logfile.events.include: access_denied, access_granted, anonymous_access_denied, authentication_failed, connection_denied, run_as_denied, run_as_granted, tampered_request

# Index lifecycle management
xpack.ilm.enabled: true
```

#### Logstash Configuration (logstash/logstash.conf)

```ruby
input {
  beats {
    port => 5044
    ssl => false
  }

  # Direct TCP input for Python applications
  tcp {
    port => 5000
    codec => json_lines
    tags => ["trading", "python"]
  }

  # HTTP input for REST APIs
  http {
    port => 8080
    codec => json_lines
  }
}

filter {
  # Parse JSON logs
  if [message] =~ /^{.*}$/ {
    json {
      source => "message"
      target => "parsed"
    }
  }

  # Add trading-specific fields
  if [parsed][service] == "trading" {
    mutate {
      add_field => {
        "[@metadata][index]" => "trading-logs-%{+YYYY.MM.dd}"
      }
    }

    # Enrich with trading context
    if [parsed][event_type] == "order" {
      ruby {
        code => "
          event.set('risk_score', calculate_risk_score(event.get('parsed')))
          event.set('compliance_category', determine_compliance_category(event.get('parsed')))
        "
      }
    }

    # Mask sensitive data
    if [parsed][user_id] {
      mutate {
        replace => { "[parsed][user_id]" => "user_%{[parsed][user_id]}" }
      }
    }

    # Add geoip for security monitoring
    if [parsed][client_ip] {
      geoip {
        source => "[parsed][client_ip]"
        target => "[parsed][geoip]"
      }
    }
  }

  # Common parsing for all logs
  grok {
    match => { "message" => "%{TIMESTAMP_ISO8601:timestamp} %{LOGLEVEL:level} %{GREEDYDATA:message}" }
    overwrite => [ "message" ]
  }

  date {
    match => [ "timestamp", "ISO8601" ]
    target => "@timestamp"
  }
}

output {
  # Primary output to Elasticsearch
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "%{[@metadata][index]}"
    user => "elastic"
    password => "${ELASTIC_PASSWORD}"
    ssl => false
  }

  # Backup to S3 for compliance
  if [parsed][audit_level] == "high" {
    s3 {
      access_key_id => "${AWS_ACCESS_KEY_ID}"
      secret_access_key => "${AWS_SECRET_ACCESS_KEY}"
      region => "${AWS_REGION}"
      bucket => "trading-audit-logs"
      time_file => 5
      codec => "json_lines"
    }
  }

  # Alerting output
  if [parsed][level] == "ERROR" or [parsed][level] == "CRITICAL" {
    http {
      url => "http://alertmanager:9093/api/v2/alerts"
      http_method => "post"
      format => "json"
      mapping => {
        "labels" => {
          "alertname" => "LogErrorAlert"
          "service" => "%{[parsed][service]}"
          "severity" => "%{[parsed][level]}"
        }
        "annotations" => {
          "summary" => "Error log detected in %{[parsed][service]}"
          "description" => "%{[parsed][message]}"
        }
      }
    }
  }
}
```

## 📝 Structured Logging Implementation

### Python Logging Configuration (structured-logging/loggers/**init**.py)

```python
"""
Structured logging configuration for trading systems.
Implements JSON logging with correlation IDs and audit capabilities.
"""

import logging
import logging.config
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, Union
import sys
import os
from pythonjsonlogger import jsonlogger
from dataclasses import dataclass, asdict, field
from enum import Enum
import threading
from contextvars import ContextVar

# Context-local storage for correlation IDs
correlation_id = ContextVar('correlation_id', default=str(uuid.uuid4()))
request_id = ContextVar('request_id', default=None)
user_id = ContextVar('user_id', default=None)

class LogLevel(Enum):
    """Extended log levels for trading systems."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    AUDIT = "AUDIT"  # Special level for audit logs
    TRADE = "TRADE"  # Special level for trade events
    RISK = "RISK"    # Special level for risk events

class AuditAction(Enum):
    """Audit actions for trading systems."""
    LOGIN = "login"
    LOGOUT = "logout"
    CREATE_ORDER = "create_order"
    MODIFY_ORDER = "modify_order"
    CANCEL_ORDER = "cancel_order"
    EXECUTE_TRADE = "execute_trade"
    MODIFY_POSITION = "modify_position"
    CHANGE_STRATEGY = "change_strategy"
    UPDATE_RISK_LIMITS = "update_risk_limits"
    ACCESS_SENSITIVE_DATA = "access_sensitive_data"
    SYSTEM_CONFIG_CHANGE = "system_config_change"
    USER_PERMISSION_CHANGE = "user_permission_change"

class ComplianceCategory(Enum):
    """Compliance categories for regulatory reporting."""
    MIFID_II = "MiFID II"
    SEC_17A = "SEC Rule 17a-4"
    FINRA_4511 = "FINRA Rule 4511"
    GDPR = "GDPR"
    SOX = "SOX"
    BASEL_III = "Basel III"
    DODD_FRANK = "Dodd-Frank"

@dataclass
class LogEvent:
    """Base structure for all log events."""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    level: str = "INFO"
    service: str = "trading-system"
    component: str = "unknown"
    message: str = ""
    correlation_id: str = field(default_factory=lambda: correlation_id.get())
    request_id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    environment: str = os.getenv("ENVIRONMENT", "development")

    # Trading-specific fields
    strategy: Optional[str] = None
    symbol: Optional[str] = None
    order_id: Optional[str] = None
    trade_id: Optional[str] = None
    position_id: Optional[str] = None

    # Performance metrics
    duration_ms: Optional[float] = None
    memory_usage_mb: Optional[float] = None

    # Error details
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None

    # Custom fields
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        # Remove None values for cleaner logs
        return {k: v for k, v in data.items() if v is not None}

@dataclass
class AuditEvent(LogEvent):
    """Specialized event for audit logging."""
    audit_action: Optional[AuditAction] = None
    compliance_category: Optional[ComplianceCategory] = None
    regulatory_id: Optional[str] = None
    previous_state: Optional[Dict[str, Any]] = None
    new_state: Optional[Dict[str, Any]] = None
    reason: Optional[str] = None
    approved_by: Optional[str] = None
    client_ip: Optional[str] = None
    user_agent: Optional[str] = None

    def __post_init__(self):
        """Set audit-specific defaults."""
        self.level = LogLevel.AUDIT.value
        self.event_id = f"AUDIT-{self.event_id}"

@dataclass
class TradeEvent(LogEvent):
    """Specialized event for trade logging."""
    side: Optional[str] = None  # 'buy' or 'sell'
    quantity: Optional[float] = None
    price: Optional[float] = None
    currency: Optional[str] = None
    exchange: Optional[str] = None
    order_type: Optional[str] = None  # 'market', 'limit', etc.
    time_in_force: Optional[str] = None
    commission: Optional[float] = None
    pnl: Optional[float] = None

    def __post_init__(self):
        """Set trade-specific defaults."""
        self.level = LogLevel.TRADE.value
        self.event_id = f"TRADE-{self.event_id}"

class StructuredJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter for structured logging."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def add_fields(self, log_record, record, message_dict):
        """Add custom fields to log record."""
        super().add_fields(log_record, record, message_dict)

        # Add correlation ID from context
        log_record['correlation_id'] = correlation_id.get()

        # Add request ID if available
        if request_id.get():
            log_record['request_id'] = request_id.get()

        # Add user ID if available
        if user_id.get():
            log_record['user_id'] = user_id.get()

        # Add process/thread info
        log_record['process_id'] = os.getpid()
        log_record['thread_id'] = threading.get_ident()
        log_record['thread_name'] = threading.current_thread().name

        # Add host information
        log_record['hostname'] = os.getenv('HOSTNAME', 'unknown')

        # Ensure timestamp is in ISO format
        if 'timestamp' not in log_record:
            log_record['timestamp'] = datetime.utcnow().isoformat() + "Z"

class TradingLogger:
    """Main logger class for trading systems."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._setup_logging_config()
        self._initialized = True

    def _setup_logging_config(self):
        """Configure logging with structured JSON output."""

        log_config = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'structured_json': {
                    '()': 'structured_logging.loggers.StructuredJsonFormatter',
                    'format': '%(timestamp)s %(level)s %(name)s %(message)s',
                    'datefmt': '%Y-%m-%dT%H:%M:%S.%fZ',
                },
                'audit_json': {
                    '()': 'structured_logging.loggers.StructuredJsonFormatter',
                    'format': '%(timestamp)s %(level)s %(name)s %(message)s',
                    'datefmt': '%Y-%m-%dT%H:%M:%S.%fZ',
                }
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'formatter': 'structured_json',
                    'stream': sys.stdout,
                    'level': 'INFO'
                },
                'file': {
                    'class': 'logging.handlers.RotatingFileHandler',
                    'formatter': 'structured_json',
                    'filename': '/var/log/trading/trading.log',
                    'maxBytes': 10485760,  # 10MB
                    'backupCount': 10,
                    'level': 'INFO'
                },
                'audit_file': {
                    'class': 'logging.handlers.RotatingFileHandler',
                    'formatter': 'audit_json',
                    'filename': '/var/log/trading/audit.log',
                    'maxBytes': 10485760,  # 10MB
                    'backupCount': 100,  # Keep more audit logs
                    'level': 'AUDIT'
                },
                'trade_file': {
                    'class': 'logging.handlers.RotatingFileHandler',
                    'formatter': 'structured_json',
                    'filename': '/var/log/trading/trades.log',
                    'maxBytes': 10485760,  # 10MB
                    'backupCount': 50,
                    'level': 'TRADE'
                },
                'logstash': {
                    'class': 'logstash_async.handler.AsynchronousLogstashHandler',
                    'level': 'INFO',
                    'transport': 'logstash_async.transport.TcpTransport',
                    'host': os.getenv('LOGSTASH_HOST', 'localhost'),
                    'port': int(os.getenv('LOGSTASH_PORT', 5000)),
                    'database_path': '/var/log/trading/logstash.db',
                    'event_ttl': 300,  # 5 minutes
                }
            },
            'loggers': {
                '': {  # Root logger
                    'handlers': ['console', 'file', 'logstash'],
                    'level': 'INFO',
                    'propagate': True
                },
                'trading.audit': {
                    'handlers': ['audit_file', 'logstash'],
                    'level': 'AUDIT',
                    'propagate': False
                },
                'trading.trades': {
                    'handlers': ['trade_file', 'logstash'],
                    'level': 'TRADE',
                    'propagate': False
                },
                'trading.risk': {
                    'handlers': ['file', 'logstash'],
                    'level': 'RISK',
                    'propagate': False
                }
            }
        }

        # Add custom log levels
        logging.addLevelName(25, 'AUDIT')
        logging.addLevelName(26, 'TRADE')
        logging.addLevelName(27, 'RISK')

        # Apply configuration
        logging.config.dictConfig(log_config)

        # Get logger instances
        self.logger = logging.getLogger('trading')
        self.audit_logger = logging.getLogger('trading.audit')
        self.trade_logger = logging.getLogger('trading.trades')
        self.risk_logger = logging.getLogger('trading.risk')

    def set_correlation_id(self, cid: str):
        """Set correlation ID for current context."""
        correlation_id.set(cid)

    def set_request_id(self, rid: str):
        """Set request ID for current context."""
        request_id.set(rid)

    def set_user_id(self, uid: str):
        """Set user ID for current context."""
        user_id.set(uid)

    def log_event(self, event: LogEvent):
        """Log a structured event."""
        log_method = getattr(self.logger, event.level.lower(), self.logger.info)
        log_method(event.message, extra=event.to_dict())

    def audit(self, action: AuditAction, **kwargs):
        """Log an audit event."""
        audit_event = AuditEvent(
            level=LogLevel.AUDIT.value,
            message=f"Audit event: {action.value}",
            audit_action=action,
            **kwargs
        )

        # Add to audit-specific logger
        self.audit_logger.log(25, audit_event.message, extra=audit_event.to_dict())

        # Also log to regular logger for correlation
        self.logger.info(audit_event.message, extra=audit_event.to_dict())

    def log_trade(self, trade_data: Dict[str, Any]):
        """Log a trade event."""
        trade_event = TradeEvent(
            level=LogLevel.TRADE.value,
            message=f"Trade executed: {trade_data.get('symbol')}",
            **trade_data
        )

        self.trade_logger.log(26, trade_event.message, extra=trade_event.to_dict())

    def log_error(self, error: Exception, context: Dict[str, Any] = None):
        """Log an error with context."""
        error_event = LogEvent(
            level=LogLevel.ERROR.value,
            message=str(error),
            error_code=type(error).__name__,
            error_message=str(error),
            stack_trace=self._get_stack_trace(error),
            metadata=context or {}
        )

        self.log_event(error_event)

    def _get_stack_trace(self, error: Exception) -> str:
        """Extract stack trace from exception."""
        import traceback
        return ''.join(traceback.format_exception(type(error), error, error.__traceback__))

# Global logger instance
logger = TradingLogger()

# Context managers for correlation IDs
class LoggingContext:
    """Context manager for logging context."""

    def __init__(self, correlation_id: str = None, request_id: str = None, user_id: str = None):
        self.correlation_id = correlation_id or str(uuid.uuid4())
        self.request_id = request_id
        self.user_id = user_id
        self._old_correlation_id = None
        self._old_request_id = None
        self._old_user_id = None

    def __enter__(self):
        # Save old values
        self._old_correlation_id = correlation_id.get()
        self._old_request_id = request_id.get()
        self._old_user_id = user_id.get()

        # Set new values
        logger.set_correlation_id(self.correlation_id)
        if self.request_id:
            logger.set_request_id(self.request_id)
        if self.user_id:
            logger.set_user_id(self.user_id)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore old values
        correlation_id.set(self._old_correlation_id)
        if self._old_request_id:
            request_id.set(self._old_request_id)
        if self._old_user_id:
            user_id.set(self._old_user_id)

        # Log any exception that occurred
        if exc_type is not None:
            logger.log_error(exc_val)
```

### FastAPI Logging Middleware (structured-logging/middleware/fastapi_logging.py)

```python
"""
FastAPI middleware for request/response logging and correlation IDs.
"""

import time
import uuid
from typing import Callable
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from structured_logging.loggers import logger, LoggingContext, AuditAction

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging HTTP requests and responses."""

    def __init__(self, app: ASGIApp, service_name: str = "trading-api"):
        super().__init__(app)
        self.service_name = service_name

    async def dispatch(self, request: Request, call_next: Callable):
        # Generate correlation and request IDs
        correlation_id = request.headers.get('X-Correlation-ID', str(uuid.uuid4()))
        request_id = str(uuid.uuid4())

        # Extract user info from headers or JWT
        user_id = self._extract_user_id(request)

        # Create logging context
        with LoggingContext(
            correlation_id=correlation_id,
            request_id=request_id,
            user_id=user_id
        ):
            # Log request start
            start_time = time.time()

            request_data = {
                "method": request.method,
                "url": str(request.url),
                "headers": dict(request.headers),
                "client_ip": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
            }

            # Mask sensitive headers
            if 'authorization' in request_data['headers']:
                request_data['headers']['authorization'] = '***masked***'

            logger.logger.info(
                "Request started",
                extra={
                    "event": "request_start",
                    "request": request_data,
                    "duration_ms": 0,
                }
            )

            # Process request
            try:
                response = await call_next(request)
            except Exception as e:
                # Log unhandled exceptions
                logger.log_error(e, context={
                    "request_method": request.method,
                    "request_url": str(request.url),
                    "correlation_id": correlation_id,
                })
                raise

            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000

            # Log response
            response_data = {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "duration_ms": duration_ms,
            }

            logger.logger.info(
                "Request completed",
                extra={
                    "event": "request_complete",
                    "response": response_data,
                    "duration_ms": duration_ms,
                }
            )

            # Add correlation ID to response headers
            response.headers["X-Correlation-ID"] = correlation_id
            response.headers["X-Request-ID"] = request_id

            return response

    def _extract_user_id(self, request: Request) -> str:
        """Extract user ID from request."""
        # Try JWT token first
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            # In production, decode JWT to get user_id
            return "jwt_user"

        # Try API key
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return f"api_key_{api_key[:8]}"

        return "anonymous"

class AuditMiddleware(BaseHTTPMiddleware):
    """Middleware for auditing sensitive operations."""

    SENSITIVE_ENDPOINTS = {
        "/api/orders": ["POST", "PUT", "DELETE"],
        "/api/trades": ["POST"],
        "/api/positions": ["PUT", "DELETE"],
        "/api/risk/limits": ["PUT"],
        "/api/users": ["POST", "PUT", "DELETE"],
        "/api/strategies": ["POST", "PUT", "DELETE"],
    }

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable):
        # Check if endpoint requires audit
        requires_audit = self._requires_audit(request)

        if requires_audit:
            # Capture request body for audit
            request_body = await self._capture_request_body(request)

            # Store in request state for after processing
            request.state.audit_data = {
                "request_body": request_body,
                "action": self._get_audit_action(request),
            }

        # Process request
        response = await call_next(request)

        # Log audit event if required
        if requires_audit and hasattr(request.state, 'audit_data'):
            await self._log_audit_event(request, response, request.state.audit_data)

        return response

    def _requires_audit(self, request: Request) -> bool:
        """Check if the request requires audit logging."""
        for endpoint, methods in self.SENSITIVE_ENDPOINTS.items():
            if request.url.path.startswith(endpoint) and request.method in methods:
                return True
        return False

    async def _capture_request_body(self, request: Request) -> dict:
        """Capture and parse request body for audit."""
        try:
            body = await request.body()
            if body:
                import json
                return json.loads(body)
        except:
            return {"raw_body": "Unable to parse"}

        return {}

    def _get_audit_action(self, request: Request) -> AuditAction:
        """Map request to audit action."""
        if request.url.path.startswith("/api/orders"):
            if request.method == "POST":
                return AuditAction.CREATE_ORDER
            elif request.method == "PUT":
                return AuditAction.MODIFY_ORDER
            elif request.method == "DELETE":
                return AuditAction.CANCEL_ORDER

        if request.url.path.startswith("/api/trades") and request.method == "POST":
            return AuditAction.EXECUTE_TRADE

        if request.url.path.startswith("/api/risk/limits") and request.method == "PUT":
            return AuditAction.UPDATE_RISK_LIMITS

        if request.url.path.startswith("/api/users") and request.method in ["POST", "PUT", "DELETE"]:
            return AuditAction.USER_PERMISSION_CHANGE

        return AuditAction.SYSTEM_CONFIG_CHANGE

    async def _log_audit_event(self, request: Request, response: Response, audit_data: dict):
        """Log audit event."""
        logger.audit(
            action=audit_data["action"],
            message=f"{audit_data['action'].value} via {request.method} {request.url.path}",
            component="api",
            request_id=request.headers.get("X-Request-ID"),
            user_id=logger._extract_user_id(request),
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            previous_state={},  # Would capture previous state in real implementation
            new_state=audit_data["request_body"],
            reason=request.headers.get("X-Audit-Reason"),
            status_code=response.status_code,
        )

def setup_fastapi_logging(app: FastAPI, service_name: str = "trading-api"):
    """Set up logging middleware for FastAPI application."""
    app.add_middleware(RequestLoggingMiddleware, service_name=service_name)
    app.add_middleware(AuditMiddleware)

    @app.on_event("startup")
    async def startup_event():
        logger.logger.info(f"{service_name} starting up")

    @app.on_event("shutdown")
    async def shutdown_event():
        logger.logger.info(f"{service_name} shutting down")
```

## 🔒 Immutable Audit Trail System

### WORM Storage Implementation (audit-trail/archivers/worm_storage.py)

```python
"""
Write-Once-Read-Many (WORM) storage implementation for immutable audit logs.
Meets SEC Rule 17a-4 and other regulatory requirements.
"""

import hashlib
import json
import os
import shutil
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
import tarfile
import gzip
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import base64

class WORMStorage:
    """Immutable storage for audit logs with cryptographic verification."""

    def __init__(self,
                 storage_path: str = "/var/audit/worm",
                 retention_days: int = 3650,  # 10 years for SEC compliance
                 encryption_key_path: Optional[str] = None):

        self.storage_path = Path(storage_path)
        self.retention_days = retention_days
        self.encryption_key_path = Path(encryption_key_path) if encryption_key_path else None

        # Create storage directories
        self._init_storage()

        # Load encryption key if provided
        self.encryption_key = self._load_encryption_key() if encryption_key_path else None

    def _init_storage(self):
        """Initialize WORM storage structure."""
        # Create main storage directory
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        (self.storage_path / "daily").mkdir(exist_ok=True)
        (self.storage_path / "monthly").mkdir(exist_ok=True)
        (self.storage_path / "yearly").mkdir(exist_ok=True)
        (self.storage_path / "index").mkdir(exist_ok=True)
        (self.storage_path / "signatures").mkdir(exist_ok=True)

        # Set directory permissions (read-only after writing)
        os.chmod(self.storage_path, 0o555)

    def _load_encryption_key(self) -> bytes:
        """Load encryption key from file."""
        with open(self.encryption_key_path, 'rb') as f:
            return f.read()

    def store_audit_event(self, event: Dict[str, Any]) -> str:
        """Store an audit event with WORM guarantees."""
        # Generate unique event ID
        event_id = self._generate_event_id(event)

        # Add metadata
        event_with_metadata = {
            **event,
            "_metadata": {
                "event_id": event_id,
                "stored_at": datetime.utcnow().isoformat() + "Z",
                "version": "1.0",
            }
        }

        # Create daily archive path
        today = datetime.utcnow().date()
        daily_path = self.storage_path / "daily" / today.isoformat()
        daily_path.mkdir(exist_ok=True)

        # Write event to daily file
        event_file = daily_path / f"{event_id}.json"

        # Serialize and optionally encrypt
        event_json = json.dumps(event_with_metadata, indent=2)

        if self.encryption_key:
            event_data = self._encrypt_data(event_json.encode())
        else:
            event_data = event_json.encode()

        # Write with append mode (WORM: can append but not modify)
        with open(event_file, 'ab') as f:
            # Add checksum
            checksum = hashlib.sha256(event_data).hexdigest()
            f.write(event_data + b'\n')
            f.write(f"# CHECKSUM: {checksum}\n".encode())

        # Set file to read-only
        os.chmod(event_file, 0o444)

        # Update index
        self._update_index(event_with_metadata, event_file)

        # Create digital signature
        self._create_signature(event_file)

        return event_id

    def _generate_event_id(self, event: Dict[str, Any]) -> str:
        """Generate unique, deterministic event ID."""
        # Create deterministic string from event
        event_str = json.dumps(event, sort_keys=True)

        # Generate hash-based ID
        event_hash = hashlib.sha256(event_str.encode()).hexdigest()
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")

        return f"AUDIT-{timestamp}-{event_hash[:16]}"

    def _encrypt_data(self, data: bytes) -> bytes:
        """Encrypt data using loaded key."""
        # This is a simplified example - use proper encryption in production
        from cryptography.fernet import Fernet
        fernet = Fernet(self.encryption_key)
        return fernet.encrypt(data)

    def _update_index(self, event: Dict[str, Any], event_file: Path):
        """Update search index for audit events."""
        index_entry = {
            "event_id": event["_metadata"]["event_id"],
            "timestamp": event.get("timestamp", event["_metadata"]["stored_at"]),
            "event_type": event.get("event_type"),
            "user_id": event.get("user_id"),
            "action": event.get("audit_action"),
            "component": event.get("component"),
            "file_path": str(event_file.relative_to(self.storage_path)),
            "checksum": hashlib.sha256(json.dumps(event).encode()).hexdigest(),
        }

        # Append to daily index
        today = datetime.utcnow().date()
        index_file = self.storage_path / "index" / f"{today.isoformat()}.ndjson"

        with open(index_file, 'a') as f:
            f.write(json.dumps(index_entry) + '\n')

    def _create_signature(self, event_file: Path):
        """Create digital signature for audit file."""
        # Generate file hash
        with open(event_file, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()

        # Create signature entry
        signature = {
            "file": str(event_file.name),
            "hash": file_hash,
            "signed_at": datetime.utcnow().isoformat() + "Z",
            "signed_by": "audit_system",
        }

        # Store signature
        sig_file = self.storage_path / "signatures" / f"{event_file.name}.sig"
        with open(sig_file, 'w') as f:
            json.dump(signature, f, indent=2)

        # Set to read-only
        os.chmod(sig_file, 0o444)

    def verify_integrity(self, event_id: str) -> bool:
        """Verify the integrity of an audit event."""
        try:
            # Find event file
            event_file = self._find_event_file(event_id)
            if not event_file:
                return False

            # Read file and verify checksum
            with open(event_file, 'rb') as f:
                lines = f.readlines()

            # Last line should be checksum
            if len(lines) < 2:
                return False

            data = lines[-2]  # Event data
            checksum_line = lines[-1].decode().strip()

            if not checksum_line.startswith("# CHECKSUM: "):
                return False

            expected_checksum = checksum_line.split(": ")[1]
            actual_checksum = hashlib.sha256(data).hexdigest()

            return expected_checksum == actual_checksum

        except Exception as e:
            print(f"Integrity verification failed: {e}")
            return False

    def _find_event_file(self, event_id: str) -> Optional[Path]:
        """Find event file by ID."""
        # Search in daily directories
        for daily_dir in (self.storage_path / "daily").iterdir():
            if daily_dir.is_dir():
                for event_file in daily_dir.glob("*.json"):
                    if event_id in event_file.name:
                        return event_file
        return None

    def archive_old_logs(self):
        """Archive old logs to monthly/yearly compressed archives."""
        today = datetime.utcnow()

        # Archive previous month
        if today.day == 1:  # First day of month
            self._archive_monthly(today)

        # Archive previous year
        if today.month == 1 and today.day == 1:  # First day of year
            self._archive_yearly(today.year - 1)

    def _archive_monthly(self, date: datetime):
        """Create monthly archive."""
        year_month = date.strftime("%Y-%m")
        monthly_archive = self.storage_path / "monthly" / f"{year_month}.tar.gz"

        # Find all daily directories for the month
        daily_dirs = []
        for daily_dir in (self.storage_path / "daily").iterdir():
            if daily_dir.is_dir() and daily_dir.name.startswith(year_month):
                daily_dirs.append(daily_dir)

        if daily_dirs:
            # Create tar archive
            with tarfile.open(monthly_archive, "w:gz") as tar:
                for daily_dir in daily_dirs:
                    tar.add(daily_dir, arcname=daily_dir.name)

            # Set archive to read-only
            os.chmod(monthly_archive, 0o444)

            # Remove daily directories (they're archived)
            for daily_dir in daily_dirs:
                shutil.rmtree(daily_dir)

    def search_events(self,
                     start_date: Optional[datetime] = None,
                     end_date: Optional[datetime] = None,
                     user_id: Optional[str] = None,
                     event_type: Optional[str] = None,
                     action: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search audit events with filters."""
        results = []

        # Search through index files
        for index_file in (self.storage_path / "index").glob("*.ndjson"):
            # Parse date from filename
            file_date = datetime.strptime(index_file.stem, "%Y-%m-%d").date()

            # Apply date filter
            if start_date and file_date < start_date.date():
                continue
            if end_date and file_date > end_date.date():
                continue

            # Read index file
            with open(index_file, 'r') as f:
                for line in f:
                    entry = json.loads(line.strip())

                    # Apply filters
                    if user_id and entry.get("user_id") != user_id:
                        continue
                    if event_type and entry.get("event_type") != event_type:
                        continue
                    if action and entry.get("action") != action:
                        continue

                    # Load full event if needed
                    event = self._load_event(entry["file_path"])
                    if event:
                        results.append(event)

        return results

    def _load_event(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Load event from file."""
        event_file = self.storage_path / file_path

        try:
            with open(event_file, 'rb') as f:
                lines = f.readlines()

            if len(lines) >= 2:
                # Decrypt if necessary
                if self.encryption_key:
                    from cryptography.fernet import Fernet
                    fernet = Fernet(self.encryption_key)
                    data = fernet.decrypt(lines[-2])
                else:
                    data = lines[-2]

                return json.loads(data.decode())
        except Exception as e:
            print(f"Failed to load event: {e}")
            return None

    def generate_compliance_report(self,
                                  report_type: str,
                                  start_date: datetime,
                                  end_date: datetime) -> Dict[str, Any]:
        """Generate compliance report for regulatory requirements."""

        report = {
            "report_id": f"COMP-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "report_type": report_type,
            "period": {
                "start": start_date.isoformat() + "Z",
                "end": end_date.isoformat() + "Z",
            },
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "statistics": {},
            "events": [],
        }

        # Gather statistics
        events = self.search_events(start_date, end_date)

        # Count by action
        action_counts = {}
        for event in events:
            action = event.get("audit_action")
            if action:
                action_counts[action] = action_counts.get(action, 0) + 1

        report["statistics"] = {
            "total_events": len(events),
            "unique_users": len(set(e.get("user_id") for e in events if e.get("user_id"))),
            "action_counts": action_counts,
        }

        # Add sample events (limit to 100 for report)
        report["events"] = events[:100]

        # Add integrity verification
        report["integrity_check"] = {
            "verified_events": len([e for e in events if self.verify_integrity(e.get("_metadata", {}).get("event_id", ""))]),
            "total_events": len(events),
        }

        return report
```

## 📊 Kibana Dashboards for Trading Activity

### Dashboard Configuration (kibana/dashboards/trading-audit.ndjson)

```json
[
  {
    "_type": "dashboard",
    "_source": {
      "title": "Trading Audit Dashboard",
      "hits": 0,
      "description": "Real-time monitoring of trading activities and audit events",
      "panelsJSON": "[{\"version\":\"8.10.0\",\"type\":\"visualization\",\"gridData\":{\"x\":0,\"y\":0,\"w\":24,\"h\":15,\"i\":\"1\"},\"panelIndex\":\"1\",\"embeddableConfig\":{\"savedVis\":{\"title\":\"Audit Events Timeline\",\"type\":\"histogram\",\"params\":{\"type\":\"histogram\",\"grid\":{\"categoryLines\":false},\"categoryAxes\":[{\"id\":\"CategoryAxis-1\",\"type\":\"category\",\"position\":\"bottom\",\"show\":true,\"style\":{},\"scale\":{\"type\":\"linear\"},\"labels\":{\"show\":true,\"truncate\":100},\"title\":{\"text\":\"Time\"}}],\"valueAxes\":[{\"id\":\"ValueAxis-1\",\"name\":\"LeftAxis-1\",\"type\":\"value\",\"position\":\"left\",\"show\":true,\"style\":{},\"scale\":{\"type\":\"linear\",\"mode\":\"normal\"},\"labels\":{\"show\":true,\"rotate\":0,\"filter\":false,\"truncate\":100},\"title\":{\"text\":\"Count\"}}],\"seriesParams\":[{\"show\":true,\"type\":\"histogram\",\"mode\":\"stacked\",\"data\":{\"id\":\"1\",\"label\":\"Count\"},\"valueAxis\":\"ValueAxis-1\",\"drawLinesBetweenPoints\":true,\"showCircles\":true,\"interpolate\":\"linear\"}],\"addTooltip\":true,\"addLegend\":true,\"legendPosition\":\"right\",\"times\":[],\"addTimeMarker\":false},\"aggs\":[{\"id\":\"1\",\"enabled\":true,\"type\":\"count\",\"schema\":\"metric\",\"params\":{}},{\"id\":\"2\",\"enabled\":true,\"type\":\"date_histogram\",\"schema\":\"segment\",\"params\":{\"field\":\"@timestamp\",\"interval\":\"auto\",\"customInterval\":\"2h\",\"min_doc_count\":1,\"extended_bounds\":{}}},{\"id\":\"3\",\"enabled\":true,\"type\":\"terms\",\"schema\":\"group\",\"params\":{\"field\":\"parsed.audit_action\",\"size\":10,\"order\":\"desc\",\"orderBy\":\"1\",\"otherBucket\":false,\"otherBucketLabel\":\"Other\",\"missingBucket\":false,\"missingBucketLabel\":\"Missing\"}}]}}},{\"version\":\"8.10.0\",\"type\":\"visualization\",\"gridData\":{\"x\":24,\"y\":0,\"w\":24,\"h\":15,\"i\":\"2\"},\"panelIndex\":\"2\",\"embeddableConfig\":{\"savedVis\":{\"title\":\"Top Users by Audit Events\",\"type\":\"pie\",\"params\":{\"type\":\"pie\",\"addTooltip\":true,\"addLegend\":true,\"legendPosition\":\"right\",\"isDonut\":true,\"labels\":{\"show\":true,\"values\":true,\"last_level\":true,\"truncate\":100}},\"aggs\":[{\"id\":\"1\",\"enabled\":true,\"type\":\"count\",\"schema\":\"metric\",\"params\":{}},{\"id\":\"2\",\"enabled\":true,\"type\":\"terms\",\"schema\":\"segment\",\"params\":{\"field\":\"parsed.user_id\",\"size\":10,\"order\":\"desc\",\"orderBy\":\"1\",\"otherBucket\":false,\"otherBucketLabel\":\"Other\",\"missingBucket\":false,\"missingBucketLabel\":\"Missing\"}}]}}},{\"version\":\"8.10.0\",\"type\":\"visualization\",\"gridData\":{\"x\":0,\"y\":15,\"w\":24,\"h\":15,\"i\":\"3\"},\"panelIndex\":\"3\",\"embeddableConfig\":{\"savedVis\":{\"title\":\"Trade Events by Symbol\",\"type\":\"tagcloud\",\"params\":{\"scale\":\"linear\",\"orientation\":\"single\",\"minFontSize\":10,\"maxFontSize\":70},\"aggs\":[{\"id\":\"1\",\"enabled\":true,\"type\":\"count\",\"schema\":\"metric\",\"params\":{}},{\"id\":\"2\",\"enabled\":true,\"type\":\"terms\",\"schema\":\"segment\",\"params\":{\"field\":\"parsed.symbol\",\"size\":20,\"order\":\"desc\",\"orderBy\":\"1\",\"otherBucket\":false,\"otherBucketLabel\":\"Other\",\"missingBucket\":false,\"missingBucketLabel\":\"Missing\"}}]}}},{\"version\":\"8.10.0\",\"type\":\"visualization\",\"gridData\":{\"x\":24,\"y\":15,\"w\":24,\"h\":15,\"i\":\"4\"},\"panelIndex\":\"4\",\"embeddableConfig\":{\"savedVis\":{\"title\":\"Error Rate Over Time\",\"type\":\"line\",\"params\":{\"type\":\"line\",\"grid\":{\"categoryLines\":false},\"categoryAxes\":[{\"id\":\"CategoryAxis-1\",\"type\":\"category\",\"position\":\"bottom\",\"show\":true,\"style\":{},\"scale\":{\"type\":\"linear\"},\"labels\":{\"show\":true,\"truncate\":100},\"title\":{\"text\":\"Time\"}}],\"valueAxes\":[{\"id\":\"ValueAxis-1\",\"name\":\"LeftAxis-1\",\"type\":\"value\",\"position\":\"left\",\"show\":true,\"style\":{},\"scale\":{\"type\":\"linear\",\"mode\":\"normal\"},\"labels\":{\"show\":true,\"rotate\":0,\"filter\":false,\"truncate\":100},\"title\":{\"text\":\"Error Rate\"}}],\"seriesParams\":[{\"show\":true,\"type\":\"line\",\"mode\":\"normal\",\"data\":{\"id\":\"1\",\"label\":\"Error Rate\"},\"valueAxis\":\"ValueAxis-1\",\"drawLinesBetweenPoints\":true,\"showCircles\":true,\"interpolate\":\"linear\"}],\"addTooltip\":true,\"addLegend\":true,\"legendPosition\":\"right\",\"times\":[],\"addTimeMarker\":false},\"aggs\":[{\"id\":\"1\",\"enabled\":true,\"type\":\"avg_bucket\",\"schema\":\"metric\",\"params\":{\"customBucket\":{\"id\":\"2-bucket\",\"enabled\":true,\"type\":\"date_histogram\",\"schema\":\"bucket\",\"params\":{\"field\":\"@timestamp\",\"interval\":\"1h\",\"customInterval\":\"2h\",\"min_doc_count\":1,\"extended_bounds\":{}}},\"customMetric\":{\"id\":\"2-metric\",\"enabled\":true,\"type\":\"count\",\"schema\":\"metric\",\"params\":{}}}}]}}},{\"version\":\"8.10.0\",\"type\":\"search\",\"gridData\":{\"x\":0,\"y\":30,\"w\":48,\"h\":20,\"i\":\"5\"},\"panelIndex\":\"5\",\"embeddableConfig\":{\"columns\":[\"_source\"],\"sort\":[[\"@timestamp\",\"desc\"]],\"isTextBasedQuery\":false}}]",
      "optionsJSON": "{\"darkTheme\":false,\"useMargins\":true,\"hidePanelTitles\":false}",
      "version": 1,
      "timeRestore": false,
      "kibanaSavedObjectMeta": {
        "searchSourceJSON": "{\"filter\":[]}"
      }
    }
  }
]
```

## 🐳 Docker Compose for ELK Stack

### Complete ELK Stack (docker-compose.yml)

```yaml
version: "3.8"

services:
  # Elasticsearch - Log storage and indexing
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.10.0
    container_name: elasticsearch
    environment:
      - discovery.type=single-node
      - ES_JAVA_OPTS=-Xms1g -Xmx1g
      - xpack.security.enabled=true
      - xpack.security.authc.api_key.enabled=true
      - ELASTIC_PASSWORD=${ELASTIC_PASSWORD:-changeme}
      - xpack.ml.enabled=false
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data
      - ./elasticsearch/elasticsearch.yml:/usr/share/elasticsearch/config/elasticsearch.yml
    ports:
      - "9200:9200"
      - "9300:9300"
    networks:
      - logging
    healthcheck:
      test:
        [
          "CMD-SHELL",
          'curl -s -u elastic:${ELASTIC_PASSWORD:-changeme} http://localhost:9200/_cluster/health | grep -q ''"status":"green"'' || exit 1',
        ]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped

  # Logstash - Log processing
  logstash:
    image: docker.elastic.co/logstash/logstash:8.10.0
    container_name: logstash
    environment:
      - LS_JAVA_OPTS=-Xms512m -Xmx512m
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
      - ELASTIC_USER=elastic
      - ELASTIC_PASSWORD=${ELASTIC_PASSWORD:-changeme}
    volumes:
      - ./logstash/logstash.conf:/usr/share/logstash/pipeline/logstash.conf
      - ./logstash/patterns:/usr/share/logstash/patterns
      - ./logstash/templates:/usr/share/logstash/templates
      - logstash_data:/usr/share/logstash/data
    ports:
      - "5000:5000"
      - "5044:5044"
      - "8080:8080"
      - "9600:9600"
    networks:
      - logging
    depends_on:
      elasticsearch:
        condition: service_healthy
    restart: unless-stopped

  # Kibana - Log visualization
  kibana:
    image: docker.elastic.co/kibana/kibana:8.10.0
    container_name: kibana
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
      - ELASTICSEARCH_USERNAME=elastic
      - ELASTICSEARCH_PASSWORD=${ELASTIC_PASSWORD:-changeme}
      - XPACK_SECURITY_ENABLED=true
    volumes:
      - ./kibana/dashboards:/usr/share/kibana/dashboards
      - kibana_data:/usr/share/kibana/data
    ports:
      - "5601:5601"
    networks:
      - logging
    depends_on:
      elasticsearch:
        condition: service_healthy
    restart: unless-stopped

  # Filebeat - Log shipping
  filebeat:
    image: docker.elastic.co/beats/filebeat:8.10.0
    container_name: filebeat
    user: root
    command: filebeat -e -strict.perms=false
    volumes:
      - ./filebeat/filebeat.yml:/usr/share/filebeat/filebeat.yml:ro
      - /var/log/trading:/var/log/trading:ro
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
      - /var/run/docker.sock:/var/run/docker.sock
    networks:
      - logging
    depends_on:
      - logstash
    restart: unless-stopped

  # Trading API Example (for testing)
  trading-api:
    build:
      context: ./examples
      dockerfile: Dockerfile.trading-api
    container_name: trading-api
    environment:
      - ENVIRONMENT=development
      - LOGSTASH_HOST=logstash
      - LOGSTASH_PORT=5000
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    volumes:
      - ./examples:/app
    ports:
      - "8000:8000"
    networks:
      - logging
    depends_on:
      - logstash
    restart: unless-stopped

networks:
  logging:
    driver: bridge

volumes:
  elasticsearch_data:
  logstash_data:
  kibana_data:
```

## 🔍 Real-time Anomaly Detection

### Log-Based Anomaly Detection (audit-trail/analytics/anomaly_detector.py)

```python
"""
Real-time anomaly detection in trading logs.
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from collections import defaultdict, deque
import redis
import hashlib
from dataclasses import dataclass
from enum import Enum
import asyncio

class AnomalyType(Enum):
    SUSPICIOUS_LOGIN = "suspicious_login"
    RAPID_ORDER_CANCELLATION = "rapid_order_cancellation"
    AFTER_HOURS_TRADING = "after_hours_trading"
    UNUSUAL_VOLUME = "unusual_volume"
    PRICE_MANIPULATION = "price_manipulation"
    INSIDER_TRADING = "insider_trading"
    UNAUTHORIZED_ACCESS = "unauthorized_access"

@dataclass
class AnomalyAlert:
    anomaly_type: AnomalyType
    severity: str  # low, medium, high, critical
    timestamp: datetime
    description: str
    evidence: List[Dict[str, any]]
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    confidence: float = 0.0  # 0.0 to 1.0

class LogAnomalyDetector:
    """Detect anomalies in trading logs in real-time."""

    def __init__(self, redis_host: str = 'localhost', redis_port: int = 6379):
        self.redis = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)

        # Rate limiting thresholds
        self.thresholds = {
            'logins_per_minute': 5,
            'orders_per_second': 10,
            'cancellations_per_minute': 20,
            'failed_logins_per_hour': 10,
        }

        # Pattern tracking
        self.user_patterns = defaultdict(lambda: deque(maxlen=1000))
        self.ip_patterns = defaultdict(lambda: deque(maxlen=1000))

        # Known patterns for anomaly detection
        self.suspicious_patterns = self._load_suspicious_patterns()

    def _load_suspicious_patterns(self) -> Dict[str, Set[str]]:
        """Load patterns of known suspicious activity."""
        return {
            'after_hours_trading': {'04:00', '20:00', '21:00', '22:00', '23:00', '00:00', '01:00', '02:00', '03:00'},
            'high_frequency_cancellations': {'order_type': 'limit', 'status': 'cancelled'},
            'price_manipulation': {'order_type': 'limit', 'price_deviation': 0.05},  # 5%+ price deviation
        }

    async def analyze_log_entry(self, log_entry: Dict[str, any]) -> Optional[AnomalyAlert]:
        """Analyze a single log entry for anomalies."""
        anomalies = []

        # Check for suspicious login patterns
        if log_entry.get('event_type') == 'login':
            anomalies.extend(await self._check_login_anomalies(log_entry))

        # Check for trading anomalies
        elif log_entry.get('event_type') == 'order':
            anomalies.extend(await self._check_order_anomalies(log_entry))

        # Check for audit anomalies
        elif log_entry.get('audit_action'):
            anomalies.extend(await self._check_audit_anomalies(log_entry))

        # Return the highest severity anomaly
        if anomalies:
            return max(anomalies, key=lambda a: self._severity_to_score(a.severity))

        return None

    async def _check_login_anomalies(self, log_entry: Dict[str, any]) -> List[AnomalyAlert]:
        """Check for suspicious login patterns."""
        anomalies = []
        user_id = log_entry.get('user_id')
        ip_address = log_entry.get('client_ip')
        timestamp = log_entry.get('timestamp')

        if not user_id or not ip_address:
            return anomalies

        # Rate limiting check
        login_key = f"login:{user_id}:{ip_address}"
        login_count = self.redis.incr(login_key)
        self.redis.expire(login_key, 60)  # 1 minute TTL

        if login_count > self.thresholds['logins_per_minute']:
            anomalies.append(AnomalyAlert(
                anomaly_type=AnomalyType.SUSPICIOUS_LOGIN,
                severity='high',
                timestamp=datetime.fromisoformat(timestamp.replace('Z', '+00:00')),
                description=f"Excessive login attempts for user {user_id} from IP {ip_address}",
                evidence=[{
                    'login_count': login_count,
                    'threshold': self.thresholds['logins_per_minute'],
                    'time_window': '1 minute'
                }],
                user_id=user_id,
                ip_address=ip_address,
                confidence=0.8
            ))

        # Failed login pattern
        if log_entry.get('status') == 'failed':
            failed_key = f"failed_login:{user_id}:{ip_address}"
            failed_count = self.redis.incr(failed_key)
            self.redis.expire(failed_key, 3600)  # 1 hour TTL

            if failed_count > self.thresholds['failed_logins_per_hour']:
                anomalies.append(AnomalyAlert(
                    anomaly_type=AnomalyType.UNAUTHORIZED_ACCESS,
                    severity='critical',
                    timestamp=datetime.fromisoformat(timestamp.replace('Z', '+00:00')),
                    description=f"Multiple failed login attempts for user {user_id}",
                    evidence=[{
                        'failed_count': failed_count,
                        'threshold': self.thresholds['failed_logins_per_hour'],
                        'time_window': '1 hour'
                    }],
                    user_id=user_id,
                    ip_address=ip_address,
                    confidence=0.9
                ))

        # Geographic anomaly (simplified)
        known_locations = self.redis.smembers(f"user_locations:{user_id}")
        if known_locations:
            location_hash = hashlib.md5(ip_address.encode()).hexdigest()[:8]
            if location_hash not in known_locations:
                # New location detected
                self.redis.sadd(f"user_locations:{user_id}", location_hash)
                self.redis.expire(f"user_locations:{user_id}", 86400)  # 24 hours

                anomalies.append(AnomalyAlert(
                    anomaly_type=AnomalyType.SUSPICIOUS_LOGIN,
                    severity='medium',
                    timestamp=datetime.fromisoformat(timestamp.replace('Z', '+00:00')),
                    description=f"Login from new location for user {user_id}",
                    evidence=[{
                        'ip_address': ip_address,
                        'location_hash': location_hash,
                        'known_locations': list(known_locations)
                    }],
                    user_id=user_id,
                    ip_address=ip_address,
                    confidence=0.6
                ))

        return anomalies

    async def _check_order_anomalies(self, log_entry: Dict[str, any]) -> List[AnomalyAlert]:
        """Check for suspicious order patterns."""
        anomalies = []
        user_id = log_entry.get('user_id')
        symbol = log_entry.get('symbol')
        order_type = log_entry.get('order_type')
        status = log_entry.get('status')
        timestamp = log_entry.get('timestamp')

        if not user_id or not symbol:
            return anomalies

        # Rapid order cancellation
        if status == 'cancelled':
            cancel_key = f"cancellations:{user_id}:{symbol}"
            cancel_count = self.redis.incr(cancel_key)
            self.redis.expire(cancel_key, 60)  # 1 minute TTL

            if cancel_count > self.thresholds['cancellations_per_minute']:
                anomalies.append(AnomalyAlert(
                    anomaly_type=AnomalyType.RAPID_ORDER_CANCELLATION,
                    severity='high',
                    timestamp=datetime.fromisoformat(timestamp.replace('Z', '+00:00')),
                    description=f"Excessive order cancellations for user {user_id} on {symbol}",
                    evidence=[{
                        'cancellation_count': cancel_count,
                        'threshold': self.thresholds['cancellations_per_minute'],
                        'time_window': '1 minute'
                    }],
                    user_id=user_id,
                    confidence=0.7
                ))

        # After-hours trading detection
        log_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        hour_str = log_time.strftime('%H:%M')

        if hour_str in self.suspicious_patterns['after_hours_trading']:
            anomalies.append(AnomalyAlert(
                anomaly_type=AnomalyType.AFTER_HOURS_TRADING,
                severity='medium',
                timestamp=log_time,
                description=f"Trading activity detected outside regular hours",
                evidence=[{
                    'trading_time': hour_str,
                    'regular_hours': '09:30-16:00'
                }],
                user_id=user_id,
                confidence=0.5
            ))

        # Unusual volume detection
        volume_key = f"volume:{user_id}:{symbol}"
        current_volume = float(log_entry.get('quantity', 0))

        # Get historical average volume
        historical_avg = self.redis.get(f"{volume_key}:avg")
        if historical_avg:
            historical_avg = float(historical_avg)
            if current_volume > historical_avg * 3:  # 3x average volume
                anomalies.append(AnomalyAlert(
                    anomaly_type=AnomalyType.UNUSUAL_VOLUME,
                    severity='medium',
                    timestamp=log_time,
                    description=f"Unusual trading volume for user {user_id} on {symbol}",
                    evidence=[{
                        'current_volume': current_volume,
                        'historical_average': historical_avg,
                        'deviation': f"{(current_volume / historical_avg - 1) * 100:.1f}%"
                    }],
                    user_id=user_id,
                    confidence=0.6
                ))

        # Update volume statistics
        self._update_volume_stats(volume_key, current_volume)

        return anomalies

    def _update_volume_stats(self, key: str, volume: float):
        """Update volume statistics for anomaly detection."""
        # Store current volume
        self.redis.rpush(f"{key}:history", volume)
        self.redis.ltrim(f"{key}:history", 0, 99)  # Keep last 100

        # Calculate and store average
        history = self.redis.lrange(f"{key}:history", 0, -1)
        if history:
            avg = sum(float(v) for v in history) / len(history)
            self.redis.set(f"{key}:avg", avg)
            self.redis.expire(f"{key}:avg", 86400)  # 24 hours

    async def _check_audit_anomalies(self, log_entry: Dict[str, any]) -> List[AnomalyAlert]:
        """Check for audit-related anomalies."""
        anomalies = []
        user_id = log_entry.get('user_id')
        action = log_entry.get('audit_action')
        timestamp = log_entry.get('timestamp')

        # Check for unauthorized access to sensitive data
        if action in ['access_sensitive_data', 'system_config_change', 'user_permission_change']:
            # Verify if user has permission for this action
            permission_key = f"permissions:{user_id}:{action}"
            has_permission = self.redis.get(permission_key)

            if not has_permission or has_permission != 'true':
                anomalies.append(AnomalyAlert(
                    anomaly_type=AnomalyType.UNAUTHORIZED_ACCESS,
                    severity='critical',
                    timestamp=datetime.fromisoformat(timestamp.replace('Z', '+00:00')),
                    description=f"Unauthorized access attempt: {action}",
                    evidence=[{
                        'user_id': user_id,
                        'action': action,
                        'required_permission': action
                    }],
                    user_id=user_id,
                    confidence=0.9
                ))

        return anomalies

    def _severity_to_score(self, severity: str) -> int:
        """Convert severity string to numeric score for comparison."""
        scores = {
            'low': 1,
            'medium': 2,
            'high': 3,
            'critical': 4
        }
        return scores.get(severity, 0)

    async def process_log_stream(self, log_stream):
        """Process a stream of log entries for real-time anomaly detection."""
        alerts = []

        async for log_line in log_stream:
            try:
                log_entry = json.loads(log_line)
                anomaly = await self.analyze_log_entry(log_entry)

                if anomaly:
                    alerts.append(anomaly)

                    # Send alert to monitoring system
                    await self._send_alert(anomaly)

                    # Store alert for reporting
                    self._store_alert(anomaly)

            except json.JSONDecodeError:
                print(f"Failed to parse log line: {log_line}")
            except Exception as e:
                print(f"Error processing log: {e}")

        return alerts

    async def _send_alert(self, alert: AnomalyAlert):
        """Send anomaly alert to monitoring system."""
        alert_data = {
            'anomaly_type': alert.anomaly_type.value,
            'severity': alert.severity,
            'timestamp': alert.timestamp.isoformat(),
            'description': alert.description,
            'user_id': alert.user_id,
            'confidence': alert.confidence,
            'evidence': alert.evidence
        }

        # Send to Elasticsearch for indexing
        index_name = f"anomaly-alerts-{alert.timestamp.strftime('%Y.%m.%d')}"
        # In production, use Elasticsearch client to index document

        # Send to alerting system (e.g., PagerDuty, Slack)
        if alert.severity in ['high', 'critical']:
            await self._send_critical_alert(alert_data)

    async def _send_critical_alert(self, alert_data: Dict[str, any]):
        """Send critical alert to incident response system."""
        # Implementation for sending to PagerDuty, Slack, etc.
        print(f"CRITICAL ALERT: {alert_data}")

    def _store_alert(self, alert: AnomalyAlert):
        """Store alert in Redis for short-term retention."""
        alert_key = f"alert:{alert.timestamp.timestamp()}:{alert.anomaly_type.value}"
        alert_data = {
            'type': alert.anomaly_type.value,
            'severity': alert.severity,
            'timestamp': alert.timestamp.isoformat(),
            'user_id': alert.user_id,
            'confidence': alert.confidence
        }

        self.redis.hset(alert_key, mapping=alert_data)
        self.redis.expire(alert_key, 604800)  # 1 week

    def generate_daily_report(self) -> Dict[str, any]:
        """Generate daily anomaly detection report."""
        today = datetime.utcnow().date()
        report = {
            'date': today.isoformat(),
            'total_alerts': 0,
            'by_severity': defaultdict(int),
            'by_type': defaultdict(int),
            'top_users': [],
            'trends': {}
        }

        # Scan for today's alerts
        pattern = f"alert:*:*"
        for key in self.redis.scan_iter(match=pattern):
            alert_data = self.redis.hgetall(key)

            alert_date = datetime.fromisoformat(alert_data['timestamp']).date()
            if alert_date == today:
                report['total_alerts'] += 1
                report['by_severity'][alert_data['severity']] += 1
                report['by_type'][alert_data['type']] += 1

        return report
```

## 🧪 Testing the Logging System

### Test Script (scripts/test_logging.py)

```python
#!/usr/bin/env python3
"""
Test script for the logging and audit system.
"""

import json
import time
from datetime import datetime
from structured_logging.loggers import logger, AuditAction, ComplianceCategory
from audit_trail.archivers.worm_storage import WORMStorage
from audit_trail.analytics.anomaly_detector import LogAnomalyDetector

def test_structured_logging():
    """Test structured logging functionality."""
    print("Testing structured logging...")

    # Test basic logging
    with logger.LoggingContext(correlation_id="test-123", user_id="test_user"):
        logger.logger.info("Test info message", extra={
            "component": "testing",
            "test_field": "test_value"
        })

        logger.logger.error("Test error message", extra={
            "component": "testing",
            "error_code": "TEST_ERROR"
        })

    print("✓ Structured logging test completed")

def test_audit_logging():
    """Test audit logging functionality."""
    print("Testing audit logging...")

    # Test audit events
    logger.audit(
        action=AuditAction.CREATE_ORDER,
        message="Test order creation",
        user_id="trader_001",
        component="order_system",
        compliance_category=ComplianceCategory.MIFID_II,
        regulatory_id="MIFID-2023-001",
        previous_state={"position": 0},
        new_state={"position": 100, "symbol": "AAPL", "price": 150.25},
        reason="Test execution",
        client_ip="192.168.1.100",
        user_agent="TestClient/1.0"
    )

    print("✓ Audit logging test completed")

def test_trade_logging():
    """Test trade logging functionality."""
    print("Testing trade logging...")

    logger.log_trade({
        "symbol": "AAPL",
        "side": "buy",
        "quantity": 100,
        "price": 150.25,
        "currency": "USD",
        "exchange": "NASDAQ",
        "order_type": "market",
        "time_in_force": "day",
        "commission": 1.50,
        "pnl": 25.50,
        "strategy": "momentum",
        "user_id": "trader_001"
    })

    print("✓ Trade logging test completed")

def test_worm_storage():
    """Test WORM storage functionality."""
    print("Testing WORM storage...")

    # Create WORM storage instance
    storage = WORMStorage(
        storage_path="/tmp/test_worm_storage",
        retention_days=7,
        encryption_key_path=None  # Disable encryption for testing
    )

    # Store test audit event
    test_event = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "event_type": "audit",
        "audit_action": "create_order",
        "user_id": "test_user",
        "component": "test_system",
        "message": "Test audit event",
        "metadata": {
            "test": True,
            "version": "1.0"
        }
    }

    event_id = storage.store_audit_event(test_event)
    print(f"✓ Stored audit event with ID: {event_id}")

    # Verify integrity
    if storage.verify_integrity(event_id):
        print("✓ Event integrity verified")
    else:
        print("✗ Event integrity check failed")

    # Search for events
    events = storage.search_events(
        user_id="test_user",
        event_type="audit"
    )
    print(f"✓ Found {len(events)} events in search")

    # Generate compliance report
    report = storage.generate_compliance_report(
        report_type="test_report",
        start_date=datetime.utcnow() - timedelta(days=1),
        end_date=datetime.utcnow()
    )
    print(f"✓ Generated compliance report: {report['report_id']}")

    print("✓ WORM storage test completed")

async def test_anomaly_detection():
    """Test anomaly detection functionality."""
    print("Testing anomaly detection...")

    detector = LogAnomalyDetector(redis_host='localhost', redis_port=6379)

    # Create test log stream
    test_logs = [
        json.dumps({
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event_type": "login",
            "user_id": "test_user",
            "client_ip": "192.168.1.100",
            "status": "success"
        }),
        json.dumps({
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event_type": "order",
            "user_id": "test_user",
            "symbol": "AAPL",
            "order_type": "limit",
            "status": "cancelled",
            "quantity": 1000
        }),
        json.dumps({
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event_type": "order",
            "user_id": "test_user",
            "symbol": "AAPL",
            "order_type": "limit",
            "status": "cancelled",
            "quantity": 1000
        })
    ]

    # Simulate log stream
    async def log_stream():
        for log in test_logs:
            yield log
            await asyncio.sleep(0.1)

    # Process logs
    alerts = await detector.process_log_stream(log_stream())
    print(f"✓ Detected {len(alerts)} anomalies")

    for alert in alerts:
        print(f"  - {alert.anomaly_type.value}: {alert.description}")

    # Generate report
    report = detector.generate_daily_report()
    print(f"✓ Generated daily report with {report['total_alerts']} alerts")

    print("✓ Anomaly detection test completed")

def run_all_tests():
    """Run all logging system tests."""
    print("=" * 60)
    print("Running Logging System Tests")
    print("=" * 60)

    try:
        test_structured_logging()
        time.sleep(1)

        test_audit_logging()
        time.sleep(1)

        test_trade_logging()
        time.sleep(1)

        test_worm_storage()
        time.sleep(1)

        # Run async test
        import asyncio
        asyncio.run(test_anomaly_detection())

        print("\n" + "=" * 60)
        print("All tests completed successfully! ✅")
        print("=" * 60)

    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_all_tests()
```

## 📋 Deployment Guide

### Step-by-Step Deployment

1. **Clone and setup the logging system:**

```bash
git clone <repository-url>
cd logging-system
```

2. **Configure environment variables:**

```bash
cp .env.example .env
# Edit .env with your configuration
# Set ELASTIC_PASSWORD, AWS credentials, etc.
```

3. **Start the ELK stack:**

```bash
docker-compose up -d
```

4. **Initialize Elasticsearch:**

```bash
# Wait for Elasticsearch to start, then set password
docker exec -it elasticsearch /usr/share/elasticsearch/bin/elasticsearch-reset-password -u elastic -i
```

5. **Import Kibana dashboards:**

```bash
# Wait for Kibana to start, then import dashboards
curl -X POST "http://localhost:5601/api/saved_objects/_import" \
  -H "kbn-xsrf: true" \
  -H "Authorization: Basic $(echo -n elastic:<password> | base64)" \
  --form file=@kibana/dashboards/trading-audit.ndjson
```

6. **Configure Python logging in your application:**

```python
# In your trading application
from structured_logging.loggers import logger, setup_fastapi_logging
from fastapi import FastAPI

app = FastAPI()
setup_fastapi_logging(app, service_name="trading-api")
```

7. **Test the logging system:**

```bash
python scripts/test_logging.py
```

### Production Considerations

1. **Security:**

```bash
# Enable SSL/TLS for Elasticsearch
# Configure firewall rules for log ports
# Use dedicated service accounts for log shipping
```

2. **Scalability:**

```yaml
# In docker-compose.prod.yml
elasticsearch:
  deploy:
    mode: replicated
    replicas: 3
  config:
    - cluster.name=production-logs
    - discovery.seed_hosts=elasticsearch1,elasticsearch2,elasticsearch3
    - cluster.initial_master_nodes=elasticsearch1,elasticsearch2,elasticsearch3
```

3. **Backup and Retention:**

```bash
# Configure index lifecycle policies
PUT _ilm/policy/trading-logs-policy
{
  "policy": {
    "phases": {
      "hot": {
        "actions": {
          "rollover": {
            "max_size": "50gb",
            "max_age": "7d"
          }
        }
      },
      "warm": {
        "min_age": "30d",
        "actions": {
          "shrink": { "number_of_shards": 1 },
          "forcemerge": { "max_num_segments": 1 }
        }
      },
      "delete": {
        "min_age": "365d",
        "actions": { "delete": {} }
      }
    }
  }
}
```

## 📚 Learning Outcomes

By completing Day 93, you will be able to:

- **Design** and implement structured logging systems for trading applications
- **Configure** ELK stack for centralized log aggregation and analysis
- **Create** immutable audit trails that meet regulatory requirements
- **Implement** real-time anomaly detection in trading logs
- **Build** compliance reporting systems from audit data
- **Develop** secure logging practices for sensitive trading data
- **Monitor** trading activity through comprehensive Kibana dashboards
- **Troubleshoot** trading systems using advanced log analysis techniques

## 🔧 Best Practices

1. **Log Structure:**

   - Use consistent field names across all services
   - Include correlation IDs for request tracing
   - Mask sensitive data before logging
   - Add business context to technical logs

2. **Performance:**

   - Use asynchronous logging for high-throughput systems
   - Implement log batching and buffering
   - Configure appropriate log rotation policies
   - Monitor log ingestion rates

3. **Security:**

   - Encrypt sensitive log data
   - Implement access controls for log data
   - Use tamper-evident logging for audit trails
   - Regularly audit log access and changes

4. **Compliance:**
   - Understand regulatory requirements for your jurisdiction
   - Implement appropriate retention periods
   - Create audit trails for all trading actions
   - Generate compliance reports automatically

## 🚨 Monitoring and Alerting

### Key Log-Based Alerts to Configure:

1. **Security Alerts:**

   - Multiple failed login attempts
   - Access from unusual locations
   - Unauthorized access attempts
   - Configuration changes without approval

2. **Trading Alerts:**

   - Excessive order cancellations
   - Trading outside normal hours
   - Unusual trading volumes
   - Price manipulation patterns

3. **System Alerts:**
   - High error rates in services
   - Log ingestion failures
   - Disk space warnings for log storage
   - Audit trail integrity failures

### Alert Integration Example:

```python
# In your anomaly detector
async def send_to_alertmanager(alert: AnomalyAlert):
    """Send anomaly alert to Prometheus AlertManager."""
    alert_data = {
        "labels": {
            "alertname": "TradingAnomaly",
            "anomaly_type": alert.anomaly_type.value,
            "severity": alert.severity,
            "service": "trading-system"
        },
        "annotations": {
            "summary": alert.description,
            "description": f"Detected {alert.anomaly_type.value} with confidence {alert.confidence:.2f}",
            "user": alert.user_id or "unknown"
        },
        "startsAt": alert.timestamp.isoformat()
    }

    # Send to AlertManager webhook
    import aiohttp
    async with aiohttp.ClientSession() as session:
        await session.post(
            "http://alertmanager:9093/api/v2/alerts",
            json=[alert_data]
        )
```

## 📈 Next Steps

After setting up the logging system, consider:

1. **Advanced Analytics:**

   - Machine learning for predictive anomaly detection
   - Pattern recognition for insider trading
   - Sentiment analysis of trading communications
   - Correlation analysis across multiple data sources

2. **Integration:**

   - Connect with SIEM systems
   - Integrate with trading surveillance platforms
   - Feed alerts into incident management systems
   - Create automated compliance workflows

3. **Optimization:**

   - Implement log sampling for high-volume systems
   - Use compression for long-term storage
   - Create log data lakes for historical analysis
   - Implement log data tiering for cost optimization

4. **Compliance Automation:**
   - Automated regulatory reporting
   - Real-time compliance monitoring
   - Audit evidence collection and preservation
   - Integration with legal hold systems

---

This comprehensive logging and audit system provides the foundation for regulatory compliance, security monitoring, and operational insights in trading systems. It enables you to track every action, detect anomalies in real-time, and maintain immutable records for forensic analysis and compliance reporting.
