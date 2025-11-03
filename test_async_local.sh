#!/bin/bash
# Test script for async processing endpoints

echo "🧪 Testing Async Processing Endpoints"
echo "======================================"
echo ""

# Step 1: Submit job
echo "📤 Step 1: Submitting transcript for formatting..."
RESPONSE=$(curl -s -X POST http://localhost:8000/format \
  -F "file=@samples/WI0110-2448_-_Last_Days.txt")

JOB_ID=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['job_id'])")

if [ -z "$JOB_ID" ]; then
    echo "❌ Failed to get job ID"
    exit 1
fi

echo "✅ Job submitted successfully!"
echo "   Job ID: $JOB_ID"
echo ""

# Step 2: Poll for status
echo "🔄 Step 2: Polling for job status (this may take 3-4 minutes)..."
echo ""

STATUS="pending"
ATTEMPTS=0
MAX_ATTEMPTS=120  # 120 attempts * 3 seconds = 6 minutes max

while [ "$STATUS" != "completed" ] && [ "$STATUS" != "failed" ] && [ $ATTEMPTS -lt $MAX_ATTEMPTS ]; do
    sleep 3
    ATTEMPTS=$((ATTEMPTS + 1))
    
    STATUS_RESPONSE=$(curl -s "http://localhost:8000/format/$JOB_ID/status")
    STATUS=$(echo $STATUS_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['status'])" 2>/dev/null)
    
    if [ -z "$STATUS" ]; then
        echo "❌ Failed to get status"
        break
    fi
    
    # Show progress every 10 attempts (30 seconds)
    if [ $((ATTEMPTS % 10)) -eq 0 ]; then
        echo "   Status: $STATUS (checking for ${ATTEMPTS} attempts / ~$((ATTEMPTS * 3)) seconds)"
    fi
    
    if [ "$STATUS" == "failed" ]; then
        ERROR=$(echo $STATUS_RESPONSE | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('error', 'Unknown error'))" 2>/dev/null)
        echo "❌ Job failed: $ERROR"
        exit 1
    fi
done

if [ "$STATUS" != "completed" ]; then
    echo "❌ Timeout waiting for job completion"
    echo "   Final status: $STATUS"
    exit 1
fi

echo ""
echo "✅ Job completed successfully!"
echo ""

# Step 3: Download the file
echo "📥 Step 3: Downloading formatted document..."
curl -s "http://localhost:8000/format/$JOB_ID/download" \
  --output test_async_output.docx

if [ -f "test_async_output.docx" ]; then
    FILE_SIZE=$(ls -lh test_async_output.docx | awk '{print $5}')
    echo "✅ File downloaded successfully!"
    echo "   File: test_async_output.docx"
    echo "   Size: $FILE_SIZE"
    
    # Verify it's a valid DOCX
    python3 -c "
from docx import Document
try:
    doc = Document('test_async_output.docx')
    print(f'   ✅ Valid DOCX: {len(doc.paragraphs)} paragraphs')
except Exception as e:
    print(f'   ⚠️  Warning: {e}')
"
else
    echo "❌ Failed to download file"
    exit 1
fi

echo ""
echo "🎉 Async processing test completed successfully!"
echo ""
echo "Summary:"
echo "  - Job submitted immediately"
echo "  - Status polled until completion"
echo "  - File downloaded successfully"
echo ""

