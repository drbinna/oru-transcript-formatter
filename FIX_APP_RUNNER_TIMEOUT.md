# 🔧 Fix: App Runner 504 Gateway Timeout

## ❌ The Problem

Your formatting endpoint is timing out with `504 Gateway Timeout` because:
- Processing takes 3-4 minutes (Claude AI API calls + formatting)
- App Runner has a **default timeout of 300 seconds (5 minutes)**
- The gateway times out before processing completes

## ✅ Solutions

### Option 1: Increase App Runner Timeout (Recommended)

App Runner allows up to **900 seconds (15 minutes)** timeout:

1. **Go to App Runner Console:**
   - https://console.aws.amazon.com/apprunner/
   - Click on your service: `oru-transcript-formatter`

2. **Edit Configuration:**
   - Click **"Configuration"** tab
   - Click **"Edit"** button
   - Scroll to **"Network settings"** or **"Service settings"**

3. **Increase Timeout:**
   - Look for **"Request timeout"** or **"Connection timeout"**
   - Change from default (300s) to **900 seconds (15 minutes)**
   - Save changes

4. **Wait for redeployment** (~5 minutes)

### Option 2: Use Async Processing (Better for Production)

Modify your application to return immediately and process asynchronously:

1. **Return a job ID immediately**
2. **Process in background**
3. **Poll for status** or use webhooks
4. **Download when ready**

This requires code changes but is better UX.

### Option 3: Use Different AWS Service

For long-running processes, consider:
- **AWS ECS Fargate** - More control, longer timeouts
- **AWS Lambda** - For async processing (max 15 minutes)
- **AWS Batch** - For heavy processing workloads

---

## 🔍 Current Status

**Working:**
- ✅ Health check: `GET /api` → 200 OK
- ✅ Service is running
- ✅ Image deployed correctly

**Not Working:**
- ❌ Format endpoint: Times out after ~2 minutes
- ❌ Processing takes 3-4 minutes

---

## 📝 Quick Fix Steps

### Increase Timeout in App Runner:

1. **AWS Console → App Runner → Your Service**
2. **Configuration → Edit**
3. **Find "Timeout" or "Request timeout" setting**
4. **Change to 900 seconds (15 minutes)**
5. **Save and wait for redeployment**

### Alternative: Check Current Settings

Run this to see current timeout:

```bash
aws apprunner describe-service \
  --service-arn $(aws apprunner list-services --region us-east-2 --query 'ServiceSummaryList[?ServiceName==`oru-transcript-formatter`].ServiceArn' --output text) \
  --region us-east-2 \
  --query 'Service.SourceConfiguration.AutoDeploymentsEnabled' \
  --output json
```

---

## 💡 Recommendation

**For now:** Increase App Runner timeout to 900 seconds

**For production:** Consider implementing async processing pattern:
1. POST /format → returns job ID
2. GET /format/{job_id}/status → check progress
3. GET /format/{job_id}/download → get file when ready

---

## ⚠️ Note

Even with increased timeout, App Runner may still have limitations. The async approach is more scalable for production use.

