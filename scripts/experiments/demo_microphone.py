#!/usr/bin/env python3
"""
A2 STT Real Microphone Demo - Speak and see transcription!
"""

import sys
import os
import asyncio
import numpy as np
from pathlib import Path

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import our logging configuration
from logging_config import setup_a2_stt_logging, get_logger

def check_audio_dependencies():
    """Check if audio recording dependencies are available."""
    try:
        import sounddevice as sd
        import scipy.io.wavfile as wavfile
        return True, (sd, wavfile)
    except ImportError:
        return False, None

def list_audio_devices(sd):
    """List available audio input devices."""
    logger = get_logger('MicrophoneDemo')
    logger.info("Available audio input devices:")
    
    devices = sd.query_devices()
    input_devices = []
    
    for i, device in enumerate(devices):
        if device['max_input_channels'] > 0:
            logger.info(f"  {i}: {device['name']} (channels: {device['max_input_channels']})")
            input_devices.append(i)
    
    return input_devices

def record_audio(sd, duration=5, sample_rate=16000, device=None):
    """Record audio from microphone."""
    logger = get_logger('MicrophoneDemo')
    
    logger.info(f"🎤 Recording for {duration} seconds...")
    logger.info("Start speaking now!")
    
    try:
        # Record audio
        audio = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype=np.float32,
            device=device
        )
        
        # Wait for recording to complete
        sd.wait()
        
        # Convert to 1D array
        audio = audio.flatten()
        
        logger.info("✓ Recording completed!")
        logger.debug(f"Audio shape: {audio.shape}, range: [{audio.min():.3f}, {audio.max():.3f}]")
        
        # Check if audio was actually recorded (not silent)
        if np.abs(audio).max() < 0.001:
            logger.warning("⚠ Very quiet audio detected - check microphone volume")
        
        return audio
        
    except Exception as e:
        logger.error(f"✗ Recording failed: {e}")
        return None

async def main():
    """Main microphone demo."""
    
    # Setup logging
    setup_a2_stt_logging(log_level="INFO")
    logger = get_logger('MicrophoneDemo')
    
    logger.info("🎙️  A2 STT Real Microphone Demo")
    logger.info("=" * 50)
    
    # Check audio dependencies
    logger.info("Checking audio dependencies...")
    has_audio, audio_modules = check_audio_dependencies()
    
    if not has_audio:
        logger.error("✗ Audio dependencies not found!")
        logger.error("Install with: pip install sounddevice scipy")
        return
    
    sd, wavfile = audio_modules
    logger.info("✓ Audio dependencies available")
    
    # List audio devices
    input_devices = list_audio_devices(sd)
    
    if not input_devices:
        logger.error("✗ No audio input devices found!")
        return
    
    # Import STT engine
    logger.info("Loading STT engine...")
    try:
        from core.stt_engine import A2STTEngine
        engine = A2STTEngine(enable_emotion=False)
        logger.info("✓ STT engine ready!")
    except Exception as e:
        logger.error(f"✗ Failed to load STT engine: {e}")
        return
    
    # Interactive loop
    logger.info("\n" + "=" * 50)
    logger.info("🎤 Ready for voice input!")
    logger.info("Commands:")
    logger.info("  - Press ENTER to record 5 seconds")
    logger.info("  - Type 'quit' to exit")
    logger.info("=" * 50)
    
    while True:
        try:
            user_input = input("\nPress ENTER to record (or 'quit' to exit): ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                logger.info("👋 Goodbye!")
                break
            
            # Record audio
            audio = record_audio(sd, duration=5, sample_rate=16000)
            
            if audio is None:
                logger.error("Recording failed, try again")
                continue
            
            # Process with STT
            logger.info("🔄 Processing audio...")
            try:
                result = await engine.process_audio(audio, sample_rate=16000)
                
                logger.info("✨ Results:")
                logger.info(f"  📝 Text: '{result.text}'")
                logger.info(f"  📊 Confidence: {result.confidence:.1f}%")
                logger.info(f"  ⏱️  Processing time: {result.processing_time:.3f}s")
                
                # Check for custom commands
                if result.text.lower() in ['stop', 'quit', 'exit']:
                    logger.info("🛑 Stop command detected, exiting...")
                    break
                    
            except Exception as e:
                logger.error(f"✗ Processing failed: {e}")
                
        except KeyboardInterrupt:
            logger.info("\n👋 Demo interrupted by user")
            break
        except Exception as e:
            logger.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
