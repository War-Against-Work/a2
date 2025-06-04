#!/usr/bin/env python3
"""
A2 STT RunPod Deployment Script (Simple Version)
Uses the official RunPod Python SDK for easy deployment
"""

import os
import runpod
from dotenv import load_dotenv

def main():
    print("🚀 A2 STT RunPod Simple Deployment")
    print("=" * 50)
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Get API key
    api_key = os.getenv("RUNPOD_API_KEY")
    if not api_key:
        print("❌ Error: RUNPOD_API_KEY not found in environment or .env file")
        print("Please set your RunPod API key:")
        print("export RUNPOD_API_KEY='your-api-key'")
        return
    
    # Set the API key
    runpod.api_key = api_key
    
    try:
        print("📦 Creating template...")
        
        # Create a template first
        template = runpod.create_template(
            name="a2-stt-template",
            image_name="aaronlax/a2-stt-api:latest",
            is_serverless=True,
            container_disk_in_gb=20,
            volume_in_gb=0,
            volume_mount_path="/app/models",
            ports="8000/http",
            env={
                "CUDA_VISIBLE_DEVICES": "0",
                "PYTHONUNBUFFERED": "1",
                "RUNPOD_SERVERLESS": "true"
            }
        )
        
        print(f"✅ Template created: {template['id']}")
        print(f"📝 Template name: {template['name']}")
        
        print("\n📡 Creating serverless endpoint...")
        
        # Create the serverless endpoint
        endpoint = runpod.create_endpoint(
            name="a2-stt-testing",
            template_id=template["id"],
            gpu_ids="NVIDIA GeForce RTX 4090,NVIDIA RTX A6000,NVIDIA RTX A5000",
            workers_min=0,  # Scale to zero for cost savings
            workers_max=2,  # Max 2 workers for testing
            idle_timeout=5,  # 5 seconds idle timeout
            scaler_type="QUEUE_DELAY",
            scaler_value=3,  # Scale when queue delay > 3 seconds
        )
        
        print(f"✅ Endpoint created successfully!")
        print(f"🆔 Endpoint ID: {endpoint['id']}")
        print(f"📝 Endpoint name: {endpoint['name']}")
        
        print(f"\n🎯 Deployment Summary:")
        print(f"💰 Cost Model: Pay-per-second (scales to $0 when idle)")
        print(f"⚡ Latency: ~1-3s cold start, <100ms warm requests")
        print(f"🔄 Scaling: 0-2 workers based on demand")
        print(f"💡 Workers: Pure pay-per-use (no always-on costs)")
        print(f"📈 Idle Timeout: 5 seconds")
        
        print(f"\n🧪 Test your endpoint:")
        print(f"Endpoint URL: https://api.runpod.ai/v2/{endpoint['id']}")
        print(f"\nHealth check:")
        print(f"curl -X POST https://api.runpod.ai/v2/{endpoint['id']}/run \\")
        print(f"  -H 'Authorization: Bearer {api_key}' \\")
        print(f"  -H 'Content-Type: application/json' \\")
        print(f"  -d '{{\"input\": {{\"endpoint\": \"/health\"}}}}'")
        
        print(f"\n✨ Deployment complete! Your A2 STT API is ready for testing.")
        print(f"💡 Remember: You only pay when the API is actively processing requests!")
        
    except Exception as e:
        print(f"❌ Error during deployment: {e}")
        return

if __name__ == "__main__":
    main()
