# Actuator part stock form, thickness, grain and R-128/R-130 allowables (D87, 2026-10-21)
Rules: R-128 (7075-T651 A-basis bands ÷1.5, LT unless the drawing fixes L; ST where load runs through thickness; unstated → 257; 320 multi-path only), R-130 (7075-T7351: 262 L/LT, 239 ST). Envelopes from the STEP bounding boxes (CadQuery) + 3 mm machining stock [EST].
**Material change:** the thick-section actuator bodies go to **7075-T7351 plate**. They need > 3.0 in stock, which is outside the T651 band table, and T7351 also suits the bonded-stator/bearing press fits (SCC, as the ankle cross, R-130). Same density, so no mass change. Materials to confirm the T7351 basis covers 3.5–4.5 in plate [EST].

| part (STEP) | envelope mm | stock form / thickness | grain direction (drawing note) | load path | allowable MPa | worst static stress MPa (source) | result |
|---|---|---|---|---|---:|---:|---|
| hip yaw housing (`hip_yaw_housing.step`) | 110×110×77.2 | 7075-T7351 plate 3.5 in | axis ∥ ST (plate thickness); flange/hoop in L–LT | **single** (all leg load) | **239** (ST: bearing moment/axial runs along the axis) | 23 vM (R1 369 N·m; R127 proxy) | PASS (SF 10) |
| hip roll housing | 110×110×83.3 | T7351 plate 3.5 in | axis ∥ ST | **single** | **239** | 23 | PASS |
| hip-pitch screw body ×4 | 82×82×105.1 | T7351 plate 3.5 in | axis ∥ L (axial screw force along L) | multi (twin) | 262 (T7351 A-basis; no T7351 typical cited, so the multi value is not raised) | 18.5 (4542 N on nut tube) | PASS |
| ankle screw body ×4 (incl. GE 12 C eye lug) | 82×82×134.2 | T7351 plate 3.5 in | axis ∥ L; lug bore axis ∥ ST | multi (twin diff.) | 262 / lug 239 | lug peak 142 (Kt 2.5, R127 proxy) | PASS |
| knee twin housing release (`knee_twin_housing_release_r116.step`) | 204.8×115.8×105.1 | **7075-T7352 (or 7050-T7452) hand forging**, ~4.25 in section (R-137 §6, option a) | **grain flow along the housing (screw) axis** | **single** (one-piece, both screws, both trunnions) | **211 interim** (R-132 T7351 ST) until Materials cites the forging A/S-basis for the 4–4.5 in band | net 75.7 (D80, 3634 N) | PASS (SF 2.8 on 211) |
| knee lever r47.5 (`knee_lever_r47p5.step`) | 24×130×58.5 | 7075-T651 plate 1.0 in | **L ∥ 130 mm crossbar** (stated, so L may be used; LT value taken anyway) | **single** | **313** (0.5–1.0 in) | 208 (crossbar, DECISIONS l.410) | PASS (unstated 257 also passes) |
| hip-pitch lever r50 (`hip_pitch_lever_r50.step`) | 24×130×61 | T651 plate 1.0 in | L ∥ crossbar | single | 313 | 240 (cad_mass check) | PASS; **superseded by Legs L47 (Legs owns)** |
| **hip-pitch lever G3-R2 (`hip_pitch_lever_g3_b34_d40_e26.step`, D92/L70)** | 60×61.5×93 per solid | **7075-T651 plate 2.5 in** (63 with stock) | plate thickness ∥ x (ST); arm y–z plane L/LT | **single** | **271** ST (294 LT); T7351 alt 239 | hand peak 119 [EST] (FEA G3-R2 pending); fatigue amp ≤ 58 | PASS [EST] |
| nut-rotor hub ×12 (`nut_rotor_hub_x1.step`) | 46×46×14 | T651 plate 0.75 in | any | multi | 320 | < 10 [CALC: ~3.6 N·m screw torque] | PASS |
| GE 12 E eye ø30×12 ×6 + hip-pitch eye ×2 | 30×30×12 | T651 plate 0.5 in | bore ∥ ST | multi | 320 | bearing 35.9 net (DECISIONS l.466) | PASS |
| hip-pitch pivot inner clamp ring (`hp_bearing.py`) | ~Ø60×6 [EST] | T651 plate 0.25–0.499 in | any | single | 308 | low (clamp only) [EST] | PASS by inspection; no calc in repo |
| D76 wrist pitch/yaw unit housings ×4 (`wrist_place_d76.step` envelopes) | Ø56×62.8 each | T651 plate 2.5 in | axis ∥ ST | single (a differential needs both units) | **271** (ST, 2.001–2.5 in) | 7.6 τ, vM 13 (CSG-14 momentary 70 N·m on Ø56×2) [CALC] | PASS |
| trunnion pins ø16/ø9 | — | 42CrMo4 bar | — | single | steel (Sy 650/1.5) | 241 bending (DECISIONS l.307) | PASS (not a 7075 rule) |

- **No actuator part fails on stress**. The knee twin housing is a hand forging (R-137 §6), held at 211 MPa until Materials cites the forging allowable. The tightest are the knee lever (208 vs 313) and the old hip-pitch lever (240 vs 313, superseded).
- Unconverged FEA hot spots stay open: the hp_lever hub 293 MPa (Legs L47 replaced that lever) and the knee boss (hand calc only). G3/G4/JOB9 FEA must use these limits.
- Drawings: each part's drawing note = the "stock form / thickness / grain" column. The parts have no separate drawings; this table is the drawing note set for cad_mass parts until Arms/Legs integrate them.
