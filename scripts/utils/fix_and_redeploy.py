#!/usr/bin/env python3
"""
Quick fix and redeploy script for the STT engine import issue
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        if result.stdout:
            print(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"Stdout: {e.stdout}")
        if e.stderr:
            print(f"Stderr: {e.stderr}")
        return False

def main():
    print("🚀 Fixing and redeploying A2 STT API...")
    
    # Change to the correct directory
    os.chdir('/home/waragainstwork/A2/a2-stt')
    
    # Build the Docker image with the fixed handler
    if not run_command(
        "docker build -f Dockerfile.runpod -t aaronlax/a2-stt-api:fixed .",
        "Building Docker image with fixed handler"
    ):
        return False
    
    # Push the fixed image
    if not run_command(
        "docker push aaronlax/a2-stt-api:fixed",
        "Pushing fixed Docker image"
    ):
        return False
    
    print("✅ Fixed image pushed successfully!")
    print("🔄 Now you need to update your RunPod endpoint to use: aaronlax/a2-stt-api:fixed")
    print("📝 Or create a new endpoint with the fixed image")
    
    return True

if __name__ == "__main__":
    main()
