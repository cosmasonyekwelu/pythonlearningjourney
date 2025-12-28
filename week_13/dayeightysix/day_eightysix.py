"""
Day 86 Challenge: Serverless Trading Pipeline on AWS
Lambda-based trading system with event-driven architecture.
"""

import json
import boto3
import os
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
import base64
import gzip
from dataclasses import dataclass, asdict
from decimal import Decimal
import numpy as np
import pandas as pd
from io import StringIO, BytesIO

# AWS Clients
lambda_client = boto3.client('lambda')
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
cloudwatch = boto3.client('cloudwatch')
secretsmanager = boto3.client('secretsmanager')
eventbridge = boto3.client('events')
stepfunctions = boto3.client('stepfunctions')

# Constants
MODEL_BUCKET = os.environ.get('MODEL_BUCKET', 'quantflow-models')
DATA_BUCKET = os.environ.get('DATA_BUCKET', 'quantflow-market-data')
STATE_TABLE = os.environ.get('STATE_TABLE', 'trading-state')
METRICS_TABLE = os.environ.get('METRICS_TABLE', 'trading-metrics')
CONFIG_TABLE = os.environ.get('CONFIG_TABLE', 'trading-config')

# Decimal encoder for DynamoDB
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


@dataclass
class MarketData:
    """Market data event."""
    symbol: str
    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    interval: str = "1min"
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'MarketData':
        return cls(**data)


@dataclass
class TradingSignal:
    """Trading signal."""
    signal_id: str
    timestamp: str
    symbol: str
    signal: str  # "BUY", "SELL", "HOLD"
    confidence: float
    price: float
    features: Dict[str, float]
    model_version: str
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'TradingSignal':
        return cls(**data)


@dataclass
class OrderRequest:
    """Order request."""
    order_id: str
    timestamp: str
    symbol: str
    side: str  # "BUY", "SELL"
    quantity: float
    order_type: str = "MARKET"
    price: Optional[float] = None
    signal_id: Optional[str] = None
    strategy_id: str = "default"
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'OrderRequest':
        return cls(**data)


@dataclass
class Position:
    """Trading position."""
    account_id: str
    symbol: str
    quantity: float
    avg_price: float
    unrealized_pnl: float
    realized_pnl: float
    last_updated: str
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Position':
        return cls(**data)


