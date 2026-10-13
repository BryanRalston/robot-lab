# Leg actuator sizing, round 1 (RL Actuators, 2026-10-13)
Generated from `modules/actuators/size.py` → `results/sizing.json` (margin 1.5) and `results/sizing_m1.3.json` (margin 1.3 sensitivity). Models reused from `v3/analysis/v3.py` (actuator(), housing(), omega_max(), thermal R values) and `v3/analysis/parts.py` (TBM2G, CSG, RV, CRBH data). Gait inputs: `modules/legs/results/*.npz`, `envelope.json`.

## Design basis (decisions in DECISIONS.md)
- Design cases: walk 0.8 / 1.0 / 1.2 m/s, stairs 18 cm, push recovery, sit-to-stand. **Carry 20 kg at 1.2 m/s is a stretch case** (not sized to; margin reported).
- Need = 1.5 × gait-ID peak (CONTRACTS §0 margin rule, P-001 method). Knee need ÷ 0.71 (v3 knee linkage factor); hip_pitch twin-screw need ÷ 0.77 [EST linkage factor].
- Speed need (P-002 definition): max ω while |τ| ≥ 30 % of gait peak; hip_yaw/hip_roll/ankle_roll keep v3 [EST] 3/3/4 rad/s (turning not simulated).
- Checks per candidate: peak torque ≥ need (gear repeated-peak cap, drive current cap); speed at 0.3 × gait peak ≥ speed need (voltage limit at min bus); **every gait τ–ω sample inside the voltage-limited envelope**; RMS-torque winding rise ≤ 100 K (air + fins, 40 °C); motor RMS torque ≤ TBM2G Tc; drive RMS current ≤ Ic; **motor rpm at speed need ≤ TBM2G Nmax 8000 rpm (new check; v3 lacked it)**; CSG input rpm ≤ grease limit; RMS ≤ CSG average-torque limit.
- Bus 20S Li-ion: 68.0 V min (3.4 V/cell) … 84.0 V max. Drive Elmo Gold Twitter R70/100 EtherCAT, 49.5 A rms continuous (no peak credit taken), 95 V max, 22.2 g.

## Requirements used (one side, worst L/R)
| joint | gait peak N·m [case] | need N·m | RMS N·m (walk/stairs) | speed need rad/s | carry peak / RMS / ω30 |
|---|---|---|---|---|---|
| hip_yaw | 44.1 [stairs] | 66 | 14.0 | 3 [EST v2] | 57.3 / 16.0 / 0.2 |
| hip_roll | 117.8 [stairs] | 177 | 44.5 | 3 [EST v2] | 122.5 / 49.8 / 0.3 |
| hip_pitch | 220.4 [stairs] | 331 (429 at nominal arm ÷0.77) | 85.8 | 8.1 [walk 1.2] | 265.1 / 99.7 / 7.4 |
| knee | 154.2 [walk 1.2] | 231 (328 at nominal arm ÷0.71) | 71.9 | 13.3 [stairs] | 177.7 / 77.5 / 11.6 |
| ankle_pitch | 203.5 [walk 1.0] | 305 | 43.6 | 6.9 [stairs] | 239.1 / 51.4 / 6.6 |
| ankle_roll | 40.7 [push] | 61 | 7.4 | 4 [EST v2] | 31.1 / 8.7 / 0.5 |

## Selected leg actuators (one side)
| joint | selection | mass kg | avail peak N·m (need) | ω at 30 % gait peak rad/s (need) | motor rpm at speed need | copper W at RMS | winding ΔT K | carry: torque ratio / ΔT K | cost [EST] |
|---|---|---|---|---|---|---|---|---|---|
| hip_yaw | TBM2G-06008A + CSG-17-100 + CRBH 6013 A | 1.11 | 70 (66) | 6.1 (3) | 2865 | 6.5 | 17 | 1.22 / 22 | ~$3.4k |
| hip_roll | TBM2G-08508A + CSG-25-100 + CRBH 6013 A | 1.56 | 204 (177) | 3.6 (3) | 2865 | 12.0 | 26 | 1.67 / 33 | ~$4.1k |
| hip_pitch | **2 × TBM2G-07613D + 2 × Rollvis RV12x4, lever 50 mm (twin screw, new)** | 2.37 (2.12 + 0.25 linkage [EST]) | 454 nominal = 350 worst-angle (331) | 12.2 (8.1) | 6066 | 28.9 | 49 | 1.32 / 66 | ~$7.2k |
| knee | **2 × TBM2G-07613D + 2 × RV12x4, lever 40 mm** | 2.37 (2.12 + 0.25 linkage [EST]) | 363 nominal = 258 worst-angle (231) | 15.2 (13.3) | 7963 (Nmax 8000) | 31.7 | 54 | 1.44 / 62 | ~$7.2k |
| ankle_pitch | 2 × TBM2G-06013D + 2 × RV12x4, lever 70 mm (differential) | 1.89 (1.74 + 0.15 linkage [EST]) | 311 (305) | 13.7 (6.9) | 7267 | 11.8 | 27 | 1.30 / 37 | ~$6.8k |
| ankle_roll | same pair, lever 40 mm | shared | 177 (61) | 24.4 (4) | 2400 | 1.0 | 2 | 5.7 / 3 | shared |
| **per leg** | | **9.30** | | | | **91.9** | | | **~$28.7k** |

