# v3 hardening checks (final)

Mass from catalog-part rollup: **63.8 kg** — actuators 32.0, hands 4.2, battery 8.0 kg (91 × Molicel P45B = 1474 Wh), structure/harness/covers 19.7.
Requirements: 5 y × 365 d × 8 h walking = 14600 h; 1 stride/s → 5.26e+07 cycles per leg; bus 44.2 V (13S at 3.4 V/cell); drive 31.8 A rms continuous / 42.4 A rms for 1 s (Everest XCR crest ratings ÷ √2); winding rise ≤ 100 K at 40 °C ambient; torque ≥ 1.5 × requirement.

## Actuators

| joint | motor | transmission | torque avail / need N·m | speed avail / need rad/s | winding ΔT K (cooling, R_h-a) | hold A rms | life L10 h | kg | result |
|---|---|---|---|---|---|---|---|---|---|
| hip_yaw | TBM2G-05008A | CSG-14-100 | 36 / 24 | 5.3 / 3 | 6 (air, 2.31 K/W) | 0.8 | 1.7e+05 | 1.02 | PASS |
| hip_roll | TBM2G-07608C | CSG-25-100 | 167 / 122 | 4.9 / 3 | 54 (air, 2.07 K/W) | 3.4 | 1.2e+05 | 1.52 | PASS |
| hip_pitch | TBM2G-07608C | CSG-25-100 | 167 / 115 | 4.9 / 4 | 69 (air, 2.07 K/W) | 10.6 | 3.4e+04 | 1.52 | PASS |
| knee | TBM2G-06808D | RV12x4 / 58 mm arm | 238 / 232 | 12.1 / 8 | 91 (air, 2.68 K/W) | 16.0 | 2.9e+05 | 1.81 | PASS |
| ankle_pitch | TBM2G-06808D | RV12x4 / 70 mm arm | 284 / 153 | 10.1 / 6 | 71 (air_fins, 1.34 K/W) | 12.5 | 2.8e+05 | 1.81 | PASS |
| ankle_roll | TBM2G-06808D | RV12x4 / 40 mm arm | 163 / 57 | 17.7 / 4 | 6 (air_fins, 1.34 K/W) | 2.5 | 3.5e+07 | 1.81 | PASS |
| waist_yaw | TBM2G-06008A | CSG-17-100 | 70 / 60 | 3.4 / 2 | 8 (air, 2.60 K/W) | 1.3 | 1.5e+06 | 1.03 | PASS |
| waist_pitch | TBM2G-06808A | CSG-25-100 | 116 / 115 | 2.8 / 2 | 60 (air, 2.40 K/W) | 6.7 | 9.5e+06 | 1.37 | PASS |
| shoulder_pitch | TBM2G-07608C | CSG-25-100 | 167 / 148 | 4.9 / 4 | 6 (air, 2.07 K/W) | 4.1 | 4.8e+06 | 1.52 | PASS |
| shoulder_roll | TBM2G-06813C | CSG-25-100 | 164 / 148 | 4.1 / 4 | 5 (air, 2.88 K/W) | 3.5 | 9.7e+07 | 1.24 | PASS |
| shoulder_yaw | TBM2G-06008C | CSG-17-100 | 70 / 59 | 7.6 / 4 | 3 (air, 3.45 K/W) | 2.6 | 6.9e+07 | 0.81 | PASS |
| elbow | TBM2G-05013C | CSG-20-100 | 76 / 74 | 7.6 / 6 | 9 (air, 3.89 K/W) | 3.2 | 1.3e+07 | 0.90 | PASS |
| wrist_roll | TBM2G-05008C | CSG-14-100 | 36 / 7 | 11.8 / 6 | 0 (air, 5.00 K/W) | 0.5 | 1.2e+09 | 0.55 | PASS |
| neck_yaw | TBM2G-05008A | CSG-14-100 | 36 / 3 | 5.3 / 4 | 0 (air, 5.00 K/W) | 0.1 | 1.8e+10 | 0.55 | PASS |
| neck_pitch | TBM2G-05008A | CSG-14-100 | 36 / 2 | 5.3 / 4 | 0 (air, 5.00 K/W) | 0.1 | 5.2e+10 | 0.55 | PASS |
| wrist_pitch | TBM2G-05008C | RV12x4 / 25 mm arm | 48 / 15 | 30.1 / 6 | 1 (air, 3.42 K/W) | 1.1 | 2.0e+11 | 1.55 | PASS |
| wrist_yaw | TBM2G-05008C | RV12x4 / 25 mm arm | 48 / 9 | 30.1 / 6 | 1 (air, 3.42 K/W) | 0.7 | 9.3e+11 | 1.55 | PASS |

## Output bearings (IKO CRBH; walking L10, landing/fall static safety fs ≥ 3)

