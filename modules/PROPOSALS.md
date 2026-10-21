# PROPOSALS.md
Any change to CONTRACTS.md or TARGETS.md, or to another module's files, starts here. Append; never edit someone else's entry (add a comment line instead). IDs: P-NNN, sequential.

## Template
```
### P-NNN: <short title>
- Date: YYYY-MM-DD
- Module / proposer: <module> / <agent>
- Affected owners: <modules>
- Change: <exact contract/target line, old → new>
- Impact on contracts: <mass Δ kg, power Δ W, envelope, mounting, bus, torque/speed>
- Impact on targets: <T# and Δ, with weights>
- Evidence: <check script + result file, datasheet URL, sim log; mark [EST] for estimates>
- Affected owner response: <agree / disagree + reason>  (date)
- Status: open | agreed | disputed → R-NNN | withdrawn
```

## Proposals

### P-001: Leg joint torque requirements from gait inverse dynamics (replace v2 mass-scaled values)
- Date: 2026-10-13
- Module / proposer: Legs / RL Legs
- Affected owners: Actuators (selection, mass, thermal), Arbiter (T5/T6 trade)
- Change (CONTRACTS §1a "need peak N·m" for leg rows, need = 1.5 × gait-ID envelope peak, per the existing margin rule): hip_yaw 24.0 → 86; hip_roll 122.1 → 184; hip_pitch 114.8 → 398; knee 231.9 → 266; ankle_pitch 153.2 → 359; ankle_roll 57.5 → 61. Also add a continuous (RMS) torque line for thermal sizing (envelope RMS, one side): hip_yaw 16, hip_roll 50, hip_pitch 100, knee 77, ankle_pitch 55, ankle_roll 17 N·m.
- Governing case: 20 kg carry while walking at 1.2 m/s, for hip_yaw, hip_roll, hip_pitch, knee and ankle_pitch peaks. Without the carry, walk 1.2 m/s alone gives peaks 40 / 96 / 203 / 154 / 203 / 26 N·m (→ needs 60 / 144 / 305 / 231 / 305 / 39). Walk 0.8 m/s gives 34 / 93 / 134 / 131 / 183 / 28.
- Impact on contracts: v3 available peak torque (36 / 167 / 167 / 238 / 284 / 163) fails the proposed need at hip_yaw, hip_roll, hip_pitch, knee and ankle_pitch. hip_yaw (57 > 36) and hip_pitch (265 > 167) fail even without margin. Actuator mass and copper loss will rise. The size is for Actuators to quantify; Legs does not choose selections.
- Impact on targets: T6 (1.2 m/s) and T5 (20 kg carry at walking speed) as written drive these numbers. If the Arbiter limits T5 to slower carry speed, the carry case must be re-run (not done; no number claimed). T2 mass risk via the actuators.
- Evidence: `modules/legs/scenarios.py`, `envelope.py`; `modules/legs/results/requirements.md`, `envelope.json`; plots in `modules/legs/plots/`. Caveats in `modules/legs/README.md` (one gait family: bent-knee ZMP, no arm swing; base-wrench residual p99 ≤ 53 N).
- Affected owner response: **Actuators: agree for the walk/stairs/push/sit cases; carry treated as stretch** (2026-10-13). Sized to need = 1.5 × max(walk 0.8–1.2, stairs, push, sit): hip_yaw 66, hip_roll 177, hip_pitch 331, knee 231, ankle_pitch 305, ankle_roll 61 N·m, with RMS 14/45/86/72/44/7 N·m for thermal. All pass with the selections in P-005. The carry-governed values (86/184/398/266/359) are not adopted until T5 is ruled. Carry torque margin on the selections is 1.22–1.67× (`modules/actuators/results/sizing.md`). Mass consequence: robot 67.6 kg > 65 kg (see P-005).
- Status: agreed (amended) → R-004 (Arbiter, 2026-10-13)

### P-002: Leg joint speed requirements from gait inverse dynamics
- Date: 2026-10-13
- Module / proposer: Legs / RL Legs
- Affected owners: Actuators
- Change (CONTRACTS §1a "need speed rad/s (at 30 % torque)", gait value = max ω while |τ| ≥ 30 % of peak, envelope): hip_pitch 4 → 8.1 (walk 1.2); knee 8 → 13.3 (stairs 18 cm); ankle_pitch 6 → 6.9 (stairs; peak ω 9.4). hip_yaw (3), hip_roll (3) and ankle_roll (4) stay unchanged: the sim gives ≤ 1.2 rad/s, but turning and side-stepping were not simulated.
- Impact on contracts: v3 available speed fails at hip_pitch (4.9 < 8.1) and knee (12.1 < 13.3). Ankle_pitch passes (10.1).
- Impact on targets: T6. Hip-pitch speed scales with walking speed (5.1 rad/s at 0.8 m/s, 6.6 at 1.0, 8.1 at 1.2).
- Evidence: as P-001.
- Affected owner response: **Actuators: agree** (2026-10-13). hip_pitch 8.1, knee 13.3, ankle_pitch 6.9 rad/s adopted. The v3 knee could not meet 13.3 rad/s even in principle: it needs 11 646 rpm, above TBM2G Nmax 8000. Meeting these speeds drives the bus change to 20S and the knee lever change to 40 mm (P-005).
- Status: agreed → R-005 (Arbiter, 2026-10-13)

### P-003: Leg range of motion: ankle dorsiflexion and hip flexion
- Date: 2026-10-13
- Module / proposer: Legs / RL Legs
- Affected owners: Legs (own geometry), Actuators (ankle screw stroke, knee/ankle linkage)
- Change (CONTRACTS §2 "Range of motion"): ankle_pitch −45…40° → at least −60…40°. The gait used −56° at 1.2 m/s and −60° on stairs, where it hit the IK limit, so the real need may be larger. hip_pitch −105…40° → at least −120…40° (sit-to-stand from a 0.46 m seat hit −120° at the IK limit). Alternative to a larger ankle stroke: a passive or active toe joint. That alternative is not evaluated.
- Impact on contracts: ankle roller-screw stroke and pin-to-pin length (§1b, `cad/stroke.py`) must be re-checked by Actuators. Hip clash check by Legs.
- Impact on targets: T6, T5 (stairs and sit-to-stand capability).
- Evidence: `modules/legs/results/<scenario>.json` → metrics.*.qmin_deg; README "Range of motion used".
- Affected owner response: **Actuators: noted, partial** (2026-10-13). Ankle stroke and the hip_pitch twin screw (new in P-005) both need a linkage geometry study with Legs. No stroke number is claimed yet (open O1 in `modules/actuators/results/DECISIONS.md`).
- Status: agreed with conditions → R-006 (Arbiter, 2026-10-13)

### P-004: Walking mechanical power and the T6 verification status (information for Arbiter / Torso)
- Date: 2026-10-13
- Module / proposer: Legs / RL Legs
- Affected owners: Arbiter, Torso (battery, placeholder)
- Change (CONTRACTS §0 walking power budget, mech line 244 W [EST, CoT 0.25]): replace with the gait-ID value. Both legs, mean positive mechanical power: 426 W at 1.2 m/s, 303 W at 1.0 m/s, 196 W at 0.8 m/s, 434 W with the 20 kg carry. Peak summed leg power is 1016 W at 1.2 m/s and 1216 W with the carry, which bears on pack peak current (open Q3). No regeneration credit is assumed.
- Impact on targets: T7 (runtime ≥ 2 h) is at risk at 1.2 m/s for this gait. Runtime must be recomputed with motor/drive efficiency (not done here). T6: forward sim on v3 actuator limits walks the full plan at 0.8 m/s (16 steps, 5.1 m), falls after 14 steps at 1.0 m/s, and after about 10 steps at 1.2 m/s, even with 2× torque limits. **1.2 m/s is not yet demonstrated.**
- Evidence: `modules/legs/fsim.py`, `modules/legs/results/fsim/*.json`, power from `results/*.npz` (README).
- Affected owner response: **Actuators: agree the gap is real; numbers below** (2026-10-13). Electrical model (`modules/actuators/size.py`) built from the gait series with the P-005 actuators, drive η 0.98 [EST], CSG η 0.75, screw η 0.85, plus 254 W for the rest of the robot. Totals at 1.2 m/s: 772 W with no regen → 1.89 h on 1620 Wh (20S5P); 576 W with shared-bus netting → 2.53 h. At 1.0 m/s: 658 / 512 W → 2.22 / 2.85 h. 2 h at 1.2 m/s with no regen credit needs 1716 Wh. Peak electrical: both legs 1.61 kW (walk 1.2), 2.64 kW (stairs), 1.99 kW (carry); per limb 2.25 kW; per joint hip_pitch 1.33, knee 1.09, ankle_pitch 0.99 kW. Proposed pack limits: 60 A continuous, 100 A for 2 s, fuse 125 A (20 A per cell at 5P vs a 45 A rating). Recommendation to the Arbiter: T7 is met at 1.0 m/s outright; at 1.2 m/s only with bus netting (evidence ×0.5 until a drive/bus sim or test).
- Status: agreed → R-002, R-007 (Arbiter, 2026-10-13)

