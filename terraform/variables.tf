variable "aws_region" {
  description = "AWS region for all resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (development, staging, production)"
  type        = string
  default     = "development"

  validation {
    condition     = contains(["development", "staging", "production"], var.environment)
    error_message = "Environment must be one of: development, staging, production."
  }
}

variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
  default     = "recruitment-platform"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "List of availability zones to use"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b", "us-east-1c"]
}

variable "enable_nat_gateway" {
  description = "Whether to create a NAT Gateway (disable for cost savings in dev)"
  type        = bool
  default     = true
}

variable "app_port" {
  description = "Port the application listens on"
  type        = number
  default     = 3000
}

variable "acm_certificate_arn" {
  description = "ARN of the ACM certificate for HTTPS (empty for CloudFront default)"
  type        = string
  default     = ""
}

# ECS Variables
variable "task_cpu" {
  description = "CPU units for the ECS task (256 = 0.25 vCPU)"
  type        = number
  default     = 512

  validation {
    condition     = contains([256, 512, 1024, 2048, 4096], var.task_cpu)
    error_message = "Task CPU must be one of: 256, 512, 1024, 2048, 4096."
  }
}

variable "task_memory" {
  description = "Memory for the ECS task in MiB"
  type        = number
  default     = 1024

  validation {
    condition     = contains([512, 1024, 2048, 4096, 8192, 16384], var.task_memory)
    error_message = "Task memory must be one of: 512, 1024, 2048, 4096, 8192, 16384."
  }
}

variable "desired_count" {
  description = "Desired number of ECS tasks"
  type        = number
  default     = 2
}

variable "min_count" {
  description = "Minimum number of ECS tasks for auto scaling"
  type        = number
  default     = 1
}

variable "max_count" {
  description = "Maximum number of ECS tasks for auto scaling"
  type        = number
  default     = 10
}

variable "fargate_spot_weight" {
  description = "Weight for Fargate Spot capacity provider (0-100)"
  type        = number
  default     = 50

  validation {
    condition     = var.fargate_spot_weight >= 0 && var.fargate_spot_weight <= 100
    error_message = "Fargate Spot weight must be between 0 and 100."
  }
}

variable "log_retention_days" {
  description = "Number of days to retain CloudWatch logs"
  type        = number
  default     = 30
}

# RDS Variables
variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "db_allocated_storage" {
  description = "Allocated storage for RDS in GB"
  type        = number
  default     = 20
}

variable "db_max_allocated_storage" {
  description = "Maximum storage for RDS autoscaling in GB"
  type        = number
  default     = 100
}

variable "db_name" {
  description = "Name of the database"
  type        = string
  default     = "recruitment_platform"
}

variable "db_username" {
  description = "Master username for the database"
  type        = string
  default     = "recruitment_admin"
}

variable "db_password" {
  description = "Master password for the database"
  type        = string
  sensitive   = true

  validation {
    condition     = length(var.db_password) >= 12
    error_message = "Database password must be at least 12 characters long."
  }
}

variable "db_backup_retention" {
  description = "Number of days to retain database backups"
  type        = number
  default     = 7
}

# ElastiCache Variables
variable "redis_node_type" {
  description = "ElastiCache node type"
  type        = string
  default     = "cache.t3.micro"
}

# CloudFront Variables
variable "cloudfront_price_class" {
  description = "CloudFront price class (PriceClass_100, PriceClass_200, PriceClass_All)"
  type        = string
  default     = "PriceClass_100"

  validation {
    condition     = contains(["PriceClass_100", "PriceClass_200", "PriceClass_All"], var.cloudfront_price_class)
    error_message = "CloudFront price class must be one of: PriceClass_100, PriceClass_200, PriceClass_All."
  }
}
