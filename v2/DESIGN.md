# Robot Lab v2: Berkeley Humanoid Lite, re-engineered toward Optimus Gen 2/3 class
*Oct 12, 2026 · Draft for Bryan Ralston · Every number marked **[EST]** is an engineering estimate. Sourced facts carry a citation. Checks live in `analysis/` and results in `analysis/results/`.*

## 0. Honest framing
v2 keeps what makes **Berkeley Humanoid Lite (BHL)** work: one smart actuator per joint, a bus per limb, a central policy computer, and RL sim-to-real. Everything else is re-engineered to a full-size, metal-geared, Optimus-class architecture. "Works if manufactured" here means the design passes **first-order** checks: torque and speed with a 1.5× margin, I²R thermal, link stress with SF ≥ 2, mass, power, COM, and hand force. It has **not** been validated by FEA, actuator dyno tests or a prototype. Those are listed as gaps in §10.

## 1. Reference facts (sourced)
| | Berkeley Humanoid Lite | Tesla Optimus |
|---|---|---|
| Height / mass | 0.8 m / 16 kg [BHL] | Gen 1: 1.73 m, 73 kg (reported) [F22][HV]; Gen 2: "10 kg total weight reduction" [ARS] |
| Body DoF / actuators | 22 actuators: 10× 6512 + 12× 5010 modules (BOM) [BHL] | 28 structural actuators; 6 actuator types (3 rotary, 3 linear) [R247] |
| Actuators | 3D-printed **cycloidal** gearbox + drone BLDC (MAD M6C12 150KV on the 6512), B-G431B-ESC1 FOC driver, AS5600 encoder, CAN [BHL] | Rotary actuators with strain-wave gearing; linear actuators with planetary roller screws; one linear actuator lifted a half-ton concert grand piano [AID][R247] |
| Hands | Simple grippers [BHL] | Gen 1/2: 11 DoF, 6 actuators, metal tendons [AID][R247][ARS]. Gen 3: 22 DoF/hand with forearm actuators (reported, not an official spec sheet) [OPT] |
| Battery | 6S 4000 mAh LiPo, ~30 min [BHL] | 2.3 kWh, 52 V; ~100 W sitting, ~500 W walking [F22] |
| Compute | Intel N95 mini PC [BHL] | Tesla FSD computer [HV] |
| Gen 2 additions | n/a | 2-DoF actuated neck, foot force/torque sensing, articulated toes, tactile sensing on all fingers, actuator-integrated electronics [ARS] |
| Cost | < $5,000 hardware [BHL] | not public |

## 2. v2 headline specs (all [EST], each backed by a check)
| Spec | v2 | Check |
|---|---|---|
| Height | 1.73 m | geometry |
| Mass | **64.8 kg** (target ≤ 65) | mass budget: PASS after fixes (initially 90.3 kg) |
| Body DoF | 30: legs 2×6, waist 2, arms 2×7, neck 2 | |
| Hand DoF | 22 per hand (17 actuated + 5 coupled DIP), actuators in the forearm | hand tendon and grip: PASS after fixes |
| Actuators | 32 body actuators (18 rotary strain-wave, 14 linear roller-screw), plus 34 hand micro-actuators | torque/speed: all 17 joint types PASS |
| Payload | 20 kg squat-lift (both arms); 10 kg per arm at reach | torque checks |
| Walking speed design point | 1.2 m/s (joint speeds sized for about 1.5 m/s) | speed checks |
| Battery | 2.3 kWh, 52 V (Optimus-matched target) | |
| Runtime | 3.8 h walking / 8.1 h standing / **5.2 h mixed** | power: PASS (≥ 4 h mixed) |
| Compute | NVIDIA Jetson AGX Thor T5000 (40–130 W [NV]) + safety MCU | power budget |

## 3. Joint and actuator table (final, v2.1)
Motor classes are **generic frameless PMSM sizes** (M115/M85/M60/M38 = stator OD in mm), with constants estimated in `design.py`. Candidate families to source from are Kollmorgen TBM2, Allied Motion MF, Parker K-series, and CubeMars RI/RO. **Verify Km and Rth against datasheets before freezing.** Strain-wave ratings are Harmonic Drive CSG catalog values [HD]. Size-14 and size-11 wave gears are estimates.

