#!/usr/bin/env python3
"""
Deploy the CORRECT RunPod serverless endpoint with proper handler
"""

import runpod
import os
import subprocess
import time
from dotenv import load_dotenv

def build_and_push_image():
    """Build and push the correct Docker image"""
    print("🐳 Building RunPod serverless Docker image...")
    
    # Build the image with the RunPod handler
    build_cmd = [
        "docker", "build", 
        "-f", "Dockerfile.runpod",
        "-t", "aaronlax/a2-stt-runpod:latest",
        "."
    ]
    
    try:
        result = subprocess.run(build_cmd, check=True, capture_output=True, text=True)
        print("✅ Docker image built successfully")
        
        # Push to registry
        print("📤 Pushing to Docker registry...")
        push_cmd = ["docker", "push", "aaronlax/a2-stt-runpod:latest"]
        subprocess.run(push_cmd, check=True)
        print("✅ Image pushed successfully")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Docker build/push failed: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return False

def create_runpod_endpoint():
    """Create the correct RunPod endpoint"""
    print("🚀 Creating RunPod serverless endpoint...")
    
    # Load environment
    load_dotenv()
    api_key = os.getenv("RUNPOD_API_KEY")
    if not api_key:
        print("❌ No API key found")
        return None
    
    runpod.api_key = api_key
    
    try:
        # Create template with RunPod handler
        print("📦 Creating template...")
        template = runpod.create_template(
            name="a2-stt-runpod-handler",
            image_name="aaronlax/a2-stt-runpod:latest",
            is_serverless=True,
            container_disk_in_gb=20,
            volume_in_gb=0,
            env={
                "CUDA_VISIBLE_DEVICES": "0",
                "PYTHONUNBUFFERED": "1"
            }
        )
        
        print(f"✅ Template created: {template['id']}")
        
        # Create endpoint
        print("📡 Creating endpoint...")
        endpoint = runpod.create_endpoint(
            name="a2-stt-runpod-working",
            template_id=template["id"],
            gpu_ids="NVIDIA RTX A5000,NVIDIA RTX A6000,NVIDIA GeForce RTX 4090",
            workers_min=1,
            workers_max=2,
            idle_timeout=300,  # 5 minutes
            scaler_type="QUEUE_DELAY",
            scaler_value=2,
        )
        
        print(f"✅ Endpoint created: {endpoint['id']}")
        
        # Save endpoint info
        with open("runpod_correct_endpoint.txt", "w") as f:
            f.write(f"CORRECT A2 STT RunPod Endpoint\n")
            f.write(f"==============================\n\n")
            f.write(f"Endpoint ID: {endpoint['id']}\n")
            f.write(f"Template ID: {template['id']}\n")
            f.write(f"Docker Image: aaronlax/a2-stt-runpod:latest\n")
            f.write(f"Endpoint URL: https://api.runpod.ai/v2/{endpoint['id']}\n\n")
            f.write(f"Configuration:\n")
            f.write(f"- Uses RunPod serverless handler (not FastAPI)\n")
            f.write(f"- Workers: 1-2\n")
            f.write(f"- Idle Timeout: 300 seconds\n\n")
            f.write(f"Test Command:\n")
            f.write(f"curl -X POST https://api.runpod.ai/v2/{endpoint['id']}/run \\\n")
            f.write(f"  -H 'Authorization: Bearer {api_key}' \\\n")
            f.write(f"  -H 'Content-Type: application/json' \\\n")
            f.write(f"  -d '{{\"input\": {{\"endpoint\": \"/health\"}}}}'\n")
        
        return endpoint['id']
        
    except Exception as e:
        print(f"❌ Failed to create endpoint: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    print("🔧 Deploying CORRECT RunPod Serverless Endpoint")
    print("=" * 50)
    
    print("🔍 The Issue:")
    print("- Previous endpoints used FastAPI server")
    print("- RunPod serverless needs a handler function")
    print("- Workers were running but couldn't process jobs")
    print("- Need to rebuild with proper RunPod handler")
    
    # Build and push the correct image
    if not build_and_push_image():
        print("❌ Failed to build/push image")
        return
    
    # Create the endpoint
    endpoint_id = create_runpod_endpoint()
    if not endpoint_id:
        print("❌ Failed to create endpoint")
        return
    
    print(f"\n🎉 SUCCESS!")
    print(f"✅ Correct endpoint created: {endpoint_id}")
    print(f"🔗 URL: https://api.runpod.ai/v2/{endpoint_id}")
    
    print(f"\n⏳ IMPORTANT:")
    print(f"- Wait 3-5 minutes for workers to initialize")
    print(f"- This time it should work because we have the proper handler")
    print(f"- Monitor in RunPod dashboard")
    
    print(f"\n📝 Frontend Update:")
    print(f"Update .env.local:")
    print(f"VITE_RUNPOD_ENDPOINT_ID={endpoint_id}")

if __name__ == "__main__":
    main()
