# A2 Robot Core Documentation

This repository contains the central documentation and architecture specifications for the A2 Robot project - a head/neck assembly with Multi-LLM Swarm Architecture.

## Repository Structure

- 📂 **docs/** - Documentation files
  - 📂 **architecture/** - System architecture documentation
  - 📂 **specifications/** - Detailed specifications
  - 📂 **diagrams/** - System diagrams and visual documentation

## Related Repositories

- [a2-ros-ws](https://github.com/aaronlax/a2-ros-ws) - ROS 2 workspace with all robot software packages
- [a2-llm-containers](https://github.com/aaronlax/a2-llm-containers) - LLM containers and model training
- [a2-teensy-firmware](https://github.com/aaronlax/a2-teensy-firmware) - Teensy 4.1 firmware for real-time control
- [a2-pi-system](https://github.com/aaronlax/a2-pi-system) - Raspberry Pi system configuration

## Getting Started

See the [project-overview.md](docs/project-overview.md) for a complete introduction to the project.

## Architecture

The A2 Robot uses a Multi-LLM Swarm Architecture with three specialized LLMs based on Mistral 7B with role-specific LoRA adapters:

1. **Communication LLM** - Handles dialogue and expression
2. **Decision LLM** - Manages goals and behavior
3. **Motion LLM** - Controls physical movement

These LLMs interact through a Shared State System to create coordinated, emergent behavior.

See [brain-architecture.md](docs/brain-architecture.md) for details.
