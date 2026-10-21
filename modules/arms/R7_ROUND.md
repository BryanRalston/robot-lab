# RL Arms & Hands R7 (2026-10-14): tuck B, pad mount on roll output, forearm margin, Controls/Materials inputs, bryan-PC job
Tags: [EST] = estimate. Geometry = sim/v3 plus model_v4. Scripts: `tuck_r6.py`, `tuck_r6.json`.

## A. model_v4 palm drop −12 mm: pushed in **c6de2ce**
Fingers and thumb −12 mm, wrist lug extended to the dropped plate. Only a syntax/import check was run; the full audit is in Job 1.

## B. Forearm stack with D76: definitive margin
The R6 −14.5 / −13.9 figures **were computed with D76** (z +28 … +90.8). Board stack 12.4 (Electronics §16.7) → total 283.9 vs 270 = **−13.9 mm**.
- R-057's "~9 mm margin" comes from Arms' R5 error: D73 was counted at 112 mm above the pivot instead of 140 / 148.8. **It is void.**
- Steps b (spool 10 → 5 [EST]) + c (D76 start +26.5) only: **−7.4 mm**.
- Board out of the forearm (step a, +12.4) + b + c: **+5.0 mm**. With CSG-14 yaw (see E): **+2.5 mm**.
- Actuators D79 keeps the board in the forearm, so **D79 + D76 does not fit by 7.4–13.9 mm.** Arbiter decides: board to the upper arm (needs an Electronics re-layout and an ≈ 50-conductor elbow loop), or lengthening is reopened.

## C. Tuck B (R-070: pitch +5, roll 0, yaw 0, elbow 0, arm hanging at the side)
Checked against the R-065 criteria with sim/v3:

| check | value | req |
|---|---|---|
| x projection ahead of chest front | **−95.9 mm** (behind) | ≤ 0 |
| forearm (r 38) to torso | 132.7 mm | ≥ 10 |
| wrist fairing (sphere r 62, any roll) to torso | 332 mm | ≥ 10 |
| wrist/hand to pelvis box (half y 0.185); hand at y 0.282 | fairing inner edge y 0.220 → **35 mm** | ≥ 10 |
| hand to thigh capsule (outer y 0.170) | ≈ 50 mm | ≥ 10 |
| forearm to pelvis | ≈ 59 mm | ≥ 10 |
| harness | elbow 0° and shoulder pitch +5° are inside the ROM the clock-spring loops are sized for (elbow 0.144 m loop, Electronics). Loops are near neutral, no extra bend. | in ROM |
| forward-fall pitch-gear torque, inertial only [EST] | 9.54 kg × 187.5 m/s² (3 m/s, 24 mm crush) × COM drop → **≈ 343 N·m** | ≤ 369 |

- The old pitch −30 tuck is **withdrawn**: it sits 153 mm ahead of the chest.
- Tuck B's fall torque is under the limit **only with a 7 % margin, and the estimate is crude.** T-031 must measure it.
- **Risks:**
  - The hand is near the thigh line when the hip abducts or flexes during a fall. T-031 must log it.
  - In a side fall, tuck B puts the arm between the torso and the ground. The pad is on the roll output, so the arm itself is the pad carrier (consistent with ID R6).

## D. Pad mount: one answer to ID R6/R7 + Materials 0b5a79e
**Housing (shoulder_roll stator):**
- 7075-T6, **2 mm wall** (`cad_mass.py`).
- The lateral face is the curved Ø84 barrel; the flat Ø98 × 4 flange faces fore/aft.
- No tapped holes. M4 × 8 is not possible. The bare ring fails at 8.94 kN (~2.9 GPa).
- It sits on shP (it moves with pitch, not with roll).
- **Not used for the mount.**

**Mount = roll-yaw link (roll output, rotates with the arm):**
- Today it is a 60 × 40 × 50 block [EST], alloy unspecified. Its lateral face is 60 × 50 (diagonal 78), **< 87.4: too small.**
- Proposal: solid **7075-T6** link with an integral 62 × 62 × 10 face boss, 4 × M4 × 8 tapped (2·d engagement; helicoils optional). +0.024 kg/side [EST].
- Materials' 62 × 62 7075 doubler bolts to this same face. **Doubler and pad both sit on the link; nothing goes on the housing.**

**Roll bearing:**
- IKO CRBH 6013 A, C0 = **24.3 kN** (C 18.8, `iko_crb_catalog.pdf`), dp ≈ 75.
- At 15°: Fn 8.86 radial, Fs 2.37 (taken as axial, worst case). P0 = Fr + 2M/dp + 0.44Fa, with M = Fn·e, e = offset of the pad centre from the bearing plane along the roll axis:

