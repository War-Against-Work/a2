---
title: "Stewart Platform Design Specifications"
type: design
status: active
created: "2025-01-01"
updated: "2025-01-01"
---

# Stewart Platform Design for A2 Neck Base

> **Document Status:** CURRENT
> **Last Updated:** 2025-06-05
> **Version:** 1.0.0
> **Scope:** Phase 1

## Overview

This document provides complete design specifications for the 6-DOF Stewart platform serving as the neck base for the A2 robot. The platform uses 6 Actuonix L16-100-35-12-P linear actuators in a Gough-Stewart configuration with DRV8871 motor drivers.

## Table of Contents

- [1. Mechanical Design](#1-mechanical-design)
- [2. Electrical System](#2-electrical-system)
- [3. Control Architecture](#3-control-architecture)
- [4. Software Implementation](#4-software-implementation)
- [5. Calibration Procedures](#5-calibration-procedures)
- [6. Safety Systems](#6-safety-systems)
- [7. Performance Specifications](#7-performance-specifications)
- [8. Assembly Instructions](#8-assembly-instructions)

---

## 1. Mechanical Design

### 1.1 Platform Geometry

**Base Plate:**
- Material: 10-15mm aluminum or 3D printed PETG with steel reinforcement
- Radius: 200mm to mounting points
- Mounting pattern: 6 points in 3 pairs
- Pair centers: 0°, 120°, 240°
- Points within pairs: 30° separation
  - Pair 1: 345°, 15°
  - Pair 2: 105°, 135°
  - Pair 3: 225°, 255°

**Top Plate:**
- Material: 10-15mm aluminum or 3D printed PETG
- Radius: 150mm to mounting points
- Mounting pattern: 6 points in 3 pairs
- Pair centers: 60°, 180°, 300° (60° rotation from base)
- Points within pairs: 30° separation
  - Pair 1: 45°, 75°
  - Pair 2: 165°, 195°
  - Pair 3: 285°, 315°

### 1.2 Actuator Connectivity

| Base Point | Top Point | Actuator ID |
|------------|-----------|-------------|
| 1 (345°)   | 2 (75°)   | A1         |
| 2 (15°)    | 1 (45°)   | A2         |
| 3 (105°)   | 4 (195°)  | A3         |
| 4 (135°)   | 3 (165°)  | A4         |
| 5 (225°)   | 6 (315°)  | A5         |
| 6 (255°)   | 5 (285°)  | A6         |

### 1.3 Ball Joint Specifications

**3D Printed Design:**
- Thread: M5 or M6 (for 20mm ball)
- Ball diameter: 20mm
- Socket clearance: 0.3mm
- Material: PETG or TPU socket liner
- Print orientation: Ball vertical, support material required
- Post-processing: Sand ball smooth, apply PTFE lubricant

**Mounting:**
- Use threaded inserts in plates
- Apply medium-strength thread locker
- Torque to 5 Nm

### 1.4 Travel Envelope

- Vertical travel (Z): ±50mm
- Tilt range (pitch/roll): ±15°
- Rotation (yaw): ±20°
- Maximum payload: 2kg (head assembly + 3DOF gimbal)

---

## 2. Electrical System

### 2.1 Power Distribution

```
LRS-350-12 (29A)
    |
    +-- 10,000µF capacitor
    |
    +-- Emergency Stop Circuit -- MOSFET -- Distribution Block
                                              |
                                              +-- DRV8871 #1-6 (L16 actuators)
                                              +-- 5V Buck #1 (5A) -- Raspberry Pi 5
                                              +-- 5V Buck #2 (5A) -- USB devices/sensors
                                              +-- 3.3V Buck (3A) -- Teensy 4.1
```

### 2.2 Motor Driver Wiring (per DRV8871)

| DRV8871 Pin | Connection | Wire Color | Notes |
|-------------|------------|------------|-------|
| VM | 12V Bus | Red | 1000µF cap at terminal |
| GND | Ground Bus | Black | Star ground |
| IN1 | Teensy PWM | Yellow | 20kHz PWM |
| IN2 | Ground | Black | Single-pin mode |
| OUT1 | L16 Red | Red | Motor + |
| OUT2 | L16 Black | Black | Motor - |
| nFAULT | Teensy Digital | Green | Interrupt capable pin |
| VREF | 0.2Ω to GND | - | 2A current limit |

### 2.3 L16 Actuator Connections

| L16 Wire | Function | Connection | Notes |
|----------|----------|------------|-------|
| Red | Motor + | DRV8871 OUT1 | Twisted pair with black |
| Black | Motor - | DRV8871 OUT2 | |
| Orange | Position FB | Teensy ADC | Shielded cable |
| Purple | Limit Switch | Teensy Digital | Internal pull-up |
| White | Limit Switch | Teensy Digital | Internal pull-up |

### 2.4 Teensy 4.1 Pin Assignments

```cpp
// Motor Control PWM (20kHz)
const int PWM_A1 = 2;  // Timer1
const int PWM_A2 = 3;  // Timer1
const int PWM_A3 = 4;  // Timer2
const int PWM_A4 = 5;  // Timer2
const int PWM_A5 = 6;  // Timer3
const int PWM_A6 = 7;  // Timer3

// Position Feedback (12-bit ADC)
const int POS_A1 = A0;  // Pin 14
const int POS_A2 = A1;  // Pin 15
const int POS_A3 = A2;  // Pin 16
const int POS_A4 = A3;  // Pin 17
const int POS_A5 = A4;  // Pin 18
const int POS_A6 = A5;  // Pin 19

// Fault Detection (Interrupt capable)
const int FAULT_A1 = 8;
const int FAULT_A2 = 9;
const int FAULT_A3 = 10;
const int FAULT_A4 = 11;
const int FAULT_A5 = 12;
const int FAULT_A6 = 24;

// Limit Switches
const int LIMIT_EXTEND[6] = {25, 26, 27, 28, 29, 30};
const int LIMIT_RETRACT[6] = {31, 32, 33, 34, 35, 36};

// Emergency Stop
const int E_STOP = 37;

// Communication
// UART to Pi 5: Serial1 (pins 0, 1)
// I2C to sensors: Wire (pins 18, 19)
```

---

## 3. Control Architecture

### 3.1 Control Loop Structure

```
ROS2 Motion Planner (Pi 5)
    |
    v
Position Commands (100Hz)
    |
    v
Teensy 4.1 Real-time Controller
    |
    +-- Inverse Kinematics (1kHz)
    +-- PID Control (1kHz)
    +-- Safety Monitor (10kHz)
    +-- Position Feedback Filter
    |
    v
PWM Outputs to DRV8871
```

### 3.2 Coordinate System

- Origin: Center of base plate
- Z-axis: Vertical up
- X-axis: Forward (toward 0° base point)
- Y-axis: Right-hand rule
- Units: millimeters and radians

### 3.3 Inverse Kinematics

The platform requires solving for 6 actuator lengths given desired pose [x, y, z, roll, pitch, yaw]:

```cpp
// Simplified IK calculation
for (int i = 0; i < 6; i++) {
    Vector3 basePoint = getBasePoint(i);
    Vector3 topPoint = getTopPoint(i);

    // Apply rotation and translation to top point
    Matrix3 R = rotationMatrix(roll, pitch, yaw);
    Vector3 P = Vector3(x, y, z);
    Vector3 transformedTop = R * topPoint + P;

    // Calculate required actuator length
    float length = (transformedTop - basePoint).magnitude();
    actuatorSetpoints[i] = length;
}
```

### 3.4 PID Control Parameters

Start with these values, tune per actuator:
- P: 2.5
- I: 0.1
- D: 0.05
- Output limits: ±100% duty cycle
- Deadband: 0.5mm

---

## 4. Software Implementation

### 4.1 Teensy Firmware Structure

```cpp
// Main control frequencies
IntervalTimer controlTimer;     // 1kHz PID
IntervalTimer safetyTimer;      // 10kHz monitors
IntervalTimer commTimer;        // 100Hz ROS comm

void setup() {
    initializeHardware();
    initializePID();
    controlTimer.begin(controlLoop, 1000);      // 1ms
    safetyTimer.begin(safetyMonitor, 100);     // 0.1ms
    commTimer.begin(rossCommunication, 10000);  // 10ms
}

void controlLoop() {
    readPositions();
    calculateIK();
    updatePID();
    writePWM();
}
```

### 4.2 ROS2 Interface

**Published Topics:**
- `/stewart/state` - Current pose and actuator positions (100Hz)
- `/stewart/status` - Health monitoring data (10Hz)
- `/stewart/imu` - Platform IMU data (200Hz)

**Subscribed Topics:**
- `/stewart/cmd_pose` - Desired platform pose
- `/stewart/cmd_vel` - Velocity commands
- `/stewart/enable` - Enable/disable control

### 4.3 Safety Features

```cpp
void safetyMonitor() {
    // Check all limit switches
    if (anyLimitTriggered()) {
        emergencyStop();
    }

    // Monitor actuator currents (via fault pins)
    if (anyFaultDetected()) {
        disableActuator();
    }

    // Position bounds checking
    if (outOfBounds()) {
        limitMotion();
    }

    // Communication watchdog
    if (millis() - lastCommand > 500) {
        holdPosition();
    }
}
```

---

## 5. Calibration Procedures

### 5.1 Initial Setup

1. **Home Position Calibration:**
   - Manually center all actuators to 50% extension
   - Measure and record actual lengths
   - Update firmware offset constants

2. **ADC Calibration:**
   ```cpp
   // Per actuator calibration
   const float ADC_TO_MM[6] = {
       24.41,  // (100mm range / 4096 counts)
       24.41,
       24.41,
       24.41,
       24.41,
       24.41
   };
   ```

3. **Kinematic Calibration:**
   - Mount precision level on top plate
   - Command known positions
   - Measure actual vs commanded
   - Update geometry constants

### 5.2 Runtime Calibration

```cpp
void autoCalibrate() {
    // Move to known positions
    moveToExtents();
    recordLimits();

    // Find center position
    moveToCenter();
    zeroIMU();

    // Test each DOF
    for (int dof = 0; dof < 6; dof++) {
        testDOF(dof);
        recordResponse();
    }
}
```

---

## 6. Safety Systems

### 6.1 Hardware Safety

- **Emergency Stop:** Hardware interrupt, cuts motor power
- **Limit Switches:** Built into L16, wired to interrupts
- **Current Limiting:** DRV8871 VREF set to 2A max
- **Thermal Protection:** DRV8871 internal shutdown

### 6.2 Software Safety

```cpp
class SafetyMonitor {
    float maxVelocity = 50.0;      // mm/s
    float maxAcceleration = 200.0;  // mm/s²
    float maxTilt = 15.0;          // degrees
    float maxExtension = 95.0;      // mm
    float minExtension = 5.0;       // mm

    bool checkMotionLimits(Pose cmd) {
        // Velocity limiting
        // Acceleration limiting
        // Workspace boundary
        // Singularity avoidance
    }
};
```

### 6.3 Fault Recovery

1. **Actuator Fault:** Disable single actuator, maintain stability
2. **Communication Loss:** Hold last safe position
3. **Power Brownout:** Controlled shutdown sequence
4. **Limit Hit:** Back off 5mm, recalibrate

---

## 7. Performance Specifications

### 7.1 Dynamic Performance

| Parameter | Value | Notes |
|-----------|-------|-------|
| Max velocity | 50 mm/s | Platform center |
| Max acceleration | 200 mm/s² | With 2kg payload |
| Position resolution | 0.024 mm | 12-bit ADC |
| Position repeatability | ±0.1 mm | After calibration |
| Control bandwidth | 10 Hz | Closed loop |
| Update rate | 1000 Hz | Internal control |

### 7.2 Power Consumption

- Idle (holding position): 6W (1A @ 12V)
- Typical motion: 24W (2A @ 12V)
- Peak (all actuators): 54W (4.5A @ 12V)

---

## 8. Assembly Instructions

### 8.1 Base Assembly

1. **Print/machine plates** with specified hole patterns
2. **Install threaded inserts** for ball joints
3. **Mount DRV8871 drivers** near base perimeter
4. **Install power distribution** with proper gauge wire
5. **Add base IMU** (ICM-20948) at platform center

### 8.2 Actuator Installation

1. **Attach ball joints** to actuator ends
2. **Mount actuators** to base points
3. **Connect to top plate** in specified pattern
4. **Route position feedback** cables (shielded)
5. **Connect motor power** with twisted pairs

### 8.3 Integration Checklist

- [ ] All actuators move freely through range
- [ ] Limit switches trigger at extremes
- [ ] Position feedback reads 0-3.3V
- [ ] No mechanical interference
- [ ] Emergency stop functional
- [ ] ROS2 communication established
- [ ] IMU data streaming
- [ ] Calibration completed

---

## Appendix A: Troubleshooting

| Symptom | Possible Cause | Solution |
|---------|----------------|----------|
| Actuator not moving | Fault condition | Check nFAULT pin, power |
| Erratic motion | Noisy position feedback | Add shielding, filter |
| Platform drift | PID tuning | Increase I term |
| Oscillation | Excessive gain | Reduce P term |
| Limited range | Mechanical binding | Check ball joints |

## Appendix B: Future Enhancements

1. **Force Sensing:** Add load cells for haptic feedback
2. **Active Damping:** Use base IMU for vibration cancellation
3. **Adaptive Control:** Neural network for dynamics learning
4. **Redundancy:** Hot-swap actuator capability
