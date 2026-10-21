# RL Actuators decision log
Format: ID, date, decision, reasoning, evidence. Estimates are marked [EST].

## Round 1 (2026-10-13), inputs P-001 to P-004 and Legs results
**D1. Design basis: size to walk and stairs, report carry margin.** Design cases are walk 0.8/1.0/1.2, stairs 18 cm, push and sit-to-stand. Need = 1.5 × gait-ID peak (rule in CONTRACTS §0). Thermal uses the walk/stairs RMS torque. Speed need follows P-002. The 20 kg carry at 1.2 m/s is a stretch case until the Arbiter rules on T5 (Robot Lab instruction). Evidence: `size.py`, `results/sizing.md`.

**D2. DC bus 13S → 20S (68.0 V min … 84.0 V max).** At 44.2 V no catalog solution reaches knee 13.3 rad/s (stairs) with 1.5× torque inside TBM2G Nmax, and hip_pitch has no solution at all. 16S works for the knee only with a heavier motor (2 × 08513D, +0.25 kg per knee). 20S gives about 25 % speed headroom on every leg joint. The cost is that every drive must be rated above 84 V, so the Everest XCR (80 V max) is out (D3). Battery 20S5P P45B = 100 cells, 1620 Wh, 8.75 kg [v3 pack factor 1.25] (+146 Wh, +0.79 kg vs 13S7P). Needs a contract change → P-005.

**D3. Drive: Novanta Everest XCR → Elmo Gold Twitter G-TWI R70/100, EtherCAT, on all 26 joints.** Specs: 70 A amplitude = 49.5 A rms continuous, 10–95 V, 22.2 g, >99 % efficiency, STO (elmomc.com/product/gold-twitter). Sizing uses the 49.5 A rms continuous limit as the peak too, so no peak-current credit is taken [conservative; datasheet peak to be read]. Effect: −15.8 g per drive and 95 V headroom over the 84 V bus. Arms, waist and neck can use the R50/100 variant (same 22.2 g package).

**D4. Fieldbus EtherCAT, 1 kHz cycle with distributed clocks. CAN-FD rejected.** Mode: CSP plus torque feedforward (or CST) at 1 kHz; current loop in the drive. Topology: one master in Brain with a 4-port junction, one line per limb plus torso/neck (6 / 6 / 7 / 7 drives). Budget: 26 slaves × ~32 B each way is about 1.7 kB per frame ≈ 15 µs on the wire at 100 Mbit/s, plus ~1 µs per slave [EST]. That fits well inside 1 ms and leaves room for 2–4 kHz. CAN-FD (5 Mbit/s data phase) carries about 64 B frames at ~15–20 k frames/s per bus [EST]. 26 drives × 2 frames × 1 kHz = 52 k frames/s would need ≥ 3–4 buses and a gateway with worse sync. Contract item §0 "Field bus" → P-005.

**D5. Twin roller-screw unit, 1.81 kg (AUDIT A5): mass arithmetic is consistent, but the unit needs revising.**
- Mass: the v3 model sums, per side, motor 0.188 + RV12 nut ~0.12 + 120 mm shaft ~0.11 + support bearing 0.08 + housing + rod ends 0.10 + 2 encoders 0.042 + drive 0.038 ≈ 0.90 kg, × 2 = 1.81 kg. The v3.2 doubling fix is applied correctly.
- Missing from that mass: the crossbar lever, trunnions and nut-rotor hub. Added +0.25 kg per hip/knee unit and +0.15 kg per ankle unit [EST, until CAD].
- Force: per screw at need, knee 328 N·m / 40 mm / 2 = 4.1 kN, hip 4.3 kN, ankle 2.2 kN. These are far below RV12x4 C0a 27.2 kN (the v3 cap is C0a/2) and Ca 17.2 kN, so the force side is plausible.
- Speed: this is the real defect. The v3 knee (06808D, 58.5 mm lever, ratio 92) needs 11 646 rpm at 13.3 rad/s, above the TBM2G Nmax of 8000 rpm. v3 never checked Nmax. A new Nmax check was added.
- Verdict: keep the twin-screw architecture and revise it to TBM2G-07613D with a 40 mm lever at the knee (ratio 63, 7963 rpm at need; 37 rpm margin is thin, see open issue O4). The same unit is used at hip_pitch with a 50 mm lever (D7). Ankle: TBM2G-06013D, 70 mm.

**D6. Knee motor inconsistency (A5): v3 had TBM2G-06808D, now superseded by TBM2G-07613D.** v3 data (`v3.json`, `v3_checks.md`, `PARTS.md`) is TBM2G-06808D. It came from REVISIONS iteration 5 (06813D → 06808D, mass reduction). The REVISIONS §F prose "TBM2G-06013D each" is stale: it predates that iteration and the D-winding twin-screw re-run. Both are replaced by D5. An erratum line was added under REVISIONS §F, and the baseline otherwise stays frozen.

**D7. hip_pitch: rotary CSG → twin roller screw (2 × TBM2G-07613D + 2 × RV12x4, 50 mm lever).** No rotary TBM2G + CSG on one drive meets 331 N·m and 8.1 rad/s at 68 V. CSG-25/32-100 exceed input rpm or torque. CSG-32-50's repeated peak of 281 N·m is below the 331 N·m need. The lightest rotary pass (TBM2G-11526D + CSG-40-50 with 70 A rms) weighs 5.7 kg vs 2.37 kg for the twin screw. The twin screw is assumed to lose 23 % of its arm over the loaded gait ROM (−76…+4°) [EST, cos 40°]. Range −120…+40° (P-003) is needed only at low torque (sit-to-stand peak 74 N·m) but must be confirmed geometrically → Legs (open O1).

**D8. hip_yaw → TBM2G-06008A + CSG-17-100; hip_roll → TBM2G-08508A + CSG-25-100.** These are the lightest that pass, with output bearing CRBH 6013 A (the v3 hip bearing). hip_yaw needs 66 N·m from stairs; the 86 N·m in P-001 comes from the carry case only.

**D9. Battery discharge limit.** Peak demand on stairs is 2.64 kW legs + 0.25 kW rest ≈ 2.9 kW, i.e. 43 A at 68 V. Decided limits: BMS continuous 60 A, 100 A for 2 s (6.8 kW at 68 V), fuse 125 A. With 5P that is 20 A per cell at the 2 s limit, against the P45B 45 A continuous rating. Per-joint peak electrical: hip_pitch 1.33 kW, knee 1.09 kW, ankle_pitch 0.99 kW, hip_roll 0.12 kW, hip_yaw 0.11 kW (carry), ankle_roll 0.03 kW. Per-limb peak 2.25 kW (stairs). The bus must absorb regen: shared-bus netting plus a brake chopper or the BMS charge path, with clamp ≤ 90 V.

**D10. Response to P-004 (power gap), with numbers.** Electrical model built from the gait time series with the selected actuators: both legs at 1.2 m/s draw 518 W with no regen and 323 W if negative joint power nets across the shared DC bus. Robot total is 772 / 576 W → 1.89 / 2.53 h on 1620 Wh. 2 h at 1.2 m/s with no regen credit needs 1716 Wh (~106 cells). 1.0 m/s passes even with no regen (2.22 h). Position: T7 at 1.2 m/s holds only with bus netting, which is physically real for a shared DC bus with simultaneous motoring/generating joints, but it is unproven here (sample-level netting, no storage). The Arbiter should rate it [EST] (×0.5).

**D11. T2 mass: 67.6 kg, over the 65 kg hard limit by 2.6 kg. This is not resolvable inside the actuator module.** Breakdown of the change: leg actuators +3.24 (incl. 1.30 [EST] linkage), drives −0.22, battery +0.79. Levers, for the Arbiter: (a) margin 1.3 for gait-ID needs (−0.52 kg); (b) CAD-verify linkage allowance (up to −1.3 kg); (c) v3 CAD solids are 56.3 kg vs the 63.8 kg rollup (REVISIONS §G), so the structure/harness/cover allowances may hold the remaining ~1–2 kg; (d) T6 at 1.0 m/s does not save actuator mass, because the knee speed is set by stairs.

## Open issues after round 1
- O1 (Legs): hip_pitch twin-screw geometry. Pelvis/thigh trunnion layout, the arm factor over the loaded ROM (0.77 assumed), and full −120…+40° clearance at low torque. A linkage study like v3 `cad/knee_linkage.py` is needed. Knee lever goes 58.5 → 40 mm, so the knee linkage factor 0.71 must be re-run.
- O2 (Arbiter): T2 is 2.6 kg over (D11). Rule on the margin (1.5 vs 1.3 for gait-ID needs) and on where the mass comes from.
- O3 (Arbiter): T5/T6. Carry at 1.2 m/s exceeds the walk/stairs sizing only through margin. Remaining carry margin: torque ratio avail/carry-peak hip_yaw 1.22, hip_roll 1.67, hip_pitch 1.32 (worst-angle), knee 1.44 (worst-angle), ankle_pitch 1.30. Speed and thermal pass with carry (max ΔT 66 K at hip_pitch). The carry is feasible on these actuators at < 1.5× margin. T7 carry runtime is 1.74 / 2.31 h (no regen / netting).
- O4 (Actuators): knee motor at 7963 rpm at the 13.3 rad/s need, against Nmax 8000. Also needed: the Rollvis RV12 max-speed rating (dN ≈ 96 k), L10 re-check at the new levers, and the Gold Twitter peak-current rating. Next round: knee lead 5 mm or a 45 mm lever trade.
- O5 (Torso/Brain placeholders): 20S pack, BMS limits (D9), regen clamp, EtherCAT master and junction.

## Round 2 (2026-10-13 PM). Inputs: R-001, R-002, R-005, R-008, CONTRACTS R1.1–R1.4
**D12. Knee rpm margin (R-005).** Rule added for all joints: motor rpm at the speed need ≤ 0.95 × Nmax (7600 rpm). The knee changes from RV12x4 on a 40 mm lever to **RV12x5 (lead 5) on a 47.5 mm lever** with the same 2 × TBM2G-07613D. Ratio is 59.7 → **7565 rpm at 13.3 rad/s**.
- Torque: 345 N·m nominal = 245 N·m at the worst linkage angle (÷0.71) vs the 231 need.
- Speed: ω30 = 16.0 rad/s.
- Thermal: ΔT 70 K walk / 82 K carry (CAD area).
- Mass: −0.39 kg per knee vs round 1, mostly from the CAD housing.
- Screw: RV12x5 has Ca 18.1 / C0a 27.3 kN (datasheet). Peak force at the need is 328 / 0.0475 / 2 = 3.5 kN per screw.

**D13. Housing mass from CAD, not the v3 formula (R-001 item 2).** `cad_mass.py` models each leg housing in CadQuery (7075-T6, 2.0 mm wall).
- Rotary: stator land, rear cap, CRBH 6013 A seat, flange with 8 × M5. Lengths are drawing values (TBM2G stack length, CSG Table 8 B).
- Screw unit: motor can plus a necked nut housing (ø41 over the nut bearings), trunnion bosses, ankle fins.
- A counted fastener + connector allowance is added (rotary 50 g, linear 24 g).
- Wall check at hip_roll: 204 N·m gives 7 MPa shear; a 3 BW × 0.1 m landing moment gives 14 MPa bending, against 503 MPa yield. The wall is set by machining minimum, not strength.
- Result: both-leg housings 4.44 → 3.34 kg (**−1.11 kg**, target −0.65). Per housing, model → CAD:
  - hip_yaw 0.355 → 0.264 kg
  - hip_roll 0.366 → 0.276 kg
  - hip_pitch pair 0.545 → 0.353 kg
  - knee pair 0.545 → 0.353 kg
  - ankle pair 0.410 → 0.422 kg (fins are now counted)
- Thermal re-run with the smaller CAD outer area: max ΔT 70 K walk / 82 K carry (knee), still ≤ 100 K.

