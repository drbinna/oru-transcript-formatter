# ⚡ Quick Start: Deploy to AWS App Runner

Follow these steps to deploy your application to AWS App Runner in **15 minutes**.

## Prerequisites Checklist

- [ ] AWS account created
- [ ] AWS CLI installed (`aws --version`)
- [ ] AWS CLI configured (`aws configure`)
- [ ] Docker installed (`docker --version`)

---

## 🚀 Step-by-Step Deployment

### Step 1: Configure AWS (if not done)

```bash
aws configure
# Enter:
# - AWS Access Key ID: (get from IAM Console)
# - AWS Secret Access Key: (get from IAM Console)
# - Default region: us-east-1 (or your preferred region)
# - Default output format: json
```

### Step 2: Run the Deployment Script

```bash
cd "/Users/drbinna/Documents/ORU transcript formatting application "
./deploy-aws.sh
```

This will:
- ✅ Check AWS credentials
- ✅ Create ECR repository (if needed)
- ✅ Build Docker image
- ✅ Push image to AWS ECR

**Expected output:**
```
🚀 AWS Deployment Script
================================
📋 Getting AWS account information...
✅ AWS Account ID: 123456789012
✅ Region: us-east-1

🔍 Checking ECR repository...
✅ Repository exists: oru-transcript-formatter

🏗️  Building Docker image...
🏷️  Tagging image...
🔐 Logging into ECR...
📤 Pushing image to ECR...
✅ Successfully deployed!
```

### Step 3: Create App Runner Service

1. **Go to App Runner Console:**
   - https://console.aws.amazon.com/apprunner/

2. **Click "Create service"**

3. **Configure Source:**
   - Select: **Container registry**
   - Provider: **Amazon ECR**
   - Container image URI: Copy from deploy script output
     - Format: `123456789012.dkr.ecr.us-east-1.amazonaws.com/oru-transcript-formatter:latest`
   - Deployment trigger: **Automatic** (or Manual)

4. **Configure Service:**
   - Service name: `oru-transcript-formatter`
   - Virtual CPU: **1 vCPU**
   - Memory: **2 GB**
   - Port: **8000**
   
5. **Environment Variables:**
   - Click "Add environment variable"
   - Key: `ANTHROPIC_API_KEY`
   - Value: Your actual API key

6. **Auto Scaling:**
   - Min: 1
   - Max: 5
   - (Optional: Keep default)

7. **Health Check:**
   - Health check path: `/api`
   - Health check interval: 10 seconds
   - Health check timeout: 5 seconds

8. **Create Service:**
   - Click "Create & deploy"
   - Wait 5-10 minutes for first deployment

### Step 4: Get Your URL

After deployment completes:
- App Runner provides a URL like: `https://xxxxx.us-east-1.awsapprunner.com`
- Copy this URL

### Step 5: Update Frontend (Optional)

If you want to test the API directly, or update your frontend:

```bash
# In frontend/src/App.tsx, update the API URL:
const apiUrl = import.meta.env.PROD 
  ? 'https://xxxxx.us-east-1.awsapprunner.com/format' 
  : 'http://localhost:8000/format'
```

Or set an environment variable and rebuild:
```bash
cd frontend
VITE_API_URL=https://xxxxx.us-east-1.awsapprunner.com npm run build
```

---

## ✅ Verify Deployment

1. **Test API endpoint:**
   ```bash
   curl https://xxxxx.us-east-1.awsapprunner.com/api
   ```
   Should return: `{"message":"ORU Transcript Formatting API","version":"1.0"}`

2. **Test formatting:**
   ```bash
   curl -X POST https://xxxxx.us-east-1.awsapprunner.com/format \
     -F "file=@samples/WI0110-2448_-_Last_Days.txt" \
     --output test_aws_output.docx
   ```

---

## 🔄 Updating Your Deployment

Whenever you make changes:

```bash
./deploy-aws.sh
```

App Runner will automatically detect the new image and redeploy (takes ~5 minutes).

---

## 🆘 Troubleshooting

### "AWS credentials not found"
```bash
aws configure
```

### "ECR repository access denied"
- Go to IAM Console
- Add ECR permissions to your user/role:
  - `ecr:GetAuthorizationToken`
  - `ecr:BatchCheckLayerAvailability`
  - `ecr:GetDownloadUrlForLayer`
  - `ecr:BatchGetImage`
  - `ecr:PutImage`
  - `ecr:InitiateLayerUpload`
  - `ecr:UploadLayerPart`
  - `ecr:CompleteLayerUpload`

### "Service fails to start"
- Check CloudWatch Logs: App Runner → Service → Logs
- Verify `ANTHROPIC_API_KEY` is set correctly
- Check that port 8000 matches

### "Timeout errors"
- App Runner has 5-minute timeout
- Your processing takes ~3-4 minutes, which should be fine
- If needed, consider async processing

---

## 💰 Cost Estimate

- **First 100 CPU hours: FREE** (new AWS accounts)
- **After that: ~$0.007 per CPU hour**
- **Estimated: $7-15/month** for light usage
- **Plus: Anthropic API costs** (~$0.05-0.10 per transcript)

---

## 📚 Next Steps

- Read full documentation: `AWS_DEPLOY.md`
- Set up billing alerts in AWS Console
- Monitor usage in CloudWatch
- Set up CI/CD (see AWS_DEPLOY.md)

---

## 🎯 Summary

You now have:
- ✅ Docker image in AWS ECR
- ✅ App Runner service running
- ✅ HTTPS URL for your API
- ✅ Auto-deployment on updates

**Your app is live! 🎉**

