"""
Day 86: Cloud Deployment for Trading Systems
AWS, Azure, GCP deployment strategies with cost optimization and production readiness.
"""

import json
import os
import sys
import time
import boto3
import yaml
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict, field
from pathlib import Path
import subprocess
import tempfile
import hashlib
from enum import Enum


class CloudProvider(Enum):
    """Supported cloud providers."""
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    HYBRID = "hybrid"


class DeploymentModel(Enum):
    """Deployment models."""
    VM = "vm"  # Virtual Machines
    CONTAINER = "container"  # Container orchestration
    SERVERLESS = "serverless"  # Function as a Service
    HYBRID = "hybrid"  # Mixed approach


class Environment(Enum):
    """Deployment environments."""
    DEV = "dev"
    STAGING = "staging"
    PROD = "prod"


@dataclass
class CostEstimate:
    """Cost estimation for deployment."""
    monthly_estimate: float
    breakdown: Dict[str, float]
    optimization_suggestions: List[str]
    confidence: float = 0.8  # 80% confidence in estimate
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class PerformanceTarget:
    """Performance targets for deployment."""
    max_latency_ms: int
    min_throughput_rps: int
    availability_target: float  # e.g., 0.9999 for 99.99%
    recovery_time_objective: int  # seconds
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class SecurityRequirement:
    """Security requirements for deployment."""
    encryption_at_rest: bool
    encryption_in_transit: bool
    vpc_isolation: bool
    audit_logging: bool
    compliance_frameworks: List[str]
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class TradingWorkload:
    """Trading workload characteristics."""
    trading_frequency: str  # "high", "medium", "low"
    data_volume_gb_per_day: float
    peak_events_per_second: int
    average_events_per_second: int
    market_hours_coverage: str  # "24/7", "market-hours", "specific-hours"
    
    def to_dict(self) -> Dict:
        return asdict(self)


