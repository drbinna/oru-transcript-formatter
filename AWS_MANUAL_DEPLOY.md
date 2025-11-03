# 🚀 Step-by-Step Manual AWS Deployment Guide

This guide walks you through deploying your ORU Transcript Formatter to AWS App Runner **manually**, step-by-step, with exact instructions for every click.

---

## 📋 Prerequisites Checklist

Before starting, make sure you have:

- [ ] **AWS Account** - Sign up at https://aws.amazon.com/ (if you don't have one)
- [ ] **AWS Access Keys** - You'll create these in Step 1
- [ ] **Docker Desktop** installed and running
- [ ] **AWS CLI** installed (we'll check this)
- [ ] **Your Anthropic API Key** ready to paste

**Estimated time:** 20-30 minutes

---

## Step 1: Set Up AWS Access Credentials

### 1.1 Create IAM User (if you don't have one)

1. **Go to AWS Console:** https://console.aws.amazon.com/
2. **Search for "IAM"** in the top search bar
3. **Click "IAM"** → Click **"Users"** in the left sidebar
4. **Click "Create user"** button (top right)
5. **Enter username:** `oru-deployment-user`
6. **Click "Next"**

### 1.2 Set Permissions

1. **Select:** "Attach policies directly"
2. **Check these boxes:**
   - ☑️ `AmazonEC2ContainerRegistryFullAccess` (for ECR)
   - ☑️ `AWSAppRunnerFullAccess` (for App Runner)
   - ☑️ `CloudWatchLogsFullAccess` (for logs)

   *If you don't see these, search for them in the search box*

3. **Click "Next"** → **Click "Create user"**

### 1.3 Create Access Keys

1. **Click on the user** you just created (`oru-deployment-user`)
2. **Click the "Security credentials" tab**
3. **Scroll down to "Access keys"**
4. **Click "Create access key"**
5. **Select:** "Command Line Interface (CLI)"
6. **Check the box:** "I understand..."
7. **Click "Next"** → **Click "Create access key"**
8. **IMPORTANT: Copy both values:**
   - **Access key ID** - Copy this
   - **Secret access key** - Copy this (you can't see it again!)
9. **Save these somewhere secure** (password manager, notes app, etc.)
10. **Click "Done"**

---

## Step 2: Install and Configure AWS CLI

### 2.1 Check if AWS CLI is Installed

Open Terminal (Mac) or Command Prompt (Windows) and run:

```bash
aws --version
```

**If you see a version number (like `aws-cli/2.x.x`):** ✅ Skip to Step 2.3

**If you see "command not found":** Continue to Step 2.2

### 2.2 Install AWS CLI (if needed)

**On Mac:**
```bash
# Install Homebrew if you don't have it
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install AWS CLI
brew install awscli
```

**On Windows:**
1. Download: https://awscli.amazonaws.com/AWSCLIV2.msi
2. Run the installer
3. Follow the installation wizard

**On Linux:**
```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

### 2.3 Configure AWS CLI

In Terminal/Command Prompt:

```bash
aws configure
```

**You'll be prompted 4 times. Enter:**

1. **AWS Access Key ID:** Paste your Access Key ID from Step 1.3
2. **AWS Secret Access Key:** Paste your Secret Access Key from Step 1.3
3. **Default region name:** `us-east-1` (or your preferred region)
4. **Default output format:** `json`

**Press Enter after each entry.**

**Test it:**
```bash
aws sts get-caller-identity
```

You should see your account ID. ✅ If so, continue to Step 3!

---

## Step 3: Prepare Your Code

### 3.1 Navigate to Your Project

```bash
cd "/Users/drbinna/Documents/ORU transcript formatting application "
```

### 3.2 Verify Docker is Running

```bash
docker --version
docker ps
```

**If Docker isn't running:**
- **Mac:** Open Docker Desktop app
- **Windows:** Open Docker Desktop app
- Wait until it says "Docker is running"

---

## Step 4: Create ECR Repository (Elastic Container Registry)

This is where AWS will store your Docker image.

### 4.1 Go to ECR Console

1. **Go to:** https://console.aws.amazon.com/ecr/
2. **Make sure you're in the right region** (top right corner - should be `us-east-1` or your region)
3. **Click "Repositories"** in the left sidebar
4. **Click "Create repository"** button (top right)

### 4.2 Configure Repository

1. **Visibility settings:**
   - Select: **"Private"** (recommended)

2. **Repository name:**
   - Enter: `oru-transcript-formatter`
   - *No spaces, lowercase, hyphens OK*

3. **Tag immutability:**
   - Leave **unchecked** (default)

4. **Scan on push:**
   - Leave **unchecked** (to save costs, optional)

5. **Encryption:**
   - Leave defaults

6. **Click "Create repository"** (bottom right)

### 4.3 View Repository URI

1. **Click on your repository:** `oru-transcript-formatter`
2. **Look at the top of the page** - you'll see "Repository URI"
   - It looks like: `123456789012.dkr.ecr.us-east-1.amazonaws.com/oru-transcript-formatter`
   - **Copy this URI** - you'll need it in the next steps!
3. **Leave this tab open**

---

## Step 5: Build and Push Docker Image

### 5.1 Get ECR Login Command

1. **In the ECR repository page**, click **"View push commands"** button (top right)
2. **You'll see 4 commands** - we'll run them one by one
3. **OR, copy the commands shown in the popup**

### 5.2 Run the Push Commands

Open Terminal in your project directory and run **each command** from the ECR push commands (or use the commands below):

```bash
# Navigate to project
cd "/Users/drbinna/Documents/ORU transcript formatting application "

# Get your AWS account ID (you'll need this)
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "Your AWS Account ID: $AWS_ACCOUNT_ID"

# Set region
AWS_REGION="us-east-1"  # Change if you used a different region

# Step 1: Login to ECR
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Step 2: Build Docker image
docker build -t oru-transcript-formatter:latest .

# Step 3: Tag the image
docker tag oru-transcript-formatter:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/oru-transcript-formatter:latest

# Step 4: Push the image
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/oru-transcript-formatter:latest
```

**This will take 5-10 minutes** (building and pushing the image).

**What you'll see:**
- Docker building your image (lots of output)
- Uploading layers to ECR (progress bars)
- ✅ Success message when done

**Troubleshooting:**
- If "login" fails: Check your AWS credentials with `aws configure`
- If "push" fails: Make sure Docker is running
- If "build" fails: Check Dockerfile is correct

---

## Step 6: Create App Runner Service

### 6.1 Go to App Runner Console

1. **Go to:** https://console.aws.amazon.com/apprunner/
2. **Make sure you're in the right region** (top right - should match ECR region)
3. **Click "Create service"** button (top right)

### 6.2 Configure Source

**Select "Container registry"**

1. **Provider:** Select **"Amazon ECR"**

2. **Container image URI:**
   - **Click the dropdown** → Select your repository: `oru-transcript-formatter`
   - **Or paste your repository URI** from Step 4.3
   - **Image tag:** Select `latest` from dropdown
   - Full URI should look like: `123456789012.dkr.ecr.us-east-1.amazonaws.com/oru-transcript-formatter:latest`

3. **Deployment trigger:**
   - Select **"Automatic"** (redeploys when you push new images)
   - *Or "Manual" if you want to control when to deploy*

4. **Click "Next"** (bottom right)

### 6.3 Configure Service Settings

1. **Service name:**
   - Enter: `oru-transcript-formatter`
   - *This can be anything, but keep it simple*

2. **Virtual CPU:**
   - Select: **1 vCPU** (minimum, enough for your app)

3. **Memory:**
   - Select: **2 GB** (minimum, enough for your app)

4. **Click "Next"**

### 6.4 Configure Service - Networking

1. **Port:**
   - Enter: `8000`
   - *This matches your Dockerfile*

2. **Environment variables:**
   - **Click "Add environment variable"**
   - **Key:** `ANTHROPIC_API_KEY`
   - **Value:** Paste your actual Anthropic API key
   - **Click "Add"**

3. **Health check:**
   - **Path:** `/api`
   - **Interval:** Leave default (10 seconds)
   - **Timeout:** Leave default (5 seconds)

4. **Click "Next"**

### 6.5 Review and Create

1. **Review your settings:**
   - Source: Your ECR image
   - Service name: `oru-transcript-formatter`
   - CPU: 1 vCPU, 2 GB memory
   - Port: 8000
   - Environment variable: ANTHROPIC_API_KEY (should show as set)

2. **Scroll down** - check auto scaling settings:
   - Min instances: 1
   - Max instances: 5 (or keep default)

3. **Click "Create & deploy"** (bottom right)

### 6.6 Wait for Deployment

1. **You'll see:** "Creating service..." with a progress bar
2. **This takes 5-10 minutes** for the first deployment
3. **Status will show:**
   - Creating → Running → ✅ Successful

**While waiting, you can:**
- Watch the logs (click on service → "Logs" tab)
- See the progress in "Events" tab

---

## Step 7: Get Your Application URL

### 7.1 Find Your URL

Once deployment is complete (status shows "Running"):

1. **On the service page**, look for **"Default domain"**
2. **Copy the URL** - it looks like:
   - `https://xxxxx.us-east-1.awsapprunner.com`
3. **Save this URL** - this is your live application!

---

## Step 8: Test Your Deployment

### 8.1 Test Health Check

Open your browser or use curl:

```bash
curl https://xxxxx.us-east-1.awsapprunner.com/api
```

**Expected response:**
```json
{"message":"ORU Transcript Formatting API","version":"1.0"}
```

✅ **If you see this, your API is working!**

### 8.2 Test Formatting Endpoint

```bash
curl -X POST https://xxxxx.us-east-1.awsapprunner.com/format \
  -F "file=@samples/WI0110-2448_-_Last_Days.txt" \
  --output test_aws_deployment.docx
```

**This will take 3-4 minutes** (same as local testing).

**If successful:**
- You'll get a `test_aws_deployment.docx` file
- ✅ Your deployment is working!

### 8.3 Test in Browser

1. **Open:** `https://xxxxx.us-east-1.awsapprunner.com` in your browser
2. **You should see:** The frontend interface (if frontend is built)
3. **Try uploading a file** through the web interface

---

## Step 9: Update Frontend (If Needed)

If your frontend needs to point to the new API:

### 9.1 Update API URL in Frontend

Edit `frontend/src/App.tsx`:

```typescript
// Find this line (around line 44):
const apiUrl = import.meta.env.PROD 
  ? '/format' 
  : 'http://localhost:8000/format'

// Change to:
const apiUrl = import.meta.env.PROD 
  ? 'https://xxxxx.us-east-1.awsapprunner.com/format' 
  : 'http://localhost:8000/format'
```

Replace `xxxxx.us-east-1.awsapprunner.com` with your actual App Runner URL.

### 9.2 Rebuild Frontend and Redeploy

```bash
cd frontend
npm run build

# Then rebuild and push Docker image
cd ..
docker build -t oru-transcript-formatter:latest .
docker tag oru-transcript-formatter:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/oru-transcript-formatter:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/oru-transcript-formatter:latest
```

App Runner will automatically detect the new image and redeploy.

---

## ✅ Success Checklist

You're done when:

- [ ] AWS CLI configured (`aws configure` works)
- [ ] ECR repository created (`oru-transcript-formatter`)
- [ ] Docker image pushed to ECR (visible in repository)
- [ ] App Runner service created and running
- [ ] Health check works (`/api` returns 200)
- [ ] Format endpoint works (can generate DOCX)
- [ ] You have your App Runner URL

---

## 🔄 Making Updates

Whenever you make code changes:

### Quick Update Process:

```bash
# 1. Navigate to project
cd "/Users/drbinna/Documents/ORU transcript formatting application "

# 2. Get your account ID (set once, reuse)
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION="us-east-1"

# 3. Login to ECR
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# 4. Build, tag, and push
docker build -t oru-transcript-formatter:latest .
docker tag oru-transcript-formatter:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/oru-transcript-formatter:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/oru-transcript-formatter:latest
```

**App Runner will automatically:**
- Detect the new image
- Start a new deployment (takes ~5-10 minutes)
- Switch traffic to the new version when ready

---

## 🆘 Troubleshooting

### Issue: "Access Denied" when pushing to ECR

**Solution:**
- Check your IAM user has `AmazonEC2ContainerRegistryFullAccess` policy
- Verify AWS credentials: `aws sts get-caller-identity`

### Issue: Service fails to start

**Solution:**
1. Go to App Runner → Your service → **"Logs"** tab
2. Look for error messages
3. Common issues:
   - Missing `ANTHROPIC_API_KEY` → Add it in environment variables
   - Wrong port → Should be 8000
   - Template file missing → Check Dockerfile copied templates

### Issue: Health check failing

**Solution:**
- Check `/api` endpoint works: `curl https://your-url/api`
- Verify port is 8000
- Check logs for errors

### Issue: Timeout errors

**Solution:**
- Your processing takes 3-4 minutes
- App Runner timeout is 5 minutes (should be fine)
- If issues persist, check CloudWatch logs

### Issue: Can't find ECR repository

**Solution:**
- Make sure you're in the same AWS region
- Check repository name matches exactly
- Verify you have permissions

---

## 💰 Cost Monitoring

### Set Up Billing Alerts:

1. **Go to:** https://console.aws.amazon.com/billing/
2. **Click "Billing preferences"**
3. **Set up CloudWatch billing alarms**
4. **Recommended:** Set alert at $10/month

### Expected Costs:

- **App Runner:** ~$0.007 per CPU hour
- **First 100 hours:** FREE (new accounts
- **ECR storage:** ~$0.10 per GB/month (very small)
- **Total estimate:** $7-15/month for light usage

---

## 📚 Next Steps

- ✅ Monitor usage in CloudWatch
- ✅ Set up billing alerts
- ✅ Bookmark your App Runner URL
- ✅ Update any documentation with your new URL

---

## 🎉 Congratulations!

Your ORU Transcript Formatter is now live on AWS! 

**Your application URL:** `https://xxxxx.us-east-1.awsapprunner.com`

Share this URL with anyone who needs to format transcripts!

---

## 📝 Quick Reference Commands

**Check AWS identity:**
```bash
aws sts get-caller-identity
```

**List ECR repositories:**
```bash
aws ecr describe-repositories
```

**View App Runner services:**
```bash
aws apprunner list-services
```

**View logs:**
```bash
# In App Runner console → Service → Logs tab
```

---

**Need help?** Check the logs in App Runner console or AWS CloudWatch!

