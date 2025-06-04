#!/usr/bin/env python3
"""
Test the existing stable endpoint that was already created
"""

import requests
import time
import os
from dotenv import load_dotenv

def test_endpoint_comprehensive(endpoint_id, api_key):
    """Comprehensive endpoint test"""
    print(f"🧪 Testing stable endpoint {endpoint_id}...")
    
    url = f"https://api.runpod.ai/v2/{endpoint_id}"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    try:
        # Submit health check
        print("📤 Submitting health check...")
        response = requests.post(
            f"{url}/run", 
            json={"input": {"endpoint": "/health"}}, 
            headers=headers,
            timeout=15
        )
        
        if response.status_code != 200:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            return False
            
        result = response.json()
        job_id = result.get("id")
        print(f"✅ Job submitted: {job_id}")
        print(f"📊 Initial status: {result.get('status', 'unknown')}")
        
        # Poll for result with detailed logging
        print("⏳ Polling for result...")
        for i in range(12):  # 3 minutes total
            time.sleep(15)
            
            try:
                status_response = requests.get(f"{url}/status/{job_id}", headers=headers, timeout=10)
                status = status_response.json()
                
                current_status = status.get('status', 'unknown')
                print(f"📊 Check {i+1}/12 ({(i+1)*15}s): {current_status}")
                
                if current_status == "COMPLETED":
                    output = status.get('output', {})
                    print(f"🎉 SUCCESS! Output: {output}")
                    return True
                elif current_status in ["FAILED", "CANCELLED", "TIMED_OUT"]:
                    print(f"❌ Job failed with status: {current_status}")
                    if 'error' in status:
                        print(f"Error details: {status['error']}")
                    return False
                elif current_status == "IN_PROGRESS":
                    print("⚡ Job is processing...")
                elif current_status == "IN_QUEUE":
                    print("⏳ Still in queue...")
                else:
                    print(f"❓ Unexpected status: {status}")
                    
            except Exception as poll_error:
                print(f"⚠️  Poll error: {poll_error}")
        
        print("⏰ Test timed out after 3 minutes")
        return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    print("🔍 Testing A2 STT Stable Endpoint")
    print("=" * 40)
    
    # Load environment
    load_dotenv()
    api_key = os.getenv("RUNPOD_API_KEY")
    if not api_key:
        print("❌ No API key found")
        return
    
    # Test the stable endpoint that already exists
    stable_endpoint_id = "xkv3xqsy50s3wt"
    
    print(f"🎯 Testing stable endpoint: {stable_endpoint_id}")
    print(f"📋 This endpoint has 1-3 workers (should be warm)")
    print(f"🔗 URL: https://api.runpod.ai/v2/{stable_endpoint_id}")
    
    success = test_endpoint_comprehensive(stable_endpoint_id, api_key)
    
    if success:
        print(f"\n🎉 STABLE ENDPOINT WORKS!")
        print(f"✅ The stable endpoint is functioning correctly")
        print(f"🔗 Working URL: https://api.runpod.ai/v2/{stable_endpoint_id}")
        
        # Update the endpoint info for frontend
        with open("runpod_working_endpoint.txt", "w") as f:
            f.write(f"A2 STT Working RunPod Endpoint\n")
            f.write(f"=============================\n\n")
            f.write(f"WORKING Endpoint ID: {stable_endpoint_id}\n")
            f.write(f"BROKEN Endpoint ID: v2lq88dd8re3ge (ignore this one)\n")
            f.write(f"Endpoint URL: https://api.runpod.ai/v2/{stable_endpoint_id}\n")
            f.write(f"Status: ✅ WORKING\n\n")
            f.write(f"Configuration:\n")
            f.write(f"- Workers: 1-3 (always has warm workers)\n")
            f.write(f"- Status: Tested and working\n\n")
            f.write(f"Test Command:\n")
            f.write(f"curl -X POST https://api.runpod.ai/v2/{stable_endpoint_id}/run \\\n")
            f.write(f"  -H 'Authorization: Bearer {api_key}' \\\n")
            f.write(f"  -H 'Content-Type: application/json' \\\n")
            f.write(f"  -d '{{\"input\": {{\"endpoint\": \"/health\"}}}}'\n\n")
            f.write(f"Frontend Update Required:\n")
            f.write(f"Update .env.local:\n")
            f.write(f"VITE_RUNPOD_ENDPOINT_ID={stable_endpoint_id}\n")
        
        print(f"\n📝 CRITICAL: Update frontend .env.local:")
        print(f"   VITE_RUNPOD_ENDPOINT_ID={stable_endpoint_id}")
        print(f"\n🚀 Frontend is ready for testing!")
        
        # Also update the frontend .env.local file directly
        env_file_path = "/home/waragainstwork/A2/a2-stt/a2-voice-flow-chat-main/.env.local"
        try:
            with open(env_file_path, "r") as f:
                env_content = f.read()
            
            # Replace the endpoint ID
            if "VITE_RUNPOD_ENDPOINT_ID=" in env_content:
                lines = env_content.split('\n')
                for i, line in enumerate(lines):
                    if line.startswith("VITE_RUNPOD_ENDPOINT_ID="):
                        lines[i] = f"VITE_RUNPOD_ENDPOINT_ID={stable_endpoint_id}"
                        break
                
                with open(env_file_path, "w") as f:
                    f.write('\n'.join(lines))
                
                print(f"✅ Frontend .env.local updated automatically!")
            else:
                print(f"⚠️  Please manually update {env_file_path}")
                
        except Exception as e:
            print(f"⚠️  Could not auto-update frontend .env.local: {e}")
            print(f"Please manually update: {env_file_path}")
        
    else:
        print(f"\n⚠️  Stable endpoint not responding properly")
        print(f"💡 Possible issues:")
        print(f"- Workers still initializing")
        print(f"- GPU allocation problems")
        print(f"- Template configuration issues")
        print(f"\n🔄 Try again in a few minutes or check RunPod dashboard")

if __name__ == "__main__":
    main()
