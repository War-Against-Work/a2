#!/usr/bin/env python3
"""
A2 STT System Demo with Enhanced Logging
"""

import sys
import os
import logging
import asyncio
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Setup logging
def setup_logging():
    """Setup comprehensive logging for the demo."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"a2_stt_demo_{timestamp}.log"
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger('A2_STT_Demo')
    logger.info(f"Logging initialized. Log file: {log_file}")
    return logger

def test_imports(logger):
    """Test core imports with logging."""
    logger.info("Testing imports...")
    try:
        from core.stt_engine import A2STTEngine, STTResult
        logger.info("✓ Core STT engine imports successful")
        return True, (A2STTEngine, STTResult)
    except ImportError as e:
        logger.error(f"✗ Import error: {e}")
        return False, None

def test_stt_result(logger, STTResult):
    """Test STTResult dataclass with logging."""
    logger.info("Testing STTResult dataclass...")
    try:
        result = STTResult(
            text="hello A2",
            emotion="neutral",
            arousal=0.5,
            confidence=0.95,
            processing_time=0.1,
            detected_events=[]
        )
        logger.info(f"✓ STTResult created: {result.text}")
        logger.info(f"  Emotion: {result.emotion}")
        logger.info(f"  Confidence: {result.confidence}")
        return True
    except Exception as e:
        logger.error(f"✗ STTResult test failed: {e}")
        return False

def test_audio_generation(logger):
    """Test audio generation with logging."""
    logger.info("Testing audio generation...")
    try:
        import numpy as np
        
        duration = 3.0
        sample_rate = 16000
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # Generate test audio (sine wave)
        frequency = 440  # A4 note
        audio = 0.3 * np.sin(2 * np.pi * frequency * t)
        audio = audio.astype(np.float32)
        
        logger.info(f"✓ Generated {duration}s of test audio")
        logger.info(f"  Shape: {audio.shape}")
        logger.info(f"  Sample rate: {sample_rate}Hz")
        logger.info(f"  Range: [{audio.min():.3f}, {audio.max():.3f}]")
        return True, audio
    except Exception as e:
        logger.error(f"✗ Audio generation failed: {e}")
        return False, None

def test_engine_creation(logger, A2STTEngine):
    """Test engine creation with logging."""
    logger.info("Testing engine creation...")
    logger.info("  Note: This will fail if models aren't downloaded yet")
    logger.info("  Run 'python3 scripts/download_models.py' first")
    
    try:
        engine = A2STTEngine(enable_emotion=False)  # Disable emotion for now
        logger.info("✓ Engine created successfully!")
        logger.info(f"  Custom vocab loaded: {len(engine.custom_vocab['commands'])} commands")
        return True, engine
    except Exception as e:
        logger.error(f"✗ Engine creation failed: {e}")
        logger.error("  This is expected if models aren't downloaded yet")
        return False, None

async def test_basic_processing(logger, engine, audio):
    """Test basic audio processing with logging."""
    logger.info("Testing basic audio processing...")
    
    try:
        logger.info("  Processing 3 seconds of test audio...")
        result = await engine.process_audio(audio, sample_rate=16000)
        
        logger.info("✓ Processing successful!")
        logger.info(f"  Text: '{result.text}'")
        logger.info(f"  Confidence: {result.confidence:.3f}")
        logger.info(f"  Processing time: {result.processing_time:.3f}s")
        return True
    except Exception as e:
        logger.error(f"✗ Processing failed: {e}")
        logger.exception("Full traceback:")
        return False

async def main():
    """Main demo function with comprehensive logging."""
    logger = setup_logging()
    
    logger.info("A2 STT System Demo with Logging")
    logger.info("=" * 50)
    
    tests_passed = 0
    total_tests = 5
    
    # Test 1: Imports
    success, imports = test_imports(logger)
    if success:
        tests_passed += 1
        A2STTEngine, STTResult = imports
    else:
        logger.error("Cannot continue without imports")
        return
    
    # Test 2: STTResult
    if test_stt_result(logger, STTResult):
        tests_passed += 1
    
    # Test 3: Audio generation
    success, audio = test_audio_generation(logger)
    if success:
        tests_passed += 1
    
    # Test 4: Engine creation
    success, engine = test_engine_creation(logger, A2STTEngine)
    if success:
        tests_passed += 1
        
        # Test 5: Basic processing (only if engine created)
        logger.info("\nRunning async processing test...")
        if await test_basic_processing(logger, engine, audio):
            tests_passed += 1
    
    # Summary
    logger.info("=" * 50)
    logger.info("Demo Summary:")
    logger.info(f"Tests passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        logger.info("✓ All tests passed! STT system is ready.")
    elif tests_passed >= 4:
        logger.warning("⚠ Most tests passed. Basic functionality works.")
        logger.warning("  Full features require model downloads.")
    else:
        logger.error("✗ Multiple test failures detected.")
        logger.error("  Check logs for details and ensure setup is complete.")

if __name__ == "__main__":
    asyncio.run(main())
