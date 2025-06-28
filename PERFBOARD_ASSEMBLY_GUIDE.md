# **Perfboard Assembly Guide**
## **INA219 Current Monitoring System - 5×7cm Board**

---

## **📋 Pre-Assembly Preparation**

### **Required Tools & Equipment:**
```
Soldering Equipment:
├── 40W temperature-controlled soldering iron (350°C)
├── 60/40 rosin-core solder (0.6mm diameter)
├── Flux paste (rosin-based)
├── Desoldering braid (for corrections)
├── Isopropyl alcohol & cotton swabs (cleaning)

Measurement Tools:
├── Digital multimeter (for continuity/resistance)
├── Fine-tip probe set
├── Precision tweezers
├── Wire strippers (24-30 AWG)
├── Flush cutters (component leads)

Assembly Aids:
├── PCB holder/vise (board stabilization)
├── Magnifying glass (2x-4x magnification)
├── Good lighting (LED desk lamp)
├── Anti-static wrist strap
├── Component organizer tray
```

### **Component Preparation & Verification:**
```
Step 1: Component Inventory Check
□ 3× INA219 breakout boards (addresses pre-configured)
□ 2× JST-XH connectors (4-pin input, 6-pin output)
□ 6× Resistors (2× 4.7kΩ, 4× 220Ω)
□ 4× Capacitors (3× 0.1µF ceramic, 1× 10µF electrolytic)
□ 1× 5×7cm perfboard (2.54mm grid)
□ 22AWG solid wire (power/ground jumpers)
□ 26AWG stranded wire (signal connections)

Step 2: INA219 Address Configuration
□ INA219-Main: A0=GND, A1=GND (Address: 0x40)
□ INA219-5V: A0=VCC, A1=GND (Address: 0x41)
□ INA219-Actuator: A0=GND, A1=VCC (Address: 0x42)
□ Verify address settings with I²C scanner before installation

Step 3: Component Lead Preparation
□ Pre-bend resistor leads to 2.54mm spacing
□ Mark electrolytic capacitor polarity clearly
□ Test continuity of all wire jumpers
□ Verify JST connector pin assignments
```

---

## **🔨 Assembly Sequence**

### **Phase 1: Foundation Components (45 minutes)**

#### **Step 1.1: Junction Points Installation**
```
Components: 4× Wire junction points
Location: Power, Ground, SDA, SCL distribution points
Technique: Solder solid wire loops to establish distribution nodes

Procedure:
1. Cut 4× pieces of 22AWG solid wire, 15mm length each
2. Strip 2mm from each end
3. Form small loops (3mm diameter) for junction points
4. Position at grid locations: (120,140), (120,360), (250,160), (250,190)
5. Solder to perfboard with minimal heat (2-3 seconds per joint)
6. Trim excess wire flush with board surface

Quality Check:
□ Junction loops are mechanically secure
□ No solder bridges between adjacent holes
□ Electrical continuity through each junction
```

#### **Step 1.2: Test Points Installation**
```
Components: 4× Test point pads
Location: TP1-TP4 for voltage/signal measurement
Technique: Enlarged solder pads for probe access

Procedure:
1. Identify test point locations: (80,140), (80,360), (210,160), (210,190)
2. Apply flux to perfboard holes
3. Form large solder pads (3-4mm diameter) using extra solder
4. Ensure smooth, dome-shaped finish for probe contact
5. Label each test point clearly (TP1: 3.3V, TP2: GND, TP3: SDA, TP4: SCL)

Quality Check:
□ Test points are easily accessible with probe tips
□ Sufficient solder for reliable contact
□ No contamination or flux residue
```

#### **Step 1.3: Resistor Installation**
```
Components: 2× 4.7kΩ (I²C pull-ups), 4× 220Ω (LED current limiting)
Technique: Vertical mounting to save space

Pull-up Resistors (4.7kΩ):
1. Install at positions (140,160) and (140,190)
2. Mount vertically with one lead through hole, other to adjacent pad
3. Solder top lead to 3.3V distribution point
4. Solder bottom lead to respective I²C signal junction

LED Resistors (220Ω):
1. Install at positions (320,280), (320,310), (320,340), (320,370)
2. Mount horizontally with standard lead spacing
3. Orient for easy routing to output connector
4. Leave output ends unconnected for now

Quality Check:
□ Correct resistor values verified (color codes)
□ Mechanically secure mounting
□ No short circuits to adjacent components
□ Proper orientation for next assembly steps
```

