# Job 3 diagnosis and job 3c (Torso, 2026-10-21; R-149, Robot Lab job 3 ruling, T&R b1fe48f)

## 1. Status of pocketing credit
**All pocketing credit is pulled.** Job 3 / 3b FAIL (fea/job3/REPORT.md). **P-148 (rails) and P-149 (partition) are ON HOLD** until job 3c passes. P-145, P-146, P-147 and P-150 do not depend on job 3 and stand.

## 2. Where LC1 33.5 kN and the 0.05 mm gate came from (R-149 item 1)
- **33.5 kN:** git `-S` trace: first in 1f3a99b (R-079, 2026-10-14, T031 rev 2 "backing sized at 22.35 kN × 1.5"), then 357cca1 (R-084), then ed6fe55. It came from the task instruction "size the backing for the new ceiling × 1.5 margin" and R-084 "22.35 kN × 1.5 = 33.5 kN": a backing sizing load, not a cited design load. In 946aa68 (FEA spec FINAL) **I then also applied SF ≥ 2 on top of an allowable that already contains 1.5** (480/1.5 = 320, R-123). That is 1.5 × 2 × 1.5 = 4.5 on typical yield. **That stacking was mine and unsourced.**
- **0.05 mm land deflection gate:** introduced by me in **946aa68** ("land deflection ≤ 0.05 mm at LC1 (≥ 10× pad stiffness of 0.53 MN/m)"). **No source; the arithmetic is wrong.** 10 × 0.53 MN/m = 5.3 MN/m gives 22.35 kN / 5.3 MN/m = **4.2 mm**, not 0.05 mm. I admit this error. Every job 3 "land deflection FAIL" was judged against it.
- **Both are superseded by T&R b1fe48f** (reliability/CHEST_DESIGN_LOAD.md):
  - Limit 29.0 kN, ultimate 43.5 kN.
  - LC1a: normal, uniform on 101 × 101. LC1b: ±25 mm offset. LC1c: 25°, 21.2 kN normal + 9.9 kN sideways.
  - At limit: ≤ fall allowable min(A-basis, Sy/1.1), 7075 ≈ 386 MPa (assumed). No permanent set; CFRP first-ply FI ≤ 1. Buckling ≥ 1.5.
  - At ultimate: no rupture, buckling ≥ 1.0.
  - **Land stiffness ≥ 5.3 MN/m (≤ 5.5 mm at 29 kN).** The 0.05 mm gate and SF ≥ 2 stacking are deleted. Mode 1 ≥ 80 Hz and LC2 per R-127 are kept.
  - The R-149 item 2 deflection proposal (≥ 5.3 MN/m, plus no contact across the pack gap) is therefore **adopted by T&R as the gate**. Remaining Torso add-on (proposal): land deflection at 29 kN + 2 mm ≤ the pad-land-to-pack-lid clearance.

## 3. Why job 3 failed (model, not only design)
- The stand-in had the 12 mm bulkhead carried **only by two 12 × 20 mm posts** to the pelvis, with no shell, pack bay or side frames. LC1 was a two-post cantilever: 58 mm deflection, post ligament 1.5 GPa, buckling 1.0 (posts). Mode 1 64 Hz was the torso mass on the posts. LC2 was post bending.
- The job 3 pelvis was the old 140 × 260 × 60 stand-in, not model_v4 (170 × 370 × 104 × 4, open top/bottom, plus an 8 mm waist deck). Fixed in 5abcd56 / 3c.
- **Found while building 3c:** the job 3 partition (x −10, z 0–300) and the bulkhead lower edge ran through the model_v4 pack envelope (185 × 220 × 144, torso z 60–204). In 3c the partition is above the pack (z 205–300) and the pack bay is a closed box.
- **3b fix:** the model_v4 pelvis is open top/bottom, so R-127's candidate "top/bottom webs" do not exist. The only sandwich candidate is the 8 mm waist/hip-yaw deck (Legs interface). The 3b pelvis-wall sandwich is withdrawn (side walls fail shear, R-127). **3b credit 0**; the deck sandwich is a later Legs-agreed item.

