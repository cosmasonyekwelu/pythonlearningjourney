# Day 86: Cloud Deployment for Trading Systems

## Objective
Deploy trading system components to cloud platforms with environment isolation, scalability, cost optimization, and production readiness.

## Core Concepts
* Cloud Platform Selection: Enterprise-grade (AWS EC2/ECS/EKS, Azure VMs/AKS, GCP Compute Engine/GKE), Managed platforms (Render, Railway, Vercel), Quant-specific (QuantConnect cloud), Cost analysis for trading workloads, Region selection based on latency requirements
* Deployment Models: VM-based deployments for full control, Container-orchestrated deployments (ECS, EKS, AKS), Serverless architectures (Lambda, Azure Functions), Hybrid approaches, Auto-scaling groups and regional deployments
* Infrastructure as Code (IaC): Terraform for multi-cloud provisioning, AWS CloudFormation/Azure Resource Manager templates, Pulumi/AWS CDK for programming language-based infrastructure, Serverless framework for event-driven architecture
* Cost & Performance Optimization: Spot instances for non-critical processing, Reserved instances for stable workloads, Auto-scaling based on market hours, Data transfer optimization, Monitoring cloud usage with budget alerts
* Security & Compliance: IAM roles and policies following least privilege, Secrets management (AWS Secrets Manager/Azure Key Vault/HashiCorp Vault), VPC design with private subnets, Compliance frameworks (SOC 2, GDPR, PCI-DSS), Broker integrations via secure cloud APIs
* Live Trading Considerations: Monitoring latency to data feeds and execution venues, Private networking and dedicated connections, Environment parity between development/staging/production, Blue-green deployments and canary releases

## Tutorial: Trading System Deployment on AWS ECS with Terraform

This tutorial creates a complete AWS infrastructure for deploying trading systems using ECS Fargate, with Terraform for infrastructure as code.

