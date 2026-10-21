# PC job 9 — T&R items (b) and (c): ready-to-run FEA spec (2026-10-21; rev 4 per R-123/R-125/R-127/R-128/R-132 allowables)
**Run on the bryan PC only. Never on the box and never on DESKTOP-B115PVV.** CalculiX (C3D10 or C3D20R) or the repo P2-tet solver (`legs/grokbuild/fea_r5.py` / `legs/fea_r8.py`, which reproduced GB). **Do not use the job 1 hex8 full-integration solver** (it locks in bending: −14 % at 2 elements through thickness, R2_VERIFY.md).
Supersedes items 2–7 of `legs/grokbuild/r031_fatigue_fea_brief.md` for T&R; item 1 (hip lever) is unchanged there.

## Common
- **Materials:** 7075-T6 (R-123 (a), MATERIALS_DB typical): **E 70 GPa**, ν 0.33, **Sy 480, Su 560**, **Se 87 MPa** (R-031, unchanged per R-123/R-125) (159 × 0.75 machined × 0.9 size × 0.814 R99). 7050-T73511 extrusion tubes (R-128; model_v4 'T7451' label corrected): Sy 435, Su 510, Se 87 [use the same value until cited]; static allowable 290 MPa multi-path; single-path 262 (S-basis 393/1.5, R-128). 6061-T6 (if the knee housing is 6061): Sy 276, A-basis Fty 241 (MMPDS, Materials to confirm), Su 310, Se = 96.5 × 0.55 = **53 MPa**. 42CrMo4 dowel: Sy 650. DP490 layer: E 2.5 GPa, ν 0.38, 0.1 mm.
- **Fatigue checks:** Goodman n = 1/(σa/Se + σm/Su) on the converged hot-spot von Mises (signed by max principal). Pulse load: σa = σm = σmax/2. Fully reversed: σm = 0.
- **Static allowable (R-123 (a), R-125 (b), R-127 (b), R-128):** every run states single- or multi-path, stock thickness and grain direction.
  - 7075 multi-path: **320 MPa** (480/1.5). 320 is multi-path only.
  - **7075-T651 single-path (R-128, MIL-HDBK-5H A-basis ÷ 1.5 by drawn stock thickness):**

| stock thickness (in) | LT (default; lower of L/LT) | ST (through-thickness load) | fall/fault min(A-basis, 480/1.1 = 436) LT / ST |
|---|---:|---:|---:|
| 0.25–0.499 | 308 | 271 | 436 / 406 |
| 0.5–1.0 | 313 | 271 | 436 / 406 |
| 1.001–2.0 | 308 | 271 | 436 / 406 |
| 2.001–2.5 | 294 | 271 | 436 / 406 |
| 2.501–3.0 | 280 | 257 | 420 / 385 |
| **unstated** | **257** | **257** | **385** |

  - Use LT unless the drawing fixes grain to L. For ≤ 2.0 in there is no ST value: a through-thickness-loaded part uses 271. Fall/fault values are my arithmetic from R-128 item 5 (band A-basis = limit × 1.5, capped at 436).
  - 7050-T73511 extrusion (femur/tibia tubes, R-128 item 3): single-path **262 MPa** (S-basis 393/1.5); fall/fault min(393, 435/1.1 = 395) = **393**. Multi-path 290.
  - 6061-T6: Fty 241 confirmed; single-path **161**, multi-path 184; fall/fault 241.
  - Peaks between the applicable single-path limit and the multi-path value are **held**, not passed.
  - **Single-path parts — band and grain (no drawing states stock thickness or grain yet, so 257 governs until the owner draws them):**

