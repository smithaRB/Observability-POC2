#!/bin/bash
set -e

if [ -f ".env" ]; then
  export $(grep -v '^#' .env | xargs)
fi

if ! command -v aws >/dev/null 2>&1; then
  echo "AWS CLI is required. Install: pip install awscli"
  exit 1
fi

if ! command -v terraform >/dev/null 2>&1; then
  echo "Terraform is required. Install from https://www.terraform.io/downloads"
  exit 1
fi

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is required. Install from https://www.docker.com/get-started"
  exit 1
fi

echo "Deploying AWS Incident Analyzer..."

cd infrastructure
terraform init
terraform apply -auto-approve \
  -var "region=${AWS_REGION:-us-east-1}" \
  -var "environment=${ENVIRONMENT:-dev}" \
  -var "ecr_repository=${ECR_REPOSITORY:-incident-analyzer}" \
  -var "ecs_cluster_name=${ECS_CLUSTER_NAME:-incident-analyzer-cluster}" \
  -var "ecs_service_name=${ECS_SERVICE_NAME:-incident-analyzer-service}" \
  -var "dynatrace_base_url=${DYNATRACE_BASE_URL}" \
  -var "anthropic_api_key=${ANTHROPIC_API_KEY}" \
  -var "servicenow_instance=${SERVICENOW_INSTANCE}" \
  -var "servicenow_username=${SERVICENOW_USERNAME}" \
  -var "servicenow_password=${SERVICENOW_PASSWORD}" \
  -var "slack_webhook_url=${SLACK_WEBHOOK_URL}" \
  -var "claude_model=${CLAUDE_MODEL}" \
  -var "confidence_threshold=${CONFIDENCE_THRESHOLD}" \
  -var "default_hours_back=${DEFAULT_HOURS_BACK}"

ECR_URL=$(terraform output -raw ecr_repository_url)
cd ..

echo "Building Docker image..."
docker build -t ${ECR_URL}:latest .

echo "Logging in to ECR..."
aws ecr get-login-password --region ${AWS_REGION:-us-east-1} | docker login --username AWS --password-stdin ${ECR_URL}

echo "Pushing Docker image to ECR..."
docker push ${ECR_URL}:latest

echo "Forcing ECS service redeployment..."
aws ecs update-service \
  --cluster ${ECS_CLUSTER_NAME:-incident-analyzer-cluster} \
  --service ${ECS_SERVICE_NAME:-incident-analyzer-service} \
  --force-new-deployment

echo "AWS deployment complete."
