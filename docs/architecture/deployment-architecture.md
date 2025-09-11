# Deployment Architecture Stories

## Docker Configuration

### Multi-Stage Docker Build

**Story:** Create optimized Docker containers for production deployment

```dockerfile
# Dockerfile
FROM node:18-alpine AS frontend-builder

# Set working directory
WORKDIR /app

# Copy package files
COPY apps/web/package*.json ./
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy frontend source
COPY apps/web ./apps/web
COPY packages ./packages

# Build frontend
WORKDIR /app/apps/web
RUN npm run build

# Python backend stage
FROM python:3.11-slim AS backend-builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY apps/api/requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim AS production

# Set working directory
WORKDIR /app

# Install system dependencies for runtime
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy Python dependencies from builder
COPY --from=backend-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend-builder /usr/local/bin /usr/local/bin

# Copy built frontend
COPY --from=frontend-builder /app/apps/web/.next ./frontend/.next
COPY --from=frontend-builder /app/apps/web/public ./frontend/public
COPY --from=frontend-builder /app/apps/web/package.json ./frontend/

# Copy backend source
COPY apps/api ./backend
COPY packages/shared ./packages/shared

# Copy startup script
COPY scripts/start.sh ./
RUN chmod +x start.sh

# Change ownership to non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose ports
EXPOSE 3000 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Start both services
CMD ["./start.sh"]
```

### Startup Script

**Story:** Create unified startup script for both frontend and backend

```bash
#!/bin/bash
# scripts/start.sh

set -e

echo "Starting Resume Analysis MVP..."

# Set environment variables
export NODE_ENV=${NODE_ENV:-production}
export PYTHONPATH=/app/backend/src:$PYTHONPATH

# Function to start frontend
start_frontend() {
    echo "Starting Next.js frontend on port 3000..."
    cd /app/frontend
    npm start &
    FRONTEND_PID=$!
    echo "Frontend started with PID: $FRONTEND_PID"
}

# Function to start backend
start_backend() {
    echo "Starting FastAPI backend on port 8000..."
    cd /app/backend
    
    # Run database migrations
    if [ "$RUN_MIGRATIONS" = "true" ]; then
        echo "Running database migrations..."
        alembic upgrade head
    fi
    
    # Start FastAPI with uvicorn
    uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 1 &
    BACKEND_PID=$!
    echo "Backend started with PID: $BACKEND_PID"
}

# Function to handle shutdown
shutdown() {
    echo "Shutting down services..."
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID
    fi
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID
    fi
    exit 0
}

# Set up signal handlers
trap shutdown SIGTERM SIGINT

# Start services
start_backend
start_frontend

# Wait for any process to exit
wait
```

### Docker Compose for Development

**Story:** Create development environment with Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
      target: production
    ports:
      - "3000:3000"  # Frontend
      - "8000:8000"  # Backend API
    environment:
      - NODE_ENV=development
      - DATABASE_URL=postgresql://postgres:password@db:5432/resume_analysis
      - REDIS_URL=redis://redis:6379/0
      - AWS_REGION=us-east-1
      - S3_BUCKET_NAME=resume-analysis-dev
      - RUN_MIGRATIONS=true
    depends_on:
      - db
      - redis
    volumes:
      - ./apps/web:/app/frontend:cached
      - ./apps/api:/app/backend:cached
      - ./packages:/app/packages:cached
    networks:
      - app-network

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=resume_analysis
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init-db.sql:/docker-entrypoint-initdb.d/init-db.sql
    networks:
      - app-network

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - app-network

  # Development tools
  pgadmin:
    image: dpage/pgadmin4:latest
    environment:
      - PGADMIN_DEFAULT_EMAIL=admin@example.com
      - PGADMIN_DEFAULT_PASSWORD=admin
    ports:
      - "5050:80"
    depends_on:
      - db
    networks:
      - app-network

volumes:
  postgres_data:
  redis_data:

networks:
  app-network:
    driver: bridge