class CloudDeploymentPlanner:
    """
    Plan and optimize cloud deployments for trading systems.
    Supports AWS, Azure, GCP with cost and performance optimization.
    """
    
    def __init__(self, provider: CloudProvider = CloudProvider.AWS):
        self.provider = provider
        self.configurations = self._load_configurations()
        
        # Provider-specific clients
        if provider == CloudProvider.AWS:
            self.client = boto3.client('ce', region_name='us-east-1')  # Cost Explorer
            self.ec2 = boto3.client('ec2', region_name='us-east-1')
        # Azure and GCP clients would be initialized here
        
    def _load_configurations(self) -> Dict:
        """Load cloud provider configurations."""
        configs = {
            CloudProvider.AWS: {
                'regions': {
                    'us-east-1': {'latency_ms': 5, 'cost_multiplier': 1.0},
                    'us-west-2': {'latency_ms': 20, 'cost_multiplier': 1.0},
                    'eu-west-1': {'latency_ms': 80, 'cost_multiplier': 1.1}
                },
                'instance_types': {
                    'compute_optimized': ['c5', 'c5n', 'c6i'],
                    'memory_optimized': ['r5', 'r5n', 'r6i'],
                    'storage_optimized': ['i3', 'i3en'],
                    'accelerated_computing': ['p3', 'p4', 'g4']
                },
                'pricing_tiers': {
                    'on_demand': 1.0,
                    'reserved_1yr': 0.6,
                    'reserved_3yr': 0.45,
                    'spot': 0.3
                },
                'services': {
                    'compute': ['ec2', 'lambda', 'fargate'],
                    'storage': ['s3', 'ebs', 'efs'],
                    'database': ['rds', 'dynamodb', 'redshift'],
                    'messaging': ['sqs', 'sns', 'kinesis'],
                    'monitoring': ['cloudwatch', 'xray']
                }
            },
            CloudProvider.AZURE: {
                'regions': {
                    'eastus': {'latency_ms': 10, 'cost_multiplier': 1.0},
                    'westus2': {'latency_ms': 25, 'cost_multiplier': 1.0},
                    'westeurope': {'latency_ms': 85, 'cost_multiplier': 1.1}
                },
                'instance_types': {
                    'compute_optimized': ['Fsv2', 'Fsv3'],
                    'memory_optimized': ['Msv2', 'Msv3'],
                    'storage_optimized': ['Lsv2', 'Lsv3'],
                    'accelerated_computing': ['NCv3', 'NDv2']
                },
                'pricing_tiers': {
                    'pay_as_you_go': 1.0,
                    'reserved_1yr': 0.58,
                    'reserved_3yr': 0.42,
                    'spot': 0.25
                }
            },
            CloudProvider.GCP: {
                'regions': {
                    'us-central1': {'latency_ms': 8, 'cost_multiplier': 1.0},
                    'us-west1': {'latency_ms': 15, 'cost_multiplier': 1.0},
                    'europe-west1': {'latency_ms': 90, 'cost_multiplier': 1.15}
                },
                'instance_types': {
                    'compute_optimized': ['c2', 'c2d'],
                    'memory_optimized': ['m2', 'm3'],
                    'storage_optimized': ['d2'],
                    'accelerated_computing': ['a2', 't4']
                },
                'pricing_tiers': {
                    'on_demand': 1.0,
                    'committed_use_1yr': 0.57,
                    'committed_use_3yr': 0.43,
                    'preemptible': 0.2
                }
            }
        }
        
        return configs[self.provider]
    
    def plan_deployment(
        self,
        workload: TradingWorkload,
        performance_targets: PerformanceTarget,
        security_requirements: SecurityRequirement,
        environment: Environment = Environment.PROD
    ) -> Dict:
        """
        Plan optimal deployment based on requirements.
        
        Args:
            workload: Trading workload characteristics
            performance_targets: Performance requirements
            security_requirements: Security requirements
            environment: Deployment environment
            
        Returns:
            Dict: Complete deployment plan
        """
        print(f"\nPlanning {self.provider.value.upper()} deployment for {environment.value} environment...")
        
        # 1. Region selection
        selected_region = self._select_region(performance_targets, workload)
        
        # 2. Compute strategy
        compute_plan = self._plan_compute(
            workload, performance_targets, environment
        )
        
        # 3. Storage strategy
        storage_plan = self._plan_storage(workload, environment)
        
        # 4. Database strategy
        database_plan = self._plan_database(workload, environment)
        
        # 5. Networking strategy
        networking_plan = self._plan_networking(security_requirements)
        
        # 6. Cost estimation
        cost_estimate = self._estimate_costs(
            compute_plan, storage_plan, database_plan, environment
        )
        
        # 7. Generate infrastructure as code templates
        iac_templates = self._generate_iac_templates(
            selected_region, compute_plan, storage_plan,
            database_plan, networking_plan, environment
        )
        
        deployment_plan = {
            'provider': self.provider.value,
            'environment': environment.value,
            'region': selected_region,
            'timestamp': datetime.utcnow().isoformat(),
            'workload': workload.to_dict(),
            'performance_targets': performance_targets.to_dict(),
            'security_requirements': security_requirements.to_dict(),
            'compute_plan': compute_plan,
            'storage_plan': storage_plan,
            'database_plan': database_plan,
            'networking_plan': networking_plan,
            'cost_estimate': cost_estimate.to_dict(),
            'iac_templates': iac_templates,
            'deployment_steps': self._generate_deployment_steps(environment)
        }
        
        return deployment_plan
    
    def _select_region(
        self,
        performance_targets: PerformanceTarget,
        workload: TradingWorkload
    ) -> str:
        """Select optimal region based on latency and requirements."""
        regions = self.configurations['regions']
        
        # Filter regions by latency
        suitable_regions = {
            name: config for name, config in regions.items()
            if config['latency_ms'] <= performance_targets.max_latency_ms
        }
        
        if not suitable_regions:
            print(f"Warning: No regions meet latency requirement of {performance_targets.max_latency_ms}ms")
            # Fall back to lowest latency region
            selected = min(regions.items(), key=lambda x: x[1]['latency_ms'])
            return selected[0]
        
        # For trading systems, prioritize low latency
        selected = min(suitable_regions.items(), key=lambda x: x[1]['latency_ms'])
        
        print(f"Selected region: {selected[0]} (latency: {selected[1]['latency_ms']}ms)")
        return selected[0]
    
    def _plan_compute(
        self,
        workload: TradingWorkload,
        performance_targets: PerformanceTarget,
        environment: Environment
    ) -> Dict:
        """Plan compute resources."""
        compute_plan = {
            'deployment_model': None,
            'instance_types': [],
            'scaling_strategy': {},
            'cost_optimization': {},
            'capacity': {}
        }
        
        # Determine deployment model based on workload
        if workload.trading_frequency == 'high':
            # High frequency trading needs dedicated, low-latency VMs
            compute_plan['deployment_model'] = DeploymentModel.VM.value
            compute_plan['instance_types'] = self._select_instance_types(
                'compute_optimized', environment
            )
            
            # For HFT, use on-demand or reserved instances (not spot)
            compute_plan['cost_optimization'] = {
                'pricing_tier': 'on_demand',
                'reserved_instances': True,
                'auto_scaling': False  # HFT needs consistent capacity
            }
            
            # Calculate required capacity
            peak_capacity = workload.peak_events_per_second / 1000  # Rough estimate
            compute_plan['capacity'] = {
                'min_instances': max(2, int(peak_capacity * 0.7)),
                'max_instances': max(4, int(peak_capacity * 1.3)),
                'baseline_instances': max(2, int(peak_capacity * 0.8))
            }
            
        elif workload.trading_frequency == 'medium':
            # Medium frequency can use containers with auto-scaling
            compute_plan['deployment_model'] = DeploymentModel.CONTAINER.value
            compute_plan['instance_types'] = self._select_instance_types(
                'memory_optimized', environment
            )
            
            compute_plan['cost_optimization'] = {
                'pricing_tier': 'reserved_1yr',
                'spot_instances': True,
                'auto_scaling': True
            }
            
            compute_plan['scaling_strategy'] = {
                'metric': 'cpu_utilization',
                'target_value': 70,
                'scale_out_cooldown': 60,
                'scale_in_cooldown': 300,
                'trading_hours_scaling': workload.market_hours_coverage != '24/7'
            }
            
        else:  # Low frequency
            # Low frequency can use serverless for cost savings
            compute_plan['deployment_model'] = DeploymentModel.SERVERLESS.value
            
            compute_plan['cost_optimization'] = {
                'pricing_tier': 'pay_as_you_go',
                'reserved_concurrency': True,
                'provisioned_concurrency': False
            }
        
        return compute_plan
    
    def _select_instance_types(
        self,
        category: str,
        environment: Environment
    ) -> List[str]:
        """Select instance types based on category and environment."""
        instance_types = self.configurations['instance_types'].get(category, [])
        
        if environment == Environment.PROD:
            # Production: Use latest generation instances
            return [it for it in instance_types if '6' in it or '3' in it][:3]
        elif environment == Environment.STAGING:
            # Staging: Mix of generations
            return instance_types[:3]
        else:  # DEV
            # Development: Cheapest instances
            return instance_types[:2]
    
    def _plan_storage(
        self,
        workload: TradingWorkload,
        environment: Environment
    ) -> Dict:
        """Plan storage resources."""
        storage_plan = {
            'market_data': {},
            'model_artifacts': {},
            'logs_metrics': {},
            'backup_strategy': {}
        }
        
        # Market data storage (time-series, high write volume)
        if workload.data_volume_gb_per_day > 10:
            # High volume: Use specialized time-series storage
            storage_plan['market_data'] = {
                'type': 'time_series_db',
                'retention_days': 365,
                'compression': True,
                'tiering': {
                    'hot': 30,  # 30 days hot
                    'warm': 90,  # 90 days warm
                    'cold': 365  # 365 days cold
                }
            }
        else:
            # Lower volume: Use object storage
            storage_plan['market_data'] = {
                'type': 'object_storage',
                'retention_days': 180,
                'compression': True,
                'storage_class': 'standard_ia'
            }
        
        # Model artifacts (ML models, checkpoints)
        storage_plan['model_artifacts'] = {
            'type': 'object_storage',
            'versioning': True,
            'lifecycle_rules': [
                {'prefix': 'models/', 'transition_days': 30, 'storage_class': 'glacier'}
            ]
        }
        
        # Logs and metrics
        storage_plan['logs_metrics'] = {
            'type': 'log_aggregation',
            'retention_days': 90 if environment == Environment.PROD else 30,
            'compression': True,
            'query_acceleration': True
        }
        
        # Backup strategy
        if environment == Environment.PROD:
            storage_plan['backup_strategy'] = {
                'frequency': 'daily',
                'retention': {
                    'daily': 30,
                    'weekly': 12,
                    'monthly': 36
                },
                'cross_region': True,
                'encryption': True
            }
        
        return storage_plan
    
    def _plan_database(
        self,
        workload: TradingWorkload,
        environment: Environment
    ) -> Dict:
        """Plan database resources."""
        database_plan = {
            'primary': {},
            'analytical': {},
            'cache': {},
            'replication': {}
        }
        
        # Primary transactional database
        if workload.trading_frequency in ['high', 'medium']:
            database_plan['primary'] = {
                'type': 'relational',
                'engine': 'postgresql',
                'version': '14+',
                'high_availability': True,
                'read_replicas': 2 if environment == Environment.PROD else 1,
                'performance_insights': True
            }
        else:
            database_plan['primary'] = {
                'type': 'document',
                'engine': 'dynamodb' if self.provider == CloudProvider.AWS else 'cosmosdb',
                'provisioned_throughput': 'auto_scaling',
                'backup': 'point_in_time_recovery'
            }
        
        # Analytical database (for backtesting, reporting)
        database_plan['analytical'] = {
            'type': 'columnar',
            'engine': 'redshift' if self.provider == CloudProvider.AWS else 'bigquery',
            'compression': True,
            'materialized_views': True,
            'workload_management': True
        }
        
        # Cache layer (for low-latency data access)
        database_plan['cache'] = {
            'type': 'in_memory',
            'engine': 'redis',
            'cluster_mode': True if environment == Environment.PROD else False,
            'data_persistence': environment == Environment.PROD,
            'backup': environment == Environment.PROD
        }
        
        # Replication strategy
        if environment == Environment.PROD:
            database_plan['replication'] = {
                'cross_region': True,
                'synchronous': False,
                'lag_monitoring': True,
                'failover_automation': True
            }
        
        return database_plan
    
    def _plan_networking(
        self,
        security_requirements: SecurityRequirement
    ) -> Dict:
        """Plan networking resources."""
        networking_plan = {
            'vpc_design': {},
            'security_groups': [],
            'load_balancing': {},
            'dns': {},
            'monitoring': {}
        }
        
        # VPC design
        networking_plan['vpc_design'] = {
            'cidr': '10.0.0.0/16',
            'subnets': {
                'public': ['10.0.1.0/24', '10.0.2.0/24'],
                'private': ['10.0.10.0/24', '10.0.11.0/24'],
                'data': ['10.0.20.0/24', '10.0.21.0/24'],
                'reserved': ['10.0.30.0/24', '10.0.31.0/24']  # For future expansion
            },
            'nat_gateways': 2,  # One per AZ for HA
            'vpc_endpoints': [
                's3', 'dynamodb', 'secretsmanager', 'kms'
            ]
        }
        
        # Security groups
        networking_plan['security_groups'] = [
            {
                'name': 'load_balancer',
                'ingress': [
                    {'protocol': 'tcp', 'ports': [80, 443], 'source': '0.0.0.0/0'}
                ],
                'egress': [
                    {'protocol': 'tcp', 'ports': [32768, 65535], 'source': '10.0.0.0/16'}
                ]
            },
            {
                'name': 'application',
                'ingress': [
                    {'protocol': 'tcp', 'ports': [8000, 9000], 'source': 'load_balancer'}
                ],
                'egress': [
                    {'protocol': 'tcp', 'ports': [443], 'source': '0.0.0.0/0'},
                    {'protocol': 'tcp', 'ports': [5432], 'source': 'database'}
                ]
            },
            {
                'name': 'database',
                'ingress': [
                    {'protocol': 'tcp', 'ports': [5432], 'source': 'application'}
                ],
                'egress': [
                    {'protocol': 'tcp', 'ports': [443], 'source': '0.0.0.0/0'}
                ]
            }
        ]
        
        # Load balancing
        networking_plan['load_balancing'] = {
            'type': 'application',  # Layer 7 for API routing
            'scheme': 'internet-facing',
            'ssl_certificate': 'acm_managed',
            'health_checks': {
                'path': '/health',
                'interval': 30,
                'timeout': 5,
                'healthy_threshold': 2,
                'unhealthy_threshold': 2
            },
            'access_logs': True,
            'waf_enabled': True
        }
        
        # DNS
        networking_plan['dns'] = {
            'domain': 'trading.example.com',
            'routing_policy': 'weighted',
            'health_checks': True,
            'failover': environment == Environment.PROD
        }
        
        # Network monitoring
        networking_plan['monitoring'] = {
            'flow_logs': True,
            'vpc_traffic_mirroring': security_requirements.audit_logging,
            'network_performance_monitoring': True,
            'latency_metrics': True
        }
        
        return networking_plan
    
    def _estimate_costs(
        self,
        compute_plan: Dict,
        storage_plan: Dict,
        database_plan: Dict,
        environment: Environment
    ) -> CostEstimate:
        """Estimate monthly costs for deployment."""
        # Simplified cost estimation
        # In production, would use cloud provider's pricing APIs
        
        base_cost = 1000.0  # Base monthly cost
        
        # Compute cost multiplier
        if compute_plan['deployment_model'] == DeploymentModel.VM.value:
            compute_multiplier = 2.0
        elif compute_plan['deployment_model'] == DeploymentModel.CONTAINER.value:
            compute_multiplier = 1.5
        else:  # Serverless
            compute_multiplier = 1.0
        
        # Environment multiplier
        if environment == Environment.PROD:
            env_multiplier = 3.0
        elif environment == Environment.STAGING:
            env_multiplier = 1.5
        else:  # DEV
            env_multiplier = 1.0
        
        # Calculate estimated costs
        estimated_monthly = base_cost * compute_multiplier * env_multiplier
        
        # Breakdown
        breakdown = {
            'compute': estimated_monthly * 0.5,
            'storage': estimated_monthly * 0.2,
            'database': estimated_monthly * 0.2,
            'networking': estimated_monthly * 0.05,
            'monitoring': estimated_monthly * 0.05
        }
        
        # Optimization suggestions
        suggestions = []
        
        if compute_plan.get('cost_optimization', {}).get('spot_instances'):
            suggestions.append("Use spot instances for non-critical workloads to save 60-90%")
        
        if storage_plan.get('market_data', {}).get('tiering'):
            suggestions.append("Implement storage tiering for historical data")
        
        if environment != Environment.PROD:
            suggestions.append("Use auto-scaling to reduce costs during off-hours")
        
        return CostEstimate(
            monthly_estimate=estimated_monthly,
            breakdown=breakdown,
            optimization_suggestions=suggestions,
            confidence=0.7 if environment == Environment.PROD else 0.8
        )
    
    def _generate_iac_templates(
        self,
        region: str,
        compute_plan: Dict,
        storage_plan: Dict,
        database_plan: Dict,
        networking_plan: Dict,
        environment: Environment
    ) -> Dict:
        """Generate Infrastructure as Code templates."""
        templates = {}
        
        if self.provider == CloudProvider.AWS:
            # Terraform templates
            templates['terraform'] = self._generate_terraform_template(
                region, compute_plan, storage_plan,
                database_plan, networking_plan, environment
            )
            
            # CloudFormation templates
            templates['cloudformation'] = self._generate_cloudformation_template(
                region, compute_plan, storage_plan,
                database_plan, networking_plan, environment
            )
            
            # CDK templates (Python)
            templates['cdk'] = self._generate_cdk_template(
                region, compute_plan, storage_plan,
                database_plan, networking_plan, environment
            )
        
        return templates
    
    def _generate_terraform_template(
        self,
        region: str,
        compute_plan: Dict,
        storage_plan: Dict,
        database_plan: Dict,
        networking_plan: Dict,
        environment: Environment
    ) -> str:
        """Generate Terraform template."""
        template = f"""# Terraform configuration for Trading System Deployment
# Provider: {self.provider.value.upper()}
# Region: {region}
# Environment: {environment.value}
# Generated: {datetime.utcnow().isoformat()}

terraform {{
  required_version = ">= 1.3.0"
  
  required_providers {{
    aws = {{
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }}
  }}
  
  backend "s3" {{
    bucket = "terraform-state-{environment.value}"
    key    = "trading-system/{region}/terraform.tfstate"
    region = "{region}"
  }}
}}

provider "aws" {{
  region = "{region}"
  
  default_tags {{
    tags = {{
      Project     = "TradingSystem"
      Environment = "{environment.value}"
      ManagedBy   = "Terraform"
    }}
  }}
}}

# VPC Configuration
module "vpc" {{
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 3.0"
  
  name = "trading-vpc-{environment.value}"
  cidr = "{networking_plan['vpc_design']['cidr']}"
  
  azs             = ["${{local.availability_zones}}"]
  private_subnets = {json.dumps(networking_plan['vpc_design']['subnets']['private'])}
  public_subnets  = {json.dumps(networking_plan['vpc_design']['subnets']['public'])}
  
  enable_nat_gateway = true
  single_nat_gateway = false
  
  tags = {{
    Environment = "{environment.value}"
  }}
}}

# Compute Resources
{"".join(self._generate_compute_resources(compute_plan, environment))}

# Storage Resources
{"".join(self._generate_storage_resources(storage_plan, environment))}

# Database Resources
{"".join(self._generate_database_resources(database_plan, environment))}

# Outputs
output "load_balancer_dns" {{
  description = "DNS name of the load balancer"
  value       = module.alb.lb_dns_name
}}

output "database_endpoint" {{
  description = "Database endpoint"
  value       = module.database.db_instance_address
  sensitive   = true
}}
"""
        return template
    
    def _generate_compute_resources(
        self,
        compute_plan: Dict,
        environment: Environment
    ) -> List[str]:
        """Generate compute resource definitions."""
        resources = []
        
        if compute_plan['deployment_model'] == DeploymentModel.VM.value:
            resources.append(f"""
# EC2 Instances for High-Frequency Trading
resource "aws_instance" "trading_servers" {{
  count = {compute_plan['capacity'].get('baseline_instances', 2)}
  
  ami           = data.aws_ami.ubuntu.id
  instance_type = "{compute_plan['instance_types'][0] if compute_plan['instance_types'] else 'c5.4xlarge'}"
  
  subnet_id              = module.vpc.private_subnets[count.index % length(module.vpc.private_subnets)]
  vpc_security_group_ids = [aws_security_group.trading.id]
  
  root_block_device {{
    volume_type = "gp3"
    volume_size = 100
    encrypted   = true
  }}
  
  tags = {{
    Name = "trading-server-${{count.index}}"
  }}
}}
""")
        
        elif compute_plan['deployment_model'] == DeploymentModel.CONTAINER.value:
            resources.append(f"""
# ECS Cluster for Containerized Trading
resource "aws_ecs_cluster" "trading" {{
  name = "trading-cluster-{environment.value}"
  
  setting {{
    name  = "containerInsights"
    value = "enabled"
  }}
}}

# ECS Service Auto-scaling
resource "aws_appautoscaling_target" "trading_service" {{
  max_capacity       = {compute_plan['capacity'].get('max_instances', 10)}
  min_capacity       = {compute_plan['capacity'].get('min_instances', 2)}
  resource_id        = "service/${{aws_ecs_cluster.trading.name}}/${{aws_ecs_service.trading.name}}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}}
""")
        
        return resources
    
    def _generate_storage_resources(
        self,
        storage_plan: Dict,
        environment: Environment
    ) -> List[str]:
        """Generate storage resource definitions."""
        resources = []
        
        # S3 Bucket for market data
        resources.append(f"""
# S3 Bucket for Market Data
resource "aws_s3_bucket" "market_data" {{
  bucket = "market-data-{environment.value}-${{random_id.bucket_suffix.hex}}"
  
  tags = {{
    Name = "market-data-{environment.value}"
  }}
}}

resource "aws_s3_bucket_lifecycle_configuration" "market_data" {{
  bucket = aws_s3_bucket.market_data.id
  
  rule {{
    id     = "tiering"
    status = "Enabled"
    
    transition {{
      days          = {storage_plan.get('market_data', {{}}).get('tiering', {{}}).get('hot', 30)}
      storage_class = "STANDARD_IA"
    }}
    
    transition {{
      days          = {storage_plan.get('market_data', {{}}).get('tiering', {{}}).get('warm', 90)}
      storage_class = "GLACIER"
    }}
  }}
}}
""")
        
        return resources
    
    def _generate_database_resources(
        self,
        database_plan: Dict,
        environment: Environment
    ) -> List[str]:
        """Generate database resource definitions."""
        resources = []
        
        if database_plan.get('primary', {}).get('type') == 'relational':
            resources.append(f"""
# RDS PostgreSQL Database
module "database" {{
  source  = "terraform-aws-modules/rds/aws"
  version = "~> 5.0"
  
  identifier = "trading-db-{environment.value}"
  
  engine               = "postgres"
  engine_version       = "14"
  family              = "postgres14"
  instance_class      = "db.r5.large"
  
  allocated_storage     = 100
  max_allocated_storage = 500
  
  db_name  = "trading"
  username = "trading_admin"
  password = random_password.db_password.result
  
  vpc_security_group_ids = [aws_security_group.database.id]
  subnet_ids             = module.vpc.database_subnets
  
  multi_az               = {"true" if environment == Environment.PROD else "false"}
  publicly_accessible    = false
  
  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  
  tags = {{
    Name = "trading-db-{environment.value}"
  }}
}}
""")
        
        return resources
    
    def _generate_cloudformation_template(
        self,
        region: str,
        compute_plan: Dict,
        storage_plan: Dict,
        database_plan: Dict,
        networking_plan: Dict,
        environment: Environment
    ) -> str:
        """Generate CloudFormation template."""
        # Simplified template
        template = {
            'AWSTemplateFormatVersion': '2010-09-09',
            'Description': f'Trading System Deployment - {environment.value}',
            'Parameters': {
                'EnvironmentName': {
                    'Type': 'String',
                    'Default': environment.value,
                    'Description': 'Deployment environment'
                },
                'VpcCIDR': {
                    'Type': 'String',
                    'Default': networking_plan['vpc_design']['cidr'],
                    'Description': 'VPC CIDR block'
                }
            },
            'Resources': {
                'TradingVPC': {
                    'Type': 'AWS::EC2::VPC',
                    'Properties': {
                        'CidrBlock': {'Ref': 'VpcCIDR'},
                        'EnableDnsSupport': True,
                        'EnableDnsHostnames': True,
                        'Tags': [
                            {'Key': 'Name', 'Value': {'Fn::Sub': 'trading-vpc-${EnvironmentName}'}},
                            {'Key': 'Environment', 'Value': {'Ref': 'EnvironmentName'}}
                        ]
                    }
                }
            },
            'Outputs': {
                'VPCId': {
                    'Description': 'VPC ID',
                    'Value': {'Ref': 'TradingVPC'}
                }
            }
        }
        
        return json.dumps(template, indent=2)
    
    def _generate_cdk_template(
        self,
        region: str,
        compute_plan: Dict,
        storage_plan: Dict,
        database_plan: Dict,
        networking_plan: Dict,
        environment: Environment
    ) -> str:
        """Generate AWS CDK template in Python."""
        template = f'''"""
AWS CDK Stack for Trading System Deployment
Environment: {environment.value}
Region: {region}
Generated: {datetime.utcnow().isoformat()}
"""

from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_rds as rds,
    aws_s3 as s3,
    aws_elasticache as elasticache,
    RemovalPolicy,
    Duration,
)
from constructs import Construct


class TradingSystemStack(Stack):
    """Trading System Infrastructure Stack."""

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # VPC
        vpc = ec2.Vpc(
            self, "TradingVPC",
            max_azs=2,
            cidr="{networking_plan['vpc_design']['cidr']}",
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name="Private",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name="Database",
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                    cidr_mask=24
                )
            ]
        )

        # Security Groups
        trading_sg = ec2.SecurityGroup(
            self, "TradingSecurityGroup",
            vpc=vpc,
            description="Security group for trading services",
            allow_all_outbound=True
        )

        # Compute Resources
        {self._generate_cdk_compute(compute_plan, environment)}
        
        # Storage Resources  
        {self._generate_cdk_storage(storage_plan, environment)}
        
        # Database Resources
        {self._generate_cdk_database(database_plan, environment, 'vpc', 'trading_sg')}

    {self._generate_cdk_compute_method(compute_plan)}
    {self._generate_cdk_storage_method(storage_plan)}
    {self._generate_cdk_database_method(database_plan)}
'''
        return template
    
    def _generate_cdk_compute(self, compute_plan: Dict, environment: Environment) -> str:
        """Generate CDK compute resource code."""
        if compute_plan['deployment_model'] == DeploymentModel.VM.value:
            return """
        # EC2 Instances for High-Frequency Trading
        for i in range(2):  # Start with 2 instances
            ec2.Instance(
                self, f"TradingServer{i}",
                vpc=vpc,
                instance_type=ec2.InstanceType("c5.4xlarge"),
                machine_image=ec2.MachineImage.latest_amazon_linux(),
                security_group=trading_sg,
                vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS)
            )
"""
        elif compute_plan['deployment_model'] == DeploymentModel.CONTAINER.value:
            return """
        # ECS Cluster for Containerized Trading
        cluster = ecs.Cluster(
            self, "TradingCluster",
            vpc=vpc,
            container_insights=True
        )
"""
        else:
            return ""
    
    def _generate_cdk_compute_method(self, compute_plan: Dict) -> str:
        """Generate CDK compute method."""
        return """
    def _setup_compute_resources(self):
        '''Setup compute resources based on deployment model.'''
        pass
"""
    
    def _generate_cdk_storage(self, storage_plan: Dict, environment: Environment) -> str:
        """Generate CDK storage resource code."""
        return """
        # S3 Bucket for Market Data
        market_data_bucket = s3.Bucket(
            self, "MarketDataBucket",
            versioned=True,
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            lifecycle_rules=[
                s3.LifecycleRule(
                    transitions=[
                        s3.Transition(
                            storage_class=s3.StorageClass.INFREQUENT_ACCESS,
                            transition_after=Duration.days(30)
                        ),
                        s3.Transition(
                            storage_class=s3.StorageClass.GLACIER,
                            transition_after=Duration.days(90)
                        )
                    ]
                )
            ]
        )
"""
    
    def _generate_cdk_storage_method(self, storage_plan: Dict) -> str:
        """Generate CDK storage method."""
        return """
    def _setup_storage_resources(self):
        '''Setup storage resources with lifecycle policies.'''
        pass
"""
    
    def _generate_cdk_database(
        self,
        database_plan: Dict,
        environment: Environment,
        vpc_var: str,
        sg_var: str
    ) -> str:
        """Generate CDK database resource code."""
        if database_plan.get('primary', {}).get('type') == 'relational':
            return f"""
        # RDS PostgreSQL Database
        database = rds.DatabaseInstance(
            self, "TradingDatabase",
            engine=rds.DatabaseInstanceEngine.postgres(
                version=rds.PostgresEngineVersion.VER_14
            ),
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.R5,
                ec2.InstanceSize.LARGE
            ),
            vpc={vpc_var},
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
            ),
            security_groups=[{sg_var}],
            multi_az={environment == Environment.PROD},
            allocated_storage=100,
            max_allocated_storage=500,
            storage_encrypted=True,
            backup_retention=Duration.days(7),
            deletion_protection={environment == Environment.PROD}
        )
"""
        else:
            return ""
    
    def _generate_cdk_database_method(self, database_plan: Dict) -> str:
        """Generate CDK database method."""
        return """
    def _setup_database_resources(self):
        '''Setup database resources with high availability.'''
        pass
"""
    
    def _generate_deployment_steps(self, environment: Environment) -> List[str]:
        """Generate deployment steps."""
        steps = [
            "1. Initialize infrastructure as code (Terraform/CDK/CloudFormation)",
            "2. Create VPC and networking resources",
            "3. Deploy security groups and IAM roles",
            "4. Create storage resources (S3 buckets, EBS volumes)",
            "5. Deploy database instances",
            "6. Set up compute resources (EC2/ECS/Lambda)",
            "7. Configure load balancing and DNS",
            "8. Deploy application code and containers",
            "9. Set up monitoring and alerting",
            "10. Run smoke tests and validate deployment",
            "11. Update DNS records and enable traffic"
        ]
        
        if environment == Environment.PROD:
            steps.insert(1, "1a. Review and approve deployment plan")
            steps.insert(6, "6a. Perform blue-green deployment validation")
            steps.append("12. Enable automatic failover and backup verification")
        
        return steps
    
    def save_deployment_plan(self, plan: Dict, output_dir: str = "deployment_plans"):
        """Save deployment plan to files."""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        provider = plan['provider']
        env = plan['environment']
        filename = f"{provider}_{env}_{timestamp}"
        
        # Save full plan as JSON
        plan_path = output_path / f"{filename}_plan.json"
        with open(plan_path, 'w') as f:
            json.dump(plan, f, indent=2, default=str)
        
        # Save IaC templates
        iac_dir = output_path / f"{filename}_iac"
        iac_dir.mkdir(exist_ok=True)
        
        for template_type, content in plan['iac_templates'].items():
            if template_type == 'terraform':
                ext = '.tf'
            elif template_type == 'cloudformation':
                ext = '.json'
            elif template_type == 'cdk':
                ext = '.py'
            else:
                ext = '.txt'
            
            template_path = iac_dir / f"main{ext}"
            with open(template_path, 'w') as f:
                f.write(content)
        
        # Save deployment steps
        steps_path = output_path / f"{filename}_steps.md"
        with open(steps_path, 'w') as f:
            f.write(f"# Deployment Steps for {provider.upper()} {env.upper()}\n\n")
            for step in plan['deployment_steps']:
                f.write(f"{step}\n")
        
        print(f"\n✅ Deployment plan saved to:")
        print(f"   Plan: {plan_path}")
        print(f"   IaC Templates: {iac_dir}")
        print(f"   Steps: {steps_path}")
        
        return {
            'plan_path': str(plan_path),
            'iac_dir': str(iac_dir),
            'steps_path': str(steps_path)
        }


