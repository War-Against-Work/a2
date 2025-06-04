#!/usr/bin/env python3
"""
Test the new RunPod endpoint with proper handler
"""

import requests
import json
import os
import time
from dotenv import load_dotenv

def test_endpoint():
    load_dotenv()
    api_key = os.getenv("RUNPOD_API_KEY")
    endpoint_id = "nu4ur5z3en0wie"
    
    url = f"https://api.runpod.ai/v2/{endpoint_id}/run"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Test health check
    print("🏥 Testing health check...")
    health_payload = {
        "input": {
            "endpoint": "/health"
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=health_payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            result = response.json()
            job_id = result.get("id")
            print(f"✅ Job submitted: {job_id}")
            
            # Poll for result
            status_url = f"https://api.runpod.ai/v2/{endpoint_id}/status/{job_id}"
            
            for i in range(30):  # Wait up to 30 seconds
                print(f"⏳ Checking status... ({i+1}/30)")
                status_response = requests.get(status_url, headers=headers)
                status_data = status_response.json()
                
                print(f"Status: {status_data.get('status', 'unknown')}")
                
                if status_data.get("status") == "COMPLETED":
                    print("🎉 SUCCESS! Job completed!")
                    print(f"Output: {status_data.get('output')}")
                    return True
                elif status_data.get("status") == "FAILED":
                    print("❌ Job failed!")
                    print(f"Error: {status_data.get('error')}")
                    return False
                
                time.sleep(2)
            
            print("⏰ Timeout waiting for job completion")
            return False
        else:
            print(f"❌ Failed to submit job: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing endpoint: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing New RunPod Endpoint")
    print("=" * 40)
    print("Endpoint ID: nu4ur5z3en0wie")
    print("This endpoint uses the proper RunPod handler!")
    print()
    
    success = test_endpoint()
    
    if success:
        print("\n🎉 ENDPOINT IS WORKING!")
        print("✅ Jobs are processing correctly")
        print("✅ Ready for frontend integration")
    else:
        print("\n⚠️  Endpoint may still be initializing")
        print("Wait a few more minutes and try again")
