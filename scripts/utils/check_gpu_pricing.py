#!/usr/bin/env python3
"""
Check RunPod GPU pricing via GraphQL API
"""

import requests
import json

def get_gpu_pricing():
    """Get GPU types and pricing from RunPod GraphQL API"""
    
    api_key = "rpa_8TZ9Q78NUTXMUYKV87XRQ8J684QD4Q2DHUJXS4SN2hb25y"
    
    # RunPod GraphQL endpoint
    url = "https://api.runpod.ai/graphql"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # GraphQL query to get GPU types and pricing
    query = """
    query {
        gpuTypes {
            id
            displayName
            memoryInGb
            vcpuCount
            communityPrice
            securePrice
            lowestPrice {
                minimumBidPrice
                uninterruptablePrice
            }
        }
    }
    """
    
    try:
        response = requests.post(url, headers=headers, json={"query": query})
        
        if response.status_code == 200:
            data = response.json()
            
            if 'errors' in data:
                print(f"❌ GraphQL errors: {data['errors']}")
                return []
            
            gpu_types = data.get('data', {}).get('gpuTypes', [])
            return gpu_types
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            return []
            
    except Exception as e:
        print(f"❌ Error fetching GPU data: {e}")
        return []

def analyze_gpu_options():
    """Analyze GPU options and recommend best choices"""
    
    print("🚀 RunPod GPU Analysis for US Regions")
    print("=" * 60)
    
    gpu_types = get_gpu_pricing()
    
    if not gpu_types:
        print("❌ Could not fetch GPU data")
        return
    
    print(f"\n📊 Found {len(gpu_types)} GPU types")
    print("-" * 60)
    
    # Filter and sort GPUs
    suitable_gpus = []
    
    for gpu in gpu_types:
        gpu_id = gpu.get('id', 'unknown')
        name = gpu.get('displayName', gpu_id)
        memory = gpu.get('memoryInGb', 0)
        community_price = gpu.get('communityPrice', 0)
        secure_price = gpu.get('securePrice', 0)
        
        # Only include GPUs with 8GB+ memory (suitable for STT)
        if memory >= 8 and community_price > 0:
            suitable_gpus.append({
                'id': gpu_id,
                'name': name,
                'memory': memory,
                'community_price': community_price,
                'secure_price': secure_price,
                'lowest_price': gpu.get('lowestPrice', {})
            })
    
    # Sort by community price (cheapest first)
    suitable_gpus.sort(key=lambda x: x['community_price'])
    
    print("\n🇺🇸 Recommended GPUs for STT (8GB+, sorted by price):")
    print("-" * 80)
    
    for i, gpu in enumerate(suitable_gpus[:8], 1):  # Top 8 options
        price_per_hour = gpu['community_price']
        price_per_minute = price_per_hour / 60
        
        print(f"{i:2d}. {gpu['name']} ({gpu['memory']}GB)")
        print(f"    💰 Community: ${price_per_hour:.4f}/hr (${price_per_minute:.4f}/min)")
        print(f"    🔒 Secure: ${gpu['secure_price']:.4f}/hr")
        print(f"    🆔 GPU ID: {gpu['id']}")
        print()
    
    if suitable_gpus:
        # Recommend top 3 cheapest
        print("🎯 TOP 3 RECOMMENDATIONS (cheapest first):")
        print("-" * 50)
        
        for i, gpu in enumerate(suitable_gpus[:3], 1):
            print(f"{i}. {gpu['name']} - ${gpu['community_price']:.4f}/hr")
            print(f"   Use this GPU ID: {gpu['id']}")
            print()
        
        print("💡 BEST CHOICE FOR TESTING:")
        best = suitable_gpus[0]
        print(f"   GPU: {best['name']}")
        print(f"   ID: {best['id']}")
        print(f"   Cost: ${best['community_price']:.4f}/hr")
        print(f"   Memory: {best['memory']}GB")
        
        return best['id']
    
    return None

def explain_sdk_failures():
    """Explain why SDK endpoint creation was failing"""
    
    print("\n🔍 WHY SDK ENDPOINT CREATION FAILED:")
    print("=" * 60)
    
    print("1. 📍 REGION ISSUES:")
    print("   - SDK may default to regions with no GPU availability")
    print("   - Manual creation shows real-time availability")
    print("   - Community Cloud has better US coverage")
    print()
    
    print("2. 💰 GPU SELECTION PROBLEMS:")
    print("   - SDK used generic GPU list: 'RTX A5000,RTX A6000,RTX 4090'")
    print("   - These might not be available in selected regions")
    print("   - Manual selection shows what's actually available")
    print()
    
    print("3. ⚙️  CONFIGURATION ISSUES:")
    print("   - Scale-to-zero (0 min workers) causes cold start delays")
    print("   - Aggressive timeouts don't allow for initialization")
    print("   - Wrong scaler settings")
    print()
    
    print("4. 🔧 SDK vs WEB INTERFACE:")
    print("   - SDK might use older API versions")
    print("   - Web interface has latest optimizations")
    print("   - Better error reporting in web interface")
    print()
    
    print("✅ SOLUTION: Use manual creation with:")
    print("   - Specific GPU ID from availability check")
    print("   - Community Cloud for US regions")
    print("   - 1 min worker (not scale-to-zero)")
    print("   - 60+ second idle timeout")

def main():
    # Get GPU recommendations
    recommended_gpu = analyze_gpu_options()
    
    # Explain SDK failures
    explain_sdk_failures()
    
    print("\n📝 MANUAL ENDPOINT CREATION CHECKLIST:")
    print("=" * 60)
    print("1. ✅ Docker Image: aaronlax/a2-stt-api:fixed")
    print("2. ✅ Cloud Type: Community Cloud")
    print("3. ✅ Workers: 1 minimum, 2 maximum")
    print("4. ✅ Idle Timeout: 60-120 seconds")
    print("5. ✅ Container Disk: 20GB")
    print("6. ✅ Ports: 8000/http")
    
    if recommended_gpu:
        print(f"7. ✅ GPU Selection: {recommended_gpu}")
    else:
        print("7. ⚠️  GPU Selection: Check web interface for availability")

if __name__ == "__main__":
    main()