```

## AWS ECS Deployment

### ECS Task Definition

**Story:** Configure ECS task definition for production deployment

```json
{
  "family": "resume-analysis-mvp",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::ACCOUNT_ID:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::ACCOUNT_ID:role/resumeAnalysisTaskRole",
  "containerDefinitions": [
    {
      "name": "resume-analysis-app",
      "image": "ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/resume-analysis:latest",
      "portMappings": [
        {
          "containerPort": 3000,
          "protocol": "tcp",
          "name": "frontend"
        },
        {
          "containerPort": 8000,
          "protocol": "tcp",
          "name": "backend"
        }
      ],
      "environment": [
        {
          "name": "NODE_ENV",
          "value": "production"
        },
        {
          "name": "AWS_REGION",
          "value": "us-east-1"
        },
        {
          "name": "RUN_MIGRATIONS",
          "value": "true"
        }
      ],
      "secrets": [
        {
          "name": "DATABASE_URL",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:ACCOUNT_ID:secret:resume-analysis/database-url"
        },
        {
          "name": "AWS_ACCESS_KEY_ID",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:ACCOUNT_ID:secret:resume-analysis/aws-credentials:access_key_id"
        },
        {
          "name": "AWS_SECRET_ACCESS_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:ACCOUNT_ID:secret:resume-analysis/aws-credentials:secret_access_key"
        },
        {
          "name": "S3_BUCKET_NAME",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:ACCOUNT_ID:secret:resume-analysis/s3-bucket"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/resume-analysis-mvp",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": [
          "CMD-SHELL",
          "curl -f http://localhost:8000/health || exit 1"
        ],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 60
      },
      "essential": true
    }
  ]
}
```

### ECS Service Configuration

**Story:** Configure ECS service with load balancer and auto-scaling

```json
{
  "serviceName": "resume-analysis-service",
  "cluster": "resume-analysis-cluster",
  "taskDefinition": "resume-analysis-mvp:1",
  "desiredCount": 2,
  "launchType": "FARGATE",
  "platformVersion": "1.4.0",
  "networkConfiguration": {
    "awsvpcConfiguration": {
      "subnets": [
        "subnet-12345678",
        "subnet-87654321"
      ],
      "securityGroups": [
        "sg-12345678"
      ],
      "assignPublicIp": "ENABLED"
    }
  },
  "loadBalancers": [
    {
      "targetGroupArn": "arn:aws:elasticloadbalancing:us-east-1:ACCOUNT_ID:targetgroup/resume-analysis-frontend/1234567890123456",
      "containerName": "resume-analysis-app",
      "containerPort": 3000
    },
    {
      "targetGroupArn": "arn:aws:elasticloadbalancing:us-east-1:ACCOUNT_ID:targetgroup/resume-analysis-backend/1234567890123456",
      "containerName": "resume-analysis-app",
      "containerPort": 8000
    }
  ],
  "serviceRegistries": [
    {
      "registryArn": "arn:aws:servicediscovery:us-east-1:ACCOUNT_ID:service/srv-12345678",
      "containerName": "resume-analysis-app"
    }
  ],
  "deploymentConfiguration": {
    "maximumPercent": 200,
    "minimumHealthyPercent": 50,
    "deploymentCircuitBreaker": {
      "enable": true,
      "rollback": true
    }
  },
  "enableExecuteCommand": true,
  "tags": [
    {
      "key": "Environment",
      "value": "production"
    },
    {
      "key": "Project",
      "value": "resume-analysis-mvp"
    }
  ]
}
```

### Application Load Balancer Configuration

**Story:** Configure ALB for routing frontend and backend traffic

```yaml
# Infrastructure as Code (AWS CDK)
import * as cdk from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as elbv2 from 'aws-cdk-lib/aws-elasticloadbalancingv2';
import * as ecs from 'aws-cdk-lib/aws-ecs';
import * as logs from 'aws-cdk-lib/aws-logs';

export class ResumeAnalysisInfrastructureStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // VPC
    const vpc = new ec2.Vpc(this, 'ResumeAnalysisVPC', {
      maxAzs: 2,
      natGateways: 1,
    });

    // ECS Cluster
    const cluster = new ecs.Cluster(this, 'ResumeAnalysisCluster', {
      vpc,
      clusterName: 'resume-analysis-cluster',
    });

    // Application Load Balancer
    const alb = new elbv2.ApplicationLoadBalancer(this, 'ResumeAnalysisALB', {
      vpc,
      internetFacing: true,
      loadBalancerName: 'resume-analysis-alb',
    });

    // Frontend Target Group
    const frontendTargetGroup = new elbv2.ApplicationTargetGroup(this, 'FrontendTargetGroup', {
      vpc,
      port: 3000,
      protocol: elbv2.ApplicationProtocol.HTTP,
      targetType: elbv2.TargetType.IP,
      healthCheck: {
        enabled: true,
        path: '/',
        healthyHttpCodes: '200',
        interval: cdk.Duration.seconds(30),
        timeout: cdk.Duration.seconds(10),
        healthyThresholdCount: 2,
        unhealthyThresholdCount: 5,
      },
    });

    // Backend API Target Group
    const backendTargetGroup = new elbv2.ApplicationTargetGroup(this, 'BackendTargetGroup', {
      vpc,
      port: 8000,
      protocol: elbv2.ApplicationProtocol.HTTP,
      targetType: elbv2.TargetType.IP,
      healthCheck: {
        enabled: true,
        path: '/health',
        healthyHttpCodes: '200',
        interval: cdk.Duration.seconds(30),
        timeout: cdk.Duration.seconds(10),
        healthyThresholdCount: 2,
        unhealthyThresholdCount: 5,
      },
    });

    // HTTPS Listener
    const httpsListener = alb.addListener('HTTPSListener', {
      port: 443,
      protocol: elbv2.ApplicationProtocol.HTTPS,
      certificates: [
        elbv2.ListenerCertificate.fromArn('arn:aws:acm:us-east-1:ACCOUNT_ID:certificate/CERTIFICATE_ID')
      ],
      defaultTargetGroups: [frontendTargetGroup],
    });

    // API routing rule
    httpsListener.addTargetGroups('APIRoute', {
      targetGroups: [backendTargetGroup],
      priority: 100,
      conditions: [
        elbv2.ListenerCondition.pathPatterns(['/api/*']),
      ],
    });

    // HTTP to HTTPS redirect
    alb.addListener('HTTPListener', {
      port: 80,
      protocol: elbv2.ApplicationProtocol.HTTP,
      defaultAction: elbv2.ListenerAction.redirect({
        protocol: elbv2.ApplicationProtocol.HTTPS,
        port: '443',
        permanent: true,
      }),
    });

    // CloudWatch Log Group
    const logGroup = new logs.LogGroup(this, 'ResumeAnalysisLogGroup', {
      logGroupName: '/ecs/resume-analysis-mvp',
      retention: logs.RetentionDays.ONE_WEEK,
    });

    // Task Definition
    const taskDefinition = new ecs.FargateTaskDefinition(this, 'ResumeAnalysisTaskDef', {
      memoryLimitMiB: 1024,
      cpu: 512,
    });

    // Container Definition
    const container = taskDefinition.addContainer('ResumeAnalysisContainer', {
      image: ecs.ContainerImage.fromRegistry('ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/resume-analysis:latest'),
      logging: ecs.LogDriver.awsLogs({
        streamPrefix: 'ecs',
        logGroup: logGroup,
      }),
      environment: {
        NODE_ENV: 'production',
        AWS_REGION: 'us-east-1',
      },
      secrets: {
        DATABASE_URL: ecs.Secret.fromSecretsManager(
          secretsManager.Secret.fromSecretArn(this, 'DatabaseSecret', 
            'arn:aws:secretsmanager:us-east-1:ACCOUNT_ID:secret:resume-analysis/database-url')
        ),
      },
    });

    // Port mappings
    container.addPortMappings({
      containerPort: 3000,
      protocol: ecs.Protocol.TCP,
    });

    container.addPortMappings({
      containerPort: 8000,
      protocol: ecs.Protocol.TCP,
    });

    // ECS Service
    const service = new ecs.FargateService(this, 'ResumeAnalysisService', {
      cluster,
      taskDefinition,
      desiredCount: 2,
      assignPublicIp: true,
      serviceName: 'resume-analysis-service',
    });

    // Attach service to target groups
    service.attachToApplicationTargetGroup(frontendTargetGroup);
    service.attachToApplicationTargetGroup(backendTargetGroup);

    // Auto Scaling
    const scaling = service.autoScaleTaskCount({
      maxCapacity: 10,
      minCapacity: 2,
    });

    scaling.scaleOnCpuUtilization('CpuScaling', {
      targetUtilizationPercent: 70,
      scaleInCooldown: cdk.Duration.seconds(60),
      scaleOutCooldown: cdk.Duration.seconds(60),
    });

    scaling.scaleOnMemoryUtilization('MemoryScaling', {
      targetUtilizationPercent: 80,
      scaleInCooldown: cdk.Duration.seconds(60),
      scaleOutCooldown: cdk.Duration.seconds(60),
    });

    // Outputs
    new cdk.CfnOutput(this, 'LoadBalancerDNS', {
      value: alb.loadBalancerDnsName,
      description: 'DNS name of the load balancer',
    });

    new cdk.CfnOutput(this, 'ClusterName', {
      value: cluster.clusterName,
      description: 'Name of the ECS cluster',
    });
  }
}
```

## CI/CD Pipeline

### GitHub Actions Workflow

**Story:** Create comprehensive CI/CD pipeline with GitHub Actions

```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