**D14. Linkage mass from CAD (R-001 item 1): 0.61 kg for both legs, vs ≤ 0.65 kg target and 1.30 kg [EST] before.** Parts, per leg:
- 6 nut-rotor hubs, 7075, 16 g each (bolt to the RV12 ø46 flange, 6 × M5).
- 4 hollow steel trunnion pin pairs, ø16/ø9, 26 g per pair (v3 stubs were solid).
- hip_pitch tapered crossbar lever at r 50 mm: 137 g (new).
- knee lever at r 47.5 mm: 127 g, replacing the v3 shank lever (r 58.5, untapered, 167 g, already counted in Legs structure). Only the −40 g difference is booked here.
Lever check: per screw at actuator max force 4.5 kN (hip) / 3.6 kN (knee) gives 240 / 192 MPa, SF 2.1 / 2.6 on 7075 yield. Ankle levers are the v3 foot instep lever (Legs structure, unchanged); ankle top bearings are the v3 spherical bearings (in the rod-end term).
**Split and what Legs must confirm (joint item with Legs):**
- (a) The hip_pitch lever (137 g) is a Legs part on the thigh top. Its mass sits in the actuator linkage line, so Legs must not count it again. Legs to confirm trunnion position on the pelvis, lever clocking, and clearance over −120…+40°.
- (b) The knee lever r 58.5 → 47.5 mm is a Legs shank part. Legs to re-run `v3/cad/knee_linkage.py` for the new radius and confirm the worst-angle factor ≥ 0.71 (if it drops, the knee needs re-sizing).
- (c) Legs to confirm the v3 thigh no longer carries the rotary hip_pitch output flange (8 × M6 interface). That mass is not credited here.
- STEP files are in `modules/actuators/cad/`.

**D15. Datasheets attached and corrected (R-008 O4).**
- Corrections: TBM2G-07613 Km (C winding) 2.01 → 0.201 (typo in the manual itself); CSG lengths from Table 8; RV12x6 added.
- Confirmed: Gold Twitter R types state no peak current (peak "2 × Ic" applies to the non-R models), so peak = Ic 49.5 A stays.
- Rollvis publishes no max speed in its tables: open, needs a vendor query.
- Re-run of `size.py` after the corrections changed only the knee (D12).
- Details: `datasheets/SOURCES.md`.

**D16. Regen path and BMS regen limit (R-002).** Shared 20S DC bus. The BMS accepts up to 30 A regen charge (6 A per cell; P45B max charge 13.5 A per cell); a brake chopper takes any excess, clamp ≤ 90 V. `regen_sim.py` result: net bus power goes to −341 W peak (4.7 A charge), so the chopper is idle in practice. Drive losses come from the Gold Twitter > 99 % rating (56 W at 5.6 kW), split [EST] into conduction and switching. Pack IR is 60 mΩ (P45B DC IR 15 mΩ).

**D17. Runtime finding: the round-1 and R-002 averages were too optimistic.** The walk_1p2 trace includes about 1 s of standing at each end. Over the steady walking window (2–7 s):
| case | steady power | runtime |
|---|---|---|
| no regen | 942 W | 1.55 h |
| shared bus + charge | 667 W | **2.19 h** |
| shared bus + charge, end of discharge | 673 W | 2.17 h |
The whole-trace average (561 W, 2.60 h) must not be used. Conclusions:
- T7 at 1.2 m/s passes **only** with regen, and the margin is about 9 %.
- Without regen it fails by 23 %.
- Regen moves to evidence ×1.0: a time-domain bus model with drive losses, battery IR and charge limit.
- Remaining unmodelled items: motor iron loss and the drive idle split (idle is counted at 3.3 W per drive).

## Open after round 2
- O6 (Arbiter): update R1.3 to steady-state numbers (667 W with regen, 942 W without).
- O7 (Legs): re-run gait ID at the final mass (R-001 item 7). Needs rise about 3 % at 65.8 kg. Knee worst-angle 245 vs 231 (6 % margin) and ankle 311 vs 305 (2 %) are the first to break.
- O8 (Actuators): Rollvis max-speed query; screw L10 at the new levers; motor iron/eddy loss in the regen sim (G5 bench test would close it). If any of these turns out heavy, write a Grok Build brief (none needed this round; all runs take seconds on CPU).
- O9: Gold Twitter sourced price is $0.9–1.7k per drive vs $0.6k [EST] in round 1, about +$8–30k per robot (T10 is not enforced).

## Round 3 (2026-10-13 PM). Input: R-009 (half regen credit, 804.5 W, 1.81 h, T7 not met, pass line ≤ 729 W)
**D18. Motor iron loss added (`iron_loss.py`), derived from datasheet rated points.** At the same 130 K winding limit, the copper loss a TBM2G gives up between stall (Tc130) and its rated point at speed must be speed-dependent loss. Fitting the 24 V and 48 V @155 °C points gives P_fe = a·n + b·n² (n in krpm):

| motor | a | b | loss at 5600 rpm |
|---|---|---|---|
| 07613D | 1.83 | 0.195 | 16 W |
| 06013D | 1.02 | 0.058 | — |
| 06008A | 1.56 | 0 | — |
| 08508A | 1.07 | 0.489 | — |

The manual gives no no-load loss table and says static friction should not be used for rotational loss, so this rated-point method is the datasheet route. The figure includes rotor drag. The bench test (§4.1) replaces it with a no-load measurement.

**D19. Transmission back-drive efficiency now separate.** Screws use the Rollvis RV12 "indirect" η 0.88 × 0.95 (datasheet p.24). The CSG back-drive value is 0.65 [EST]. Round 2 used the forward efficiency in both directions.

**D20. Steady window is now automatic:** from 1 s after hip_pitch first exceeds 1 rad/s to 1 s before it last does. That gives 1.78–6.76 s at 1.2 m/s and 1.80–7.00 s at 1.0 m/s.

**D21. Result at 1.2 m/s with iron loss.** No regen 964 W (1.51 h); modeled regen 245 W (iron loss takes about 24 W of it); half credit 842 W (1.73 h); full regen 719 W (2.03 h). Full regen passes the 729 W line by only 10 W. Against the absolute line, realised regen must be ≥ 964 − 729 = 235 W, i.e. **96 % of modeled**, not the 77 % in R-009. R-009 used the iron-free 942/276 W numbers.

**D22. Sensitivity sweep (`regen_sweep.py`)**: 6561 corners varying:
- drive loss ×0.5–2
- iron ×0.5–2
- back-drive η ×0.85–1.1
- copper temperature factor 1.0–1.6
- charge limit 0/10/30 A
- battery 3.4 V + IR ×1.5 … 4.0 V
- torque ×1–1.06 (mass)
- cadence ×0.9–1.1

Retention at 1.2 m/s:
| statistic | value |
|---|---|
| worst corner | **0.62** (drive ×2, iron ×2, back-drive η ×0.85, hot copper, no charging, faster cadence) |
| worst, model uncertainty only (mass and cadence nominal) | 0.70 |
| 5th percentile | 0.75 |
| median | 0.99 |

**The ≥ 77 % worst-corner condition is NOT met.** Only 37 % of corners (47 % model-only) meet ≤ 729 W. The largest single factors are back-drive η (−15 % → −15 % regen), iron ×2 (−9 %), drive loss ×2 (−5.5 %) and cadence. The worst corners combine all of them pessimistically, which is unlikely in practice. Only a measurement narrows this, hence the bench test plan.

**D23. 1.0 m/s fallback (steady, iron incl.).** 1.0 m/s passes T7 at half credit on the 1620 Wh nominal pack. On the 1550 Wh minimum-capacity pack it is 4 W over the line (1.996 h).

| case | power | 1620 Wh | 1550 Wh (min-capacity pack) |
|---|---|---|---|
| no regen | 783 W | 1.86 h | 1.78 h |
| half credit | **699 W ≤ 729** | **2.09 h** | 2.00 h (1.996, 4 W over) |
| full regen | 615 W | 2.37 h | 2.27 h |

1.0 m/s sweep:
- 99 % of model-only corners and 95 % of all corners keep full-regen power ≤ 729 W.
- Retention minimum is 0.59 (0.67 model-only).
- At the worst model-only corner, P_regen is 709 W, still ≤ 729.

0.8 m/s passes even with no regen (626 W, 2.33 h).

**D24. Bench plan drafted** (`BENCH_TEST_PLAN.md`): one-leg, 4-quadrant load rig, shared 20S bus or battery emulator, A/B/C bus configurations, stride-synced DC energy. Pass: P1 netting ≥ 213 W robot-equivalent and P2 ≤ 729 W absolute.

## Open after round 3
- O10 (Arbiter): the pass condition in R-009 should be absolute, P ≤ 729 W (96 % retention with iron loss), not 77 %. The sweep shows that 1.2 m/s cannot be shown robustly in simulation. Recommend ruling the T6/T7 trade now, with **1.0 m/s as the 2 h rating speed** and 1.2 m/s as a burst/shorter-duration speed; bench results still go in.
- O11 (Legs): export the forward-sim gait in regen_core format (b) (`t`, `tau[N,12]`, `omega[N,12]`, LEG order L then R) once 1.2 m/s walks. Then run `python3 regen_sweep.py <path>`.
- O12 (Torso placeholder): the 1550 Wh minimum-capacity pack fails 1.0 m/s half credit by 4 W. Either cell binning or a 2 % pack-usable increase (90 → 92 %) closes it.

