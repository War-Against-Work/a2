#!/usr/bin/env python3
"""
RunPod Diagnosis Script
Check template and endpoint configuration to identify the issue
"""

import runpod
import os
from dotenv import load_dotenv

def main():
    print("🔍 RunPod A2 STT Diagnosis")
    print("=" * 40)
    
    # Load environment
    load_dotenv()
    api_key = os.getenv("RUNPOD_API_KEY")
    if not api_key:
        print("❌ No API key found")
        return
    
    runpod.api_key = api_key
    
    try:
        # Get current endpoint info
        print("📡 Checking current endpoint...")
        endpoint_id = "v2lq88dd8re3ge"
        
        # List all endpoints to find ours
        endpoints = runpod.get_endpoints()
        current_endpoint = None
        
        for endpoint in endpoints:
            if endpoint['id'] == endpoint_id:
                current_endpoint = endpoint
                break
        
        if not current_endpoint:
            print(f"❌ Endpoint {endpoint_id} not found")
            return
        
        print(f"✅ Found endpoint: {current_endpoint['name']}")
        print(f"📊 Status: {current_endpoint.get('status', 'unknown')}")
        print(f"🔧 Template ID: {current_endpoint.get('template', {}).get('id', 'unknown')}")
        
        # Get template info
        template_id = current_endpoint.get('template', {}).get('id')
        if template_id:
            print(f"\n📦 Checking template {template_id}...")
            templates = runpod.get_templates()
            current_template = None
            
            for template in templates:
                if template['id'] == template_id:
                    current_template = template
                    break
            
            if current_template:
                print(f"✅ Template found: {current_template['name']}")
                print(f"🐳 Image: {current_template.get('imageName', 'unknown')}")
                print(f"💾 Container disk: {current_template.get('containerDiskInGb', 'unknown')}GB")
                print(f"🔌 Ports: {current_template.get('ports', 'unknown')}")
                print(f"🌍 Environment vars: {len(current_template.get('env', {}))}")
                
                # Check if it's serverless
                if current_template.get('isServerless'):
                    print("✅ Template is serverless-enabled")
                else:
                    print("❌ Template is NOT serverless-enabled - THIS IS THE PROBLEM!")
            else:
                print(f"❌ Template {template_id} not found")
        
        # Check endpoint configuration
        print(f"\n⚙️  Endpoint Configuration:")
        print(f"Workers min: {current_endpoint.get('workersMin', 'unknown')}")
        print(f"Workers max: {current_endpoint.get('workersMax', 'unknown')}")
        print(f"Idle timeout: {current_endpoint.get('idleTimeout', 'unknown')}")
        print(f"GPU types: {current_endpoint.get('gpuIds', 'unknown')}")
        
        # Check for common issues
        print(f"\n🔍 Potential Issues:")
        
        if current_endpoint.get('workersMin', 0) == 0:
            print("⚠️  Min workers = 0: Cold start issues likely")
        
        if current_endpoint.get('idleTimeout', 0) < 10:
            print("⚠️  Very short idle timeout: Workers shutting down too quickly")
        
        if not current_template or not current_template.get('isServerless'):
            print("🚨 CRITICAL: Template not configured for serverless!")
        
        # Recommendations
        print(f"\n💡 Recommendations:")
        print("1. Check RunPod dashboard for worker logs")
        print("2. Verify template is serverless-enabled")
        print("3. Consider increasing min workers to 1")
        print("4. Check GPU availability in your regions")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