env:
  AWS_REGION: us-east-1
  ECR_REPOSITORY: resume-analysis
  ECS_SERVICE: resume-analysis-service
  ECS_CLUSTER: resume-analysis-cluster

jobs:
  # Test and Build
  test-and-build:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18'
        cache: 'npm'

    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        cache: 'pip'

    - name: Install dependencies
      run: |
        npm ci
        cd apps/api && pip install -r requirements.txt

    - name: Run frontend linting
      run: |
        cd apps/web
        npm run lint

    - name: Run frontend tests
      run: |
        cd apps/web
        npm run test:ci

    - name: Run backend linting
      run: |
        cd apps/api
        flake8 src/ --max-line-length=100

    - name: Run backend tests
      run: |
        cd apps/api
        pytest tests/ -v --cov=src --cov-report=xml

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        files: ./apps/api/coverage.xml
        flags: backend

    - name: Build frontend
      run: |
        cd apps/web
        npm run build

    - name: Run E2E tests
      run: |
        npx playwright install
        npm run test:e2e
      env:
        CI: true

  # Security scanning
  security-scan:
    runs-on: ubuntu-latest
    needs: test-and-build
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Run Trivy vulnerability scanner
      uses: aquasecurity/trivy-action@master
      with:
        scan-type: 'fs'
        scan-ref: '.'
        format: 'sarif'
        output: 'trivy-results.sarif'

    - name: Upload Trivy scan results to GitHub Security tab
      uses: github/codeql-action/upload-sarif@v2
      with:
        sarif_file: 'trivy-results.sarif'

  # Build and push Docker image
  build-and-push:
    runs-on: ubuntu-latest
    needs: [test-and-build, security-scan]
    if: github.ref == 'refs/heads/main'
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v4
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: ${{ env.AWS_REGION }}

    - name: Login to Amazon ECR
      id: login-ecr
      uses: aws-actions/amazon-ecr-login@v2

    - name: Build, tag, and push image to Amazon ECR
      id: build-image
      env:
        ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
        IMAGE_TAG: ${{ github.sha }}
      run: |
        # Build Docker image
        docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
        docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:latest .
        
        # Push images to ECR
        docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
        docker push $ECR_REGISTRY/$ECR_REPOSITORY:latest
        
        # Output image URI
        echo "image=$ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG" >> $GITHUB_OUTPUT

    - name: Scan Docker image
      uses: aquasecurity/trivy-action@master
      with:
        image-ref: ${{ steps.build-image.outputs.image }}
        format: 'sarif'
        output: 'docker-trivy-results.sarif'

    - name: Upload Docker scan results
      uses: github/codeql-action/upload-sarif@v2
      with:
        sarif_file: 'docker-trivy-results.sarif'

  # Deploy to staging
  deploy-staging:
    runs-on: ubuntu-latest
    needs: build-and-push
    if: github.ref == 'refs/heads/main'
    environment: staging
    
    steps:
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v4
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: ${{ env.AWS_REGION }}

    - name: Update ECS service
      run: |
        # Update task definition with new image
        aws ecs update-service \
          --cluster ${{ env.ECS_CLUSTER }}-staging \
          --service ${{ env.ECS_SERVICE }}-staging \
          --force-new-deployment

    - name: Wait for deployment
      run: |
        aws ecs wait services-stable \
          --cluster ${{ env.ECS_CLUSTER }}-staging \
          --services ${{ env.ECS_SERVICE }}-staging

    - name: Run smoke tests
      run: |
        # Wait for service to be ready
        sleep 30
        
        # Run basic health checks
        curl -f https://staging.resumeanalysis.com/health || exit 1
        curl -f https://staging.resumeanalysis.com/api/health || exit 1

  # Deploy to production
  deploy-production:
    runs-on: ubuntu-latest
    needs: deploy-staging
    if: github.ref == 'refs/heads/main'
    environment: production
    
    steps:
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v4
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: ${{ env.AWS_REGION }}

    - name: Deploy to production
      run: |
        # Update production service
        aws ecs update-service \
          --cluster ${{ env.ECS_CLUSTER }} \
          --service ${{ env.ECS_SERVICE }} \
          --force-new-deployment

    - name: Wait for deployment
      run: |
        aws ecs wait services-stable \
          --cluster ${{ env.ECS_CLUSTER }} \
          --services ${{ env.ECS_SERVICE }}

    - name: Run production smoke tests
      run: |
        # Wait for service to be ready
        sleep 30
        
        # Run comprehensive health checks
        curl -f https://resumeanalysis.com/health || exit 1
        curl -f https://resumeanalysis.com/api/health || exit 1

    - name: Notify deployment
      uses: 8398a7/action-slack@v3
      with:
        status: ${{ job.status }}
        channel: '#deployments'
        webhook_url: ${{ secrets.SLACK_WEBHOOK }}
      if: always()

  # Rollback on failure
  rollback:
    runs-on: ubuntu-latest
    needs: deploy-production
    if: failure()
    environment: production
    
    steps:
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v4
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: ${{ env.AWS_REGION }}

    - name: Rollback deployment
      run: |
        # Get previous task definition
        PREVIOUS_TASK_DEF=$(aws ecs describe-services \
          --cluster ${{ env.ECS_CLUSTER }} \
          --services ${{ env.ECS_SERVICE }} \
          --query 'services[0].deployments[1].taskDefinition' \
          --output text)
        
        # Update service to previous version
        aws ecs update-service \
          --cluster ${{ env.ECS_CLUSTER }} \
          --service ${{ env.ECS_SERVICE }} \
          --task-definition $PREVIOUS_TASK_DEF

    - name: Wait for rollback
      run: |
        aws ecs wait services-stable \
          --cluster ${{ env.ECS_CLUSTER }} \
          --services ${{ env.ECS_SERVICE }}

    - name: Notify rollback
      uses: 8398a7/action-slack@v3
      with:
        status: 'warning'
        text: 'Production deployment failed and was rolled back'
        channel: '#alerts'
        webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

