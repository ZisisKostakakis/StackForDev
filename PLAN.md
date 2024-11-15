# Backend Infrastructure

## Core Components
- Language: Python 3.11 with Pydantic for data validation
- Runtime: AWS Lambda using Docker container
- Container Registry: AWS ECR
- API Layer: AWS API Gateway
- Storage: AWS S3 for Dockerfile storage
- Infrastructure: Terraform Cloud with GitHub integration

## Architecture Details
1. Infrastructure Management
   - Terraform Cloud organization: StackForDev
   - Automated deployments through GitHub integration
   - State management handled by Terraform Cloud

2. AWS Resources
   - ECR Repository for Docker images
   - Lambda function with Docker runtime
   - API Gateway with throttling and usage plans
   - S3 bucket for Dockerfile storage
   - IAM roles and policies for secure access

3. API Configuration
   - Regional endpoint deployment
   - Rate limiting: 1 request/second
   - Monthly quota: 10,000 requests
   - API key authentication
   - Timeout: 30 seconds for Lambda execution

4. Security
   - Private S3 bucket with public access blocked
   - IAM role-based access control
   - API Gateway usage plans and API keys
   - ECR repository policies with specific permissions

5. Docker Configuration
   - Base image: Python 3.11 Bullseye
   - Custom dependencies management
   - Standardized Dockerfile generation

## Development Workflow
1. Code changes pushed to GitHub
2. Terraform Cloud triggers infrastructure updates
3. Docker images built and pushed to ECR
4. Lambda function updated with new image
5. API Gateway handles request routing


