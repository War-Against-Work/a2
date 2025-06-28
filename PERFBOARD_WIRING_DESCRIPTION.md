# Perfboard Wiring Description - Current Monitoring System

## Overview
This perfboard implements a multi-channel current monitoring system using INA219 sensors with I²C communication, status LEDs, and proper signal conditioning. The board is designed with a 2.54mm (0.1") grid layout suitable for standard perfboard construction.

## System Purpose
This perfboard is part of a larger power management and monitoring system for an A2 robotics project. It serves as a centralized current monitoring hub that interfaces between:
- Main system controller (via I²C bus)
- Multiple power rails (12V main, 5V rail, actuator power)
- Status indication LEDs
- Test points for debugging

## Component Inventory

### Power Management Components
- **3x INA219 Current Sensors** - Texas Instruments bidirectional current/power monitors
  - Main Bus Monitor (Address: 0x40)
  - 5V Rail Monitor (Address: 0x41)
  - Actuator Monitor (Address: 0x42)
  - Operating voltage: 3.0-5.5V
  - Current measurement range: ±3.2A (with 0.1Ω shunt)

### Signal Conditioning
- **2x 4.7kΩ Resistors** - I²C pull-up resistors (SDA/SCL lines)
- **4x 220Ω Resistors** - Current limiting resistors for status LEDs
- **3x 0.1µF Ceramic Capacitors** - High-frequency decoupling (one per INA219)
- **1x 10µF Electrolytic Capacitor** - Bulk decoupling for low-frequency noise

### Interconnection
- **2x JST-XH Connectors**
  - Input: 4-pin I²C Bus connector
  - Output: 6-pin Control/Status connector
- **6x Through-hole Vias** (0.6mm drill, 1.2mm pad)
  - 3x Power vias (3.3V distribution)
  - 3x Ground vias (GND distribution)
- **4x Test Points** - Gold-plated test pads for debugging
  - 3.3V Test Point
  - GND Test Point
  - SDA Test Point
  - SCL Test Point

## Circuit Topology

### Power Distribution
**Input Power (3.3V):**
- Enters via I²C connector Pin 1
- Distributed through bottom layer traces (6 mil width)
- Connected to 3 power vias for layer transition
- Each via feeds one INA219 sensor through top layer

**Ground Distribution:**
- Common ground plane on bottom layer
- Multiple via connections for low impedance
- Star grounding topology to minimize ground loops
- Wide traces (6 mil) for current capacity

### I²C Communication Bus
**Signal Routing:**
- SDA (Serial Data): Green traces, 2 mil width
- SCL (Serial Clock): Blue traces, 2 mil width
- Daisy-chain topology: Controller → INA219-Main → INA219-5V → INA219-Actuator
- 4.7kΩ pull-up resistors to 3.3V rail (required for I²C operation)
- Test points provided for signal integrity verification

**I²C Addresses:**
- INA219-Main: 0x40 (A0=GND, A1=GND)
- INA219-5V: 0x41 (A0=VCC, A1=GND)
- INA219-Actuator: 0x42 (A0=GND, A1=VCC)

### Status LED Interface
**LED Control Signals:**
- Power LED: Control connector Pin 1 → 220Ω → LED anode
- 12V LED: Control connector Pin 2 → 220Ω → LED anode
- 5V LED: Control connector Pin 3 → 220Ω → LED anode
- Fault LED: Control connector Pin 4 → 220Ω → LED anode
- All LED cathodes connected to ground via respective vias

## Connector Pinouts

### Input Connector (J1 - JST-XH 4-pin)
| Pin | Signal | Wire Color | Function |
|-----|--------|------------|----------|
| 1   | 3.3V   | Red        | Power supply input |
| 2   | GND    | Black      | Ground return |
| 3   | SDA    | Green      | I²C Serial Data |
| 4   | SCL    | Blue       | I²C Serial Clock |

### Output Connector (J2 - JST-XH 6-pin)
| Pin | Signal | Wire Color | Function |
|-----|--------|------------|----------|
| 1   | PWR_LED| Yellow     | Power status LED drive |
| 2   | 12V_LED| Orange     | 12V rail status LED |
| 3   | 5V_LED | Purple     | 5V rail status LED |
| 4   | FLT_LED| Red        | Fault indication LED |
| 5   | SPARE  | White      | Reserved for future use |
| 6   | GND    | Black      | Ground return |

## Layer Stackup

### Top Layer (Component Side)
- **Components:** All INA219s, resistors, capacitors, connectors
- **Traces:** I²C signal routing, LED control signals
- **Via connections:** Power and ground distribution points
- **Test points:** Accessible measurement pads

### Bottom Layer (Solder Side)
- **Power planes:** 3.3V distribution (flood fill where possible)
- **Ground plane:** Continuous ground pour
- **Via connections:** Through-hole plating for layer transition
- **Trace routing:** Wide power/ground distribution

## Critical Design Notes

### Signal Integrity
- I²C traces kept short with minimal via transitions
- Pull-up resistors located close to first device in chain
- Test points provided for oscilloscope probing
- Ground plane provides return path for all signals

### Power Integrity
- Decoupling capacitors placed within 0.2" of each INA219
- Bulk capacitor handles low-frequency supply variations
- Multiple ground vias reduce ground impedance
- Power traces sized for 500mA continuous current

### Thermal Considerations
- Components spaced for natural air cooling
- No high-power dissipation components
- Copper pour on both layers aids heat distribution

### Manufacturing Notes
- Standard 1.6mm FR4 substrate
- HASL surface finish for hand soldering
- 0.6mm via drill size (standard perfboard compatible)
- Component spacing optimized for hand assembly

## Testing and Validation

### Test Point Access
- **TP1 (3.3V):** Verify power supply voltage (3.15-3.45V nominal)
- **TP2 (GND):** Reference ground for all measurements
- **TP3 (SDA):** I²C data line integrity (logic levels)
- **TP4 (SCL):** I²C clock line integrity (400kHz operation)

### Functional Verification
1. Power-on test: Verify 3.3V at all INA219 VCC pins
2. I²C communication: Scan for devices at addresses 0x40, 0x41, 0x42
3. Current measurement: Apply known loads and verify readings
4. LED functionality: Test all status LED drive circuits

## Integration Notes
This perfboard interfaces with the larger A2 system as follows:
- **Upstream:** Connects to main system controller I²C bus
- **Downstream:** Monitors power rails feeding actuators and sensors
- **Status:** Provides visual indication of system power health
- **Debug:** Test points enable troubleshooting and optimization

The board is designed for modular installation and can be easily replaced or upgraded as system requirements evolve.
