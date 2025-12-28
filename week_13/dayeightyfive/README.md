# Day 85: System Architecture Design for AI Trading Systems

## Objective
Design scalable, maintainable, and fault-tolerant system architectures for production trading systems, incorporating microservices, event-driven patterns, and resilience patterns.

## Core Concepts
* Architecture Patterns: Microservices vs. monolithic trade-offs, event-driven architecture with Kafka/RabbitMQ, CQRS for trading systems, hexagonal architecture for domain isolation, layered architecture with clear service boundaries
* Component Design: Market data ingestion with WebSocket processing, signal generation with model versioning, order management with idempotency guarantees, risk management with real-time exposure tracking, portfolio management with P&L calculation, AI integration pipelines
* Fault Tolerance & Resilience: Circuit breaker patterns, retry strategies with exponential backoff, bulkhead isolation, graceful degradation, failover mechanisms and disaster recovery planning
* Data Flow Architecture: Real-time vs. batch processing trade-offs, data lineage and provenance tracking, schema evolution strategies, dead letter queues, complex event processing (CEP)
* Latency Optimization: Co-location considerations, network optimization, hybrid rule-based/ML designs, low-latency queues (Disruptor pattern), in-memory processing

## Tutorial: C4 Model Architecture Documentation for Trading System

This tutorial creates comprehensive C4 model diagrams and documentation for a production trading system architecture.

