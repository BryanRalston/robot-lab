# v2 engineering checks (final)
All inputs are ESTIMATES unless sourced in design.py. Robot mass used: 64.8 kg.

### Actuator masses [EST]

| joint | type | motor | transmission | qty | kg each | kg total |
|---|---|---|---|---|---|---|
| hip_yaw | rotary | M60 | CSG-20-100 | 2 | 0.85 | 1.70 |
| hip_roll | rotary | M115 | CSG-25-100 | 2 | 1.90 | 3.80 |
| hip_pitch | rotary | M115 | CSG-25-100 | 2 | 1.90 | 3.80 |
| knee | linear | M85 | roller screw 5.0 mm | 2 | 1.54 | 3.08 |
| ankle_pitch | linear2 | M60 | roller screw 4.0 mm | 2 | 1.10 | 2.20 |
| ankle_roll | linear2 | M60 | roller screw 4.0 mm | 2 | 1.10 | 2.20 |
| waist_yaw | rotary | M60 | CSG-20-100 | 1 | 0.85 | 0.85 |
| waist_pitch | rotary | M85 | CSG-25-100 | 1 | 1.40 | 1.40 |
| shoulder_pitch | rotary | M85 | CSG-25-100 | 2 | 1.40 | 2.80 |
| shoulder_roll | rotary | M85 | CSG-25-100 | 2 | 1.40 | 2.80 |
| shoulder_yaw | rotary | M60 | CSG-20-100 | 2 | 0.85 | 1.70 |
| elbow | linear | M60 | roller screw 4.0 mm | 2 | 1.10 | 2.20 |
| wrist_roll | rotary | M38 | SW-14-100 | 2 | 0.52 | 1.04 |
| wrist_pitch | linear2 | M38 | roller screw 2.0 mm | 2 | 0.65 | 1.29 |
| wrist_yaw | linear2 | M38 | roller screw 2.0 mm | 2 | 0.65 | 1.29 |
| neck_yaw | rotary | M38 | SW-11-100 | 1 | 0.37 | 0.37 |
| neck_pitch | rotary | M38 | SW-11-100 | 1 | 0.37 | 0.37 |

### Mass budget [EST]

| item | kg |
|---|---|
| pelvis structure (7075 machined) | 1.6 |
| torso frame (7075 + CF shells) | 2.8 |
| thigh structure x2 | 2.0 |
| shank structure x2 | 1.6 |
| feet x2 (incl. 6-axis F/T, sole) | 1.8 |
| upper arm+forearm structure x2 | 1.6 |
| head (cameras, shell) | 1.6 |
| hands x2 (22-DoF, actuators in forearm counted here) | 2.6 |
| battery pack | 10.0 |
| compute (Jetson Thor + RT ctrl + cooling) | 1.8 |
| harness, connectors | 2.0 |
| covers/padding | 1.5 |
| thermal (pump, radiator, coolant) | 1.0 |
| actuators (all) | 32.9 |
| **TOTAL** | **64.8** |

Mass check: total 64.8 kg vs target <= 65.0 kg (Optimus Gen 1 reported 73 kg; Gen 2 is 10 kg lighter per Tesla): PASS

### Squat with 20 kg (static, 110° knee flexion, per leg)

| quantity | value |
|---|---|
| trunk lean (deg) | -8.6 |
| ankle N·m | 24 |
| knee N·m | 111 |
| hip N·m | 15 |

### Joint torque & speed vs requirement (requirement = max of walk, stairs, 20 kg squat; ×1.5 safety margin)

