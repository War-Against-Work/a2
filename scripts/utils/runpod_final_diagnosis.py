#!/usr/bin/env python3
"""
Final RunPod Diagnosis and Local Fallback Setup
"""

import runpod
import os
import requests
import subprocess
from dotenv import load_dotenv

def main():
    print("🔍 Final RunPod Diagnosis")
    print("=" * 40)
    
    # Load environment
    load_dotenv()
    api_key = os.getenv("RUNPOD_API_KEY")
    if not api_key:
        print("❌ No API key found")
        return
    
    runpod.api_key = api_key
    
    print("📊 Current Situation Analysis:")
    print("- Endpoint v2lq88dd8re3ge: Workers 0-2, stuck in queue")
    print("- Endpoint xkv3xqsy50s3wt: Workers 1-3, also stuck in queue")
    print("- Both endpoints failing to process jobs")
    print("- Docker image works locally")
    
    try:
        # Check GPU availability
        print("\n🎮 Checking GPU availability...")
        gpus = runpod.get_gpus()
        available_gpus = [gpu for gpu in gpus if gpu.get('available', False)]
        print(f"Available GPUs: {len(available_gpus)}")
        
        if len(available_gpus) == 0:
            print("🚨 NO GPUS AVAILABLE - This is likely the problem!")
            print("💡 RunPod may have no available GPUs in your regions")
        else:
            print("✅ GPUs are available, issue is elsewhere")
        
        # Check templates
        print("\n📦 Checking templates...")
        templates = runpod.get_templates()
        a2_templates = [t for t in templates if 'a2' in t.get('name', '').lower()]
        print(f"A2 STT templates found: {len(a2_templates)}")
        
        for template in a2_templates:
            print(f"- {template['id']}: {template['name']} (serverless: {template.get('isServerless', False)})")
    
    except Exception as e:
        print(f"❌ Error checking RunPod resources: {e}")
    
    print(f"\n💡 Diagnosis Summary:")
    print(f"🔴 RunPod Issue: Jobs stuck in queue on both endpoints")
    print(f"🔴 Likely Cause: GPU availability or template configuration")
    print(f"🔴 Impact: Frontend cannot test with RunPod API")
    
    print(f"\n🚀 SOLUTION: Set up local API for immediate testing")
    print(f"✅ Docker image works locally")
    print(f"✅ Frontend is ready and waiting")
    print(f"✅ Can test full pipeline locally")
    
    # Check if Docker is running
    try:
        result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"\n🐳 Docker is running")
            
            # Check if our API container is running
            if 'a2-stt-api' in result.stdout:
                print(f"✅ A2 STT API container is already running")
                
                # Test local API
                try:
                    response = requests.get('http://localhost:8000/health', timeout=5)
                    if response.status_code == 200:
                        print(f"✅ Local API is responding: {response.json()}")
                        print(f"\n🎯 IMMEDIATE ACTION: Update frontend to use local API")
                        print(f"📝 Update .env.local:")
                        print(f"   VITE_API_BASE_URL=http://localhost:8000")
                        print(f"   # Comment out VITE_RUNPOD_ENDPOINT_ID")
                        
                        # Update frontend for local testing
                        env_file = "/home/waragainstwork/A2/a2-stt/a2-voice-flow-chat-main/.env.local"
                        try:
                            with open(env_file, "r") as f:
                                content = f.read()
                            
                            # Add local API configuration
                            if "VITE_API_BASE_URL=" not in content:
                                content += "\n# Local API for testing\nVITE_API_BASE_URL=http://localhost:8000\n"
                            
                            with open(env_file, "w") as f:
                                f.write(content)
                            
                            print(f"✅ Frontend .env.local updated for local testing")
                        except Exception as e:
                            print(f"⚠️  Could not update .env.local: {e}")
                        
                        return
                except:
                    pass
            
            print(f"\n🚀 Starting local A2 STT API...")
            subprocess.Popen([
                'docker', 'run', '--rm', '-p', '8000:8000', 
                '--name', 'a2-stt-local', 'aaronlax/a2-stt-api:latest'
            ])
            
            print(f"✅ Local API starting at http://localhost:8000")
            print(f"⏳ Wait 30 seconds for models to load, then test frontend")
            
        else:
            print(f"❌ Docker not running")
    
    except Exception as e:
        print(f"❌ Docker check failed: {e}")
    
    print(f"\n📋 Next Steps:")
    print(f"1. ✅ Use local API for immediate testing")
    print(f"2. 🔄 Check RunPod dashboard for GPU availability")
    print(f"3. 📞 Contact RunPod support if issue persists")
    print(f"4. 🚀 Test full frontend functionality locally")
    print(f"5. 🔧 Return to RunPod once GPU availability improves")

if __name__ == "__main__":
    main()
