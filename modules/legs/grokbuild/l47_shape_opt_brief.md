# Grok Build brief L47-SO: hip_pitch lever shape optimisation (R-069 mass-down). Run on the bryan PC, NOT the box
**Status: FINAL 2026-10-21** (Robot Lab job 5). Self-contained; no open TODOs. Items not verifiable from the repo are marked [EST] or listed under §0 Assumptions.

## 0. Allowables (cite MATERIALS_DB) and assumptions
- **Material source:** `modules/materials/MATERIALS_DB.md` row AL7075T6: ρ 2.81, E 70 GPa, Sy 480, Su 560, fatigue 160 (MIF, cycle basis not stated). R-031 §6 overrides fatigue: **Se = 87 MPa** (corrected value, rule).
- G3 brief (Actuators) uses E 71.7 / Sy 503 / Su 572 (repo datasheet REPO_AL7075). To stay comparable with G3, **solve with E 71.7, ν 0.33**; E difference <3 %, no effect on stress in a load-controlled linear solve.
- **Design/fault pass = von Mises ≤ 320 MPa** (MATERIALS_DB Sy 480 / 1.5, the more conservative value). Also report SF vs 335 (503/1.5, G3 rule). A peak in 320–335 is reported as a flag to the Arbiter, not as a pass.
- **Fatigue pass = hot-spot amplitude ≤ 58 MPa** (87/1.5, R-031 §6). Unchanged.
- Assumption A1: G3 converged mesh settings are taken from Actuators' G3 report when it lands; if G3 reports none, use the G3 brief sequence (global h 4→3→2, local 1.5→1.0→0.6 mm).
- Assumption A2: A38 rev D (tine bore 22, flange clearance 2.0 mm) and R-1xx rulings through R-115 do not touch the lever's frozen regions or load path; femur clearance check uses model_v4 as of main 2026-10-21.
- Booking: L47-R/R-069 +0.430 kg robot stands until this result is measured; credit only on measured CAD + passing converged FEA (R-073).

**Owner:** RL Legs (spec). The part belongs to RL Actuators (release CAD).
**Prerequisite (hard gate):** run this only **after Actuators' G3** (`modules/actuators/results/GROKBUILD_lever_fea_r031.md`) has finished and **G3 passes**:
- design peak ≤ 335 MPa, and
- fatigue amplitude ≤ 58 MPa at the converged level.

**If G3 fails, do NOT run this brief.** G3's own fallback path (b35/d40, then 17-4PH) takes over. Report back.
**Baseline:** the G3 converged result, i.e. mesh settings, peak/amplitude, hot-spot locations and the measured mass of the RC STEP. Re-use G3's mesh/solve setup (`hp_lever_fea_v2.py` functions with STEP import) unchanged, so both results are comparable.

## 1. Inputs
- **Geometry:** `modules/actuators/cad/hip_pitch_lever_r031_mw_b30_d36_RC.step` (2 solids, 155,055 mm³).
- **Mass rule:** (V − 2·π·6²·25) × 2.81e-6 + 0.0444 steel pins = **0.4642 kg per lever**.
- **Booking:** the booked delta is +0.430 kg robot vs sf15 0.2492 (Legs L47-R, Arbiter R-056).
- **Material:** 7075-T6 per §0 (solve E 71.7 GPa, ν 0.33; ρ 2.81; Se 87 per R-031 §6).
- **Loads:** same cases as G3.
  - Design: 4542 N per pin (454.2 N·m / 0.050 / 2), pass ≤ 320 MPa von Mises (§0; report vs 335 too).
  - Fatigue: 2030 N per pin, fully reversed (R = −1), pass **hot-spot amplitude ≤ 58 MPa** (87/1.5).
  - Also the single-pin fault cases (`fault_phi*`, `faultL_phi*` in `hp_lever_fea_v2.cases`). Pass ≤ 320 (§0).
- **Supports:** as G3/v2. Cosine bearing pressure in the ø42 needle bores (|y| 13.5–33.5), yoke face |y| = 13.5 fixed.

## 2. Frozen regions (no material removed or added)
- **Needle bores:** ø42 bores, the bore relief torus, the cheek ring r ≤ 30 between |y| 13.5 and 33.5 (needle seats TLA3520), and the yoke bolt faces.
- **Ears and pins:** ears ø26 × 12 and the ø12 × 25 pin stubs at (x 0, |y| 50–75, z −50). **Rod eye interface unchanged** (GE12 C eye position, washer faces).
- **Arm axis:** unchanged. Arm-to-femur angle ≥ 30° holds automatically (58°/78° today).

## 3. Clearance constraints (re-check every candidate)
- **RV12 rod sweep:** ≥ 1.0 mm over screw angle −110…+45° (Actuators `lever_r031.py` check 3). Today 1.94 mm.
- **Femur tube:** ≥ 10 mm over hip_pitch −107.3…+40° in model_v4 with the candidate swapped in. Use Legs `lever_l35_model.py`, TAG/STEP swap; today 11.0 mm at +40°.
- **Envelope:** no growth anywhere. Candidate must be a subset of the RC body: bounding |y|, r and the r ≤ 34 envelope (57.7) must not grow.
- **Manufacturability (3-axis + 4th):**
  - pocket floors ≥ 2.5 mm, ribs ≥ 3 mm;
  - internal fillets ≥ R3 (≥ R8 at the web/arm junction and at the bore-lip blends, as in RC);
  - no enclosed voids.