| joint | bearing | P walk N | L10 h | fs (required) | result |
|---|---|---|---|---|---|
| hip_yaw | CRBH 6013 A | 3039 | 2.7e+06 | 3.5 (3) | PASS |
| hip_roll | CRBH 6013 A | 3039 | 2.2e+06 | 3.5 (3) | PASS |
| hip_pitch | CRBH 6013 A | 3039 | 5.4e+05 | 3.5 (3) | PASS |
| waist_yaw | CRBH 5013 A | 1058 | 6.9e+07 | 4.9 (3) | PASS |
| waist_pitch | CRBH 5013 A | 1058 | 1.4e+08 | 4.9 (3) | PASS |
| shoulder_pitch | CRBH 6013 A | 469 | 3.7e+08 | 1.3 (1) | PASS |
| shoulder_roll | CRBH 4010 A | 640 | 5.8e+07 | 4.4 (3) | PASS |
| shoulder_yaw | CRBH 4010 A | 640 | 5.8e+07 | 4.4 (3) | PASS |
| elbow | CRBH 3010 A | 280 | 1.5e+08 | 8.8 (3) | PASS |
| wrist_roll | CRBH 208 A | 165 | 7.1e+07 | 3.2 (3) | PASS |
| neck_yaw | CRBH 208 A | 165 | 7.1e+07 | 3.2 (3) | PASS |
| neck_pitch | CRBH 208 A | 165 | 7.1e+07 | 3.2 (3) | PASS |

## Bolted joints (VDI 2230-style; 12.9; μG=μK=0.12; αA=1.6; fz=11 µm; Φ=0.15 [EST])

| joint | bolts | FM,min kN | residual clamp kN | needed kN | σ max MPa | σa / σASV MPa | result |
|---|---|---|---|---|---|---|---|
| hip bracket → pelvis (landing 3BW + 0.10 m moment) | 8×M5 | 7.7 | 6.4 | 0.3 | 884 | 6 / 64 | PASS |
| hip-pitch flexspline → output flange (momentary peak by friction) | 8×M6 | 10.9 | 10.3 | 9.2 | 870 | 0 / 60 | PASS |
| knee clevis → femur flange (landing 3BW, 0.12 m lever) | 4×M5 | 7.7 | 4.1 | 0.3 | 913 | 20 / 64 | PASS |
| shoulder actuator → torso frame (side-fall impact) | 8×M8 | 20.0 | 15.7 | 9.6 | 890 | 8 / 54 | PASS |

## Side fall from standing (energy method)
Energy 613 J; topple rate at impact 4.28 rad/s; hip contact 3.9 m/s → 14.1 kN; shoulder 6.4 m/s → 11.5 kN (pad 30 mm, 70 % usable crush + 3 mm structure, constant-force crush, 55/45 hip/shoulder split [EST]). These forces drive the fall FEA cases.
Shoulder-roll strain wave: impact torque 1725 N·m (force on upper arm 0.15 m below the axis) vs momentary peak 369 / ratcheting 650 N·m → with overload clutch 300 N·m.

## Hand drive
Per hand: 6 flexor drives (maxon DCX 22 S + GPX 22 HP 111:1, Ø8 mm spool) + 5 small drives (DCX 16 S + GPX 16 LN 103:1) for abduction/thumb rotation, extension by return springs. Continuous spool torque 1.10 N·m → tendon 276 N → **38.2 N continuous fingertip force** (MCP tendon arm 9 mm, contact 65 mm from MCP in a power grasp [EST geometry]); full close (30 mm tendon) in 0.74 s. Tendon LIROS D-Pro 1 mm (195 daN): static SF 7.1. Bend fatigue: 1.75e+06 grasps in 5 y vs ≤ 5×10⁴ cycles of published evidence → not demonstrable without testing.

## Power
Walking: mechanical 244 W + copper 132 W + compute/drives/sensors → 622 W → runtime 2.1 h (1474 Wh, 90 % usable).

## Structure FEA (v3/cad/out/fea_v3.md)

| case | peak vM MPa | SF yield | Goodman SF (5 y) | converged |
|---|---|---|---|---|
| knee_clevis | 54 | 9.35 | 10.68 | True |
| fall_hip_bracket | 33 | 15.34 | — | True |
| fall_shoulder_housing | 56 | 8.92 | — | True |
| pelvis_hip | 44 | 11.37 | 12.98 | True |
| femur_full | 47 | 10.62 | 12.13 | True |
| fall_torso_panel | 132 | 3.04 | — | False |
| tibia_full | 81 | 6.19 | 7.06 | True |

## Cable routing (igus CFROBOT rule: bend radius ≥ 10 × d when moving)

| joint | cable Ø mm | min radius mm | required mm | result |
|---|---|---|---|---|
| elbow | 4.0 | 43 | 40 | PASS |
| hip pitch | 4.0 | 53 | 40 | PASS |
| hip roll | 4.0 | 53 | 40 | PASS |
| hip yaw | 4.0 | 53 | 40 | PASS |
| shoulder pitch | 4.0 | 53 | 40 | PASS |
| shoulder roll | 4.0 | 50 | 40 | PASS |
| shoulder yaw | 4.0 | 40 | 40 | PASS |
| wrist roll | 3.0 | 34 | 30 | PASS |
| neck pitch | 3.0 | 34 | 30 | PASS |
| neck yaw | 3.0 | 34 | 30 | PASS |
| waist pitch | 4.0 | 50 | 40 | PASS |
| waist yaw | 4.0 | 48 | 40 | PASS |
| knee | 4.0 | 45 | 40 | PASS |
| ankle (pitch+roll) | 3.0 | 35 | 30 | PASS |

## Open failures

- tendon-fatigue-UNVERIFIABLE: needs 1.75e+06 bend cycles; published evidence ≤ 5e4 (D/d 4, 150 N)
- FEA-convergence fall_torso_panel: only one mesh level