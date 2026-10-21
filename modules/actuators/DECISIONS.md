
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

## D92 (job2 334e848 G3 FAIL, Legs L69/L70) Hip-pitch lever: R8/R5 blends + section b34/d40
The job2 singular point was the unfilleted upper web/arm edge at |y| 38.5 (−15.7, 38.6, −10.0); the ear root was the second hot spot.

**Hand check:** the RC FEA field 3–12 mm from that corner reads 116–157 MPa at design (p99.9 120.6). Nominal ≈ 120 MPa gives a 54 MPa amplitude. This contradicts the L69 50 MPa / 22.4 MPa amplitude [EST]. With R8 (Peterson shoulder fillet, r/d 0.24–0.27, Kt ≈ 1.3–1.42) the b30 local amplitude would be ≈ 70–76 MPa against 58, so the fillet alone FAILS and the section must grow.

**Chosen design:**
- b34/d40/d1 21, ear Ø26.
- R8 upper blend and R5 ear blend, both built as explicit concave solids (BRep fillet fails on the loft edges); lower R8 kept.
- The nominal scales 1/(d·b²) by 0.70, giving 88 MPa design / 39 MPa amplitude, then × Kt 1.35 gives a **peak ≈ 119 MPa, amplitude ≈ 53 MPa against 58** (9 % margin) [EST].
- Ear-root amplitude ≈ 48–64 MPa [EST]: at risk, and the FEA decides.
- b36/b38 and ear Ø32/34 were rejected: the RV12 rod sweep falls to 0.5–0.83 mm (<1.0). b34 gives 1.18 mm. Fillets on b30 leave the rod at 1.94.

**Mass:** 0.5207 kg per lever against 0.4642 RC, so **+0.0565 per lever, +0.113 kg robot** (2 levers) → P-155. The RC + blends only would be +0.003 per lever.

**Stock (L70):** 7075-T651 2.5 in plate. Each solid is 60 × 61.5 × 93 (+3 stock = 63 ≤ 63.5). x ∥ ST, arm plane L/LT. Single-path allowable 271 ST / 294 LT (R-128); the 119 peak passes even T7351's 239. STOCK_GRAIN line 13 (`hip_pitch_lever_r50`, 1.0 in T651 313) is the superseded lever and does not apply. The new row is below.

Re-run brief: GROKBUILD_lever_fea_r031.md §G3-R2.

## D93 (Thermal rev 4 44b7c36, ID e61cbf2, R-143) Knee plate rev 4: 18.5 mm fins + lower taper under ID's low-ε PC guard
Fins are 8 × 18.5 × 1 at 6 mm pitch, with R0.5 tips and the lower ends tapered 45° × 8 to match ID's guard chamfer. The taper alone (18 mm) gives 76.1 °C standing, over 75.5, so the fins go +0.5 mm: UA 0.248 at h 8, 75.2 °C standing duty. The corner screws are replaced by PEM FHS-M3 studs (no fin cut). ID's guard is used as-is but its inner face moves out 0.5 mm (proud 30.0); the edge seal is inboard and clears the 4 mm flange. Mass booked +0.066 kg vs rev 3 (P-153). Thermal re-check and an ID rod-sweep re-run are requested.

## D94 (Legs L71) Knee plate rev 4b: 46 mm wide (y 107–153)
8 fins × 0.75 mm at 5.75 pitch (5.0 gap), 18.5 mm, taper kept. UA 0.247, 75.4 °C standing duty (scaled from Thermal rev 4). −21 g robot. The guard must narrow to a 50 mm wall, and it still sits 1 mm from the L58 tabs (ID/Legs). Taper accepted at 18.5 mm (R-145 §4).

## D95 (Legs L72) Drive plate placements, swept with full drive envelopes
Ankle plates go on the shin front, normal +x, at (40, 130, 215/290): 3.5 mm, PASS through knee 145. Hip pitch plates go outboard of the pelvis rear wall (x −85, Torso), normal −x, at (−88, 45/135, 1178): 3.0 mm, PASS. The sweep uses the release knee housing. The knee release STEP has front fins (9 mm), and model_v4 uses the unfinned D59, so Legs should swap it. Harness to the hip pitch motors is about 0.45–0.6 m [EST]. Torso to provide the mounting; ID to check the shin cover (x ≥ 69.5) and rear cover (x ≤ −117.5).

## D96 (R-146/R-147 P-157, Legs L73–L75) Ankle toggle 3D, carrier relief, knee fin-tip trim, knee stop/peak
3D toggle −61.0° at roll 0 (Legs' 62/44 N·m at −52.5/−55 confirmed). It moves to −58.6° at roll ±18 (37.8/21.9 N·m), so kneel only at −52.5° or |roll| ≤ 10°. Carrier relief (|y| ≥ 18 lowered 6 mm, R3) gives 4.6 mm at −55° / knee 145, SF 2.4, −0.047 kg. Knee housing rear fin-tip spot trim (12 tips, −0.27 % fin area, forging margin unchanged) gives 3.5 mm to the L60 plate over knee 0–145 (r116b STEP). No knee mechanical stop exists (sim limit only; screw not bottoming), so a separate PU stop is proposed and STOP_IMPACT_N is TBD. K_PEAK = 1.0 (7267 N pair = motor peak). Details: results/D96_ANKLE_TOGGLE_CARRIER_KNEE_TRIM.md.

## D97 (Controls 0fb7c0e, Robot Lab D96 approval) PU knee stop pair at 135°
Each pad is 3 × 12 mm cast PU 90A (Freelin-Wade PUR90A) + steel shims, 30 × 30 face, r 60 mm. 62.7 J per knee (rotors 17 %). Peak 1030 N·m at 6.9° stroke (max 141.9°), energy SF 1.54, stiffness ≈ 8.6 kN·m/rad. Screw axial from rotor deceleration 1840–2590 N per screw (0.095 C0a). +0.263 kg robot (P-158). Legs owes the tongue/clevis check at 17.2 kN. results/KNEE_STOP_PU_D97.md.
