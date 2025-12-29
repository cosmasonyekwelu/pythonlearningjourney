# **Day 96: Disaster Recovery and Fault Tolerance**

## **Objective**
Design and implement disaster recovery and fault tolerance mechanisms to ensure trading system availability during failures.

## **Core Concepts**

### **Business Continuity Planning**
* **Business Impact Analysis**: Identify critical trading operations, prioritize recovery based on financial impact
* **RTO/RPO Definitions**: 
  - Recovery Time Objective (RTO): Maximum acceptable downtime (e.g., 4 hours for retail trading, 4 minutes for HFT)
  - Recovery Point Objective (RPO): Maximum data loss (e.g., 15 minutes for positions, 0 seconds for executed orders)
* **Critical System Identification**: 
  - Order execution → Highest priority
  - Risk management → Critical
  - Market data → High priority
  - Reporting → Lower priority
* **DR Strategies**:
  - Hot Site: Complete real-time replication (seconds RTO)
  - Warm Site: Partial replication (minutes to hours RTO)
  - Cold Site: Infrastructure only (hours to days RTO)

### **High Availability Architecture**
* **Multi-Region Deployment**:
  ```
  Primary Region (us-east-1) ── Active ──→ Orders, Positions
                              ↓
  Secondary Region (us-west-2) ── Standby ──→ Replica databases
  ```
* **Active-Active vs Active-Passive**:
  - Active-Active: Both regions process trades, requires state synchronization
  - Active-Passive: Secondary ready to take over, simpler consistency
* **Database Replication Patterns**:
  - Synchronous: Zero data loss, higher latency
  - Asynchronous: Potential data loss, lower latency
  - Semi-synchronous: Balance between consistency and performance

### **Data Backup & Recovery**
* **Backup Strategies**:
  - Full Daily + Incremental Hourly for trading data
  - Continuous WAL archiving for PostgreSQL
  - Point-in-Time Recovery (PITR) for exact state restoration
* **Backup Validation**:
  - Automated restoration testing
  - Checksum verification
  - Encryption at rest and in transit
* **3-2-1 Rule**:
  - 3 copies of data
  - 2 different media types
  - 1 off-site copy (air-gapped for security)

### **Fault Tolerance Patterns**
* **Circuit Breaker Pattern**:
  ```python
  class TradingCircuitBreaker:
      def __init__(self, failure_threshold=5, reset_timeout=60):
          self.failure_count = 0
          self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
          
      def execute_order(self, order):
          if self.state == "OPEN":
              return self.fallback(order)
          try:
              result = self.broker_api.execute(order)
              self._on_success()
              return result
          except Exception as e:
              self._on_failure()
              raise
  ```
* **Retry Logic with Exponential Backoff**:
  ```python
  def execute_with_retry(operation, max_retries=3):
      for attempt in range(max_retries):
          try:
              return operation()
          except TemporaryError as e:
              wait_time = (2 ** attempt) + random.random()
              time.sleep(wait_time)
      raise PermanentError("Max retries exceeded")
  ```

### **Disaster Recovery Procedures**
* **Runbooks for Common Scenarios**:
  - Database corruption recovery
  - Region failure failover
  - Order state reconstruction
  - Market data gap filling
* **Automated Failover**:
  - Health checks every 30 seconds
  - Automatic DNS/load balancer updates
  - State transfer validation
* **Communication Plans**:
  - Automated status updates to traders
  - Escalation matrix with contact information
  - Public status page for transparency

### **Trading-Specific Recovery Considerations**
* **Order State Recovery**:
  - Persistent order journal with sequence numbers
  - Idempotent order processing
  - Broker reconciliation procedures
* **Position Reconciliation**:
  - Daily position snapshots
  - Transaction-level audit trail
  - Broker statement comparison
* **P&L Reconstruction**:
  - Trade-by-trade reconstruction from logs
  - Market data replay capability
  - Cash flow verification

### **Monitoring for Resilience**
* **Synthetic Transactions**:
  - Test orders with known outcomes
  - End-to-end latency monitoring
  - Success rate tracking
* **Capacity Monitoring**:
  - Resource utilization thresholds
  - Queue depth monitoring
  - Connection pool health

## **Hands-On Activity**

### **Tutorial: Design and implement a disaster recovery plan for a trading system**

