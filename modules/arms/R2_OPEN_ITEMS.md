# RL Arms & Hands: R2 open items O-A1…O-A5 (2026-10-14)
This file builds on `R1_ARCHITECTURE.md`. Every number cites a repo file. Where data is missing, that is stated, with the exact question for the owner. Proposals filed this round: **P-026** (ROM cut) and **P-027** (wrist pair downsize), both in `modules/PROPOSALS.md`.

## O-A1: sim arm mass vs catalog → RL Torso & Power
**Determined:** `sim/v3/humanoid_v3.xml` gives 5.953 kg/side: shoulderP 1.379, upper_arm 1.806, forearm 1.951, hand 0.817. The catalog allocation is 9.54 kg/side: CONTRACTS §1a arm rows 6.57, arms structure 0.80 (§3), hands 2.10 (§3, `v3.json`), palm 0.072 (R-027). The gap is **3.59 kg/side**. Shoulder mount per CONTRACTS §1c: 8 × M8 12.9, side-fall case. Mount at y ±0.170, z +0.220 above the waist-pitch axis (sim).
**Needed from Torso & Power:**
1. Do you own the shoulder mount (torso side) and the sim torso/arm inertials? Confirm you will update the arm body masses to the catalog values above, or tell me who does (Robot Lab / Controls).
2. Shoulder-to-torso load case to design the frame for. Arms supplies these per side at the shoulder_pitch flange: static 82.2 N·m (10 kg reach) / 61.3 N·m (carry); need 123.4 N·m. Side-fall: v3 `FALL['shoulder_F']` with the roll clutch at 300 N·m. Do you accept 8 × M8 12.9 on your frame, and at what PCD? CONTRACTS uses r_pcd 50 [EST].
3. Shoulder y-position: is ±0.170 m kept in the v5 tapered chest (330 → 250 mm, V5 plan row 4)?

## O-A2: holding thermal at carry → RL Thermal
**Determined:** holding torques per arm are 61.3 N·m shoulder_pitch, 40.1 elbow, 7.4 wrist_pitch (`arm_loads_r1.json`, carry_waist_10kg_per_hand, static). Reach case: 82.2 / 40.1 / 7.4. Motors and gears per CONTRACTS §1a:
- shoulder_pitch: TBM2G-07608C + CSG-25-100
- elbow: TBM2G-05013C + CSG-20-100
- wrist: 2× TBM2G-05008C + RV12x4, 25 mm arm

Thermal rule: ΔT ≤ 100 K at 40 °C. Not determined: hold duration (no task spec; T5 says "at walking"). Strain-wave efficiency at hold and motor Kt/R hot are Actuators data, so I have not computed them.
**Needed from Thermal:** steady-state and time-to-limit winding ΔT for (a) shoulder_pitch at 61.3 N·m and (b) elbow at 40.1 N·m, continuous hold, with the arm mid-swing in walking airflow. Use the CSG static efficiency and motor Kt/R that Actuators publish. Answer as "minutes to 100 K" per joint. If < 10 min, Arms will propose a brake or a non-backdrivable hold mode.

## O-A3: forearm drive fit (done by Arms, geometry only)
**Repo data:** `model/model_v4.py` forearm shell is OD 70 / **ID 66**. Free bore length is f0 − f1 = (ez − 36) − (wz + 57) = **177 mm** (forearm 270 mm). The elbow housing (OD72) sits above f0, and the wrist_roll housing (OD56 × 34) sits below f1. The v3 hand uses 6 × maxon DCX 22 S + GPX 22 HP (Ø22) and 5 × DCX 16 S + GPX 16 LN (Ø16; GPX16 is 25.7 mm long per `v3/PARTS.md`). The model also calls for 2 wrist pitch/yaw drives in the forearm.
**Cross-section check:**
- 6 × Ø22 in one ring needs ring radius 22.0 mm → **min ID 66.0 at zero clearance**, and 70.0 with 1 mm gaps. At ID 66 there is no room for walls or cable pass-through, so **this layout FAILS**.
- 5 × Ø16 in one ring needs ID 46.9 (1 mm gaps), so that layout fits.
- Total footprint area is 3 286 mm² vs bore 3 421 mm². Single-tier packing is impossible, so two tiers are required.

