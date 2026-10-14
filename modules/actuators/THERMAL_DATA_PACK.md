# Thermal data pack for RL Controls (A40 / P-043), RL Actuators 2026-10-14
Sources: Kollmorgen TBM2G manual June 2023 (`datasheets/tbm2g_manual.txt`, §1.2.2, §1.3.7.4, §1.4, §9 per-frame tables; values via `v3/analysis/tbm2g.json`), Elmo MAN-G-TWI v2.011 §11.2 (`datasheets/elmo_gold_twitter_install_guide.pdf` p.76), `iron_loss.py` → `results/iron_loss.json`, `knee_thermal.py` → `results/knee_thermal.json`.

## 1. Winding temperature limit — resolved
- The manual sets the hard limit as **winding ≤ 155 °C** (§1.2.2 "it must be ensured that winding temperature doesn't exceed 155 °C"; §1.4 Kt/Ke "measured at 155 °C winding"; Tc rated at ΔT 130 K from 25 °C = 155 °C; PTC option trips at 155 °C). That is the Class F (155 °C) temperature. The manual text does not print the words "insulation class", so "Class F" is our inference from the 155 °C limit.
- **So both 130 and 140 °C are our own margins, not datasheet limits.** Recommendation for Controls: derate starts at 120 °C, the continuous-torque point is at 130 °C, and torque-off is at **140 °C**. That leaves 15 K to the 155 °C limit for observer error and single-phase hot spots (a PT1000 sees only one phase, §1.3.7.4.1). Thermal owns the final number.

## 2. Stator temperature sensor — yes
- The option is mounted under the PCB (§1.1 item 8, §1.3.7.4). It comes out on 2 white flying leads, 26 AWG ETFE, 0.5 m (a no-lead solder-pad version is also offered).
- **The thermal-device code letter is in the part number:** `A` = PT1000 RTD (IEC 60751), `B` = 3 × avalanche PTC in series (normally < 1500 Ω, > 7000 Ω when one phase hits 155 °C), `N` = none (§9 drawing "Thermal Device Options"). The letter's position in the PN is on the §1.1.7 nomenclature graphic, which does not extract as text, so check the full PN against that page.
- **Recommendation: specify `A` (PT1000)** on every TBM2G, so the observer gets a continuous correction. Kollmorgen warns the sensor is too slow for peak current (§1.3.7.4.1), so the I²t model stays in the loop. Harness: +2 × 26 AWG per motor. Electronics should allocate an analog input per motor; the Elmo has none listed for this in our notes, so that is still to be checked.

## 3. Copper mass / winding time constant
- **Not published.** The manual gives no copper mass, winding thermal capacity or thermal time constant for any TBM2G frame. Cw stays [EST] (Controls F_CU 0.25). Close it by measurement in the bench plan: a step-current heating test with the PT1000, fitting τ_w and Rwh (added to BENCH_TEST_PLAN as an open item).
- **Rth w-a (datasheet) is winding to ambient**, with the motor housed in the Kollmorgen-defined aluminium heat sink (§1.4). There is no separate winding-to-housing value. The 0.6·Rth split for Rwh is [EST] (size.py convention); keep it until the bench test.

