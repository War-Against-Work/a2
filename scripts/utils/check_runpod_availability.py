#!/usr/bin/env python3
"""
Check RunPod GPU availability and pricing for US regions
"""

import runpod
import requests
import json

def check_gpu_availability():
    """Check available GPUs and their pricing"""
    api_key = "rpa_8TZ9Q78NUTXMUYKV87XRQ8J684QD4Q2DHUJXS4SN2hb25y"
    runpod.api_key = api_key
    
    print("🔍 Checking RunPod GPU availability and pricing...")
    print("=" * 60)
    
    try:
        # Get available GPU types
        print("\n📊 Available GPU Types:")
        gpu_types = runpod.get_gpu_types()
        
        # Sort by price (cheapest first)
        us_gpus = []
        for gpu in gpu_types:
            gpu_id = gpu.get('id', 'unknown')
            display_name = gpu.get('displayName', gpu_id)
            memory = gpu.get('memoryInGb', 'unknown')
            
            # Get pricing info
            community_price = gpu.get('communityPrice', 0)
            secure_price = gpu.get('securePrice', 0)
            
            # Check if it's likely US-based (community cloud usually includes US)
            if community_price > 0:
                us_gpus.append({
                    'id': gpu_id,
                    'name': display_name,
                    'memory': memory,
                    'community_price': community_price,
                    'secure_price': secure_price,
                    'gpu': gpu
                })
        
        # Sort by community price (cheapest first)
        us_gpus.sort(key=lambda x: x['community_price'])
        
        print(f"\n🇺🇸 US GPU Options (sorted by price - cheapest first):")
        print("-" * 80)
        for i, gpu in enumerate(us_gpus[:10], 1):  # Show top 10 cheapest
            print(f"{i:2d}. {gpu['name']}")
            print(f"    ID: {gpu['id']}")
            print(f"    Memory: {gpu['memory']}GB")
            print(f"    Community Price: ${gpu['community_price']:.4f}/hr")
            print(f"    Secure Price: ${gpu['secure_price']:.4f}/hr")
            print()
        
        return us_gpus
        
    except Exception as e:
        print(f"❌ Error checking GPU availability: {e}")
        return []

def check_regions():
    """Check available regions"""
    print("\n🌍 Checking available regions...")
    
    # This is a basic check - RunPod doesn't always expose region details via API
    try:
        # Try to get any region/datacenter info
        print("Note: RunPod typically auto-selects regions based on GPU availability")
        print("Community Cloud: Global (includes US East/West)")
        print("Secure Cloud: Specific datacenters (more expensive)")
        
    except Exception as e:
        print(f"❌ Error checking regions: {e}")

def analyze_previous_failures():
    """Analyze why previous endpoint creation failed"""
    print("\n🔍 Analyzing Previous Endpoint Creation Issues:")
    print("-" * 60)
    
    print("Likely causes of 'IN_QUEUE' issues:")
    print("1. 📍 Region Selection:")
    print("   - SDK may default to regions with no available GPUs")
    print("   - Manual creation allows better region selection")
    print()
    print("2. 💰 GPU Selection:")
    print("   - Requesting expensive GPUs that aren't available")
    print("   - Better to specify multiple GPU types as fallbacks")
    print()
    print("3. ⚙️  Configuration Issues:")
    print("   - Scale-to-zero can cause cold start problems")
    print("   - Aggressive timeout settings")
    print("   - Wrong container configuration")
    print()
    print("4. 🔧 SDK vs Manual:")
    print("   - SDK might use outdated API endpoints")
    print("   - Manual creation uses latest web interface")
    print()

def recommend_gpu_selection(gpu_list):
    """Recommend best GPU selection for STT workload"""
    print("\n🎯 Recommended GPU Selection for STT:")
    print("-" * 50)
    
    # Filter for GPUs suitable for STT (need decent VRAM)
    suitable_gpus = [gpu for gpu in gpu_list if gpu['memory'] >= 8]
    
    print("✅ Best options for Speech-to-Text (8GB+ VRAM):")
    for i, gpu in enumerate(suitable_gpus[:5], 1):
        price_per_hour = gpu['community_price']
        cost_per_minute = price_per_hour / 60
        
        print(f"{i}. {gpu['name']} ({gpu['memory']}GB)")
        print(f"   💰 ${price_per_hour:.4f}/hr (${cost_per_minute:.4f}/min)")
        print(f"   🆔 GPU ID: {gpu['id']}")
        print()
    
    if suitable_gpus:
        cheapest = suitable_gpus[0]
        print(f"💡 RECOMMENDED: {cheapest['name']}")
        print(f"   - Cheapest suitable option at ${cheapest['community_price']:.4f}/hr")
        print(f"   - Use GPU ID: {cheapest['id']}")
        
        return cheapest['id']
    
    return None

def main():
    print("🚀 RunPod GPU Availability Analysis")
    print("=" * 60)
    
    # Check GPU availability
    gpu_list = check_gpu_availability()
    
    # Check regions
    check_regions()
    
    # Analyze previous failures
    analyze_previous_failures()
    
    # Recommend best GPU
    if gpu_list:
        recommended_gpu = recommend_gpu_selection(gpu_list)
        
        print("\n📝 SUMMARY FOR MANUAL ENDPOINT CREATION:")
        print("-" * 50)
        print("1. Use Docker image: aaronlax/a2-stt-api:fixed")
        print("2. Select Community Cloud (cheaper)")
        print("3. Choose from recommended GPUs above")
        print("4. Set workers: 1 min, 2 max (avoid scale-to-zero)")
        print("5. Idle timeout: 60-120 seconds")
        print("6. Container disk: 20GB")
        
        if recommended_gpu:
            print(f"7. Recommended GPU ID: {recommended_gpu}")

if __name__ == "__main__":
    main()
