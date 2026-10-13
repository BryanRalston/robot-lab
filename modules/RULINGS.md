# RULINGS.md
Arbiter rulings on disputed proposals. Rulings are made only against TARGETS.md and evidence (CHARTER). TARGETS.md was approved by Bryan on 2026-10-13, so rulings from R-001 on are final. IDs: R-NNN.

## Template
```
### R-NNN: on P-NNN <title>
- Date: YYYY-MM-DD
- Module(s) / proposer: <...>
- Change requested: <old → new>
- Impact on contracts / targets: <summary, weighted score per TARGETS.md method>
- Evidence reviewed: <files, URLs; quality factor 1.0 / 0.5 / 0>
- Ruling: accepted | accepted with conditions | rejected | deferred (needs evidence: ...)
- Rationale: <hard constraints checked, weighted score, evidence quality>
- Contract edits made: <CONTRACTS.md lines changed, commit>
```

## Rulings

### R-001: on P-005 / D11, mass overrun 67.60 kg vs 65 kg (T2 hard)
- Date: 2026-10-13
- Module(s) / proposer: Actuators (D11, P-005), Legs (mass consumer), Torso placeholder
- Change requested: choose among (a) margin 1.5 → 1.3, (b) CAD-verify the 1.30 kg [EST] linkage allowance, (c) take mass from the v3 CAD 56.3 vs rollup 63.8 kg gap.
- Impact on contracts / targets: robot 67.60 kg (`actuators/results/sizing.md` mass rollup) = 63.79 + 3.24 (leg actuators, incl. 1.30 [EST] linkage) − 0.22 (drives) + 0.79 (battery). T2 hard limit exceeded by 2.60 kg.
  - (a) margin 1.3 → 67.08 kg (`sizing_m1.3.json`), Δ −0.52 kg, script-backed ×1.0. Weighted T2 score = 0.52/65 × 0.15 = +0.0012. That is below the 0.01 threshold, so per the TARGETS method the contract stays at 1.5. Also, the gait is one family that is not yet walking at 1.2 m/s (P-004), so cutting margin now is not justified.
  - (b) CAD linkage: up to −1.30 kg, but the allowance is itself [EST]; the saving is unknown until CAD. Credit now: 0.
  - (c) Gap reconciliation (from `v3/cad/out/mass.md` and `v3/analysis/results/v3.json`): gap 63.79 − 56.30 = 7.49 kg. Items in the rollup that the CAD lacks: harness 2.00 + covers 1.86 = 3.86 kg (CAD note "no harness/covers"); hands 4.21 rollup vs 2 × 0.72 = 1.44 CAD → 2.77 kg. Explained: 6.63 kg. Unexplained residual: 0.86 kg. The gap is mostly missing parts, not spare mass. The 0.86 kg is unsupported → credit 0.
