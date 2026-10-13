# CONTRACTS.md: module interfaces and budgets (v3-derived, rev 0)
Single source of truth for interfaces and budgets (CHARTER). Changes only via PROPOSALS.md → RULINGS.md. Written by RL Arbiter 2026-10-13 from v3.2 results; every number cites its v3 file. Targets referenced are in TARGETS.md (DRAFT).

Sources used: `v3/analysis/results/v3_checks.md` and `v3.json` (per-joint rows, mass, power), `v3/analysis/v3.py` (requirement formulas, housing envelope model), `v3/REVISIONS.md` §F–G, `sim/v3/humanoid_v3.xml`, `sim/v3/balance_v3.json`.

## 0. Global
| item | value | derivation / source |
|---|---|---|
| Robot mass budget | ≤ 65.0 kg (T2) | v3 rollup 63.8 kg → 1.2 kg unallocated reserve (owned by Arbiter) |
| DC bus | 13S Li-ion, 44.2 V min (3.4 V/cell) … 54.6 V max (4.2 V/cell) [max EST from cell chemistry] | `v3.py` VBUS_MIN = 13 × 3.4; Molicel P45B 13S7P, 91 cells, 1474 Wh |
| Drive (every joint) | Novanta Everest XCR: 31.8 A rms cont. / 42.4 A rms 1 s, 80 V max, 38 g | `parts.py` DRIVE (45/60 A crest ÷ √2) |
| Thermal rule | winding ΔT ≤ 100 K at 40 °C ambient | `v3.py` AMB, DT_LIMIT |
| Torque margin rule | available peak ≥ 1.5 × requirement; leg requirements scale with robot mass (req_v2 × m/64.285) | `v3.py` line 126 |
| Life rule | L10 ≥ 14 600 h at walking duty (5 y × 365 × 8 h) | `v3.py` LIFE_H |
| Walking power budget | 622 W total → 2.13 h on 1474 Wh × 0.9 | `v3.json` power: mech 244 + copper 132 + compute 120 + drives 26 × 3.3 = 86 + sensors 40 |
| Field bus / data | **TBD (open Q2)**. v3 selects Everest XCR (EtherCAT/CANopen capable [check datasheet]) but no topology, cycle rate or cabling is specified anywhere in v3 | — |
| Encoders | RLS AksIM-2, 2 per joint (motor + output) | `v3.py` actuator() mass term `2*(ring+head)` |

## 1. Actuator module (owner: RL Actuators)
Supplies every joint actuator (motor + transmission + output bearing + encoders + drive + housing) to the other modules. Owns: motor/gear/screw selection, thermal, drive current, life.