### P-005: Leg actuator family, 20S bus, Gold Twitter drives, EtherCAT (actuator re-size to P-001/P-002)
- Date: 2026-10-13
- Module / proposer: Actuators / RL Actuators
- Affected owners: Legs (hip_pitch twin-screw geometry, knee lever 58.5 → 40 mm, mass), Torso placeholder (battery 20S5P, BMS), Brain placeholder (EtherCAT master), Arbiter (T2, T7)
- Change:
  - CONTRACTS §0 DC bus: 13S 44.2…54.6 V → 20S 68.0…84.0 V (Molicel P45B 20S5P, 100 cells, 1620 Wh).
  - §0 Drive: Everest XCR → Elmo Gold Twitter R70/100 (legs) / R50/100 (others), EtherCAT, 49.5 / 35.3 A rms continuous, 95 V max, 22.2 g.
  - §0 Field bus: TBD → EtherCAT, 1 kHz DC-synchronised, one line per limb.
  - §0 Walking power budget: 622 W → 772 W at 1.2 m/s with no regen (576 W with bus netting).
  - §1a leg rows: hip_yaw TBM2G-06008A + CSG-17-100, 70 N·m, 1.11 kg. hip_roll TBM2G-08508A + CSG-25-100, 204 N·m, 1.56 kg. hip_pitch 2 × TBM2G-07613D + 2 × RV12x4 at 50 mm, 350 N·m worst-angle, 12.2 rad/s, 2.37 kg. knee 2 × TBM2G-07613D + 2 × RV12x4 at 40 mm, 258 N·m worst-angle, 15.2 rad/s, 2.37 kg. ankle_pitch/roll 2 × TBM2G-06013D + 2 × RV12x4 at 70/40 mm, 311/177 N·m, 1.89 kg. Needs per P-001 (walk/stairs) and P-002.
  - §1d: peak electrical per joint/limb as in the P-004 response. Pack limit 60 A continuous, 100 A for 2 s.
- Impact on contracts: leg actuator mass 15.36 → 18.60 kg (+3.24, incl. 1.30 [EST] linkage). Non-leg drives −0.22 kg. Battery +0.79 kg. **Robot 63.79 → 67.60 kg, over the 65 kg limit by 2.6 kg.** Leg copper at RMS: 184 W (both legs). Envelope: twin-screw units 82 × 101 mm motor/nut housing [v3 model EST]; hip_pitch moves from a rotary at the hip to a pelvis–thigh screw pair.
- Impact on targets: T6 is enabled actuator-side (1.2 m/s envelope met with ≥ 50 % speed margin). T7: 1.89–2.53 h at 1.2 m/s, 2.22–2.85 h at 1.0 m/s. **T2 is violated (hard).** The Arbiter must choose among: margin 1.3 (−0.52 kg); CAD check of the linkage allowance (up to −1.3 kg); structure/harness allowance (v3 CAD solids 56.3 kg vs 63.8 rollup).
- Evidence: `modules/actuators/size.py`, `results/sizing.md`, `results/sizing.json`, `results/sizing_m1.3.json`, `results/DECISIONS.md` (D1–D11); `media/progress/2026-10-13_actuators_torque_speed.png`. Datasheets: Kollmorgen TBM2G manual (v3 parts.py), Harmonic Drive CSG-2A rating table (harmonicdrive.net CSG-32-50-2A-GR, CSG-40-50-2A-GR), Rollvis RV tables, Elmo Gold Twitter (elmomc.com/product/gold-twitter).
- Affected owner response:
- Status: agreed with conditions → R-001, R-008 (Arbiter, 2026-10-13)

### P-006: Round-2 actuator updates: knee screw/lever, CAD masses, steady-state walking power
- Date: 2026-10-13
- Module / proposer: Actuators / RL Actuators
- Affected owners: Legs (knee lever r 58.5 → 47.5 mm, hip_pitch lever on the thigh, gait re-run at final mass), Arbiter (R1.1 mass, R1.3 power), Torso placeholder (BMS regen limit)
- Change:
  - CONTRACTS R1.2 knee: 2 × TBM2G-07613D + RV12x4 at 40 mm → 2 × TBM2G-07613D + **RV12x5 at 47.5 mm**. 345 N·m nominal (245 worst-angle), 16.0 rad/s, 7565 rpm at 13.3 rad/s (R-005 met).
  - R1.2 max mass per side: hip_yaw 1.02, hip_roll 1.46, hip_pitch 2.15, knee 1.98, ankle 1.78 kg.
  - R1.1 leg actuators both legs: 18.60 → **16.79 kg** (≤ 17.30 target met). Housing CAD −1.11 kg, linkage CAD 0.61 kg vs 1.30 [EST].
  - R1.3 walking power at 1.2 m/s, steady state (2–7 s of walk_1p2): 942 W no regen / **667 W with shared bus + 30 A BMS regen charge → 2.19 h** on 1620 Wh × 0.9 (2.17 h at end of discharge). This replaces 772 / 674 W, which averaged in the standing start and stop.
  - R1.3 add: BMS regen-charge limit 30 A, brake chopper, clamp ≤ 90 V.
- Impact on contracts: robot 67.60 → 65.79 kg (64.49 kg once Legs −0.50 and Torso −0.80 per R-001 are delivered). T7 passes only with regen (9 % margin) and fails without (1.55 h).
- Evidence: `modules/actuators/cad_mass.py` → `results/cad_mass.json` + `cad/*.step` (CadQuery mass properties, ×1.0); `regen_sim.py` → `results/regen_sim.json`, `regen_sim_eod.json` (time-domain bus sim, ×1.0 requested for R-002 full credit); `size.py` → `results/sizing.json`; datasheets in `modules/actuators/datasheets/` (SOURCES.md); `media/progress/2026-10-13_actuators_r2_regen_mass.png`; `results/DECISIONS.md` D12–D17.
- Affected owner response:
- Status: agreed with conditions → R-009 (Arbiter, 2026-10-13). Knee/CAD mass accepted; regen credit ×0.5 → 804.5 W / 1.81 h (T7 NOT MET) until bench evidence.

### P-007: Walking power with iron loss, 1.0 m/s fallback and regen sensitivity (input to the R-009 T6/T7 re-rule)
- Date: 2026-10-13
- Module / proposer: Actuators / RL Actuators
- Affected owners: Arbiter (T6/T7), Legs (forward-sim trace export), Torso placeholder (pack usable %)
- Change: CONTRACTS R1.3 steady walking power with motor iron loss (D18, D19):
  - 1.2 m/s: 942/667 → **964 W no regen / 842 W half credit / 719 W full**.
  - Add 1.0 m/s: **783 / 699 / 615 W → 1.86 / 2.09 / 2.37 h** on 1620 Wh × 0.9.
  - Proposed T7 rating: 2 h at 1.0 m/s (passes at R-009 half credit); 1.2 m/s rated at 1.73 h (half credit) until the bench (BENCH_TEST_PLAN.md) shows ≥ 235 W realised regen.
  - Proposed restatement of the R-009 pass condition in absolute terms: steady P ≤ 729 W. With iron loss, 77 % retention is no longer sufficient; 96 % is needed.
- Impact on contracts: no mass change; power line as above.
- Impact on targets: T7 met at 1.0 m/s (half credit); T6 1.2 m/s remains a capability without the 2 h rating unless bench-proven.
- Evidence: `modules/actuators/iron_loss.py`, `regen_core.py`, `regen_sim.py` → `results/regen_sim.json`; `regen_sweep.py` → `results/regen_sweep_walk_1p2.json`, `results/regen_sweep_walk_1p0.json` (6561 corners each; retention minimum 0.62 / 0.59); `results/BENCH_TEST_PLAN.md`; `media/progress/2026-10-13_actuators_r3_regen_sweep.png`; DECISIONS D18–D24.
- Affected owner response:
- Status: accepted with conditions → R-010 (Arbiter, 2026-10-13). Absolute pass line ≤ usable Wh/2 h; 2 h rated at 1.0 m/s (deviation, 1.2 m/s tracked at 1.73 h); 92 % usable rejected; cell binning ≥ 4400 mAh required.

### P-008: Legs round 2: 65 kg requirement table update, ankle-pitch carry margin, ankle loaded ROM
- Owner: Legs. Date: 2026-10-13.
- Change 1, requirement table at 65 kg (R-001 item 7).
  - Basis: 1.5 × max non-carry peak over walk 0.8/1.0/1.2 (reference plan), stairs 18 cm, push, sit-to-stand.
  - Needs: hip_yaw 66 (R-004: 66), hip_roll 180 (177), hip_pitch 334 (331), knee 235 (231), ankle_pitch 309 (305), ankle_roll 62 (61) N·m.
  - All fit R1.2 avail (70/204/350/258/311/177), but ankle_pitch has only 2 N·m of headroom.
- Change 2, carry check.
  - 20 kg carry peaks (max of the two carry plans): ankle_pitch 283 N·m. avail/carry = 1.10, below a 1.2 margin.
  - Hip_pitch 276 (1.27), knee 180 (1.43), hip_yaw 56 (1.26).
  - Proposal: either restrict carry gait to ≤ 1.0 m/s, or let Actuators review ankle_pitch. No selection change is made by Legs.
- Change 3, ankle ROM need.
  - −60° → −50° loaded dorsiflexion. Swing is unconstrained.
  - Stance minimum is −48° in walk_1p2_r2 and −36 to −42° in stairs. The −74° on stairs is a swing artefact of holding the swing foot flat (DECISIONS L5).
- Note: the longer-step r2 gait (arm swing + pelvis yaw) raises hip_pitch to 282, knee to 201 and ankle to 243 N·m with no benefit to hip yaw. It is not adopted (L3).
- Evidence:
  - modules/legs/results/r2/requirements.md, envelope.json, run65.log, stairs_var/
  - plots/r2/envelope_vs_contract.png
- Status: accepted with conditions → R-011. Needs accepted; carry speed 0.8 m/s per R-003 (not 1.0) pending re-run; ankle lever 77 mm study ordered; ankle loaded −50°, mechanical −60°.