class CloudCostOptimizer:
    """
    Optimize cloud costs for trading systems.
    Analyzes usage patterns and suggests optimizations.
    """
    
    def __init__(self, provider: CloudProvider = CloudProvider.AWS):
        self.provider = provider
        
        # Cost optimization patterns
        self.optimization_patterns = {
            'compute': [
                {
                    'name': 'right_sizing',
                    'description': 'Match instance size to actual workload requirements',
                    'savings_potential': 0.3,  # 30% savings
                    'implementation': 'Analyze CPU/memory usage and resize instances'
                },
                {
                    'name': 'reserved_instances',
                    'description': 'Purchase reserved instances for predictable workloads',
                    'savings_potential': 0.4,  # 40% savings
                    'implementation': 'Convert on-demand to 1-year or 3-year reservations'
                },
                {
                    'name': 'spot_instances',
                    'description': 'Use spot instances for fault-tolerant workloads',
                    'savings_potential': 0.7,  # 70% savings
                    'implementation': 'Implement spot fleets with fallback to on-demand'
                }
            ],
            'storage': [
                {
                    'name': 'lifecycle_policies',
                    'description': 'Move infrequently accessed data to cheaper storage classes',
                    'savings_potential': 0.6,  # 60% savings
                    'implementation': 'Implement S3 lifecycle policies based on access patterns'
                },
                {
                    'name': 'compression',
                    'description': 'Compress data to reduce storage requirements',
                    'savings_potential': 0.5,  # 50% savings
                    'implementation': 'Enable compression for databases and file storage'
                },
                {
                    'name': 'data_retention',
                    'description': 'Implement data retention policies',
                    'savings_potential': 0.4,  # 40% savings
                    'implementation': 'Archive or delete old data based on compliance requirements'
                }
            ],
            'database': [
                {
                    'name': 'auto_scaling',
                    'description': 'Use database auto-scaling for variable workloads',
                    'savings_potential': 0.3,  # 30% savings
                    'implementation': 'Enable read replica auto-scaling and storage auto-scaling'
                },
                {
                    'name': 'serverless',
                    'description': 'Use serverless databases for intermittent workloads',
                    'savings_potential': 0.7,  # 70% savings
                    'implementation': 'Migrate to Aurora Serverless or DynamoDB on-demand'
                }
            ],
            'networking': [
                {
                    'name': 'data_transfer_optimization',
                    'description': 'Optimize data transfer between regions and services',
                    'savings_potential': 0.5,  # 50% savings
                    'implementation': 'Use VPC endpoints, compress data, and batch transfers'
                },
                {
                    'name': 'cdn_caching',
                    'description': 'Use CDN for static content delivery',
                    'savings_potential': 0.6,  # 60% savings
                    'implementation': 'Configure CloudFront for API responses and static assets'
                }
            ]
        }
    
    def analyze_usage_patterns(self, workload: TradingWorkload) -> Dict:
        """
        Analyze usage patterns for cost optimization opportunities.
        
        Args:
            workload: Trading workload characteristics
            
        Returns:
            Dict: Optimization recommendations
        """
        print(f"\nAnalyzing usage patterns for {workload.trading_frequency} frequency trading...")
        
        recommendations = {
            'compute': [],
            'storage': [],
            'database': [],
            'networking': [],
            'estimated_savings': 0.0
        }
        
        # Analyze compute patterns
        if workload.trading_frequency == 'high':
            # HFT: Use reserved instances, avoid spot
            recommendations['compute'].append(self.optimization_patterns['compute'][1])  # Reserved instances
            
        elif workload.trading_frequency == 'medium':
            # Medium frequency: Mix of reserved and spot
            recommendations['compute'].append(self.optimization_patterns['compute'][1])  # Reserved instances
            recommendations['compute'].append(self.optimization_patterns['compute'][2])  # Spot instances
            
        else:  # Low frequency
            # Low frequency: Serverless and spot
            recommendations['compute'].append(self.optimization_patterns['compute'][2])  # Spot instances
            recommendations['database'].append(self.optimization_patterns['database'][1])  # Serverless DB
        
        # Storage optimizations based on data volume
        if workload.data_volume_gb_per_day > 10:
            recommendations['storage'].extend([
                self.optimization_patterns['storage'][0],  # Lifecycle policies
                self.optimization_patterns['storage'][1]   # Compression
            ])
        
        # Calculate estimated savings
        total_savings = 0.0
        
        for category, opts in recommendations.items():
            if category != 'estimated_savings':
                for opt in opts:
                    total_savings += opt['savings_potential']
        
        # Average savings across categories
        if recommendations['compute'] or recommendations['storage'] or recommendations['database']:
            avg_savings = total_savings / max(1, len(recommendations['compute']) + 
                                              len(recommendations['storage']) + 
                                              len(recommendations['database']))
        else:
            avg_savings = 0.0
        
        recommendations['estimated_savings'] = avg_savings
        
        return recommendations
    
    def generate_cost_report(self, current_costs: Dict, recommendations: Dict) -> str:
        """
        Generate cost optimization report.
        
        Args:
            current_costs: Current monthly costs by category
            recommendations: Optimization recommendations
            
        Returns:
            str: Formatted cost report
        """
        report = f"""
        CLOUD COST OPTIMIZATION REPORT
        ==============================
        Generated: {datetime.utcnow().isoformat()}
        Provider: {self.provider.value.upper()}
        
        CURRENT COSTS:
        --------------
        """
        
        total_current = sum(current_costs.values())
        for category, cost in current_costs.items():
            percentage = (cost / total_current * 100) if total_current > 0 else 0
            report += f"  {category.title()}: ${cost:,.2f} ({percentage:.1f}%)\\n"
        
        report += f"  Total: ${total_current:,.2f}\\n\\n"
        
        report += "OPTIMIZATION RECOMMENDATIONS:\\n"
        report += "------------------------------\\n"
        
        estimated_savings = 0
        
        for category in ['compute', 'storage', 'database', 'networking']:
            if recommendations.get(category):
                report += f"\\n{category.upper()}:\\n"
                
                for rec in recommendations[category]:
                    savings_amount = current_costs.get(category, 0) * rec['savings_potential']
                    estimated_savings += savings_amount
                    
                    report += f"  • {rec['name'].replace('_', ' ').title()}\\n"
                    report += f"    Description: {rec['description']}\\n"
                    report += f"    Potential Savings: {rec['savings_potential']:.0%} (${savings_amount:,.2f}/month)\\n"
                    report += f"    Implementation: {rec['implementation']}\\n"
        
        new_total = total_current - estimated_savings
        savings_percentage = (estimated_savings / total_current * 100) if total_current > 0 else 0
        
        report += f"\\nSUMMARY:\\n"
        report += f"---------\\n"
        report += f"Current Monthly Cost: ${total_current:,.2f}\\n"
        report += f"Estimated Savings: ${estimated_savings:,.2f} ({savings_percentage:.1f}%)\\n"
        report += f"New Monthly Cost: ${new_total:,.2f}\\n"
        
        return report


