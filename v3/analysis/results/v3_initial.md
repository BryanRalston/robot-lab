# v3.0 — v2 with catalog parts substituted (before fixes)

Mass from catalog-part rollup: **80.1 kg** — actuators 45.1, hands 4.2, battery 11.4 kg (130 × Molicel P45B = 2106 Wh), structure/harness/covers 19.4.
Requirements: 5 y × 365 d × 8 h walking = 14600 h; 1 stride/s → 5.26e+07 cycles per leg; bus 44.2 V (13S at 3.4 V/cell); drive 31.8 A rms continuous / 42.4 A rms for 1 s (Everest XCR crest ratings ÷ √2); winding rise ≤ 100 K at 40 °C ambient; torque ≥ 1.5 × requirement.

## Actuators

| joint | motor | transmission | torque avail / need N·m | speed avail / need rad/s | winding ΔT K (cooling, R_h-a) | hold A rms | life L10 h | kg | result |
|---|---|---|---|---|---|---|---|---|---|
| hip_yaw | TBM2G-06013C | CSG-20-100 | 107 / 30 | 5.1 / 3 | 2 (air, 2.42 K/W) | 0.9 | 1.2e+07 | 1.24 | **FAIL** |
| hip_roll | TBM2G-11513C | CSG-25-100 | 204 / 153 | 3.9 / 3 | 6 (air, 1.21 K/W) | 3.2 | 6.0e+04 | 2.87 | PASS |
| hip_pitch | TBM2G-11513C | CSG-25-100 | 204 / 144 | 3.9 / 4 | 7 (air, 1.21 K/W) | 10.0 | 1.7e+04 | 2.87 | **FAIL** |
| knee | TBM2G-08513C | RV12x5 / 45 mm arm | 212 / 291 | 5.6 / 8 | 99 (air, 1.99 K/W) | 19.5 | 1.6e+04 | 1.20 | **FAIL** |
| ankle_pitch | TBM2G-06013C | RV12x4 / 50 mm arm | 222 / 192 | 6.5 / 6 | 348 (air, 2.99 K/W) | 10.9 | 7.3e+04 | 1.77 | **FAIL** |
| ankle_roll | TBM2G-06013C | RV12x4 / 40 mm arm | 177 / 72 | 8.1 / 4 | 15 (air, 2.99 K/W) | 1.5 | 1.8e+07 | 1.77 | PASS |
| waist_yaw | TBM2G-06013C | CSG-20-100 | 107 / 60 | 5.1 / 2 | 4 (air, 2.42 K/W) | 1.8 | 7.2e+06 | 1.24 | PASS |
| waist_pitch | TBM2G-08513C | CSG-25-100 | 204 / 145 | 3.2 / 2 | 11 (air, 1.21 K/W) | 8.8 | 4.8e+06 | 2.44 | PASS |
| shoulder_pitch | TBM2G-08513C | CSG-25-100 | 204 / 148 | 3.2 / 4 | 1 (air, 1.21 K/W) | 2.7 | 4.8e+06 | 2.44 | **FAIL** |
| shoulder_roll | TBM2G-08513C | CSG-25-100 | 204 / 148 | 3.2 / 4 | 1 (air, 1.21 K/W) | 2.7 | 9.7e+07 | 2.44 | **FAIL** |
| shoulder_yaw | TBM2G-06013C | CSG-20-100 | 107 / 59 | 5.1 / 4 | 2 (air, 2.42 K/W) | 1.8 | 3.2e+08 | 1.24 | PASS |
| elbow | TBM2G-06013C | CSG-20-100 | 107 / 74 | 5.1 / 6 | 3 (air, 2.42 K/W) | 2.2 | 1.3e+07 | 1.24 | **FAIL** |
| wrist_roll | TBM2G-05008C | CSG-14-100 | 36 / 7 | 11.8 / 6 | 0 (air, 2.69 K/W) | 0.5 | 1.2e+09 | 0.93 | PASS |
| neck_yaw | TBM2G-05008C | CSG-14-100 | 36 / 3 | 11.8 / 4 | 0 (air, 2.69 K/W) | 0.2 | 1.8e+10 | 0.93 | PASS |
| neck_pitch | TBM2G-05008C | CSG-14-100 | 36 / 2 | 11.8 / 4 | 0 (air, 2.69 K/W) | 0.1 | 5.2e+10 | 0.93 | PASS |
| wrist_pitch | TBM2G-05008C | RV12x4 / 25 mm arm | 48 / 15 | 30.1 / 6 | 1 (air, 3.42 K/W) | 1.1 | 2.0e+11 | 1.55 | PASS |
| wrist_yaw | TBM2G-05008C | RV12x4 / 25 mm arm | 48 / 9 | 30.1 / 6 | 1 (air, 3.42 K/W) | 0.7 | 9.3e+11 | 1.55 | PASS |

## Output bearings (IKO CRBH; walking L10, landing/fall static safety fs ≥ 3)