## 4. Job 3c design: closed boxes, mass at full (`fea_job3c.yaml`)
- **Pack-bay torsion box** replaces the posts. 7075: sides y ±115, 3 mm (the pack rail walls); front web x +106 and rear web x −84, 2 mm; lid 1.5 mm at z 140 (pack lid). Seated on the model_v4 pelvis plus the 8 mm deck.
- **Closed sternum box:** 2 shear webs at y ±60, 3 mm, plus a 3 mm top cap at z 300, tying the bulkhead/land back to the bay rear web.
- Loads and gates per T&R b1fe48f (§2). LC1 variants LC1a/b/c at 29 kN against fall allowables (bulkhead/box 386 = 1.5 × 257, ST 3.0 in; pelvis 406 = 1.5 × 271; CFRP FI proxy 450 [EST]). LC1u at 43.5 kN against Ftu ≈ 504 [EST, verify MIL-HDBK-5H] for no rupture. LC2 SF 1.0 on R-128 allowables (R-127). Mode 1 ≥ 80. Buckling ≥ 1.5 on LC1a.
- **[COARSE] box run (h 25 mm, 23.7k nodes, 49 s; fea/job3c_COARSE_results.json):**
  - **Fixed:** land deflection **1.54 mm at 29 kN (k ≈ 19 MN/m ≥ 5.3, PASS)**, 2.1 mm offset, 1.3 mm at 25°. Buckling **4.6 (≥ 1.5, PASS)**. Mode 1 **382 Hz (≥ 80, PASS; was 64)**. LC2 bulkhead SF **1.14, pelvis 2.79 (PASS; was 0.77 posts)**. LC3–LC6 PASS.
  - **Still failing:** bulkhead-group stress SF 0.86 (LC1a), 0.56 (LC1b), 0.82 (LC1c), 0.75 (ultimate). Pelvis 0.82 (LC1b), 0.996 (ultimate). At h 25 on 2–3 mm walls these are junction peaks (web-to-lid, land step) and not converged. The refined run on the bryan PC decides.
  - Pre-sized fixes if the refined peaks stay: R3 fillets at web/lid/land junctions, a 3 mm lid, and webs 3 → 4 mm locally under the land.
- **Mass at full (mesh):** bulkhead + land + rib + boxes **3.41 kg**, against job 3 bulkhead + posts **1.99 kg** → **+1.43 kg [CALC, full]**. Not yet credited against the pack enclosure walls/rails (0.75 + 0.20) that the bay box partly replaces. That overlap must be itemised with Electronics/pack before any credit (half credit at most). Pelvis 3.21 kg is the model_v4 shell plus deck (existing, not new). Partition 0.04 kg.
- **Verdict:** 3c fixes stiffness, buckling, mode 1 and LC2 at coarse mesh, at a large full-mass cost. Stress is open pending the refined PC run.

## 5. Cartridge spec additions (T&R b1fe48f)
- **Dynamic crush coupon per lot:** drop or impact at **5.7 m/s**. Peak force ≤ **29.0 kN** (98 × 98 face, 0°), plateau within the R-102 band (quasi-static equivalent 19.5–22.3 kN). Record densification strain.
- **Pre-crush inspection:** pre-crush depth and evenness (no cell tearing; first-peak removed, initial peak ≤ 1.05 × plateau), dimensional check 98 × 98 × 116 ±0.5, bond-face flatness ≤ 0.2 mm, ribbon direction marked (L along z).

## 3c-final (aligned to model_v4 pack), coarse run 2026-10-21
- **Geometry:** bay box set to the model_v4 pack envelope (pack x −80.5…104.5, y ±110, sim z 129.6–273.6, 144 mm tall) plus a 4 mm wall: box x −84.5…108.5, y ±115, z 120–278. 4 mm land webs under the land. Front window y ±56. Lid 1.5 mm is the baseline; 3 mm is the variant (fea_job3c_lid3.yaml). **R3 fillets were NOT modelled** (left for the fine mesh).
- **CLASH: OPEN.** The 116 mm core plus socket wall (land x 56–59, core x 56–172, z 171–269) overlaps the pack's front-top corner and the box front web by about 48–52 mm in x. The bulkhead also sits inside the pack envelope. Minimum-change options:
  - (i) Notch the pack's front-top corner by about 52×110×100 mm and relocate about 10 cells [EST] (Electronics). Can be combined with moving the pack rear 26.5 mm to the shell inner wall. This is the recommended option.
  - (ii) Move the skin out 52 mm to x ≈227 (ID standout).
  - (iii) A 64 mm core fails the 57 mm stroke, so it is rejected.
