# 🔧 Fix: App Runner Validation Error - Image URI Format

## ❌ The Error

The error shows:
```
Validation error: '860639121362.dkr.ecr.us-east-2.amazonaws.com/oru-transcript-formatter:latest'
failed to satisfy constraint: Member must satisfy regular expression pattern
```

**Issue:** App Runner doesn't accept the tag (`:latest`) in the image URI field when using ECR. You need to use **separate fields** for repository and tag.

## ✅ The Solution

### Use App Runner's Dropdown Fields (Recommended)

When configuring your App Runner service:

1. **In "Container image URI" section:**
   - **DO NOT** paste the full URI with `:latest`
   - **DO NOT** type `860639121362.dkr.ecr.us-east-2.amazonaws.com/oru-transcript-formatter:latest`

2. **Instead, use the dropdown menus:**
   - **Repository dropdown:** Select or paste: `oru-transcript-formatter`
   - **Image tag dropdown:** Select: `latest`
   - Let App Runner combine them automatically

3. **OR enter repository URI without tag:**
   - Repository URI: `860639121362.dkr.ecr.us-east-2.amazonaws.com/oru-transcript-formatter`
   - **Leave off the `:latest` part**
   - Then select tag separately

### Step-by-Step in App Runner Console

1. **Go to:** https://console.aws.amazon.com/apprunner/
2. **Click your service** (or create new)
3. **Edit Configuration** → **Source configuration**
4. **Container registry** section:

   **Option A - Use Dropdowns (Easiest):**
   - **Repository:** Select `oru-transcript-formatter` from ECR dropdown
   - **Image tag:** Select `latest` from tag dropdown
   
   **Option B - Manual Entry:**
   - **Container image URI field:**
     - Enter ONLY: `860639121362.dkr.ecr.us-east-2.amazonaws.com/oru-transcript-formatter`
     - **Do NOT include `:latest`**
   - **Image tag field** (if separate): Enter `latest`

5. **Save changes**

---

## 🔍 Understanding the Format

App Runner expects ECR images in this format:
- **Repository URI:** `account.dkr.ecr.region.amazonaws.com/repository-name`
- **Tag:** Separate field or selected from dropdown

**NOT:** `repository-uri:tag` in a single field

---

## 📝 Alternative: Use Image Digest Instead of Tag

If you continue having issues with tags, you can use the image digest:

1. **Get the image digest:**
   ```bash
   aws ecr describe-images \
     --repository-name oru-transcript-formatter \
     --region us-east-2 \
     --image-ids imageTag=latest \
     --query 'imageDetails[0].imageDigest' \
     --output text
   ```

2. **Use in App Runner:**
   - Repository: `860639121362.dkr.ecr.us-east-2.amazonaws.com/oru-transcript-formatter`
   - Image identifier: `sha256:xxxxx` (the digest you got)

---

## ✅ Quick Fix Checklist

- [ ] Don't include `:latest` in the Container image URI field
- [ ] Use repository URI only: `860639121362.dkr.ecr.us-east-2.amazonaws.com/oru-transcript-formatter`
- [ ] Select tag `latest` from dropdown or enter in separate tag field
- [ ] If using dropdowns, let App Runner auto-fill the URI
- [ ] Save and redeploy

---

## 🎯 Correct Configuration

**In App Runner Console:**

```
Source:
  Container registry
  Provider: Amazon ECR
  
  Container image URI: [Use dropdown to select repository]
  OR manually enter: 860639121362.dkr.ecr.us-east-2.amazonaws.com/oru-transcript-formatter
  
  Image tag: latest (from dropdown or manual entry)
```

**Key point:** Tag is separate from URI in App Runner's ECR configuration!

---

After fixing this, your App Runner service should validate and deploy successfully! ✅

