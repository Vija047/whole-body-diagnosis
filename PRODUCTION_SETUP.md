# 🏭 Production Setup Guide

**Complete guide for deploying the ML Ops platform to production.**

---

## 📋 Table of Contents

1. [Pre-deployment Checklist](#pre-deployment-checklist)
2. [Infrastructure Setup](#infrastructure-setup)
3. [Database Configuration](#database-configuration)
4. [Application Deployment](#application-deployment)
5. [Monitoring & Alerting](#monitoring--alerting)
6. [Backup & Disaster Recovery](#backup--disaster-recovery)
7. [Security Hardening](#security-hardening)
8. [Performance Tuning](#performance-tuning)
9. [Troubleshooting](#troubleshooting)

---

## ✅ Pre-deployment Checklist

- [ ] All code reviewed and tests passing
- [ ] API keys and secrets generated
- [ ] Database credentials configured
- [ ] SSL certificates obtained
- [ ] DNS records configured
- [ ] Monitoring alert emails set up
- [ ] Backup procedures documented
- [ ] Security scan completed
- [ ] Load testing completed
- [ ] Runbook created for on-call team

---

## 🏗️ Infrastructure Setup

### AWS Deployment (Recommended)

```bash
# 1. Create VPC and Subnets
aws ec2 create-vpc --cidr-block 10.0.0.0/16

# 2. Create Security Groups
aws ec2 create-security-group \
  --group-name mlops-api-sg \
  --description "ML Ops API security group"

# 3. Create RDS PostgreSQL Instance
aws rds create-db-instance \
  --db-instance-identifier mlops-prod-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username admin \
  --master-user-password $(python -c "import secrets; print(secrets.token_urlsafe(32))") \
  --allocated-storage 100 \
  --storage-type gp3 \
  --backup-retention-period 30 \
  --multi-az

# 4. Launch EC2 Instance (t3.medium minimum for 2 vCPU)
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t3.medium \
  --key-name my-key \
  --security-group-ids sg-xxxxx

# 5. Create S3 Bucket for Model Storage
aws s3 mb s3://mlops-prod-models \
  --region us-east-1
```

### GCP Deployment

```bash
# 1. Create Compute Instance
gcloud compute instances create mlops-api \
  --image-family ubuntu-2204-lts \
  --image-project ubuntu-os-cloud \
  --machine-type n1-standard-2 \
  --zone us-central1-a

# 2. Create Cloud SQL Instance
gcloud sql instances create mlops-postgres \
  --database-version POSTGRES_15 \
  --tier db-f1-micro \
  --region us-central1

# 3. Create Storage Bucket
gsutil mb gs://mlops-prod-models
```

---

## 💾 Database Configuration

### PostgreSQL Setup

```bash
# 1. Connect to RDS/Cloud SQL
psql -h <production-db-host> -U admin -d postgres

# 2. Create database
CREATE DATABASE mlops ENCODING 'UTF8';

# 3. Create user with limited permissions
CREATE USER mlops_app WITH PASSWORD '<generated-secure-password>';
GRANT CONNECT ON DATABASE mlops TO mlops_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE ON TABLES TO mlops_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO mlops_app;

# 4. Enable extensions
\c mlops
CREATE EXTENSION IF NOT EXISTS uuid-ossp;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
```

### Application User Setup

```bash
# 1. Create .env.production file
cat > .env.production << EOF
# Production environment variables
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=False
API_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")

# Database for production
DATABASE_URL=postgresql://mlops_app:password@db-host:5432/mlops
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10

# Logging
LOG_LEVEL=INFO
LOG_DIR=/var/log/mlops

# MLflow
MLFLOW_TRACKING_URI=http://localhost:5001
MLFLOW_REGISTRY_URI=postgresql://mlops_app:password@db-host:5432/mlflow

# Drift detection
DRIFT_THRESHOLD=0.30
DRIFT_CHECK_INTERVAL=3600
EOF
```

### Database Migrations

```bash
# 1. Initialize Alembic
alembic init alembic

# 2. Generate initial migration
alembic revision --autogenerate -m "Initial schema"

# 3. Run migrations
alembic upgrade head
```

---

## 🚀 Application Deployment

### Docker Deployment

```bash
# 1. Build Docker image
docker build -t mlops-api:2.0.0 .

# 2. Tag for registry
docker tag mlops-api:2.0.0 <registry>/mlops-api:2.0.0
docker tag mlops-api:2.0.0 <registry>/mlops-api:latest

# 3. Push to registry
docker push <registry>/mlops-api:2.0.0

# 4. Pull on production server
docker pull <registry>/mlops-api:2.0.0

# 5. Run container
docker run -d \
  --name mlops-api \
  --env-file .env.production \
  --restart unless-stopped \
  --health-cmd='curl -f http://localhost:8000/health || exit 1' \
  --health-interval=30s \
  --health-timeout=10s \
  --health-retries=3 \
  -p 8000:8000 \
  <registry>/mlops-api:2.0.0
```

### Kubernetes Deployment

```bash
# 1. Create namespace
kubectl create namespace mlops

# 2. Create secret for API key
kubectl create secret generic mlops-secrets \
  --from-literal=api_key=$(python -c "import secrets; print(secrets.token_urlsafe(32))") \
  -n mlops

# 3. Deploy using helm (recommended)
helm install mlops ./helm/mlops-chart -n mlops -f helm/values-prod.yaml

# 4. Verify deployment
kubectl get pods -n mlops
kubectl logs -n mlops -l app=mlops-api
```

---

## 📊 Monitoring & Alerting

### Prometheus Metrics Export

```python
# Add to main.py for Prometheus scraping
from prometheus_client import Counter, Histogram, generate_latest
import time

# Metrics
prediction_counter = Counter('predictions_total', 'Total predictions', ['disease', 'result'])
prediction_latency = Histogram('prediction_latency_seconds', 'Prediction latency')

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

### Grafana Dashboard

```json
{
  "dashboard": {
    "title": "ML Ops Monitoring",
    "panels": [
      {
        "title": "Predictions per minute",
        "targets": [{
          "expr": "rate(predictions_total[1m])"
        }]
      },
      {
        "title": "Average latency",
        "targets": [{
          "expr": "histogram_quantile(0.95, prediction_latency_seconds)"
        }]
      },
      {
        "title": "Model drift score",
        "targets": [{
          "expr": "drift_score"
        }]
      }
    ]
  }
}
```

### Email Alerts

```python
# Send drift alerts
from email.mime.text import MIMEText
import smtplib

def send_drift_alert(disease, drift_score):
    msg = MIMEText(f"Drift detected for {disease}: {drift_score:.1%}")
    msg['Subject'] = f"⚠️ Model Drift Alert: {disease}"
    msg['From'] = 'alerts@yourorg.com'
    msg['To'] = 'team@yourorg.com'
    
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(USERNAME, PASSWORD)
        server.send_message(msg)
```

---

## 🔄 Backup & Disaster Recovery

### Automated Backups

```bash
# 1. Database backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -h $DB_HOST -U $DB_USER $DB_NAME | \
  gzip > /backups/mlops_$DATE.sql.gz

# 2. Model artifacts backup
aws s3 sync ./models s3://mlops-backups/models/$DATE/

# 3. Schedule with cron
0 2 * * * /scripts/backup_production.sh
```

### Restore Procedures

```bash
# Restore database
gunzip < /backups/mlops_20240331_020000.sql.gz | \
  psql -h $DB_HOST -U $DB_USER $DB_NAME

# Restore models
aws s3 sync s3://mlops-backups/models/latest/ ./models/
```

---

## 🔒 Security Hardening

### SSL/TLS Configuration

```nginx
# Nginx reverse proxy configuration
server {
    listen 443 ssl http2;
    server_name api.yourorg.com;

    ssl_certificate /etc/ssl/certs/your_cert.crt;
    ssl_certificate_key /etc/ssl/private/your_key.key;
    
    # Modern configuration
    ssl_protocols TLSv1.3 TLSv1.2;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### API Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter

@app.post("/predict/diabetes")
@limiter.limit("100/minute")
async def predict_diabetes(request: Request, data: DiabetesInput):
    ...
```

### Secrets Management

```bash
# AWS Secrets Manager
aws secretsmanager create-secret \
  --name mlops/prod/api-key \
  --secret-string $(python -c "import secrets; print(secrets.token_urlsafe(32))")

# Retrieve in application
import json
import boto3

def get_secret(secret_name):
    client = boto3.client('secretsmanager', region_name='us-east-1')
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])
```

---

## ⚡ Performance Tuning

### Database Query Optimization

```sql
-- Add indexes for common queries
CREATE INDEX idx_predictions_disease_timestamp 
  ON predictions(disease, timestamp DESC);

CREATE INDEX idx_predictions_client_id 
  ON predictions(client_id);

-- Analyze query performance
EXPLAIN ANALYZE
SELECT * FROM predictions 
WHERE disease = 'diabetes' 
ORDER BY timestamp DESC 
LIMIT 100;
```

### Connection Pooling

```python
# Increase connection pool size
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,  # Verify connections
    pool_recycle=3600    # Recycle connections hourly
)
```

### Caching Strategy

```python
from functools import lru_cache
import redis

# Cache model metadata
r = redis.Redis(host='localhost', port=6379, db=0)

@lru_cache(maxsize=100)
def get_model_version(disease):
    cached = r.get(f"model_version:{disease}")
    if cached:
        return cached.decode()
    # Query database if not in cache
    result = db.query(ModelMetadata).filter(...).first()
    r.setex(f"model_version:{disease}", 3600, result.version)
    return result.version
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Models not loading at startup

```bash
# Check file permissions
ls -la models/

# Verify model files exist
python -c "import joblib; joblib.load('models/diabetes_model.pkl')"

# Check disk space
df -h
```

#### 2. Database connection errors

```bash
# Test connection
psql -h $DB_HOST -U $DB_USER -d mlops -c "SELECT 1"

# Check connection pool
SELECT count(*) FROM pg_stat_activity;

# Increase pool size in .env.production
DB_POOL_SIZE=30
```

#### 3. High API latency

```bash
# Check resource usage
docker stats

# Monitor database slow queries
SET log_min_duration_statement = 1000;

# Profile prediction endpoint
pip install py-spy
py-spy record -o profile.svg -p <pid>
```

#### 4. Stuck predictions

```bash
# Kill hanging processes
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE duration > '5 minutes';

# Clear celery queue (if async)
celery -A tasks purge
```

---

## 📞 Support & Escalation

**On-call Runbook**: `/docs/RUNBOOK.md`  
**Alert Contacts**: See PagerDuty configuration  
**Escalation Policy**: Lead Engineer → Manager → VP Engineering

For issues, create GitHub issue with details: logs, error message, reproduction steps.

---

**Version**: 2.0.0  
**Last Updated**: March 2024  
**Status**: Production Ready ✅