### P-009: Legs round 2: hip_pitch deep flexion and knee lever (information for Actuators)
- Owner: Legs. Date: 2026-10-13.
- Finding 1, hip_pitch (50 mm lever, 9084 N, slider-crank, Lmin ≥ 250 mm).
  - A packaged pelvis-mounted geometry gives min ratio 1.27 (torque/speed/carry) over the gait range −80…+40°, with 94 mm stroke.
  - Below −80° the available torque collapses (5 N·m vs a 111 N·m sit-to-stand need at −120°).
  - Proposal: change the hip ROM need to −80…+40° loaded and −120° unloaded. Legs re-plans sit-to-stand within this range (higher seat or trunk lean), or a second linkage is added.
  - The arm factor min is 0.56 vs the assumed K_HIP 0.77, which is acceptable on the angle-resolved basis.
- Finding 2, knee lever sweep with RV12x5 (7267 N, 0.633 m/s).
  - Speed ratio: 58.5 mm 0.92 (fails), 52.5 mm 0.99, 47.5 mm 1.06 (current, OK), 42.5 mm 1.14 (best balanced; torque 1.31, carry 1.14).
  - No change is requested. 47.5 mm is fine.
- Evidence: results/r2/linkage_study.json, plots/r2/linkage_study.png, DECISIONS L7.
- Status: accepted (re-plan) → R-012. Loaded hip_pitch −80…+40°, second linkage rejected; Legs re-plans sit-to-stand.

### P-010: Legs round 2: structure 4.84 kg + linkage allowance 0.588 kg (R-001 items)
- Structure (both legs): 6.13 kg v3-CAD basis → 4.84 kg. Tube walls 1.6 mm, pocketed lugs/clevis/tongue/fork, ribbed foot plate −25 %.
- Margin against 4.90 kg is +0.06 kg, pending FEA (grokbuild/structure_fea.md).
- Linkage allowance per leg:
  - knee crossbar + cheeks 0.125 kg
  - hip crossbar + cheeks 0.127 kg
  - ankle instep lugs 0.042 kg
  - total 0.294 kg per leg; 0.588 kg both legs
  - this leaves 0.062 kg of 0.65 for nut-rotor hubs
- These are parametric-solid estimates. The pelvis trunnion bracket is out of scope (Torso).
- Evidence: modules/legs/structure.py, results/r2/structure_mass.md/.json, DECISIONS L6, L8.
- Status: structure accepted provisionally (FEA pending); linkage split rejected → R-013 (hubs 12 × 16 g = 0.192 kg ≠ 0.062).

### P-011: Legs round 3: T5 carry verification at 1.0 m/s (evidence run), sit-to-stand re-plan done, linkage table
- Owner: Legs. Date: 2026-10-13. Commits: 1e65b3f and later.
- Change 1, carry verification speed 0.8 → **1.0 m/s**.
  - The 20 kg carry at 65 kg (`legs/results/r3/carry_20kg_1p0.json`) has ankle_pitch peak 238.3 N·m, so 311/238.3 = 1.31 ≥ 1.2. Avail/peak on the other joints: hip_yaw 1.69, hip_roll 1.82, hip_pitch 1.52, knee 1.62, ankle_roll 5.6.
  - The forward sim completes on R1.2 limits (16 touchdowns, no saturation: `results/r3/fsim/carry_20kg_1p0_fb1_kr4.json`).
  - Run at 0.8 m/s: ankle_pitch 219.8 (1.41).
  - Caveat, the same as every carry run: 29–30 frames (≈0.15 s total, at touchdown transitions) have a base residual above 5 % BW, with friction ratio 1.13 in those frames. CoP stays inside the sole.
- Change 2, R-012 condition met.
  - Sit-to-stand from a 0.46 m seat with hip ≥ −74.6°. Hip ratio is ≥ 20.6 throughout and knee ≥ 2.35 (DECISIONS L12).
  - Loaded hip need −80…+40° stands. Note: the condition is shown in inverse dynamics only, not forward sim.
- Information (R-013): one linkage table, `modules/legs/LINKAGE_TABLE.md`.
  - It counts 1.086 kg both legs, against the 0.609 kg in CONTRACTS. The difference is the dropped v3 knee-lever credit, the hip lever at dy 69 and the ankle lugs.
  - Open lines: hip pivot bearing (unowned), rod-end bearings, thigh trunnion clamp.
  - Owners need assigning. The mass impact on T2 must be ruled.
- Structure is 4.85 kg (hand check passes with a closed-box foot; the r2 ribbed foot failed). It remains provisional until FEA.
- Status: ACCEPTED (R-014 carry 1.0 m/s, sit-to-stand condition met in ID); linkage table accepted, mass recovery ordered (R-015)

### P-012: Actuators round 3b: hip_pitch lever + pivot bearing mass, linkage table, T2
- Date 2026-10-13. Proposer: Actuators (`actuators/results/DECISIONS.md` D25–D31, `results/LINKAGE_TABLE.md`).
- Evidence:
  - The hip_pitch lever for config B weighs 0.371 kg at SF 2.13 (CPU FEA, coarse mesh).
  - The pivot bearing CRBH 5013 A adds 0.314 kg/leg; this was a previously unowned line.
  - The single linkage table gives 2.527 kg for both legs (contract 0.609).
  - Rollup is 67.71 kg CAD-supported, or 66.35 kg if Legs and Torso land.
- Requests:
  - (a) Change the contract linkage line to 2.53 kg, with the hip pivot bearing owned by Actuators.
  - (b) Arbiter to rule where the ~1.4 kg for T2 comes from. Options: a two-bearing straddle with needle rollers (~−0.2 kg, needs a datasheet); lever SF 2 → 1.5 with a bench proof test (~−0.1 kg); controller force cap in deep flexion; or relief elsewhere.
  - (c) Ankle lever stays 70 mm. 77 mm breaks R-005 at 99.9 % Nmax, and carry at the 0.8 / 1.0 m/s rating speeds already passes at 1.41 / 1.30.
- Status: ACCEPTED with conditions (R-016): (a) linkage 2.53 kg, hip bearing Actuators; (b) cuts ordered per R-015/R-016, T2 limit raise PENDING BRYAN; (c) ankle 70 mm

### P-013: Actuators round 4: M1 result, M3 harness 0.82 kg, contract lines
- Date 2026-10-13. Proposer: Actuators (D32–D40, `results/mass_rollup_r4.json`).
- (a) Linkage line 2.53 → **2.25 kg** (needle straddle, lever SF 1.5 + proof test, catalogue rod ends). Net M1 is −0.278 kg. Margin 1.3 and housing CAD deliver 0, with evidence in D34 and D35.
- (b) Harness line 2.00 → **0.82 kg [EST]**. Ask for credit ×0.5 now, full credit after datasheets + routed CAD.
- (c) Robot 66.45 kg vs 66.5 (full credit). At ×0.5 harness credit it is 67.04 kg.
- No targets loosened.
- Status: ACCEPTED with conditions (R-018): (a) linkage 2.25 kg, M1 closed at −0.278, 1.3× re-size rescinded; (b) harness credited per part at 1.344 kg (−0.656), not ×0.5 flat; (c) credible 66.98 kg, 0.78 kg reassigned to Legs M2 (A1) + harness evidence (A2), deadline end of round 5

### P-014: Legs round 4: M2 design 4.79 kg, hip mechanical range −105°, thigh clamp form, ankle_pitch at 66.5 kg
- Owner: Legs. Date: 2026-10-13.
- **Change 1, M2.** Structure + thigh clamp + instep lugs = **4.792 kg** both legs (≤ 4.85). Breakdown in `legs/results/r4/structure_m2.md`.
  - FEA (box, P2, coarse): foot SF 2.77 at p99.9 under a 6 BW fall, with a singular peak of SF 1.56 at the rigid fixture. Clamp SF 2.90.
  - Hand checks for the tubes at 1.2 mm wall and the ring.
  - Request: provisional credit 5.40 → 4.79, final when `grokbuild/structure_fea.md` r4 confirms.
- **Change 2, hip_pitch mechanical range.** −120…+40° → **−105…+40°** (hard stop −105°, screw toggle −114.5°, Actuators D26). The loaded −80…+40° range is unchanged. Sit-to-stand needs only −76°.
- **Change 3, clamp form (Actuators interface).** Hip_pitch bodies mount on an axial ø12 spherical eye at the body end, not on side trunnion pin pairs. A two-sided trunnion's inner boss would sit inside the femur (L18).
  - Actuators' table changes by −2 trunnion pin pairs per leg and +1 eye per body.
  - Clamp mass 0.237 kg/leg, included in Change 1.
- **Information, 66.5 kg re-run.** At the R-017 mass limit, ankle_pitch need = 1.5 × 209.3 = **314 N·m > 311 avail (0.99×)**.
  - Options: a 73 mm ankle lever (Actuators D28 maximum, 323.8 N·m), or keep the needs basis at the actual rollup mass.
  - Other joints fit. Carry at 1.0 m/s gives 1.29×. Evidence: `legs/results/r4/requirements.md`.
- Status: **ruled R-019** — hip stop −105° accepted (R-012 amended); ankle 73 mm accepted conditional (stroke, L10, instep clearance); clamp form accepted conditional on Actuators; M2 credited −0.339 of −0.892 (foot+clamp FEA ×1, hand parts ×0.5)

