# RL Electronics R1: electronics architecture (compute, drives, buses, sensors, harness, safety chain)

Owner: RL Electronics (4066f15e). Date 2026-10-14. Status: **proposal for Arbiter ruling** (A11, A24) and **interface proposal to RL Actuators** (A25). No targets, contracts or other modules' files are changed by this commit.

Evidence labels: **[DS]** datasheet/manual read (source given), **[REPO]** already cited and accepted in this repo (ruling given), **[UNVERIFIED]** part exists/plausible but the number was not checked against a primary source this round, **[EST]** engineering estimate. No spec in this file was invented; anything without [DS]/[REPO] must be checked before purchase.

## 0. Findings that change existing bookings (read first)

1. **The booked brain converter cannot work.** `arbiter/a3_size.py` books Vicor **DCM3623x75H26C2** (24 g). Its datasheet [DS: vicorpower.com DCM3623x75H26C2yzz_ds.pdf] is **36–75 V in, 24.0 V out (14.4–26.4 trim), 320 W**. Two mismatches:
   - input max 75 V < pack 84 V max (and < 90 V regen clamp, R1.3);
   - output 24 V < Gauntlet AGX301 input **+36 to +60 V DC** [DS: connecttech.com AGX301 product page, "Input Power", 6-pin Mini-Fit Jr.].
2. **Harness "compute 24 V feed"** (`actuators/results/harness.md`) should be a 48 V feed (AGX301 needs 36–60 V). Gauge 1.0 mm² still suffices (lower current); mass unchanged.
3. ~~Elmo R70/100 not in the install guide~~ **CORRECTED (R1.1, see §9.1):** the guide on file *does* list it in §4.4 Table 3 "R Type Models Technical Data". My R1 grep only read Table 1. R70/100: 10–95 V supply, 85 V nominal, 49.5 A rms / 70 A amplitude continuous, 5.6 kW.
4. **Voltage margin:** regen clamp 90 V vs drive 95 V absolute max = 5 V (5.6 %). Acceptable only with a hard clamp (brake chopper / TVS) that is verified on the G5 bench, see §6.

## 1. Power architecture

| node | part | key verified specs | label |
|---|---|---|---|
| Pack | 20S5P Molicel P45B, 68–84 V, 60 A cont / 100 A 2 s, fuse 125 A | per CONTRACTS R1.3 | [REPO R-010] |
| Main fuse + pre-charge + contactor | fuse 125 A (R1.3); contactor and pre-charge resistor **to be selected** (must open under fault current at ≤ 90 V DC) | — | [EST] part TBD (Torso & Power) |
| Motor bus | 68–84 V direct to every Elmo VP+ | drive VP+ 10–95 V [DS MAN-G-TWI Table 1] | [DS] |
| Regen clamp | brake chopper/TVS to hold bus ≤ 90 V | 90 V is the R1.3 design value | [EST] part TBD |
| Brain 48 V rail (**A11 proposal**) | **Vicor DCM3623TA5N53B4T00** | **43–154 V in, 48.0 V out (28.8–52.8 V trim), 240 W, 5.0 A**, 38.72 × 22.8 × 7.21 mm ChiP, isolated, SELV, arrays up to 8 [DS: vicorpower.com DCM3623xA5N53B4yzz_ds.pdf + product page]; Vicor common-mode choke 47718-232 (43–154 V, 8 A) listed for it [DS product page] | [DS]; mass 24 g assumed from same 3623 package **[UNVERIFIED for this variant]** |
| Head 12 V | RECOM RP40-11012SFR/P-HC + note-9 filter | 43–160 V in, 12 V/3.33 A | [REPO R-026/R-027] |
| Drive logic VL | from the 48 V rail through a 24 V point-of-load **or** single-supply from VP+ on S/H drive variants (guide §10.2.4.2 "Single Power Supply Topology (VP+ < 95VDC)") | VL must be SELV/PELV [DS §4.5]; < 4 W per drive at 24 V [DS §4.5 table] | [DS]; choice open (O-E3) |
| Hands 24 V | wrist DC/DC (harness model) | part TBD with Arms & Hands | [EST] |

DCM3623TA5N53B4 vs the 120 W brain budget (CONTRACTS §3): T5000 module 40–130 W [REPO humanoid_plan_v1.md, NV]. 240 W rating leaves margin for carrier + JCB022 PoC + NVMe, but the AGX301 board's own consumption and JCB022 power are **[UNVERIFIED]** (not in the extracts read). Rule: Thor runs a capped nvpmodel so module + carrier ≤ 200 W [EST]; if the bench shows more, add a second DCM in array (no derating per datasheet). Supply risk: Vicor product page shows 52-week lead time and 0 distributor stock (2026-09-12) — this is a T10/G1 risk, not a mass item.

## 2. Compute

| function | part | interfaces used | label |
|---|---|---|---|
| AI + EtherCAT master | NVIDIA Jetson T5000 on Connect Tech **AGX301 Gauntlet** | 2× 1GBASE-T (one = EtherCAT master port), 2× 10GBASE-T, 16-lane MIPI expansion (JCB022), 2× RS-232/RS-485 FD (neck Dynamixel), 4× CAN FD (T5000 only), GPIO 4 in/6 out @ 3.3 V, 2× M.2 M NVMe, −40…+85 °C, 155 × 126 mm [DS AGX301 page] | [DS] |
| Camera deserializer | **Connect Tech JCB022** (MAX9296A ×4, 8× GMSL2, PoC, 45 g, 75 × 57 mm, MATE-AX quad coax, short protection, V/I monitor) | [DS connecttech.com GMSL2 Plus page] | [DS]/[REPO R-025] |
| Safety / RT MCU (A11 part pick) | **TI TMS570LC4357** (dual Cortex-R5F lockstep, ASIL-D/SIL-3 capable family) on the brain tray | owns STO lines, e-stop inputs, watchdog of Thor EtherCAT cycle | [UNVERIFIED] part choice; mass 0.040 already booked [EST] in a3_size |
| Storage | NVMe 2280 | — | [REPO a3_size, EST] |

EtherCAT master on Thor: Linux PREEMPT_RT + IgH EtherCAT Master or SOEM, 1 kHz DC (R1.4). Jitter on T5000 **[UNVERIFIED]** — bench item O-E1. The safety MCU is **not** the EtherCAT master; it only observes and can force STO.

## 3. Field buses / topology

