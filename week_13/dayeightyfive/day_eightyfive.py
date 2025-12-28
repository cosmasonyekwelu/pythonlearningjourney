"""
Day 85: System Architecture Design for AI Trading Systems
Comprehensive architecture patterns, event-driven systems, and resilience engineering.
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass, asdict, field
from abc import ABC, abstractmethod
import random
import statistics

import redis.asyncio as redis
from pydantic import BaseModel, Field, validator
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# Architecture Patterns Implementation
# ============================================================================

class CircuitBreakerState(Enum):
    """Circuit breaker states."""
    CLOSED = "CLOSED"      # Normal operation
    OPEN = "OPEN"          # Circuit is open, failing fast
    HALF_OPEN = "HALF_OPEN" # Testing if service is recovering


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker pattern."""
    failure_threshold: int = 5           # Failures before opening circuit
    reset_timeout: int = 60              # Seconds before attempting recovery
    success_threshold: int = 3           # Successes before closing circuit
    timeout: int = 10                    # Operation timeout in seconds


class CircuitBreaker:
    """
    Circuit breaker pattern implementation.
    Prevents cascading failures in distributed systems.
    """
    
    def __init__(self, name: str, config: CircuitBreakerConfig):
        self.name = name
        self.config = config
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.metrics = {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "circuit_opened": 0,
            "circuit_closed": 0
        }
    
    async def execute(self, operation: Callable, *args, **kwargs) -> Any:
        """
        Execute operation with circuit breaker protection.
        
        Args:
            operation: Async function to execute
            *args, **kwargs: Arguments to pass to operation
            
        Returns:
            Result of operation
            
        Raises:
            CircuitBreakerError: If circuit is open
            Exception: If operation fails
        """
        self.metrics["total_calls"] += 1
        
        # Check circuit state
        if self.state == CircuitBreakerState.OPEN:
            # Check if reset timeout has passed
            if (self.last_failure_time and 
                (datetime.now() - self.last_failure_time).seconds > self.config.reset_timeout):
                self.state = CircuitBreakerState.HALF_OPEN
                logger.info(f"Circuit {self.name}: Transitioning to HALF_OPEN")
            else:
                self.metrics["failed_calls"] += 1
                raise CircuitBreakerError(f"Circuit {self.name} is OPEN")
        
        try:
            # Execute operation with timeout
            result = await asyncio.wait_for(
                operation(*args, **kwargs),
                timeout=self.config.timeout
            )
            
            # Handle success
            self._on_success()
            return result
            
        except asyncio.TimeoutError:
            self._on_failure("Timeout")
            raise TimeoutError(f"Operation timed out after {self.config.timeout}s")
        except Exception as e:
            self._on_failure(str(e))
            raise
    
    def _on_success(self):
        """Handle successful operation."""
        self.metrics["successful_calls"] += 1
        
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                self.state = CircuitBreakerState.CLOSED
                self.success_count = 0
                self.failure_count = 0
                self.metrics["circuit_closed"] += 1
                logger.info(f"Circuit {self.name}: Transitioning to CLOSED")
        else:
            # Reset failure count on success streak
            self.failure_count = max(0, self.failure_count - 1)
    
    def _on_failure(self, error: str):
        """Handle failed operation."""
        self.metrics["failed_calls"] += 1
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if (self.state == CircuitBreakerState.CLOSED and 
            self.failure_count >= self.config.failure_threshold):
            self.state = CircuitBreakerState.OPEN
            self.metrics["circuit_opened"] += 1
            logger.warning(f"Circuit {self.name}: Transitioning to OPEN due to {error}")
        
        elif self.state == CircuitBreakerState.HALF_OPEN:
            # Failure during half-open state, go back to open
            self.state = CircuitBreakerState.OPEN
            self.success_count = 0
            logger.warning(f"Circuit {self.name}: Failed during HALF_OPEN, returning to OPEN")
    
    def get_metrics(self) -> Dict:
        """Get circuit breaker metrics."""
        success_rate = (self.metrics["successful_calls"] / self.metrics["total_calls"] * 100 
                       if self.metrics["total_calls"] > 0 else 0)
        
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "metrics": {
                **self.metrics,
                "success_rate_percent": round(success_rate, 2),
                "last_failure_time": self.last_failure_time.isoformat() if self.last_failure_time else None
            }
        }


class CircuitBreakerError(Exception):
    """Circuit breaker is open."""
    pass


class RetryStrategy:
    """
    Retry strategy with exponential backoff and jitter.
    """
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 30.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.jitter = 0.1  # 10% jitter
    
    async def execute(self, operation: Callable, *args, **kwargs) -> Any:
        """
        Execute operation with retry logic.
        
        Args:
            operation: Async function to execute
            *args, **kwargs: Arguments to pass to operation
            
        Returns:
            Result of operation
            
        Raises:
            Exception: If all retries fail
        """
        last_exception = None
        
        for attempt in range(self.max_retries + 1):  # +1 for initial attempt
            try:
                return await operation(*args, **kwargs)
            except Exception as e:
                last_exception = e
                
                if attempt == self.max_retries:
                    logger.error(f"Operation failed after {self.max_retries} retries: {e}")
                    break
                
                # Calculate delay with exponential backoff and jitter
                delay = min(
                    self.max_delay,
                    self.base_delay * (2 ** attempt)  # Exponential backoff
                )
                
                # Add jitter (±10%)
                jitter_amount = delay * self.jitter
                delay = delay + random.uniform(-jitter_amount, jitter_amount)
                delay = max(0.1, delay)  # Minimum delay
                
                logger.info(f"Retry attempt {attempt + 1}/{self.max_retries} after {delay:.2f}s")
                await asyncio.sleep(delay)
        
        raise last_exception