class TradingSystemDeployer:
    """
    Deploy trading systems to cloud platforms.
    Supports multiple deployment strategies and environments.
    """
    
    def __init__(self, provider: CloudProvider = CloudProvider.AWS):
        self.provider = provider
        self.planner = CloudDeploymentPlanner(provider)
        self.optimizer = CloudCostOptimizer(provider)
        
        # Deployment status tracking
        self.deployments = {}
    
    def create_environment(
        self,
        environment: Environment,
        workload: TradingWorkload,
        performance_targets: PerformanceTarget,
        security_requirements: SecurityRequirement,
        dry_run: bool = True
    ) -> Dict:
        """
        Create a complete trading system environment.
        
        Args:
            environment: Environment to create
            workload: Trading workload characteristics
            performance_targets: Performance requirements
            security_requirements: Security requirements
            dry_run: If True, only plan without actual deployment
            
        Returns:
            Dict: Deployment results
        """
        print(f"\n{'Planning' if dry_run else 'Creating'} {environment.value} environment...")
        print("="*80)
        
        # 1. Plan deployment
        deployment_plan = self.planner.plan_deployment(
            workload, performance_targets, security_requirements, environment
        )
        
        # 2. Analyze cost optimization opportunities
        cost_recommendations = self.optimizer.analyze_usage_patterns(workload)
        
        # 3. Generate cost report
        current_costs = {
            'compute': deployment_plan['cost_estimate']['monthly_estimate'] * 0.5,
            'storage': deployment_plan['cost_estimate']['monthly_estimate'] * 0.2,
            'database': deployment_plan['cost_estimate']['monthly_estimate'] * 0.2,
            'networking': deployment_plan['cost_estimate']['monthly_estimate'] * 0.1
        }
        
        cost_report = self.optimizer.generate_cost_report(current_costs, cost_recommendations)
        
        # 4. Save deployment artifacts
        if dry_run:
            artifacts = self.planner.save_deployment_plan(deployment_plan)
            
            result = {
                'status': 'PLANNED',
                'environment': environment.value,
                'deployment_plan': deployment_plan,
                'cost_recommendations': cost_recommendations,
                'cost_report': cost_report,
                'artifacts': artifacts,
                'next_steps': [
                    'Review deployment plan',
                    'Adjust configuration if needed',
                    'Run actual deployment with dry_run=False'
                ]
            }
            
            print(f"\n✅ Environment planning complete for {environment.value}")
            print(f"   Estimated monthly cost: ${deployment_plan['cost_estimate']['monthly_estimate']:,.2f}")
            print(f"   Potential savings: {cost_recommendations['estimated_savings']:.0%}")
            
        else:
            # Actual deployment would go here
            # This would involve calling cloud provider APIs to create resources
            print(f"\n🚀 Starting actual deployment for {environment.value}...")
            
            # Simulate deployment steps
            deployment_id = f"deploy_{int(time.time())}"
            
            for i, step in enumerate(deployment_plan['deployment_steps'], 1):
                print(f"  Step {i:2d}: {step}")
                time.sleep(0.5)  # Simulate deployment time
            
            result = {
                'status': 'DEPLOYED',
                'environment': environment.value,
                'deployment_id': deployment_id,
                'deployment_plan': deployment_plan,
                'endpoints': {
                    'api_gateway': f'https://api.{environment.value}.trading.example.com',
                    'monitoring': f'https://monitor.{environment.value}.trading.example.com',
                    'database': f'database.{environment.value}.trading.example.com'
                },
                'cost_report': cost_report,
                'monitoring_instructions': self._generate_monitoring_instructions(environment)
            }
            
            # Track deployment
            self.deployments[deployment_id] = {
                'environment': environment.value,
                'timestamp': datetime.utcnow().isoformat(),
                'status': 'ACTIVE'
            }
            
            print(f"\n✅ Environment deployment complete!")
            print(f"   Deployment ID: {deployment_id}")
            print(f"   API Endpoint: {result['endpoints']['api_gateway']}")
        
        return result
    
    def _generate_monitoring_instructions(self, environment: Environment) -> str:
        """Generate monitoring setup instructions."""
        instructions = f"""
        MONITORING SETUP FOR {environment.value.upper()} ENVIRONMENT
        ===========================================================
        
        1. CLOUDWATCH DASHBOARDS:
           - Create dashboard: Trading-{environment.value}
           - Add widgets for:
             * CPU/Memory utilization
             * API latency and error rates
             * Database performance metrics
             * Cost and usage metrics
        
        2. ALARMS TO CONFIGURE:
           - High CPU utilization (>80% for 5 minutes)
           - High memory utilization (>85% for 5 minutes)
           - API error rate (>1% for 5 minutes)
           - Database connection count (>80% of limit)
           - Monthly cost threshold (80% of budget)
        
        3. LOG AGGREGATION:
           - Enable CloudWatch Logs for all services
           - Set up log groups with retention policies:
             * Application logs: 30 days
             * Access logs: 90 days
             * Audit logs: 365 days
        
        4. PERFORMANCE MONITORING:
           - Enable X-Ray tracing for distributed tracing
           - Set up synthetic monitoring for key user journeys
           - Configure Real User Monitoring (RUM) for web interface
        
        5. COST MONITORING:
           - Enable Cost Explorer with daily reports
           - Set up budget alerts at 50%, 80%, 100% of budget
           - Tag all resources for cost allocation
        
        Next Steps:
        1. Review and customize alarms based on your SLAs
        2. Set up notification channels (Email, Slack, PagerDuty)
        3. Create runbooks for common incidents
        4. Schedule regular reviews of monitoring configuration
        """
        
        return instructions
    
    def list_deployments(self) -> List[Dict]:
        """List all deployments."""
        return [
            {
                'deployment_id': dep_id,
                **details
            }
            for dep_id, details in self.deployments.items()
        ]
    
    def teardown_environment(self, deployment_id: str, dry_run: bool = True) -> Dict:
        """
        Teardown a deployed environment.
        
        Args:
            deployment_id: ID of deployment to teardown
            dry_run: If True, only show what would be deleted
            
        Returns:
            Dict: Teardown results
        """
        if deployment_id not in self.deployments:
            return {'error': f'Deployment {deployment_id} not found'}
        
        deployment = self.deployments[deployment_id]
        
        print(f"\n{'Planning' if dry_run else 'Starting'} teardown of {deployment_id}...")
        print(f"Environment: {deployment['environment']}")
        
        # Simulate teardown steps
        teardown_steps = [
            "1. Disable auto-scaling policies",
            "2. Terminate compute instances",
            "3. Delete load balancers",
            "4. Delete database instances (with final snapshot)",
            "5. Delete storage buckets (after confirming backup)",
            "6. Remove security groups and IAM roles",
            "7. Delete VPC resources",
            "8. Clean up monitoring resources",
            "9. Verify all resources are deleted",
            "10. Update deployment tracking"
        ]
        
        for step in teardown_steps:
            print(f"  {step}")
            if not dry_run:
                time.sleep(0.3)  # Simulate teardown time
        
        if not dry_run:
            # Mark deployment as terminated
            self.deployments[deployment_id]['status'] = 'TERMINATED'
            self.deployments[deployment_id]['terminated_at'] = datetime.utcnow().isoformat()
            
            result = {
                'status': 'TERMINATED',
                'deployment_id': deployment_id,
                'environment': deployment['environment'],
                'terminated_at': self.deployments[deployment_id]['terminated_at'],
                'backup_created': True,
                'final_snapshot_id': f"snapshot-{deployment_id}"
            }
            
            print(f"\n✅ Environment {deployment_id} terminated successfully")
            
        else:
            result = {
                'status': 'TEARDOWN_PLANNED',
                'deployment_id': deployment_id,
                'environment': deployment['environment'],
                'steps': teardown_steps,
                'warning': 'This is a dry run. No resources will be deleted.'
            }
            
            print(f"\n📋 Teardown plan generated for {deployment_id}")
            print("   Run with dry_run=False to execute teardown")
        
        return result