```
               AGX301 (Thor)                         safety MCU (TMS570)
   1GbE#1 ── EtherCAT junction PCB (torso, 0.020 [EST], harness M3)
                 ├─ L leg line:  hip_yaw→hip_roll→hip_pitch(2)→knee(2)→ankle(2)→foot F/T      (8 slaves)
                 ├─ R leg line:  same                                                      (8)
                 ├─ L arm line:  sh_pitch→sh_roll→sh_yaw→elbow→wrist×3→hand/tactile node     (8)
                 ├─ R arm line:  same                                                      (8)
                 └─ waist line:  waist_yaw→waist_pitch (+ torso IMU node optional)           (2–3)
   RS-485 #1 ── neck: 2× Dynamixel XM430-W350-R daisy chain (R-025 c, current limit 1.5 A addr 38, R-027)
   MIPI ── JCB022 ── 1× GMSL2 coax (PoC) ── ZED X Mini (head)
   GPIO/SPI ── torso IMU (if not on EtherCAT)
```
Slave counts follow `actuators/harness.py` (E list: 8/leg, 8/arm, 5 for waist+neck+head) — with the neck on RS-485 (R-025 c) the waist line drops to 2–3 slaves. Per-branch line topology from a torso junction is kept (as harness model); a junction is an EtherCAT branch device (e.g. Beckhoff EK1122-class function on a custom PCB, [UNVERIFIED] part). Line redundancy (ring) is **not** proposed in R1: cable mass, and STO, not EtherCAT, is the safety function.

Drive count: harness model uses 34 drives (incl. twin-motor hip_pitch/knee/ankle). Hands' 11 drives/hand are **not** Elmo/EtherCAT here; the hand node is one EtherCAT slave fronting the hand's own bus — interface owned with Arms & Hands (open O-E4).

## 4. Sensors

| sensor | proposal | label |
|---|---|---|
| Joint position | Renishaw/RLS AksIM-2 absolute encoders (actuator module, G1 list) | [REPO] |
| Head stereo | ZED X Mini via JCB022 (A24 below) | [REPO R-025] |
| Torso IMU | candidate Analog Devices ADIS16470 (SPI) — specs not checked this round | [UNVERIFIED] |
| Foot F/T | on EtherCAT leg end (harness model) — part not yet selected | [EST] |
| Fingertip tactile | T4 requires it; part with Arms & Hands | [EST] |
| Pack/BMS | BMS state + current shunt to safety MCU (CAN FD) | [EST] part TBD with Torso & Power |
| Drive temperature | motor thermistor via encoder lead (harness "encoder/thermistor leads") | [REPO harness] |

## 5. Safety chain (e-stop, STO)

Facts from the Elmo guide on file [DS MAN-G-TWI]: every Gold Twitter has **two opto-isolated STO inputs (STO1, STO2, STO_RET)** on the MAIN connector (pins 12–14), 5 V logic level, with a PLC 24 V connection variant via 1 kΩ series resistor (Figs 37/38, §10.4.3); full STO details are in the "MAN-G-Board Level Modules Hardware manual" ch. 9, **not on file** — required before claiming a SIL/PL (O-E2).

Chain (proposed):
1. **Inputs:** back-mounted mushroom e-stop (2 NC channels) + wireless e-stop receiver (2 channels) + safety-MCU internal faults (EtherCAT cycle watchdog loss > 3 cycles [EST], IMU fall detect, bus over-voltage > 90 V, pack fault). E-stop button and radio parts TBD [EST].
2. **Logic:** TMS570 drives two independent STO rails (STO1 bus, STO2 bus), each through its own driver, to all 34 drives in parallel (star from torso, 2-core 0.25 mm² per branch — the harness model has only the back-button loop; see A25 item 4).
3. **Stop category:** default **SS1** (commanded controlled stop via EtherCAT, then STO after ≤ 300 ms [EST]) because a humanoid dropped by pure STO (Cat 0) falls; **Cat 0 STO** immediately on e-stop button or MCU self-fault. Fall-on-STO behaviour must be covered by T8 (falls on pads).
4. **Main contactor** opens on e-stop after STO (de-energizes bus); pre-charge on restart.
5. Restart requires manual reset (no auto-restart).
A real PL d / SIL 2 claim needs the Elmo STO manual, an FMEDA and a certified reset device — out of scope for R1, listed as O-E2.

## 6. Harness (M3, owned by RL Actuators; Electronics = electrical interface)
Accepted as-is: `actuators/results/harness.md` routing, Lapp SiF / Stäubli SILI-E power cores, Belden MachFlex MRTA2P26S EtherCAT, Amass/JST connectors, 1.286 kg credited (R-022). Electronics requests (A25 proposal, §7.3).

## 7. Proposed resolutions

### 7.1 A11 (Thor power and GMSL2) — proposed CLOSE with changes
- GMSL2: **JCB022** on the AGX301 MIPI expansion, +0.045 kg as booked in R-025 §4. **Drop JCB009 as an alternative**: JCB022 is the board named in CTI's Thor BSP release notes (see A24); JCB009 is listed as "adapter support" but without ZED X named.
- Power: **replace DCM3623x75H26C2 (36–75 V → 24 V) with DCM3623TA5N53B4T00 (43–154 V → 48 V, 240 W)** [DS]. Same 3623 ChiP package → mass 0.024 kept, label [UNVERIFIED for variant] until datasheet mass is read; add Vicor choke 47718-232 mass [UNVERIFIED] inside the existing dcm_filter_heatsink 0.030 [EST].
- Carrier input confirmed **36–60 V** [DS]; 48 V nominal sits inside.
- RT MCU: TMS570LC4357 [UNVERIFIED], mass inside existing rt_safety_mcu 0.040 [EST].
- Cold plate / tray drawings remain open (Thermal / Torso), not Electronics.
- Mass effect: 0.000 (like-for-like), power: no change to the 120 W compute line; converter efficiency not yet read from the TA5N53B4 datasheet → keep the existing compute loss assumption [EST].