- **Coarse results, 1.5 mm lid / 3 mm lid:**
  - SF_bulkhead: LC1a 0.74/0.80, LC1b 0.43/0.52, LC1c 1.01/1.10, LC1u 0.64/0.70.
  - SF_pelvis: about 0.33/0.27/0.41/0.28.
  - SF_posts: about 0.16/0.13/0.20/0.14.
  - Land deflection 138 mm at 29 kN: fails. Mode 1: 37.6/36.5 Hz, fails. Buckling 18/17, passes. LC2 passes.
  - **Model artefact:** the aligned box floor (z 120) no longer touches the pelvis, so the whole load path runs through the two stand-in posts. The previous box run (floor tied to the pelvis) gave about 19 MN/m and 382 Hz. Next step: tie the floor to the pelvis deck (the floor at z 120 needs to meet the pelvis top) or make the box sides the waist path. Re-run after that.
- **Mass (mesh, full):**
  - 1.5 mm lid: box + bulkhead 4.47 + posts 0.57 = 5.04 kg, against job 3's 1.99 kg → +3.05 gross. With the same enclosure credit as before (−0.74), net **+2.31 kg [CALC]**.
  - 3 mm lid: 5.20 kg → +3.21 gross, net **+2.47 kg**.
  - This supersedes the +0.692 net figure.

## 3c-final Option A: waist load path + notched pack (2026-10-21, supersedes the 3c-final section above)
**Waist path (model_v4 build_upper).** The torso hangs on the waist_pitch output through ONE torso bracket: a +y cheek 70×8 from wp−30 to tb, plus the 220×340×8 floor plate at tb. waistY is a yoke plate 120×140×8 + a −y cheek 70×8 on the waist_yaw output (yaw axis dk+35, pitch axis dk+143 = global 1349.6, tb 1409.6).
- Modelled as is: no posts. Pelvis at its true height (sim z −154…−50, deck top −73.4).
- Actuator housings are solid Al stand-ins (stiffer than real).
- BC: pelvis bottom fixed (conservative for a fall: the real reaction is whole-body inertia).

**Geometry, Option A (P-057):**
- The box follows the notched pack: socket walls at y ±50.5…54.5, notch floor z 167–171, and the land is the notch rear wall.
- The bulkhead web is removed inside the box (wings at |y| ≥ 112 plus the strip above the lid remain). The rib and sternum box are deleted (they passed through cells).
- Box x −107 (rear web at the shell inner) … 108.5, z 121.6–278.
- The vent moved to the floor (−80, 80), outlet down into the pelvis open top.

**Coarse results (h 25), lid 1.5 / lid 3:**
- LC1a/b/c/u SF: bulkhead 0.13/0.08/0.16/0.12 (lid 3: 0.18/0.11/0.23/0.16), peak at the wing/lid corner (40, 112, 278). Waist 0.23/0.19/0.15/0.20, peak at the −y yoke cheek root. Pelvis 0.34/0.30/0.42/0.28.
- LC2: bulkhead 0.46, waist 0.13.
- Land deflection 50.7 mm at 29 kN, **k ≈ 0.57 MN/m** (needs ≥ 5.3). **Mode 1 40.7/38.7 Hz** (needs ≥ 80). Buckling 5.2 (pass).
- Verdict: **the model_v4 single-cheek waist bracket cannot carry LC1**. Only 21 shared nodes at the cheek/floor (coarse). This is a load-path design problem, not a mesh artefact.
- Minimum fixes for the next run (not done):
  - (a) a double-sided torso bracket (±y cheeks) / full ring flange on the pitch output;
  - (b) the box side walls carried down as the yoke;
  - (c) T&R to confirm the BC: a fixed pelvis for a chest fall.