### 1a. Per-joint performance contract (one side; "need" = 1.5 × req, legs mass-scaled)
| joint | type | v3 selection | need peak N·m | v3 avail N·m | need speed rad/s (at 30 % torque) | v3 avail | max mass kg (v3) | copper W walking (v3) |
|---|---|---|---|---|---|---|---|---|
| hip_yaw | rotary | TBM2G-05008A + CSG-14-100 | 24.0 | 36 | 3 | 5.3 | 1.02 | 1.3 |
| hip_roll | rotary | TBM2G-07608C + CSG-25-100 | 122.1 | 167 | 3 | 4.9 | 1.52 | 16.6 |
| hip_pitch | rotary | TBM2G-07608C + CSG-25-100 | 114.8 | 167 | 4 | 4.9 | 1.52 | 15.2 |
| knee | 2× roller screw | TBM2G-06808D + RV12x4, arm 58.5 mm | 231.9 | 238 | 8 | 12.1 | 1.81 | 11.2 |
| ankle_pitch | 2× roller screw (diff.) | TBM2G-06808D + RV12x4, arm 70 mm | 153.2 | 284 | 6 | 10.1 | 1.81 | 18.0 |
| ankle_roll | same screws as ankle_pitch | arm 40 mm | 57.5 | 163 | 4 | 17.7 | 0 (shared) | 1.9 |
| waist_yaw | rotary | TBM2G-06008A + CSG-17-100 | 60.0 | 70 | 2 | 3.4 | 1.03 | 1.4 |
| waist_pitch | rotary | TBM2G-06808A + CSG-25-100 | 115.4 | 116 | 2 | 2.8 | 1.37 | 2.8 |
| shoulder_pitch | rotary | TBM2G-07608C + CSG-25-100 | 148.2 | 167 | 4 | 4.9 | 1.52 | 0.7 |
| shoulder_roll | rotary + 300 N·m slip clutch | TBM2G-06813C + CSG-25-100 | 148.2 | 164 | 4 | 4.1 | 1.24 | 0.3 |
| shoulder_yaw | rotary | TBM2G-06008C + CSG-17-100 | 59.2 | 70 | 4 | 7.6 | 0.81 | 0.2 |
| elbow | rotary | TBM2G-05013C + CSG-20-100 | 73.5 | 76 | 6 | 7.6 | 0.90 | 0.6 |
| wrist_roll | rotary | TBM2G-05008C + CSG-14-100 | 7.4 | 36 | 6 | 11.8 | 0.55 | 0.0 |
| wrist_pitch | 2× roller screw (diff.) | TBM2G-05008C + RV12x4, arm 25 mm | 14.7 | 48 | 6 | 30.1 | 1.55 | 0.0 |
| wrist_yaw | shared with wrist_pitch | arm 25 mm | 8.9 | 48 | 6 | 30.1 | 0 (shared) | 0.0 |
| neck_yaw | rotary | TBM2G-05008A + CSG-14-100 | 3.0 | 36 | 4 | 5.3 | 0.55 | 0.0 |
| neck_pitch | rotary | TBM2G-05008A + CSG-14-100 | 2.1 | 36 | 4 | 5.3 | 0.55 | 0.0 |

Contract: the "need" columns are binding requirements; "max mass" and "copper W" are binding ceilings. Selection is the Actuator module's choice. Speed needs are themselves [EST, v2] (`v3.py` SPEED) — Legs may propose firmer values from gait sim.
Actuator total (both sides, counts from `v3.json` state): **31.97 kg** ceiling; v3 = 31.97 kg. Thin margins (< 5 %): knee 238/232, waist_pitch 116/115, elbow 76/73.5 — these are the first places a mass increase on Legs breaks the actuator contract (leg needs scale with m).

### 1b. Envelope (rotary), from `v3.py` housing() model: D = max(motor OD, bearing OD) + 6 mm; L = stator stack + gear length [EST] + bearing width + 16 mm
| joint | D × L mm | joint | D × L mm |
|---|---|---|---|
| hip_yaw | 96 × 72 | shoulder_pitch | 96 × 86 |
| hip_roll | 96 × 86 | shoulder_roll | 74 × 87 (+ clutch, TBD) |
| hip_pitch | 96 × 86 | shoulder_yaw | 71 × 73 |
| waist_yaw | 86 × 76 | elbow | 61 × 81 |
| waist_pitch | 86 × 86 | wrist_roll, neck ×2 | 56 × 67 |
Linear (knee, ankle, wrist): pin-to-pin envelope from `cad/stroke.py`: knee min length 276 mm ≥ 247 mm stack; ankle 263 ≥ 253 mm (REVISIONS §F). Knee screws at y ±45 mm, lever r 58.5 mm, trunnions x −125 mm (REVISIONS §F).
Gear lengths are [EST] in v3 (`GEAR_LEN`); Actuators must replace them with Harmonic Drive CSG drawing values (AUDIT A4).

