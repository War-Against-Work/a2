#!/usr/bin/env python3
"""
Check RunPod Logs and Detailed Status
"""

import runpod
import os
import requests
from dotenv import load_dotenv

def main():
    print("🔍 Checking RunPod Logs and Status")
    print("=" * 40)
    
    # Load environment
    load_dotenv()
    api_key = os.getenv("RUNPOD_API_KEY")
    if not api_key:
        print("❌ No API key found")
        return
    
    runpod.api_key = api_key
    
    # Get the fresh endpoint ID
    endpoint_id = "qg4svw2rm81sz9"
    
    try:
        print(f"📊 Checking endpoint status: {endpoint_id}")
        
        # Get endpoint details
        endpoints = runpod.get_endpoints()
        fresh_endpoint = None
        
        for endpoint in endpoints:
            if endpoint['id'] == endpoint_id:
                fresh_endpoint = endpoint
                break
        
        if not fresh_endpoint:
            print(f"❌ Endpoint {endpoint_id} not found")
            return
        
        print(f"\n📋 Endpoint Details:")
        print(f"Name: {fresh_endpoint.get('name', 'N/A')}")
        print(f"ID: {fresh_endpoint.get('id', 'N/A')}")
        print(f"Status: {fresh_endpoint.get('status', 'N/A')}")
        print(f"Workers Min: {fresh_endpoint.get('workersMin', 'N/A')}")
        print(f"Workers Max: {fresh_endpoint.get('workersMax', 'N/A')}")
        print(f"Workers Running: {fresh_endpoint.get('workersRunning', 'N/A')}")
        print(f"Workers Idle: {fresh_endpoint.get('workersIdle', 'N/A')}")
        print(f"Jobs In Queue: {fresh_endpoint.get('jobsInQueue', 'N/A')}")
        print(f"Jobs In Progress: {fresh_endpoint.get('jobsInProgress', 'N/A')}")
        print(f"Jobs Completed: {fresh_endpoint.get('jobsCompleted', 'N/A')}")
        print(f"Jobs Failed: {fresh_endpoint.get('jobsFailed', 'N/A')}")
        
        # Check if there are any error messages
        if 'error' in fresh_endpoint:
            print(f"🚨 Error: {fresh_endpoint['error']}")
        
        if 'message' in fresh_endpoint:
            print(f"💬 Message: {fresh_endpoint['message']}")
        
        # Check worker details if available
        if 'workers' in fresh_endpoint:
            print(f"\n👷 Worker Details:")
            for i, worker in enumerate(fresh_endpoint['workers']):
                print(f"Worker {i+1}:")
                print(f"  Status: {worker.get('status', 'N/A')}")
                print(f"  GPU: {worker.get('gpu', 'N/A')}")
                print(f"  Location: {worker.get('location', 'N/A')}")
                if 'error' in worker:
                    print(f"  Error: {worker['error']}")
        
        # Try to get more detailed status via direct API call
        print(f"\n🔍 Direct API Status Check:")
        try:
            headers = {"Authorization": f"Bearer {api_key}"}
            status_url = f"https://api.runpod.ai/v2/{endpoint_id}/status"
            
            response = requests.get(status_url, headers=headers, timeout=10)
            print(f"Status API Response: {response.status_code}")
            
            if response.status_code == 200:
                status_data = response.json()
                print(f"Status Data: {status_data}")
            else:
                print(f"Status Error: {response.text}")
                
        except Exception as api_error:
            print(f"API Error: {api_error}")
        
        # Check GPU availability again
        print(f"\n🎮 Current GPU Availability:")
        try:
            gpus = runpod.get_gpus()
            available_count = 0
            total_count = len(gpus)
            
            for gpu in gpus:
                if gpu.get('available', False):
                    available_count += 1
                    print(f"✅ {gpu.get('displayName', 'Unknown')}: Available")
                else:
                    print(f"❌ {gpu.get('displayName', 'Unknown')}: Not Available")
            
            print(f"\n📊 Summary: {available_count}/{total_count} GPUs available")
            
            if available_count == 0:
                print(f"🚨 CONFIRMED: No GPUs available - this explains the initialization delay")
        
        except Exception as gpu_error:
            print(f"GPU check error: {gpu_error}")
        
        # Check if we can get logs
        print(f"\n📜 Checking for logs...")
        try:
            # Try to get endpoint logs if they exist
            logs_url = f"https://api.runpod.ai/v2/{endpoint_id}/logs"
            headers = {"Authorization": f"Bearer {api_key}"}
            
            logs_response = requests.get(logs_url, headers=headers, timeout=10)
            if logs_response.status_code == 200:
                logs_data = logs_response.json()
                print(f"📜 Logs: {logs_data}")
            else:
                print(f"📜 No logs available yet (endpoint still initializing)")
                
        except Exception as logs_error:
            print(f"Logs error: {logs_error}")
        
        # Provide recommendations
        print(f"\n💡 Analysis:")
        if fresh_endpoint.get('workersRunning', 0) == 0:
            print(f"🔴 No workers running - endpoint stuck in initialization")
            print(f"🔴 Likely cause: No GPUs available to allocate workers")
            print(f"🔴 Workers cannot start without GPU allocation")
        
        print(f"\n📋 Recommendations:")
        print(f"1. 🕐 Wait 10-15 more minutes (sometimes takes longer)")
        print(f"2. 🌍 Try different GPU types (only high supply ones)")
        print(f"3. ⏰ Try again during off-peak hours (late night/early morning)")
        print(f"4. 🏠 Use local testing while waiting for GPU availability")
        print(f"5. 📞 Contact RunPod support if this persists")
        
    except Exception as e:
        print(f"❌ Error checking status: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