| joint | actuator | req N·m | req×1.5 | peak avail | margin | torque | req rad/s | max rad/s | speed |
|---|---|---|---|---|---|---|---|---|---|
| hip_yaw | rotary | 16 | 24 | 107 | 6.61 | PASS | 3 | 6.3 | PASS |
| hip_roll | rotary | 83 | 124 | 204 | 2.47 | PASS | 3 | 4.7 | PASS |
| hip_pitch | rotary | 78 | 117 | 204 | 2.62 | PASS | 4 | 4.7 | PASS |
| knee | linear | 111 | 166 | 226 | 2.05 | PASS | 8 | 9.3 | PASS |
| ankle_pitch | linear2 | 104 | 155 | 251 | 2.42 | PASS | 6 | 8.0 | PASS |
| ankle_roll | linear2 | 39 | 58 | 201 | 5.17 | PASS | 4 | 10.0 | PASS |
| waist_yaw | rotary | 40 | 60 | 107 | 2.67 | PASS | 2 | 6.3 | PASS |
| waist_pitch | rotary | 78 | 118 | 204 | 2.60 | PASS | 2 | 5.2 | PASS |
| shoulder_pitch | rotary | 99 | 148 | 204 | 2.07 | PASS | 4 | 5.2 | PASS |
| shoulder_roll | rotary | 99 | 148 | 204 | 2.07 | PASS | 4 | 5.2 | PASS |
| shoulder_yaw | rotary | 40 | 59 | 107 | 2.71 | PASS | 4 | 6.3 | PASS |
| elbow | linear | 49 | 73 | 101 | 2.05 | PASS | 6 | 10.0 | PASS |
| wrist_roll | rotary | 5 | 7 | 28 | 5.71 | PASS | 6 | 8.4 | PASS |
| wrist_pitch | linear2 | 10 | 15 | 63 | 6.40 | PASS | 6 | 10.7 | PASS |
| wrist_yaw | linear2 | 6 | 9 | 63 | 10.67 | PASS | 6 | 10.7 | PASS |
| neck_yaw | rotary | 2 | 3 | 11 | 5.50 | PASS | 4 | 8.4 | PASS |
| neck_pitch | rotary | 1 | 2 | 11 | 7.79 | PASS | 4 | 8.4 | PASS |

### Thermal: winding temperature rise (limit 115 K = 155 °C class F at 40 °C ambient). Walk 1 h, then 10× (10 s 20 kg squat hold + 50 s walk)

| joint | motor | walk Cu loss W | walk ΔT K | hold Cu loss W | hold motor torque/peak N·m | max ΔT K | result |
|---|---|---|---|---|---|---|---|
| hip_pitch | M115 | 2 | 2 | 0 | 0.20/12.0 | 2 | PASS |
| hip_roll | M115 | 1 | 1 | 1 | 0.33/12.0 | 1 | PASS |
| knee | M85 | 26 | 39 | 149 | 2.44/5.0 | 60 | PASS |
| ankle_pitch | M60 | 51 | 64 | 9 | 0.19/2.0 | 63 | PASS |
| waist_pitch | M85 | 1 | 1 | 27 | 1.05/5.0 | 5 | PASS |
| shoulder_pitch | M85 | 0 | 0 | 30 | 1.10/5.0 | 5 | PASS |
| elbow | M60 | 1 | 2 | 81 | 0.81/2.0 | 30 | PASS |

### Structural checks (landing 3.0×BW, walking 1.3×BW, SF required ≥ 2)

| part | material | section | case | stress MPa / load | limit | SF | result |
|---|---|---|---|---|---|---|---|
| femur | 7075-T6 | Ø50×2.0 | landing | 72 | 503 (yield) | 6.98 | PASS |
| femur | 7075-T6 | Ø50×2.0 | walking fatigue | 31 | 159 (endurance) | 5.09 | PASS |
| tibia | 7075-T6 | Ø45×2.0 | landing | 76 | 503 (yield) | 6.65 | PASS |
| tibia | 7075-T6 | Ø45×2.0 | walking fatigue | 33 | 159 (endurance) | 4.85 | PASS |
| hip actuator flange bolts | 8×M5 12.9 | PCD 90 | landing | 58 | 900 (yield) | 15.52 | PASS |
| hip pitch output moment (CSG-25-100 bearing Mc not published, not credited + 600 N·m crossed-roller support bearing [EST]) | - | - | landing moment | 191 N·m | 600 N·m | 3.15 | PASS |

### Power & runtime [EST]

| mode | W | runtime h (90% usable of 2300 Wh) |
|---|---|---|
| walking 1.2 m/s | 548 | 3.8 |
| standing/manipulating | 254 | 8.1 |
| 50/50 mix | 401 | 5.2 |

Reference: Tesla stated ~100 W sitting / 500 W walking for Optimus (AI Day 2022, via Forbes). Runtime check (mix ≥ 4 h): PASS

### Center of mass

| pose | COM x (m, + forward of ankle) | COM height m | support polygon x | result |
|---|---|---|---|---|
| standing | 0.060 | 1.00 | [-0.06, 0.18] | PASS |
| squat + 20 kg | 0.060 | 0.76 | [-0.06, 0.18] | PASS |

COM height standing / total height = 0.58 (human ≈ 0.55).

## Summary (hand checks appended below)
**All checks pass.**

### Hand: tendon actuator capacity [EST]

| quantity | value | requirement | result |
|---|---|---|---|
| tendon force cont / peak (N) | 121 / 352 | < 500 (tendon SF 4) | PASS |
| fingertip force per finger cont / peak (N) | 14.7 / 43.0 | ≥ 36.8 peak (10 kg hook grasp ×1.5) | PASS |

**Hand check failures:** none
