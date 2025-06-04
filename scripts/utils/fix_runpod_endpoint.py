#!/usr/bin/env python3
"""
Fix RunPod Endpoint Configuration
Update the existing endpoint to fix the worker issues
"""

import runpod
import os
import requests
import time
from dotenv import load_dotenv

def test_endpoint_simple(endpoint_id, api_key):
    """Simple endpoint test"""
    print(f"🧪 Testing endpoint {endpoint_id}...")
    
    url = f"https://api.runpod.ai/v2/{endpoint_id}"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    try:
        # Submit simple health check
        response = requests.post(
            f"{url}/run", 
            json={"input": {"endpoint": "/health"}}, 
            headers=headers,
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            return False
            
        result = response.json()
        job_id = result.get("id")
        print(f"✅ Job submitted: {job_id}")
        
        # Wait and check status
        time.sleep(10)
        status_response = requests.get(f"{url}/status/{job_id}", headers=headers)
        status = status_response.json()
        
        print(f"📊 Status after 10s: {status.get('status')}")
        
        if status.get("status") == "COMPLETED":
            print(f"🎉 SUCCESS! Output: {status.get('output', {})}")
            return True
        elif status.get("status") == "IN_QUEUE":
            print("⏳ Still in queue - worker initialization issue")
            return False
        else:
            print(f"❓ Status: {status}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    print("🔧 RunPod A2 STT Endpoint Fix")
    print("=" * 40)
    
    # Load environment
    load_dotenv()
    api_key = os.getenv("RUNPOD_API_KEY")
    if not api_key:
        print("❌ No API key found")
        return
    
    runpod.api_key = api_key
    
    # Current problematic endpoint
    old_endpoint_id = "v2lq88dd8re3ge"
    
    print(f"🔍 Current endpoint {old_endpoint_id} has issues:")
    print("- Min workers: 0 (cold start problems)")
    print("- Idle timeout: 5s (too short)")
    print("- Workers not initializing properly")
    
    try:
        print(f"\n📦 Creating new template with fixed configuration...")
        
        # Create a properly configured template
        template = runpod.create_template(
            name="a2-stt-fixed-template",
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
        
        print(f"\n📡 Creating fixed endpoint...")
        
        # Create endpoint with better configuration
        endpoint = runpod.create_endpoint(
            name="a2-stt-fixed",
            template_id=template["id"],
            gpu_ids="NVIDIA RTX A5000,NVIDIA RTX A6000,NVIDIA GeForce RTX 4090",  # A5000 first (more stable)
            workers_min=1,  # Always keep 1 worker running
            workers_max=2,  # Max 2 for testing
            idle_timeout=60,  # 1 minute timeout
            scaler_type="QUEUE_DELAY",
            scaler_value=1,  # Scale immediately when queue builds
        )
        
        print(f"✅ Fixed endpoint created!")
        print(f"🆔 New Endpoint ID: {endpoint['id']}")
        print(f"📝 Name: {endpoint['name']}")
        
        print(f"\n🔧 Fixed Configuration:")
        print(f"✅ Min workers: 1 (always warm)")
        print(f"✅ Idle timeout: 60s (keeps workers alive)")
        print(f"✅ GPU priority: A5000 first (more stable)")
        print(f"✅ Scale value: 1s (immediate scaling)")
        
        # Save new endpoint info
        with open("runpod_fixed_endpoint.txt", "w") as f:
            f.write(f"A2 STT Fixed RunPod Endpoint\n")
            f.write(f"===========================\n\n")
            f.write(f"NEW Endpoint ID: {endpoint['id']}\n")
            f.write(f"OLD Endpoint ID: {old_endpoint_id} (problematic)\n")
            f.write(f"Template ID: {template['id']}\n")
            f.write(f"Endpoint URL: https://api.runpod.ai/v2/{endpoint['id']}\n\n")
            f.write(f"Fixed Configuration:\n")
            f.write(f"- Workers: 1-2 (always has 1 warm worker)\n")
            f.write(f"- Idle Timeout: 60 seconds\n")
            f.write(f"- GPU Priority: RTX A5000, A6000, 4090\n")
            f.write(f"- Scale Value: 1 second\n\n")
            f.write(f"Test Command:\n")
            f.write(f"curl -X POST https://api.runpod.ai/v2/{endpoint['id']}/run \\\n")
            f.write(f"  -H 'Authorization: Bearer {api_key}' \\\n")
            f.write(f"  -H 'Content-Type: application/json' \\\n")
            f.write(f"  -d '{{\"input\": {{\"endpoint\": \"/health\"}}}}'\n\n")
            f.write(f"Frontend Update:\n")
            f.write(f"Update .env.local:\n")
            f.write(f"VITE_RUNPOD_ENDPOINT_ID={endpoint['id']}\n")
        
        print(f"\n📄 Details saved to: runpod_fixed_endpoint.txt")
        
        # Wait for endpoint to initialize
        print(f"\n⏳ Waiting 45 seconds for endpoint to initialize...")
        time.sleep(45)
        
        # Test the new endpoint
        success = test_endpoint_simple(endpoint['id'], api_key)
        
        if success:
            print(f"\n🎉 ENDPOINT FIXED!")
            print(f"✅ New endpoint is working correctly")
            print(f"🔗 New URL: https://api.runpod.ai/v2/{endpoint['id']}")
            print(f"\n📝 Next steps:")
            print(f"1. Update frontend .env.local:")
            print(f"   VITE_RUNPOD_ENDPOINT_ID={endpoint['id']}")
            print(f"2. Test audio processing with frontend")
            print(f"3. Old endpoint {old_endpoint_id} can be deleted")
        else:
            print(f"\n⚠️  Endpoint created but needs more time to initialize")
            print(f"💡 Try testing again in 2-3 minutes")
            print(f"🔗 New URL: https://api.runpod.ai/v2/{endpoint['id']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
