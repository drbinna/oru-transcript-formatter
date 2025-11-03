# 🚀 AWS Deployment Guide - ORU Transcript Formatter

This guide covers deploying your application to AWS using multiple options, from simplest to more advanced.

---

## 🎯 Option 1: AWS App Runner (Recommended - Simplest)

**Best for:** Quick deployment, similar to Render experience  
**Cost:** ~$7-25/month (pay per use, first 100 CPU hours free)  
**Time:** 15-20 minutes

### Why App Runner?
- ✅ Container-based (uses your Dockerfile)
- ✅ Auto-scaling
- ✅ HTTPS included
- ✅ Easy environment variable management
- ✅ Similar to Render experience

### Prerequisites:
- AWS account
- AWS CLI installed (`aws --version`)
- Docker installed (for building)
- ECR access

### Steps:

#### 1. Install AWS CLI and Configure
```bash
# Install AWS CLI (if not installed)
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configure AWS credentials
aws configure
# Enter your Access Key ID, Secret Access Key, region (e.g., us-east-1), and output format (json)
```

#### 2. Build and Push Docker Image to ECR

```bash
# Set variables
AWS_REGION="us-east-1"  # Change to your preferred region
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REPO="oru-transcript-formatter"

# Create ECR repository
aws ecr create-repository --repository-name $ECR_REPO --region $AWS_REGION

# Get login token
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Build Docker image
docker build -t $ECR_REPO:latest .

# Tag image
docker tag $ECR_REPO:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO:latest

# Push to ECR
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO:latest
```

#### 3. Create App Runner Service via AWS Console

1. **Go to AWS App Runner Console**
   - Navigate to https://console.aws.amazon.com/apprunner/
   - Click "Create service"

2. **Configure Source**
   - Choose "Container registry"
   - Select ECR
   - Choose your repository: `oru-transcript-formatter`
   - Choose image tag: `latest`

3. **Configure Deployment**
   - Deployment trigger: "Automatic" (redeploys on new image push)
   - Or "Manual" for manual deployments

4. **Configure Service**
   - Service name: `oru-transcript-formatter`
   - Virtual CPU: 1 vCPU (minimum)
   - Memory: 2 GB (minimum)
   - Port: `8000`
   - Environment variables:
     - Key: `ANTHROPIC_API_KEY`
     - Value: `your-api-key-here`
   - Health check path: `/api`

5. **Create Service**
   - Review and create
   - Wait 5-10 minutes for first deployment

#### 4. Access Your Application

- App Runner provides a URL like: `https://xxxxx.us-east-1.awsapprunner.com`
- Your app will be available at this URL

### Auto-Deployment Setup:

To automatically rebuild and redeploy on code changes:

```bash
# Create a simple deploy script
cat > deploy.sh << 'EOF'
#!/bin/bash
AWS_REGION="us-east-1"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REPO="oru-transcript-formatter"

# Build and push
docker build -t $ECR_REPO:latest .
docker tag $ECR_REPO:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO:latest

echo "✅ Image pushed! App Runner will auto-deploy in ~5 minutes"
EOF

chmod +x deploy.sh
```

Run `./deploy.sh` whenever you want to deploy updates.

---

## 🎯 Option 2: AWS Elastic Beanstalk (Alternative)

**Best for:** More control, traditional PaaS  
**Cost:** ~$15-30/month (EC2 + Load Balancer)  
**Time:** 20-30 minutes

### Steps:

#### 1. Install EB CLI
```bash
pip install awsebcli --upgrade
```

#### 2. Initialize Elastic Beanstalk
```bash
cd "/Users/drbinna/Documents/ORU transcript formatting application "
eb init -p docker -r us-east-1 oru-transcript-formatter
```

#### 3. Create Environment
```bash
eb create oru-transcript-formatter-env \
  --envvars ANTHROPIC_API_KEY=your-api-key-here \
  --instance-type t3.small \
  --single
```

#### 4. Deploy
```bash
eb deploy
```

#### 5. Open Application
```bash
eb open
```

#### 6. View Logs
```bash
eb logs
```

---

## 🎯 Option 3: AWS ECS Fargate (Advanced)

**Best for:** Maximum control, production workloads  
**Cost:** ~$15-40/month  
**Time:** 30-45 minutes

### Steps:

1. **Push Docker image to ECR** (same as App Runner step 2)

