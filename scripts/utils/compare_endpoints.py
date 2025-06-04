#!/usr/bin/env python3
"""
Compare the working endpoint vs my failed endpoint
"""

import runpod
import os
from dotenv import load_dotenv

def main():
    print("🔍 Comparing Working vs Failed Endpoints")
    print("=" * 50)
    
    # Load environment
    load_dotenv()
    api_key = os.getenv("RUNPOD_API_KEY")
    if not api_key:
        print("❌ No API key found")
        return
    
    runpod.api_key = api_key
    
    try:
        # Get all endpoints
        endpoints = runpod.get_endpoints()
        
        working_endpoint = None
        my_endpoint = None
        
        for endpoint in endpoints:
            if endpoint['id'] == 'ez2hb2e6fqeh54':
                working_endpoint = endpoint
            elif endpoint['id'] == 'qg4svw2rm81sz9':
                my_endpoint = endpoint
        
        print("✅ USER'S WORKING ENDPOINT:")
        if working_endpoint:
            print(f"ID: {working_endpoint.get('id')}")
            print(f"Name: {working_endpoint.get('name')}")
            print(f"Template ID: {working_endpoint.get('templateId')}")
            print(f"Workers Min: {working_endpoint.get('workersMin')}")
            print(f"Workers Max: {working_endpoint.get('workersMax')}")
            print(f"Workers Running: {working_endpoint.get('workersRunning')}")
            print(f"Idle Timeout: {working_endpoint.get('idleTimeout')}")
            print(f"GPU IDs: {working_endpoint.get('gpuIds')}")
            print(f"Locations: {working_endpoint.get('locations')}")
        else:
            print("❌ Working endpoint not found")
        
        print(f"\n❌ MY FAILED ENDPOINT:")
        if my_endpoint:
            print(f"ID: {my_endpoint.get('id')}")
            print(f"Name: {my_endpoint.get('name')}")
            print(f"Template ID: {my_endpoint.get('templateId')}")
            print(f"Workers Min: {my_endpoint.get('workersMin')}")
            print(f"Workers Max: {my_endpoint.get('workersMax')}")
            print(f"Workers Running: {my_endpoint.get('workersRunning')}")
            print(f"Idle Timeout: {my_endpoint.get('idleTimeout')}")
            print(f"GPU IDs: {my_endpoint.get('gpuIds')}")
            print(f"Locations: {my_endpoint.get('locations')}")
        else:
            print("❌ My endpoint not found")
        
        # Get template details
        if working_endpoint:
            print(f"\n📦 WORKING ENDPOINT'S TEMPLATE:")
            try:
                templates = runpod.get_templates()
                working_template = None
                for template in templates:
                    if template['id'] == working_endpoint.get('templateId'):
                        working_template = template
                        break
                
                if working_template:
                    print(f"Template Name: {working_template.get('name')}")
                    print(f"Docker Image: {working_template.get('imageName')}")
                    print(f"Container Disk: {working_template.get('containerDiskInGb')}GB")
                    print(f"Volume: {working_template.get('volumeInGb')}GB")
                    print(f"Ports: {working_template.get('ports')}")
                    print(f"Env Vars: {working_template.get('env')}")
                    print(f"Is Serverless: {working_template.get('isServerless')}")
                else:
                    print("❌ Template not found")
            except Exception as template_error:
                print(f"❌ Error getting template: {template_error}")
        
        # Check if there's a difference in the Docker image or configuration
        print(f"\n💡 ANALYSIS:")
        if working_endpoint and my_endpoint:
            print(f"🔍 Key Differences:")
            
            if working_endpoint.get('templateId') != my_endpoint.get('templateId'):
                print(f"📦 Different templates:")
                print(f"  Working: {working_endpoint.get('templateId')}")
                print(f"  Mine: {my_endpoint.get('templateId')}")
            
            if working_endpoint.get('workersRunning', 0) != my_endpoint.get('workersRunning', 0):
                print(f"👷 Different worker status:")
                print(f"  Working: {working_endpoint.get('workersRunning', 0)} running")
                print(f"  Mine: {my_endpoint.get('workersRunning', 0)} running")
        
        # The real issue might be the Docker container configuration
        print(f"\n🐳 DOCKER CONTAINER ISSUE:")
        print(f"Even though your endpoint has workers running,")
        print(f"jobs are stuck in queue. This suggests:")
        print(f"1. Workers are running but container isn't responding")
        print(f"2. Wrong port configuration")
        print(f"3. Container startup script issues")
        print(f"4. Missing environment variables")
        
        print(f"\n🔧 DEBUGGING STEPS:")
        print(f"1. Check what template your working endpoint uses")
        print(f"2. Verify the Docker image is correct")
        print(f"3. Check if container needs specific startup command")
        print(f"4. Verify port 8000 is properly exposed")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