## Environment Configuration

### Environment-Specific Configuration

**Story:** Configure different environments with appropriate settings

```bash
# .env.development
NODE_ENV=development
DATABASE_URL=postgresql://postgres:password@localhost:5432/resume_analysis_dev
REDIS_URL=redis://localhost:6379/0
AWS_REGION=us-east-1
S3_BUCKET_NAME=resume-analysis-dev
AWS_ACCESS_KEY_ID=your-dev-access-key
AWS_SECRET_ACCESS_KEY=your-dev-secret-key
NEXT_PUBLIC_API_URL=http://localhost:8000
LOG_LEVEL=debug
RUN_MIGRATIONS=true
```

```bash
# .env.staging
NODE_ENV=staging
DATABASE_URL=${DATABASE_URL}
REDIS_URL=${REDIS_URL}
AWS_REGION=us-east-1
S3_BUCKET_NAME=resume-analysis-staging
NEXT_PUBLIC_API_URL=https://api-staging.resumeanalysis.com
LOG_LEVEL=info
RUN_MIGRATIONS=true
ENABLE_METRICS=true
```

```bash
# .env.production
NODE_ENV=production
DATABASE_URL=${DATABASE_URL}
REDIS_URL=${REDIS_URL}
AWS_REGION=us-east-1
S3_BUCKET_NAME=resume-analysis-prod
NEXT_PUBLIC_API_URL=https://api.resumeanalysis.com
LOG_LEVEL=warn
RUN_MIGRATIONS=false
ENABLE_METRICS=true
SENTRY_DSN=${SENTRY_DSN}
```