class Bulkhead:
    """
    Bulkhead pattern for isolating failures.
    Limits concurrent operations to prevent resource exhaustion.
    """
    
    def __init__(self, name: str, max_concurrent: int = 10):
        self.name = name
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.metrics = {
            "total_operations": 0,
            "concurrent_operations": 0,
            "max_concurrent_reached": 0,
            "rejected_operations": 0
        }
    
    async def execute(self, operation: Callable, *args, **kwargs) -> Any:
        """
        Execute operation within bulkhead limits.
        
        Args:
            operation: Async function to execute
            *args, **kwargs: Arguments to pass to operation
            
        Returns:
            Result of operation
            
        Raises:
            BulkheadFullError: If bulkhead is at capacity
        """
        current_concurrent = self.max_concurrent - self.semaphore._value
        self.metrics["concurrent_operations"] = current_concurrent
        
        if current_concurrent >= self.max_concurrent:
            self.metrics["rejected_operations"] += 1
            self.metrics["max_concurrent_reached"] += 1
            raise BulkheadFullError(f"Bulkhead {self.name} is full")
        
        async with self.semaphore:
            self.metrics["total_operations"] += 1
            return await operation(*args, **kwargs)
    
    def get_metrics(self) -> Dict:
        """Get bulkhead metrics."""
        current_concurrent = self.max_concurrent - self.semaphore._value
        
        return {
            "name": self.name,
            "max_concurrent": self.max_concurrent,
            "current_concurrent": current_concurrent,
            "available_slots": self.semaphore._value,
            "metrics": self.metrics
        }


class BulkheadFullError(Exception):
    """Bulkhead is at capacity."""
    pass


# ============================================================================
# Event-Driven Architecture
# ============================================================================

class EventType(str, Enum):
    """Event types for trading system."""
    MARKET_DATA_TICK = "market_data_tick"
    MARKET_DATA_BAR = "market_data_bar"
    TRADING_SIGNAL = "trading_signal"
    ORDER_REQUEST = "order_request"
    ORDER_EXECUTION = "order_execution"
    POSITION_UPDATE = "position_update"
    RISK_VIOLATION = "risk_violation"
    SYSTEM_HEALTH = "system_health"
    MODEL_UPDATE = "model_update"
    FEATURE_UPDATE = "feature_update"


@dataclass
class Event:
    """Base event class."""
    event_id: str
    event_type: EventType
    timestamp: datetime
    source: str
    data: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert event to dictionary."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "data": self.data,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Event':
        """Create event from dictionary."""
        return cls(
            event_id=data["event_id"],
            event_type=EventType(data["event_type"]),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            source=data["source"],
            data=data["data"],
            metadata=data.get("metadata", {})
        )


class EventBus:
    """
    Event bus for event-driven architecture.
    Supports multiple backends (Redis, Kafka, in-memory).
    """
    
    def __init__(self, backend: str = "memory", **kwargs):
        self.backend = backend
        self.subscribers: Dict[EventType, Set[Callable]] = {}
        self.metrics = {
            "events_published": 0,
            "events_delivered": 0,
            "delivery_errors": 0,
            "subscription_count": 0
        }
        
        if backend == "redis":
            self.redis_url = kwargs.get("redis_url", "redis://localhost:6379")
            self.redis_client = None
            self.pubsub = None
        elif backend == "kafka":
            # Kafka configuration
            self.kafka_config = kwargs.get("kafka_config", {})
        else:  # memory
            self.event_queue = asyncio.Queue(maxsize=10000)
    
    async def connect(self):
        """Connect to event bus backend."""
        if self.backend == "redis":
            self.redis_client = await redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            self.pubsub = self.redis_client.pubsub()
            logger.info(f"Connected to Redis event bus at {self.redis_url}")
        elif self.backend == "kafka":
            # Initialize Kafka producer/consumer
            logger.info("Initialized Kafka event bus")
        else:
            logger.info("Using in-memory event bus")
    
    async def disconnect(self):
        """Disconnect from event bus backend."""
        if self.backend == "redis" and self.redis_client:
            await self.redis_client.close()
        logger.info(f"Disconnected from {self.backend} event bus")
    
    async def publish(self, event: Event):
        """Publish event to event bus."""
        self.metrics["events_published"] += 1
        
        if self.backend == "redis":
            await self._publish_redis(event)
        elif self.backend == "kafka":
            await self._publish_kafka(event)
        else:
            await self._publish_memory(event)
    
    async def _publish_redis(self, event: Event):
        """Publish event to Redis."""
        channel = f"events:{event.event_type.value}"
        await self.redis_client.publish(channel, json.dumps(event.to_dict()))
    
    async def _publish_kafka(self, event: Event):
        """Publish event to Kafka."""
        # Kafka implementation would go here
        pass
    
    async def _publish_memory(self, event: Event):
        """Publish event to memory queue."""
        try:
            await self.event_queue.put(event)
        except asyncio.QueueFull:
            logger.warning("Event queue is full, dropping event")
    
    async def subscribe(self, event_type: EventType, callback: Callable):
        """Subscribe to event type."""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = set()
        
        self.subscribers[event_type].add(callback)
        self.metrics["subscription_count"] += 1
        
        logger.info(f"Subscribed to {event_type.value}")
    
    async def unsubscribe(self, event_type: EventType, callback: Callable):
        """Unsubscribe from event type."""
        if event_type in self.subscribers:
            self.subscribers[event_type].discard(callback)
            self.metrics["subscription_count"] -= 1
    
    async def start_consuming(self):
        """Start consuming events from event bus."""
        if self.backend == "redis":
            await self._consume_redis()
        elif self.backend == "kafka":
            await self._consume_kafka()
        else:
            await self._consume_memory()
    
    async def _consume_redis(self):
        """Consume events from Redis."""
        # Subscribe to all event channels
        channels = [f"events:{et.value}" for et in self.subscribers.keys()]
        if channels:
            await self.pubsub.subscribe(*channels)
        
        async for message in self.pubsub.listen():
            if message["type"] == "message":
                channel = message["channel"]
                event_type_str = channel.replace("events:", "")
                event_type = EventType(event_type_str)
                
                event_data = json.loads(message["data"])
                event = Event.from_dict(event_data)
                
                await self._deliver_event(event_type, event)
    
    async def _consume_memory(self):
        """Consume events from memory queue."""
        while True:
            try:
                event = await self.event_queue.get()
                await self._deliver_event(event.event_type, event)
                self.event_queue.task_done()
            except Exception as e:
                logger.error(f"Error consuming event: {e}")
    
    async def _consume_kafka(self):
        """Consume events from Kafka."""
        # Kafka implementation would go here
        pass
    
    async def _deliver_event(self, event_type: EventType, event: Event):
        """Deliver event to subscribers."""
        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                try:
                    await callback(event)
                    self.metrics["events_delivered"] += 1
                except Exception as e:
                    self.metrics["delivery_errors"] += 1
                    logger.error(f"Error delivering event to callback: {e}")
    
    def get_metrics(self) -> Dict:
        """Get event bus metrics."""
        subscription_counts = {
            et.value: len(callbacks)
            for et, callbacks in self.subscribers.items()
        }
        
        return {
            "backend": self.backend,
            "metrics": self.metrics,
            "subscription_counts": subscription_counts
        }