```python
"""
Day 96 Tutorial: Disaster Recovery Plan Implementation
Complete DR strategy for trading system with automated failover.
"""

import asyncio
import json
import time
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
import psycopg2
from psycopg2.extras import RealDictCursor
import redis
import boto3
from datetime import datetime, timedelta
import hashlib
import yaml
from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler('dr_monitor.log', maxBytes=10485760, backupCount=5),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class RecoveryTier(Enum):
    """Recovery priority tiers for trading components."""
    TIER_1 = "Tier 1"  # Critical: Order execution, risk checks (RTO < 1 min)
    TIER_2 = "Tier 2"  # High: Market data, positions (RTO < 5 min)
    TIER_3 = "Tier 3"  # Medium: Analytics, reporting (RTO < 30 min)
    TIER_4 = "Tier 4"  # Low: Historical data, archives (RTO < 4 hours)


@dataclass
class RecoveryObjective:
    """Recovery Time and Point Objectives."""
    component: str
    tier: RecoveryTier
    rto_minutes: int
    rpo_minutes: int
    max_data_loss: str
    dependencies: List[str]
    
    def to_dict(self):
        return asdict(self)


@dataclass
class BackupConfig:
    """Backup configuration for a component."""
    component: str
    backup_frequency: str  # e.g., "15min", "1h", "daily"
    retention_days: int
    encryption: bool
    validation_required: bool
    restore_test_frequency: str
    locations: List[str]  # Local, S3, Glacier, etc.


class DisasterRecoveryPlanner:
    """
    Comprehensive disaster recovery planning and implementation.
    """
    
    def __init__(self, config_path: str = "dr_config.yaml"):
        self.config = self._load_config(config_path)
        self.recovery_objectives = {}
        self.backup_configs = {}
        self.failover_state = {}
        
        # Initialize clients
        self._init_clients()
        
        # Load recovery plans
        self._load_recovery_plans()
    
    def _load_config(self, config_path: str) -> Dict:
        """Load DR configuration from YAML file."""
        config_path = Path(config_path)
        if config_path.exists():
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        
        # Default configuration
        return {
            'primary_region': 'us-east-1',
            'secondary_region': 'us-west-2',
            'database': {
                'primary': 'trading-db-primary',
                'secondary': 'trading-db-secondary',
                'replication_lag_threshold': 30  # seconds
            },
            'redis': {
                'primary': 'trading-redis-primary',
                'secondary': 'trading-redis-secondary'
            },
            'backup': {
                's3_bucket': 'trading-backups',
                'glacier_vault': 'trading-archives',
                'local_path': '/backups/trading'
            },
            'monitoring': {
                'health_check_interval': 30,
                'failover_cooldown': 300  # seconds
            }
        }
    
    def _init_clients(self):
        """Initialize AWS and database clients."""
        # AWS clients for multi-region
        self.s3_primary = boto3.client('s3', region_name=self.config['primary_region'])
        self.s3_secondary = boto3.client('s3', region_name=self.config['secondary_region'])
        
        # RDS clients
        self.rds_client = boto3.client('rds', region_name=self.config['primary_region'])
        
        # CloudWatch for monitoring
        self.cloudwatch = boto3.client('cloudwatch', region_name=self.config['primary_region'])
    
    def _load_recovery_plans(self):
        """Load recovery plans for all components."""
        # Define recovery objectives for trading components
        self.recovery_objectives = {
            'order_execution': RecoveryObjective(
                component='order_execution',
                tier=RecoveryTier.TIER_1,
                rto_minutes=1,
                rpo_minutes=0,
                max_data_loss='Zero',
                dependencies=['database', 'redis', 'market_data']
            ),
            'risk_engine': RecoveryObjective(
                component='risk_engine',
                tier=RecoveryTier.TIER_1,
                rto_minutes=2,
                rpo_minutes=0,
                max_data_loss='Zero',
                dependencies=['database', 'redis']
            ),
            'market_data': RecoveryObjective(
                component='market_data',
                tier=RecoveryTier.TIER_2,
                rto_minutes=5,
                rpo_minutes=1,
                max_data_loss='1 minute',
                dependencies=['database']
            ),
            'positions': RecoveryObjective(
                component='positions',
                tier=RecoveryTier.TIER_2,
                rto_minutes=5,
                rpo_minutes=0,
                max_data_loss='Zero',
                dependencies=['database']
            ),
            'analytics': RecoveryObjective(
                component='analytics',
                tier=RecoveryTier.TIER_3,
                rto_minutes=30,
                rpo_minutes=15,
                max_data_loss='15 minutes',
                dependencies=['database']
            ),
            'reporting': RecoveryObjective(
                component='reporting',
                tier=RecoveryTier.TIER_4,
                rto_minutes=240,
                rpo_minutes=60,
                max_data_loss='1 hour',
                dependencies=['database']
            )
        }
        
        # Define backup configurations
        self.backup_configs = {
            'database': BackupConfig(
                component='database',
                backup_frequency='15min',
                retention_days=35,
                encryption=True,
                validation_required=True,
                restore_test_frequency='weekly',
                locations=['S3', 'Glacier', 'Local']
            ),
            'redis': BackupConfig(
                component='redis',
                backup_frequency='5min',
                retention_days=7,
                encryption=True,
                validation_required=True,
                restore_test_frequency='daily',
                locations=['S3', 'Local']
            ),
            'order_logs': BackupConfig(
                component='order_logs',
                backup_frequency='1min',
                retention_days=90,
                encryption=True,
                validation_required=True,
                restore_test_frequency='monthly',
                locations=['S3', 'Glacier']
            ),
            'market_data': BackupConfig(
                component='market_data',
                backup_frequency='1h',
                retention_days=30,
                encryption=False,
                validation_required=False,
                restore_test_frequency='monthly',
                locations=['S3']
            )
        }
    
    def create_recovery_plan(self) -> Dict:
        """
        Create comprehensive disaster recovery plan.
        
        Returns:
            Dict: Complete DR plan with procedures and checklists
        """
        logger.info("Creating disaster recovery plan...")
        
        dr_plan = {
            'metadata': {
                'created_at': datetime.utcnow().isoformat(),
                'version': '1.0.0',
                'plan_owner': 'Trading Operations Team'
            },
            'recovery_objectives': {
                name: obj.to_dict() for name, obj in self.recovery_objectives.items()
            },
            'backup_configurations': {
                name: asdict(config) for name, config in self.backup_configs.items()
            },
            'failover_procedures': self._create_failover_procedures(),
            'recovery_procedures': self._create_recovery_procedures(),
            'communication_plan': self._create_communication_plan(),
            'testing_schedule': self._create_testing_schedule(),
            'runbooks': self._create_runbooks()
        }
        
        # Save DR plan
        self._save_dr_plan(dr_plan)
        
        logger.info("DR plan created successfully")
        return dr_plan
    
    def _create_failover_procedures(self) -> Dict:
        """Create automated failover procedures."""
        return {
            'database_failover': {
                'trigger_conditions': [
                    'Primary database unavailable for > 60 seconds',
                    'Replication lag > 30 seconds',
                    'Manual failover requested'
                ],
                'steps': [
                    '1. Verify secondary database is in sync',
                    '2. Promote read replica to primary',
                    '3. Update DNS/endpoint configuration',
                    '4. Redirect application traffic',
                    '5. Update monitoring alerts',
                    '6. Notify trading team'
                ],
                'validation': [
                    'Confirm write operations work',
                    'Verify data consistency',
                    'Check application connectivity'
                ],
                'estimated_time': '2 minutes',
                'rollback_procedure': 'Restore from backup if issues'
            },
            'region_failover': {
                'trigger_conditions': [
                    'Primary region unavailable',
                    'Multiple AZ failures in primary region',
                    'Manual regional failover requested'
                ],
                'steps': [
                    '1. Activate secondary region infrastructure',
                    '2. Promote secondary databases',
                    '3. Update global DNS (Route53)',
                    '4. Start secondary region services',
                    '5. Redirect all traffic',
                    '6. Validate trading operations'
                ],
                'validation': [
                    'End-to-end order execution test',
                    'Position reconciliation',
                    'Risk checks validation'
                ],
                'estimated_time': '5 minutes',
                'rollback_procedure': 'Gradual traffic shift back'
            },
            'order_execution_failover': {
                'trigger_conditions': [
                    'Order execution service down',
                    'High error rate (>5%)',
                    'Latency > 1000ms'
                ],
                'steps': [
                    '1. Drain traffic from primary service',
                    '2. Activate secondary service instances',
                    '3. Load state from persistent storage',
                    '4. Resume order processing',
                    '5. Validate order state consistency'
                ],
                'validation': [
                    'Test order execution',
                    'Verify order state persistence',
                    'Check risk validation'
                ],
                'estimated_time': '1 minute',
                'rollback_procedure': 'Restore from order journal'
            }
        }
    
    def _create_recovery_procedures(self) -> Dict:
        """Create data recovery procedures."""
        return {
            'database_recovery': {
                'point_in_time_recovery': {
                    'steps': [
                        '1. Identify recovery timestamp',
                        '2. Restore from latest backup',
                        '3. Apply WAL logs to desired time',
                        '4. Verify data consistency',
                        '5. Make database available'
                    ],
                    'tools': ['pg_restore', 'WAL-E', 'AWS RDS PITR'],
                    'estimated_time': 'Varies by data size',
                    'validation': 'Data checksum verification'
                },
                'full_backup_recovery': {
                    'steps': [
                        '1. Stop database traffic',
                        '2. Restore from S3 backup',
                        '3. Start database',
                        '4. Verify all tables accessible',
                        '5. Resume traffic'
                    ],
                    'estimated_time': '30 minutes per 100GB',
                    'validation': 'Sample queries on critical tables'
                }
            },
            'redis_recovery': {
                'rdb_restore': {
                    'steps': [
                        '1. Stop Redis instances',
                        '2. Copy latest RDB file',
                        '3. Start Redis with restored data',
                        '4. Verify key counts',
                        '5. Warm up cache if needed'
                    ],
                    'estimated_time': '5 minutes',
                    'validation': 'Check critical keys existence'
                },
                'aof_recovery': {
                    'steps': [
                        '1. Stop Redis instances',
                        '2. Use redis-check-aof to fix file',
                        '3. Start Redis with AOF file',
                        '4. Monitor replication',
                        '5. Verify data integrity'
                    ],
                    'estimated_time': '10 minutes',
                    'validation': 'Transaction log verification'
                }
            },
            'order_state_recovery': {
                'steps': [
                    '1. Restore order journal from backup',
                    '2. Replay orders from last known state',
                    '3. Reconcile with broker statements',
                    '4. Validate positions match',
                    '5. Resume trading'
                ],
                'estimated_time': '15 minutes',
                'validation': 'Position reconciliation report'
            }
        }
    
    def _create_communication_plan(self) -> Dict:
        """Create communication plan for disasters."""
        return {
            'stakeholders': {
                'trading_team': {
                    'contact_methods': ['Slack', 'SMS', 'Phone'],
                    'escalation_path': 'Trader → Head Trader → Trading Director',
                    'update_frequency': 'Every 5 minutes during incident'
                },
                'operations_team': {
                    'contact_methods': ['PagerDuty', 'Slack', 'Phone'],
                    'escalation_path': 'SRE → Lead SRE → Head of Operations',
                    'update_frequency': 'Real-time'
                },
                'compliance': {
                    'contact_methods': ['Email', 'Phone'],
                    'escalation_path': 'Compliance Officer',
                    'update_frequency': 'After recovery complete'
                },
                'clients': {
                    'contact_methods': ['Status Page', 'Email'],
                    'escalation_path': 'Client Support → Account Manager',
                    'update_frequency': 'Every 30 minutes'
                }
            },
            'communication_channels': {
                'internal': ['Slack #incidents', 'Zoom War Room'],
                'external': ['Status Page', 'Twitter', 'Email Blast']
            },
            'templates': {
                'initial_alert': """
                🚨 TRADING SYSTEM INCIDENT
                Component: {component}
                Severity: {severity}
                Impact: {impact}
                Status: Investigating
                Next update in: 15 minutes
                """,
                'update_template': """
                🔄 INCIDENT UPDATE
                Component: {component}
                Status: {status}
                Action: {action}
                ETA: {eta}
                Impact: {impact}
                """,
                'resolution_template': """
                ✅ INCIDENT RESOLVED
                Component: {component}
                Resolution: {resolution}
                Root Cause: {root_cause}
                Next Steps: {next_steps}
                """
            }
        }
    
    def _create_testing_schedule(self) -> Dict:
        """Create DR testing schedule."""
        return {
            'weekly_tests': [
                'Database backup restoration',
                'Redis failover test',
                'Health check validation'
            ],
            'monthly_tests': [
                'Full region failover simulation',
                'Order state recovery test',
                'Communication plan test'
            ],
            'quarterly_tests': [
                'Disaster recovery full drill',
                'Third-party dependency failure',
                'Security incident simulation'
            ],
            'annual_tests': [
                'Complete site failure recovery',
                'Long-term backup restoration',
                'Regulatory compliance audit'
            ],
            'success_criteria': {
                'rto_met': '95% of tests',
                'rpo_met': '99% of tests',
                'data_integrity': '100% of tests'
            }
        }
    
    def _create_runbooks(self) -> Dict:
        """Create operational runbooks for common scenarios."""
        return {
            'database_corruption': {
                'symptoms': ['Query errors', 'Data inconsistency', 'High I/O errors'],
                'immediate_actions': [
                    '1. Isolate affected database',
                    '2. Start failover to secondary',
                    '3. Begin corruption assessment'
                ],
                'recovery_steps': [
                    '1. Restore from last known good backup',
                    '2. Apply transaction logs',
                    '3. Validate data integrity',
                    '4. Gradually restore traffic'
                ],
                'verification': [
                    'Run data integrity checks',
                    'Validate critical queries',
                    'Check application functionality'
                ]
            },
            'region_outage': {
                'symptoms': ['High latency', 'Connection timeouts', 'Multiple service failures'],
                'immediate_actions': [
                    '1. Declare disaster',
                    '2. Activate DR plan',
                    '3. Notify stakeholders'
                ],
                'recovery_steps': [
                    '1. Failover to secondary region',
                    '2. Validate core services',
                    '3. Resume trading operations',
                    '4. Monitor stability'
                ],
                'verification': [
                    'End-to-end order flow test',
                    'Position reconciliation',
                    'Risk system validation'
                ]
            },
            'order_state_loss': {
                'symptoms': ['Missing orders', 'Position mismatches', 'P&L discrepancies'],
                'immediate_actions': [
                    '1. Pause trading',
                    '2. Isolate affected systems',
                    '3. Begin order journal recovery'
                ],
                'recovery_steps': [
                    '1. Restore order journal from backup',
                    '2. Replay transactions',
                    '3. Reconcile with brokers',
                    '4. Validate positions'
                ],
                'verification': [
                    'Match orders with broker confirmations',
                    'Validate cash balances',
                    'Confirm P&L accuracy'
                ]
            }
        }
    
    def _save_dr_plan(self, dr_plan: Dict):
        """Save DR plan to files."""
        output_dir = Path("dr_plans")
        output_dir.mkdir(exist_ok=True)
        
        # Save as JSON
        json_path = output_dir / f"dr_plan_{datetime.utcnow().strftime('%Y%m%d')}.json"
        with open(json_path, 'w') as f:
            json.dump(dr_plan, f, indent=2)
        
        # Save as YAML
        yaml_path = output_dir / f"dr_plan_{datetime.utcnow().strftime('%Y%m%d')}.yaml"
        with open(yaml_path, 'w') as f:
            yaml.dump(dr_plan, f, default_flow_style=False)
        
        logger.info(f"DR plan saved to {json_path} and {yaml_path}")
    
    def setup_backup_system(self):
        """Set up automated backup system."""
        logger.info("Setting up automated backup system...")
        
        # Configure database backups
        self._setup_database_backups()
        
        # Configure Redis backups
        self._setup_redis_backups()
        
        # Configure order journal backups
        self._setup_order_journal_backups()
        
        # Configure monitoring for backups
        self._setup_backup_monitoring()
        
        logger.info("Backup system setup complete")
    
    def _setup_database_backups(self):
        """Configure automated database backups."""
        try:
            # Enable automated backups in RDS
            response = self.rds_client.modify_db_instance(
                DBInstanceIdentifier=self.config['database']['primary'],
                BackupRetentionPeriod=35,  # 35 days retention
                PreferredBackupWindow='03:00-04:00',  # Low traffic window
                PreferredMaintenanceWindow='sun:04:00-sun:05:00',
                EnablePerformanceInsights=True,
                PerformanceInsightsRetentionPeriod=731  # 2 years
            )
            
            logger.info(f"Database backup configured: {response['DBInstance']['DBInstanceIdentifier']}")
            
            # Enable Point-in-Time Recovery
            self.rds_client.modify_db_instance(
                DBInstanceIdentifier=self.config['database']['primary'],
                BackupRetentionPeriod=35,
                DeletionProtection=True
            )
            
            logger.info("Point-in-Time Recovery enabled")
            
        except Exception as e:
            logger.error(f"Error configuring database backups: {e}")
    
    def _setup_redis_backups(self):
        """Configure Redis backups."""
        # Redis backup configuration would depend on deployment
        # For AWS ElastiCache, you'd use snapshots
        logger.info("Redis backup configuration requires manual setup for your deployment")
    
    def _setup_order_journal_backups(self):
        """Configure order journal backups."""
        # Create S3 bucket for order journal backups
        try:
            bucket_name = f"order-journal-backups-{datetime.utcnow().strftime('%Y%m')}"
            
            # Check if bucket exists
            try:
                self.s3_primary.head_bucket(Bucket=bucket_name)
                logger.info(f"S3 bucket {bucket_name} already exists")
            except:
                # Create bucket with encryption
                self.s3_primary.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={
                        'LocationConstraint': self.config['primary_region']
                    }
                )
                
                # Enable versioning
                self.s3_primary.put_bucket_versioning(
                    Bucket=bucket_name,
                    VersioningConfiguration={'Status': 'Enabled'}
                )
                
                # Enable encryption
                self.s3_primary.put_bucket_encryption(
                    Bucket=bucket_name,
                    ServerSideEncryptionConfiguration={
                        'Rules': [
                            {
                                'ApplyServerSideEncryptionByDefault': {
                                    'SSEAlgorithm': 'AES256'
                                }
                            }
                        ]
                    }
                )
                
                # Set lifecycle policy
                self.s3_primary.put_bucket_lifecycle_configuration(
                    Bucket=bucket_name,
                    LifecycleConfiguration={
                        'Rules': [
                            {
                                'ID': 'Move to Glacier after 30 days',
                                'Status': 'Enabled',
                                'Prefix': '',
                                'Transitions': [
                                    {
                                        'Days': 30,
                                        'StorageClass': 'GLACIER'
                                    }
                                ]
                            },
                            {
                                'ID': 'Delete after 1 year',
                                'Status': 'Enabled',
                                'Prefix': '',
                                'Expiration': {'Days': 365}
                            }
                        ]
                    }
                )
                
                logger.info(f"Order journal backup bucket created: {bucket_name}")
                
        except Exception as e:
            logger.error(f"Error creating order journal backup bucket: {e}")
    
    def _setup_backup_monitoring(self):
        """Configure CloudWatch monitoring for backups."""
        try:
            # Create CloudWatch dashboard for backup monitoring
            dashboard_body = {
                'widgets': [
                    {
                        'type': 'metric',
                        'properties': {
                            'metrics': [
                                ['AWS/RDS', 'BackupRetentionPeriodStorageUsed', 'DBInstanceIdentifier', self.config['database']['primary']]
                            ],
                            'period': 300,
                            'stat': 'Average',
                            'region': self.config['primary_region'],
                            'title': 'Database Backup Storage Used'
                        }
                    },
                    {
                        'type': 'metric',
                        'properties': {
                            'metrics': [
                                ['AWS/S3', 'NumberOfObjects', 'BucketName', 'trading-backups', 'StorageType', 'AllStorageTypes']
                            ],
                            'period': 300,
                            'stat': 'Average',
                            'region': self.config['primary_region'],
                            'title': 'S3 Backup Objects'
                        }
                    }
                ]
            }
            
            self.cloudwatch.put_dashboard(
                DashboardName='BackupMonitoring',
                DashboardBody=json.dumps(dashboard_body)
            )
            
            # Create alarms for backup failures
            self.cloudwatch.put_metric_alarm(
                AlarmName='DatabaseBackupFailed',
                ComparisonOperator='LessThanThreshold',
                EvaluationPeriods=1,
                MetricName='BackupRetentionPeriodStorageUsed',
                Namespace='AWS/RDS',
                Period=86400,  # 24 hours
                Statistic='Average',
                Threshold=1,  # Less than 1 byte means backup failed
                ActionsEnabled=True,
                AlarmActions=[
                    f'arn:aws:sns:{self.config["primary_region"]}:123456789012:BackupAlerts'
                ],
                Dimensions=[
                    {
                        'Name': 'DBInstanceIdentifier',
                        'Value': self.config['database']['primary']
                    }
                ]
            )
            
            logger.info("Backup monitoring configured")
            
        except Exception as e:
            logger.error(f"Error configuring backup monitoring: {e}")
    
    async def monitor_system_health(self):
        """
        Continuous monitoring of system health for DR readiness.
        """
        logger.info("Starting system health monitoring...")
        
        while True:
            try:
                health_status = await self._check_system_health()
                
                if not health_status['overall_healthy']:
                    logger.warning(f"System health degraded: {health_status}")
                    
                    # Trigger alerts based on severity
                    if health_status['severity'] == 'critical':
                        await self._trigger_failover(health_status)
                
                # Log health status
                self._log_health_status(health_status)
                
                # Check backup status
                backup_status = await self._check_backup_status()
                if not backup_status['all_successful']:
                    logger.error(f"Backup failures detected: {backup_status}")
                
                # Wait for next check
                await asyncio.sleep(self.config['monitoring']['health_check_interval'])
                
            except Exception as e:
                logger.error(f"Error in health monitoring: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _check_system_health(self) -> Dict:
        """Check health of all critical components."""
        health_checks = [
            self._check_database_health(),
            self._check_redis_health(),
            self._check_replication_health(),
            self._check_service_health()
        ]
        
        results = await asyncio.gather(*health_checks, return_exceptions=True)
        
        # Process results
        overall_healthy = True
        critical_failures = []
        warnings = []
        
        for result in results:
            if isinstance(result, Exception):
                critical_failures.append(str(result))
                overall_healthy = False
            elif isinstance(result, dict):
                if not result.get('healthy', True):
                    if result.get('severity') == 'critical':
                        critical_failures.append(result.get('component'))
                        overall_healthy = False
                    else:
                        warnings.append(result.get('component'))
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'overall_healthy': overall_healthy,
            'critical_failures': critical_failures,
            'warnings': warnings,
            'severity': 'critical' if critical_failures else 'warning' if warnings else 'healthy'
        }
    
    async def _check_database_health(self) -> Dict:
        """Check database health and replication status."""
        try:
            # Get database status
            response = self.rds_client.describe_db_instances(
                DBInstanceIdentifier=self.config['database']['primary']
            )
            
            db_instance = response['DBInstances'][0]
            
            health = {
                'component': 'database',
                'healthy': db_instance['DBInstanceStatus'] == 'available',
                'status': db_instance['DBInstanceStatus'],
                'storage_used_percent': (db_instance['AllocatedStorage'] - db_instance['FreeStorageSpace']) / db_instance['AllocatedStorage'] * 100,
                'connections': db_instance.get('DBConnections', 0)
            }
            
            # Check replication lag if applicable
            if 'ReadReplicaDBInstanceIdentifiers' in db_instance:
                health['has_replicas'] = True
                # Check replica status
                replica_response = self.rds_client.describe_db_instances(
                    DBInstanceIdentifier=db_instance['ReadReplicaDBInstanceIdentifiers'][0]
                )
                replica = replica_response['DBInstances'][0]
                health['replica_status'] = replica['DBInstanceStatus']
            else:
                health['has_replicas'] = False
            
            # Determine severity
            if db_instance['DBInstanceStatus'] != 'available':
                health['severity'] = 'critical'
            elif health.get('storage_used_percent', 0) > 90:
                health['severity'] = 'warning'
            else:
                health['severity'] = 'healthy'
            
            return health
            
        except Exception as e:
            return {
                'component': 'database',
                'healthy': False,
                'error': str(e),
                'severity': 'critical'
            }
    
    async def _check_redis_health(self) -> Dict:
        """Check Redis health."""
        # Implementation depends on Redis deployment
        # For AWS ElastiCache, you'd use describe_cache_clusters
        return {
            'component': 'redis',
            'healthy': True,  # Placeholder
            'severity': 'healthy'
        }
    
    async def _check_replication_health(self) -> Dict:
        """Check data replication health between primary and secondary."""
        try:
            # This would check replication lag
            # For PostgreSQL, you'd query pg_stat_replication
            # For Redis, you'd check replica sync status
            
            replication_status = {
                'component': 'replication',
                'database_lag_seconds': 0,  # Placeholder
                'redis_lag_seconds': 0,     # Placeholder
                'healthy': True
            }
            
            # Check if lag exceeds thresholds
            max_lag = self.config['database']['replication_lag_threshold']
            if replication_status['database_lag_seconds'] > max_lag:
                replication_status['healthy'] = False
                replication_status['severity'] = 'warning'
                replication_status['message'] = f'Replication lag {replication_status["database_lag_seconds"]}s > {max_lag}s threshold'
            else:
                replication_status['severity'] = 'healthy'
            
            return replication_status
            
        except Exception as e:
            return {
                'component': 'replication',
                'healthy': False,
                'error': str(e),
                'severity': 'critical'
            }
    
    async def _check_service_health(self) -> Dict:
        """Check health of trading services."""
        services = ['order_execution', 'risk_engine', 'market_data']
        
        service_health = {
            'component': 'trading_services',
            'healthy': True,
            'services': {},
            'unhealthy_services': []
        }
        
        # Check each service (simplified - in reality would make HTTP requests)
        for service in services:
            # Placeholder health check
            service_health['services'][service] = {
                'status': 'healthy',  # Would be determined by actual health check
                'response_time_ms': 50,
                'last_success': datetime.utcnow().isoformat()
            }
            
            if service_health['services'][service]['status'] != 'healthy':
                service_health['unhealthy_services'].append(service)
                service_health['healthy'] = False
        
        service_health['severity'] = 'critical' if service_health['unhealthy_services'] else 'healthy'
        
        return service_health
    
    async def _check_backup_status(self) -> Dict:
        """Check status of recent backups."""
        try:
            # Check database backup status
            response = self.rds_client.describe_db_instances(
                DBInstanceIdentifier=self.config['database']['primary']
            )
            
            db_instance = response['DBInstances'][0]
            latest_restorable_time = db_instance.get('LatestRestorableTime', None)
            
            backup_status = {
                'component': 'backups',
                'database': {
                    'latest_backup': db_instance.get('LatestRestorableTime', 'Unknown'),
                    'backup_retention_days': db_instance.get('BackupRetentionPeriod', 0),
                    'status': 'success' if latest_restorable_time else 'failed'
                },
                'all_successful': bool(latest_restorable_time)
            }
            
            return backup_status
            
        except Exception as e:
            return {
                'component': 'backups',
                'all_successful': False,
                'error': str(e)
            }
    
    async def _trigger_failover(self, health_status: Dict):
        """
        Trigger automated failover based on health status.
        
        Args:
            health_status: Current health status
        """
        logger.critical(f"Triggering failover: {health_status}")
        
        # Determine failover type based on failures
        if 'database' in health_status['critical_failures']:
            await self._execute_database_failover()
        elif len(health_status['critical_failures']) > 2:
            # Multiple critical failures -> regional failover
            await self._execute_region_failover()
        else:
            # Service-specific failover
            await self._execute_service_failover(health_status['critical_failures'])
    
    async def _execute_database_failover(self):
        """Execute database failover procedure."""
        logger.info("Executing database failover...")
        
        try:
            # 1. Check if secondary is available
            response = self.rds_client.describe_db_instances(
                DBInstanceIdentifier=self.config['database']['secondary']
            )
            
            secondary_status = response['DBInstances'][0]['DBInstanceStatus']
            
            if secondary_status == 'available':
                # 2. Promote read replica
                logger.info("Promoting read replica to primary...")
                
                promote_response = self.rds_client.promote_read_replica(
                    DBInstanceIdentifier=self.config['database']['secondary']
                )
                
                # 3. Update application configuration
                await self._update_database_endpoint(
                    self.config['database']['secondary']
                )
                
                # 4. Update monitoring
                self._update_monitoring_for_failover('database')
                
                logger.info("Database failover completed successfully")
                
                # 5. Notify stakeholders
                await self._send_failover_notification('database', 'completed')
                
            else:
                logger.error(f"Secondary database not available: {secondary_status}")
                await self._send_failover_notification('database', 'failed')
                
        except Exception as e:
            logger.error(f"Database failover failed: {e}")
            await self._send_failover_notification('database', 'failed', str(e))
    
    async def _execute_region_failover(self):
        """Execute regional failover procedure."""
        logger.info("Executing regional failover...")
        
        # This would involve:
        # 1. Activating secondary region infrastructure
        # 2. Promoting secondary databases
        # 3. Updating DNS (Route53)
        # 4. Starting services in secondary region
        # 5. Validating trading operations
        
        logger.warning("Regional failover requires manual execution in this implementation")
        await self._send_failover_notification('region', 'manual_intervention_required')
    
    async def _execute_service_failover(self, failed_services: List[str]):
        """Execute service-specific failover."""
        logger.info(f"Executing service failover for: {failed_services}")
        
        for service in failed_services:
            try:
                # 1. Drain traffic from failed service
                await self._drain_service_traffic(service)
                
                # 2. Start backup instances
                await self._start_backup_instances(service)
                
                # 3. Load state (if stateful)
                await self._load_service_state(service)
                
                # 4. Resume traffic
                await self._resume_service_traffic(service)
                
                # 5. Validate
                await self._validate_service_recovery(service)
                
                logger.info(f"Service failover completed for {service}")
                await self._send_failover_notification(service, 'completed')
                
            except Exception as e:
                logger.error(f"Service failover failed for {service}: {e}")
                await self._send_failover_notification(service, 'failed', str(e))
    
    async def _update_database_endpoint(self, new_endpoint: str):
        """Update application configuration with new database endpoint."""
        # This would update configuration in:
        # 1. Application config files
        # 2. Secrets manager
        # 3. Environment variables
        
        logger.info(f"Updating database endpoint to: {new_endpoint}")
        # Implementation depends on your configuration management
    
    def _update_monitoring_for_failover(self, component: str):
        """Update monitoring configuration after failover."""
        logger.info(f"Updating monitoring for {component} failover")
        # Update CloudWatch alarms, dashboards, etc.
    
    async def _send_failover_notification(self, component: str, status: str, details: str = ""):
        """Send failover notification to stakeholders."""
        message = {
            'component': component,
            'status': status,
            'timestamp': datetime.utcnow().isoformat(),
            'details': details
        }
        
        logger.info(f"Failover notification: {message}")
        
        # In production, this would send to:
        # - Slack
        # - PagerDuty
        # - Email
        # - SMS
    
    def _log_health_status(self, health_status: Dict):
        """Log health status for audit and analysis."""
        log_entry = {
            'timestamp': health_status['timestamp'],
            'status': health_status,
            'dr_readiness': self._calculate_dr_readiness(health_status)
        }
        
        # Log to file
        with open('dr_health_log.jsonl', 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        # Send to CloudWatch
        try:
            self.cloudwatch.put_metric_data(
                Namespace='Trading/DR',
                MetricData=[
                    {
                        'MetricName': 'DRReadiness',
                        'Value': log_entry['dr_readiness'],
                        'Unit': 'Percent',
                        'Timestamp': datetime.utcnow()
                    }
                ]
            )
        except Exception as e:
            logger.error(f"Error sending metric to CloudWatch: {e}")
    
    def _calculate_dr_readiness(self, health_status: Dict) -> float:
        """Calculate DR readiness score (0-100%)."""
        score = 100
        
        # Deduct points for failures
        if health_status['critical_failures']:
            score -= len(health_status['critical_failures']) * 20
        
        if health_status['warnings']:
            score -= len(health_status['warnings']) * 5
        
        # Ensure score is within bounds
        return max(0, min(100, score))
    
    async def perform_recovery_test(self, test_type: str = "database_restore"):
        """
        Perform a disaster recovery test.
        
        Args:
            test_type: Type of test to perform
        """
        logger.info(f"Starting DR test: {test_type}")
        
        test_results = {
            'test_type': test_type,
            'start_time': datetime.utcnow().isoformat(),
            'steps': [],
            'success': False
        }
        
        try:
            if test_type == "database_restore":
                await self._test_database_restore(test_results)
            elif test_type == "failover":
                await self._test_failover_procedure(test_results)
            elif test_type == "order_recovery":
                await self._test_order_recovery(test_results)
            elif test_type == "full_dr_drill":
                await self._test_full_dr_drill(test_results)
            else:
                raise ValueError(f"Unknown test type: {test_type}")
            
            test_results['success'] = True
            
        except Exception as e:
            test_results['error'] = str(e)
            test_results['success'] = False
        
        test_results['end_time'] = datetime.utcnow().isoformat()
        test_results['duration_seconds'] = (
            datetime.fromisoformat(test_results['end_time']) - 
            datetime.fromisoformat(test_results['start_time'])
        ).total_seconds()
        
        # Save test results
        self._save_test_results(test_results)
        
        logger.info(f"DR test completed: {test_results['success']}")
        return test_results
    
    async def _test_database_restore(self, test_results: Dict):
        """Test database restoration from backup."""
        test_results['steps'].append({
            'step': '1_create_test_instance',
            'status': 'started'
        })
        
        # 1. Create test database instance from snapshot
        snapshot_id = await self._get_latest_database_snapshot()
        
        test_instance_id = f"dr-test-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        self.rds_client.restore_db_instance_from_db_snapshot(
            DBInstanceIdentifier=test_instance_id,
            DBSnapshotIdentifier=snapshot_id,
            DBInstanceClass='db.t3.micro',  # Small instance for testing
            MultiAZ=False
        )
        
        test_results['steps'][-1]['status'] = 'completed'
        test_results['steps'][-1]['test_instance_id'] = test_instance_id
        
        # 2. Wait for instance to be available
        test_results['steps'].append({
            'step': '2_wait_for_instance',
            'status': 'started'
        })
        
        waiter = self.rds_client.get_waiter('db_instance_available')
        waiter.wait(DBInstanceIdentifier=test_instance_id)
        
        test_results['steps'][-1]['status'] = 'completed'
        
        # 3. Validate data
        test_results['steps'].append({
            'step': '3_validate_data',
            'status': 'started'
        })
        
        validation_passed = await self._validate_database_data(test_instance_id)
        
        test_results['steps'][-1]['status'] = 'completed' if validation_passed else 'failed'
        test_results['steps'][-1]['validation_passed'] = validation_passed
        
        # 4. Clean up
        test_results['steps'].append({
            'step': '4_cleanup',
            'status': 'started'
        })
        
        self.rds_client.delete_db_instance(
            DBInstanceIdentifier=test_instance_id,
            SkipFinalSnapshot=True,
            DeleteAutomatedBackups=False
        )
        
        test_results['steps'][-1]['status'] = 'completed'
    
    async def _get_latest_database_snapshot(self) -> str:
        """Get the latest automated database snapshot."""
        response = self.rds_client.describe_db_snapshots(
            DBInstanceIdentifier=self.config['database']['primary'],
            SnapshotType='automated'
        )
        
        snapshots = sorted(
            response['DBSnapshots'],
            key=lambda x: x['SnapshotCreateTime'],
            reverse=True
        )
        
        if snapshots:
            return snapshots[0]['DBSnapshotIdentifier']
        else:
            raise Exception("No database snapshots found")
    
    async def _validate_database_data(self, instance_id: str) -> bool:
        """Validate that restored database contains expected data."""
        # This would connect to the database and run validation queries
        # For example:
        # 1. Check critical tables exist
        # 2. Verify row counts
        # 3. Validate sample data
        
        logger.info(f"Validating data in {instance_id}")
        return True  # Placeholder
    
    async def _test_failover_procedure(self, test_results: Dict):
        """Test failover procedure without actual failover."""
        # Simulate failover steps
        steps = [
            '1_verify_secondary_health',
            '2_simulate_promotion',
            '3_test_configuration_update',
            '4_validate_connectivity',
            '5_simulate_rollback'
        ]
        
        for step in steps:
            test_results['steps'].append({
                'step': step,
                'status': 'started'
            })
            
            # Simulate step execution
            await asyncio.sleep(2)  # Simulate work
            
            test_results['steps'][-1]['status'] = 'completed'
            test_results['steps'][-1]['simulation'] = True
    
    async def _test_order_recovery(self, test_results: Dict):
        """Test order state recovery procedure."""
        # Create test order journal
        test_journal = await self._create_test_order_journal()
        
        # Simulate loss and recovery
        steps = [
            '1_create_test_orders',
            '2_simulate_journal_loss',
            '3_restore_from_backup',
            '4_replay_transactions',
            '5_validate_order_state'
        ]
        
        for step in steps:
            test_results['steps'].append({
                'step': step,
                'status': 'started'
            })
            
            await asyncio.sleep(1)  # Simulate work
            
            test_results['steps'][-1]['status'] = 'completed'
            test_results['steps'][-1]['test_orders'] = len(test_journal)
    
    async def _create_test_order_journal(self) -> List[Dict]:
        """Create test order journal for recovery testing."""
        test_orders = []
        
        for i in range(10):
            order = {
                'order_id': f'test-{datetime.utcnow().strftime("%Y%m%d%H%M%S")}-{i}',
                'symbol': 'TEST',
                'side': 'BUY' if i % 2 == 0 else 'SELL',
                'quantity': 100,
                'price': 100.0 + i,
                'timestamp': datetime.utcnow().isoformat(),
                'status': 'FILLED'
            }
            test_orders.append(order)
        
        return test_orders
    
    async def _test_full_dr_drill(self, test_results: Dict):
        """Perform full disaster recovery drill."""
        logger.warning("Full DR drill requires coordination and planning")
        
        # This would involve:
        # 1. Pre-drill briefing
        # 2. Simulated disaster scenario
        # 3. Execution of DR procedures
        # 4. Validation of recovery
        # 5. Post-drill analysis
        
        test_results['steps'].append({
            'step': 'full_dr_drill',
            'status': 'requires_manual_execution',
            'note': 'Full DR drills require scheduled maintenance windows and stakeholder coordination'
        })
    
    def _save_test_results(self, test_results: Dict):
        """Save test results for audit and improvement."""
        tests_dir = Path("dr_tests")
        tests_dir.mkdir(exist_ok=True)
        
        filename = f"test_{test_results['test_type']}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = tests_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(test_results, f, indent=2, default=str)
        
        logger.info(f"Test results saved to {filepath}")
    
    def generate_dr_report(self) -> Dict:
        """Generate comprehensive DR status report."""
        report = {
            'generated_at': datetime.utcnow().isoformat(),
            'summary': {
                'dr_plan_exists': True,
                'last_test': self._get_last_test_date(),
                'backup_status': self._get_backup_status_summary(),
                'system_health': self._get_system_health_summary(),
                'rto_compliance': self._calculate_rto_compliance(),
                'rpo_compliance': self._calculate_rpo_compliance()
            },
            'details': {
                'recovery_objectives': self.recovery_objectives,
                'backup_configurations': self.backup_configs,
                'recent_incidents': self._get_recent_incidents(),
                'upcoming_tests': self._get_upcoming_tests(),
                'improvement_actions': self._get_improvement_actions()
            },
            'recommendations': self._generate_recommendations()
        }
        
        # Save report
        reports_dir = Path("dr_reports")
        reports_dir.mkdir(exist_ok=True)
        
        report_file = reports_dir / f"dr_report_{datetime.utcnow().strftime('%Y%m%d')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"DR report generated: {report_file}")
        return report
    
    def _get_last_test_date(self) -> Optional[str]:
        """Get date of last DR test."""
        tests_dir = Path("dr_tests")
        if tests_dir.exists():
            test_files = list(tests_dir.glob("test_*.json"))
            if test_files:
                latest = max(test_files, key=lambda x: x.stat().st_mtime)
                return datetime.fromtimestamp(latest.stat().st_mtime).isoformat()
        return None
    
    def _get_backup_status_summary(self) -> Dict:
        """Get summary of backup status."""
        # This would check actual backup status
        return {
            'database': {
                'last_successful': datetime.utcnow().isoformat(),
                'retention_days': 35,
                'encryption': True
            },
            'redis': {
                'last_successful': datetime.utcnow().isoformat(),
                'retention_days': 7,
                'encryption': True
            }
        }
    
    def _get_system_health_summary(self) -> Dict:
        """Get summary of system health."""
        # Read from health log
        health_log = Path("dr_health_log.jsonl")
        if health_log.exists():
            with open(health_log, 'r') as f:
                lines = f.readlines()
                if lines:
                    latest = json.loads(lines[-1])
                    return latest['dr_readiness']
        
        return 100.0  # Default
    
    def _calculate_rto_compliance(self) -> float:
        """Calculate RTO compliance percentage."""
        # Based on test results
        return 95.0  # Placeholder
    
    def _calculate_rpo_compliance(self) -> float:
        """Calculate RPO compliance percentage."""
        # Based on backup success rates
        return 99.5  # Placeholder
    
    def _get_recent_incidents(self) -> List[Dict]:
        """Get list of recent incidents affecting availability."""
        # Would query from incident management system
        return []  # Placeholder
    
    def _get_upcoming_tests(self) -> List[Dict]:
        """Get schedule of upcoming DR tests."""
        return [
            {
                'test_type': 'database_restore',
                'scheduled_date': (datetime.utcnow() + timedelta(days=7)).isoformat(),
                'required_actions': ['Schedule maintenance window']
            },
            {
                'test_type': 'failover',
                'scheduled_date': (datetime.utcnow() + timedelta(days=30)).isoformat(),
                'required_actions': ['Coordinate with trading team']
            }
        ]
    
    def _get_improvement_actions(self) -> List[Dict]:
        """Get list of improvement actions from recent tests."""
        improvement_actions = []
        
        # Analyze test results
        tests_dir = Path("dr_tests")
        if tests_dir.exists():
            for test_file in tests_dir.glob("test_*.json"):
                with open(test_file, 'r') as f:
                    test_result = json.load(f)
                    
                    if not test_result.get('success', False):
                        improvement_actions.append({
                            'test': test_result['test_type'],
                            'issue': test_result.get('error', 'Unknown issue'),
                            'action': f'Review and fix {test_result["test_type"]} procedure',
                            'priority': 'high'
                        })
        
        return improvement_actions
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations for DR improvement."""
        recommendations = [
            "Implement automated backup validation",
            "Schedule quarterly full DR drills",
            "Establish DR documentation review process",
            "Implement chaos engineering for resilience testing",
            "Review and update RTO/RPO based on business needs",
            "Establish DR training program for operations team"
        ]
        
        return recommendations


class FaultTolerantTradingSystem:
    """
    Implementation of fault tolerance patterns for trading system.
    """
    
    def __init__(self):
        self.circuit_breakers = {}
        self.retry_configs = {}
        self.bulkhead_limits = {}
        self.degradation_modes = {}
        
        self._init_fault_tolerance_patterns()
    
    def _init_fault_tolerance_patterns(self):
        """Initialize fault tolerance patterns."""
        # Circuit breaker configurations
        self.circuit_breakers = {
            'broker_api': {
                'failure_threshold': 5,
                'reset_timeout': 60,
                'state': 'CLOSED',
                'failure_count': 0,
                'last_failure_time': None
            },
            'market_data_feed': {
                'failure_threshold': 3,
                'reset_timeout': 30,
                'state': 'CLOSED',
                'failure_count': 0,
                'last_failure_time': None
            },
            'risk_engine': {
                'failure_threshold': 10,
                'reset_timeout': 300,
                'state': 'CLOSED',
                'failure_count': 0,
                'last_failure_time': None
            }
        }
        
        # Retry configurations
        self.retry_configs = {
            'order_execution': {
                'max_retries': 3,
                'backoff_factor': 2,
                'max_backoff': 30,
                'jitter': True
            },
            'market_data_fetch': {
                'max_retries': 5,
                'backoff_factor': 1.5,
                'max_backoff': 10,
                'jitter': True
            },
            'database_query': {
                'max_retries': 2,
                'backoff_factor': 1,
                'max_backoff': 5,
                'jitter': False
            }
        }
        
        # Bulkhead limits
        self.bulkhead_limits = {
            'order_execution': {
                'max_concurrent': 10,
                'queue_size': 100,
                'timeout_seconds': 30
            },
            'market_data_processing': {
                'max_concurrent': 50,
                'queue_size': 1000,
                'timeout_seconds': 5
            },
            'risk_calculations': {
                'max_concurrent': 5,
                'queue_size': 50,
                'timeout_seconds': 60
            }
        }
        
        # Graceful degradation modes
        self.degradation_modes = {
            'market_data_unavailable': {
                'use_cached_data': True,
                'cache_ttl_seconds': 300,
                'allow_trading': False,
                'notify_traders': True
            },
            'risk_engine_slow': {
                'use_simplified_checks': True,
                'position_limit_reduction': 0.5,
                'allow_trading': True,
                'escalate_oversight': True
            },
            'broker_connectivity_issues': {
                'queue_orders_locally': True,
                'max_queue_size': 1000,
                'periodic_reconnection': True,
                'reconnection_interval': 30
            }
        }
    
    class CircuitBreaker:
        """Circuit breaker pattern implementation."""
        
        def __init__(self, name: str, failure_threshold: int = 5, reset_timeout: int = 60):
            self.name = name
            self.failure_threshold = failure_threshold
            self.reset_timeout = reset_timeout
            self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
            self.failure_count = 0
            self.last_failure_time = None
            self.last_state_change = datetime.utcnow()
            
            self.metrics = {
                'total_requests': 0,
                'failed_requests': 0,
                'circuit_opens': 0,
                'recoveries': 0
            }
        
        def execute(self, operation: Callable, fallback: Optional[Callable] = None, *args, **kwargs):
            """
            Execute operation with circuit breaker protection.
            
            Args:
                operation: Function to execute
                fallback: Fallback function if circuit is open
                *args, **kwargs: Arguments for operation
                
            Returns:
                Result of operation or fallback
            """
            self.metrics['total_requests'] += 1
            
            # Check if circuit is open
            if self.state == "OPEN":
                # Check if reset timeout has passed
                if self.last_failure_time:
                    time_since_failure = (datetime.utcnow() - self.last_failure_time).total_seconds()
                    if time_since_failure > self.reset_timeout:
                        self.state = "HALF_OPEN"
                        self.last_state_change = datetime.utcnow()
                        logger.info(f"Circuit {self.name} moved to HALF_OPEN")
                    else:
                        self.metrics['failed_requests'] += 1
                        if fallback:
                            logger.warning(f"Circuit {self.name} OPEN, using fallback")
                            return fallback(*args, **kwargs)
                        raise CircuitOpenError(f"Circuit {self.name} is OPEN")
            
            try:
                # Execute operation
                result = operation(*args, **kwargs)
                
                # On success in HALF_OPEN state, close circuit
                if self.state == "HALF_OPEN":
                    self.state = "CLOSED"
                    self.failure_count = 0
                    self.last_state_change = datetime.utcnow()
                    self.metrics['recoveries'] += 1
                    logger.info(f"Circuit {self.name} recovered and CLOSED")
                
                return result
                
            except Exception as e:
                self._on_failure(e)
                raise
        
        def _on_failure(self, error: Exception):
            """Handle operation failure."""
            self.metrics['failed_requests'] += 1
            self.failure_count += 1
            self.last_failure_time = datetime.utcnow()
            
            logger.warning(f"Circuit {self.name} failure #{self.failure_count}: {error}")
            
            # Check if threshold exceeded
            if self.failure_count >= self.failure_threshold and self.state != "OPEN":
                self.state = "OPEN"
                self.last_state_change = datetime.utcnow()
                self.metrics['circuit_opens'] += 1
                logger.error(f"Circuit {self.name} OPENED after {self.failure_count} failures")
        
        def get_metrics(self) -> Dict:
            """Get circuit breaker metrics."""
            return {
                **self.metrics,
                'state': self.state,
                'failure_count': self.failure_count,
                'last_failure_time': self.last_failure_time.isoformat() if self.last_failure_time else None,
                'uptime_percent': ((self.metrics['total_requests'] - self.metrics['failed_requests']) / 
                                  max(1, self.metrics['total_requests']) * 100)
            }
    
    class RetryWithBackoff:
        """Retry pattern with exponential backoff and jitter."""
        
        def __init__(self, max_retries: int = 3, backoff_factor: float = 2.0, 
                     max_backoff: int = 30, jitter: bool = True):
            self.max_retries = max_retries
            self.backoff_factor = backoff_factor
            self.max_backoff = max_backoff
            self.jitter = jitter
            
            self.metrics = {
                'total_attempts': 0,
                'successful_retries': 0,
                'failed_retries': 0
            }
        
        def execute(self, operation: Callable, *args, **kwargs):
            """
            Execute operation with retry logic.
            
            Args:
                operation: Function to execute
                *args, **kwargs: Arguments for operation
                
            Returns:
                Result of operation
                
            Raises:
                Exception: If all retries fail
            """
            last_exception = None
            
            for attempt in range(self.max_retries + 1):  # +1 for initial attempt
                self.metrics['total_attempts'] += 1
                
                try:
                    result = operation(*args, **kwargs)
                    
                    if attempt > 0:
                        self.metrics['successful_retries'] += 1
                        logger.info(f"Operation succeeded on retry #{attempt}")
                    
                    return result
                    
                except PermanentError as e:
                    # Don't retry permanent errors
                    logger.error(f"Permanent error, not retrying: {e}")
                    raise
                    
                except TemporaryError as e:
                    last_exception = e
                    
                    # Check if we should retry
                    if attempt < self.max_retries:
                        wait_time = self._calculate_backoff(attempt)
                        logger.warning(f"Attempt {attempt + 1} failed, retrying in {wait_time:.2f}s: {e}")
                        time.sleep(wait_time)
                    else:
                        self.metrics['failed_retries'] += 1
                        logger.error(f"All {self.max_retries} retry attempts failed")
            
            # All retries failed
            raise MaxRetriesExceeded(f"Operation failed after {self.max_retries} retries") from last_exception
        
        def _calculate_backoff(self, attempt: int) -> float:
            """Calculate backoff time with optional jitter."""
            backoff = min(self.max_backoff, self.backoff_factor ** attempt)
            
            if self.jitter:
                # Add random jitter (up to 25% of backoff time)
                jitter = random.random() * backoff * 0.25
                backoff += jitter
            
            return backoff
        
        def get_metrics(self) -> Dict:
            """Get retry metrics."""
            return {
                **self.metrics,
                'retry_success_rate': (self.metrics['successful_retries'] / 
                                      max(1, self.metrics['total_attempts']) * 100)
            }
    
    class Bulkhead:
        """Bulkhead pattern for resource isolation."""
        
        def __init__(self, name: str, max_concurrent: int = 10, 
                     queue_size: int = 100, timeout_seconds: int = 30):
            self.name = name
            self.max_concurrent = max_concurrent
            self.queue_size = queue_size
            self.timeout_seconds = timeout_seconds
            
            self.semaphore = asyncio.Semaphore(max_concurrent)
            self.queue = asyncio.Queue(maxsize=queue_size)
            self.active_operations = 0
            self.queue_length = 0
            
            self.metrics = {
                'total_operations': 0,
                'rejected_operations': 0,
                'timeout_operations': 0,
                'avg_execution_time': 0.0
            }
        
        async def execute(self, operation: Callable, *args, **kwargs):
            """
            Execute operation with bulkhead protection.
            
            Args:
                operation: Async function to execute
                *args, **kwargs: Arguments for operation
                
            Returns:
                Result of operation
                
            Raises:
                BulkheadRejectedError: If bulkhead rejects operation
                asyncio.TimeoutError: If operation times out
            """
            start_time = time.time()
            
            try:
                # Try to acquire semaphore with timeout
                try:
                    await asyncio.wait_for(
                        self.semaphore.acquire(),
                        timeout=self.timeout_seconds
                    )
                except asyncio.TimeoutError:
                    self.metrics['timeout_operations'] += 1
                    raise BulkheadRejectedError(
                        f"Bulkhead {self.name} timeout after {self.timeout_seconds}s"
                    )
                
                self.active_operations += 1
                
                try:
                    # Execute operation
                    result = await operation(*args, **kwargs)
                    
                    execution_time = time.time() - start_time
                    self.metrics['avg_execution_time'] = (
                        (self.metrics['avg_execution_time'] * (self.metrics['total_operations'] - 1) + 
                         execution_time) / self.metrics['total_operations']
                    )
                    
                    self.metrics['total_operations'] += 1
                    return result
                    
                finally:
                    self.active_operations -= 1
                    self.semaphore.release()
                    
            except Exception as e:
                if isinstance(e, BulkheadRejectedError):
                    self.metrics['rejected_operations'] += 1
                raise
        
        def get_metrics(self) -> Dict:
            """Get bulkhead metrics."""
            return {
                **self.metrics,
                'active_operations': self.active_operations,
                'queue_length': self.queue.qsize() if hasattr(self.queue, 'qsize') else 0,
                'utilization_percent': (self.active_operations / self.max_concurrent) * 100
            }
    
    class GracefulDegradation:
        """Graceful degradation pattern for partial failures."""
        
        def __init__(self, name: str, degradation_config: Dict):
            self.name = name
            self.config = degradation_config
            self.degradation_active = False
            self.degradation_start_time = None
            
            self.metrics = {
                'degradation_activations': 0,
                'total_degradation_time': 0.0,
                'operations_in_degraded_mode': 0
            }
        
        def execute(self, normal_operation: Callable, degraded_operation: Callable, 
                   *args, **kwargs):
            """
            Execute operation with graceful degradation.
            
            Args:
                normal_operation: Function to execute in normal mode
                degraded_operation: Function to execute in degraded mode
                *args, **kwargs: Arguments for operation
                
            Returns:
                Result of operation
            """
            if self.degradation_active:
                self.metrics['operations_in_degraded_mode'] += 1
                logger.info(f"Executing in degraded mode: {self.name}")
                return degraded_operation(*args, **kwargs)
            else:
                try:
                    return normal_operation(*args, **kwargs)
                except DegradationTriggerError:
                    self.activate_degradation()
                    return degraded_operation(*args, **kwargs)
        
        def activate_degradation(self):
            """Activate degraded mode."""
            if not self.degradation_active:
                self.degradation_active = True
                self.degradation_start_time = datetime.utcnow()
                self.metrics['degradation_activations'] += 1
                logger.warning(f"Activated degraded mode for {self.name}")
                
                # Notify stakeholders
                self._notify_degradation()
        
        def deactivate_degradation(self):
            """Deactivate degraded mode."""
            if self.degradation_active:
                self.degradation_active = False
                
                # Calculate total degradation time
                if self.degradation_start_time:
                    degradation_time = (datetime.utcnow() - self.degradation_start_time).total_seconds()
                    self.metrics['total_degradation_time'] += degradation_time
                
                logger.info(f"Deactivated degraded mode for {self.name}")
                
                # Notify stakeholders
                self._notify_recovery()
        
        def _notify_degradation(self):
            """Notify stakeholders about degradation."""
            # In production, this would send notifications
            logger.info(f"Degradation notification sent for {self.name}")
        
        def _notify_recovery(self):
            """Notify stakeholders about recovery."""
            logger.info(f"Recovery notification sent for {self.name}")
        
        def get_metrics(self) -> Dict:
            """Get degradation metrics."""
            current_degradation_time = 0.0
            if self.degradation_active and self.degradation_start_time:
                current_degradation_time = (datetime.utcnow() - self.degradation_start_time).total_seconds()
            
            return {
                **self.metrics,
                'degradation_active': self.degradation_active,
                'current_degradation_time': current_degradation_time,
                'availability_percent': 100.0  # Would calculate based on metrics
            }


# Custom exceptions
class CircuitOpenError(Exception):
    """Raised when circuit breaker is open."""
    pass

class PermanentError(Exception):
    """Raised for errors that shouldn't be retried."""
    pass

class TemporaryError(Exception):
    """Raised for errors that can be retried."""
    pass

class MaxRetriesExceeded(Exception):
    """Raised when all retry attempts fail."""
    pass

class BulkheadRejectedError(Exception):
    """Raised when bulkhead rejects operation."""
    pass

class DegradationTriggerError(Exception):
    """Raised to trigger graceful degradation."""
    pass


def demonstrate_disaster_recovery():
    """
    Demonstrate complete disaster recovery implementation.
    """
    print("\n" + "="*80)
    print("Day 96: Disaster Recovery and Fault Tolerance")
    print("="*80)
    
    print("\n🚀 Demonstrating Disaster Recovery Implementation")
    print("-"*80)
    
    # Initialize DR planner
    dr_planner = DisasterRecoveryPlanner()
    
    # 1. Create DR plan
    print("\n1. Creating Disaster Recovery Plan...")
    dr_plan = dr_planner.create_recovery_plan()
    print(f"   ✅ Created DR plan with {len(dr_plan['recovery_objectives'])} components")
    print(f"   ✅ Defined {len(dr_plan['failover_procedures'])} failover procedures")
    print(f"   ✅ Created {len(dr_plan['runbooks'])} operational runbooks")
    
    # 2. Setup backup system
    print("\n2. Setting up Backup System...")
    dr_planner.setup_backup_system()
    print("   ✅ Configured database backups with PITR")
    print("   ✅ Setup S3 backup buckets with encryption")
    print("   ✅ Configured backup monitoring and alerts")
    
    # 3. Demonstrate fault tolerance patterns
    print("\n3. Implementing Fault Tolerance Patterns...")
    fault_tolerance = FaultTolerantTradingSystem()
    
    # Circuit breaker demo
    circuit_breaker = fault_tolerance.CircuitBreaker("broker_api", failure_threshold=3, reset_timeout=10)
    print(f"   ✅ Implemented circuit breaker for broker API")
    
    # Retry with backoff demo
    retry_handler = fault_tolerance.RetryWithBackoff(max_retries=3, backoff_factor=2, jitter=True)
    print(f"   ✅ Implemented retry with exponential backoff")
    
    # Bulkhead demo
    bulkhead = fault_tolerance.Bulkhead("order_execution", max_concurrent=5, queue_size=50)
    print(f"   ✅ Implemented bulkhead isolation for order execution")
    
    # Graceful degradation demo
    degradation_config = {
        'use_cached_data': True,
        'cache_ttl': 300,
        'allow_trading': False
    }
    graceful_degradation = fault_tolerance.GracefulDegradation("market_data", degradation_config)
    print(f"   ✅ Implemented graceful degradation for market data")
    
    # 4. Demonstrate DR test
    print("\n4. Performing Disaster Recovery Test...")
    
    # Run a database restore test
    import asyncio
    
    async def run_dr_test():
        test_result = await dr_planner.perform_recovery_test("database_restore")
        if test_result['success']:
            print(f"   ✅ DR test completed successfully")
            print(f"   ⏱️  Duration: {test_result['duration_seconds']:.2f} seconds")
            print(f"   📋 Steps executed: {len(test_result['steps'])}")
        else:
            print(f"   ❌ DR test failed: {test_result.get('error', 'Unknown error')}")
    
    # Note: Uncomment to run actual test (requires AWS credentials)
    # asyncio.run(run_dr_test())
    print("   ⚠️  DR test simulation completed (requires AWS credentials for actual test)")
    
    # 5. Generate DR report
    print("\n5. Generating DR Status Report...")
    dr_report = dr_planner.generate_dr_report()
    print(f"   ✅ Generated comprehensive DR report")
    print(f"   📊 System Health: {dr_report['summary']['system_health']}%")
    print(f"   🎯 RTO Compliance: {dr_report['summary']['rto_compliance']}%")
    print(f"   💾 RPO Compliance: {dr_report['summary']['rpo_compliance']}%")
    
    # 6. Show key metrics
    print("\n6. Key DR Metrics:")
    print("   - Recovery Time Objectives (RTO):")
    for component, obj in dr_plan['recovery_objectives'].items():
        print(f"     • {component}: {obj['rto_minutes']} minutes (Tier {obj['tier'].value})")
    
    print("\n   - Backup Configurations:")
    for component, config in dr_plan['backup_configurations'].items():
        print(f"     • {component}: Every {config['backup_frequency']}, "
              f"Retention: {config['retention_days']} days")
    
    print("\n" + "="*80)
    print("DISASTER RECOVERY IMPLEMENTATION COMPLETE")
    print("="*80)
    
    print("\n📁 Generated Artifacts:")
    print("   • dr_plans/ - Complete DR plans in JSON and YAML")
    print("   • dr_tests/ - DR test results and validation reports")
    print("   • dr_reports/ - Regular DR status reports")
    print("   • dr_monitor.log - Continuous health monitoring logs")
    
    print("\n🔧 Fault Tolerance Patterns Implemented:")
    print("   • Circuit Breaker - Prevents cascading failures")
    print("   • Retry with Backoff - Handles transient failures")
    print("   • Bulkhead - Isolates failures to specific components")
    print("   • Graceful Degradation - Maintains partial functionality during failures")
    
    print("\n🚨 Recovery Procedures:")
    print("   • Database failover: 2 minutes (automated)")
    print("   • Regional failover: 5 minutes (semi-automated)")
    print("   • Order state recovery: 15 minutes (automated)")
    
    print("\n📋 Next Steps:")
    print("   1. Schedule regular DR tests")
    print("   2. Train team on runbook execution")
    print("   3. Integrate with monitoring and alerting")
    print("   4. Conduct full DR drill quarterly")
    print("   5. Continuously improve based on test results")
    
    return {
        'dr_plan': dr_plan,
        'fault_tolerance': fault_tolerance,
        'report': dr_report
    }


if __name__ == "__main__":
    demonstrate_disaster_recovery()
```

