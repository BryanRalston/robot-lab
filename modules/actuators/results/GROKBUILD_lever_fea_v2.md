# Grok Build brief: hip_pitch lever FEA v2 (O13 redo) — READY FOR QUEUE

Scope: **G2 only.** Legs cf9eb63 (L34/L35) confirmed no through shaft. G3 has been dropped.

The box can't run this study. It has about 1.1 GB of free RAM, 2 cores and no swap, and other agents' desktops use the rest. At 64k P2 dofs (h 4 / local 2 mm) a run uses 865 MB RSS and takes 330 s. A 3-level local study down to 0.6 mm needs more than 300k dofs, which needs about 4 GB or more. Everything below is set up to run as-is with `modules/actuators/hp_lever_fea_v2.py`, which already has the pressure-loaded bore, the yoke-face support and gmsh Ball refinement.

## 0. What the box found (O13b, one run, h 4 / local 2, not converged)
- **Geometry B0 (O13: R2.8 fillet, bore clamped):** the peak is at the bore-lip end of the fillet. It sits where the arm root overlaps the bore end at |y| = 33.5. That is a real 90° re-entrant corner: the bore wall meets the underside of the arm. It is not only a clamp artefact.
- **Geometry B1 (cheek RO 28, fillet R3, bore pocket run 5 mm deeper with an R5 end torus, distributed bearing pressure):**
  - The peak is 583 MPa at (−13.4, 35.0, −16.5), sym φ+60. The fault cases are 581 and 575 MPa.
  - The relief undercut thins the arm root right at the hot spot. **Reject B1.**
  - Mass 0.2883 kg, vs O13's 0.2492 kg.
  - φ±90 rises to 542 MPa once the radial pin load reacts through the bore rather than a rigid clamp.
- **Conclusion:** the fix is topological. Either the arm root must not overlap the bore end, or the bore end must be closed with a filleted pocket. Sizing comes after that.

## 1. Geometry to build: variant G2 ("cap + flanks", all analytic)
Frame: y is the pivot axis, the lever radius is in xz, and ears are at (0, ±69, −50).

- **Cheek:** a cylinder r 21 → 27 over |y| 13.5 → 33.5, holding the TLA 3520 Z needle seat (ø42 H7, 20 wide).
- **End cap:** a disc r 0 → 27 over |y| 33.5 → 38.5 (5 mm), closing the bore.
  - The bore bottom corner (r 21, |y| 33.5) is **R0.6 max**. This replaces the R1.0 in the earlier draft.
    - The INA HK 3520 / IKO TLA 3520 Z cup has an edge radius r min of 0.8 mm (Schaeffler HK 3520 data sheet, via TME HK3520.pdf; nodeshk HK3520).
    - A housing corner radius larger than the cup's edge radius would let the cup's free end ride up on it. The housing corner radius must stay below the cup's r min.
    - Keeping R1.0 would need a 1 mm axial gap beyond the cup. That pushes the cap to |y| 39.5, which breaks the ±38.5 envelope.
    - Use a ≥ 0.4 mm-deep undercut only if the FEA asks for more radius.
    - Housing bore ø42 N7 (41.967…41.992).
- **Arms:** a planar slab in the yz plane, extruded in x to b = 25.
  - Profile: a straight-sided band about the line (y 33.5, z −24) → (54, −48), width d0 = 30 at the root and d1 = 16 at the ear.
  - A tangent arc R8 joins the slab to the cap face |y| = 38.5. Both concave corners use exact 2D arcs, so the fillet is a cylinder surface along x with no B-spline.
  - The x-edges get an R3 round (convex).
- **Junction to the cheek cylinder:** R5 on the arm-flank/cylinder intersection edges, with r 27 − 21 = 6 mm wall under them. If OCC refuses, add the R5 as a 2D arc in a revolved profile.
- **Mass target:** ≤ 0.270 kg per lever including pins, about +21 g vs O13. Report the actual figure.

## 1b. Fixed constraints (Legs L34/L35)
- **Shaft:** ø35 h6 outside / ø30 inside, hollow. It is press-fitted in the femur tongue, which is 27 mm wide (|y| < 13.5).
  - Length ≤ 66 mm. The cup seats span |y| 13.5…33.5 and the cap's inner face is at 33.5, so the shaft ends must clear the cap by ≥ 0.5 mm on each side.
- **Needles:** the TLA 3520 Z / HK 3520 cups sit in the cheeks at |y| 13.5…33.5, run directly on the shaft, and are pressed into the lever.
- **Service:** remove the lever first. The cap means the shaft can't be pushed out with the lever fitted.
- **Envelope:** ±38.5 mm is accepted.

| Item | Clearance (mm) |
|---|---|
| Cap to tongue | 20 |
| Cap to collar / femur | 25 |
| Cap to bumper | 53 |

- **Arms:** they reach about r 61 at the ears. Over the whole ROM (−120…+40°), each arm's centreline must stay ≥ 30° off the femur axis. Below 30° the gap to the thigh clamp collar drops to about 1.5 mm.

## 2. Loads and supports (already in hp_lever_fea_v2.py)
- **Pin loads:** F = 4542 N per pin (454.2 N·m / 0.05 / 2). Applied as a uniform traction on the pin-stub end face, |y| > 62.5, r_pin > 5.7.
  - Directions φ = −90…+90 in 30° steps.
  - Cases: sym (both pins), fault R (pin +y only) and fault L (pin −y only). That is 21 cases from 4 unit solves.