### AWS Secrets Manager Integration

**Story:** Manage secrets securely using AWS Secrets Manager

```python
# apps/api/src/config/secrets.py
import boto3
import json
from typing import Dict, Any
from functools import lru_cache

class SecretsManager:
    def __init__(self, region_name: str = 'us-east-1'):
        self.client = boto3.client('secretsmanager', region_name=region_name)
        self._cache = {}
    
    @lru_cache(maxsize=128)
    def get_secret(self, secret_name: str) -> Dict[str, Any]:
        """Get secret from AWS Secrets Manager with caching"""
        try:
            response = self.client.get_secret_value(SecretId=secret_name)
            secret_string = response['SecretString']
            return json.loads(secret_string)
        except Exception as e:
            raise Exception(f"Failed to retrieve secret {secret_name}: {str(e)}")
    
    def get_database_url(self) -> str:
        """Get database URL from secrets"""
        db_secret = self.get_secret('resume-analysis/database')
        return f"postgresql://{db_secret['username']}:{db_secret['password']}@{db_secret['host']}:{db_secret['port']}/{db_secret['database']}"
    
    def get_aws_credentials(self) -> Dict[str, str]:
        """Get AWS credentials from secrets"""
        return self.get_secret('resume-analysis/aws-credentials')
    
    def get_s3_config(self) -> Dict[str, str]:
        """Get S3 configuration from secrets"""
        return self.get_secret('resume-analysis/s3-config')

# Usage in settings
secrets_manager = SecretsManager()

# Get secrets based on environment
if os.getenv('NODE_ENV') == 'production':
    DATABASE_URL = secrets_manager.get_database_url()
    aws_creds = secrets_manager.get_aws_credentials()
    AWS_ACCESS_KEY_ID = aws_creds['access_key_id']
    AWS_SECRET_ACCESS_KEY = aws_creds['secret_access_key']
else:
    DATABASE_URL = os.getenv('DATABASE_URL')
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
```

## Monitoring and Observability

### CloudWatch Configuration

**Story:** Set up comprehensive monitoring with CloudWatch

```python
# apps/api/src/utils/monitoring.py
import boto3
import time
from typing import Dict, Any
from contextlib import contextmanager

class CloudWatchMetrics:
    def __init__(self, namespace: str = 'ResumeAnalysis/MVP'):
        self.cloudwatch = boto3.client('cloudwatch')
        self.namespace = namespace
    
    def put_metric(self, metric_name: str, value: float, unit: str = 'Count', dimensions: Dict[str, str] = None):
        """Put custom metric to CloudWatch"""
        try:
            metric_data = {
                'MetricName': metric_name,
                'Value': value,
                'Unit': unit,
                'Timestamp': time.time()
            }
            
            if dimensions:
                metric_data['Dimensions'] = [
                    {'Name': k, 'Value': v} for k, v in dimensions.items()
                ]
            
            self.cloudwatch.put_metric_data(
                Namespace=self.namespace,
                MetricData=[metric_data]
            )
        except Exception as e:
            print(f"Failed to put metric {metric_name}: {str(e)}")
    
    @contextmanager
    def timer(self, metric_name: str, dimensions: Dict[str, str] = None):
        """Context manager for timing operations"""
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            self.put_metric(
                metric_name=metric_name,
                value=duration * 1000,  # Convert to milliseconds
                unit='Milliseconds',
                dimensions=dimensions
            )
    
    def increment_counter(self, metric_name: str, dimensions: Dict[str, str] = None):
        """Increment a counter metric"""
        self.put_metric(metric_name, 1, 'Count', dimensions)
    
    def record_analysis_metrics(self, analysis_time: float, success: bool, file_type: str):
        """Record metrics for resume analysis"""
        dimensions = {
            'FileType': file_type,
            'Status': 'Success' if success else 'Failed'
        }
        
        # Analysis duration
        self.put_metric('AnalysisDuration', analysis_time * 1000, 'Milliseconds', dimensions)
        
        # Analysis count
        self.increment_counter('AnalysisCount', dimensions)
        
        # Success rate
        self.put_metric('AnalysisSuccess', 1 if success else 0, 'Count', dimensions)

# Usage in services
metrics = CloudWatchMetrics()

async def analyze_resume(file_content: bytes, file_type: str):
    with metrics.timer('ResumeAnalysis', {'FileType': file_type}):
        try:
            result = await perform_analysis(file_content)
            metrics.record_analysis_metrics(
                analysis_time=result['processing_time'],
                success=True,
                file_type=file_type
            )
            return result
        except Exception as e:
            metrics.record_analysis_metrics(
                analysis_time=0,
                success=False,
                file_type=file_type
            )
            raise
```