# ============================================================================
# CQRS Pattern Implementation
# ============================================================================

class Command(BaseModel):
    """Base command for CQRS pattern."""
    command_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    correlation_id: Optional[str] = None
    
    class Config:
        arbitrary_types_allowed = True


class Query(BaseModel):
    """Base query for CQRS pattern."""
    query_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        arbitrary_types_allowed = True


class CommandResult(BaseModel):
    """Result of command execution."""
    command_id: str
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        arbitrary_types_allowed = True


class QueryResult(BaseModel):
    """Result of query execution."""
    query_id: str
    data: Any
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        arbitrary_types_allowed = True


class CommandHandler(ABC):
    """Abstract command handler."""
    
    @abstractmethod
    async def handle(self, command: Command) -> CommandResult:
        """Handle command."""
        pass


class QueryHandler(ABC):
    """Abstract query handler."""
    
    @abstractmethod
    async def handle(self, query: Query) -> QueryResult:
        """Handle query."""
        pass


class CommandBus:
    """
    Command bus for CQRS pattern.
    Routes commands to appropriate handlers.
    """
    
    def __init__(self):
        self.handlers: Dict[str, CommandHandler] = {}
        self.metrics = {
            "commands_processed": 0,
            "command_errors": 0,
            "avg_processing_time_ms": 0
        }
        self.processing_times: List[float] = []
    
    def register_handler(self, command_type: str, handler: CommandHandler):
        """Register command handler."""
        self.handlers[command_type] = handler
        logger.info(f"Registered handler for command type: {command_type}")
    
    async def dispatch(self, command: Command) -> CommandResult:
        """Dispatch command to handler."""
        start_time = time.time()
        command_type = command.__class__.__name__
        
        if command_type not in self.handlers:
            error_msg = f"No handler registered for command type: {command_type}"
            logger.error(error_msg)
            return CommandResult(
                command_id=command.command_id,
                success=False,
                error=error_msg
            )
        
        try:
            handler = self.handlers[command_type]
            result = await handler.handle(command)
            
            # Update metrics
            processing_time = (time.time() - start_time) * 1000
            self.processing_times.append(processing_time)
            if len(self.processing_times) > 1000:
                self.processing_times = self.processing_times[-1000:]
            
            self.metrics["commands_processed"] += 1
            self.metrics["avg_processing_time_ms"] = statistics.mean(self.processing_times) if self.processing_times else 0
            
            logger.info(f"Command {command_type} processed in {processing_time:.2f}ms")
            return result
            
        except Exception as e:
            self.metrics["command_errors"] += 1
            logger.error(f"Error processing command {command_type}: {e}")
            return CommandResult(
                command_id=command.command_id,
                success=False,
                error=str(e)
            )
    
    def get_metrics(self) -> Dict:
        """Get command bus metrics."""
        return {
            "handlers_registered": len(self.handlers),
            "metrics": self.metrics,
            "handler_types": list(self.handlers.keys())
        }