| part | run | likely stock (from repo geometry) | band if drawn so | grain | limit now |
|---|---|---|---|---|---|
| leg clevis (cheeks 46×14×62 + bridge 40×70×22) | b1 | one piece about 70 mm → 2.501–3.0 in [EST] | LT 280 (ST 257 if cheek load is through-thickness) | not stated | **257** |
| femur tongue (55 mm neck, 27 mm wide) | b4 | 27–55 mm → 1.001–2.5 in [EST] | LT 308 or 294; press-fit bore hoop load may be ST → 271 | not stated | **257** |
| foot collar (integral with the 18 mm foot plate) | b5 | 18 mm plate → 0.5–1.0 in [EST] | LT 313 (ST 271 if the flange load runs through the plate thickness) | not stated | **257** |
| knee twin-housing centre web | c | housing billet ≥ 85 mm frame → > 3.0 in [EST]; > 4.0 in not permitted in T651 (R-132) | T651 3.001–3.5 in L/LT/ST 276/267/248; 3.501–4.0 in 257/248/230. Sustained ST load (press/bolt) → **T7351 required**, 3.5–4.0 in S-basis 221/221/211 | not stated; sustained ST load assumed | **211 static / 317 fall** (T7351 ST interim, R-132); 6061 161 |
| femur/tibia tubes | b3 | 7050-T73511 extrusion (not 7075) | — | extrusion L | **262** |

  - Owners put stock thickness + grain on the drawing to release the band value: Legs for b1/b4/b5/b3, and **Legs for the knee web stock thickness and sustained ST load** (R-132 item 2).
- **SF definition:** SF_static = allowable / converged peak von Mises (must be ≥ 1.0). **Fall/fault cases: peak ≤ min(A-basis band, typical Sy/1.1)** (R-127 (b), recomputed per band by R-128 item 5; see the table above; 480 is withdrawn). E 70 GPa for every deflection, stiffness or buckling gate; 71.7 is acceptable only in a load-controlled linear stress-only run (R-123).
- **Pass:** **n_Goodman ≥ 1.5 (P-046, Se 87, Su 560)** and SF_static ≥ 1.0 against the allowable at design; fall/fault peak ≤ the min(A-basis, Sy/1.1) limit above.
- **Mesh convergence (mandatory):** three levels globally h = 3/2/1.5 mm, plus local refinement at every fillet/notch to **≤ R/4 (R6 → 1.5, 1.0, 0.5 mm; R8 → 2, 1, 0.5)**, ≥ 4 quadratic elements through every wall. Accept when the hot-spot peak changes < 5 % between the last two levels. Report the Richardson extrapolation and the observed order p. If the peak keeps growing (p < 0.5) the point is singular: report linearized membrane + bending through the section instead and flag it.
- **Outputs per run** → `modules/reliability/results/job9_<item>.json`: geometry hash, mesh table (h, local h, nodes, dofs, peak, p99.9, location xyz), Richardson value, σmax/σa/σm, Goodman n, SF_yield, max displacement, reaction balance (Σ reactions = applied, < 0.5 %), plus a stress plot PNG of the hot spot. A summary table goes into `JOB9_RESULTS.md`.

## (b) A15 structure round 2 with P-046…P-049 fixes
Source geometry: `legs/structure_r5.py`, `legs/fea_r8.py` (R-023 r8 cases), `legs/grokbuild/structure_fea_r2.md` items 1–5, with the fixes in `legs/R031_FIXES.md`. Loads: R-023 cases as already coded in `fea_r8.py` (3 BW walk/stairs pulse, fall 3 BW+screw, one-screw fault), at 66.5 kg.