### P-015: Actuators round 5b: ankle 73 mm, hip-body eye interface, clamp retention
- Owner: Actuators. Date: 2026-10-13.
- **Ankle lever.** Ankle_pitch lever is 73 mm (D45). Legs' instep-lug pin radius moves to 73 mm. Actuator mass +0.013 kg/leg.
- **Hip-body interface.** Hip_pitch bodies mount on the clamp through a GE 12 E eye with a ø12 pin (D46). The clamp arm bore is ø12 H7. Linkage +0.068 kg/leg vs pin pairs.
- **Clamp retention.** The femur clamp needs bonded or form-locked axial retention. Friction alone crushes the 1.2 mm tube (SF 1.06).
- **Contract rows.** Harness 1.296 kg (O20/O21) and linkage both legs 2.326 kg.
- Status: **ACCEPTED with conditions (R-020)** — needle/ø35 tongue holds (O17 closed); bond + light clamp + Legs sleeve/cross-pin backup (shoulder overruled); maintenance-free GE eyes subject to T9 life (A8); linkage 2.326 accepted; harness credited 1.324 (JST calc ×0.5); credible 66.89 vs 66.5. Legs r5 (L21–L24) ruled in R-020: M2 4.862 accepted, tongue −0.086 credited ×0.5.

### P-016: Actuators round 6 (71f3c3e): A8 eye wear part, A9 JST-GH weights, A5 ankle stroke/L10, rollup 66.853 (logged by Arbiter; no P-number filed)
- Date: 2026-10-13. Proposer: Actuators (D52–D55).
- Status: **ruled R-022**. A8 GE 12 C wear part every 5 250 h accepted with access conditions. A9 harness 1.286 credited ×1.0. A5 2.9 mm not adequate, so ankle_roll is limited to ±18° (margin 10.9 mm). The 66.853 rollup is superseded by the official rollup, credible 66.054.

### P-017: Legs r8 L36 structure FEA fixes (f480ed2) + A14 stops/panels (4f772c6) (logged by Arbiter; no P-number filed)
- Change: M2 4.822 → 5.114 kg (5.154 incl. bolts/bumper), +0.292 both legs: clevis pad, clamp arm 34 mm, 55 mm tangent tongue neck + retaining compound, foot doubler collar, bonded tube doublers. Hip ring retired. A14: ankle_roll ±18° stops 0.033, thigh pin panels 0.018/leg.
- Status: **ruled R-023**. Accepted (safety over the 4.87 sub-cap, reserve-funded). A1' −0.596 void; 0.267 tube hold until GB r2 (A15). A14 credited ×1.0. Credible 66.125, reserve 0.375.

### P-018: Actuators v4 audit fixes (knee twin housing, ankle end joints, ankle body, hip body trim)
- Owner: Actuators. Date: 2026-10-14. Evidence: `actuators/results/DECISIONS.md` D59–D62, `v4_deltas.json`, `ankle_v4.json`, `verify_v4.json`.
- **Knee:** merged twin housing with a shared web (−0.0013 kg/leg). No clash over 0…135°.
- **Ankle:**
  - Top: axial GE 12 C eye in a 0.6 mm-gap clevis.
  - Bottom: high-misalignment PTFE rod end (27° vs 20.8° demand) with a 4.5 mm spacer. Lug clearance is 2.15 mm over the full pitch −45…+40 × roll ±18 grid.
  - Trunnion raised 40 mm. Stroke margin 13.9 mm.
  - Rod end is a wear part every 4 250 h ([EST] rating; bench test required).
- **Ankle body:** valid STEP.
- **Hip body:** ≥ 3.0 mm verified; unused bosses trimmed.
- **Net mass: +0.069 kg/leg, +0.138 kg both legs** (actuator-owned only).
- **Legs asks (Legs mass, not included):**
  1. Model: −y knee screw uses the mirrored knee_body_x1, or place `knee_twin_housing.step`.
  2. Ankle:
     - Replace the trunnion cheeks, pins and centre plate with 2 clevises at y ±45, each with a 10.75 + 2 × 0.6 mm slot, PTFE thrust washers and a ø12 pin.
     - Raise the trunnion to z 450.
  3. Instep lug inner face moves 5.0 mm outboard (y 52.5 → 57.5). The pin gets 5 mm longer.
- Status: **ACCEPTED (R-024)**, +0.138 credited ×1.0; QA1 rod end wear part every 4 250 h until rating/bench (A22). Legs 15c602d +0.200 also accepted. Credible 66.463, reserve 0.037 (floor waived to end of round 13).

### P-019: Robot Lab head/neck own line (modules/head/HEAD_BALANCER.md)
- Head as balance actuator: studied and **rejected** (<1 % peak hip/waist torque; ≤3.5 % transient). The neck is designed for gaze and stabilization.
- New line "head + neck": **0.800 kg** (0.314 catalog, 0.179 calc, 0.307 [EST]); 2× Dynamixel XM430-W350-R, ZED X Mini, CF shell (replaces PA12), 7075 yoke.
- **Mass delta claimed: 0.000 kg** (R-024). Ask: move head + neck out of "all other lines" as its own line, at 0.800 kg. If the A12 itemization shows the basis carried the sim's 1.137 kg, credit −0.337 kg; if it carried less than 0.800, the difference must be offset (proposed offset: the A19 cover-panel cut).
- Power: +4.4 W [EST] if the camera isn't in the 699 W budget; runtime −0.6 %, so 2 h stays met at 1.0 m/s.
- Requests: Legs updates the sim neck (mass, armature 0.0005, ctrlrange 4.1 Nm); the A11 brain check covers the GMSL2 input.
- Status: **ACCEPTED (R-025)**. Head line 0.810 paper (BOM incl. spring) / 1.178 credited; basis removed 2.692 (v3 head 1.6 + 2 neck actuators) → −1.514 credible. +4.4 W booked; T7 stays met (703.4 W). AGX301 needs a JCB022/JCB009 GMSL board (+0.045). Credible 64.995, reserve 1.505.

#### P-019 addendum (A23, Robot Lab, 2026-10-14): cited masses for RL Arbiter
- Bearings now catalog: 6806-2RS 0.026 + 6800-2RS 0.005 = **0.031** (was 0.027 EST, +0.004).
- Converter fixed for the 68–84 V bus: **RECOM RP40-11012SFR/P**, 43–160 V → 12 V/3.33 A, **0.043** with heatsink, catalog (was 0.040 EST, +0.003). Servo current limit 1.5 A each.
- Shell material cited (ACP 5.8 oz 2×2 RTS prepreg); mass stays calc 0.179. Yoke/deck stock is cited (7075-T651 plate / 7075-T6 sheet), but the machined masses stay [EST] 0.110/0.070. Spring (Lee Spring LTL series) and harness stay [EST].
- Line total **0.817 kg** (+0.007): catalog 0.388, calc 0.179, [EST] 0.250 → cited/calc share 69.4 %.
- R-021 credit recomputed: saving 2.692 − 0.817 = 1.875; credited 1.875×0.694 + 1.875×0.306×0.5 = 1.588 → **credited head + neck 1.104 kg (was 1.178; −0.074 credible)**. Paper +0.007.
- The neck servos use the AGX301 RS485, so no added mass. The JCB022/JCB009 +0.045 is unchanged in the brain area (R-025 §4).
- Status: **ACCEPTED (R-026), A23 closed.** Credited head + neck 1.104 (−0.074) confirmed; converter verified vs RP40-FR datasheet. Conditions: order RP40-11012SFR/P-HC (43 g heat-sink variant); add the note-9 input filter (A27). Credible 64.920, reserve 1.580.

### P-020: Robot Lab v5 cover set (104c9ad, `design/V5_POLISH_PLAN.md`): replace the PA12 MJF covers M3 line with a CF set
- Claimed: +0.2 to +0.5 kg net, replacing 1.384 paper / 1.622 credited.
- Status: **ACCEPTED IN PART (R-027).** The PA12 line is replaced, but by **thermoformed PC 1.5 mm** (weighted score near-tie, PC wins on cost and fall toughness): 1.567 paper / 1.713 credited (+0.091 credited). CF is allowed panel by panel at ≤ the PC panel mass. Extra V5 coverage (skirt, bellows, boots, knee caps) needs separate P-numbers. "No 3D printing" is recorded as a crew preference, not a Bryan rule.

### P-021: Robot Lab v5 plan item 7: PA12 hand palm → machined 7075 (104c9ad)
- Status: **ACCEPTED (R-027)**, +0.144 kg both hands (×1.0, upper bound from the model_v4 palm envelope); A32 refines it with CAD.

### A27 (a61995b, Robot Lab): RP40 /P-HC + note-9 input filter + XM430 current limit
- Status: **BOOKED and CLOSED (R-027).** Head 0.817 → 0.833 paper (+0.016 ×1.0). Obsolete Rubycon BXF needs an equivalent before purchase (A28).

#### Robot Lab note for RL Arbiter: A28 / A30 / A32 (R-027)
- **A28:** Panasonic **EEU-EE2D680** (68 µF/200 V, 105 °C, 10,000 h, 12.5×25 mm, active) replaces the obsolete Rubycon BXF. 4.70 g each, catalog (distributor unit weight), $0.597. Caps 0.0105 [EST] → **0.0141 catalog (+0.0036)**, so the head line is **0.833 → 0.837 paper**; the [EST] share drops (catalog 0.402 / calc 0.179 / EST 0.256). Flags: 25 mm tall (vs ≤20 asked), ripple 1.33 A vs 1.35 A.
- **A30:** `covers/COVER_COST.md` + `.csv`. PC sheet is cited at $25.80 per 24×48″. Tooling [EST]: 16 tools + fixtures ≈ $18.4k, ≈ $86 per panel, first set ≈ $19.8k, further sets ≈ $1.4k. No mass change.
- **A32:** `model/palm_7075.py` (CadQuery) is fitted into model_v4 and replaces the PA12 palm: 1.5 mm walls, 4 mm knuckle bar, 3 mm wrist plate, 4 dorsal + 4 palmar windows 32×30 R3, 20×60 side windows. **0.0924 kg/hand** (CAD volume × 2.81) vs the R-027 upper bound 0.1127 → **−0.0203/hand, −0.041 kg both hands** (P-021 net is +0.103 instead of +0.144). Clash/audit results are in the commit message.

