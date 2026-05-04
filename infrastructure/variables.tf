variable "region" {
  type    = string
  default = "us-east-1"
}

variable "environment" {
  type    = string
  default = "dev"
}

variable "ecr_repository" {
  type    = string
  default = "incident-analyzer"
}

variable "ecs_cluster_name" {
  type    = string
  default = "incident-analyzer-cluster"
}

variable "ecs_task_family" {
  type    = string
  default = "incident-analyzer-task"
}

variable "ecs_service_name" {
  type    = string
  default = "incident-analyzer-service"
}

variable "task_cpu" {
  type    = number
  default = 512
}

variable "task_memory" {
  type    = number
  default = 1024
}

variable "desired_count" {
  type    = number
  default = 1
}

variable "dynatrace_base_url" {
  type = string
}

variable "anthropic_api_key" {
  type      = string
  sensitive = true
}

variable "servicenow_instance" {
  type = string
}

variable "servicenow_username" {
  type      = string
  sensitive = true
}

variable "servicenow_password" {
  type      = string
  sensitive = true
}

variable "slack_webhook_url" {
  type      = string
  sensitive = true
}

variable "claude_model" {
  type    = string
  default = "claude-3-sonnet-20240229"
}

variable "confidence_threshold" {
  type    = number
  default = 0.8
}

variable "default_hours_back" {
  type    = number
  default = 24
}

variable "servicenow_assignment_group" {
  type    = string
  default = "IT Operations"
}

variable "servicenow_category" {
  type    = string
  default = "Software"
}

variable "servicenow_subcategory" {
  type    = string
  default = "Application"
}