| e mm | P0 kN | s0 |
|---|---|---|
| 0 | 9.9 | 2.45 |
| 10 | 12.3 | 1.98 |
| 20 | 14.6 | 1.66 |
| 40 | 19.4 | 1.25 |

**Requirement: pad centre within 10 mm of the CRBH plane (s0 ≥ 2.0).** The link then carries the load into the yaw joint as bending; G3 FEA.

**Bolts:** about 615 N shear per M4 12.9 against a ≈ 5 kN shear capacity: OK, provided the pad bears in compression on the boss face.

**Abduction with the 67.5 mm pad on the link:**
- At roll 0–90° the pad faces lateral and then up, away from the shoulder cap, so it is clear. It moves with the arm, so it doesn't clash with the upper arm.
- Above roll ≈ 135° the pad face turns toward the head. **Not verified (no head clearance in the light model).** Interim soft limit roll ≤ 135°; head and cap clearance goes in Job 1.
- Fallback (ID R6): shoulder_P load ring + pad bottom z ≥ +0.19 (R6 §5(2)).

**Wrist fairing:** open-frame palm side is accepted by R-070, net +0.043 pair.
- Arms condition: the 6 flexor tendons must stay inside their Ø2.5 sheaths across the open span. The tendons stay sheathed from the roll output to the palm stops (A42 routing), so nothing bare is exposed.
- If CAD shows a gap, add a 0.5 mm PC guard strip (≈ 0.005 kg [EST]).

## E. Yaw CSF-11 (D76) and mass line
- CSF-11: 11 N·m vs need. CONTRACTS v2 row 8.9 gives 1.24×. Arms sim need after the palm drop is 1.5 × 8.58 = 12.9, giving **0.85× FAIL.**
- **Arms recommends CSG-14-100 (36 N·m, 2.8×):** +2.5 mm, +0.04/side, which cancels D76's −0.04 half credit.

**Mass deltas this round (arms line unless stated):**
| item | kg |
|---|---|
| fairing net (R-070) | +0.043 |
| link face boss 2 × 0.024 [EST] | +0.048 |
| Materials doubler 2 × (62 × 62 × 4 7075) [EST, Materials to confirm thickness] | +0.086 |
| D76 −0.04 half credit, cancelled by CSG-14 yaw | 0.000 |
| **arms total** | **+0.177** |
| motor leads 0.404 → 0.130 (harness line) | −0.274 |
| net robot | −0.097 |

## F. Controls / Materials inputs
- **Pad lever:**
  - Housing-cap pad (old): lever 0.026–0.036 m (R6 §3), vs 0.06.
  - With the pad on the roll-output link, the lever to the **roll** bearing is e ≤ 0.010 m (requirement above).
  - To the shoulder_pitch bearing, the lever is the link's z offset: 0.064 m [model_v4] for a load at the link centre. Use **0.064 m** in T-030 for the R6/R7 mount.
- **Hook release:** 0.12–0.22 s (5–10 mm tendon pay-out [EST]), not 50 ms.
- **Forward fall:** untucked/brace ≫ 369. Old R5 tuck: R-065 ~510. Tuck B ≈ 343 [EST, inertial].
- **Sheaths (Materials):**
  - 6 flexor sheaths, flexor ring (z +103 … +185 above the pivot) → palm stops: **≈ 0.20 m each [EST]**, 0.21 for the thumb flexor.
  - The 5 DCX16 drives sit in the palm and have no sheath across the wrist.
  - Bend r ≥ 37.6 mm at the combined wrist (A42). Slack ≥ 10 mm.
  - **Peak stall tension:** 1.67 A cap → (1.67 − 0.036) × 18.4 mN·m/A × 103 / 4 mm spool = **775 N ideal**, 503 N at η 0.65. Design the sheath/end stops for 775 N.

## G. Job spec, bryan PC (Grok Interface)
**Job 1: audit_v4 + clash_v4** at origin/main ≥ c6de2ce.
- Wrist sweep pitch ±60 × yaw ±30 (5° grid) × roll ±170 (30°): fork/cross vs palm, sheath bores, fairing ≥ 5 mm (lower edge z ≥ +10).
- Tuck B (+5/0/0/0) and loaded tuck: arm, fairing (124 mm), harness loops vs torso, pelvis, thighs over hip ±30°, ≥ 10 mm.
- Abduction roll 0–180° with the 67.5 mm pad on the link: head/cap clearance, contact band.
- Hand board CAD fit (§16.7: LQFP corner r 29.74/30, stack 12.4) in the forearm, and the alternative 40 × 60 in the upper arm.
- Output: interference table, `audit_v4` md/json, PNGs into `modules/arms/results/`.

