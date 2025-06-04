#!/bin/bash
# Deploy A2 LLM containers to RunPod cloud
set -e

echo "=== A2 Robot - Cloud LLM Deployment ==="

# Configuration
LLM_CONTAINERS=${LLM_CONTAINERS:-"llm-containers"}
RUNPOD_API_KEY=${RUNPOD_API_KEY:-""}

if [ -z "$RUNPOD_API_KEY" ]; then
    echo "Error: RUNPOD_API_KEY environment variable not set"
    echo "Set it with: export RUNPOD_API_KEY=your_api_key"
    exit 1
fi

echo "Deploying LLM containers to RunPod..."

# Check if submodule is initialized
if [ ! -d "$LLM_CONTAINERS/.git" ]; then
    echo "Error: LLM containers submodule not initialized"
    echo "Run: git submodule update --init --recursive"
    exit 1
fi

# Update submodule to latest
echo "Updating LLM containers submodule..."
git submodule update --remote $LLM_CONTAINERS

# Deploy to RunPod
cd $LLM_CONTAINERS
if [ -f "deploy_runpod.sh" ]; then
    echo "Running RunPod deployment script..."
    ./deploy_runpod.sh
elif [ -f "docker-compose.runpod.yml" ]; then
    echo "Building containers for RunPod..."
    docker-compose -f docker-compose.runpod.yml build
    
    echo "Pushing to registry..."
    docker-compose -f docker-compose.runpod.yml push
    
    echo "Creating RunPod endpoints..."
    python3 scripts/create_runpod_endpoints.py
else
    echo "Error: RunPod deployment scripts not found"
    exit 1
fi

echo "=== Cloud deployment complete! ==="
echo "Check RunPod dashboard for endpoint status"