#### **Step 1.4: Ceramic Capacitor Installation**
```
Components: 3× 0.1µF ceramic capacitors
Location: Adjacent to each INA219 position
Technique: Close proximity to power pins (<5mm)

Procedure:
1. Install at positions (160,120), (300,120), (440,120)
2. Mount with short leads for minimal inductance
3. Connect one terminal to local 3.3V distribution
4. Connect other terminal to local ground point
5. Position to avoid interference with INA219 placement

Quality Check:
□ Capacitors within 5mm of intended INA219 power pins
□ Solid electrical connections to power/ground
□ Adequate clearance for component installation
□ No mechanical stress on ceramic bodies
```

**⏱️ Phase 1 Checkpoint:**
- Continuity test all junction points
- Measure resistance of pull-up resistors (4.7kΩ ±5%)
- Verify no short circuits between power/ground

---

### **Phase 2: Power Distribution (30 minutes)**

#### **Step 2.1: Bottom Layer Power Traces**
```
Wire Type: 22AWG solid copper wire
Routing: Point-to-point with minimal crossings
Technique: Bottom-side routing with through-hole vias

Power Distribution (3.3V):
1. Main route: Input connector pin 1 → Power junction
2. Branch routes: Power junction → Each INA219 VCC pin
3. Test connection: Power junction → TP1 test point
4. Use red wire for easy identification

Ground Distribution:
1. Main route: Input connector pin 2 → Ground junction
2. Branch routes: Ground junction → Each INA219 GND pin
3. Test connection: Ground junction → TP2 test point
4. Use black wire for easy identification

Procedure:
1. Cut wires to exact lengths (measure twice, cut once)
2. Strip 2mm from each end
3. Route on bottom side of board where possible
4. Use through-hole vias for layer transitions
5. Solder with good heat transfer (3-4 seconds per joint)
6. Trim excess wire flush with board

Quality Check:
□ All power connections show <0.1Ω resistance
□ No voltage drop >10mV across any power trace
□ Ground connections show <0.05Ω resistance
□ No accidental short circuits detected
```

#### **Step 2.2: Electrolytic Capacitor Installation**
```
Component: 1× 10µF electrolytic capacitor
Location: Position (130,220) - near input power
Technique: Correct polarity, strain relief

Procedure:
1. Identify positive terminal (longer lead, + marking)
2. Connect positive terminal to power junction
3. Connect negative terminal to ground junction
4. Mount with slight mechanical flexibility
5. Add strain relief if needed (heat-shrink tubing)

Quality Check:
□ Correct polarity verified (positive to 3.3V)
□ Mechanically secure but not over-stressed
□ Electrical continuity verified
□ No electrolyte leakage or damage
```

**⏱️ Phase 2 Checkpoint:**
- Power-on test: Apply 3.3V to input connector
- Measure 3.3V ±50mV at all power distribution points
- Measure <10mA quiescent current draw
- Verify no heating of components after 1 minute

---

### **Phase 3: INA219 Sensor Installation (40 minutes)**

#### **Step 3.1: INA219 Breakout Board Mounting**
```
Components: 3× INA219 breakout boards (pre-configured addresses)
Mounting: Female headers for removability (recommended)
Alternative: Direct soldering for permanent installation

Header Installation Method:
1. Install 8-pin female headers at INA219 positions
2. Use temporary male headers to maintain alignment during soldering
3. Solder female headers to perfboard pads
4. Insert INA219 breakouts with male headers

Direct Solder Method:
1. Position INA219 breakouts at (180,80), (320,80), (460,80)
2. Verify correct orientation (VCC/GND pins toward bottom)
3. Solder power pins first (VCC, GND)
4. Solder signal pins (SDA, SCL)
5. Solder current sense pins (Vin+, Vin-)

Quality Check:
□ INA219 boards are level and properly seated
□ All solder joints are solid and well-formed
□ No solder bridges between adjacent pins
□ Power pins show proper continuity to distribution points
```