Each actuator mass includes motor, gear or screw + nut, output bearing, housing (v3 model, [EST] ×1.25), 2 × AksIM-2 encoders and the drive (22.2 g). Linkage hardware (crossbar lever, trunnions, rod-end bearings) was not in the v3 linear-actuator mass; it is added here as an [EST] until CAD (see D5). Costs are [EST] list-price ranges (TBM2G ~$0.9–1.5k, CSG-17/25 component set ~$0.9–1.4k, RV12 ~$1.2k, Gold Twitter ~$0.6k, AksIM-2 ~$0.25k each). No vendor quote was obtained; T10 is not enforced (CHARTER, standing decisions).

## v3 baseline vs the new needs (13S, Everest XCR)
| joint | v3 selection | mass | avail N·m | fails against walk/stairs needs |
|---|---|---|---|---|
| hip_yaw | TBM2G-05008A + CSG-14-100 | 1.02 | 36 | torque |
| hip_roll | TBM2G-07608C + CSG-25-100 | 1.52 | 167 | torque |
| hip_pitch | TBM2G-07608C + CSG-25-100 | 1.52 | 167 | torque, speed, envelope, thermal, continuous, CSG input rpm (7724 rpm > 5600 rpm) |
| knee | 2 × TBM2G-06808D + RV12x4, 58.5 mm | 1.81 | 238 | torque, speed, envelope, **motor 11 646 rpm > Nmax 8000** |
| ankle_pitch | 2 × TBM2G-06808D + RV12x4, 70 mm | 1.81 | 284 | torque |
| ankle_roll | shared | — | 163 | none |

## Rotary hip_pitch was checked and rejected
No TBM2G + CSG combination on one drive meets 331 N·m and 8.1 rad/s at 44–68 V: the torque × speed corner is drive-current and voltage limited. The lightest rotary pass, TBM2G-11526D + CSG-40-50 + Gold Twitter at 16S with 70 A rms, is 5.7 kg per hip, +3.3 kg per hip over the twin screw.

## Power (both legs, electrical at the bus, drive η 0.98 [EST], gear η 0.75 [v3], screw η 0.85)
| case | mean, no regen W | mean, shared-bus netting W | peak per joint W (joint) | peak per limb W | peak both legs W |
|---|---|---|---|---|---|
| walk 0.8 | 297 | 198 | 774 (ankle_pitch) | 1039 | 1109 |
| walk 1.0 | 404 | 258 | 987 (ankle_pitch) | 1391 | 1470 |
| walk 1.2 | 518 | 323 | 1332 (hip_pitch) | 1366 | 1612 |
| stairs 18 cm | 341 | 287 | 1093 (knee) | 2249 | 2636 |
| carry 20 kg (stretch) | 583 | 377 | 1285 (hip_pitch) | 1416 | 1992 |
| push recovery | 167 | 114 | 277 | 321 | 577 |
Rest of robot: compute 120 + sensors 40 + 26 drives × 3.3 W idle + other-joint copper 8 = 254 W (v3 lines).

## Energy (pack 20S5P Molicel P45B, 100 cells, 1620 Wh, 8.75 kg; 90 % usable)
| case | total W (no regen / netting) | runtime h (no regen / netting) | Wh for 2 h (no regen / netting) |
|---|---|---|---|
| walk 0.8 | 551 / 452 | 2.65 / 3.23 | 1224 / 1003 |
| walk 1.0 | 658 / 512 | 2.22 / 2.85 | 1461 / 1137 |
| walk 1.2 | 772 / 576 | **1.89** / 2.53 | 1716 / 1281 |
| carry 20 kg | 837 / 631 | 1.74 / 2.31 | 1859 / 1402 |

