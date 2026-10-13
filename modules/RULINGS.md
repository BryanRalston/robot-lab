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