**Length:** the DCX 22 S, GPX 22 HP and DCX 16 S lengths are **not in the repo**. The `v3/datasheets/dcx16s.pdf` and `gpx16.pdf` files are saved HTML error pages, not datasheets. So the axial fit (tier 1 + tier 2 + spools + 2 wrist drives within 177 mm) **cannot be confirmed**.
**Result:** NOT SHOWN TO FIT. The minimum change is forearm ID ≥ 70 (OD ≥ 74 at 2 mm wall), still inside the sim capsule r 38 (Ø76). The alternative is a 4 + 2 flexor split with 2 flexors in tier 2. Ask to Actuators: the drive lengths (motor + gear + encoder) for these parts, as cited datasheets. Then Arms closes O-A3. I'll propose the ID change to Industrial Design (forearm shell, V5 row 6) once lengths confirm the tier layout.

## O-A4: arm/hand harness and slip ring → RL Electronics
**Determined:** `actuators/results/harness.md` already includes arms in the 1.286 kg line, using clock-spring loops, not slip rings:
- arm trunk pack→shoulder_yaw 2 × 1.465 m, 0.052 kg
- elbow→wrist 0.017 kg
- arm pigtails 0.020 kg
- hand 24 V from wrist DC/DC 0.013 kg
- EtherCAT arm branch → hand/tactile 2 × 2.913 m Belden MRTA2P26S, 0.151 kg

That totals ≈ 0.253 kg for both arms. Harness ROM used: shoulder_yaw 300°, wrist_roll 340°. MRTA2P26S is rated 8e6 torsion cycles at ±180°/m. So **O-A4 part 1 is closed: the arm harness is inside the 1.286 kg line**. Open items:
- the 340° wrist_roll and 300° shoulder_yaw loops exceed ±180°, the range the torsion rating covers
- STO star to the arm drives is not yet in the harness (Electronics A25 item 4)
- P-026 shortens the elbow and wrist loops

**Needed from Electronics:**
1. For wrist_roll ±170° and shoulder_yaw ±150°: clock-spring (as modelled) or slip ring? If clock-spring, confirm the MRTA2P26S rating holds for one 340° loop over the drum length in `cables.json`.
2. Confirm the STO pair runs to the 7 arm drives per side, and give the added mass for arms specifically.
3. Re-run harness loop lengths with the P-026 ROM.

## O-A5: hand drive electronics → RL Electronics
**Determined:** `electronics/R1_ARCHITECTURE.md` gives the hand as **one EtherCAT slave per hand fronting the hand's own bus** (O-E4). Hands run on 24 V from a wrist DC/DC whose part is TBD with Arms. The arm line is sh_pitch→…→wrist×3→hand/tactile node (8 slaves). Hand load: 11 brushed DC motors (6 × DCX 22 S 24 V, 5 × DCX 16 S), each needing current control and position feedback (encoder option not chosen), plus fingertip tactile (T4, part not chosen).
**Needed from Electronics:**
1. Hand-node part or architecture. Proposed: one board with 11 H-bridges + current sense, an EtherCAT slave (ESC) and a tactile ADC/I²C hub. Give your mass/power/size estimate and where it sits: forearm tier 2 or wrist.
2. Wrist DC/DC part (68–84 V → 24 V) and its peak current. Arms peak = 6 flexors stalling at once. Motor stall current is not in repo data; it comes from the DCX 22 S datasheet once fetched.
3. Tactile bus choice (I²C/SPI through wrist pitch/yaw), so Arms can route ≤ N conductors through the wrist cross.

## Summary table
| item | status | owner of next step |
|---|---|---|
| O-A1 | gap 3.59 kg/side quantified; awaiting sim update + mount PCD | Torso & Power |
| O-A2 | holding torques given; thermal minutes-to-limit needed | Thermal (data from Actuators) |
| O-A3 | cross-section FAIL at ID 66; lengths missing | Actuators (lengths) → Arms |
| O-A4 | harness mass inside 1.286 line (closed); loop-vs-slip-ring + STO open | Electronics |
| O-A5 | architecture per Electronics R1; node part, DC/DC, tactile bus open | Electronics |