def demonstrate_cloud_deployment():
    """Demonstrate cloud deployment planning and optimization."""
    print("\n" + "="*80)
    print("Day 86: Cloud Deployment for Trading Systems")
    print("="*80)
    
    # Create sample requirements
    workload = TradingWorkload(
        trading_frequency="medium",
        data_volume_gb_per_day=50.0,
        peak_events_per_second=5000,
        average_events_per_second=1000,
        market_hours_coverage="market-hours"
    )
    
    performance_targets = PerformanceTarget(
        max_latency_ms=100,
        min_throughput_rps=1000,
        availability_target=0.9999,
        recovery_time_objective=300  # 5 minutes
    )
    
    security_requirements = SecurityRequirement(
        encryption_at_rest=True,
        encryption_in_transit=True,
        vpc_isolation=True,
        audit_logging=True,
        compliance_frameworks=["SOC2", "GDPR"]
    )
    
    # Create deployer for AWS
    deployer = TradingSystemDeployer(CloudProvider.AWS)
    
    print("\n1. Planning Production Environment...")
    prod_result = deployer.create_environment(
        environment=Environment.PROD,
        workload=workload,
        performance_targets=performance_targets,
        security_requirements=security_requirements,
        dry_run=True
    )
    
    print("\n2. Planning Development Environment...")
    # Lower requirements for dev
    dev_workload = TradingWorkload(
        trading_frequency="low",
        data_volume_gb_per_day=5.0,
        peak_events_per_second=500,
        average_events_per_second=100,
        market_hours_coverage="specific-hours"
    )
    
    dev_result = deployer.create_environment(
        environment=Environment.DEV,
        workload=dev_workload,
        performance_targets=performance_targets,
        security_requirements=security_requirements,
        dry_run=True
    )
    
    print("\n3. Cost Comparison:")
    prod_cost = prod_result['deployment_plan']['cost_estimate']['monthly_estimate']
    dev_cost = dev_result['deployment_plan']['cost_estimate']['monthly_estimate']
    
    print(f"   Production: ${prod_cost:,.2f}/month")
    print(f"   Development: ${dev_cost:,.2f}/month")
    print(f"   Ratio: {prod_cost/dev_cost:.1f}x more expensive")
    
    print("\n4. Optimization Opportunities:")
    prod_savings = prod_result['cost_recommendations']['estimated_savings']
    dev_savings = dev_result['cost_recommendations']['estimated_savings']
    
    print(f"   Production savings potential: {prod_savings:.0%}")
    print(f"   Development savings potential: {dev_savings:.0%}")
    
    print("\n5. Deployment Artifacts Generated:")
    print(f"   Production plan: {prod_result['artifacts']['plan_path']}")
    print(f"   Development plan: {dev_result['artifacts']['plan_path']}")
    
    # Show cost report
    print("\n" + "="*80)
    print("SAMPLE COST OPTIMIZATION REPORT")
    print("="*80)
    
    # Create sample current costs for demo
    sample_costs = {
        'compute': 5000.0,
        'storage': 1000.0,
        'database': 1500.0,
        'networking': 500.0
    }
    
    optimizer = CloudCostOptimizer(CloudProvider.AWS)
    sample_recommendations = optimizer.analyze_usage_patterns(workload)
    cost_report = optimizer.generate_cost_report(sample_costs, sample_recommendations)
    
    print(cost_report)
    
    print("\n" + "="*80)
    print("CLOUD DEPLOYMENT BEST PRACTICES:")
    print("="*80)
    print("\n1. COST OPTIMIZATION:")
    print("   • Use reserved instances for stable workloads")
    print("   • Implement auto-scaling based on trading hours")
    print("   • Use spot instances for non-critical components")
    print("   • Implement storage lifecycle policies")
    print("   • Monitor with AWS Cost Explorer")
    
    print("\n2. PERFORMANCE OPTIMIZATION:")
    print("   • Use low-latency instance types (c5n, c6i)")
    print("   • Implement connection pooling")
    print("   • Use read replicas for databases")
    print("   • Implement caching strategies")
    print("   • Optimize network paths")
    
    print("\n3. SECURITY BEST PRACTICES:")
    print("   • Use private subnets for sensitive resources")
    print("   • Implement least-privilege IAM policies")
    print("   • Encrypt data at rest and in transit")
    print("   • Regular security audits")
    print("   • Implement WAF and DDoS protection")
    
    print("\n4. OPERATIONAL EXCELLENCE:")
    print("   • Implement comprehensive monitoring")
    print("   • Use infrastructure as code")
    print("   • Implement blue-green deployments")
    print("   • Regular backup and disaster recovery testing")
    print("   • Document runbooks and procedures")
    
    print("\n" + "="*80)
    print("NEXT STEPS:")
    print("="*80)
    print("1. Review generated deployment plans")
    print("2. Adjust configurations based on specific requirements")
    print("3. Deploy to cloud using generated IaC templates")
    print("4. Set up monitoring and alerting")
    print("5. Perform load testing and optimization")
    print("6. Implement cost monitoring and optimization cycles")


