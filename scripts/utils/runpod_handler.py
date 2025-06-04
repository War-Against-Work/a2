#!/usr/bin/env python3
"""
RunPod Serverless Handler for A2 STT API
This is what should be the main entry point for RunPod serverless
"""

import runpod
import sys
import os
import base64
import io
import json
import logging
import time
from pathlib import Path

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Audio processing
import numpy as np
import librosa

# Our modules
from logging_config import setup_a2_stt_logging, get_logger

# Initialize logging
setup_a2_stt_logging(log_level="INFO")
logger = get_logger('A2_STT_RUNPOD')

# Global STT engine instance
stt_engine = None

def initialize_stt_engine():
    """Initialize the STT engine once"""
    global stt_engine
    if stt_engine is None:
        try:
            logger.info(" Initializing STT engine...")
            
            # Import and initialize STT engine
            from src.core.stt_engine import STTSTT
            stt_engine = STTSTT()
            
            logger.info(" STT engine initialized successfully")
            return True
        except Exception as e:
            logger.error(f" Failed to initialize STT engine: {e}")
            import traceback
            traceback.print_exc()
            return False
    return True

def process_audio_data(audio_data: str, sample_rate: int = 16000) -> dict:
    """Process base64 encoded audio data"""
    try:
        # Decode base64 audio
        audio_bytes = base64.b64decode(audio_data)
        
        # Convert to numpy array
        audio_buffer = io.BytesIO(audio_bytes)
        audio_array, sr = librosa.load(audio_buffer, sr=sample_rate, dtype=np.float32)
        
        logger.info(f" Processing audio: {len(audio_array)} samples at {sr}Hz")
        
        # Process with STT engine
        if not initialize_stt_engine():
            raise Exception("STT engine not available")
        
        start_time = time.time()
        result = stt_engine.transcribe(audio_array, sr)
        processing_time = time.time() - start_time
        
        logger.info(f" Transcription completed in {processing_time:.2f}s")
        
        return {
            "text": result.get("text", ""),
            "confidence": result.get("confidence", 0.0),
            "emotion": result.get("emotion", "neutral"),
            "arousal": result.get("arousal", 0.0),
            "processing_time": processing_time
        }
        
    except Exception as e:
        logger.error(f" Audio processing failed: {e}")
        import traceback
        traceback.print_exc()
        raise

def handler(event):
    """
    RunPod serverless handler function
    This is the main entry point that RunPod calls
    """
    try:
        logger.info(f" Received request: {event}")
        
        # Get input from event
        input_data = event.get("input", {})
        
        # Handle different endpoint types
        endpoint = input_data.get("endpoint", "/process-audio")
        
        if endpoint == "/health":
            # Health check
            logger.info(" Health check requested")
            
            # Initialize STT engine to verify it works
            engine_status = initialize_stt_engine()
            
            return {
                "status": "healthy" if engine_status else "unhealthy",
                "message": "A2 STT API is running" if engine_status else "STT engine failed to initialize",
                "version": "1.0.0",
                "model_loaded": engine_status,
                "timestamp": time.time()
            }
            
        elif endpoint == "/process-audio":
            # Audio processing
            audio_data = input_data.get("audio_data")
            if not audio_data:
                raise ValueError("Missing audio_data in request")
            
            sample_rate = input_data.get("sample_rate", 16000)
            
            logger.info(" Processing audio request")
            result = process_audio_data(audio_data, sample_rate)
            
            return {
                "success": True,
                "result": result
            }
            
        elif endpoint == "/models":
            # Model information
            return {
                "models": [
                    {
                        "name": "whisper-large-v3",
                        "type": "speech-to-text",
                        "language": "multilingual",
                        "status": "loaded" if stt_engine else "not_loaded"
                    }
                ]
            }
            
        else:
            raise ValueError(f"Unknown endpoint: {endpoint}")
            
    except Exception as e:
        logger.error(f" Handler error: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            "error": str(e),
            "success": False,
            "traceback": traceback.format_exc()
        }

if __name__ == "__main__":
    # For local testing
    # Test the handler locally
    test_event = {
        "input": {
            "endpoint": "/health"
        }
    }
    
    print(" Testing handler locally...")
    result = handler(test_event)
    print(f"Result: {result}")
    
    # Start RunPod serverless
    logger.info(" Starting RunPod serverless handler...")
    runpod.serverless.start({"handler": handler})