## Mass rollup (T2 ≤ 65 kg hard)
| item | v3 kg | new kg | Δ kg |
|---|---|---|---|
| leg actuators (both) | 15.36 | 18.60 (incl. 1.30 linkage [EST]) | +3.24 |
| 14 non-leg drives XCR → Gold Twitter | — | — | −0.22 |
| battery 13S7P 1474 Wh → 20S5P 1620 Wh | 7.96 | 8.75 | +0.79 |
| **robot total** | 63.79 | **67.60** | +3.81 → **over 65 kg by 2.6 kg** |
Sensitivity: margin 1.3 instead of 1.5 → 67.08 kg (hip_roll TBM2G-07608A 1.50 kg, hip_pitch 2 × 06813D at 65 mm 2.17 kg, ankle lever 60 mm). Without the [EST] linkage allowance (the v3 basis) → 66.30 kg.

---
# Round 2 update (2026-10-13 PM)
New: `cad_mass.py` (CadQuery housings + linkages → `results/cad_mass.json`, STEP files in `cad/`), `regen_sim.py` (→ `results/regen_sim.json`, `regen_sim_eod.json`), datasheets in `datasheets/` (SOURCES.md). `size.py` now uses datasheet GEAR_LEN, RV12x6, Km fix, rpm ≤ 0.95 Nmax, CAD housing/linkage masses and a CAD-area thermal re-check.

## Selected leg actuators, round 2 (one side)
| joint | selection | mass kg (r1) | housing model → CAD+fasteners kg | linkage kg | avail N·m | ω30 rad/s | motor rpm at need | ΔT K walk / carry (CAD area) | carry ratio |
|---|---|---|---|---|---|---|---|---|---|
| hip_yaw | TBM2G-06008A + CSG-17-100 + CRBH 6013 A | 1.02 (1.11) | 0.355 → 0.264 | — | 70 | 6.1 | 2865 | 17 / 22 | 1.22 |
| hip_roll | TBM2G-08508A + CSG-25-100 + CRBH 6013 A | 1.46 (1.56) | 0.366 → 0.276 | — | 204 | 3.6 | 2865 | 26 / 33 | 1.67 |
| hip_pitch | 2× TBM2G-07613D + 2× RV12x4, 50 mm | 2.15 (2.37) | 0.545 → 0.353 | 0.221 | 454 (350 worst) | 12.2 | 6066 | 58 / 78 | 1.32 |
| knee | **2× TBM2G-07613D + 2× RV12x5, 47.5 mm** | 1.98 (2.37) | 0.545 → 0.353 | 0.051 | 345 (245 worst ÷0.71) | 16.0 | **7565 ≤ 7600** | 70 / 82 | 1.37 |
| ankle_pitch/roll | 2× TBM2G-06013D + 2× RV12x4, 70/40 mm | 1.78 (1.89) | 0.410 → 0.422 (fins) | 0.032 | 311 / 177 | 13.7 | 7267 | 31 / 43 | 1.30 |
| **both legs** | | **16.79 (18.60)** | **4.44 → 3.34 (−1.11)** | **0.61 (was 1.30 EST)** | | | | | |

## Mass (T2)
Robot 63.79 − 15.36 + 16.79 − 0.22 + 0.79 = **65.79 kg** (actuator module recovered −1.81 kg vs −1.30 target). With Legs −0.50 and Torso −0.80 (R-001 items 3–4, not yet delivered): **64.49 kg**, 0.51 kg reserve.

## Regen sim, walk 1.2 m/s, 1620 Wh × 0.9
| case | whole trace (incl. ~1 s stand at each end) W / h | **steady walking 2–7 s** W / h | end-of-discharge (3.4 V/cell, IR ×1.5) steady W / h |
|---|---|---|---|
| A: no regen | 744 / 1.96 | **942 / 1.55** | 952 / 1.53 |
| B: shared bus, no charge | 566 / 2.58 | 672 / 2.17 | 678 / 2.15 |
| C: shared bus + 30 A charge | 561 / 2.60 | **667 / 2.19** | 673 / 2.17 |
Bus: 70.4–72.3 V nominal, 65.5–68.5 V end-of-discharge (≤ 90 V clamp never approached); chopper energy 5 W mean in case B, 0 in C. Bus net-negative 3 % of the time, peak −341 W (4.7 A charge, well under 30 A).
