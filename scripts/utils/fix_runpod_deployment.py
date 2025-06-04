#!/usr/bin/env python3
"""
A2 STT RunPod Fix Deployment Script
Creates a new endpoint with stable worker configuration to fix the IN_QUEUE issue
"""

import os
import runpod
import requests
import time
from dotenv import load_dotenv

def test_endpoint(endpoint_id, api_key, max_attempts=5):
    """Test the endpoint with health checks"""
    print(f"\n🧪 Testing endpoint {endpoint_id}...")
    
    url = f"https://api.runpod.ai/v2/{endpoint_id}"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    for attempt in range(max_attempts):
        print(f"Attempt {attempt + 1}/{max_attempts}: Submitting health check...")
        
        try:
            # Submit health check
            response = requests.post(
                f"{url}/run", 
                json={"input": {"endpoint": "/health"}}, 
                headers=headers,
                timeout=10
            )
            
            if response.status_code != 200:
                print(f"❌ HTTP {response.status_code}: {response.text}")
                continue
                
            result = response.json()
            job_id = result.get("id")
            
            if not job_id:
                print(f"❌ No job ID in response: {result}")
                continue
                
            print(f"✅ Job submitted: {job_id}")
            
            # Poll for result
            for poll_attempt in range(20):  # 60 seconds max
                time.sleep(3)
                status_response = requests.get(f"{url}/status/{job_id}", headers=headers)
                status = status_response.json()
                
                print(f"  Poll {poll_attempt + 1}/20: {status.get('status', 'unknown')}")
                
                if status.get("status") == "COMPLETED":
                    print(f"🎉 SUCCESS! Output: {status.get('output', {})}")
                    return True
                elif status.get("status") in ["FAILED", "CANCELLED", "TIMED_OUT"]:
                    print(f"❌ Job failed: {status}")
                    break
                elif status.get("status") != "IN_QUEUE" and status.get("status") != "IN_PROGRESS":
                    print(f"❓ Unexpected status: {status}")
                    break
            
            print(f"⏰ Attempt {attempt + 1} timed out")
            
        except Exception as e:
            print(f"❌ Attempt {attempt + 1} error: {e}")
        
        if attempt < max_attempts - 1:
            print("⏳ Waiting 10 seconds before next attempt...")
            time.sleep(10)
    
    return False

def main():
    print("🔧 A2 STT RunPod Fix Deployment")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Get API key
    api_key = os.getenv("RUNPOD_API_KEY")
    if not api_key:
        print("❌ Error: RUNPOD_API_KEY not found in environment")
        return
    
    # Set the API key
    runpod.api_key = api_key
    
    try:
        print("📦 Creating new template with stable configuration...")
        
        # Create a new template with better configuration
        template = runpod.create_template(
            name="a2-stt-stable-template",
            image_name="aaronlax/a2-stt-api:latest",
            is_serverless=True,
            container_disk_in_gb=25,  # Increased disk space
            volume_in_gb=0,
            ports="8000/http",
            env={
                "CUDA_VISIBLE_DEVICES": "0",
                "PYTHONUNBUFFERED": "1",
                "RUNPOD_SERVERLESS": "true",
                "TORCH_CUDA_ARCH_LIST": "7.5;8.0;8.6;8.9",  # Better GPU compatibility
                "NVIDIA_VISIBLE_DEVICES": "all"
            }
        )
        
        print(f"✅ Template created: {template['id']}")
        
        print("\n📡 Creating stable serverless endpoint...")
        
        # Create endpoint with more stable configuration
        endpoint = runpod.create_endpoint(
            name="a2-stt-stable",
            template_id=template["id"],
            gpu_ids="NVIDIA RTX A5000,NVIDIA RTX A6000,NVIDIA GeForce RTX 4090",  # Reordered for stability
            workers_min=1,  # Keep 1 worker always running to avoid cold starts
            workers_max=3,  # Allow more workers for better scaling
            idle_timeout=30,  # Longer timeout to keep workers warm
            scaler_type="QUEUE_DELAY",
            scaler_value=2,  # Scale faster
        )
        
        print(f"✅ Stable endpoint created!")
        print(f"🆔 Endpoint ID: {endpoint['id']}")
        print(f"📝 Endpoint name: {endpoint['name']}")
        
        print(f"\n🔧 Configuration Changes:")
        print(f"✅ Min workers: 1 (was 0) - eliminates cold start issues")
        print(f"✅ Idle timeout: 30s (was 5s) - keeps workers warm longer")
        print(f"✅ Disk space: 25GB (was 20GB) - more room for models")
        print(f"✅ GPU order: A5000 first - more stable GPU type")
        print(f"✅ Scale value: 2s (was 3s) - faster scaling")
        
        # Save endpoint info
        with open("runpod_stable_endpoint.txt", "w") as f:
            f.write(f"A2 STT Stable RunPod Endpoint\n")
            f.write(f"============================\n\n")
            f.write(f"Endpoint ID: {endpoint['id']}\n")
            f.write(f"Template ID: {template['id']}\n")
            f.write(f"Endpoint URL: https://api.runpod.ai/v2/{endpoint['id']}\n")
            f.write(f"API Key: {api_key}\n\n")
            f.write(f"Configuration:\n")
            f.write(f"- Workers: 1-3 (always has 1 warm worker)\n")
            f.write(f"- Idle Timeout: 30 seconds\n")
            f.write(f"- GPU: RTX A5000, A6000, 4090\n")
            f.write(f"- Disk: 25GB\n\n")
            f.write(f"Test Command:\n")
            f.write(f"curl -X POST https://api.runpod.ai/v2/{endpoint['id']}/run \\\n")
            f.write(f"  -H 'Authorization: Bearer {api_key}' \\\n")
            f.write(f"  -H 'Content-Type: application/json' \\\n")
            f.write(f"  -d '{{\"input\": {{\"endpoint\": \"/health\"}}}}'\n")
        
        print(f"\n📄 Endpoint details saved to: runpod_stable_endpoint.txt")
        
        # Wait for endpoint to initialize
        print(f"\n⏳ Waiting 30 seconds for endpoint to initialize...")
        time.sleep(30)
        
        # Test the new endpoint
        success = test_endpoint(endpoint['id'], api_key)
        
        if success:
            print(f"\n🎉 DEPLOYMENT SUCCESSFUL!")
            print(f"✅ New stable endpoint is working correctly")
            print(f"🔗 Endpoint URL: https://api.runpod.ai/v2/{endpoint['id']}")
            print(f"\n💡 Next steps:")
            print(f"1. Update frontend .env.local with new endpoint ID")
            print(f"2. Test audio processing with the frontend")
            print(f"3. Monitor costs (1 worker always running)")
        else:
            print(f"\n⚠️  Endpoint created but still having issues")
            print(f"📋 Check RunPod dashboard for worker logs")
            print(f"🔗 Dashboard: https://www.runpod.io/console/serverless")
        
    except Exception as e:
        print(f"❌ Error during deployment: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
