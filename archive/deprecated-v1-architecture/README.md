# A2 Robot: Deprecated V1 Architecture Documentation

## Overview

This archive contains documentation from the original A2 Robot architecture that has been superseded by the June 2025 refined architecture revision. These documents are preserved for historical reference and potential future use.

## Archived Components

### Stewart Platform System
- **`stewart-platform-design.md`** - Original 6-DOF Stewart platform design
- **`stewart-platform-firmware.md`** - L16 actuator control firmware
- **`stewart-platform-quickstart.md`** - Implementation guide
- **`stewart-platform-cad-reference.md`** - CAD specifications

### Rationale for Archival

The June 2025 architecture revision focused on achieving Apple-grade motion fluidity through:

1. **1kHz Servo Control**: Moved from 100Hz ROS 2 control to 1kHz Teensy-based control
2. **Impedance Overlay**: Added 500Hz virtual spring-damper model for smooth motion
3. **Antenna Expression System**: Introduced MG996R + LX224 servos for emotional expressions
4. **Hardware Efficiency**: Achieved major quality upgrade with only $120 additional investment

The Stewart platform remains a valuable future enhancement but was deprioritized in favor of:
- Immediate motion quality improvements
- Hardware investment efficiency
- Development timeline acceleration
- Complexity reduction for Phase 1

## Current Architecture Benefits

**Achieved with Refined Architecture:**
- Apple-grade motion fluidity (1kHz control loop)
- Rich emotional expression (antenna system)
- Full compatibility with existing XL430/XL330 servos
- Minimal additional hardware cost ($120)
- Reduced development complexity

**Deferred to Future Phases:**
- Stewart platform 6-DOF base motion
- Full body expressiveness
- Complex spatial positioning

## Future Integration Path

The Stewart platform documentation is preserved because:

1. **Hardware Investment**: 6× L16-100-35-12-P actuators remain available
2. **Proven Design**: Stewart platform kinematics are well-established
3. **Scalability**: Can be integrated after head/antenna system validation
4. **User Request**: May be reactivated based on user preferences

When ready to reintegrate:
1. Review archived documentation for current relevance
2. Update for refined architecture (1kHz control, impedance overlay)
3. Integrate with antenna expression system for full-body coordination
4. Validate combined system performance

## Document Status

- **Archived Date**: 2025-06-11
- **Superseded By**: Refined Architecture v2.0.0
- **Preservation Reason**: Future enhancement potential
- **Integration Complexity**: Medium (requires control stack integration)

This archive ensures that the substantial engineering work on the Stewart platform is preserved while allowing the project to focus on immediate motion quality and expression improvements.
