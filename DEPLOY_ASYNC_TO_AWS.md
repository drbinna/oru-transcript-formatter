# 🚀 Deploy Async Version to AWS App Runner

## ✅ Image Pushed Successfully!

**New image tag:** `async-20251102-213113`  
**Full image URI:** `860639121362.dkr.ecr.us-east-2.amazonaws.com/oru-transcript-formatter:async-20251102-213113`

## 📝 Update App Runner Service

Since your ECR repository has **tag immutability** enabled, we pushed with a new tag. Now update your App Runner service:

### Option 1: Update via AWS Console (Recommended)

1. **Go to App Runner Console:**
   - https://console.aws.amazon.com/apprunner/
   - Click on your service: `oru-transcript-formatter`

2. **Update Configuration:**
   - Click **"Configuration"** tab
   - Click **"Edit"** button
   - Scroll to **"Source configuration"**

3. **Update Image:**
   - **Container registry** → Select **Amazon ECR**
   - **Image repository:** `oru-transcript-formatter`
   - **Image tag:** Select or enter: `async-20251102-213113`
     - *This is the new tag with async processing*

4. **Save and Deploy:**
   - Click **"Save changes"**
   - App Runner will automatically redeploy (~5-10 minutes)

### Option 2: Update via AWS CLI

```bash
# Get your service ARN
SERVICE_ARN=$(aws apprunner list-services --region us-east-2 \
  --query 'ServiceSummaryList[?ServiceName==`oru-transcript-formatter`].ServiceArn' \
  --output text)

# Update service configuration
aws apprunner update-service \
  --service-arn "$SERVICE_ARN" \
  --region us-east-2 \
  --source-configuration '{
    "ImageRepository": {
      "ImageIdentifier": "860639121362.dkr.ecr.us-east-2.amazonaws.com/oru-transcript-formatter:async-20251102-213113",
      "ImageRepositoryType": "ECR"
    }
  }'
```

## 🧪 Test After Deployment

Once deployment completes (status shows "Running"):

### Test 1: Submit Job (Should return immediately)
```bash
curl -X POST https://pmkdmqvn5v.us-east-2.awsapprunner.com/format \
  -F "file=@samples/WI0110-2448_-_Last_Days.txt" | python3 -m json.tool
```

**Expected:** Immediate response with `job_id` (no timeout!)

### Test 2: Check Status
```bash
# Replace {job_id} with the job_id from Test 1
curl https://pmkdmqvn5v.us-east-2.awsapprunner.com/format/{job_id}/status | python3 -m json.tool
```

### Test 3: Download When Complete
```bash
curl https://pmkdmqvn5v.us-east-2.awsapprunner.com/format/{job_id}/download \
  --output test_aws_async.docx
```

## ✅ What's New

### Async Processing Features:
- ✅ **POST /format** - Returns job ID immediately (no timeout!)
- ✅ **GET /format/{job_id}/status** - Check processing progress
- ✅ **GET /format/{job_id}/download** - Download when ready

### Benefits:
- 🚀 **No more 2-minute timeout errors**
- 📊 **Real-time status updates**
- ⚡ **Immediate response** to user
- 🔄 **Background processing** (3-4 minutes)

## 📋 Deployment Checklist

- [x] Frontend built with async changes
- [x] Docker image built with async backend
- [x] Image pushed to ECR with tag: `async-20251102-213113`
- [ ] Update App Runner service with new tag
- [ ] Wait for deployment (~5-10 minutes)
- [ ] Test async endpoints

## 🔍 Verify Deployment

After updating App Runner, check the logs:

```bash
aws logs tail /aws/apprunner/oru-transcript-formatter/19bed1ae4b544a31ab42fcbbcd3fc609/application \
  --follow --region us-east-2
```

You should see:
- Job creation logs
- Status endpoint calls
- Background processing

---

## 🎯 Quick Summary

**Image pushed:** ✅ `async-20251102-213113`  
**Next step:** Update App Runner service to use this tag  
**Result:** Async processing will work without timeouts! 🎉

---

**After deployment, your application will handle long-running processing without timeout errors!**