class QueryBus:
    """
    Query bus for CQRS pattern.
    Routes queries to appropriate handlers.
    """
    
    def __init__(self):
        self.handlers: Dict[str, QueryHandler] = {}
        self.metrics = {
            "queries_processed": 0,
            "query_errors": 0,
            "avg_processing_time_ms": 0
        }
        self.processing_times: List[float] = []
    
    def register_handler(self, query_type: str, handler: QueryHandler):
        """Register query handler."""
        self.handlers[query_type] = handler
        logger.info(f"Registered handler for query type: {query_type}")
    
    async def dispatch(self, query: Query) -> QueryResult:
        """Dispatch query to handler."""
        start_time = time.time()
        query_type = query.__class__.__name__
        
        if query_type not in self.handlers:
            error_msg = f"No handler registered for query type: {query_type}"
            logger.error(error_msg)
            return QueryResult(
                query_id=query.query_id,
                data={"error": error_msg}
            )
        
        try:
            handler = self.handlers[query_type]
            result = await handler.handle(query)
            
            # Update metrics
            processing_time = (time.time() - start_time) * 1000
            self.processing_times.append(processing_time)
            if len(self.processing_times) > 1000:
                self.processing_times = self.processing_times[-1000:]
            
            self.metrics["queries_processed"] += 1
            self.metrics["avg_processing_time_ms"] = statistics.mean(self.processing_times) if self.processing_times else 0
            
            logger.info(f"Query {query_type} processed in {processing_time:.2f}ms")
            return result
            
        except Exception as e:
            self.metrics["query_errors"] += 1
            logger.error(f"Error processing query {query_type}: {e}")
            return QueryResult(
                query_id=query.query_id,
                data={"error": str(e)}
            )
    
    def get_metrics(self) -> Dict:
        """Get query bus metrics."""
        return {
            "handlers_registered": len(self.handlers),
            "metrics": self.metrics,
            "handler_types": list(self.handlers.keys())
        }


# ============================================================================
# Trading System Components with Resilience Patterns
# ============================================================================

class CreateOrderCommand(Command):
    """Command to create an order."""
    symbol: str
    side: str  # "BUY" or "SELL"
    quantity: float
    order_type: str = "MARKET"
    price: Optional[float] = None
    strategy_id: str
    signal_id: Optional[str] = None


class OrderCreatedEvent(Event):
    """Event emitted when order is created."""
    pass