```python
# architecture/c4_documentation.py
"""
C4 Model documentation for AI Trading System Architecture.
Context, Containers, Components, and Code-level diagrams.
"""

from enum import Enum
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json
import yaml
from pathlib import Path


class ComponentType(Enum):
    """Types of system components in C4 model."""
    SYSTEM = "System"
    CONTAINER = "Container"
    COMPONENT = "Component"
    CODE = "Code"


class Technology(Enum):
    """Technology stack enumerations."""
    # Programming Languages
    PYTHON = "Python 3.9+"
    RUST = "Rust"
    CPP = "C++"
    
    # Frameworks
    FASTAPI = "FastAPI"
    FAST_STREAMS = "Faust (Fast Streams)"
    AIRFLOW = "Apache Airflow"
    DASK = "Dask"
    RAY = "Ray"
    
    # Databases
    POSTGRESQL = "PostgreSQL 14+"
    TIMESCALEDB = "TimescaleDB"
    REDIS = "Redis 7+"
    KAFKA = "Apache Kafka"
    QUESTDB = "QuestDB"
    CLICKHOUSE = "ClickHouse"
    
    # Message Brokers
    RABBITMQ = "RabbitMQ"
    NATS = "NATS"
    
    # Cloud
    AWS = "AWS"
    DOCKER = "Docker"
    KUBERNETES = "Kubernetes"
    TERRAFORM = "Terraform"
    
    # ML/AI
    TENSORFLOW = "TensorFlow"
    PYTORCH = "PyTorch"
    MLFLOW = "MLflow"
    KUBEFLOW = "Kubeflow"


@dataclass
class Persona:
    """User persona interacting with the system."""
    name: str
    description: str
    responsibilities: List[str]
    interactions: List[str] = field(default_factory=list)


@dataclass
class SystemInteraction:
    """Interaction between systems or components."""
    source: str
    destination: str
    protocol: str
    description: str
    frequency: str  # "real-time", "batch", "on-demand"
    data_volume: str  # "low", "medium", "high", "very-high"


@dataclass
class Component:
    """Base component in C4 model."""
    id: str
    name: str
    component_type: ComponentType
    description: str
    technology: List[Technology]
    responsibilities: List[str]
    interfaces: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    scaling_requirements: Dict = field(default_factory=dict)
    failure_modes: List[str] = field(default_factory=list)
    monitoring_metrics: List[str] = field(default_factory=list)


@dataclass
class ArchitectureContext:
    """Context-level C4 model."""
    system_name: str
    description: str
    personas: List[Persona]
    external_systems: List[Component]
    key_goals: List[str]
    non_functional_requirements: Dict[str, str]
    system_interactions: List[SystemInteraction]


@dataclass 
class ContainerDiagram:
    """Container-level C4 model."""
    containers: List[Component]
    relationships: List[Tuple[str, str, str]]  # (from, to, description)
    deployment_view: Dict[str, List[str]]  # deployment node -> containers
    data_flow: List[Dict]  # detailed data flow between containers


@dataclass
class ComponentDiagram:
    """Component-level C4 model."""
    container_id: str
    components: List[Component]
    internal_relationships: List[Tuple[str, str, str]]
    external_dependencies: List[Tuple[str, str, str]]


class TradingSystemArchitecture:
    """
    Complete C4 model documentation for AI-powered trading system.
    """
    
    def __init__(self):
        self.context = self._create_context_diagram()
        self.containers = self._create_container_diagram()
        self.component_diagrams = self._create_component_diagrams()
        self.code_structure = self._create_code_structure()
        self.deployment_view = self._create_deployment_view()
        
    def _create_context_diagram(self) -> ArchitectureContext:
        """Create context-level diagram (Level 1)."""
        return ArchitectureContext(
            system_name="QuantFlow AI Trading Platform",
            description="""AI-powered quantitative trading platform supporting 
            multiple asset classes, real-time market data processing, 
            machine learning signal generation, and automated execution 
            with comprehensive risk management.""",
            
            personas=[
                Persona(
                    name="Quantitative Researcher",
                    description="Develops and tests trading strategies using ML models",
                    responsibilities=[
                        "Research and develop predictive models",
                        "Backtest strategies on historical data",
                        "Analyze model performance and risk metrics",
                        "Deploy models to production environment"
                    ],
                    interactions=[
                        "Uses research notebooks and backtesting tools",
                        "Monitors model performance in production",
                        "Adjusts model parameters and features"
                    ]
                ),
                Persona(
                    name="Risk Manager",
                    description="Monitors and controls trading risk exposure",
                    responsibilities=[
                        "Sets and monitors risk limits",
                        "Reviews trading activity for compliance",
                        "Approves new strategies for production",
                        "Manages stress testing scenarios"
                    ],
                    interactions=[
                        "Uses risk dashboard for real-time monitoring",
                        "Receives alerts for risk limit breaches",
                        "Reviews risk reports and analytics"
                    ]
                ),
                Persona(
                    name="Trader",
                    description="Executes and monitors trading strategies",
                    responsibilities=[
                        "Monitors live trading performance",
                        "Manages position sizing and allocation",
                        "Intervenes in exceptional market conditions",
                        "Reviews daily P&L and performance metrics"
                    ],
                    interactions=[
                        "Uses trading dashboard for real-time monitoring",
                        "Receives alerts for system issues",
                        "Manually overrides automated strategies when needed"
                    ]
                ),
                Persona(
                    name="DevOps Engineer",
                    description="Manages infrastructure and deployment",
                    responsibilities=[
                        "Maintains production infrastructure",
                        "Manages CI/CD pipelines",
                        "Monitors system health and performance",
                        "Handles incident response and recovery"
                    ],
                    interactions=[
                        "Uses infrastructure monitoring tools",
                        "Manages deployment pipelines",
                        "Responds to system alerts and incidents"
                    ]
                )
            ],
            
            external_systems=[
                Component(
                    id="ext-market-data",
                    name="Market Data Providers",
                    component_type=ComponentType.SYSTEM,
                    description="External market data sources (Bloomberg, Reuters, Polygon, etc.)",
                    technology=[Technology.AWS],  # Cloud-based data feeds
                    responsibilities=[
                        "Provide real-time market data",
                        "Deliver historical data for backtesting",
                        "Supply corporate actions and fundamental data"
                    ]
                ),
                Component(
                    id="ext-brokers",
                    name="Trading Brokers",
                    component_type=ComponentType.SYSTEM,
                    description="Execution venues and broker APIs (Interactive Brokers, Alpaca, etc.)",
                    technology=[Technology.AWS],
                    responsibilities=[
                        "Execute trading orders",
                        "Provide account information",
                        "Deliver execution reports"
                    ]
                ),
                Component(
                    id="ext-risk-systems",
                    name="Enterprise Risk Systems",
                    component_type=ComponentType.SYSTEM,
                    description="Enterprise risk management and compliance systems",
                    technology=[Technology.AWS],
                    responsibilities=[
                        "Aggregate risk across all trading systems",
                        "Provide compliance reporting",
                        "Support regulatory requirements"
                    ]
                ),
                Component(
                    id="ext-data-warehouse",
                    name="Enterprise Data Warehouse",
                    component_type=ComponentType.SYSTEM,
                    description="Centralized data storage for analytics and reporting",
                    technology=[Technology.AWS],
                    responsibilities=[
                        "Store historical trading data",
                        "Support regulatory reporting",
                        "Provide data for enterprise analytics"
                    ]
                )
            ],
            
            key_goals=[
                "Achieve consistent risk-adjusted returns across market regimes",
                "Maintain sub-100ms latency for high-frequency strategies",
                "Ensure 99.99% system availability during trading hours",
                "Support concurrent execution of 100+ trading strategies",
                "Provide comprehensive audit trail for regulatory compliance"
            ],
            
            non_functional_requirements={
                "performance": "Process 1M+ market data events per second with <50ms latency",
                "reliability": "99.99% uptime during market hours, automatic failover within 60 seconds",
                "scalability": "Scale from 10 to 1000+ concurrent strategies without redesign",
                "security": "SOC 2 Type II compliant, end-to-end encryption, role-based access control",
                "maintainability": "Independent deployability of components, comprehensive monitoring",
                "cost": "Optimize cloud costs with auto-scaling, spot instances for batch processing"
            },
            
            system_interactions=[
                SystemInteraction(
                    source="QuantFlow AI Trading Platform",
                    destination="Market Data Providers",
                    protocol="WebSocket/REST/FIX",
                    description="Real-time market data ingestion",
                    frequency="real-time",
                    data_volume="very-high"
                ),
                SystemInteraction(
                    source="QuantFlow AI Trading Platform",
                    destination="Trading Brokers",
                    protocol="FIX/REST",
                    description="Order submission and execution",
                    frequency="real-time",
                    data_volume="medium"
                ),
                SystemInteraction(
                    source="QuantFlow AI Trading Platform",
                    destination="Enterprise Risk Systems",
                    protocol="REST/Message Queue",
                    description="Risk exposure reporting and limit checks",
                    frequency="near-real-time",
                    data_volume="low"
                ),
                SystemInteraction(
                    source="QuantFlow AI Trading Platform",
                    destination="Enterprise Data Warehouse",
                    protocol="Batch/REST",
                    description="End-of-day data synchronization",
                    frequency="batch",
                    data_volume="high"
                )
            ]
        )
    
    def _create_container_diagram(self) -> ContainerDiagram:
        """Create container-level diagram (Level 2)."""
        containers = [
            # Market Data Services
            Component(
                id="market-data-ingestion",
                name="Market Data Ingestion Service",
                component_type=ComponentType.CONTAINER,
                description="Real-time ingestion and normalization of market data from multiple sources",
                technology=[Technology.PYTHON, Technology.FASTAPI, Technology.KAFKA, Technology.REDIS],
                responsibilities=[
                    "Connect to market data feeds via WebSocket/REST/FIX",
                    "Normalize data across different providers and formats",
                    "Validate data quality and detect anomalies",
                    "Publish normalized data to message bus",
                    "Handle reconnection and recovery from data feed disruptions"
                ],
                interfaces=["WebSocket clients", "REST API", "Kafka producers"],
                dependencies=["kafka-cluster", "redis-cache"],
                scaling_requirements={
                    "horizontal": True,
                    "min_instances": 2,
                    "max_instances": 10,
                    "scaling_metric": "message_rate"
                },
                failure_modes=[
                    "Data feed connection loss",
                    "Message bus connectivity issues",
                    "Memory leaks from data buffers",
                    "CPU saturation during market volatility"
                ],
                monitoring_metrics=[
                    "market_data_latency_ms",
                    "message_processing_rate",
                    "connection_status",
                    "data_quality_errors",
                    "memory_usage_percent"
                ]
            ),
            
            Component(
                id="market-data-processing",
                name="Market Data Processing Service",
                component_type=ComponentType.CONTAINER,
                description="Real-time processing and enrichment of market data streams",
                technology=[Technology.PYTHON, Technology.FAST_STREAMS, Technology.KAFKA],
                responsibilities=[
                    "Calculate real-time technical indicators",
                    "Aggregate tick data to bar data (1min, 5min, etc.)",
                    "Enrich data with derived features for ML models",
                    "Detect market microstructure events",
                    "Generate derived data streams for consumption"
                ],
                interfaces=["Kafka consumers/producers"],
                dependencies=["kafka-cluster", "feature-store"],
                scaling_requirements={
                    "horizontal": True,
                    "min_instances": 3,
                    "max_instances": 20,
                    "scaling_metric": "processing_latency"
                },
                failure_modes=[
                    "Stream processing lag",
                    "State corruption in windowed operations",
                    "Backpressure from downstream consumers"
                ],
                monitoring_metrics=[
                    "processing_latency_p99_ms",
                    "throughput_events_per_second",
                    "consumer_lag_seconds",
                    "window_completion_rate"
                ]
            ),
            
            # AI/ML Services
            Component(
                id="feature-store",
                name="Feature Store Service",
                component_type=ComponentType.CONTAINER,
                description="Centralized feature storage and serving for ML models",
                technology=[Technology.PYTHON, Technology.FASTAPI, Technology.REDIS, Technology.POSTGRESQL],
                responsibilities=[
                    "Store and version feature definitions",
                    "Serve features for training and inference",
                    "Calculate features on-demand from raw data",
                    "Maintain feature lineage and metadata",
                    "Handle feature transformation pipelines"
                ],
                interfaces=["REST API", "gRPC", "Python SDK"],
                dependencies=["postgresql-db", "redis-cache"],
                scaling_requirements={
                    "horizontal": True,
                    "min_instances": 2,
                    "max_instances": 8,
                    "scaling_metric": "request_latency"
                },
                failure_modes=[
                    "Feature calculation timeouts",
                    "Database connection issues",
                    "Cache inconsistency",
                    "Version mismatch between training/inference"
                ],
                monitoring_metrics=[
                    "feature_serving_latency_ms",
                    "cache_hit_rate_percent",
                    "concurrent_feature_requests",
                    "feature_calculation_errors"
                ]
            ),
            
            Component(
                id="model-serving",
                name="Model Serving Service",
                component_type=ComponentType.CONTAINER,
                description="Real-time ML model inference for trading signals",
                technology=[Technology.PYTHON, Technology.FASTAPI, Technology.TENSORFLOW, Technology.MLFLOW],
                responsibilities=[
                    "Serve ML models via REST/gRPC endpoints",
                    "Handle model versioning and A/B testing",
                    "Perform real-time inference on streaming features",
                    "Monitor model performance and drift",
                    "Manage model artifacts and dependencies"
                ],
                interfaces=["REST API", "gRPC", "Kafka consumers"],
                dependencies=["feature-store", "model-registry", "redis-cache"],
                scaling_requirements={
                    "horizontal": True,
                    "min_instances": 2,
                    "max_instances": 15,
                    "scaling_metric": "inference_latency"
                },
                failure_modes=[
                    "Model loading failures",
                    "GPU memory exhaustion",
                    "Inference timeout under load",
                    "Version rollback failures"
                ],
                monitoring_metrics=[
                    "inference_latency_p99_ms",
                    "requests_per_second",
                    "model_throughput",
                    "prediction_distribution",
                    "model_drift_score"
                ]
            ),
            
            # Trading Services
            Component(
                id="strategy-engine",
                name="Strategy Engine Service",
                component_type=ComponentType.CONTAINER,
                description="Orchestrates trading strategies and generates trading signals",
                technology=[Technology.PYTHON, Technology.FASTAPI, Technology.RAY],
                responsibilities=[
                    "Execute trading strategy logic",
                    "Combine multiple signal sources",
                    "Apply position sizing and risk scaling",
                    "Manage strategy state and lifecycle",
                    "Handle strategy-specific configurations"
                ],
                interfaces=["REST API", "Kafka consumers/producers"],
                dependencies=["model-serving", "risk-engine", "portfolio-manager"],
                scaling_requirements={
                    "horizontal": True,
                    "strategy_based": True,
                    "min_instances": 2,
                    "max_instances": 50,  # One per strategy group
                    "scaling_metric": "strategy_count"
                },
                failure_modes=[
                    "Strategy logic errors",
                    "State corruption",
                    "Signal generation delays",
                    "Dependency service failures"
                ],
                monitoring_metrics=[
                    "signal_generation_latency",
                    "active_strategies_count",
                    "strategy_health_status",
                    "signal_quality_metrics"
                ]
            ),
            
            Component(
                id="order-management",
                name="Order Management Service",
                component_type=ComponentType.CONTAINER,
                description="Manages order lifecycle and execution",
                technology=[Technology.PYTHON, Technology.FASTAPI, Technology.POSTGRESQL],
                responsibilities=[
                    "Validate and route orders to appropriate venues",
                    "Manage order state transitions",
                    "Handle order amendments and cancellations",
                    "Provide idempotent order operations",
                    "Maintain order audit trail"
                ],
                interfaces=["REST API", "FIX protocol", "WebSocket"],
                dependencies=["postgresql-db", "risk-engine", "broker-gateway"],
                scaling_requirements={
                    "horizontal": True,
                    "min_instances": 2,
                    "max_instances": 10,
                    "scaling_metric": "order_rate"
                },
                failure_modes=[
                    "Order state inconsistency",
                    "Broker connectivity loss",
                    "Duplicate order submission",
                    "Order execution timeouts"
                ],
                monitoring_metrics=[
                    "order_processing_latency_ms",
                    "orders_per_second",
                    "order_error_rate",
                    "execution_quality",
                    "pending_orders_count"
                ]
            ),
            
            # Risk & Portfolio Services
            Component(
                id="risk-engine",
                name="Risk Engine Service",
                component_type=ComponentType.CONTAINER,
                description="Real-time risk calculation and limit monitoring",
                technology=[Technology.PYTHON, Technology.FASTAPI, Technology.REDIS],
                responsibilities=[
                    "Calculate real-time P&L and risk metrics",
                    "Monitor and enforce risk limits",
                    "Perform stress testing and scenario analysis",
                    "Generate risk alerts and reports",
                    "Maintain risk model configurations"
                ],
                interfaces=["REST API", "WebSocket", "Kafka consumers"],
                dependencies=["postgresql-db", "redis-cache", "market-data-processing"],
                scaling_requirements={
                    "horizontal": True,
                    "min_instances": 2,
                    "max_instances": 8,
                    "scaling_metric": "position_count"
                },
                failure_modes=[
                    "Risk calculation delays",
                    "Limit breach detection failures",
                    "Position reconciliation errors",
                    "Market data staleness"
                ],
                monitoring_metrics=[
                    "risk_calculation_latency_ms",
                    "limit_check_frequency",
                    "risk_metric_accuracy",
                    "alert_generation_latency"
                ]
            ),
            
            Component(
                id="portfolio-manager",
                name="Portfolio Manager Service",
                component_type=ComponentType.CONTAINER,
                description="Manages portfolio composition and allocation",
                technology=[Technology.PYTHON, Technology.FASTAPI, Technology.POSTGRESQL],
                responsibilities=[
                    "Track positions and holdings across strategies",
                    "Calculate portfolio-level metrics",
                    "Manage capital allocation",
                    "Handle corporate actions and adjustments",
                    "Generate portfolio reports"
                ],
                interfaces=["REST API", "Kafka consumers"],
                dependencies=["postgresql-db", "risk-engine", "order-management"],
                scaling_requirements={
                    "horizontal": True,
                    "min_instances": 2,
                    "max_instances": 6,
                    "scaling_metric": "position_updates"
                },
                failure_modes=[
                    "Position tracking errors",
                    "Capital allocation conflicts",
                    "Reporting delays",
                    "Data reconciliation issues"
                ],
                monitoring_metrics=[
                    "position_update_latency",
                    "portfolio_recalculation_time",
                    "capital_utilization",
                    "report_generation_time"
                ]
            ),
            
            # Infrastructure Services
            Component(
                id="api-gateway",
                name="API Gateway",
                component_type=ComponentType.CONTAINER,
                description="Single entry point for all external API requests",
                technology=[Technology.PYTHON, Technology.FASTAPI, Technology.KONG],
                responsibilities=[
                    "Route requests to appropriate services",
                    "Handle authentication and authorization",
                    "Implement rate limiting and quotas",
                    "Collect API usage metrics",
                    "Provide request/response transformation"
                ],
                interfaces=["REST API", "WebSocket"],
                dependencies=["all-services"],  # Routes to all internal services
                scaling_requirements={
                    "horizontal": True,
                    "min_instances": 2,
                    "max_instances": 8,
                    "scaling_metric": "request_rate"
                },
                failure_modes=[
                    "Routing errors",
                    "Authentication failures",
                    "Rate limiting misconfiguration",
                    "Load balancing issues"
                ],
                monitoring_metrics=[
                    "request_latency_p99_ms",
                    "requests_per_second",
                    "error_rate_percent",
                    "authentication_failures",
                    "rate_limit_hits"
                ]
            ),
            
            Component(
                id="monitoring-dashboard",
                name="Monitoring Dashboard",
                component_type=ComponentType.CONTAINER,
                description="Real-time monitoring and visualization of system metrics",
                technology=[Technology.PYTHON, Technology.FASTAPI, Technology.GRAFANA],
                responsibilities=[
                    "Display real-time system health metrics",
                    "Visualize trading performance and P&L",
                    "Show risk metrics and limit utilization",
                    "Provide alert management interface",
                    "Generate historical reports and analytics"
                ],
                interfaces=["Web UI", "REST API"],
                dependencies=["prometheus", "grafana", "postgresql-db"],
                scaling_requirements={
                    "horizontal": True,
                    "min_instances": 2,
                    "max_instances": 4,
                    "scaling_metric": "concurrent_users"
                },
                failure_modes=[
                    "Dashboard loading failures",
                    "Metric data gaps",
                    "Visualization rendering issues",
                    "Alert notification failures"
                ],
                monitoring_metrics=[
                    "dashboard_load_time",
                    "concurrent_users",
                    "metric_query_latency",
                    "alert_notification_rate"
                ]
            )
        ]
        
        relationships = [
            # Market data flow
            ("market-data-ingestion", "market-data-processing", "Publishes normalized market data"),
            ("market-data-processing", "feature-store", "Sends processed data for feature calculation"),
            ("market-data-processing", "risk-engine", "Provides market data for risk calculations"),
            
            # AI/ML flow
            ("feature-store", "model-serving", "Serves features for model inference"),
            ("model-serving", "strategy-engine", "Provides ML-based trading signals"),
            
            # Trading flow
            ("strategy-engine", "order-management", "Sends orders for execution"),
            ("order-management", "portfolio-manager", "Updates position changes"),
            
            # Risk management flow
            ("portfolio-manager", "risk-engine", "Provides position data for risk calculation"),
            ("risk-engine", "strategy-engine", "Enforces risk limits on strategies"),
            
            # API Gateway routing
            ("api-gateway", "market-data-ingestion", "Routes market data API requests"),
            ("api-gateway", "model-serving", "Routes model inference requests"),
            ("api-gateway", "strategy-engine", "Routes strategy management requests"),
            ("api-gateway", "order-management", "Routes order management requests"),
            ("api-gateway", "risk-engine", "Routes risk management requests"),
            ("api-gateway", "portfolio-manager", "Routes portfolio management requests"),
            
            # Monitoring
            ("all-services", "monitoring-dashboard", "Sends metrics for monitoring")
        ]
        
        deployment_view = {
            "aws-region-us-east-1": [
                "market-data-ingestion",
                "market-data-processing",
                "order-management",
                "risk-engine"
            ],
            "aws-region-us-west-2": [
                "feature-store",
                "model-serving",
                "strategy-engine",
                "portfolio-manager"
            ],
            "global": [
                "api-gateway",
                "monitoring-dashboard"
            ]
        }
        
        data_flow = [
            {
                "name": "Real-time Trading Pipeline",
                "description": "End-to-end flow from market data to order execution",
                "steps": [
                    "Market data ingestion → Normalization → Feature calculation → Model inference → Signal generation → Risk check → Order creation → Execution → Position update"
                ],
                "latency_target": "<100ms end-to-end",
                "throughput_target": "10,000 events/second"
            },
            {
                "name": "Risk Monitoring Pipeline",
                "description": "Continuous risk calculation and limit monitoring",
                "steps": [
                    "Position updates + Market data → Risk calculation → Limit checks → Alert generation → Dashboard update"
                ],
                "latency_target": "<50ms for limit breaches",
                "throughput_target": "1,000 updates/second"
            }
        ]
        
        return ContainerDiagram(
            containers=containers,
            relationships=relationships,
            deployment_view=deployment_view,
            data_flow=data_flow
        )
    
    def _create_component_diagrams(self) -> Dict[str, ComponentDiagram]:
        """Create component-level diagrams (Level 3) for key containers."""
        component_diagrams = {}
        
        # Component diagram for Market Data Ingestion Service
        market_data_components = [
            Component(
                id="feed-connector",
                name="Feed Connector Component",
                component_type=ComponentType.COMPONENT,
                description="Manages connections to external market data feeds",
                technology=[Technology.PYTHON, Technology.WEBSOCKET],
                responsibilities=[
                    "Establish WebSocket connections to data providers",
                    "Handle connection retries and recovery",
                    "Manage authentication and session state",
                    "Parse raw data feed messages"
                ]
            ),
            Component(
                id="data-normalizer",
                name="Data Normalization Component",
                component_type=ComponentType.COMPONENT,
                description="Normalizes data across different providers and formats",
                technology=[Technology.PYTHON],
                responsibilities=[
                    "Convert provider-specific formats to internal schema",
                    "Handle currency and unit conversions",
                    "Apply data quality checks",
                    "Generate standardized market data events"
                ]
            ),
            Component(
                id="message-publisher",
                name="Message Publisher Component",
                component_type=ComponentType.COMPONENT,
                description="Publishes normalized data to message bus",
                technology=[Technology.PYTHON, Technology.KAFKA],
                responsibilities=[
                    "Serialize data to Avro/Protobuf format",
                    "Publish to appropriate Kafka topics",
                    "Handle publishing errors and retries",
                    "Monitor publish latency and success rate"
                ]
            ),
            Component(
                id="health-monitor",
                name="Health Monitoring Component",
                component_type=ComponentType.COMPONENT,
                description="Monitors service health and data quality",
                technology=[Technology.PYTHON, Technology.PROMETHEUS],
                responsibilities=[
                    "Track connection status to all feeds",
                    "Monitor data latency and staleness",
                    "Detect data anomalies and gaps",
                    "Publish health metrics for observability"
                ]
            )
        ]
        
        component_diagrams["market-data-ingestion"] = ComponentDiagram(
            container_id="market-data-ingestion",
            components=market_data_components,
            internal_relationships=[
                ("feed-connector", "data-normalizer", "Sends raw market data"),
                ("data-normalizer", "message-publisher", "Sends normalized data"),
                ("feed-connector", "health-monitor", "Provides connection metrics"),
                ("data-normalizer", "health-monitor", "Provides data quality metrics")
            ],
            external_dependencies=[
                ("feed-connector", "ext-market-data", "Connects to external data feeds"),
                ("message-publisher", "kafka-cluster", "Publishes to message bus"),
                ("health-monitor", "prometheus", "Exports metrics for monitoring")
            ]
        )
        
        # Component diagram for Model Serving Service
        model_serving_components = [
            Component(
                id="model-registry-client",
                name="Model Registry Client",
                component_type=ComponentType.COMPONENT,
                description="Interacts with model registry to load models",
                technology=[Technology.PYTHON, Technology.MLFLOW],
                responsibilities=[
                    "Discover available model versions",
                    "Load model artifacts and dependencies",
                    "Cache loaded models in memory",
                    "Handle model version switching"
                ]
            ),
            Component(
                id="inference-engine",
                name="Inference Engine",
                component_type=ComponentType.COMPONENT,
                description="Executes model inference on input data",
                technology=[Technology.PYTHON, Technology.TENSORFLOW],
                responsibilities=[
                    "Preprocess input features for model",
                    "Execute model inference (CPU/GPU)",
                    "Post-process model outputs",
                    "Batch inference for efficiency"
                ]
            ),
            Component(
                id="feature-fetcher",
                name="Feature Fetcher",
                component_type=ComponentType.COMPONENT,
                description="Retrieves features from feature store",
                technology=[Technology.PYTHON, Technology.GRPC],
                responsibilities=[
                    "Request features from feature store",
                    "Cache frequently used features",
                    "Handle feature versioning",
                    "Transform features for model input"
                ]
            ),
            Component(
                id="a-b-test-router",
                name="A/B Testing Router",
                component_type=ComponentType.COMPONENT,
                description="Routes requests to different model versions for testing",
                technology=[Technology.PYTHON],
                responsibilities=[
                    "Route traffic based on experiment configuration",
                    "Track experiment assignments",
                    "Collect experiment metrics",
                    "Handle gradual rollouts"
                ]
            )
        ]
        
        component_diagrams["model-serving"] = ComponentDiagram(
            container_id="model-serving",
            components=model_serving_components,
            internal_relationships=[
                ("feature-fetcher", "inference-engine", "Provides features for inference"),
                ("model-registry-client", "inference-engine", "Provides loaded models"),
                ("a-b-test-router", "inference-engine", "Routes to specific model version")
            ],
            external_dependencies=[
                ("model-registry-client", "model-registry", "Loads models from registry"),
                ("feature-fetcher", "feature-store", "Fetches features from store"),
                ("inference-engine", "prometheus", "Exports inference metrics")
            ]
        )
        
        return component_diagrams
    
    def _create_code_structure(self) -> Dict:
        """Create code-level structure (Level 4) for key components."""
        return {
            "project_structure": {
                "src/": {
                    "market_data/": {
                        "ingestion/": [
                            "feed_connector.py",
                            "data_normalizer.py",
                            "message_publisher.py",
                            "health_monitor.py",
                            "__init__.py"
                        ],
                        "processing/": [
                            "stream_processor.py",
                            "technical_indicators.py",
                            "feature_engineering.py",
                            "__init__.py"
                        ]
                    },
                    "ml/": {
                        "feature_store/": [
                            "feature_server.py",
                            "feature_calculator.py",
                            "feature_registry.py",
                            "__init__.py"
                        ],
                        "model_serving/": [
                            "inference_server.py",
                            "model_manager.py",
                            "experiment_router.py",
                            "__init__.py"
                        ]
                    },
                    "trading/": {
                        "strategies/": [
                            "strategy_engine.py",
                            "signal_generator.py",
                            "position_sizer.py",
                            "__init__.py"
                        ],
                        "orders/": [
                            "order_manager.py",
                            "execution_handler.py",
                            "order_router.py",
                            "__init__.py"
                        ]
                    },
                    "risk/": {
                        "risk_engine/": [
                            "risk_calculator.py",
                            "limit_monitor.py",
                            "alert_generator.py",
                            "__init__.py"
                        ],
                        "portfolio/": [
                            "portfolio_manager.py",
                            "position_tracker.py",
                            "performance_calculator.py",
                            "__init__.py"
                        ]
                    },
                    "infrastructure/": {
                        "api/": ["api_gateway.py", "auth_middleware.py", "rate_limiter.py"],
                        "monitoring/": ["metrics_collector.py", "alert_manager.py", "dashboard.py"],
                        "config/": ["config_manager.py", "secrets_manager.py", "__init__.py"]
                    }
                },
                "tests/": {
                    "unit/": ["test_market_data.py", "test_ml_models.py", "test_trading.py"],
                    "integration/": ["test_data_flow.py", "test_end_to_end.py"],
                    "performance/": ["load_tests.py", "latency_tests.py"]
                },
                "configs/": ["development.yaml", "staging.yaml", "production.yaml"],
                "deployment/": {
                    "docker/": ["Dockerfile.*", "docker-compose.*"],
                    "kubernetes/": ["deployment.*.yaml", "service.*.yaml"],
                    "terraform/": ["main.tf", "variables.tf", "outputs.tf"]
                },
                "docs/": ["architecture.md", "api_documentation.md", "operational_guide.md"]
            },
            "key_dependencies": {
                "core": ["python>=3.9", "fastapi", "pydantic", "asyncio"],
                "data_processing": ["pandas", "numpy", "apache-kafka", "redis"],
                "ml": ["tensorflow", "scikit-learn", "mlflow", "xgboost"],
                "trading": ["ccxt", "ibapi", "alpaca-trade-api"],
                "monitoring": ["prometheus-client", "grafana-api", "jaeger-client"]
            }
        }
    
    def _create_deployment_view(self) -> Dict:
        """Create deployment view with infrastructure details."""
        return {
            "cloud_provider": "AWS",
            "regions": ["us-east-1", "us-west-2", "eu-west-1"],
            "networking": {
                "vpc": {
                    "name": "trading-vpc",
                    "cidr": "10.0.0.0/16",
                    "subnets": {
                        "public": ["10.0.1.0/24", "10.0.2.0/24"],
                        "private": ["10.0.10.0/24", "10.0.11.0/24"],
                        "data": ["10.0.20.0/24", "10.0.21.0/24"]
                    }
                },
                "security_groups": {
                    "api_gateway": ["443/tcp from 0.0.0.0/0"],
                    "internal_services": ["All traffic within VPC"],
                    "database": ["5432/tcp from internal services"],
                    "cache": ["6379/tcp from internal services"]
                }
            },
            "compute": {
                "ec2_instances": {
                    "market_data": {
                        "instance_type": "c5.4xlarge",
                        "count": 4,
                        "auto_scaling": {"min": 2, "max": 8},
                        "purchasing_option": "on-demand"
                    },
                    "ml_serving": {
                        "instance_type": "g4dn.xlarge",  # GPU instances
                        "count": 2,
                        "auto_scaling": {"min": 1, "max": 4},
                        "purchasing_option": "on-demand"
                    },
                    "trading_services": {
                        "instance_type": "c5.2xlarge",
                        "count": 8,
                        "auto_scaling": {"min": 4, "max": 16},
                        "purchasing_option": "spot"  # Use spot for cost savings
                    }
                },
                "kubernetes": {
                    "cluster_name": "trading-eks-cluster",
                    "node_groups": {
                        "general_purpose": {"instance_type": "m5.large", "min_size": 3, "max_size": 10},
                        "ml_workloads": {"instance_type": "g4dn.xlarge", "min_size": 2, "max_size": 6}
                    }
                }
            },
            "databases": {
                "postgresql": {
                    "engine": "PostgreSQL 14",
                    "instance_type": "db.r5.4xlarge",
                    "storage": 1000,  # GB
                    "multi_az": True,
                    "read_replicas": 2
                },
                "redis": {
                    "engine": "Redis 7",
                    "instance_type": "cache.r6g.xlarge",
                    "cluster_mode": True,
                    "shards": 3,
                    "replicas_per_shard": 1
                },
                "kafka": {
                    "service": "MSK (Managed Streaming for Kafka)",
                    "broker_type": "kafka.t3.small",
                    "broker_count": 3,
                    "storage_per_broker": 1000  # GB
                }
            },
            "monitoring": {
                "metrics": "Amazon Managed Service for Prometheus",
                "logs": "Amazon CloudWatch Logs",
                "traces": "AWS X-Ray",
                "dashboard": "Grafana (Managed)",
                "alerting": "Amazon SNS + PagerDuty integration"
            },
            "cost_optimization": {
                "spot_instances": ["trading_services", "batch_processing"],
                "reserved_instances": ["databases", "market_data"],
                "auto_scaling_schedule": {
                    "market_hours": {"min": 4, "max": 8},
                    "off_hours": {"min": 2, "max": 4}
                },
                "data_retention": {
                    "hot_data": "30 days",
                    "warm_data": "90 days",
                    "cold_data": "365 days",
                    "archival": "7 years for compliance"
                }
            }
        }
    
    def generate_documentation(self, output_dir: str = "architecture_docs"):
        """Generate complete architecture documentation."""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Generate context diagram documentation
        context_doc = {
            "system": self.context.system_name,
            "description": self.context.description,
            "personas": [
                {
                    "name": p.name,
                    "description": p.description,
                    "responsibilities": p.responsibilities,
                    "interactions": p.interactions
                }
                for p in self.context.personas
            ],
            "external_systems": [
                {
                    "id": s.id,
                    "name": s.name,
                    "description": s.description,
                    "responsibilities": s.responsibilities
                }
                for s in self.context.external_systems
            ],
            "key_goals": self.context.key_goals,
            "non_functional_requirements": self.context.non_functional_requirements,
            "system_interactions": [
                {
                    "from": i.source,
                    "to": i.destination,
                    "protocol": i.protocol,
                    "description": i.description,
                    "frequency": i.frequency,
                    "data_volume": i.data_volume
                }
                for i in self.context.system_interactions
            ]
        }
        
        with open(output_path / "context_diagram.json", "w") as f:
            json.dump(context_doc, f, indent=2)
        
        # Generate container diagram documentation
        container_doc = {
            "containers": [
                {
                    "id": c.id,
                    "name": c.name,
                    "type": c.component_type.value,
                    "description": c.description,
                    "technology": [t.value for t in c.technology],
                    "responsibilities": c.responsibilities,
                    "interfaces": c.interfaces,
                    "dependencies": c.dependencies,
                    "scaling_requirements": c.scaling_requirements,
                    "failure_modes": c.failure_modes,
                    "monitoring_metrics": c.monitoring_metrics
                }
                for c in self.containers.containers
            ],
            "relationships": [
                {"from": r[0], "to": r[1], "description": r[2]}
                for r in self.containers.relationships
            ],
            "deployment_view": self.containers.deployment_view,
            "data_flows": self.containers.data_flow
        }
        
        with open(output_path / "container_diagram.json", "w") as f:
            json.dump(container_doc, f, indent=2)
        
        # Generate component diagrams
        component_docs = {}
        for container_id, diagram in self.component_diagrams.items():
            component_docs[container_id] = {
                "components": [
                    {
                        "id": c.id,
                        "name": c.name,
                        "type": c.component_type.value,
                        "description": c.description,
                        "technology": [t.value for t in c.technology],
                        "responsibilities": c.responsibilities
                    }
                    for c in diagram.components
                ],
                "internal_relationships": [
                    {"from": r[0], "to": r[1], "description": r[2]}
                    for r in diagram.internal_relationships
                ],
                "external_dependencies": [
                    {"from": r[0], "to": r[1], "description": r[2]}
                    for r in diagram.external_dependencies
                ]
            }
        
        with open(output_path / "component_diagrams.json", "w") as f:
            json.dump(component_docs, f, indent=2)
        
        # Generate code structure
        with open(output_path / "code_structure.json", "w") as f:
            json.dump(self.code_structure, f, indent=2)
        
        # Generate deployment view
        with open(output_path / "deployment_view.json", "w") as f:
            json.dump(self.deployment_view, f, indent=2)
        
        # Generate markdown summary
        self._generate_markdown_summary(output_path)
        
        print(f"Architecture documentation generated in {output_path}")
        return output_path
    
    def _generate_markdown_summary(self, output_path: Path):
        """Generate comprehensive markdown documentation."""
        md_content = f"""# {self.context.system_name} - System Architecture
        
## Overview

{self.context.description}

## Key Goals

{"".join(f"* {goal}\\n" for goal in self.context.key_goals)}

## Architecture Levels

### Level 1: Context Diagram

**System Context**: {self.context.system_name} interacts with the following external systems:

| System | Description | Key Interactions |
|--------|-------------|------------------|
{"".join(
    f"| {sys.name} | {sys.description} | {', '.join(sys.responsibilities[:2])} |\\n" 
    for sys in self.context.external_systems
)}

**Key User Personas**:
{"".join(
    f"#### {p.name}\\n{p.description}\\n\\n**Responsibilities**:\\n" + 
    "".join(f"* {r}\\n" for r in p.responsibilities) + "\\n"
    for p in self.context.personas
)}

### Level 2: Container Diagram

The system is composed of {len(self.containers.containers)} main containers:

| Container | Technology | Key Responsibilities |
|-----------|------------|----------------------|
{"".join(
    f"| {c.name} | {', '.join([t.value for t in c.technology[:2]])} | {c.responsibilities[0]} |\\n"
    for c in self.containers.containers
)}

**Key Data Flows**:
{"".join(
    f"#### {flow['name']}\\n{flow['description']}\\n\\n**Steps**: {flow['steps'][0]}\\n" +
    f"**Latency Target**: {flow['latency_target']}\\n" +
    f"**Throughput Target**: {flow['throughput_target']}\\n\\n"
    for flow in self.containers.data_flow
)}

### Level 3: Component Diagrams

**Market Data Ingestion Service Components**:
{"".join(
    f"* **{c.name}**: {c.description}\\n"
    for c in self.component_diagrams["market-data-ingestion"].components
)}

**Model Serving Service Components**:
{"".join(
    f"* **{c.name}**: {c.description}\\n"
    for c in self.component_diagrams["model-serving"].components
)}

### Level 4: Code Structure
