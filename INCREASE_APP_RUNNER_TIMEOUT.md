# ⏱️ How to Increase App Runner Request Timeout

## Understanding the Timeouts

There are **two different timeouts** in App Runner:

1. **Health Check Timeout** (5 seconds) - ✅ This is fine
   - Used for `/api` health check endpoint
   - Your endpoint responds in 0.16 seconds, so 5 seconds is plenty

2. **Request Timeout** (Default: 300 seconds / 5 minutes) - ❌ This needs to be increased
   - This is what's causing your 504 Gateway Timeout
   - Your processing takes 3-4 minutes, which should work, but gateway timeouts happen earlier

## ✅ Solution: Increase Request Timeout

App Runner doesn't expose request timeout directly in the console, but you can increase it via:

### Option 1: Via AWS Console (If Available)

1. **Go to:** https://console.aws.amazon.com/apprunner/
2. **Click your service:** `oru-transcript-formatter`
3. **Configuration → Edit**
4. **Look for:** "Request timeout", "Connection timeout", or "Timeout" settings
5. **Increase to:** 900 seconds (15 minutes - max allowed)
6. **Save**

**Note:** Some App Runner configurations don't expose this directly. If you don't see it, use Option 2.

### Option 2: Update Service Configuration via AWS CLI

Unfortunately, App Runner's request timeout is **not directly configurable** through the console or CLI. It's typically:
- Default: 300 seconds (5 minutes)
- Maximum: Set by App Runner internally

However, App Runner should handle requests up to 5 minutes. Your issue might be:

1. **Gateway timeout** (happens before request reaches your app)
2. **Application timeout** (happens in your FastAPI app)

### Option 3: Check FastAPI Timeout Settings

Your FastAPI/Uvicorn might have its own timeout. Check `backend/main.py`:

```python
# If using uvicorn.run directly, add timeout:
uvicorn.run(app, host="0.0.0.0", port=8000, timeout_keep_alive=900)
```

### Option 4: Use Async/Background Processing (Best Solution)

Since App Runner has timeout limitations, the best solution is to make processing asynchronous:

1. **POST /format** → Returns job ID immediately
2. **Process in background**
3. **GET /format/{job_id}/status** → Check if ready
4. **GET /format/{job_id}/download** → Download when ready

This avoids timeout issues entirely.

---

## 🔍 Check Current Configuration

Run this to see all your service settings:

```bash
aws apprunner describe-service \
  --service-arn $(aws apprunner list-services --region us-east-2 --query 'ServiceSummaryList[?ServiceName==`oru-transcript-formatter`].ServiceArn' --output text) \
  --region us-east-2 \
  --output json | python3 -m json.tool
```

Look for timeout-related settings in the output.

---

## 📝 Immediate Workaround

While you work on a permanent solution:

1. **Check CloudWatch Logs** to see exact timeout point
2. **Verify ANTHROPIC_API_KEY** is set correctly (long processing might be due to API issues)
3. **Test with smaller file** to see if timeout is file-size related
4. **Consider async processing** for production use

---

## 💡 Recommendation

**Short-term:** The 5-minute limit should work for your 3-4 minute processing, so the timeout might be coming from elsewhere. Check CloudWatch logs.

**Long-term:** Implement async processing pattern for better UX and reliability.

