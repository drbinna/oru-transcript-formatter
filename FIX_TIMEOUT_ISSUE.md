# 🔧 Fix: App Runner 504 Gateway Timeout Issue

## 🔍 Current Configuration

From your service:
- **Health Check Path:** `/` (should be `/api`)
- **Health Check Timeout:** 5 seconds ✅ (fine for health checks)
- **Request Timeout:** Not directly configurable (App Runner default ~300s)

## ❌ The Problem

Your `/format` endpoint times out with 504 Gateway Timeout. This is likely because:

1. **App Runner gateway timeout** (~2 minutes observed)
2. **Processing takes 3-4 minutes** (Claude API calls + formatting)
3. **Request exceeds gateway limit**

## ✅ Solutions

### Solution 1: Update Health Check Path (Do This First)

1. **Go to:** https://console.aws.amazon.com/apprunner/
2. **Click service:** `oru-transcript-formatter`
3. **Configuration → Edit**
4. **Health check settings:**
   - **Path:** Change from `/` to `/api`
   - **Timeout:** Keep 5 seconds (it's fine)
   - **Interval:** 10 seconds (keep current)
5. **Save and wait for redeployment**

This ensures health checks use the correct endpoint.

### Solution 2: Check CloudWatch Logs

View logs to see exact timeout point:

1. **AWS Console → CloudWatch → Log groups**
2. **Find:** `/aws/apprunner/oru-transcript-formatter/...`
3. **Check recent logs** around the time you made the request
4. **Look for:**
   - Timeout errors
   - Processing progress
   - Where it fails

Or use CLI:
```bash
aws logs tail /aws/apprunner/oru-transcript-formatter --follow --region us-east-2
```

### Solution 3: Verify Environment Variable

Make sure `ANTHROPIC_API_KEY` is set correctly:

```bash
aws apprunner describe-service \
  --service-arn $(aws apprunner list-services --region us-east-2 --query 'ServiceSummaryList[?ServiceName==`oru-transcript-formatter`].ServiceArn' --output text) \
  --region us-east-2 \
  --query 'Service.SourceConfiguration.AutoDeploymentsEnabled' \
  --output json
```

Check environment variables in App Runner console to confirm the API key is set.

### Solution 4: Test with Smaller Processing

The timeout might be related to processing time. To diagnose:

1. Check if Claude API calls are taking longer than expected
2. Verify rate limiting isn't causing delays
3. Test with a smaller transcript file

### Solution 5: Implement Async Processing (Best for Production)

Since App Runner has timeout limitations, implement async processing:

**Backend changes needed:**
1. POST `/format` → Returns job ID immediately
2. Background worker processes the file
3. GET `/format/{job_id}/status` → Check progress
4. GET `/format/{job_id}/download` → Download when ready

This completely avoids timeout issues.

---

## 📝 Quick Checklist

- [ ] Update health check path from `/` to `/api`
- [ ] Verify `ANTHROPIC_API_KEY` is set in App Runner
- [ ] Check CloudWatch logs for error details
- [ ] Test with smaller file to isolate issue
- [ ] Consider async processing for production

---

## 🔍 Debugging Steps

1. **Check if it's a gateway timeout or application timeout:**
   ```bash
   # Watch logs in real-time
   aws logs tail /aws/apprunner/oru-transcript-formatter --follow --region us-east-2
   ```

2. **Test health check:**
   ```bash
   curl https://pmkdmqvn5v.us-east-2.awsapprunner.com/api
   ```

3. **Test format endpoint with verbose output:**
   ```bash
   curl -v -X POST https://pmkdmqvn5v.us-east-2.awsapprunner.com/format \
     -F "file=@samples/WI0110-2448_-_Last_Days.txt" \
     --max-time 600
   ```

---

## 💡 Note

App Runner's request timeout is not directly configurable through the console. The gateway typically allows up to 5 minutes, but may timeout earlier in some cases. The async processing approach is the most reliable solution for long-running operations.

