# L77/L78 fit + stop checks (Legs, 2026-10-21)
Scripts → results/r031: housing_plate_gap_l77, knee_rom_raised_plate_l77, skirt_r6_sweep_l77 (rev 6, **superseded by rev 8**), skirt_r8_sweep_l77, knee_stop_l77, knee_stop_pad_sweep_l78, knee_stop_struct_l78 (.py/.json). All model_v4 with D96 `knee_twin_housing_release_r116b`. Distances on surface samples ±1.5 mm [EST] for the STL sweeps; OCC exact for model parts.

## Housing r116b ↔ L60 top plate (knee 0–145, real fins)
| knee | 0 | 90 | 130 | 135 | 140 | 145 |
|---|---|---|---|---|---|---|
| plate z 816 | 4.86 | 9.29 | 5.60 | 4.92 | 4.22 | **3.50** |
| plate z 820 | 8.86 | 13.29 | 9.60 | 8.92 | 8.22 | 7.50 |
Tolerance (L75: 0.72 worst / 0.33 RSS) at z 816: 145° → 2.78 worst / 3.17 RSS; **135° (PU stop contact) → 4.20 worst; 141.9/143.6° (max crush) ≈ 3.0–3.6 nominal → ≈ 2.3–2.9 worst**. Verdict: with the PU stop the 4 mm raise can be dropped **only on an RSS basis**; worst-case at max crush is < 3. Keep +4 mm unless Arbiter accepts RSS.
Raised plate (z 820–828) + straps, knee 0–145 + hip ROM: housing 7.5 @145, hip-pitch RV12 rods 8.07, femur 12.1; trunnion cheeks 0.0 = the intended joint; L hand/palm placeholders 0.0 at both-leg yaw −35 (arm placeholder, also with the original plate — Arms). **PASS ≥ 3.**
Stack top z 817 → plate underside 820: 3.0 nominal, static (both thigh-rigid); tol stack PA12 ±0.3 + plate 0.15 + flatness 0.1 [EST] → 2.45 worst, foam-sealed so contact is benign. Stack walls (y 102.8–104 / 156–157.2, x −40…−33.3) overlap the strap footprint in plan but are 3.0 mm below (817 vs 820) and above (831 vs 828): **no hit**.

## Rev 8 skirt (ID df1e9e3); rev 6 superseded
- Pelvis hem ↔ thigh panel + shroud + outlet, 357 hip poses: **min 0.1 mm at (pitch 10, roll 45, yaw 45)**; ≤ 0.2 at (30,45,45), (20,45,45), (30,−20,−35/0). Zero pose 46.5. ID's 25.7 is not reproduced (our set includes the outlet stack/shroud box; same chain as skirt_outlet_l75). **FAIL 3 mm** at full roll/yaw extremes.
- Cross-leg (both legs same mirrored pose): **0.0 at (−107.3, −20, −35)** and deep flexion + adduction (ID found the same).
- Thigh panel ↔ knee housing r116b: **1.2–1.4 mm at all knee angles (FAIL)**; ↔ shank/tibia/ankle plates/v5 shin fairing ≥ 69 mm (145°).
- Air path at the 5 worst hem poses: est. free **1688–2300 mm²** (≥ 1200 and ≥ 500): open.
- Inserts: panel upper edge 3.9 mm from the v5 thigh skin (z 820–845) — lands; **lower edge 33.5 mm off the skin (z 797–817)**: no skin there — the lower inserts must go on the shroud/stack frame or a bracket. Insert coordinates not given by ID; L61 cheek windows are outboard and ≥ 69 mm away, vent bosses (z 684/796, y 112/148) are below the panel.

## Knee stop (Actuators D97/P-159; Controls 0fb7c0e 6.2 rad/s)
- Placement [EST, no CAD from Actuators]: inside the clevis there is no room (tongue y 116–144 fills it); outboard of the cheeks at r60/135° the stacks hit the knee lever r47.5 (0.0 @120°), the RV12 rods (0.0 @0°) and the GE12 eyes (0.0 @90°). Tibia 5.5 mm. **FAIL as placed — Actuators to give a real location** (e.g. on the tongue back face in the clevis bridge region).
- Structure (393 fall, R-128 bearing tiers):

| | D97 r60 (1030 N·m, 17.2 kN) | fallback r75 (830 N·m, 11.1 kN) |
|---|---|---|
| tibia 45×1.5 | **0.82 FAIL** | 1.02 |
| femur 50×1.5 | 1.03 | 1.27 |
| tongue neck 36×28 | 2.31 | 2.86 |
| striker lug 20×30 [EST] | 6.87 | 10.65 |
| holder bolts 2×M6 12.9 shear | 4.83 | 7.49 |
| cheek bearing (455 tier) | 8.91 | 13.8 |
| seat bearing | 9.5 MPa | 6.1 MPa |
- Recommend **r75 fallback** (lighter D97 fails the tibia; r75 is ≈ +0.02 kg/knee [EST]) if Actuators confirm 62.7 J within the 25 % strain travel (SF ≥ 1.5) and max ≤ 143.6°. Brief T_STOP = **830 N·m**.
- **FLAG:** T&R's 29 kN drive fall case is 1.38 kN·m at the knee (29 kN × 47.5 mm): tibia 45×1.5 SF 0.61, femur 0.77 if that moment reaches the tubes — this, not the stop, governs the tube walls (T&R/Arbiter: confirm the DF 2.0 basis; tibia needs ≈ 2.5 mm wall [EST] to pass).

## P-158 thigh-front pad (ID 77dbea6), conservative box x 46–72, y 95–165, z 540–590
Min **33.0 mm** (knee tongue at both-leg yaw −35), shank ankle bracket 40.0, RV12 rods 70.4, over knee 0–145 + hip ROM: **PASS ≥ 3**.
