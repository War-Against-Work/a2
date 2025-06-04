#!/usr/bin/env python3
"""
Test the working endpoint that the user manually created
"""

import requests
import time
import os
from dotenv import load_dotenv

def test_working_endpoint():
    print("🧪 Testing User's Working Endpoint")
    print("=" * 40)
    
    # Load environment
    load_dotenv()
    api_key = os.getenv("RUNPOD_API_KEY")
    if not api_key:
        print("❌ No API key found")
        return
    
    # User's working endpoint
    endpoint_id = "ez2hb2e6fqeh54"
    url = f"https://api.runpod.ai/v2/{endpoint_id}/run"
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    
    print(f"🎯 Testing endpoint: {endpoint_id}")
    print(f"🔗 URL: {url}")
    
    # Test with health check for our A2 STT API
    test_payload = {
        "input": {
            "endpoint": "/health"
        }
    }
    
    try:
        print("📤 Sending health check request...")
        response = requests.post(url, json=test_payload, headers=headers, timeout=15)
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            job_id = result.get("id")
            status = result.get("status")
            
            print(f"✅ Job submitted successfully!")
            print(f"🆔 Job ID: {job_id}")
            print(f"📊 Initial Status: {status}")
            
            # Poll for result
            print("⏳ Polling for result...")
            for i in range(8):  # 2 minutes max
                time.sleep(15)
                
                try:
                    status_url = f"https://api.runpod.ai/v2/{endpoint_id}/status/{job_id}"
                    status_response = requests.get(status_url, headers=headers, timeout=10)
                    
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        current_status = status_data.get('status', 'unknown')
                        
                        print(f"📊 Check {i+1}/8 ({(i+1)*15}s): {current_status}")
                        
                        if current_status == "COMPLETED":
                            output = status_data.get('output', {})
                            print(f"🎉 SUCCESS! Output: {output}")
                            
                            # This endpoint works! Save the info
                            with open("working_endpoint_info.txt", "w") as f:
                                f.write(f"WORKING A2 STT RunPod Endpoint\n")
                                f.write(f"=============================\n\n")
                                f.write(f"Endpoint ID: {endpoint_id}\n")
                                f.write(f"Endpoint URL: https://api.runpod.ai/v2/{endpoint_id}\n")
                                f.write(f"Status: ✅ WORKING AND TESTED\n\n")
                                f.write(f"Test Results:\n")
                                f.write(f"- Health check: ✅ PASSED\n")
                                f.write(f"- Response time: {(i+1)*15}s\n")
                                f.write(f"- Output: {output}\n\n")
                                f.write(f"Frontend Configuration:\n")
                                f.write(f"Update .env.local:\n")
                                f.write(f"VITE_RUNPOD_ENDPOINT_ID={endpoint_id}\n")
                            
                            print(f"\n🚀 ENDPOINT IS WORKING!")
                            print(f"📝 Update frontend .env.local:")
                            print(f"   VITE_RUNPOD_ENDPOINT_ID={endpoint_id}")
                            
                            return True
                            
                        elif current_status in ["FAILED", "CANCELLED", "TIMED_OUT"]:
                            print(f"❌ Job failed: {current_status}")
                            if 'error' in status_data:
                                print(f"Error: {status_data['error']}")
                            return False
                            
                    else:
                        print(f"⚠️  Status check failed: {status_response.status_code}")
                        
                except Exception as poll_error:
                    print(f"⚠️  Poll error: {poll_error}")
            
            print("⏰ Test timed out")
            return False
            
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def analyze_differences():
    print(f"\n🔍 Analyzing What Went Wrong With My Approach")
    print("=" * 50)
    
    print(f"✅ User's Working Endpoint:")
    print(f"- Created manually through RunPod dashboard")
    print(f"- 5 workers running on RTX 4090s")
    print(f"- Endpoint ID: ez2hb2e6fqeh54")
    
    print(f"\n❌ My Failed Endpoint:")
    print(f"- Created via Python SDK")
    print(f"- Endpoint ID: qg4svw2rm81sz9")
    print(f"- Stuck in initialization")
    
    print(f"\n💡 Possible Issues with My Approach:")
    print(f"1. Wrong template configuration")
    print(f"2. Incorrect Docker image specification")
    print(f"3. Bad environment variables")
    print(f"4. Wrong GPU selection method")
    print(f"5. SDK vs Dashboard differences")
    
    print(f"\n🔧 Next Steps:")
    print(f"1. Test user's working endpoint")
    print(f"2. Compare configurations")
    print(f"3. Update frontend to use working endpoint")
    print(f"4. Figure out what I did wrong for future reference")

if __name__ == "__main__":
    success = test_working_endpoint()
    analyze_differences()
    
    if success:
        print(f"\n🎉 READY FOR FRONTEND TESTING!")
        print(f"🚀 The working endpoint can now be used for full integration testing")
    else:
        print(f"\n🤔 Need to investigate further...")
