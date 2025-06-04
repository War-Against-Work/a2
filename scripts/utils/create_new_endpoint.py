#!/usr/bin/env python3
"""
Create New RunPod Endpoint and Wait for Proper Initialization
"""

import runpod
import os
import time
from dotenv import load_dotenv

def main():
    print("🚀 Creating New A2 STT RunPod Endpoint")
    print("=" * 50)
    
    # Load environment
    load_dotenv()
    api_key = os.getenv("RUNPOD_API_KEY")
    if not api_key:
        print("❌ No API key found")
        return
    
    runpod.api_key = api_key
    
    try:
        print("📦 Step 1: Creating template...")
        
        # Create a fresh template
        template = runpod.create_template(
            name="a2-stt-fresh-template",
            image_name="aaronlax/a2-stt-api:latest",
            is_serverless=True,
            container_disk_in_gb=20,
            volume_in_gb=0,
            ports="8000/http",
            env={
                "CUDA_VISIBLE_DEVICES": "0",
                "PYTHONUNBUFFERED": "1",
                "RUNPOD_SERVERLESS": "true"
            }
        )
        
        print(f"✅ Template created: {template['id']}")
        
        print("\n📡 Step 2: Creating serverless endpoint...")
        
        # Create endpoint with conservative settings
        endpoint = runpod.create_endpoint(
            name="a2-stt-fresh",
            template_id=template["id"],
            gpu_ids="NVIDIA RTX A5000,NVIDIA RTX A6000,NVIDIA GeForce RTX 4090",
            workers_min=1,  # Keep 1 worker always running
            workers_max=2,  # Conservative max
            idle_timeout=300,  # 5 minutes - long timeout
            scaler_type="QUEUE_DELAY",
            scaler_value=2,  # Scale when queue delay > 2 seconds
        )
        
        print(f"✅ Endpoint created successfully!")
        print(f"🆔 Endpoint ID: {endpoint['id']}")
        print(f"📝 Endpoint name: {endpoint['name']}")
        
        # Save endpoint info
        with open("runpod_fresh_endpoint.txt", "w") as f:
            f.write(f"A2 STT Fresh RunPod Endpoint\n")
            f.write(f"===========================\n\n")
            f.write(f"Endpoint ID: {endpoint['id']}\n")
            f.write(f"Template ID: {template['id']}\n")
            f.write(f"Endpoint URL: https://api.runpod.ai/v2/{endpoint['id']}\n")
            f.write(f"API Key: {api_key}\n\n")
            f.write(f"Configuration:\n")
            f.write(f"- Workers: 1-2 (1 always running)\n")
            f.write(f"- Idle Timeout: 300 seconds (5 minutes)\n")
            f.write(f"- GPU Priority: RTX A5000, A6000, 4090\n")
            f.write(f"- Scale Value: 2 seconds\n\n")
            f.write(f"Status: CREATED - Waiting for worker initialization\n\n")
            f.write(f"Next Steps:\n")
            f.write(f"1. Wait 3-5 minutes for workers to initialize\n")
            f.write(f"2. Check RunPod dashboard for worker status\n")
            f.write(f"3. Only then send test jobs\n\n")
            f.write(f"Test Command (ONLY after workers are ready):\n")
            f.write(f"curl -X POST https://api.runpod.ai/v2/{endpoint['id']}/run \\\n")
            f.write(f"  -H 'Authorization: Bearer {api_key}' \\\n")
            f.write(f"  -H 'Content-Type: application/json' \\\n")
            f.write(f"  -d '{{\"input\": {{\"endpoint\": \"/health\"}}}}'\n")
        
        print(f"\n📄 Endpoint details saved to: runpod_fresh_endpoint.txt")
        
        print(f"\n⚠️  IMPORTANT - DO NOT SEND JOBS YET!")
        print(f"🔄 Workers are now initializing...")
        print(f"⏳ This process takes 3-5 minutes")
        print(f"📊 Check RunPod dashboard to monitor worker status")
        print(f"🎯 Look for 'READY' status before sending jobs")
        
        print(f"\n📋 Next Steps:")
        print(f"1. Go to RunPod Dashboard → Serverless → Endpoints")
        print(f"2. Find endpoint: {endpoint['name']} ({endpoint['id']})")
        print(f"3. Wait for worker status to show 'READY'")
        print(f"4. Only then test with health check")
        print(f"5. If workers show 'READY' but jobs still queue, GPU availability issue")
        
        print(f"\n🔗 RunPod Dashboard: https://www.runpod.io/console/serverless")
        
    except Exception as e:
        print(f"❌ Error creating endpoint: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