class ServerlessTradingPipeline:
    """
    Serverless trading pipeline using AWS Lambda and other serverless services.
    Implements event-driven architecture with cost optimization.
    """
    
    def __init__(self):
        self.tables = {
            'state': dynamodb.Table(STATE_TABLE),
            'metrics': dynamodb.Table(METRICS_TABLE),
            'config': dynamodb.Table(CONFIG_TABLE)
        }
        
        # Initialize configuration
        self._load_config()
        
        # Cost tracking
        self.cost_tracker = CostTracker()
        
        # Performance metrics
        self.metrics = {
            'events_processed': 0,
            'signals_generated': 0,
            'orders_executed': 0,
            'errors': 0,
            'total_cost': 0.0
        }
    
    def _load_config(self):
        """Load pipeline configuration from DynamoDB."""
        try:
            response = self.tables['config'].get_item(Key={'config_type': 'pipeline'})
            if 'Item' in response:
                self.config = response['Item']
            else:
                # Default configuration
                self.config = {
                    'config_type': 'pipeline',
                    'enabled': True,
                    'trading_hours': {
                        'start': '09:30',
                        'end': '16:00',
                        'timezone': 'America/New_York'
                    },
                    'risk_limits': {
                        'max_position_size': 10000,
                        'max_daily_loss': -5000,
                        'max_drawdown': -0.1  # 10%
                    },
                    'cost_limits': {
                        'max_daily_lambda_cost': 10.0,  # $10/day
                        'max_daily_data_cost': 5.0,     # $5/day
                        'alert_threshold': 0.8          # 80% of limit
                    },
                    'performance_targets': {
                        'max_latency_ms': 1000,
                        'min_throughput_per_min': 100,
                        'error_rate_threshold': 0.01  # 1%
                    }
                }
                self.tables['config'].put_item(Item=self.config)
        except Exception as e:
            print(f"Error loading config: {e}")
            raise
    
    def update_config(self, updates: Dict):
        """Update pipeline configuration."""
        try:
            # Get current config
            response = self.tables['config'].get_item(Key={'config_type': 'pipeline'})
            current_config = response.get('Item', self.config)
            
            # Update with new values
            for key, value in updates.items():
                if isinstance(value, dict) and key in current_config:
                    current_config[key].update(value)
                else:
                    current_config[key] = value
            
            # Save updated config
            self.tables['config'].put_item(Item=current_config)
            self.config = current_config
            
            print(f"Configuration updated: {updates}")
            
        except Exception as e:
            print(f"Error updating config: {e}")
            raise
    
    def process_market_data(self, event: Dict) -> Dict:
        """
        Process incoming market data.
        Lambda handler for market data processing.
        """
        try:
            start_time = time.time()
            
            # Parse market data
            market_data = self._parse_market_data(event)
            
            # Store raw data in S3 (cost-effective storage)
            self._store_raw_data(market_data)
            
            # Calculate features
            features = self._calculate_features(market_data)
            
            # Check if we should generate signal
            if self._should_generate_signal(market_data):
                # Trigger signal generation asynchronously
                self._invoke_signal_generation({
                    'symbol': market_data.symbol,
                    'timestamp': market_data.timestamp,
                    'features': features,
                    'market_data': market_data.to_dict()
                })
            
            # Update metrics
            processing_time = (time.time() - start_time) * 1000
            self._record_metric('market_data_processing', {
                'symbol': market_data.symbol,
                'processing_time_ms': processing_time,
                'data_size_bytes': len(json.dumps(event).encode())
            })
            
            # Track cost
            self.cost_tracker.record_lambda_invocation('process_market_data', 128, processing_time)
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'Market data processed',
                    'symbol': market_data.symbol,
                    'timestamp': market_data.timestamp,
                    'processing_time_ms': processing_time
                })
            }
            
        except Exception as e:
            print(f"Error processing market data: {e}")
            self.metrics['errors'] += 1
            self._record_error('process_market_data', str(e))
            
            return {
                'statusCode': 500,
                'body': json.dumps({'error': str(e)})
            }
    
    def _parse_market_data(self, event: Dict) -> MarketData:
        """Parse market data from event."""
        # Support different event formats
        if 'Records' in event:  # S3 event
            record = event['Records'][0]
            bucket = record['s3']['bucket']['name']
            key = record['s3']['object']['key']
            
            # Get data from S3
            response = s3_client.get_object(Bucket=bucket, Key=key)
            data = json.loads(response['Body'].read().decode('utf-8'))
            
        elif 'detail' in event:  # EventBridge event
            data = event['detail']
            
        else:  # Direct invocation
            data = event
        
        return MarketData.from_dict(data)
    
    def _store_raw_data(self, market_data: MarketData):
        """Store raw market data in S3 with compression for cost savings."""
        try:
            # Create partitioned path for cost optimization
            date = datetime.fromisoformat(market_data.timestamp.replace('Z', '+00:00'))
            year = date.year
            month = date.month
            day = date.day
            
            key = f"raw/{market_data.symbol}/{year}/{month:02d}/{day:02d}/{market_data.timestamp}.json.gz"
            
            # Compress data to save storage costs
            data_json = json.dumps(market_data.to_dict()).encode('utf-8')
            compressed_data = gzip.compress(data_json)
            
            # Store in S3 (cheapest storage class for historical data)
            s3_client.put_object(
                Bucket=DATA_BUCKET,
                Key=key,
                Body=compressed_data,
                StorageClass='STANDARD_IA',  # Infrequent Access for cost savings
                ContentEncoding='gzip',
                Metadata={
                    'symbol': market_data.symbol,
                    'timestamp': market_data.timestamp,
                    'interval': market_data.interval
                }
            )
            
            # Track data storage cost
            data_size_mb = len(compressed_data) / (1024 * 1024)
            self.cost_tracker.record_s3_storage(data_size_mb, 'STANDARD_IA')
            
        except Exception as e:
            print(f"Error storing raw data: {e}")
            raise
    
    def _calculate_features(self, market_data: MarketData) -> Dict[str, float]:
        """Calculate features from market data."""
        # Get historical data for feature calculation
        history = self._get_historical_data(market_data.symbol, market_data.timestamp, 20)
        
        if len(history) < 5:
            return {}
        
        # Calculate basic features
        closes = [h['close'] for h in history]
        volumes = [h['volume'] for h in history]
        
        # Simple moving averages
        sma_5 = sum(closes[-5:]) / 5 if len(closes) >= 5 else closes[-1]
        sma_10 = sum(closes[-10:]) / 10 if len(closes) >= 10 else closes[-1]
        
        # Volatility (standard deviation of returns)
        returns = [closes[i] / closes[i-1] - 1 for i in range(1, len(closes))]
        volatility = np.std(returns) if returns else 0
        
        # Volume features
        avg_volume = sum(volumes[-5:]) / 5 if len(volumes) >= 5 else volumes[-1]
        volume_ratio = market_data.volume / avg_volume if avg_volume > 0 else 1
        
        return {
            'price': market_data.close,
            'sma_5': sma_5,
            'sma_10': sma_10,
            'sma_ratio': sma_5 / sma_10 if sma_10 > 0 else 1,
            'volatility': volatility,
            'volume_ratio': volume_ratio,
            'returns_5min': (market_data.close / closes[-5] - 1) if len(closes) >= 5 else 0,
            'high_low_ratio': (market_data.high - market_data.low) / market_data.close if market_data.close > 0 else 0
        }
    
    def _get_historical_data(self, symbol: str, timestamp: str, lookback: int) -> List[Dict]:
        """Get historical market data from S3."""
        try:
            date = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            
            # Calculate start time
            start_date = date - timedelta(minutes=lookback * 5)  # Assume 5-minute intervals
            
            # Build S3 prefix for querying
            prefix = f"raw/{symbol}/{start_date.year}/{start_date.month:02d}/{start_date.day:02d}/"
            
            # List objects in S3 (in production, would use Athena or Glue for querying)
            response = s3_client.list_objects_v2(
                Bucket=DATA_BUCKET,
                Prefix=prefix,
                MaxKeys=lookback
            )
            
            historical_data = []
            
            if 'Contents' in response:
                for obj in response['Contents']:
                    # Get object
                    data_obj = s3_client.get_object(Bucket=DATA_BUCKET, Key=obj['Key'])
                    
                    # Decompress and parse
                    compressed_data = data_obj['Body'].read()
                    decompressed_data = gzip.decompress(compressed_data)
                    data = json.loads(decompressed_data.decode('utf-8'))
                    
                    historical_data.append(data)
            
            # Sort by timestamp
            historical_data.sort(key=lambda x: x['timestamp'])
            
            return historical_data[-lookback:]  # Return most recent data
            
        except Exception as e:
            print(f"Error getting historical data: {e}")
            return []
    
    def _should_generate_signal(self, market_data: MarketData) -> bool:
        """Determine if we should generate a trading signal."""
        # Check if trading is enabled
        if not self.config.get('enabled', True):
            return False
        
        # Check trading hours
        if not self._is_within_trading_hours(market_data.timestamp):
            return False
        
        # Check if we have enough data
        # (In production, would check for data completeness and quality)
        
        # Throttle signals to control costs
        # Generate signal every 5 minutes for each symbol
        signal_key = f"last_signal_{market_data.symbol}"
        
        try:
            response = self.tables['state'].get_item(Key={'key': signal_key})
            
            if 'Item' in response:
                last_signal_time = datetime.fromisoformat(response['Item']['value'].replace('Z', '+00:00'))
                current_time = datetime.fromisoformat(market_data.timestamp.replace('Z', '+00:00'))
                
                # Only generate signal if 5 minutes have passed
                if (current_time - last_signal_time).total_seconds() < 300:
                    return False
            
            # Update last signal time
            self.tables['state'].put_item(Item={
                'key': signal_key,
                'value': market_data.timestamp,
                'updated_at': datetime.utcnow().isoformat()
            })
            
            return True
            
        except Exception as e:
            print(f"Error checking signal generation: {e}")
            return False
    
    def _is_within_trading_hours(self, timestamp: str) -> bool:
        """Check if timestamp is within trading hours."""
        try:
            # Parse timestamp
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            
            # Get trading hours config
            trading_hours = self.config.get('trading_hours', {})
            start_time = trading_hours.get('start', '09:30')
            end_time = trading_hours.get('end', '16:00')
            
            # Parse times
            start_hour, start_minute = map(int, start_time.split(':'))
            end_hour, end_minute = map(int, end_time.split(':'))
            
            # Check if weekday (Monday=0, Friday=4)
            if dt.weekday() > 4:  # Saturday or Sunday
                return False
            
            # Check time
            current_time = dt.time()
            start_time_obj = datetime.strptime(start_time, '%H:%M').time()
            end_time_obj = datetime.strptime(end_time, '%H:%M').time()
            
            return start_time_obj <= current_time <= end_time_obj
            
        except Exception as e:
            print(f"Error checking trading hours: {e}")
            return True  # Default to allowing if check fails
    
    def _invoke_signal_generation(self, event: Dict):
        """Invoke signal generation Lambda asynchronously."""
        try:
            # Use EventBridge to decouple and for retry capabilities
            eventbridge.put_events(
                Entries=[{
                    'Source': 'trading.pipeline',
                    'DetailType': 'signal.generation',
                    'Detail': json.dumps(event),
                    'EventBusName': 'default'
                }]
            )
            
            print(f"Triggered signal generation for {event['symbol']}")
            
        except Exception as e:
            print(f"Error invoking signal generation: {e}")
            raise
    
    def generate_trading_signal(self, event: Dict) -> Dict:
        """
        Generate trading signal using ML model.
        Lambda handler for signal generation.
        """
        try:
            start_time = time.time()
            
            # Parse event
            symbol = event['symbol']
            timestamp = event['timestamp']
            features = event['features']
            market_data = event['market_data']
            
            # Load ML model from S3
            model = self._load_model(symbol)
            
            if model is None:
                return {
                    'statusCode': 404,
                    'body': json.dumps({'error': f'No model found for {symbol}'})
                }
            
            # Generate prediction
            signal, confidence = self._predict_with_model(model, features)
            
            # Create trading signal
            trading_signal = TradingSignal(
                signal_id=f"signal_{int(time.time())}_{hashlib.md5(symbol.encode()).hexdigest()[:8]}",
                timestamp=timestamp,
                symbol=symbol,
                signal=signal,
                confidence=confidence,
                price=market_data['close'],
                features=features,
                model_version=model.get('version', '1.0')
            )
            
            # Store signal
            self._store_signal(trading_signal)
            
            # Check risk limits before creating order
            if self._check_risk_limits(symbol, trading_signal):
                # Trigger order generation
                self._invoke_order_generation(trading_signal.to_dict())
            
            # Update metrics
            processing_time = (time.time() - start_time) * 1000
            self._record_metric('signal_generation', {
                'symbol': symbol,
                'signal': signal,
                'confidence': confidence,
                'processing_time_ms': processing_time,
                'model_version': model.get('version', '1.0')
            })
            
            self.metrics['signals_generated'] += 1
            
            # Track cost
            self.cost_tracker.record_lambda_invocation('generate_trading_signal', 1024, processing_time)
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'Signal generated',
                    'signal': trading_signal.to_dict(),
                    'processing_time_ms': processing_time
                })
            }
            
        except Exception as e:
            print(f"Error generating trading signal: {e}")
            self.metrics['errors'] += 1
            self._record_error('generate_trading_signal', str(e))
            
            return {
                'statusCode': 500,
                'body': json.dumps({'error': str(e)})
            }
    
    def _load_model(self, symbol: str) -> Optional[Dict]:
        """Load ML model from S3."""
        try:
            # Check for latest model version
            model_key = f"models/{symbol}/latest/model.json"
            
            try:
                response = s3_client.get_object(Bucket=MODEL_BUCKET, Key=model_key)
                model_data = json.loads(response['Body'].read().decode('utf-8'))
                
                # For demo, return a simple model
                # In production, would load actual ML model
                return {
                    'symbol': symbol,
                    'version': model_data.get('version', '1.0'),
                    'created_at': model_data.get('created_at'),
                    'performance': model_data.get('performance', {})
                }
                
            except s3_client.exceptions.NoSuchKey:
                # Try to find any model for this symbol
                response = s3_client.list_objects_v2(
                    Bucket=MODEL_BUCKET,
                    Prefix=f"models/{symbol}/",
                    MaxKeys=1
                )
                
                if 'Contents' in response:
                    latest_model = response['Contents'][0]
                    model_response = s3_client.get_object(
                        Bucket=MODEL_BUCKET,
                        Key=latest_model['Key']
                    )
                    model_data = json.loads(model_response['Body'].read().decode('utf-8'))
                    
                    return {
                        'symbol': symbol,
                        'version': model_data.get('version', '1.0'),
                        'created_at': model_data.get('created_at'),
                        'performance': model_data.get('performance', {})
                    }
                
                return None
                
        except Exception as e:
            print(f"Error loading model: {e}")
            return None
    
    def _predict_with_model(self, model: Dict, features: Dict) -> tuple:
        """Generate prediction using model."""
        # For demo, use simple rule-based logic
        # In production, would use actual ML model inference
        
        sma_ratio = features.get('sma_ratio', 1)
        volatility = features.get('volatility', 0)
        volume_ratio = features.get('volume_ratio', 1)
        
        # Simple moving average crossover strategy
        if sma_ratio > 1.02 and volume_ratio > 1.5:  # Bullish
            return "BUY", 0.7
        elif sma_ratio < 0.98 and volume_ratio > 1.5:  # Bearish
            return "SELL", 0.7
        else:
            return "HOLD", 0.5
    
    def _store_signal(self, signal: TradingSignal):
        """Store trading signal in DynamoDB."""
        try:
            # Store in DynamoDB
            item = signal.to_dict()
            item['signal_id'] = signal.signal_id  # Primary key
            item['timestamp'] = signal.timestamp
            item['ttl'] = int(time.time()) + (7 * 24 * 3600)  # 7 day TTL
            
            self.tables['state'].put_item(Item=item)
            
            # Also store in S3 for historical analysis
            date = datetime.fromisoformat(signal.timestamp.replace('Z', '+00:00'))
            key = f"signals/{signal.symbol}/{date.year}/{date.month:02d}/{date.day:02d}/{signal.signal_id}.json"
            
            s3_client.put_object(
                Bucket=DATA_BUCKET,
                Key=key,
                Body=json.dumps(item, cls=DecimalEncoder),
                StorageClass='STANDARD_IA'
            )
            
        except Exception as e:
            print(f"Error storing signal: {e}")
            raise
    
    def _check_risk_limits(self, symbol: str, signal: TradingSignal) -> bool:
        """Check risk limits before creating order."""
        try:
            risk_limits = self.config.get('risk_limits', {})
            
            # Get current positions
            positions = self._get_positions()
            
            # Calculate current exposure
            total_exposure = sum(abs(p['quantity'] * p['avg_price']) for p in positions)
            
            # Check max position size
            max_position_size = risk_limits.get('max_position_size', 10000)
            if total_exposure >= max_position_size:
                print(f"Risk limit: Max position size reached ({total_exposure} >= {max_position_size})")
                return False
            
            # Check daily loss
            daily_pnl = self._get_daily_pnl()
            max_daily_loss = risk_limits.get('max_daily_loss', -5000)
            if daily_pnl <= max_daily_loss:
                print(f"Risk limit: Max daily loss reached ({daily_pnl} <= {max_daily_loss})")
                return False
            
            # Symbol-specific checks
            symbol_position = next((p for p in positions if p['symbol'] == symbol), None)
            if symbol_position:
                # Check concentration limit
                concentration = abs(symbol_position['quantity'] * symbol_position['avg_price']) / total_exposure
                if concentration > 0.3:  # 30% concentration limit
                    print(f"Risk limit: Concentration limit reached ({concentration:.2%})")
                    return False
            
            # Check signal confidence
            min_confidence = 0.6  # Minimum confidence threshold
            if signal.confidence < min_confidence:
                print(f"Risk limit: Signal confidence too low ({signal.confidence} < {min_confidence})")
                return False
            
            return True
            
        except Exception as e:
            print(f"Error checking risk limits: {e}")
            return False
    
    def _get_positions(self) -> List[Dict]:
        """Get current positions from DynamoDB."""
        try:
            response = self.tables['state'].query(
                KeyConditionExpression='begins_with(#key, :prefix)',
                ExpressionAttributeNames={'#key': 'key'},
                ExpressionAttributeValues={':prefix': 'position_'}
            )
            
            positions = []
            for item in response.get('Items', []):
                if 'position' in item:
                    positions.append(item['position'])
            
            return positions
            
        except Exception as e:
            print(f"Error getting positions: {e}")
            return []
    
    def _get_daily_pnl(self) -> float:
        """Get daily P&L from DynamoDB."""
        try:
            today = datetime.utcnow().date().isoformat()
            response = self.tables['metrics'].get_item(
                Key={'metric_date': today, 'metric_type': 'daily_pnl'}
            )
            
            if 'Item' in response:
                return float(response['Item'].get('value', 0))
            
            return 0.0
            
        except Exception as e:
            print(f"Error getting daily P&L: {e}")
            return 0.0
    
    def _invoke_order_generation(self, signal: Dict):
        """Invoke order generation Lambda."""
        try:
            # Use Step Functions for stateful workflow with error handling
            stepfunctions.start_execution(
                stateMachineArn=os.environ.get('ORDER_WORKFLOW_ARN'),
                name=f"order-{signal['signal_id']}",
                input=json.dumps({
                    'signal': signal,
                    'timestamp': datetime.utcnow().isoformat()
                })
            )
            
            print(f"Started order workflow for signal {signal['signal_id']}")
            
        except Exception as e:
            print(f"Error invoking order generation: {e}")
            # Fall back to direct Lambda invocation
            lambda_client.invoke(
                FunctionName=os.environ.get('ORDER_GENERATION_FUNCTION'),
                InvocationType='Event',  # Asynchronous
                Payload=json.dumps(signal).encode('utf-8')
            )
    
    def create_order(self, event: Dict) -> Dict:
        """
        Create trading order.
        Lambda handler for order creation.
        """
        try:
            start_time = time.time()
            
            # Parse signal from event
            if 'signal' in event:
                signal = TradingSignal.from_dict(event['signal'])
            else:
                signal = TradingSignal.from_dict(event)
            
            # Calculate order parameters
            order = self._calculate_order_parameters(signal)
            
            # Store order
            self._store_order(order)
            
            # Simulate order execution (in production, would call broker API)
            execution_result = self._simulate_order_execution(order)
            
            # Update position
            self._update_position(order, execution_result)
            
            # Update metrics
            processing_time = (time.time() - start_time) * 1000
            self._record_metric('order_creation', {
                'order_id': order.order_id,
                'symbol': order.symbol,
                'side': order.side,
                'quantity': order.quantity,
                'processing_time_ms': processing_time
            })
            
            self.metrics['orders_executed'] += 1
            
            # Track cost
            self.cost_tracker.record_lambda_invocation('create_order', 512, processing_time)
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'Order created and executed',
                    'order': order.to_dict(),
                    'execution': execution_result,
                    'processing_time_ms': processing_time
                })
            }
            
        except Exception as e:
            print(f"Error creating order: {e}")
            self.metrics['errors'] += 1
            self._record_error('create_order', str(e))
            
            return {
                'statusCode': 500,
                'body': json.dumps({'error': str(e)})
            }
    
    def _calculate_order_parameters(self, signal: TradingSignal) -> OrderRequest:
        """Calculate order parameters based on signal and risk limits."""
        # Get account balance
        account_balance = self._get_account_balance()
        
        # Calculate position size (2% risk per trade)
        risk_per_trade = 0.02
        risk_amount = account_balance * risk_per_trade
        
        # Calculate quantity based on risk and volatility
        volatility = signal.features.get('volatility', 0.02)
        stop_loss_pct = 0.03  # 3% stop loss
        
        # Position size formula: risk_amount / (price * stop_loss_pct)
        quantity = risk_amount / (signal.price * stop_loss_pct)
        
        # Round to whole shares
        quantity = max(1, int(quantity))
        
        # Cap at max position size
        max_shares = 1000
        quantity = min(quantity, max_shares)
        
        return OrderRequest(
            order_id=f"order_{int(time.time())}_{hashlib.md5(signal.symbol.encode()).hexdigest()[:8]}",
            timestamp=datetime.utcnow().isoformat(),
            symbol=signal.symbol,
            side=signal.signal,
            quantity=quantity,
            order_type="MARKET",
            signal_id=signal.signal_id,
            strategy_id="serverless_pipeline"
        )
    
    def _get_account_balance(self) -> float:
        """Get account balance from DynamoDB."""
        try:
            response = self.tables['state'].get_item(Key={'key': 'account_balance'})
            
            if 'Item' in response:
                return float(response['Item'].get('value', 100000))
            
            # Default balance
            return 100000.0
            
        except Exception as e:
            print(f"Error getting account balance: {e}")
            return 100000.0
    
    def _store_order(self, order: OrderRequest):
        """Store order in DynamoDB."""
        try:
            item = order.to_dict()
            item['key'] = f"order_{order.order_id}"
            item['created_at'] = datetime.utcnow().isoformat()
            item['status'] = 'CREATED'
            item['ttl'] = int(time.time()) + (30 * 24 * 3600)  # 30 day TTL
            
            self.tables['state'].put_item(Item=item)
            
            # Also store in S3 for audit trail
            date = datetime.fromisoformat(order.timestamp.replace('Z', '+00:00'))
            key = f"orders/{order.symbol}/{date.year}/{date.month:02d}/{date.day:02d}/{order.order_id}.json"
            
            s3_client.put_object(
                Bucket=DATA_BUCKET,
                Key=key,
                Body=json.dumps(item, cls=DecimalEncoder),
                StorageClass='GLACIER_IR'  # Instant Retrieval for audit data
            )
            
        except Exception as e:
            print(f"Error storing order: {e}")
            raise
    
    def _simulate_order_execution(self, order: OrderRequest) -> Dict:
        """Simulate order execution."""
        # In production, would call actual broker API
        # For demo, simulate execution with random price improvement
        
        import random
        
        # Simulate execution price
        if order.side == "BUY":
            # Buy at slightly higher price
            execution_price = order.price * (1 + random.uniform(0.0001, 0.001)) if order.price else 100.0
        else:
            # Sell at slightly lower price
            execution_price = order.price * (1 - random.uniform(0.0001, 0.001)) if order.price else 100.0
        
        # Simulate commission
        commission = max(1.0, order.quantity * execution_price * 0.0001)  # 0.01% or $1 minimum
        
        return {
            'execution_id': f"exec_{int(time.time())}",
            'order_id': order.order_id,
            'symbol': order.symbol,
            'side': order.side,
            'quantity': order.quantity,
            'price': execution_price,
            'commission': commission,
            'executed_at': datetime.utcnow().isoformat()
        }
    
    def _update_position(self, order: OrderRequest, execution: Dict):
        """Update position after order execution."""
        try:
            position_key = f"position_{order.symbol}"
            
            # Get current position
            response = self.tables['state'].get_item(Key={'key': position_key})
            
            if 'Item' in response and 'position' in response['Item']:
                current_position = Position.from_dict(response['Item']['position'])
                
                # Update position
                if order.side == "BUY":
                    new_quantity = current_position.quantity + order.quantity
                    new_avg_price = (
                        (current_position.quantity * current_position.avg_price) +
                        (order.quantity * execution['price'])
                    ) / new_quantity
                    
                    # Update unrealized P&L (simplified)
                    current_price = execution['price']  # For demo, use execution price
                    unrealized_pnl = (current_price - new_avg_price) * new_quantity
                    
                    updated_position = Position(
                        account_id=current_position.account_id,
                        symbol=order.symbol,
                        quantity=new_quantity,
                        avg_price=new_avg_price,
                        unrealized_pnl=unrealized_pnl,
                        realized_pnl=current_position.realized_pnl,
                        last_updated=datetime.utcnow().isoformat()
                    )
                    
                else:  # SELL
                    new_quantity = current_position.quantity - order.quantity
                    
                    # Calculate realized P&L
                    realized_pnl = (execution['price'] - current_position.avg_price) * order.quantity
                    realized_pnl -= execution['commission']  # Subtract commission
                    
                    if new_quantity <= 0:
                        # Position closed
                        self.tables['state'].delete_item(Key={'key': position_key})
                        
                        # Update daily P&L
                        self._update_daily_pnl(realized_pnl)
                        
                        return
                    
                    # Update position
                    updated_position = Position(
                        account_id=current_position.account_id,
                        symbol=order.symbol,
                        quantity=new_quantity,
                        avg_price=current_position.avg_price,  # Keep same avg price for remaining
                        unrealized_pnl=0,  # Reset for remaining position
                        realized_pnl=current_position.realized_pnl + realized_pnl,
                        last_updated=datetime.utcnow().isoformat()
                    )
            else:
                # New position
                updated_position = Position(
                    account_id="default",
                    symbol=order.symbol,
                    quantity=order.quantity,
                    avg_price=execution['price'],
                    unrealized_pnl=0,
                    realized_pnl=0,
                    last_updated=datetime.utcnow().isoformat()
                )
            
            # Store updated position
            self.tables['state'].put_item(Item={
                'key': position_key,
                'position': updated_position.to_dict(),
                'updated_at': datetime.utcnow().isoformat()
            })
            
            # Update daily P&L for realized gains
            if order.side == "SELL":
                self._update_daily_pnl(updated_position.realized_pnl)
            
        except Exception as e:
            print(f"Error updating position: {e}")
            raise
    
    def _update_daily_pnl(self, pnl: float):
        """Update daily P&L in metrics table."""
        try:
            today = datetime.utcnow().date().isoformat()
            
            # Use update_item with atomic increment
            self.tables['metrics'].update_item(
                Key={
                    'metric_date': today,
                    'metric_type': 'daily_pnl'
                },
                UpdateExpression='ADD #value :pnl',
                ExpressionAttributeNames={'#value': 'value'},
                ExpressionAttributeValues={':pnl': Decimal(str(pnl))},
                ReturnValues='UPDATED_NEW'
            )
            
        except Exception as e:
            print(f"Error updating daily P&L: {e}")
    
    def _record_metric(self, metric_type: str, data: Dict):
        """Record performance metric."""
        try:
            timestamp = datetime.utcnow().isoformat()
            metric_id = f"{metric_type}_{int(time.time())}"
            
            item = {
                'metric_date': datetime.utcnow().date().isoformat(),
                'metric_type': metric_type,
                'metric_id': metric_id,
                'timestamp': timestamp,
                'data': data,
                'ttl': int(time.time()) + (30 * 24 * 3600)  # 30 day TTL
            }
            
            self.tables['metrics'].put_item(Item=item)
            
            # Also publish to CloudWatch for monitoring
            self._publish_cloudwatch_metric(metric_type, data)
            
        except Exception as e:
            print(f"Error recording metric: {e}")
    
    def _publish_cloudwatch_metric(self, metric_type: str, data: Dict):
        """Publish metric to CloudWatch."""
        try:
            namespace = 'TradingPipeline'
            
            # Extract relevant metrics
            dimensions = []
            
            if 'symbol' in data:
                dimensions.append({'Name': 'Symbol', 'Value': data['symbol']})
            
            if 'processing_time_ms' in data:
                cloudwatch.put_metric_data(
                    Namespace=namespace,
                    MetricData=[{
                        'MetricName': 'ProcessingTime',
                        'Dimensions': dimensions,
                        'Value': data['processing_time_ms'],
                        'Unit': 'Milliseconds',
                        'Timestamp': datetime.utcnow()
                    }]
                )
            
            if 'signal' in data:
                signal_value = 1 if data['signal'] == 'BUY' else (-1 if data['signal'] == 'SELL' else 0)
                cloudwatch.put_metric_data(
                    Namespace=namespace,
                    MetricData=[{
                        'MetricName': 'TradingSignal',
                        'Dimensions': dimensions,
                        'Value': signal_value,
                        'Unit': 'Count',
                        'Timestamp': datetime.utcnow()
                    }]
                )
            
        except Exception as e:
            print(f"Error publishing CloudWatch metric: {e}")
    
    def _record_error(self, function_name: str, error: str):
        """Record error in metrics table."""
        try:
            item = {
                'metric_date': datetime.utcnow().date().isoformat(),
                'metric_type': 'error',
                'metric_id': f"error_{int(time.time())}",
                'timestamp': datetime.utcnow().isoformat(),
                'data': {
                    'function': function_name,
                    'error': error[:500]  # Truncate long errors
                },
                'ttl': int(time.time()) + (7 * 24 * 3600)  # 7 day TTL
            }
            
            self.tables['metrics'].put_item(Item=item)
            
            # Publish to CloudWatch for alerting
            cloudwatch.put_metric_data(
                Namespace='TradingPipeline',
                MetricData=[{
                    'MetricName': 'ErrorCount',
                    'Dimensions': [{'Name': 'Function', 'Value': function_name}],
                    'Value': 1,
                    'Unit': 'Count',
                    'Timestamp': datetime.utcnow()
                }]
            )
            
        except Exception as e:
            print(f"Error recording error: {e}")
    
    def monitor_performance(self) -> Dict:
        """
        Monitor pipeline performance and costs.
        Lambda handler for performance monitoring.
        """
        try:
            # Calculate performance metrics
            performance = self._calculate_performance_metrics()
            
            # Calculate costs
            costs = self.cost_tracker.calculate_daily_costs()
            
            # Check against limits
            alerts = self._check_limits(performance, costs)
            
            # Generate report
            report = self._generate_performance_report(performance, costs, alerts)
            
            # Store report
            self._store_performance_report(report)
            
            # Send alerts if needed
            if alerts:
                self._send_alerts(alerts)
            
            return {
                'statusCode': 200,
                'body': json.dumps(report)
            }
            
        except Exception as e:
            print(f"Error monitoring performance: {e}")
            return {
                'statusCode': 500,
                'body': json.dumps({'error': str(e)})
            }
    
    def _calculate_performance_metrics(self) -> Dict:
        """Calculate performance metrics."""
        try:
            today = datetime.utcnow().date().isoformat()
            
            # Get today's metrics
            response = self.tables['metrics'].query(
                KeyConditionExpression='metric_date = :date AND begins_with(metric_type, :prefix)',
                ExpressionAttributeValues={
                    ':date': today,
                    ':prefix': 'market_data_processing'
                }
            )
            
            processing_times = []
            for item in response.get('Items', []):
                if 'processing_time_ms' in item.get('data', {}):
                    processing_times.append(item['data']['processing_time_ms'])
            
            # Calculate statistics
            avg_processing_time = statistics.mean(processing_times) if processing_times else 0
            p95_processing_time = np.percentile(processing_times, 95) if processing_times else 0
            
            # Count signals and orders
            signals_response = self.tables['metrics'].query(
                KeyConditionExpression='metric_date = :date AND metric_type = :type',
                ExpressionAttributeValues={
                    ':date': today,
                    ':type': 'signal_generation'
                }
            )
            
            orders_response = self.tables['metrics'].query(
                KeyConditionExpression='metric_date = :date AND metric_type = :type',
                ExpressionAttributeValues={
                    ':date': today,
                    ':type': 'order_creation'
                }
            )
            
            signals_count = len(signals_response.get('Items', []))
            orders_count = len(orders_response.get('Items', []))
            
            # Calculate error rate
            errors_response = self.tables['metrics'].query(
                KeyConditionExpression='metric_date = :date AND metric_type = :type',
                ExpressionAttributeValues={
                    ':date': today,
                    ':type': 'error'
                }
            )
            
            errors_count = len(errors_response.get('Items', []))
            total_operations = signals_count + orders_count + (len(processing_times) or 1)
            error_rate = errors_count / total_operations if total_operations > 0 else 0
            
            return {
                'date': today,
                'throughput': {
                    'signals_per_hour': signals_count / 24,
                    'orders_per_hour': orders_count / 24,
                    'total_operations': total_operations
                },
                'latency': {
                    'avg_processing_time_ms': avg_processing_time,
                    'p95_processing_time_ms': p95_processing_time
                },
                'reliability': {
                    'error_rate': error_rate,
                    'error_count': errors_count
                },
                'trading': {
                    'signals_generated': signals_count,
                    'orders_executed': orders_count,
                    'daily_pnl': self._get_daily_pnl()
                }
            }
            
        except Exception as e:
            print(f"Error calculating performance metrics: {e}")
            return {}
    
    def _check_limits(self, performance: Dict, costs: Dict) -> List[Dict]:
        """Check performance and cost against limits."""
        alerts = []
        
        # Check performance limits
        perf_targets = self.config.get('performance_targets', {})
        
        latency = performance.get('latency', {}).get('p95_processing_time_ms', 0)
        max_latency = perf_targets.get('max_latency_ms', 1000)
        
        if latency > max_latency:
            alerts.append({
                'type': 'performance',
                'severity': 'WARNING',
                'message': f'Latency exceeded: {latency:.0f}ms > {max_latency}ms',
                'metric': 'latency',
                'value': latency,
                'threshold': max_latency
            })
        
        error_rate = performance.get('reliability', {}).get('error_rate', 0)
        error_threshold = perf_targets.get('error_rate_threshold', 0.01)
        
        if error_rate > error_threshold:
            alerts.append({
                'type': 'performance',
                'severity': 'ERROR',
                'message': f'Error rate exceeded: {error_rate:.2%} > {error_threshold:.2%}',
                'metric': 'error_rate',
                'value': error_rate,
                'threshold': error_threshold
            })
        
        # Check cost limits
        cost_limits = self.config.get('cost_limits', {})
        
        lambda_cost = costs.get('lambda', 0)
        max_lambda_cost = cost_limits.get('max_daily_lambda_cost', 10.0)
        
        if lambda_cost > max_lambda_cost:
            alerts.append({
                'type': 'cost',
                'severity': 'ERROR',
                'message': f'Lambda cost exceeded: ${lambda_cost:.2f} > ${max_lambda_cost:.2f}',
                'metric': 'lambda_cost',
                'value': lambda_cost,
                'threshold': max_lambda_cost
            })
        
        # Check alert thresholds (80% of limit)
        alert_threshold = cost_limits.get('alert_threshold', 0.8)
        
        if lambda_cost > max_lambda_cost * alert_threshold:
            alerts.append({
                'type': 'cost',
                'severity': 'WARNING',
                'message': f'Lambda cost approaching limit: ${lambda_cost:.2f} > ${max_lambda_cost * alert_threshold:.2f}',
                'metric': 'lambda_cost',
                'value': lambda_cost,
                'threshold': max_lambda_cost * alert_threshold
            })
        
        return alerts
    
    def _generate_performance_report(self, performance: Dict, costs: Dict, alerts: List[Dict]) -> Dict:
        """Generate performance report."""
        return {
            'report_id': f"report_{int(time.time())}",
            'date': datetime.utcnow().isoformat(),
            'performance': performance,
            'costs': costs,
            'alerts': alerts,
            'summary': {
                'status': 'HEALTHY' if not alerts else 'DEGRADED',
                'alert_count': len(alerts),
                'total_cost_today': sum(costs.values()),
                'operations_today': performance.get('throughput', {}).get('total_operations', 0)
            }
        }
    
    def _store_performance_report(self, report: Dict):
        """Store performance report in S3."""
        try:
            date = datetime.fromisoformat(report['date'].replace('Z', '+00:00'))
            key = f"reports/{date.year}/{date.month:02d}/{date.day:02d}/{report['report_id']}.json"
            
            s3_client.put_object(
                Bucket=DATA_BUCKET,
                Key=key,
                Body=json.dumps(report, cls=DecimalEncoder, indent=2),
                ContentType='application/json'
            )
            
        except Exception as e:
            print(f"Error storing performance report: {e}")
    
    def _send_alerts(self, alerts: List[Dict]):
        """Send alerts via SNS."""
        try:
            # Group alerts by severity
            critical_alerts = [a for a in alerts if a['severity'] == 'ERROR']
            warning_alerts = [a for a in alerts if a['severity'] == 'WARNING']
            
            if critical_alerts:
                message = {
                    'subject': f'CRITICAL: Trading Pipeline Alerts ({len(critical_alerts)} critical)',
                    'body': json.dumps(critical_alerts, indent=2)
                }
                self._publish_sns_alert(message)
            
            if warning_alerts:
                message = {
                    'subject': f'WARNING: Trading Pipeline Alerts ({len(warning_alerts)} warnings)',
                    'body': json.dumps(warning_alerts, indent=2)
                }
                self._publish_sns_alert(message)
                
        except Exception as e:
            print(f"Error sending alerts: {e}")
    
    def _publish_sns_alert(self, message: Dict):
        """Publish alert to SNS topic."""
        try:
            sns = boto3.client('sns')
            topic_arn = os.environ.get('ALERT_SNS_TOPIC')
            
            if topic_arn:
                sns.publish(
                    TopicArn=topic_arn,
                    Subject=message['subject'],
                    Message=message['body']
                )
        except Exception as e:
            print(f"Error publishing SNS alert: {e}")
    
    def deploy_pipeline(self) -> Dict:
        """
        Deploy the serverless pipeline.
        Creates all required AWS resources.
        """
        try:
            # This would be called from a deployment script or CI/CD pipeline
            # For demo, just return success
            
            deployment_id = f"deploy_{int(time.time())}"
            
            # In production, would:
            # 1. Create CloudFormation stack
            # 2. Deploy Lambda functions
            # 3. Configure EventBridge rules
            # 4. Set up monitoring
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'deployment_id': deployment_id,
                    'status': 'SUCCESS',
                    'message': 'Pipeline deployed successfully',
                    'resources': {
                        'lambda_functions': [
                            'market-data-processor',
                            'signal-generator',
                            'order-creator',
                            'performance-monitor'
                        ],
                        'storage': {
                            's3_buckets': [MODEL_BUCKET, DATA_BUCKET],
                            'dynamodb_tables': [STATE_TABLE, METRICS_TABLE, CONFIG_TABLE]
                        },
                        'monitoring': [
                            'CloudWatch alarms',
                            'SNS topics',
                            'Cost Explorer dashboards'
                        ]
                    }
                })
            }
            
        except Exception as e:
            print(f"Error deploying pipeline: {e}")
            return {
                'statusCode': 500,
                'body': json.dumps({'error': str(e)})
            }


