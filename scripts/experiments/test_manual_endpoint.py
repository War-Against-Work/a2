#!/usr/bin/env python3
"""
Test the manually created RunPod endpoint
"""

import requests
import json
import time

def test_endpoint():
    endpoint_id = "4jhkt8m1zttxpm"
    api_key = "rpa_8TZ9Q78NUTXMUYKV87XRQ8J684QD4Q2DHUJXS4SN2hb25y"
    url = f"https://api.runpod.ai/v2/{endpoint_id}/run"
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    
    # Test health check
    print("🔍 Testing health check...")
    payload = {
        "input": {
            "endpoint": "/health"
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        print(f"Response status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'IN_QUEUE':
                job_id = data.get('id')
                print(f"Job queued: {job_id}")
                
                # Poll for result
                status_url = f"https://api.runpod.ai/v2/{endpoint_id}/status/{job_id}"
                
                for i in range(10):
                    print(f"Polling attempt {i+1}...")
                    status_response = requests.get(status_url, headers=headers)
                    status_data = status_response.json()
                    print(f"Status: {status_data}")
                    
                    if status_data.get('status') == 'COMPLETED':
                        print("✅ Health check completed!")
                        break
                    elif status_data.get('status') == 'FAILED':
                        print("❌ Health check failed!")
                        break
                    
                    time.sleep(3)
                else:
                    print("⏰ Health check timed out")
            else:
                print("✅ Immediate response received")
        else:
            print(f"❌ Request failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_endpoint()
