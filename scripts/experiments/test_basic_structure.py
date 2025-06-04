#!/usr/bin/env python3
"""
Basic structure test for A2 STT system.
Tests imports and basic functionality without external dependencies.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append('src')

def test_imports():
    """Test that the core module structure is correct."""
    print("Testing basic imports...")
    try:
        # Test if we can import the module structure
        import core.stt_engine
        print("✓ Core STT engine module found")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_class_definitions():
    """Test that classes are defined correctly."""
    print("\nTesting class definitions...")
    try:
        from core.stt_engine import STTResult, A2STTEngine
        print("✓ STTResult and A2STTEngine classes found")
        
        # Test STTResult creation (without external deps)
        result = STTResult(
            text="test",
            emotion="neutral",
            arousal=0.5,
            confidence=0.9,
            processing_time=0.1,
            detected_events=[]
        )
        print(f"✓ STTResult created: {result.text}")
        return True
    except Exception as e:
        print(f"✗ Class definition error: {e}")
        return False

def test_file_structure():
    """Test that all required files exist."""
    print("\nTesting file structure...")
    required_files = [
        "requirements.txt",
        "setup_stt_env.sh", 
        "scripts/download_models.py",
        "src/core/stt_engine.py",
        "tests/test_stt_basic.py",
        "benchmarks/benchmark_models.py",
        "README.md"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"✗ Missing files: {missing_files}")
        return False
    else:
        print(f"✓ All {len(required_files)} required files found")
        return True

def test_directory_structure():
    """Test that all required directories exist."""
    print("\nTesting directory structure...")
    required_dirs = [
        "src/core",
        "src/ros_nodes", 
        "src/utils",
        "models/distil-whisper",
        "models/sensevoice",
        "tests",
        "benchmarks",
        "configs",
        "scripts"
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            missing_dirs.append(dir_path)
    
    if missing_dirs:
        print(f"✗ Missing directories: {missing_dirs}")
        return False
    else:
        print(f"✓ All {len(required_dirs)} required directories found")
        return True

def main():
    """Run all basic structure tests."""
    print("A2 STT Basic Structure Test")
    print("=" * 50)
    
    tests = [
        test_file_structure,
        test_directory_structure,
        test_imports,
        test_class_definitions,
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    # Summary
    print("\n" + "=" * 50)
    print("Structure Test Summary:")
    passed = sum(results)
    total = len(results)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All structure tests passed! Ready for environment setup.")
        print("\nNext steps:")
        print("1. Run: ./setup_stt_env.sh")
        print("2. Activate environment: conda activate a2_stt")
        print("3. Test with models: python3 demo.py")
    else:
        print("✗ Some structure issues detected.")
        
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 