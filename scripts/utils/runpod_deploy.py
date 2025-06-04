#!/usr/bin/env python3
"""
RunPod Deployment Script for A2 STT API
"""

import os
import sys
import time
import requests
import json
from typing import Dict, Any, Optional

def check_runpod_api_key():
    """Check if RunPod API key is available."""
    api_key = os.getenv('RUNPOD_API_KEY')
    if not api_key:
        print("❌ RUNPOD_API_KEY environment variable not set")
        print("Get your API key from: https://www.runpod.io/console/user/settings")
        return None
    return api_key

def create_runpod_template(api_key: str) -> Optional[str]:
    """Create a RunPod template for A2 STT."""
    
    template_config = {
        "name": "a2-stt-api",
        "imageName": "aaronlax/a2-stt-api:latest",  # Updated with correct username
        "dockerArgs": "",
        "containerDiskInGb": 20,
        "volumeInGb": 10,
        "volumeMountPath": "/app/models",
        "ports": "8000/http",
        "env": [
            {"key": "CUDA_VISIBLE_DEVICES", "value": "0"},
            {"key": "PYTHONUNBUFFERED", "value": "1"}
        ],
        "startJupyter": False,
        "startSsh": True
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            "https://api.runpod.io/graphql",
            headers=headers,
            json={
                "query": """
                mutation createTemplate($input: TemplateInput!) {
                    createTemplate(input: $input) {
                        id
                        name
                        imageName
                    }
                }
                """,
                "variables": {"input": template_config}
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            if "data" in result and result["data"]["createTemplate"]:
                template_id = result["data"]["createTemplate"]["id"]
                print(f"✅ Template created: {template_id}")
                return template_id
            else:
                print(f"❌ Template creation failed: {result}")
                return None
        else:
            print(f"❌ API request failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error creating template: {e}")
        return None

def deploy_pod(api_key: str, template_id: str, gpu_type: str = "NVIDIA GeForce RTX 3070") -> Optional[str]:
    """Deploy a pod using the template."""
    
    pod_config = {
        "name": f"a2-stt-{int(time.time())}",
        "templateId": template_id,
        "gpuTypeId": gpu_type,
        "cloudType": "ALL",
        "supportPublicIp": True,
        "startJupyter": False,
        "startSsh": True
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            "https://api.runpod.io/graphql",
            headers=headers,
            json={
                "query": """
                mutation createPod($input: PodInput!) {
                    createPod(input: $input) {
                        id
                        name
                        machine {
                            podHostId
                        }
                    }
                }
                """,
                "variables": {"input": pod_config}
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            if "data" in result and result["data"]["createPod"]:
                pod_id = result["data"]["createPod"]["id"]
                print(f"✅ Pod deployed: {pod_id}")
                return pod_id
            else:
                print(f"❌ Pod deployment failed: {result}")
                return None
        else:
            print(f"❌ API request failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error deploying pod: {e}")
        return None

def get_pod_status(api_key: str, pod_id: str) -> Dict[str, Any]:
    """Get pod status and connection info."""
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            "https://api.runpod.io/graphql",
            headers=headers,
            json={
                "query": """
                query getPod($input: String!) {
                    pod(input: $input) {
                        id
                        name
                        runtime {
                            uptimeInSeconds
                            ports {
                                ip
                                isIpPublic
                                privatePort
                                publicPort
                                type
                            }
                        }
                        machine {
                            podHostId
                        }
                    }
                }
                """,
                "variables": {"input": pod_id}
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            if "data" in result and result["data"]["pod"]:
                return result["data"]["pod"]
        
        return {}
        
    except Exception as e:
        print(f"❌ Error getting pod status: {e}")
        return {}

def main():
    """Main deployment function."""
    print("🚀 A2 STT RunPod Deployment")
    print("=" * 40)
    
    # Check API key
    api_key = check_runpod_api_key()
    if not api_key:
        return
    
    print("📋 Deployment Steps:")
    print("1. Build and push Docker image to registry")
    print("2. Create RunPod template")
    print("3. Deploy pod")
    print("4. Get connection details")
    print()
    
    # Step 1: Docker build instructions
    print("🐳 Step 1: Build and Push Docker Image")
    print("Run these commands locally:")
    print("  docker build -t your-dockerhub-username/a2-stt-api:latest .")
    print("  docker push your-dockerhub-username/a2-stt-api:latest")
    print()
    
    input("Press Enter when Docker image is pushed...")
    
    # Step 2: Create template
    print("📝 Step 2: Creating RunPod Template...")
    template_id = create_runpod_template(api_key)
    if not template_id:
        print("❌ Failed to create template")
        return
    
    # Step 3: Deploy pod
    print("🚀 Step 3: Deploying Pod...")
    pod_id = deploy_pod(api_key, template_id)
    if not pod_id:
        print("❌ Failed to deploy pod")
        return
    
    # Step 4: Wait for pod to start and get details
    print("⏳ Step 4: Waiting for pod to start...")
    for i in range(30):  # Wait up to 5 minutes
        time.sleep(10)
        pod_info = get_pod_status(api_key, pod_id)
        
        if pod_info and "runtime" in pod_info and pod_info["runtime"]:
            ports = pod_info["runtime"].get("ports", [])
            for port in ports:
                if port["privatePort"] == 8000:
                    public_url = f"http://{port['ip']}:{port['publicPort']}"
                    print(f"✅ A2 STT API is running!")
                    print(f"🌐 API URL: {public_url}")
                    print(f"📚 Documentation: {public_url}/docs")
                    print(f"❤️ Health Check: {public_url}/health")
                    return
        
        print(f"⏳ Still starting... ({i+1}/30)")
    
    print("⚠️ Pod may still be starting. Check RunPod console for details.")

if __name__ == "__main__":
    main()