- Evidence reviewed: `actuators/results/sizing.md`, `sizing.json`, `sizing_m1.3.json`, `DECISIONS.md` D5/D11 (×1.0 for script values, ×0.5 for linkage/housing [EST]); `v3/cad/out/mass.md` (×1.0); `v3/analysis/results/v3.json` (×1.0).
- Ruling: **accepted with conditions (combine b + c, a as pre-authorized fallback).** The design is NOT T2-compliant today; P-005 selections stand, and a mass-recovery plan of −2.60 kg is binding:
  1. Actuators + Legs (joint): model the hip_pitch, knee and ankle linkages (crossbar, trunnions, nut-rotor hub) in CAD; replace the 1.30 kg [EST] with CAD mass. Accept: CAD mass report in `modules/actuators/results/`. Target: ≤ 0.65 kg for both legs (−0.65 kg).
  2. Actuators: replace the housing [EST ×1.25] model and v3 `GEAR_LEN` with Harmonic Drive / Rollvis drawing values (AUDIT A4) for the 6 leg actuators. Accept: per-actuator mass table with drawing references. Target −0.65 kg.
  3. Legs: thigh/shank/foot structure budget 5.40 → 4.90 kg (−0.50 kg), shown by CAD mass with FEA SF ≥ 2 fall and Goodman pass at the new loads.
  4. Torso placeholder (Arbiter holds until staffed): harness 2.00 → 1.60 kg (−0.40, EtherCAT one line per limb per D4 replaces v3's unspecified harness) and covers 1.86 → 1.46 kg (−0.40). Accept: harness/cable mass from `v3/cad/cables.py` extended to the EtherCAT topology; covers from CAD.
  5. Arbiter: reconcile the 0.86 kg residual line by line next round (`v3/cad/out/mass.md` vs `v3.json`). Any spare found goes to reserve, not to a module.
  6. Fallback: if after round 2 the CAD-supported total is still > 65.0 kg, margin 1.3 is pre-authorized for hip_roll, hip_pitch and ankle only (−0.52 kg) provided every joint keeps carry torque ratio ≥ 1.0 (hip_pitch at 1.3: need 287 ≥ carry peak 265).
  7. Legs: re-run gait ID at the final mass. The current needs were computed at 63.79 kg (`requirements.md` checks.mass_kg); at 67.6 kg they rise ~6 % and must still be met.
  - Sum of targets 1–4: −0.65 −0.65 −0.50 −0.80 = −2.60 kg → 65.00 kg, zero reserve. Acceptance for R-001 closure: CAD-supported whole-robot total ≤ 65.0 kg with no [EST] line counted at more than face value.
- Rationale: T2 is hard, so no option that leaves > 65 kg can close this. Only script-backed savings are credited; [EST] and unsupported savings are 0 until shown. Margin cut fails the 0.01 score threshold and is held as fallback only.
- Contract edits made: CONTRACTS.md "Round 1 amendments" §R1.1 (mass budgets), §R1.2 leg actuator rows.

### R-002: regen credit for T7 runtime (≥ 2 h walking at 1.2 m/s, hard)
- Date: 2026-10-13
- Module(s) / proposer: Legs (P-004), Actuators (D10)
- Change requested: count shared-DC-bus netting of negative joint power toward runtime.
- Impact on contracts / targets: 1.2 m/s total 772 W no regen → 1.89 h (fails T7); 576 W with full netting → 2.53 h (`sizing.md` energy table, 1620 Wh × 0.9).
- Evidence reviewed: `actuators/size.py`, `results/sizing.md` (power model ×1.0). The netting itself is sample-level arithmetic with no bus/drive regen-efficiency or brake-chopper model → [EST] ×0.5.
- Ruling: **accepted with conditions: half credit.** Credit = 0.5 × (772 − 576) = 98 W → 674 W → 1620 × 0.9 / 674 = **2.16 h ≥ 2 h (provisional pass)**. Full credit only on evidence: (i) Actuators: bus-level sim including drive regen efficiency, chopper/BMS-charge path and the ≤ 90 V clamp (D9), or (ii) the G5 single-leg bench test measuring net bus energy per stride. If evidence shows < 98 W of netting, Torso must go to 20S6P (120 cells, 1944 Wh, 10.5 kg, +1.75 kg at the v3 pack factor), which T2 cannot absorb today, so this evidence is priority.
- Rationale: T7 is hard. The netting is physically real on a shared bus, but unmodelled losses make the full value an estimate, so it counts at half weight per TARGETS. 1.0 m/s passes with no credit (2.22 h), which bounds the risk.
- Contract edits made: CONTRACTS.md §R1.3 walking power budget.

### R-003: 20 kg carry speed (T5)
- Date: 2026-10-13
- Module(s) / proposer: Legs (P-001 carry case), Actuators (D1, O3)
- Change requested: size actuators to carry at 1.2 m/s (P-001 carry-governed needs 86/184/398/266/359), or accept a slower carry.
- Impact on contracts / targets: sizing to carry-governed needs would add actuator mass on a robot already 2.6 kg over T2. The walk/stairs-sized selections already deliver carry at 1.2 m/s with torque ratio avail/carry-peak hip_yaw 1.22, hip_roll 1.67, hip_pitch 1.32, knee 1.44, ankle_pitch 1.30; speed and thermal pass (max ΔT 66 K) (`sizing.md`, script ×1.0).
- Evidence reviewed: `legs/results/carry_20kg.json`, `actuators/results/sizing.md`.
- Ruling: **T5 carry is a verification case, not a sizing case.** Requirement: 20 kg two-handed carry at **1.2 m/s with ≥ 1.2× torque ratio on every leg joint** (not 1.5×). If a later change drops any joint below 1.2×, carry speed may fall to 0.8 m/s, but only after Legs re-runs the carry at that speed (no number is claimed for it today). T7 runtime does not apply to carry (carry 1.99 h with the R-002 half credit, information only).
- Rationale: T2 is hard and weighted 0.15; T5 is soft (0.12). Requiring 1.2 m/s costs no mass today because the selections already meet it at ≥ 1.22×, so there is no reason to relax speed.
- Contract edits made: CONTRACTS.md §R1.2 note.

### R-004: on P-001 leg torque needs from gait ID
- Date: 2026-10-13
- Module(s) / proposer: Legs / RL Legs; Actuators agreed for walk/stairs/push/sit
- Change requested: CONTRACTS §1a leg need peak → 1.5 × gait-ID peak, plus RMS lines.
- Evidence reviewed: `legs/results/requirements.md`, `envelope.json` (×1.0, one gait family).
- Ruling: **accepted as amended.** Needs = 1.5 × max(walk 0.8–1.2, stairs, push, sit): hip_yaw 66, hip_roll 177, hip_pitch 331, knee 231, ankle_pitch 305, ankle_roll 61 N·m; RMS 14/45/86/72/44/7 N·m. Carry-governed values are not needs (R-003). Must be re-run at final mass (R-001 item 7).
- Rationale: replaces v2 mass-scaled guesses (AUDIT A3) with sim-backed values; both owners agree.
- Contract edits made: §R1.2.

### R-005: on P-002 leg speed needs
- Date: 2026-10-13
- Ruling: **accepted.** hip_pitch 8.1, knee 13.3, ankle_pitch 6.9 rad/s; hip_yaw/hip_roll/ankle_roll stay 3/3/4 [EST] until turning/side-step is simulated (Legs action). Condition (from O4): knee motor runs 7963 rpm vs Nmax 8000 (0.5 % margin). Actuators must show ≥ 5 % rpm margin (≤ 7600 rpm at 13.3 rad/s) next round via lead or lever trade.
- Evidence reviewed: `requirements.md`, `sizing.md` (×1.0). Contract edits made: §R1.2.

### R-006: on P-003 leg range of motion
- Date: 2026-10-13
- Ruling: **accepted with conditions.** ROM need ankle_pitch ≥ −60…40°, hip_pitch ≥ −120…40°. Because −60° hit the IK limit on stairs, Legs must re-run stairs with a wider IK limit and report the true ankle need; the toe-joint alternative is deferred until that number exists. Acceptance: Legs + Actuators linkage study (O1) shows screw stroke and clash-free motion at these ROMs (feeds G2).
- Evidence reviewed: `legs/results/*.json` qmin_deg (×1.0). Contract edits made: §R1.2.

### R-007: on P-004 walking power and T6 status
- Date: 2026-10-13
- Ruling: **accepted.** CONTRACTS mech power line 244 W [EST CoT] is replaced by gait-ID mechanical 426 W (1.2 m/s) and the electrical totals in R-002. T6 status recorded as NOT DEMONSTRATED (G4): falls at 1.0 and 1.2 m/s in forward sim. Legs' first priority is a controller that walks 1.2 m/s on CONTRACTS limits.
- Evidence reviewed: `legs/fsim.py`, `legs/results/fsim/*.json` (×1.0). Contract edits made: §R1.3.

### R-008: on P-005 actuator family, 20S bus, Gold Twitter, EtherCAT
- Date: 2026-10-13
- Ruling: **accepted with conditions.** Adopt 20S (68–84 V), Elmo Gold Twitter, EtherCAT 1 kHz DC one line per limb, the leg selections and pack limits (60 A cont, 100 A/2 s, fuse 125 A). Conditions: R-001 mass recovery; R-005 knee rpm margin; Actuators to read the Gold Twitter peak-current rating and the Rollvis RV12 max speed and re-check screw L10 at the new levers (O4). Rotary hip_pitch rejected (5.7 kg vs 2.37 kg per hip; T2).
- Rationale: only proposal that meets P-001/P-002 needs; mass cost handled by R-001.
- Evidence reviewed: `size.py`, `sizing.md`, `DECISIONS.md` D2–D9, Elmo/Kollmorgen/HD/Rollvis datasheets cited there (×1.0; housing/linkage ×0.5). Contract edits made: §R1.1–R1.4.

### R-009: on P-006 regen credit for T7 at steady-state 1.2 m/s (supersedes R-002 numbers)
- Date: 2026-10-13
- Module(s) / proposer: Actuators (P-006, D16/D17); affects Legs, Torso placeholder
- Change requested: full (×1.0) regen credit from `regen_sim.py`; R1.3 → 667 W / 2.19 h.
- Verification (`actuators/results/regen_sim.json`, usable 1620 Wh × 0.9 = 1458 Wh): steady 2–7 s no regen 942.4 W → 1458/942.4 = 1.55 h; netting + 30 A BMS charge 666.6 W → 2.19 h; netting only 672.3 W → 2.17 h; end-of-discharge 673 W → 2.17 h (D17). Numbers reproduce. Chopper idle (bus min −341 W, negative 2.9 % of time, Vbus max 72.3 V ≪ 90 V clamp).
- Assumptions reviewed: bus/battery model is a time-domain sim (OCV 72 V, R_pack 60 mΩ, 30 A charge limit) ×1.0. But its input is the Legs **gait-ID trace walk_1p2, a modeled gait that the forward sim cannot yet walk** (falls at 1.2 m/s, G4/R-007); drive-loss conduction/switching split is [EST]; motor iron loss unmodelled; transmission back-drive efficiencies are model values; one gait, one 5 s window, no sensitivity sweep supplied. The regen delta (275.8 W) is therefore modeled evidence → ×0.5.
- Math: credit = 0.5 × (942.4 − 666.6) = 137.9 W → contract **804.5 W → 1458/804.5 = 1.81 h**. T7 (≥ 2 h, hard) needs ≤ 729.0 W, i.e. realised regen ≥ 942.4 − 729.0 = 213.4 W = **77 % of the modeled 275.8 W**.
- Fallbacks checked: 20S6P (1944 Wh, +1.75 kg per R-002) → 1749.6/804.5 = 2.17 h, but mass 65.79 + 1.75 = 67.54 kg (64.49 + 1.75 = 66.24 kg if R-001 cuts land) → violates T2 hard. Not available unless ≥ 1.75 kg more is found below the 65 kg line (total ≤ 63.25 kg before the pack change). Lower speed: no steady-state regen-sim number at 1.0 m/s exists yet (R-002's 658/512 W were whole-trace averages, now invalid per D17) → no credit claimed.
- Ruling: **P-006 power section accepted with conditions; full regen credit DENIED pending bench measurement.** T7 status: **NOT MET (1.81 h at weighted evidence; 2.19 h modeled best case).** Pack stays 20S5P (no mass for 6P). Full credit is granted when the G5 single-leg (or dual-actuator shared-bus) bench measures net DC-bus energy per stride on the walk_1p2 joint trajectories ≥ 213 W of netting relative to the no-regen case, or a forward-sim gait that walks 1.2 m/s under CONTRACTS limits is re-run through `regen_sim.py` with a sensitivity sweep showing ≥ 77 % of credit at worst corner (that upgrades to ×1.0 sim, bench still required before build). Hard deadline: evidence by end of round 4; if missed or failed, Arbiter re-rules T6/T7 trade (cruise speed for the 2 h rating) using a steady 1.0 m/s regen-sim number. P-006 knee (D12) and CAD masses (D13/D14) accepted as filed; BMS 30 A regen-charge limit, brake chopper and ≤ 90 V clamp adopted.
- Rationale: T7 is hard and the only cheap fix (bigger pack) breaks T2, also hard. The regen physics is credible but rests on a gait that does not walk; counting it at ×1.0 would let the design pass a hard constraint on a modeled input. D17's correction (steady vs whole-trace) is accepted ×1.0 and makes the prior R-002 2.16 h figure void.
- Contract edits made: CONTRACTS.md §R1.3; TARGETS.md G5 and status lines.

### R-010: on P-007 iron-loss walking power, T7 rating speed, R-009 pass line (Arbiter deviation ruling)
- Date: 2026-10-13
- Module(s) / proposer: Actuators (P-007, b14fdc3, D18–D24); affects Legs, Torso placeholder
- Verification (`actuators/results/regen_sim.json`, `regen_sweep_walk_1p2.json`, `regen_sweep_walk_1p0.json`, usable 1620 × 0.9 = 1458 Wh): 1.2 m/s 963.9 no regen / 841.6 half / 719.4 W full (regen 244.5 W, iron 44.0 W) → 1.51 / 1.73 / 2.03 h. 1.0 m/s 783.3 / 699.0 / 614.8 W → 1.86 / **2.09** / 2.37 h. Required regen at 1.2 m/s = 963.9 − 729.0 = 234.9 W = 234.9/244.5 = **96.1 %** of modeled. Sweep fraction of corners with full-regen P ≤ 729 W: 1.2 m/s **0.367** (model-only 0.473), retention min 0.62, p05 0.75; 1.0 m/s 0.949 (model-only 0.988). All P-007 claims reproduce. Iron loss from TBM2G rated points ×1.0 (datasheet method, D18); CSG back-drive η 0.65 [EST]; gait still not forward-sim walkable at 1.0/1.2 m/s (G4) → regen delta stays ×0.5.
- (a) Pass line restated: **accepted.** T7 pass = steady walking P ≤ usable Wh / 2 h (729.0 W on 1620 × 0.9). The R-009 "77 % / ≥ 213 W" form is superseded: bench must show realised regen ≥ 235 W at 1.2 m/s (or P ≤ 729 W absolute).
- (b) 2 h rating at 1.0 m/s: **accepted as an explicit Arbiter deviation from R-002/R-009** (which read T7 at the T6 speed; TARGETS T7 text itself names no speed). Options, hard constraints first: keep 2 h at 1.2 m/s → 1.73 h at weighted evidence, T7 hard FAIL → rejected; 20S6P pack → T2 hard FAIL (R-009) → rejected; rate 2 h at 1.0 m/s → T7 2.09 h, no hard violation. Weighted cost of (b): T6 endurance speed Δ = −(1.2 − 1.0)/1.2 = −0.167 × w 0.10 × evidence 1.0 = **−0.017**. Only option that passes all hard constraints, so it stands regardless of score. T6 target value (≥ 1.2 m/s sustained) is NOT changed and stays tracked.
- (c) 1.2 m/s rating: **accepted.** 1.2 m/s rated at **1.73 h** (half credit; 2.03 h modeled full) until the G5 bench shows ≥ 235 W realised regen; then the 2 h rating moves back to 1.2 m/s. Tracked values: 963.9 / 841.6 / 719.4 W.
- Minimum-capacity pack (O12): Molicel P45B datasheet (`actuators/datasheets/molicel_p45b.txt`): typical 4500 mAh / 16.2 Wh, **minimum 4300 mAh / 15.5 Wh**, discharge cutoff 2.5 V. 100 cells min = 1550 Wh × 0.9 = 1395 Wh → 1.0 m/s half credit 699.0 W → 1.996 h, pass line 697.5 W → **fails T7 by 1.5 W (Actuators' "4 W" is ~1.5 W at 1.0 m/s; either way a fail)**. T7 is hard, so it must hold on the minimum pack, not the typical one.
  - **92 % usable: rejected (evidence ×0).** No cell or BMS data supports it. Note that even 90 % is unverified: the 20S bus floor 68 V = 3.4 V/cell, far above the datasheet's 2.5 V cutoff, so usable fraction at a 3.4 V floor and ~1.9 A/cell (699 W / 72 V / 5P) must be read from the P45B discharge curve or measured. 90 % is reclassified [EST] pending that.
  - **Cell binning: accepted as a Torso pack requirement**, no mass change: incoming cells screened ≥ 4400 mAh at 0.2C → 100 × 4.4 Ah × 3.6 V = 1584 Wh × 0.9 = 1425.6 Wh → 699.0 W → **2.04 h**, pass line 712.8 W (13.8 W margin). Credit is conditional on (i) a supplier binning spec/yield and (ii) the usable-fraction check above.
- Ruling: **P-007 accepted with conditions.** T7 status: **MET provisionally at 1.0 m/s** (2.09 h typical pack / 2.04 h binned pack, half credit), contingent on binning + usable-fraction evidence; **1.2 m/s NOT MET (1.73 h)**. Mass unchanged (no pack change; T2 respected).
- Contract edits made: CONTRACTS §R1.3 rewritten; TARGETS status + G5.

### R-011: on P-008 65 kg requirement table, ankle_pitch carry margin, ankle loaded ROM
- Date: 2026-10-13. Proposer: Legs (4d1ea52..2c0dbe9, `legs/results/r2/requirements.md`, ×1.0 one gait family).
- Change 1 (needs at 65 kg 66/180/334/235/309/62 N·m): **accepted.** All within R1.2 avail; ankle_pitch 309 vs 311 (0.6 % headroom) flagged as the tightest joint.
- Change 2 (carry): verified ankle_pitch carry peak 283.2 N·m (carry_20kg_r2) → 311/283.2 = **1.10× < 1.2×** at 1.2 m/s. Applying R-003 as written: the fallback is **0.8 m/s, not 1.0 m/s**, and only after Legs re-runs the carry at that speed. No 1.0 m/s carry run exists, so Legs' 1.0 m/s proposal has no evidence (×0). **Ruling: T5 carry verification speed = 0.8 m/s (provisional until Legs' 0.8 m/s carry run shows ≥ 1.2× on every leg joint); 1.2 m/s carry stays tracked at 1.10×.** Legs may re-propose 1.0 m/s with a 1.0 m/s carry run ≥ 1.2×.
  - Preferred restore path (zero mass): ankle_pitch lever 70 → 77 mm [EST, linear scaling]: 311 × 77/70 = 342 N·m ≥ 1.2 × 283.2 = 340 (1.21×); speed 13.7 × 70/77 = 12.5 rad/s ≥ 9.43 gait peak. Actuators to check stroke, screw L10, envelope/clash. Weighted: restores T5 Δ +(0.4/1.2) × 0.12 = +0.040 at ~0 T2 cost → preferred over the speed cut once verified.
- Change 3 (ankle ROM): **accepted with split.** Loaded torque need over **−50…+40°** (stance min −48° walk_1p2_r2, −36…−42° stairs). Mechanical stroke/clash range stays **−60…+40°** because every gait uses past −50° in swing (walk_1p2_r2 −59°, walk_1p2 −56°, carry −55°; `requirements.md` ROM column).
- Contract edits: §R1.2 ROM/carry note and need column.

### R-012: on P-009 hip_pitch deep flexion
- Date: 2026-10-13. Proposer: Legs (`r2/linkage_study.json`, L7, ×1.0).
- Verified issue: sit_to_stand uses hip_pitch −120…−13° (`requirements.md`), and the 50 mm slider-crank gives 5 N·m at −120° vs 111 N·m need (P-009).
- Options: (i) second linkage/variable lever: adds parts (lever, pins, bearings; ≥ 2 × 0.137 kg by the CAD hip lever mass [EST lower bound]), a new mechanism in G1/G2/G3 and a new failure mode, against a T2 margin of ~0.5 kg; (ii) re-plan sit-to-stand within the strong range: no mass, controller-only.
- Ruling: **re-plan accepted; second linkage rejected (T2 hard margin + complexity, no target requires −120° loaded).** Loaded hip_pitch need **−80…+40°**; mechanical (unloaded) range keeps −120° for clash/G2. Condition: Legs re-plans sit_to_stand (higher seat and/or trunk lean), states the seat height used, and shows hip_pitch ratio ≥ 1.2 throughout at 65 kg. If no feasible seat height ≤ a standard chair can be shown, re-propose.
- Knee lever 47.5 mm: no change (noted).

### R-013: on P-010 structure 4.84 kg and linkage split
- Date: 2026-10-13. Proposer: Legs (`structure.py`, `r2/structure_mass.md`, parametric solids).
- Structure 4.84 kg (both legs) vs 4.90 binding: **accepted provisionally.** Not credited to the CAD-supported total until `grokbuild/structure_fea.md` shows SF ≥ 2 fall and Goodman pass at 65 kg loads (R-001 item 3). Until then the rollup keeps 5.40 kg.
- Linkage split (0.588 kg both legs, 0.062 kg left for nut-rotor hubs): **not plausible as stated.** Actuators CAD `cad_mass.json` nut_rotor_hub_x1 = 0.0160 kg each. Two hubs per twin-screw unit (Legs' own note) × 3 units (hip_pitch, knee, ankle) × 2 legs = 12 hubs = **0.192 kg** vs 0.062 → 0.130 kg short (0.062/12 = 5.2 g per hub, 1/3 of the CAD part). Also overlap risk: Actuators' CAD linkage line (0.609 kg both legs, already in the 16.79 kg actuator rollup) contains the hip/knee levers that Legs' "crossbar + cheeks" appear to re-estimate, while Legs' ankle instep lugs (0.084 kg) are in neither CAD table.
- Ruling: **rejected as a contract split; one linkage table required.** Rollup keeps Actuators' CAD 0.609 kg. Mass risk carried: +0.084 (ankle lugs) + up to +0.128 (hubs beyond the 4 already in Actuators' table) = **+0.21 kg risk**. Actuators + Legs deliver one non-overlapping linkage table (part, owner, CAD mass, count) next round; target stays ≤ 0.65 kg.

### R-014: on P-011 change 1, T5 carry verification speed 0.8 → 1.0 m/s; change 2, sit-to-stand
- Date: 2026-10-13. Proposer: Legs (1e65b3f, 284251e).
- Verification (`legs/results/r3/carry_20kg_1p0.json` peaks vs CONTRACTS R1.2 avail): hip_yaw 70/41.3 = 1.69, hip_roll 204/112.1 = 1.82, hip_pitch 350/229.9 = 1.52, knee 258/159.6 = 1.62, **ankle_pitch 311/238.3 = 1.31**, ankle_roll 177/31.6 = 5.6 → all ≥ 1.2 (R-003). Forward sim `fsim/carry_20kg_1p0_fb1_kr4.json`: fell_at_s null, 16 touchdowns, saturated_frac {} (none), torque_limit_scale 1.0, final track error −0.9 mm. Steady step 0.47 m / 0.47 s = 1.0 m/s (mean 0.68 m/s over 8.75 s includes ramp-up/down steps). 0.8 m/s run: ankle 219.8 → 1.41. All P-011 claims reproduce.
- Caveats weighed: 29 frames (~0.15 s) with base residual > 5 % BW (max 61.2 N, friction ratio 1.13) at touchdowns, same as every carry run; one nominal gait, no domain randomization (G4) → evidence ×0.5 for G4, ×1.0 for the R-003 margin test as written.
- Ruling: **accepted. T5 carry verification speed = 1.0 m/s, replacing the R-011 0.8 m/s fallback.** 1.2 m/s carry stays tracked (ankle 1.10×, fails). 77 mm ankle lever path (R-011) stays open with Actuators; if it lands (≥ 1.2× at 1.2 m/s carry, stroke/L10/clash pass, mass ≤ R-015 actuator ceiling) carry returns to 1.2 m/s. Weighted: T5 deficit vs 1.2 m/s drops from (0.4/1.2) to (0.2/1.2) × 0.12 = 0.020.
- Change 2 (sit-to-stand 0.46 m seat, hip ≥ −74.6°, hip ratio ≥ 20.6, knee ≥ 2.35, ID only): **R-012 condition met (ID).** Forward-sim confirmation folds into G4; no re-proposal needed.

### R-015: on P-011 information, leg linkage overrun and T2 mass recovery (supersedes R-013 risk numbers)
- Date: 2026-10-13. Inputs: `legs/LINKAGE_TABLE.md` (committed, 284251e); Actuators' `actuators/results/LINKAGE_TABLE.json` (33a7186, 2.527 kg both legs, rollup 67.71) cross-checked.
- Verified (committed table): per leg 0.1666 + 0.1346 + 0.0960 + 0.1036 + 0.0420 = 0.5428 → **1.086 kg both** vs 0.609 in rollup → **+0.477 kg**. Leg total: structure 4.85 + linkage 1.086 = 5.94 vs 4.90 + 0.65 = 5.55 → +0.39 kg (Robot Lab figure reproduces).
- Unmassed / risk lines (both legs):
  - trunnion pairs 5–6: 2 × 2 × 0.0259 = **+0.104** (Actuators 33a7186 confirms 6 pairs/leg → real).
  - rod-end eyes ø12, 12 pcs × 0.025 [EST, Actuators 33a7186; catalog datasheet pending] = **+0.300 [EST]**.
  - hip_pitch pivot bearing (owner Actuators per Robot Lab 1:09): IKO CRBH 5013 A 0.29 kg (datasheet, per Actuators 33a7186) + 0.024 clamp [EST] = 0.314 × 2 = **+0.628**.
  - thigh trunnion clamp (Legs, unsized): 2 × 0.10 [EST] = **+0.200 [EST]**.
  - Sum unmassed = 1.232 kg. Hip lever config B (Actuators CAD+FEA, 33a7186): 0.371 vs 0.167 each → **+0.409** (committed, counted).
- Rollup (math): CAD-supported 65.79 + 0.477 = **66.27 kg**; + 1.232 unmassed = **67.50 kg**; pending credits: Legs structure 5.40 → 4.85 (−0.55, FEA pending) and Torso −0.80 (R-001) → 66.15 kg; + config B lever 0.409 → **66.56 kg** (Actuators' 66.35 = same minus my 0.20 [EST] clamp; incl. lever, uncredited total 67.91 vs Actuators 67.71). **Overrun vs 65.00: 1.56 kg.**
- Options: bigger linkage budget alone → T2 hard FAIL, rejected; 20S5P → smaller pack → T7 hard FAIL (R-010), rejected; drop twin-screw → reopens R1.2 torque, rejected. Only recovery across module budgets passes all hard constraints.
- Ruling: **linkage table accepted as the single source (1.086 kg counted, unmassed carried at the values above). Linkage budget raised 0.65 → 1.40 kg incl. hip pivot bearings and rod ends, inside a reduced leg-actuator ceiling. Recovery of 1.95 kg ordered:**

| # | owner | budget change | kg | acceptance criterion |
|---|---|---|---|---|
| M1 | Actuators | leg actuator line incl. linkage, hip bearings, rod ends: all-in now 16.79 (incl. 0.609 linkage) + 0.477 − 0.084 (Legs-owned lugs) + 1.032 (trunnion, rod ends, hip bearings) + 0.409 (lever B) = 18.63 → ceiling **≤ 17.63 kg** all-in (replaces 17.30 excl. linkage) | −1.00 | CAD mass of housings (remove ×1.25 [EST] factor with solids), hip lever B back toward ≤ 0.20 kg each (FEA SF held) or offset, catalog rod ends with datasheet mass; one table, round 4 |
| M2 | Legs | structure + thigh clamp + instep lugs ≤ **4.85 kg** both legs (clamp absorbed: −0.25 vs 4.85 + 0.20 + 0.084) | −0.25 | Grok Build FEA SF ≥ 2 fall + Goodman at 65 kg incl. clamp; until then structure stays provisional at 5.40 in rollup |
| M3 | Torso (placeholder, Robot Lab assigns) | covers 1.46 → 1.20, harness 1.60 → 1.46 (on top of R-001 −0.80) | −0.40 | cover areal mass + harness routing estimate with sources |
| M4 | Brain/Head (placeholders) | brain 1.80 → 1.50 kg | −0.30 | compute module + enclosure datasheet mass |
| | | **total** | **−1.95** | |

- Result: 66.56 − 1.95 = **64.61 kg (reserve 0.39)**. Reserve stays with the Arbiter. If M1–M4 miss by > reserve at end of round 4, Arbiter re-rules (candidate: arm/hand mass, then T5 carry 20 → 15 kg at w 0.12).
- Structure remains provisional (R-013); the FEA after the walking-controller session gates the −0.55 credit.

### R-016: whole-robot T2 mass ruling: P-012 folded with P-011 overrun (supersedes R-015 allocation table; R-015 verification stands)
- Date: 2026-10-13. Inputs: P-012 (f484aca, 33a7186, c37232a; D25–D31), P-011, R-001 fallback, R-010 (pack), R-015.
- Verified: lever B 0.371 kg each (SF 2.13, coarse CPU FEA, ×0.5 for SF), CRBH 5013 A 0.29 kg datasheet + 0.024 [EST] = 0.314/leg, table 2.527 kg both vs 0.609 → +1.918; Actuators rollup 65.79 + 1.918 = 67.71 kg (reproduces); with Legs structure −0.56 and Torso −0.80 → 66.35. Arbiter adds thigh clamp 0.20 [EST] (unsized, not in table) → **67.91 / 66.55 kg**. Gap to 65.00 at best current evidence: **1.55 kg**.
- (a) Contract linkage line 2.53 kg, hip pivot bearing owned by Actuators: **accepted** (inside the R-015 M1 all-in ceiling).
- (c) Ankle lever stays 70 mm: **accepted** (77 mm at 99.9 % Nmax violates R-005); R-014 1.0 m/s carry (1.31×) stands; 1.2 m/s carry tracked, path closed unless a new lever/screw option appears.
- Levers evaluated (kg, evidence):
  - Needle-roller straddle instead of CRBH: −0.20 [EST, datasheet needed] → ordered.
  - Lever SF 2.0 → 1.5 + bench proof test at 1.5× fall load: −0.10 [EST] → ordered (proof test added to G5).
  - Margin 1.5 → 1.3 (R-001 item 6, pre-approved): −0.52 script-backed (`sizing_m1.3.json`) for hip_roll, hip_pitch, ankle. Ankle_pitch is the tightest joint (309 need vs 311, carry 1.31× at 1.0 m/s) → **invoked for hip_roll and hip_pitch only**; ankle excluded. Credit: not until Actuators re-runs sizing for those two joints [EST −0.30, ×0.5]. Condition: carry ratio ≥ 1.2 at 1.0 m/s on every joint after re-size.
  - Housing ×1.25 [EST] factor replaced by CAD solids: unknown, credit 0 until CAD.
  - Battery: smaller pack → T7 hard FAIL (R-010, binned pack has 13.8 W margin) → rejected. Bigger pack also rejected (T2).
  - Torso/arms/hands/head/brain budgets: unstaffed v3 placeholder [EST] numbers; cuts are paper until a module owner substantiates → ordered but credited ×0.
- Ruling: **R-015 M1–M4 stand (−1.95 kg total, target 64.61 kg, reserve 0.39), with M1 (−1.00, Actuators) now explicitly comprising straddle −0.20, lever SF 1.5 −0.10, margin 1.3 hip_roll/hip_pitch ~−0.30, housing CAD ≥ −0.40.** Acceptance per R-015; deadline end of round 4. T2 status: **NOT MET**.
- Risk stated: evidence-backed savings today are ~−0.30 (straddle + SF, [EST]) plus a script-backed margin cut not yet re-run → credible end state ≈ 66.55 − 0.30 − 0.30 = **65.95 kg [EST]**, i.e. ~0.95 kg over unless housing CAD and placeholder cuts (all ×0 evidence today) deliver. No credible plan reaches 65.00 kg on current evidence.

#### R-016 recommendation: RESOLVED by R-017 (Bryan approved Option B)
- Option A, keep 65.0 kg: depends on ~1.0 kg of unsubstantiated cuts; if they miss, the next levers are T5 payload 20 → 15 kg (weighted −(5/20) × 0.12 = **−0.030**) or T7 runtime (hard, no room).
- Option B, raise T2 hard limit to **66.5 kg** (stretch ≤ 60 kg unchanged): covers the current-evidence end state 65.95 with 0.55 reserve. Weighted cost −(1.5/65) × 0.15 = **−0.0035** — an order of magnitude cheaper than A's fallback and below the 0.01 threshold. Optimus reference: secondary 57/63 kg figures (TARGETS T2), so 66.5 sits ~5 % above the heavier report.
- Arbiter recommended **B (66.5 kg), keeping all R-015/R-016 cuts ordered.** Bryan approved B on 2026-10-13 (R-017); 66.5 kg is now the binding hard limit.

### R-017: Bryan approves T2 hard limit 65.0 → 66.5 kg (resolves R-016 PENDING BRYAN)
- Date: 2026-10-13 (Bryan confirmation in Arbiter chat ~2:14 PM ET)
- Module(s) / proposer: Arbiter (R-016 Option B); Bryan approval relayed via Robot Lab and confirmed directly to Arbiter
- Change requested: raise T2 hard limit from ≤ 65.0 kg to ≤ 66.5 kg; keep 20 kg carry (T5); keep all R-015/R-016 cuts M1–M4 ordered
- Impact on contracts / targets: T2 hard → ≤ 66.5 kg (stretch ≤ 60 kg unchanged). Rollup if M1–M4 land: 64.61 kg (reserve 1.89 vs 66.5). Credible evidence end state ≈ 65.95 kg [EST] (reserve 0.55, thin). Weighted cost of the limit raise: −(1.5/65) × 0.15 = −0.0035 (below 0.01 threshold). T5 20 kg carry retained (vs fallback 15 kg at −0.030). No module budget loosened.
- Evidence reviewed: R-016 recommendation and numbers; Bryan direct confirmation in Arbiter chat 2026-10-13 ~2:14 PM ET ("Yea i dont see why not"); Robot Lab standing delegation that the crew owns design calls.
- Ruling: **accepted.** T2 hard limit is **≤ 66.5 kg**. Cuts M1–M4 remain ordered and binding. Owners for unstaffed cuts (Robot Lab assignment, recorded here):
  - **M3 harness** (2.00 → 1.46 kg): **RL Actuators** (owns bus and harness).
  - **M3 covers** (1.86 → 1.20 kg): **Arbiter placeholder** — size from catalog parts; credit only when backed by real numbers.
  - **M4 brain/compute** (1.80 → 1.50 kg): **Arbiter placeholder** — size from catalog parts; credit only when backed by real numbers.
  - M1 Actuators and M2 Legs unchanged from R-015/R-016.
- Rationale: Bryan confirmed the R-016 Option B recommendation. Raising the hard limit by 1.5 kg is far cheaper on the TARGETS score than cutting payload, and the credible end state (65.95 kg) fits inside 66.5 with a thin reserve. Cuts stay ordered so the design still lands as low as evidence allows.
- Contract edits made: TARGETS.md T2 row + hard-constraints + R5 status; CONTRACTS.md §0 robot mass and §R1.1 robot row → ≤ 66.5 kg (module budgets unchanged).

### R-018: on P-013 (Actuators round 4: M1 result, M3 harness credit, O19 shortfall)
- Date: 2026-10-13. Proposer: Actuators (ce469c4, 26c6f8b, 0f21a0a; D32–D40, `results/mass_rollup_r4.json`, `results/harness.{py,json,md}`).
- **Verified (reproduced from `mass_rollup_r4.json`):** base 67.91 (R-016) − 0.153 needle straddle − 0.245 lever SF 1.5 + 0.120 rod ends (GE 12 E datasheet 0.016 kg + 7075 eye 0.019 calc, ×12) + 0 margin 1.3 + 0 housing = **67.632 kg; M1 = −0.278** (vs −1.00). Harness model 0.435 wire + 0.284 connectors + 0.052 sleeving + 0.050 BMS leads = **0.821 kg**, cut vs 2.00 rollup line = −1.179 → paper **66.453 kg**; flat ×0.5 → 67.04. All Robot Lab numbers reproduce.
- **D34 (1.3× re-size) accepted:** catalogue steps make hip_roll 1.500 vs 1.455 kg and hip_pitch 2.171 vs 2.154 kg at 1.3×, i.e. heavier. **R-016's 1.3× invocation for hip_roll/hip_pitch is rescinded; both stay at 1.5× units.** R-001 1.3× fallback stays closed for mass purposes (no gain). Carry 1.0 m/s ratios unchanged (1.82 / 1.97).
- **D35 accepted:** housing ×1.25 factor was already removed in round 2 (D13, −1.11 in the 65.79 base); R-016's −0.40 was a double count, withdrawn.
- **Lever SF 1.5 (−0.245):** mass is CAD (credited ×1.0); structural adequacy stays gated on O13 converged FEA + the hip-lever proof test before G5. If O13 shows SF < 1.5 the mass returns.
- **Harness credit, per part** (`harness.py` evidence; no harness datasheet is committed in the repo):
  - Physics/catalogue-named parts, full credit at the +20 % length/tolerance bound: copper (area × 8.96 g/cm³) 0.217 × 1.2 = 0.261; connectors (Amass XT60/XT30/AS150U, JST-GH masses named, ±20 %) 0.284 × 1.2 = 0.341 → **0.602**.
  - [EST] parts, half credit against their pro-rata share of the 2.00 baseline (k = 2.00/0.821 = 2.435): insulation g/m 0.063 × 1.2, EtherCAT 14 g/m 0.154 × 1.2, BMS leads 0.050 → 0.311 → credited 0.311 + 0.5 × (0.311 × 1.435) = **0.534**; sleeving 12 % of the 1.2× wire (0.522) = 0.0626 → credited **0.108**.
  - Completeness allowance [EST] for runs not in the model (cameras/head data, IMU, foot F/T, e-stop loop, tactile bus): **+0.10**.
  - **Credited harness = 0.602 + 0.534 + 0.108 + 0.100 = 1.344 kg → credit −0.656 kg** (vs −1.179 paper, −0.589 flat ×0.5). Full credit to the routed-CAD mass once O16 delivers datasheet g/m + routed lengths.
- **Rollup vs 66.5 hard:** paper 66.45 (reserve 0.05); **credible 67.632 − 0.656 = 66.976 kg → 0.48 kg OVER.** Torso −0.80 (R-001) and M3 covers / M4 brain stay credited ×0 (no owner data; Arbiter could not source a catalogue mass for the compute module this round: NVIDIA AGX Orin datasheet gives 100×87×16 mm with TTP, mass not stated → [EST]).
- **O19 ruling:** Actuators' M1 obligation is closed at −0.278 (no further actuator lever without a T5/T6 trade; accepted). The 0.72 shortfall is reassigned. Required: 0.48 to reach 66.5 + **0.30 kg reserve** = **0.78 kg credible**.

| # | owner | action | credible kg | acceptance | deadline |
|---|---|---|---|---|---|
| A1 | RL Legs | M2: structure FEA credit (5.40 → 4.85) and absorb thigh clamp + lugs inside 4.85 | −0.56 −0.25 = **−0.81** | `grokbuild/structure_fea.md`: SF ≥ 2 fall + Goodman pass at 66.5 kg loads incl. clamp; CAD/parametric mass table ≤ 4.85 kg both legs | end of round 5 |
| A2 | RL Actuators | O16 harness: datasheet g/m (silicone AWG, EtherCAT cable), connector datasheets, routed lengths from Legs/Torso geometry, incl. the completeness runs | up to −0.52 more (1.344 → model value) | committed datasheets + routed-length table; credit moves part by part | end of round 5 |
| A3 | Arbiter | M3 covers / M4 brain sized from cited catalogue parts | credited ×0 until cited | each line cites a datasheet mass | end of round 5 |
| A4 | RL Actuators | O13 converged lever FEA + proof-test plan | 0 (protects −0.245) | SF ≥ 1.5 converged | before G5 |

- **Result:** A1 alone → 66.976 − 0.81 = **66.17 kg (reserve 0.33)**; A1 + A2 full → 65.65 (reserve 0.85). T2 stays **NOT MET** until A1 lands.
- **Fallback (end of round 5, if credible > 66.2):** Arbiter re-rules across arms/hands/Torso budgets first. Any change to T2 or T5 values goes to Bryan; the Arbiter will not change them.
- Contract edits: CONTRACTS R1.1 harness, actuator, reserve, robot rows; TARGETS status R6; P-013 status.

### R-019: on P-014 (Legs round 4: M2 credit, hip stop −105°, thigh clamp form, ankle at 66.5 kg) + O18
- Date: 2026-10-13. Proposer: Legs (2236c98; L16–L20, `legs/results/r4/structure_m2.md`, `requirements.md`, `envelope.json`, `fea_*_r4*.json`); Actuators D26, D28 (`results/hp_clearance.json`, `results/ankle_lever_77.json`). Robot Lab design calls reviewed, each verified below.
- **1. Hip_pitch hard stop −105° (amends R-012): accepted.** Verified: max flexion in every r4 scenario (walk 0.8/1.0/1.2, carry, stairs, push, sit-to-stand) is −76° (`requirements.md` q range [−76, 11]; sit-to-stand −74.6° at 0.46 m seat) → 29° spare to the stop. Toggle −114.5° (`hp_clearance.json`: rod passes through pivot, stroke reversal) → 9.5° margin stop-to-toggle; −120° is physically past toggle, so R-012's −120° mechanical range is void. New layout (pivot parts |y| ≤ 22, rods |y| 63–75) gives 41 mm lateral clearance at every angle, so −80…−105° has no clash. R-012 amended: hip_pitch loaded −80…+40°, **mechanical −105…+40°**, G2 clash sweep to −105°. Condition: stop bumper deflection + stop-structure compliance under a fall into the stop < 9.5° (Legs, with the bumper's ~0.01 kg [EST]).
- **2. Ankle lever 70 → 73 mm: accepted, conditional on stroke/L10/clearance.** Verified from `ankle_lever_77.json` (Actuators `ankle_lever.py`): T_out 323.8 N·m; motor 7578 rpm at the 6.92 rad/s need = **94.7 % Nmax ≤ 95 % (R-005; margin 0.3 %, thin)** — 74 mm already fails (96.0 %), 77 mm closed by R-016 (99.9 %). Need at 66.5 kg: 323.8/314.0 = **1.031×** (70 mm: 311/314 = 0.99× fail). R-003 carry at 1.0 m/s (66.5 kg run, peak 241.5): 323.8/241.5 = **1.34× ≥ 1.2** (70 mm: 1.29×). 1.2 m/s carry: 1.14× (stays tracked, fails). Stroke +4.3 % (stroke_scale 1.043); lever +0.0014 kg each. Screw life: for equal joint torque, screw force × 70/73 and nut travel × 73/70 → L10 hours scale (73/70)³/(73/70) = **1.088× better** (derived; absolute ankle L10 is still unverified, O4/O8 open). Not verified anywhere: RV12x4 stroke availability for +4.3 % and instep clearance at 73 mm. Conditions (C2a Actuators: stroke vs RV12x4 catalogue + absolute L10 at 73 mm; C2b Legs: instep/lug clearance over −60…+40°), round 6; if either fails, fallback is the needs basis at the actual credible mass (66.72 → 1.5 × 209.3 × 66.72/66.5 ≈ 315 [EST, linear], still > 311) → re-rule.
- **3. Thigh clamp: split collar + axial ø12 eye, 0.237 kg/leg: accepted, conditional on Actuators' written agreement** to swap 2 trunnion pin pairs/leg for 1 axial eye per hip_pitch body. Verified: FEA (P2 h2.5, 4542 N/screw) σmax 174 MPa → SF 2.90; walking 0.52× fully reversed SF 1.76 ≥ 1.5. Actuator-table delta carried now (from table masses): −4 × 0.0259 + 4 × 0.035 = **+0.036 kg** both legs [EST until Actuators re-tables].
- **4. M2/A1 credit, by evidence (A1 criteria: fall SF ≥ 2, fatigue at 66.5 kg):** M2 line 4.792 kg replaces structure 5.40 + clamp 0.20 [EST] + instep lugs 0.084 (in the linkage table) = 5.684 → **−0.892 paper**.
  - FEA-backed, ×1.0: foot 2 × 0.870 = 1.740 vs v3 feet 1.80 → −0.060 (fall 6 BW toe p99.9 SF 2.77 at 65 kg loads (3826 N); linear to 66.5 kg → 2.71 ≥ 2; Goodman 4.81; singular fixture peak SF 1.56 left to Grok Build); clamp 0.474 vs 0.20 → +0.274. Sum **+0.214**.
  - Hand / v3-scaled only (tubes 1.2 mm wall, femur ring ø80, clevis, tongue, fork): thigh 1.356 vs 2.00 → −0.644; shank 1.138 vs 1.60 → −0.462; sum −1.106 at **×0.5 = −0.553** (A1 requires FEA; hand checks pass, so half credit).
  - Credited M2 change: +0.214 − 0.553 = **−0.339 kg**; remaining −0.553 on Grok Build `structure_fea.md` items 1–5.
- **5. Ankle-lug 0.084: subtracted from the linkage table, confirmed double count only once M2 is credited** (lugs are inside 4.792 per `structure_m2.md` and in `LINKAGE_TABLE.md` row "ankle rod-end lugs"; 5.40 baseline did not hold them). Done in the replacement above (5.684 includes them); linkage line 2.249 → 2.165 kg.
- Also added: split-collar bolts + hip-stop bumper +0.04 [EST, L16] at ×1.0 (conservative); ankle levers +0.003.
- **Mass rollup (vs ≤ 66.5 hard):** paper 66.453 − 0.892 + 0.036 + 0.04 + 0.003 = **65.64 kg** (reserve 0.86). Credible 66.976 + 0.214 − 0.553 + 0.079 = **66.72 kg → 0.22 kg OVER.** With Actuators' A2 datasheet harness claim (−0.030, e8acfb5, not yet ruled) 66.69. After Grok Build FEA confirms the hand-checked parts: 66.976 − 0.892 + 0.079 = **66.16 kg (reserve 0.34)**. T2 NOT MET.
- **O18 (ITECH emulator RFQ): permanently parked.** Project is theoretical: no vendor contact; emulator specs stay [EST] from published ITECH data (Actuators D44). G5 bench plan remains a paper plan.
- Actions:

| # | owner | action | kg / effect | deadline |
|---|---|---|---|---|
| A1' | RL Legs → Grok Build | `structure_fea.md` items 1–5 (foot h ≤ 2 mm with flange, clamp h ≤ 1.5 fatigue, femur ring, tubes buckling/denting at 1.2 mm, clevis/tongue/fork) at **66.5 kg loads** | releases −0.553 | end of round 5 |
| A5 | RL Actuators | agree clamp interface + re-table (−2 pin pairs, +1 eye/body); C2a ankle 73 mm stroke + absolute L10 | +0.036 confirm; ankle condition | round 6 |
| A6 | RL Legs | C2b instep clearance at 73 mm; hip stop bumper compliance < 9.5° | ankle/hip conditions | round 6 |
| A2, A3, A4 | unchanged (R-018) | A2 claim −0.030 to be ruled with next Actuators round | | |

- Fallback unchanged (R-018): if credible > 66.2 at end of round 5, Arbiter re-rules arms/hands/Torso budgets; T2/T5 values go to Bryan only.

### R-020: on P-015 (Actuators R5b, a09054a) + Legs r5 (28bcb61, L21–L24): O17 seat, clamp retention, GE eyes, M2 4.862, harness 1.296
- Date: 2026-10-13. Proposers: Actuators (D45–D51, `clamp_review.json`, `harness.md`, `LINKAGE_TABLE.md`, `mass_rollup_r5b.json`); Legs (L21–L24, `legs/results/r5/structure_r5.json`, `ankle_clearance.json`). Robot Lab design calls verified one by one. **Every new structural number this round is a hand calculation (no FEA), so FEA credit rules apply: mass reductions resting on hand checks ×0.5, mass additions ×1.0 (conservative), FEA-backed ×1.0.**
- **1. O17, ø35 needle straddle over ø80 CRBH seat: accepted (Robot Lab call recorded).** Actuators' needle straddle has been the credited design since R-018 (−0.153 in M1); Legs L21 drops the ø80 ring for a ø35 press-fit tongue (55 × 27). Hand checks at 10.06 kN + 192 N·m: net tension SF 9.0, shear-out 15.6, bearing 9.0, press-fit hoop 142 MPa SF 3.55, 49 MPa retained at +60 K, axial hold 21.9 kN (2.2× the 10.06 kN load), Goodman 2.74. Conflict flag closed. Condition: press-fit tongue joins the Grok Build `structure_fea.md` list (A1').
- **2. Thigh clamp retention: bonded collar + light 3 MPa clamp + Legs' internal 7075 sleeve with 2 × ø6 cross pins. Robot Lab's "internal shoulder" backup is overruled.** Reason: a machined shoulder cannot be cut into a ø50 × 1.2 mm tube without thicker stock (mass) and leaves a notch at the highest-stress section; Legs' sleeve + pins is positive, already sized, and its sleeve also stiffens the tube under the clamp. Verified (L22): bond static SF 9.4, one-screw fault 2.8, fatigue 7.3; backup alone (bond failed) pin shear SF 6.7, bearing 4.41, fatigue 2.68; clamp hoop 62.5 MPa vs friction-only 378 MPa (SF 1.06, Actuators D46, rejected). So the bond is **not** a single load path: the joint is fail-safe on the pins.
  - **Bond fatigue/inspection risk (open, accepted with conditions):** fatigue SF 7.3 rests on "20 % of lap shear" and a 0.5 knock-down, both [EST]; no DP490 fatigue, humidity or +60 K data is in the repo, and a bond cannot be inspected visually. Conditions: (a) each bonded clamp is proof-loaded at assembly to 1.5 × 8.76 kN = 13.1 kN axial, no slip; (b) witness mark across collar/tube, checked at each service interval — slip means bond failed and the pins are carrying; (c) Grok Build FEA includes the ø6 cross-pin holes (Kt in the 1.2 mm tube is unchecked by any number today); (d) DP490 datasheet (lap shear, temperature) committed by Legs.
- **3. Maintenance-free GE 12 eyes: accepted, with a life condition.** D46's G_h ≈ 3400 h is for relubricated steel/steel and is **below T9's 14 600 h**; no maintenance-free (PTFE) life figure exists in the repo. Actuators computes the PTFE-liner life from the SKF datasheet at p = 21.9 N/mm², ±4.1° swing; if < 14 600 h the eye is declared a replaceable wear part with a stated interval (T9 allows this). Mass: use the maintenance-free variant's datasheet mass (currently GE 12 E 0.016 kg carried).
- **4. M2 at 4.862 kg (+0.012 over 4.85): accepted; no safety-margin trim.** Weighted cost (0.012/66.5) × 0.15 = 0.00003 ≪ 0.01. Trims (ø5 pins −0.008, shorter collar) are not taken without FEA. M2 binding line becomes **≤ 4.87 kg** incl. bolts + bumper, funded from the Arbiter reserve.
- **5. ø35 femur tongue: −0.043 kg per leg = −0.086 both legs** (0.183/leg vs ring 0.226). Hand-checked replacement of a hand-checked ring → **×0.5 = −0.043 credited** both legs; remaining −0.043 released by A1'.
- **6. Harness 1.296 kg (vs R-018 credited 1.344): credited 1.324 kg (−0.020).** Per part: power wire 0.515 and EtherCAT/data 0.395 (committed Belden MachFlex datasheet, SILI-E/SiF g/m × v3 routed lengths) ×1.0; connectors 0.257 — distributor listings ×1.0 except JST-GH 0.5 g/pair *calculated* (was 1.2 [EST]): 80 × 0.7 g = 0.056 reduction ×0.5 → +0.028 back; sleeving 12 % [EST] 0.109 vs 0.108 already credited (no gain). Completeness runs (cameras, IMU, foot F/T, e-stop loop, tactile) are now modeled, so R-018's +0.10 allowance is retired into the model. Credited = 1.296 + 0.028 = **1.324**. O20 flex-cable choice (+0.053) is included. O20a/O20b tests stay open.
- **7. Linkage (D47): 2.326 kg both legs accepted**; eye interface +0.068/leg (datasheet + calc additions, ×1.0) and ankle 73 mm +0.0128/leg; C2b instep clearance **closed** (L23: min gap 8.5 mm rod vs tibia over −60…+40° × ±25°). C2a (RV12x4 stroke + absolute L10 at 73 mm) still open.
- **Mass reconciliation (vs ≤ 66.5 hard):**
  - R-019 credible 66.716 (= 66.976 + 0.214 − 0.553 + 0.079), which already carried +0.036 eye [EST] and +0.003 ankle lever.
  - Eye true delta +0.136 replaces +0.036 → **+0.100**; ankle +0.0256 replaces +0.003 → **+0.023**; harness **−0.020**; M2 r5: clamp sleeve/pins/adhesive +0.116 (×1.0) and tongue −0.043 (×0.5) → **+0.073**.
  - **Credible = 66.716 + 0.100 + 0.023 − 0.020 + 0.073 = 66.89 kg → 0.39 kg OVER.**
  - **Paper = 65.640 + 0.100 + 0.023 − 0.048 + 0.030 = 65.75 kg (reserve 0.75).**
  - **Why Actuators' 67.089 differs:** it starts from R-018's 66.976 and skips R-019 (net −0.260 = +0.214 − 0.553 + 0.079), double counts R-019's +0.039 eye/lever placeholders, omits Legs r5's +0.073, and takes the JST calc at full credit (−0.028): 67.089 − 0.260 − 0.039 + 0.073 + 0.028 = **66.891** ✓. Its "66.22 if A1" uses P-014's −0.868 at full credit on the r4 design; on r5 design with full FEA credit the figure is 66.89 − 0.553 − 0.043 − 0.028 = **66.27 kg** (reserve 0.23, below the 0.30 target).
- Actions:

| # | owner | action | kg / effect | deadline |
|---|---|---|---|---|
| A1' | RL Legs → Grok Build | `structure_fea.md` items 1–5 at 66.5 kg loads **plus ø35 press-fit tongue and clamp cross-pin holes** | releases −0.596 (0.553 + 0.043) | end of round 5 (unchanged) |
| A7 | RL Legs | clamp: proof-load spec 13.1 kN, witness-mark inspection, DP490 datasheet | closes bond risk | round 6 |
| A8 | RL Actuators | maintenance-free GE 12 life vs 14 600 h from SKF datasheet, or wear-part interval; datasheet mass | T9 | round 6 |
| A9 | RL Actuators | weigh or datasheet the JST-GH pair (releases −0.028); O20a/O20b test plans | −0.028 | round 6 |
| A5 | RL Actuators | C2a ankle 73 mm stroke + absolute L10 (clamp interface agreed, closed) | ankle condition | round 6 |
| A6 | RL Legs | hip stop bumper compliance < 9.5° (C2b closed) | hip condition | round 6 |
| A3 | Arbiter | covers / brain from cited catalogue parts (only remaining route to ≥ 0.30 reserve) | ×0 until cited | end of round 5 |

- Fallback (R-018) now likely triggers: even with A1' at full credit, 66.27 > 66.2. If so at end of round 5, Arbiter re-rules covers/brain/arms/hands/Torso budgets; T2 (66.5) and T5 (20 kg) are not touched.
