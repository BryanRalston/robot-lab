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