- **Bearing reaction:** cosine pressure p(θ) = p0·max(cos(θ − θR), 0) on each bore, r 21, |y| 13.5…33.5. It is equal and opposite to the net pin force, split half per cheek. **No clamp on the bore.**
- **Yoke:** the cheek inner face |y| = 13.5 is fixed and reacts the pitch torque. Elements within 2.5 mm of it are excluded from the check. Stress there is checked separately as bolt-face bearing.
- **Material:** 7075-T6, E 71.7 GPa, ν 0.33, Sy 503 MPa, Su 572 MPa. Fatigue allowable is 127 MPa (159 × 0.8 at 5e8, R = −1).

## 3. Mesh plan
- P2 tets throughout. Global h = 4 mm.
- gmsh Ball fields, radius 7 mm and thickness 8 mm, at every hot spot: the 4 junction points (±11, ±34, −17), the 2 cap-arc roots, and the 2 ear roots (0, ±50, −50).
- Local h at 2.0, 1.4, 1.0 and 0.7 mm, plus 0.5 mm if the 0.7 → 1.0 change is still above 5%.
- Solver: pyamg SA-CG to tol 1e-9 (relative residual below 1e-6 asserted). If RSS exceeds 70% of RAM, switch to MUMPS or PARDISO.
- **Optional submodel** (same result, about 5× cheaper): cut a 30 × 20 × 25 mm block around each hot spot. Drive it with the P2 displacement field of the h 4 / local 2 global run on the cut faces, then refine it to 0.4 mm.

## 4. Stress measures and convergence
For each case, report:
- (a) element max of nodal-averaged von Mises in the Ball regions
- (b) stress at 0.5 mm depth, on the inward normal from the hot-spot surface point
- (c) membrane + bending linearisation along a through-thickness line at the arm root (ASME VIII-2 5.A style)

Convergence passes when (a) or (b) changes by less than 5% over the last two refinements and the Richardson p is between 0.5 and 4. If (a) keeps rising while (b) and (c) converge, the point is a singularity: it must be geometric, and you report that and do not quote (a). Table columns: hloc, ndof, (a), (b), (c), Richardson vm0, p.

## 5. Pass criteria
1. **Yield:** converged peak ≤ 335 MPa, which is SF ≥ 1.5 on yield, for all 21 cases, both fault sides included.
2. **Fatigue:** stress amplitude at the hot spot at the duty load ≤ 127 MPa. Take the duty load as 0.5 × the peak pin load with R ≈ 0, so σa = 0.25 × peak. Use Goodman with σm = σa: σa/127 + σm/572 ≤ 1 / 1.5.
3. **Stiffness:** pin deflection ≤ 0.20 mm at the design load (O13 was 0.16 mm).
4. **Envelope:** no lever material at |y| > 38.5 inside r < 34 except the arms. The arms must stay ≥ 30° off the femur axis (L35) and stay ≥ 1 mm off the rod-end eye (ø22) and the RV12 rod sweep (|y| 63…75) over −120…+40°. The rods at |y| ≥ 63 keep 63 − 38.5 = 24.5 mm off the cap.
   - D25's "41 mm" assumed the R3b CRBH hub (|y| ≤ 22). The needle cheeks already went to |y| 33.5 in R4, so the current figure is 29.5 mm. G2 makes it 24.5 mm, which is still above the 10 mm minimum. **Legs must accept the cap at |y| ≤ 38.5.**
5. **Mass:** report kg per lever and the delta ×2 vs the official rollup line (hip_pitch lever 0.2492 kg/each in `actuator_deltas.json` / `hp_lever_fea_r4.json`).

## 6. Deliverables
- `cad/hip_pitch_lever_B_v2.step`
- `results/hp_lever_v2_<hloc>.json` for each level
- `results/hp_lever_v2_convergence.{json,png}`
- A von Mises plot of the governing case at the finest level
- **Clearance check** (script and JSON):
  - Arm/ear solid vs the femur clamp collar, the bumper and the tongue over −120…+40°.
  - Report the minimum angle between the arm and the femur axis (≥ 30°) and the minimum gap (≥ 1 mm).
  - Report the cap-to-shaft-end gap (≥ 0.5 mm per side).
- Proof-test strain-gauge locations, updated to the converged hot spot
- **If G2 fails:** increase d0 in 2 mm steps (about 4 g/mm) up to 36. If it still fails, increase b to 28.


## AMENDMENT 1 (2026-10-14, RL Actuators): T&R 8daecff fatigue finding, which this brief did NOT cover
The fatigue criterion above (allowable 127 MPa, duty = 0.5 × peak at R ≈ 0) is **superseded**. It is unconservative on three counts:
- Se: 127 → **87 MPa** (T&R: 159 × 0.75 machined × 0.9 size × 0.814 at 99 % reliability; R-031 §6).
- Load: walk 1.2 m/s hip_pitch peak is 203 N·m, which is 0.447 × the 454.2 N·m design peak (`legs/results/walk_1p2.json`).
- Ratio: the walk load is **fully reversed (R = −1)**, not R ≈ 0.

**New pass criterion 2:** hot-spot von Mises amplitude at 0.447 × the design pin load (2030 N per pin) ≤ **Se/1.5 = 58 MPa**. That is about a ≤ 130 MPa peak at the design load. Report it at the converged level.
- The G2 geometry as briefed (target SF_yield 1.5, peak about 335 MPa) would give about 150 MPa amplitude, so **it will fail this criterion**.
- Per R-031 §6, **Legs owns the fix (P-046..P-050)**: a bigger 7075 section first, and steel only if 7075 grows by more than +0.25 kg.
- The "If G2 fails" growth steps (d0 to 36, b to 28) are unlikely to close a 2.6× gap. Legs should provide the section family to sweep.
- Optional: a finite-life case with a cited S-N curve and shot-peen.
