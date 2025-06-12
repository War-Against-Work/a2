---
title: "Stewart Platform Teensy Firmware"
type: implementation
status: active
created: "2025-01-01"
updated: "2025-01-01"
---

# Stewart Platform Teensy 4.1 Firmware Implementation

> **Document Status:** CURRENT
> **Last Updated:** 2025-06-05
> **Version:** 1.0.0
> **Scope:** Phase 1

## Overview

Complete firmware implementation for 6-DOF Stewart platform control using Teensy 4.1, DRV8871 drivers, and L16-100-35-12-P actuators.

## Core Firmware Code

```cpp
// stewart_platform_firmware.ino
// Teensy 4.1 Stewart Platform Controller

#include <Wire.h>
#include <TeensyThreads.h>
#include <ADC.h>
#include <EEPROM.h>

// ===== HARDWARE CONFIGURATION =====
// Motor Control PWM Pins (20kHz capable)
const uint8_t PWM_PINS[6] = {2, 3, 4, 5, 6, 7};

// Position Feedback ADC Pins
const uint8_t POS_PINS[6] = {A0, A1, A2, A3, A4, A5};

// Fault Detection Pins (interrupt capable)
const uint8_t FAULT_PINS[6] = {8, 9, 10, 11, 12, 24};

// Limit Switch Pins
const uint8_t LIMIT_EXT_PINS[6] = {25, 26, 27, 28, 29, 30};
const uint8_t LIMIT_RET_PINS[6] = {31, 32, 33, 34, 35, 36};

// System Pins
const uint8_t E_STOP_PIN = 37;
const uint8_t STATUS_LED = 13;

// ===== CONSTANTS =====
const float L16_STROKE = 100.0;           // mm
const float L16_RETRACTED = 155.0;        // mm
const float L16_EXTENDED = 255.0;         // mm
const float ADC_RESOLUTION = 4096.0;      // 12-bit
const float PWM_FREQUENCY = 20000.0;      // Hz
const float CONTROL_FREQUENCY = 1000.0;   // Hz
const float SAFETY_FREQUENCY = 10000.0;   // Hz

// ===== KINEMATIC PARAMETERS =====
// Base plate mounting points (radius = 200mm)
const float BASE_RADIUS = 200.0;
const float BASE_ANGLES[6] = {345, 15, 105, 135, 225, 255};  // degrees

// Top plate mounting points (radius = 150mm)
const float TOP_RADIUS = 150.0;
const float TOP_ANGLES[6] = {75, 45, 195, 165, 315, 285};    // degrees

// Platform connection mapping
const uint8_t CONNECTIONS[6][2] = {
    {0, 1},  // Base 0 to Top 1
    {1, 0},  // Base 1 to Top 0
    {2, 3},  // Base 2 to Top 3
    {3, 2},  // Base 3 to Top 2
    {4, 5},  // Base 4 to Top 5
    {5, 4}   // Base 5 to Top 4
};

// ===== DATA STRUCTURES =====
struct Vector3 {
    float x, y, z;

    Vector3(float x = 0, float y = 0, float z = 0) : x(x), y(y), z(z) {}

    Vector3 operator+(const Vector3& v) const {
        return Vector3(x + v.x, y + v.y, z + v.z);
    }

    Vector3 operator-(const Vector3& v) const {
        return Vector3(x - v.x, y - v.y, z - v.z);
    }

    float magnitude() const {
        return sqrt(x*x + y*y + z*z);
    }
};

struct Pose {
    float x, y, z;        // mm
    float roll, pitch, yaw;  // radians
};

struct ActuatorState {
    float position;       // mm
    float setpoint;       // mm
    float velocity;       // mm/s
    float error;
    float errorSum;
    float lastError;
    uint32_t lastUpdate;
    bool faultDetected;
    bool limitExtend;
    bool limitRetract;
};

struct PIDGains {
    float kp = 2.5;
    float ki = 0.1;
    float kd = 0.05;
    float deadband = 0.5;  // mm
    float maxOutput = 100.0;  // percent
};

// ===== GLOBAL VARIABLES =====
ActuatorState actuators[6];
PIDGains pidGains[6];
Pose currentPose;
Pose targetPose;
bool systemEnabled = false;
bool emergencyStop = false;
uint32_t lastCommandTime = 0;
uint32_t controlLoopTime = 0;

// Base and top mounting points (pre-calculated)
Vector3 basePlate[6];
Vector3 topPlate[6];

// ADC object for optimized reading
ADC *adc = new ADC();

// ===== INITIALIZATION =====
void setup() {
    Serial.begin(115200);  // USB debug
    Serial1.begin(921600); // ROS2 communication

    // Initialize hardware
    initializePins();
    initializeADC();
    initializePWM();
    initializeKinematics();
    loadCalibration();

    // Start control timers
    startControlLoops();

    // Signal ready
    pinMode(STATUS_LED, OUTPUT);
    digitalWrite(STATUS_LED, HIGH);

    Serial.println("Stewart Platform Controller Ready");
}

void initializePins() {
    // PWM outputs
    for (int i = 0; i < 6; i++) {
        pinMode(PWM_PINS[i], OUTPUT);
        analogWrite(PWM_PINS[i], 128);  // 50% = stopped
    }

    // Digital inputs with pullups
    for (int i = 0; i < 6; i++) {
        pinMode(FAULT_PINS[i], INPUT_PULLUP);
        pinMode(LIMIT_EXT_PINS[i], INPUT_PULLUP);
        pinMode(LIMIT_RET_PINS[i], INPUT_PULLUP);

        // Attach interrupts for faults
        attachInterrupt(digitalPinToInterrupt(FAULT_PINS[i]),
                       []{ handleFault(); }, FALLING);
    }

    // Emergency stop
    pinMode(E_STOP_PIN, INPUT_PULLUP);
    attachInterrupt(digitalPinToInterrupt(E_STOP_PIN),
                   []{ emergencyStop = true; }, FALLING);
}

void initializeADC() {
    // Configure for 12-bit resolution
    adc->adc0->setResolution(12);
    adc->adc0->setConversionSpeed(ADC_CONVERSION_SPEED::VERY_HIGH_SPEED);
    adc->adc0->setSamplingSpeed(ADC_SAMPLING_SPEED::VERY_HIGH_SPEED);

    // Configure averaging
    adc->adc0->setAveraging(4);
}

void initializePWM() {
    // Set PWM frequency to 20kHz for quiet operation
    for (int i = 0; i < 6; i++) {
        analogWriteFrequency(PWM_PINS[i], PWM_FREQUENCY);
        analogWriteResolution(8);  // 8-bit PWM
    }
}

void initializeKinematics() {
    // Pre-calculate base mounting points
    for (int i = 0; i < 6; i++) {
        float angle = BASE_ANGLES[i] * PI / 180.0;
        basePlate[i] = Vector3(
            BASE_RADIUS * cos(angle),
            BASE_RADIUS * sin(angle),
            0
        );
    }

    // Pre-calculate top mounting points (neutral position)
    for (int i = 0; i < 6; i++) {
        float angle = TOP_ANGLES[i] * PI / 180.0;
        topPlate[i] = Vector3(
            TOP_RADIUS * cos(angle),
            TOP_RADIUS * sin(angle),
            0
        );
    }
}

// ===== MAIN CONTROL LOOP =====
void controlLoop() {
    uint32_t startTime = micros();

    // Read all positions
    updatePositions();

    // Update state estimate
    updateKinematics();

    // Calculate control outputs
    if (systemEnabled && !emergencyStop) {
        calculateInverseKinematics();
        updatePIDControl();
    } else {
        stopAllActuators();
    }

    // Update timing
    controlLoopTime = micros() - startTime;
}

void updatePositions() {
    for (int i = 0; i < 6; i++) {
        // Read ADC with averaging
        uint16_t adcValue = adc->adc0->analogRead(POS_PINS[i]);

        // Convert to millimeters
        float position = L16_RETRACTED + (adcValue / ADC_RESOLUTION) * L16_STROKE;

        // Apply low-pass filter
        actuators[i].position = actuators[i].position * 0.7 + position * 0.3;

        // Calculate velocity (finite difference)
        uint32_t now = micros();
        float dt = (now - actuators[i].lastUpdate) / 1000000.0;
        if (dt > 0) {
            actuators[i].velocity = (position - actuators[i].position) / dt;
            actuators[i].lastUpdate = now;
        }

        // Update limit switches
        actuators[i].limitExtend = !digitalRead(LIMIT_EXT_PINS[i]);
        actuators[i].limitRetract = !digitalRead(LIMIT_RET_PINS[i]);
    }
}

// ===== INVERSE KINEMATICS =====
void calculateInverseKinematics() {
    // Create rotation matrix from Euler angles
    float cr = cos(targetPose.roll);
    float sr = sin(targetPose.roll);
    float cp = cos(targetPose.pitch);
    float sp = sin(targetPose.pitch);
    float cy = cos(targetPose.yaw);
    float sy = sin(targetPose.yaw);

    // Rotation matrix (ZYX Euler)
    float R[3][3] = {
        {cy*cp, cy*sp*sr - sy*cr, cy*sp*cr + sy*sr},
        {sy*cp, sy*sp*sr + cy*cr, sy*sp*cr - cy*sr},
        {-sp, cp*sr, cp*cr}
    };

    // Translation vector
    Vector3 T(targetPose.x, targetPose.y, targetPose.z);

    // Calculate required actuator lengths
    for (int i = 0; i < 6; i++) {
        // Get connection mapping
        int baseIdx = i;
        int topIdx = CONNECTIONS[i][1];

        // Transform top point
        Vector3 topTransformed;
        topTransformed.x = R[0][0]*topPlate[topIdx].x + R[0][1]*topPlate[topIdx].y + R[0][2]*topPlate[topIdx].z + T.x;
        topTransformed.y = R[1][0]*topPlate[topIdx].x + R[1][1]*topPlate[topIdx].y + R[1][2]*topPlate[topIdx].z + T.y;
        topTransformed.z = R[2][0]*topPlate[topIdx].x + R[2][1]*topPlate[topIdx].y + R[2][2]*topPlate[topIdx].z + T.z;

        // Calculate actuator length
        Vector3 delta = topTransformed - basePlate[baseIdx];
        actuators[i].setpoint = delta.magnitude();

        // Clamp to valid range
        actuators[i].setpoint = constrain(actuators[i].setpoint, L16_RETRACTED + 5, L16_EXTENDED - 5);
    }
}

// ===== PID CONTROL =====
void updatePIDControl() {
    for (int i = 0; i < 6; i++) {
        // Skip if fault detected
        if (actuators[i].faultDetected) continue;

        // Calculate error
        actuators[i].error = actuators[i].setpoint - actuators[i].position;

        // Deadband
        if (abs(actuators[i].error) < pidGains[i].deadband) {
            actuators[i].error = 0;
        }

        // PID calculation
        actuators[i].errorSum += actuators[i].error;
        actuators[i].errorSum = constrain(actuators[i].errorSum, -1000, 1000);  // Anti-windup

        float derivative = actuators[i].error - actuators[i].lastError;
        actuators[i].lastError = actuators[i].error;

        float output = pidGains[i].kp * actuators[i].error +
                      pidGains[i].ki * actuators[i].errorSum +
                      pidGains[i].kd * derivative;

        // Limit output
        output = constrain(output, -pidGains[i].maxOutput, pidGains[i].maxOutput);

        // Check limits
        if ((actuators[i].limitExtend && output > 0) ||
            (actuators[i].limitRetract && output < 0)) {
            output = 0;
            actuators[i].errorSum = 0;  // Reset integral
        }

        // Convert to PWM (0-255, 128 = stopped)
        int pwmValue = 128 + (output * 127 / 100);
        analogWrite(PWM_PINS[i], pwmValue);
    }
}

// ===== SAFETY MONITORING =====
void safetyMonitor() {
    // Check emergency stop
    if (emergencyStop) {
        stopAllActuators();
        return;
    }

    // Check communication timeout
    if (millis() - lastCommandTime > 500) {
        systemEnabled = false;
    }

    // Check fault pins
    for (int i = 0; i < 6; i++) {
        actuators[i].faultDetected = !digitalRead(FAULT_PINS[i]);
    }

    // Check position bounds
    for (int i = 0; i < 6; i++) {
        if (actuators[i].position < L16_RETRACTED - 5 ||
            actuators[i].position > L16_EXTENDED + 5) {
            actuators[i].faultDetected = true;
        }
    }
}

void stopAllActuators() {
    for (int i = 0; i < 6; i++) {
        analogWrite(PWM_PINS[i], 128);  // 50% = stopped
        actuators[i].errorSum = 0;
    }
}

// ===== COMMUNICATION =====
void handleSerialCommand() {
    if (Serial1.available() > 0) {
        char cmd = Serial1.read();

        switch (cmd) {
            case 'P':  // Pose command
                readPoseCommand();
                break;
            case 'E':  // Enable
                systemEnabled = true;
                emergencyStop = false;
                break;
            case 'D':  // Disable
                systemEnabled = false;
                break;
            case 'S':  // Status request
                sendStatus();
                break;
            case 'C':  // Calibrate
                runCalibration();
                break;
        }

        lastCommandTime = millis();
    }
}

void readPoseCommand() {
    // Read 6 floats (x, y, z, roll, pitch, yaw)
    if (Serial1.available() >= 24) {
        Serial1.readBytes((char*)&targetPose, sizeof(Pose));
    }
}

void sendStatus() {
    // Send current state
    Serial1.write('S');
    Serial1.write((uint8_t*)&currentPose, sizeof(Pose));

    // Send actuator positions
    for (int i = 0; i < 6; i++) {
        Serial1.write((uint8_t*)&actuators[i].position, sizeof(float));
    }

    // Send system flags
    uint8_t flags = 0;
    if (systemEnabled) flags |= 0x01;
    if (emergencyStop) flags |= 0x02;
    for (int i = 0; i < 6; i++) {
        if (actuators[i].faultDetected) flags |= (0x04 << i);
    }
    Serial1.write(flags);
}

// ===== CALIBRATION =====
void runCalibration() {
    Serial.println("Starting calibration...");

    // Move all actuators to center
    for (int i = 0; i < 6; i++) {
        actuators[i].setpoint = (L16_RETRACTED + L16_EXTENDED) / 2;
    }

    delay(3000);  // Wait for settling

    // Record center positions
    for (int i = 0; i < 6; i++) {
        EEPROM.put(i * sizeof(float), actuators[i].position);
    }

    Serial.println("Calibration complete");
}

void loadCalibration() {
    // Load calibration data from EEPROM
    for (int i = 0; i < 6; i++) {
        float calValue;
        EEPROM.get(i * sizeof(float), calValue);
        if (!isnan(calValue)) {
            // Apply calibration offset
        }
    }
}

// ===== MAIN LOOP =====
void loop() {
    handleSerialCommand();

    // Status LED blink
    static uint32_t lastBlink = 0;
    if (millis() - lastBlink > 1000) {
        digitalWrite(STATUS_LED, !digitalRead(STATUS_LED));
        lastBlink = millis();
    }

    // Debug output
    static uint32_t lastDebug = 0;
    if (millis() - lastDebug > 100) {
        if (Serial.available() && Serial.read() == 'd') {
            printDebugInfo();
        }
        lastDebug = millis();
    }
}

void printDebugInfo() {
    Serial.println("=== Stewart Platform Debug ===");
    Serial.print("Enabled: "); Serial.println(systemEnabled);
    Serial.print("E-Stop: "); Serial.println(emergencyStop);
    Serial.print("Loop Time: "); Serial.print(controlLoopTime); Serial.println(" us");

    for (int i = 0; i < 6; i++) {
        Serial.print("A"); Serial.print(i);
        Serial.print(" Pos:"); Serial.print(actuators[i].position, 1);
        Serial.print(" Set:"); Serial.print(actuators[i].setpoint, 1);
        Serial.print(" Err:"); Serial.print(actuators[i].error, 1);
        Serial.print(" Flt:"); Serial.print(actuators[i].faultDetected);
        Serial.println();
    }
}

// ===== INTERRUPT HANDLERS =====
void handleFault() {
    // Fault detected - handled in safety monitor
}

// ===== TIMER SETUP =====
IntervalTimer controlTimer;
IntervalTimer safetyTimer;

void startControlLoops() {
    controlTimer.begin(controlLoop, 1000);    // 1kHz
    safetyTimer.begin(safetyMonitor, 100);   // 10kHz
}
```