| joint | bearing | P walk N | L10 h | fs (required) | result |
|---|---|---|---|---|---|
| hip_yaw | CRBH 5013 A | 4237 | 6.8e+05 | 2.1 (3) | **FAIL** |
| hip_roll | CRBH 9016 A | 2951 | 1.6e+07 | 6.9 (3) | PASS |
| hip_pitch | CRBH 9016 A | 2951 | 4.0e+06 | 6.9 (3) | PASS |
| waist_yaw | CRBH 5013 A | 1330 | 3.2e+07 | 3.9 (3) | PASS |
| waist_pitch | CRBH 9016 A | 958 | 1.7e+09 | 13.2 (3) | PASS |
| shoulder_pitch | CRBH 9016 A | 342 | 7.0e+09 | 1.2 (1) | PASS |
| shoulder_roll | CRBH 9016 A | 342 | 4.2e+10 | 38.1 (3) | PASS |
| shoulder_yaw | CRBH 5013 A | 531 | 1.1e+09 | 10.6 (3) | PASS |
| elbow | CRBH 5013 A | 198 | 7.4e+09 | 31.8 (3) | PASS |
| wrist_roll | CRBH 5013 A | 84 | 2.6e+11 | 58.2 (3) | PASS |
| neck_yaw | CRBH 5013 A | 84 | 2.6e+11 | 58.2 (3) | PASS |
| neck_pitch | CRBH 5013 A | 84 | 2.6e+11 | 58.2 (3) | PASS |

## Bolted joints (VDI 2230-style; 12.9; μG=μK=0.12; αA=1.6; fz=11 µm; Φ=0.15 [EST])

| joint | bolts | FM,min kN | residual clamp kN | needed kN | σ max MPa | σa / σASV MPa | result |
|---|---|---|---|---|---|---|---|
| hip bracket → pelvis (landing 3BW + 0.10 m moment) | 8×M5 | 7.7 | 6.2 | 0.3 | 887 | 7 / 64 | PASS |
| hip-pitch flexspline → output flange (momentary peak by friction) | 8×M4 | 4.8 | 4.5 | 9.2 | 866 | 0 / 70 | **FAIL** |
| knee clevis → femur flange (landing 3BW, 0.12 m lever) | 4×M5 | 7.7 | 3.3 | 0.4 | 923 | 25 / 64 | PASS |
| shoulder actuator → torso frame (side-fall impact) | 6×M5 | 7.7 | -5.8 | 38.5 | 1036 | 81 / 64 | **FAIL** |

## Side fall from standing (energy method)
Energy 613 J; topple rate at impact 4.28 rad/s; hip contact 3.9 m/s → 14.1 kN; shoulder 6.4 m/s → 11.5 kN (pad 10 mm, 70 % usable crush + 3 mm structure, constant-force crush, 55/45 hip/shoulder split [EST]). These forces drive the fall FEA cases.
Shoulder-roll strain wave: impact torque 5200 N·m (force on upper arm 0.15 m below the axis) vs momentary peak 369 / ratcheting 650 N·m → with overload clutch 5200 N·m.

## Hand drive
Per hand: 6 flexor drives (maxon DCX 22 S + GPX 22 HP 111:1, Ø8 mm spool) + 5 small drives (DCX 16 S + GPX 16 LN 103:1) for abduction/thumb rotation, extension by return springs. Continuous spool torque 1.10 N·m → tendon 276 N → **38.2 N continuous fingertip force** (MCP tendon arm 9 mm, contact 65 mm from MCP in a power grasp [EST geometry]); full close (30 mm tendon) in 0.74 s. Tendon LIROS D-Pro 1 mm (195 daN): static SF 7.1. Bend fatigue: 1.75e+06 grasps in 5 y vs ≤ 5×10⁴ cycles of published evidence → not demonstrable without testing.

## Power
Walking: mechanical 307 W + copper 173 W + compute/drives/sensors → 726 W → runtime 2.6 h (2106 Wh, 90 % usable).

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

- output-bearing-static hip_yaw: CRBH 5013 A fs=2.14
- speed hip_pitch: 3.9 < 4 rad/s at 30 % torque, 44 V bus
- torque knee: 212 < 291 N·m
- speed knee: 5.6 < 8 rad/s at 30 % torque, 44 V bus
- thermal ankle_pitch: winding ΔT 348 K > 100 K (air, R_h-a 2.99 K/W)
- speed shoulder_pitch: 3.2 < 4 rad/s at 30 % torque, 44 V bus
- speed shoulder_roll: 3.2 < 4 rad/s at 30 % torque, 44 V bus
- speed elbow: 5.1 < 6 rad/s at 30 % torque, 44 V bus
- fall-shoulder-gear: 5200 N·m > momentary peak 369 (ratcheting 650)
- bolted hip-pitch flexspline → output flange (momentary peak by friction): separation_or_slip
- bolted shoulder actuator → torso frame (side-fall impact): separation_or_slip, fatigue
- tendon-fatigue-UNVERIFIABLE: needs 1.75e+06 bend cycles; published evidence ≤ 5e4 (D/d 4, 150 N)
- FEA-convergence fall_torso_panel: only one mesh level
- mass-target: 80.1 kg > 65 kg