### 7.2 A24 (ZED X Mini on CTI board) — proposed CLOSE (conditional)
Evidence:
- Connect Tech Jetson Thor BSP release notes **THOR-38.4.0** (JetPack 7.1): supported cameras include "Stereolabs Zedx Stereocam", "Zedx One GS", "Zedx One 4K"; AGX301 feature list "JCB022 GMSL adapter support"; ZED X drivers are included in the BSP, enabled via `zed_x_daemon.service`, ZED SDK for JetPack 7.1 (L4T 38.4) installed separately [DS: connecttech.com/ftp/Drivers/L4T-Release-Notes/Jetson-Thor/THOR-38.4.0.pdf].
- Stereolabs staff (forum, 2026-03-06): supported Thor partner boards are "Connectech Gauntlet carrier board" and Advantech MIC-742; partner boards use a GMSL capture card on the same MIPI workflow as AGX Orin [community.stereolabs.com/t/10961]. Stereolabs help center: partner carriers support ZED X, **ZED X Mini**, ZED X One on Thor T5000.
- Residual gap: CTI release notes name "Zedx Stereocam", not "ZED X Mini" explicitly. Same GMSL2 driver family [UNVERIFIED]. Condition: first-article bring-up test (stream + ZED SDK depth) before series order; fallback is not ZED Link (no Samtec connector on AGX301; ZED Link cards target devkits/Advantech) but a ZED X (non-Mini) at its own mass under R-024.
- Recommended config: AGX301 + JCB022 + CTI BSP r38.4.0 or later (r39.2.0 / JP7.2 also published 2026-09-02), ZED SDK matching JetPack. Mass: no change.

### 7.3 A25 (harness) — interface proposal to RL Actuators
Principle: **M3 owns every conductor that crosses the neck joint; the head line owns only wiring inside the head.**
1. Delete M3 run "head cameras data (2 × quad, completeness)" 0.024 kg (2× Belden quad). Replace with **one GMSL2 50 Ω coax** JCB022 (MATE-AX) → FAKRA → ZED X Mini, routed through the neck clock-spring; cable part/g·m TBD by Actuators (flex-rated coax, [EST] until cited). PoC removes any separate camera power pair.
2. Keep M3 "neck/head bus" (0.75 mm² pair, 68–84 V to the head RP40) and add **one RS-485 FD pair** (AGX301 → Dynamixel) — could share the MachFlex quad already in "ECAT waist+neck+head", whose neck/head segment is otherwise obsolete since the neck left EtherCAT (R-025 c).
3. Shorten "ECAT waist+neck+head" to the waist segment only; the freed quad length to the head carries RS-485 (item 2).
4. Add **STO 2-wire star** to all drive branches (0.25 mm² SiF ×2 alongside each EtherCAT branch) — currently missing from the harness model (only the back e-stop loop is modelled). Rough add: ~13 m × 2 × 5.4 g/m ≈ 0.14 kg [EST] (lengths from the EtherCAT branch table; Actuators to compute properly).
5. Change "compute 24 V feed" to **48 V** (no mass change).
6. Head line 0.060 [EST] then covers only in-head: RP40 + note-9 filter carrier wiring, servo daisy-chain, FAKRA pigtail ≤ 0.1 m. Robot Lab (head) to re-estimate; expected reduction removes the double count.
Net: −0.024 + coax (TBD) + STO ~+0.14 [EST] + head reduction (TBD).

## 8. Open items (Electronics)
| # | item | owner | needed for |
|---|---|---|---|
| O-E1 | EtherCAT 1 kHz jitter on T5000 PREEMPT_RT (bench) | Electronics/Controls | G4/G5 |
| O-E2 | Elmo MAN-G-Board Level Modules ch. 9 STO + FMEDA → PL/SIL claim | Electronics | safety hard constraint |
| O-E3 | drive VL: single-supply S/H variant vs 24 V PoL | Electronics + Actuators | G1 |
| O-E4 | hand bus interface (one EtherCAT slave per hand) | Electronics + Arms & Hands | G1 |
| O-E5 | ~~Elmo R70/100 datasheet~~ CLOSED R1.1: on file, Table 3; R-type peak current not tabulated | Actuators | G1 |
| O-E6 | regen clamp part (≤ 90 V, 5 V under drive abs max) + contactor/pre-charge | Electronics + Torso & Power | safety |
| O-E7 | DCM3623TA5N53B4 mass CLOSED R1.1 (24.0 g, datasheet); efficiency values not readable in the PDF text; lead time 52 wk | Electronics | T2 evidence, T10 |
| O-E8 | IMU, foot F/T, e-stop, radio e-stop parts cited | Electronics | G1 |

Sources fetched this round (2026-10-14): Connect Tech AGX301 product page; Connect Tech GMSL2 Plus (JCB022) page; CTI THOR-38.4.0 and THOR_38.2.1 release notes; Stereolabs help center article 8527024569 and forum threads 9953/10961/11115; Vicor DCM3623x75H26C2 and DCM3623xA5N53B4 datasheets/product pages; repo `actuators/datasheets/elmo_gold_twitter_install_guide.txt`.

## 9. R1.1 addendum (2026-10-14, after R-028: A34, Vicor mass, regen clamp, A33 STO wiring)

### 9.1 A34: Elmo Gold Twitter R70/100. Verified, keep it
- **The repo copy has it:** `actuators/datasheets/elmo_gold_twitter_install_guide.txt` (MAN-G-TWI Ver 2.011) §4.4 **Table 3 "R Type Models Technical Data"**, column R70/100: min 10 V, **nominal 85 V, max 95 V**, **5.6 kW** max continuous electrical output, efficiency > 99 % at rated power, output up to 96 % of bus, **70 A** amplitude sinusoidal/DC continuous, **49.5 A** sinusoidal continuous RMS (Ic). R50/100: 10/85/95 V, 4.0 kW, 50 A / 35.3 A rms. [DS]
- **Elmo's own site agrees:** product page https://www.elmomc.com/product/gold-twitter/ ("Ultra high current: up to 80A/80V, 70A/100V, 35A/200V"; "100VDC: 10VDC–95VDC"; the same R-type table) [DS, fetched via search 2026-10-14]. Ordering code G-TWIR70/100EES is listed by distributor e-motionsupply (secondary).
- **Gaps (not invented):** Table 3 has **no peak-current row** for R types (Tables 1–2 give "2 × Ic" for standard models; do not assume it carries over). Sizing must use 49.5 A rms continuous, as `sizing.md` already does ("no peak credit taken"). The R-type mass is in Elmo's spec as 18–22 g; 22.2 g is the EtherCAT version without heatsink (§4.1). The drive is a PCB-mount part; heatsinking at 49.5 A has to be checked by Thermal.
- **Suitability:** 68–84 V pack sits inside 10–95 V. The 90 V regen design point leaves 5 V under absolute max. That is acceptable only with the clamp in §9.3. **A34: proposed CLOSE, no drive swap.**