#### **Step 3.2: I²C Signal Routing**
```
Wire Type: 26AWG stranded wire (flexible)
Signals: SDA, SCL from junctions to each INA219
Color Coding: Green (SDA), Blue (SCL)

SDA Connections:
1. SDA junction → INA219-Main SDA pin
2. SDA junction → INA219-5V SDA pin
3. SDA junction → INA219-Actuator SDA pin
4. SDA junction → TP3 test point

SCL Connections:
1. SCL junction → INA219-Main SCL pin
2. SCL junction → INA219-5V SCL pin
3. SCL junction → INA219-Actuator SCL pin
4. SCL junction → TP4 test point

Procedure:
1. Cut wires to appropriate lengths with 10% extra
2. Strip 2mm from each end
3. Pre-tin all wire ends
4. Solder to junction points first
5. Route to INA219 pins with gentle curves
6. Solder to INA219 signal pins
7. Secure wires to avoid mechanical stress

Quality Check:
□ All I²C connections show proper continuity
□ No short circuits between SDA and SCL
□ Wire routing avoids mechanical stress points
□ Test points accessible for measurement
```

**⏱️ Phase 3 Checkpoint:**
- I²C bus test: Connect I²C scanner tool
- Verify detection of all three INA219 addresses (0x40, 0x41, 0x42)
- Check I²C signal integrity at test points
- Measure pull-up resistor effectiveness (3.3V idle state)

---

### **Phase 4: Connector Installation (25 minutes)**

#### **Step 4.1: Input Connector (JST-XH 4-pin)**
```
Component: 1× JST-XH 4-pin through-hole connector
Location: Position (30,180) - board left edge
Function: I²C bus input (3.3V, GND, SDA, SCL)

Installation:
1. Verify connector orientation (keying tab facing outward)
2. Insert connector pins through board holes
3. Ensure connector body sits flush with board surface
4. Solder pins starting with corner pins for stability
5. Complete all four pins with good fillet formation

Wire Connections:
Pin 1 (3.3V) → Power junction (red wire)
Pin 2 (GND) → Ground junction (black wire)
Pin 3 (SDA) → SDA junction (green wire)
Pin 4 (SCL) → SCL junction (blue wire)

Quality Check:
□ Connector mechanically secure and properly oriented
□ All pins show electrical continuity to respective junctions
□ No solder bridges between adjacent pins
□ Adequate wire strain relief
```

#### **Step 4.2: Output Connector (JST-XH 6-pin)**
```
Component: 1× JST-XH 6-pin through-hole connector
Location: Position (470,300) - board right edge
Function: LED control output signals

Installation:
1. Verify connector orientation (keying tab facing outward)
2. Insert connector pins through board holes
3. Ensure connector body sits flush with board surface
4. Solder pins starting with corner pins for stability
5. Complete all six pins with good fillet formation

Wire Connections:
Pin 1 → LED resistor R1 (PWR LED)
Pin 2 → LED resistor R2 (12V LED)
Pin 3 → LED resistor R3 (5V LED)
Pin 4 → LED resistor R4 (FLT LED)
Pin 5 → Spare (no connection)
Pin 6 → Ground junction (black wire)

Quality Check:
□ Connector mechanically secure and properly oriented
□ LED control signals routed correctly
□ Ground connection established
□ No short circuits between control signals
```

**⏱️ Phase 4 Checkpoint:**
- Connector pin assignment verification with cable
- Continuity test of all connector pins
- Mechanical stress test (gentle insertion/removal)
- Final dimensional check for enclosure fit

---

### **Phase 5: Final Assembly & Testing (20 minutes)**

#### **Step 5.1: Final Wire Routing**
```
Objective: Complete any remaining connections and secure all wiring

Top Layer Jumpers:
1. Any power connections requiring top-side routing
2. LED control signals from resistors to output connector
3. Use 26AWG stranded wire for flexibility
4. Secure with small cable ties if needed

Wire Management:
1. Ensure no wires cross over solder joints
2. Maintain minimum bend radius (5× wire diameter)
3. Secure loose wires to prevent mechanical stress
4. Add strain relief at connector interfaces

Quality Check:
□ All electrical connections completed
□ No loose or unsecured wires
□ Adequate mechanical strain relief
□ Clean appearance with professional routing
```

