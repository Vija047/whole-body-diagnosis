# 🚀 Quick Start: Production Deployment

**Get the ML Ops platform running in production in 30 minutes.**

---

## 📋 Prerequisites

- Docker & Docker Compose installed
- AWS account (or GCP/Azure)
- Python 3.10+ installed locally
- Git
- 4GB RAM minimum, 10GB disk space

---

## ⚡ 5-Minute Local Test

```bash
# 1. Clone and setup
git clone https://github.com/yourorg/diagnosis-mlops.git
cd diagnosis-mlops

# 2. Create environment
python -m venv .venv
source .venv/Scripts/activate  # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Initialize database
python database.py

# 5. Run tests
pytest tests/ -v

# 6. Start API
python -m api.main

# Visit: http://localhost:8000/api/docs
```

---

## 🐳 30-Minute Docker Deployment (Local)

```bash
# 1. Start everything
docker-compose up -d

# 2. Wait for services to be healthy
docker-compose ps  # Check STATUS column

# 3. Test health
curl http://localhost:8000/health

# 4. View logs
docker-compose logs -f api

# 5. Access
- API: http://localhost:8000/api/docs
- MLflow: http://localhost:5001
- Database: localhost:5432
```

---

## 🌐 Production Deployment (AWS)

### Step 1: Prepare (5 min)

```bash
# 1. Create .env.production
cp .env.example .env.production
# Edit with production values

# 2. Generate strong API key
python -c "import secrets; print(secrets.token_urlsafe(32))"
# Copy output to API_KEY in .env.production

# 3. Generate strong DB password
python -c "import secrets; print(secrets.token_urlsafe(32))"
# Copy output to DB_PASSWORD in .env.production
```

### Step 2: Build Docker Image (10 min)

```bash
# 1. Build locally
docker build -t mlops-api:2.0.0 .

# 2. Test locally
docker run -p 8000:8000 mlops-api:2.0.0

# 3. Tag for AWS
docker tag mlops-api:2.0.0 <account-id>.dkr.ecr.us-east-1.amazonaws.com/mlops-api:2.0.0

# 4. Push to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/mlops-api:2.0.0
```

### Step 3: Deploy Infrastructure (10 min)

```bash
# 1. Create RDS Database
aws rds create-db-instance \
  --db-instance-identifier mlops-prod \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username admin \
  --master-user-password "$(cat .env.production | grep DB_PASSWORD | cut -d= -f2)"

# 2. Create S3 bucket for models
aws s3 mb s3://mlops-prod-models
aws s3 sync ./models s3://mlops-prod-models/

# 3. Create security groups
aws ec2 create-security-group \
  --group-name mlops-api-sg \
  --description "ML Ops API security group"

# 4. Launch EC2 instance
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t3.medium \
  --key-name my-key
```

### Step 4: Deploy Application (5 min)

```bash
# 1. SSH to instance
ssh -i my-key.pem ec2-user@<instance-ip>

# 2. Clone code
git clone https://github.com/yourorg/diagnosis-mlops.git
cd diagnosis-mlops

# 3. Copy environment file (from local)
# scp -i my-key.pem .env.production ec2-user@<instance-ip>:/home/ec2-user/diagnosis-mlops/

# 4. Start services
docker-compose -f docker-compose.prod.yml up -d

# 5. Verify
curl https://<instance-ip>/health
```

---

## ✅ Verification Checklist

After deployment, verify:

```bash
# ✅ API Health
curl https://api.yourorg.com/health

# ✅ Database Connection
psql -h <db-host> -U mlops_app -d mlops -c "SELECT 1;"

# ✅ Models Loaded
curl -H "x-api-key: $API_KEY" https://api.yourorg.com/models/info

# ✅ Test Prediction
curl -X POST https://api.yourorg.com/predict/diabetes \
  -H "x-api-key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "hbA1c_level": 7.5,
    "blood_glucose_level": 150,
    "age": 45
  }'

# ✅ Check Logs
docker logs mlops-api | tail -50
```

---

## 🔧 Common Issues & Fixes

### Issue: Models not found
```bash
# Solution: Upload models to S3
aws s3 sync ./models s3://mlops-prod-models/
docker-compose -f docker-compose.prod.yml restart api
```

### Issue: Database connection failed
```bash
# Solution: Check database is running
docker-compose -f docker-compose.prod.yml logs postgres

# Or verify RDS
aws rds describe-db-instances --db-instance-identifier mlops-prod
```

### Issue: API returns 503
```bash
# Solution: Check if models are loaded
docker logs mlops-api | grep -i "loaded\|failed"

# Rebuild and restart
docker-compose -f docker-compose.prod.yml up -d --build
```

### Issue: High latency
```bash
# Solution: Check database query performance
psql -h $DB_HOST -U mlops_app -d mlops -c "SELECT * FROM pg_stat_statements;"

# Monitor system resources
docker stats
```

---

## 📊 Monitoring Setup

### Setup CloudWatch (AWS)

```bash
# 1. Install CloudWatch agent
wget https://s3.amazonaws.com/amazoncloudwatch-agent/amazon_linux/amd64/latest/amazon-cloudwatch-agent.rpm
rpm -U ./amazon-cloudwatch-agent.rpm

# 2. Create IAM role with CloudWatch permissions
aws iam create-role --role-name mlops-cloudwatch-role

# 3. Configure CloudWatch
/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
  -a fetch-config \
  -m ec2 \
  -s \
  -c file:cloudwatch-config.json
```

### Setup Grafana Dashboard

```bash
# 1. Access Grafana
# http://localhost:3000

# 2. Add Prometheus datasource
# Settings → Data Sources → Add → Prometheus
# URL: http://prometheus:9090

# 3. Import dashboard JSON
# Dashboards → New → Import → Paste JSON
```

---

## 🔄 Backup & Recovery

### Automated Backup

```bash
# Daily automated backup
aws rds create-db-snapshot \
  --db-instance-identifier mlops-prod \
  --db-snapshot-identifier mlops-backup-$(date +%Y%m%d)
```

### Restore from Backup

```bash
# Restore to new instance
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier mlops-prod-restored \
  --db-snapshot-identifier mlops-backup-20240331
```

---

## 📞 Support

| Issue | Solution |
|-------|----------|
| API not responding | Check health: `curl /health` |
| Models not loaded | Check logs: `docker logs mlops-api` |
| Database error | Verify connection: `psql...` |
| High latency | Monitor: `docker stats` |
| Out of disk | Check: `df -h /` |

**For more help**: See [README.md](README.md) or [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

---

**Version**: 2.0.0  
**Status**: Production Ready ✅
