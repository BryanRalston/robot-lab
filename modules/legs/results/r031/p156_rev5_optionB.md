# L74: P-156 Option B (L60 trunnion top-plate cut-out) stress + fit, D95 plate re-check
Robot Lab ruling: T&R 7f12ce9 rejected the rev 5 side exit → Option B (rear outlet through a ~52 × 40 cut-out in the 8 mm L60 top plate). Rev 5 side-exit gates are moot (run kept for record only: `p156_rev5_check_l74.py/.json`).
Scripts: `l60_cutout_optB_l74.py` → `p156_rev5_optionB.json` (hand calc [EST]); `p156_rev5_check_l74.py` (release housing bbox); `drive_plate_sweep_d95_l74.py` → `drive_plate_sweep_d95_l74.json`.
Housing: Actuators D95 release STEP `knee_twin_housing_release_r116` rev B swapped into model_v4 (thigh-fixed).

## Fit with the release housing (model_v4 placed bbox)
- Release housing **x −184.1…−61.0, y 27.6–232.4, z 684.9–814.0** (D59 was −176.1…−79.4, top 805.5).
- **Housing top 814.0 vs top-plate underside 816 → 2.0 mm (bbox, < 3: FLAG Actuators/L60 re-check of the real fin tops vs plate).**
- Front fins at x −61.0: 8.0 mm to the plate fin tips (−53), 4.0 mm to the baffle back (−57).
- Consequence: the plate area aft of x −61 has ≤ 2 mm of air under it, so **only x −34.5…−61 (the chimney top) can pass flow**. ID's 52 × 40 at x −40…−80 is half over the housing (no flow) and half over the strut root.

## Stress (single-path 7075-T7351 plate ≤1.5 in, R-127/R-128: 262 design = 393/1.5, fall limit 393, fatigue amplitude 58 MPa)
Loads (L60/L61 basis): bracket couple **8.66 kN design / 5.77 kN walk** carried in-plane by the top plate into the strut (x −45…5, y 110–150, 40 × 8) to the femur; walk amplitude = walk/2 [EST].
- **ID cut 52 × 40, x −40…−80: FAIL.** The strut lies inside the cut's y-range (110–150 ⊂ 104–156) and lands at x −45…−40, so the cut severs the strut from both side ligaments: band 0, SF 0.
- Cut placed aft of a transverse band of depth b (feeding the ligaments into the strut; arm 6 mm, Kt 2.0 at R5 [EST]):

| band b | σ design | SF 262 | σa·Kt | SF 58 fatigue | fall capacity (σ=393) |
|---|---|---|---|---|---|
| 10 | 194.8 | 1.34 | 129.7 | **0.45** | 17.5 kN |
| 12 | 135.3 | 1.94 | 90.1 | **0.64** | 25.2 kN |
| 15 | 86.6 | 3.03 | 57.7 | 1.01 | 39.3 kN |
| 18 | 60.1 | 4.36 | 40.0 | **1.45** | 56.6 kN |
- Net section across the 52 mm hole (ligaments 144 × 8): 7.5 MPa net; Inglis Kt 5.56/4.61/4.22 at R5/R8/R10 → peak 30.7/25.4/23.3 → SF 8.5/10.3/11.2 design, 5.7/6.9/7.5 fatigue, fall net SF 52. **Net section is not the issue; the strut junction is.**
- Largest passing plain cut: band 18 → cut x −63…−88, R8 (1245 mm², −0.028 kg/side). **But it lies entirely over the release housing (2 mm gap) → no thermal value.** So a plain cut-out cannot pass both stress and flow.
- **Fall:** L60/L61 define no fall case for the bracket; capacities above are given instead. Needs the knee-bracket fall load from the fall budget (Test/T030) before booking.

## Fix proposed (Legs part, [EST], FEA owed on the bryan PC)
**Twin straps instead of the central strut:** two 20 × 8 straps at y 84–104 and 156–176, top plate to the L58 band clamps / a femur saddle, and the cut-out **x −34.5…−61 × y 104–156, R8 corners** (plate edge at −40, so the opening is the 21 × 52 plate notch plus the open strip forward of the plate) → **≈ 1320 mm² free** (≥ 1200).
- Straps: 4.33 kN each design → 27 MPa (SF 9.7); walk amplitude 9.0 × Kt 2.0 = 18 MPa (SF 3.2 vs 58); fall capacity at 393 = 126 kN total. Ligaments feed the straps directly in line (no band bending).
- Mass: notch −0.023 kg/side; strut −0.045, straps +0.054 [EST] → **≈ −0.014 kg/side, −0.029 pair [EST]** (ID's −0.047/side assumed the plain cut).
- Open items: strap-to-femur/band-clamp joint (bonded saddle per BOND_SPEC or bolted to the L58 clamp ears), and re-checking the L71 PEM/G10 thermal isolation (Thermal: no metal path to the femur bond) — the straps are a new metal path from the bracket and must keep the existing break.

## D95 plate re-placements (Actuators 27afe00, release housing, L72 pose set + ankle −52.5/−55 (P-157), knee 140, knee 145 + ankle −55, both-leg roll/yaw)
| Plate | Min | Limiter | Result |
|---|---|---|---|
| AN1 shin front (40,130,215) +x | **3.5** | tibia tube (back face, intended), also at ankle −55 | PASS |
| AN2 shin front (40,130,290) +x | **3.5** | tibia tube | PASS |
| HP1 (−88,45,1178) −x | 3.0 to pelvis shell (back-face gap, Torso's); nearest leg part 24.5 (hip yaw yoke plate [EST]) | PASS (leg parts) |
| HP2 (−88,135,1178) −x | 3.0 to pelvis shell; nearest leg part 18.0 (hip yaw yoke plate [EST]) | PASS (leg parts) |
- Shin fairing: ankle plate outer face (drive + PCB) x 40 + 10 + 16.5 = **66.5 → 3.0 mm to x 69.5: exactly at the gate.**
- Back face: tibia tube wall (≤ 50 °C likely [EST]) — OK. Hip plates' back face/pelvis temperature: Torso to judge.