| Joint (×2 if limb) | Architecture | Motor | Transmission | Peak torque avail. (N·m) | Required ×1.5 (N·m) | Max speed (rad/s) |
|---|---|---|---|---|---|---|
| Hip yaw | rotary | M60 | CSG-20-100 (rep. peak 107) | 107 | 24 | 6.3 |
| Hip roll | rotary | M115, 4500 rpm winding | CSG-25-100 (204) + crossed-roller support bearing | 204 | 124 | 4.7 |
| Hip pitch | rotary | M115, 4500 rpm | CSG-25-100 (204) + crossed-roller support bearing | 204 | 117 | 4.7 |
| Knee | **linear**: inverted planetary roller screw, 5 mm lead, 45 mm lever | M85, 5000 rpm | roller screw → linkage | 226 | 166 | 9.3 |
| Ankle pitch + roll | **2 parallel linear** (differential), 4 mm lead, 50/40 mm levers | 2× M60 | roller screws | 251 / 201 | 156 / 58 | 8.0 / 10 |
| Waist yaw | rotary | M60 | CSG-20-100 | 107 | 60 | 6.3 |
| Waist pitch | rotary | M85 | CSG-25-100 | 204 | 118 | 5.2 |
| Shoulder pitch / roll | rotary | M85 | CSG-25-100 | 204 | 148 | 5.2 |
| Shoulder yaw | rotary | M60 | CSG-20-100 | 107 | 59 | 6.3 |
| Elbow | **linear**, 4 mm lead, 40 mm lever | M60 | roller screw | 101 | 73 | 10 |
| Wrist roll | rotary | M38 | size-14 strain-wave [EST] | 28 | 7 | 8.4 |
| Wrist pitch + yaw | **2 parallel linear**, 2 mm lead | 2× M38 | roller screws | 63 | 15 / 9 | 10.7 |
| Neck yaw / pitch | rotary | M38 | size-11 strain-wave [EST] | 11 | 3 / 2 | 8.4 |

Requirement basis: the maximum of (a) human-normalized peak joint moments for level walking and stair ascent [EST, from gait literature, scaled by robot mass], (b) a static double-support squat at 110° knee flexion holding 20 kg, solved with trunk lean for COM over the mid-foot, and (c) bent-knee single support at 1.3×BW. All are then ×1.5.

**Every actuator module includes:** frameless PMSM, integrated GaN/MOSFET FOC driver (52 V, sized for ~110 A peak on the M115 [EST]), dual absolute encoders (motor and output), a winding NTC, CAN-FD/EtherCAT, and a hollow shaft. This follows the BHL "smart module" idea and Optimus Gen 2's actuator-integrated electronics [ARS].

## 4. Hands (22 DoF)
- **Kinematics:** thumb 5 (CMC 2, MCP 2, IP 1). Index, middle, ring and little 4 each (MCP flex and abduction, PIP, DIP). Palm arch 1. That makes **22**. DIP is coupled to PIP by linkage on all four fingers plus the thumb IP, giving **17 actuators per hand**.
- **Drive:** 17 Ø16 mm BLDC micro-motors (Maxon EC-i/ECX class, torque [EST]) in the forearm. Each drives an M3×0.5 ball screw pulling a **1.5 mm UHMWPE (Dyneema-class) tendon**, with antagonistic return springs and an 11 mm MCP pulley radius. This is tendon-driven like Optimus [AID] and NEO.
- **Checks [EST]:** peak tendon force 352 N vs a 500 N allowable (SF 4 on break load) gives **PASS**. Peak fingertip force is 43 N vs 36.8 N required (10 kg hook grasp ×1.5), also **PASS**. **However, continuous fingertip force is only 14.7 N, so holding 10 kg indefinitely is not supported** (see gaps).
- **Sensing:** tendon tension (strain gauge at the screw nut), Hall joint encoders, and fingertip/phalanx tactile arrays. Optimus Gen 2 has tactile sensing on all fingers [ARS].