class CostTracker:
    """
    Track and estimate costs for serverless trading pipeline.
    """
    
    # AWS Pricing (us-east-1, as of 2024)
    # These are example prices, actual prices may vary
    PRICING = {
        'lambda': {
            'price_per_gb_second': 0.0000166667,  # $0.0000166667 per GB-second
            'price_per_request': 0.0000002,       # $0.0000002 per request
            'free_tier': {
                'requests': 1000000,
                'compute': 400000  # GB-seconds
            }
        },
        's3': {
            'standard': 0.023,  # $0.023 per GB-month
            'standard_ia': 0.0125,  # $0.0125 per GB-month
            'glacier_ir': 0.004,  # $0.004 per GB-month
            'requests': {
                'put': 0.000005,  # $0.000005 per 1000 requests
                'get': 0.0000004, # $0.0000004 per 1000 requests
            }
        },
        'dynamodb': {
            'write': 0.00000125,  # $0.00000125 per WCU
            'read': 0.00000025,   # $0.00000025 per RCU
            'storage': 0.25,      # $0.25 per GB-month
        },
        'eventbridge': {
            'events': 1.00,  # $1.00 per million events
        },
        'cloudwatch': {
            'metrics': 0.30,  # $0.30 per metric per month
            'alarms': 0.10,   # $0.10 per alarm per month
            'logs': 0.50,     # $0.50 per GB ingested
        }
    }
    
    def __init__(self):
        self.daily_usage = {
            'lambda': {
                'invocations': 0,
                'compute_gb_seconds': 0,
                'cost': 0.0
            },
            's3': {
                'storage_gb': 0,
                'put_requests': 0,
                'get_requests': 0,
                'cost': 0.0
            },
            'dynamodb': {
                'write_units': 0,
                'read_units': 0,
                'storage_gb': 0,
                'cost': 0.0
            },
            'eventbridge': {
                'events': 0,
                'cost': 0.0
            },
            'cloudwatch': {
                'metrics': 0,
                'alarms': 0,
                'log_gb': 0,
                'cost': 0.0
            }
        }
        
        self.monthly_total = 0.0
    
    def record_lambda_invocation(self, function_name: str, memory_mb: int, duration_ms: float):
        """Record Lambda function invocation."""
        gb_seconds = (memory_mb / 1024) * (duration_ms / 1000)
        
        self.daily_usage['lambda']['invocations'] += 1
        self.daily_usage['lambda']['compute_gb_seconds'] += gb_seconds
        
        # Calculate cost (simplified)
        invocation_cost = self.PRICING['lambda']['price_per_request']
        compute_cost = gb_seconds * self.PRICING['lambda']['price_per_gb_second']
        
        self.daily_usage['lambda']['cost'] += invocation_cost + compute_cost
    
    def record_s3_storage(self, size_mb: float, storage_class: str = 'standard'):
        """Record S3 storage usage."""
        size_gb = size_mb / 1024
        
        if storage_class == 'standard':
            price_per_gb = self.PRICING['s3']['standard']
        elif storage_class == 'standard_ia':
            price_per_gb = self.PRICING['s3']['standard_ia']
        elif storage_class == 'glacier_ir':
            price_per_gb = self.PRICING['s3']['glacier_ir']
        else:
            price_per_gb = self.PRICING['s3']['standard']
        
        # Daily cost (approximate)
        daily_cost = (size_gb * price_per_gb) / 30
        
        self.daily_usage['s3']['storage_gb'] += size_gb
        self.daily_usage['s3']['cost'] += daily_cost
    
    def record_s3_request(self, request_type: str, count: int = 1):
        """Record S3 request."""
        if request_type == 'put':
            self.daily_usage['s3']['put_requests'] += count
            cost = count * self.PRICING['s3']['requests']['put']
        elif request_type == 'get':
            self.daily_usage['s3']['get_requests'] += count
            cost = count * self.PRICING['s3']['requests']['get']
        else:
            return
        
        self.daily_usage['s3']['cost'] += cost
    
    def record_dynamodb_write(self, wcus: int = 1):
        """Record DynamoDB write operation."""
        self.daily_usage['dynamodb']['write_units'] += wcus
        self.daily_usage['dynamodb']['cost'] += wcus * self.PRICING['dynamodb']['write']
    
    def record_dynamodb_read(self, rcus: int = 1):
        """Record DynamoDB read operation."""
        self.daily_usage['dynamodb']['read_units'] += rcus
        self.daily_usage['dynamodb']['cost'] += rcus * self.PRICING['dynamodb']['read']
    
    def record_eventbridge_event(self, count: int = 1):
        """Record EventBridge event."""
        self.daily_usage['eventbridge']['events'] += count
        self.daily_usage['eventbridge']['cost'] += count * (self.PRICING['eventbridge']['events'] / 1000000)
    
    def calculate_daily_costs(self) -> Dict:
        """Calculate total daily costs."""
        # Sum up all costs
        total_cost = sum(service['cost'] for service in self.daily_usage.values())
        
        return {
            'lambda': self.daily_usage['lambda']['cost'],
            's3': self.daily_usage['s3']['cost'],
            'dynamodb': self.daily_usage['dynamodb']['cost'],
            'eventbridge': self.daily_usage['eventbridge']['cost'],
            'cloudwatch': self.daily_usage['cloudwatch']['cost'],
            'total': total_cost
        }
    
    def estimate_monthly_cost(self, daily_volume: Dict) -> Dict:
        """
        Estimate monthly costs based on expected daily volume.
        
        Args:
            daily_volume: Dictionary with expected daily volumes
                Example: {
                    'market_data_events': 10000,
                    'signals': 1000,
                    'orders': 100,
                    'data_storage_gb': 10,
                    'position_updates': 1000
                }
        """
        # Calculate costs based on volume
        monthly_costs = {
            'lambda': self._estimate_lambda_cost(daily_volume),
            's3': self._estimate_s3_cost(daily_volume),
            'dynamodb': self._estimate_dynamodb_cost(daily_volume),
            'eventbridge': self._estimate_eventbridge_cost(daily_volume),
            'cloudwatch': self._estimate_cloudwatch_cost(daily_volume),
            'total': 0.0
        }
        
        monthly_costs['total'] = sum(monthly_costs.values())
        
        return monthly_costs
    
    def _estimate_lambda_cost(self, volume: Dict) -> float:
        """Estimate Lambda costs."""
        # Average Lambda invocations per day
        invocations = (
            volume.get('market_data_events', 0) +
            volume.get('signals', 0) +
            volume.get('orders', 0) * 2  # Order creation + execution
        )
        
        # Average compute (GB-seconds)
        avg_memory_gb = 1  # Average 1GB memory
        avg_duration_sec = 0.5  # Average 500ms execution
        
        compute_gb_seconds = invocations * avg_memory_gb * avg_duration_sec
        
        # Calculate cost
        invocation_cost = invocations * self.PRICING['lambda']['price_per_request']
        compute_cost = compute_gb_seconds * self.PRICING['lambda']['price_per_gb_second']
        
        monthly_cost = (invocation_cost + compute_cost) * 30
        
        # Apply free tier
        free_invocations = min(invocations * 30, self.PRICING['lambda']['free_tier']['requests'])
        free_compute = min(compute_gb_seconds * 30, self.PRICING['lambda']['free_tier']['compute'])
        
        invocation_cost_after_free = max(0, (invocations * 30) - free_invocations) * self.PRICING['lambda']['price_per_request']
        compute_cost_after_free = max(0, (compute_gb_seconds * 30) - free_compute) * self.PRICING['lambda']['price_per_gb_second']
        
        return invocation_cost_after_free + compute_cost_after_free
    
    def _estimate_s3_cost(self, volume: Dict) -> float:
        """Estimate S3 costs."""
        storage_gb = volume.get('data_storage_gb', 0)
        
        # Mix of storage classes
        standard_storage = storage_gb * 0.3  # 30% hot data
        ia_storage = storage_gb * 0.5  # 50% warm data
        glacier_storage = storage_gb * 0.2  # 20% cold data
        
        storage_cost = (
            standard_storage * self.PRICING['s3']['standard'] +
            ia_storage * self.PRICING['s3']['standard_ia'] +
            glacier_storage * self.PRICING['s3']['glacier_ir']
        )
        
        # Request costs
        daily_requests = volume.get('market_data_events', 0) * 2  # Put + eventual get
        
        request_cost = daily_requests * (
            self.PRICING['s3']['requests']['put'] +
            self.PRICING['s3']['requests']['get'] * 0.1  # 10% read rate
        )
        
        monthly_cost = (storage_cost + request_cost) * 30
        
        return monthly_cost
    
    def _estimate_dynamodb_cost(self, volume: Dict) -> float:
        """Estimate DynamoDB costs."""
        daily_writes = (
            volume.get('market_data_events', 0) * 0.1 +  # 10% of market data stored
            volume.get('signals', 0) +
            volume.get('orders', 0) * 2 +
            volume.get('position_updates', 0)
        )
        
        daily_reads = daily_writes * 5  # More reads than writes
        
        write_cost = daily_writes * self.PRICING['dynamodb']['write']
        read_cost = daily_reads * self.PRICING['dynamodb']['read']
        
        # Storage (estimate 1KB per item)
        items_per_day = daily_writes
        storage_gb = (items_per_day * 1 * 1024) / (1024**3)  # Convert KB to GB
        storage_cost = storage_gb * self.PRICING['dynamodb']['storage']
        
        monthly_cost = (write_cost + read_cost + storage_cost) * 30
        
        return monthly_cost
    
    def _estimate_eventbridge_cost(self, volume: Dict) -> float:
        """Estimate EventBridge costs."""
        daily_events = (
            volume.get('market_data_events', 0) +
            volume.get('signals', 0) +
            volume.get('orders', 0)
        )
        
        monthly_events = daily_events * 30
        monthly_cost = monthly_events * (self.PRICING['eventbridge']['events'] / 1000000)
        
        return monthly_cost
    
    def _estimate_cloudwatch_cost(self, volume: Dict) -> float:
        """Estimate CloudWatch costs."""
        # Metrics (5 metrics per service × 5 services)
        metrics_cost = 25 * self.PRICING['cloudwatch']['metrics']
        
        # Alarms (2 alarms per service × 5 services)
        alarms_cost = 10 * self.PRICING['cloudwatch']['alarms']
        
        # Logs (estimate 1KB per Lambda invocation)
        daily_invocations = (
            volume.get('market_data_events', 0) +
            volume.get('signals', 0) +
            volume.get('orders', 0) * 2
        )
        
        log_gb_per_day = (daily_invocations * 1 * 1024) / (1024**3)  # Convert KB to GB
        logs_cost = log_gb_per_day * self.PRICING['cloudwatch']['logs'] * 30
        
        monthly_cost = metrics_cost + alarms_cost + logs_cost
        
        return monthly_cost


