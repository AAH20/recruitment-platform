# Deployment Guide

This guide covers deploying the Recruitment Platform using Docker, Kubernetes, and Terraform.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Docker Deployment](#docker-deployment)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Terraform Deployment](#terraform-deployment)
- [Environment Configuration](#environment-configuration)
- [Monitoring & Logging](#monitoring--logging)
- [Backup & Disaster Recovery](#backup--disaster-recovery)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

- Docker 24+ and Docker Compose 2+
- Kubernetes cluster (EKS/GKE/AKS) with kubectl 1.28+
- Terraform 1.6+
- Helm 3.13+
- AWS CLI / gcloud / az (depending on target cloud)

---

## Docker Deployment

### Quick Start with Docker Compose

```bash
# Clone the repository
git clone https://github.com/your-org/recruitment-platform.git
cd recruitment-platform

# Copy environment configuration
cp .env.example .env

# Edit .env with your configuration
nano .env

# Start all services
docker-compose up -d

# Verify services are running
docker-compose ps

# View logs
docker-compose logs -f app
```

### Docker Compose Configuration

```yaml
# docker-compose.yml
version: "3.9"

services:
  app:
    build:
      context: .
      dockerfile: docker/Dockerfile
      target: production
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - DATABASE_URL=postgresql://postgres:postgres@postgres:5432/recruitment
      - REDIS_URL=redis://redis:6379
      - JWT_SECRET=${JWT_SECRET}
      - S3_BUCKET=${S3_BUCKET}
      - S3_REGION=${S3_REGION}
      - ELASTICSEARCH_URL=http://elasticsearch:9200
      - KAFKA_BROKERS=kafka:9092
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      elasticsearch:
        condition: service_healthy
      kafka:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped
    networks:
      - app-network

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: recruitment
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - app-network

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - app-network

  elasticsearch:
    image: elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    ports:
      - "9200:9200"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:9200/_cluster/health || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 5
    networks:
      - app-network

  kafka:
    image: confluentinc/cp-kafka:7.5.0
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
    healthcheck:
      test: ["CMD", "kafka-broker-api-versions", "--bootstrap-server", "localhost:9092"]
      interval: 30s
      timeout: 10s
      retries: 5
    networks:
      - app-network

  zookeeper:
    image: confluentinc/cp-zookeeper:7.5.0
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000
    networks:
      - app-network

  nginx:
    image: nginx:1.25-alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./docker/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./docker/ssl:/etc/nginx/ssl:ro
    depends_on:
      - app
    networks:
      - app-network

volumes:
  postgres_data:
  redis_data:
  elasticsearch_data:

networks:
  app-network:
    driver: bridge
```

### Production Docker Build

```dockerfile
# docker/Dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production && npm cache clean --force

COPY . .
RUN npm run build

# Production stage
FROM node:18-alpine AS production

RUN addgroup -g 1001 -S nodejs && adduser -S recruitment -u 1001

WORKDIR /app

COPY --from=builder --chown=recruitment:nodejs /app/dist ./dist
COPY --from=builder --chown=recruitment:nodejs /app/node_modules ./node_modules
COPY --from=builder --chown=recruitment:nodejs /app/package.json ./

USER recruitment

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3000/health || exit 1

CMD ["node", "dist/main.js"]
```

### Scaling with Docker Compose

```bash
# Scale the app service to 3 instances
docker-compose up -d --scale app=3

# Use with a load balancer (nginx or traefik)
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

---

## Kubernetes Deployment

### Architecture

```mermaid
graph TB
    subgraph "Kubernetes Cluster"
        subgraph "Ingress"
            IN[Ingress Controller - Nginx/Traefik]
        end

        subgraph "App Namespace"
            DEP[Deployment - App Service]
            HPA[HPA - Horizontal Pod Autoscaler]
            SVC[Service - ClusterIP]
        end

        subgraph "Data Namespace"
            PG[(PostgreSQL - StatefulSet)]
            RD[(Redis - Deployment)]
            ES[(Elasticsearch - StatefulSet)]
            KF[(Kafka - Strimzi)]
        end

        subgraph "Monitoring"
            PM[Prometheus]
            GF[Grafana]
            ELK[ELK Stack]
        end
    end

    IN --> SVC
    SVC --> DEP
    HPA --> DEP
    DEP --> PG
    DEP --> RD
    DEP --> ES
    DEP --> KF
```

### Namespace Setup

```bash
# Create namespaces
kubectl create namespace recruitment
kubectl create namespace recruitment-data
kubectl create namespace monitoring

# Set context
kubectl config set-context --current --namespace=recruitment
```

### ConfigMap

```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: recruitment-config
  namespace: recruitment
data:
  NODE_ENV: "production"
  PORT: "3000"
  DATABASE_URL: "postgresql://postgres:postgres@postgres.recruitment-data.svc.cluster.local:5432/recruitment"
  REDIS_URL: "redis://redis.recruitment-data.svc.cluster.local:6379"
  ELASTICSEARCH_URL: "http://elasticsearch.recruitment-data.svc.cluster.local:9200"
  KAFKA_BROKERS: "kafka:9092"
  S3_BUCKET: "recruitment-platform-uploads"
  S3_REGION: "us-east-1"
  LOG_LEVEL: "info"
```

### Secret

```yaml
# k8s/secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: recruitment-secrets
  namespace: recruitment
type: Opaque
stringData:
  JWT_SECRET: "<generate-with-openssl-rand-base64-32>"
  S3_ACCESS_KEY: "<aws-access-key>"
  S3_SECRET_KEY: "<aws-secret-key>"
  SENDGRID_API_KEY: "<sendgrid-api-key>"
  TWILIO_ACCOUNT_SID: "<twilio-sid>"
  TWILIO_AUTH_TOKEN: "<twilio-token>"
```

### Deployment

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: recruitment-app
  namespace: recruitment
  labels:
    app: recruitment
    tier: api
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: recruitment
      tier: api
  template:
    metadata:
      labels:
        app: recruitment
        tier: api
    spec:
      containers:
        - name: app
          image: your-registry/recruitment-platform:latest
          imagePullPolicy: Always
          ports:
            - containerPort: 3000
              protocol: TCP
          envFrom:
            - configMapRef:
                name: recruitment-config
            - secretRef:
                name: recruitment-secrets
          resources:
            requests:
              cpu: 250m
              memory: 512Mi
            limits:
              cpu: 1000m
              memory: 1Gi
          livenessProbe:
            httpGet:
              path: /health
              port: 3000
            initialDelaySeconds: 30
            periodSeconds: 10
            timeoutSeconds: 5
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: /health/ready
              port: 3000
            initialDelaySeconds: 10
            periodSeconds: 5
            timeoutSeconds: 3
            failureThreshold: 3
          volumeMounts:
            - name: tmp
              mountPath: /tmp
      volumes:
        - name: tmp
          emptyDir: {}
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
            - weight: 100
              podAffinityTerm:
                labelSelector:
                  matchExpressions:
                    - key: app
                      operator: In
                      values:
                        - recruitment
                topologyKey: kubernetes.io/hostname
```

### Service

```yaml
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: recruitment-service
  namespace: recruitment
  labels:
    app: recruitment
spec:
  type: ClusterIP
  ports:
    - port: 80
      targetPort: 3000
      protocol: TCP
      name: http
  selector:
    app: recruitment
    tier: api
```

### Horizontal Pod Autoscaler

```yaml
# k8s/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: recruitment-hpa
  namespace: recruitment
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: recruitment-app
  minReplicas: 3
  maxReplicas: 20
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
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
        - type: Percent
          value: 100
          periodSeconds: 15
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
        - type: Percent
          value: 10
          periodSeconds: 60
```

### Ingress

```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: recruitment-ingress
  namespace: recruitment
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/rate-limit-window: "1m"
    nginx.ingress.kubernetes.io/proxy-body-size: "50m"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "300"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "300"
spec:
  tls:
    - hosts:
        - api.recruitment-platform.example.com
      secretName: recruitment-tls
  rules:
    - host: api.recruitment-platform.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: recruitment-service
                port:
                  number: 80
```

### PostgreSQL StatefulSet

```yaml
# k8s/postgres.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: recruitment-data
spec:
  serviceName: postgres
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
        - name: postgres
          image: postgres:15-alpine
          ports:
            - containerPort: 5432
          env:
            - name: POSTGRES_DB
              value: recruitment
            - name: POSTGRES_USER
              value: postgres
            - name: POSTGRES_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: postgres-secret
                  key: password
            - name: PGDATA
              value: /var/lib/postgresql/data/pgdata
          volumeMounts:
            - name: postgres-storage
              mountPath: /var/lib/postgresql/data
          resources:
            requests:
              cpu: 250m
              memory: 512Mi
            limits:
              cpu: 1000m
              memory: 2Gi
  volumeClaimTemplates:
    - metadata:
        name: postgres-storage
      spec:
        accessModes: ["ReadWriteOnce"]
        storageClassName: gp3
        resources:
          requests:
            storage: 50Gi
---
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: recruitment-data
spec:
  ports:
    - port: 5432
  selector:
    app: postgres
```

### Deploy to Kubernetes

```bash
# Apply all manifests
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/hpa.yaml
kubectl apply -f k8s/ingress.yaml

# Verify deployment
kubectl get pods -n recruitment
kubectl get svc -n recruitment
kubectl get ingress -n recruitment

# Check logs
kubectl logs -f deployment/recruitment-app -n recruitment

# Port forward for local testing
kubectl port-forward svc/recruitment-service 8080:80 -n recruitment
```

### Helm Chart (Alternative)

```bash
# Add repository
helm repo add recruitment https://charts.recruitment-platform.example.com
helm repo update

# Install with custom values
helm install recruitment recruitment/recruitment-platform \
  --namespace recruitment \
  --create-namespace \
  -f values-production.yaml

# Upgrade
helm upgrade recruitment recruitment/recruitment-platform \
  -f values-production.yaml

# Uninstall
helm uninstall recruitment -n recruitment
```

---

## Terraform Deployment

### AWS Infrastructure

```hcl
# terraform/main.tf
terraform {
  required_version = ">= 1.6"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.23"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.11"
    }
  }

  backend "s3" {
    bucket         = "recruitment-platform-terraform-state"
    key            = "production/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-locks"
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "recruitment-platform"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}

# VPC and Networking
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "${var.project_name}-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["${var.aws_region}a", "${var.aws_region}b", "${var.aws_region}c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  enable_nat_gateway     = true
  single_nat_gateway     = var.environment != "production"
  enable_dns_hostnames   = true
  enable_dns_support     = true

  public_subnet_tags = {
    "kubernetes.io/role/elb" = "1"
  }

  private_subnet_tags = {
    "kubernetes.io/role/internal-elb" = "1"
  }
}

# EKS Cluster
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 19.0"

  cluster_name    = "${var.project_name}-${var.environment}"
  cluster_version = "1.28"

  vpc_id                         = module.vpc.vpc_id
  subnet_ids                     = module.vpc.private_subnets
  control_plane_subnet_ids       = module.vpc.private_subnets

  cluster_endpoint_private_access = true
  cluster_endpoint_public_access  = true

  cluster_addons = {
    coredns = {
      most_recent = true
    }
    kube-proxy = {
      most_recent = true
    }
    vpc-cni = {
      most_recent = true
    }
    aws-ebs-csi-driver = {
      most_recent = true
    }
  }

  eks_managed_node_groups = {
    general = {
      desired_size = 3
      min_size     = 2
      max_size     = 10

      instance_types = ["m6i.xlarge"]
      capacity_type  = "ON_DEMAND"

      labels = {
        workload = "general"
      }

      taints = []

      update_config = {
        max_unavailable_percentage = 25
      }
    }

    spot = {
      desired_size = 2
      min_size     = 0
      max_size     = 20

      instance_types = ["m6i.large", "m5.large", "m5a.large"]
      capacity_type  = "SPOT"

      labels = {
        workload = "spot"
      }

      taints = [{
        key    = "spot"
        value  = "true"
        effect = "NO_SCHEDULE"
      }]
    }
  }
}

# RDS PostgreSQL
module "rds" {
  source  = "terraform-aws-modules/rds/aws"
  version = "~> 6.0"

  identifier = "${var.project_name}-${var.environment}"

  engine               = "postgres"
  engine_version       = "15.4"
  family               = "postgres15"
  major_engine_version = "15"
  instance_class       = var.environment == "production" ? "db.r6g.xlarge" : "db.t3.medium"

  allocated_storage     = 100
  max_allocated_storage = 500

  db_name  = "recruitment"
  username = "postgres"
  port     = 5432

  multi_az               = var.environment == "production"
  db_subnet_group_name   = module.vpc.database_subnet_group
  vpc_security_group_ids = [aws_security_group.rds.id]

  maintenance_window      = "Mon:00:00-Mon:03:00"
  backup_window           = "03:00-06:00"
  backup_retention_period = var.environment == "production" ? 30 : 7

  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]

  deletion_protection = var.environment == "production"

  performance_insights_enabled = true
}

# ElastiCache Redis
module "elasticache" {
  source  = "terraform-aws-modules/elasticache/aws"
  version = "~> 1.0"

  cluster_id               = "${var.project_name}-${var.environment}"
  description              = "Redis cluster for recruitment platform"
  node_type                = var.environment == "production" ? "cache.r6g.large" : "cache.t3.micro"
  num_cache_nodes          = var.environment == "production" ? 2 : 1
  engine_version           = "7.0"
  port                     = 6379
  parameter_group_name     = "default.redis7"
  subnet_group_name        = aws_elasticache_subnet_group.redis.name
  security_group_ids       = [aws_security_group.redis.id]

  automatic_failover_enabled = var.environment == "production"
  multi_az_enabled           = var.environment == "production"
}

# S3 Bucket
resource "aws_s3_bucket" "uploads" {
  bucket = "${var.project_name}-uploads-${var.environment}-${data.aws_caller_identity.current.account_id}"
}

resource "aws_s3_bucket_versioning" "uploads" {
  bucket = aws_s3_bucket.uploads.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "uploads" {
  bucket = aws_s3_bucket.uploads.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "uploads" {
  bucket = aws_s3_bucket.uploads.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Application Load Balancer
module "alb" {
  source  = "terraform-aws-modules/alb/aws"
  version = "~> 9.0"

  name = "${var.project_name}-${var.environment}"

  load_balancer_type = "application"

  vpc_id  = module.vpc.vpc_id
  subnets = module.vpc.public_subnets

  security_groups = [aws_security_group.alb.id]

  listeners = {
    https = {
      port            = 443
      protocol        = "HTTPS"
      certificate_arn = aws_acm_certificate.main.arn

      fixed_response = {
        content_type = "text/plain"
        message_body = "OK"
        status_code  = "200"
      }
    }
  }
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "app" {
  name              = "/aws/eks/${var.project_name}-${var.environment}/application"
  retention_in_days = var.environment == "production" ? 90 : 30
}

# Outputs
output "cluster_endpoint" {
  value = module.eks.cluster_endpoint
}

output "rds_endpoint" {
  value = module.rds.db_instance_endpoint
}

output "redis_endpoint" {
  value = module.elasticache.cluster_address
}

output "s3_bucket" {
  value = aws_s3_bucket.uploads.id
}
```

### Terraform Variables

```hcl
# terraform/variables.tf
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"

  validation {
    condition     = contains(["development", "staging", "production"], var.environment)
    error_message = "Environment must be development, staging, or production."
  }
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "recruitment-platform"
}
```

### Terraform Deployment Commands

```bash
# Initialize Terraform
cd terraform/
terraform init

# Validate configuration
terraform validate

# Plan deployment
terraform plan -var-file="environments/production.tfvars" -out=tfplan

# Apply deployment
terraform apply tfplan

# Destroy (use with caution!)
terraform destroy -var-file="environments/production.tfvars"
```

### Terraform Production Variables

```hcl
# terraform/environments/production.tfvars
aws_region  = "us-east-1"
environment = "production"
project_name = "recruitment-platform"
```

---

## Environment Configuration

### Production Environment Variables

```env
# Application
NODE_ENV=production
PORT=3000
LOG_LEVEL=info

# Database
DATABASE_URL=postgresql://user:password@rds-endpoint:5432/recruitment
DATABASE_POOL_SIZE=20
DATABASE_SSL=true

# Redis
REDIS_URL=redis://elasticache-endpoint:6379
REDIS_TLS=true

# Elasticsearch
ELASTICSEARCH_URL=http://es-endpoint:9200

# Kafka
KAFKA_BROKERS=kafka-1:9092,kafka-2:9092,kafka-3:9092

# Storage
S3_BUCKET=recruitment-platform-uploads-production
S3_REGION=us-east-1

# Auth
JWT_SECRET=<strong-random-secret>
JWT_EXPIRATION=24h
BCRYPT_ROUNDS=12

# Email
SENDGRID_API_KEY=<sendgrid-api-key>
EMAIL_FROM=noreply@recruitment-platform.example.com

# SMS
TWILIO_ACCOUNT_SID=<twilio-sid>
TWILIO_AUTH_TOKEN=<twilio-token>
TWILIO_FROM_NUMBER=+15551234567

# Feature Flags
ENABLE_RESUME_PARSING=true
ENABLE_AI_MATCHING=true
ENABLE_ANALYTICS=true
ENABLE_WEBHOOKS=true
```

---

## Monitoring & Logging

### Prometheus ServiceMonitor

```yaml
# k8s/servicemonitor.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: recruitment-metrics
  namespace: monitoring
  labels:
    release: prometheus
spec:
  selector:
    matchLabels:
      app: recruitment
  namespaceSelector:
    matchNames:
      - recruitment
  endpoints:
    - port: http
      path: /metrics
      interval: 30s
      scrapeTimeout: 10s
```

### Grafana Dashboard

Import the provided dashboard JSON:

```bash
# Port forward Grafana
kubectl port-forward svc/grafana 3001:3000 -n monitoring

# Access at http://localhost:3001
# Default credentials: admin / admin
```

### Key Metrics

| Metric | Description | Alert Threshold |
|--------|-------------|-----------------|
| `http_requests_total` | Total HTTP requests | — |
| `http_request_duration_seconds` | Request latency | p99 > 2s |
| `http_errors_total` | Total error responses | rate > 5% |
| `db_connections_active` | Active DB connections | > 80% of pool |
| `queue_depth` | Kafka consumer lag | > 1000 |
| `memory_usage` | Pod memory usage | > 85% |

### Log Aggregation

```yaml
# Fluentd configuration for ELK
<match recruitment.**>
  @type elasticsearch
  host elasticsearch
  port 9200
  logstash_format true
  logstash_prefix recruitment
  include_tag_key true
  type_name _doc
  flush_interval 10s
</match>
```

---

## Backup & Disaster Recovery

### Database Backups

```bash
# Automated RDS snapshots (configured in Terraform)
# Manual snapshot
aws rds create-db-snapshot \
  --db-instance-identifier recruitment-production \
  --db-snapshot-identifier recruitment-manual-$(date +%Y%m%d)

# Point-in-time recovery
aws rds restore-db-instance-to-point-in-time \
  --source-db-instance-identifier recruitment-production \
  --target-db-instance-identifier recruitment-recovery \
  --restore-time 2024-01-15T00:00:00Z
```

### S3 Backup Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "EnableVersioning",
      "Effect": "Allow",
      "Principal": {"AWS": "arn:aws:iam::ACCOUNT_ID:role/backup-role"},
      "Action": ["s3:GetObject", "s3:PutObject"],
      "Resource": "arn:aws:s3:::recruitment-platform-uploads-production/*"
    }
  ]
}
```

### Disaster Recovery Runbook

1. **RTO**: 4 hours | **RPO**: 1 hour
2. Restore RDS from latest snapshot
3. Redeploy application via Terraform
4. Verify data integrity
5. Update DNS/ingress if needed

---

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Pods stuck in `Pending` | Insufficient resources | Check node capacity, scale cluster |
| `CrashLoopBackOff` | App startup failure | Check logs: `kubectl logs <pod>` |
| Database connection errors | Network/security group | Verify VPC peering and security groups |
| High memory usage | Memory leak or insufficient limits | Increase limits, profile application |
| Kafka consumer lag | Slow consumers | Scale consumer pods, optimize processing |

### Useful Commands

```bash
# Check pod status
kubectl get pods -n recruitment -o wide

# Describe pod for events
kubectl describe pod <pod-name> -n recruitment

# View logs
kubectl logs -f <pod-name> -n recruitment
kubectl logs -f <pod-name> -n recruitment --previous

# Execute into pod
kubectl exec -it <pod-name> -n recruitment -- /bin/sh

# Check resource usage
kubectl top pods -n recruitment
kubectl top nodes

# Port forward for debugging
kubectl port-forward svc/recruitment-service 8080:80 -n recruitment

# Check HPA status
kubectl get hpa -n recruitment

# Rollback deployment
kubectl rollout undo deployment/recruitment-app -n recruitment

# View rollout history
kubectl rollout history deployment/recruitment-app -n recruitment
```
