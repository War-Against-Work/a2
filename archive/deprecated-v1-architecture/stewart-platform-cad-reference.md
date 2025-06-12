---
title: "Stewart Platform CAD Reference"
type: reference
status: active
created: "2025-01-01"
updated: "2025-01-01"
---

# Stewart Platform CAD Reference - Top View

> **Document Status:** CURRENT
> **Last Updated:** 2025-06-05
> **Version:** 1.0.0
> **Scope:** Phase 1

## Final Configuration for CAD Design

### Base Plate (Bottom) - Top View
```
                    0° (X-axis)
                       │
                       │
               Point 2 ┼ Point 1
                  (15°)│(345°)
                       │
                       │
270° ──────────────────┼────────────────── 90°
       Point 6         │         Point 3
        (255°)         │         (105°)
                       │
       Point 5         │         Point 4
        (225°)         │         (135°)
                       │
                     180°

Circle radius: 200mm
Material thickness: 10-15mm
Center hole: 80mm diameter (for cable routing)
```

**Base Plate Coordinates (from center):**
- Point 1: X = 193.2mm, Y = -51.8mm  (345°)
- Point 2: X = 193.2mm, Y = 51.8mm   (15°)
- Point 3: X = 51.8mm, Y = 193.2mm   (105°)
- Point 4: X = -51.8mm, Y = 193.2mm  (135°)
- Point 5: X = -193.2mm, Y = -51.8mm (225°)
- Point 6: X = -193.2mm, Y = 51.8mm  (255°)

### Top Plate (Platform) - Top View
```
                    0° (X-axis)
                       │
                       │
                       │
                       │ Point 1 (45°)
           Point 2     │
            (75°)      │
270° ──────────────────┼────────────────── 90°
                       │
       Point 6         │         Point 3
        (315°)         │         (165°)
                       │
       Point 5         │         Point 4
        (285°)         │         (195°)
                       │
                     180°

Circle radius: 150mm
Material thickness: 10-15mm
Center hole: 60mm diameter (for gimbal mounting)
```

**Top Plate Coordinates (from center):**
- Point 1: X = 106.1mm, Y = 106.1mm  (45°)
- Point 2: X = 38.8mm, Y = 145.0mm   (75°)
- Point 3: X = -145.0mm, Y = 38.8mm  (165°)
- Point 4: X = -145.0mm, Y = -38.8mm (195°)
- Point 5: X = 38.8mm, Y = -145.0mm  (285°)
- Point 6: X = 106.1mm, Y = -106.1mm (315°)

### Connection Map (Base → Top)
```
Base Point 1 (345°) ─────→ Top Point 2 (75°)
Base Point 2 (15°)  ─────→ Top Point 1 (45°)
Base Point 3 (105°) ─────→ Top Point 4 (195°)
Base Point 4 (135°) ─────→ Top Point 3 (165°)
Base Point 5 (225°) ─────→ Top Point 6 (315°)
Base Point 6 (255°) ─────→ Top Point 5 (285°)
```

## CAD Design Specifications

### Mounting Holes
- **Ball Joint Mounting**: M5 or M6 threaded inserts
- **Depth**: 10mm minimum
- **Clearance**: 25mm radius around each mounting point

### Additional Features

**Base Plate:**
- Motor driver mounting points (6x DRV8871)
  - 40mm x 30mm footprint each
  - Mount near perimeter between actuator points
- Teensy 4.1 mounting (center or offset)
  - 65mm x 25mm footprint
- Power distribution mounting
  - Terminal blocks or bus bars
- Cable management clips

**Top Plate:**
- 3DOF gimbal mounting pattern (center)
- IMU mounting point (ICM-20948)
  - 20mm x 15mm footprint
  - Mount flat on plate surface
- Cable pass-through slots

### Material Recommendations
1. **Aluminum**: 10mm 6061-T6 (best rigidity)
2. **3D Printed**: PETG 15mm with 50% infill
3. **Hybrid**: 3D printed with aluminum reinforcement plates

### Critical Dimensions
- **Neutral actuator length**: ~205mm
- **Min actuator length**: 155mm (hard limit)
- **Max actuator length**: 255mm (hard limit)
- **Operating range**: 165-245mm (with safety margin)
- **Ball joint socket clearance**: 0.3mm

### Assembly Notes
1. Install threaded inserts before assembly
2. Apply PTFE lubricant to ball joints
3. Use medium-strength thread locker
4. Torque ball studs to 5 Nm
5. Route cables before final assembly

## Coordinate Formulas for Verification

```python
import math

# Base plate points
base_radius = 200  # mm
base_angles = [345, 15, 105, 135, 225, 255]  # degrees

for i, angle in enumerate(base_angles):
    rad = math.radians(angle)
    x = base_radius * math.cos(rad)
    y = base_radius * math.sin(rad)
    print(f"Base Point {i+1}: X={x:.1f}, Y={y:.1f}")

# Top plate points
top_radius = 150  # mm
top_angles = [45, 75, 165, 195, 285, 315]  # degrees

for i, angle in enumerate(top_angles):
    rad = math.radians(angle)
    x = top_radius * math.cos(rad)
    y = top_radius * math.sin(rad)
    print(f"Top Point {i+1}: X={x:.1f}, Y={y:.1f}")
```

## Quick Checklist for CAD

- [ ] Base plate: 200mm radius, 6 mounting points
- [ ] Top plate: 150mm radius, 6 mounting points
- [ ] 60° rotation between base and top patterns
- [ ] Center holes for cable routing
- [ ] Threaded inserts M5 or M6
- [ ] Motor driver mounting locations
- [ ] Teensy mounting location
- [ ] Cable management features
- [ ] No interference at full travel
- [ ] Gimbal mounting pattern on top

---

*Use this reference with the main [Stewart Platform Design](stewart-platform-design.md) document.*