## 4. Motor parameters, all Elmo-driven joints (datasheet §9; R hot = R25 × (1 + 0.00393 × 130))
| joint | motor | Tc130 N·m | Kt hot (155 °C) N·m/A | R l-l 25 °C Ω | R l-l 155 °C Ω (×1.511) | Km 25 °C N·m/√W | mass kg (kit) | Rth w-a K/W | iron loss a·n+b·n² (n krpm) |
|---|---|---|---|---|---|---|---|---|---|
| hip_yaw (×1/leg) | TBM2G-06008A | 0.45 | 0.121 | 1.6 | 2.418 | 0.087 | 0.139 | 2.6 | 1.56·n + 0.000·n² |
| hip_roll (×1/leg) | TBM2G-08508A | 1.21 | 0.206 | 0.86 | 1.299 | 0.203 | 0.295 | 1.93 | 1.07·n + 0.489·n² |
| hip_pitch (×2/leg) | TBM2G-07613D | 1.23 | 0.081 | 0.136 | 0.205 | 0.201 | 0.321 | 1.85 | 1.83·n + 0.195·n² |
| knee (×2/leg) | TBM2G-07613D | 1.23 | 0.081 | 0.136 | 0.205 | 0.201 | 0.321 | 1.85 | 1.83·n + 0.195·n² |
| ankle pitch/roll diff. (×2/leg) | TBM2G-06013D | 0.6 | 0.051 | 0.168 | 0.254 | 0.114 | 0.195 | 2.52 | 1.02·n + 0.058·n² |
| waist (O-T2, ×2) | TBM2G-08508A | 1.21 | 0.206 | 0.86 | 1.299 | 0.203 | 0.295 | 1.93 | 1.07·n + 0.489·n² |
| shoulder_pitch (CONTRACTS §1a) | TBM2G-07608C | 0.89 | 0.096 | 0.318 | 0.480 | 0.156 | 0.236 | 2.15 | not fitted (use 07613D/06008A fit scaled by mass [EST]) |
| shoulder_roll (CONTRACTS §1a) | TBM2G-06813C | 0.86 | 0.113 | 0.427 | 0.645 | 0.157 | 0.254 | 2.3 | not fitted (use 07613D/06008A fit scaled by mass [EST]) |
| shoulder_yaw (CONTRACTS §1a; row added R5, was mislabelled elbow) | TBM2G-06008C | 0.45 | 0.061 | 0.4 | 0.604 | 0.087 | 0.139 | 2.6 | not fitted (use 07613D/06008A fit scaled by mass [EST]) |
| elbow (CONTRACTS §1a; was mislabelled wrist roll) | TBM2G-05013C | 0.38 | 0.061 | 0.46 | 0.695 | 0.082 | 0.149 | 3.4 | not fitted (use 07613D/06008A fit scaled by mass [EST]) |
| wrist_roll (CONTRACTS §1a) | TBM2G-05008C | 0.27 | 0.04 | 0.37 | 0.559 | 0.061 | 0.111 | 3.6 | not fitted (use 07613D/06008A fit scaled by mass [EST]) |
| wrist pair D65 (×2/side) | TBM2G-05008C | 0.27 | 0.04 | 0.37 | 0.559 | 0.061 | 0.111 | 3.6 | not fitted (use 07613D/06008A fit scaled by mass [EST]) |
| knee D69 candidate | TBM2G-08513D | 1.65 | 0.085 | 0.082 | 0.124 | 0.271 | 0.403 | 1.8 | not fitted (use 07613D/06008A fit scaled by mass [EST]) |

Notes:
- The 07613 Km for winding D is 0.201: the manual prints 2.01 for winding C, a typo (D15).
- Kit mass is stator + rotor only.
- Arm motor assignments follow Arms R1_ARCHITECTURE / R2_OPEN_ITEMS. Arms owns the joint mapping.
- The neck is Dynamixel XM430 and is not covered here.
- Hold-mode strain-wave efficiency is not in the HD CSF/CSG catalog text we hold, so it is not given here (Arms asked separately).

## 5. Iron loss vs speed (per motor)
P_fe = a·n + b·n² W, with n in krpm. It is fitted from the two rated points at 155 °C in §9 (method in `iron_loss.py`):
- **07613D:** a 1.83, b 0.195. That is 2.0 W at 1 krpm, 9.1 W at 3 krpm and 24.9 W at 7.6 krpm.
- **06013D:** a 1.02, b 0.058.
- **06008A:** a 1.56, b 0.
- **08508A:** a 1.07, b 0.489.
- **Knee, walk 1.2 m/s** (legs walk_1p2 knee speed trace, mean |ω| 1.77 rad/s): **4.6 W per joint (both motors)**.

## 6. Elmo Gold Twitter drive loss (MAN-G-TWI v2.011 §11.2.1, 6–50 A / 100 V chart, 85 V curve, read by eye ±1 W)
| Motor current A (amplitude) | 5 | 10 | 20 | 30 | 40 | 50 |
|---|---|---|---|---|---|---|
| Loss W | ~2 | ~5 | ~13 | ~22 | ~32 | ~44 |

- The chart is worst-case: Elmo states measured losses are 20–30 % lower.
- Add 25–30 % for pulsed duty (§11.2.2).
- Without an added heatsink the drive is good for about 1.5 W; the flat heatsink takes 5.5 W and the finned one 7.0 W.
- The heatsink shuts down at about 85 °C, so design for ≤ 80–82 °C.
- **Knee:** I_rms is about 8.8 A per motor (12.4 A amplitude), so roughly **7 W per drive**. That is above the flat-heatsink limit, so the knee drives must be chassis-mounted to the housing (Thermal). The drive is a separate node: its heat goes into the housing, which adds to Th. **It is not in the D69 run** below.

## 7. Knee check, 1.2 m/s WBC cruise looped, 35 °C ambient, open housing (`knee_thermal.py`, Controls model + iron loss)
| Option | τ_cont at 130 °C N·m | min to 120 °C L / R | Tw at 60 min °C L / R |
|---|---|---|---|
| base 07613D | 83 | 8.5 / 7.4 | 231 / 250 |
| (a) 2x 08513D | 113 | 50.7 / 37.4 | 122 / 128 |
| (b) shank path Rha/2 | 104 | 11.9 / 9.6 | 140 / 149 |
| (d) fan h40 | 118 | None / None | 110 / 116 |
| (a)+(d) | 161 | None / None | 74 / 76 |
| (a)+(b) | 141 | None / None | 87 / 91 |

None = never reaches 120 °C. Knee RMS on this trace is 105 / 108 N·m.
