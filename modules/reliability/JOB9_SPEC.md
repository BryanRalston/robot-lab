# PC job 9 — T&R items (b) and (c): ready-to-run FEA spec (2026-10-21)
**Run on the bryan PC only. Never on the box and never on DESKTOP-B115PVV.** CalculiX (C3D10 or C3D20R) or the repo P2-tet solver (`legs/grokbuild/fea_r5.py` / `legs/fea_r8.py`, which reproduced GB). **Do not use the job 1 hex8 full-integration solver** (it locks in bending: −14 % at 2 elements through thickness, R2_VERIFY.md).
Supersedes items 2–7 of `legs/grokbuild/r031_fatigue_fea_brief.md` for T&R; item 1 (hip lever) is unchanged there.

## Common
- **Materials:** 7075-T6 E 71.7 GPa, ν 0.33, Sy 503, Su 572, **Se 87 MPa** (159 × 0.75 machined × 0.9 size × 0.814 R99). 7050-T7451 tubes: Sy 435, Su 510, Se 87 [use the same value until cited]. 6061-T6 (if the knee housing is 6061): Sy 276, Su 310, Se = 96.5 × 0.55 = **53 MPa**. 42CrMo4 dowel: Sy 650. DP490 layer: E 2.5 GPa, ν 0.38, 0.1 mm.
- **Fatigue checks:** Goodman n = 1/(σa/Se + σm/Su) on the converged hot-spot von Mises (signed by max principal). Pulse load: σa = σm = σmax/2. Fully reversed: σm = 0.
- **Pass:** **n_Goodman ≥ 1.5 (P-046)** and SF_yield ≥ 1.5 at design; ≥ 1.0 at the fall/fault case.
- **Mesh convergence (mandatory):** three levels globally h = 3/2/1.5 mm, plus local refinement at every fillet/notch to **≤ R/4 (R6 → 1.5, 1.0, 0.5 mm; R8 → 2, 1, 0.5)**, ≥ 4 quadratic elements through every wall. Accept when the hot-spot peak changes < 5 % between the last two levels. Report the Richardson extrapolation and the observed order p. If the peak keeps growing (p < 0.5) the point is singular: report linearized membrane + bending through the section instead and flag it.
- **Outputs per run** → `modules/reliability/results/job9_<item>.json`: geometry hash, mesh table (h, local h, nodes, dofs, peak, p99.9, location xyz), Richardson value, σmax/σa/σm, Goodman n, SF_yield, max displacement, reaction balance (Σ reactions = applied, < 0.5 %), plus a stress plot PNG of the hot spot. A summary table goes into `JOB9_RESULTS.md`.

## (b) A15 structure round 2 with P-046…P-049 fixes
Source geometry: `legs/structure_r5.py`, `legs/fea_r8.py` (R-023 r8 cases), `legs/grokbuild/structure_fea_r2.md` items 1–5, with the fixes in `legs/R031_FIXES.md`. Loads: R-023 cases as already coded in `fea_r8.py` (3 BW walk/stairs pulse, fall 3 BW+screw, one-screw fault), at 66.5 kg.

| run | part / change | load cases | criterion |
|---|---|---|---|
| b1 | Clevis: cheek 14 → **17 mm**, re-entrant fillets **R8** (and the R-023 R6 baseline for comparison), 16 mm bridge pad | `clevis_h4_f6_pad16` cases: 3BW+screw (pulse), fall | Goodman ≥ 1.5, fall SF ≥ 1.0; locate the hot spot (cheek vs bridge edge) |
| b2 | Thigh clamp: arm 34 mm, root **28 mm** deep, R1.5 root lines (also try R3) | `clamp_h3_f34` cases, rev load as GB h1.5 | rev Goodman ≥ 1.5 (σm = 0) |
| b3 | Femur 7050 **1.6 mm** wall, tibia 1.6 mm, 0.5×100 mm sleeve, 15° taper ends, DP490 cohesive layer | R-023 dent/bending + fall | SF ≥ 1.5 outside the sleeve; adhesive peel < 10 MPa / shear < 7.7 MPa at the sleeve ends |
| b4 | Femur tongue 55 mm neck + **ø6 dowel** (P-048), 60 MPa interference (frictional contact μ 0.15) | press + design; press + fault | SF ≥ 1.5 fault-only; **bore opening** (contact gap) = 0 under fault; dowel shear SF ≥ 2 |
| b5 | Foot collar r30.2–45 × 3 with **R2 + 10° taper** at the OD (P-049), steel flange contact | R-023 foot toe case (heel too) | SF_yield ≥ 1.5; Goodman ≥ 1.5 at the walk pulse; report the contact slip amplitude (fretting) |
| b6 | Mass of each fixed part from the solid (vs R031_FIXES.md [EST]) | — | report Δkg vs booked |

## (c) Knee v4 twin housing centre web
- **Geometry:** `actuators/cad/knee_twin_housing_finned_revc.step` (latest; rev B for reference). Shared 6 mm centre web with 3 mm flanges (D59), D69 ø85 frame, Ø12 trunnion bosses grown to Ø23 (D69 rev B note). Confirm the material from the STEP/BOM note: run 7075-T6 **and** 6061-T6.
- **Loads:** **3.6 kN per screw** axial (actuator max: 3634 N per pin, `actuators/results/DECISIONS.md` ~l.795), both screws in phase (D59). Cases: (c1) both screws 3.6 kN tension, (c2) both in compression, (c3) one screw 3.6 kN + the other 0 (fault/asymmetric), (c4) walk 1682 N per pin, treated as fully reversed (fatigue).
- **BCs:** trunnion pins = rigid pins in Ø12 bores (cosine-pressure bearing, not bonded), shank clevis side fixed; screw loads put through the nut/7202 bearing seat as a distributed axial load. The stator is bonded (include it as a stiffness or exclude it, and state which).
- **Criteria:** SF_yield ≥ 1.5 at c1–c3; at c4 the fully reversed amplitude ≤ Se/1.5 (58 MPa for 7075, 35 MPa for 6061); 7202 bearing-seat ovality < 10 µm at c1; web buckling eigenvalue ≥ 3 at c2.

## Run order and estimate
b1, b2 first (they gate P-046 and the mass), then b4, c, b3, b5. About 3 levels × 6 runs; P2 tets at local 0.5 mm need about 4–8 GB RAM each.
**Ready:** yes for b1, b2, b4 and b5 (geometry is parametric in `fea_r8.py`, apply the R031 deltas). b3 needs the sleeve/adhesive layer added to the `fea_r8` tube model. c needs Actuators to confirm the rev C STEP is the release geometry and its material.