### P-026: Arms & Hands: arm ROM cut to the clash-free/usable range (elbow −125…0, wrist_pitch ±60, wrist_yaw ±30)
- Date: 2026-10-14
- Module / proposer: Arms & Hands / RL Arms & Hands (R2)
- Affected owners: Arbiter (ruling), Actuators (hard stops, harness loop lengths), Controls (joint limits), Electronics (harness ROM in `actuators/results/harness.md`)
- Change: required ROM in `sim/v3/humanoid_v3.xml` / `model/JOINT_AUDIT.md`: elbow −140…0 → **−125…0**; wrist_pitch ±70 → **±60**; wrist_yaw ±40 → **±30**. Shoulder_roll is unchanged here (−15…180 required vs −5…175 clash-free; geometry fix, R2+).
- Evidence: v4 audit sweep (`model/JOINT_AUDIT.md`, `audit_v4.py`): elbow clear −115…0 (clash at −120°: upper-arm tube × forearm shell); wrist_pitch clear ±40 (±45: roll fork × palm); wrist_yaw clear ±25 (±30: fork × palm). All of these are [EST] placeholder geometry. Load cases in `arms/R1_ARCHITECTURE.md` (T5 reach/carry) use elbow ≥ −90° and wrist 0°. No target names an arm ROM: T3 counts DoF only.
- Impact on contracts: mass 0. Power 0. Harness loop length goes down (elbow 140 → 125°, wrist pitch 140 → 120°, yaw 80 → 60° in the harness ROM list), so harness mass falls slightly [not computed]. Torque/speed unchanged.
- Impact on targets: T3 unchanged (DoF kept). T4/T5 no change: all load cases are inside the new range. The cut ROM is still wider than the current clash-free range, so R2+ geometry has to free up elbow −125 and wrist ±60/±30. Hard stops sit at the new limits.
- Asks: **Arbiter**: rule on the cut ROM against T3/T4/T5. **Controls**: agree that no manipulation primitive needs elbow < −125°, wrist_pitch > 60° or wrist_yaw > 30°.
- Status: OPEN

### P-027: Arms & Hands: wrist pitch/yaw differential screw pair downsize, ≤ 0.90 kg/side (was 1.55)
- Date: 2026-10-14
- Module / proposer: Arms & Hands / RL Arms & Hands (R2)
- Affected owners: Actuators (selection, citations), Arbiter (mass credit)
- Change: CONTRACTS §1a wrist_pitch max mass 1.55 → **≤ 0.90 kg/side** (pair, shared with wrist_yaw). Need peak stays at the v3 contract value of 14.7 N·m (pitch) and 8.9 N·m (yaw). R1 sim-based need is 11.1 N·m for both. Speed need is 6 rad/s [EST v2].
- Evidence: `arms/arm_loads_r1.json`: max static wrist load 7.4 N·m (10 kg at the hand-box centre, sim/v3 geometry) → need 11.1 at 1.5×. The v3 selection (2× TBM2G-05008C + RV12x4, 25 mm arm) gives 48 N·m, 4.3× need, 30.1 rad/s. Per screw at the 25 mm arm: 14.7 N·m / 0.025 m / 2 = **294 N axial** (pitch, both screws in phase).
- Impact on contracts: mass up to −0.65 kg/side, **−1.30 kg both** (paper). **No credit until Actuators cite parts** (credit ×0 now, ×1.0 on datasheet). Envelope is the same or smaller. Power is negligible (v3 copper 0.0 W).
- Impact on targets: T2 +1.30 kg reserve if it lands (weight 0.15). T9: Actuators must show the new screw L10 ≥ 14 600 h at arm duty.
- Asks: **Actuators**: cite a motor + screw (or ball-screw / micro strain-wave) pair meeting ≥ 14.7 N·m peak, ≥ 6 rad/s at 30 % torque, ≤ 0.90 kg/side all-in incl. encoders/drive, with screw C_a and L10. **Arbiter**: credit on citation.
- Status: OPEN

### P-042: Arms & Hands: 20 kg carry pose with elbow ≤ 15 N·m, plus a hold-time limit (R-030 A39; renumbered from P-028 by R-031)
- Date: 2026-10-14
- Module / proposer: Arms & Hands / RL Arms & Hands (R3)
- Affected owners: Controls (pose + I²t, P-043/A40), Thermal, Legs/Controls (carry COM), Arbiter
- Change: new carry-pose contract line (CONTRACTS §3 Arms / Controls): **the T5 two-hand 20 kg carry is done in the "chest carry" pose: shoulder_pitch −60°, elbow −110°, shoulder roll/yaw 0, wrist 0.** Band: shoulder_pitch −60…−50°, elbow −115…−100°, while elbow ≤ 15 N·m (rows in `arms/carry_pose_r3.json`).
- Evidence: `arms/carry_pose_r3.py` → `carry_pose_r3.json`, the R1 load model (sim/v3 masses, 10 kg/hand at the hand-box centre, static).
  - At the pose: **elbow 6.95 N·m, shoulder_pitch 43.45 N·m**, shoulder_roll 0.02.
  - Hand position vs the waist_pitch axis: x +0.321 m, z +0.415 m.
  - For comparison, the R1 carry pose (sp −30, el −60) gives elbow 40.14 and shoulder 61.25.
  - Elbow −110° is inside P-026 (−125…0, approved R-031) and inside today's clash-free range −115…0.
  - Across the band, the elbow stays at 3.5–13.7 N·m and shoulder_pitch at 40.0–50.2 N·m.
- Thermal (`thermal/O-A2_ARM_HOLD.md`, f4e6dfb; copper ∝ T², steady ΔT ∝ copper):
  - elbow: 59.5 W → **1.8 W, ≈ +6.7 K**. Thermal gives 8.3 W / +31 K at 15 N·m.
  - shoulder_pitch: steady +91 K at 61.3 N·m (≈ 1 K over the 130 °C basis) → **+46 K at 43.45 N·m**, so the shoulder margin is restored (≈ 44 K to 130 °C at 40 °C ambient).
  - At the band edge (50.2 N·m) the shoulder is +61 K.