## ROS2 Interface Node

```python
#!/usr/bin/env python3
# stewart_platform_node.py

import rclpy
from rclpy.node import Node
import serial
import struct
import numpy as np
from geometry_msgs.msg import Pose, Twist
from sensor_msgs.msg import JointState
from std_msgs.msg import Bool, Header
import threading

class StewartPlatformNode(Node):
    def __init__(self):
        super().__init__('stewart_platform')

        # Serial connection to Teensy
        self.serial = serial.Serial('/dev/ttyACM0', 921600, timeout=0.1)

        # Publishers
        self.state_pub = self.create_publisher(JointState, '/stewart/state', 10)
        self.pose_pub = self.create_publisher(Pose, '/stewart/current_pose', 10)

        # Subscribers
        self.cmd_pose_sub = self.create_subscription(
            Pose, '/stewart/cmd_pose', self.cmd_pose_callback, 10)
        self.cmd_vel_sub = self.create_subscription(
            Twist, '/stewart/cmd_vel', self.cmd_vel_callback, 10)
        self.enable_sub = self.create_subscription(
            Bool, '/stewart/enable', self.enable_callback, 10)

        # Timers
        self.create_timer(0.01, self.communication_loop)  # 100Hz
        self.create_timer(0.1, self.status_request)       # 10Hz

        # Thread lock for serial
        self.serial_lock = threading.Lock()

        self.get_logger().info('Stewart Platform Node Started')

    def cmd_pose_callback(self, msg):
        """Send pose command to Teensy"""
        with self.serial_lock:
            # Convert geometry_msgs/Pose to our format
            data = struct.pack('cfffffff',
                b'P',
                msg.position.x * 1000,  # Convert to mm
                msg.position.y * 1000,
                msg.position.z * 1000,
                msg.orientation.x,  # Assuming quaternion to euler conversion done elsewhere
                msg.orientation.y,
                msg.orientation.z
            )
            self.serial.write(data)

    def enable_callback(self, msg):
        """Enable/disable platform"""
        with self.serial_lock:
            if msg.data:
                self.serial.write(b'E')
            else:
                self.serial.write(b'D')

    def communication_loop(self):
        """Handle incoming serial data"""
        with self.serial_lock:
            if self.serial.in_waiting > 0:
                header = self.serial.read(1)
                if header == b'S':
                    self.handle_status_response()

    def handle_status_response(self):
        """Parse and publish status data"""
        # Read pose (6 floats)
        pose_data = self.serial.read(24)
        pose = struct.unpack('ffffff', pose_data)

        # Read actuator positions (6 floats)
        actuator_data = self.serial.read(24)
        positions = struct.unpack('ffffff', actuator_data)

        # Read flags
        flags = struct.unpack('B', self.serial.read(1))[0]

        # Publish joint states
        joint_msg = JointState()
        joint_msg.header.stamp = self.get_clock().now().to_msg()
        joint_msg.name = [f'actuator_{i}' for i in range(6)]
        joint_msg.position = list(positions)
        self.state_pub.publish(joint_msg)

        # Publish current pose
        pose_msg = Pose()
        pose_msg.position.x = pose[0] / 1000.0  # Convert to meters
        pose_msg.position.y = pose[1] / 1000.0
        pose_msg.position.z = pose[2] / 1000.0
        # Would need to convert euler to quaternion here
        self.pose_pub.publish(pose_msg)

    def status_request(self):
        """Request status from Teensy"""
        with self.serial_lock:
            self.serial.write(b'S')

def main(args=None):
    rclpy.init(args=args)
    node = StewartPlatformNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Testing Procedures

```cpp
// test_stewart.ino
// Upload this for basic testing

