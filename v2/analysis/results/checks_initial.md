# v2 engineering checks (initial)
All inputs are ESTIMATES unless sourced in design.py. Robot mass used: 90.3 kg.

### Actuator masses [EST]

| joint | type | motor | transmission | qty | kg each | kg total |
|---|---|---|---|---|---|---|
| hip_yaw | rotary | M85 | CSG-20-100 | 2 | 1.93 | 3.86 |
| hip_roll | rotary | M115 | CSG-25-100 | 2 | 2.85 | 5.70 |
| hip_pitch | rotary | M115 | CSG-32-100 | 2 | 4.55 | 9.10 |
| knee | linear | M85 | roller screw 4.0 mm | 2 | 1.65 | 3.30 |
| ankle_pitch | linear2 | M60 | roller screw 2.0 mm | 2 | 1.08 | 2.15 |
| ankle_roll | linear2 | M60 | roller screw 2.0 mm | 2 | 1.08 | 2.15 |
| waist_yaw | rotary | M85 | CSG-25-100 | 1 | 2.45 | 2.45 |
| waist_pitch | rotary | M115 | CSG-32-100 | 1 | 4.55 | 4.55 |
| shoulder_pitch | rotary | M85 | CSG-25-100 | 2 | 2.45 | 4.90 |
| shoulder_roll | rotary | M85 | CSG-25-100 | 2 | 2.45 | 4.90 |
| shoulder_yaw | rotary | M60 | CSG-20-100 | 2 | 1.68 | 3.36 |
| elbow | linear | M60 | roller screw 2.0 mm | 2 | 1.23 | 2.45 |
| wrist_roll | rotary | M38 | SW-14-100 | 2 | 0.85 | 1.70 |
| wrist_pitch | linear2 | M38 | roller screw 1.0 mm | 2 | 0.84 | 1.68 |
| wrist_yaw | linear2 | M38 | roller screw 1.0 mm | 2 | 0.84 | 1.68 |
| neck_yaw | rotary | M38 | SW-11-100 | 1 | 0.70 | 0.70 |
| neck_pitch | rotary | M38 | SW-11-100 | 1 | 0.70 | 0.70 |

### Mass budget [EST]

| item | kg |
|---|---|
| pelvis structure (7075 machined) | 2.0 |
| torso frame (7075 + CF shells) | 3.5 |
| thigh structure x2 | 2.0 |
| shank structure x2 | 1.6 |
| feet x2 (incl. 6-axis F/T, sole) | 1.8 |
| upper arm+forearm structure x2 | 1.6 |
| head (cameras, shell) | 1.6 |
| hands x2 (22-DoF, actuators in forearm counted here) | 2.6 |
| battery pack | 12.0 |
| compute (Jetson Thor + RT ctrl + cooling) | 1.8 |
| harness, connectors | 2.0 |
| covers/padding | 1.5 |
| thermal (pump, radiator, coolant) | 1.0 |
| actuators (all) | 55.3 |
| **TOTAL** | **90.3** |

Mass check: total 90.3 kg vs target <= 65.0 kg (Optimus Gen 1 reported 73 kg; Gen 2 is 10 kg lighter per Tesla): **FAIL**

### Squat with 20 kg (static, 110° knee flexion, per leg)

| quantity | value |
|---|---|
| trunk lean (deg) | -3.4 |
| ankle N·m | 32 |
| knee N·m | 146 |
| hip N·m | 22 |

### Joint torque & speed vs requirement (requirement = max of walk, stairs, 20 kg squat; ×1.5 safety margin)

| joint | actuator | req N·m | req×1.5 | peak avail | margin | torque | req rad/s | max rad/s | speed |
|---|---|---|---|---|---|---|---|---|---|
| hip_yaw | rotary | 23 | 34 | 107 | 4.74 | PASS | 3 | 4.2 | PASS |
| hip_roll | rotary | 115 | 173 | 204 | 1.77 | PASS | 3 | 3.1 | PASS |
| hip_pitch | rotary | 108 | 163 | 433 | 4.00 | PASS | 4 | 3.1 | **FAIL** |
| knee | linear | 146 | 219 | 314 | 2.15 | PASS | 8 | 5.3 | **FAIL** |
| ankle_pitch | linear2 | 145 | 217 | 603 | 4.17 | PASS | 6 | 3.3 | **FAIL** |
| ankle_roll | linear2 | 54 | 81 | 402 | 7.42 | PASS | 4 | 5.0 | PASS |
| waist_yaw | rotary | 40 | 60 | 204 | 5.10 | PASS | 2 | 4.2 | PASS |
| waist_pitch | rotary | 108 | 163 | 433 | 3.99 | PASS | 2 | 3.1 | PASS |
| shoulder_pitch | rotary | 99 | 148 | 204 | 2.07 | PASS | 4 | 4.2 | PASS |
| shoulder_roll | rotary | 99 | 148 | 204 | 2.07 | PASS | 4 | 4.2 | PASS |
| shoulder_yaw | rotary | 40 | 59 | 107 | 2.71 | PASS | 4 | 6.3 | PASS |
| elbow | linear | 49 | 73 | 201 | 4.11 | PASS | 6 | 5.0 | **FAIL** |
| wrist_roll | rotary | 5 | 7 | 28 | 5.71 | PASS | 6 | 8.4 | PASS |
| wrist_pitch | linear2 | 10 | 15 | 126 | 12.81 | PASS | 6 | 5.3 | **FAIL** |
| wrist_yaw | linear2 | 6 | 9 | 126 | 21.35 | PASS | 6 | 5.3 | **FAIL** |
| neck_yaw | rotary | 2 | 3 | 11 | 5.50 | PASS | 4 | 8.4 | PASS |
| neck_pitch | rotary | 1 | 2 | 11 | 7.79 | PASS | 4 | 8.4 | PASS |

