#!/usr/bin/env python3
"""
Simple demo script for A2 STT system.
Tests basic functionality without requiring models to be downloaded.
"""

import numpy as np
import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.append('src')

def test_imports():
    """Test that all imports work."""
    print("Testing imports...")
    try:
        from core.stt_engine import A2STTEngine, STTResult
        print("✓ Core STT engine imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_stt_result():
    """Test STTResult dataclass."""
    print("\nTesting STTResult dataclass...")
    try:
        from core.stt_engine import STTResult
        
        result = STTResult(
            text="hello A2",
            emotion="neutral", 
            arousal=0.5,
            confidence=0.95,
            processing_time=0.1,
            detected_events=[]
        )
        
        print(f"✓ STTResult created: {result.text}")
        print(f"  Emotion: {result.emotion}")
        print(f"  Confidence: {result.confidence}")
        return True
    except Exception as e:
        print(f"✗ STTResult test failed: {e}")
        return False

def test_engine_creation():
    """Test engine creation (without models)."""
    print("\nTesting engine creation...")
    try:
        from core.stt_engine import A2STTEngine
        
        # This will fail if models aren't available, but we can test the class
        print("  Note: This will fail if models aren't downloaded yet")
        print("  Run 'python3 scripts/download_models.py' first")
        
        # Try to create engine
        engine = A2STTEngine(enable_emotion=False)
        print("✓ Engine created successfully!")
        print(f"  Custom vocab loaded: {len(engine.custom_vocab['commands'])} commands")
        return True
        
    except Exception as e:
        print(f"✗ Engine creation failed: {e}")
        print("  This is expected if models aren't downloaded yet")
        return False

def test_audio_generation():
    """Test audio generation for testing."""
    print("\nTesting audio generation...")
    try:
        # Generate 3 seconds of test audio
        sample_rate = 16000
        duration = 3.0
        samples = int(sample_rate * duration)
        
        # Generate sine wave + noise
        t = np.linspace(0, duration, samples)
        frequency = 440  # A4 note
        audio = 0.1 * np.sin(2 * np.pi * frequency * t)
        audio += 0.05 * np.random.randn(samples)  # Add noise
        audio = audio.astype(np.float32)
        
        print(f"✓ Generated {duration}s of test audio")
        print(f"  Shape: {audio.shape}")
        print(f"  Sample rate: {sample_rate}Hz")
        print(f"  Range: [{audio.min():.3f}, {audio.max():.3f}]")
        return True
        
    except Exception as e:
        print(f"✗ Audio generation failed: {e}")
        return False

async def test_basic_processing():
    """Test basic audio processing if models are available."""
    print("\nTesting basic audio processing...")
    try:
        from core.stt_engine import A2STTEngine
        
        # Create engine
        engine = A2STTEngine(enable_emotion=False)
        
        # Generate test audio
        audio = np.random.randn(48000).astype(np.float32) * 0.1
        
        # Process audio
        print("  Processing 3 seconds of test audio...")
        result = await engine.process_audio(audio)
        
        print(f"✓ Processing successful!")
        print(f"  Text: '{result.text}'")
        print(f"  Confidence: {result.confidence:.3f}")
        print(f"  Processing time: {result.processing_time:.3f}s")
        return True
        
    except Exception as e:
        print(f"✗ Audio processing failed: {e}")
        return False

def main():
    """Run all demo tests."""
    print("A2 STT System Demo")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_stt_result,
        test_audio_generation,
        test_engine_creation,
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    # Test async processing if basic tests pass
    if all(results):
        print("\nRunning async processing test...")
        try:
            result = asyncio.run(test_basic_processing())
            results.append(result)
        except Exception as e:
            print(f"Async test failed: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 50)
    print("Demo Summary:")
    passed = sum(results)
    total = len(results)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All tests passed! STT system is ready.")
    elif passed >= 3:
        print("⚠ Basic functionality works. Download models to enable full features.")
        print("  Run: python3 scripts/download_models.py")
    else:
        print("✗ Basic setup issues detected. Check dependencies.")
        print("  Run: pip install -r requirements.txt")

if __name__ == "__main__":
    main() 