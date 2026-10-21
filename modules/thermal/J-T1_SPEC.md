# J-T1 CFD/conjugate thermal spec: hip_pitch / thigh-clamp collar / knee, FINAL (RL Thermal, 2026-10-21)
Runs on the 'bryan' PC through Grok Interface, as Robot Lab's queue entry "Thermal J-T1" (job 14 in the 10/14 4:49 PM order; "job 11" in Robot Lab's 10/21 note). Robot Lab launches it; RL Thermal does not.
**This file supersedes** the 10/14 queue text: r1_budget losses (0040976), 4 cover/break cases, and the f4e6dfb vents.
**Outputs go to** `modules/thermal/results/J-T1/` (REPORT.md, results.json, field plots). Report to RL Thermal, RL Controls, RL Legs, RL Arbiter, Robot Lab.

## 1. Geometry (repo main at or after this commit)
| item | source | notes |
|---|---|---|
| hip_pitch twin-screw housing + motor (TBM2G 07608D class) | `modules/model/model_v4.py` / Actuators CAD | drives OFF the housings (R-062/R-066) |
| knee twin housing, **rev B fins** | `modules/actuators/cad/knee_twin_housing*.step` with the rev B fins: 14 rear × 25 mm + 7 front × 9 mm axial, 1.0 mm, 0.0703 m² (R-081, D69C) | **rev C is withdrawn** (Controls a5e14ff); the D69C trim credit is withdrawn |
| thigh fairing / knee cap / hip skirt vents | ID A36 (`modules/design/a36_vents.json`, 6f842b0) + **grille bulge +12.7 mm over the front fins (R-113, Legs/ID: grille moved out ~5 mm beyond the R1 keep-out)** | knee: inlet 84 cm² slots, rear fully open; hip: inlet 75 cm², exhaust hem band 171 cm² at 35 % (use ≥ 60 cm²; also run 70 cm² per A35/A36 note) |
| femur tube | Ø50 × 1.2 mm 7075 (L-210) | full length hip pivot → knee clevis |
| thigh-clamp collar + bond | Legs BOND_SPEC; **adhesive EA 9396 AERO** (R-112, post-cured 1 h at 82 °C) | 8 × ø7 L63 radial pins (R-115) as conduction paths, collar ↔ femur |
| A37 rev D tine break | PEI sleeves 22/12 × 8 per tine, flange lands ≤ 15 % of the face, ≥ 0.3 mm air gap (A37/A38, R-081/R-099) | model as solids, k_PEI 0.22 W/mK |
| hip rod → lever → shaft → femur path | Legs L49 path 2 | unbroken (lever-eye sleeve rejected, R-099); steel k 42 |
| **knee trunnion → femur break, L62** | Ultem 4001 bush, 12 mm pin, 1.8 mm wall (R-114/R-116), ≈ 10.6 K/W after wear | EA 9396 did **not** remove the break (R-112/R-114). Run with L62, plus one sensitivity case "unbroken" (metal pin) |
| knee rod → lever → clevis | ≥ 58 K/W path | include as solids |

## 2. Heat loads (D68/D69 basis, drives off the housings)
- **hip_pitch, worst side:** copper per `modules/thermal/results/d68_rerun.json`, temperature-dependent R(T) and Kt (D68), plus iron 5.4 W.
- **knee:** 2× TBM2G-07613D, P-042 carry × 1.1 losses from Controls `controls/thermal/winding_model.py` (the traces used in `actuators/r069_knee_fin_trim.py`).
- **Mass:** sim mass 67.1 kg (R-118). Scale leg torques by 67.1/66.2 if the traces predate it.
- Steady state **and** transient: 60 min carry from walk-hot, plus the R-081 revised duty (≤ 40 % carry, bouts ≤ 5 min).

## 3. Cases (35 °C ambient; 25 °C only for walk, as a reference)
| # | condition | relative air |
|---|---|---|
| C1 | walk 1.0 m/s + 20 kg carry, vents per A36 | 1.0 m/s mean + leg-swing motion (moving mesh or MRF; at minimum a swing-averaged 1.5 m/s and a stance 1.0 m/s pair) |
| C2 | walk **1.2 m/s** carry × 1.1, vents per A36 | 1.2 m/s + swing |
| C3 | standing still, carry pose, natural convection only | 0 |
| C4 | C1 with hip exhaust 70 cm² open | as C1 |
| C5 | C1 with the knee trunnion **unbroken** (sensitivity) | as C1 |
| C6 | C1 with closed covers (reference only; expected fail) | as C1 |

## 4. Required outputs (results.json keys)
1. **R_col** (K/W): collar + femur-fin resistance to ambient, from the solved collar heat balance (Q_in through all paths vs T_collar − T_amb). Report per case.
2. **h_eff** (W/m²K) on the knee finned housing and on the hip_pitch housing, area-averaged over the wetted area including fins. Report for C1, C2, C3 separately, plus the fin-channel velocity.
3. **Bond peak temperature** (max over the EA 9396 bondline surface, steady and transient peak) for every case.
4. **Winding temperature:** knee and hip_pitch, steady and transient peak, using the Controls winding model with the CFD h.
5. **Heat flows** (W) through: tine break, hip rod path, knee trunnion path, knee rod path, L63 pins.
6. **Collar thermocouple prediction** at the G5 location (§6), so the bench can be correlated.

## 5. Pass/fail
| quantity | pass | basis |
|---|---|---|
| bond peak, C1/C2 | **≤ 60 °C** | design point (R-101) |
| bond peak, worst of C1–C5 | **≤ 70 °C** (EA 9396 80 °C service − 10 K) | R-111/R-112 |
| R_col | **≤ 8 K/W** books the A37 rev D −0.009 credit; ≤ 14 K/W passes the design | R-081/R-101 |
| knee winding, C2 at R-081 duty | ≤ 120 °C (derate trip 130, abs 155) | D68/R-077 |
| knee h_eff, C1/C2 | ≥ 12 W/m²K lifts the R-081 carry duty limit; < 9 keeps it and triggers the fan option review (R077_KNEE_H.md) | R-077 |
| hip_pitch winding, C1/C2 | ≤ 120 °C | D68 |
| C3 standing | report only; Controls derate covers it | |
If the bond fails at R_col > 14, Thermal brings it back to the Arbiter (R-101).

## 6. Collar thermocouple (G5 correlation point)
- Type K, 0.13 mm bead, bonded with thermally conductive epoxy into a **ø1.0 × 2 mm blind hole in the collar outer wall**.
- **Location:** mid-length of the bond, on the **hip_pitch-eye side** (the tine side, where the break heat enters), 90° from the clamp split. Bead ≤ 1 mm from the bondline.
- A second bead on the femur tube 20 mm below the collar lower edge (knee side), for the trunnion-path gradient.
- J-T1 reports the predicted temperatures at both points.

## 7. Method guidance
- Conjugate heat transfer: solid conduction + air.
- Laminar/transitional (k-ω SST acceptable); y+ ≤ 1 on the fins; radiation ε 0.85 anodised, 0.9 PC/EPP.
- Mesh study: 3 levels on C1, Δbond ≤ 1 K.
- Hand-calc cross-check: `A37_BREAK_REQUIREMENT.md`, `A38_FEMUR_PATH.md` (`a38_r110.py`), `R077_KNEE_H.md`, `D69C_KNEE_FINS.md`. Flag any > 5 K disagreement in REPORT.md.
- Budget: one Grok Build session; if compute is short, run C1, C2, C3, C5 first.
