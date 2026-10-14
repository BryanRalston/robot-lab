# R-031 hip_pitch lever section check + D69 knee strap (RL Actuators, 2026-10-14)

## 1. Lever section check (`lever_r031.py`, CadQuery/OCC distances, light)
Geometry: the G2 arms of `hp_lever_fea_v2.geom()` with Legs' b/d0/d1 (R031_FIXES pick b30/d0 36/d1 19, fallback b35/d0 40/d1 21.3), compared with G2 as briefed (b25/d0 30/d1 16), all with the same R5 bore relief.

**Limitation:** `geom()` is the smooth-loft G2 arm. It does not model Legs' "cap merged into a full-depth web". The R8 junction blend also failed in OCC for both new sections (the R4 fallback only took on the baseline), so the STEPs are **unfilleted envelopes for checking, not release CAD**. Release CAD with the R8 web is still to do, ideally alongside the T&R converged FEA on the bryan PC.

| Check | G2 baseline | **Pick b30/d36** | Fallback b35/d40 | Criterion | Verdict |
|---|---|---|---|---|---|
| Mass per lever (7075 + steel needle race, script rule) | 0.332 kg | **0.394 (+0.062)** | 0.458 (+0.126) | Legs: +0.045 / +0.09 per lever | **Heavier than Legs' estimate:** +0.123 kg robot (pick), **+0.252 kg robot (fallback), past the 0.25 steel switch-over** |
| RV12 rod sweep, r6 rod over screw angle −110…+45° | 2.06 mm | **1.94 mm** | 1.07 mm | ≥ 1 mm | pick OK; fallback has only 0.07 mm of margin |
| Rod-end eye (GE12 C ø30×12 outboard of the ear, ±10° tilt) | 0.0 | 0.0 | 0.0 | ≥ 1 mm | unchanged by the section, because the ear isn't touched. The 0 comes from my proxy (0.5 mm gap with a 10° tilt touches the ear face) and is the same for G2. The real stack is D63/G2 PTFE washers |
| Max \|y\| inside r < 34 (this loft) | 54.9 | 57.7 (+2.8) | 59.4 (+4.5) | Legs L35: \|y\| ≤ 38.5 | my measure doesn't reproduce L35's 38.5 even for G2 (the loft's arm top edge runs close to the axis). **Reportable: the deeper section moves the arm edge +2.8 / +4.5 mm in \|y\|** compared with the accepted G2. Legs must re-run their L35 check with the merged-web CAD |
| Arm axis vs femur at −107.3 / +40° | 78° / 58° | same | same | ≥ 30° | OK (the arm axis is unchanged) |
| Femur tube clearance | — | — | — | ≥ 1 mm | **not determined:** my ø50 tube proxy passes through the cheeks for all three, so the proxy is wrong. Needs model_v4 placement (model_v4 currently fails to import: palm_7075 missing) |

STEPs: `cad/hip_pitch_lever_r031_b30_d36.step`, `..._b35_d40.step`, plus the baseline `..._b25_d30.step`.

## 2. Knee heat strap across the thigh trunnion (D69 path)
- **Correction:** RL Thermal is right. D69's "≥ 1.2 W/K" was wrong; the added path conductance needed is 1/0.72 − 1/1.44 = **0.69 W/K**.
- **Geometry finding:** the knee twin housing pivots on the **thigh** trunnions. Relative to the tibia it moves through the full knee ROM (0–135°) plus 60–88 mm of screw stroke, and no strap survives that. Relative to the **thigh** it only rotates about the trunnion axis by **5.7–12.6°** (computed from linkage_study r47.5 geometry, trunnion (−130, 270), both sign conventions). That's 9 mm of arc at 40 mm radius.
- **So the heat sink should be on the thigh (femur) side, not the tibia saddle** in Thermal's D69_KNEE_CHECK. The finned clamp-on spreader concept moves to the femur below the trunnion.
- **Strap sizing:**
  - The strap sits in series with Thermal's spreader (0.69 K/W at h 12, 0.59 at h 20).
  - Path target 1/0.69 = 1.45 K/W, so the strap needs ≤ 0.76 K/W, i.e. **≥ 1.32 W/K** (≥ 1.16 W/K at h 20).
- **Product: Technology Applications Inc. GFTS® graphite fiber thermal strap** (techapps.com/previous-gfts-designs; techapps.com/graphite-fiber-thermal-straps; Thermal_Straps price PDF):
  - "Large strap sections 0.5–0.9 W/K per section", in parallel combinations, U/J/S shapes. Assemblies reach > 2.5 W/K at 10 in.
  - Rated for "> 0.5 in dynamic motion" (12.7 mm, versus our 9 mm).
  - "Most custom and standard straps weigh only 10–30 g"; small straps are 0.15–0.25 W/K at 15–20 g.
  - **2 large sections (2 × 0.66 W/K mid-range) per knee.**
  - **Mass:** the vendor does not state a large-section mass. Scaling from 0.2 W/K at 17.5 g gives about 0.115 kg per knee [scaled EST]; on the vendor's 30 g/strap figure it would be 0.06. **Book 0.12 kg per knee [EST].**
  - **Cost:** $1,000–5,000 per unit (TAI PDF), so roughly $2–10k per knee.
- **Copper braid alternative:** k 390, 0.12 m loop → 406 mm² → **0.44 kg per knee** (solid-Cu equivalent before braid packing). Rejected on mass.
- **Bend life: not rated.** TAI publishes motion range only, no cycle life. The duty is about 5.8e7 strides over T9 14,600 h (T&R count) at ±6° about the trunnion, so this must be a bench flex-and-conductance test (add to O20).
- **Fallback that avoids the pivot:** (a)+(d) forced air (D69 table), or fins directly on the housing.
- **Mass delta for D69:**
  - strap 0.12 + femur spreader 0.12 (Thermal) − the 0.03 already booked = **+0.21 per knee, +0.42 robot**, on top of the motor +0.164 per knee and housing +0.04.
  - **Total for the robot: about +0.83 kg [part EST].**