#### **Step 5.2: Final Cleaning & Inspection**
```
Cleaning Process:
1. Remove all flux residue with isopropyl alcohol
2. Use cotton swabs for detailed cleaning
3. Inspect all solder joints under magnification
4. Check for any contamination or foreign material

Visual Inspection Checklist:
□ All solder joints are shiny and well-formed
□ No cold solder joints or dry connections
□ No solder bridges between adjacent pads
□ All components properly seated and aligned
□ Wire routing neat and professional
□ Labels and markings clearly visible
□ No physical damage to components or board
```

#### **Step 5.3: Comprehensive Electrical Testing**
```
Test 1: Power Distribution
- Apply 3.3V to input connector
- Measure voltage at each INA219 VCC pin (3.25-3.35V)
- Verify ground continuity (<0.1Ω resistance)
- Check quiescent current draw (<15mA)

Test 2: I²C Communication
- Connect I²C master device to input connector
- Scan for devices: should detect 0x40, 0x41, 0x42
- Verify signal levels at test points
- Check pull-up resistor function (3.3V idle)

Test 3: LED Interface
- Apply control signals to output connector
- Verify current limiting (15mA ±3mA per channel)
- Test each LED channel independently
- Check for proper ground isolation

Test 4: Current Measurement Function
- Apply known current through INA219 sense terminals
- Read values via I²C interface
- Compare measured vs. applied (±1% accuracy)
- Test all three channels independently

Pass Criteria:
□ All power rails within specification
□ I²C communication reliable and stable
□ LED channels function correctly
□ Current measurement accuracy verified
□ No crosstalk or interference between channels
```

---

## **📊 Quality Assurance Checklist**

### **Critical Inspection Points:**
```
Electrical Safety:
□ No short circuits between power and ground
□ All polarized components correctly oriented
□ No exposed high-voltage connections
□ Proper strain relief on all connections

Mechanical Integrity:
□ All components mechanically secure
□ No loose or damaged solder joints
□ Adequate clearance for thermal expansion
□ Board fits properly in intended enclosure

Functional Performance:
□ All I²C addresses respond correctly
□ Current measurement accuracy within spec
□ LED control signals function properly
□ Test points accessible and functional

Documentation Compliance:
□ Component values match BOM specification
□ Wire colors match schematic convention
□ Address configuration matches system design
□ Assembly matches approved layout
```

### **Common Problems & Solutions:**
```
Problem: INA219 not detected on I²C bus
Solution: Check address configuration jumpers, verify power connections

Problem: Erratic current measurements
Solution: Check decoupling capacitor installation, verify ground integrity

Problem: LED channels not responding
Solution: Verify resistor values, check continuity to output connector

Problem: Power supply noise or instability
Solution: Check bulk capacitor polarity, verify ground plane integrity
```

---

## **📝 Assembly Documentation**

### **Record Keeping:**
- Take photos of completed assembly from multiple angles
- Record actual component values used (if different from nominal)
- Note any assembly deviations or modifications
- Create test data log with measurement results
- Document any issues encountered and solutions applied

### **Handoff Package:**
- Completed assembly with all components installed
- Test results documentation showing pass/fail status
- Cable assembly with proper connector termination
- Assembly photos for reference
- Any special notes or recommendations for operation

---

## **🎯 Success Metrics**

### **Assembly Quality Targets:**
- **Total assembly time**: <2.5 hours for experienced assembler
- **First-pass electrical test**: >90% success rate
- **Rework requirement**: <10% of assemblies need correction
- **Long-term reliability**: >95% operational after 1000 hours

### **Performance Validation:**
- **I²C communication**: 100% reliable at 400kHz operation
- **Current measurement**: ±1% accuracy across 100mA-3A range
- **Power efficiency**: <5% losses in power distribution
- **Thermal stability**: <0.1%/°C drift in measurements

This assembly guide provides step-by-step instructions for reliable, repeatable construction of the perfboard layout with professional quality results.