## Round 3b (2026-10-13): hip_pitch lever (config B), clearance, pivot bearing
**D25. hip_pitch lever re-designed for the thigh-mounted layout (L10 config B, screw half-spacing 69 mm): 0.371 kg, SF_yield 2.13 (CPU FEA).**
- New topology (`hp_lever_fea.py`, `cad/hip_pitch_lever_B.step`): round hub ø56 / bore ø40 clamped on the pelvis-side shaft, ø50 spigot carrying the pivot-bearing inner ring, two smooth 3-section lofted arms (root 44×30 → 30×30 → 25.5×18 mm), ears ø26×12, pressed steel pins ø12×25 (single shear, rod-end at y ±69). R2 fillets at the arm/hub-face junction.
- FEA: CadQuery → gmsh → scikit-fem P2 tets (h 4 mm, 5.2k nodes / 18.8k tets; the box had <1 GB free, so finer meshes OOM'd), pyamg CG to 1e-8. 4542 N per screw (454 N·m / 50 mm / 2), force direction φ = −90…+90° from tangential (loaded ROM −80…+40° is |φ| ≤ 60°), symmetric and one-screw-fault cases.
- Worst: symmetric φ −60° 237 MPa max, **SF 2.13** (p99.9 183 MPa → 2.75); fault 2.41; tangential φ 0° SF 4.35. Hub max 293 MPa next to the clamped bore (support-adjacent; SF 1.72 there, p99.5 150 MPa).
- Mesh caveat: the peak is at the arm-root junction and rose 250→343 MPa from h 3.5 → 3.2 before the fillet was added. Treat SF 2.13 as ±15 %. A converged run at h ≤ 2 mm, with the fillets drawn, is needed (Grok Build or a box with ≥4 GB free).
- Fatigue (walking peak per screw 2377 N = 0.52 × max, σ ≈ 93 MPa, fully reversed, 7075-T6 Se 159 × 0.8 = 127 MPa at 5e8): SF 1.37. Goodman R=0: 2.2.
- Pin deflection under max load 0.20 mm. Material stays 7075-T6; Ti-6Al-4V would be +58 % mass for the same SF.
- Mass vs Legs' 0.167 estimate: +0.204 kg/leg. Breakdown: the bearing spigot/hub (~0.11), steel pins (0.044) and arm sections sized for the radial φ ±60…90° case, which the crossbar estimate left out.

**D26. Clearance (`hp_clearance.py`, `results/hp_clearance.json`).** L10 layout (ø32 boss in the screw plane):
- 2.69 mm nominal at −80° (4.01 at the −78° L12 limit). Stack: pins 0.35 + lever deflection 0.20 + rod bow 0.10 + bearing play 0.05 + OD tolerances 0.10 = 0.80 mm → **1.89 mm worst case, < 2 mm**.
- Full −120…+40°: the screw line passes through the pivot at the toggle **−114.5° (−21.8 mm, hard clash; arm 0.5 mm, stroke reversal)**.
- Fix adopted in D25: nothing of the pivot (hub, bearing, femur tongue) outside |y| ≤ 22 mm. Rods run at |y| 63…75 → **41 mm lateral clearance at every angle**. Ear-to-rod-end axial gap 1.0 mm → add a 1 mm spacer washer (2 mm).
- The mechanical stop must stay ≥ −105° (toggle at −114.5°) → Legs/Arbiter.

**D27. hip_pitch pivot bearing is now Actuators-owned: IKO CRBH 5013 A (50×80×13, 0.29 kg, C 17.3 kN, C0 20.9 kN; `datasheets/iko_crb_catalog.pdf`).**
- Loads: 2 × 4542 N + 1.5 BW + M = 192 N·m (hip_roll 180 / yaw 66 needs) → static fs 1.30. One-screw fault +313 N·m → fs 0.99.
- Walking life L10 23 700 h. CRBH 4010/4510 are rejected (fs 0.61 / 0.67); CRBH 6013 would give fs 1.59 for +0.04 kg.
- Line: 0.314 kg/leg (bearing + clamp ring + 6 × M4 [EST]).
- Legs: femur tongue seat ø32 → ø80 H7 × 13; tongue stays inside |y| ≤ 12.5.

**D28. Ankle lever 77 mm (R-011): not adopted. 73 mm is the maximum under R-005.**
- 77 mm gives 341.6 N·m (1.21× carry at 1.2 m/s), but the motor needs 7993 rpm at the 6.92 rad/s speed need = 99.9 % Nmax > 95 %. Max lever for 95 % is 73.2 mm (323.8 N·m, 1.14× at 1.2 m/s).
- With carry rated at 0.8 m/s (R-011) / 1.0 m/s (Legs L11, 238.3 N·m), 70 mm already gives 1.41× / 1.30×, so keep 70 mm.
- Stroke +10 % and mass +0.003 kg at 77 mm. Clearance not checked; Legs owns the instep geometry. `ankle_lever.py`, `results/ankle_lever_77.json`.

**D29. One linkage table (R-013): `results/LINKAGE_TABLE.md` (`linkage_table.py`): 1.263 kg/leg, 2.527 kg both legs vs 0.609 contract.**
- Accepts Legs L14 (knee-lever credit dropped, ankle lugs).
- Closes the trunnion risk as real: 6 pin pairs/leg.
- Adds rod-end eyes 6 × 0.025 [EST], the R3b lever and the pivot bearing.
- Open: the thigh trunnion clamp (Legs).

**D30. Mass rollup: 65.79 → 67.71 kg CAD-supported.**
- Actuators R3b hip_pitch: +1.096 (lever +0.468, bearing +0.628). Linkage corrections: +0.822.
- 66.35 kg if Legs structure and Torso −0.80 land. **T2 NOT MET; P-012 opened.**

**D31. Battery placeholder (`battery_bin.py`).**
- Published 0.2C P45B capacities (n = 6, three sources): mean 4479, sd 14 mAh. Yield ≥ 4400 mAh: ≈ 100 % (published sd), 97 % (sd ×3 for lot spread), 84 % (conservative 4450 / 50).
- Usable to 3.4 V at 1.94 A/cell: 0.91 [EST] (range 0.88–0.93).
- 1.0 m/s half credit, binned-minimum pack: 2.06 h (1.99 h at 0.88, 2.11 h at 0.93). 1.2 m/s half credit: 1.71 h.
- Bench must measure the usable fraction.

## Open after round 3b
- O13 (Grok Build): converged lever FEA, h ≤ 2 mm with drawn fillets, SF target 2 (D25).
- O14 (Legs): pivot structure inside |y| ≤ 22, femur seat ø80, mechanical stop ≥ −105°, thigh trunnion clamp mass (D26/D27/D29).
- O15 (Arbiter): T2 67.71 kg (P-012).

## Round 4 (2026-10-13): M1 cuts, M3 harness, emulator RFQ (R-016/R-017, limit 66.5 kg)
**D32. M1(a) needle straddle (`hp_pivot_needle.py`): −0.153 kg both legs (target −0.20).**
- Two IKO TLA 3520 Z (35×42×20, 43.5 g, C 20.7 / C0 42.3 kN; `datasheets/iko_shell_needle_catalog.pdf`) sit in the lever cheeks (span 47 mm) on a case-hardened 16MnCr5 shaft ø35/ø30 × 67 pressed into the femur tongue. PTFE/bronze thrust washers + circlips.
- Static fs 4.65 at max (9.1 kN per bearing) and 3.13 in the one-screw fault, both ≥ 3 (IKO shell rule). L10 280 000 h walking. Shaft bending 110 MPa.
- Line 0.237 vs 0.314 kg/leg. The shaft (0.134) is the cost; a thinner wall would fail the raceway case depth.

**D33. M1(b) lever SF 2.0 → 1.5 with the new needle cheeks: 0.249 kg/leg (was 0.371), −0.245 both legs (incl. hub change).**
- FEA (HUB=needle, h 4 mm): SF 1.51 at φ −60° (fault 1.54), pin deflection 0.16 mm. STEP is `cad/hip_pitch_lever_B_needle_sf15.step`.
- The lever is now two halves joined by the hip-roll yoke; nothing sits in |y| < 13.5, where the femur tongue is.
- Lateral clearance to the rods is 29.5 mm.
- Proof test: `results/PROOF_TEST_hip_lever.md` (100 % at 1.25 × design, qualification to 2 ×).
- O13 is NOT closed: < 1.5 GB was free and h = 3 swapped, so it was killed. Brief: `results/GROKBUILD_lever_fea_converged.md`.

**D34. M1(c) margin 1.3 for hip_roll / hip_pitch: 0 kg.** `sizing_m1.3.json`:
- hip_roll at 1.3 picks TBM2G-07608A + CSG-25 at 1.500 kg vs 1.455 at 1.5. Heavier: the catalogue steps don't go down.
- hip_pitch at 1.3 picks TBM2G-06813D at arm 65 mm, 2.171 vs 2.154 kg. Heavier, and it would undo the 50 mm lever/clearance geometry.
- Keep the current units. The carry checks at 1.0 m/s still pass (hip_roll 204/112 = 1.82, hip_pitch 454/230 = 1.97). The R-016 [EST −0.30] does not exist.

**D35. M1(d) housing CAD: 0 kg new.**
- No unit changed (D34), so there are no new housings.
- The ×1.25 [EST] housing factor was already replaced by CAD in round 2 (D13, −1.11 kg in the 65.79 base). R-016's "≥ −0.40" would double-count it.

**D36. M1(e) rod ends: +0.120 kg both legs.**
- Catalogue SKF SIKAC 12 M (0.118 kg, C0 14 kN, fs 3.1) is rejected for mass.
- Chosen: SKF GE 12 E spherical plain bearing (0.016 kg, C 10.8 / C0 54 kN, fs 11.9; `datasheets/skf_ge12e.pdf`) in a 7075 eye ø30 × 12 with an M12 boss (0.019 kg calc) = 0.035 vs 0.025 [EST], × 12.

**D37. M1 total −0.278 kg vs −1.00 target.** The linkage table is now 2.249 kg both legs (`LINKAGE_TABLE.md`). Shortfall 0.72 kg: margin and housing were paper credits (D34/D35).

**D38. M3 harness (`harness.py`, `results/harness.md`): 0.821 kg vs ≤ 1.46 target (contract 2.00) → −1.179 kg.**
- 20S star to 4 limb trunks: leg 12/14/16 AWG tapered (peak 33.2 A, rms 7.0 A), arms 16/18 AWG.
- EtherCAT daisy chain 4 × 26 AWG at 14 g/m [EST], 34 drives on the actuators, short phase/encoder leads.
- Connectors: Amass XT60/XT30/MR30/AS150U, JST-GH for EtherCAT.
- Worst voltage drop 0.30 % at peak; worst conductor ΔT 10.8 K (24 V compute feed).
- Evidence [EST]: vendor-typical g/m and connector masses, lengths ±20 %. Credit at ×0.5 until datasheets and a routed CAD harness exist.

**D39. Rollup: 67.91 (R-016) − 0.278 − 1.179 = 66.45 kg vs 66.5 hard (0.05 reserve). It becomes 65.09 if Legs structure and Torso −0.80 land.** At ×0.5 harness credit it would be 67.04 (over).

**D40. Emulator RFQ drafted, not sent (`results/RFQ_ITECH.md`).** Route: AV-TEK (US distributor) sales@avtekconsulting.com, ITECH direct info@itechate.com as fallback.
- Flag: the IT6005C-80-150 is an 80 V class unit and the bus reaches 84 V. The RFQ asks the vendor to confirm 84 V operation, else the 300 V class.

## Open after round 4
- O13 converged lever FEA (Grok Build brief).
- O16 harness datasheets + routed lengths (Legs/Torso geometry).
- O17 Legs: tongue bore ø35 press-fit; yoke joining the two lever halves.
- O18 RFQ send (Bryan).
- O19 M1 shortfall 0.72 kg: no further actuator lever without a T5/T6 trade.

## Round 5 A2 (2026-10-13): O16 harness datasheets + routed lengths (R-018)
**D41. Harness model rebuilt on datasheet g/m and v3 CAD routed lengths (`harness.py`, `results/harness.md`, `results/harness.json`): 1.314 kg.**
- **Routes.**
  - Coordinates come from `v3/cad/model.py`: the hip yaw/roll/pitch, knee and ankle chain points; the pack and compute bounding boxes; shoulder, neck and waist from P.
  - Straight runs are Manhattan distance × 1.15.
  - Each crossed joint gets a clock-spring loop of r_wrap (`v3/cad/out/cables.json`) × ROM + 50 mm, and each drive gets an 80 mm pigtail.
  - The per-run table is in harness.md. Completeness runs are now modelled instead of the 0.10 allowance: foot F/T on the leg EtherCAT branch, hand/tactile on the arm branch, 2 head-camera quads, IMU, and the e-stop loop.
- **Cables.**
  - Power: Lapp ÖLFLEX HEAT 180 SiF. Gauge is auto-chosen per run: ΔV ≤ 2 % series at peak, ΔT ≤ 30 K at rms with a 2× bundle factor, 0.5 mm² floor on bus runs. The result is leg trunk 2.5 mm², thigh 2.5 mm², shank 1.0 mm².
  - EtherCAT: GORE GSC-03-84820-00 at 23 g/m. The R4 [EST] was 14 g/m, so this raises the mass.
- **Mass blocks.** Power wire 0.533, EtherCAT/data 0.346 (wire + data = 0.886, datasheet × routed), connectors 0.301, sleeving 12 % 0.106 [EST], EtherCAT junction 0.020 [EST].
- **Checks.**
  - Worst ΔV is 0.77 %, against the 2 % limit.
  - Worst ΔT is 15.8 K, against the 30 K limit.
  - Drum bend radius is r/OD ≥ 10.3 at every moving joint.
- **Flex life is not qualified.** SiF is datasheet-rated for fixed install only. GORE quadrax has a static 15 mm bend rating and no published cycle rating. The flex-rated igus CFBUS.040 (7 mm, 59 g/m) would need r ≥ 70 mm, which does not fit the drums, and would add 0.18 kg on the 5.1 m of loops. → O20.

**D42. Credit per R-018: essentially none; the R4 [EST] model was optimistic.**
- Moving from [EST] to datasheet-backed values roughly doubled wire + EtherCAT: 0.435 → 0.886 kg.
- **Claim:** model value 1.314 vs R-018 credited 1.344 → **−0.030 kg**. Credible robot 66.976 → **66.946 kg, 0.45 over 66.5.**
- If the R-018 half-credit rule is applied to the remaining 0.252 kg of [EST] items (JST-GH/AS150U masses, sleeving, junction), with listed connectors at ×1.2, the harness is 1.530 → +0.186 → 67.16 kg.
- The −0.52 kg A2 potential is **not** available. A1 (Legs −0.81) remains necessary.

**D43. AS150U 2025V0 is rated 80 V DC, below the 84 V bus max.** Pack main connector needs the 500 V-rated AS150U (older 2+4 spec) or an XT90-class part; mass impact is small [EST].

**D44. ITECH RFQ parked (Robot Lab, R5).** Theoretical project, so no vendor contact. `RFQ_ITECH.md` is marked PARKED. The emulator stays [EST] from published ITECH specs. O18 is closed.

## Open after round 5 A2
- O13 converged lever FEA (Grok Build, untouched).
- O17 Legs: tongue bore ø35 press-fit; yoke joining the two lever halves.
- O20 (new) clock-spring flex-life qualification for SiF + GORE quadrax (1e6 cycles, full ROM, r_min), or a thinner flex-rated EtherCAT cable.
- O21 (new) connector masses to be weighed (JST-GH, AS150U); ROMs other than hip pitch are [EST] human-range values.

## Round 5b (2026-10-13): ankle 73 mm, thigh clamp review, linkage cleanup, O20/O21
**D45. Ankle_pitch lever 73 mm adopted (Robot Lab; P-014).**
- Change: `size.py` ARM_FIX 0.073. Unit unchanged: TBM2G-06013D + 2× RV12x4, 1.78 kg.
- T_out 323.8 N·m vs the 66.5 kg need of 314 (Legs L20) → **1.03×**.
- Carry at 1.0 m/s: 323.8 / (239.1 × 66.5/65) = **1.32×** (≥ 1.2).
- Motor speed: 7578 rpm vs 7600 (95 % rule) → **passes with only 0.3 % margin**.
- Thermal: ΔT_cad 31 → 28 K; carry 43 → 39 K.
- Mass: stroke +4.3 %. Two RV12 screws +4 mm and two body tubes +4 mm = +0.013 kg/leg (calc, linkage table). There is no Actuators ankle lever solid. Legs moves the instep-lug pin radius 70 → 73 mm.

**D46. Thigh split-collar clamp (Legs L18): agree on form and FEA; counter on retention (`clamp_review.py`, `results/clamp_review.json`).**
- **Loads.** Body angle to the femur is −15.3…−7.0° over −105…+40°. Both bodies together give 8764 N axial and 2390 N transverse at max force.
- **Friction-only collar fails.**
  - At μ 0.15 with SF_slip 1.5 it needs 87.6 kN radial, i.e. 18.6 MPa on the ø50 × 1.2 tube.
  - That is 378 MPa hoop stress: SF 1.06 against 7075 yield including ±25 % torque-tightening scatter. The long-tube collapse pressure is only 2.4 MPa.
  - Bolts could deliver it (13.9 kN per side, 2× M6 10.9), but the tube cannot take it.
- **Counter.** Bond the collar to the femur (DP490-class epoxy, τ 1.86 MPa, fatigue SF 3.2 at 20 % of lap shear [EST]) plus a light clamp at ~3 MPa (hoop 61 MPa). Alternatively, add an internal 7075 sleeve or plug under the collar, or seat the collar on a machined femur collar shoulder. Mass +~0.003 kg adhesive.
- **Spherical eye, SKF GE 12 E.**
  - Static s0 = 11.9.
  - Walking p = 21.9 N/mm² (K 100). G_h ≈ 3400 h at 1 Hz when relubricated (steel/steel). Use the maintenance-free variant or set a relube interval.
  - Swing ±4.1°: plain rotation if the pin is parallel to the hip axis, otherwise tilt within α 10°.
  - Pin ø12 42CrMo4 in single shear: τ 40 MPa, bending 241 MPa → SF 3.1.
- **Clamp fatigue.** Legs FEA 174 MPa max × 0.52 gives SF 1.76 on Se 159 [EST]; p99.9 gives 2.66. Accept, pending the Grok Build refinement.
- **Mass.** "Two fewer pin pairs" is not a saving. −2 pin pairs (0.026 each) + 2 eyes (GE 12 E + eye + pin, 0.060 each) = **+0.068 kg/leg**. A GE 10 E with a ø10 pin would save ~0.012 kg per eye (s0 still > 6); this is offered to Legs.

**D47. Linkage table.**
- Ankle-lug row zeroed (−0.084 both legs). It is in the Legs M2 line (L19); the rollup already counted it once, so the rollup impact is 0.
- Thigh clamp row marked as in the Legs M2 line.
- Trunnion pin pairs 6 → 4 per leg. Hip-body eyes +2 per leg. Ankle 73 mm row added.
- Linkage both legs 2.249 → 2.326. Net vs R-018: **+0.161 kg**.

**D48. Harness line now generated from data.** `linkage_table.py` reads `results/harness.json` and writes `results/mass_rollup_r5b.json`. Re-running verified that it persists, and the hand-appended line is gone.

**D49. O20 flex cable.**
- EtherCAT is now **Belden MachFlex MRTA2P26S** on every branch: 4.2 mm, 25.9 g/m, 8e6 bend at 7.5D and 8e6 torsion. Minimum drum r/OD is 8.1 ≥ 7.5.
- Power cores inside the loops are **Stäubli SILI-E** (class 6).
- Δ **+0.053 kg** (EtherCAT +0.044, SILI-E +0.003, sleeving +0.006).
- Lighter Ethernet-rated flex cables (Lapp ETHERLINE Flex, igus CFBUS) need r 70–84 mm and do not fit the drums.
- Still open: O20a, a power-loop cycle test (Stäubli gives no cycle rating), and O20b, a TDR/EtherCAT link test (MachFlex has no 100 Ω specification).

**D50. O21.**
- Joint ranges now come from the v3 MJCF (hip pitch −105…+40, knee 0…135, shoulder pitch −180…60 etc.); hip roll is 27°.
- AS150U: 41.4 g/pair, from a distributor listing.
- JST-GH: 0.5 g/pair, calculated from datasheet dimensions (was 1.2 [EST]).
- Harness **1.296 kg** (was 1.314) → −0.048 vs R-018's 1.344.
- **O21 is closed, except that the JST-GH mass is a calculation, not a weighed value.**

**D51. Rollup R5b.** R-018 credible 66.976 + 0.161 linkage − 0.048 harness = **67.089 kg, 0.59 over 66.5**. With Legs A1 (P-014 4.79 kg, −0.868 provisional) it would be **66.22** (reserve 0.28).

**Conflict flag.** Legs L17 confirms a ø80 femur seat for the CRBH 5013. Actuators replaced that bearing with the needle straddle in R4 (D32/O17: tongue bore ø35 press-fit, two lever halves + yoke). Legs and the Arbiter need to resolve which design holds.

## Open after round 5b
- O13: converged lever FEA (Grok Build).
- O17: ø35 vs ø80 seat conflict (see the flag above).
- O20a: power-loop flex test.
- O20b: MachFlex EtherCAT TDR/link test.
- O22: Legs adopts bonded clamp retention, and optionally GE 10 E eyes.

## Round 6 (2026-10-13, R-020): A8 eye life, A9 JST-GH + O20 plans, A5 ankle stroke/L10
**D52. A8: the SKF GE 12 C maintenance-free eye is a wear part (`life_r6.py`, `results/life_r6.json`).**
- **Method and inputs.**
  - SKF steel/PTFE sintered bronze: G_h = b1 b2 1400/(p^1.3 v), with b1 0.2 (alternating 0.5–5 Hz, catalogue Table 6) and b2 1.
  - p = K P/C, with C 11.4 kN and K 100. P is the 1.3-power time mean of the screw force from Legs' gait-ID torques at 66.5 kg.
  - v = 5.82e-7 · 18 · β · f, where β is half the body swing per stride (3.1–5.6°) and f is 33–67 min⁻¹.
  - Duty mix [EST]: walk 1.0 60 %, walk 1.2 15 %, carry 15 %, stairs 10 %.
- **Result.** p 4.3–8.3 N/mm²; G_h 7 600–21 500 h per scenario, **10 600 h combined < 14 600 h (T9)**. The peak p is 26 at the gait peak and 39.8 at the actuator max, both ≤ 40 permitted.
- **Correction to D46.** The steel/steel 3400 h used f = 1 min⁻¹. The true f is about 60 min⁻¹, so the relubricated steel/steel life is far lower. The PTFE C design is clearly the right choice.
- **Wear-part definition.**
  - Replace every **5 250 h**, i.e. 50 % of the mean wear life G_h. That is ≈ 1.8 y at 8 h/d, so 2 replacements over the T9 life.
  - The spare is an **eye subassembly**: GE 12 C pre-pressed into the 7075 eye, with a new ø12 pin and circlips. It is 0.060 kg (no change on the robot: GE 12 C 0.016 kg = GE 12 E 0.016 kg).
  - Cost [EST]: GE 12 C $17.20 + eye $25 + pin and clips $5 ≈ **$47 per eye, $190 per robot per interval**. Spares line: 4 per robot per 5 250 h.
- **Procedure (about 30 min per leg).**
  1. Robot on the stand, hip_pitch actuator de-energised, and the hip held at 0° by the stand strap.
  2. Remove the femur clamp-arm circlip and press out the ø12 pin; the screw body swings free on its lever-end rod end.
  3. Unscrew the eye subassembly from the body end (M12 thread + jam nut, Loctite 243).
  4. Fit the new eye, set the length to the gauge mark ±0.1 mm, refit the pin and circlip, and witness-mark it.
  5. Run the 5-cycle hip-sweep check: current trace vs baseline, and no knock.
- **Inspection between replacements.** Check axial/radial play every 1 000 h with the dial-gauge procedure. Replace early if radial play > 0.15 mm (the SKF PTFE liner wear limit is about 0.2 mm).

**D53. A9: JST-GH mass from published distributor weights (there is no scale).**
- Mated 4-pin pair = TME weights GHR-04V-S 0.079 g + 4 × SSHL-002T-P0.2 0.021 g + BM04B-GHS-TBT 0.221 g (gross) = **0.384 g**. The GAM-GEC listing gives 0.32 g.
- Method: distributor unit or gross weights. **Uncertainty ±0.06 g per pair (±15 %)**: TME gross weights include packaging share, GAM values are rounded. JST 3D CAD was not used (it needs registration).
- Model mass uses 0.384 g × 80. Harness **1.286 kg** (was 1.296). This is datasheet/listing grade, so credit ×1.0 per R-020 §6, which releases the held +0.028 and adds −0.010 → **−0.038 vs R-020's 1.324 credited**.
- O20 test plans are in `results/O20_TEST_PLANS.md` (rigs, cycle blocks 1e6 full-ROM + 6e7 gait, pass criteria).

**D54. A5: ankle at 73 mm, stroke and L10 (`ankle_stroke.py`, `life_r6.py`).**
- **Stroke.** v3 CAD layout at P['ankle_lever'] 73, over pitch −45…+40 × roll ±25:
  - **118.6 mm** (114.4 at 70 mm).
  - Shortest pin-to-pin length 260.6 vs need 257.6 (motor env + nut 36 + housing 60 + stroke + rod end 14) → **margin 2.9 mm** (was 9.8). It passes, but it is tight.
  - Fix if the build shows less: limit roll at full dorsiflexion to ±22°, or shorten the rod end by 3 mm with a GE 12 C eye in place of the M12 boss.
- **L10 of the RV12x4** (Rollvis Ca 17.2 kN, C0a 27.2 kN).
  - Per-screw force F = τp/(2·0.073) ± τr/(2·0.040), and revolutions from the joint speeds over the lead, under the same gait mix at 66.5 kg.
  - Cubic-mean Fm is 350–445 N and peak 1.73 kN → **L10 ≈ 544 000 h ≫ 14 600 h**.
  - Static: C0a/F_gait peak 15.7. At the actuator max (2.22 kN per screw) it is 12.3.
- No fix needed for life. **R-020 C2a is closed.**

**D55. Rollup (R-020 basis, `results/mass_rollup_r6.json`, generated by `linkage_table.py`).** 66.89 + 0.000 linkage − 0.038 harness = **66.853 kg, 0.35 over 66.5**. With A1' (Grok Build FEA, −0.596) it would be **66.257** (reserve 0.24 < 0.30).

## Open after round 6
- O13: lever FEA (Grok Build).
- O20a/O20b: run the plans.
- O23: eye wear part. Confirm G_h with a bench wear test, run in the O20 rig with the eye loaded at 2.4 kN alternating.

## D58 (O13b) hip_pitch lever v2: box study stopped, Grok Build brief issued
- New `hp_lever_fea_v2.py`:
  - The bore clamp is gone. The bearing reaction is a cosine pressure on each needle bore, and the yoke face |y| = 13.5 carries the pitch torque.
  - Gmsh Ball local refinement at the hot spots, P2 elements.
  - Fault cases on both sides, 21 cases in total.
- B1 trial (cheek RO 28, R3 junction fillet, bore pocket +5 mm with an R5 end torus), h 4 / local 2:
  - Peak 583 MPa at sym φ+60, 581 / 575 MPa in the fault cases. Mass 0.2883 kg. **Rejected.**
  - The undercut thins the arm root.
- The O13 hot spot is a real 90° re-entrant corner where the arm root overlaps the bore end. The fix has to be topological: an end cap with a filleted pocket (G2), or a flange-mounted root (G3).
- Not feasible on the box: about 1.1 GB free, and the 64k-dof run already used 865 MB. Brief: `results/GROKBUILD_lever_fea_v2.md` (geometry G2/G3, mesh plan to 0.7 mm or a submodel, three stress measures, pass criteria).
- O13 stays open. The mass line is unchanged at 0.2492 kg each. The −0.245 kg credit stays gated.
- Envelope: D25's 41 mm figure belongs to the CRBH hub. With the needle cheeks it is already 29.5 mm, and G2 would make it 24.5 mm. Legs needs to confirm.

## D59 (v4 audit) Knee: merged twin housing (option a)
- **Option a: one housing with a shared centre web.** Each half has only its outer boss. A 6 mm web with 3 mm flanges runs over the motor section to the mid-plane.
  - The two screws sit on one trunnion axis and stay in phase, so this is kinematically free.
  - The inner bosses were never supported (the bracket has outer cheeks only).
  - Mass: 0.305 kg vs 2 × 0.153 kg, which is −0.0013 kg/leg.
  - Model v4 (patched): no clash at knee 0…135° in 15° steps.
- **Option b, wider spacing (dy 50):**
  - Kinematics are planar, so lever r47.5, the 95% rpm rule and torque are unchanged.
  - The crossbar gets longer: σ 192 → 208 MPa, SF 2.62 → 2.42, lever +0.006 kg.
  - Inner trunnion support plates are needed (Legs, about +0.03 kg).
  - The leg gets 10 mm wider.
  - **Rejected.**
- STEPs: `knee_twin_housing.step` (one piece) and `knee_body_x1.step` (one half; mirror it for the −y screw).

## D60 (v4 audit) Ankle end joints: spherical top eye + high-misalignment bottom rod end
- **Kinematics (1° grid, pitch −45…+40 × roll ±18):**
  - The body tilts 1.8° out of plane.
  - The real problem is at the bottom eye: rod-to-instep-pin misalignment reaches **19.6°**. SKF GE 12 C allows α 10° (SKF product page).
- **Cardan gimbal at the top: rejected.**
  - It locks spin to the shank, but the bottom then still needs 19.6° plus spin.
  - The gimbal ring (about 8 mm/side) doesn't fit between the bodies and the 12 mm centre plate at dy 45.
- **Spherical top eye + U-joint bottom: rejected.** The top GE would need 15.7°.
- **Adopted:**
  - **Top:** axial GE 12 C eye in a lug behind the rear cap, held in a shank clevis with a 0.6 mm side gap. That gap limits spin to ≤ 2.3°, giving a top tilt of 2.8° vs α 10°.
  - **Bottom:** high-misalignment PTFE rod end, QA1 MGF12T class: ball 22.23, ball width 16, head ø30 × 10.75, 27°, C0r 17.4 kN. Demand is 20.8° including spin, so 6.2° margin.
  - **Spacer:** 4.5 mm spacer to the lug. Head axial excursion is 10.35 mm, so clearance to the lug face is 2.15 mm over the full grid. The rod-end shank starts above the lug top.
  - **Anti-rotation:** an internal key against a flat on the rod. The unit is S-P-S, like the hip.
- **Stroke:** the eye pivot is 36.1 mm further from the body than the old boss pivot, so the trunnion moves up 40 mm (z 410 → 450).
  - Lmin 301.6 / Lmax 414.2, stroke 112.6, need 287.7.
  - Margin 13.9 mm (about 12.9 by the Arbiter's method).
- **Life (SKF G_h method):** C_est 21.5 kN [EST, no maker dynamic rating], gives G_h 8 523 h, below T9 14 600.
  - **Wear part: replace every 4 250 h.**
  - Peak load is 0.10 C0r.
  - Needs a supplier rating or a bench test (G5).

## D61 (v4 audit) Ankle body STEP
- The bosses that overlapped the fins (fins z 6–36 vs bosses z 11–31) are removed. The axial eye lug is added at z −15.
- The solid is valid (BRepCheck), single. Mass 0.1875 → 0.192 kg.
- Separate fix: trunnion bosses were tangent to the can (a separate solid in STEP). They now sink 1 mm into the wall in every body that keeps them.

## D62 (v4 audit) Hip body clearance
- Model v4 measured the hip_pitch body at **≥ 3.0 mm** to every thigh part over −105…+40° in 15° steps:
  - femur tube 3.0 mm (lateral, constant)
  - collar 7.7–10.7 mm
  - clamp arm root ≥ 8.9 mm
- I couldn't reproduce the audit's 0.3 mm. It's a hand note in `audit_v4.py`, not a measurement.
- Envelope trim anyway: the unused trunnion bosses are removed from the hip body (it mounts on the axial eye, P-014). That saves −0.010 kg each.
- Net actuator delta for D59–D62: **+0.069 kg/leg, +0.138 kg both legs** (`results/v4_deltas.json`). Pending P-018.

## D63 (Legs L37–L40 reply) Ankle top clevis fit, tine ligament, instep lugs
- **Fit: yes, with one correction to the numbers.** 10.75 mm is the QA1 *bottom* rod-end head width. The top lug carries a GE 12 C (B 10, C 7) in a 10 mm lug.
  - Stack in the 11.95 slot: inner ring 10 + 2 × 0.8 mm PTFE-faced steel thrust washers. The washers bear on the inner ring only. Total 11.6, so 0.35 mm axial float.
  - Relieve the lug body to 8.0 mm (C 7 + 0.5 per side) so it can't touch the washers. Rim clearance is then 1.0 mm per side, which allows 3.8° of tilt or spin about the lug edge (r 15).
  - Need: 2.8° combined, i.e. 0.73 mm at r 15. Margin 0.27 mm.
  - Spin ≤ 3.8° keeps the bottom misalignment ≤ 23.4°, vs the 27° rating.
  - The lug mass change is negligible (−0.002 kg/leg, not booked).
- **Tine ligament: passes.** Tines are 7075-T6, 6 thick × 30 wide, ø12 hole, 12 mm from the pin centre to the tine end (ligament 6 mm).
  - Max actuator force per screw: 323.8 N·m / 0.073 / 2 = 2218 N (motor-peak limited; the roll case is 2212 N). That's 1109 N per tine.

| Check | Stress (MPa) | SF |
|---|---|---|
| Bearing | 15.4 | 21.8 vs 1.5·Sy |
| Tear-out (2 shear planes, 6 × 6) | 15.4 | 18.8 vs 0.577·Sy |
| Net section | 10.3 | — |
| Net section peak (pin-lug Kt 3.5) | 35.9 | 14 on yield, 3.5 on fatigue (127 MPa) |

  - No change needed. Keep the edge distance at 12 or more, and fillet the tine root at R3 or more.
- **Instep lugs: keep Legs' outboard position** (outrigger, +0.031 kg/leg). Moving them inboard would erode the 2.15 mm head clearance (D60). The lug face has to stay at least 12.5 mm from the eye mid-plane, so inboard is not better.

## D64 (A25, Electronics 1e33c96 §7.3) Harness: neck-crossing conductors owned by M3
- `harness.py` now reads `results/v3_cables.json`, a copy of `v3/cad/out/cables.json` at a98ba03. R-029 (da6a72f) deleted `v3/cad/out`.

| Item | Change | kg |
|---|---|---|
| 1 | Delete "head cameras data 2× quad" | −0.0241 |
| 1 | Add one GMSL2 coax, HUBER+SUHNER ENVIROFLEX_178 (RG178 class, 50 Ω, ø1.84, 6.5 g/m), 0.564 m | +0.0037 |
| 2+3 | ECAT run cut to the waist only (2 taps), 0.0172; RS-485 FD reuses the MachFlex quad to the head, 0.0120. Was 0.0354 | −0.0062 |
| 2 | Neck/head 0.75 mm² pair kept | 0 |
| 4 | STO 2-wire star, 0.25 mm² SiF (SILI-E in the loops). Legs 0.0611, arms 0.0545, waist 0.0068. 0.137 incl. 12 % sleeving, vs R-028 A33 hold 0.14 | +0.1224 |
| 5 | Compute feed 24 → 48 V: 2.5 A rms / 4 A pk → 0.25 mm² SiF, ΔV 0.04 %, ΔT 14 K | −0.0007 |
| — | Sleeving on the above | +0.0114 |

- **Coax link check:**
  - Loss over 0.564 m: 1.75 dB at 3 GHz (GMSL2 6 Gbps Nyquist) and 1.16 dB at 1.5 GHz. That is far inside a GMSL2 automotive channel; the budget is sized for about 15 m of coax [EST, ADI channel spec not cited].
  - PoC loop resistance 0.45 Ω.
  - Neck drum r 34 mm, above the 30 mm dynamic bend minimum. The datasheet rates repeated bending at 20 mm for only 30 000 cycles, so add the coax to the O20a clock-spring cycle test.
- **Net harness: 1.2864 → 1.3925 kg (+0.106).**
- **Elmo:** MAN-G-TWI v2.011 (installation guide, Table 3 "R Type") is in `datasheets/`.
  - R70/100: Ic 70 A amplitude / **49.5 A rms**, 10–95 V (85 nominal), 5.6 kW.
  - R50/100: 50 A / 35.3 A rms, 95 V max, 4.0 kW.
  - The values used (49.5 A rms, 95 V) are confirmed. No correction.

## D65 (Arms R1, e1032af) Wrist differential pair downsize
- Needs per Arms R1, arm r 25 mm unchanged:
  - pitch 11.1 and yaw 11.1 N·m (1.5 × 7.4), 6 rad/s
  - RMS 7.4 N·m hold
- **Motor:** keep TBM2G-05008, the smallest TBM2G: Tp 0.72, Tmc 0.20 / 0.27 N·m, 0.111 kg.
- **Screw:** RV12x4 → **THK BNK1004-2.5** (ø10, lead 4, Ca 2.1 kN).
  - Per-screw peak 1018 N: 4.6× per axis, 2.3× with pitch and yaw at peak together.
  - Continuous 283 N vs 148 N RMS: 1.9×.
  - 4500 rpm with pitch + yaw together, within 95 % of 4900 rated.
  - L10 about 85 kh [EST duty].
- **Rejected:** BNK0810 (lead 10) fails RMS at 0.76× and simultaneous peak at 0.92×.
- **Mass:** pair 0.865 kg/side, vs 1.55 contract and ≤ 0.90 Arms target. **−0.685 kg/side, −1.371 kg both arms.**
  - Housing from the linear_body geometry (ø56 can, ø32 nut section).
  - Nut and rod-end/misc masses are [EST].
- **Cost:** BNK1004 about $150–250 [EST]; the RV12 price is not public. Net saving likely but not quantified.
- Pending Arbiter.

## D66 (A33, Electronics 1d70018 §9.4) STO 3-wire daisy chain; drive count 32
- Elmo STO uses 3 conductors per drive (STO1 / STO_RET / STO2; the return is not shared). Each EtherCAT branch now carries 3 × 0.25 mm² SiF (SILI-E inside the loops), with a 0.08 m tee at each drive.

| Run | n | Length m | kg |
|---|---|---|---|
| Legs (8 tees each) | 6 | 3.431 | 0.1058 |
| Arms (7 tees each) | 6 | 2.833 | 0.0855 |
| Waist (2 tees) | 3 | 0.663 | 0.0102 |
| MCU → torso junction | 3 | 0.25 | 0.0041 |
| **Wire total** | | | **0.2055** |

- With the 32 JST-GH 4-pin tees (0.012 kg) STO is 0.218 kg, or 0.243 kg including sleeving. That replaces D64's 2-wire 0.122.
- **Electronics' 0.270 is 0.05 high.** Their lengths (3.439 / 2.913) already include the EtherCAT tee pigtails, and they added STO tees on top of that. They also kept the neck segment (1.368 m), but the neck has no Elmo drives.
- **Drive count: 32 Elmo drives**, from size.py `cnt`:
  - Legs 8 each: hip yaw, hip roll, 2 × hip_pitch, 2 × knee, 2 × ankle.
  - Arms 7 each: shoulder ×3, elbow, wrist roll, wrist pair ×2.
  - Waist 2.
- Why the counts differ:
  - The old 34 included the 2 neck motors. Those are now Dynamixel XM430s (P-019 / R-025) with no Elmo STO.
  - Electronics' 30 took the harness row "leg drive pigtails (7/leg)", which was a typo: it should be 8/leg.
- Fixed in `harness.py`: leg pigtails 14 → 16 (+0.0048), phase and encoder leads 34 → 32 (−0.0052), JST-GH tees +32.
- Elmo: R70/100 is verified in MAN-G-TWI v2.011 Table 3 (49.5 A rms, 95 V). R50/100 is in the same table (35.3 A rms, 95 V, 4.0 kW), so it is verified as well. No separate datasheet is needed.
- **Net harness: 1.4959 kg (+0.2095 vs the official 1.2864).**

## D67 (Arms R2 357b72a, P-027) Wrist pair vs exact P-027 numbers (`wrist_p027.py` → `results/wrist_p027.json`)
- Pair: 2× TBM2G-05008 (Tp 0.72 N·m, tbm2g_manual §9.2.1 p.252) + 2× THK BNK1004-2.5 (ø10, lead 4, **Ca 2.1 kN / C0a 2.7 kN**, thk_bnk_lmsystems.html), arm r 25 mm, η 0.9 [EST].
- **Peak:** capacity 1018 N per screw. Pitch 14.7 N·m needs 294 N: **3.46×**. Yaw 8.9 N·m needs 178 N: 5.7×. Pitch + yaw together need 472 N: 2.16×. PASS.
- **Speed:** 6 rad/s is 2250 rpm per axis and 4500 rpm with both axes. At 30 % torque (88 N), the motor needs 0.062 N·m. PASS.
- **L10 (duty-weighted):** the duty profile is [EST] because no arm duty sim exists (O-A2): 5 % at 294 N at full speed, 25 % at 148 N (7.4 N·m hold), 70 % at 20 N, both at 30 % speed. This gives Fm 165 N and a mean of 754 rpm.
  - At THK fw 1.2 (smooth): **26.2 kh**. PASS, 1.79×.
  - At fw 1.5: 13.4 kh. FAIL.
  - At 294 N continuous and full speed: 0.8 kh.
  - **Accepted at fw 1.2. This is sensitive to the duty profile.** O-A2 duty data is needed to close.
  - **Update (Arms 7f71f86, `arms/wrist_duty_r3.json`):** fw 1.5 with the R3 duty gives **L10 57.7 kh. PASS.** Credit is **−0.666 kg/side (−1.332 both)**, closed in R-035. The hardware is superseded by D70 (O-A3 fit).
- **Alternative:** BNK1404-3 (ø14 lead 4, Ca 4.2 kN, same ø26 nut) gives 8× the L10 (107 kh at fw 1.5), but it adds 0.130 kg per side and fails 0.90.
- **Mass per side:**
  - Mechanical 0.865 (D65).
  - Encoders: +0.019 for 2× RLS AksIM-2 MB022 + MRA022 (2.7 + 7.0 g, MBD01_15 selection table). Total **0.884 ≤ 0.90. PASS.**
  - Elmo Gold Twitter EtherCAT drives on the arm: +0.044 for 2× 22.2 g without heatsink (MAN-G-TWI v2.011 spec table). Total 0.928. FAIL by 28 g. In that case the drives must stay booked in the Electronics drive line (D66, 32 drives).

## D68 (Arms R2 O-A3 + Thermal) maxon drive lengths, TBM2G hot constants, strain-wave efficiency
**O-A3 lengths.** Length = motor + gearhead L1 + encoder, per maxon's own rule (assembly parts and shaft stub excluded).
- **DCX 22 S + GPX 22 HP, 3-stage (62–231:1; the config sheets for 231:1 and 103:1 both give 38.2 mm):**
  - 34.2 + 38.2 = **72.4 mm** with no encoder.
  - **70.9 mm** with ENX 22 EASY INT (−1.5 mm).
  - **80.9 mm** with ENX 16 EASY (+8.5 max).
  - Not the sterilizable GPX 22 HP on p.393 (45.9 mm).
- **DCX 16 S + GPX 16 LN:**
  - 3-stage (25.7 mm, matching v3/PARTS): 26.5 + 25.7 = **52.2 mm**, or **60.7 mm** with ENX 16 EASY (8.5 max).
  - 4-stage (30.6 mm): 57.1 mm, or 65.6 mm with the encoder.
- maxon flags L1 as configuration-dependent. Allow about 1 mm.

**Thermal: TBM2G hot constants** (manual, June 2023: 05013 §9.2.2 p.254–255; 07608 §9.5.1 p.282–283).
- Rated winding temperature is 155 °C (ΔT 130 K at 25 °C ambient).
- **Hot Kt** is published directly:
  - 07608 A/C/D: 0.193 / 0.096 / 0.056 N·m/Arms (cold: 0.216 / 0.108 / 0.062).
  - 05013 A/C/D: 0.122 / 0.061 / 0.035 (cold: 0.136 / 0.068 / 0.039).
  - The implied magnet coefficient is hot/cold = 0.889 (07608C) and 0.897 (05013C), i.e. **about −0.08 %/K**. This comes from the datasheet pair. No magnet grade or Br coefficient is published (not found).
- **Hot resistance:** Rm is line-to-line at 25 °C. Copper α20 = 0.00393 /°C (NBS Circ. 31), so R(T)/R(25) = (234.5 + T)/(259.5). At 155 °C this is **1.501**.
  - 07608 A/C/D: 1.27 / 0.318 / 0.106 → **1.906 / 0.477 / 0.159 Ω**.
  - 05013 A/C/D: 1.78 / 0.46 / 0.15 → **2.672 / 0.690 / 0.225 Ω**.

**Strain-wave hold efficiency** (HD CSF/CSG catalog p.39, Component Set 17–100, SK-1A/SK-2 grease, rated torque, read from the graph, σ ≈ 3 %):
- Ratio 80/100 at the lowest published speed of 500 r/min: about **84 % at 25 °C** (about 74 % at 0 °C).
- Below rated torque, multiply by Fig. 9: about 0.9 at 0.5 Trated and about 0.44 at 0.1 Trated.
- **Efficiency at stall / 0 r/min (true hold) and back-driving efficiency: not found** in the HD catalog. For hold copper loss, Thermal should take the motor torque as T_out/(N·η), with η ≤ 0.84 as the conservative bound [EST].

## D69 (Controls A40 / Robot Lab) Knee thermal fix: 2× TBM2G-08513D + conductive shank heat path
- **Problem:** with the 1.2 m/s WBC cruise looped at 35 °C (`knee_thermal.py`, the Controls A40 2-node model plus iron loss of 4.6 W per joint), the current 2× 07613D knee reaches 120 °C at **7.4–8.5 min** and runs away (τ_cont 83 vs RMS 105–108 N·m).

| Option | τ_cont N·m | To 120 °C | Tw at 60 min | Δmass per knee | Verdict |
|---|---|---|---|---|---|
| (a) 2× TBM2G-08513D | 113 | 37–51 min | 122–128 °C | motor +0.164 (2 × (0.403 − 0.321), datasheet); housing ø85 stator vs ø76 +0.04 [EST] | not enough alone |
| (b) conductive path into shank, Rha ×0.5 [EST] | 104 | 9.6–12 min | 140–149 °C | strap/gap pad +0.03 [EST] | not enough alone |
| (c) more lever/screw ratio | — | — | — | — | **infeasible:** motor is at 7565 rpm vs the 7600 cap at the 13.3 rad/s stairs need. The 1.3× ratio needed puts it over Nmax 8000 |
| (d) forced air, h 12 → 40 [EST], Sunon PF40281B1 42 g / 6.12 W (Electronics f4e839c) | 118 | never | 110–116 °C | +0.042 fan + duct [EST] | marginal; fails once Thermal's +35 K cover penalty is added; adds a fan failure mode |
| **(a)+(b)** | **141** | **never** | **87–91 °C** (Tss ≈ 92–95) | **≈ +0.23 per knee, +0.47 robot [part EST]** | **selected** |
| (a)+(d) | 161 | never | 74–76 °C | ≈ +0.25 per knee | fallback if (b) can't reach Rha/2 |

- **Why (a)+(b):**
  - The 08513D has a similar hot Kt to the 07613D (0.085 vs 0.081 N·m/A), so the voltage envelope and rpm hardly change. ω30 drops by about 5 %, roughly 16.0 → 15.2 vs the 13.3 need [scaled]; `size.py` envelope re-run pending.
  - Km goes 0.201 → 0.271 (−45 % copper loss) and Rth 1.85 → 1.80.
  - It is passive, with no fan, and keeps 30 K of margin to the derate at 35 °C.
- **Interfaces:**
  - Legs: knee twin housing stator bore ø76 → ø85 frame (D59 merged housing re-CAD; centre web check still open per T&R #8), plus a bolted conductive pad face to the shank.
  - Thermal: confirm a shank path that halves Rha (≥ 1.2 W/K added conductance) and the covered case.
  - Electronics: knee drives chassis-mount to the housing (about 7 W each, over the 5.5 W flat-heatsink limit).
- **Cost:** TBM2G list prices are not public. Both frames sit in the same ~$0.9–1.5k [EST] band, so the delta is unquantified.
- **Mass:** +0.47 kg. Needs Arbiter funding under R-031 §11, since no credit is available until A12; it could come from P-027 wrist savings (−1.371) once credited.
- **Also:** specify thermal-device code `A` (PT1000) on all TBM2G (THERMAL_DATA_PACK §2).

## D70 (Arms O-A3, D67 fit fail) Wrist: compact rotary units at the wrist (`d70_wrist_rotary.py` → `results/d70_wrist.json`)
- **(a) Push rods (D67 pair moved to the elbow/upper arm): REJECTED.**
  - 2× ø8×1 steel tube rods, 0.30 m: Euler Pcr 3.0 kN vs 294 N, 10×. Each rod is 0.052 kg.
  - Side mass 0.884 + 0.104 rods + 4 rod ends 0.02 [EST] = **1.01 kg. FAILS 0.90.**
  - Backlash: 4 rod joints per axis; rod-end play is not published (not found).
- **(b) Rotary, per axis: TBM2G-05008C + Harmonic Drive CSG-14-100 component set + IKO CRBH 258 A + AksIM-2 MB022. CHOSEN.**
  - Gear: HD Table 3 rated 10, repeated peak **36 (2.45× vs 14.7)**, average 14, momentary 70 N·m. Set 0.09 kg (catalog weight table).
  - CSF-11-100 has a repeated peak of 11 N·m, below 14.7, so it fails.
  - Motor: Tp 0.72 gives 50 N·m at the output (η 0.70 [EST]), so the gear limits.
  - Speed: 6 rad/s is 5730 rpm input, within 8500 rpm (grease max) and 8000 rpm (motor).
  - 30 % torque needs 0.063 N·m.
  - Hold 7.4 N·m needs 0.106 N·m vs Tmc2 0.20 (1.9×). Current 2.6 A hold, 5.3 A peak (hot Kt 0.040).
  - **Mass 0.336/axis, 0.671 kg/side. PASS.** That is −0.213/side vs D67. Housing 0.06 and fasteners 0.015 are [EST].
  - The forearm bore is now free of wrist drives. Envelope: TBM2G-050 frame + CSG-14 at the wrist [EST]. CAD is needed.
  - Cost: HD, TBM2G and IKO prices are not public (SOURCES row 32).

## D71 (Torso bd02c23 / Arms R2) shoulder_pitch output bearing vs 690 N·m side fall
- The bearing is IKO CRBH 6013 A (v3.json bearing map; C0 24.3 kN, IKO CAT-57151 dims table). P0r = Fr + 2M/Dpw + 0.44Fa (IKO eq. 2). Dpw is taken as (d+D)/2 [EST].
- With the 11.5 kN impact axial (lateral fall along the pitch axis): P0r 23.5 kN, **fs 1.04. Passes v3's fs ≥ 1 with no margin.**
- If the force is radial: fs 0.81. FAIL.
- **Change: CRBH 8016 A** (C0 43.4 kN, 0.74 vs 0.33 kg, **+0.41 kg/side**). fs is 2.30 axial and 1.72 radial.
  - CRBH 7013 A (+0.05 kg) gives fs 1.30 axial and 1.00 radial. That is the minimum if the mass is refused.
- **Pitch slip clutch: not needed for the side fall.** The 690 N·m acts about the roll/x axis and is carried as bearing moment, not as pitch-gear torque, so the CSG-25 ratchet (650) is not loaded.
- **A pitch-axis fall component (forward fall) is not quantified.** Torso/Arms should supply it. If it is above 369 N·m (CSG-25 momentary), add a ≤300 N·m clutch like roll.

## D72 (Electronics R1 §10.6, 4b85cc8) Wrist motor leads, shoulder bay → wrist (D70 motors at the wrist, 1.7 m/side)
- Per motor:
  - Phase: 3× Lapp SiF 0.25 mm², twisted (5.4 g/m each).
  - Encoder: Belden MRTA2P26S 2×2 shielded + 2× SiF 0.25 for 5 V/GND.
  - Thermistor: 2× SiF 0.25.
  - Total 63.7 g/m.
- ΔV at 5.3 A peak is 1.7 V (2.5 % of 68 V, above the 2 % leg-series budget; acceptable for a 0.2 N·m motor). Going to 0.5 mm² phases adds 0.037 kg/side.
- **0.244 kg/side** (wire 0.217 + sleeving 12 % [EST] + JST-GH). That is 0.488 both arms, vs Electronics' 0.15 estimate.
- The EtherCAT and STO tees for the 2 wrist drives move to the shoulder bay: ~0 kg net.
- Booked in actuator_deltas.json `wrist_pair_pending`: D70 −0.425 + D72 +0.488 = **+0.063 kg both, pending Arbiter**. The D67 −1.332 credit stands.
- Not yet merged into the harness.py totals.

## D71 update (Arbiter: D71 = CRBH 7013 A) Dpw is cited
- The IKO CAT-57151 crossed-roller section defines the pitch circle diameter as **Dpw ≒ (d+D)/2** (eq. 2 legend, `datasheets/iko_crb_catalog.txt` lines 299–303 and 593–598). It is IKO's own definition, not our estimate. The catalog publishes no roller diameter or separate Dpw.
- CRBH 7013 A: d 70, D 100, B 13, da 76, Da 94, C0 27.7 kN, 0.38 kg. Dpw = 85.
- **fs = 1.30 (axial 11.5 kN + 690 N·m) and 1.00 (radial).** D71 is unchanged.
- **Bounding check** with the shoulder diameters (Dpw 76…94): axial fs 1.19–1.40, radial fs 0.93–1.06.
- The radial case is still at fs 1.0 with no margin. The forward-fall pitch component is still unquantified (Torso/Arms).

## D69 addendum (R-031 lever check + knee strap): see results/LEVER_R031_AND_KNEE_STRAP.md
- The added conductance needed is corrected to 0.69 W/K (Thermal).
- The heat sink moves to the femur, because the housing pivots only 5.7–12.6° about the thigh trunnion.
- Strap: TAI GFTS, 2 large sections, ≥ 1.32 W/K, 0.12 kg per knee [EST], $2–10k per knee, flex life untested.
- D69 total is now about +0.83 kg robot.

## D73 (Arms A42 440c7a8) Wrist pitch/yaw unit placement: above the pivot (`wrist_place_d73.py`, `cad/wrist_place_d73.step`)
- The D70 units (Ø56 × 54 [EST envelope]) ride on the roll output at z ≥ +28 (pitch axis at z 56; the yaw unit is stacked above it, z 86–140). Each drives its joint through one 7075 link (6 × 3, 56 mm, 2 × Ø3 pins). The fork cheeks are r 24.5, and the palm swept zone stays clear.
- **Outboard (|y| ≥ 45) is rejected:** the wrist would be 198 mm wide.
- **Links: 7.9 g per side, 15.8 g both. Pending/frozen (R-043), not booked.**
- **Backlash:** ISO 286 H7/g6 at Ø3 gives 2–18 µm per pin, so ≤ 36 µm per link, which is **≤ 0.08°** at the 25 mm crank. This excludes CSG-14 lost motion.
- **Flag for ID:** the stack adds about 112 mm of wrist segment above the pivot. This needs a check against the forearm (163.8/177 used).

## D74 (Arms A42.3) Hollow wrist roll: Harmonic Drive SHG-20-100-2SH (or -2UH)
- Bore **Ø21** (Illus. 14.3 / 14.1).
- **Torque:** rep peak 107, avg 64, rated 52, momentary 191 N·m (Table 13.1).
- **Size and mass:** 2SH is OD 90, L 42, 0.89 kg; 2UH is OD 95, L 51.5, 1.38 kg.
- SHG-14 has only a Ø14 bore and fails the ≥ 21 requirement.
- **Motor:** not selected. A hollow frameless motor with rotor ID ≥ 21 is needed. The TBM2G rotor ID was not checked (not found here).
- **Sheath minimum bend radius (Ø2.5 PTFE-lined, A32):** the product is not named in the arms files or v3 (only the LIROS D-Pro 1 mm tendon). The bend radius is **not found**. Materials/Arms must name a product.

## D75 (A43, Arbiter R-045 2461a14) Hand-board location options, pending/frozen
- **(A) Board in the shoulder bay** (Electronics §16.4(3) acac380):
  - 22 × 0.25 mm² per side, 1.7 m, SILI-E 4.5 g/m in the 0.911 m of arm loops and SiF 5.4 g/m elsewhere. That is 0.184 kg per side bare.
  - Removing the hand 24 V loop saves −0.013.
  - **Net +0.398 kg both arms, sleeved.**
- **(B) Board in the forearm:** the short leads and the 24 V loop are unchanged, so **0.000**. If the RP40s stay in the bay (R-038), a 24 V pair must run bay → forearm: **+0.077 kg**.
  - Board fit in the forearm: the R4 pack leaves 13.2 mm axial spare in the Ø66 bore. **The board dimensions are not in the repo**, so fit is unconfirmed. The envelope is a disc ≤ Ø65 × ≤ 13 mm.
- **Drum fill (A):** a 10–11 mm bundle on the shoulder drums (r 40.5–53). Per-conductor bend r/OD ≥ 24 (SILI-E 0.25 at 1.7 mm OD). The drum width/depth is not in the model, so **fill is not verified**.
- Harness booked total is unchanged at **1.9841 kg**. If (A) were booked: 2.382, **breaking the 2.00 kg contract by 0.382**.

## D69 rev B (R-043 / Arbiter A46–A47): keep 2× TBM2G-07613D, add 0.05 m² of axial housing fins. −0.47 kg vs the +0.65 booked
- **Script:** `knee_resize_r043.py`, which uses Controls' winding_model 2-node loop as in knee_id_r1.py.
  - Traces: Legs ID walk_1p2_r7 (ref_ds25) and r4 carry_20kg_1p0. **Carry torque ×1.10 [EST]** as margin for the P-042×0.32 regen.
  - 2× Elmo drive loss goes into the housing node (Thermal 9b9e169). 35 °C, 60 min. Worse knee of L/R.
  - Cases: open (h 12), vented (A35, h 15), and closed cover (+35 K on the air side).
- **Candidates:** all are datasheet TBM2G frames with hot Kt ≤ 0.085, so the 7565 rpm envelope is kept.
  - 08508D was dropped: Km 0.203, which is no gain over 0.201.
  - 07626D was dropped: hot Kt 0.156, so back-EMF doubles and it fails the 68 V envelope.

| Option | Δkg per knee | τ_cont at 130 °C | walk open / vented | carry ×1.1 open / vented | closed (walk / carry) | Pass ≤ 120 |
|---|---|---|---|---|---|---|
| 07613D, no change | 0 | 83 | 137 / 120 | 174 / 149 | 180 / 221 | no |
| 07613D + fins 0.025 m² (Thermal C) | 0.05 | 94 | 110 / 98 | 136 / 119 | 152 / 181 | no (carry open) |
| **07613D + fins 0.05 m²** | **0.09 [EST, interpolated from Thermal 0.05 / 0.12 kg]** | **102** | **96 / 87** | **116 / 104** | — | **yes** |
| 07613D + fins 0.07 m² | 0.12 | 107 | 89 / 82 | 107 / 96 | — | yes |
| 07613D + fan, h 40 (Thermal D) | 0.02 + 1–2 W | 118 | 77 / 72 | 90 / 83 | 116 / 130 | yes (moving part, stall sensor, power) |
| 09408D + fins 0.025 | 0.24 (motor 2 × 0.053 + housing scaled ×94/76 [EST]) | 122 | 95 / 85 | 110 / 98 | 133 / 150 | yes |
| 08513D + fins 0.025 (old D69 motor) | 0.256 | 128 | 83 / 76 | 95 / 86 | 121 / 135 | yes |

- **Selected: 2× 07613D (unchanged) + about 12 axial 6061 fins × 20 mm × 101 mm (+0.05 m² wetted). +0.09 kg per knee, +0.18 kg robot [EST].**
  - **A46 net D69 = +0.18 kg robot, replacing +0.65 (and the earlier +0.83). That returns −0.47 kg to the reserve.**
  - It is the lightest passive option that passes. The fan is lighter (+0.04 robot) but adds a moving part and 2–4 W, so it stays the fallback.
- **Dropped:** the 08513D swap, the ø85 housing re-CAD, the shank spreader, the femur spreader and the GFTS strap.
- **Closed covers fail every passive option,** so the knee stays uncovered or vented (P-026, A35).
- **Drives:** the 2× Elmo drives go on the housing, inside the analysis basis.
- **Carry margin:** 4 K. If Legs' regenerated carry shows knee RMS more than 10 % above r4, re-run. The step-up is 0.07 m² of fins (+0.03 kg per knee).
- **A47 fin clash sweep (`knee_fin_sweep_a47.py`, model_v4, L_knee 0–135° in 15° steps with the screw stroke following, plus the hip_pitch −105/+40 corners):**
  - The housing's free distance to non-mated parts is **10.5–13.6 mm to the knee trunnion bracket top plate (thigh) [EST part] on one face**. Everything else is ≥ 50 mm: tibia 50.5 at 135°, hip_pitch body 60, bracket strut 58, femur 81.
  - So **no 20 mm fins on the bracket-facing sector** (≤ 9 mm there, for 1 mm clearance). The lost area goes onto the other faces, which have ≥ 50 mm of room, using 25 mm fins.
  - The v5 fairing envelopes are not in model_v4. **Legs to confirm.**

## D69 rev B fins as built (Thermal D69C b785697 layout, Legs L48 envelope); R-031 lever release candidate
- **Fins (`knee_fins_revb.py` → `cad/knee_twin_housing_finned_revb.step`, valid solid):** these sit on the existing D59 twin housing (07613D, can r41, z 1–43). Per can:
  - 14 rear fins × 25 mm, centred on 180° (span ±60°), against the L48 limit of 28.3.
  - 7 front fins × 9 mm (span ±27.7°), against the limit of 12.
  - All 1.0 mm thick, 6.6 mm root pitch, 5.6 mm root gap.
  - No fins on the ±y sides.
- **Measured: added area 0.0703 m² per knee, 6061 fin mass 0.0932 kg per knee, 0.186 kg robot.** Thermal estimated 0.070 m² and about 0.11 kg; Arbiter R-052 booked +0.24, so this is **−0.054 kg** against that booking.
- **Temperatures (`knee_resize_r043.py`, fins_cad):** continuous 107 N·m at 130 °C.
  - walk_1p2_r7: **89.2 °C open**, 81.8 vented.
  - carry r4 +10 %: **106.4 °C open**, 96.3 vented.
  - Thermal's independent prediction was 88 / 105, so it is reproduced within 1.4 K.
  - Closed covers: 129 / 149, which fails, so the knee stays vented or uncovered.
- **Edge fins:** the outer rear fins sit exactly on the 120° and 240° sector boundaries, where the 60–120° side is limited to 0 mm by the RV12 rod at knee 135°. Legs to confirm, or drop to 13 rear fins (area 0.0682 m², still passes).
- **Hip lever L47 release candidate:** `cad/hip_pitch_lever_r031_mw_b30_d36_RC.step` (copy of Legs' STEP; 2 valid solids, 155,055 mm³).
  - **Measured 0.464 kg per lever** (7075 0.420 + steel pins 0.044, hp_lever_fea_v2 rule).
  - That is +0.215 per lever versus the 0.2491 booked in LINKAGE_TABLE, and +0.132 versus the G2-as-briefed loft (0.332).
  - **Legs' +0.118 kg robot is not reproduced. My measurement gives +0.26 to +0.43 kg robot, depending on the baseline.** This needs reconciling.
  - The fatigue check (≤ 58 MPa at 2030 N per pin) is not run on the box (gmsh can't load, and converged dofs need about 4 GB). See brief `results/GROKBUILD_lever_fea_r031.md` (G3).

## D76 (Arms R5 7f0ff7a, Arbiter R-055) D73 compaction
**Cited unit length** (axis direction):
- TBM2G-05008 "A" max 19.84 mm (manual §9.2.5 p.260 stack table).
- CSG-14 H1 18.5 mm (CSF-14 17.6; CSF-11 16.0) (HD CSF/CSG catalog dims table).
- CRBH 258 A, B 8 mm.
- AksIM-2 MRA022/MB022 system thickness 12.45 mm (MBD01_15).
- Total **58.8 mm**, plus 2 × 2 mm walls [EST] = **62.8 mm**. The D73 envelope of 54 was low.
- With cited lengths, the D73 stack (pitch can on its Ø56 side + yaw axial) reaches z +148.8 above the pivot, not +140.

**Options:**
- **Shorter stack TBM2G-05004:** does not exist (only 05008/05013/05026; manual p.260). Not found.
- **CSF-11-100 for yaw:** repeated peak 11 N·m ≥ 8.9 (1.24×), Table 1. Saves 2.5 mm in length and 0.04 kg/side (set 0.05 vs 0.09). Adopt.
- **Pancake/nested (WG inside the motor rotor):** the TBM2G-050 rotor ID vs the CSF-11/14 WG size is not cited. Not found.
- **Partly into the forearm bore:** not possible. The R4 pack leaves 13.2 mm, and the centre is only Ø20.
- **Side by side: CHOSEN.** Both units axial along the forearm axis (z), at y ±(28+1). Each drives its joint by a link, as in D73. They occupy z +28 … +90.8 above the pivot.
  - **That is −49 mm vs D73 as booked (+140), or −58 mm vs D73 at cited lengths (+148.8). Meets the ≥ 40 mm ask.**
  - Cost: wrist width in y becomes about 116 mm (2 × 58), vs the 86 mm palm and the Ø70 forearm. This needs a local fairing; ID to accept.
- **Torque:** pitch CSG-14-100 36 ≥ 14.7 (2.45×). Yaw CSF-11-100 11 ≥ 8.9 (1.24×). Motor Tp 0.72 × 100 × 0.70 [EST η] = 50 N·m, so the gear limits. Input 5730 rpm ≤ 8500.
- **Mass:** −0.04/side (CSF-11). Links keep 56 mm (D73). **Net −0.08 kg both arms.**

## D77 (Arms R5) Shoulder-pitch slip clutch ≤ 300 N·m: off-the-shelf parts are too heavy
- **Mayr ROBA-slip hub Size 2:** Type 100.2 130–250 N·m, Type 100.3 250–400 N·m. **1.6 kg** pilot-bored (catalogue K.123.V16 table). Length not extracted.
- **R+W SK2:** the size 200 (120–240 N·m) is OD 90 mm, **4.0 kg**, length 128/140 mm. Size 300 (200–320 N·m) is 5.9 kg (RW-DS-PK SK2 data sheet, rw_sk2.pdf).
- Both are ≥ 1.6 kg/side against a frozen mass budget. Per D71, the side fall does not load pitch torque, so **no pitch clutch is recommended**. The open input is still the forward-fall pitch torque (Torso/Arms). A custom friction ring inside the CSG-25 output would need design (not cited).

## D78 (Arms R5) Ø2.5 tendon sheath minimum bend radius ≤ 35 mm
- **Not found.** No Ø2.5 PTFE-lined or PEEK sheath datasheet with a published bend radius turned up. The nearest cited one is the RINGSPANN Express push/pull cable at **51 mm** (12 mm fixture, too large).
- Materials should source a candidate (Zeus PTFE/PEEK tubing, Asahi/medical coil sheath) with a datasheet radius.

## D79 (Arms R5) Hand board stays in the forearm; ENX22 EASY INT on 6 flexors
- The booked harness is unchanged at **1.9841 kg** (option B, D75).
- The encoder leads board → DCX22 are inside the forearm and not in the harness model (they belong to the hand allowance). The ENX 22 EASY INT is integrated, −1.5 mm length (D68), 10-pin.
- **Change to flag:** the RP40 converters are in the shoulder bay (R-038). A 24 V pair bay → forearm is needed: **+0.077 kg pending/frozen**, unless the converters move back to the forearm.

## D76 update (R-076 yaw CSG-14; R-080 binding −1.5 mm) (`wrist_place_d76.py` → `cad/wrist_place_d76.step`, `results/wrist_place_d76.json`)
- **Yaw is back to CSG-14-100.** Repeated peak 36 vs the new 12.9 N·m need is 2.79×; CSF-11 at 11 is 0.85× and fails.
  - Mass: the HD catalog weight table (l.1101) gives CSF/CSG-11 0.05 and size 14 0.09 kg, so **+0.04 kg/side, +0.08 pair** vs D76's CSF-11. That cancels the D76 −0.08 credit. Arms R8 has already booked +0.080, so don't double count it.
  - Length: +2.5 mm (H1 18.5 vs 16.0). The yaw unit now equals the pitch unit (62.8 mm), so the stack top is set by the pitch unit either way.
- **Width is unchanged:** 114 mm over the two Ø56 TBM2G-050 cans at y ±29, about 118 with 2 mm walls [EST]. This is inside the ID fairing (124). The Ø56 frame sets the width; the CSG-14 OD was not separately checked, so this rests on the D70 Ø56 envelope [EST].
- **Lowering 1.5 mm (z +28 → +26.5, top +90.8 → +89.3): FEASIBLE.**
  - Fork/cross r 24.5 sphere (wrist_clash_r4 rule): 3.52 → **2.02 mm** (rule ≥ 2.0; 0.02 mm spare).
  - Fork cheeks: 16.5 mm.
  - Palm swept over P-026 (max z +12.9): 13.6 mm.
  - No wrist-roll output or bearing sits below the units, because roll is at the elbow end (D76, D74 dropped).
  - The forearm shell, board and 0.244 kg/side lead bundle are all on the elbow side above the units, so the move only increases those gaps.
  - **Governing gap: 2.02 mm to the 24.5 mm envelope sphere.** That sphere is a rule envelope, not real cross CAD. Arms must keep every fork/cross part inside r 24.5.

## Tendon spool 10 → 5 mm (Arms R6 trim b): NOT SUPPORTED
- No catalog Ø5 spool or capstan for 1 mm Dyneema was found.
- **Cited minimum:** Marlow Ropes, "Maximising Ropes Performance" sheave table: braided ropes need **8 × rope diameter**, so ≥ 8 mm for LIROS D-Pro 1 mm.
  - 5 mm (D/d 5) violates this. The current 10 mm (D/d 10) complies.
  - The IFREMER HMPE bend-over-sheave fatigue tests used D/d 20, a larger ratio that gives no basis for going below 8.
- With stall tension at 775 N (~40 % of break, Materials) and 1.75e6 cycles as a wear part, going smaller would worsen bend fatigue. **Keep 10 mm.** Ø8 is the cited floor and would give back +1 mm at most (needs Arms to check the bend-fatigue life).

## D77 CLOSED: no shoulder-pitch slip clutch (Arms R7 550ab88 / R8)
- With tuck B, the forward-fall shoulder-pitch torque is **≈ 343 N·m (Arms inertial [EST])**, below the CSG-25-100 momentary rating of 369 N·m (HD Table 3), a 1.08× margin.
- No clutch is fitted. The cited options are 1.6–4.0 kg/side.
- **Caveat:** this is an estimate with only 8 % margin, pending Controls T-031. If T-031 exceeds 369 N·m, reopen D77.
- D71 (CRBH 7013 A, conditional on T-030 ≤ 550 N·m) is consistent. 343 N·m is pitch torque through the gear; the bearing moment basis is unchanged.

## D80 (R-114) Knee trunnion bore Ø9 → Ø12 for Legs L62 (`knee_trunnion_bore_r114.py` → `results/knee_trunnion_bore_r114.json`)
- **CAD (rev B STEP):**
  - The boss is Ø20 × 7 at x ±85…92, and is backed by the r41 can wall. The bore is modelled blind, 6 mm deep.
  - Ø12 leaves a **4.0 mm** radial wall (Ø9: 5.5).
  - The floor to the stator cavity is 2.0 mm (the can wall, the same for both sizes), and the floor to the stator OD is 3.0 mm.
  - Fin roots are 15.1 mm away and the nut/7202 bearing section 29.8 mm. No bolt holes are near the boss.
  - **There is no bearing-seat distortion risk** (≥ 29.8 mm away). Use a slip or bonded pin fit, not interference, over the 2 mm can wall above the bonded stator.
- **Loads per pin** (2 pins share the screw pair; legs TRUNNION_BREAK.md L61, legs DECISIONS l.25):
  - actuator max 3634 N (7267 / 2);
  - design 2526 N;
  - walk 1682 N (fatigue, taken as R = −1, conservative).
- **6061-T6 (ASM):** Sy 276, Se 96.5 MPa. This is evaluated as asked; cad_mass.py books the housing as 7075, which would be no worse statically.
- **Lug hand-calc** ignores the can backing, so it is conservative.
- **Ø12 in the existing Ø20 boss:**
  - Bearing 50.5 MPa max (Sy/p 5.5).
  - Net section 75.7 MPa (SF 3.65).
  - Shear-out SF 2.84.
  - **Fatigue: Kt 2.4 [EST] × 35.0 = 84 MPa → Se/σ 1.15 < 1.5. FAILS the fatigue margin.**
- **Ø12 with the boss grown to Ø23 (keeping the 5.5 wall): PASSES.**
  - Net 55.1 MPa (SF 5.0), shear SF 3.63.
  - Fatigue 58.6 MPa → **1.65**.
  - +3.8 g per knee (6061 density; 4.0 g at 7075), +7.7 g robot.
  - Fin gap ≈ 13 mm.
- **Ruling proposed:** YES to Ø12, but only with the boss grown Ø20 → Ø23 (outward only, same 7 mm). Its net mass is about −2 g robot vs Legs' Ø9 fallback (+10 g). In the plain Ø20 boss, NO (fatigue 1.15).

## D81 (Robot Lab job1 a556d44) "Forearm-roll" 566–773 N·m is the superseded shoulder_roll pad case
- Job1 Mx is spin about the **shoulder_roll** axis from the side-fall pad (9.17 kN, pad 64 mm off-axis, CRBH 6013). Not the D76 wrist roll; forearm cap unaffected. Superseded by R-120/R-121 (Z −20, CRBH 7013 A): Mx 321 N·m, CSG-25-100 SF 1.09 at ×1.05, ratchet 650 SF 1.93, s0 2.04–2.31.
- Options costed (`results/FOREARM_ROLL_TORQUE.md`): CSG-32 +≈1.1 kg pair [EST incl. housing], CSG-40 +2.56 kg gears alone, SHG same ratings heavier, clutch 1.6–4.0 kg (R-057), current limit gives no impact credit.
- Decision: keep CSG-25-100 + CRBH 7013 A, no clutch; P-055 removes the clutch from the shoulder_roll contract row. Gate Job 8 Mx ≤ 351 N·m; fallbacks CSG-25-120 (0 kg) then CSG-32-100.

## D82 (R-122) Actuators mass-down rows and fastener BOM (`r122_actuators.py`)
- Row 3 housing pocketing: R-122 basis 0.78 kg is one-of-each; robot is 2.221 kg. Candidate-region estimate −0.316 full (−0.354 with Thermal-gated tube windows), half credit −0.158. Ankle ring fins −0.265 only if Thermal accepts. `results/R122_ACTUATORS.md`.
- Fastener BOM (`results/FASTENER_BOM.md`): 1234 screws, 2.08 kg steel; 384 non-structural, Ti64 swap −0.091 kg (−0.074 without drive mounts). Flag: legs counted 0.82 vs 0.30 kg booked (+0.5 kg risk).

## D83 (Job 9 c) Knee release body = rev B fins + R-116 boss; material 7075-T6
- `cad/knee_twin_housing_release_r116.step` (`knee_release_r116.py`): rev B + Ø23 boss + Ø12×6 bore. Rev C (trimmed fins) is withdrawn; it is not a housing rev.
- 7075-T6 one-piece (cad_mass booking). Fin mass at 7075 is +0.008 kg robot vs the 6061 figure; flagged for the Arbiter, not booked. `results/JOB9_KNEE_GEOMETRY.md`.

## D84 (R-123) Arm/waist fastener delta, 7075 basis 480/560/70, row 12 conditions
- Arm/waist fasteners: counted 1.265 kg vs booked 0.39 (conservative; v3 0.03/unit + D70 0.015) → **+0.875 kg** (range +0.475..+0.875). `FASTENER_BOM.md`.
- G3 and G4 briefs → E 70, Sy 480, Su 560, static 320, overload 400; Se unchanged. cad_mass.py lever SF on 480: hip 2.00, knee 2.50.
- Re-check (`results/R123_RECHECK.md`): one stale result fails 320 (h4 needle lever 332 MPa in PROOF_TEST); no live part fails.

## D85 (R-126) v3 actuator() adders traced (`results/R126_V3_ADDERS.md`)
- All four constants come from 3c7b50e with no comment; they are the residual of the v2 ACT_OVERHEAD split. Inferred: rotary 0.03 fasteners, 0.04 cabling/connectors; linear 0.08 the 7202 pair (kept), 0.10 linkage hardware (double with LINKAGE_TABLE).
- Double counts: 0.04 × 14–18 = 0.56–0.72; 0.10 × 12 = 1.20; leg 0.03 × 4 = 0.12; leg FAST connectors 0.18. Elmo G-TWI 22.2 g (MAN-G-TWI p.10) vs 0.038 placeholder × 32 = −0.506.
- Recommended credit now −1.63 kg (drive and connectors full, the inferred lines at half); full −2.57 to −2.73 kg after a per-unit bottom-up table.

## D86 (R-127 C(b)) Mg housings: Elektron 43, not AZ91D (`results/R127_MG_HOUSINGS.md`)
- From CAD volumes: −0.625 kg (equal geometry + 7075 seat inserts) to −0.263 (+25 % stiffness volume) for hip yaw/roll + hip-pitch/ankle bodies. Multi-path only (hip-pitch/ankle): −0.377 / −0.159. Not additive with row 3 (combined ≈ −0.85).
- Hand proxy passes at A-basis 130 MPa except the ankle eye lug (142 MPa peak) → 7075 bush. Stiffness/ovality needs the G4-Mg FEA (addendum in the file). No Ti in Mg; PEO + sealant + isolated fasteners; Thermal re-check of the unit ΔT.