**Mass (mesh):**
- Box + bulkhead **2.92 kg** (lid 3: 3.11). Waist stand-in 5.22 kg is the existing actuators/yoke, so it is excluded; the bracket cheek 0.13 kg is existing (model_v4 torso bracket).
- Against job 3's 1.99: +0.93 gross. Enclosure credit −0.738 (unchanged, still to be itemised with Electronics). Electronics P-057 +0.050.
- **Net +0.24 kg** (lid 3: +0.43). Supersedes +2.31.

**Clash:** the core plus socket now clears the pack (cells x ≤ 50.2, with 1.5 mm air + liner to the land at x 52). Residual flags:
- the bulkhead strip z 278–300 vs Thor (x −57…73) is unchecked;
- the box front web at 108.5 is beyond the shell inner at 107 (pre-existing).
Layout: pack/pack_layout_optA.{py,json,svg}, pack/pack_layout_optA_tables.md.

## 3c-final: two-sided yoke (Robot Lab decision 10:18), coarse h 25, 3 iterations
**Design:** the box side walls are carried down as cheeks at y ±(103…117), D 140 (x ±70), from z 19.6 to the floor (121.6).
- **+y side:** the waist-pitch actuator output flange plus an Al spacer Ø100/88 (40 mm).
- **−y side:** a **THK RB7013** crossed-roller ring (d 70, D 100, B 13; C 19.4 kN, C0 27.7 kN, 0.35 kg; THK catalog A18-24, tech.thk.com/en/products/pdfs/en_a18_024.pdf) on a stub from the waistY −y cheek, plus a 27 mm spacer.
- Bearing static check: P0 = Fr + 0.44 Fa = 14.5 + 0.44 × 9.9 = 18.9 kN (LC1c, half of 29 kN radial), fs = 1.47. At ultimate the radial load alone is 21.75 kN, fs = 1.27.
- The model_v4 single +y bracket cheek is deleted.

**Iterations:**
1. t 12: bulkhead SF 0.009 at the Thor-cut sliver corner (a geometry artefact; the strip cut is widened to |y| < 112.5).
2. t 20: yoke SF 2.07/3.05/2.33/1.80 (LC1a/b/c/u).
3. **t 14, final:** yoke SF **1.92/1.97/1.98/1.67**, LC2 4.07. The cheeks pass.

**Rest of the path (t 14):**
- Bulkhead wing/lid corner (49, 112.8, 278): **0.136/0.082/0.185/0.119**.
- waistY −y cheek root (model_v4 8 mm, (31, −57, 26)): **0.24/0.20/0.14/0.21**.
- Pelvis 4 mm shell at the deck: **0.34/0.31/0.41/0.28**.
- Land deflection 31.3 mm, **k 0.93 MN/m** (≥ 5.3 needed). Moving the cheeks from t 12 to t 20 changed deflection by < 0.1 mm, so the compliance is in the waistY yoke, the pelvis shell and the bulkhead/socket, not the cheeks.
- **Mode 1 41.6 Hz** (≥ 80 needed). Buckling 6.3 (pass).

**The fixed-pelvis BC is kept and is conservative:** in a chest fall the real reaction is whole-body inertia.

**Pitch torque:** the LC1 moment about the pitch axis is 29 kN × 0.150 m = 4.36 kN·m, against a 116 N·m motor. A yoke hard stop must carry it (open: T&R / Actuators).

**Clearances:**
- **Pitch −30/+60° (sim v3):**
  - The cheek corner radius is 86 mm, so its lowest point is z −16.4, 33.6 mm above the pelvis top (−50). The cheeks sit at |y| ≥ 103, clear of the waistY plate and cheek (|y| ≤ 70).
  - At +60° the box front-bottom corner reaches (x 98, z 3.4). That's outside the pelvis footprint (x ≤ 85) and clear of the yoke plate (|x| ≤ 60).
- **Yaw ±90°:** nothing static sits above z −50 within r 157 except the waist yaw housing (r 55). Pass.
- **Hip sweep:** the hips are below the pelvis deck (sim z ≤ −73); the torso parts stay ≥ 33 mm above the pelvis top. Pass.
- **Thor (model_v4, x −57…73, y ±100, z 273.6–313.6):**
  - The bulkhead strip at z 278–300 clashed. It is now removed for |y| < 112.5 (wings only).
  - **The lid top at 278 overlaps the Thor bottom by 4.4 mm.** Minimum change: raise the Thor bay 6 mm (tb + 170). Cover chamfer clearance goes from 24 to 18 mm; head/cover recheck open (ID).
  - The duct partition at x −10, z 278–300 sits inside the Thor footprint (pre-existing; Thermal/Electronics to check).