## 5. Structure and materials
- **Femur:** 7075-T6 tube Ø50×2 mm with machined end lugs. Landing at 3×BW: 72 MPa, SF 7.0 on yield. Walking fatigue: SF 5.1 on the 159 MPa endurance limit.
- **Tibia:** 7075-T6 tube Ø45×2 mm. Landing SF 6.7, fatigue SF 4.9. These are simple beam models with a 0.10–0.12 m effective bending lever [EST]; they need FEA at the lugs and bolt holes.
- **Hip:** 8× M5 12.9 bolts on a 90 mm PCD, SF 15.5. The hip-pitch output has a **dedicated crossed-roller support bearing (allowable moment ≥ 600 N·m [EST], ~Ø140 mm class)** that carries the full landing moment of 191 N·m alone, for SF 3.1. The CSG-25 output bearing is not credited because its moment rating isn't in the sources I used. In v2.0 (CSG-32 bearing alone, Mc 313 N·m catalog [HD], 266 N·m moment at 90 kg) SF was 1.18, which **failed**.
- **Pelvis:** machined 7075. **Torso:** 7075 spine frame with CF-sandwich shells. The battery is a structural member between pelvis and shoulder girdle.
- **Feet:** 7075 plate with a 6-axis F/T sensor at the ankle and a passive spring toe. Optimus Gen 2 has foot F/T and articulated toes [ARS].
- **Covers:** replaceable padded textile.

## 6. Sensors
- **Head:** stereo global-shutter pair plus wide side cameras, and a mic array.
- **Pelvis:** tactical-grade IMU plus a redundant MEMS IMU. BHL uses a phone-grade IMU [BHL]; this is the upgrade.
- **Joints:** dual encoders, phase currents and winding temperature.
- **Feet:** 6-axis F/T. **Wrists:** 6-axis F/T. **Hands:** tactile and tendon tension.

## 7. Compute and electronics
- **Compute:** Jetson AGX Thor T5000 for perception, policy and VLA [NV], plus a lockstep safety MCU with STO (safe torque off) on every driver.
- **Buses:** 4× CAN-FD at 5 Mbps (one per limb, as in BHL) or EtherCAT. The policy runs at 50 Hz and joint PD at 1 kHz on the drives.

## 8. Battery and power
- **Pack:** 2.3 kWh, 52 V (14S NMC, ~10 kg at ~230 Wh/kg pack-level [EST]) with BMS and pre-charge. This matches Optimus's published pack size [F22].
- **Power model [EST]:** mechanical COT 0.20 at 1.2 m/s, plus copper losses from the thermal model, plus compute (110 W), sensors (25 W), idle drivers (40 W) and cooling (30 W).
  - Walking: 548 W, comparable to Tesla's ~500 W walking figure [F22].
  - Standing: 254 W.
  - Mixed: 401 W, giving 5.2 h at 90% usable capacity.

## 9. Thermal
I²R model with first-order RC per motor: 1 h walking, then 10 cycles of a 10 s 20 kg squat hold plus 50 s walking. The limit is a 115 K winding rise (155 °C class F at 40 °C ambient).
- **Worst joint:** ankle (M60) at 63 K, then knee (M85) at 60 K. All joints PASS.
- **Why the margins are large:** the 100:1 wave gears and roller screws keep motor torque low. The real thermal risks are **gear and screw losses** (not modeled) and **drive MOSFET** temperatures.
- **Cooling:** forced air through the thighs and shanks, and a liquid cold plate for Thor.

## 10. What changed after the checks failed (v2.0 → v2.1)
| Failed check (v2.0) | Fix (v2.1) |
|---|---|
| Mass 90.3 kg | CSG component sets in our own housings instead of housed 2UH units (catalog: CSG-32 component set 0.89 kg vs 3.2 kg unit) [HD]. CF torso shells. 230 Wh/kg pack. Downsized over-margined joints (hip yaw, waist, hip pitch, knee motor). Overhead model refined by motor size. Result: 64.8 kg |
| Hip pitch speed 3.1 < 4 rad/s | 4500 rpm winding at 52 V (Km unchanged, so thermal unchanged; higher drive current) |
| Knee, ankle, elbow and wrist speed | Re-chose roller-screw lead and lever arm (e.g. knee 4 mm/50 mm → 5 mm/45 mm; ankle 2 → 4 mm lead) |
| Hip output bearing moment SF 1.18 | Added a crossed-roller support bearing (≥ 600 N·m [EST]) sized to carry the full moment alone → SF 3.1 |
| Hand grip 31 N < 36.8 N | MCP pulley radius 8 → 11 mm |
| Hand tendon SF < 4 | 1 mm → 1.5 mm UHMWPE line |

