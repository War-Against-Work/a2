#!/usr/bin/env python3
"""
A2 STT System Production Demo with Full Logging
"""

import sys
import os
import asyncio
from pathlib import Path

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import our logging configuration
from logging_config import setup_a2_stt_logging, get_logger, log_async_performance

def main():
    """Main production demo with comprehensive logging."""
    
    # Setup logging
    setup_a2_stt_logging(
        log_level="INFO",
        log_to_file=True,
        log_to_console=True
    )
    
    logger = get_logger('A2_STT_Production_Demo')
    
    try:
        # Run the demo
        asyncio.run(run_demo(logger))
    except KeyboardInterrupt:
        logger.info("Demo interrupted by user")
    except Exception as e:
        logger.error(f"Demo failed with error: {e}")
        logger.exception("Full traceback:")
        sys.exit(1)

@log_async_performance
async def run_demo(logger):
    """Run the production demo with full logging."""
    
    logger.info("Starting A2 STT Production Demo")
    logger.info("=" * 60)
    
    # Test imports
    logger.info("Testing core imports...")
    try:
        from core.stt_engine import A2STTEngine, STTResult
        logger.info("✓ Core STT engine imports successful")
    except ImportError as e:
        logger.error(f"✗ Import error: {e}")
        return
    
    # Test STTResult
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
    except Exception as e:
        logger.error(f"✗ STTResult test failed: {e}")
        return
    
    # Generate test audio
    logger.info("Generating test audio...")
    try:
        import numpy as np
        
        duration = 3.0
        sample_rate = 16000
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # Generate more complex test audio (multiple frequencies)
        audio = (
            0.3 * np.sin(2 * np.pi * 440 * t) +  # A4
            0.2 * np.sin(2 * np.pi * 880 * t) +  # A5
            0.1 * np.sin(2 * np.pi * 220 * t)    # A3
        )
        
        # Add envelope to make it more speech-like
        envelope = np.exp(-t * 0.5)
        audio = audio * envelope
        audio = audio.astype(np.float32)
        
        logger.info(f"✓ Generated {duration}s test audio")
        logger.debug(f"Audio shape: {audio.shape}, range: [{audio.min():.3f}, {audio.max():.3f}]")
        
    except Exception as e:
        logger.error(f"✗ Audio generation failed: {e}")
        return
    
    # Create STT engine
    logger.info("Creating STT engine...")
    try:
        engine = A2STTEngine(enable_emotion=False)
        logger.info("✓ STT engine created successfully")
        logger.info(f"Custom vocabulary: {len(engine.custom_vocab['commands'])} commands loaded")
        
    except Exception as e:
        logger.error(f"✗ Engine creation failed: {e}")
        logger.error("Ensure models are downloaded: python3 scripts/download_models.py")
        return
    
    # Process audio
    logger.info("Processing test audio...")
    try:
        result = await engine.process_audio(audio, sample_rate=16000)
        
        logger.info("✓ Audio processing successful!")
        logger.info(f"Transcription: '{result.text}'")
        logger.info(f"Confidence: {result.confidence:.1f}%")
        logger.info(f"Processing time: {result.processing_time:.3f}s")
        logger.info(f"Emotion: {result.emotion} (arousal: {result.arousal:.2f})")
        
        if result.detected_events:
            logger.info(f"Detected events: {result.detected_events}")
        
        # Performance metrics
        audio_duration = len(audio) / sample_rate
        real_time_factor = audio_duration / result.processing_time
        logger.info(f"Real-time factor: {real_time_factor:.1f}x")
        
    except Exception as e:
        logger.error(f"✗ Audio processing failed: {e}")
        logger.exception("Processing error details:")
        return
    
    logger.info("=" * 60)
    logger.info("✓ A2 STT Production Demo completed successfully!")
    logger.info("System is ready for production use.")

if __name__ == "__main__":
    main()
