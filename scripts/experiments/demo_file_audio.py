#!/usr/bin/env python3
"""
A2 STT File Audio Demo - Process audio files with your voice!
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
    """Check if audio file processing dependencies are available."""
    try:
        import scipy.io.wavfile as wavfile
        import librosa
        return True, (wavfile, librosa)
    except ImportError as e:
        return False, str(e)

def load_audio_file(filepath, target_sr=16000):
    """Load and process audio file."""
    logger = get_logger('FileAudioDemo')
    
    try:
        import librosa
        
        logger.info(f"📁 Loading audio file: {filepath}")
        
        # Load audio with librosa (handles many formats)
        audio, sr = librosa.load(filepath, sr=target_sr, mono=True)
        
        logger.info(f"✓ Audio loaded successfully!")
        logger.info(f"  Duration: {len(audio)/sr:.2f} seconds")
        logger.info(f"  Sample rate: {sr} Hz")
        logger.info(f"  Shape: {audio.shape}")
        logger.info(f"  Range: [{audio.min():.3f}, {audio.max():.3f}]")
        
        # Check if audio is too quiet
        if np.abs(audio).max() < 0.001:
            logger.warning("⚠ Very quiet audio detected")
        
        return audio.astype(np.float32)
        
    except Exception as e:
        logger.error(f"✗ Failed to load audio file: {e}")
        return None

def create_sample_audio():
    """Create a sample audio file with speech-like characteristics."""
    logger = get_logger('FileAudioDemo')
    
    try:
        import scipy.io.wavfile as wavfile
        
        logger.info("🎵 Creating sample audio file...")
        
        # Generate more realistic speech-like audio
        duration = 3.0
        sample_rate = 16000
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # Create formant-like frequencies (speech characteristics)
        f1 = 800   # First formant
        f2 = 1200  # Second formant
        f3 = 2400  # Third formant
        
        # Generate speech-like signal
        audio = (
            0.3 * np.sin(2 * np.pi * f1 * t) * np.exp(-t * 0.5) +
            0.2 * np.sin(2 * np.pi * f2 * t) * np.exp(-t * 0.3) +
            0.1 * np.sin(2 * np.pi * f3 * t) * np.exp(-t * 0.7)
        )
        
        # Add some noise for realism
        noise = np.random.normal(0, 0.02, len(audio))
        audio = audio + noise
        
        # Apply envelope to simulate speech patterns
        envelope = np.ones_like(t)
        # Add some pauses
        envelope[int(0.8*sample_rate):int(1.2*sample_rate)] *= 0.1
        envelope[int(2.0*sample_rate):int(2.3*sample_rate)] *= 0.1
        
        audio = audio * envelope
        
        # Normalize
        audio = audio / np.abs(audio).max() * 0.7
        
        # Save as WAV file
        sample_file = "sample_speech.wav"
        wavfile.write(sample_file, sample_rate, (audio * 32767).astype(np.int16))
        
        logger.info(f"✓ Sample audio created: {sample_file}")
        return sample_file
        
    except Exception as e:
        logger.error(f"✗ Failed to create sample audio: {e}")
        return None

async def process_audio_file(engine, filepath):
    """Process an audio file through the STT engine."""
    logger = get_logger('FileAudioDemo')
    
    # Load audio
    audio = load_audio_file(filepath)
    if audio is None:
        return False
    
    # Process with STT
    logger.info("🔄 Processing with STT engine...")
    try:
        result = await engine.process_audio(audio, sample_rate=16000)
        
        logger.info("✨ STT Results:")
        logger.info(f"  📝 Transcription: '{result.text}'")
        logger.info(f"  📊 Confidence: {result.confidence:.1f}%")
        logger.info(f"  😊 Emotion: {result.emotion} (arousal: {result.arousal:.2f})")
        logger.info(f"  ⏱️  Processing time: {result.processing_time:.3f}s")
        
        # Calculate real-time factor
        audio_duration = len(audio) / 16000
        rtf = audio_duration / result.processing_time
        logger.info(f"  🚀 Real-time factor: {rtf:.1f}x")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ STT processing failed: {e}")
        return False

async def main():
    """Main file audio demo."""
    
    # Setup logging
    setup_a2_stt_logging(log_level="INFO")
    logger = get_logger('FileAudioDemo')
    
    logger.info("📁 A2 STT File Audio Demo")
    logger.info("=" * 50)
    
    # Check audio dependencies
    logger.info("Checking audio file dependencies...")
    has_audio, error_or_modules = check_audio_dependencies()
    
    if not has_audio:
        logger.error(f"✗ Audio dependencies not found: {error_or_modules}")
        logger.error("Install with: pip install librosa")
        return
    
    logger.info("✓ Audio file dependencies available")
    
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
    logger.info("📁 File Audio Processing Options:")
    logger.info("  1. Process existing audio file")
    logger.info("  2. Create and process sample audio")
    logger.info("  3. Quit")
    logger.info("=" * 50)
    
    while True:
        try:
            choice = input("\nEnter your choice (1/2/3): ").strip()
            
            if choice == "3" or choice.lower() in ['quit', 'exit', 'q']:
                logger.info("👋 Goodbye!")
                break
            
            elif choice == "1":
                filepath = input("Enter path to audio file (WAV, MP3, etc.): ").strip()
                
                if not os.path.exists(filepath):
                    logger.error(f"File not found: {filepath}")
                    continue
                
                await process_audio_file(engine, filepath)
            
            elif choice == "2":
                logger.info("Creating sample speech-like audio...")
                sample_file = create_sample_audio()
                
                if sample_file:
                    logger.info(f"Sample created: {sample_file}")
                    await process_audio_file(engine, sample_file)
            
            else:
                logger.warning("Invalid choice. Please enter 1, 2, or 3.")
                
        except KeyboardInterrupt:
            logger.info("\n👋 Demo interrupted by user")
            break
        except Exception as e:
            logger.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
