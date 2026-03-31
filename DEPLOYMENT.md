# 🚀 Deployment Guide

**Step-by-step deployment to AWS, GCP, and Azure.**

---

## 📋 Table of Contents

- [AWS Deployment](#aws-deployment)
- [GCP Deployment](#gcp-deployment)
- [Azure Deployment](#azure-deployment)
- [Deployment Validation](#deployment-validation)
- [Rollback Procedures](#rollback-procedures)

---

## ☁️ AWS Deployment

### Architecture

```
Internet Gateway
    ↓
Application Load Balancer (port 443)
    ↓
EC2 Auto Scaling Group (t3.medium)
    ↓
├─ RDS PostgreSQL (multi-AZ)
├─ S3 (models & backups)
├─ CloudWatch (monitoring)
└─ Systems Manager (secrets)
```

### Step 1: Create Infrastructure

```bash
#!/bin/bash

# Export variables
export AWS_REGION=us-east-1
export APP_NAME=mlops-api
export ENV=production

# 1. Create VPC
VPC_ID=$(aws ec2 create-vpc \
  --cidr-block 10.0.0.0/16 \
  --query 'Vpc.VpcId' \
  --output text)

# 2. Create subnets
SUBNET_1=$(aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.1.0/24 \
  --availability-zone ${AWS_REGION}a \
  --query 'Subnet.SubnetId' \
  --output text)

SUBNET_2=$(aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.2.0/24 \
  --availability-zone ${AWS_REGION}b \
  --query 'Subnet.SubnetId' \
  --output text)

# 3. Create security group for API
SG_API=$(aws ec2 create-security-group \
  --group-name ${APP_NAME}-api-sg \
  --description "ML Ops API security group" \
  --vpc-id $VPC_ID \
  --query 'GroupId' \
  --output text)

# Allow HTTPS from anywhere
aws ec2 authorize-security-group-ingress \
  --group-id $SG_API \
  --protocol tcp --port 443 --cidr 0.0.0.0/0

# Allow HTTP from Load Balancer
aws ec2 authorize-security-group-ingress \
  --group-id $SG_API \
  --protocol tcp --port 8000 --source-security-group-name ${APP_NAME}-alb-sg

# 4. Create security group for RDS
SG_DB=$(aws ec2 create-security-group \
  --group-name ${APP_NAME}-db-sg \
  --description "ML Ops Database security group" \
  --vpc-id $VPC_ID \
  --query 'GroupId' \
  --output text)

# Allow PostgreSQL from API
aws ec2 authorize-security-group-ingress \
  --group-id $SG_DB \
  --protocol tcp --port 5432 --source-security-group-name $SG_API

# 5. Create RDS PostgreSQL instance
aws rds create-db-instance \
  --db-instance-identifier ${APP_NAME}-prod \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --engine-version 15.4 \
  --master-username admin \
  --master-user-password "$(python -c 'import secrets; print(secrets.token_urlsafe(32))')" \
  --allocated-storage 100 \
  --storage-type gp3 \
  --vpc-security-group-ids $SG_DB \
  --db-subnet-group-name default \
  --backup-retention-period 30 \
  --multi-az \
  --enable-cloudwatch-logs-exports postgresql \
  --enable-iam-database-authentication

# 6. Create S3 bucket for models
aws s3 mb s3://${APP_NAME}-models-${AWS_REGION}

# 7. Upload models to S3
aws s3 sync ./models s3://${APP_NAME}-models-${AWS_REGION}/models/

echo "Infrastructure created successfully!"
echo "VPC ID: $VPC_ID"
echo "API Security Group: $SG_API"
echo "DB Security Group: $SG_DB"
```

### Step 2: Create ECR Repository

```bash
# Create ECR repository
aws ecr create-repository \
  --repository-name mlops-api \
  --region us-east-1

# Get login token
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Tag and push image
docker build -t mlops-api:2.0.0 .
docker tag mlops-api:2.0.0 <account-id>.dkr.ecr.us-east-1.amazonaws.com/mlops-api:2.0.0
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/mlops-api:2.0.0
```

### Step 3: Launch Instances

```bash
# Create launch template
aws ec2 create-launch-template \
  --launch-template-name mlops-api-template \
  --version-description "ML Ops API Launch Template" \
  --launch-template-data '{
    "ImageId": "ami-0c55b159cbfafe1f0",
    "InstanceType": "t3.medium",
    "IamInstanceProfile": {"Name": "mlops-instance-profile"},
    "SecurityGroupIds": ["sg-xxxxx"],
    "UserData": "IyEvYmluL2Jhc2gKYXB0IHVwZGF0ZQphcHQgaW5zdGFsbCAteSBkb2NrZXIuaW8KYXdzIHMzIGNwIHMzOi8vbWxvcHMtbW9kZWxzL21vZGVscy8gL2hvbWUvdWJ1bnR1L21vZGVscwpkb2NrZXIgcHVsbCAkRUNSX1JFR0lTVFJZ"
  }'

# Create auto scaling group
aws autoscaling create-auto-scaling-group \
  --auto-scaling-group-name mlops-api-asg \
  --launch-template LaunchTemplateName=mlops-api-template,Version='$Latest' \
  --min-size 2 \
  --max-size 10 \
  --desired-capacity 3 \
  --vpc-zone-identifier "subnet-xxxxx subnet-yyyyy" \
  --target-group-arns arn:aws:elasticloadbalancing:us-east-1:<account>:targetgroup/mlops-api/xxxxx
```

### Step 4: Setup Application Load Balancer

```bash
# Create ALB
ALB=$(aws elbv2 create-load-balancer \
  --name mlops-api-alb \
  --subnets subnet-xxxxx subnet-yyyyy \
  --security-groups $SG_ALB \
  --query 'LoadBalancers[0].LoadBalancerArn' \
  --output text)

# Create target group
TG=$(aws elbv2 create-target-group \
  --name mlops-api-tg \
  --protocol HTTP \
  --port 8000 \
  --vpc-id $VPC_ID \
  --query 'TargetGroups[0].TargetGroupArn' \
  --output text)

# Register with auto scaling
aws autoscaling attach-load-balancer-target-groups \
  --auto-scaling-group-name mlops-api-asg \
  --target-group-arns $TG

# Create listener for HTTPS (with certificate)
aws elbv2 create-listener \
  --load-balancer-arn $ALB \
  --protocol HTTPS \
  --port 443 \
  --certificates CertificateArn=arn:aws:acm:us-east-1:<account>:certificate/xxxxx \
  --default-actions Type=forward,TargetGroupArn=$TG
```

---

## ☁️ GCP Deployment

### Step 1: Create Cloud Infrastructure

```bash
# Set project
export PROJECT_ID=your-project-id
gcloud config set project $PROJECT_ID

# Create VPC
gcloud compute networks create mlops-network \
  --subnet-mode=custom

gcloud compute networks subnets create mlops-subnet \
  --network=mlops-network \
  --range=10.0.0.0/24 \
  --region=us-central1

# Create firewall rules
gcloud compute firewall-rules create mlops-allow-https \
  --network=mlops-network \
  --allow=tcp:443

gcloud compute firewall-rules create mlops-allow-http \
  --network=mlops-network \
  --allow=tcp:8000
```

### Step 2: Create Cloud SQL Instance

```bash
# Create PostgreSQL instance
gcloud sql instances create mlops-postgres \
  --database-version POSTGRES_15 \
  --tier db-f1-micro \
  --region us-central1 \
  --network $VPC_ID \
  --enable-bin-log

# Create database
gcloud sql databases create mlops --instance=mlops-postgres

# Create user
gcloud sql users create mlops_app \
  --instance=mlops-postgres \
  --password=$(python -c 'import secrets; print(secrets.token_urlsafe(32))')
```

### Step 3: Deploy with Cloud Run

```bash
# Build image
gcloud builds submit --tag gcr.io/$PROJECT_ID/mlops-api:2.0.0

# Deploy to Cloud Run
gcloud run deploy mlops-api \
  --image gcr.io/$PROJECT_ID/mlops-api:2.0.0 \
  --platform managed \
  --region us-central1 \
  --memory 2Gi \
  --cpu 2 \
  --set-env-vars API_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(32))'),DATABASE_URL=postgresql://... \
  --allow-unauthenticated
```

### Step 4: Setup Cloud Load Balancer

```bash
# Create health check
gcloud compute health-checks create https mlops-health-check \
  --request-path=/health \
  --port=8000

# Create backend service
gcloud compute backend-services create mlops-backend \
  --global \
  --protocol HTTP \
  --health-checks mlops-health-check \
  --port-name http

# Create frontend
gcloud compute addresses create mlops-ip \
  --global

gcloud compute url-maps create mlops-lb \
  --default-service mlops-backend

gcloud compute target-https-proxies create mlops-proxy \
  --url-map mlops-lb \
  --ssl-certificates mlops-cert

gcloud compute forwarding-rules create mlops-forwarding-rule \
  --global \
  --target-https-proxy mlops-proxy \
  --address mlops-ip \
  --ports 443
```

---

## ☁️ Azure Deployment

### Step 1: Setup Azure Resources

```bash
# Set variables
RESOURCE_GROUP="mlops-rg"
LOCATION="eastus"
APP_NAME="mlops-api"

# Create resource group
az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION

# Create storage account for models
az storage account create \
  --name mlopsmodels \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --sku Standard_LRS

# Create Key Vault for secrets
az keyvault create \
  --name mlops-kv \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION

# Store API key
az keyvault secret set \
  --vault-name mlops-kv \
  --name api-key \
  --value $(python -c 'import secrets; print(secrets.token_urlsafe(32))')
```

### Step 2: Create Azure Database for PostgreSQL

```bash
az postgres server create \
  --resource-group $RESOURCE_GROUP \
  --name mlops-postgres \
  --location $LOCATION \
  --admin-user mlops_admin \
  --admin-password $(python -c 'import secrets; print(secrets.token_urlsafe(32))') \
  --sku-name B_Gen5_2 \
  --storage-size 102400 \
  --backup-retention 30 \
  --geo-redundant-backup Enabled
```

### Step 3: Deploy with Azure Container Instances

```bash
# Push to ACR
az acr build \
  --registry mlopsregistry \
  --image mlops-api:2.0.0 .

# Deploy to ACI
az container create \
  --resource-group $RESOURCE_GROUP \
  --name mlops-api-container \
  --image mlopsregistry.azurecr.io/mlops-api:2.0.0 \
  --cpu 2 --memory 2 \
  --ports 8000 \
  --environment-variables \
    API_KEY=$(az keyvault secret show --vault-name mlops-kv --name api-key --query value) \
    DATABASE_URL=postgresql://...
```

---

## ✅ Deployment Validation

### Post-Deployment Checklist

```bash
#!/bin/bash

echo "Running deployment validation..."

# 1. Check API health
echo "✓ Checking API health..."
curl -f https://api.yourorg.com/health || exit 1

# 2. Test predictions
echo "✓ Testing predictions..."
curl -X POST https://api.yourorg.com/predict/diabetes \
  -H "x-api-key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"hbA1c_level": 7.5, "blood_glucose_level": 150, "age": 45}' || exit 1

# 3. Verify database connection
echo "✓ Checking database..."
psql -h $DB_HOST -U $DB_USER -d mlops -c "SELECT COUNT(*) FROM predictions;" || exit 1

# 4. Check logs
echo "✓ Reviewing logs..."
tail -50 /var/log/mlops/api.log

# 5. Verify models loaded
echo "✓ Verifying models..."
curl -s https://api.yourorg.com/models/info \
  -H "x-api-key: $API_KEY" | grep -q "diabetes" || exit 1

echo "✅ All validation checks passed!"
```

---

## 🔄 Rollback Procedures

### Quick Rollback (Within 1 hour)

```bash
# 1. Identify previous good version
aws ec2 describe-launch-templates \
  --launches-template-name mlops-api-template \
  --query 'LaunchTemplates[].VersionNumber'

# 2. Create new version with previous image
aws ec2 create-launch-template-version \
  --launch-template-name mlops-api-template \
  --source-version 2 \
  --launch-template-data '{"ImageId": "ami-0000000000000000"}'

# 3. Update ASG to use previous version
aws autoscaling update-auto-scaling-group \
  --auto-scaling-group-name mlops-api-asg \
  --launch-template LaunchTemplateName=mlops-api-template,Version='$Latest'

# 4. Terminate old instances
aws ec2 terminate-instances --instance-ids i-xxxxx i-yyyyy
```

### Database Rollback

```bash
# 1. Restore from snapshot
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier mlops-restored \
  --db-snapshot-identifier mlops-snapshot-2024-03-31-02-00

# 2. Update DNS to point to restored instance
aws route53 change-resource-record-sets \
  --hosted-zone-id ZXXXXXX \
  --change-batch file://dns-change.json
```

---

**Version**: 2.0.0  
**Last Updated**: March 2024  
**Status**: Production Ready ✅
