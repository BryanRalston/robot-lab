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