- **Front web:** moved from 108.5 to 106.5, 0.5 mm inside the 107 shell inner. The c1/c2 FET/busbar zone (x 52–104.5) is unaffected.

**Mass:**
- Box + bulkhead 2.73 kg (mesh); cheeks 1.08 kg (mesh); spacers 0.335 kg [CALC Ø100/88]; RB7013 0.35 kg.
- Credits: job 3 baseline −1.99; sim "waist ring 7075" −0.25 (replaced by the yoke); enclosure credit −0.738 (still to itemise).
- Electronics P-057: +0.05.
- **Net +1.56 kg.** The 3 mm lid adds about +0.19 (yaml updated, not re-run with the yoke).

**COM:** whole robot Δ ≈ (−0.2, 0, +6.3) mm [EST; robot COM z ≈ 1.0 m assumed]. That brings the cumulative total to ≈ 6.7 mm, under the 10 mm limit.

## 3c-final rev B (10:25 ruling: waist yaw/pitch + pelvis shell are Torso parts), 4 coarse iterations
**Model fix:** the FEA pelvis was a closed box. The model_v4 shell is open top and bottom, and the open shell is now modelled.

**Changes:**
- (a) Bulkhead/lid: the strip above the lid is removed. Added an internal corner gusset (x 52–64, |y| 100–112, z 250–276.5), a lid underside doubler in the c1/c2 zone (x 52–106.5, |y| 54.5–80, 4 mm), a land-top cap (x 52–64, |y| < 54.5, z 270.5–276.5), and an external wing gusset (x 52–72, |y| 115–122, z 240–278). Iteration 4 added a **lid-top doubler 3 mm, x 30–106.5, |y| < 70**. Socket walls are 8 mm and the notch floor is 8 mm (z 163–171).
- (b) waistY: yoke plate 8 → 16 mm. Both cheeks are 120 deep (x). The −y cheek is 8 mm; the +y side is a stator cradle (y 47–55) to z 69.6. Fore/aft closing webs, 6 mm, run to z 50, making a closed section.
- (c) Hard stop: P-160.
- (d) **Thor bay raised +9 mm** (6 for the lid plus 3 for the lid-top doubler). ID must recheck the chamfer clearance, now **15 mm** (was 24; 18 with +6 only). The duct partition moved to x −63, 6 mm behind Thor's rear face (Thermal to confirm the duct function).
- **Pelvis reinforcement (internal only; outer surface unchanged):**
  - Top lip ring 20 × 8 inside the walls.
  - Transverse ribs 8 mm at y ±(57…65), from the deck top to the pelvis top.
  - Annular rib r 55–66 around the waist-yaw seat.
  - Deck widened to touch the fore/aft walls (162).
  - Clearances: the hip-yaw housings and L39 bumpers are below the deck. The ribs and ring sit ≥ 7 mm outside a bolt-pattern keep-out (r 58 about (0, ±130), i.e. y ≥ 72). HP1/HP2 plates are outside the rear wall and untouched.
  - Hip range of motion acts below the deck, so the ≥ 3 mm clearance holds through the full range.

**Iterations (LC1a/b/c/u SF; LC1a deflection; mode 1):**

| it | bulkhead | pelvis | waistY+act | yoke | defl mm | Hz |
|---|---|---|---|---|---|---|
| 1 | 0.46/0.26/0.35/0.40 | 0.72/0.65/0.93/0.60 | 1.18/1.06/1.43/1.03 | 2.0/1.8/2.0/1.75 | 9.21 | 138 |
| 2 | 0.74/0.30/0.69/0.64 | 1.16/1.02/0.79/0.96 | ≥ 2.0 | ≥ 1.6 | 5.67 | 175 |
| 3 | 0.28/0.19/0.39/0.25 | 1.19/1.10/0.83/0.99 | ≥ 2.1 | ≥ 1.9 | 4.64 | 184 |
| 4 | **0.08/0.06/0.10/0.07** | **2.13/1.95/1.54/1.76** | **2.45/2.07/2.86/2.14** | **2.27/2.08/2.16/1.98** | **3.44 (k 8.4 MN/m; LC1b 3.95)** | **239** |

