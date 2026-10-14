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

### R-021: A3, M3 covers and M4 brain sized from cited parts (Arbiter placeholders, R-017/R-018)
- Date: 2026-10-13
- Module(s) / proposer: Arbiter (A3, R-018 to R-020)
- Change requested: replace v3 placeholder lines covers 1.86 kg and brain 1.80 kg (`v3/analysis/v3.py` line 162) with sized stacks. Script: `modules/arbiter/a3_size.py` → `a3_size.json`.
- **M4 brain (v3 compute bay 130×200×40 mm, Jetson AGX Thor per `v3/cad/model.py`):**

| item | kg | source / quality |
|---|---|---|
| NVIDIA Jetson T5000 module (100×87×15.3 mm, TTP + heatpipe) | 0.280 | NVIDIA product sheet 900-13834-0080-000, "weight w/out packaging (approx.) 0.28 kg" (https://www.es-france.com/index.php?controller=attachment&id_attachment=17976 ; also https://download.kamami.pl/p1200075-Jetson%20Thor%20T5000%20SKU%20Setup.docx.pdf). The module datasheet DS-11945-001 gives no mass. Cited ×1.0 |
| Connect Tech Gauntlet AGX301 carrier, board only + PHY heat spreader | 0.266 | Connect Tech manual CTIM-00140 "Weight" table (https://connecttech.com/ftp/pdf/CTIM-00140-AGX301_Manual.pdf). Cited ×1.0 (alt.: Seeed reComputer J601 312 g, distributor listing) |
| Vicor DCM3623x75H26C2 48→24 V, 320 W isolated DC-DC | 0.024 | Vicor datasheet 24.0 g (https://www.vicorpower.com/documents/datasheets/DCM3623x75H26C2yzz_ds.pdf). Cited ×1.0 |
| cold plate 6061, 100×87×6 mm on TTP | 0.141 | calc, thickness [EST] |
| tray 7075, 130×200×2 mm | 0.146 | calc, thickness [EST] |
| lid PA12 MJF 1.5 mm | 0.079 | calc (HP PA12 1.01 g/cm³), thickness [EST] |
| RT / safety MCU board (EtherCAT master + e-stop) | 0.040 | [EST], basis: Nucleo-144 class board, no part chosen |
| NVMe 2280 SSD | 0.008 | [EST] |
| DCM input filter + heatsink | 0.030 | [EST] |
| standoffs, fasteners | 0.030 | [EST] |
| **paper total** | **1.044** | cited 0.570 + [EST] 0.474 |

  - Credit: saving 1.80 − 1.044 = 0.756 is split by mass share. The cited share (54.6 %, 0.413) is credited ×1.0, and the [EST] share (0.343) ×0.5. **Credited brain = 1.216 kg (−0.584). Meets the M4 ≤ 1.50 target on both paper and credible numbers.** The heat path beyond the cold plate stays in the torso thermal line (1.0 kg) and is not double counted. Open item: Thor SYS_VIN is 7–20 V, so the carrier's input range must accept the DCM output, or a 48→12 V DCM variant has to be picked (same 24 g ChiP package). Brain power stays 120 W (T5000 modes 70–130 W).
- **M3 covers:**
  - Area: convex-hull area of v3 CAD segments (`v3/cad/export/bhl_v3.glb`). Thigh 0.209, shank 0.290, upper arm 0.079, forearm 0.065 m², each ×2, for **1.285 m²**. Torso and pelvis get no cover, because the CFRP 3 mm and 7075 4 mm structural shells already form the outer skin (v3 CAD). The head keeps its PA12 shell in the head line. Hands and feet are not covered.
  - Material: HP 3D High Reusability PA 12 (MJF), density 1.01 g/cm³ ASTM D792 (https://www.shapeways.com/wp-content/uploads/2021/01/HP-MJF-PA-12-Data-sheet.pdf). Wall 1.5 mm [EST], set to the Shapeways MJF PA12 1.5 mm smooth unsupported-wall minimum (https://www.shapeways.com/materials/multi-jet-fusion-pa12).
  - Full-coverage limb skins would weigh 1.285 × 1.5e-3 × 1010 = 1.948 kg (+0.41 pads and clips = **2.36 kg, over v3's 1.86**). The design is therefore **front and lateral panels at 50 % coverage [EST]**: 0.974 kg, plus clips and fasteners 0.050 [EST], plus EPP fall pads 0.360 (v3 formula at 30 mm, carried unchanged, still [EST]) = **paper 1.384 kg**.
  - Credit: the whole saving rests on the [EST] wall and coverage, so 1.86 − 0.5 × 0.476 = **credited 1.622 kg (−0.238). This misses the M3 ≤ 1.20 target** (paper −0.18, credited −0.42).
- **Mass reconciliation (vs ≤ 66.5 hard):** credible 66.891 − 0.584 − 0.238 = **66.07 kg (reserve 0.43, MET on credible)**. Paper 65.75 − 0.756 − 0.476 = **64.52 kg (reserve 1.98)**. With A1' FEA at full credit, credible is 66.07 − 0.596 = 65.47.
- **R-018 fallback:** **not expected to trigger.** Credible 66.07 is below the 66.2 trigger and the reserve of 0.43 is at least 0.30. A1' and the other round-5 items have no further downside on this line. The trigger is re-checked at end of round 5 as written.
- Ruling: **accepted. M4 credited 1.216 kg (target met). M3 credited 1.622 kg (target missed, gap carried by reserve).** No change to T2 (66.5), T5 (20 kg) or any authority wording.
- Actions:

| # | owner | action | releases | deadline |
|---|---|---|---|---|
| A10 | Arbiter (placeholder; Torso when staffed) | covers: panel layout on CAD, measured panel areas, and a wall/rib check of the 1.5 mm panels against the T8 fall case. Cite the EPP grade density and size pads from contact patches | up to −0.24 covers, plus pad delta | round 6 |
| A11 | Arbiter (placeholder; Brain when staffed) | brain: pick the RT MCU part, confirm the carrier input voltage and DCM variant, and draw the cold plate and tray | up to −0.17 brain | round 6 |

### R-022: official mass rollup + Actuators R6 (71f3c3e: A8 eye life, A9 JST-GH, A5 ankle stroke) + Legs r6 mass (2bf99d5)
- Date: 2026-10-13. Proposers: Actuators (D52–D55, `life_r6.json`, `ankle_stroke_73.json`, `harness.json`, `mass_rollup_r6.json`); Legs r6 (L25–L27, `r5/hip_stop.json`). Arbiter checks: `arbiter/mass_rollup_official.py`, `arbiter/a5_ankle_rom.py` (+ `.json`). Targets unchanged (T2 ≤ 66.5, T5 20 kg).
- **1. One official rollup: `modules/arbiter/mass_rollup_official.json` (+ `MASS_ROLLUP_OFFICIAL.md`) is the single source of truth.** Module rollups must reconcile to it line by line, naming the line and ruling for any difference. Only the Arbiter edits it.
  - **Why 66.853 vs 66.07:** Actuators started from R-020's 66.89 and kept the **stale v3 brain 1.80 / covers 1.86 placeholders** (missing R-021's −0.584 and −0.238). R-021 predates the new real deltas A9 harness −0.038 and GE 12 C linkage +0.0002. **Both missed Legs r6's new real +0.022** (bumper + collar bolts 0.062 vs 0.04 allowance, addition ×1.0). No double counts; the JST credit (release +0.028 hold, −0.010 new) is correct.
  - Credible = 66.891 − 0.584 − 0.238 − 0.038 + 0.0002 + 0.022 = **66.054 kg, MET, reserve +0.446** (≥ 0.30). Paper = 65.75 − 0.756 − 0.476 − 0.010 + 0.0002 + 0.022 = **64.531 kg**. With A1' FEA: 65.458.
  - Note: M2 design now 4.884 vs the ≤ 4.87 line (+0.014); accepted, funded from reserve (weighted cost (0.014/66.5)×0.15 ≈ 0.00003 ≪ 0.01).
- **2. A8: GE 12 C (steel/PTFE sintered bronze) eye as a wear part, replace every 5 250 h: ACCEPTED with conditions.**
  - Math checked (walk 1.0 row): p = K·P/C = 100 × 0.778/11.4 = 6.82 N/mm²; v = 5.82e-7 × 18 × 3.05° × 63.8 min⁻¹ = 2.04e-3 m/s; G_h = 0.2 × 1 × 1400/(6.82^1.3 × 2.04e-3) = 280/(12.13 × 2.04e-3) ≈ 11 300 h ✓. Duty-weighted harmonic mean 10 612 h < 14 600 h T9. b1 0.2 at p < 25 is conservative; duty mix is [EST].
  - Interval 5 250 h = 0.49 × G_h (G_h is a mean wear life, not L10), so 2 replacements over T9; T9 allows stated-interval wear parts. Plus play inspection every 1 000 h, replace if radial play > 0.15 mm.
  - Cost check: GE 12 C listed at €9.79 ex VAT (motionparts.de), US$31.37 (sunrisebearingsfl.com, maintenance-free steel/PTFE confirmed), vs Actuators' $17.20. Bearing $10–31 + eye $25 [EST] + pin/clips $5 [EST] ≈ **$40–61 per eye**, 4 eyes/robot → **$160–245 per interval, ≤ $490 over life**. Negligible against T9 weight.
  - Access: 30 min/leg procedure accepted. **Conditions:** (a) the femur clamp-arm pin and circlip must be reachable through a removable cover panel. The Arbiter covers line keeps the thigh lateral panel tool-removable (no mass change). (b) Legs confirms tool access at the clamp in the r7 layout. (c) O23 bench wear test in the O20 rig confirms G_h before G5.
- **3. A9: harness 1.286 kg credited ×1.0 (−0.038 vs 1.324).** JST-GH 0.384 g/pair is from published distributor weights (TME; GAM 0.32 g), not calculated, so it is listing grade under R-020 §6. TME gross weights bias high (packaging share), so ±0.06 g × 80 = ±0.005 kg is conservative. No scale weigh required. Sleeving 12 % [EST] is unchanged and gains no credit.
- **4. A5: ankle RV12x4 pin-to-pin margin 2.9 mm: NOT ADEQUATE as a design margin. Ruling: limit ankle_roll mechanical range to ±18° (hard stop); rod end not shortened.**
  - Actuators' sweep covered pitch only −45…+40 (MJCF). Arbiter re-ran their rule over the contract mechanical −60…+40: margin is still 2.9 mm (B), because the governing corner is pitch +40 × roll ±25.
  - Stack against 2.9 mm (a nominal, parametric v3 layout with no assembly CAD, G2): eye length set ±0.1, 2 PTFE eyes at the 0.2 mm wear limit (≈ 0.4), screw/nut/housing/motor-envelope machining and thread engagement (≈ 4 × ±0.2 worst case 0.8), lug and lever positions (±0.2 each) → worst case ≈ 1.5–2 mm [EST]. Elastic shortening of the screw at 2.22 kN: δ = FL/EA = 2220 × 250/(71 mm² × 210 GPa) ≈ 0.04 mm (negligible). Remaining ≤ 1 mm on a model that is not CAD is too thin. Floor set: **≥ 5 mm** nominal pin-to-pin margin on parametric layouts.
  - Gait need (Legs npz, all scenarios): ankle_pitch −59.9…+25.7°, |roll| ≤ 7.8° walking/carry, ≤ 11.3° stairs, **13.8° push recovery**, and no roll at pitch > +30°.
  - Options: shorten the rod end by 3 mm → 5.9 mm, and it adds an unverified eye-on-screw part. ±22° at full dorsiflexion (D54) is not computed. **±18° everywhere → 10.9 mm (F)**, keeping 4.2° over the push peak. ±15° gives 14.6 mm but only 1.2° over the push. A coupled ±25° up to +20° pitch gives 25.6 mm, but its stop is complex. **Pick ±18°.** It is the simplest stop, covers every gait with headroom, and costs no mass. Ankle roll torque/speed needs are unchanged.
  - L10 544 000 h ≫ 14 600 h and static C0a/F 12.3 accepted as computed (not re-derived). **R-020 C2a closed with the ±18° condition.**
- Actions:

| # | owner | action | effect | deadline |
|---|---|---|---|---|
| A1' | RL Legs → Grok Build | structure FEA items 1–7 (unchanged) | releases −0.596 | queued |
| A12 | Arbiter | itemise "all other lines" (leg actuators/linkage, torso, arms, hands, head) in the official rollup | audit trail | round 7 |
| A13 | RL Actuators | re-base `mass_rollup_*` on `arbiter/mass_rollup_official.json`; ankle_stroke at ROM −60…+40 × ±18 | reconcile | round 7 |
| A14 | RL Legs | ankle_roll hard stop ±18° in MJCF/CAD; re-run push recovery with the stop; femur clamp pin tool access through the thigh panel | A5, A8(b) | round 7 |
| O23 | RL Actuators | GE 12 C bench wear test (O20 rig) | confirms 5 250 h | before G5 |

- Needs Bryan: nothing. All calls are within approved targets.

### R-023: on Legs r8 L36 structure FEA fixes (f480ed2) + Legs A14 (4f772c6): M2 5.154, A1' voided, A14 additions
- Date: 2026-10-14. Proposers: Legs (L36, `results/r8/structure_fixes_r8.json`, `r8/*.json`, `grokbuild/structure_fea_r2.md`; A14 `results/r7/a14.json`). Inputs: Grok Build 48a9da0 `STRUCTURE_FEA_REPORT.md`. Arbiter check: `arbiter/mass_rollup_official.py` (+ `.json`). Targets unchanged (T2 ≤ 66.5, T5 20 kg).
- **Verification of the FEA claims (Arbiter read of the result JSONs):**
  - Clevis: `clevis_h4_f0` 3BW+screw 549.7 MPa (SF 0.915) → `clevis_h4_f6_pad16` 147.1 MPa (SF 3.42), fall 233 → 62 ✓. Mass 0.2345 → 0.2624 = +0.028/leg ✓. h4 only; convergence not shown.
  - Clamp: `clamp_h3_f12` 182.0 → `f34` 137.6 MPa (−24 %) ✓, +0.020/leg ✓. Rev Goodman ~1.95 is **scaled, not solved** (GB h1.5 baseline 1.472 failed).
  - Femur tongue: `tongue_h4_f0` combined_fault 574.1 (SF 0.876) → `f1` 234.3 (SF 2.15); fault-only 340.0 (SF 1.48, below 1.5) ✓ as stated. +0.0275/leg ✓. Bore opening under fault **not checked**.
  - Foot collar (+0.029/leg) and tube doublers (+0.042/leg): **hand only**, no solve (box OOM). Not verified.
  - **Hip-ring artifact claim: CONFIRMED.** GB report: 912/870 MPa cases are a bonded model with a tensile bore traction carrying 192 N·m across a 13 mm bearing (not contact); the compressive 12.4 kN case is SF 2.0. The part is the ø80 CRBH ring that L21 (R-020, O17) replaced with the ø35 tongue, and it is not in the rollup. Retired; no re-run needed. Note: its compressive neck Goodman (1.21) would have failed, so the claim rests on obsolescence, not only on the artifact.
- **1. M2 5.114 kg (5.154 with bolts/bumper allowance), +0.292 both legs: ACCEPTED.** Safety fixes beat the old 4.87 sub-cap (T8 is hard; the sub-cap is not). Funded from the reserve. Weighted cost (0.292/66.5)×0.15 ≈ 0.0007 ≪ 0.01.
- **2. A1' −0.596 credit: VOID.** It was the ×0.5 hold on the r5 hand-checked reductions. GB FEA failed those parts (clevis, tongue, clamp root, foot toe, tube dent), so the reductions are not released; the fixed design replaces them. Credible M2 = 5.154 paper (fixes as additions ×1.0) **+ 0.267 hold** for the hand-only tube doublers (fallback = GB-measured full 1.9 mm wall, +0.175/leg, minus doubler 0.042/leg) = **5.421**. The hold is released when GB r2 passes the doublers. Foot-collar fallback (r50 or 4 mm) has no computed mass: unquantified risk, covered by the reserve.
- **3. A14 additions credited ×1.0:** ankle_roll stops 0.033 (both legs) + thigh pin access panels 2 × 0.0179 = 0.036 → **+0.069**. Paper geometry only; PA12-CF and fastener layout [EST]. Push re-run with the stop: roll peak 19.9° (1.9° pad/soft overtravel, 8.7 mm clearance left), CoP inside sole. R-022 A5 and A8(b) closed on paper; CAD check stays in G2.
- **Official rollup (regenerated):** paper **64.891 kg** (reserve 1.609); credible **66.125 kg, MET vs ≤ 66.5, reserve +0.375 (≥ 0.30 met)**. If GB r2 passes the tube doublers: 65.858 (reserve 0.642). If the tube fallback is needed, the hold already covers it. Fix: the rollup script now reads Actuators' `mass_rollup_r6.json` from 71f3c3e (they removed it in 2d81b29); no numbers changed.
- Actions:

| # | owner | action | effect | deadline |
|---|---|---|---|---|
| A15 | RL Legs → Grok Build | structure FEA re-check r2 (`structure_fea_r2.md` items 1–5): h-convergence; clamp at h1.5; tongue bore opening under fault (size dowel/70 MPa fit if it opens); foot collar OD; tube doubler + DP490 bond | releases the 0.267 tube hold; closes G3 structure | next GB slot |
| A16 | RL Legs | tongue fault-only SF 1.48 < 1.5: show margin at converged mesh or add the dowel | T8 | with A15 |
| A17 | RL Legs | clevis pad vs knee-tongue clearance over full knee flexion; G2 arm clocking ≥ 30° off the femur axis (L35 open check) | G2 | round 9 |
| A12 | Arbiter | itemise "all other lines" (carried) | audit trail | round 9 |

- Needs Bryan: nothing. All calls are within approved targets.

### R-024: on the v4 audit fixes — Legs 15c602d (L37–L40, +0.200) + Actuators 67b0b13 / P-018 (D59–D62, +0.138); reserve recovery plan
- Date: 2026-10-14. Responds to: Robot Lab v4 model-fidelity audit 9447a9d (`model/JOINT_AUDIT.md`: 4 BUILDABLE / **2 FAIL** / 26 PLACEHOLDER). Arbiter check: `arbiter/mass_rollup_official.py` (+ `.json`, `MASS_ROLLUP_OFFICIAL.md`). Targets unchanged (T2 ≤ 66.5, T5 20 kg). Reserve floor ≥ 0.30 credible unchanged.
- **Verification (Arbiter read of the commits):**
  - Audit FAIL 1, knee: twin-body inner trunnion bosses overlap (1257 mm³). D59 merged twin housing, −0.0013/leg. **Real function fix**, mass-neutral. ✓
  - Audit FAIL 2, ankle_roll: screw bodies tilt 1.8° out of plane at ±18° roll on sagittal-only trunnions; bottom eye misalignment 19.6° > GE 12 C α 10°. D60/D61 + L38: axial GE 12 C top eye in shank clevises, QA1 MGF12T-class 27° PTFE bottom rod end (demand 20.8°), spacer, anti-rotation key, trunnion z 410→450, instep outrigger because the lugs sit outside the 100 mm foot. **Real function fix** (the joint could not move through its ruled ±18° range). Mass justified by line items; trunnion pins retired (−0.052/leg) offset the new eyes/pins. Actuators lines are actuator parts only; Legs lines are clevis/outrigger/pin only — no double count found. ✓
  - L39 hip yaw/roll hard stops (+0.090/leg [EST]): audit listed no mechanical stops on these joints; T8/safety requires them. **Real safety fix.** Impact energies 0.07 J / 0.76 J vs bumper 1.2 J / 4 J. ✓
  - L37/D62 hip-body 0.3 mm: was a hand note, not a measurement; model measures ≥ 3.0 mm. Correction accepted; the clamp step (−0.021/leg) and boss trim (−0.021/leg) are savings. ✓
  - L40 clevis cheek rounding −0.024/leg from real dims. ✓
  - Audit rerun: 6 BUILDABLE / 0 FAIL, 0 standing clashes.
- **1. Legs 15c602d +0.200 both legs: ACCEPTED**, credited ×1.0 as an addition (additions are not discounted; hip-stop parts [EST], Legs to replace with sized parts in G2).
- **2. P-018 Actuators +0.138 both legs: ACCEPTED**, credited ×1.0. Conditions: QA1 rod end is a wear part every 4 250 h until a supplier dynamic rating or bench test (G5) — same access rule as the R-022 A8 eyes; the +0.010 head and key [EST] are replaced by catalog mass at G1.
- **Official rollup (regenerated):** paper **65.229 kg** (reserve 1.271); credible **66.463 kg — MET vs ≤ 66.5 (reserve +0.037), BELOW the 0.30 floor.**
- **3. Floor waiver (temporary):** the 0.30 floor is the Arbiter's own margin rule, not a target. Waived to ≥ 0.0 credible **until end of round 13**. No new mass may be added to the robot during the waiver without an offsetting credited cut.
- **4. Margin plan (ranked by likelihood):**

| rank | source | credible gain | likelihood | owner | deadline |
|---|---|---|---|---|---|
| 1 | Release the 0.267 tube-doubler hold if Grok Build job 6 (A15) passes | 0.267 → reserve 0.304 | likely (doublers are a stiffening add; GB measured the full-wall fallback) | RL Legs → GB | next GB slot / round 12 |
| 2 | Brain M4 [EST] parts → cited parts (cold plate, tray, lid, MCU, NVMe, filter, standoffs; now 0.474 at ×0.5) | up to 0.172 (penalty removed; more if parts lighter) | likely, catalog work only | Arbiter (A18) | round 12 |
| 3 | Covers M3 CAD panel layout (coverage/wall now [EST]; credited 1.622 vs paper 1.384) | up to 0.238 | medium — needs real panel areas | Arbiter (A19) | round 13 |
| 4 | A12 itemise "all other lines" (47.739 credible, derived) | unknown; may find credit or debit | low-medium; not quick, so not done this round (no numbers invented) | Arbiter (A12) | round 13 |
| 5 | Other modules' budgets (torso/arms/hands unstaffed placeholders) | — | last resort | Robot Lab to staff | — |

  - Expected: rank 1 alone restores 0.304; ranks 1+2 ≈ 0.48.
- **5. Contingency if job 6 fails:** the tube fallback (full 1.9 mm wall) is already inside the 0.267 hold, so credible stays 66.463 (≤ 66.5). Then ranks 2+3 must deliver ≥ 0.263 by end of round 13. If they do not, the Arbiter cuts EPP pads/cover coverage (covers line) and brain tray/lid to restore 0.30, and reports the trade.
- **Worst case:** credible 66.463 ≤ 66.5 with the tube fallback covered. Residual unquantified risk: foot-collar fallback (r50 or 4 mm) mass not computed (R-023) — A20. If it exceeds +0.037 before ranks 1–3 land, credible would exceed 66.5 and that goes to Bryan.
- Actions:

| # | owner | action | effect | deadline |
|---|---|---|---|---|
| A15 | RL Legs → Grok Build | job 6 structure re-check r2 (carried) | releases 0.267 | next GB slot |
| A18 | Arbiter | brain M4: replace [EST] lines with cited parts | up to 0.172 | round 12 |
| A19 | Arbiter | covers M3: CAD panel layout from model_v4 hulls | up to 0.238 | round 13 |
| A20 | RL Legs | compute foot-collar fallback mass (r50 / 4 mm) | closes unquantified risk | with A15 |
| A21 | RL Legs | hip yaw/roll stop brackets + bumpers sized from catalog PU parts | replaces [EST] | G2 |
| A22 | RL Actuators | QA1 MGF12T dynamic rating (supplier) or bench plan; catalog mass for head/key | T9, G1 | G5 |
| A12 | Arbiter | itemise all other lines (carried) | audit trail | round 13 |

- Needs Bryan: nothing now. Within approved targets; escalates only if A20 pushes credible over 66.5.

### R-025: on P-019 (Robot Lab head/neck own line, a88c2d8) + A11 GMSL2 input + A12 (head share) + Actuators D63 (3789f1d)
- Date: 2026-10-14. Arbiter check: `arbiter/mass_rollup_official.py` (+ `.json`). Targets, mass limit (≤ 66.5), 20 kg carry and authority wording unchanged.
- **1. Where the 0.800 comes from:** `head/BOM.md` itemises **0.810 kg** (the 0.800 in P-019 omits the 10 g pitch gravity spring; 0.810 is booked). Split: catalog 0.314 (2 × XM430-W350-R 0.082, ZED X Mini 0.150), calc 0.179 (CF shell), [EST] 0.317 (yoke 0.110, deck 0.070, bearings 0.027, DC-DC + harness + fasteners 0.100, spring 0.010).
- **2. A12 itemisation, head share (settles the credit):** "all other lines" carries the v3 basis unchanged (R-018: head cuts credited ×0). From `v3/analysis/results/v3.json`: struct `head` **1.600** (CONTRACTS §3: incl. neck structure, sensors) + neck_yaw and neck_pitch actuators (TBM2G-05008A + CSG-14-100 + drive, encoders) **2 × 0.546** = **2.692 kg**. The sim's 1.137 is not the rollup basis. No double count: the head line replaces exactly these three items, removed from the derived line (47.739 → 45.047 credible).
- **3. P-019: ACCEPTED, credited by the R-021 split rule.** Saving 2.692 − 0.810 = 1.882; cited/calc share (60.9 %) ×1.0 = 1.146, [EST] share (39.1 %) ×0.5 = 0.368. **Credited head + neck = 1.178 kg (−1.514 credible; −1.882 paper).** This is larger than the −0.337 P-019 asked for, because the basis is 2.692, not 1.137.
  - Conditions: (a) the credit holds for the P-019 scope (one ZED X Mini; head-as-balancer rejected). Any further head sensors are new mass under R-024. (b) Bus: pack is 20S, 68–84 V (R1.3), **not 48 V**. The BOM's "48→12 V" DC-DC must be an input-range part for 68–84 V (or fed from the brain DCM rail); mass stays [EST] at ×0.5 until a part is cited. (c) The neck leaves EtherCAT/Elmo for Dynamixel RS485: Brain must provide an RS485 port (AGX301 has 2× RS-232/RS-485, manual CTIM-00140) — no added mass. (d) Head harness 0.060 [EST] may overlap the M3 harness neck/head bus and camera-data runs (`actuators/results/harness.md`); kept (conservative) until Actuators reconciles. (e) Legs updates the sim neck per P-019 (request, not a ruling on Legs files).
- **4. A11, GMSL2 input on Thor:** the Gauntlet AGX301 has **no native GMSL2 connector**. Manual CTIM-00140 lists "1x 16-Lane MIPI Expansion Connector that interfaces directly to a range of MIPI CSI, GMSL2 or FPD-Link III image sensors" via CTI camera boards. Needed: **Connect Tech JCB022** (MAX9296A, GMSL2) or JCB009 (MAX96792A, GMSL3 back-compatible to GMSL2), **45 g** (CTIM-00143 datasheet), PoC to the camera, 75 × 57 mm. Booked **+0.045 kg ×1.0** in the brain area (new line). Open: ZED X Mini driver support on a CTI deserializer board (Stereolabs normally ships ZED Link capture cards) — confirm with Stereolabs/CTI before purchase; fallback is a ZED Link card, mass to be cited then.
- **5. Power (R1.3 / R-010):** the 40 W sensors line already carries head sensors (CONTRACTS §3), so the ZED's ~2 W is arguably in budget, and the v3 neck drives' 2 × 3.3 W drive overhead disappears. Booked conservatively at the full **+4.4 W [EST]**, no offset taken: 1.0 m/s 699.0 → **703.4 W ≤ 729.0 (typical), ≤ 712.8 (binned)** → 2.07 h typical / 2.03 h binned. **T7 stays MET** at the rating speed. 1.2 m/s tracked: 841.6 → 846.0 W, 1.72 h (still NOT MET, unchanged status). Minimum (unbinned 1550) pack already failed; binning requirement unchanged. Deserializer board power not in its datasheet extract; inside the 40 W sensors line [EST].
- **6. Actuators D63 (3789f1d): reviewed, no rollup change.** Top clevis fit with PTFE thrust washers and lug relief to 8.0 mm (margin 0.27 mm on 0.73 mm need; bottom misalignment ≤ 23.4° vs 27°); tine ligament SF 14 yield / 3.5 fatigue at motor-peak 2218 N per screw; instep lugs stay outboard (+0.031/leg already inside Legs 15c602d). Lug −0.002/leg not booked (conservative). **Accepted**; G2 to carry the washer stack and R3 tine fillet.
- **Official rollup (regenerated):** paper **63.392 kg** (reserve 3.108); credible **64.995 kg — MET vs ≤ 66.5, reserve 1.505 ≥ 0.30 floor** (64.728 if A15 releases the tube hold). The R-024 floor waiver is no longer drawn on; its wording is unchanged.
- Actions:

| # | owner | action | effect | deadline |
|---|---|---|---|---|
| A23 | Robot Lab (head) | cite the head [EST] parts: 68–84 V → 12 V converter, yoke, deck, bearings, spring | raises head credit by up to 0.368 | round 13 |
| A24 | Arbiter (A11) | confirm ZED X Mini on JCB022/JCB009 under JetPack for Thor, or cite ZED Link mass | A11 | round 13 |
| A25 | RL Actuators | reconcile head harness 0.060 [EST] against M3 neck/head runs | removes possible double count | round 13 |
| A26 | RL Legs | sim neck update per P-019 (mass, armature 0.0005, ctrlrange 4.1 N·m) | sim fidelity | round 13 |
| A12 | Arbiter | itemise the rest of "all other lines" (head done) | audit trail | round 13 |

- Needs Bryan: nothing. All within approved targets.

### R-026: on A23 (Robot Lab, 6e75636) — P-019 addendum, cited head parts
- Date: 2026-10-14. Arbiter check: `arbiter/mass_rollup_official.py` (+ `.json`), RECOM RP40-FR datasheet (REV 8/2020, https://recom-power.com/pdf/Powerline_DC-DC/RP40-FR.pdf). Targets, mass limit (≤ 66.5), 20 kg carry and authority wording unchanged.
- **1. BOM arithmetic checked:** catalog 2 × 0.082 + 0.150 + 0.026 + 0.005 + 0.043 = **0.388**; calc 0.179; [EST] 0.110 + 0.070 + 0.010 + 0.060 = **0.250**; total **0.817** (+0.007). Cited/calc share 0.567/0.817 = 69.4 %.
- **2. Credit (R-021/R-025 split rule, recomputed):** saving 2.692 − 0.817 = 1.875; credited 1.875 × 0.694 + 1.875 × 0.306 × 0.5 = 1.588 → **head + neck 1.104 kg credited (was 1.178; −0.074 credible)**, paper +0.007. Robot Lab's figure confirmed. **A23 ACCEPTED and CLOSED.**
- **3. Converter verified against the datasheet:** RP40-11012SFR: input 43–160 VDC (nom. 110), 12 V / 3333 mA, 90.5 % eff.; 1 s surge 170 VDC; UVLO on 43 / off 40 VDC. The 68–84 V bus and the 90 V regen clamp sit inside the continuous range (no surge reliance); UVLO is far below the 68 V pack floor. 40 W rating vs head load: servos 2 × 1.5 A = 3.0 A (36 W, 90 %). The ZED X Mini is powered by PoC from the deserializer board (Stereolabs: "Power via GMSL2 (PoC)"), so it is not on this rail; even if it were, ~1.9 W (USB spec 5 V/380 mA) adds ≈ 0.16 A → 3.16 A (95 %), still inside 3.33 A. Mass 43 g is **with heat-sink**; 32 g without.
  - Conditions: (a) the 43 g/heat-sink variant is ordered **RP40-11012SFR/P-HC** (datasheet note 4: "-HC" = premounted heat-sink); `/P` alone is the bare 32 g module. Mass stays 0.043 (conservative). (b) Datasheet note 9: the 110 V-input part needs 3 × 68 µF/200 V Rubycon BXF electrolytics + 2 × SMDJ90A TVS in series at its input for EN61000-4-4/-5; the filter is not in the BOM — Robot Lab adds it to the head harness/converter [EST] by round 13 (expected a few grams, inside the 0.060 harness [EST]; any excess is new mass under R-024). (c) Dynamixel current limits 1.5 A each are a firmware requirement in the Brain/head config, not optional.
- **4. Neck on the AGX301 RS485 (CTIM-00140): accepted, no mass.** **GMSL2 board: no double count** — JCB022/JCB009 +0.045 appears only in the brain-area line (R-025 §4); not in `head/BOM.md` or `a3_size`. The head's FAKRA cable sits in the head 0.060 [EST]; possible overlap with the M3 "head cameras data" run stays with A25.
- **Power:** no change; R-025's +4.4 W [EST] stands, T7 met at 1.0 m/s (703.4 W).
- **Official rollup (regenerated):** paper **63.399 kg** (reserve 3.101); credible **64.920 kg — MET vs ≤ 66.5, reserve 1.580 ≥ 0.30 floor** (64.653 if A15 releases the tube hold).
- Actions: A23 closed. A24, A25, A26, A12 unchanged (round 13). New: A27 Robot Lab (head) — add the RP40 input filter (note 9) and fix the part number to /P-HC in `head/BOM.md`, round 13.
- Needs Bryan: nothing. All within approved targets.

### R-027: A27 input filter booked + closed; "no 3D printing" provenance; P-020 cover set (PA12 MJF → thermoformed PC); P-021 PA12 palm → machined 7075
- Date: 2026-10-14. Inputs: Robot Lab a61995b (A27, `head/BOM.md`), 104c9ad (`design/V5_POLISH_PLAN.md`). Arbiter check: `arbiter/a28_covers_palm.py` (+ `.json`), `arbiter/mass_rollup_official.py`. Targets unchanged (T2 ≤ 66.5, T5 20 kg); no authority wording changed.
- **1. A27 booked and CLOSED.** RP40-11012SFR/P-HC specified; note-9 filter added: 3× 68 µF/200 V caps 0.0105 [EST] + 2× SMDJ90A 0.0004 catalog + carrier PCB 0.005 [EST] = **+0.0159**. Additions count in full (×1.0), so the head line goes **0.817 → 0.833 paper, 1.104 → 1.120 credited**. TVS 90 V standoff > 84 V pack max and 146 V clamp < 160 V RP40 max: checked, OK. XM430 1.5 A current limit (addr 38) is a required firmware setting. **The Rubycon 200BXF68MEFC12.5X20 is listed obsolete / not for new designs: an equivalent (68 µF, ≥ 160 V, 105 °C, radial ≤ 12.5×20 mm, ripple ≥ BXF) must be selected and cited before purchase → A28 (Robot Lab, head).**
- **2. Where "no 3D printing" comes from: a crew rule, not a Bryan rule.** It is not in CHARTER.md, TARGETS.md or CONTRACTS.md, and no Bryan statement in the repo sets it. The first appearance is Robot Lab's head study (a88c2d8, 2026-10-14 13:16, "no 3D printing; replaces PA12"), then 104c9ad ("Nothing is 3D-printed", "3D-printed: not allowed"). The only Bryan-related fact is `research/open_source_starting_points.md` / `research/NOTES.md`: "Bryan has no printer" — a sourcing note that lists print services as an option, not a ban. **This ruling treats it as a Robot Lab crew design preference.** PA12 MJF covers and the PA12 palm do not violate any Bryan rule; they are replaced below on their own merits (crew preference + score), not as a violation. If Bryan wants it as a hard rule, it must come from him.
- **3. P-020 cover set: PA12 MJF line REPLACED (not added to). Winner: thermoformed PC 1.5 mm, not CF.** Same basis as R-021: 1.285 m² limb area × 50 % coverage [EST] + EPP pads 0.360 [EST]; credit = saving vs 1.86 ×0.5.

| option | ρ (source) | wall (source) | paper kg | credited kg | Δ credited vs PA12 1.622 | fall | cost [EST] | score |
|---|---|---|---|---|---|---|---|---|
| **thermoformed PC sheet** | 1.20 g/cm³ (Palram PALSUN TDS; SABIC LEXAN ISO 1183) | 1.5 mm, heavy-gauge thermoform 1.5 mm+ (Select Plastics guide); draw ≤ 3:1 (LEXAN forming guide) | 1.567 | 1.713 | +0.091 | ductile, dents not cracks (PALSUN 130 J E50 at 3 mm) | ~$1.3k (tooling-board moulds) | **+0.0030** |
| injection-moulded PC/ABS | ~1.15 [EST] | 1.5 mm [EST] | 1.518 | 1.689 | +0.067 | tough | ~$24k (≈8 hard tools) — wrong for qty 1–2 | +0.0018 |
| CF prepreg 2×2 twill, 4 × 0.25 mm | 1.55 (Toray 3900 TDS laminate 1.51–1.54; twill sheet TDS 1.55 ±0.05; conservative vs Easy Composites XC110 1.152) | 1.0 mm = 4 plies × 0.25 mm consolidated (Easy Composites XC110/XC130 210 g) | 1.426 | 1.643 | +0.021 | edge cracking on impact | ~$3.8k (machined Al moulds, repo head basis $400/mould) | −0.0001 |
| formed 5052 Al 0.8 mm | 2.68 | 0.8 mm [EST] (Protolabs machined nominal ≥ 1.02 mm would be heavier) | 1.788 | 1.824 | +0.202 | permanent dents | ~$2.4k | −0.0037 |

  - Score = −Δcredited/66.5 × 0.15 (T2) + fall Δ [EST] × 0.13 (T8) × 0.5. All |score| < 0.01 (a near-tie under the TARGETS rule), so cost and fall toughness break it: **thermoformed PC** (cheapest, toughest, +0.091 kg). The covers are not structural; the EPP pads carry the T8 fall energy, so a ductile skin that dents is preferred over a brittle one. Robot Lab's "+0.2 to +0.5 kg" assumed ρ≈1.55 at 1.0 mm **plus** more coverage; at the same 50 % basis CF is only +0.04 paper. CF at the V5 75 % coverage would be 1.924 paper (+0.54).
  - **CF is allowed panel by panel** (e.g. the gold thigh/shin fairings for looks or stiffness) if that panel's own mass is no more than its PC version. The extra V5 coverage (hip skirt, waist bellows, ankle boots, knee caps, wider shin fairings) is **not booked here**: each needs its own sized P-number, paid from the reserve.
  - Cost figures are [EST] apart from the cited material sources; a cost spreadsheet is A30.
- **4. P-021 palm: PA12 → machined 7075, booked +0.144 kg (both hands, ×1.0).** Basis: model_v4 palm envelope 32 × 86 × 90 mm ("7075 skeleton + PA12", `model/model_v4.py` l.261). The skeleton is unchanged; the PA12 skin at 1.5 mm (0.0405 kg/hand, PA12 1.01) becomes 7075 at 1.5 mm (0.1127 kg/hand, 2.81) → **+0.072 per hand**. Wall kept at 1.5 mm (Protolabs: features ≥ 0.51 mm, nominal ≥ 1.02 mm). It's an upper bound with no openings (6061 would be +0.069/hand). The Hands owner may credit the openings back with CAD.
- **Also flagged:** the brain lid (R-021, 0.079 kg) is still "PA12 MJF 1.5 mm". Under the crew preference it should become thermoformed PC or 7075 sheet (≤ +0.02 kg as PC) → A31.
- **Official rollup (regenerated):** paper **63.742 kg** (reserve 2.758); credible **65.171 kg — MET vs ≤ 66.5, reserve 1.329 ≥ 0.30 floor** (64.904 if A15 releases the tube hold). Δ vs R-026: head +0.016, covers +0.183 paper / +0.091 credited, palm +0.144.
- Actions:

| # | owner | action | releases | deadline |
|---|---|---|---|---|
| A27 | Robot Lab (head) | — **CLOSED** (R-027) | — | — |
| A28 | Robot Lab (head) | pick and cite an in-production equivalent to the obsolete Rubycon 200BXF68 (68 µF, ≥ 160 V, 105 °C, radial ≤ 12.5×20) with its mass; update `head/BOM.md` | purchase gate | before purchase / round 13 |
| A29 | Arbiter (placeholder; Torso when staffed) + Legs (envelopes) | PC cover panel layout on the v4 CAD: measured areas replace the 50 % coverage [EST]; mould list | up to the ×0.5 credit on covers | round 13 |
| A30 | Robot Lab | cost sheet for the cover set (sheet, moulds, forming quotes), replacing [EST] costs | T10 tracking | round 13 |
| A31 | Arbiter (placeholder; Brain when staffed) | brain lid PA12 MJF → PC or 7075 sheet; book the delta | crew preference | round 13 |
| A32 | Robot Lab → Hands agent | machined 7075 palm CAD with openings; replaces the +0.144 upper bound | credit for the openings | when Hands is staffed |

- Needs Bryan: **nothing for mass.** Optional: whether "no 3D printing" should be a real project rule. Today it is only a crew preference.

## R-028 (2026-10-14) A11 / A24, raised by RL Electronics R1 (1e33c96)
- A11 CLOSED. The booked DCM3623x75H26C2 (36–75 V in, 24 V out) can't take the 68–84 V pack or feed the AGX301 (36–60 V), so it's rejected. Replaced by DCM3623TA5N53B4T00 (43–154 V in, 48 V out, 240 W). The harness compute feed is now 48 V. The 0.024 kg converter mass is credited at half until the variant's datasheet mass is cited. GMSL2 is JCB022 only. The TMS570LC4357 stays inside the 0.040 estimate (credited at half).
- A24 CLOSED WITH CONDITION. THOR-38.4.0 BSP support for ZED X and JCB022 on AGX301 is accepted. ZED X Mini isn't named, so the hardware test plan (G5) must include a first-unit stream and depth test (new item T-024). No mass change.
- New actions:
  - A33 (Actuators): add STO wiring to the harness model. A +0.14 kg estimate is held in the rollup, credited at half until itemized.
  - A34 (Electronics): get a cited source for Elmo R70/100 integration, or swap the drive.
## R-029 (2026-10-14) Cover set v5 (A29 input, ID 6cc6c3b) and P-022..P-025
- Rejected as drawn: the full set adds +1.24 kg. That fails the reserve check (1.329 kg reserve against a 0.30 kg floor).
- Approved basis for the panel layout and mould list (the trimmed set):
  - Front and outboard fairings only.
  - Arm shells deferred to Arms R2.
  - Foot top cover only.
  - CF shin and thigh fairings are allowed under R-027 because they are lighter than PC.
- P-022 (knee cap 0.116 kg), P-023 (hip skirt 0.114 kg), P-024 (waist bellows 0.055 kg) and P-025 (ankle boot 0.098 kg) are booked as part of the trimmed set.
- Booking: the trimmed delta is booked in full at 0.30 kg, the top of ID's 0.2–0.3 range, until the itemized trimmed JSON lands. With the A33 STO hold (0.07 credited), the reserve is about 0.96 kg, which is above the floor.
- Condition: ID must send the itemized trimmed cover_set JSON before round 13 closes. If the measured delta is above 0.30 kg, the arbiter re-rules.
- A29 transfers to Industrial Design.

## R-030 (2026-10-14) Trimmed cover set itemized (f651270), vents, Thermal R1 proposals
- The trimmed set is booked at +0.236 kg, counted in full as added mass. Panel areas are estimates, so CAD must measure them before G2. If they come in more than 10% higher, the arbiter re-rules. The CF shin/thigh option (+0.126 kg) is preferred, and the booking moves to that number once Legs commits the envelopes to main.
- A30 (Robot Lab): update COVER_COST.md to the A29 tool list: 12 thermoform tools, 12 trim fixtures, 1 rim strip, 1 bellows mould (or COTS), and 2 sewing patterns.
- Thermal R1 (0040976) proposals are accepted and assigned:
  - P-026 (ID): no closed PC over hip-pitch or knee. Knee cap, hip skirt and thigh panels must be louvred with at least 30% open area, or made of CF or aluminium. Thermal sets the open area and airflow path for each joint (A35). ID redesigns to that spec (A36).
  - P-027 (Legs + Materials): G10 or PEEK thermal break at every motor-to-clamp-collar joint, collar left uncovered, drives mounted off the housings. It must bring the bondline to 60 °C or below. Materials picks the material (A37). Legs books the mass (A38).
  - P-028 (Arms): carry pose keeps elbow torque at 15 N·m or below, plus a hold-time limit (A39). The 20 kg carry target must still pass.
  - P-029 (Controls): winding temperature model for each joint, with derating that trips at about 120 °C (A40).
  - P-030 (Electronics + Torso): ducted chest air for Thor at about 21 CFM (2× 40 mm blowers, about 3 W, about 40 g), chest vents and a fin stack. The brain DC-DC goes on the cold plate or in the duct. The pack stays out of the exhaust (A41). The +0.04 kg blower estimate is booked in full.
- Any of these that adds net mass, or more than 5 W, comes back to the arbiter with numbers.

## R-031 (2026-10-14) Numbering fix, Electronics R1.1, STO, Arms R2, T&R R1 fatigue, Materials R1, Torso R1
1. **Numbering.** Arms already holds P-026 and P-027 in PROPOSALS.md, so R-030's Thermal items are renumbered: P-026→P-040 (louvred or CF covers), P-027→P-041 (thermal breaks), P-028→P-042 (carry pose), P-029→P-043 (winding temp derate), P-030→P-044 (Thor ducted air). The action numbers A35–A41 stay as they are.
2. **A34 closed.** Elmo Gold Twitter R70/100 is cited (MAN-G-TWI 2.011 §4.4 Table 3, 10–95 V, 70 A continuous). Sizing stays on 49.5 A RMS. **Vicor DCM3623TA5N53B4T00** is cited at 24.0 g (datasheet Rev 1.2), so it's credited at ×1.0.
3. **P-045 regen clamp (Torso & Power, with Electronics).** The clamp is required. It switches on at 88 V and off at 86 V, the absolute bus ceiling is 92 V, and it must absorb a pulse of at least 4.5 kW / 400 J. It's booked at 0.15 kg in full until the parts are cited. The 90 V regen point is allowed only with the clamp fitted.
4. **A33 closed.** STO is booked at 0.218 kg (Actuators D66) plus 0.013 kg of connectors, 0.231 kg in full. That replaces R-028's 0.14 kg hold.
5. **P-026 (Arms ROM cut) approved.** Evidence: v4 clash-free ranges, every T5 load case sits inside the new range, and T3 DoF is unchanged. **P-027** (wrist pair ≤0.90 kg per side) gets credit only once Actuators cite the parts.
6. **Hip pitch lever fatigue (T&R 8daecff) is a hard fail and the top priority.** Fix it to a walk-load hot-spot amplitude of ≤58 MPa, with converged FEA and Goodman checked against the corrected 87 MPa Se. Try a bigger 7075 section first. Switch to steel only if the section grows by more than +0.25 kg. The mass limit is not relaxed. The fix is funded in this order:
   1. the reserve above the 0.30 kg floor
   2. the 7050-T7451 femur (approved, 0 g, better fatigue)
   3. printed small cover parts and the palm hybrid (credited at half until measured)
   4. P-027 wrist savings once cited
   
   Legs fixes P-046 to P-050:
   - P-046: redo the clevis and clamp Goodman checks at 87 MPa (the clevis is currently about 1.03; it needs ≥1.5 after the fix)
   - P-047: thicken the femur and tibia tube wall outside the doubler, or extend the sleeve, to SF ≥1.5
   - P-048: femur tongue A16 dowel plus a bore-opening check
   - P-049: FEA on the new foot collar edge
   - P-050: per-lot DP490 bond coupon test, added to G5
7. **3D printing (Bryan, in my chat 2026-10-14: "I dont see why we would ban it?")** is allowed when strength, heat and wear analysis supports it. R-027 §2 and A31 are reopened, so the brain lid may be printed if it passes those checks.
8. **Galvanic isolation** of CF and Ti from 7075 is required at every joint (Materials).
9. **A22.** Actuators to cite a rated replacement for the QA1.
10. **Torso R1.**
   - **O-T5:** cutting idle power is allowed. Re-rating the 4 h mixed-work duty changes an approved target, so it needs Bryan's own words, and 2.92 h is tracked as failing until then. 20S6P is not approved.
   - **O-T2:** the waist swap to TBM2G-08508A + CSG-25-100 (+0.19 kg in full) is approved once the torque margin is cited.
   - **O-T3:** a FET-only disconnect is not accepted without a written single-fault safety case. The contactor stays until that case exists.
11. **A12 (arbiter).** The official rollup will be recomputed with R-028 to R-031. The credible reserve in MASS_ROLLUP_OFFICIAL (0.037 vs 1.329) disagrees with itself and has to be reconciled. Until that's done, no new mass credit goes to anyone.

## R-032 (2026-10-14) A41 Thor cooling (Electronics f4e839c)
- P-044 basis corrected. Two Delta 40 mm blowers give only 6 CFM, short of the 24.3 CFM needed at a 10 K rise.
- Accepted: one Sunon PF40281B1-000U-S99 (cited 21.9 CFM min, 42 g). Booked at 0.042 kg (replaces the 0.04 estimate).
- Power: the R-030 5 W cap is raised for this item only. 6.12 W rated is counted in full in T7 runtime. The fan-law figure of about 3.7 W is not credited until J-T2 CFD and a duct flow measurement confirm it.
- The heat-pipe alternative is not directed.
- Placement: DCM on the Thor cold plate, with the pack sealed from the exhaust.
- Harness/STO: Actuators' 1.4959 kg harness (STO included) is booked. The separate STO 0.231 booking in R-031 §4 is void.

## R-033 (2026-10-14) Pack disconnect, clamp, OV trip (Electronics 318818f / a095c0c)
- Pack disconnect: approved as a diverse disconnect (contactor plus semiconductor).
  - TE LEV100A4ANG contactor: 0.20 kg. This is an estimate, but it's added mass, so it's booked in full.
  - HS50 47R precharge resistor: 0.032 kg, from the datasheet.
  - Precharge FET: inside that total.
  - Booked at +0.232 kg under R-024 unless it's already in the rollup. A cited contactor mass is due before G1.
- P-045 clamp: the HS100 1R5 resistor is accepted.
  - The booking stays at 0.15 kg until the parts are fully cited.
  - Charge-limit rule: ≤4.15 V per cell, with the BMS accepting regen at any state of charge. Adopted.
  - O-T8: the pulse-overload curve must be read before G3.
- O-T9 cell-fault sequence (immediate STO, clamp powered from the drive-side bus, latched restart): accepted.
- New G5 test items:
  - T-025: read WI[35] on the first bench drive. If it's below 91 V, P-045 thresholds are re-planned with Torso & Power.
  - T-026: measured clamp pulse test at 4.5 kW / 400 J.
- No 24 V logic supply is needed (Elmo S-variant). No mass change.

## R-034 (2026-10-14) Knee thermal fix D69 (f205f7b), funding order
- **Approved.** The current knee goes past 120 °C in 7–8.5 minutes, which is a hard fail. The D69 fix (twin TBM2G-08513D plus a heat path into the shank) holds 87–91 °C for 60 minutes at 1.2 m/s and 35 °C. It is booked at +0.47 kg in full.
- **Budget:** credible weight is 65.809 + 0.232 (R-033) + 0.47 = 66.511 kg. That is 0.011 kg over the 66.5 kg limit **until P-027 (wrist, −1.371) is credited**. With P-027 it is 65.140 kg, which leaves a 1.36 kg reserve.
- P-027's cross-check against Arms R2 is now **blocking**. If it hasn't closed by the end of round 13, the arbiter will re-rule.
- **Funding queue after P-027:**
  1. The hip lever fix, capped at +0.25 kg before switching to steel.
  2. The torso overrun. It gets no credit or booking until it's itemized. It must come in at **≤0.80 kg net** to keep the 0.30 kg floor. Torso should go after the lighter pre-charge and the ±0.2 kg estimates first.
- **Repo:** stash@{0} was dropped with Actuators' OK. It's backed up at refs/backup/stash-actuators-d59-d62. A32 moves to Arms & Hands.

## R-035 (2026-10-14) P-027 credit, torso line, arm fit, hand power
- **P-027 closed (Arms 7f71f86).** The credit is −1.332 kg, cited ×1.0. D65 left out the encoders. Credible mass is 65.179 kg, reserve 1.321 kg.
- **P-042 carry pose accepted** (sp −60 / el −110, elbow ≤13.96 N·m, 20 kg carry passes). Arms owns the hold-time limit.
- **Torso line (8c26b7f).** Booked at 5.026 kg. That's Torso's 5.024 itemization with the duct fan at the cited 0.042 Sunon (R-032). The separate P-045 clamp (0.150), R-033 disconnect (0.232) and Thor fan (0.042) bookings move into this line, so nothing is counted twice. Net new mass is +0.202 kg, which gives a credible total of about 65.381 kg and a reserve of about 1.12 kg.
  - All structure is estimated, so it's booked in full and has to be confirmed by CAD before G2.
  - If O-T8 fails, the fallback of 2× HS100 0R75 (+0.09 kg) is pre-approved.
- **Remaining queue:** the hip lever fix (≤0.25 kg before steel), then P-040, P-041 and P-046 to P-050 once each is sized.
- **O-A3 forearm fit.** Don't enlarge the 66×177 mm forearm envelope. Move the hand board out of the forearm, into the upper arm or the torso shoulder bay next to the drives. Arms leads, with Actuators and ID, and must show a clash check and wire routing through the wrist ROM (A42).
- **T4 hand close ≤1 s under load.** The 40 W continuous hand cap stays. A peak of up to 80 W for ≤1 s is allowed if Electronics confirms the supply, Thermal confirms the duty, and Arms shows by sim that T4 passes (A43). T4 stays at risk until then.

## R-036 (2026-10-14) Charge cap amended (Torso 8c26b7f §15, Electronics agrees)
- The R-033 4.15 V/cell cap is withdrawn because it breaks the 2 h walk at 1.0 m/s (1.89–1.94 h). The new charge voltage is 4.20 V/cell.
- Hard requirements:
  - The BMS accepts regen pulses at any SoC. This becomes a G5 test item, T-027.
  - Cell OV sits just above 4.20 V. The exact value needs a Molicel citation before G1.
  - The P-045 clamp must absorb the full regen energy in the top-of-charge window even if the BMS refuses it. Electronics verifies this at the O-T8 pulse rating.
- Runtime: the 2 h at 1.0 m/s passes with screened cells, but only by +1.0 W, so it's flagged thin. Any new continuous load above 1 W comes back to the arbiter with a runtime check.
- 1.2 m/s still fails (1.65 h) and stays tracked as failing.
- The mixed-duty figure (4.14 h) depends on which duty definition is used. That's still open with Bryan (O-T5), so it isn't counted as a pass yet.

## R-037 (2026-10-14) Palm CAD, torso R1.4, regen check, hand PSU
- **Palm (A32/P-021, dd5f70f), accepted.** Measured on the same skin-only basis as the R-027 booking (0.0525 vs 0.1127 kg/hand). Mass is taken from CAD geometry, so it's credited ×1.0: −0.120 kg for both hands. A32 is closed. The hybrid skins aren't needed.
- **Wrist ROM conflict.** The wrist roll fork against the palm limits pitch to ±40 and yaw to ±25. P-026 is ±60/±30. Arms resolves this in A42: either fix the fork clash, or file an amendment showing every T5 load case and task pose fits within the reduced range. G2 is blocked until one of those lands.
- **Torso R1.4 (1dd529b), accepted.**
  - Contactor cited at 190 g, so the torso line becomes 5.016 kg (−0.010).
  - The BQ77216 independent OV channel plus the S32K344 host adds +0.26 W. The walk margin is now +0.74 W, still under the 1 W rule.
  - Molicel's written confirmation of the 4.25 V OV threshold is still due before G1.
  - Cell screening at ≥4400 mAh stays as a supplier requirement.
- **Regen check (Electronics 605cb1a), accepted.** The booked HS100 1R5 absorbs the full top-of-charge window even when the BMS refuses regen. O-T8 (400 J fault pulse) is still due before G3. Stair-descent regen gets checked against measured traces in G5 (T-028).
- **A43 hand PSU.** The RP40 can't burst to 80 W. The RP100H-11024SRW is accepted in principle. Its mass is booked in full at the chosen variant once Arms picks it. Until then, +0.228 kg is held, because that's the upper bound.
- **Net this ruling:** −0.120 − 0.010 + 0.228 hold = +0.098 kg. Credible total is about 65.48 kg, with a reserve of about 1.02 kg.

## R-038 (2026-10-14) Thermal A43 answer (c8ce472), knee spreader
- **Hand power.** The R-035 80 W condition is unmet on the RP40. The lightest option that meets ≥80 W peak wins: 2× RP40 per hand (+0.086 kg for both hands) or the RP100H. The R-037 hold drops from 0.228 to 0.086 kg once Arms and Electronics confirm the 2× RP40 burst. Per-motor current caps and the ≤52 W / ≤1 s / 5 s duty apply until then. T4 is still at risk.
- **Shoulder caps.** The corrected shoulder caps are adopted (10 min cap only up to 62 N·m).
- **Knee spreader.** The finned shank spreader adds +0.09 kg per knee, booked +0.18 kg in full unless Actuators shows it's already inside D69's +0.47. Credible weight is about 65.66 kg, leaving about 0.84 kg of reserve.

## R-039 (2026-10-14) Mass recount; D70/D72 wrist; D71 shoulder bearing
- **The knee D69 stays provisionally booked at +0.65 kg** (R-034 +0.47 plus R-038 +0.18, so there's no new delta). It can be released down once A40 is re-run against the planned torque (71–76 N·m RMS). No knee hardware gets frozen before that.
- **Booked in full:**
  - Legs R-031 fatigue fixes: +0.33 (the hip lever slab is +0.09, so no steel is needed)
  - P-041 thermal breaks: +0.02
  - D70 wrist: −0.425, with housing estimated, so this saving counts at half for the estimated share until CAD confirms it
  - D72 leads: +0.488, which takes the harness to 1.984 kg, inside the 2.00 kg contract
  - Treated conservatively, the arms net comes to +0.063 and is booked at +0.10.
- **D71 shoulder-pitch bearing: CRBH 7013 A (+0.10 kg) is adopted.** CRBH 8016 A (+0.82) doesn't fit the budget. The 6013 is rejected because its radial safety factor is 0.81.
  - The 7013 has a 1.00 radial safety factor on an estimated roller size, which is the minimum. So:
    - (a) Actuators must cite the roller dimensions before G3.
    - (b) Controls must show a side-fall strategy that brings the shoulder load to ≤550 N·m (A44), which gives a radial safety factor of at least 1.25.
    - (c) If A40 or the hand-power hold frees ≥0.6 kg, the upgrade to 8016 is pre-approved.
- **Recount:** the R-038 total of about 65.66, plus 0.33, 0.02, 0.10 and 0.10, gives about **66.21 kg credible**. That leaves a reserve of about 0.29, just under the 0.30 floor.
  - Releasing the hand-PSU hold to 2× RP40 (−0.142) brings it to about 66.07, with a reserve of about 0.43.
  - So **A43 (confirm the 2× RP40 burst) is now blocking**, and so is the A40 knee re-run.
  - No new additions are booked until one of them lands.
- The palm credit of −0.120 is already in (R-037). The palm_7075 import is fixed (dd5f70f).

## R-040 (2026-10-14) Cover set rerun on final Legs envelopes (ID e2ad740)
- P-022 knee cap re-ruled. It's accepted at 0.139 kg, which trips the R-030 10% trigger but is justified because the shin fairing is deleted. P-023 is 0.120, P-024 is 0.055 and P-025 is 0.098.
- The set rebooks to −0.124 kg against the booking (PC thigh basis). All figures are estimates (measured:false), so under the credit rules the saving counts at half: −0.062 kg credited. The CF-thigh figure (−0.184) gets no extra credit until it's chosen and measured.
- Full credit follows the bryan-PC CAD measurement, and anything more than 10% over on any line gets re-ruled.
- Recount: the credible total is about 66.15 kg and the reserve is about 0.35, back above the 0.30 floor. A43 and A40 still stand as the next releases. The R-039 freeze on new additions lifts for additions of 0.05 kg or less. Anything larger comes back to the arbiter.
- Tooling is down to 8 PC tools, with the first set costing about $12.5k. Robot Lab updates COVER_COST.md (A30).

## R-041 (2026-10-14) A43 closed: hand supplies (Electronics 413d80f, Thermal d4cca06)
- 2× RP40-11024SFR per hand is approved. The two rails are independent and are never paralleled.
- Thermal's four conditions are binding:
  - Strap each RP40 to the Al shoulder bulkhead through a ≤1 mm, ≥3 W/mK pad. This is preferred because it adds no mass. A separate 6061 bracket only if the bulkhead can't take it, and that mass comes back here.
  - Vent the bay ≥25 cm² in and ≥25 cm² out, out of the Thor exhaust.
  - Add a bracket temperature sensor: derate at 90 °C, shut off at 100 °C.
  - Put a bench thermocouple on the case. This is G5 item T-029.
- Drop the clip heatsinks. The −0.044 kg is an estimated saving, so it's credited at half (−0.022).
- Mass:
  - The R-039 hold drops from 0.228 to 0.146 (0.086 supplies + 0.060 O-E11 filters, booked in full unless Arms shows they're already counted).
  - Net with the heatsink drop is −0.104 kg.
  - Credible total is about 66.05 kg, with a reserve of about 0.45 kg.
- J-T2 chest CFD has to include the shoulder bays. T4 moves from at-risk to pending sim (A43 sim part, Arms).