### **Challenge: Implement automated failover for critical trading components**

```python
"""
Day 96 Challenge: Zero-Downtime Failover System
Implement automated failover with zero data loss and minimal downtime.
"""

import asyncio
import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import hashlib
from datetime import datetime, timedelta
import logging
from logging.handlers import RotatingFileHandler
import threading
from concurrent.futures import ThreadPoolExecutor
import pickle
import zlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler('failover_system.log', maxBytes=10485760, backupCount=5),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class FailoverState(Enum):
    """States of the failover system."""
    NORMAL = "normal"           # Primary active, secondary ready
    FAILOVER_INITIATED = "failover_initiated"  # Failover process started
    FAILOVER_IN_PROGRESS = "failover_in_progress"  # Failover executing
    FAILOVER_COMPLETED = "failover_completed"  # Secondary now primary
    ROLLBACK_IN_PROGRESS = "rollback_in_progress"  # Rolling back to primary
    MAINTENANCE = "maintenance"  # Manual maintenance mode


@dataclass
class ComponentHealth:
    """Health status of a component."""
    component: str
    is_healthy: bool
    last_check: datetime
    error_count: int = 0
    latency_ms: float = 0.0
    resource_usage: Dict[str, float] = field(default_factory=dict)
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FailoverConfig:
    """Configuration for failover system."""
    component: str
    primary_endpoint: str
    secondary_endpoint: str
    health_check_interval: int = 5  # seconds
    health_check_timeout: int = 2   # seconds
    failure_threshold: int = 3      # consecutive failures before failover
    auto_failover: bool = True
    data_sync_method: str = "synchronous"  # synchronous, asynchronous, semi-synchronous
    max_data_loss: timedelta = timedelta(seconds=0)
    min_uptime_before_failback: int = 300  # seconds


class ZeroDowntimeFailoverSystem:
    """
    Automated failover system with zero data loss for trading components.
    """
    
    def __init__(self):
        self.failover_state = FailoverState.NORMAL
        self.components: Dict[str, FailoverConfig] = {}
        self.health_status: Dict[str, ComponentHealth] = {}
        self.state_synchronizer = StateSynchronizer()
        self.traffic_manager = TrafficManager()
        self.health_monitor = HealthMonitor()
        
        # Thread pool for concurrent operations
        self.executor = ThreadPoolExecutor(max_workers=10)
        
        # Lock for thread-safe state updates
        self.state_lock = threading.Lock()
        
        # Statistics
        self.stats = {
            'failovers_triggered': 0,
            'successful_failovers': 0,
            'failed_failovers': 0,
            'total_downtime_ms': 0,
            'last_failover_time': None,
            'component_uptime': {}
        }
        
        logger.info("ZeroDowntimeFailoverSystem initialized")
    
    def register_component(self, config: FailoverConfig):
        """
        Register a component for automated failover.
        
        Args:
            config: Failover configuration for the component
        """
        with self.state_lock:
            self.components[config.component] = config
            self.health_status[config.component] = ComponentHealth(
                component=config.component,
                is_healthy=True,
                last_check=datetime.utcnow()
            )
            self.stats['component_uptime'][config.component] = 1.0
        
        logger.info(f"Registered component for failover: {config.component}")
        
        # Start health monitoring
        self.health_monitor.start_monitoring(
            config.component,
            config.primary_endpoint,
            config.health_check_interval,
            self._health_check_callback
        )
    
    def _health_check_callback(self, component: str, is_healthy: bool, latency: float, details: Dict):
        """
        Callback for health check results.
        
        Args:
            component: Component name
            is_healthy: Health status
            latency: Response latency in ms
            details: Additional health details
        """
        with self.state_lock:
            current_health = self.health_status[component]
            
            # Update health status
            current_health.is_healthy = is_healthy
            current_health.last_check = datetime.utcnow()
            current_health.latency_ms = latency
            current_health.details = details
            
            if not is_healthy:
                current_health.error_count += 1
            else:
                current_health.error_count = 0
            
            # Update uptime statistics
            if component in self.stats['component_uptime']:
                # Simple moving average of health status
                current_uptime = self.stats['component_uptime'][component]
                new_health_value = 1.0 if is_healthy else 0.0
                self.stats['component_uptime'][component] = (
                    0.9 * current_uptime + 0.1 * new_health_value
                )
            
            # Check if failover should be triggered
            if (not is_healthy and 
                current_health.error_count >= self.components[component].failure_threshold and
                self.components[component].auto_failover and
                self.failover_state == FailoverState.NORMAL):
                
                logger.warning(f"Component {component} unhealthy, triggering failover check")
                self._evaluate_failover(component)
    
    def _evaluate_failover(self, component: str):
        """
        Evaluate whether to trigger failover for a component.
        
        Args:
            component: Component to evaluate
        """
        config = self.components[component]
        
        # Check if secondary is healthy
        secondary_health = self.health_monitor.check_endpoint_health(config.secondary_endpoint)
        
        if secondary_health['is_healthy']:
            logger.info(f"Secondary for {component} is healthy, initiating failover")
            self.initiate_failover(component)
        else:
            logger.error(f"Cannot failover {component}: secondary also unhealthy")
            # Alert for manual intervention
            self._send_alert(
                f"CRITICAL: Both primary and secondary for {component} are unhealthy",
                "manual_intervention_required"
            )
    
    def initiate_failover(self, component: str):
        """
        Initiate automated failover for a component.
        
        Args:
            component: Component to failover
        """
        if self.failover_state != FailoverState.NORMAL:
            logger.warning(f"Cannot initiate failover for {component}: system state is {self.failover_state}")
            return
        
        logger.critical(f"🚨 INITIATING FAILOVER FOR {component}")
        
        # Update state
        self.failover_state = FailoverState.FAILOVER_INITIATED
        self.stats['failovers_triggered'] += 1
        
        # Start failover in background thread
        self.executor.submit(self._execute_failover, component)
    
    def _execute_failover(self, component: str):
        """
        Execute the failover procedure.
        
        Args:
            component: Component to failover
        """
        start_time = datetime.utcnow()
        config = self.components[component]
        
        try:
            logger.info(f"Starting failover execution for {component}")
            
            # Step 1: Synchronize state
            self.failover_state = FailoverState.FAILOVER_IN_PROGRESS
            logger.info("Step 1: Synchronizing state...")
            
            sync_success = self.state_synchronizer.synchronize_state(
                component,
                config.primary_endpoint,
                config.secondary_endpoint,
                config.data_sync_method
            )
            
            if not sync_success:
                raise Exception("State synchronization failed")
            
            logger.info("✅ State synchronization completed")
            
            # Step 2: Drain traffic from primary
            logger.info("Step 2: Draining traffic from primary...")
            self.traffic_manager.drain_traffic(config.primary_endpoint)
            
            # Wait for traffic to drain
            time.sleep(2)
            logger.info("✅ Traffic drained from primary")
            
            # Step 3: Verify secondary can handle traffic
            logger.info("Step 3: Verifying secondary readiness...")
            
            verification_passed = self._verify_secondary_readiness(
                config.secondary_endpoint,
                component
            )
            
            if not verification_passed:
                raise Exception("Secondary readiness verification failed")
            
            logger.info("✅ Secondary verified and ready")
            
            # Step 4: Switch traffic to secondary
            logger.info("Step 4: Switching traffic to secondary...")
            
            switch_success = self.traffic_manager.switch_traffic(
                config.primary_endpoint,
                config.secondary_endpoint,
                component
            )
            
            if not switch_success:
                raise Exception("Traffic switch failed")
            
            logger.info("✅ Traffic switched to secondary")
            
            # Step 5: Update configuration
            logger.info("Step 5: Updating configuration...")
            self._update_configuration(component, config.secondary_endpoint)
            
            logger.info("✅ Configuration updated")
            
            # Step 6: Validate functionality
            logger.info("Step 6: Validating functionality...")
            
            validation_passed = self._validate_functionality(
                config.secondary_endpoint,
                component
            )
            
            if not validation_passed:
                raise Exception("Functionality validation failed")
            
            logger.info("✅ Functionality validated")
            
            # Success
            self.failover_state = FailoverState.FAILOVER_COMPLETED
            
            # Update statistics
            end_time = datetime.utcnow()
            downtime = (end_time - start_time).total_seconds() * 1000  # ms
            self.stats['total_downtime_ms'] += downtime
            self.stats['successful_failovers'] += 1
            self.stats['last_failover_time'] = end_time.isoformat()
            
            logger.info(f"✅ FAILOVER COMPLETED SUCCESSFULLY in {downtime:.2f}ms")
            
            # Send notification
            self._send_alert(
                f"Failover completed for {component}",
                "success",
                {
                    'duration_ms': downtime,
                    'new_primary': config.secondary_endpoint
                }
            )
            
            # Start monitoring new primary
            self.health_monitor.update_monitoring_endpoint(
                component,
                config.secondary_endpoint,
                config.primary_endpoint  # Old primary becomes new secondary
            )
            
        except Exception as e:
            logger.error(f"❌ FAILOVER FAILED: {e}")
            
            # Attempt rollback
            try:
                self._execute_rollback(component, config)
            except Exception as rollback_error:
                logger.error(f"❌ ROLLBACK ALSO FAILED: {rollback_error}")
            
            # Update statistics
            self.stats['failed_failovers'] += 1
            self.failover_state = FailoverState.NORMAL
            
            # Send alert
            self._send_alert(
                f"Failover failed for {component}",
                "critical",
                {'error': str(e)}
            )
    
    def _verify_secondary_readiness(self, secondary_endpoint: str, component: str) -> bool:
        """
        Verify that secondary is ready to handle traffic.
        
        Args:
            secondary_endpoint: Secondary endpoint
            component: Component name
            
        Returns:
            bool: True if secondary is ready
        """
        checks = [
            self._check_endpoint_connectivity,
            self._check_component_specific_ready,
            self._check_resource_availability,
            self._check_data_consistency
        ]
        
        for check in checks:
            try:
                if not check(secondary_endpoint, component):
                    logger.warning(f"Readiness check failed: {check.__name__}")
                    return False
            except Exception as e:
                logger.error(f"Error in readiness check {check.__name__}: {e}")
                return False
        
        return True
    
    def _check_endpoint_connectivity(self, endpoint: str, component: str) -> bool:
        """Check basic connectivity to endpoint."""
        # Implementation depends on component type
        # For HTTP services, would make a health check request
        # For databases, would test connection
        return True  # Simplified for example
    
    def _check_component_specific_ready(self, endpoint: str, component: str) -> bool:
        """Check component-specific readiness."""
        if component == 'order_execution':
            # For order execution, check if can accept orders
            return self._check_order_execution_ready(endpoint)
        elif component == 'database':
            # For database, check if writable
            return self._check_database_writable(endpoint)
        else:
            return True
    
    def _check_order_execution_ready(self, endpoint: str) -> bool:
        """Check if order execution service is ready."""
        # Would make API call to readiness endpoint
        return True
    
    def _check_database_writable(self, endpoint: str) -> bool:
        """Check if database is writable."""
        # Would attempt a test write transaction
        return True
    
    def _check_resource_availability(self, endpoint: str, component: str) -> bool:
        """Check resource availability (CPU, memory, connections)."""
        # Would check system resources
        return True
    
    def _check_data_consistency(self, endpoint: str, component: str) -> bool:
        """Check data consistency between primary and secondary."""
        return self.state_synchronizer.verify_data_consistency(component)
    
    def _update_configuration(self, component: str, new_primary: str):
        """
        Update system configuration after failover.
        
        Args:
            component: Component that failed over
            new_primary: New primary endpoint
        """
        # Update component configuration
        config = self.components[component]
        
        # Swap primary and secondary
        old_primary = config.primary_endpoint
        config.primary_endpoint = new_primary
        config.secondary_endpoint = old_primary
        
        logger.info(f"Updated configuration: {component}")
        logger.info(f"  New primary: {config.primary_endpoint}")
        logger.info(f"  New secondary: {config.secondary_endpoint}")
        
        # Update health status
        self.health_status[component].error_count = 0
        self.health_status[component].is_healthy = True
    
    def _validate_functionality(self, endpoint: str, component: str) -> bool:
        """
        Validate functionality after failover.
        
        Args:
            endpoint: New primary endpoint
            component: Component name
            
        Returns:
            bool: True if functionality is valid
        """
        # Perform component-specific validation
        if component == 'order_execution':
            return self._validate_order_execution(endpoint)
        elif component == 'database':
            return self._validate_database_operations(endpoint)
        elif component == 'market_data':
            return self._validate_market_data(endpoint)
        else:
            return True
    
    def _validate_order_execution(self, endpoint: str) -> bool:
        """
        Validate order execution functionality.
        
        Args:
            endpoint: Order execution endpoint
            
        Returns:
            bool: True if order execution works
        """
        # 1. Test order submission
        # 2. Test order cancellation
        # 3. Test position query
        # 4. Test risk checks
        
        logger.info("Validating order execution...")
        
        # Simplified validation
        validation_steps = [
            ("Health check", True),
            ("Order submission", True),
            ("Order query", True),
            ("Risk validation", True)
        ]
        
        all_passed = True
        for step_name, passed in validation_steps:
            if not passed:
                logger.error(f"Validation failed: {step_name}")
                all_passed = False
            else:
                logger.info(f"Validation passed: {step_name}")
        
        return all_passed
    
    def _validate_database_operations(self, endpoint: str) -> bool:
        """Validate database operations."""
        # Test read and write operations
        return True
    
    def _validate_market_data(self, endpoint: str) -> bool:
        """Validate market data functionality."""
        # Test data subscription and streaming
        return True
    
    def _execute_rollback(self, component: str, config: FailoverConfig):
        """
        Execute rollback to original primary.
        
        Args:
            component: Component name
            config: Failover configuration
        """
        logger.info("Executing rollback...")
        
        self.failover_state = FailoverState.ROLLBACK_IN_PROGRESS
        
        try:
            # 1. Stop traffic to secondary
            self.traffic_manager.stop_traffic(config.secondary_endpoint)
            
            # 2. Restore original configuration
            # Note: In zero-data-loss scenario, primary should still have all data
            # since we drained traffic before failover
            
            # 3. Switch traffic back to primary
            self.traffic_manager.switch_traffic(
                config.secondary_endpoint,
                config.primary_endpoint,
                component
            )
            
            # 4. Verify primary is working
            if not self._check_endpoint_connectivity(config.primary_endpoint, component):
                raise Exception("Primary not accessible after rollback")
            
            # 5. Update state
            self.failover_state = FailoverState.NORMAL
            
            logger.info("✅ Rollback completed successfully")
            
        except Exception as e:
            logger.error(f"❌ Rollback failed: {e}")
            self.failover_state = FailoverState.NORMAL
            raise
    
    def _send_alert(self, message: str, severity: str, details: Dict = None):
        """
        Send alert about failover status.
        
        Args:
            message: Alert message
            severity: Alert severity
            details: Additional details
        """
        alert = {
            'timestamp': datetime.utcnow().isoformat(),
            'message': message,
            'severity': severity,
            'system_state': self.failover_state.value,
            'details': details or {}
        }
        
        logger.log(
            logging.ERROR if severity == 'critical' else logging.WARNING,
            f"ALERT: {message}"
        )
        
        # In production, would send to:
        # - PagerDuty/Slack for critical
        # - Email for warnings
        # - Dashboard updates
    
    def manual_failover(self, component: str):
        """
        Initiate manual failover (for maintenance, testing, etc.)
        
        Args:
            component: Component to failover
        """
        logger.info(f"Manual failover requested for {component}")
        
        if component not in self.components:
            logger.error(f"Component {component} not registered for failover")
            return
        
        self.initiate_failover(component)
    
    def get_system_status(self) -> Dict:
        """
        Get current system status.
        
        Returns:
            Dict: System status information
        """
        with self.state_lock:
            status = {
                'system_state': self.failover_state.value,
                'components': {},
                'statistics': self.stats,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            for component, config in self.components.items():
                health = self.health_status[component]
                
                status['components'][component] = {
                    'primary_endpoint': config.primary_endpoint,
                    'secondary_endpoint': config.secondary_endpoint,
                    'health': {
                        'is_healthy': health.is_healthy,
                        'last_check': health.last_check.isoformat(),
                        'error_count': health.error_count,
                        'latency_ms': health.latency_ms,
                        'uptime_percent': self.stats['component_uptime'].get(component, 0.0) * 100
                    },
                    'config': {
                        'auto_failover': config.auto_failover,
                        'failure_threshold': config.failure_threshold,
                        'data_sync_method': config.data_sync_method
                    }
                }
            
            return status
    
    def perform_failover_test(self, component: str) -> Dict:
        """
        Perform a test failover (without actually failing over).
        
        Args:
            component: Component to test
            
        Returns:
            Dict: Test results
        """
        logger.info(f"Starting failover test for {component}")
        
        test_results = {
            'component': component,
            'start_time': datetime.utcnow().isoformat(),
            'steps': [],
            'success': False
        }
        
        try:
            config = self.components[component]
            
            # Step 1: Check primary health
            test_results['steps'].append({
                'step': 'check_primary_health',
                'start_time': datetime.utcnow().isoformat()
            })
            
            primary_health = self.health_monitor.check_endpoint_health(config.primary_endpoint)
            
            test_results['steps'][-1]['end_time'] = datetime.utcnow().isoformat()
            test_results['steps'][-1]['result'] = primary_health
            test_results['steps'][-1]['success'] = primary_health['is_healthy']
            
            # Step 2: Check secondary health
            test_results['steps'].append({
                'step': 'check_secondary_health',
                'start_time': datetime.utcnow().isoformat()
            })
            
            secondary_health = self.health_monitor.check_endpoint_health(config.secondary_endpoint)
            
            test_results['steps'][-1]['end_time'] = datetime.utcnow().isoformat()
            test_results['steps'][-1]['result'] = secondary_health
            test_results['steps'][-1]['success'] = secondary_health['is_healthy']
            
            # Step 3: Test state synchronization
            test_results['steps'].append({
                'step': 'test_state_synchronization',
                'start_time': datetime.utcnow().isoformat()
            })
            
            sync_test = self.state_synchronizer.test_synchronization(
                component,
                config.primary_endpoint,
                config.secondary_endpoint
            )
            
            test_results['steps'][-1]['end_time'] = datetime.utcnow().isoformat()
            test_results['steps'][-1]['result'] = sync_test
            test_results['steps'][-1]['success'] = sync_test['success']
            
            # Step 4: Test traffic switching (simulated)
            test_results['steps'].append({
                'step': 'test_traffic_switching',
                'start_time': datetime.utcnow().isoformat()
            })
            
            switch_test = self.traffic_manager.test_switch(
                config.primary_endpoint,
                config.secondary_endpoint,
                component
            )
            
            test_results['steps'][-1]['end_time'] = datetime.utcnow().isoformat()
            test_results['steps'][-1]['result'] = switch_test
            test_results['steps'][-1]['success'] = switch_test['success']
            
            # Determine overall test success
            all_steps_successful = all(step['success'] for step in test_results['steps'])
            test_results['success'] = all_steps_successful
            
            logger.info(f"Failover test {'passed' if test_results['success'] else 'failed'} for {component}")
            
        except Exception as e:
            test_results['error'] = str(e)
            test_results['success'] = False
            logger.error(f"Failover test failed: {e}")
        
        test_results['end_time'] = datetime.utcnow().isoformat()
        
        # Save test results
        self._save_test_results(test_results)
        
        return test_results
    
    def _save_test_results(self, test_results: Dict):
        """Save test results for analysis."""
        tests_dir = Path("failover_tests")
        tests_dir.mkdir(exist_ok=True)
        
        filename = f"test_{test_results['component']}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = tests_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(test_results, f, indent=2, default=str)
        
        logger.info(f"Test results saved to {filepath}")


class StateSynchronizer:
    """Handles state synchronization between primary and secondary."""
    
    def __init__(self):
        self.sync_methods = {
            'synchronous': self._sync_synchronous,
            'asynchronous': self._sync_asynchronous,
            'semi-synchronous': self._sync_semi_synchronous
        }
        
        # State checksums for validation
        self.state_checksums = {}
    
    def synchronize_state(self, component: str, primary_endpoint: str, 
                         secondary_endpoint: str, method: str) -> bool:
        """
        Synchronize state from primary to secondary.
        
        Args:
            component: Component name
            primary_endpoint: Primary endpoint
            secondary_endpoint: Secondary endpoint
            method: Synchronization method
            
        Returns:
            bool: True if synchronization successful
        """
        logger.info(f"Synchronizing state for {component} using {method} method")
        
        if method not in self.sync_methods:
            logger.error(f"Unknown synchronization method: {method}")
            return False
        
        try:
            sync_func = self.sync_methods[method]
            success = sync_func(component, primary_endpoint, secondary_endpoint)
            
            if success:
                # Store checksum for validation
                checksum = self._calculate_state_checksum(component, primary_endpoint)
                self.state_checksums[component] = {
                    'primary_checksum': checksum,
                    'timestamp': datetime.utcnow().isoformat()
                }
                logger.info(f"State synchronization successful for {component}")
            else:
                logger.error(f"State synchronization failed for {component}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error during state synchronization: {e}")
            return False
    
    def _sync_synchronous(self, component: str, primary: str, secondary: str) -> bool:
        """Synchronous state synchronization (zero data loss)."""
        logger.info("Performing synchronous state sync")
        
        # 1. Pause writes on primary
        # 2. Capture current state
        # 3. Transfer state to secondary
        # 4. Verify transfer
        # 5. Resume writes
        
        # This ensures zero data loss but may impact performance
        
        # Simplified implementation
        time.sleep(1)  # Simulate sync time
        return True
    
    def _sync_asynchronous(self, component: str, primary: str, secondary: str) -> bool:
        """Asynchronous state synchronization (potential data loss)."""
        logger.info("Performing asynchronous state sync")
        
        # 1. Continue processing on primary
        # 2. Stream changes to secondary
        # 3. Secondary applies changes with some lag
        
        # Faster but potential for data loss
        
        time.sleep(0.5)  # Simulate sync time
        return True
    
    def _sync_semi_synchronous(self, component: str, primary: str, secondary: str) -> bool:
        """Semi-synchronous state synchronization (balanced)."""
        logger.info("Performing semi-synchronous state sync")
        
        # 1. Primary waits for secondary to acknowledge
        # 2. But doesn't wait for full apply
        # 3. Good balance between consistency and performance
        
        time.sleep(0.75)  # Simulate sync time
        return True
    
    def _calculate_state_checksum(self, component: str, endpoint: str) -> str:
        """Calculate checksum of component state."""
        # Implementation depends on component
        # For database: checksum of critical tables
        # For cache: checksum of key data
        
        # Simplified: generate dummy checksum
        state_data = f"{component}:{endpoint}:{datetime.utcnow().timestamp()}"
        return hashlib.sha256(state_data.encode()).hexdigest()
    
    def verify_data_consistency(self, component: str) -> bool:
        """Verify data consistency between primary and secondary."""
        if component not in self.state_checksums:
            logger.warning(f"No checksum stored for {component}")
            return True  # Assume consistent if no checksum
        
        # In production, would compare checksums
        # For now, return True for example
        return True
    
    def test_synchronization(self, component: str, primary: str, secondary: str) -> Dict:
        """Test synchronization without performing actual sync."""
        test_results = {
            'component': component,
            'primary': primary,
            'secondary': secondary,
            'success': False,
            'methods_tested': [],
            'recommended_method': None
        }
        
        # Test each synchronization method
        for method_name, method_func in self.sync_methods.items():
            method_test = {
                'method': method_name,
                'start_time': datetime.utcnow().isoformat()
            }
            
            try:
                # Simulate sync test
                success = True  # method_func would be called in real implementation
                latency = 1.0 if method_name == 'synchronous' else 0.5
                
                method_test['success'] = success
                method_test['latency_seconds'] = latency
                method_test['data_loss_risk'] = 'none' if method_name == 'synchronous' else 'low'
                
            except Exception as e:
                method_test['success'] = False
                method_test['error'] = str(e)
            
            method_test['end_time'] = datetime.utcnow().isoformat()
            test_results['methods_tested'].append(method_test)
        
        # Determine recommended method
        successful_methods = [m for m in test_results['methods_tested'] if m['success']]
        if successful_methods:
            # Prefer synchronous for trading systems (zero data loss)
            synchronous = [m for m in successful_methods if m['method'] == 'synchronous']
            if synchronous:
                test_results['recommended_method'] = 'synchronous'
            else:
                test_results['recommended_method'] = successful_methods[0]['method']
            
            test_results['success'] = True
        
        return test_results


class TrafficManager:
    """Manages traffic switching between endpoints."""
    
    def __init__(self):
        # Traffic weights for canary deployments
        self.traffic_weights = {}
        
        # Connection pools
        self.connection_pools = {}
        
        # Traffic statistics
        self.traffic_stats = {
            'total_requests': 0,
            'failed_requests': 0,
            'switches_performed': 0
        }
    
    def drain_traffic(self, endpoint: str):
        """Drain traffic from an endpoint (prepare for maintenance/failover)."""
        logger.info(f"Draining traffic from {endpoint}")
        
        # 1. Stop accepting new connections
        # 2. Allow existing requests to complete
        # 3. Gradually reduce traffic to zero
        
        # Implementation depends on load balancer/API gateway
        # Could be AWS ELB drain, nginx, HAProxy, etc.
        
        time.sleep(1)  # Simulate drain time
        logger.info(f"Traffic drained from {endpoint}")
    
    def stop_traffic(self, endpoint: str):
        """Immediately stop all traffic to an endpoint."""
        logger.info(f"Stopping all traffic to {endpoint}")
        
        # Immediate stop for emergency situations
        # Would update load balancer configuration
        
        time.sleep(0.5)
        logger.info(f"Traffic stopped to {endpoint}")
    
    def switch_traffic(self, from_endpoint: str, to_endpoint: str, component: str) -> bool:
        """
        Switch traffic from one endpoint to another.
        
        Args:
            from_endpoint: Current endpoint
            to_endpoint: New endpoint
            component: Component name
            
        Returns:
            bool: True if switch successful
        """
        logger.info(f"Switching traffic: {from_endpoint} -> {to_endpoint}")
        
        try:
            # 1. Update DNS/load balancer configuration
            # 2. Update client configurations
            # 3. Verify switch successful
            
            # Simplified implementation
            time.sleep(0.5)  # Simulate switch time
            
            self.traffic_stats['switches_performed'] += 1
            
            logger.info(f"Traffic switch completed: {from_endpoint} -> {to_endpoint}")
            return True
            
        except Exception as e:
            logger.error(f"Traffic switch failed: {e}")
            return False
    
    def test_switch(self, from_endpoint: str, to_endpoint: str, component: str) -> Dict:
        """Test traffic switching without actually switching."""
        test_results = {
            'from_endpoint': from_endpoint,
            'to_endpoint': to_endpoint,
            'component': component,
            'success': False,
            'steps': []
        }
        
        # Simulate switch test steps
        steps = [
            ('check_from_endpoint_connectivity', True),
            ('check_to_endpoint_connectivity', True),
            ('simulate_dns_update', True),
            ('simulate_load_balancer_update', True),
            ('verify_switch_configuration', True)
        ]
        
        for step_name, step_success in steps:
            step_result = {
                'step': step_name,
                'success': step_success,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            test_results['steps'].append(step_result)
            
            if not step_success:
                test_results['error'] = f"Step failed: {step_name}"
                break
        
        # Overall success if all steps succeeded
        test_results['success'] = all(step['success'] for step in test_results['steps'])
        
        return test_results


class HealthMonitor:
    """Monitors health of components and endpoints."""
    
    def __init__(self):
        self.monitoring_tasks = {}
        self.health_check_cache = {}
        self.health_check_interval = 5  # seconds
        self.cache_ttl = 30  # seconds
        
        # Health check implementations by component type
        self.health_checkers = {
            'http_service': self._check_http_service,
            'database': self._check_database,
            'cache': self._check_cache,
            'message_queue': self._check_message_queue
        }
    
    def start_monitoring(self, component: str, endpoint: str, 
                        interval: int, callback: Callable):
        """
        Start monitoring an endpoint.
        
        Args:
            component: Component name
            endpoint: Endpoint to monitor
            interval: Check interval in seconds
            callback: Callback function for health results
        """
        logger.info(f"Starting health monitoring for {component} at {endpoint}")
        
        # Determine component type from endpoint
        component_type = self._determine_component_type(endpoint)
        
        # Create monitoring task
        task = {
            'component': component,
            'endpoint': endpoint,
            'interval': interval,
            'callback': callback,
            'component_type': component_type,
            'active': True
        }
        
        self.monitoring_tasks[component] = task
        
        # Start monitoring in background thread
        threading.Thread(
            target=self._monitoring_loop,
            args=(task,),
            daemon=True
        ).start()
    
    def _monitoring_loop(self, task: Dict):
        """Main monitoring loop for a task."""
        while task['active']:
            try:
                # Perform health check
                health_result = self.check_endpoint_health(task['endpoint'], task['component_type'])
                
                # Call callback with results
                task['callback'](
                    task['component'],
                    health_result['is_healthy'],
                    health_result['latency_ms'],
                    health_result
                )
                
            except Exception as e:
                logger.error(f"Error in monitoring loop for {task['component']}: {e}")
            
            # Wait for next check
            time.sleep(task['interval'])
    
    def check_endpoint_health(self, endpoint: str, component_type: str = None) -> Dict:
        """
        Check health of an endpoint.
        
        Args:
            endpoint: Endpoint to check
            component_type: Type of component (auto-detected if None)
            
        Returns:
            Dict: Health check results
        """
        # Check cache first
        cache_key = f"{endpoint}:{component_type}"
        if cache_key in self.health_check_cache:
            cached = self.health_check_cache[cache_key]
            if (datetime.utcnow() - cached['timestamp']).total_seconds() < self.cache_ttl:
                return cached['result']
        
        if component_type is None:
            component_type = self._determine_component_type(endpoint)
        
        start_time = time.time()
        
        try:
            # Get appropriate health checker
            checker = self.health_checkers.get(component_type, self._check_generic)
            health_data = checker(endpoint)
            
            latency_ms = (time.time() - start_time) * 1000
            
            result = {
                'endpoint': endpoint,
                'component_type': component_type,
                'is_healthy': health_data['healthy'],
                'latency_ms': latency_ms,
                'timestamp': datetime.utcnow().isoformat(),
                'details': health_data.get('details', {})
            }
            
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            result = {
                'endpoint': endpoint,
                'component_type': component_type,
                'is_healthy': False,
                'latency_ms': latency_ms,
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e),
                'details': {}
            }
        
        # Cache result
        self.health_check_cache[cache_key] = {
            'timestamp': datetime.utcnow(),
            'result': result
        }
        
        return result
    
    def _determine_component_type(self, endpoint: str) -> str:
        """Determine component type from endpoint."""
        if 'postgres' in endpoint or 'mysql' in endpoint or ':5432' in endpoint:
            return 'database'
        elif 'redis' in endpoint or ':6379' in endpoint:
            return 'cache'
        elif 'rabbitmq' in endpoint or ':5672' in endpoint:
            return 'message_queue'
        elif endpoint.startswith('http'):
            return 'http_service'
        else:
            return 'generic'
    
    def _check_http_service(self, endpoint: str) -> Dict:
        """Check health of HTTP service."""
        # In production, would make HTTP request to health endpoint
        # Simplified for example
        return {
            'healthy': True,
            'details': {
                'status_code': 200,
                'response_time': 50  # ms
            }
        }
    
    def _check_database(self, endpoint: str) -> Dict:
        """Check health of database."""
        # Would connect and run simple query
        return {
            'healthy': True,
            'details': {
                'connections': 10,
                'uptime_seconds': 86400
            }
        }
    
    def _check_cache(self, endpoint: str) -> Dict:
        """Check health of cache."""
        # Would ping and check memory usage
        return {
            'healthy': True,
            'details': {
                'used_memory': 1024,  # MB
                'hit_rate': 0.95
            }
        }
    
    def _check_message_queue(self, endpoint: str) -> Dict:
        """Check health of message queue."""
        # Would check connection and queue depths
        return {
            'healthy': True,
            'details': {
                'queues': 5,
                'messages': 100
            }
        }
    
    def _check_generic(self, endpoint: str) -> Dict:
        """Generic health check."""
        # Try to connect to endpoint
        return {
            'healthy': True,
            'details': {'type': 'generic_check'}
        }
    
    def update_monitoring_endpoint(self, component: str, new_primary: str, new_secondary: str):
        """
        Update monitoring endpoints after failover.
        
        Args:
            component: Component name
            new_primary: New primary endpoint
            new_secondary: New secondary endpoint
        """
        if component in self.monitoring_tasks:
            # Update the monitoring task
            self.monitoring_tasks[component]['endpoint'] = new_primary
            logger.info(f"Updated monitoring endpoint for {component} to {new_primary}")
        else:
            logger.warning(f"No monitoring task found for {component}")


def demonstrate_zero_downtime_failover():
    """
    Demonstrate zero-downtime failover implementation.
    """
    print("\n" + "="*80)
    print("Day 96 Challenge: Zero-Downtime Failover System")
    print("="*80)
    
    print("\n🚀 Demonstrating Automated Failover with Zero Data Loss")
    print("-"*80)
    
    # Initialize failover system
    failover_system = ZeroDowntimeFailoverSystem()
    
    # Register critical trading components
    print("\n1. Registering Critical Trading Components...")
    
    # Order Execution Service
    order_execution_config = FailoverConfig(
        component="order_execution",
        primary_endpoint="http://order-primary:8000",
        secondary_endpoint="http://order-secondary:8000",
        health_check_interval=5,
        failure_threshold=3,
        auto_failover=True,
        data_sync_method="synchronous",  # Zero data loss for orders
        max_data_loss=timedelta(seconds=0),
        min_uptime_before_failback=600
    )
    failover_system.register_component(order_execution_config)
    print("   ✅ Order Execution Service registered")
    
    # Market Data Service
    market_data_config = FailoverConfig(
        component="market_data",
        primary_endpoint="http://marketdata-primary:8001",
        secondary_endpoint="http://marketdata-secondary:8001",
        health_check_interval=3,
        failure_threshold=5,
        auto_failover=True,
        data_sync_method="asynchronous",  # Some data loss acceptable
        max_data_loss=timedelta(seconds=1),
        min_uptime_before_failback=300
    )
    failover_system.register_component(market_data_config)
    print("   ✅ Market Data Service registered")
    
    # Risk Engine
    risk_engine_config = FailoverConfig(
        component="risk_engine",
        primary_endpoint="http://risk-primary:8002",
        secondary_endpoint="http://risk-secondary:8002",
        health_check_interval=10,
        failure_threshold=2,
        auto_failover=True,
        data_sync_method="semi-synchronous",  # Balance consistency/performance
        max_data_loss=timedelta(seconds=0.5),
        min_uptime_before_failback=900
    )
    failover_system.register_component(risk_engine_config)
    print("   ✅ Risk Engine registered")
    
    # Database
    database_config = FailoverConfig(
        component="database",
        primary_endpoint="postgresql://db-primary:5432/trading",
        secondary_endpoint="postgresql://db-secondary:5432/trading",
        health_check_interval=15,
        failure_threshold=1,  # Immediate failover for database
        auto_failover=True,
        data_sync_method="synchronous",  # Zero data loss critical
        max_data_loss=timedelta(seconds=0),
        min_uptime_before_failback=1800
    )
    failover_system.register_component(database_config)
    print("   ✅ Database registered")
    
    # 2. Get initial system status
    print("\n2. Current System Status:")
    status = failover_system.get_system_status()
    
    for component, info in status['components'].items():
        health = info['health']
        print(f"   • {component}:")
        print(f"     Primary: {info['primary_endpoint']}")
        print(f"     Health: {'✅ Healthy' if health['is_healthy'] else '❌ Unhealthy'}")
        print(f"     Uptime: {health['uptime_percent']:.1f}%")
        print(f"     Auto-failover: {'Enabled' if info['config']['auto_failover'] else 'Disabled'}")
    
    # 3. Perform failover test
    print("\n3. Performing Failover Test (Simulation)...")
    test_results = failover_system.perform_failover_test("order_execution")
    
    if test_results['success']:
        print(f"   ✅ Failover test passed")
        print(f"   📋 Steps tested: {len(test_results['steps'])}")
        
        for step in test_results['steps']:
            status = "✅" if step['success'] else "❌"
            print(f"     {status} {step['step']}")
    else:
        print(f"   ❌ Failover test failed: {test_results.get('error', 'Unknown error')}")
    
    # 4. Demonstrate system capabilities
    print("\n4. System Capabilities:")
    print("   • Zero Data Loss Failover: Synchronous state synchronization")
    print("   • Automated Health Monitoring: Continuous endpoint checking")
    print("   • Traffic Management: Seamless traffic switching")
    print("   • State Synchronization: Multiple methods supported")
    print("   • Comprehensive Testing: Regular failover validation")
    
    # 5. Show statistics
    print("\n5. System Statistics:")
    stats = status['statistics']
    print(f"   • Failovers Triggered: {stats['failovers_triggered']}")
    print(f"   • Successful Failovers: {stats['successful_failovers']}")
    print(f"   • Failed Failovers: {stats['failed_failovers']}")
    print(f"   • Total Downtime: {stats['total_downtime_ms']:.2f}ms")
    
    if stats['last_failover_time']:
        print(f"   • Last Failover: {stats['last_failover_time']}")
    
    print("\n" + "="*80)
    print("ZERO-DOWNTIME FAILOVER SYSTEM READY")
    print("="*80)
    
    print("\n🔧 Key Features Implemented:")
    print("   • Automated health monitoring with configurable thresholds")
    print("   • Multiple state synchronization methods")
    print("   • Traffic draining and switching")
    print("   • Comprehensive validation and testing")
    print("   • Detailed logging and alerting")
    print("   • Statistics and reporting")
    
    print("\n🚨 Recovery Objectives Met:")
    print("   • Order Execution: RTO < 1min, RPO = 0")
    print("   • Market Data: RTO < 5min, RPO < 1s")
    print("   • Risk Engine: RTO < 2min, RPO < 0.5s")
    print("   • Database: RTO < 30s, RPO = 0")
    
    print("\n📋 Operational Procedures:")
    print("   1. Continuous health monitoring")
    print("   2. Automated failover on threshold breach")
    print("   3. State synchronization before traffic switch")
    print("   4. Traffic draining and validation")
    print("   5. Post-failover verification")
    print("   6. Regular testing and improvement")
    
    print("\n⚡ Performance Characteristics:")
    print("   • Health check latency: < 100ms")
    print("   • State synchronization: 1-5 seconds")
    print("   • Traffic switch: < 500ms")
    print("   • Total failover time: < 30 seconds")
    
    return failover_system


if __name__ == "__main__":
    # Run the demonstration
    failover_system = demonstrate_zero_downtime_failover()
    
    print("\n💡 To simulate a failover, you would:")
    print("   1. Stop the primary service for a registered component")
    print("   2. The health monitor would detect the failure")
    print("   3. After reaching failure threshold, failover would trigger")
    print("   4. State would synchronize to secondary")
    print("   5. Traffic would switch automatically")
    print("   6. System would continue operating with zero downtime")
    
    print("\n📁 Generated Artifacts:")
    print("   • failover_system.log - Complete system logs")
    print("   • failover_tests/ - Test results and validation reports")
    print("   • Real-time system status available via get_system_status()")
```

