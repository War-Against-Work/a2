# A2 Project Scripts

## Overview
Centralized location for all A2 project scripts, organized by function and purpose.

## Directory Structure

### setup/
One-time setup scripts for environments and dependencies.
- Environment setup scripts
- Dependency installation
- Initial configuration

### utils/
Reusable utility scripts for common operations.
- RunPod endpoint management
- Documentation validation
- System maintenance
- API utilities

### validation/
Testing and validation scripts.
- Documentation validation
- System health checks
- Integration tests
- Performance benchmarks

### experiments/
Experimental and temporary test scripts.
- POC demos
- Performance tests
- Feature experiments
- Should be dated when created

### deprecated/
Old scripts kept for reference.
- No longer maintained
- May not work with current system
- Retained for historical reference

## Naming Conventions

1. **Use descriptive names**: 
   - ✅ `validate_documentation.py`
   - ❌ `test.py`

2. **Include component prefix**:
   - ✅ `stt_benchmark.py`
   - ✅ `teensy_flash.sh`
   - ❌ `benchmark.py`

3. **Date experimental scripts**:
   - ✅ `experiment_2025_05_27_audio_latency.py`
   - ❌ `audio_test.py`

## Script Categories

### RunPod Management (utils/)
- `runpod_endpoint_manager.py` - Main endpoint management tool
- `runpod_deploy.py` - Deployment utilities
- `fix_runpod_*.py` - Troubleshooting scripts
- `check_runpod_*.py` - Status checking utilities

### STT Testing (experiments/)
- `demo_*.py` - Various STT demo scripts
- `test_*.py` - STT testing scripts

### Documentation (validation/)
- `validate_docs.py` - Document validation
- `check_links.py` - Link checker
- `generate_doc_index.py` - Index generator

## Usage Guidelines

1. **Before creating a new script**, check if similar functionality exists
2. **Add documentation** to complex scripts (docstrings, comments)
3. **Move scripts** to appropriate directories as they mature
4. **Date experimental scripts** to track their relevance
5. **Clean up** experiments older than 3 months

## Adding New Scripts

1. Choose the appropriate directory based on script purpose
2. Use descriptive naming following conventions
3. Add a header comment explaining the script's purpose
4. Update this README if adding a new category

Example header:
```python
#!/usr/bin/env python3
"""
Script: validate_sensor_data.py
Purpose: Validates sensor data format and ranges
Author: [Your Name]
Date: 2025-05-27
"""
```