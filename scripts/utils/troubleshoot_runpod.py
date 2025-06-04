#!/usr/bin/env python3
"""
RunPod A2 STT API Troubleshooting Script
Systematically diagnose and fix the stuck endpoint issue
"""

import requests
import time
import json
from datetime import datetime

# Configuration
ENDPOINT_URL = "https://api.runpod.ai/v2/v2lq88dd8re3ge"
API_KEY = "rpa_8TZ9Q78NUTXMUYKV87XRQ8J684QD4Q2DHUJXS4SN2hb25y"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

def log(message):
    """Log with timestamp"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

def check_job_status(job_id):
    """Check status of a specific job"""
    try:
        response = requests.get(f"{ENDPOINT_URL}/status/{job_id}", headers=HEADERS)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def submit_health_check():
    """Submit a health check job"""
    try:
        response = requests.post(
            f"{ENDPOINT_URL}/run", 
            json={"input": {"endpoint": "/health"}}, 
            headers=HEADERS
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def submit_simple_job():
    """Submit a very simple job to test basic functionality"""
    try:
        response = requests.post(
            f"{ENDPOINT_URL}/run", 
            json={"input": {"test": "simple"}}, 
            headers=HEADERS
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def main():
    log("🔍 Starting RunPod A2 STT API Troubleshooting")
    log(f"Endpoint: {ENDPOINT_URL}")
    
    # Step 1: Check existing stuck job
    log("\n📋 Step 1: Checking existing stuck job")
    stuck_job_id = "f6cae666-8ae6-4476-a204-5ec7cf2dee06-u2"
    status = check_job_status(stuck_job_id)
    log(f"Stuck job {stuck_job_id}: {status}")
    
    # Step 2: Submit new health check
    log("\n🏥 Step 2: Submitting new health check")
    health_result = submit_health_check()
    log(f"Health check submission: {health_result}")
    
    if "id" in health_result:
        job_id = health_result["id"]
        log(f"New job ID: {job_id}")
        
        # Poll for 60 seconds
        log("⏱️  Polling for 60 seconds...")
        for i in range(20):  # 20 attempts, 3 seconds each
            time.sleep(3)
            status = check_job_status(job_id)
            log(f"Attempt {i+1}/20: {status}")
            
            if status.get("status") not in ["IN_QUEUE", "IN_PROGRESS"]:
                log(f"✅ Job completed with status: {status.get('status')}")
                if "output" in status:
                    log(f"Output: {status['output']}")
                break
        else:
            log("⚠️  Job still not completed after 60 seconds")
    
    # Step 3: Try simple job
    log("\n🧪 Step 3: Trying simple job")
    simple_result = submit_simple_job()
    log(f"Simple job submission: {simple_result}")
    
    if "id" in simple_result:
        job_id = simple_result["id"]
        time.sleep(5)
        status = check_job_status(job_id)
        log(f"Simple job status: {status}")
    
    # Step 4: Recommendations
    log("\n💡 Step 4: Recommendations")
    log("Based on the results above:")
    log("- If jobs are stuck in IN_QUEUE: Worker initialization issue")
    log("- If jobs fail immediately: Docker image or template issue")
    log("- If no response: Endpoint configuration issue")
    log("\nNext steps:")
    log("1. Check RunPod dashboard for worker logs")
    log("2. Consider redeploying with different configuration")
    log("3. Try local API fallback for immediate testing")

if __name__ == "__main__":
    main()
