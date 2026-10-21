
## D56 (R-022 A13) Rollup re-based on modules/arbiter/mass_rollup_official.json
linkage_table.py reads the official file; emits only results/actuator_deltas.json (harness 1.28644 vs 1.2864, +0.00004; linkage 2.32616 vs 2.3262, -0.00004). No parallel robot total; mass_rollup_r6.json removed. Official credible 66.054 kg (paper 64.531; pending A1' -0.596 -> 65.458). Prior divergence of my 66.853: brain -0.584, covers -0.238, Legs r6 +0.022 missed, harness -0.038. Open: GE 12 C cost $17.20 (mine) vs $10-31 (Arbiter); ankle +0.0256 and leg actuator lines inside unitemised 47.739 until A12.

## D57 (R-022 A13) Ankle 73 mm at +/-18 roll
Pitch -45..+40 and -60..+40 identical: Lmin 262.6, Lmax 374.3, stroke 111.7, need 250.7, margin 11.9 mm OK. Lmin falls mid-ROM (L(-60)=270.5, L(-45)=278.0), so extending to -60 does not govern. Arbiter F: 10.9 mm (Lmin 262.1 / stroke 112.2) - 1 mm grid-resolution difference; use 10.9 as conservative.

## D89 (R-134..R-136) Elmo drive standoff heat plates
6061 plates on G10/PEEK standoffs (results/DRIVE_HEAT_PLATES.md, drive_heat_plates.py, cad/drive_plate_*.step). Knee 2 × 45.0 g finned (0.0273 m², 12 × 8 × 1 fins, L51 depth 25.4/26); hip_pitch 4 × 25.8; ankle 4 × 13.5; shoulder_pitch 2 × 25.8 flat. CAD mass 0.298 + hardware 0.041 [EST] = 0.339 kg; net of R-066 bare knee plates +0.300 vs R-136 +0.256 ⇒ +0.044 proposed for Arbiter booking (freeze). Duty h8 baseplate 62–75 °C, all ≤80. Mass file results/drive_heat_plates.json.

## D90 (P-055 / R-140 / R-141) Heat plates rev 2: G-TWI M2 pattern, knee stack in 26 mm, hip pitch ≤72 °C
(The D89 number is duplicated, used by both the knee forging and the heat plates; this is the next free number.) The drive mounts on 4 × M2 30.6 × 25.6 clearance holes, with screws coming up from the structure side and one serrated washer per plate (no PE lead). The knee fins moved to the drive side (6 × 15 × 1). With a 4.0 standoff the stack is 23.0 of 26 (ID 3 mm fits, 0 left) and duty is 70.7 °C at h 8. Hip pitch goes to 84 × 84 for 71.5 °C at duty. Plates total 0.347 kg (+0.008 vs R-140), proposed to the Arbiter as P-153. Thermal re-run requested for the knee gap and fin flow. See results/DRIVE_HEAT_PLATES.md rev 2.

## D91 (Thermal R131 rev 2 16f8176) Heat plates rev 3: knee plate as finned thigh-shell window
Rev 2 knee FAILED (1.17 mm fin gaps dead, ≈107–112 °C). The plate is flipped: drives on the femur side, outer black face at the 26 mm boundary, 8 × 13 × 1 fins at 6 mm pitch in the open stream (13 mm beyond L51; 12 mm minimum). UA 0.203 W/K, 71.5 °C duty h8, femur gap 7 mm with foil shield, ≈0.3 W to the femur [EST]. Fitting inside 26 mm is not achievable on Thermal's basis. Interface condition: the hip pitch/ankle/shoulder plate back faces see ≤50 °C structure, never the hip-pitch housing (no assembly CAD yet to verify). Mass 0.355 kg, +0.016 vs R-140 (P-153 updated). Legs/ID envelope change needed.
