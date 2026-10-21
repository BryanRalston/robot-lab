# Grok Build brief: 7075-T6 ankle cross, pocketed (R-069, Robot Lab confirmed). Run on the bryan PC after L47-SO, NOT the box
**Why not the box:** gmsh can't load (libGLU missing), and a converged 3D P2 study needs about 4 GB. Our box hand model is `legs/ankle_cross_pocket_est.py` (mass only, [EST]).

**Status: FINAL 2026-10-21** (Robot Lab job 7). Self-contained; no open TODOs. Unverifiable items marked [EST] or in Assumptions.

## Allowables (MATERIALS_DB `modules/materials/MATERIALS_DB.md`)
- **AL7075T6:** ρ 2.81, E 70 GPa (solve E 70, ν 0.33), Sy 480, Su 560. Fatigue per **R-031 §6: Se 87 MPa** (overrides DB 160). SCC-susceptible short-transverse (DB note): orient plate so pin loads are not short-transverse.
- **Design/fault/stop peak ≤ 320 MPa** (480/1.5). **Fatigue amplitude ≤ 58 MPa** (87/1.5).
- **Pin-bore bearing ≤ 1.5·Sy/2 = 360 MPa nominal (P/(d·t))** — rule stated: projected-area bearing, static. (Materials L63 gave 720 MPa bearing yield at e/D ≥ 2.0 for static fault; not adopted here, kept conservative.) Edge distance e/D ≥ 2.0 at every bore, else derate to 600 MPa × 0.5 = 300 MPa [EST].
- **TI64** (comparison/keep): ρ 4.4, Sy 910, fatigue 530.
- **STL42CRMO4** pins: Sy 990, fatigue 650.

## Assumptions (unresolved in repo)
- B1: stop-block positions (±21, ±38, −25) and the "stop carrier" are [EST]; L29 places 2 blocks 20×12×10 at r 45 mm. Use L29 (r 45) for load, the coordinates for geometry.
- B2: pin stubs are **pressed 42CrMo4 steel** (chosen: wear), bores hard-anodized + sealed, pins with MoS2/PTFE dry film.
- B3: A38 rev D and R-099…R-115 do not touch the ankle; no change taken from them. Proof rule is R-020 / BOND_SPEC §5.
- B4: ankle screw forces derived from `actuators/ankle_v4.py` / LINKAGE_TABLE; the run must cite the extracted values in the load table.

## Explicit load inputs (minimums; the run derives per pose and keeps the larger)
- Ankle pitch peak 209.3 N·m (walk_1p0), stairs_18cm peak per `legs/results/r4/requirements.md`; max GRF 1.31 BW at 65 kg.
- Screw max 8.76 kN each; **proof 13.1 kN** (1.5 × 8.76, both screws), plus one-screw fault (8.76 kN one side, 0 other) ×1.5.
- Roll stop: hold 3933 N per block at r 45 mm (177 N·m), `legs/results/r7/a14.json`; impact energy 5.9 J if unbraked — apply 3933 N static ×1.5 dynamic factor [EST] = 5.9 kN.

## Goal
Replace the Ti-6Al-4V ankle cross (booked 0.120 kg/leg, unverified; model_v4 l.198 solid box 30×46×30) with **pocketed 7075-T6**.
- Hand-model mass: W5/F5 **0.078 kg/leg** (−0.042/leg, **−0.084 robot**); W4/F4 0.067.
- Confirm by FEA, and report a measured CAD mass.

## Geometry inputs
- Envelope 30 (x) × 46 (y) × 30 (z), centred on the ankle axes (model_v4 `ankle cross`).
- **Pitch pin stubs:** ø12 × 18 along y at y ±24 pressed 42CrMo4 steel (B2).
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
   - Pass: amplitude ≤ 58 MPa; design/fault/stop ≤ 320 MPa; bearing ≤ 360 MPa (see Allowables).

## Method
- Solid P2 tets via gmsh, h 3 → 2 → 1 with refinement at the pocket corners and the bore edges. Peak change < 5 % over the last two levels.
- Pins as rigid cylinders with cosine bearing pressure (as hp_lever_fea_v2).
- Size study over W/F/boss. Pick the lightest that passes all cases.

## Surface treatment (spec, even though 7075 removes Materials' Ti-on-7075 galvanic/galling issue)
- **Bearing seats (pitch/roll pin bores and faces): hard anodize Type III, 25–50 µm**, sealed, with the bores honed after anodize to the fit.
- Steel pins (B2) carry a **MoS2/PTFE dry film**; justify against fretting at walking amplitude in the report. DU bush is the fallback if bore wall < 3 mm.
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

## Outputs (exact)
- `modules/legs/cad/ankle_cross_7075_pocketed.step`, `modules/legs/results/ankle_cross_fea/params.json`, `ANKLE_CROSS_FEA_REPORT.md`, `ankle_cross_results.json` (keys: mass_kg_per_leg, delta_vs_0.120, per-case peak/amp/bearing, convergence, clearances, pass), plots `*.png`, scripts `ankle_cross_*.py`. Commit as `Legs ankle-cross FEA ...`; write nowhere else.

## Compute budget
- bryan PC, ≤ 6 h wall, ≤ 6 GB RAM; size study ≤ 27 candidates (W,F ∈ {4,5,6} × boss {20,22,24}) at h 2, full h 3→2→1 only on the chosen one.

**Where:** the bryan PC (ff639f5a) via Grok Interface. **Never DESKTOP-B115PVV.**
