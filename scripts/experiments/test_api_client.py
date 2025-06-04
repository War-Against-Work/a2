#!/usr/bin/env python3
"""
A2 STT API Test Client
"""

import requests
import base64
import json
import time
import sys
import os
from pathlib import Path

# Audio generation for testing
import numpy as np
import scipy.io.wavfile as wavfile

class A2STTClient:
    """Client for A2 STT API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def health_check(self):
        """Check API health."""
        try:
            response = self.session.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return None
    
    def process_audio_data(self, audio_data: bytes, sample_rate: int = 16000):
        """Process raw audio data."""
        try:
            # Encode audio as base64
            audio_b64 = base64.b64encode(audio_data).decode('utf-8')
            
            payload = {
                "audio_data": audio_b64,
                "sample_rate": sample_rate,
                "enable_emotion": False
            }
            
            response = self.session.post(
                f"{self.base_url}/process-audio",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            print(f"❌ Audio processing failed: {e}")
            return None
    
    def process_audio_file(self, file_path: str):
        """Process audio file."""
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (os.path.basename(file_path), f, 'audio/wav')}
                response = self.session.post(
                    f"{self.base_url}/process-audio-file",
                    files=files,
                    timeout=30
                )
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            print(f"❌ File processing failed: {e}")
            return None
    
    def get_models(self):
        """Get available models."""
        try:
            response = self.session.get(f"{self.base_url}/models")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Models request failed: {e}")
            return None
    
    def get_stats(self):
        """Get API statistics."""
        try:
            response = self.session.get(f"{self.base_url}/stats")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Stats request failed: {e}")
            return None

def create_test_audio(duration: float = 3.0, sample_rate: int = 16000) -> bytes:
    """Create test audio data."""
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # Create speech-like audio
    f1, f2, f3 = 800, 1200, 2400
    audio = (
        0.3 * np.sin(2 * np.pi * f1 * t) * np.exp(-t * 0.5) +
        0.2 * np.sin(2 * np.pi * f2 * t) * np.exp(-t * 0.3) +
        0.1 * np.sin(2 * np.pi * f3 * t) * np.exp(-t * 0.7)
    )
    
    # Add envelope
    envelope = np.ones_like(t)
    envelope[int(0.8*sample_rate):int(1.2*sample_rate)] *= 0.1
    audio = audio * envelope * 0.7
    
    # Convert to 16-bit PCM
    audio_int16 = (audio * 32767).astype(np.int16)
    
    # Create WAV bytes
    import io
    wav_io = io.BytesIO()
    wavfile.write(wav_io, sample_rate, audio_int16)
    return wav_io.getvalue()

def test_api(base_url: str = "http://localhost:8000"):
    """Test the A2 STT API."""
    print("🧪 A2 STT API Test Client")
    print("=" * 40)
    
    client = A2STTClient(base_url)
    
    # Test 1: Health check
    print("1️⃣ Testing health check...")
    health = client.health_check()
    if health:
        print(f"   ✅ Status: {health['status']}")
        print(f"   🧠 Engine loaded: {health['engine_loaded']}")
        print(f"   📦 Models: {health['models_available']}")
        print(f"   ⏱️ Uptime: {health['uptime']:.1f}s")
    else:
        print("   ❌ Health check failed")
        return
    
    print()
    
    # Test 2: Get models
    print("2️⃣ Testing models endpoint...")
    models = client.get_models()
    if models:
        print(f"   ✅ Models status: {models['status']}")
        for name, info in models['models'].items():
            print(f"   📦 {name}: {'✅' if info['loaded'] else '❌'} {info['description']}")
    
    print()
    
    # Test 3: Process test audio
    print("3️⃣ Testing audio processing...")
    test_audio_data = create_test_audio()
    
    start_time = time.time()
    result = client.process_audio_data(test_audio_data)
    end_time = time.time()
    
    if result:
        print(f"   ✅ Processing successful!")
        print(f"   📝 Text: '{result['text']}'")
        print(f"   📊 Confidence: {result['confidence']:.1f}%")
        print(f"   😊 Emotion: {result['emotion']} (arousal: {result['arousal']:.2f})")
        print(f"   ⏱️ Processing time: {result['processing_time']:.3f}s")
        print(f"   🚀 Real-time factor: {result['real_time_factor']:.1f}x")
        print(f"   🌐 API latency: {end_time - start_time:.3f}s")
    else:
        print("   ❌ Audio processing failed")
    
    print()
    
    # Test 4: Get stats
    print("4️⃣ Testing stats endpoint...")
    stats = client.get_stats()
    if stats:
        print(f"   ✅ API uptime: {stats['uptime_formatted']}")
        print(f"   🧠 Engine status: {stats['engine_status']}")
        print(f"   📦 API version: {stats['api_version']}")
    
    print()
    print("🎉 API testing completed!")

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="A2 STT API Test Client")
    parser.add_argument("--url", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--file", help="Audio file to process")
    
    args = parser.parse_args()
    
    if args.file:
        # Process specific file
        client = A2STTClient(args.url)
        print(f"🎵 Processing file: {args.file}")
        result = client.process_audio_file(args.file)
        if result:
            print(f"📝 Text: '{result['text']}'")
            print(f"📊 Confidence: {result['confidence']:.1f}%")
        else:
            print("❌ Processing failed")
    else:
        # Run full test suite
        test_api(args.url)

if __name__ == "__main__":
    main()