def lambda_handler(event: Dict, context: Any) -> Dict:
    """
    Main Lambda handler for serverless trading pipeline.
    Routes events to appropriate functions based on event source.
    """
    pipeline = ServerlessTradingPipeline()
    
    # Determine event source and route accordingly
    if 'Records' in event:
        # S3 event (market data)
        return pipeline.process_market_data(event)
    
    elif 'source' in event and event['source'] == 'aws.events':
        # Scheduled Event (performance monitoring)
        return pipeline.monitor_performance()
    
    elif 'detail-type' in event and event['detail-type'] == 'signal.generation':
        # EventBridge event (signal generation)
        return pipeline.generate_trading_signal(event['detail'])
    
    elif 'stateMachineArn' in event:
        # Step Functions execution (order workflow)
        return pipeline.create_order(event)
    
    elif 'httpMethod' in event:
        # API Gateway request
        return handle_api_request(event, pipeline)
    
    else:
        # Direct invocation
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Unknown event type'})
        }


def handle_api_request(event: Dict, pipeline: ServerlessTradingPipeline) -> Dict:
    """Handle API Gateway requests."""
    http_method = event['httpMethod']
    path = event['path']
    
    if http_method == 'GET':
        if path == '/health':
            return {
                'statusCode': 200,
                'body': json.dumps({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})
            }
        
        elif path == '/metrics':
            performance = pipeline._calculate_performance_metrics()
            costs = pipeline.cost_tracker.calculate_daily_costs()
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'performance': performance,
                    'costs': costs,
                    'timestamp': datetime.utcnow().isoformat()
                })
            }
        
        elif path == '/positions':
            positions = pipeline._get_positions()
            return {
                'statusCode': 200,
                'body': json.dumps({'positions': positions})
            }
    
    elif http_method == 'POST':
        if path == '/deploy':
            return pipeline.deploy_pipeline()
        
        elif path == '/config':
            body = json.loads(event['body'])
            pipeline.update_config(body)
            return {
                'statusCode': 200,
                'body': json.dumps({'message': 'Configuration updated'})
            }
    
    return {
        'statusCode': 404,
        'body': json.dumps({'error': 'Not found'})
    }