def compare_cloud_providers():
    """Compare different cloud providers for trading workloads."""
    print("\n" + "="*80)
    print("Cloud Provider Comparison for Trading Systems")
    print("="*80)
    
    # Sample workload
    workload = TradingWorkload(
        trading_frequency="high",
        data_volume_gb_per_day=100.0,
        peak_events_per_second=10000,
        average_events_per_second=2000,
        market_hours_coverage="market-hours"
    )
    
    requirements = PerformanceTarget(
        max_latency_ms=50,  # Very low latency for HFT
        min_throughput_rps=5000,
        availability_target=0.9999,
        recovery_time_objective=60  # 1 minute for HFT
    )
    
    security = SecurityRequirement(
        encryption_at_rest=True,
        encryption_in_transit=True,
        vpc_isolation=True,
        audit_logging=True,
        compliance_frameworks=["SOC2", "PCI-DSS"]
    )
    
    providers = [CloudProvider.AWS, CloudProvider.AZURE, CloudProvider.GCP]
    results = {}
    
    for provider in providers:
        print(f"\nAnalyzing {provider.value.upper()}...")
        
        planner = CloudDeploymentPlanner(provider)
        
        try:
            plan = planner.plan_deployment(
                workload, requirements, security, Environment.PROD
            )
            
            results[provider] = {
                'monthly_cost': plan['cost_estimate']['monthly_estimate'],
                'region': plan['region'],
                'compute_model': plan['compute_plan']['deployment_model'],
                'optimization_suggestions': plan['cost_estimate']['optimization_suggestions']
            }
            
        except Exception as e:
            print(f"  Error analyzing {provider.value}: {e}")
            results[provider] = {'error': str(e)}
    
    # Compare results
    print("\n" + "="*80)
    print("COMPARISON RESULTS")
    print("="*80)
    
    valid_results = {k: v for k, v in results.items() if 'error' not in v}
    
    if valid_results:
        # Find cheapest provider
        cheapest = min(valid_results.items(), key=lambda x: x[1]['monthly_cost'])
        print(f"\n💰 Most Cost Effective: {cheapest[0].value.upper()}")
        print(f"   Monthly Cost: ${cheapest[1]['monthly_cost']:,.2f}")
        
        # Provider details
        for provider, data in valid_results.items():
            print(f"\n{provider.value.upper()}:")
            print(f"  Monthly Cost: ${data['monthly_cost']:,.2f}")
            print(f"  Recommended Region: {data['region']}")
            print(f"  Compute Model: {data['compute_model']}")
            print(f"  Optimization Suggestions:")
            for suggestion in data['optimization_suggestions'][:2]:
                print(f"    • {suggestion}")
    
    print("\n" + "="*80)
    print("RECOMMENDATIONS:")
    print("="*80)
    print("\nFor High-Frequency Trading:")
    print("  Primary: AWS (best ecosystem for trading, lowest latency options)")
    print("  Secondary: GCP (strong data analytics, good ML integration)")
    print("  Consider: Hybrid (on-prem for ultra-low latency, cloud for everything else)")
    
    print("\nFor Medium-Frequency Trading:")
    print("  AWS: Mature, extensive service catalog")
    print("  Azure: Good for enterprises already using Microsoft stack")
    print("  GCP: Excellent for data-heavy and ML-driven strategies")
    
    print("\nFor Low-Frequency/Research:")
    print("  GCP: Best for data analytics and ML")
    print("  AWS: Good all-around choice")
    print("  Consider: Multi-cloud for best-of-breed services")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Cloud Deployment for Trading Systems')
    parser.add_argument('--demo', action='store_true', help='Run deployment demonstration')
    parser.add_argument('--compare', action='store_true', help='Compare cloud providers')
    parser.add_argument('--plan', help='Generate deployment plan for environment (dev/staging/prod)')
    parser.add_argument('--provider', default='aws', choices=['aws', 'azure', 'gcp'], 
                       help='Cloud provider to use')
    
    args = parser.parse_args()
    
    # Map provider string to enum
    provider_map = {
        'aws': CloudProvider.AWS,
        'azure': CloudProvider.AZURE,
        'gcp': CloudProvider.GCP
    }
    
    provider = provider_map.get(args.provider, CloudProvider.AWS)
    
    if args.demo:
        demonstrate_cloud_deployment()
    
    elif args.compare:
        compare_cloud_providers()
    
    elif args.plan:
        # Generate specific deployment plan
        env_map = {
            'dev': Environment.DEV,
            'staging': Environment.STAGING,
            'prod': Environment.PROD
        }
        
        if args.plan not in env_map:
            print(f"Error: Environment must be one of: {', '.join(env_map.keys())}")
            return
        
        environment = env_map[args.plan]
        
        # Sample requirements
        workload = TradingWorkload(
            trading_frequency="medium",
            data_volume_gb_per_day=50.0,
            peak_events_per_second=5000,
            average_events_per_second=1000,
            market_hours_coverage="market-hours"
        )
        
        performance_targets = PerformanceTarget(
            max_latency_ms=100,
            min_throughput_rps=1000,
            availability_target=0.999,
            recovery_time_objective=300
        )
        
        security_requirements = SecurityRequirement(
            encryption_at_rest=True,
            encryption_in_transit=True,
            vpc_isolation=True,
            audit_logging=True,
            compliance_frameworks=["SOC2"]
        )
        
        deployer = TradingSystemDeployer(provider)
        result = deployer.create_environment(
            environment=environment,
            workload=workload,
            performance_targets=performance_targets,
            security_requirements=security_requirements,
            dry_run=True
        )
        
        print(f"\n✅ Deployment plan generated for {args.plan} on {provider.value.upper()}")
        print(f"   Cost estimate: ${result['deployment_plan']['cost_estimate']['monthly_estimate']:,.2f}/month")
        print(f"   Plan saved to: {result['artifacts']['plan_path']}")
    
    else:
        # Default: run demonstration
        demonstrate_cloud_deployment()


if __name__ == "__main__":
    main()