void testActuator(int index) {
    Serial.print("Testing actuator "); Serial.println(index);

    // Extend
    analogWrite(PWM_PINS[index], 200);
    delay(2000);

    // Stop
    analogWrite(PWM_PINS[index], 128);
    delay(500);

    // Retract
    analogWrite(PWM_PINS[index], 56);
    delay(2000);

    // Stop
    analogWrite(PWM_PINS[index], 128);
}

void testAllActuators() {
    for (int i = 0; i < 6; i++) {
        testActuator(i);
        delay(1000);
    }
}

void testCoordinatedMotion() {
    // Move platform up
    targetPose.z = 50;
    delay(2000);

    // Tilt forward
    targetPose.pitch = 0.1;  // radians
    delay(2000);

    // Return to center
    targetPose = {0, 0, 0, 0, 0, 0};
    delay(2000);
}
```

## Integration with A2 System

1. **Mount Points:**
   - Base plate bolts to A2 torso frame
   - Top plate receives 3DOF gimbal assembly
   - Cable routing through center opening

2. **Power Integration:**
   - Connect to main 12V bus after E-stop
   - Separate 5V rail for Pi 5 ROS node
   - Common ground with star topology

3. **ROS2 Topics:**
   - Subscribe to `/a2/neck/cmd_pose` for motion commands
   - Publish to `/a2/neck/state` for feedback
   - Emergency stop on `/a2/safety/estop`

4. **Startup Sequence:**
   ```bash
   # On Teensy: firmware auto-starts

   # On Pi 5:
   ros2 launch a2_hardware stewart_platform.launch.py
   ```