- Buckling 10.8 (pass). LC2: bulkhead 0.21, all others ≥ 2.1.
- **The bulkhead still fails.** In iteration 4 the peak moved to a lid sliver at (56, 95, 278): 1.5 mm lid between the doubler, cap and gusset edges, at h 25. The SF fell as the stiffening went up, which points to a mesh/sliver singularity. Needs a fine-mesh (h 6) check of the lid/socket corner before any redesign. **Not claimed as a pass.**

**Pelvis compliance:**
- Diagnostic with a rigid pelvis: LC1a deflection 3.44 → 2.22 mm, so the **pelvis shell is 35 % of the remaining land compliance** (52 % before the reinforcement, iteration 1).
- The fixed-pelvis BC is kept and is conservative.

**Mass (iteration 4):**
- Box + bulkhead 3.026 kg (mesh); yoke cheeks 1.165 (mesh); spacers 0.335; RB7013 0.35; waistY delta +0.657 [CALC]; pelvis reinforcement +0.804 (mesh 3.373 − open shell 2.569); hard stop +0.05; tap fuses/FPC +0.01; Electronics +0.05.
- Credits: −1.99 job 3, −0.25 waist ring, −0.738 enclosure.
- **Net +3.47 kg.** Mass critical. The obvious cuts are the lid-top doubler (if the fine mesh clears the sliver) and pocketing the pelvis lip/ring.

**COM:**
- Since the last tracker entry: about +0.30 kg near the lid (global ≈ 1550), +0.66 waistY (≈ 1300), +0.80 pelvis (≈ 1218). That's Δz ≈ **+8.4 mm** [EST, robot COM z ≈ 1.0 m assumed]. The cumulative total would be ≈ 15 mm, **> 10 mm**.
- **Controls flagged; NOT booked:** sim_torso_body_r1.json and model_v4 are unchanged for rev B.

**Electronics §18.7 items 1–4** (details in pack/pack_layout_optA.json):
1. **Tap fuses:** a fusible element at the cell end of each of the 22 taps, on the tap FPC/collector.
   - Candidate: Littelfuse 451/453 Nano2 0.5 A, 125 V class. Voltage rating to be verified on the datasheet.
   - Littelfuse 438 0603 is rejected: 63 VDC max is below an 84 V full-stack fault (438 datasheet rev 05/30/24).
2. **BMS board:** on the rear web, x −105…−95, on 3 mm G10 standoffs, with back-side parts ≤ 4.4 mm. The 22-way tap connector (vertical dual-row, e.g. Molex Micro-Fit 3.0 24-ckt [part EST]) and the isolation transformers face +x into the 35 mm gap to c7 (≤ 30 mm with mated plug and wire bend [EST]).
3. **SBS75X faces inward:**
   - Mounted on a G10 bracket off the rear web at (−100, −60, 160), mating face +x.
   - The robot-side half mates inside the box; the main cable exits through a side-wall gland at (−80, −112, 150).
   - 72 mm from the vent.
4. **Vent at y ≈ 0 (not blocked):**
   - Floor at (−90, 0), sim z 121.6 = **global 1401.6**.
   - A 0.5 mm stainless deflector on the floor underside turns the plume rearward, exiting at x −107, global z ≈ 1390. It's torso-mounted, so it moves with the torso through the pitch and yaw range.
   - 54 mm from the pitch housing surface. All hip-yaw drives, bumpers and harness are below global 1206.6, so the vent stays clear of them.

## 3c-final rev C (10:37): fine-mesh lid submodel + mass round
**(1) Fine submodel:** a local Ball refinement in the full model (h 1.0 within r 30 of (56, 95, 278), h 25 elsewhere; `--refine`, `mesh.refine`). 137k nodes, 4.7 min, LC1a/b only.
- Results: fea/job3c_lid_submodel_FINE_results.json.
- **SF did not converge** (0.081 coarse → 0.089 fine; the peak moved to the mirrored −y corner). It's a sharp step/edge singularity at the lid-to-doubler/gusset junction on a 1.5 mm lid, so **it did not clear**.
- I redesigned rather than keep the doubler: **lid 4.5 mm**, no top doubler, no sliver gusset; the under-lid c1/c2 doubler runs continuously to |y| 112. The lid top is at 281, so the **Thor bay stays at +9 mm (ID: chamfer 15 mm)**.

