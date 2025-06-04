#!/usr/bin/env python3
"""
RunPod Serverless Deployment Script for A2 STT API
Optimized for cost efficiency and low latency
"""

import os
import requests
import json
import time
from typing import Dict, Any, Optional

# Load environment variables from .env file if it exists
def load_env_file():
    """Load environment variables from .env file"""
    env_file = ".env"
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

class RunPodServerlessDeployer:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.runpod.ai/graphql"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def create_serverless_endpoint(self) -> Optional[str]:
        """Create a serverless endpoint optimized for A2 STT"""
        
        # Serverless endpoint configuration
        endpoint_config = {
            "name": "a2-stt-serverless",
            "description": "A2 STT Speech-to-Text API - Testing",
            "dockerImage": "aaronlax/a2-stt-api:latest",
            "gpuIds": "NVIDIA GeForce RTX 4090,NVIDIA RTX A6000,NVIDIA RTX A5000",  # Cost-effective GPUs
            "containerDiskInGb": 20,
            "volumeInGb": 0,  # No persistent volume needed
            "volumeMountPath": "/app/models",
            "env": [
                {"key": "CUDA_VISIBLE_DEVICES", "value": "0"},
                {"key": "PYTHONUNBUFFERED", "value": "1"},
                {"key": "RUNPOD_SERVERLESS", "value": "true"}
            ],
            "ports": "8000/http",
            
            # Optimized for minimal testing usage
            "scalerType": "QUEUE_DELAY",  # Scale based on queue delay
            "scalerValue": 3,  # Scale when queue delay > 3 seconds (relaxed for testing)
            "workersMin": 0,  # Scale to zero when not in use
            "workersMax": 2,  # Max 2 workers for testing
            "idleTimeout": 5,  # Keep workers alive for 5 seconds after request
            "flashBoot": True,  # Enable FlashBoot for faster cold starts
            
            # Cost optimization for testing
            "activeWorkers": 0,  # No active workers - pure pay-per-use
            "flexWorkers": 2,   # Only flex workers for testing
        }
        
        mutation = """
        mutation createServerlessEndpoint($input: ServerlessEndpointInput!) {
            createServerlessEndpoint(input: $input) {
                id
                name
                status
                urls {
                    stream
                    sync
                    async
                }
            }
        }
        """
        
        variables = {"input": endpoint_config}
        
        response = requests.post(
            self.base_url,
            headers=self.headers,
            json={"query": mutation, "variables": variables}
        )
        
        if response.status_code == 200:
            result = response.json()
            if "errors" in result:
                print(f"❌ Error creating endpoint: {result['errors']}")
                return None
            
            endpoint = result["data"]["createServerlessEndpoint"]
            print(f"✅ Serverless endpoint created successfully!")
            print(f"📋 Endpoint ID: {endpoint['id']}")
            print(f"🌐 Sync URL: {endpoint['urls']['sync']}")
            print(f"🔄 Async URL: {endpoint['urls']['async']}")
            print(f"📡 Stream URL: {endpoint['urls']['stream']}")
            
            return endpoint['id']
        else:
            print(f"❌ Failed to create endpoint: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    
    def get_endpoint_status(self, endpoint_id: str) -> Dict[str, Any]:
        """Get the status of a serverless endpoint"""
        
        query = """
        query getServerlessEndpoint($endpointId: String!) {
            getServerlessEndpoint(endpointId: $endpointId) {
                id
                name
                status
                activeWorkers
                idleWorkers
                runningWorkers
                urls {
                    stream
                    sync
                    async
                }
            }
        }
        """
        
        variables = {"endpointId": endpoint_id}
        
        response = requests.post(
            self.base_url,
            headers=self.headers,
            json={"query": query, "variables": variables}
        )
        
        if response.status_code == 200:
            result = response.json()
            if "errors" not in result:
                return result["data"]["getServerlessEndpoint"]
        
        return {}

def main():
    """Deploy A2 STT API to RunPod Serverless"""
    
    print("🚀 A2 STT RunPod Serverless Deployment")
    print("=" * 50)
    
    # Load environment variables from .env file if it exists
    load_env_file()
    
    # Get API key
    api_key = os.getenv("RUNPOD_API_KEY")
    if not api_key:
        print("❌ RUNPOD_API_KEY environment variable not set")
        print("Get your API key from: https://runpod.io/console/user/settings")
        return
    
    deployer = RunPodServerlessDeployer(api_key)
    
    print("📦 Creating serverless endpoint...")
    endpoint_id = deployer.create_serverless_endpoint()
    
    if endpoint_id:
        print(f"\n🎯 Deployment Summary:")
        print(f"💰 Cost Model: Pay-per-second (scales to $0 when idle)")
        print(f"⚡ Latency: ~1-3s cold start, <100ms warm requests")
        print(f"🔄 Scaling: 0-2 workers based on demand")
        print(f"💡 Active Workers: 0 (pure pay-per-use)")
        print(f"📈 FlashBoot: Enabled (faster cold starts)")
        
        print(f"\n🧪 Test your endpoint:")
        print(f"curl -X POST https://api.runpod.ai/v2/{endpoint_id}/run \\")
        print(f"  -H 'Authorization: Bearer {api_key}' \\")
        print(f"  -H 'Content-Type: application/json' \\")
        print(f"  -d '{{\"input\": {{\"endpoint\": \"/health\"}}}}'")
        
        # Wait a moment and check status
        print(f"\n⏳ Checking endpoint status...")
        time.sleep(5)
        status = deployer.get_endpoint_status(endpoint_id)
        if status:
            print(f"📊 Status: {status.get('status', 'Unknown')}")
            print(f"🏃 Active Workers: {status.get('activeWorkers', 0)}")
            print(f"💤 Idle Workers: {status.get('idleWorkers', 0)}")
            print(f"⚙️ Running Workers: {status.get('runningWorkers', 0)}")

if __name__ == "__main__":
    main()
