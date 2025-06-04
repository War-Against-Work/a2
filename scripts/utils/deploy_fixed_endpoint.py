#!/usr/bin/env python3
"""
Deploy a new RunPod endpoint with the fixed STT engine import
"""

import runpod
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    print("🚀 Deploying new RunPod endpoint with fixed STT engine...")
    
    # Set API key
    api_key = "rpa_8TZ9Q78NUTXMUYKV87XRQ8J684QD4Q2DHUJXS4SN2hb25y"
    runpod.api_key = api_key
    
    try:
        # Create template with fixed image
        print("📋 Creating template with fixed image...")
        template = runpod.create_template(
            name="a2-stt-fixed",
            image_name="aaronlax/a2-stt-api:fixed",
            container_disk_in_gb=20,
            volume_in_gb=0,
            ports="8000/http"
        )
        
        template_id = template['id']
        print(f"✅ Template created: {template_id}")
        
        # Create endpoint
        print("🔗 Creating endpoint...")
        endpoint = runpod.create_endpoint(
            name="a2-stt-fixed",
            template_id=template_id,
            gpu_ids="NVIDIA RTX A5000,NVIDIA RTX A6000,NVIDIA GeForce RTX 4090",
            workers_min=1,
            workers_max=2,
            idle_timeout=120,
            scaler_type="QUEUE_DELAY",
            scaler_value=1,
        )
        
        endpoint_id = endpoint['id']
        endpoint_url = f"https://api.runpod.ai/v2/{endpoint_id}"
        
        print(f"✅ Endpoint created successfully!")
        print(f"📍 Endpoint ID: {endpoint_id}")
        print(f"🌐 Endpoint URL: {endpoint_url}")
        print(f"🔑 API Key: {api_key}")
        
        # Save to file
        with open("fixed_endpoint_info.txt", "w") as f:
            f.write(f"FIXED A2 STT ENDPOINT\n")
            f.write(f"====================\n\n")
            f.write(f"Endpoint ID: {endpoint_id}\n")
            f.write(f"Endpoint URL: {endpoint_url}\n")
            f.write(f"API Key: {api_key}\n")
            f.write(f"Template ID: {template_id}\n")
            f.write(f"Docker Image: aaronlax/a2-stt-api:fixed\n\n")
            f.write(f"Update your .env.local file:\n")
            f.write(f"VITE_RUNPOD_API_URL={endpoint_url}\n")
            f.write(f"VITE_RUNPOD_API_KEY={api_key}\n")
            f.write(f"VITE_RUNPOD_ENDPOINT_ID={endpoint_id}\n")
        
        print("📝 Endpoint details saved to fixed_endpoint_info.txt")
        print("\n🔧 Next steps:")
        print(f"1. Update your .env.local with the new endpoint ID: {endpoint_id}")
        print(f"2. Update VITE_RUNPOD_API_URL to: {endpoint_url}")
        print("3. Wait 1-2 minutes for the endpoint to initialize")
        print("4. Test the frontend again")
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
