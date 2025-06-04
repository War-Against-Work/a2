# A2 Robot Project - Monorepo

> An expressive robotic head with cloud-enhanced intelligence

A monorepo containing all components of the A2 expressive humanoid robot system, designed for distributed deployment across multiple physical and cloud platforms.

## Repository Structure

This monorepo orchestrates the following components as submodules:

```
A2/                          # Main orchestrator repository  
├── docs/                    # Documentation submodule → a2-docs
├── ros-workspace/           # ROS2 workspace → a2-ros-ws
├── stt-service/            # Speech-to-text service → a2-stt  
├── pi-system/              # Raspberry Pi system services → a2-pi-system
├── teensy-firmware/        # Teensy 4.1 firmware → a2-teensy-firmware
├── llm-containers/         # LLM containers for cloud → a2-llm-containers
├── control-interface/      # Control interface → a2-control-interface
├── deployment/             # Deployment scripts and configs
│   ├── configs/           # Deployment configurations
│   └── scripts/           # Deployment automation scripts
└── README.md              # This file
```

## What is A2?

A2 is a robotic head/neck assembly that can:
- 🎤 Understand speech and respond naturally
- 👀 Track faces and objects with expressive movements  
- 🤖 Display emotions through biomimetic motion primitives
- 💬 Generate contextual responses using cloud AI
- ⚡ React reflexively to environmental stimuli

## Deployment Architecture

### Physical Deployment Targets

1. **Raspberry Pi 5** (`ros-workspace/`, `pi-system/`)
   - ROS2 workspace with hardware interfaces
   - System services for robot control
   - Local sensor processing and motor control

2. **RTX 4080 Local System** (`stt-service/`, `control-interface/`)
   - High-performance speech-to-text processing
   - Control interface and monitoring dashboard
   - Local GPU compute for real-time processing

3. **Teensy 4.1 Microcontroller** (`teensy-firmware/`)
   - Real-time safety systems
   - Motor control and sensor interfaces
   - Hardware abstraction layer

4. **RunPod Cloud** (`llm-containers/`)
   - LLM inference containers
   - Cloud-based decision making
   - Scalable compute resources

### System Requirements

**Hardware:**
- Raspberry Pi 5 (8GB RAM)
- Teensy 4.1
- NVIDIA GPU with 16GB+ VRAM (RTX 4080 recommended)
- Ubuntu 22.04 or WSL2

**Software:**
- ROS 2 Humble
- Python 3.10+
- CUDA 12.0+
- Docker & Docker Compose

## Getting Started

### Prerequisites

- Git with submodule support
- Docker and Docker Compose
- ROS2 Humble (for Pi deployment)
- PlatformIO (for Teensy firmware)

### Clone with Submodules

```bash
git clone --recursive https://github.com/War-Against-Work/A2.git
cd A2

# If already cloned without --recursive:
git submodule update --init --recursive
```

### Component-Specific Setup

Each submodule has its own setup instructions:

- **Documentation**: See `docs/README.md`
- **ROS Workspace**: See `ros-workspace/README.md`
- **STT Service**: See `stt-service/README.md`
- **Pi System**: See `pi-system/README.md`
- **Teensy Firmware**: See `teensy-firmware/README.md`
- **LLM Containers**: See `llm-containers/README.md`
- **Control Interface**: See `control-interface/README.md`

### Deployment

Use the deployment scripts for target-specific deployment:

```bash
# Deploy to Raspberry Pi
./deployment/scripts/deploy-pi.sh

# Deploy STT service to RTX 4080 system
./deployment/scripts/deploy-stt.sh

# Deploy LLM containers to RunPod
./deployment/scripts/deploy-cloud.sh

# Flash firmware to Teensy
./deployment/scripts/deploy-teensy.sh
```

## Development Workflow

### Working with Submodules

```bash
# Update all submodules to latest
git submodule update --remote

# Work on a specific component
cd ros-workspace
# Make changes, commit, push to component repo

# Update main repo to point to new commit
cd ..
git add ros-workspace
git commit -m "Update ros-workspace to latest version"
```

### Component Development

Each component can be developed independently:

1. Navigate to the component directory
2. Create feature branches as needed
3. Commit and push to the component repository
4. Update the main monorepo to reference new commits

## Key Documentation

Once submodules are set up, documentation will be available at:

**Start Here:**
1. 📋 [docs/reports/ROADMAP.md](docs/reports/ROADMAP.md) - 8-week implementation plan
2. 🏗️ [docs/architecture/ARCHITECTURE.md](docs/architecture/ARCHITECTURE.md) - System design overview
3. 📚 [docs/DOCUMENTATION-INDEX.md](docs/DOCUMENTATION-INDEX.md) - All docs organized

**Hardware Setup:**
- [docs/hardware/bill-of-materials.md](docs/hardware/bill-of-materials.md) - Parts list
- [docs/hardware/wiring-guide.md](docs/hardware/wiring-guide.md) - Electrical connections
- [docs/hardware/sensor-configuration-guide.md](docs/hardware/sensor-configuration-guide.md) - I2C setup

**Software Development:**
- [docs/guides/local-development-setup.md](docs/guides/local-development-setup.md)
- [docs/architecture/interfaces-definition.md](docs/architecture/interfaces-definition.md)
- [docs/software/](docs/software/) - Software architecture guides

## Architecture Overview

```
┌─────────────┐     ┌─────────────┐     ┌──────────────┐
│   Sensors   │────▶│ Raspberry   │────▶│    Cloud     │
│  (100 Hz)   │     │   Pi 5      │     │   Services   │
└─────────────┘     │  (ROS 2)    │     │   (LLMs)     │
                    └──────┬──────┘     └──────────────┘
                           │
                    ┌──────▼──────┐
                    │  Teensy 4.1 │
                    │  (Safety)   │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  Actuators  │
                    │ (Dynamixel) │
                    └─────────────┘
```

## Contributing

1. Fork the relevant component repository
2. Create a feature branch
3. Make your changes and test thoroughly
4. Submit a pull request to the component repository
5. Update this monorepo to reference the new version

For detailed contribution guidelines, see individual component repositories.

## Troubleshooting

**Common Issues:**

- **Submodule Issues:** Run `git submodule update --init --recursive`
- **WSL2 Network Access:** See [docs/guides/WSL-NETWORK-ACCESS-GUIDE.md](docs/guides/WSL-NETWORK-ACCESS-GUIDE.md)
- **Teensy Not Detected:** Check USB permissions and udev rules
- **ROS 2 Topics Missing:** Source the workspace: `source ros-workspace/install/setup.bash`
- **GPU Out of Memory:** Check [docs/software/gpu-compute-strategy.md](docs/software/gpu-compute-strategy.md)

## Support

- Documentation: `docs/`
- Issues: Component-specific GitHub issues
- Architecture Questions: See `docs/architecture/`

## License

See individual component repositories for license information.