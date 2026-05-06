# LLM-Powered-Incident-Analyzer---Dynatrace

Standalone AWS package for the LLM-Powered Incident Analyzer.

## Supported AWS regions
- Primary: `us-east-1` (US East)
- Alternate: `us-west-2` (US West)

## What is included
- Full Python incident analyzer code
- AWS architecture reference (`aws_architecture.md`)
- AWS Terraform deployment templates (`infrastructure/*.tf`)
- Dockerfile and local container support
- GitHub Actions CI/CD workflow (`.github/workflows/aws-terraform-docker-cicd.yml`)
- Deployment guide (`DEPLOYMENT.md`)
- AWS deploy helper script (`deploy.sh`)

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Copy environment file:
   ```bash
   cp .env.example .env
   ```
3. Update `.env` with secrets and endpoints.

## Run locally
```bash
python main.py
```

## AWS Deployment
The package deploys via Terraform to AWS ECS Fargate with Docker containers.

- Use `infrastructure/terraform.tfvars.example` as a starting point.
- The package defaults to `us-east-1`. To deploy to `us-west-2`, set `AWS_REGION=us-west-2` or update your Terraform vars.
- GitHub Actions builds the Docker image, pushes it to ECR, and forces a new ECS deployment.

See `DEPLOYMENT.md` for full AWS deployment steps.
