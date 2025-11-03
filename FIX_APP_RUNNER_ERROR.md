# 🔧 Fix: Invalid Image URL Error in App Runner

## ❌ The Error

You're seeing this error:
```
The image url provided in the request is invalid: 
860639121362.dkr.ecr.us-east-2.amazonaws.com/oru-transcript-formatter
```

## 🔍 The Problem

The image URI is **missing the tag** (like `:latest`). App Runner needs the **complete image URI including the tag**.

## ✅ The Solution

### Option 1: Add the Tag in App Runner Console

When configuring the container image in App Runner:

1. **Container image URI:** 
   - **Instead of:** `860639121362.dkr.ecr.us-east-2.amazonaws.com/oru-transcript-formatter`
   - **Use:** `860639121362.dkr.ecr.us-east-2.amazonaws.com/oru-transcript-formatter:latest`

2. **OR use the dropdown:**
   - Select your repository from the dropdown
   - **Then select the image tag:** `latest` (from the tag dropdown)
   - App Runner will combine them automatically

### Option 2: Find the Correct Image URI

1. **Go to ECR Console:**
   - https://console.aws.amazon.com/ecr/
   - Make sure you're in **us-east-2** region (top right)

2. **Click on your repository:** `oru-transcript-formatter`

3. **Find the image:**
   - You should see images with tags (like `latest`)
   - **Copy the full URI** from the "Image URI" column
   - It should look like: `860639121362.dkr.ecr.us-east-2.amazonaws.com/oru-transcript-formatter:latest`

4. **Use this full URI** in App Runner

### Option 3: Get Image URI via CLI

Run this command:

```bash
aws ecr describe-images \
  --repository-name oru-transcript-formatter \
  --region us-east-2 \
  --query 'imageDetails[0].{URI:imageTags[0]}' \
  --output text
```

Or to see all images:

```bash
aws ecr describe-images \
  --repository-name oru-transcript-formatter \
  --region us-east-2 \
  --output table
```

---

## 📝 Step-by-Step Fix in App Runner

1. **Go to App Runner Console:**
   - https://console.aws.amazon.com/apprunner/
   - Click on your service (or create new if starting over)

2. **Edit Configuration:**
   - Click **"Configuration"** tab
   - Click **"Edit"** button
   - Scroll to **"Container image URI"**

3. **Fix the Image URI:**
   - **Option A:** Use the dropdowns:
     - Repository: Select `oru-transcript-formatter`
     - Image tag: Select `latest`
   - **Option B:** Paste the full URI:
     - `860639121362.dkr.ecr.us-east-2.amazonaws.com/oru-transcript-formatter:latest`

4. **Save and Deploy:**
   - Click **"Save changes"**
   - App Runner will redeploy

---

## 🔍 Verify Image Exists

Before fixing in App Runner, verify your image exists:

```bash
# Set your account ID
AWS_ACCOUNT_ID="860639121362"
AWS_REGION="us-east-2"

# List images in repository
aws ecr describe-images \
  --repository-name oru-transcript-formatter \
  --region $AWS_REGION
```

**Expected output:** Should show your image with tags.

**If no images found:** You need to push the image first (see below).

---

## 🚀 If Image Doesn't Exist: Push It

If you haven't pushed your image yet, run:

```bash
# Set variables
AWS_ACCOUNT_ID="860639121362"
AWS_REGION="us-east-2"

# Navigate to project
cd "/Users/drbinna/Documents/ORU transcript formatting application "

# Login to ECR
aws ecr get-login-password --region $AWS_REGION | \
  docker login --username AWS --password-stdin \
  $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Build image
docker build -t oru-transcript-formatter:latest .

# Tag image
docker tag oru-transcript-formatter:latest \
  $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/oru-transcript-formatter:latest

# Push image
docker push \
  $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/oru-transcript-formatter:latest
```

---

## ✅ Correct Image URI Format

The correct format for App Runner:

```
<account-id>.dkr.ecr.<region>.amazonaws.com/<repository-name>:<tag>
```

**Your correct URI:**
```
860639121362.dkr.ecr.us-east-2.amazonaws.com/oru-transcript-formatter:latest
```

**Components:**
- `860639121362` = Your AWS account ID
- `us-east-2` = Your region
- `oru-transcript-formatter` = Repository name
- `:latest` = Image tag (required!)

---

## 🎯 Quick Fix Checklist

- [ ] Verify image exists in ECR with tag `latest`
- [ ] Use full URI with `:latest` tag in App Runner
- [ ] Or use dropdowns to select repository + tag separately
- [ ] Save configuration and wait for deployment

---

## 💡 Pro Tip

**When using App Runner's dropdowns:**
1. Repository dropdown → Select `oru-transcript-formatter`
2. Image tag dropdown → Select `latest`
3. App Runner automatically combines them correctly!

This is easier than typing the full URI manually.

---

After fixing, your App Runner service should deploy successfully! ✅

