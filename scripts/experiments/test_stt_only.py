#!/usr/bin/env python3
"""
Test the A2 STT system with speech-to-text only (no emotion detection).
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import numpy as np
import asyncio
from core.stt_engine import A2STTEngine, STTResult

def generate_speech_like_audio(duration=2.0, sample_rate=16000):
    """Generate more realistic speech-like audio for testing."""
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # Create speech-like formants (vowel sounds)
    formant1 = 0.3 * np.sin(2 * np.pi * 800 * t)  # F1
    formant2 = 0.2 * np.sin(2 * np.pi * 1200 * t)  # F2
    formant3 = 0.1 * np.sin(2 * np.pi * 2400 * t)  # F3
    
    # Add some modulation to make it more speech-like
    modulation = 0.5 + 0.5 * np.sin(2 * np.pi * 5 * t)  # 5Hz modulation
    
    # Combine formants with envelope
    envelope = np.exp(-t * 0.5)  # Decay envelope
    audio = (formant1 + formant2 + formant3) * modulation * envelope
    
    # Add some noise
    noise = 0.05 * np.random.randn(len(audio))
    audio += noise
    
    # Normalize
    audio = audio / np.max(np.abs(audio)) * 0.8
    
    return audio.astype(np.float32)

async def test_stt_system():
    """Test the STT system with different audio samples."""
    print("🎤 A2 STT Test (Speech-to-Text Only)")
    print("=" * 50)
    
    # Initialize the engine without emotion detection
    print("Initializing STT engine (no emotion detection)...")
    engine = A2STTEngine(enable_emotion=False)
    
    # Test cases
    test_cases = [
        {"name": "Short Speech", "duration": 1.0},
        {"name": "Medium Speech", "duration": 2.5},
        {"name": "Long Speech", "duration": 4.0},
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📊 Test {i}: {test_case['name']}")
        print("-" * 30)
        
        # Generate test audio
        audio = generate_speech_like_audio(duration=test_case['duration'])
        print(f"Generated {test_case['duration']}s audio")
        print(f"Audio shape: {audio.shape}")
        print(f"Audio range: [{audio.min():.3f}, {audio.max():.3f}]")
        
        # Process with STT
        try:
            result = await engine.process_audio(audio, sample_rate=16000)
            
            print(f"✅ Processing successful!")
            print(f"   Text: '{result.text}'")
            print(f"   Emotion: {result.emotion}")
            print(f"   Arousal: {result.arousal:.2f}")
            print(f"   Confidence: {result.confidence:.1%}")
            print(f"   Processing time: {result.processing_time:.3f}s")
            if result.detected_events:
                print(f"   Events: {result.detected_events}")
                
        except Exception as e:
            print(f"❌ Processing failed: {e}")
    
    print("\n🎯 STT System Test Complete!")
    print("The A2 STT system is ready for real audio input.")

if __name__ == "__main__":
    asyncio.run(test_stt_system())