### 1c. Mounting
| interface | v3 pattern | load case | source |
|---|---|---|---|
| hip bracket → pelvis | 8 × M5 12.9 | landing 3 BW + 0.10 m moment | v3_checks bolted table |
| hip-pitch flexspline → output flange | 8 × M6 12.9 | momentary peak, friction-transmitted | same |
| knee clevis → femur flange | 4 × M5 12.9 | landing 3 BW, 0.12 m lever | same |
| shoulder actuator → torso frame | 8 × M8 12.9 | side-fall impact | same |
Bolt-circle diameters: v3 uses r_pcd = 50 mm default in `bolted()` [EST]; not tied to CAD. Actuators to publish flange drawings (PCD, pilot, bolt count) per frame size; Legs/Torso design to them.

### 1d. Electrical/data per actuator
Bus 44–55 V DC; ≤ 31.8 A rms cont / 42.4 A rms 1 s phase current; 2 absolute encoders; overhead 3.3 W per drive (`v3.py` line 200). Peak electrical power per joint and per limb: **not computed in v3 — TBD** (open Q3). Connector, bus protocol, cycle time: TBD (§0).

## 2. Leg module (owner: RL Legs)
Owns: pelvis-to-foot kinematics, thigh/shank/foot structure, knee/ankle linkages, foot sensing, leg harness, gait requirements. Consumes actuators per §1.

| budget | value | derivation |
|---|---|---|
| Mass, structure (both legs) | ≤ 5.4 kg | thigh 2.0 + shank 1.6 + feet 1.8 (`v3.json` mass.struct) |
| Mass, leg actuators (both legs) | ≤ 15.36 kg | 2 × (1.02 + 1.52 + 1.52 + 1.81 + 1.81) |
| Mass, leg total | ≤ 20.76 kg | sum; pelvis (1.6 kg) assigned to Torso |
| Walking power, legs | ≤ 409 W | copper 2 × (1.3+16.6+15.2+11.2+18.0) = 124.6 W + whole-robot mech 244 W (all attributed to legs) + 12 drives × 3.3 W = 39.6 W |
| Joint requirements | the leg rows of §1a (torque & speed) | Legs may tighten/revise via gait sim; any revision is a contract change |
| Range of motion | per `sim/v3/humanoid_v3.xml` (e.g. hip_yaw −35…45°, hip_roll −12…15°), knee 0…135° stops (clash-free to 145°) | REVISIONS §F–G |
| Hip spacing | hip joints at y ±130 mm; hip_roll axis 115 mm below hip_yaw | humanoid_v3.xml |
| Structural | FEA SF ≥ 2 fall, Goodman over 5 y for walking: femur 10.6, tibia 6.2, knee clevis 10.1 (v3) | fea_v3 table |
| COM / balance | standing COM within foot (v3 +4.4 mm ahead of ankle; foot −60…+180 mm); stand 10 s + recover 125 N/0.2 s pushes with balance on | REVISIONS §G, balance_v3.json |
| Interface to Torso | hip bracket → pelvis 8 × M5 (§1c) | |

## 3. Placeholders (no owner yet; v3 allocations hold until a module is staffed)
| module | mass budget (v3) | power budget (v3) | interfaces to define |
|---|---|---|---|
| Torso (pelvis, torso frame, waist actuators, battery, harness, covers, thermal) | pelvis 1.6 + torso 2.8 + harness 2.0 + covers 1.86 + thermal 1.0 + battery 7.96 = 17.2 kg (+ waist actuators 2.40 kg in §1) | battery supplier: 1474 Wh, 622 W walking | shoulder mounts 8×M8, hip mounts 8×M5, pack swap, BMS, e-stop |
| Arms (structure) | 1.6 kg | ~3.6 W copper (arm rows ×2) | shoulder/elbow/wrist flanges, payload case T5 |
| Hands | 4.2 kg both (`v3.json` hands) | not separately budgeted (TBD) | wrist flange, tendon routing, tactile bus |
| Head (incl. neck structure, sensors) | 1.6 kg | in 40 W sensors line | neck flange, cameras |
| Brain (compute) | 1.8 kg | 120 W | bus master, sensors, safety |
| Arbiter reserve | 1.2 kg | — | 65.0 − 63.8 |