**(2) Mass round:**
- Pelvis lip 16 × 8 (was 20 × 8); ring r 55–61 (was 66); ribs 8.
- waistY webs 4 mm to z 40 (was 6 to z 50); yoke plate 12 (was 16).
- Cheeks t 11 × D 130 (was 14 × 140).
- Floor 6 (was 8); socket walls and notch floor 6; spacer tubes Ø100/92.
- Rib T-caps were tried in run 4 and made the pelvis worse (0.60), so they were removed.

| run | bulkhead LC1a/b/c/u | pelvis | waistY | yoke | defl a/b mm | Hz |
|---|---|---|---|---|---|---|
| m1 (cuts, no top doubler) | 0.29/0.17/0.39/0.25 | 1.07/0.95/0.74/0.89 | ≥ 1.14 | ≥ 1.50 | 5.68/6.70 | 167 |
| m2 (+top doubler) | 0.16/0.13/0.19/0.14 | 1.22/1.09/0.86/1.01 | ≥ 1.22 | ≥ 1.56 | 5.16/5.95 | 179 |
| m3 (lid 3, no doubler) | 0.81/0.48/0.77/0.70 | 1.22/1.08/0.87/1.01 | ≥ 1.15 | ≥ 1.54 | 5.20/6.01 | 176 |
| m4 (lid 4.5 + rib caps) | 1.01/0.60/0.86/0.88 | 0.85/0.76/0.60/0.70 | ≥ 1.12 | ≥ 1.58 | 5.01/5.72 | 178 |
| **m5 final (lid 4.5)** | **1.00/0.65/0.87/0.87** | **1.22/1.09/0.87/1.01** | **≥ 1.17** | **≥ 1.56** | **5.13/5.89** | **169** |

- **m5 FAILS:** bulkhead LC1b/c/u (peaks at the wing/lid corner (40, 113, 280) and the notch floor front corner (100, 52, 168)); pelvis LC1c 0.87 (rib top at the lip, (−35, 59, −53)); LC1b deflection 5.89 > 5.5 (k 4.9 MN/m offset; 5.65 MN/m centred). Mode 1 169 Hz and buckling 12.4 pass.
- **Mass (m5):**
  - Box + bulkhead 3.034 (mesh); cheeks 0.842 (mesh); spacers 0.225; RB7013 0.35; waistY +0.411; pelvis +0.637; stop / fuses / Electronics +0.11.
  - Credits −2.978.
  - **Net +2.63 kg, target ≤ 1.5 NOT met.**
  - The remaining big items are the 4.5 mm lid (~0.41) and the bay box itself. The next lever is architectural: the land load into the side walls should not go through the lid (for example, socket-to-side-wall diagonal struts in the c1/c2 zone).
- **COM:** Δz ≈ +4.6 mm since the booked state [EST, robot COM z ≈ 1.0 m] → cumulative ≈ 11.3 mm, **> 10 mm. Controls flagged; not booked** (sim_torso_body/model_v4 unchanged).

**(3) Tap fuse:** **Littelfuse 0451.500** (NANO2, 0.5 A, **125 VAC/VDC**, 50 A @125 VDC interrupting, 0.3046 Ω cold), from the Littelfuse 451/453 datasheet. Rated ≥ 84 V DC, so it passes. Its 2 × 0.30 Ω in the balance path gives ≈ 146 mV at 240 mA: include it in R_CB sizing, and measure with balancing paused.