**Job 2: T-030/T-031** (Controls `modules/controls/fall/`, d43f14a, 2422c87).
- Tuck B instead of the −30 tuck. Pad lever 0.064 m (pitch), e ≤ 0.010 (roll).
- Log pitch-gear torque (gate 369), CRBH P0 (s0 ≥ 2), hand–thigh distance, and impact points outside the core.

**Job 8 add-on (Arms R13, R-120): pad stand-off + CRBH 7013 A FEA.** Queue via Robot Lab on the bryan PC, one Grok Build session at a time. Not launched. Supersedes the job1 R10 case (Z −64, 6013), which must not run.
- Geometry: `modules/arms/R13_STANDOFF_7013.md` + `pad_r13.json`, and ID `modules/design/pad_r10_standoff.json` (00ff254) with the Arms flange (OD 70/ID 44 × 5, 8 × M4 12.9 PCD 62 + 2 × Ø4 dowels). Hub Ø70/Ø54. CRBH 7013 A as a bearing element (C0 27.7 kN, dp 85). Housing seat OD 108/Ø100.
- Load: R10 core pressure patch 54.8², 7.0 kN peak at 15° (Fn 6.76, Fs 1.81, applied axial and downward = worst), pad centre Z −20, contact Y 102.3, e = 0/5/10 mm. Sensitivity case mu 0.15 (not credited).
- Report: s0 (≥ 2.0 at e5), Mx raw and CSG-25 SF at fault ×1.05 (≥ 1.0), rib weak-axis and face-pocket von Mises ≤ 335 MPa, flange bolt/dowel shear, no M4 separation, pad deflection (feeds the e stack, 0.5 mm assumed).
- Clash in CAD: pad + stand-off + housing Ø108 axial gap ≥ 3 mm, abduction −15…180 × pitch with the head shell (not the sphere), overhead pitch ≤ −150 / roll ≥ 170 vs the torso cover, tuck B, ID cover trims.
- Output: `modules/arms/results/job8_r13_*` md/json/png.

**Job 8b (Arms R14): stand-off R11/R14 FEA re-run.** Not launched. **Do not queue until the Arbiter rules on the R14 placement blocker** (`R14_STANDOFF_VERIFY.md`): the R-120 geometry intersects the CRBH 7013 A when the roll axis is X.
- Geometry: ID `design/pad_r11_standoff.json` (ec12542) + Arms R14 (flange OD76, bore Ø36, 2 × Ø6 m6 on PCD57, 8 × M4 12.9 PCD62, 3 × Ø8 plate access holes, R3 fillets). Use `arms/cad/r14/standoff_r14.step`, or the ruled placement (e.g. W2 wrap carrier) once decided. Housing `housing_7013_r14.step` coaxial with X.
- Loads and gates as job1_pad_r11/CASE.md (7.0 kN at 15°, axial + down, e 0/5 qualified, 10 informative; μ 0.15 sensitivity). Gate SF ≥ 1.5 vs 503 on box, plate (around the access holes), ring ligaments and root land. Deflection ≤ 0.69 mm as booked in the e stack (≤ 1 mm hard). Dowel shear, bearing at the OD76 edge, bolt separation.
- Model the flange/hub as elastic (not a fixed root at Y0), including the CRBH stiffness, so the root-on-bore issue shows.
- CAD clash (needs these models; Arms supplies the first three as STEP via `cad/r14/r14_cad.py`):
  - stand-off, housing 7013/OD108, pad envelope (Arms)
  - shoulder cover / cover window (ID, `design/cad/shoulder_pad`)
  - head shell and torso cover (Head/ID: **not yet existing**, minimum = outer-surface STEP)
  - shoulder_P bracket (Arms, to be made)
  - Checks: ≥ 3 mm everywhere through abduction −15…180 × pitch, tuck B, and overhead pitch ≤ −150 / roll ≥ 170.
- Output: `modules/arms/results/job8b_*`.
- Job 8b update (2026-10-21): the head/torso cover STEPs now exist: `modules/design/cad/covers/head_shell.step` and `torso_cover.step`. They are faceted, in mm, in the site frame (Y-up), so transform them to the arms frame (X roll axis, Y outboard, Z up) before the clash check. The torso is a coarse 28-triangle envelope, so treat its clearances as indicative. Real housing STEP: `arms/cad/r14/housing_7013_real_coaxX.step`. **Job 8b stays on hold until the Arbiter's placement ruling.**