- **Hold-time limit:**
  - (a) Inside the P-042 band: **unlimited** (steady state within limits on Thermal's numbers).
  - (b) Elbow > 15 N·m (pick-up or reach), per Thermal 7675c8b (D68 T-dependent R/Kt, 155 °C motor limit): at 40.1 N·m the elbow runs away and reaches 155 °C in 6.0 min (4.0 min at η 0.76). **Limit: ≤ 3 min at up to 40 N·m, then ≤ 28 N·m.** Arms adds that pick-up and set-down transitions must reach the band within 30 s.
  - (c) Shoulder_pitch: at 61.3 N·m it settles at 126 °C, inside the 120–130 °C derate band (P-043). In the P-042 band (≤ 53.75 N·m catalog) it runs well below that. **Static shoulder > 55 N·m: ≤ 10 min [conservative, Arms]**, or until the P-043 derate trips, whichever comes first.
  - (b) and (c) still rest on [EST] capacitance. The G5 bench elbow thermistor test replaces them.
- **Elbow solution (explicit):**
  1. **Primary: the P-042 15 N·m pose.** It adds 0 kg and 0 W, and the hold is unlimited (catalog recheck: elbow 7.09 N·m).
  2. **Option evaluated: a power-off brake / hold mode on the elbow.** A spring-applied brake would carry the static hold with zero copper. The repo has no cited brake for the TBM2G-05013/CSG-20 frame, so its mass and envelope are **unknown, not invented**. It also lengthens the 81 mm elbow housing inside a forearm that is already short (O-A3 shortfall). A hold mode without a brake does not help: a CSG-20 is backdrivable, so holding still costs copper. **Not proposed now.** Revisit only if Controls cannot guarantee the pose, with a cited brake part (Actuators).
  3. **Fallback named by Thermal:** a 2× continuous elbow, i.e. a TBM2G-06013-class frame or CSG-20-160. Mass not booked.
- Impact on contracts: mass 0. Power: carry arm copper ≈ 194.6 → ≈ 42 W for both arms [EST scaling]. Carry bus draw is ≈ 830 W vs Thermal R1's 984 W [EST].
- Impact on targets:
  - T5 passes: needs are far below the selections, wrist 7.4 N·m is unchanged, and elbow ≤ 15 holds across the band.
  - **Risk:** the load sits 0.32 m forward at chest height. The Legs carry model (`legs/scenarios.py`) uses a box 0.25 m ahead of the waist axis with a 0.25 rad trunk lean. Legs/Controls must re-check the ankle margin (R-014: 1.31×) with x = 0.32.
  - **Risk:** the sim arm is 3.59 kg/side light (O-A1). The band keeps ≥ 8 N·m elbow headroom.
- Re-check with the catalog inertials (`arms/recheck_r3.json`, O-A1 file `arm_inertials_r3.json`):
  - pose: elbow **7.09**, shoulder **46.87** N·m (shoulder ≈ +53 K)
  - band edges: elbow 13.96 N·m (≤ 15, OK), shoulder ≤ 53.75 (≈ +70 K)
- Asks:
  - **Controls:** adopt the pose as the carry primitive, plus limits (b)/(c) in P-043.
  - **Legs/Controls:** confirm the COM at x +0.32 / z +0.415.
  - **Thermal:** confirm (c), and the shoulder at 43–50 N·m.
- Status: OPEN

### P-151 (renumbered from P-053 by R-123): Materials: hollow ankle pitch/roll pins (ø12 steel, ø6 bore)
- Date: 2026-10-21
- Module / proposer: Materials / RL Materials
- Affected owners: Legs (job 7 ankle cross, pins), Arbiter (mass)
- Change: the 4 ankle pins per leg (pitch stubs ø12 × 18 + 12 press, roll pins ø12 × 12 each side, legs/grokbuild/ankle_cross_fea_brief.md) are made as gun-drilled ø12/ø6 tubes in 42CrMo4 Q&T (or 17-4PH).
- Evidence (materials/R_SWAP_SCAN_R7.md):
  - Steel volume ≈ 12.2 cm³/leg [EST, lengths from the brief] → 95 g/leg at ρ 7.8.
  - A ø6 bore removes 25 % of the volume (**−24 g/leg, −0.048 kg robot [EST]**). Bending stiffness falls only 6 % (1 − 0.5⁴), and the section modulus by 6 %.
  - Hollow pins also suit the DU bushes in ANKLE_CROSS_7075 §3.
- Impact on contracts: mass −0.048 [EST]; no interface change (pin OD unchanged).
- Risks: pin bending stress +6.7 %, which Legs checks in the job-7 FEA; plug the bore ends against debris.
- Status: OPEN

### P-054: Materials: Ti-6Al-4V ankle pins instead of steel (alternative to P-151, higher risk)
- Date: 2026-10-21
- Module / proposer: Materials / RL Materials
- Affected owners: Legs, Arbiter
- Change: solid Ti-6Al-4V (ρ 4.4, YS 910, MIFTi64) ankle pins with a nitrided or DLC running surface, in DU bushes.
- Evidence: 95 g/leg → 54 g/leg, **−0.082 kg robot [EST]**. Ti pins are ~1.8× as flexible as steel (E 110 vs 190).
- Risks: Ti galls and wears without a hard coating (coating spec and supplier data not yet in repo); galvanic to 7075 is worse than steel (both need the bush/sealant); cost. Not combinable with P-151 (pick one). Recommend P-151 first.
- Status: OPEN

### P-145..P-150: Torso & Power mass cuts (Torso, 2026-10-21; R-079 FEA priority)
All keep R-076 (reinforced isolation, IEC 60664-1 creepage, IP2X), R-074 (main link ≥10 mm², 2.5 mm² only on branches fused ≤30 A), R-036 / 2 h walk margin (+1.0 W, none of these add load) and T-031 crush (pad, land, rib untouched). Savings are [EST] unless cited; book at half credit until weighed.

| P | Cut | Basis | Saving kg | Risk |
|---|---|---|---|---|
| P-145 | PDB shrink: no limb connectors on the bulkhead (R-079), so the PDB carries only fuse, contactor, clamp FETs and 5 branch lugs; 2-layer 2 oz → 4-layer 3 oz half-area board | PDB/busbar/branch line 0.25 [EST] | −0.06 [EST] | creepage must stay 1.5 mm/≥ reinforced per R-076 at 92 V; re-layout cost |
| P-146 | Merge BMS host (S32K344 + BQ79600) and FET/pre-charge board onto the BQ79616 board, one board in the pack | pack "BMS+FET+fuse+connector" 0.30 [EST] | −0.04 [EST] | thermal coupling of FETs to AFE; channel-2 BQ77216 stays on its own isolated section (independence per R-036) |
| P-147 | Titanium Gr5 M3–M5 for non-preload-critical torso fasteners (shell, partition, duct, PDB, bezel, EtherCAT board); shoulder M8 12.9 steel and pelvis/waist joints unchanged. Ti density 4.43 vs steel 7.85 g/cm³ (−44 %) | ~70 fasteners, ~0.14 kg steel [EST] | −0.05 [EST] (see torso/BOM_fasteners.md) | galling (use anti-seize/thread-lock), cost; galvanic with CFRP is better than Al |
| P-148 | Pack rails + latch 0.20 → pocketed 7075 rails, and SBS75X blind-mate (R-084) takes the alignment, so one rail becomes a plain guide | 0.20 [EST] | −0.05 [EST] | in FEA job 3 scope; latch retention vs 10 g crash load |
| P-149 | Partition 1 mm CFRP → 0.6 mm CFRP with a 3 mm Rohacell core strip under the EtherCAT board bosses | partition [EST] | −0.03 [EST] | stiffness at board mounts (FEA job 3 checks); duct seal flange |
| P-150 | A41 duct walls: mould the duct side walls into the shell/partition instead of separate 1 mm PC walls | duct 0.04 P-030 [EST] | −0.02 [EST] | tooling; Electronics co-owns A41 (R-030), needs their sign-off |

- Considered and rejected: contactor swap (only lighter cited part, EV100, fails the coil-power limit, R-074); fan (Sunon fixed, no cited lighter part at the airflow); bus-bar downsizing below 10 mm² (R-074); DC-DC repackaging (DCM is a sealed module on the cold plate).
- Total proposed: **−0.25 kg [EST]**, −0.125 at half credit (P-147 corrected to −0.05)
- **2026-10-21: job 3 FAILED. P-148 and P-149 are ON HOLD (pocketing credit pulled). P-145/P-146/P-147/P-150 are independent: −0.17 [EST], −0.085 at half.** See torso/DIAGNOSIS.md.. P-148 and P-149 are confirmed by FEA job 3 (FEA_SPEC_torso_pocketing.md).
- Status: OPEN (Arbiter)
### P-055: Actuators: shoulder_roll contract row drops the slip clutch (R-120)
- Date: 2026-10-21
- Module / proposer: Actuators / RL Actuators
- Affected owners: Arms & Hands, Arbiter
- Change: CONTRACTS shoulder_roll row "rotary + 300 N·m slip clutch" → "rotary"; envelope "74 × 87 (+ clutch, TBD)" → "74 × 87 (CRBH 7013 A seat flange Ø108 per R13)".
- Impact on contracts: mass 0 (clutch was never booked); torque basis CSG-25-100 momentary 369 N·m, gate Mx ≤ 351 N·m at ×1.05.
- Impact on targets: none.
- Evidence: actuators/forearm_roll_torque.py, results/FOREARM_ROLL_TORQUE.md; R-120 (Mx 321 N·m, SF 1.10).
- Affected owner response: pending
- Status: open

### P-053: ID: thigh pin access (L63-R), band and hatches deleted
- Date: 2026-10-21
- Module / proposer: Design / RL Industrial Design
- Affected owners: Legs, Arbiter
- Change: 218° thigh band, L30 front hatch and rear panel deleted; front skin runs continuous. Fairing covers 5 of 8 pin ends (180° end visible through rear 40×50 window; 225/270° face the open inboard side, as L30; cosmetic). Pins extracted on the bench only; ends tapped M3 (Legs confirmed angles 0/90/180/270°, 45/135/225/315°).
- Impact on contracts: none (no mechanism change); fairing fasteners TBD under A29 CAD.
- Impact on targets: mass −0.036 kg robot [EST].
- Evidence: design/thigh_pin_access_p053.py, design/thigh_pin_access_p053.json (adopted fe09355).
- Affected owner response: Legs confirmed pin angles and M3 ends
- Status: adopted (fe09355)

## L65 (Legs, R-130) — femur/tibia side-dent fix: uniform 1.5 mm wall (supersedes P-047 1.6 mm)
- **Limit:** R-130 "7050 395" = Sy_typ 435/1.1 (R-128 §5/R-127). R-128 §5 fall limit is min(A/S-basis, Sy/1.1) = min(393, 395) = **393** (S-basis Fty, JOB9_SPEC). "No permanent dent" = stay below minimum (S-basis) yield → 393 used (stricter).
- **Data:** STRUCTURE_FEA_REPORT f58c40a dent table. (Report's "SF" column is vs Sy 503; R-130's 0.56/0.82 are vs single-path 262.) Script `modules/legs/femur_dent_l65.py` → `results/r031/femur_dent_l65.json`.
- **(c) P-047 1.6 mm as-is:** femur 318.4 → SF **1.23** vs 393; tibia 327.2 → 1.20. PASSES. +0.0995 femur pair, +0.0954 tibia pair.
- **(a) uniform minimum:** σ∝t^-n fitted on the 1.2/1.6 FEA points [EST] → t_min femur 1.37, tibia 1.40 mm. Chosen **1.5 mm** (standard tube wall, covers interpolation error): femur 347.3 [EST] → SF **1.13**; tibia 357.9 [EST] → **1.10**. Mass +0.0748 femur pair, +0.0717 tibia pair = **+0.147 kg robot vs 1.2 baseline; −0.003 vs P-047's +0.15 booking (vs 1.6 actual −0.049)**.
- **(b) local step/doubler over 80 mm:** rejected. ~+0.013 pair per tube at 1.4 mm, but the 80 mm is the FE stub length, not a defined impact zone — a side fall can strike any exposed span, so the band can't be placed with evidence. A step adds Kt ~1.5–2 [EST] on the fall bending (220.1 at 1.2 → ~330–440 vs 262 single-path) and fatigue at the step; a local internal step means boring from thicker stock or bonding (DP490 peel, R1 §8 concerns). Saving ≤0.03 kg/pair does not justify it.
- **Other cases at 1.5:** fall bending and 3 BW scale down from 1.2 (220.1/110.1 MPa at 1.2 → lower at 1.5), so fall SF vs 262 ≥1.19 and fatigue no worse than baseline. Bond/collar ID unchanged (OD held 50/45); internal sleeve 47.6 OD must become ≤47.0 (tube ID 47.0 at 1.5) — flag to self/BOND_SPEC. No thigh-cover load path counted.
- **Gate:** job 9 b3 re-run at 1.5 mm to confirm dent ≤393.

### P-152: Legs: femur/tibia inner bonded sleeve OD 47.6 → 46.80 mm for the 1.5 mm wall (L65, R-135)
- Date: 2026-10-21
- Module / proposer: Legs / RL Legs
- Affected owners: Actuators (hip-pitch output / collar interface, per R-135 "through CONTRACTS with Actuators"), Materials (bond), Arbiter
- Change: inner 7075 sleeve (DECISIONS L22, BOND_SPEC header "47.6/43.6 × 34") OD **47.6 → ≤ 47.0; proposed 46.80 mm** (ID 43.6 and length 34 unchanged → sleeve wall 2.0 → 1.6 mm). Reason: L65 ø50 × 1.5 tube gives a 47.0 bore. **The brief's 46.9 does NOT keep the BOND_SPEC §3 bond line**: §3 sets diametral clearance 0.20 ± 0.03 mm (0.10 radial target, 0.08–0.13 range); 47.0 − 0.20 = **46.80** (46.9 would give 0.05 radial, below the 0.08 floor). Tolerance: sleeve OD 46.80 ± 0.015 with tube bore 47.00 ± 0.015 [EST tolerance split] holds 0.20 ± 0.03.
- Contract row: **no CONTRACTS.md row currently states the sleeve OD** (searched: only "knee clevis → femur flange | 4 × M5 12.9" in §1c Mounting and the §Structural femur/tibia line; sleeve is defined only in legs/DECISIONS L22 and legs/BOND_SPEC). Requested Arbiter edit (Legs does not edit CONTRACTS): add to §1c Mounting table a row
  `| hip-pitch collar → femur tube (bonded) | 7075 split collar ID 50 × 34 + femur ø50 × 1.5 (bore 47.0) + inner 7075 sleeve OD 46.80 / ID 43.6 × 34, DP490 0.10 mm bond line (0.20 ± 0.03 diametral), 8 × ø7 42CrMo4 backup pins (L63-R) | fall + R-023 dent/bending; bond SF per BOND_SPEC | legs/BOND_SPEC.md, legs/DECISIONS L22/L63/L65, P-152 |`
  and the same sleeve line for the tibia (ø45 × 1.5) if Arbiter wants the tibia joint listed. Owner: Legs (sleeve, tube); Actuators co-sign (collar / hip-pitch output side).
- Fallback: if JOB9 b3 re-run at min-wall 1.37 femur / 1.40 tibia fails SF ≥ 1.0 vs 393 (R-135), revert to P-047 1.6 mm → bore 46.8, sleeve OD ≤ 46.8 (by BOND_SPEC §3: **46.60**).
- Impact on contracts: sleeve mass −0.004 kg/sleeve [EST: π/4(47.6²−46.8²)·34·2.81e-6]; booking unchanged (+0.15, R-135).
- Impact on targets: none beyond L65.
- Evidence: legs/femur_dent_l65.py, results/r031/femur_dent_l65.json, BOND_SPEC §3, RULINGS R-135 (b8a2c69).
- Affected owner response: **Actuators co-signs (2026-10-21).** The collar (ID 50 × 34) and the hip-pitch output side are unchanged; the collar bore still mates the ø50 tube OD; no actuator load or contract value changes. Co-sign stays conditional on the P-152 fallback (JOB9 b3) passing.
- Status: open

### P-153: Actuators: heat plates rev 2/3 mass +0.016 kg and knee thigh-shell window (D90, D91; P-055 / R-141, Thermal R131 rev 2)
- **Change:** (D90) hip_pitch plate 80 → 84 mm square for ≤72 °C (Thermal: 68.8 °C at duty, h 8, if the back face sees ≤50 °C structure), +2.6 g × 4; PE washers +0.1 g × 12. (D91) Knee plate flipped into a black-anodised thigh-shell window at the L51 26 mm face, with 8 × 13 × 1 fins at 6 mm pitch protruding 13 mm into the stream: UA 0.203 W/K, 71.5 °C at duty. +1.8 g × 2 vs R-140 (net of D90's −1.6); foil femur shield +0.6 g × 2.
- **Mass:** 0.339 (R-140) → 0.355 kg, **+0.016 kg** (over the 0.005 freeze), separate from R-141's +0.008 for the M2 screws.
- **Envelope (Legs/ID):** a 100 × 48 window in the thigh fairing over the L51 box, with fins standing 13 mm proud (12 mm minimum), axial so they run along the flow. No change to the 26 mm L51 depth inside.
- **Interface condition:** the hip pitch/ankle/shoulder plate back faces see ≤50 °C structure, never the hip-pitch housing (85–98 °C), or carry a low-ε shield.
- **Evidence:** modules/actuators/drive_heat_plates.py, results/drive_heat_plates.json, results/DRIVE_HEAT_PLATES.md rev 3, cad/drive_plate_*.step; Thermal R131_ELMO_MG.md rev 2.
- **Open:** Thermal verification of rev 3, the R-140 conditions (Controls duty sim), and Electronics confirming the mated plug fits the 7 mm femur gap.

- **Rev 4 update (D93, 2026-10-21):** knee fins 13 → 18.5 mm with a 45° × 8 lower taper, plus ID's P-154 low-ε PC guard (2 × ≈20.3 g). **+0.066 kg vs rev 3 booked in full** (the plate and the guard). **P-153 total: +0.082 kg vs R-140** (0.016 + 0.066). Envelope: the guard is 30.0 mm proud of L51 (ID rev 4 had 29.5, +0.5 for the taper compensation). Gates: Thermal re-check of rev 4 at 18.5 mm with the taper, and the ID rod sweep at 30.0 mm.
### P-154: ID: knee fin guard (perforated PC over Actuators knee plate rev 4)
- Date: 2026-10-21
- Module / proposer: Design / RL Industrial Design
- Affected owners: Actuators, Legs, Thermal, Test & Reliability, Arbiter
- Change (rev 4b; Actuators 5008683, Thermal 44b7c36, Legs L71 6060973):
  - Thermoformed 1.5 mm PC cap, 104 × 66 outer / 101 × 63 inner, 30.0 mm proud (inner face 28.5; fins 18.5, tips x −53.0); fin tip to inner face 10 mm; outer fins 10 mm to the side walls.
  - Walls 7.5 mm/side outboard of the plate (≥ 0.5 fit); edge seal is a 1 mm silicone bead inboard of x −34.5 (Actuators).
  - 4 base notches 10 × 7 at the L58 tabs (≥ 3 mm); 45° × 8 mm lower outer-edge chamfer + matching fin taper (Actuators).
  - 11 slots 4.0 mm, 62 % face open, 57.9 cm² total; ends open; low-ε (≤ 0.1) Al inner face, outer in cover colour.
  - 4× M2.5 A2 captive into ribbed PA12 bosses Ø6 × ≥ 5 at y 112/148, z 684/796 (off the L58 screw line); drive-bay panel gets the window frame. Guard is sacrificial (Legs L71 d).
- Impact on contracts: none (no mechanism change); envelope 30.0 mm proud at the femur rear.
- Impact on targets: mass +0.012 kg pair [EST] (guard 0.031 incl. liner/paint, window −0.019); fin growth is Actuators'.
- Evidence: design/cad/covers/knee_fin_guard.py/.json/.stl, r143_knee_sweep.py/.json (rods 12.0 mm at knee 140°; housing 18.1 mm at 145°, Legs L71); V5_COVER_SET.md R-143 section.
- Affected owner response: Legs L71 confirmed placement, lever eye, rods y ±45, sacrificial guard; Actuators 5008683 fins/seal
- Status: **WITHDRAWN (2026-10-21, Robot Lab per Thermal 389f91b: guard redundant behind the fairing grille).** Mass: Robot Lab books −0.041 (T&R 20.3 g/side); ID CALC guard was 0.031 pair (+0.012 net with the −0.019 window). True delta of withdrawal −0.031; replaced by P-156.

### P-155: Actuators: hip-pitch lever G3-R2: section b30/d36 → b34/d40, R8 upper + R5 ear blends, +0.113 kg (D92)
- **Why:** job2 (334e848) FAILED with a singular unfilleted upper web/arm edge, and the near-corner field (116–157 MPa design) puts the nominal amplitude at about 54 MPa. Even with R8 (Kt ≈ 1.35) that is ≈ 73 against 58, so a fillet alone is not enough (this contradicts the L69 estimate).
- **Change:** b34/d40/d1 21. R8 on the upper web/arm edges and R5 on the ear roots (both sides). Estimated peak 119 MPa, amplitude 53 MPa [EST]. RV12 rod 1.18 mm. 7075-T651 2.5 in, single-path 271 ST.
- **Mass:** 0.4642 → 0.5207 kg per lever, **+0.113 kg robot** (over the 0.005 freeze). This sits inside Legs L47's b35/d40 fallback booking (+0.242 vs the old baseline), so it depends on what is currently booked for the lever.
- **Gate:** the G3-R2 FEA (brief GROKBUILD_lever_fea_r031.md §G3-R2) has to converge with amplitude ≤ 58 at both the upper R8 and the ear R5.

### P-156: ID: thigh-fairing knee venting (grille + low inlet/high outlet + duct insert), replaces P-154
- Date: 2026-10-21
- Module / proposer: Design / RL Industrial Design
- Affected owners: Legs, Actuators, Thermal, Test & Reliability, Arbiter
- Change: grille integrated in the v5 rear thigh skin (x −82.5) over the D91/D94 fin field, 104 × 52, 8 slots 4.5 mm, 65 % open, Al liner ε ≤ 0.1 inside, cover colour outside; low inlet z 643–681 and high outlet z 799–837, 1296 mm² free each; PA12 duct insert, side gap 5 mm, notched at the L58 tabs, 4× M2.5 into bosses at y 112/148 z 684/796.
- Impact on contracts: none (no mechanism change; v5 skin position unchanged).
- Rev 4e (T&R 67e6eed): outlet recessed 11 mm under a flush +6 mm skin shroud (17 mm standoff, 2686 mm² exits up/upper sides, ≥2× outlet); knee-housing fairing slots 5 × 4.0 ± 0.3 × 20 per end (370 mm² min); housing low-ε callout removed (housing bare).
- Rev 5 (Legs L72 e44c588 real geometry): rear grille/rear outlet dropped (the rear turn over the housing is 4.5 mm, 234 mm², FAIL; the trunnion top plate blocks). New route: lower-rear-hull inlet (1440 mm²) → baffle chimney → transfer duct z 793–813 outboard in front of the housing (1358 mm²) → outboard side exit (1287 mm² free) under a 26 mm Al-lined hood (2652 open + 1024 dilution); H ≈ 0.14 m. Static gaps 3.0 mm; Legs CAD ROM recheck. Mechanism fallback: L60 top-plate cut-out (Option B). Rev 5a: hood louvred (4.5 ± 0.3 gaps), 3394 mm² free, IP2X; P-156 +0.112 pair [EST], knee-venting total +0.062.
- Impact on targets: rev 5 +0.097 kg pair [EST] (knee-venting total +0.047); rev 4e +0.054 kg pair [EST] (rev 4d +0.039); with the P-154 withdrawal (−0.031) and the window (−0.019) the knee-venting total is +0.035 pair.
- **Rev 6 (2026-10-21, Option B; T&R 7f12ce9, Thermal a32d341 B2, Legs L74 af1b331): CURRENT.** Removes the side duct and hood. The chimney rises straight through the Legs L60 notch x −34.5…−61 × y 104–156 (≈ 1323 mm²) to a z 860 stack and a foil-lined PC shroud: 20 mm standoff, 2646 mm² min free, 710 mm² min dilution, all ≤ 4.8 mm, no bare louvres. The P-023 skirt gets inner-face foil and a ≥ 15 mm gap. P-156 **+0.097 pair [EST]**, knee-venting total **+0.047**. **Notch PENDING the Legs FEA/fall/thermal-break check; Thermal area recheck pending.** Script thigh_knee_vents_r6.py.
- **Rev 6b (T&R 925d72e, Legs L75):** stack top z 840 (pending Thermal), shroud x −100…−20 × y 86–150 × z 840–904 with aft-only openings (2680 min free, 710 dilution), 40° chamfer + TPU strip (100 N SF 2.2). P-156 0.134 pair, venting total +0.084. P-023 skirt rev 6 relief (hip_skirt_r6), worst 4.0 mm, −0.198 kg. Thermal 5fd6a54 PASS (stack z 840).
- **P-023 rev 7 study (thigh-fixed flap):** FAILS intent: 59.7 % fixed-skirt cut (jet rule included), 5.5 mm worst, 112/255 poses in the 5–25 mm finger trap. ID recommends a per-leg split rear skirt (thigh-fixed) with a raised pelvis hem; Robot Lab to rule. hip_skirt_r7.py/.json.
- **P-023 rev 8 (Robot Lab option i): CURRENT.** Split rear skirt per leg: a thigh panel (R150 about the pitch axis, φ 35–60, carries the rev 6b shroud) plus a spherical pelvis hem about (0,130,1045), R152.8. 44.4 % of the fixed skirt kept. Hem↔panel min 25.7 mm, no 5–25 traps; jet clear (27 mm); single-leg L/R PASS. **16 bilateral poses FAIL L↔R** (both-leg roll −20 in flexion, both-leg yaw 45): Controls bilateral keep-out needed. Shank gap: Legs CAD. Mass −0.274 (−0.076 vs rev 6). hip_skirt_r8.*
- **Rev 8b (Controls 164eeab, T&R ca68f3a):** panel inboard edge y 86 + 40 mm chamfer (L/R contact poses 488→82; worst still 0.1 → **Controls L/R keep-out 35/30/28 mm required**). Hem R 144 (28.3 mm with overtravel, PASS ≥27.5; 41.3 % fixed kept). 28 mm closed-cell PE foam edges ≤140 N on panel inboard + hem edges. Net −0.006/side vs rev 8.
- Evidence: design/cad/covers/thigh_knee_vents.py/.json/.stl; V5_COVER_SET.md P-156 section; Thermal 389f91b; Actuators D94 7d22c91.
- Rev 4d (Thermal ec7b49d): 1 mm Al-taped PC fin-tip baffle (x −56) closes the chimney; outlet aft/up z 822–860 (30 mm above the grille, H ≈ 0.18 m; the H 0.20 option declined: fairing top / skirt hem); housing-fairing 0.05 mm Al foil (fairing inner face only) + slots, local bulge +2 mm for a 10 mm gap. Mass P-156 +0.039 pair [EST] (knee-venting total +0.020).
- Affected owner response: pending (Legs CAD ROM + housing extent, Thermal areas, T&R touch/IP2X)
- Status: open

### P-157: Legs (R-146, L73): ankle_pitch dorsiflexion ROM row
- Change: CONTRACTS ROM ankle_pitch mechanical −60…+40° → **−55…+40°** (toggle at ≈ −61°; −60° has a 1.7 mm moment arm), loaded −50…+40° → **−52.5…+40°** for the kneel only; sim MJCF −0.785 → −0.916 rad (controlled) with a −0.960 hard stop.
- Evidence: modules/legs/results/r146/ankle_stop_extension.md (torque 62/44 N·m avail vs 29 N·m kneel [EST]; screw 1043/1465 N < walk peak 1734 N).
- Conditions: Actuators confirm the toggle angle and torque in 3D CAD and relieve the [EST] ankle-roll stop carrier corners (0.9 mm to the fork cheek at −45°). Controls: the extension does not reach knee-pad contact (needs ≈ −78°); the kneel still needs a CoM-ahead-of-toe drop of ≈ 90–140 mm [EST].
- D96 (Actuators da63827) 3D confirmation: toggle −61.0° at roll 0, −58.6° at roll ±18°; kneel met at −52.5° for all roll, at −55° only for |roll| ≤ ~12°. **Controls restriction: command ankle_pitch past −52.5° (−0.916 rad) only with |ankle_roll| ≤ 10°.** Carrier lowered 6 mm with R3 corners → 4.6 mm at −55° / knee 145°. Accepted R-147 (5deb2be).
- Affected owners: Actuators, Controls, Arbiter (contract). Status: open

### P-158: Torso: pack rail-end stop shoulders (R-146 ruling)
- Change: integral 7075 lips, 12 × 8 × 9 mm, on both rail ends, plus pack-side lugs. They carry 13.4 kN along the insertion axis (8.9 kN at 104 g × 1.5); the latch only retains. Sized in torso/R146_pack_shock.md §4.2: bearing 70, shear 62, bending 165 MPa against 320 (multi-path, R-128).
- Mass: **+0.010 kg [EST]** (adopted by Robot Lab). Closes the latch OPEN item.
- 25° tuck options (same file §4.1/4.4): (1) Controls caps TUCK chest pitch at 5–15° head-up: no mass, and it also fixes head clearance (≥68 mm); (2) confirm densification ≥0.75 in the R-102 lot coupon, because the 100 mm core passes 25° at 0.75 (14 %) and fails at 0.70 (8 %); (3) a further core length increase (not recommended: standout/ID).
- Status: ADOPTED (Robot Lab), Arbiter to book

### P-158: ID: thigh-front knee-pad extension (Controls 49fd991)
- Crushable honeycomb + CF + TPU strip on the thigh front, z 540–590 (s 40–90 above the knee axis), y 95–165, laps the knee pad. Covers thigh contact angles 0–50.1° (needed 2–22°). Clear of the vents, the rev 8 panel and H4. +0.028 kg pair [EST]. Legs CAD ROM check owed. Evidence: design/thigh_knee_pad_p158.json, V5_COVER_SET.md.

### P-159: Actuators: PU knee stop pair at 135° (D97), +0.263 kg robot
- **Change:** 2 laminated cast PU 90A pads per knee (30 × 30, 3 × 12 mm + shims) at r 60, tongue → clevis. Peak ≈ 1030 N·m at 6.9° stroke (max 141.9°), screw axial from the rotors ≤ 2590 N (0.095 C0a).
- **Mass:** +0.131 kg per knee, **+0.263 kg robot** (over the freeze). **Envelope:** two 40 × 40 × 41 stacks in the thigh clevis (Legs to place and sweep).
- **Evidence:** modules/actuators/results/KNEE_STOP_PU_D97.md, knee_stop_pu_d97.py/.json, cad/knee_stop_pu_pad_d97.step.
- **Gates:** Legs tongue/clevis/pad-seat check at 17.2 kN; Controls re-run with the stiffness curve.
