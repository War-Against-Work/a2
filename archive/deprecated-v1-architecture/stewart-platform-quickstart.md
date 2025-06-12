---
title: "Stewart Platform Quick Start Guide"
type: guide
status: active
created: "2025-01-01"
updated: "2025-01-01"
---

# Stewart Platform Quick Start Guide

> **Document Status:** CURRENT
> **Last Updated:** 2025-06-05
> **Version:** 1.0.0
> **Scope:** Phase 1

## Overview

Quick reference for building and programming the 6-DOF Stewart platform neck base for A2.

## Parts List

### Required Components
- **6x** Actuonix L16-100-35-12-P linear actuators
- **6x** DRV8871 motor drivers (HiLetgo or similar)
- **12x** 20mm ball joint rod ends (M5 or M6 thread)
- **1x** Teensy 4.1
- **1x** LRS-350-12 power supply (already in BOM)
- **6x** 1000µF capacitors
- **1x** 0.2Ω resistors (6 pack for current limiting)
- Shielded cable for position feedback

### 3D Printed Parts
- Base plate (200mm radius, 10-15mm thick)
- Top plate (150mm radius, 10-15mm thick)
- Ball joint sockets (if printing custom)

## Wiring Quick Reference

### DRV8871 Connections (per driver)
| DRV8871 | Connect To | Notes |
|---------|------------|-------|
| VM | 12V Bus | Add 1000µF cap |
| GND | Star Ground | |
| IN1 | Teensy PWM | See pin table |
| IN2 | Ground | Single-pin mode |
| OUT1 | L16 Red | Motor + |
| OUT2 | L16 Black | Motor - |
| nFAULT | Teensy Digital | Fault detect |
| VREF | 0.2Ω → GND | 2A limit |

### Teensy Pin Assignments
| Function | Actuator 1-6 Pins |
|----------|-------------------|
| PWM | 2, 3, 4, 5, 6, 7 |
| Position ADC | A0-A5 (14-19) |
| Fault Detect | 8-12, 24 |
| E-Stop | 37 |

### L16 Wire Colors
- **Red**: Motor + (to DRV8871 OUT1)
- **Black**: Motor - (to DRV8871 OUT2)
- **Orange**: Position feedback (to Teensy ADC)
- **Purple**: Extend limit switch
- **White**: Retract limit switch

## Mechanical Assembly

### Base Plate Mount Points
- 6 points in 3 pairs at 0°, 120°, 240°
- Points within pairs separated by 30°

### Top Plate Mount Points
- 6 points in 3 pairs at 60°, 180°, 300°
- 60° rotation from base pattern

### Actuator Connections
| Base | Top | Actuator |
|------|-----|----------|
| 1 (345°) | 2 (75°) | A1 |
| 2 (15°) | 1 (45°) | A2 |
| 3 (105°) | 4 (195°) | A3 |
| 4 (135°) | 3 (165°) | A4 |
| 5 (225°) | 6 (315°) | A5 |
| 6 (255°) | 5 (285°) | A6 |

## Software Setup

### 1. Flash Teensy Firmware
```bash
# In PlatformIO
pio run -t upload
```

### 2. Calibrate Platform
1. Power on with platform unloaded
2. Send 'C' command via serial
3. Platform will center all actuators
4. Calibration saved to EEPROM

### 3. Test Basic Motion
```python
# Python test script
import serial
import struct

ser = serial.Serial('/dev/ttyACM0', 921600)

# Enable platform
ser.write(b'E')

# Send pose command (x,y,z,roll,pitch,yaw)
pose = struct.pack('cfffffff', b'P', 0, 0, 50, 0, 0, 0)  # 50mm up
ser.write(pose)
```

### 4. ROS2 Integration
```bash
# Launch Stewart platform node
ros2 run a2_hardware stewart_platform_node

# Send test command
ros2 topic pub /stewart/cmd_pose geometry_msgs/Pose "{position: {z: 0.05}}"
```

## Performance Specs

- **Travel**: ±50mm vertical, ±15° tilt, ±20° rotation
- **Speed**: 50mm/s max
- **Resolution**: 0.024mm (12-bit ADC)
- **Control Rate**: 1kHz internal, 100Hz ROS
- **Payload**: 2kg (head + gimbal)

## Safety Features

1. **Hardware E-Stop**: Cuts motor power
2. **Limit Switches**: Built into L16
3. **Current Limiting**: 2A per actuator
4. **Watchdog**: 500ms timeout
5. **Position Bounds**: Software limits

## Troubleshooting

| Issue | Check | Fix |
|-------|-------|-----|
| No motion | Power, E-stop | Check 12V, reset E-stop |
| Erratic motion | Position feedback | Shield cables, add caps |
| Drift | PID tuning | Increase I gain |
| Fault LED | Current/limits | Check mechanical binding |

## PID Starting Values
- **P**: 2.5
- **I**: 0.1
- **D**: 0.05
- **Deadband**: 0.5mm

## Next Steps

1. Mount 3DOF gimbal on top plate
2. Add base IMU for vibration compensation
3. Implement force feedback (future)
4. Test with full head assembly weight

---

*For complete details, see:*
- [Stewart Platform Design](stewart-platform-design.md)
- [Stewart Platform Firmware](stewart-platform-firmware.md)
- [Wiring Guide](wiring-guide.md)