**Job 8b: RELEASED (R-125, W2).** This supersedes the R14 "hold" and the R11/R-120 geometry. Route via Robot Lab, one Grok Build session at a time.
- Geometry: `arms/cad/r15/carrier_w2.step` (one-piece 7075-T6 carrier + flange OD76/ID36 × 5, 8 × M4 12.9 PCD62, 2 × Ø6 m6 dowels PCD57). Elastic `hub_r15.step`. CRBH 7013 A as a bearing element (C0 27.7 kN, dp 85) in `housing_7013_coaxX.step`. Pad envelope `pad_envelope_w2.step`: R10 core 54.8² × 75.3 + 0.5 tray, contact Y 138.8, pad centre X0/Z0. Params in `r15_w2.json`.
- Loads: 7.0 kN at 15° (Fn 6761, Fs 1812), axial and down, e = 0 / 2.4 (drawing limit) / 5 (informative). μ 0.15 sensitivity is not credited.
- **Gates:** vM ≤ 320 MPa (arm root, plate root and ribs, flange ligaments), s0 ≥ 2.0 at e worst (stack 1.92 mm + FE e under load), Mx ≤ 351 N·m, deflection ≤ 1 mm. **Report pad X displacement under load (e)**, plus dowel/bolt slip and separation.
- Hand expectations: arm 289 MPa, plate 295, Mx 251, s0 1.999 at e2.4.
- Clash (CAD): carrier vs OD108 ≥ 3 mm (nominal 3.0); head shell and torso cover (`design/cad/covers`, site Y-up; transform x = x_s, y = −z_s, z = y_s − 57.1). Arms light check: torso penetration at roll ≥ ~118°.
- Output: `modules/arms/results/job8b_*`.
- **Job 8b gates per R-127 (5c203ad), supersede the above:**
  - vM ≤ **294 MPa** (≤ **262** if Materials cannot cite T651 A-basis at stock thickness)
  - drawing e ≤ **2.3** (Arms notes the s0 = 2.0 crossing at 2.246 mm for gap 3.4, so proposes 2.2)
  - plate gap **3.4 ± 0.2** nominal, ≥ **3.0 loaded** (report the loaded gap)
  - Mx ≤ 351, s0 ≥ 2.0, deflection ≤ 1 mm
  - Geometry: `cad/r15/carrier_w2.step` (R-127 revision: gap 3.4, arm 60 × 4.0, R6 plate-root fillet on the drawing).
  - Hand expectations: arm 243, plate 255 (R6) / 294 (R3) MPa.
  - Roll soft limit 115° (ID: torso contact 132°).

**Stock / grain (R-128):** see `modules/arms/STOCK_GRAIN.md`, which gives stock thickness, grain direction and single-path limit for every Arms 7075 part. An unstated row takes 257 MPa.
- **Job 8b gate per R-128 (9e49b7a), supersedes 294/262 (R-127):**
  - Carrier stock is 7075-T651 **2.5 in plate**, grain L = Y (arm), LT = X, ST = Z, so the single-path vM gate is **294 MPa** (2.001–2.5 in, LT). The ≤ 2 in band (308) is not available: the carrier is 73 × 63.4 × 62.
  - Report stresses by grain axis (L = Y, LT = X), and any ST (Z) component against 271.
  - Other gates unchanged: e ≤ 2.3 (Arms proposes 2.2), gap 3.4 ± 0.2, ≥ 3.0 loaded, Mx ≤ 351, s0 ≥ 2.0, deflection ≤ 1 mm.
**Job 8c (Arms R16, option C(b)): CF forearm link FEA.** Not launched. Run after Job 8b, via Robot Lab, one Grok Build session at a time.
- Geometry:
  - CF tube Ø70/67 × 194: roll-wrapped 0/90 with an optional ±45 braid overwrap, laminate per `cf_links_r16.py` [E 75 / G 5 GPa EST until Materials cites]
  - 2 × 7075-T651 spigots Ø67/64, 20 mm bond length, 0.15 mm DP460 bondline
  - 0.8 mm 7075 heat-spreader sleeve over 120 mm
  - elbow and wrist end fittings per model_v4
  - upper-arm CF is rejected (R16), so it is not run
- Loads: bending 78 N·m (fall) and 69 N·m (elbow cap), torsion 36 N·m (wrist roll), P-042 20 kg carry (elbow 14.6), all combined at worst phase.
- Gates:
  - 7075 fittings vM ≤ the R-128 band for their stock (`STOCK_GRAIN.md`; spigots 1.0 in plate → 313; unstated 257), R-125/R-127 fall/fault = min(A-band, Sy/1.1)
  - bond peak shear ≤ 4.6 MPa and peel reported
  - CF ply failure index (Tsai-Wu) ≤ 1/1.5
  - stiffness: EI ≥ 0.8 and GJ reported vs 7075 (Controls to set a GJ floor)
  - thermal: hand-off to Thermal ladder B with the sleeve