def deploy_serverless_pipeline():
    """
    Deploy the complete serverless trading pipeline.
    This would be called from a deployment script.
    """
    print("Deploying Serverless Trading Pipeline...")
    print("="*80)
    
    # Initialize pipeline
    pipeline = ServerlessTradingPipeline()
    
    # Deploy pipeline
    result = pipeline.deploy_pipeline()
    
    if result['statusCode'] == 200:
        deployment_info = json.loads(result['body'])
        print(f"✅ Deployment successful!")
        print(f"Deployment ID: {deployment_info['deployment_id']}")
        
        print("\n📊 Resources deployed:")
        for resource_type, resources in deployment_info['resources'].items():
            print(f"\n{resource_type.replace('_', ' ').title()}:")
            for resource in resources:
                if isinstance(resource, dict):
                    for k, v in resource.items():
                        print(f"  • {k}: {v}")
                else:
                    print(f"  • {resource}")
        
        # Estimate costs
        print("\n💰 Cost Estimation:")
        cost_tracker = CostTracker()
        
        # Example daily volume
        daily_volume = {
            'market_data_events': 10000,  # 10K market data events per day
            'signals': 1000,              # 1K trading signals per day
            'orders': 100,                # 100 orders per day
            'data_storage_gb': 10,        # 10GB data storage
            'position_updates': 1000      # 1K position updates per day
        }
        
        monthly_costs = cost_tracker.estimate_monthly_cost(daily_volume)
        
        print(f"Estimated Monthly Costs:")
        for service, cost in monthly_costs.items():
            if service != 'total':
                print(f"  • {service.upper()}: ${cost:.2f}")
        
        print(f"\n  Total Monthly Cost: ${monthly_costs['total']:.2f}")
        
        print("\n🎯 Optimization Tips:")
        print("  1. Use Lambda provisioned concurrency for consistent latency")
        print("  2. Implement S3 lifecycle policies for cost optimization")
        print("  3. Use DynamoDB auto-scaling for variable workloads")
        print("  4. Monitor CloudWatch metrics for performance tuning")
        print("  5. Set up budget alerts in AWS Cost Explorer")
        
        print("\n🔒 Security Considerations:")
        print("  1. Use IAM roles with least privilege")
        print("  2. Encrypt data at rest (S3, DynamoDB)")
        print("  3. Use VPC endpoints for private connectivity")
        print("  4. Implement API Gateway authentication")
        print("  5. Regular security audits and penetration testing")
        
    else:
        print(f"❌ Deployment failed!")
        print(f"Error: {result['body']}")
    
    print("\n" + "="*80)
    print("Serverless Trading Pipeline Deployment Complete")
    print("="*80)