## 3c rev D (10:49): chest load taken off the lid (step 4), coarse n1–n6
**Load path:** the land/socket goes straight down to the floor and cheeks; the lid is no longer in the path.
- Socket walls run from the floor (z 125.5) to the land top (270.5); they no longer touch the lid.
- A socket top cap (x 52–106.5, |y| < 54.5, z 270.5–274.5) is 2 mm below the lid. The front window is closed above 270.5.
- Two shelves (struts as shear plates) run from the socket walls to the side walls through the empty front zone: x 52–106.5, |y| 54.5–112, at z 165–171 and 262–268.
- Side-wall inner doublers, front zone (x 52–106.5, y ±(109–112), z 125.5–268). External wing doubler y ±(115–118), x 30–72, z 240–278.
- **Lid back to 1.5 mm** (z1 278), so the **Thor bay is +6 mm and the ID chamfer is 18 mm**. The lid-top doubler, under-lid shelf and land cap are deleted.
- **Pocketing:** floor 4 mm plus 4 mm strips under the cells/cheeks; pelvis ribs 6 mm plus fore-aft ribs at x ±55 (|y| ≤ 66, clear of the hip-yaw bolt keep-out).
- n4/n5 first attempts failed meshing (0.01 mm slivers / negative Jacobian) and were fixed by re-snapping the boxes.

| run | bulkhead LC1a/b/c/u | pelvis LC1a/b/c/u | defl a/b mm | Hz |
|---|---|---|---|---|
| n1 | 0.33/0.17/0.45/0.29 | 1.08/0.97/0.75/0.90 | 5.27/6.35 | 166 |
| n3 (walls stop below lid) | 0.87/0.33/0.78/0.76 | 1.20/1.06/0.93/0.99 | 5.70/7.91 | 185 |
| n4 (socket top cap) | 0.36/0.23/0.43/0.32 | 1.08/0.96/0.95/0.89 | 4.41/5.22 | 191 |
| **n6 final** | **2.01/1.04/2.09/1.75** | **1.08/0.95/0.95/0.89** | **4.36/5.21** | **190** |

- n6, other parts: waistY ≥ 1.17, yoke ≥ 1.90, LC2 bulkhead 1.30, buckling 12.6.
- **Only the pelvis fails** (5–11 % short), at the rib/fore-aft rib tops near the lip: (−61.5, 59.5, −52) and (53.5, −39, −53).
- Fix, not run (run budget used): ribs back to 8 mm. Rev B had ribs 8 and lip 20 × 8 with pelvis ≥ 1.54. Estimated +0.06 kg.
- **Stiffness:** 6.65 MN/m centred, 5.57 MN/m offset (5.21 mm ≤ 5.5). **PASS.**

**Clearances:**
- The struts/shelves sit at x ≥ 52: cells x ≤ 50.2 (1.8 mm incl. liner) ✓; BMS and SBS75X at x ≤ −60 ✓.
- **Two geometry nits for the next run:**
  - The 6 mm socket walls have their inner face at |y| 48.5 against the core half-width 49, a **0.5 mm interference**. Fix: land_web.y 56.5.
  - The notch floor top at z 171 touches the core bottom, 0 mm against 1.5 needed. Fix: notch floor top 169.5.
  - The pad stroke is along x inside |y| ≤ 49 and z 171–269, so the shelves, which are outboard of the socket walls, don't touch it.
- The FET/busbar zone is now between the shelves: x 52–104.5, |y| 54.5–109, z 171–262 (91 mm tall). Electronics to confirm.

**Mass (n6):**
- Box + bulkhead 2.953 kg (mesh); cheeks 0.842 (mesh); spacers 0.225; RB7013 0.35; waistY +0.411; pelvis +0.659 (mesh 3.228 − 2.569); stop / fuses / Electronics +0.11.
- Credits −2.978.
- **Net +2.57 kg. The ≤ 1.5 target is NOT reachable** in this architecture.
- Honest floor ≈ +2.2 kg: the two-sided yoke (cheeks + spacers + bearing ≈ 1.42), waistY +0.41 and pelvis reinforcement ≈ 0.6 are needed by the T&R loads with a fixed pelvis, and the box beyond job 3's 1.99 + 0.74 credit is ≈ 0.2–0.5.
- Getting to +1.5 would need a lower LC1 basis or a non-fixed-pelvis reaction (T&R).

**COM:** Δz ≈ +4.0 mm since the booked state [EST, robot COM z ≈ 1.0 m] → cumulative ≈ 10.7 mm, **> 10. Controls flagged; not booked.**