## 11. Simulation and control status
- **Model:** `sim/v2/humanoid_v2.xml`, 64.4 kg, 30 actuators, torque limits equal to the checked peak capacities.
  - Inertias come from geom shapes with the budgeted masses.
  - Reflected rotor inertia (armature) is estimated from the rotor class × ratio².
  - Linear actuators are modeled as equivalent rotary joints.
- **RL walking:** **not trained.** The box has 8 CPU cores and about 1 GB of free RAM and no GPU. A 30-DoF humanoid walking policy in MJX/Brax on CPU would need many hours to days. It is the next step, on a GPU in Isaac Lab or MJX, reusing BHL's training stack.
- **Controller instead:** a **scripted standing-balance controller** (`sim/v2/balance_v2.py`): joint PD plus COM-feedback ankle/roll strategy.
  - It stands for 20 s. Plain PD with bent knees falls.
  - It recovers from 0.2 s pushes of 175 N forward and 125–175 N sideways.
  - There is no stepping, so it cannot recover from larger pushes.

## 12. Remaining gaps to Optimus (honest)
1. **No hardware validation.** Motor constants, roller-screw efficiency and life, and gear efficiency at low load are estimates. Optimus's actuators are custom, dyno-validated parts.
2. **Roller screw life and shock** are not checked (L10 life, buckling, and impact on falls). Roller screw parts are not selected yet.
3. **Hand:** holds peak grip only briefly (continuous fingertip force 14.7 N). There is no tactile-skin design detail and no durability data.
4. **Control:** no walking, no stepping recovery, and no whole-body or VLA policy. Optimus demonstrates walking and dexterous manipulation [ARS].
5. **Thermal model** ignores gear, screw and driver losses and the enclosure. **Structure** is beam-theory only (no FEA or fatigue at joints).
6. **Mass** sits at 64.8 kg, right at the target, and is within estimate uncertainty (±10% [EST]).
7. **Manufacturing:** no CAD, tolerance stack or DFM. Optimus is designed for volume production [R247].

## Sources
- [BHL] "Demonstrating Berkeley Humanoid Lite…", RSS 2025, arXiv:2504.17249: https://arxiv.org/abs/2504.17249 · repo: https://github.com/hybridrobotics/berkeley-humanoid-lite
- [AID] Tesla AI Day 2022 (video): https://www.youtube.com/watch?v=ODSJsviD_SU
- [R247] Robotics 24/7, "Tesla shares more details about Optimus": https://www.robotics247.com/article/tesla_shares_more_details_about_optimus_humanoid_robot
- [F22] Forbes, "Tesla Bot Optimus: Everything We Know So Far" (Oct 2022): https://www.forbes.com/sites/johnkoetsier/2022/10/01/tesla-bot-optimus-everything-we-know-so-far/
- [HV] HumanoidVersus, Optimus Gen 1 (73 kg reported): https://humanoidversus.com/robots/tesla-optimus-gen-1
- [ARS] Ars Technica, Optimus Gen 2 (Dec 2023): https://arstechnica.com/information-technology/2023/12/teslas-latest-humanoid-robot-optimus-gen-2-can-handle-eggs-without-cracking-them/
- [OPT] Optimusk blog, Optimus Gen 3 hardware (third-party, unofficial): https://optimusk.blog/blog/tesla-optimus-hardware-specs/
- [HD] Harmonic Drive CSG catalog/product pages: https://www.harmonicdrive.net/products/gear-units/gear-units/csg-2uh/csg-32-100-2uh · https://www.harmonicdrive.net/products/component-sets/cup-type/csg-2a/csg-32-100-2a-gr · https://www.harmonicdrive.net/_hd/content/documents1/CSG-CSF_GearUnits.pdf
- [NV] NVIDIA Jetson Thor: https://www.nvidia.com/en-us/autonomous-machines/embedded-systems/jetson-thor/