## 4. Method
1. **Topology screen (optional, ≤ 1 h):**
   - Run SIMP on the design domain = RC minus frozen regions. Use the fatigue case plus the design and fault cases, with compliance + stress constraints.
   - Volume fractions 0.70 / 0.60.
   - Only to find where material is idle. Do not export the density field as CAD.
2. **Parametric CAD (main loop, CadQuery):**
   - Re-interpret the screen as features on the RC body:
     - (a) web pockets through/blind between the arms, floor ≥ 2.5;
     - (b) arm taper: d1 at the ear 19 → 15, and b at the ear 25.5 → 22;
     - (c) cheek outer-ring lightening (r 30 → 27 outside the needle seat, only where the screen shows it idle);
     - (d) arm slab hollowing / I-section (flange ≥ 3, web ≥ 3).
   - Keep R8 at every web/arm junction.
3. **Size optimisation:**
   - 6–10 parameters, Latin hypercube 20–30 candidates.
   - For each: rebuild, check validity, measure mass, check clearances (§3), then FEA at **G3's converged mesh level** with refinement balls at G3's hot spots plus any new pocket corners.
   - Then local refine (Nelder–Mead or a surrogate) on the best 3.
4. **Final:** converged FEA on the chosen candidate (h sequence as G3, peak change < 5 % over the last two levels).

## 5. Targets and stop rules
- **Target:** save **0.13–0.17 kg robot**, i.e. 0.065–0.085 kg per lever, which is 0.379–0.399 kg per lever.
- **Pass:**
  - fatigue amplitude ≤ 58 MPa;
  - design and fault ≤ 320 MPa at the converged level (§0);
  - all §3 clearances met;
  - valid solid.
- **Stop when any of these holds:**
  - (1) A candidate passes with ≥ 0.17 kg robot saved. Stop and report.
  - (2) 2 full size-opt rounds done and the best passing saving is < 0.13 kg robot. Stop and report the best passing (even if < target) plus the governing constraint.
  - (3) 8 h wall time on the bryan PC.
  - (4) No candidate passes fatigue. Stop and report RC as final, saving 0.
- **Never** hand-tune stresses, drop a case, or relax 58 MPa / 10 mm / 1 mm. If a peak is a singularity (no convergence at a sharp re-entrant corner), report it and its location; don't average it away.

## 6. Outputs (to `modules/legs/results/l47_so/`; STEP to `modules/legs/cad/`)
1. `hip_pitch_lever_r031_so.step`, the optimised body: 2 valid solids, with feature parameters in a JSON.
2. **Measured mass** by the same rule, plus the delta vs RC 0.4642 and vs booked sf15 0.2492, per lever and robot.
3. FEA report:
   - per case and level: peak and amplitude, location, convergence table;
   - plots of the governing case;
   - comparison against the G3 baseline at the same hot spots.
4. Clearance table: rod sweep min, femur min (and angle), envelope bounds vs RC.
5. The candidate table (all candidates: params, mass, pass/fail, governing).
6. Scripts used (`l47_so_*.py`), so the box can reproduce the mass and clearance checks.

## 6b. Mesh/convergence (explicit)
- P2 tets (gmsh), same functions as `actuators/hp_lever_fea_v2.py` with STEP import.
- Screening candidates: G3's converged level only (A1). Final candidate: full sequence, peak change < 5 % over the last two levels, else declare singularity with location.
- Refinement balls: G3 hot spots + every new pocket corner/rib root (local h ≤ 1.0 mm).

## 6c. Compute budget
- bryan PC only, ≤ 8 h wall, ≤ 8 GB RAM; topology screen ≤ 1 h; ≤ 30 LHS candidates + ≤ 3 local refinements; ≤ 2 rounds.
- Commit outputs as `Legs L47-SO <summary>` to `modules/legs/results/l47_so/` and `modules/legs/cad/` only. Summary file: `modules/legs/results/l47_so/L47_SO_REPORT.md` + `l47_so_results.json` (keys: mass_kg_per_lever, delta_vs_RC, delta_vs_sf15, per-case peak/amp, clearances, pass).

## 7. Resources and rules
- **Where:** run on Bryan's "bryan" PC (ff639f5a) via Grok Interface. **Never on DESKTOP-B115PVV.** Expected about 4–8 GB RAM, ≤ 8 h.
- **What to change:** don't edit CONTRACTS.md or Actuators files. Write only to the output paths above. Commit on a branch or as `Legs L47-SO ...`.
- **Sources:**
  - R-031 §6 (fatigue rule), Arbiter R-056 / R-066 / R-069;
  - Legs DECISIONS L47 / L47-R;
  - Actuators DECISIONS (RC measurement);
  - `GROKBUILD_lever_fea_r031.md` (G3).
