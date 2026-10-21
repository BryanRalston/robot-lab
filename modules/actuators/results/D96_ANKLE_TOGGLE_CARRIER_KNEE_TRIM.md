# D96: ankle toggle in 3D (P-157 / R-147), roll-stop carrier relief, knee housing fin-tip trim, knee stop / peak thrust (L75), 2026-10-21
Scripts: `ankle_toggle_3d.py` → `results/ankle_toggle_3d.json`; `ankle_carrier_relief_d96.py` → `results/ankle_carrier_relief_d96.json`; `knee_housing_fin_trim_d96.py` → `results/knee_housing_fin_trim_d96.json` + `cad/knee_twin_housing_release_r116b.step`; `resweep_d96.py` (Legs' `drive_plate_sweep_d95_l74.py` unchanged except the r116b housing and the relieved carrier) → `results/resweep_d96.json`.

## 1. Ankle toggle, 3D (model_v4 D60 geometry)
Setup: trunnions at (90, ±45, 450) on the shank, instep pins at (73, ±45, 100) on the foot, cross at z 80, pitch then roll (model_v4 order), q < 0 = dorsiflexion. Force per screw is 2218 N [EST, as Legs]. "Torque" below is the maximum pitch torque with |F| ≤ 2218 on each screw and zero net roll moment (τ = Jᵀ F). The singularity is det J = 0 (screw lengths vs q, φ).

| roll φ | per-screw toggle (moment arm = 0) | parallel singularity (det J = 0) | τ at −52.5° | τ at −55° | τ at −57.5° |
|---|---|---|---|---|---|
| 0° | −61.25° / −61.25° | ≈ −61.0° | **61.8** | **43.8** | 25.6 |
| ±10° | −55.7° / −67.1° | ≈ −60.1° | 50.5 | 33.9 | 17.4 |
| ±12° | −54.75° / −68.4° | ≈ −59.7° | 47.6 | 31.3 | 14.9 |
| ±18° | **−52.25°** / beyond −66° | ≈ −58.6° | **37.8** | **21.9** | 6.0 |

- **At roll 0 this confirms Legs' 2D figures exactly:** toggle −61°, 62 N·m at −52.5°, 44 N·m at −55°.
- **With roll the singularity moves in:** at ±18° the twin-screw singularity is at −58.6°, so the −55° mechanical stop has 3.6° of margin (6° at roll 0). One screw passes its own toggle at −52.25°; past that the other screw carries the pitch torque.
- **Kneel 29 N·m [EST]:**
  - At **−52.5° controlled**, the kneel passes at every roll: SF 2.1 at roll 0, **1.3 at ±18°**.
  - At **−55°** it passes only for |roll| ≤ about 12° (31 N·m). At ±18° it's 21.9 N·m, short of 29.
- **Recommendation:** keep P-157 (−0.960 mechanical / −0.916 controlled). Controls should limit kneeling deeper than −52.5° to |roll| ≤ 10°. The −55° stop is an end stop only; don't kneel against it.

## 2. Ankle-roll stop carrier relief (placeholder carrier 54 × 62 × 15, z 50–65)
- **Relief:** a top step on both ±y sides, **|y − yc| ≥ 18 mm lowered 6 mm** (z 65 → 59) along the full 54 mm length, R3 inner corners (drawing note). The stop blocks (y 31–45, z 50–60) still seat on a 9 mm face.
- **Clearance to the fork cheeks at knee 145°:** 6.1 (−45°), 5.1 (−52.5°), **4.6 (−55°)**, 3.7 (−60°) mm. Roll has no effect (the carrier rides on the cross and doesn't roll). Gate ≥3 met through −60°. Legs had 0.9 at −45° and 0 from −55°.
- **Strength [EST]:** a roll-stop hold of 3.93 kN per block (L29) acts on the 9 × 54 section at y 18, 20 mm arm: 78.6 N·m, Z 729 mm³, **108 MPa vs 7075-T7351 262 (SF 2.4)**. Stop events are rare, so fatigue doesn't govern.
- **Mass:** −2 × 54 × 13 × 6 mm³ = **−23.7 g per ankle, −0.047 kg robot**, a credit against the [EST] placeholder (not booked).
- The carrier is still a placeholder. Re-check this when it's real CAD.

## 3. Knee release housing vs the L60 trunnion top plate
- The housing **pivots with the knee** (it's not thigh-fixed), so the gap was swept over knee 0–145. The top points are the **rear fin tips at the motor-can end** (local y +58…65.8, z 1–4.3), not the boss or the body. They were 2.0 mm at zero pose and **1.9 mm at knee 145**.
- **Fix:** spot-trim (a chamfer face) on 12 rear fin tip corners, the zone within 3.5 mm of the plate in any pose. Removes 84 mm³ (0.23 g per knee), **fin area −0.00019 m² (−0.27 % of 0.0703)**.
- **Result** (`cad/knee_twin_housing_release_r116b.step`): min **3.5 mm** (at knee 145; 4.9 at knee 0). The body and boss are untouched, so the **forging margin (net 75.7 vs 211 MPa) is unchanged**.
- **Re-sweep (Legs L74 script):** AN1/AN2 3.5 mm (tibia mount, also at ankle −55); HP1/HP2 3.0 to the pelvis shell (mount); leg parts ≥18.

## 4. Legs L75 answers
**(1) Knee stop.** **No separate mechanical knee stop is designed anywhere in the repo.**
- The "knee 0…135° stops (clash-free to 145°)" in CONTRACTS l.116 is the v3 sim/MJCF joint limit (REVISIONS §F–G). No stop hardware, bumper or impact rating exists.
- It is **not** at the screw stroke end either: knee pin-to-pin min 276 ≥ 247 mm stack (CONTRACTS l.90), so the nut doesn't bottom inside the ROM.
- The Rollvis RV12 catalogue gives no end-stop or impact rating, only Ca/C0a (rollvis_rv_tables.pdf p.24). The screw must not be used as a stop: an impact on the nut/end would be limited only by C0a 27.3 kN per screw.
- **Proposal:** a separate elastomer stop pair at 135° (shank tongue against a thigh-clevis pad, like the L29 ankle PU stops), sized by Legs/Actuators. **STOP_IMPACT_N is TBD.** Until then, Legs should report capacity (as their brief says). Actuators can supply the knee joint kinetic energy at fall-mode speed once Controls gives the impact velocity.

**(2) Knee peak thrust.** **K_PEAK = 1.0 for motor-driven loads.**
- 7267 N is already the **peak**: the screw-pair thrust at motor peak torque, 2 × 2π × Tp 3.42 N·m × η 0.845 / lead 5 mm, i.e. 3634 N per screw (DECISIONS D80; RV12x5 D12).
- Tp 3.42 N·m is the TBM2G-07613D peak at Ip 45.2 Arms, D winding (tbm2g_manual §9.5.2 p.284). The drive limit doesn't bind: Gold Twitter R type peak = Ic 49.5 A (DECISIONS l.74).
- Continuous: Tmc 1.23 N·m (ΔT 130 °C) gives **1307 N per screw / 2614 N pair**.
- RV12x5: **Ca 18.1 kN, C0a 27.3 kN per screw** (SOURCES l.20, p.24). Peak is 0.20 Ca / 0.13 C0a.
- **Caveat:** externally driven (fall/impact) loads are not limited by motor torque. The screw then sees whatever the load is, up to C0a 27.3 kN, as with the forearm-roll case (FOREARM_ROLL_TORQUE.md). That's a fall-load question (T&R 29 kN), not K_PEAK.
