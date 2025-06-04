#!/usr/bin/env python3
"""
Cleanup and Fix RunPod
Delete old endpoints to free quota, then create a properly configured one
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
        
        # Wait and check status multiple times
        for i in range(6):  # Check for 90 seconds
            time.sleep(15)
            status_response = requests.get(f"{url}/status/{job_id}", headers=headers)
            status = status_response.json()
            
            print(f"📊 Status after {(i+1)*15}s: {status.get('status')}")
            
            if status.get("status") == "COMPLETED":
                print(f"🎉 SUCCESS! Output: {status.get('output', {})}")
                return True
            elif status.get("status") in ["FAILED", "CANCELLED", "TIMED_OUT"]:
                print(f"❌ Job failed: {status}")
                return False
        
        print("⏰ Test timed out after 90 seconds")
        return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    print("🧹 RunPod A2 STT Cleanup and Fix")
    print("=" * 40)
    
    # Load environment
    load_dotenv()
    api_key = os.getenv("RUNPOD_API_KEY")
    if not api_key:
        print("❌ No API key found")
        return
    
    runpod.api_key = api_key
    
    try:
        # List all endpoints
        print("📋 Listing all endpoints...")
        endpoints = runpod.get_endpoints()
        
        print(f"Found {len(endpoints)} endpoints:")
        for endpoint in endpoints:
            print(f"- {endpoint['id']}: {endpoint['name']} (workers: {endpoint.get('workersMin', 0)}-{endpoint.get('workersMax', 0)})")
        
        # Calculate current quota usage
        total_max_workers = sum(endpoint.get('workersMax', 0) for endpoint in endpoints)
        print(f"\n📊 Current quota usage: {total_max_workers}/5 max workers")
        
        # Find the problematic endpoint
        current_endpoint_id = "v2lq88dd8re3ge"
        current_endpoint = None
        
        for endpoint in endpoints:
            if endpoint['id'] == current_endpoint_id:
                current_endpoint = endpoint
                break
        
        if not current_endpoint:
            print(f"❌ Current endpoint {current_endpoint_id} not found")
            return
        
        print(f"\n🔍 Current problematic endpoint:")
        print(f"ID: {current_endpoint['id']}")
        print(f"Name: {current_endpoint['name']}")
        print(f"Workers: {current_endpoint.get('workersMin', 0)}-{current_endpoint.get('workersMax', 0)}")
        
        # Delete the problematic endpoint to free up quota
        print(f"\n🗑️  Deleting problematic endpoint to free quota...")
        runpod.delete_endpoint(current_endpoint_id)
        print(f"✅ Deleted endpoint {current_endpoint_id}")
        
        # Wait a moment for deletion to process
        time.sleep(5)
        
        print(f"\n📦 Creating new properly configured endpoint...")
        
        # Create a new template (reuse existing one if possible)
        template_id = "ok3g1h2cvh"  # From previous attempt
        
        # Create new endpoint with proper configuration
        endpoint = runpod.create_endpoint(
            name="a2-stt-working",
            template_id=template_id,
            gpu_ids="NVIDIA RTX A5000,NVIDIA RTX A6000,NVIDIA GeForce RTX 4090",
            workers_min=1,  # Always keep 1 worker running
            workers_max=2,  # Max 2 workers
            idle_timeout=120,  # 2 minute timeout
            scaler_type="QUEUE_DELAY",
            scaler_value=1,  # Scale immediately
        )
        
        print(f"✅ New endpoint created!")
        print(f"🆔 New Endpoint ID: {endpoint['id']}")
        print(f"📝 Name: {endpoint['name']}")
        
        print(f"\n🔧 Proper Configuration:")
        print(f"✅ Min workers: 1 (always warm)")
        print(f"✅ Max workers: 2 (fits quota)")
        print(f"✅ Idle timeout: 120s (keeps workers alive)")
        print(f"✅ GPU priority: A5000 first (most stable)")
        print(f"✅ Scale value: 1s (immediate scaling)")
        
        # Save new endpoint info
        with open("runpod_working_endpoint.txt", "w") as f:
            f.write(f"A2 STT Working RunPod Endpoint\n")
            f.write(f"=============================\n\n")
            f.write(f"NEW Endpoint ID: {endpoint['id']}\n")
            f.write(f"OLD Endpoint ID: {current_endpoint_id} (deleted)\n")
            f.write(f"Template ID: {template_id}\n")
            f.write(f"Endpoint URL: https://api.runpod.ai/v2/{endpoint['id']}\n\n")
            f.write(f"Working Configuration:\n")
            f.write(f"- Workers: 1-2 (always has 1 warm worker)\n")
            f.write(f"- Idle Timeout: 120 seconds\n")
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
        
        print(f"\n📄 Details saved to: runpod_working_endpoint.txt")
        
        # Wait for endpoint to initialize
        print(f"\n⏳ Waiting 60 seconds for endpoint to fully initialize...")
        time.sleep(60)
        
        # Test the new endpoint
        success = test_endpoint_simple(endpoint['id'], api_key)
        
        if success:
            print(f"\n🎉 RUNPOD FIXED!")
            print(f"✅ New endpoint is working correctly")
            print(f"🔗 New URL: https://api.runpod.ai/v2/{endpoint['id']}")
            print(f"\n📝 CRITICAL: Update frontend .env.local:")
            print(f"   VITE_RUNPOD_ENDPOINT_ID={endpoint['id']}")
            print(f"\n🚀 Ready for frontend testing!")
        else:
            print(f"\n⚠️  Endpoint created but may need more initialization time")
            print(f"💡 Workers are starting up - try again in 2-3 minutes")
            print(f"🔗 New URL: https://api.runpod.ai/v2/{endpoint['id']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
