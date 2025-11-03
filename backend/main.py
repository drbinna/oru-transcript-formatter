from fastapi import FastAPI, UploadFile, File, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from formatter import format_transcript
import os
from dotenv import load_dotenv
import asyncio
import uuid
from datetime import datetime
from typing import Dict, Optional
from enum import Enum

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="ORU Transcript Formatter")

# Serialize formatting requests to reduce rate/egress spikes in hosted envs
format_semaphore = asyncio.Semaphore(1)

# Job storage (in-memory, could be upgraded to Redis/database for production)
class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

jobs: Dict[str, dict] = {}

async def process_job(job_id: str, text: str):
    """Background task to process transcript formatting"""
    try:
        jobs[job_id]["status"] = JobStatus.PROCESSING
        jobs[job_id]["started_at"] = datetime.utcnow().isoformat()
        
        # Process the transcript (this takes 3-4 minutes)
        async with format_semaphore:
            # Run in thread pool since format_transcript is synchronous
            loop = asyncio.get_event_loop()
            docx_bytes = await loop.run_in_executor(None, format_transcript, text)
        
        # Store the result
        jobs[job_id]["status"] = JobStatus.COMPLETED
        jobs[job_id]["docx_bytes"] = docx_bytes
        jobs[job_id]["completed_at"] = datetime.utcnow().isoformat()
        
    except Exception as e:
        jobs[job_id]["status"] = JobStatus.FAILED
        jobs[job_id]["error"] = str(e)
        jobs[job_id]["failed_at"] = datetime.utcnow().isoformat()
        print(f"Job {job_id} failed: {e}")

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/format")
async def format_transcript_endpoint(file: UploadFile = File(...)):
    """
    Accepts a raw transcript text file and returns a job ID immediately.
    Processing happens in the background. Use /format/{job_id}/status to check progress.
    """
    # Read the uploaded file content
    content = await file.read()
    text = content.decode('utf-8')
    
    # Create a new job
    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        "status": JobStatus.PENDING,
        "created_at": datetime.utcnow().isoformat(),
        "filename": file.filename or "transcript.txt"
    }
    
    # Start background processing
    asyncio.create_task(process_job(job_id, text))
    
    # Return job ID immediately
    return {
        "job_id": job_id,
        "status": JobStatus.PENDING,
        "message": "Processing started. Use /format/{job_id}/status to check progress.",
        "status_url": f"/format/{job_id}/status",
        "download_url": f"/format/{job_id}/download"
    }

@app.get("/format/{job_id}/status")
async def get_job_status(job_id: str):
    """Get the status of a formatting job"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    response = {
        "job_id": job_id,
        "status": job["status"],
        "created_at": job["created_at"]
    }
    
    if "started_at" in job:
        response["started_at"] = job["started_at"]
    if "completed_at" in job:
        response["completed_at"] = job["completed_at"]
    if "failed_at" in job:
        response["failed_at"] = job["failed_at"]
        response["error"] = job.get("error", "Unknown error")
    
    return response

@app.get("/format/{job_id}/download")
async def download_formatted_transcript(job_id: str):
    """Download the formatted transcript when job is completed"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    
    if job["status"] == JobStatus.FAILED:
        raise HTTPException(status_code=400, detail=f"Job failed: {job.get('error', 'Unknown error')}")
    
    if job["status"] != JobStatus.COMPLETED:
        raise HTTPException(status_code=202, detail=f"Job is still {job['status']}. Please wait.")
    
    if "docx_bytes" not in job:
        raise HTTPException(status_code=500, detail="Job completed but file not found")
    
    # Return as downloadable .docx
    filename = job.get("filename", "transcript.txt").replace(".txt", "") + "_formatted.docx"
    
    return Response(
        content=job["docx_bytes"],
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@app.get("/api")
async def api_info():
    return {"message": "ORU Transcript Formatting API", "version": "1.0"}

@app.get("/debug/template")
async def debug_template():
    """Debug endpoint to check template file location"""
    import os
    from formatter import get_template_path
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(current_dir)
    
    info = {
        "current_dir": current_dir,
        "root_dir": root_dir,
        "working_dir": os.getcwd(),
        "file_loc": __file__,
        "templates_dir_exists": os.path.exists(os.path.join(root_dir, 'templates')),
    }
    
    # Try to get template path
    try:
        template_path = get_template_path()
        info["template_path"] = template_path
        info["template_exists"] = os.path.exists(template_path)
    except Exception as e:
        info["error"] = str(e)
    
    return info

# Mount static files at the end - this will serve index.html and all assets
static_dir = os.path.join(os.path.dirname(__file__), "../frontend/dist")
if os.path.exists(static_dir):
    # Mount the dist folder - html=True will serve index.html for /
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

