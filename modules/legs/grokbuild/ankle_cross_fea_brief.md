# Grok Build brief: 7075-T6 ankle cross, pocketed (R-069, Robot Lab confirmed). Run on the bryan PC after L47-SO, NOT the box
**Why not the box:** gmsh can't load (libGLU missing), and a converged 3D P2 study needs about 4 GB. Our box hand model is `legs/ankle_cross_pocket_est.py` (mass only, [EST]).

## Goal
Replace the Ti-6Al-4V ankle cross (booked 0.120 kg/leg, unverified; model_v4 l.198 solid box 30×46×30) with **pocketed 7075-T6**.
- Hand-model mass: W5/F5 **0.078 kg/leg** (−0.042/leg, **−0.084 robot**); W4/F4 0.067.
- Confirm by FEA, and report a measured CAD mass.

## Geometry inputs
- Envelope 30 (x) × 46 (y) × 30 (z), centred on the ankle axes (model_v4 `ankle cross`).
- **Pitch pin stubs:** ø12 × 18 along y at y ±24 (integral, or pressed steel). Specify which; steel is preferred for wear.
- **Roll pins:** ø12 from the foot lugs along x into cross bores, depth 12 each side.
- Stop blocks: 4× at (±21, ±38, −25), on the stop carrier [EST] beneath.
- **Start shape:** `ankle_cross_pocket_est.py` (4 blind pockets per ±z face, ribs/walls W, floor F, R2 pocket corners). Parameters: W, F ∈ {4, 5, 6}, plus boss OD around the bores ≥ ø20.

## Loads (derive, then cite each one)
1. **Walking/stairs:**
   - Ankle joint reaction from `legs/exports/walk_0p8_fsim_65kg.csv` and the r4 scenarios (max GRF 1.31 BW, stairs_18cm, `results/r4/requirements.md`), using mj_inverse reactions at the ankle, **plus the two ankle screw forces** (Actuators `ankle_v4.py` / LINKAGE_TABLE).
   - Resolve them into pitch-pin and roll-pin bearing loads per pose. Use the 10 worst poses.
2. **Fault/proof:** the R-020 proof rule as in BOND_SPEC §5. That is 1.5 × the max screw force with both screws at max, plus a **one-screw fault** case.
3. **Roll hard-stop impact:** the ±18° stop block load (L29/A14 stop stiffness) at the walking peak roll velocity.
4. **Fatigue:** walking cycle amplitude, R per pose pair.
   - Pass: amplitude ≤ Se/1.5 = 58 MPa (7075-T6 Se 87, R-031 §6).
   - Design/fault: peak ≤ 503/1.5 = 335 MPa.
   - Bearing at the pin bores ≤ 1.5 × Sy/2 [state the rule used].

## Method
- Solid P2 tets via gmsh, h 3 → 2 → 1 with refinement at the pocket corners and the bore edges. Peak change < 5 % over the last two levels.
- Pins as rigid cylinders with cosine bearing pressure (as hp_lever_fea_v2).
- Size study over W/F/boss. Pick the lightest that passes all cases.

## Surface treatment (spec, even though 7075 removes Materials' Ti-on-7075 galvanic/galling issue)
- **Bearing seats (pitch/roll pin bores and faces): hard anodize Type III, 25–50 µm**, sealed, with the bores honed after anodize to the fit.
- If the pins are steel: add a **MoS2/PTFE dry film** on the pin, or a pressed bronze/PTFE-lined bush (DU-type) in the 7075 bores. Pick one and justify it against fretting at walking amplitude.
- Pins must not run directly on bare 7075. Steel against 7075 needs isolation: anodize plus a sealant at press fits.
- Thrust faces against the fork cheeks: anodize plus PTFE washers.

## Outputs (`legs/results/ankle_cross_fea/`; STEP to `legs/cad/`)
1. `ankle_cross_7075_pocketed.step` plus params JSON, and the **measured mass** (density 2.81; steel pins separate).
2. Load table with sources.
3. Convergence plus case table (peak, amplitude, location), and plots of the governing cases.
4. Pass/fail and SFs. Clearances against the fork cheeks, stop blocks and roll lugs over pitch −45/+40 × roll ±18 (model_v4).

## Stop rules
- Lightest passing candidate found → stop.
- No 7075 candidate passes at W6/F6 → report the governing case and keep Ti (no saving).
- 6 h wall time. Never relax the limits or drop a case.

**Where:** the bryan PC (ff639f5a) via Grok Interface. **Never DESKTOP-B115PVV.**
