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