- Output: `modules/arms/results/job8c_*`.

### §G status after R-132 / R-133 (2026-10-21). Supersedes the earlier Job 8b and 8c gate lines.
**Job 8b: RELEASED (W2 carrier, `cad/r15/carrier_w2.step`).**
- Drawing **e ≤ 2.2 mm** (s0 = 2.0 at e = 2.246; worst stack 1.92).
- Stock 7075-T651, 2.5 in plate, grain L = Y / LT = X / ST = Z.
- vM gates: **294 MPa LT** (governing in-plane), **271 MPa for any ST-loaded (Z) feature**.
- Gap 3.4 ± 0.2 nominal, ≥ 3.0 loaded. Mx ≤ 351 N·m. s0 ≥ 2.0 at e worst (stack + FE e under load). Deflection ≤ 1 mm.
- R6 plate-root fillet. Report stresses by grain axis.
- Roll soft limit is 127° (R-133).

**Job 8c: FINAL, QUEUEABLE by Robot Lab (R-132 §4). CF forearm with a 0.8 mm 7075 heat-spreader sleeve.**
- **Geometry:**
  - CF tube Ø70/67 × 194, roll-wrapped 0/90; E 75 / G 5 GPa until Materials cites
  - 2 × 7075-T651 spigots Ø67/64 (1.0 in plate → 313 MPa band), 20 mm DP460 bond each end, 0.15 mm bondline
  - **0.8 mm 7075 inner sleeve over the 120 mm flexor-motor zone, bonded**
  - elbow and wrist end fittings per model_v4
  - galvanic isolation scrim in the bondline (Materials)
- **Loads:** bending 78 N·m (fall) and 69 N·m (elbow cap); torsion 36 N·m (wrist roll); P-042 20 kg carry (elbow 14.6); combined at worst phase.
- **Gates (R-132):**
  - 7075 fittings and sleeve vM ≤ the R-128 band for their stock (`STOCK_GRAIN.md`; unstated 257); fall = min(A-band, Sy/1.1)
  - bond peak shear ≤ 4.6 MPa, peel reported
  - CF Tsai-Wu FI ≤ 1/1.5
  - EI ≥ 0.8 × 7075
- **Torsional stiffness vs Controls' gate (8f80c42, `modules/controls/arm/FOREARM_TORSION_REQ.md`):**
  - Gate 1: forearm assembly stiffness (tube + fittings + bond) **k_t ≥ 2.9 kN·m/rad**.
  - Gate 2: first torsion mode with the CSG-14-100 wrist-roll gear in series (4.7 kN·m/rad) and the payload inertia: **≥ 15 Hz** at 0.2 kg·m² (10 kg single-hand T5), and **≥ 40 Hz** hand-only (3.8e-4 kg·m²).
  - Hand calc at CF 9.8: series stiffness 3.18 kN·m/rad, so **20.1 Hz** at T5 (Controls estimates ≈ 20.1, a pass) and **460 Hz** hand-only.
  - 8c must report both: the FE assembly k_t and both modes.
  - The ±45° braid overwrap re-run happens only if the FE assembly k_t < 2.9 (mass at full).
- **Thermal:** hand off the sleeve geometry to Thermal for ladder B. The Job 8c pass alone does not release credit (R-132: booked 0 until Job 8c, Thermal and Materials all sign off).
- **Output:** `modules/arms/results/job8c_*`.
**Job 8d (Arms R17): pocketed elbow clevis + roll-yaw link FEA.** Not launched. Run after 8b/8c, via Robot Lab.
- Geometry: needs Arms CAD (to make from `R17_CLEVIS_LINK.md`):
  - clevis: base 3 mm floor, 4 mm rims, tube boss; lugs 9 mm tapered
  - link: box 60 × 40 × 50, 4 mm wall, solid bolt lands
- Loads: upper-arm fall 104 N·m; elbow cap 69 N·m; lug reaction 520 N + 78 N·m couple; yaw torque 70 N·m; 20 kg P-042 carry.
- Gates:
  - clevis 2.5 in T651: 294 LT / 271 ST
  - link 2.0 in T651: 308 (ST-loaded features 271)
  - fall = min(A-band, Sy/1.1)
  - deflection at the elbow axis ≤ 0.5 mm [EST], to be confirmed by Controls
  - report CAD mass