### Health Check Endpoints

**Story:** Implement comprehensive health checks

```python
# apps/api/src/routes/health.py
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any
import boto3
import redis
import time

from ..database import get_db
from ..config.settings import get_settings

router = APIRouter(tags=["health"])
settings = get_settings()

@router.get("/health")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0"
    }

@router.get("/health/detailed")
async def detailed_health_check(db: Session = Depends(get_db)):
    """Detailed health check with dependency status"""
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0",
        "checks": {}
    }
    
    overall_healthy = True
    
    # Database check
    try:
        db.execute("SELECT 1")
        health_status["checks"]["database"] = {
            "status": "healthy",
            "message": "Database connection successful"
        }
    except Exception as e:
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "message": f"Database connection failed: {str(e)}"
        }
        overall_healthy = False
    
    # Redis check
    try:
        r = redis.Redis.from_url(settings.REDIS_URL)
        r.ping()
        health_status["checks"]["redis"] = {
            "status": "healthy",
            "message": "Redis connection successful"
        }
    except Exception as e:
        health_status["checks"]["redis"] = {
            "status": "unhealthy",
            "message": f"Redis connection failed: {str(e)}"
        }
        overall_healthy = False
    
    # S3 check
    try:
        s3_client = boto3.client('s3', region_name=settings.AWS_REGION)
        s3_client.head_bucket(Bucket=settings.S3_BUCKET_NAME)
        health_status["checks"]["s3"] = {
            "status": "healthy",
            "message": "S3 bucket accessible"
        }
    except Exception as e:
        health_status["checks"]["s3"] = {
            "status": "unhealthy",
            "message": f"S3 bucket check failed: {str(e)}"
        }
        overall_healthy = False
    
    # Bedrock check
    try:
        bedrock_client = boto3.client('bedrock-runtime', region_name=settings.AWS_REGION)
        # Simple list models call to check connectivity
        bedrock_client.list_foundation_models()
        health_status["checks"]["bedrock"] = {
            "status": "healthy",
            "message": "Bedrock service accessible"
        }
    except Exception as e:
        health_status["checks"]["bedrock"] = {
            "status": "unhealthy",
            "message": f"Bedrock service check failed: {str(e)}"
        }
        overall_healthy = False
    
    # Update overall status
    if not overall_healthy:
        health_status["status"] = "unhealthy"
        raise HTTPException(status_code=503, detail=health_status)
    
    return health_status

@router.get("/health/ready")
async def readiness_check(db: Session = Depends(get_db)):
    """Kubernetes readiness probe"""
    try:
        # Quick database check
        db.execute("SELECT 1")
        return {"status": "ready"}
    except Exception:
        raise HTTPException(status_code=503, detail={"status": "not ready"})

@router.get("/health/live")
async def liveness_check():
    """Kubernetes liveness probe"""
    return {"status": "alive"}
```

This comprehensive deployment architecture provides:

1. **Optimized Docker containers** with multi-stage builds
2. **AWS ECS deployment** with Fargate for serverless containers
3. **Application Load Balancer** for traffic routing
4. **Complete CI/CD pipeline** with GitHub Actions
5. **Environment-specific configurations** with secrets management
6. **Comprehensive monitoring** with CloudWatch metrics
7. **Health checks** for container orchestration
8. **Auto-scaling** based on CPU and memory utilization
9. **Security scanning** in the CI/CD pipeline
10. **Rollback capabilities** for failed deployments

The deployment is designed for high availability, scalability, and operational excellence in production environments.