## R3 update (2026-10-14): P-042 carry pose (A39), Thermal O-A2, Electronics §10
**O-A2: answered by Thermal (`thermal/O-A2_ARM_HOLD.md`, f4e6dfb) and addressed by P-042** (renumbered from P-028, R-031).
- At the R1 carry pose, the elbow at 40.1 N·m reaches +100 K in about 3.6 min (two-node), and the shoulder at 61.3 N·m sits at a steady +91 K.
- The P-042 chest-carry pose is sp −60°, el −110°. It gives elbow 6.95 N·m (+6.7 K) and shoulder 43.45 N·m (+46 K), so the hold is **unlimited**.
- Above 15 N·m on the elbow: ≤ 3 min at 40 N·m, then ≤ 28 N·m (Thermal 7675c8b: 155 °C in 6.0 min at 40.1 N·m). Above 55 N·m static on the shoulder: ≤ 10 min. Both are [EST] until the G5 bench measures τ_w.

**O-A4: closed by Electronics** (`electronics/R1_ARCHITECTURE.md` §10, f4e839c).
- Clock-spring loops, not slip rings.
- STO 0.085 kg, inside the 1.496 kg harness (Actuators D66).
- The P-026 elbow loop is 0.144 m.

**O-A5: hand electronics booked into the arms line** (Electronics §10.4–10.5; both items are [EST]/[DS], ×1.0 once cited).
| item | per hand | both |
|---|---|---|
| hand node 70 × 45 mm, 2–4 W | 0.035 | 0.070 [EST] |
| wrist converter RECOM RP40-11024SFR, /P-HC with heat sink (43–160 V → 24 V / 1.666 A) | 0.043 | 0.086 [DS family, R-026] |
| note-9 input filter | not massed by Electronics | TBD |
| **added** | **0.078** | **0.156** |
Arms + hands now total **19.24 kg vs the 19.08 allowance (+0.156 over)**. Arms asks the Arbiter to book it, offset by P-027 (−1.30 once Actuators cite parts).

