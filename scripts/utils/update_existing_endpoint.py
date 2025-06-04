#!/usr/bin/env python3
"""
Update Existing RunPod Endpoint
Fix the current endpoint configuration instead of creating a new one
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
        time.sleep(15)
        status_response = requests.get(f"{url}/status/{job_id}", headers=headers)
        status = status_response.json()
        
        print(f"📊 Status after 15s: {status.get('status')}")
        
        if status.get("status") == "COMPLETED":
            print(f"🎉 SUCCESS! Output: {status.get('output', {})}")
            return True
        elif status.get("status") == "IN_QUEUE":
            print("⏳ Still in queue - will check again")
            # Try one more time
            time.sleep(15)
            status_response = requests.get(f"{url}/status/{job_id}", headers=headers)
            status = status_response.json()
            print(f"📊 Status after 30s: {status.get('status')}")
            return status.get("status") == "COMPLETED"
        else:
            print(f"❓ Status: {status}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    print("🔧 RunPod A2 STT Endpoint Update")
    print("=" * 40)
    
    # Load environment
    load_dotenv()
    api_key = os.getenv("RUNPOD_API_KEY")
    if not api_key:
        print("❌ No API key found")
        return
    
    runpod.api_key = api_key
    
    # Current endpoint
    endpoint_id = "v2lq88dd8re3ge"
    
    print(f"🔍 Current endpoint {endpoint_id} issues:")
    print("- Min workers: 0 (cold start problems)")
    print("- Idle timeout: 5s (too short)")
    print("- Worker quota limit reached")
    
    try:
        print(f"\n📡 Updating existing endpoint configuration...")
        
        # Update the existing endpoint with better settings
        updated_endpoint = runpod.update_endpoint(
            endpoint_id=endpoint_id,
            workers_min=1,  # Keep 1 worker always running
            workers_max=2,  # Reduce max to fit quota
            idle_timeout=60,  # Increase timeout to 1 minute
            scaler_type="QUEUE_DELAY",
            scaler_value=1,  # Scale immediately
        )
        
        print(f"✅ Endpoint updated successfully!")
        print(f"🆔 Endpoint ID: {endpoint_id}")
        
        print(f"\n🔧 Updated Configuration:")
        print(f"✅ Min workers: 1 (was 0) - eliminates cold starts")
        print(f"✅ Max workers: 2 (was 2) - fits quota")
        print(f"✅ Idle timeout: 60s (was 5s) - keeps workers alive")
        print(f"✅ Scale value: 1s (immediate scaling)")
        
        # Update the endpoint info file
        with open("runpod_endpoint_info.txt", "w") as f:
            f.write(f"A2 STT RunPod Endpoint (UPDATED)\n")
            f.write(f"=================================\n\n")
            f.write(f"Endpoint ID: {endpoint_id}\n")
            f.write(f"Endpoint URL: https://api.runpod.ai/v2/{endpoint_id}\n")
            f.write(f"Status: UPDATED with fixed configuration\n\n")
            f.write(f"Updated Configuration:\n")
            f.write(f"- Workers: 1-2 (always has 1 warm worker)\n")
            f.write(f"- Idle Timeout: 60 seconds (was 5s)\n")
            f.write(f"- Scale Value: 1 second (immediate)\n")
            f.write(f"- GPU: RTX 4090, A6000, A5000\n\n")
            f.write(f"Test Command:\n")
            f.write(f"curl -X POST https://api.runpod.ai/v2/{endpoint_id}/run \\\n")
            f.write(f"  -H 'Authorization: Bearer {api_key}' \\\n")
            f.write(f"  -H 'Content-Type: application/json' \\\n")
            f.write(f"  -d '{{\"input\": {{\"endpoint\": \"/health\"}}}}'\n")
        
        print(f"\n📄 Updated info saved to: runpod_endpoint_info.txt")
        
        # Wait for changes to take effect
        print(f"\n⏳ Waiting 30 seconds for configuration changes to take effect...")
        time.sleep(30)
        
        # Test the updated endpoint
        success = test_endpoint_simple(endpoint_id, api_key)
        
        if success:
            print(f"\n🎉 ENDPOINT FIXED!")
            print(f"✅ Updated endpoint is working correctly")
            print(f"🔗 URL: https://api.runpod.ai/v2/{endpoint_id}")
            print(f"\n📝 Next steps:")
            print(f"1. Frontend should now work with existing endpoint")
            print(f"2. Test audio processing with the frontend")
            print(f"3. Monitor performance and costs")
        else:
            print(f"\n⚠️  Configuration updated but may need more time")
            print(f"💡 The 1 min worker should be initializing now")
            print(f"🔄 Try testing again in 2-3 minutes")
            print(f"📊 Check RunPod dashboard for worker status")
        
    except Exception as e:
        print(f"❌ Error updating endpoint: {e}")
        import traceback
        traceback.print_exc()
        
        print(f"\n🔄 Alternative approach: Restart existing workers")
        print(f"💡 Sometimes restarting the endpoint helps:")
        print(f"1. Go to RunPod dashboard")
        print(f"2. Find endpoint {endpoint_id}")
        print(f"3. Stop and restart workers")
        print(f"4. Or try the manual curl test again")

if __name__ == "__main__":
    main()