class OrderCommandHandler(CommandHandler):
    """Handler for order commands."""
    
    def __init__(self, event_bus: EventBus, circuit_breaker: CircuitBreaker):
        self.event_bus = event_bus
        self.circuit_breaker = circuit_breaker
        self.retry_strategy = RetryStrategy(max_retries=3)
    
    async def handle(self, command: CreateOrderCommand) -> CommandResult:
        """Handle create order command."""
        try:
            # Use circuit breaker for external service call
            async def create_order():
                # Simulate order creation with external service
                if random.random() < 0.1:  # 10% failure rate for demo
                    raise Exception("External order service unavailable")
                
                order_id = f"ORD_{int(time.time())}_{random.randint(1000, 9999)}"
                return {
                    "order_id": order_id,
                    "status": "CREATED",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Execute with circuit breaker
            result = await self.circuit_breaker.execute(create_order)
            
            # Publish event
            event = Event(
                event_id=f"EVT_{int(time.time())}",
                event_type=EventType.ORDER_REQUEST,
                timestamp=datetime.now(),
                source="OrderCommandHandler",
                data={
                    "order_id": result["order_id"],
                    "command_id": command.command_id,
                    "symbol": command.symbol,
                    "side": command.side,
                    "quantity": command.quantity,
                    "strategy_id": command.strategy_id
                }
            )
            
            await self.event_bus.publish(event)
            
            return CommandResult(
                command_id=command.command_id,
                success=True,
                result=result
            )
            
        except Exception as e:
            logger.error(f"Failed to create order: {e}")
            return CommandResult(
                command_id=command.command_id,
                success=False,
                error=str(e)
            )


class GetPortfolioQuery(Query):
    """Query to get portfolio information."""
    account_id: str
    include_positions: bool = True
    include_history: bool = False


class PortfolioQueryHandler(QueryHandler):
    """Handler for portfolio queries."""
    
    def __init__(self, bulkhead: Bulkhead):
        self.bulkhead = bulkhead
    
    async def handle(self, query: GetPortfolioQuery) -> QueryResult:
        """Handle get portfolio query."""
        try:
            # Use bulkhead for database query
            async def get_portfolio():
                # Simulate database query
                await asyncio.sleep(0.1)  # Simulate DB latency
                
                # Mock portfolio data
                return {
                    "account_id": query.account_id,
                    "total_value": 1000000.0,
                    "cash_balance": 250000.0,
                    "positions": [
                        {"symbol": "AAPL", "quantity": 100, "avg_price": 175.0},
                        {"symbol": "GOOGL", "quantity": 50, "avg_price": 130.0}
                    ] if query.include_positions else [],
                    "last_updated": datetime.now().isoformat()
                }
            
            # Execute within bulkhead
            data = await self.bulkhead.execute(get_portfolio)
            
            return QueryResult(
                query_id=query.query_id,
                data=data
            )
            
        except Exception as e:
            logger.error(f"Failed to get portfolio: {e}")
            return QueryResult(
                query_id=query.query_id,
                data={"error": str(e)}
            )


# ============================================================================
# Hexagonal Architecture Adapters
# ============================================================================

class MarketDataPort(ABC):
    """Port for market data (driving port)."""
    
    @abstractmethod
    async def get_latest_price(self, symbol: str) -> float:
        """Get latest price for symbol."""
        pass
    
    @abstractmethod
    async def subscribe_to_ticks(self, symbol: str, callback: Callable):
        """Subscribe to tick updates for symbol."""
        pass


class OrderExecutionPort(ABC):
    """Port for order execution (driving port)."""
    
    @abstractmethod
    async def execute_order(self, order: Dict) -> Dict:
        """Execute trading order."""
        pass


class PositionRepositoryPort(ABC):
    """Port for position repository (driven port)."""
    
    @abstractmethod
    async def get_positions(self, account_id: str) -> List[Dict]:
        """Get positions for account."""
        pass
    
    @abstractmethod
    async def update_position(self, account_id: str, position: Dict):
        """Update position for account."""
        pass


class RedisMarketDataAdapter(MarketDataPort):
    """Redis adapter for market data port."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis_client = None
        self.subscriptions = {}
    
    async def connect(self):
        """Connect to Redis."""
        self.redis_client = await redis.from_url(self.redis_url)
    
    async def get_latest_price(self, symbol: str) -> float:
        """Get latest price from Redis."""
        price = await self.redis_client.get(f"price:{symbol}")
        return float(price) if price else 0.0
    
    async def subscribe_to_ticks(self, symbol: str, callback: Callable):
        """Subscribe to tick updates via Redis Pub/Sub."""
        if symbol not in self.subscriptions:
            self.subscriptions[symbol] = []
        
        self.subscriptions[symbol].append(callback)
        
        # In real implementation, would set up Redis Pub/Sub subscription
        logger.info(f"Subscribed to ticks for {symbol}")


class MockOrderExecutionAdapter(OrderExecutionPort):
    """Mock adapter for order execution (for testing)."""
    
    def __init__(self, success_rate: float = 0.95):
        self.success_rate = success_rate
        self.execution_count = 0
    
    async def execute_order(self, order: Dict) -> Dict:
        """Mock order execution."""
        self.execution_count += 1
        
        # Simulate execution with some failure rate
        if random.random() > self.success_rate:
            raise Exception("Order execution failed")
        
        # Simulate execution delay
        await asyncio.sleep(0.05)
        
        return {
            "order_id": order.get("order_id", f"EXEC_{self.execution_count}"),
            "status": "FILLED",
            "execution_price": order.get("price", 100.0),
            "execution_time": datetime.now().isoformat(),
            "commission": 1.0
        }


class InMemoryPositionRepository(PositionRepositoryPort):
    """In-memory adapter for position repository."""
    
    def __init__(self):
        self.positions = {}  # account_id -> list of positions
    
    async def get_positions(self, account_id: str) -> List[Dict]:
        """Get positions from memory."""
        return self.positions.get(account_id, [])
    
    async def update_position(self, account_id: str, position: Dict):
        """Update position in memory."""
        if account_id not in self.positions:
            self.positions[account_id] = []
        
        # Find and update existing position or add new
        for i, pos in enumerate(self.positions[account_id]):
            if pos["symbol"] == position["symbol"]:
                self.positions[account_id][i] = position
                break
        else:
            self.positions[account_id].append(position)


# ============================================================================
# Trading System Domain Core
# ============================================================================

class TradingStrategy:
    """
    Trading strategy domain entity.
    Demonstrates hexagonal architecture with ports and adapters.
    """
    
    def __init__(
        self,
        strategy_id: str,
        market_data_port: MarketDataPort,
        order_execution_port: OrderExecutionPort,
        position_repository_port: PositionRepositoryPort
    ):
        self.strategy_id = strategy_id
        self.market_data = market_data_port
        self.order_execution = order_execution_port
        self.position_repository = position_repository_port
        self.is_running = False
        self.metrics = {
            "signals_generated": 0,
            "orders_executed": 0,
            "total_pnl": 0.0,
            "winning_trades": 0,
            "losing_trades": 0
        }
    
    async def start(self):
        """Start the trading strategy."""
        self.is_running = True
        logger.info(f"Strategy {self.strategy_id} started")
        
        # Subscribe to market data
        symbols = ["AAPL", "GOOGL", "MSFT"]
        for symbol in symbols:
            await self.market_data.subscribe_to_ticks(
                symbol,
                self._on_tick_update
            )
    
    async def stop(self):
        """Stop the trading strategy."""
        self.is_running = False
        logger.info(f"Strategy {self.strategy_id} stopped")
    
    async def _on_tick_update(self, tick: Dict):
        """Handle tick update."""
        if not self.is_running:
            return
        
        symbol = tick["symbol"]
        price = tick["price"]
        
        # Simple strategy: Buy on dip, sell on rally
        positions = await self.position_repository.get_positions(self.strategy_id)
        current_position = next(
            (p for p in positions if p["symbol"] == symbol),
            {"quantity": 0, "avg_price": 0}
        )
        
        # Generate signal based on simple logic
        signal = await self._generate_signal(symbol, price, current_position)
        
        if signal:
            self.metrics["signals_generated"] += 1
            
            # Execute order if signal is strong enough
            if abs(signal["confidence"]) > 0.7:
                order = {
                    "strategy_id": self.strategy_id,
                    "symbol": symbol,
                    "side": "BUY" if signal["confidence"] > 0 else "SELL",
                    "quantity": 10,
                    "order_type": "MARKET",
                    "signal_confidence": signal["confidence"]
                }
                
                try:
                    result = await self.order_execution.execute_order(order)
                    self.metrics["orders_executed"] += 1
                    
                    # Update position
                    await self._update_position(symbol, order["side"], order["quantity"], result["execution_price"])
                    
                    logger.info(f"Strategy {self.strategy_id}: Executed {order['side']} order for {symbol}")
                    
                except Exception as e:
                    logger.error(f"Strategy {self.strategy_id}: Order execution failed: {e}")
    
    async def _generate_signal(self, symbol: str, price: float, position: Dict) -> Optional[Dict]:
        """Generate trading signal."""
        # Simple mean reversion strategy
        historical_prices = [price * (1 + random.uniform(-0.02, 0.02)) for _ in range(20)]
        avg_price = sum(historical_prices) / len(historical_prices)
        
        # Calculate deviation from mean
        deviation = (price - avg_price) / avg_price
        
        # Generate confidence based on deviation
        if deviation < -0.03:  # 3% below average
            return {"confidence": 0.8, "reason": "Oversold"}
        elif deviation > 0.03:  # 3% above average
            return {"confidence": -0.8, "reason": "Overbought"}
        
        return None
    
    async def _update_position(self, symbol: str, side: str, quantity: float, price: float):
        """Update position after trade."""
        positions = await self.position_repository.get_positions(self.strategy_id)
        
        # Find existing position
        position_idx = -1
        for i, pos in enumerate(positions):
            if pos["symbol"] == symbol:
                position_idx = i
                break
        
        if position_idx >= 0:
            # Update existing position
            pos = positions[position_idx]
            if side == "BUY":
                new_quantity = pos["quantity"] + quantity
                new_avg_price = ((pos["quantity"] * pos["avg_price"]) + (quantity * price)) / new_quantity
                positions[position_idx] = {
                    "symbol": symbol,
                    "quantity": new_quantity,
                    "avg_price": new_avg_price
                }
            else:  # SELL
                new_quantity = pos["quantity"] - quantity
                if new_quantity <= 0:
                    # Position closed
                    positions.pop(position_idx)
                    # Calculate P&L
                    pnl = quantity * (price - pos["avg_price"])
                    self.metrics["total_pnl"] += pnl
                    if pnl > 0:
                        self.metrics["winning_trades"] += 1
                    else:
                        self.metrics["losing_trades"] += 1
                else:
                    positions[position_idx] = {
                        "symbol": symbol,
                        "quantity": new_quantity,
                        "avg_price": pos["avg_price"]  # Keep same avg price for remaining
                    }
        else:
            # New position
            if side == "BUY":
                positions.append({
                    "symbol": symbol,
                    "quantity": quantity,
                    "avg_price": price
                })
        
        # Save updated positions
        await self.position_repository.update_position(self.strategy_id, positions)
    
    def get_metrics(self) -> Dict:
        """Get strategy metrics."""
        win_rate = (self.metrics["winning_trades"] / 
                   (self.metrics["winning_trades"] + self.metrics["losing_trades"]) * 100
                   if (self.metrics["winning_trades"] + self.metrics["losing_trades"]) > 0 else 0)
        
        return {
            "strategy_id": self.strategy_id,
            "is_running": self.is_running,
            "metrics": {
                **self.metrics,
                "win_rate_percent": round(win_rate, 2)
            }
        }


# ============================================================================
# System Orchestrator
# ============================================================================

class TradingSystemOrchestrator:
    """
    Orchestrates all components of the trading system.
    Demonstrates layered architecture and resilience patterns.
    """
    
    def __init__(self):
        # Initialize resilience patterns
        self.order_circuit_breaker = CircuitBreaker(
            "OrderService",
            CircuitBreakerConfig(
                failure_threshold=3,
                reset_timeout=30,
                success_threshold=2
            )
        )
        
        self.db_bulkhead = Bulkhead("Database", max_concurrent=5)
        
        # Initialize event bus
        self.event_bus = EventBus(backend="memory")
        
        # Initialize CQRS buses
        self.command_bus = CommandBus()
        self.query_bus = QueryBus()
        
        # Initialize adapters
        self.market_data_adapter = RedisMarketDataAdapter()
        self.order_execution_adapter = MockOrderExecutionAdapter(success_rate=0.9)
        self.position_repository = InMemoryPositionRepository()
        
        # Initialize domain entities
        self.strategies: Dict[str, TradingStrategy] = {}
        
        # System metrics
        self.metrics = {
            "start_time": datetime.now(),
            "total_events": 0,
            "system_uptime_seconds": 0
        }
        
        # Register command and query handlers
        self._register_handlers()
    
    def _register_handlers(self):
        """Register command and query handlers."""
        # Register order command handler
        order_handler = OrderCommandHandler(
            event_bus=self.event_bus,
            circuit_breaker=self.order_circuit_breaker
        )
        self.command_bus.register_handler("CreateOrderCommand", order_handler)
        
        # Register portfolio query handler
        portfolio_handler = PortfolioQueryHandler(bulkhead=self.db_bulkhead)
        self.query_bus.register_handler("GetPortfolioQuery", portfolio_handler)
    
    async def initialize(self):
        """Initialize the trading system."""
        logger.info("Initializing trading system...")
        
        # Connect to external services
        await self.event_bus.connect()
        await self.market_data_adapter.connect()
        
        # Create sample strategies
        strategy1 = TradingStrategy(
            strategy_id="strategy_001",
            market_data_port=self.market_data_adapter,
            order_execution_port=self.order_execution_adapter,
            position_repository_port=self.position_repository
        )
        
        self.strategies[strategy1.strategy_id] = strategy1
        
        logger.info("Trading system initialized")
    
    async def start(self):
        """Start the trading system."""
        logger.info("Starting trading system...")
        
        # Start event bus consumption
        asyncio.create_task(self.event_bus.start_consuming())
        
        # Start strategies
        for strategy in self.strategies.values():
            await strategy.start()
        
        # Start monitoring task
        asyncio.create_task(self._monitoring_task())
        
        logger.info("Trading system started")
    
    async def stop(self):
        """Stop the trading system."""
        logger.info("Stopping trading system...")
        
        # Stop strategies
        for strategy in self.strategies.values():
            await strategy.stop()
        
        # Disconnect from external services
        await self.event_bus.disconnect()
        
        logger.info("Trading system stopped")
    
    async def _monitoring_task(self):
        """Periodic monitoring task."""
        while True:
            try:
                await asyncio.sleep(10)  # Update every 10 seconds
                
                # Update system metrics
                self.metrics["system_uptime_seconds"] = (
                    datetime.now() - self.metrics["start_time"]
                ).total_seconds()
                
                # Get event bus metrics
                event_bus_metrics = self.event_bus.get_metrics()
                self.metrics["total_events"] = event_bus_metrics["metrics"]["events_published"]
                
                # Log system status
                logger.info(f"System Status - Uptime: {self.metrics['system_uptime_seconds']:.0f}s, "
                          f"Events: {self.metrics['total_events']}")
                
                # Log circuit breaker status
                cb_metrics = self.order_circuit_breaker.get_metrics()
                if cb_metrics["state"] != "CLOSED":
                    logger.warning(f"Circuit Breaker: {cb_metrics['name']} is {cb_metrics['state']}")
                
            except Exception as e:
                logger.error(f"Error in monitoring task: {e}")
    
    async def create_order(self, symbol: str, side: str, quantity: float, strategy_id: str) -> Dict:
        """Create order through command bus."""
        command = CreateOrderCommand(
            command_id=f"CMD_{int(time.time())}",
            symbol=symbol,
            side=side,
            quantity=quantity,
            strategy_id=strategy_id
        )
        
        result = await self.command_bus.dispatch(command)
        return result.dict()
    
    async def get_portfolio(self, account_id: str) -> Dict:
        """Get portfolio through query bus."""
        query = GetPortfolioQuery(
            query_id=f"QRY_{int(time.time())}",
            account_id=account_id,
            include_positions=True
        )
        
        result = await self.query_bus.dispatch(query)
        return result.dict()
    
    async def get_system_status(self) -> Dict:
        """Get comprehensive system status."""
        # Collect metrics from all components
        cb_status = self.order_circuit_breaker.get_metrics()
        bulkhead_status = self.db_bulkhead.get_metrics()
        event_bus_status = self.event_bus.get_metrics()
        command_bus_status = self.command_bus.get_metrics()
        query_bus_status = self.query_bus.get_metrics()
        
        # Strategy metrics
        strategy_metrics = {}
        for strategy_id, strategy in self.strategies.items():
            strategy_metrics[strategy_id] = strategy.get_metrics()
        
        return {
            "system": {
                "uptime_seconds": self.metrics["system_uptime_seconds"],
                "total_events": self.metrics["total_events"],
                "start_time": self.metrics["start_time"].isoformat()
            },
            "resilience_patterns": {
                "circuit_breaker": cb_status,
                "bulkhead": bulkhead_status
            },
            "architecture_components": {
                "event_bus": event_bus_status,
                "command_bus": command_bus_status,
                "query_bus": query_bus_status
            },
            "strategies": strategy_metrics
        }


# ============================================================================
# Demo and Testing
# ============================================================================

async def demonstrate_architecture_patterns():
    """Demonstrate architecture patterns in action."""
    print("\n" + "="*80)
    print("Day 85: System Architecture Design for AI Trading Systems")
    print("="*80)
    
    # Initialize orchestrator
    print("\n1. Initializing Trading System Orchestrator...")
    orchestrator = TradingSystemOrchestrator()
    await orchestrator.initialize()
    
    # Start system
    print("\n2. Starting Trading System...")
    await orchestrator.start()
    
    try:
        # Demonstrate circuit breaker pattern
        print("\n3. Demonstrating Circuit Breaker Pattern...")
        print("   Simulating order creation with occasional failures...")
        
        for i in range(10):
            try:
                result = await orchestrator.create_order(
                    symbol="AAPL",
                    side="BUY" if i % 2 == 0 else "SELL",
                    quantity=100,
                    strategy_id="strategy_001"
                )
                
                if result["success"]:
                    print(f"   ✓ Order {i+1}: Success")
                else:
                    print(f"   ✗ Order {i+1}: Failed - {result['error']}")
                
            except Exception as e:
                print(f"   ✗ Order {i+1}: Exception - {str(e)[:50]}")
            
            await asyncio.sleep(0.5)
        
        # Demonstrate CQRS pattern
        print("\n4. Demonstrating CQRS Pattern...")
        print("   Querying portfolio through query bus...")
        
        portfolio = await orchestrator.get_portfolio("account_001")
        print(f"   Portfolio data: {json.dumps(portfolio['data'], indent=2)[:100]}...")
        
        # Demonstrate bulkhead pattern
        print("\n5. Demonstrating Bulkhead Pattern...")
        print("   Simulating concurrent database queries...")
        
        queries = []
        for i in range(8):  # More than bulkhead limit (5)
            query = orchestrator.get_portfolio(f"account_{i:03d}")
            queries.append(query)
        
        results = await asyncio.gather(*queries, return_exceptions=True)
        
        successful = sum(1 for r in results if not isinstance(r, Exception))
        failed = sum(1 for r in results if isinstance(r, BulkheadFullError))
        
        print(f"   Successful queries: {successful}")
        print(f"   Failed due to bulkhead: {failed}")
        
        # Get system status
        print("\n6. Getting System Status...")
        status = await orchestrator.get_system_status()
        
        print(f"   System Uptime: {status['system']['uptime_seconds']:.0f}s")
        print(f"   Total Events: {status['system']['total_events']}")
        
        cb_state = status['resilience_patterns']['circuit_breaker']['state']
        print(f"   Circuit Breaker State: {cb_state}")
        
        event_count = status['architecture_components']['event_bus']['metrics']['events_published']
        print(f"   Events Published: {event_count}")
        
        # Strategy metrics
        for strategy_id, metrics in status['strategies'].items():
            print(f"\n   Strategy {strategy_id}:")
            print(f"     Signals Generated: {metrics['metrics']['signals_generated']}")
            print(f"     Orders Executed: {metrics['metrics']['orders_executed']}")
            print(f"     Total P&L: ${metrics['metrics']['total_pnl']:.2f}")
        
        print("\n" + "="*80)
        print("Architecture Patterns Demonstrated:")
        print("  ✓ Circuit Breaker - Prevents cascading failures")
        print("  ✓ Retry Strategy - Exponential backoff with jitter")
        print("  ✓ Bulkhead - Isolates failures and limits concurrency")
        print("  ✓ Event-Driven - Loose coupling through events")
        print("  ✓ CQRS - Separate command and query models")
        print("  ✓ Hexagonal Architecture - Ports and adapters")
        print("  ✓ Layered Architecture - Clear separation of concerns")
        print("="*80)
        
        # Let system run for a bit more
        print("\n7. Letting system run for 30 seconds...")
        print("   (Press Ctrl+C to stop early)")
        
        for i in range(30):
            await asyncio.sleep(1)
            if i % 10 == 0:
                current_status = await orchestrator.get_system_status()
                events = current_status['system']['total_events']
                print(f"   ... {i+10}s: {events} total events")
        
    except KeyboardInterrupt:
        print("\n\nStopping demonstration...")
    
    finally:
        # Stop system
        print("\n8. Stopping Trading System...")
        await orchestrator.stop()
        
        print("\n✅ Demonstration complete!")
        print("\nKey Takeaways:")
        print("  • Architecture patterns make systems more resilient")
        print("  • Event-driven design enables loose coupling")
        print("  • CQRS separates read and write concerns")
        print("  • Hexagonal architecture improves testability")
        print("  • Proper monitoring is essential for production systems")


async def performance_test():
    """Test performance of architecture patterns."""
    print("\n" + "="*80)
    print("Performance Test: Architecture Patterns")
    print("="*80)
    
    # Test circuit breaker performance
    print("\n1. Testing Circuit Breaker Performance...")
    
    config = CircuitBreakerConfig(
        failure_threshold=3,
        reset_timeout=2,
        success_threshold=2
    )
    
    cb = CircuitBreaker("TestService", config)
    
    async def failing_operation():
        await asyncio.sleep(0.01)
        raise Exception("Simulated failure")
    
    async def successful_operation():
        await asyncio.sleep(0.01)
        return "success"
    
    # Test failure handling
    failures = 0
    start_time = time.time()
    
    for i in range(10):
        try:
            await cb.execute(failing_operation)
        except Exception:
            failures += 1
    
    duration = time.time() - start_time
    print(f"   Processed 10 operations in {duration*1000:.2f}ms")
    print(f"   Failures: {failures}")
    print(f"   Final State: {cb.state.value}")
    
    # Test bulkhead performance
    print("\n2. Testing Bulkhead Performance...")
    
    bulkhead = Bulkhead("TestDB", max_concurrent=3)
    
    async def db_operation(idx: int):
        await asyncio.sleep(0.1)
        return idx
    
    # Run concurrent operations
    tasks = []
    start_time = time.time()
    
    for i in range(10):
        task = asyncio.create_task(
            bulkhead.execute(db_operation, i)
        )
        tasks.append(task)
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    duration = time.time() - start_time
    
    successful = sum(1 for r in results if not isinstance(r, Exception))
    failed = sum(1 for r in results if isinstance(r, BulkheadFullError))
    
    print(f"   Processed 10 operations in {duration*1000:.2f}ms")
    print(f"   Successful: {successful}, Failed (bulkhead full): {failed}")
    
    # Test event bus performance
    print("\n3. Testing Event Bus Performance...")
    
    event_bus = EventBus(backend="memory")
    await event_bus.connect()
    
    event_count = 1000
    received_count = 0
    
    async def event_handler(event: Event):
        nonlocal received_count
        received_count += 1
    
    # Subscribe to events
    await event_bus.subscribe(EventType.MARKET_DATA_TICK, event_handler)
    
    # Publish events
    start_time = time.time()
    
    for i in range(event_count):
        event = Event(
            event_id=f"test_{i}",
            event_type=EventType.MARKET_DATA_TICK,
            timestamp=datetime.now(),
            source="test",
            data={"index": i}
        )
        await event_bus.publish(event)
    
    # Process events
    await asyncio.sleep(0.1)  # Give time for event delivery
    
    duration = time.time() - start_time
    events_per_second = event_count / duration
    
    print(f"   Published {event_count} events in {duration*1000:.2f}ms")
    print(f"   Received {received_count} events")
    print(f"   Throughput: {events_per_second:.0f} events/second")
    
    await event_bus.disconnect()
    
    print("\n" + "="*80)
    print("Performance Test Complete")
    print("="*80)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Trading System Architecture Patterns")
    parser.add_argument("--demo", action="store_true", help="Run architecture patterns demonstration")
    parser.add_argument("--performance", action="store_true", help="Run performance tests")
    parser.add_argument("--all", action="store_true", help="Run all demonstrations")
    
    args = parser.parse_args()
    
    if args.all or (not args.demo and not args.performance):
        # Run both by default
        asyncio.run(demonstrate_architecture_patterns())
        asyncio.run(performance_test())
    elif args.demo:
        asyncio.run(demonstrate_architecture_patterns())
    elif args.performance:
        asyncio.run(performance_test())


if __name__ == "__main__":
    main()