| run | part / change | load cases | criterion |
|---|---|---|---|
| b1 | Clevis: cheek 14 → **17 mm**, re-entrant fillets **R8** (and the R-023 R6 baseline for comparison), 16 mm bridge pad | `clevis_h4_f6_pad16` cases: 3BW+screw (pulse), fall | Goodman ≥ 1.5; peak ≤ single-path band limit (257 until stock/grain drawn; 280 LT / 257 ST if 2.501–3.0 in) at design; fall peak ≤ 385 until drawn (420 LT if 2.501–3.0 in); locate the hot spot (cheek vs bridge edge) |
| b2 | Thigh clamp: arm 34 mm, root **28 mm** deep, R1.5 root lines (also try R3) | `clamp_h3_f34` cases, rev load as GB h1.5 | rev Goodman ≥ 1.5 (σm = 0); peak ≤ 320 at design (multi-path unless Legs flags otherwise) |
| b3 | Femur 7050-T73511 extrusion **1.6 mm** wall, tibia 1.6 mm, 0.5×100 mm sleeve, 15° taper ends, DP490 cohesive layer | R-023 dent/bending + fall | **single-path, 7050-T73511 extrusion:** peak ≤ 262 outside the sleeve (262–290 held); fall peak ≤ 393; adhesive peel < 10 MPa / shear < 7.7 MPa at the sleeve ends |
| b4 | Femur tongue 55 mm neck + **ø6 dowel** (P-048), 60 MPa interference (frictional contact μ 0.15) | press + design; press + fault | fault-only peak ≤ single-path band limit (257 until drawn) and ≤ 385 with press + fault (406 if drawn ≤ 2.5 in, ST); **bore opening** (contact gap) = 0 under fault; dowel shear SF ≥ 2 |
| b5 | Foot collar r30.2–45 × 3 with **R2 + 10° taper** at the OD (P-049), steel flange contact | R-023 foot toe case (heel too) | peak ≤ single-path band limit (257 until drawn; 313 LT if drawn 0.5–1.0 in) at design; fall peak ≤ 385 until drawn (436 LT); Goodman ≥ 1.5 at the walk pulse; report the contact slip amplitude (fretting) |
| b6 | Mass of each fixed part from the solid (vs R031_FIXES.md [EST]) | — | report Δkg vs booked |

## (c) Knee v4 twin housing centre web
- **Interim allowables (R-132 item 2):** **211 MPa static, 317 MPa fall/fault** (7075-T7351 ST, 3.5–4.0 in S-basis Fty 317 ÷ 1.5; fall = min(A/S-basis, Sy_typ/1.1) per band). Results above these are **held**, not passed. They replace the 257/385 interim values. Supporting data: Materials 5e33b17, MATERIALS_DB `AL7075T651_THICK` (MIL-HDBK-5H p. 3-346; T651 A-basis Fty 3.001–3.5 in L/LT/ST 414/400/372, 3.501–4.0 in 386/372/345; **no T651 band above 4.0 in**, so stock above 4.0 in is not permitted; **T651 ST SCC rating D**, so a web with sustained ST load must be T7351, p. 3-348). **The stock thickness (and the sustained ST load) must be stated on the drawing** (Legs); the final limit is then the band value for the drawn temper/thickness.
- **Geometry:** `actuators/cad/knee_twin_housing_finned_revc.step` (latest; rev B for reference). Shared 6 mm centre web with 3 mm flanges (D59), D69 ø85 frame, Ø12 trunnion bosses grown to Ø23 (D69 rev B note). Confirm the material from the STEP/BOM note: run 7075-T7351 (interim 211 static / 317 fall, above) **and** 6061-T6 (single-path limit 161).
- **Loads:** **3.6 kN per screw** axial (actuator max: 3634 N per pin, `actuators/results/DECISIONS.md` ~l.795), both screws in phase (D59). Cases: (c1) both screws 3.6 kN tension, (c2) both in compression, (c3) one screw 3.6 kN + the other 0 (fault/asymmetric), (c4) walk 1682 N per pin, treated as fully reversed (fatigue).
- **BCs:** trunnion pins = rigid pins in Ø12 bores (cosine-pressure bearing, not bonded), shank clevis side fixed; screw loads put through the nut/7202 bearing seat as a distributed axial load. The stator is bonded (include it as a stiffness or exclude it, and state which).
- **Criteria:** peak ≤ the static allowable at c1–c3 (single-path: 7075 **211** interim, 6061 161); fault case c3 peak ≤ **317** (7075) / 241 (6061); at c4 the fully reversed amplitude ≤ Se/1.5 (58 MPa for 7075, 35 MPa for 6061); 7202 bearing-seat ovality < 10 µm at c1; web buckling eigenvalue ≥ 3 at c2.

## Run order and estimate
b1, b2 first (they gate P-046 and the mass), then b4, c, b3, b5. About 3 levels × 6 runs; P2 tets at local 0.5 mm need about 4–8 GB RAM each.
**Ready:** yes for b1, b2, b4 and b5 (geometry is parametric in `fea_r8.py`, apply the R031 deltas). b3 needs the sleeve/adhesive layer added to the `fea_r8` tube model. c needs Actuators to confirm the rev C STEP is the release geometry and its material.