2. **Create ECS Cluster and Service** via AWS Console:
   - Go to ECS → Clusters → Create Cluster
   - Choose Fargate
   - Create task definition with your ECR image
   - Create service with load balancer
   - Configure environment variables

3. **Set up Application Load Balancer** for HTTPS

---

## 🔧 Configuration Files Created

### Files for AWS deployment:

1. **`apprunner.yaml`** - App Runner configuration
2. **`.ebextensions/01_python.config`** - Elastic Beanstalk configuration
3. **`Dockerrun.aws.json`** - Elastic Beanstalk Docker configuration

### Existing files:
- **`Dockerfile`** - Already configured, works with AWS

---

## 🔐 Environment Variables

All AWS deployment options require:

| Variable | Description | Required |
|----------|-------------|----------|
| `ANTHROPIC_API_KEY` | Your Claude API key | ✅ Yes |
| `PORT` | Server port (default: 8000) | ⚠️ Optional |

---

## 💰 Cost Comparison

| Service | Estimated Monthly Cost |
|---------|----------------------|
| **AWS App Runner** | $7-25 (pay per use) |
| **AWS Elastic Beanstalk** | $15-30 (always-on EC2) |
| **AWS ECS Fargate** | $15-40 (always-on) |
| **Render (old)** | Free (with limitations) |

**Note:** All prices exclude Anthropic API costs (~$0.05-0.10 per transcript)

---

## 🚀 Quick Deploy Script (App Runner)

Create `deploy.sh`:

```bash
#!/bin/bash
set -e

AWS_REGION="${AWS_REGION:-us-east-1}"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REPO="oru-transcript-formatter"
IMAGE_TAG="${1:-latest}"

echo "🏗️  Building Docker image..."
docker build -t $ECR_REPO:$IMAGE_TAG .

echo "🏷️  Tagging image..."
docker tag $ECR_REPO:$IMAGE_TAG $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO:$IMAGE_TAG

echo "📤 Pushing to ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO:$IMAGE_TAG

echo "✅ Deployed! Image: $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO:$IMAGE_TAG"
echo "🔄 App Runner will auto-deploy in ~5-10 minutes"
```

Make it executable:
```bash
chmod +x deploy.sh
./deploy.sh
```

---

## 🔍 Troubleshooting

### App Runner Issues:

**Service fails to start:**
- Check CloudWatch logs: AWS Console → App Runner → Service → Logs
- Verify `ANTHROPIC_API_KEY` is set correctly
- Check that port 8000 is correct

**Timeout issues:**
- App Runner has a 5-minute timeout by default
- For longer processing, consider increasing timeout or using async processing

### Elastic Beanstalk Issues:

**Application fails to deploy:**
```bash
eb logs
eb health
```

**View detailed logs:**
```bash
eb logs --all
```

### General Issues:

**Can't push to ECR:**
- Verify AWS credentials: `aws sts get-caller-identity`
- Check ECR repository exists
- Verify IAM permissions for ECR

**Docker build fails:**
- Test locally: `docker build -t test .`
- Check Dockerfile syntax

---

## 📊 Monitoring

### CloudWatch Logs:
- App Runner: Automatic in CloudWatch
- Elastic Beanstalk: `eb logs` or AWS Console

### Health Checks:
- App Runner: Automatically monitors `/api` endpoint
- Elastic Beanstalk: Configure in `.ebextensions`

---

## 🔄 CI/CD Setup (Optional)

### GitHub Actions Example:

Create `.github/workflows/deploy-aws.yml`:

```yaml
name: Deploy to AWS App Runner

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v1
      
      - name: Build and push Docker image
        run: |
          docker build -t oru-transcript-formatter .
          docker tag oru-transcript-formatter:latest ${{ secrets.AWS_ECR_REGISTRY }}/oru-transcript-formatter:latest
          docker push ${{ secrets.AWS_ECR_REGISTRY }}/oru-transcript-formatter:latest
```

---

## ✅ Recommendation

**For easiest migration from Render: Use AWS App Runner**

- Most similar experience to Render
- Automatic deployments
- Pay-per-use pricing
- HTTPS included
- Minimal configuration

**Next steps:**
1. Follow "Option 1: AWS App Runner" above
2. Run the deploy script when needed
3. Update your frontend API URL to point to App Runner URL

---

## 📝 Notes

- **First 100 CPU hours free** on App Runner (new accounts)
- **Always test locally first** before deploying
- **Monitor costs** in AWS Cost Explorer
- **Set up billing alerts** to avoid surprises

