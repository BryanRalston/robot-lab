# RL Arms & Hands R8 (2026-10-14): R-076 forearm length, mass delta, pad-face qualification
Scripts: `forearm_ext_r7.py`, `forearm_ext_r7.json`. [EST] = estimate.

## 1. Required lengthening (board in forearm, CSG-14 yaw)
| case | margin vs 270 | need |
|---|---|---|
| cited lengths, board 12.4, D76, no trims | −13.9 − 2.5 (CSG-14) = **−16.4** | 16.4 (> 15) |
| + trim c (D76 start +26.5, geometric) | −14.9 | 14.9 |
| + trim b (spool 10 → 5 [EST, not cited]) | −9.9 | 9.9 |

**Adopted: +15 mm, forearm 270 → 285** (`model_v4.py` P['forearm']).
- Margin is +0.1 mm with trim c only. It is +5.1 mm if trim b is also confirmed.
- Trim c is required: without it the need is 16.4, more than the 15 mm cap. **Flag:** this rests on 0.1 mm until Actuators cites the integrated spool (b).
- (R7's "+2.5 with CSG-14" assumed the board was in the upper arm. It does not apply now.)

## 2. Mass of the extension
Forearm shell 7075-T6, OD 70 / ID 66 (model_v4), ρ 2.81 g/cm³ (ASM 7075-T6). 6.41 cm³ × 2.81 = 0.018 kg, plus sheaths/leads +15 mm ≈ 0.001 [EST].
→ **+0.019 kg/side, +0.038 pair.**

## 3. Torque delta (R1 load model, 10 kg/hand, sim/v3 with the hand moved 15 mm and the extension mass added)
| case | elbow before → after (N·m) | shoulder_pitch before → after (N·m) |
|---|---|---|
| P-042 carry (sp −20, el 0) | 13.96 → **14.51** (≤ 15 ✓, cap margin 0.49) | 29.67 → 30.24 |
| R1 carry (−30, −60) | 40.82 → 42.41 | 63.79 → 65.41 |
| horizontal reach (−90, 0), reach 0.650 → 0.665 m | 40.82 → 42.41 | 86.76 → 88.41 |

**1.5× check on R1 statics (rating / (1.5 × static)):**
- shoulder_pitch: 82.2 + 1.65 = 83.9 → 1.5× = 125.8, against 167. Margin 1.35 → **1.33.** The momentary peak with inertia 148.2 → ≈ 151 (rated 167), still OK.
- elbow: 40.1 + 1.59 = 41.7 → 1.5× = 62.6, against 76. Margin 1.26 → **1.21.** Peak 73.5 → ≈ 75.5 vs 76: **1.01, thin.**

P-042 elbow stays ≤ 15, so the hold limit is unchanged (unlimited at ~15 N·m, Thermal).
- The 40 N·m interim cap: the R1 carry is now 42.4 N·m, above the 40 N·m ≤ 3 min cap, so the 20 kg carry must use the P-042 pose (already required).
- Inertia: the forearm + hand about the shoulder rises by ≈ (m_hand + 10) · 2 · 0.585 · 0.015 ≈ +0.19 kg·m² with payload [EST]. Controls to re-run.

**TARGETS:** no reach number in TARGETS (T5: 10 kg at full reach [EST]). Reach +15 mm → 0.665 m, and torques pass as above.
- Proportion: forearm/upper arm 0.90 → 0.95 (ID to sign off).
- Tuck B: the hand drops 15 mm, so lateral gaps are unchanged (pelvis 35, thigh ~50 mm). Controls to re-run in T-031.

## 4. Roll-yaw link face qualification (light hand calc; FEA queued, bryan PC)
- **Face bearing:** 8.86 kN over 62 × 62 = 2.3 MPa, against 7075-T6 bearing yield ~ 700 MPa (ASM) → ≫ 10. The boss overhangs the 60 × 50 link core by 1–6 mm; bending is negligible.
- **M4 × 8 in 7075 (Le = 2d):**
  - Internal thread strip ≈ π·4·8·0.75 = 75 mm² × 331 MPa (τ, ASM) = 24.9 kN, against the M4 12.9 proof load 8.78 mm² × 970 = 8.5 kN. **The bolt yields before the thread strips ✓.**
- **Shear 615 N/bolt** (2.37 kN / 4 at 15°):
  - M4 12.9 shear ≈ 0.6 · 1220 · 8.78 = 6.4 kN, SF 10.
  - Friction joint: preload ≈ 5.5 kN [EST, 70 % proof] × 4 × μ 0.15 = 3.3 kN vs 2.37 → slip SF 1.4 (the bolts carry the shear if it slips, SF 10 anyway).
- **Pass, conditional on** the roll-bearing offset e ≤ 10 mm (R7, s0 ≥ 2.0) and the G3 FEA of the link → yaw joint bending.

## 5. Arms line, delta against existing bookings (base 17.890 kg, R-041)
| item | Δ kg | source |
|---|---|---|
| fairing booked +0.079 (R-059) → net +0.043 (R-070 open frame) | −0.036 | R-059 / R-070 |
| CSG-14 yaw pair (replaces CSF-11) | +0.080 | R-076 |
| ladder B + end-cap clamps | +0.004 | R-076 |
| doubler 2 × 0.0155 | +0.031 | Materials 953cd46 |
| roll-yaw link 62 × 62 × 10 face boss 2 × 0.024 | +0.048 | [EST], geometry, ρ 2.81 |
| forearm +15 mm 2 × 0.019 | +0.038 | §2, ρ 2.81 cited, sheaths [EST] |
| **delta this round** | **+0.165** | |

- Arms line: 17.890 + 0.079 (R-059, already booked) + 0.165 = **18.134 kg**.
- If the D76 −0.04 half credit (R-057) was booked, it is superseded by the R-076 CSG-14 figure and should not be counted twice.
- Harness −0.274 stays uncredited (R-061).
- **This replaces the R7 "+0.177".**