### 9.2 Vicor DCM3623TA5N53B4T00 mass (closes the R-028 half-credit condition)
Official datasheet DCM3623xA5N53B4yzz_ds.pdf **Rev 1.2, 03/2024**, vicorpower.com: "**Weight 24.0 g [0.85 oz]**" (mechanical table and page-1 summary). Same value as booked, so **0.024 kg can be credited ×1.0**. Efficiency rows come out as "NaN" in the PDF text extraction, so I am not quoting an efficiency (open; read from the plotted curves or ask Vicor).

### 9.3 Regen: 90 V peak vs 95 V drive max, clamp proposal, bus ceiling
**Physics of the problem.** With the pack connected, regen goes into the pack: the modeled mean regen is 245 W at 1.2 m/s (`actuators/results/regen_sim.json`), about 3 A into a 20S5P pack, which is negligible. The bus only climbs toward 95 V when the pack **cannot accept charge**: contactor or BMS charge-FET open (fault, e-stop sequencing), or a full pack (84 V) whose BMS stops charge. The drives have no internal shunt. The Elmo guide (§10.2.3) requires a supply "with sufficient internal capacitance and shunt regulator to handle power flow in both directions", or else the drive over-voltage set by command XP[1] (the guide's 60 V-model example is XP[1]=38). So a bus clamp is mandatory, not optional.

**Proposed thresholds:**
| level | value | basis |
|---|---|---|
| pack max (normal) | 84.0 V | 20S × 4.2 V (R1.3) |
| chopper ON | **88 V** | 4 V above pack max, so it never fires on a healthy pack |
| chopper OFF (hysteresis) | **86 V** | [EST] |
| regen design value | 90 V (R1.3) | clamp must hold the bus ≤ 90 V at the design pulse |
| drive OV trip (XP[1]) | **92 V** | 3 V under the 95 V max; 100 V-model XP[1] range to be confirmed with Elmo [UNVERIFIED] |
| **bus ceiling (absolute)** | **92 V** | nothing on the bus may be rated < 100 V. RP40 (160 V), DCM TA5N53B4 (154 V) and SMDJ90A (90 V standoff) are OK. The SMDJ90A starts conducting near 100 V (breakdown above standoff), so it is not the clamp. |

**Design pulse [EST, to be replaced by the G5 bench]:** peak power 4.5 kW = 2 legs × 2.25 kW peak electrical per limb (R1.3 peak values taken as regen bound). Energy per event ≤ 400 J: kinetic ½·65·1.2² = 47 J, plus a full CoM drop of 0.5 m, 65·9.81·0.5 = 319 J, all assumed regenerated (upper bound).
→ resistor R ≤ 88² / 4500 = **1.72 Ω** (51 A at 88 V); pulse energy 400 J; continuous rating sized for repeated stop events, ≥ 200 W [EST].

**Catalog shunt checked and REJECTED: Roboteq SR5K100V25R** (datasheet Version 1.0, 2 June 2024): presets are only 20/25/30/35/40/60/80/100 V or AUTO (≈ 5 V above the voltage read at power-up). 80 V clips a healthy 84 V pack, 100 V is above the 95 V drive max, and AUTO set at 70 V power-up clips at about 75 V. It also has 1.0 ms sampling, 200 W continuous / 2.5 Ω, and weighs **0.54 kg**. Not suitable.
**Proposal: custom chopper on the power-distribution board (Torso & Power):** hardware comparator (no firmware in the loop), 88/86 V, a ≥ 150 V MOSFET (100 V parts leave too little margin over a 92 V ceiling plus ringing), and a pulse-rated resistor ≤ 1.72 Ω / ≥ 400 J pulse / ≥ 200 W continuous with a thermal cutout, reporting to the safety MCU. Specific MOSFET and resistor part numbers are **not yet cited** (O-E6 stays open). Mass [EST] 0.10–0.15 kg, **not booked** until parts are cited; this is new mass under R-024.
Interlock: the BMS must not open the charge path while drives are enabled, except through SS1 → STO first (§5).

### 9.4 A33: STO wiring itemized per drive branch (proposal to Actuators)
Elmo STO interface [DS, MAN-G-TWI Table 9]: MAIN connector pin 12 STO1, 13 STO_RET, 14 STO2. Opto-isolated, 5 V logic, or 24 V PLC through 1 kΩ series per input (Figs 37/38). **3 conductors per drive**: STO1, STO2 and STO_RET; the return must not be shared with power return. Proposed: SiF 0.25 mm² (5.4 g/m, harness model cable) ×3 per branch, run alongside each EtherCAT branch, daisy-chained along the branch with a tee at each drive. Lengths are the routed EtherCAT branch lengths in `actuators/results/harness.md`.

| branch | n | length m (= ECAT branch) | drives | trunk kg (3 × 5.4 g/m) | tees kg (drives × 0.08 m × 3 × 5.4 g/m) |
|---|---|---|---|---|---|
| leg | 2 | 3.439 | 7 each | 0.111 | 0.018 |
| arm | 2 | 2.913 | 7 each | 0.094 | 0.018 |
| waist (+ neck segment kept, conservative) | 1 | 1.368 | 2 (+ waist IMU none) | 0.022 | 0.003 |
| torso: safety MCU → junction | 1 | 0.25 [EST] | — | 0.004 | — |
| **total** | | **14.3 m** | 30 per this count (harness says 34; Actuators reconcile) | **0.231** | **0.039** |

**SUPERSEDED (A25 closed by Actuators, 3718e93 / 68cb6eb): accepted Actuators D66 = 0.218 kg bare (~0.243 sleeved), 32 Elmo drives (8/leg, 7/arm, 2 waist). My 0.270 double-counted the tee pigtails and wrongly included the 1.368 m neck segment (neck is Dynamixel, no STO).** Original estimate: STO wiring ≈ 0.270 kg (datasheet g/m × routed length; route lengths per harness model). This replaces my R1 rough estimate of +0.14 kg, which assumed 2 conductors. Connector pins: if each drive tee uses a JST-GH 4-pin (harness model part, 0.384 g/pair), add 30–34 × 0.384 g ≈ 0.013 kg. Alternative to cut mass: carry STO on spare pairs if the drive carrier PCB connector allows it; not counted.
Electrical check: STO input current per drive is not in the extract read, so the rail driver current is open. The R1.1 total load is 34 drives in parallel per channel.

## 10. Arms & Hands interface answers (2026-10-14, after P-026)

### 10.1 Wrist roll ±170° and shoulder yaw ±150°: clock-spring, not slip ring
- **Belden MRTA2P26S** datasheet (`actuators/datasheets/belden_mrta2p26s.pdf`): "±90° bending: min. 8 million cycles (bending radius 7.5D)"; "Vertical torsion test ±180°/m: min. 8 million cycles; horizontal torsion test ±90°/m: min. 8 million cycles"; 25.9 kg/km. [DS]
- **±180°/m does not cover a straight torsion run.** ±170° of pure twist at ±180°/m needs ≥ 170/180 = **0.94 m** of free twisting cable per joint, which a wrist doesn't have. (Shoulder yaw ±150° needs 0.83 m.)
- **A flat clock-spring (spiral) loop turns rotation into bending.** The harness model already assumes this (`harness.py` loop = r_wrap × ROM + 50 mm). At the wrist, r_wrap 34 mm / OD 4.2 mm = **8.1 D ≥ 7.5 D** (the datasheet bending condition); at shoulder yaw, 40.5 mm = 9.6 D. The datasheet's 8e6 cycles is for ±90° bending at 7.5D, and a spiral's per-cycle bending amplitude is not the same test. So the **O20a clock-spring cycle test stays mandatory** before claiming T9 life. [EST that the spiral is within rating]
- **Slip ring: not recommended.** The ROM is bounded (no continuous rotation needed), and a slip ring in EtherCAT + 68–84 V power + STO adds contact noise on 100 Mbit/s and a wear part. Decision: **clock-spring at wrist roll and shoulder yaw**; revisit only if Arms wants continuous wrist rotation.

### 10.2 STO 3-wire, arm branch (7 Elmo drives/side)
From Actuators D66 (`actuators/results/harness.md`, row "STO 3-wire daisy chain, arms branch", 0.25 mm² SiF, SILI-E in loops, 7 drive tees × 0.08 m): 2.833 m routed per side, **0.085 kg both arms bare → 0.0425 kg per side** (sleeved ≈ +12 % [EST] per the harness rule). This is already inside Actuators' A25/A33 closure (harness 1.496), so no new mass.

### 10.3 Arm loop lengths re-run with P-026 ROM
Formula and r_wrap from `harness.py` / `v3/cad/out/cables.json` (loop = r_wrap × ROM + 0.05 m).
| joint | r_wrap mm | ROM old → P-026 ° | loop old m | loop new m |
|---|---|---|---|---|
| shoulder pitch | 53 | 240 → 240 | 0.272 | 0.272 |
| shoulder roll | 50.5 | 195 → 195 (P-026 unchanged) | 0.222 | 0.222 |
| shoulder yaw | 40.5 | 300 → 300 | 0.262 | 0.262 |
| elbow | 43 | 140 → **125** | 0.155 | **0.144** |
| wrist roll | 34 | 340 → 340 | 0.252 | 0.252 |
Wrist pitch/yaw ROM (±60/±30) do not appear in any harness crossing: the arm runs end at the wrist roll / hand feed, and the pitch/yaw differential sits distal. **Change: −0.011 m per crossing run at the elbow.** Runs crossing the elbow per side: power 0.5 mm² (9 g/m) + MachFlex (25.9) + STO 3 × 5.4 (16.2) = 51.1 g/m, so **−0.0012 kg both arms**. Negligible; not worth a rollup change.

### 10.4 Hand node (one board per hand)
Function: 11 brushed/BLDC hand drives (T4: ≥ 11 actuated DoF), current sense, one EtherCAT slave, tactile hub. **All parts below are candidates; specs [UNVERIFIED] unless marked [DS].**
| block | candidate | note |
|---|---|---|
| EtherCAT slave | Microchip **LAN9252** (2-port EtherCAT slave controller with SPI host interface) | 2 ports allow pass-through if needed; specs not re-read this round |
| MCU | ST STM32H7-class (SPI to LAN9252, 11 PWM/current loops) | [UNVERIFIED] |
| H-bridges | 6× TI DRV8874-class single H-bridge with integrated current sense (flexors) + 5× smaller (or 3× dual) for the small drives | depends on Arms motor choice; current-sense integrated in the bridge saves shunts |
| tactile bus | **SPI, one chip-select per finger (5) + palm** from the MCU; fingertip ADC/taxel IC per finger | SPI over ≤ 0.3 m tendon-side flex is fine at a few MHz; I²C rejected (capacitance over flex, address limits); CAN FD only if the fingers get their own MCUs |
| logic rail | 24 V → 3.3 V buck on board | |
**Size [EST]:** 70 × 45 mm, 6-layer, double-sided. **Mass [EST]:** PCB + parts 0.020 kg, connectors 0.010 kg, conformal coat/standoffs 0.005 kg → **≈ 0.035 kg per hand**. **Power [EST]:** logic + EtherCAT ≈ 2 W; bridge losses scale with the hand motor current (Arms to supply the duty), so ≈ 2–4 W per hand total at the harness-model hand feed of 0.5 A rms at 24 V (12 W in).
**Location:** in the **forearm, proximal to the wrist pitch/yaw**, next to the hand motors (tendon hand, motors in the forearm per T4/Gen-3 style), so only the tendon bundle and the tactile flex cross the wrist pitch/yaw. EtherCAT + 24 V + STO arrive across wrist roll. **Mass booking:** this falls inside the hands line or arm electronics — Arms & Hands to book; not yet in the rollup.

### 10.5 Wrist 24 V converter
**RECOM RP40-11024SFR** [DS: RP40-FR datasheet, recom-power.com, same family as the head RP40-11012SFR accepted in R-026]: **input 43–160 V**, output **24 V / 1666 mA (40 W)**, efficiency **90 %**, max capacitive load 1300 µF. Bus fit: 68–84 V normal, 90 V regen and 92 V ceiling are all inside the continuous range (R-026 also checked the family's 170 V/1 s surge and UVLO 43 on / 40 off). Mass: R-026 cites the RP40 family at 32 g bare / 43 g with heat-sink (/P-HC). It needs the same note-9 input filter as the head (3 × 68 µF/200 V + 2 × SMDJ90A; Rubycon BXF obsolete, see A28).
**Check needed:** harness-model hand feed peak is 2.0 A at 24 V = 48 W > 40 W rated. Either Arms confirms the hand peak ≤ 1.67 A, or the hand node limits total motor current in firmware (recommended), or a larger part is cited. Placement: forearm, beside the hand node, with the cover/forearm shell as heat path (Thermal).

### 10.6 Updates (2026-10-14, per RL Arms & Hands)
- **Hand-node firmware caps total hand motor current at 1.67 A** (40 W = RP40-11024SFR rating). Consequence (Arms): a six-finger loaded close is ~2–3× slower than 0.74 s; T4 (≤ 1 s close) is flagged to the Arbiter by Arms.
- **Booked in the arms line:** hand node 0.035 [EST] + RP40 0.043 (with heat-sink) per hand.
- **Interface item (harness M3, Actuators):** the wrist-pair drives sit in the **torso shoulder bay**, so their motor phase + encoder leads run shoulder bay → shoulder (3 loops) → elbow → forearm, instead of the 0.06 m local leads in the harness model. Rough size [EST]: per side 2 motors × 3 phases × ~1.7 m × 9 g/m (SiF 0.5) ≈ 0.092 kg + encoder/thermistor 2 × 3 × 1.7 m × 5.4 g/m ≈ 0.055 kg → **≈ 0.15 kg/side, ≈ 0.29 kg both [EST]**. These are PWM phase leads in the arm next to EtherCAT, so they need to be shielded or twisted (EMC); Actuators to route/rate them in harness.py.

## 11. A41 (R-030 / P-030, with Torso & Power): Thor ducted air cooling

**Heat load:** Thor 120 W + brain DCM ≈ 13.9 W (Thermal `R1_BUDGET.md`, η 0.92 [EST]) = 134 W. **Air needed** (energy balance, ρ 1.16 kg/m³, c_p 1007 J/kgK): **24.3 CFM at 10 K air rise, 16.2 CFM at 15 K**.

**P-030's "2× 40 mm blowers, 21 CFM, ~3 W, ~40 g" does not match the catalog parts.** Delta **BFB0412HHA-A** (40×40×10 mm blower) is **3.0 CFM**, 140.5 Pa, 0.96 W, 12.25 g (DigiKey listing of the Delta datasheet) [DS secondary], so 2 × gives 6 CFM, about ¼ of the need. A 40 mm blower cannot do it.

**Proposal: one Sunon PF40281B1-000U-S99** (40 × 40 × 28 mm axial, 12 V, 4-wire FG + PWM), Sunon spec D04092350G (DigiKey-hosted Sunon PDF, F99 variant has identical ratings): **24.9 CFM (min 21.9)** free air, static pressure 1.95 inH₂O (min 1.20), rated **6.12 W** (max 7.05 W), 17 600 rpm, **42 g**, 70 000 h L10 at 40 °C, 56–58.8 dB(A). [DS]
- Budget check: **mass 0.042 kg vs +0.040 booked → +0.002 kg over**; **power 6.12 W rated vs 5 W cap → over**. With PWM speed control the fan laws (flow ∝ rpm, power ∝ rpm³) give ≈ 3.7 W at 85 % speed [EST]. But the duct operating point (flow at the system pressure drop) is not known until J-T2 CFD/bench, and free-air CFM is an upper bound. **Both exceed the A41 budget on datasheet values, so this goes back to the Arbiter.**
- Alternative inside budget: heat pipes to an aluminium chest spreader (Thermal's option). Mass not estimated here.
- Fan supply: 12 V from the 48 V rail through a small buck (part to cite with Torso & Power). The fan's FG (tach) goes to the safety MCU: fan stall leads to Thor power-mode cap, then a controlled stop.

**Duct routing:** intake low on the chest front (V5 vents) → filter mesh → fan → across the Thor cold-plate fin stack (130 × 200 bay) → over the **DCM3623 mounted on the same cold plate with TIM** (downstream of Thor is acceptable: 14 W ChiP; datasheet thermal limits to be read) → exhaust **high, at the upper back/shoulder line, ducted away from the pack**. The pack bay (below the compute bay, z 1333–1477 vs compute 1485–1525 in the v3 layout) stays sealed with a closed partition; the exhaust never crosses it.
**DC-DC placement:** on the Thor cold plate (preferred, one TIM/heat path, no extra bracket) rather than free in the duct.

## 12. Drive over-voltage trip (XP[1]) range, 100 V Gold Twitter (2026-10-14, after R-031)
Source: Elmo **Command Reference for Gold Line Drives, MAN-G-CR Ver. 1.406** (public copy, pk-rus.ru/fileadmin/download/man-g-cr.pdf), sections XP[], WI[], BV. [DS]
- **XP[1]** "Defines the overvoltage threshold in volts. Can only be reduced from the default value (BV)". Default WI[35], values **0 to WI[35]**.
- **WI[35]** "overvoltage maximum threshold", range **0 to < BV**. It is factory-burnt per drive. **WI[36]** reads back the actual threshold (≤ WI[35]). BV is the burnt-in label bus voltage. Actual bus voltage reads via AN[6].
- **So the trip can only be lowered.** Our 92 V setting is allowed only if the factory WI[35] for G-TWIR70/100 and R50/100 is ≥ 92 V. **The numeric WI[35] for 100 V models is not in any public Elmo document found** (the install guide gives 95 V max supply only, and the Twitter power-supply note gives only the 40 V single-supply example, XP[1]=40, with shunt-on 2–3 V below the OV trip, which matches our 88 V on / 92 V trip).
- **Workaround that needs no vendor answer:** read WI[35] on the first bench drive (G5) and record it. If WI[35] < 92 V, set XP[1] = WI[35] and lower the clamp to WI[35] − 3 V (still ≥ 4 V above the 84 V pack only if WI[35] ≥ 91 V; otherwise re-plan the P-045 clamp thresholds).
- Support question for Bryan to send if wanted (draft in the Electronics report): open item O-E9.

## 13. Replies to RL Torso & Power (8a24475 / bd02c23) after R-032 (b018941)
Recorded R-032: Sunon PF40281B1 accepted **0.042 kg / 6.12 W in full in T7** (3.7 W PWM credit only after J-T2 CFD + measured flow); DCM on the Thor cold plate; pack sealed from exhaust; STO inside Actuators' 1.4959 kg harness (the 0.231 booking is void); duct = P-044, clamp = P-045.

### 13.1 P-045 clamp: is 200 W continuous needed? No. Resistor downsized.
**When the clamp fires.** Only when the pack cannot accept charge. Walking is net discharge (703 W at 1.0 m/s, R1.3); regen arrives as pulses with a 245 W mean at 1.2 m/s (`actuators/results/regen_sim.json`) on a pack that is discharging. A connected pack absorbs them. The clamp therefore fires in two cases:
- (a) **Pack disconnected** (fault, e-stop, O-T9 exception). The drives are STO'd in the same sequence (§13.2), so the energy is one bounded event: ≤ 400 J [EST, R1.1 §9.3: kinetic 47 J + full CoM drop 319 J].
- (b) **Pack full at 84 V** and the BMS refuses charge. This is the only case that could make the clamp dissipate the 245 W mean for minutes, which is where 200 W came from. **Remove it by rule, not by resistor:** (i) operational charge limit ≤ 4.15 V/cell (83.0 V) [EST, standard practice, costs ~1–2 % capacity — Torso to quantify against T7]; (ii) the BMS must accept regen pulses at any SOC ≤ the 84 V limit (no charge-FET block for regen; cell OV protection stays). After (i)+(ii), case (b) does not occur in normal use.
**Repetitive need [EST]:** worst plausible = one 400 J event per 10 s (repeated e-stop/fault cycling) → **40 W average**, and normally ≈ 0.

**Smaller resistor: Arcol/Ohmite HS100 1R5 F** (HS range datasheet, Ohmite/Arcol "HS Aluminium Housed Resistors", DigiKey-hosted PDF; Arcol "Heatsink Range Technical Information"): [DS]
| HS100 | value |
|---|---|
| power on std heatsink (995 cm² × 3 mm Al) / free air @25 °C | 100 W / 30 W |
| resistance range | R01–70K (1.5 Ω inside) |
| limiting element voltage | 1900 V |
| mass mounted (approx.) | 115 g (tech-info sheet unit weight 90 g) |
| thermal capacity | **76.7 J/°C** |
| overload (Arcol) | 10× rating for 1 s, 5× for 5 s, 2× for 3 min; max hot-spot 220 °C |
- Pulse: 88²/1.5 = 5.16 kW, 400 J in 78 ms. Adiabatic rise = 400 / 76.7 = **5.2 K per event** (wire-to-body heat spreading inside 78 ms is not guaranteed; that is why the overload curve matters). 5.16 kW = 52× rating at 78 ms is **off the tabulated points** (10× for 1 s = 1 kJ). I could not read the overload-vs-duration curve (it is a graph image) → **O-T8 stays open: read the curve or ask Arcol**. Energy-wise, 400 J < the 1 kJ of the 10×/1 s point.
- Continuous: 40 W [EST] repetitive > 30 W free air, so it **needs a small plate**: bolting to the shoulder bulkhead (7075, exhaust side, per Torso) gives far more than the datasheet's 995 cm² reference [EST]. Fine.
- (HS50 1R5 is 32 g / 19.8 J/°C → 20 K per 400 J event, but only 14 W free air. Kept as fallback if the curve allows.)
**Clamp mass:** HS100 0.115 + 2× IPT059N15N3 / comparator / gate driver / board 0.030 [Torso EST] = **0.145 kg ≤ 0.15 booked (P-045). No Arbiter escalation for the clamp itself.**
**Not clamp mass:** TE LEV100A4ANG contactor (0.20 [EST], mass not read) + HS50 47R pre-charge (0.032 datasheet) + BSC520N15NS3 = **≈ 0.23 kg of pack-disconnect hardware, Torso's line.** It is new mass under R-024 → **goes to the Arbiter as a Torso item.** Electronics supports the contactor on safety grounds (two diverse disconnects, §13.2).

### 13.2 O-T9 interlock exception: ACCEPTED with this sequence
Cell-at-risk faults (cell OV/UV/OT, internal short; external short is handled by the FETs/fuse regardless):
1. t = 0: the BMS raises a **hard-fault line (hardwired, dual-channel)** to the TMS570 **and** sends the CAN FD fault frame.
2. The TMS570 asserts **STO1+STO2 on all 32 drives at once (Cat 0)**; no SS1 wait. Robot falls (covered by T8 pads).
3. The BMS opens the BQ76200 FET pair at the same time (it does not wait for STO confirmation). The contactor opens once current is < 5 A (Torso §13.2).
4. **The clamp must be powered from the drive side of the disconnect** (comparator + gate supply derived from the DC bus, not from the pack side or the 48 V rail), so it keeps working after the pack is gone. It absorbs any back-EMF/regen energy from STO'd but still-moving joints (≤ 400 J [EST]). Bus capacitance (Elmo: ≥ rated current × 20 µF per drive for single-supply use, MAN-G-TWI §10.2.4.2) holds the rest.
5. Latch: no automatic restart; restart requires fault clear, then a manual reset, then pre-charge, then contactor close.
6. Verification on the G5 bench: open the pack at peak regen, measure bus peak ≤ 90 V and drive OV trip (WI[36]) not reached.
Normal (non-cell) faults keep the standard rule: SS1, then STO confirmed, then open.

### 13.3 O-T10: fan operating point (Sunon PF40281B1 P-Q curve)
Datasheet performance curve (Sunon PF40281B1-000U-F99 spec, page 5, read from the graph, ±1 CFM): ~1.95 inH₂O at 0 CFM, ~1.0 at 10–15 CFM, ~0.85 at 18 CFM, ~0 at 25 CFM.
System: Torso's 20 Pa (0.080 inH₂O) at 24.4 CFM, quadratic. Intersection: **≈ 24 CFM at ≈ 0.08 inH₂O (≈ 20 Pa)**, i.e. the fan sits on the steep low-pressure end. ΔT_air = 134 W / (ρ c_p Q) ≈ **10 K**. Using the datasheet minimum free-air flow (21.9 CFM) as a tolerance proxy: ≈ 21.5 CFM → **11 K**. Robustness: even if fins + filter push the drop to 0.5 inH₂O (~125 Pa), the curve still gives ≈ 20 CFM (≈ 12 K). **O-T10: PASS on datasheet curve [graph read]**; J-T2 CFD and a measured flow remain needed for the 3.7 W PWM credit (R-032).

### 13.4 Choke and DCM location
- **DCM3623TA5N53B4T00: on the Thor cold plate** with TIM (R-032), downstream of the fan. Mass 0.024 ×1.0 (R-031), brain line.
- **Vicor 47718-232 choke** (2.26 mH, 8 A, 40 mΩ, 26.5 × 26.0 × 9.5 mm, through-hole [distributor listings of the Vicor datasheet]): **mass not published** (an LCSC "gross weight 1 g" is a shipping field; not credible for a 26 mm toroid). **Book it in the brain line inside the existing `dcm_filter_heatsink` 0.030 [EST]**, on the brain tray next to the DCM input. Owner of the mass: Electronics/brain line (not Torso).

### 13.5 O-E3: drive logic supply. No separate 24 V supply needed
Elmo MAN-G-TWI §10.2.4 / 10.2.4.2 [DS]: for **G-TWIXXX/YYYZZS or H** models, VL accepts **12–95 V** and "a single power supply can be used to power both the main and control within the range of 12 to 95VDC" (VL+ connected internally). Conditions: supply capacitance > drive rated current × 20 µF; VL− to PR on the integration board via a ground plane. Our ordering code **G-TWIR70/100EES** ends in **S**, so it matches this variant [confirm the suffix at order; R50/100 likewise]. **Proposal: single-supply from VP+ (68–84 V, ceiling 92 V < 95 V).** No 24 V VL converter, no mass; logic power < 4 W/drive at 24 V-equivalent [DS §4.5] stays in the drive-overhead line. Consequence: drive logic drops when the pack disconnects. That is acceptable (STO already asserted; absolute encoders, AksIM-2).
Open: the per-drive bus capacitance (70 A × 20 µF = 1400 µF for R70/100 if "rated current" means the 70 A amplitude; 990 µF at 49.5 A rms) has to sit on the drive carrier boards. Mass/volume for Actuators/Torso → **O-E10**.

### 13.6 TRACO TSR 1-48120WI check
Datasheet (tracopower.com/tsr1wi-datasheet) [DS]: **input 17–72 VDC (48 V nominal)**, 12 V out, 93 % at 24 Vin. **It does not cover the 68–84 V pack or the 92 V ceiling.** Torso's design feeds it from the **48 V DCM rail** (§13.2 there), and on that rail it is fine: DCM output 48 V nominal, trim max 52.8 V [DS DCM]. **Rule: the TSR must never be connected to the pack bus**; label its net "48V_BRAIN only". The fan's 0.51 A fits its 1 A.

### 13.7 BMS → safety controller (TMS570) messages (CAN FD, plus hardwired)
| ID / channel | content | rate | consumer |
|---|---|---|---|
| **hardwired dual-channel FAULT_N** | cell-at-risk hard fault (OV/UV/OT/short) | asynchronous, < 1 ms [EST] | TMS570 → immediate STO (§13.2) |
| BMS_STATUS | state (sleep/precharge/ready/fault), FET + contactor state & feedback, pre-charge done, interlock request | 100 Hz | TMS570, Thor |
| BMS_PACK | pack V, current, SOC, SOH, max charge/discharge current limits (for regen acceptance) | 100 Hz | TMS570, Controls power limiter |
| BMS_CELLS_SUMMARY | min/max cell V + index, min/max temp + index | 10 Hz | TMS570, Thor log |
| BMS_WARN | soft warnings (approaching limits, contactor coil, imbalance) | on change + 1 Hz | Thor |
| BMS_HEARTBEAT | rolling counter + CRC | 100 Hz; TMS570 → SS1 if 3 missed [EST] | TMS570 |
| TMS570 → BMS: SAFE_CMD | request open (after STO confirmed), allow close (post-reset), drives-enabled flag | 100 Hz + event | BMS (enforces the §13.2 interlock) |
| clamp → TMS570 (digital) | clamp active, resistor over-temp | event | TMS570 → SS1 / log |
All safety frames: counter + CRC (E2E-style). Rates are [EST].

### 13.8 Changelog: Arbiter R-033 (73d1984)
- Contactor + pre-charge **+0.232 kg approved** (Torso line). A cited contactor mass is needed before G1.
- **HS100 1R5 clamp accepted** at the 0.15 booking (P-045). Fallback if O-T8 fails: 2× HS100 0R75 in series, +0.09 kg.
- 4.15 V/cell charge limit adopted. **Electronics now supports Torso's alternative** (Torso 8c26b7f §15): charge to 4.20 V **plus** BMS accepts regen at any SoC; 1.94 h walk, 49–81 Wh lost under the 4.15 V cap. Molicel to confirm the regen pulse acceptance at 4.20 V. Sent to the Arbiter.
- O-T9 sequence accepted (§13.2).
- G5 tests: **T-025** read WI[35] on the first drive; **T-026** clamp pulse test. **O-T8** (HS100 overload curve) is due before G3.

### 13.9 Additions to §13.7: fault channels and contactor/FET weld detection
- **TI BQ79616 has one hardware fault line.** The dual-channel FAULT_N needs a second, independent channel: **Torso picks the second-channel protector IC and the BMS host MCU.**
- **Electronics owns a drive-side bus voltage sense** for welded-contactor / shorted-FET detection (the LEV100A4ANG has no aux contact, and the BQ76200 cannot detect a shorted FET). It is 2 independent channels, each a resistive divider (84–92 V → < 2 V) into a **TI AMC1311** reinforced isolated amplifier → TMS570 ADC.
  - AMC1311 (ti.com product page / datasheet Rev. C) [DS]: 2 V high-impedance input, fixed gain 1, differential output; reinforced isolation 5000 V rms (UL1577) / 7000 V pk (VDE 0884-17), 1500 V rms working; gain error ±1 % max (AMC1311B ±0.2 %); missing high-side supply indication; −40…+125 °C; SOIC-8 DWV 5.85 × 11.5 mm. TI lists AMC0311D as the newer drop-in.
  - Each channel needs an isolated high-side supply (e.g. a small isolated DC/DC module; part to cite) [EST].
  - Mass [EST]: 2 × (AMC1311 + divider + isolated supply) on the safety board ≈ 0.005 kg, inside the existing rt_safety_mcu 0.040 [EST] allowance.
  - Checks: **before pre-charge** (drive-side bus must be ≈ 0 V with the disconnect open; otherwise weld/short → no close), and **after every open** (bus must decay per the bus-capacitance RC; otherwise latched fault, no restart). Both channels must agree within tolerance [EST ±2 V].
- **Internal cell short detection** (self-discharge/imbalance trend) is a **soft warning** (BMS_WARN), not a hard-fault trigger.