def demonstrate_serverless_pipeline():
    """Demonstrate the serverless trading pipeline."""
    print("Serverless Trading Pipeline Demonstration")
    print("="*80)
    
    # Initialize pipeline
    pipeline = ServerlessTradingPipeline()
    
    print("\n1. Processing Market Data...")
    
    # Simulate market data events
    market_events = [
        {
            'symbol': 'AAPL',
            'timestamp': datetime.utcnow().isoformat(),
            'open': 175.0,
            'high': 176.5,
            'low': 174.5,
            'close': 176.0,
            'volume': 1000000,
            'interval': '1min'
        },
        {
            'symbol': 'GOOGL',
            'timestamp': datetime.utcnow().isoformat(),
            'open': 135.0,
            'high': 136.0,
            'low': 134.5,
            'close': 135.5,
            'volume': 500000,
            'interval': '1min'
        }
    ]
    
    for event in market_events:
        result = pipeline.process_market_data(event)
        if result['statusCode'] == 200:
            print(f"  ✓ Processed {event['symbol']} market data")
        else:
            print(f"  ✗ Failed to process {event['symbol']}")
    
    print("\n2. Generating Trading Signals...")
    
    # Simulate signal generation
    signal_event = {
        'symbol': 'AAPL',
        'timestamp': datetime.utcnow().isoformat(),
        'features': {
            'price': 176.0,
            'sma_5': 175.5,
            'sma_10': 174.8,
            'sma_ratio': 1.004,
            'volatility': 0.015,
            'volume_ratio': 1.2
        },
        'market_data': market_events[0]
    }
    
    result = pipeline.generate_trading_signal(signal_event)
    if result['statusCode'] == 200:
        signal_data = json.loads(result['body'])
        print(f"  ✓ Generated signal: {signal_data['signal']['signal']} with {signal_data['signal']['confidence']:.1%} confidence")
    else:
        print(f"  ✗ Failed to generate signal")
    
    print("\n3. Creating and Executing Orders...")
    
    # Simulate order creation
    order_result = pipeline.create_order(signal_event)
    if order_result['statusCode'] == 200:
        order_data = json.loads(order_result['body'])
        print(f"  ✓ Created order: {order_data['order']['side']} {order_data['order']['quantity']} shares of {order_data['order']['symbol']}")
        print(f"    Execution price: ${order_data['execution']['price']:.2f}")
    else:
        print(f"  ✗ Failed to create order")
    
    print("\n4. Monitoring Performance and Costs...")
    
    # Check performance
    performance_result = pipeline.monitor_performance()
    if performance_result['statusCode'] == 200:
        perf_data = json.loads(performance_result['body'])
        print(f"  ✓ Performance monitoring active")
        print(f"    Status: {perf_data['summary']['status']}")
        print(f"    Total cost today: ${perf_data['summary']['total_cost_today']:.2f}")
    else:
        print(f"  ✗ Performance monitoring failed")
    
    print("\n5. Cost Optimization Analysis...")
    
    # Estimate costs for different volumes
    cost_tracker = CostTracker()
    
    volumes = [
        ('Low Volume', {
            'market_data_events': 1000,
            'signals': 100,
            'orders': 10,
            'data_storage_gb': 1,
            'position_updates': 100
        }),
        ('Medium Volume', {
            'market_data_events': 10000,
            'signals': 1000,
            'orders': 100,
            'data_storage_gb': 10,
            'position_updates': 1000
        }),
        ('High Volume', {
            'market_data_events': 100000,
            'signals': 10000,
            'orders': 1000,
            'data_storage_gb': 100,
            'position_updates': 10000
        })
    ]
    
    print("\nCost Estimates for Different Volumes:")
    for volume_name, volume in volumes:
        costs = cost_tracker.estimate_monthly_cost(volume)
        print(f"\n  {volume_name}:")
        print(f"    Monthly Cost: ${costs['total']:.2f}")
        print(f"    Cost per Signal: ${costs['total'] / volume['signals'] / 30:.4f}")
    
    print("\n" + "="*80)
    print("Serverless Pipeline Advantages:")
    print("  ✓ No server management")
    print("  ✓ Automatic scaling")
    print("  ✓ Pay-per-use pricing")
    print("  ✓ High availability")
    print("  ✓ Built-in monitoring")
    print("\nCost Optimization Strategies:")
    print("  • Use appropriate S3 storage classes")
    print("  • Implement Lambda memory optimization")
    print("  • Use DynamoDB auto-scaling")
    print("  • Set up cost allocation tags")
    print("  • Monitor with AWS Cost Explorer")
    print("="*80)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Serverless Trading Pipeline')
    parser.add_argument('--deploy', action='store_true', help='Deploy the pipeline')
    parser.add_argument('--demo', action='store_true', help='Run demonstration')
    parser.add_argument('--estimate-costs', action='store_true', help='Estimate costs')
    
    args = parser.parse_args()
    
    if args.deploy:
        deploy_serverless_pipeline()
    elif args.demo:
        demonstrate_serverless_pipeline()
    elif args.estimate_costs:
        cost_tracker = CostTracker()
        
        # Get user input for volume estimation
        print("Cost Estimation for Serverless Trading Pipeline")
        print("="*80)
        
        market_data_events = int(input("Daily market data events: ") or "10000")
        signals = int(input("Daily trading signals: ") or "1000")
        orders = int(input("Daily orders: ") or "100")
        data_storage_gb = float(input("Data storage (GB): ") or "10")
        position_updates = int(input("Daily position updates: ") or "1000")
        
        volume = {
            'market_data_events': market_data_events,
            'signals': signals,
            'orders': orders,
            'data_storage_gb': data_storage_gb,
            'position_updates': position_updates
        }
        
        costs = cost_tracker.estimate_monthly_cost(volume)
        
        print("\n" + "="*80)
        print("COST ESTIMATION RESULTS")
        print("="*80)
        
        print(f"\nEstimated Monthly Costs:")
        for service, cost in costs.items():
            if service != 'total':
                service_name = service.upper().replace('_', ' ')
                print(f"  {service_name:15} ${cost:8.2f}")
        
        print(f"\n{'Total Monthly Cost':15} ${costs['total']:8.2f}")
        
        print(f"\nCost Breakdown:")
        total = costs['total']
        for service, cost in costs.items():
            if service != 'total':
                percentage = (cost / total * 100) if total > 0 else 0
                service_name = service.upper().replace('_', ' ')
                print(f"  {service_name:15} {percentage:6.1f}%")
        
        print("\nOptimization Recommendations:")
        if costs['lambda'] / total > 0.5:
            print("  • Consider Lambda memory optimization")
            print("  • Use provisioned concurrency for consistent workloads")
        
        if costs['s3'] / total > 0.3:
            print("  • Implement S3 lifecycle policies")
            print("  • Use appropriate storage classes")
        
        if costs['dynamodb'] / total > 0.4:
            print("  • Optimize DynamoDB read/write capacity")
            print("  • Consider DAX caching for frequent reads")
        
        print("\n" + "="*80)
        
    else:
        # Default: run demonstration
        demonstrate_serverless_pipeline()


if __name__ == "__main__":
    # Import statistics for performance metrics
    import statistics
    
    main()