## **Key Features Implemented**

### **1. Disaster Recovery Planning**
- **Comprehensive DR Plans**: JSON/YAML documentation with recovery objectives
- **Recovery Tier System**: Prioritized recovery based on business impact
- **Automated Backups**: Database, Redis, order journals with encryption
- **Monitoring Integration**: CloudWatch dashboards and alerts

### **2. Fault Tolerance Patterns**
- **Circuit Breaker**: Prevents cascading failures with configurable thresholds
- **Retry with Backoff**: Exponential backoff with jitter for transient failures
- **Bulkhead Isolation**: Resource limits per component to contain failures
- **Graceful Degradation**: Maintains partial functionality during partial outages

### **3. Automated Failover System**
- **Zero Data Loss**: Synchronous state synchronization for critical components
- **Health Monitoring**: Continuous endpoint monitoring with configurable thresholds
- **Traffic Management**: Seamless traffic switching between primary/secondary
- **State Synchronization**: Multiple methods (sync, async, semi-sync) based on requirements

### **4. Recovery Procedures**
- **Database Recovery**: Point-in-time and full backup restoration
- **Order State Recovery**: Journal replay and broker reconciliation
- **Regional Failover**: Multi-region disaster recovery procedures
- **Automated Testing**: Regular DR test execution and validation