```python
# deployment/terraform/main.tf
"""
AWS Infrastructure for Trading System Deployment using Terraform.
Complete setup with ECS, RDS, Redis, and monitoring.
"""

terraform {
  required_version = ">= 1.3.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
    
    random = {
      source  = "hashicorp/random"
      version = "~> 3.4"
    }
  }
  
  backend "s3" {
    bucket         = "quantflow-terraform-state"
    key            = "trading-system/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
  }
}

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = "QuantFlow-Trading"
      Environment = var.environment
      ManagedBy   = "Terraform"
      CostCenter  = "Trading-Operations"
    }
  }
}

# ============================================================================
# Variables
# ============================================================================

variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Deployment environment (dev, staging, prod)"
  type        = string
  default     = "dev"
  
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod"
  }
}

variable "trading_hours_scaling" {
  description = "Enable scaling based on trading hours"
  type        = bool
  default     = true
}

variable "market_data_throughput" {
  description = "Expected market data throughput (events/second)"
  type        = number
  default     = 10000
}

variable "enable_spot_instances" {
  description = "Use spot instances for cost optimization"
  type        = bool
  default     = true
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "Availability zones to use"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b", "us-east-1c"]
}

variable "container_cpu" {
  description = "CPU units for containers"
  type        = map(number)
  default = {
    market_data = 2048   # 2 vCPU
    strategy    = 1024   # 1 vCPU
    execution   = 1024   # 1 vCPU
    risk        = 1024   # 1 vCPU
    api         = 512    # 0.5 vCPU
  }
}

variable "container_memory" {
  description = "Memory for containers (MB)"
  type        = map(number)
  default = {
    market_data = 4096   # 4GB
    strategy    = 2048   # 2GB
    execution   = 2048   # 2GB
    risk        = 2048   # 2GB
    api         = 1024   # 1GB
  }
}

# ============================================================================
# Local Values
# ============================================================================

locals {
  project_name = "quantflow-trading"
  
  # Environment-specific configurations
  environment_configs = {
    dev = {
      instance_count = {
        market_data = 1
        strategy    = 1
        execution   = 1
        risk        = 1
        api         = 1
      }
      database_instance_class = "db.t3.medium"
      redis_node_type         = "cache.t3.medium"
      enable_backup           = false
      multi_az               = false
    }
    
    staging = {
      instance_count = {
        market_data = 2
        strategy    = 2
        execution   = 2
        risk        = 2
        api         = 2
      }
      database_instance_class = "db.m5.large"
      redis_node_type         = "cache.m5.large"
      enable_backup           = true
      multi_az               = true
    }
    
    prod = {
      instance_count = {
        market_data = 3
        strategy    = 3
        execution   = 3
        risk        = 3
        api         = 3
      }
      database_instance_class = "db.r5.large"
      redis_node_type         = "cache.r5.large"
      enable_backup           = true
      multi_az               = true
    }
  }
  
  current_config = local.environment_configs[var.environment]
  
  # Common tags
  common_tags = {
    Project     = local.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
  
  # Trading hours schedule (EST: 9:30 AM - 4:00 PM)
  trading_hours = {
    start = "14:30"  # 9:30 AM EST = 14:30 UTC
    end   = "21:00"  # 4:00 PM EST = 21:00 UTC
  }
}

# ============================================================================
# Networking
# ============================================================================

# VPC
resource "aws_vpc" "trading_vpc" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = merge(local.common_tags, {
    Name = "${local.project_name}-vpc-${var.environment}"
  })
}

# Subnets
resource "aws_subnet" "public" {
  count = length(var.availability_zones)
  
  vpc_id                  = aws_vpc.trading_vpc.id
  cidr_block              = cidrsubnet(var.vpc_cidr, 8, count.index)
  availability_zone       = var.availability_zones[count.index]
  map_public_ip_on_launch = true
  
  tags = merge(local.common_tags, {
    Name = "${local.project_name}-public-${var.availability_zones[count.index]}"
    Type = "Public"
  })
}

resource "aws_subnet" "private" {
  count = length(var.availability_zones)
  
  vpc_id            = aws_vpc.trading_vpc.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index + 10)
  availability_zone = var.availability_zones[count.index]
  
  tags = merge(local.common_tags, {
    Name = "${local.project_name}-private-${var.availability_zones[count.index]}"
    Type = "Private"
  })
}

resource "aws_subnet" "data" {
  count = length(var.availability_zones)
  
  vpc_id            = aws_vpc.trading_vpc.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index + 20)
  availability_zone = var.availability_zones[count.index]
  
  tags = merge(local.common_tags, {
    Name = "${local.project_name}-data-${var.availability_zones[count.index]}"
    Type = "Data"
  })
}

# Internet Gateway
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.trading_vpc.id
  
  tags = merge(local.common_tags, {
    Name = "${local.project_name}-igw"
  })
}

# NAT Gateway (one per AZ for high availability)
resource "aws_eip" "nat" {
  count = length(var.availability_zones)
  
  domain = "vpc"
  
  tags = merge(local.common_tags, {
    Name = "${local.project_name}-nat-eip-${var.availability_zones[count.index]}"
  })
}

resource "aws_nat_gateway" "nat" {
  count = length(var.availability_zones)
  
  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id
  
  tags = merge(local.common_tags, {
    Name = "${local.project_name}-nat-${var.availability_zones[count.index]}"
  })
  
  depends_on = [aws_internet_gateway.igw]
}

# Route Tables
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.trading_vpc.id
  
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }
  
  tags = merge(local.common_tags, {
    Name = "${local.project_name}-public-rt"
  })
}

resource "aws_route_table" "private" {
  count = length(var.availability_zones)
  
  vpc_id = aws_vpc.trading_vpc.id
  
  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.nat[count.index].id
  }
  
  tags = merge(local.common_tags, {
    Name = "${local.project_name}-private-rt-${var.availability_zones[count.index]}"
  })
}

# Route Table Associations
resource "aws_route_table_association" "public" {
  count = length(var.availability_zones)
  
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "private" {
  count = length(var.availability_zones)
  
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private[count.index].id
}

resource "aws_route_table_association" "data" {
  count = length(var.availability_zones)
  
  subnet_id      = aws_subnet.data[count.index].id
  route_table_id = aws_route_table.private[count.index].id
}

# Security Groups
resource "aws_security_group" "load_balancer" {
  name        = "${local.project_name}-lb-sg"
  description = "Security group for load balancer"
  vpc_id      = aws_vpc.trading_vpc.id
  
  # Allow HTTP/HTTPS from anywhere
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTP access"
  }
  
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS access"
  }
  
  # Allow all outbound
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = merge(local.common_tags, {
    Name = "${local.project_name}-lb-sg"
  })
}

resource "aws_security_group" "ecs_service" {
  name        = "${local.project_name}-ecs-sg"
  description = "Security group for ECS services"
  vpc_id      = aws_vpc.trading_vpc.id
  
  # Allow from load balancer only
  ingress {
    from_port       = 0
    to_port         = 65535
    protocol        = "tcp"
    security_groups = [aws_security_group.load_balancer.id]
    description     = "From load balancer"
  }
  
  # Allow internal communication between services
  ingress {
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
    description = "Internal service communication"
  }
  
  # Allow all outbound
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = merge(local.common_tags, {
    Name = "${local.project_name}-ecs-sg"
  })
}

resource "aws_security_group" "database" {
  name        = "${local.project_name}-db-sg"
  description = "Security group for database"
  vpc_id      = aws_vpc.trading_vpc.id
  
  # Allow from ECS services only
  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs_service.id]
    description     = "PostgreSQL access from ECS"
  }
  
  # Allow all outbound
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = merge(local.common_tags, {
    Name = "${local.project_name}-db-sg"
  })
}

resource "aws_security_group" "redis" {
  name        = "${local.project_name}-redis-sg"
  description = "Security group for Redis"
  vpc_id      = aws_vpc.trading_vpc.id
  
  # Allow from ECS services only
  ingress {
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs_service.id]
    description     = "Redis access from ECS"
  }
  
  # Allow all outbound
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = merge(local.common_tags, {
    Name = "${local.project_name}-redis-sg"
  })
}

# ============================================================================
# Database (PostgreSQL with TimescaleDB)
# ============================================================================

resource "random_password" "db_password" {
  length  = 32
  special = false
}

resource "aws_db_subnet_group" "trading" {
  name       = "${local.project_name}-db-subnet-group"
  subnet_ids = aws_subnet.data[*].id
  
  tags = merge(local.common_tags, {
    Name = "${local.project_name}-db-subnet-group"
  })
}

resource "aws_db_instance" "trading_db" {
  identifier = "${local.project_name}-db-${var.environment}"
  
  engine         = "postgres"
  engine_version = "14"
  instance_class = local.current_config.database_instance_class
  
  allocated_storage     = 100
  max_allocated_storage = 500
  storage_type         = "gp3"
  storage_encrypted    = true
  
  db_name  = "trading"
  username = "trading_admin"
  password = random_password.db_password.result
  
  port = 5432
  
  vpc_security_group_ids = [aws_security_group.database.id]
  db_subnet_group_name   = aws_db_subnet_group.trading.name
  
  multi_az               = local.current_config.multi_az
  availability_zone      = var.availability_zones[0]
  
  backup_retention_period = local.current_config.enable_backup ? 7 : 0
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  
  deletion_protection      = var.environment == "prod"
  skip_final_snapshot      = var.environment != "prod"
  final_snapshot_identifier = var.environment == "prod" ? "${local.project_name}-db-final-snapshot" : null
  
  performance_insights_enabled = true
  performance_insights_retention_period = 7
  
  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]
  
  parameter_group_name = aws_db_parameter_group.trading.name
  
  tags = merge(local.common_tags, {
    Name = "${local.project_name}-db-${var.environment}"
  })
}

resource "aws_db_parameter_group" "trading" {
  name   = "${local.project_name}-db-params"
  family = "postgres14"
  
  parameter {
    name  = "shared_preload_libraries"
    value = "timescaledb,pg_stat_statements"
  }
  
  parameter {
    name  = "timescaledb.telemetry_level"
    value = "off"
  }
  
  parameter {
    name  = "log_statement"
    value = "ddl"
  }
  
  parameter {
    name  = "log_min_duration_statement"
    value = "1000"  # Log queries taking >1s
  }
  
  tags = merge(local.common_tags, {
    Name = "${local.project_name}-db-params"
  })
}

# ============================================================================
# Redis (ElastiCache)
# ============================================================================

resource "aws_elasticache_subnet_group" "trading" {
  name       = "${local.project_name}-redis-subnet-group"
  subnet_ids = aws_subnet.data[*].id
  
  tags = merge(local.common_tags, {
    Name = "${local.project_name}-redis-subnet-group"
  })
}

resource "aws_elasticache_cluster" "trading_cache" {
  cluster_id           = "${local.project_name}-redis-${var.environment}"
  engine              = "redis"
  engine_version      = "7.0"
  node_type           = local.current_config.redis_node_type
  num_cache_nodes     = 1
  port                = 6379
  parameter_group_name = "default.redis7"
  
  subnet_group_name    = aws_elasticache_subnet_group.trading.name
  security_group_ids   = [aws_security_group.redis.id]
  
  snapshot_retention_limit = local.current_config.enable_backup ? 7 : 0
  snapshot_window         = "05:00-06:00"
  
  tags = merge(local.common_tags, {
    Name = "${local.project_name}-redis-${var.environment}"
  })
}

# ============================================================================
# ECR Repositories
# ============================================================================

resource "aws_ecr_repository" "services" {
  for_each = toset([
    "market-data",
    "strategy-engine",
    "execution-service",
    "risk-management",
    "api-gateway"
  ])
  
  name = "${local.project_name}/${each.key}"
  
  image_scanning_configuration {
    scan_on_push = true
  }
  
  encryption_configuration {
    encryption_type = "AES256"
  }
  
  tags = merge(local.common_tags, {
    Service = each.key
    Name    = "${local.project_name}-ecr-${each.key}"
  })
}

resource "aws_ecr_lifecycle_policy" "services" {
  for_each = aws_ecr_repository.services
  
  repository = each.value.name
  
  policy = jsonencode({
    rules = [{
      rulePriority = 1
      description  = "Keep last 30 images"
      selection = {
        tagStatus   = "any"
        countType   = "imageCountMoreThan"
        countNumber = 30
      }
      action = {
        type = "expire"
      }
    }]
  })
}

# ============================================================================
# ECS Cluster & Services
# ============================================================================

resource "aws_ecs_cluster" "trading" {
  name = "${local.project_name}-cluster-${var.environment}"
  
  setting {
    name  = "containerInsights"
    value = "enabled"
  }
  
  capacity_providers = var.enable_spot_instances ? [
    "FARGATE",
    "FARGATE_SPOT"
  ] : ["FARGATE"]
  
  default_capacity_provider_strategy {
    capacity_provider = var.enable_spot_instances ? "FARGATE_SPOT" : "FARGATE"
    weight           = 1
    base             = var.enable_spot_instances ? 0 : 1
  }
  
  tags = merge(local.common_tags, {
    Name = "${local.project_name}-cluster-${var.environment}"
  })
}

resource "aws_ecs_task_definition" "services" {
  for_each = {
    market_data = {
      cpu    = var.container_cpu.market_data
      memory = var.container_memory.market_data
    }
    strategy = {
      cpu    = var.container_cpu.strategy
      memory = var.container_memory.strategy
    }
    execution = {
      cpu    = var.container_cpu.execution
      memory = var.container_memory.execution
    }
    risk = {
      cpu    = var.container_cpu.risk
      memory = var.container_memory.risk
    }
    api = {
      cpu    = var.container_cpu.api
      memory = var.container_memory.api
    }
  }
  
  family                   = "${local.project_name}-${each.key}-${var.environment}"
  network_mode            = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                     = each.value.cpu
  memory                  = each.value.memory
  execution_role_arn      = aws_iam_role.ecs_execution.arn
  task_role_arn          = aws_iam_role.ecs_task.arn
  
  container_definitions = jsonencode([
    {
      name      = each.key
      image     = "${aws_ecr_repository.services[each.key].repository_url}:latest"
      cpu       = each.value.cpu
      memory    = each.value.memory
      essential = true
      
      portMappings = each.key == "api" ? [
        {
          containerPort = 8000
          hostPort      = 8000
          protocol      = "tcp"
        }
      ] : []
      
      environment = [
        {
          name  = "ENVIRONMENT"
          value = var.environment
        },
        {
          name  = "DB_HOST"
          value = aws_db_instance.trading_db.address
        },
        {
          name  = "DB_PORT"
          value = tostring(aws_db_instance.trading_db.port)
        },
        {
          name  = "DB_NAME"
          value = aws_db_instance.trading_db.db_name
        },
        {
          name  = "REDIS_HOST"
          value = aws_elasticache_cluster.trading_cache.cache_nodes[0].address
        },
        {
          name  = "REDIS_PORT"
          value = tostring(aws_elasticache_cluster.trading_cache.cache_nodes[0].port)
        }
      ]
      
      secrets = [
        {
          name      = "DB_PASSWORD"
          valueFrom = aws_secretsmanager_secret.db_password.arn
        }
      ]
      
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.ecs[each.key].name
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "ecs"
        }
      }
      
      healthCheck = {
        command     = ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 60
      }
    }
  ])
  
  tags = merge(local.common_tags, {
    Service = each.key
    Name    = "${local.project_name}-task-${each.key}"
  })
}

resource "aws_ecs_service" "services" {
  for_each = aws_ecs_task_definition.services
  
  name            = "${local.project_name}-${each.key}-service"
  cluster         = aws_ecs_cluster.trading.id
  task_definition = each.value.arn
  desired_count   = local.current_config.instance_count[each.key]
  launch_type     = "FARGATE"
  
  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.ecs_service.id]
    assign_public_ip = false
  }
  
  load_balancer {
    target_group_arn = each.key == "api" ? aws_lb_target_group.api.arn : null
    container_name   = each.key
    container_port   = each.key == "api" ? 8000 : null
  }
  
  # Enable deployment circuit breaker
  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }
  
  # Deployment configuration
  deployment_controller {
    type = "ECS"
  }
  
  # Auto scaling configuration
  dynamic "capacity_provider_strategy" {
    for_each = var.enable_spot_instances ? [1] : []
    
    content {
      capacity_provider = "FARGATE_SPOT"
      weight           = 100
      base             = 0
    }
  }
  
  dynamic "capacity_provider_strategy" {
    for_each = !var.enable_spot_instances ? [1] : []
    
    content {
      capacity_provider = "FARGATE"
      weight           = 100
      base             = 1
    }
  }
  
  tags = merge(local.common_tags, {
    Service = each.key
    Name    = "${local.project_name}-service-${each.key}"
  })
  
  depends_on = [
    aws_lb_listener.api,
    aws_db_instance.trading_db,
    aws_elasticache_cluster.trading_cache
  ]
}

# ============================================================================
# Auto Scaling
# ============================================================================

resource "aws_appautoscaling_target" "services" {
  for_each = aws_ecs_service.services
  
  max_capacity       = each.key == "market_data" ? 10 : 5
  min_capacity       = local.current_config.instance_count[each.key]
  resource_id        = "service/${aws_ecs_cluster.trading.name}/${each.value.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

# CPU-based scaling
resource "aws_appautoscaling_policy" "cpu_scaling" {
  for_each = aws_appautoscaling_target.services
  
  name               = "${each.key}-cpu-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = each.value.resource_id
  scalable_dimension = each.value.scalable_dimension
  service_namespace  = each.value.service_namespace
  
  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    
    target_value       = 70.0
    scale_in_cooldown  = 300
    scale_out_cooldown = 60
  }
}

# Trading hours scaling
resource "aws_appautoscaling_scheduled_action" "trading_hours" {
  for_each = var.trading_hours_scaling ? aws_appautoscaling_target.services : {}
  
  name               = "${each.key}-trading-hours-scaling"
  service_namespace  = each.value.service_namespace
  resource_id        = each.value.resource_id
  scalable_dimension = each.value.scalable_dimension
  
  # Scale up during trading hours
  scalable_target_action {
    min_capacity = local.current_config.instance_count[each.key]
    max_capacity = each.key == "market_data" ? 10 : 5
  }
  
  # Trading hours: Monday-Friday, 9:30 AM - 4:00 PM EST
  schedule = "cron(30 14 ? * MON-FRI *)"  # 14:30 UTC = 9:30 AM EST
  
  timezone = "UTC"
}

resource "aws_appautoscaling_scheduled_action" "non_trading_hours" {
  for_each = var.trading_hours_scaling ? aws_appautoscaling_target.services : {}
  
  name               = "${each.key}-non-trading-hours-scaling"
  service_namespace  = each.value.service_namespace
  resource_id        = each.value.resource_id
  scalable_dimension = each.value.scalable_dimension
  
  # Scale down outside trading hours
  scalable_target_action {
    min_capacity = max(1, local.current_config.instance_count[each.key] - 1)
    max_capacity = max(2, (each.key == "market_data" ? 10 : 5) - 2)
  }
  
  # Non-trading hours: All other times
  schedule = "cron(0 21 ? * MON-FRI *)"  # 21:00 UTC = 4:00 PM EST
  
  timezone = "UTC"
}

# ============================================================================
# Load Balancer
# ============================================================================

resource "aws_lb" "api" {
  name               = "${local.project_name}-api-lb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.load_balancer.id]
  subnets           = aws_subnet.public[*].id
  
  enable_deletion_protection = var.environment == "prod"
  
  tags = merge(local.common_tags, {
    Name = "${local.project_name}-api-lb"
  })
}

resource "aws_lb_target_group" "api" {
  name        = "${local.project_name}-api-tg"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = aws_vpc.trading_vpc.id
  target_type = "ip"
  
  health_check {
    enabled             = true
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 5
    interval            = 30
    path                = "/health"
    matcher             = "200"
  }
  
  tags = merge(local.common_tags, {
    Name = "${local.project_name}-api-tg"
  })
}

resource "aws_lb_listener" "api" {
  load_balancer_arn = aws_lb.api.arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy       = "ELBSecurityPolicy-2016-08"
  certificate_arn  = aws_acm_certificate.api.arn
  
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.api.arn
  }
  
  tags = merge(local.common_tags, {
    Name = "${local.project_name}-api-listener"
  })
}

# Redirect HTTP to HTTPS
resource "aws_lb_listener" "api_http" {
  load_balancer_arn = aws_lb.api.arn
  port              = "80"
  protocol          = "HTTP"
  
  default_action {
    type = "redirect"
    
    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
  
  tags = merge(local.common_tags, {
    Name = "${local.project_name}-api-http-listener"
  })
}

# ============================================================================
# SSL Certificate
# ============================================================================

resource "aws_acm_certificate" "api" {
  domain_name       = var.environment == "prod" ? "api.quantflow.trading" : "*.quantflow-trading.dev"
  validation_method = "DNS"
  
  tags = merge(local.common_tags, {
    Name = "${local.project_name}-api-cert"
  })
  
  lifecycle {
    create_before_destroy = true
  }
}

# ============================================================================
# IAM Roles & Policies
# ============================================================================

resource "aws_iam_role" "ecs_execution" {
  name = "${local.project_name}-ecs-execution-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
  
  tags = merge(local.common_tags, {
    Name = "${local.project_name}-ecs-execution-role"
  })
}

resource "aws_iam_role_policy_attachment" "ecs_execution" {
  role       = aws_iam_role.ecs_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role" "ecs_task" {
  name = "${local.project_name}-ecs-task-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
  
  tags = merge(local.common_tags, {
    Name = "${local.project_name}-ecs-task-role"
  })
}

resource "aws_iam_policy" "ecs_task" {
  name = "${local.project_name}-ecs-task-policy"
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "kms:Decrypt"
        ]
        Resource = [
          aws_secretsmanager_secret.db_password.arn,
          "arn:aws:kms:${var.aws_region}:*:key/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogStreams"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "cloudwatch:PutMetricData",
          "cloudwatch:GetMetricStatistics",
          "cloudwatch:ListMetrics"
        ]
        Resource = "*"
      }
    ]
  })
  
  tags = merge(local.common_tags, {
    Name = "${local.project_name}-ecs-task-policy"
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task" {
  role       = aws_iam_role.ecs_task.name
  policy_arn = aws_iam_policy.ecs_task.arn
}

# ============================================================================
# Secrets Management
# ============================================================================

resource "aws_secretsmanager_secret" "db_password" {
  name = "${local.project_name}/database/password"
  
  description = "Database password for trading system"
  
  tags = merge(local.common_tags, {
    Name = "${local.project_name}-db-password-secret"
  })
}

resource "aws_secretsmanager_secret_version" "db_password" {
  secret_id = aws_secretsmanager_secret.db_password.id
  secret_string = jsonencode({
    username = aws_db_instance.trading_db.username
    password = random_password.db_password.result
    engine   = "postgres"
    host     = aws_db_instance.trading_db.address
    port     = aws_db_instance.trading_db.port
    dbname   = aws_db_instance.trading_db.db_name
  })
}

# ============================================================================
# CloudWatch Logs
# ============================================================================

resource "aws_cloudwatch_log_group" "ecs" {
  for_each = toset([
    "market-data",
    "strategy-engine",
    "execution-service",
    "risk-management",
    "api-gateway"
  ])
  
  name              = "/ecs/${local.project_name}/${each.key}"
  retention_in_days = var.environment == "prod" ? 30 : 7
  
  tags = merge(local.common_tags, {
    Service = each.key
    Name    = "${local.project_name}-logs-${each.key}"
  })
}

# ============================================================================
# CloudWatch Alarms
# ============================================================================

resource "aws_cloudwatch_metric_alarm" "high_cpu" {
  for_each = aws_ecs_service.services
  
  alarm_name          = "${each.key}-high-cpu"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name        = "CPUUtilization"
  namespace          = "AWS/ECS"
  period             = "300"
  statistic          = "Average"
  threshold          = "80"
  alarm_description  = "CPU utilization is high for ${each.key} service"
  alarm_actions      = [aws_sns_topic.alerts.arn]
  
  dimensions = {
    ClusterName = aws_ecs_cluster.trading.name
    ServiceName = each.value.name
  }
  
  tags = merge(local.common_tags, {
    Service = each.key
    Name    = "${local.project_name}-alarm-cpu-${each.key}"
  })
}

resource "aws_cloudwatch_metric_alarm" "high_memory" {
  for_each = aws_ecs_service.services
  
  alarm_name          = "${each.key}-high-memory"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name        = "MemoryUtilization"
  namespace          = "AWS/ECS"
  period             = "300"
  statistic          = "Average"
  threshold          = "85"
  alarm_description  = "Memory utilization is high for ${each.key} service"
  alarm_actions      = [aws_sns_topic.alerts.arn]
  
  dimensions = {
    ClusterName = aws_ecs_cluster.trading.name
    ServiceName = each.value.name
  }
  
  tags = merge(local.common_tags, {
    Service = each.key
    Name    = "${local.project_name}-alarm-memory-${each.key}"
  })
}

# ============================================================================
# SNS Topics for Alerts
# ============================================================================

resource "aws_sns_topic" "alerts" {
  name = "${local.project_name}-alerts"
  
  tags = merge(local.common_tags, {
    Name = "${local.project_name}-alerts-topic"
  })
}

resource "aws_sns_topic_subscription" "email" {
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = "trading-alerts@quantflow.trading"
}

# ============================================================================
# Cost Management
# ============================================================================

resource "aws_budgets_budget" "monthly" {
  name              = "${local.project_name}-monthly-budget"
  budget_type       = "COST"
  limit_amount      = var.environment == "prod" ? "5000" : "1000"
  limit_unit        = "USD"
  time_unit         = "MONTHLY"
  time_period_start = "2024-01-01_00:00"
  
  cost_types {
    include_credit             = false
    include_discount           = true
    include_other_subscription = true
    include_recurring          = true
    include_refund             = false
    include_subscription       = true
    include_support            = true
    include_tax                = true
    include_upfront            = true
    use_amortized              = false
    use_blended                = false
  }
  
  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 80
    threshold_type             = "PERCENTAGE"
    notification_type          = "ACTUAL"
    subscriber_email_addresses = ["finops@quantflow.trading"]
  }
  
  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 100
    threshold_type             = "PERCENTAGE"
    notification_type          = "ACTUAL"
    subscriber_email_addresses = ["finops@quantflow.trading"]
  }
  
  tags = merge(local.common_tags, {
    Name = "${local.project_name}-monthly-budget"
  })
}

# ============================================================================
# Outputs
# ============================================================================

output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.trading_vpc.id
}

output "load_balancer_dns" {
  description = "Load Balancer DNS name"
  value       = aws_lb.api.dns_name
}

output "database_endpoint" {
  description = "Database endpoint"
  value       = aws_db_instance.trading_db.address
  sensitive   = true
}

output "redis_endpoint" {
  description = "Redis endpoint"
  value       = aws_elasticache_cluster.trading_cache.cache_nodes[0].address
}

output "ecr_repositories" {
  description = "ECR repository URLs"
  value = {
    for service, repo in aws_ecr_repository.services :
    service => repo.repository_url
  }
}

output "ecs_cluster_name" {
  description = "ECS cluster name"
  value       = aws_ecs_cluster.trading.name
}

output "services" {
  description = "ECS service names"
  value = {
    for service, svc in aws_ecs_service.services :
    service => svc.name
  }
}

output "secrets_arn" {
  description = "Secrets Manager ARN for database password"
  value       = aws_secretsmanager_secret.db_password.arn
  sensitive   = true
}

output "cloudwatch_log_groups" {
  description = "CloudWatch log groups"
  value = {
    for service, lg in aws_cloudwatch_log_group.ecs :
    service => lg.name
  }
}

output "sns_topic_arn" {
  description = "SNS topic ARN for alerts"
  value       = aws_sns_topic.alerts.arn
}