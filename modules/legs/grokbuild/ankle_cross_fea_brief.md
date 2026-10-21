# Grok Build brief: 7075-T7351 ankle cross, pocketed (R-069, Robot Lab confirmed). Run on the bryan PC after L47-SO, NOT the box
**Why not the box:** gmsh can't load (libGLU missing), and a converged 3D P2 study needs about 4 GB. Our box hand model is `legs/ankle_cross_pocket_est.py` (mass only, [EST]).

**Status: FINAL rev C 2026-10-21** (Robot Lab job 7). Rev C applies Materials e98d18d / R-125(b) (`modules/materials/ANKLE_CROSS_7075.md`, R-123 update + R-125(b) VERIFIED): verified A-basis limits, plate stock ≤ 1.500 in, ST check at 239 MPa, grain orientation, bearing 295. Rev B applied Materials a2bf811 `modules/materials/ANKLE_CROSS_7075.md` (§1–§4) and P-151 hollow pins (Materials, `modules/PROPOSALS.md`). Self-contained; no open TODOs. Unverifiable items marked [EST] or in Assumptions.

## Allowables (Materials a2bf811 `ANKLE_CROSS_7075.md` §1–§2; MATERIALS_DB)
- **Material: 7075-T7351 plate ONLY.** T6/T651 is not allowed: SCC risk in short-transverse under sustained press-fit hoop stress at the bores (§1). If the lightest W/F passes only at T6 values, re-size; never drop to T6.
- **AL7075T7351:** ρ 2.81, E 70 GPa (ν 0.33). Fty A-basis L/LT **393 MPa** (57 ksi), MIL-HDBK-5H p. 3-348, T7351 plate, stock 1.001–1.500 in (verified, Materials e98d18d / R-125(b), `ANKLE_CROSS_7075.md` R-123 update). Single load path → A-basis governs. (Superseded: 410 MIF typical, 273/308.)
- **Stock: 7075-T7351 plate ≤ 1.500 in (38.1 mm) thick as heat-treated** (band set by stock at heat treat, not finished part). Envelope check: cross is 30 (x) × 46 (y) × 30 (z); with plate thickness along z the 30 mm fits in 38.1 mm stock (≥ 8 mm machining allowance; 46 mm and 30 mm x lie in the plate plane). Order 1.25 in (31.75 mm) or 1.5 in plate [stock size choice EST]. Thicker stock (1.501–2.000 in) is NOT allowed: limit would drop to 253 MPa L/LT, 239 MPa ST.
- **Grain orientation (mandatory on drawing):** plate thickness (ST) = cross z; L along y (pitch pin axis), LT along x (roll pin axis). Pin axes therefore lie in L/LT; pin-bore hoop/press-fit stress acts in the L–ST and LT–ST planes, so ST stress is NOT excluded.
- **Design/fault/stop peak ≤ 262 MPa** (393/1.5) on L/LT von Mises.
- **ST check ≤ 239 MPa:** the run extracts the σ_zz (ST) normal stress component at every case and reports it against 239 MPa (Materials' 1.501–2.000 in ST A-basis 52 ksi /1.5; applied conservatively here because `ANKLE_CROSS_7075.md` gives no ST value for the 1.001–1.500 in band — gap flagged to Materials). Sustained press-fit hoop tension in ST also reported (SCC, §1).
- **Pin-bore bearing ≤ 295 MPa** nominal P/(d·t) on the bush OD bore (1.5 × 393/2, re-derived on the same basis per `ANKLE_CROSS_7075.md` R-123 update; replaces 308). Edge distance e/D ≥ 2.0 at every bore.
- **Fatigue amplitude ≤ 58 MPa** on un-anodized machined surfaces (R-031 §6 Se 87 / 1.5). Not recomputed: Materials §1 gives the same 160 MPa MIF fatigue for T73 and T6 and instructs keeping Se 87 / 58 MPa. [EST]: Se 87 was set on the T6 basis and no T7351-specific endurance data is in the repo; the run reports the amplitude SF vs 58 and flags any location < 1.2 SF for Materials. FEA peak includes Kt; compare to Se, not Se/Kf (§2).
- Any anodized-corner amplitude limit would be ≈ 35 MPa [EST] (§2); not applicable because hard anodize is banned there (see Surface treatment).
- **TI64** (comparison/keep): ρ 4.4, Sy 910, fatigue 530.
- **STL42CRMO4** pins Q&T (or 17-4PH H1025, §3): Sy 990, fatigue 650.

## Assumptions (unresolved in repo)
- B1: stop-block positions (±21, ±38, −25) and the "stop carrier" are [EST]; L29 places 2 blocks 20×12×10 at r 45 mm. Use L29 (r 45) for load, the coordinates for geometry.
- B2: pitch stubs are **pressed steel** (42CrMo4 Q&T or 17-4PH H1025), mandatory per §3 (integral 7075 stubs not acceptable). All four ø12 bores carry pressed PTFE-lined DU bushes; no hard anodize in bores.
- B5 (P-151 hollow pins, adopted): all 4 pins/leg (2 pitch stubs, 2 roll pins) are gun-drilled ø12/ø6 tubes, OD unchanged. −24 g/leg, −0.048 kg robot [EST, Materials]. Conditions: (a) the run checks pin bending/shear on the hollow section (Z −6 %, stress +6.7 %) against 42CrMo4 Sy 990 / fatigue 650 at all cases; (b) pitch-stub press-fit interference re-derived for the hollow section (lower radial stiffness → lower contact pressure; report pull-out margin vs one-screw fault axial load); (c) bore ends plugged against debris. No conflict found: interfaces and OD unchanged; P-054 (Ti pins) is not taken.
- B3: A38 rev D and R-099…R-115 do not touch the ankle; no change taken from them. Proof rule is R-020 / BOND_SPEC §5.
- B4: ankle screw forces derived from `actuators/ankle_v4.py` / LINKAGE_TABLE; the run must cite the extracted values in the load table.

## Explicit load inputs (minimums; the run derives per pose and keeps the larger)
- Ankle pitch peak 209.3 N·m (walk_1p0), stairs_18cm peak per `legs/results/r4/requirements.md`; max GRF 1.31 BW at 65 kg.
- Screw max 8.76 kN each; **proof 13.1 kN** (1.5 × 8.76, both screws), plus one-screw fault (8.76 kN one side, 0 other) ×1.5.
- Roll stop: hold 3933 N per block at r 45 mm (177 N·m), `legs/results/r7/a14.json`; impact energy 5.9 J if unbraked — apply 3933 N static ×1.5 dynamic factor [EST] = 5.9 kN.

## Goal
Replace the Ti-6Al-4V ankle cross (booked 0.120 kg/leg, unverified; model_v4 l.198 solid box 30×46×30) with **pocketed 7075-T7351**.
- Hand-model mass: W5/F5 **0.078 kg/leg** (−0.042/leg, **−0.084 robot**); W4/F4 0.067 [both T6-era hand model].
- DU bushes add ≈ +4 g/leg [EST, §3] and must be in the FEA mass. Expected net ≈ −0.076 kg robot [EST, §4], less if T7351 forces W5/F5 → W6/F6. P-151 pins −0.048 robot [EST] reported separately.
- Confirm by FEA, and report a measured CAD mass.

## Geometry inputs
- Envelope 30 (x) × 46 (y) × 30 (z), centred on the ankle axes (model_v4 `ankle cross`).
- **Pitch pin stubs:** ø12 × 18 (+12 press) along y at y ±24, pressed steel, hollow ø6 bore (B2, B5).
- **Roll pins:** ø12 (hollow ø6, B5) from the foot lugs along x into cross bores, depth 12 each side.
- **Bores:** all four ø12 pin bores take a pressed DU bush (~1 mm wall) → cross bore ø14; bores bare-machined, wet-installed sealant (MIL-PRF-81733 polysulfide, or Loctite 638 if retention fit) [§3].
- Stop blocks: 4× at (±21, ±38, −25), on the stop carrier [EST] beneath.
- **Start shape:** `ankle_cross_pocket_est.py` (4 blind pockets per ±z face, ribs/walls W, floor F, R2 pocket corners). Parameters: W, F ∈ {4, 5, 6}, plus boss OD around the bores **≥ ø22** (bush OD ø14).

## Loads (derive, then cite each one)
1. **Walking/stairs:**
   - Ankle joint reaction from `legs/exports/walk_0p8_fsim_65kg.csv` and the r4 scenarios (max GRF 1.31 BW, stairs_18cm, `results/r4/requirements.md`), using mj_inverse reactions at the ankle, **plus the two ankle screw forces** (Actuators `ankle_v4.py` / LINKAGE_TABLE).
   - Resolve them into pitch-pin and roll-pin bearing loads per pose. Use the 10 worst poses.
2. **Fault/proof:** the R-020 proof rule as in BOND_SPEC §5. That is 1.5 × the max screw force with both screws at max, plus a **one-screw fault** case.
3. **Roll hard-stop impact:** the ±18° stop block load (L29/A14 stop stiffness) at the walking peak roll velocity.
4. **Fatigue:** walking cycle amplitude, R per pose pair.
   - Pass: amplitude ≤ 58 MPa; design/fault/stop ≤ 262 MPa (L/LT), σ_ST ≤ 239 MPa; bearing ≤ 295 MPa (see Allowables); hollow pins pass B5(a)/(b).

## Method
- Solid P2 tets via gmsh, h 3 → 2 → 1 with refinement at the pocket corners and the bore edges. Peak change < 5 % over the last two levels.
- Pins as rigid cylinders with cosine bearing pressure (as hp_lever_fea_v2).
- Size study over W/F/boss. Pick the lightest that passes all cases.

## Surface treatment and bearings (Materials §2–§3)
- **No hard anodize (Type III) on fatigue-critical surfaces:** pocket corners, rib roots, nor in the bores. General surface: Type II sulfuric 5–10 µm or TSA, corrosion only.
- **Bores:** PTFE-lined DU-type bushes (PTFE/bronze on steel back, e.g. GGB DU) pressed into all four ø12 bores, sealant as above. Pins run on the PTFE layer, never on bare 7075.
- **Pitch stubs:** pressed steel; integral 7075 stubs not acceptable.
- Thrust faces against the fork cheeks: Type II anodize plus PTFE washers.

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
- bryan PC, ≤ 6 h wall, ≤ 6 GB RAM; size study ≤ 27 candidates (W,F ∈ {4,5,6} × boss {22,24,26}) at h 2, full h 3→2→1 only on the chosen one.

**Where:** the bryan PC (ff639f5a) via Grok Interface. **Never DESKTOP-B115PVV.**