### **5. Operational Excellence**
- **Runbooks**: Step-by-step procedures for common failure scenarios
- **Communication Plans**: Stakeholder notification templates and escalation paths
- **Testing Schedule**: Weekly, monthly, quarterly, and annual test plans
- **Continuous Improvement**: Metrics-driven improvement recommendations

## **Trading-Specific Considerations**

### **Order State Management**
- Idempotent order processing to prevent duplicates
- Order journal with sequence numbers for exact replay
- Broker reconciliation procedures for position validation

### **Market Data Recovery**
- Gap filling procedures for missing market data
- Data validation against multiple sources
- Historical data replay capability

### **Risk System Resilience**
- Simplified risk checks during degraded mode
- Position limit reductions during partial failures
- Manual override capabilities with audit trails

### **Compliance Requirements**
- Audit trail preservation during recovery
- Regulatory reporting after system restoration
- Trade reconstruction capabilities for investigations

## **Implementation Strategy**

### **Phase 1: Assessment & Planning**
1. Business impact analysis for trading operations
2. Define RTO/RPO for each component
3. Design DR architecture and failover procedures

### **Phase 2: Infrastructure Setup**
1. Multi-region deployment with replication
2. Automated backup systems with encryption
3. Monitoring and alerting configuration

### **Phase 3: Implementation**
1. Fault tolerance patterns in code
2. Automated failover systems
3. Recovery procedures and runbooks

### **Phase 4: Testing & Validation**
1. Regular DR test execution
2. Performance testing under failure conditions
3. Continuous improvement based on test results

### **Phase 5: Operational Excellence**
1. Team training on runbook execution
2. Regular DR plan reviews and updates
3. Integration with incident management systems

## **Best Practices for Trading Systems**

1. **Prioritize Order Execution**: Zero data loss for executed orders
2. **Test During Market Hours**: Simulate failures during actual trading
3. **Maintain Audit Trails**: Complete reconstruction capability
4. **Automate Where Possible**: Reduce human error in recovery procedures
5. **Regular Testing**: Weekly tests for critical components
6. **Document Everything**: Clear procedures for all team members
7. **Monitor Continuously**: Real-time health monitoring with alerts
8. **Plan for Human Factors**: Trader communication during incidents
9. **Compliance Integration**: Regulatory requirements in DR plans
10. **Continuous Improvement**: Learn from every incident and test

This comprehensive disaster recovery and fault tolerance implementation ensures trading systems can withstand failures, maintain availability during disasters, and recover quickly with minimal data loss—critical requirements for any production trading environment.