**Hand peak current (Electronics' 1.67 A question):** the repo cannot confirm ≤ 1.67 A.
- `v3/analysis/parts.py` holds only DCX 22 S T_cont 15.3 mNm, 66 g, Rth 23 K/W, and DCX 16 S 5.2 mNm. There is no Kt, terminal resistance, nominal or stall current, and the v3 datasheet PDFs are error pages.
- A power bound from v3 data: a full close (30 mm tendon, Ø8 spool, 0.74 s) means the spool turns at 10.1 rad/s, so the motor turns at 1 124 rad/s (111:1). At T_cont that is ≈ 17 W mechanical per flexor, and 6 flexors closing at once is ≈ 103 W mechanical. That is well above the 40 W converter.
- **Decision: the hand node caps total motor current at 1.67 A (40 W) in firmware.**
- Consequences: a loaded six-finger simultaneous close is power-limited to ≈ 40 W and takes ≈ 2–3× longer than 0.74 s [EST]. A no-load close (low torque) and a static grip (copper-only) stay inside the cap, but static grip current needs the DCX 22 S terminal resistance.
- T4 ≤ 1 s close is **at risk under load** at 40 W. Unloaded, it is unaffected.
- If T4 must hold under load, the fallback is a larger converter (RP60-class, not cited).

## R3 update 2: P-027 credit, wrist duty, O-A1 inertials, O-A3 fit, side fall
**Mass line (arms + hands, both sides):** 19.084 allowance. Changes:
- −2 × 0.666 for the P-027 / D67 wrist pair (0.884/side, Elmo drives off-arm)
- +0.156 for the hand node + RP40-11024SFR
- **= 17.908 kg, 1.176 under the allowance**

Per-side catalog total 8.957 kg (`arm_inertials_r3.json`), of which 1.52 sits in the torso wall.

**Wrist drives off-arm:** the 2 Elmo Gold Twitter drives for the wrist pair (and every arm drive) stay booked in the Electronics/Actuators drive line (D66), mounted in the torso shoulder bay. Electronics confirms the phase-lead routing.

**Wrist duty for P-027 L10** (`wrist_duty_r3.py` → `.json`):
- Forces come from Arms load cases at screw = T / 0.025 / 2.
- Time fractions are an [EST] mission profile, since there is no task spec:

| share | force | speed | case |
|---|---|---|---|
| 1 % | 294 N | 1.0 | contract peak |
| 10 % | 148 N | 0.3 | 10 kg manipulation, 7.4 N·m |
| 20 % | 25.2 N | 0.02 | P-042 carry hold, 1.26 N·m |
| 39 % | 20 N | 0.3 | unloaded manipulation |
| 30 % | 20 N | 0.02 | idle |

- Result: Fm 128.3 N, mean 376 rpm.
- **L10 at fw 1.2: 112.6 kh. At fw 1.5: 57.7 kh. At fw 2.0: 24.3 kh.** All pass 14.6 kh.
- Arms recommends **fw 1.5** for contact/impact in manipulation. BNK1004 passes at 3.95×, so the BNK1404 fallback isn't needed.

**O-A1 (closed on Arms' side):** `arm_inertials_r3.json` (script `arm_inertials_r3.py`) gives the catalog mass, COM and full inertia per sim body:

| body | mass (kg) |
|---|---|
| shoulderP | 1.39 |
| upper_arm | 1.16 |
| forearm | 4.415 |
| hand | 0.472 |
| torso add at the shoulder (shoulder_pitch actuator) | 1.52 |

Masses are cited. Placements, radii and lengths are [EST]. Recheck (`recheck_r3.py`):
- reach: shoulder 86.8, elbow 40.8 N·m → shoulder need 130 vs 167 avail, 1.28×
- shoulder_yaw and elbow statics rise ≈ 0.7 N·m

**O-A3 forearm fit (D68 lengths): SHORTFALL.** Bore is Ø66 × 177 mm (model_v4).
- Tier 1, 6 × DCX22S+GPX22HP with ENX22 EASY INT: 70.9 + 1 mm, plus spool ≈ 10 [EST] → **82 mm**. The ring of 6 × Ø22 needs ID 70 at 1 mm gaps, so it **fails at Ø66**.
- Tier 2, 5 × DCX16S+GPX16LN 3-stage with ENX16: 60.7 + 1 + 10 → **72 mm**. Fits in diameter (ID 46.9).
- The two hand tiers take **154 of 177 mm**, leaving 23 mm.
- Wrist pair (D67): 2 × Ø56 cans coaxial with the screws at r 25 reach r 53 > 33. Even side by side they need about Ø112. The screw shafts are 110 mm long. **They do not fit in any remaining space.**
- Hand node 70 × 45: it fits only axially, as a chord at ≤ 24 mm offset, and the 23 mm left over is too short for 70.
- RP40: dimensions are not in the repo (not cited).
- **Total axial need is ≥ 154 + 110 (wrist screws) + 70 (node) ≈ 334 mm against 177: about 157 mm short**, plus the diameter fails.

Options for R4, which need ID (shell) and Arbiter input:
1. Forearm ID ≥ 72 and the hand tiers stretched into the elbow-adjacent zone, with the wrist pair moved to the upper arm, driving through push rods across the elbow. This needs geometry.
2. Wrist pitch/yaw as compact rotary units at the wrist (v4 audit placeholder "micro strain-wave").
3. Hand node and RP40 moved to the upper arm or the palm back.

Until then O-A3 is OPEN/FAIL.

**Side fall (Torso bd02c23):** the bulkhead sees 690 N·m (11.5 kN at 60 mm). It is not clutch-limited: the 300 N·m shoulder_roll clutch caps only the roll gear. On the arm side, 690 N·m enters as a moment on the shoulder_pitch output bearing (v3.py line 99). If any of it reaches the pitch gear as torque, it is above the CSG-25-100 ratchet torque of 650 (momentary 369, parts.py). **Ask Actuators:**
- the shoulder_pitch output crossed-roller static moment rating vs 690 N·m (fs ≥ 1 per v3.py)
- whether shoulder_pitch also needs a slip clutch (≤ 300 N·m)

The arm-side flange stays 8 × M8 12.9 on BC 80 (Torso accepted).