### Thermal: winding temperature rise (limit 115 K = 155 °C class F at 40 °C ambient). Walk 1 h, then 10× (10 s 20 kg squat hold + 50 s walk)

| joint | motor | walk Cu loss W | walk ΔT K | hold Cu loss W | hold motor torque/peak N·m | max ΔT K | result |
|---|---|---|---|---|---|---|---|
| hip_pitch | M115 | 3 | 3 | 1 | 0.30/12.0 | 3 | PASS |
| hip_roll | M115 | 2 | 2 | 1 | 0.46/12.0 | 2 | PASS |
| knee | M85 | 28 | 41 | 135 | 2.33/5.0 | 59 | PASS |
| ankle_pitch | M60 | 17 | 21 | 3 | 0.11/2.0 | 21 | PASS |
| waist_pitch | M115 | 0 | 0 | 13 | 1.45/12.0 | 1 | PASS |
| shoulder_pitch | M85 | 0 | 0 | 30 | 1.10/5.0 | 5 | PASS |
| elbow | M60 | 0 | 0 | 20 | 0.41/2.0 | 7 | PASS |

### Structural checks (landing 3.0×BW, walking 1.3×BW, SF required ≥ 2)

| part | material | section | case | stress MPa / load | limit | SF | result |
|---|---|---|---|---|---|---|---|
| femur | 7075-T6 | Ø50×2.0 | landing | 100 | 503 (yield) | 5.01 | PASS |
| femur | 7075-T6 | Ø50×2.0 | walking fatigue | 44 | 159 (endurance) | 3.65 | PASS |
| tibia | 7075-T6 | Ø45×2.0 | landing | 105 | 503 (yield) | 4.77 | PASS |
| tibia | 7075-T6 | Ø45×2.0 | walking fatigue | 46 | 159 (endurance) | 3.48 | PASS |
| hip actuator flange bolts | 8×M5 12.9 | PCD 90 | landing | 81 | 900 (yield) | 11.13 | PASS |
| hip pitch output moment (CSG-32-100 bearing Mc=313 N·m catalog) | - | - | landing moment | 266 N·m | 313 N·m | 1.18 | **FAIL** |

### Power & runtime [EST]

| mode | W | runtime h (90% usable of 2300 Wh) |
|---|---|---|
| walking 1.2 m/s | 555 | 3.7 |
| standing/manipulating | 235 | 8.8 |
| 50/50 mix | 395 | 5.2 |

Reference: Tesla stated ~100 W sitting / 500 W walking for Optimus (AI Day 2022, via Forbes). Runtime check (mix ≥ 4 h): PASS

### Center of mass

| pose | COM x (m, + forward of ankle) | COM height m | support polygon x | result |
|---|---|---|---|---|
| standing | 0.060 | 1.02 | [-0.06, 0.18] | PASS |
| squat + 20 kg | 0.060 | 0.75 | [-0.06, 0.18] | PASS |

COM height standing / total height = 0.59 (human ≈ 0.55).

## Summary (hand checks appended below)
**8 FAILED:** mass budget, speed hip_pitch, speed knee, speed ankle_pitch, speed elbow, speed wrist_pitch, speed wrist_yaw, struct hip bearing moment

### Hand: tendon actuator capacity [EST]

| quantity | value | requirement | result |
|---|---|---|---|
| tendon force cont / peak (N) | 121 / 352 | < 250 (tendon SF 4) | **FAIL** |
| fingertip force per finger cont / peak (N) | 10.7 / 31.3 | ≥ 36.8 peak (10 kg hook grasp ×1.5) | **FAIL** |

**Hand check failures:** hand tendon SF, hand grip force
