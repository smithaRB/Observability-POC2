# AWS Deployment Guide

This guide explains how to deploy the Incident Analyzer using Terraform, Docker, and GitHub Actions.

## Prerequisites
- Python 3.11+
- AWS CLI configured
- Terraform CLI installed
- Docker installed
- An AWS account with permissions for ECR, ECS, IAM, and ELB

## Local Deployment
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` and fill values.
3. Run locally:
   ```bash
   python main.py
   ```

## Docker Local Deployment
1. Build the image:
   ```bash
   docker build -t incident-analyzer:latest .
   ```
2. Run locally:
   ```bash
   docker run --rm --env-file .env incident-analyzer:latest
   ```
3. Or run with Docker Compose:
   ```bash
   docker compose up
   ```

## AWS Deployment with Terraform
1. Ensure AWS CLI is configured:
   ```bash
   aws configure
   ```
2. Initialize Terraform:
   ```bash
   cd infrastructure
   terraform init
   ```
3. Apply Terraform:
   ```bash
   terraform apply -auto-approve \
     -var="region=us-east-1" \
     -var="environment=dev" \
     -var="ecr_repository=incident-analyzer" \
     -var="ecs_cluster_name=incident-analyzer-cluster" \
     -var="ecs_service_name=incident-analyzer-service" \
     -var="dynatrace_base_url=${DYNATRACE_BASE_URL}" \
     -var="anthropic_api_key=${ANTHROPIC_API_KEY}" \
     -var="servicenow_instance=${SERVICENOW_INSTANCE}" \
     -var="servicenow_username=${SERVICENOW_USERNAME}" \
     -var="servicenow_password=${SERVICENOW_PASSWORD}" \
     -var="slack_webhook_url=${SLACK_WEBHOOK_URL}"
   ```
4. When Terraform finishes, note the Application Load Balancer DNS in the outputs.

## GitHub CI/CD Deployment
This repository includes a GitHub Actions workflow at `.github/workflows/aws-terraform-docker-cicd.yml`.

This deployment is designed to run from the `main` branch of the GitHub repo:
`https://github.com/sharmasaket10/AWS_LLM-Powered-Incident-Analyzer---Dynatrace`.

### Required GitHub secrets
- `AWS_ROLE_TO_ASSUME`
- `ENVIRONMENT`
- `ECR_REPOSITORY`
- `ECS_CLUSTER_NAME`
- `ECS_SERVICE_NAME`
- `DYNATRACE_BASE_URL`
- `ANTHROPIC_API_KEY`
- `SERVICENOW_INSTANCE`
- `SERVICENOW_USERNAME`
- `SERVICENOW_PASSWORD`
- `SLACK_WEBHOOK_URL`
- `CLAUDE_MODEL`
- `CONFIDENCE_THRESHOLD`
- `DEFAULT_HOURS_BACK`

### Workflow behavior
- Terraform provisions AWS infrastructure
- Docker image is built and pushed to ECR
- ECS service is forced to redeploy the latest container image

## Infrastructure
The AWS Terraform deployment templates are located in `infrastructure/`.

## Next Steps
- Verify the Application Load Balancer DNS output
- Confirm the ECS service is running successfully
- Monitor CloudWatch logs for the service
