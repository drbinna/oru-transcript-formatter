# ⚡ Quick Fix: App Runner Invalid Image URL

## The Problem
Your image URI is missing the tag. App Runner needs: `repository:tag`

## ✅ Immediate Fix (2 Options)

### Option 1: Fix in App Runner Console (Easiest)

1. Go to: https://console.aws.amazon.com/apprunner/
2. Click on your service or create a new one
3. When configuring **"Container image URI"**:
   
   **USE THE DROPDOWNS:**
   - **Repository:** Select `oru-transcript-formatter` from dropdown
   - **Image tag:** Select `latest` from dropdown
   
   **OR paste this full URI:**
   ```
   860639121362.dkr.ecr.us-east-2.amazonaws.com/oru-transcript-formatter:latest
   ```
   ⚠️ Notice the `:latest` at the end - that's what was missing!

4. Click **"Save"** or **"Create"**

---

### Option 2: Make Sure Image Exists First

If you haven't pushed your image yet, run this:

```bash
cd "/Users/drbinna/Documents/ORU transcript formatting application "

# Set your details
AWS_ACCOUNT_ID="860639121362"
AWS_REGION="us-east-2"

# Login to ECR
aws ecr get-login-password --region $AWS_REGION | \
  docker login --username AWS --password-stdin \
  $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Build and push
docker build -t oru-transcript-formatter:latest .
docker tag oru-transcript-formatter:latest \
  $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/oru-transcript-formatter:latest
docker push \
  $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/oru-transcript-formatter:latest
```

Then use the full URI with `:latest` in App Runner.

---

## 🎯 The Correct Format

**❌ Wrong:**
```
860639121362.dkr.ecr.us-east-2.amazonaws.com/oru-transcript-formatter
```

**✅ Correct:**
```
860639121362.dkr.ecr.us-east-2.amazonaws.com/oru-transcript-formatter:latest
```

The `:latest` tag is required!

