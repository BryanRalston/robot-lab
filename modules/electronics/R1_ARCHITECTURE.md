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

## 14. A43 (R-035): 80 W hand burst on top of 40 W continuous
**Hand board location: moving from forearm to upper arm or shoulder bay (A42), TBD.**
1. **RP40-11024SFR cannot do it.** RP40-FR datasheet [DS]: Over Load Protection **150 % typ., hiccup mode**; SCP continuous, auto recovery; max capacitive load 1300 µF (24 V part); 32 g bare / 43 g with heat-sink. 150 % = 60 W is a *typical* trip, not a guaranteed rating. **80 W puts it into hiccup** (output collapses and restarts), so the hand loses power mid-grip. **Max guaranteed burst: 40 W (its rating). Do not plan on 60 W.**
2. **24 V-side storage (supercap/bulk) — not recommended.** The burst needs 40 J extra (40 W × 1 s). Allowing 24 → 18 V droop: C = 2E/(V1²−V2²) = 80/252 = **0.32 F at ≥ 24 V**. Electrolytics: not credible (hundreds of grams). Supercap: a ≥ 9-cell series stack with balancing **plus** a current-limited charger/ideal-diode stage, because the RP40 allows only 1300 µF of direct capacitive load and would hiccup charging 0.32 F. Mass [EST] 0.05–0.10 kg per hand with charger. No part cited, more parts, cycle-life and temperature limits. Rejected unless mass forces it.
3. **Recommended: RECOM RP100H-11024SRW** (RP100H-RW datasheet REV 4/2020) [DS]: input **43–160 V**, **24 V / 4.2 A (101 W)**, 90 %, max capacitive load 1750 µF, OLP 150 % typ. hiccup (110 Vin), SCP continuous auto-recovery, trim −20/+10 %, EN50155; half brick **61.0 × 57.9 × 12.7 mm, 105 g** (24.13 mm / **157 g with heat-sink**). This gives **80 W continuous, so an 80 W burst of unlimited duration within thermal limits** (baseplate-cooled). The 68–84 V bus, 90 V regen and 92 V ceiling are inside 43–160 V.
   - Mass delta per hand vs RP40/P-HC 0.043: **+0.062 (bare, plate-mounted to the structure) or +0.114 (with heat-sink)** → **+0.124 / +0.228 kg both** → Arms books it via the Arbiter (new mass under R-024).
   - Size favours the **shoulder bay** location (A42) over the forearm.
   - **Input filter:** the RP40 note-9 filter does not transfer. The RP100H datasheet's own EMC/transient filter recommendation must be read and cited before purchase (open, O-E11). Keep the 90 V-standoff TVS logic: standoff ≥ 84 V, clamp < 160 V.
4. **Wrist harness at 3.3 A (80 W / 24 V):** the current model hand feed is SiF 0.5 mm² (`harness.md`). If the converter sits in the shoulder bay with the hand board, the 24 V run is shoulder → hand board (location TBD). If the motors stay in the forearm, the board-to-motor leads become the long run instead (Arms to define). For a 24 V pair of ~1.9 m [EST route+loops] in 0.5 mm²: R = 2 × 1.72e-8 × 1.9 / 0.5e-6 = 0.13 Ω → **0.43 V drop (1.8 %) at 3.3 A**; I²R = 1.4 W over 3.8 m of conductor. Heating at 1.67 A continuous is ¼ of that. SiF 0.5 mm² is adequate [ampacity from the Lapp table not re-read: EST]. Going to 0.75 mm² costs +3 g/m per conductor and is only needed if the run is > 3 m.

## 15. R-036 (3b50c3c): 4.20 V/cell, BMS regen acceptance a hard requirement (G5 T-027). Can the P-045 clamp absorb the top-of-charge window anyway?
**Method.** Actuators' regen model traces (`actuators/results/regen_sim_trace_walk_1p0/1p2.npz`; `regen_core.py`: PB = Σ signed joint electrical power + p_other, i.e. the **net DC-bus power with full sharing between joints and the compute/sensor loads**). If the BMS refuses charge, the clamp only sees the **negative part of PB**; every regenerating joint first feeds the other joints and the ~140 W of compute/sensors on the same bus.
| gait (steady window) | net bus mean | clamp mean (neg. part) | clamp peak | pulses | max / mean pulse energy | duty |
|---|---|---|---|---|---|---|
| walk 1.0 m/s (5.2 s) | +609 W | **4.2 W** | 221 W | 2.1 /s | 2.6 J / 2.0 J | 3.4 % |
| walk 1.2 m/s (5.0 s) | +710 W | **3.6 W** | 202 W | 2.2 /s | 2.1 J / 1.6 J | 2.4 % |
**5-min top-of-charge window (Torso):** 4.2 W × 300 s = **1.26 kJ** total, in ~640 pulses of ≤ 2.6 J.
- Bus capacitance alone (Elmo single-supply rule ≥ rated I × 20 µF ≈ 1 mF per drive, ×32 ≈ 32 mF [EST]) stores ½C(88² − 84²) = **11 J** between pack-max and clamp-ON. **Each ≤ 2.6 J pulse is absorbed by the caps; the clamp fires rarely**, and the energy it eventually burns averages ≤ 4.2 W.
| | HS100 1R5 F (booked) | 2× HS100 0R75 series (pre-approved fallback, +0.09) |
|---|---|---|
| R / ON power at 88 V | 1.5 Ω / 5.16 kW | 1.5 Ω / 5.16 kW (2.58 kW each) |
| continuous: free air / std heatsink [DS] | 30 W / 100 W | 60 W / 200 W |
| thermal capacity [DS] | 76.7 J/°C | 153.4 J/°C |
| 5-min window, adiabatic rise (1.26 kJ) | **16 K** | **8 K** |
| steady state at 4.2 W | ≪ free-air rating (14 % of 30 W) | ≪ |
| per-event pulse (2.6 J gait / 400 J fault) | 0.03 K / 5.2 K | 0.02 K / 2.6 K (each sees half) |
**Result: the booked HS100 1R5 absorbs the full 5-min top-of-charge window with large margin, even with the BMS refusing charge.** The 2× 0R75 fallback is not needed for this case; it stays only as the O-T8 fallback for the 400 J / 78 ms fault pulse.
**Caveats:** the traces are nominal walking only. Stairs-down, sit-down, braking from speed and arm lowering are not in the regen model. Bound for those [EST]: descending 18 cm steps at 0.5 step/s gives 65 × 9.81 × 0.18 × 0.5 = **57 W gross**, below the ~140 W compute/sensor load on the same bus, so net bus power stays positive in steady descent. Short transients (sit-down ≤ 319 J CoM drop) are inside the 400 J design event. **O-T8 (pulse curve) is still needed for the 400 J fault event, before G3.** T-027 (BMS acceptance) stays the primary measure; the clamp is the backstop and does not need to stop the robot during the top-of-charge window.

## 16. Alignment with Torso R1.4 (1dd529b) and Arbiter R-038 (2026-10-14)

### 16.1 §13.7 / §13.9 update: BMS fault channels and bus-sense frame
- **FAULT_N channel 1:** TI BQ79616 fault line (via BQ79600-Q1 bridge path; Torso).
- **FAULT_N channel 2:** **2× TI BQ77216** (10S + 10S secondary protectors), open-drain outputs wire-ORed, **opto level-shifted** to the TMS570. Independent of the BQ79616 and the host (Torso R1.4).
- **BMS host:** NXP **S32K344** with TI **BQ79600-Q1** communication bridge to the BQ79616 stack, **CAN FD to the TMS570** (frames per §13.7).
- **New frame: TMS570 → BMS host, BUS_SENSE_STATUS** (drive-side bus sense, §13.9, 2× AMC1311):
| field | bits | content |
|---|---|---|
| v_bus_ch1 | 12 | drive-side bus voltage ch1, 0.05 V/LSB |
| v_bus_ch2 | 12 | ch2, same scaling |
| agree | 1 | ch1/ch2 within ±2 V [EST] |
| precheck_result | 2 | 0 = not run, 1 = PASS (bus ≈ 0 V with disconnect open), 2 = FAIL (weld/short suspected), 3 = sensor fault |
| postopen_result | 2 | same coding: bus decayed per RC after open? |
| weld_short_latched | 1 | latched fault, blocks close until manual reset |
| amc_hs_supply_ok | 2 | AMC1311 missing-high-side-supply flags ch1/ch2 |
| counter | 4 | rolling |
| crc | 16 | E2E CRC |
Rate: 100 Hz, plus an event frame on any result change. The host must not close the FETs/contactor unless precheck_result = PASS with agree = 1 in the last frame received ≤ 30 ms ago [EST].

### 16.2 §14 update: R-038, 2× RP40-11024SFR per hand (supersedes the RP100H recommendation)
- **Decision (Arbiter R-038):** 2× RECOM RP40-11024SFR/P-HC per hand, **+0.086 kg total** vs the booked single RP40, in the **shoulder bay with the hand board (A42)**.
- **Parallel/share check (RP40-FR datasheet REV 8/2020):** the datasheet lists only **ON/OFF CTRL** (positive/negative logic) and **output voltage trimming** (24 V: −10 %/+20 %) as control functions. It gives **no current-share or parallel-operation pin or note**. The single-output parts are not specified for paralleling. **So: two independent rails, never paralleled.** (The statement to Arms & Hands that the RP40 has no current-share pin is correct.)
- **Architecture:** rail A and rail B, each ≤ 40 W, **firmware cap 1.67 A per rail** on the hand board. **Flexors split 3/3 across rails** and the small drives split as Arms defines, so one rail failure leaves a partial grip. Each rail has its own bulk capacitance **≤ 1300 µF** (RP40-11024SFR max capacitive load, datasheet) including the motor-driver input caps. Burst capability = 2 × 40 W = 80 W total, only if the load is split; no single rail may exceed 40 W.
- **O-E11 input filter, sized from the RP40-FR datasheet** (note 9 + "EMC filtering EN55032 Class A" component list for RP40-110xx): per converter **TVS1 + TVS2 = 2× SMDJ90A in series**; **C1 = 3× 68 µF/200 V** electrolytic in parallel (datasheet names Rubycon BXF, which is obsolete: equivalent required, see A28); **C2 = 33 µF/250 V** Al (Chemi-con KXJ); **C3, C4 = 1 µF/250 V** 1812 MLCC; **L1 = 22 µH, 1.5 A** SMD inductor (TDK CD series); **C5–C7 = 1000 pF Y1**. Input current per converter at 40 W / 90 % / 68 V = 0.65 A < 1.5 A L1 rating.
  - **Use one datasheet filter per converter** (validated configuration, keeps rails independent). A shared filter would need L1 ≥ 1.3 A × margin and is not datasheet-validated.
  - Mass [EST]: ~0.015 kg per filter (3× radial caps + inductor + MLCCs + PCB share) → ~0.03 kg per hand. **Not in the R-038 +0.086**, so Arms to confirm whether that number already includes filters; if not, it is new mass.

### 16.3 §14 A43 closure (Arbiter accepted electrically; Thermal PASS with conditions, d4cca06)
- Thermal: RP40 case ≈ 71 °C at 35 °C ambient, 2 × 40 W continuous.
- **Mounting conditions:** each RP40 strapped to the Al shoulder bulkhead or a 6061 bracket (≥ 3 mm thick, ≥ 40 cm²) through a ≤ 1 mm, ≥ 3 W/mK gap pad. The hand board sits on the same plate. Shoulder bay vented ≥ 25 cm² in and ≥ 25 cm² out, out of the Thor exhaust path. **Clip heatsinks dropped (−0.044 kg)**: order the bare /P parts, not /P-HC.
- **Bracket temperature sensor: TI TMP117** (ti.com product page, datasheet Rev. D) [DS]: digital I²C/SMBus, ±0.2 °C max (−40…100 °C), ±0.25 °C (−55…125 °C), operating −55…150 °C, 1.7/1.8–5.5 V supply, 3.5 µA at 1 Hz, programmable ALERT, 4 addresses, WSON-6 2 × 2 mm. Mounted on a small flex/PCB tab screwed to the bracket next to the converters, wired to the hand board I²C. Mass negligible (< 1 g) [EST].
- **Firmware:** the hand board reads the TMP117 at ≥ 1 Hz. At **≥ 90 °C bracket** it derates both rail current caps linearly (1.67 A → 0 A at 100 °C [EST profile]). At **≥ 100 °C** it disables both RP40s via ON/OFF CTRL and reports to Thor/TMS570. The TMP117 ALERT pin is wired to CTRL logic as a hardware backup at 100 °C.
- **Mass (Arbiter):** +0.086 kg + up to 0.06 kg O-E11 filters (both hands), final in **R-040 (pending)**.

### 16.4 Hand supply rails, RP40 outline, filter mass check, hand-motor leads (after Arms 440c7a8)
Recorded: rail A = F1–F3 + S1, S2 + hand logic; rail B = F4–F6 + S3–S5. Sim `hand_close_r4.json`: loaded close ≤ 0.68 s, each rail ≤ 40.5 W / 1.69 A peak, hold 11–18 W/rail. **Keep the 1.67 A firmware cap**: 1.69 A is 1 % over and only lengthens the close marginally. Filters booked +0.060 kg (Arms).

**(1) RP40-11024SFR/P (bare) outline** [DS RP40-FR REV 8/2020, "Dimensions and physical characteristics" + dimension drawing]: **50.8 × 25.4 × 10.2 mm**, 32 g, case copper alloy (CuZn33), FR4 base, silicone potting (UL94 V-0); 2" × 1" through-hole, pins Ø1.0 ±0.1 mm on a 2.54 mm grid (pins 1 +Vin, 2 −Vin, 3 CTRL, 4 +Vout, 5 −Vout, 6 Trim), pin standoff 5.6 mm per drawing; max case temperature +105 °C. **Mounting:** PCB-soldered pins. There are no mounting holes or threaded inserts on the bare part, so the Thermal strap (case → gap pad → bracket) is a clamp/strap over the case top. 1.6 kVDC I/P–O/P–case isolation means the case can touch the grounded bracket.

**(2) O-E11 filter mass, itemized (per RP40-110xx Class A list):**
| item | part | size | mass | basis |
|---|---|---|---|---|
| C1 3× 68 µF/200 V | **Panasonic EEU-EE2D680** (A28 choice, head BOM) | 12.5 × 25 mm radial | 3 × 4.7 = **14.1 g** | catalog/distributor (head/BOM.md) |
| TVS 2× SMDJ90A | Littelfuse SMDJ90A | DO-214AB | 0.4 g | R-027 catalog |
| C2 33 µF/250 V | Chemi-con KXJ series | ~12.5 × 25 mm [EST, same can class] | ~4.7 g | [EST by similarity] |
| C3, C4 2× 1 µF/250 V | 1812 MLCC | 4.5 × 3.2 mm | ~0.1 g | [EST] |
| L1 22 µH 1.5 A | TDK CD-series SMD inductor (per datasheet) | ~12 × 12 mm [EST] | ~2 g | [EST] |
| C5–C7 3× 1000 pF Y1 | disc ceramic Y1 | ~8 mm disc | ~1.5 g | [EST] |
| PCB | FR4 1.6 mm, ~45 × 35 mm | 15.8 cm² | ~4.7 g | calc (1.85 g/cm³) [EST area] |
| **total per filter** | | | **≈ 27.5 g** | 51 % catalog |
**Corrected: ≈ 0.028 kg per filter, not 0.015.** Four filters (2 per hand × 2 hands) = **0.110 kg vs 0.060 booked, so +0.050 kg short** (to Arms/Arbiter, R-040). Options: one filter per hand feeding both RP40s (L1 then carries 2 × 0.65 A = 1.3 A < 1.5 A rating, but not the datasheet-validated configuration; EMC test required) → 0.055 kg both hands, inside 0.060. **Side finding:** the head filter booked in R-027 (3 caps 0.0105 [EST]) is also light vs 3 × 4.7 g = 14.1 g catalog → Robot Lab (head) should re-book (+0.004).

**(3) Hand-motor leads, shoulder bay → forearm (proposal for Actuators' M3)**
- **Conductors:** 11 brushed maxon motors per hand (6× DCX 22 S, 5× DCX 16 S; `arms/A42_A43_R4.md`). Each is driven by a full H-bridge (bidirectional), so **2 conductors per motor, no shared return: 22 conductors per side.**
- **Current:** per motor ≤ rail cap 1.67 A peak (DCX 22 S I_nom 0.869 A; DCX 16 S I_nom 0.144 A, Arms' list). Rail totals ≤ 1.69 A peak, 11–18 W hold.
- **Gauge: SiF 0.25 mm² (5.4 g/m) for all 22**, SILI-E 0.25 (4.5 g/m) inside the clock-spring loops per the harness rule. Check over 1.7 m: R = 1.72e-8 × 1.7 / 0.25e-6 = 0.117 Ω per conductor → 0.39 V loop drop (1.6 % of 24 V) at 1.67 A; 0.33 W per conductor (0.19 W/m) at peak, much less at hold. Ampacity from the Lapp table not re-read [EST adequate]. No smaller size exists in the harness model's SiF table.
- **Route/length:** shoulder bay → shoulder pitch/roll/yaw loops → upper arm → elbow loop → forearm motor tiers (not across the wrist; motors sit proximal to the roll). **1.7 m per conductor** (Arms D72 route incl. loops; elbow loop 0.144 m per §10.3).
- **Mass:** 22 × 1.7 m × 5.4 g/m = **0.202 kg/side, 0.404 kg both** (bare; sleeving +12 % [EST] → 0.452). Using SILI-E in the loop portions (~0.9 m of loops at 4.5 g/m) saves ~0.02 kg/side.
- **Bundle:** 22 × ~1.9 mm OD [SiF 0.25 datasheet OD] ≈ 10–11 mm bundle; the shoulder clock-spring drums must take it (r_wrap/OD fine for single cores). EMC: twist each motor pair (PWM leads next to EtherCAT).
- **Encoders:** if maxon ENX encoders are fitted, each adds 4–6 conductors (+50 to +100 % mass). **Recommend no motor encoders**: tendon position from motor-current/back-EMF estimation plus joint sensing at the fingers (Arms decision).

### 16.5 Hand board in the forearm; thermal derate, 125 °C parts, hardware OT cutoff (R-046/R-047, Thermal A43C 64b6af8, R-051)
**Layout (Arbiter R-046/R-047):** hand board in the **forearm**; 2× RP40-11024SFR + **one shared O-E11 filter** in the shoulder bay (R-041 conditions stand). Round 2-board stack **ø60 × 12–13 mm [EST]**.

**Thermal A43C (board-only, 64b6af8):** with the shell derate ladder, shell ≤ 90 °C (walking 59.8 °C, still air 79.7 °C), board 68/88 °C, H-bridge Tj ≤ 80/100 °C. Without the derate, still air **fails** (board 135 °C, Tj 147 °C). **Derate ladder adopted (mandatory per R-051, verified by G5 T-029):** shell sensor (TMP117, §16.3 part) on the hand board pressed against the shell. Thresholds **55 / 70 / 80 / 88 °C → flexor current 0.84 / 0.70 / 0.50 / 0.35 / 0 A** (step ≥ 88 °C → 0), 5 K hysteresis on the way down.

**125 °C-rated parts (board reaches 88 °C in still air; 125 °C grade gives ≥ 37 K margin):**
| function | part | temp grade | source |
|---|---|---|---|
| EtherCAT slave | **Infineon XMC4300-F100K256-AA** (XMC4300F100K256AAXQMA1): Cortex-M4 144 MHz with integrated EtherCAT node, 256 kB flash, 128 kB RAM, 2× CAN, 2× 12-bit ADC, LQFP-100 | **−40…125 °C** (Infineon product page; Infineon NPI 2016 "125 °C ambient") | [DS]. One distributor (Rutronik) lists T(A)max 85 °C in its parameter table while its text says 125 °C; the Infineon page governs, confirm in the datasheet at order. |
| (rejected) LAN9252 | Microchip LAN9252TV/ML | **−40…105 °C max**, and only in QFN with an external 1.2 V regulator + 2.5 V magnetics; LAN9252I = −40…85 | Microchip product page / datasheet |
| MCU (if kept separate) | **STM32H725VGT3 / STM32H735VGT3** ("3" suffix) | **−40…125 °C ambient, 140 °C junction** | ST eStore (STM32H725VGT3: −40…125, LQFP-100); ST STM32H72x/73x training deck |
| Note | With XMC4300 as the EtherCAT node and controller, the STM32H7 can be **dropped** (XMC4300 has CCU timers for PWM and 2 ADCs; 11 current loops at hand rates are within an M4 at 144 MHz [EST]). Saves one IC + area on the ø60 stack. | | |
| H-bridges ×11 | **TI DRV8874-Q1** (4.5–37 V, 6 A peak, integrated current sense IPROPI, HTSSOP) | **AEC-Q100 grade 1: TA −40…125 °C, TJ −40…150 °C** | TI datasheet Rev. B |
| EtherCAT PHYs ×2 (XMC4300 needs external PHYs) | 125 °C-rated 100BASE-TX PHY, candidate **TI DP83822** (automotive/HF variant) | **[UNVERIFIED: check that the variant is rated 125 °C]** | open, O-E12 |
| Passives | MLCC **X7R (−55…125 °C)** or X8R/C0G; no Y5V/X5R; electrolytics excluded from the hand board (MLCC bulk only, within the 1300 µF RP40 limit on the supply side) | X7R = 125 °C class | EIA class II code definition |

**Hardware over-temperature cutoff (R-051), independent of the MCU:**
- Sensor: **Murata NCP15WF104F03RC** 100 kΩ NTC, 0402 (Murata NCP series; temp range **[UNVERIFIED in the extract read: confirm ≥ 125 °C]**), placed between the H-bridge rows on the board.
- Comparator: **TI LM2903B-Q1** dual comparator (TI datasheet Rev. M: **AEC-Q100 grade 1, −40…125 °C**, 2–36 V supply, ±4 mV max offset over temperature, open-collector, 1 µs response) [DS].
- Circuit: NTC + precision divider sets the trip at **≈ 110 °C board**. Comparator A has positive-feedback **hysteresis ≈ 10 K** (re-enables at ≈ 100 °C). Its open-collector output pulls down the **nSLEEP/EN of all 11 DRV8874-Q1** through a wired-AND line, so the MCU cannot override it. Comparator B is a latch option (SR via the second channel; reset only by power cycle or MCU-independent reset line) if the Arbiter prefers latching. Default: **latching** (safer; the derate ladder should keep the board well below 110 °C, so a trip means something is wrong).
- Status: the trip line is also read by the MCU and reported over EtherCAT.
- Mass/area: < 1 g, ~20 mm² [EST].

**RP40 derating above 60 °C (RP40-FR datasheet REV 8/2020, page PD-6, "Derating Graph", chamber, natural convection 0.1 m/s):** **graph only, no table.** For **RP40-2415SFR (bare)**: 100 % output to **60 °C**, linear to **0 % at 105 °C** (≈ 2.2 %/K; e.g. ~78 % at 70 °C, ~56 % at 80 °C, ~33 % at 90 °C, read from the graph). For **-HC**: 100 % to 65 °C, 0 % at 105 °C. Environmental table: operating −40…+60 °C without derating, to +105 °C with derating; max case +105 °C; thermal impedance 10.8 K/W bare / 10.3 K/W with heat-sink (natural convection 0.1 m/s). **Datasheet note 8: the graphs are valid only for the part numbers shown (RP40-2415SFR); the RP40-11024SFR curve is not published, so RECOM techsupport must confirm it.** For our design: the shoulder-bay ambient must stay ≤ 60 °C for full 40 W per converter, or the per-rail cap must derate along this curve. Thermal's strapped case of ~71 °C (35 °C ambient) is below the 105 °C case limit.

### 16.6 R-051 ruling applied: latching HW OT cutoff, reset by rail power cycle, MCU fault flag, NTC rating, RECOM curve

**Ruling (R-051):** The HW OT cutoff is LATCHING ONLY. The hysteresis option in §16.5 is removed. The only reset is a power cycle of hand rails A and B (RP40-11024SFR/P). The XMC4300 commands that power cycle, and only after the MCU NTC reading is below 70 °C. The MCU must be able to read a fault flag.

**NTC rating:** The Murata NCP15WF104F03RC is rated −40 to +125 °C (Murata product page "Operating Temperature Range −40℃ to 125℃"; NCP15 spec sheet, pim.murata.com SPEC_NCP15, row NCP15WF104F03RC "-40 to +125"). That meets the ≥125 °C requirement, so the part is retained. Note: above 125 °C Murata requires voltage/temperature derating. Our divider bias is ≤3.3 V across 100k + 100k, well below the 5 V max, and the trip is at ~110 °C.

**Latch implementation (LM2903B-Q1, both channels; no added ICs):**
- **Channel A (trip + latch):**
  - Inputs: the NTC/100k divider and the 110 °C reference.
  - Positive feedback: a 1 MΩ resistor from the open-collector output to the reference node, with a BAS16 (or 1N4148WS, 150 °C) in series. The diode is oriented so feedback acts only once the output is LOW.
  - Effect: after a trip, the release threshold moves to a divider voltage the NTC cannot reach at or above −40 °C. The output stays LOW until the 3V3_HAND logic rail (derived from rail A) collapses.
  - Power-on reset: a 100 nF capacitor on the reference node sets the comparator's power-up state. It starts un-tripped and only latches on a genuine over-temperature.
- **Output OT_N:** open-collector, with a 10 kΩ pull-up to 3V3_HAND.
  - **Driver enables:** OT_N gates all 11 DRV8874-Q1 nSLEEP/EN lines through a series 100 Ω on each enable, plus a BAT54 (125 °C+ AEC-Q101) per line from the enable to OT_N. A LOW OT_N clamps every enable LOW regardless of the MCU.
  - **MCU fault flag:** channel B is a non-inverting buffer of OT_N (threshold 1.65 V). Its open-collector output OT_FLAG_N has a 10 kΩ pull-up to the XMC4300 VDDP and goes to a GPIO with interrupt. The MCU can therefore read the latch state without loading the latch node.
- **Reset path:**
  1. The XMC4300 reads the NTC through its ADC (separate sense NTC, same part).
  2. When it reads below 70 °C, it drives HAND_RAIL_EN low for ≥200 ms.
  3. That pulls the RP40 A/B CTRL/remote-off pins through the existing shoulder-bay control line.
  4. Then it re-enables the rails.
  - The MCU sits on the XMC4300 logic supply, which is not cut by the hand rails, so it survives the cycle.
- **Firmware:** the MCU cannot clear the latch any other way. There is no reset pin by design.
- **Parts and mass:** all parts are rated ≥125 °C (LM2903B-Q1 −40 to 125 °C; 0402 thick-film resistors at 155 °C; X7R capacitors at 125 °C; BAS16/BAT54 at 150 °C). Added parts versus §16.5: 1 diode, 11 BAT54, ~14 resistors, 1 capacitor. That is <0.001 kg, well inside the R-043 0.02 kg freeze.
- **Verification (T-029 bench):**
  - Heat-gun trip at 110 ±3 °C.
  - Confirm no release when cooling to −40 °C equivalent (divider substitution).
  - Confirm release only on a rail cycle.
  - Confirm OT_FLAG_N is read correctly.

**Ladder:** The 55/70/80/88 °C → 0.84/0.70/0.50/0.35/0 A ladder stays mandatory as written in §16.5. Tuning it is contingent on the Arms grip check (grip force at each derate step). It is not tuned until Arms reports.

**RECOM curve:** The §16.5 derating (full power to 60 °C, zero at 105 °C) comes from the RP40-2415SFR graph only. Confirming the 11024SFR curve needs a vendor answer. A draft question for Bryan to send to RECOM is held off-repo. Nobody contacts RECOM from the agents. This stays open as O-E13 until RECOM answers.

### 16.7 Forearm hand-board fit (Arms 2026-10-14, R-055), MCU sizing, PHYs, XMC current table, harness re-book, shoulder-bay air sensor

**Inputs.** Arms: annulus board, OD ≤ Ø62 (bore Ø66 × 13.2), centre hole ≥ Ø21 (tendon sheaths), stack ≤ 12.5 mm, axial connectors only; RP40s + filter stay in the shoulder bay (R-047), only the 24 V feed crosses the elbow; 6× maxon ENX22 EASY INT on the DCX22 flexors (local leads), none on the DCX16s; the 1.7 m bay→forearm motor harness is void; size for 11 current + 6 position loops. R-055 accepted these fit conditions (provisional until CAD). Forearm length still open (R-055: D73 compaction first, ≤ 40 mm lengthen fallback). Nothing below depends on forearm length, only on the Ø66 × 13.2 slot. Thermal ceaf729: board 3.5 W typ / 4.0 W hot; asks for the XMC current table; recommends a bay-air sensor.

**(1) MCU check: can the XMC4300 alone run 11 current + 6 position loops?** Figures are from the XMC4300 Data Sheet V1.0 2016-02 (Table 3, Table 6, §3.2.8 Table 33, Table 25).
| resource | need | XMC4300-F100 has | verdict |
|---|---|---|---|
| CPU | 11 PI current loops at 10 kHz (~150 cycles each incl. ADC result handling) = 16.5 Mcyc/s; 6 position loops at 1 kHz (~500 cyc) = 3 Mcyc/s; ladder/OT/EtherCAT application ~10 Mcyc/s [EST cycle counts] | 144 MHz M4F | ≈ 21 % load, **OK** |
| ADC | 11 IPROPI + sense NTC + rail A/B 24 V monitor (2) + bay-air NTC (item 6) = **15** | 2 VADC × 8 = **16** ch; 12-bit post-calibrated 459 ns | fits with 1 spare. 6 conversions/group/period ≈ 2.8 µs, **OK** |
| PWM | DRV8874-Q1 in PH/EN mode: 1 PWM (EN) + 1 GPIO (PH) per bridge = **11 PWM** | CCU8 1×4 slices (2 compare ch each → 8 PWM) + CCU4 2×4 slices (8) = 16 timer outputs | OK, 5 CCU4 slices left |
| encoders | **6 quadrature** counters (ENX22 A/B/I) | **no POSIF** in XMC4300; the 5 remaining CCU4 slices can only do count + direction | **FAIL: 1 slice short, and no x4 hardware decode** |

**Decision: change the MCU to Infineon XMC4800-F100K2048 AA** (XMC4700/XMC4800 Data Sheet V1.2 2023-04; Infineon product page). It is the same family and the same LQFP-100 package, rated −40…125 °C ("K" grade), with the same EtherCAT node. It has 2 POSIF, 4×4 CCU4 + 2×4 CCU8 slices (24 timers), 4 VADC with 24 channels on LQFP-100 per DS Table 6 (the Infineon product page says "18 input lines"; take 18 as the planning figure, which still covers 15), and 2 MB flash / 352 kB RAM. Encoder allocation: 2 flexors on POSIF0/1 (x4 hardware quadrature); 4 flexors on CCU4 slices using external count + external up/down (A edges, B level; x2 if both A edges counted) [check CCU4 function in RM at layout]. The XMC4800-F100 Table 33 supply figures are identical to the XMC4300 (below). Mass and area are unchanged (same package). **STM32H725/735 is dropped** (one IC fewer; the XMC4800 covers loops + EtherCAT). XMC4300→XMC4800 pin-compatibility on LQFP-100 **[UNVERIFIED]**; the layout is not started, so this does not matter yet. The Arbiter accepted the XMC4300 under R-051; this swap needs a note to the Arbiter (temperature grade unchanged, no mass delta).

**(2) XMC4300 / XMC4800 supply current (DS §3.2.8 Table 33; VDDP = 3.3 V, TA = 25 °C unless stated; "not subject to production test")**
| condition (fCPU / fPERIPH / fCCU MHz) | symbol | typ | max | at 3.3 V |
|---|---|---|---|---|
| Active, peripherals enabled, 144/144/144 | IDDPA | 135 mA | – | 0.446 W |
| Active, peripherals enabled, 144/72/72 | IDDPA | 125 mA | – | 0.41 W |
| Active, peripherals enabled, 72/72/144 | IDDPA | 97 mA | – | 0.32 W |
| Active, code from RAM, Flash asleep, 144/144/144 | IDDPA | 108 mA | – | 0.36 W |
| Active, peripherals disabled, 144/144/144 | IDDPA | 86 mA | – | 0.28 W |
| Sleep, peripherals enabled, 144/144/144 | IDDPS | 127 mA | – | 0.42 W |
| **Worst-case active** (VDDP 3.6 V, TJ 150 °C, benchmark from Flash, all CCUs running) | IDDPA | – | **250 mA** | **0.90 W** |
| Power dissipation limit (VDDP 3.6 V, TJ 150 °C) | PDISS | – | 1.4 W | – |
| RθJA LQFP-100 (4-layer JEDEC, pad soldered) | | 22.5 K/W | | |
**Effect on Thermal ceaf729:** Thermal booked 0.33 W typ / 0.6 W hot for the MCU. The datasheet gives **0.45 W typ / 0.90 W worst case**, so the board total rises to **≈ 3.6 W typ / ≈ 4.3 W hot**. That is over the 4.0 W case in `a43c_board.json`, so Thermal must re-check (as an upper bound, PDISS max 1.4 W would give 4.8 W). PHY figure confirmed: DP83822 3.3 V AVD < 220 mW each (TI) → 0.44 W for two, consistent with Thermal's 0.4–0.45 W. EtherCAT ESC current is inside the "peripherals enabled" figure.

**(3) PHYs (closes O-E12): TI DP83822HF** (TI product page: operating temperature **−40…125 °C**, EtherCAT listed, MII/RMII/RGMII, VQFN-32 RHB 5 × 5 mm, single 3.3 V supply < 220 mW). 2 per hand (EtherCAT IN/OUT, MII to the ESC). **Fallback:** if the hand is the end of its EtherCAT line, port 1 is unused, so fit **one** PHY (saves ~70 mm², 0.22 W).

**(4) Annulus area budget.** Usable ring per face: r 11.5…30 mm (1 mm clearance from Ø21 and Ø62) = π(30² − 11.5²) = **2412 mm²/face**. Two boards × top face = **4824 mm²**; the facing (inner) sides give a further 4824 mm² for tall/passive parts and are held as margin.
| block | parts (package source) | courtyard mm² |
|---|---|---|
| MCU | XMC4800 LQFP-100 PG-LQFP-100-25: 14 × 14 body, 16 × 16 over leads, 17 × 17 courtyard (Infineon DS) | 289 |
| PHYs | 2× DP83822HF VQFN-32 5 × 5 (6 × 6 courtyard) | 72 |
| clocks | 12 MHz MCU + 25 MHz PHY/ESC crystal, 3.2 × 2.5 | 28 |
| H-bridges | 11× DRV8874-Q1 HTSSOP-16 PWP: 5.0 × 4.4 body, 6.4 over leads (TI DS), 38.5 mm² courtyard + VM 0.1 µF/10 µF, IPROPI R, ~16 mm² each | 600 |
| encoder I/F | 6× (ESD array SOT-23-6 + RC filter on A/B/I + supply) [EST 25 mm² each; ENX22 EASY INT is single-ended TTL, so no line receivers; if the line-driver variant is chosen, add 2× quad receivers, ~90 mm²] | 150 |
| latch | LM2903B-Q1 VSSOP-8 + diode + 14 R + 11 BAT54 SOD-323 (§16.6) | 95 |
| sensors | 2× NCP15 NTC 0402 + TMP117 WSON 2 × 2 | 15 |
| decoupling | MCU 10× 0402 + 2× 0805; PHYs 2× ~20 mm² | 65 |
| PHY coupling | capacitive coupling + ESD per port (no magnetics on an internal link) [EST] | 60 |
| power | 24 V→3.3 V buck (LMR36006-Q1 class) + 4×4 inductor + caps, input TVS, 24 V bulk MLCC 4× 1210 per rail | 175 |
| axial connectors | 66 pins (22 motor, 30 encoder 6 × 5, 4 power 24 V A/B + returns, 8 EtherCAT, 2 spare) at 1.0 mm pitch vertical, ~5 mm²/pin + housings [EST] | 365 |
| board-to-board | 2 × 40-pin 0.5 mm stacker halves | 150 |
| mounting | 3× M2 holes, Ø5 keep-out | 60 |
| **sum** | | **2124** |
| **with 1.5× routing/spacing** | | **3185 of 4824 mm² (66 %)** |

**Geometry checks:**
- MCU 17 × 17 courtyard with its inner edge at r = 11.5: outer corner at √(28.5² + 8.5²) = **29.74 mm < 30.0**. It fits, with 0.26 mm to spare. This is the tightest single item, and the MCU must sit with one flat edge tangent to the centre hole.
- DRV8874-Q1 rows: 11 × 6.4 mm tangentially at r ≈ 24 mm uses 70 of 151 mm circumference.
- Height: 2 × 0.8 mm boards + 5.0 mm stacker gap (inner-face parts ≤ 4.5 mm, e.g. the 4 × 4 × 2 inductor) + outer faces ≤ 2.5 mm each (connector bodies, LQFP 1.6 mm) = **12.4 mm ≤ 12.5** (slot 13.2). The mating plugs sit axially outside the stack, as allowed by "axial connectors".
- Thermal: the DRV8874 pads need via arrays to inner copper. Board heat spreading is per Thermal A43C.

**Fit verdict: FITS** (area 66 %, MCU corner 0.26 mm inside, height 12.4/12.5 mm), provisional until CAD.

**Fallbacks, in order, if CAD fails:**
1. Single PHY (end-of-line hand), saving ~110 mm² with coupling.
2. Fine-pitch 0.5 mm board-to-board header + 0.8 mm connectors (~−150 mm²).
3. Populate the inner faces with passives, gaining up to +4824 mm².
4. Put the 5 DCX16 S bridges (I_nom 0.144 A) on one DRV8912-Q1-class multi-half-bridge. This saves ~170 mm² but loses analog current sense on the DCX16s, so it needs Arms/Controls agreement.
5. If the height fails: 0.6 mm boards (−0.4 mm).

**(5) Harness re-book (supersedes §16.4(3)).** The motors and board are both in the forearm, so the 22 motor conductors × 1.7 m are void.
| item | conductors × length | gauge / mass per m | per side |
|---|---|---|---|
| motor leads, board→motor (local) | 22 × 0.15 m [EST, Arms layout] | SiF 0.25, 5.4 g/m | 17.8 g |
| 24 V feed bay→forearm, rails A and B never paralleled (R-038), so +A, −A, +B, −B | 4 × 1.6 m [EST, bay→forearm board, incl. loops] | SiF 0.25, 5.4 g/m (0.37 V drop at 1.67 A) | 34.6 g |
| HAND_RAIL_EN A/B to the RP40 CTRL pins (§16.6 reset) | 2 × 1.6 m | 0.14 mm², ~2.5 g/m [EST] | 8.0 g |
| encoder leads (local) | 6 × 5 × 0.1 m | AWG30, ~1.5 g/m [EST] | 4.5 g |
| **total** | | | **≈ 65 g/side → 0.130 kg both** |

**Change: 0.404 → 0.130 kg bare (−0.274 kg); sleeved (+12 %) 0.452 → 0.146 kg (−0.306 kg).** EtherCAT to the hand is unchanged and not in this line. Arms' "only the 24 V pair crosses" needs to say **4 power conductors + 2 enable lines**, because the two rails are separate by R-038. A shared return would save 1 conductor (−8.6 g/side) but couples the rails; not proposed.

**(6) Shoulder-bay air sensor (Thermal ceaf729): ADOPTED.** One NCP15WF104F03RC 0402 NTC (−40…125 °C, §16.6) on the RP40 bracket PCB in bay free air, read differentially on one XMC4800 ADC channel over 1 conductor + the rail-A return (0.14 mm² × 1.6 m ≈ 4 g + 2 resistors). Firmware: per-rail cap 1.67 A to 60 °C bay air, then derated along the RECOM curve (provisionally the RP40-2415SFR bare curve, 2.2 %/K to 0 at 105 °C; O-E13 open). Open-sensor or short-sensor reads as hot, so the cap goes to 0. It replaces the 90/100 °C bracket-NTC rule. **Mass ≈ 0.005 kg/side, 0.010 kg both ≤ 0.02 kg (R-043)**, booked inside the harness credit above.

**Open:**
- CAD fit (Arms).
- XMC4300→XMC4800 swap note to the Arbiter.
- Thermal re-check at 4.3 W hot.
- XMC4800 pin-compatibility and CCU4 count/direction confirmation in the reference manual.
- Encoder resolution choice (Arms).
- O-E13 RECOM.
- O-E12 **closed** by the DP83822HF.

### 16.8 R-061 conditions: encoder decoding, B-config lead mass vs the R-047 +0.077, power-tree and RP40 CTRL checks (after Arms/Thermal 7f2fa7d)

**Item 2: O-E12 is CLOSED** (R-061, DP83822HF).

**Item 5: Thermal 7f2fa7d (A43C at 4.3 W PASS) clears the 4.3 W A43 reopen condition.** Board 69/77 °C, MCU Tj 78/86 °C, H-bridge Tj 81/91 °C, shoulder bay 48–53 °C in still air (≤ 60 °C, so no RP40 derate). Closing A43 is the Arbiter's call.

**ENX22 EASY INT output** (maxon Product Information ENX EASY INT, DocID 4174182-04, 2023-04, §1.2–1.6 and §5):
- Output is a **line driver, differential EIA RS-422** (ChA, A/, B, B/, I, I/), not TTL.
- Vcc is 5 V ±10 %, 22 mA typ.
- 1…1024 cpt, factory-set; pulse frequency 4 MHz; minimum state 62.5 ns.
- 10-pin connector, so **8 conductors per encoder**.
- **Operating temperature is −40…+100 °C** (connectors 105 °C). The maxon shop page says 125 °C; the Product Information governs.
- This corrects §16.7, which assumed TTL, 5 wires, no receivers and no 5 V rail.

**Item 1: decoding at maximum speed.**
- **Basis:** DCX 22 S 24 V no-load speed is **12 400 rpm** (D68 datasheet as cited in Arms R6_ROUND.md), i.e. 206.7 rev/s. The maxon max permissible speed was not re-read.
- At 1024 cpt: A = 211.6 kHz, quadrature states at 846.5 kHz, nominal state 1.18 µs. The minimum state is 0.8 LSB (maxon Table 2), i.e. **0.945 µs**.
- **2 flexors on POSIF0/1 (incremental, x4 in hardware):**
  - The input path is a 2-clock synchroniser plus a low-pass filter of 3/5/7 fCCU clocks [XMC4800 RM, not re-read: UNVERIFIED].
  - Worst case at 144 MHz is (2 + 7)/144 MHz = 62.5 ns per state. **Margin: 0.945 µs / 62.5 ns = 15×.**
  - Needs 2 RS-422 quad receivers, AEC-Q100 grade 1 (AM26C32-Q1 class, **grade to confirm**), TSSOP-16, ~40 mm² each.
- **Count/direction on a CCU slice for the other 4: REJECTED.**
  - Counting on A edges with B level as direction gives x1 at best.
  - Dither on A while B is static is counted in one direction on every edge, so the count drifts at standstill.
- **ERU edge-interrupt decoding: REJECTED at 1024 cpt.**
  - 4 × 846.5 k = 3.39 M interrupts/s leaves 42 CPU cycles per edge, i.e. 100 % load.
  - It is only feasible at ≤ 64 cpt.
- **Fix adopted: ENX 22 EASY INT Absolute (BiSS-C) on the 4 non-POSIF flexors.**
  - Same housing and integration. Read by 4 XMC4800 USIC channels in SSC mode, with BiSS framing and CRC in software. The remaining 2 USICs serve the TMP117 (I²C) and a spare.
  - 12-bit single-turn. Frame is 3 + 12 + 2 + 6 CRC = 23 bits at 5 MHz (certified maximum) = 4.6 µs. Adding the timeout (1.5/fclk + 3.75 µs) gives **8.65 µs per read**.
  - Read at the 10 kHz current-loop rate: 7.44° per sample at 12 400 rpm. The unwrap limit is < 180°, so the **margin is 24×** (2.4× at 1 kHz). The CRC catches bad frames.
  - CPU cost ≈ 8 Mcyc/s (+5.6 %, total ≈ 27 %).
  - Interface is 4 conductors: CLK in (VIH ≥ 2 V, so a 3.3 V drive works), DATA out (5 V CMOS, so a divider to 3.3 V is needed).
  - Encoder mass unchanged (5 g). Board area: 4 × ~10 mm² instead of 4 × 25 mm², plus the receivers (+30), so **net −30 mm²**. The §16.7 FITS verdict stands. Connector pins: 32 (was 30).
  - **New 5 V encoder rail:** 132 mA, fed from the always-on (AO) feed.
- **Fallback:** 4 encoders at ≤ 64 cpt on ERU interrupts.

**Item 4b: RP40-11024SFR/P CTRL** (RECOM RP40-FR datasheet: ON/OFF CTRL, note 5, pin table):
- Pin 3 CTRL is **referenced to −Vin**, the bus side.
- The "/P" suffix is positive logic: **ON = open or 3.0 V < VCTRL < 12 V; OFF = short or 0 V < VCTRL < 1.2 V**. CTRL draws 3 mA when off.
- **The §16.6 assumption (MCU drives CTRL directly) was wrong as written.** The MCU sits on the isolated 24 V side.
- **Fix (R-073, supersedes the tied-grounds design):** RP40 isolation is kept. One **Toshiba TLP383** phototransistor optocoupler per RP40 (2 per hand, 4 total). The output transistor (V_CEO 80 V) runs from CTRL (pin 3) to −Vin. The parts sit on the RP40 bracket PCB in the shoulder bay, next to the pins. The LED is driven from the hand board's AO-powered EN line (one conductor + return).
  - LED on = CTRL pulled low = OFF, held for ≥ 200 ms. LED off = CTRL open = ON.
  - A broken EN wire fails ON. The R-051 hardware latch still disables all 11 bridges independently.

**Item 4a: power tree. The assumption was FALSE.**
- Sources: `arms/A42_A43_R4.md` says "board logic 4 W on rail A"; §16.4 says "rail A = … + hand logic"; §16.6 says 3V3_HAND is derived from rail A. The MCU would lose power during its own reset cycle.
- **Fix: separate always-on 12 V feed (AO).**
  - Converter: TI LM5164-Q1 class 100 V buck (6–100 V, 1 A, AEC-Q100) in the shoulder bay, fed from the shared O-E11 filter output.
  - The 92 V bus ceiling against the 100 V rating is tight, so it needs an input TVS/RC. Fallback is the RECOM RP03-11024SRAW (36–160 V, isolated 3 W, DIP-24, 14 g).
  - Wiring: 1 conductor to the forearm, return shared with the rail return.
  - AO feeds the XMC4800, PHYs, TMP117 and the 5 V encoder buck.
  - The latch and 3V3_HAND stay on rail A, so the R-051 reset still works.
  - Load ≈ 3.0 W hot (0.25 A at 12 V).
  - **Mass ≈ 0.002 kg/side [EST], +0.004 kg both sides** (RP03 fallback: +0.028).

**Item 3: B-config leads vs the R-047 booking.**
- The +0.077 kg booked comes from Actuators `harness.py` line 119: a 24 V pair, SiF 0.5 mm² at 9 g/m (Lapp), 1.9 m/side, 2 conductors = 34.2 g/side, × 2 sides × 1.12 sleeving.
- The same 1.9 m route is used below. The NTC is booked separately (+0.010, R-061).

| line (per side) | conductors | gauge, g/m | g/side |
|---|---|---|---|
| +24 V A, +24 V B (never paralleled) | 2 × 1.9 m | SiF 0.25, 5.4 (cited) | 20.5 |
| common return (≤ 3.4 A) | 1 × 1.9 m | SiF 0.5, 9 (cited) | 17.1 |
| AO 12 V + EN + bay-air NTC | 3 × 1.9 m | AWG28 PTFE ~1.0 [EST] | 5.7 |
| local motor leads (Arms: ~0.15 m) | 12 × 0.15 at AWG26 ~1.6 [EST] + 10 × 0.15 at AWG30 ~0.7 [EST] | | 3.9 |
| encoder leads | maxon integral 200 mm cable | in encoder mass | 0 |
| AO buck | | | 2.0 |
| **per side** | | | **49.2** |

| case | both sides (12 % sleeving on the 1.9 m runs) | booked | delta |
|---|---|---|---|
| **B-config, best case** | (43.3 × 1.12 + 3.9 + 2.0) × 2 = **0.109 kg** | 0.077 + 0.010 NTC = **0.087** | **+0.022 OVER** |
| B-config, cited gauges only | 0.193 kg | 0.087 | +0.106 over |

- **Verdict: the B-config leads do NOT fit.** The best case is 0.022 kg over, which is above the R-043 0.02 kg limit, so this goes back to the Arbiter.
- **Cause:** R-047 booked one pair, but B needs 2 rails + return + AO + EN + NTC.
- **Options:**
  - (a) A cited thin multi-core cable for the signal lines.
  - (b) Move the bay-air derate into the bay as an analog clamp, which saves 1 conductor (−2.1 g/side).
  - (c) Offsets.
- Arms CAD may shorten the 1.9 m route.

**Risk only:** if the forearm length forces the board into the upper arm (Arms R6 option a), about 54 conductors cross the elbow (22 motor + 32 encoder), ≈ 0.12 kg [Arms EST]. This is not adopted.

**Open:**
- RS-422 receiver grade.
- XMC4800 RM filter figures.
- LM5164-Q1 transient margin.
- ENX 100 °C rating vs the motor-end temperature (Thermal/Arms).
- Item 3 overage (Arbiter).

## 17. R-062: knee Elmo drives off the finned knee housing (mount location and harness delta)

**Count.** The knee is 2 × TBM2G-07613D + 2 × RV12x5 (`sizing.json` sel.knee, nmot 2), and `harness.py` counts 2 knee drives per leg. So this moves **2 drives per leg (4 per robot)**, not 1 per leg. All figures below are per leg for 2 drives.

### 17.1 Location: thigh shell just above the knee housing (recommended)
- **Heat:** off the housing, so the knee fins lose the drive load (R-062 condition 2: margin 3.7 K on the housing vs 18 K off it). Mount the drives on a small 6061 plate (~1.5 mm) standing off the femur tube/thigh shell with G10 or PEEK spacers, so there is no metal path back to the finned housing. Each G-TWI has a flat base heatsink face and 2 mounting holes; the plate is the heat spreader. At 8.8 A rms per drive, the dissipation is small and spread over the plate area.
- **Phase run:** shortest option, about 0.20 m extra per motor [EST: L48 places the housing ≥150 mm from the knee-cap keep-out, plus routing ×1.15; Legs to confirm with CAD]. No joint is crossed, because the motors are thigh-side, so there is no extra clock-spring loop and no extra EMI loop area across the hip.
- **EtherCAT, bus, STO:** these run as a line down the thigh (hip_pitch → knee → ankle; `harness.py`). The drives just tee in a little higher on the same trunk, keeping the same 0.08 m pigtails.
- **Hip/pelvis bay (rejected):** about 0.42 m × 1.15 + a hip-pitch clock-spring loop ≈ 0.6–0.7 m extra per conductor. That is 6 phase conductors at up to ~42 A peak, crossing the hip_pitch drum, for about 2.5–3× the mass (≈ 0.15–0.17 kg/leg). It is the worst option for EMI and loss, and it competes with the hip drives already in the bay.

### 17.2 Phase gauge
- **Current:** I_rms 8.8 A per motor (sizing.json, carry rms ≈ 9.5 A from 77.5 N·m). Peak ≈ 345 N·m / (59.69 × 0.8455 × 2) / Kt 0.081 ≈ **42 A** at full knee capability (gait peak 178 N·m ≈ 22 A). The G-TWI R70/100 is 49.5 A.
- **Gauge rule:** this uses the `harness.py` rule (ΔT ≤ 30 K at rms, bundle factor 2, h 10 W/m²K) at 9.5 A:
  - 0.5 mm² → 94 K (fail)
  - 1.0 mm² → 40 K (fail)
  - **1.5 mm² (≈16 AWG) → 24 K (pass)**
- **Mass:** Lapp ÖLFLEX HEAT 180 SiF 1.5 mm² is **20 g/m** (datasheet, including the silicone jacket). That is 13.4 g/m of copper (1.5 mm² × 8.96 g/cm³) plus about 6.6 g/m of jacket. The 42 A peak only lasts seconds; ΔV over 0.26 m is negligible.
- **Pigtails:** the existing 0.06 m local phase pigtails are booked at 0.5 mm², which fails the same rule. This section re-books them at 1.5 mm².

### 17.3 Signal leads
- **Encoders:** RLS AksIM-2 (Actuators SPEC; 2 per joint: motor + output). BiSS-C/SSI RS-422 = **6 conductors** (MA±, SLO±, +5 V, GND). Per leg that is 3 leads (2 motor encoders, 1 knee output encoder), each lengthened about 0.20 m.
- **Encoder cable:** uses the D72 precedent, Belden MRTA2P26S 2×2×26 AWG shielded (25.9 g/m) + 2 × SiF 0.25 mm² (5.4 g/m) = 36.7 g/m.
- **PT1000:** 2 × SiF 0.25 mm² per motor.

### 17.4 Harness delta per leg (L_extra = 0.20 m [EST])
| conductor | gauge | count × extra m | g/m | kg |
|---|---|---|---|---|
| motor phase (2 motors × 3) | SiF 1.5 mm² | 6 × 0.20 = 1.20 m | 20 | 0.0240 |
| encoder (3 leads × 6 cond) | MRTA2P26S + 2× SiF 0.25 | 3 × 0.20 = 0.60 m | 36.7 | 0.0220 |
| PT1000 (2 motors × 2) | SiF 0.25 mm² | 4 × 0.20 = 0.80 m | 5.4 | 0.0043 |
| pigtail re-gauge 0.5 → 1.5 mm² | | 6 × 0.06 = 0.36 m | +11 | 0.0040 |
| bus / STO / EtherCAT | | tee moves up the same trunk | | 0.0000 |
| subtotal | | | | 0.0543 |
| sleeving 12 % (harness.py rule) | | | | 0.0065 |
| drive plate + isolating standoffs [EST] | | | | 0.010 |
| **net per leg** | | | | **≈ +0.071** |

- **Robot total:** ≈ **+0.142 kg** (wire only ≈ +0.122 kg).
- **No saving on bus, STO or EtherCAT:** these are line runs that continue down to the ankle drives, so moving the knee tee upward does not shorten them.
- **Mass freeze:** this exceeds the R-043 freeze threshold (0.02 kg). It needs an Arbiter booking against R-062 (an R-062 consequence, not discretionary).
- **Open:** Legs CAD for the actual drive-to-motor distance. Each 0.05 m changes the result by about ±0.013 kg/leg.

## 18. R-069 mass-down pass: electronics and harness (2026-10-14)

**Rules applied.**
- Baseline = what `actuators/harness.py` / `harness.json` (total 1.984 kg at this commit) or `arbiter/a3_size.py` actually books.
- Replacement wire mass = Lapp ÖLFLEX HEAT 180 SiF datasheet g/m (runs) and Stäubli SILI-E (clock-spring loops), the same tables already in `harness.py`.
- Ratings use `harness.py`'s own rule: ΔT ≤ 30 K at the booked I_rms (bundle ×2, h 10 W/m²K), and ΔV at the booked I_pk within the per-run budget.
- Savings include the 12 % sleeving that `harness.py` applies to wire mass.
- STO wiring and the R-038 separate RP40 rails are untouched.

### 18.1 Ranked candidates
| # | item (harness.py row) | baseline | new | ΔT / ΔV at booked I | cited saving kg | risk |
|---|---|---|---|---|---|---|
| 1 | Drive bus tees, 40 × XT30U pairs (`CON`, 3.6 g/pair AMOV listing) | 0.144 | soldered + heat-shrunk splices into a harness section per drive, ~0.5 g each [EST] | n/a | **0.124 (conditional)** | HIGH: no field swap of a drive without re-splicing; the replacement mass is an estimate. Arbiter/Actuators decision. |
| 2 | Leg drive bus pigtails, 16 × 2 × 0.08 m (`P` row, floor a_min 1.0) | SiF 1.0 mm², 0.0384 | SiF 0.5 mm² | 16.7 K / 0.10 % (4 A rms, 12 A pk) | 0.0172 | Low. XT30U takes 0.5 mm². |
| 3 | BMS → fuse → contactor → bus bar, 2 × 0.30 m (floor 4.0) | SiF 4.0, 0.030 | SiF 2.5 | 24.7 K / 0.40 % (13.8 A rms, 66 A pk) | 0.0121 | MEDIUM: pack-side fault current before the fuse; fuse I²t must be checked against 2.5 mm² (Torso). |
| 4 | Arm drive pigtails, 14 × 2 × 0.08 m | SiF 0.5, 0.0202 | SiF 0.25 | 5.2 K / 0.08 % | 0.0090 | Low |
| 5 | Arm elbow → wrist, 2 × 0.466 m (incl. elbow loop) | SiF 0.5 / SILI-E 0.5, 0.0165 | 0.25 / SILI-E 0.25 | 1.1 K / 0.25 % (budget 0.6) | 0.0079 | Low-med: thinner core in the elbow clock-spring (cycle test O20a covers it) |
| 6 | Neck/head bus, 0.501 m (floor 0.75) | 0.012 | SiF 0.25 / SILI-E 0.25 | 2.3 K / 0.41 % | 0.0079 | Low-med: neck loop flex, same as #5 |
| 7 | Waist drives feed, 0.31 m (floor 1.0) | 0.0097 | 0.25 | 5.2 K / 0.38 % (1.5 A rms, 6 A pk [booked EST]) | 0.0075 | MEDIUM: the 6 A waist peak is itself an estimate; take 0.5 mm² (saving ≈ 0.004) if Actuators can't confirm it |
| 8 | Waist/neck pigtails, 4 × 2 × 0.08 m | 0.5, 0.0058 | 0.25 | 2.3 K / 0.06 % | 0.0026 | Low |
| | **Wire subtotal (#2–#8)** | | | | **0.0642** | |
| | **With #1** | | | | **≈ 0.188** | |


### 18.1a R-071 follow-up: mixed plan for the 40 XT30U drive tees (replaces candidate #1)

**Serviceability.**
- No doc marks any Elmo drive as non-replaceable, so all **32 Elmo drive tees are serviceable**. They keep a pluggable connector.
- `harness.py` books XT30U × (32 + 8). The extra 8 are not identified anywhere in the repo (they are not drives, and the 2 neck Dynamixels are not Elmo). They are the only candidates for splices, if Actuators confirms they are bus trunk junctions.

**Rating basis.** The connector carries the drive's **bus** current, not the motor phase current. The 49.5 A figure is G-TWI phase current. The booked bus tee figures (`harness.py` `P` pigtail rows) are 4 A rms / 12 A pk for the legs (worst case), 1.5 / 5 A for the arms, and 1 / 4 A for the waist and neck.

| branch type | count | baseline (XT30U pair 3.6 g, AMOV listing in harness.py) | new part | cited mass | rating vs need | saving kg |
|---|---|---|---|---|---|---|
| Elmo drive tees (serviceable) | 32 | 0.1152 | Amass MR30 pair (MR30-M + MR30-FB, 2 of 3 pins used, or both poles paralleled on 2+1) | 2 × 1.41 g = 2.82 g (TME MR30-M "gross weight 1.41 g", taken for both halves; conservative vs 1.0–1.2 g retail listings) | 15 A rated / 30 A momentary, 1000 cycles, −20…120 °C (Amass MR30 spec V1.2) ≥ 4 A rms / 12 A pk | **0.0250** |
| Unidentified tees (possible trunk junctions) | 8 | 0.0288 | TE PIDG 320559 butt splice × 2 poles (22–16 AWG; M7928/5 crimp, apply to A-620 Class 3) | 2 × 1.48 g = 2.96 g (TE product page) | fits ≤ 1.42 mm² only; 2.5 mm² trunks need 320562, mass not cited | 0.0051 **not credited** (8 not identified; a butt splice is in-line only, and a 3-way tee needs a different part) |

**Result.**
- **+0.025 kg cited** (MR30 at the drive tees).
- The splices barely apply: at most 0.005 kg, and not credited.
- R-069 electronics total: 0.064 (wire, of which 0.012 battery link pending Torso I²t) + 0.025 = **0.089 kg**. Firm: 0.077 kg.
- Former candidate #1 (−0.124) is withdrawn.

**Risks.**
- MR30 is a hobby-grade connector, the same class as the booked XT30U. It has no positive latch, so it needs a strain-relief clip or tie-down at each drive (mass inside the 12 % sleeving allowance).
- Mating cycles drop from XT30U's to 1000. That is adequate for service swaps.


### 18.2a Arbiter R-073 (recorded 2026-10-14)
1. **BiSS-C accepted (R-061 condition met in principle).**
   - Firmware item **FW-E14**: XMC4800 acts as BiSS-C master for the 4 ENX22 Absolute encoders, read at 10 kHz (§16.8 4c: 8.65 µs/read).
   - Bench item added to **T-029**: run at 12 400 rpm. Pass = 0 CRC errors over the full test duration, and position is correct (checked against the reference encoder/unwrap).
2. **Hand leads booked +0.022 kg.**
3. **RP40 CTRL isolation kept.**
   - Optocoupler adopted: **Toshiba TLP383** (SO6L-4, Ta −55…125 °C, 5000 Vrms, V_CEO 80 V, CTR ≥ 50 %; DS TLP383_E 2022-05-17, **weight 0.128 g typ**).
   - Placement: one per RP40, on the RP40 bracket PCB in the shoulder bay, output across CTRL/−Vin (§16.8 4b, tied-grounds design removed).
   - Mass: 4 × 0.128 g + 4 × 0402 resistor ≈ **0.0006 kg robot**, within the +0.001 booked.
   - **Open (to Arbiter):** the §16.8 AO feed (LM5164-Q1 non-isolated buck, return shared with the rail return) references the hand logic to −Vin anyway. For the isolation to be real, AO must use the isolated fallback **RP03-11024SRAW** (14 g each per DS). The mass delta against the LM5164 is not yet booked or cited, so it is not claimed here.
4. **MR30 accepted, −0.025 kg.**
   - Every connector gets a strain-relief clip that positively retains it.
   - G5 vibration and retention tests are added.
   - No cited clip mass was found (Amass publishes no MR30 retention clip). Fit inside the 12 % sleeving allowance is **unverified** until a part is chosen and its mass cited.
5. **ENX22 100 °C limit:** stays open with Thermal and Arms.

**Mass change this section:** +0.022 (hand leads, booked by the Arbiter) + 0.0006 (optos, inside the +0.001 booked). No other change.


### 18.2b Arbiter R-075 (recorded 2026-10-14)
- **Functional isolation not sufficient.** The TLP383 ×4 functional isolation with a shared return was accepted only if the pack bus is SELV (≤ 60 V DC). It is not: 4.20 V/cell (R-036), the P-045 clamp turns on at 88 V, and the ceiling is 92 V. **The condition fails.**
- **Always-on hand-logic supply:** RECOM RP03-RAW, isolated, ×2 (one per arm, in the shoulder bay). It **replaces the LM5164-Q1** in §16.8 item 4a. The AO return is no longer shared with −Vin. The TLP383s stay on CTRL (§16.8 4b, §18.2a).
  - **Datasheet:** RECOM RP03-RAW (recom-power.com/pdf/Powerline_DC-DC/RP03-RAW.pdf).
    - Input 36–160 VDC continuous, 4:1, 200 VDC for 1 s.
    - 3 kVAC/1 min reinforced isolation.
    - −40…+105 °C with derating; > 90 °C without derating.
    - DIP-24, 31.8 × 20.3 × 10.6 mm, **14 g typ.**
  - **Input check:** 43–92 V lies inside 36–160 V, with a 68 V margin to 160 V and a 108 V margin to the 200 V surge rating. **PASS.** No alternative needed.
  - **Variant note (to Arbiter):** R-075 names the 11024SRAW (24 V / 125 mA). §16.8 sized AO as a **12 V, ≈ 3.0 W hot** rail. The 12 V variant of the same series is **RP03-11012SRAW** (12 V / 250 mA, 84.5 %, same package and 14 g). Recommend that variant. Load 3.0 W against the 3 W rating gives **≈ 0 % margin**. Thermal and Arms must confirm the 3.0 W hot figure, or hand logic load must be trimmed. Otherwise the next size up is needed (not cited here).
  - **Mass:** 2 × 0.014 = 0.028 kg, against the 0.004 kg [EST] for the LM5164-Q1 buck. **Net +0.024 kg robot.**
- **T-029 addition:** no BiSS-C CRC errors and no POSIF count errors under common-mode stress. Test with the isolated AO ground floating against −Vin, with drives PWM-switching at full bus (43–92 V).
- **G1 gate item:** the MR30 retention clip must be a cited catalogue part or a drawn part with a computed mass before G1.


### 18.2c Arbiter R-076: bus insulation audit (recorded 2026-10-14)
**Ruling.**
- RP03 ×2 booked +0.024 kg.
- Binding: reinforced or double isolation bus (43–92 V) ↔ every SELV rail; IP2X on bus parts; creepage/clearance for 92 V; every bus connector cited ≥ 100 V DC before G1.
- The forearm board stays in the forearm (Arms lengthens the forearm).

**Connector and part audit (bus side), 100 V DC criterion**
| part on bus | cited DC rating | source | 100 V |
|---|---|---|---|
| Amass MR30 (32 drive tees) | 500 V DC | Amass MR30 spec V1.2 (MR30-M / MR30-FB "额定电压 DC 500V") | PASS |
| Amass XT30U (8 remaining) | 500 V DC | Amass XT30U-M/F spec V1.2 | PASS |
| Amass AS150U (pack main) | DC 500 V (withstand, UL1977); creepage 4 mm | Amass AS150U spec | PASS |
| Amass XT60 (4) | not yet cited | – | OPEN: cite Amass XT60 spec before G1 |
| TE LEV100A4ANG contactor | not cited in repo | – | OPEN: cite TE datasheet before G1 |
| Elmo G-TWI R70/100 power pins (PCB-soldered, no connector) | 95 V max bus (drive rating) | Elmo G-TWI product page / MAN-G-TWI | PASS for 92 V ceiling (part, not connector) |
| Vicor DCM3623TA5N53B4T00 input | 43–154 V | Vicor DS Rev 1.2 | PASS |
| RP40-11024SFR/P input | 43–160 V | RECOM RP40-FR DS | PASS |
| RP03-11012/11024SRAW input | 36–160 V (200 V 1 s) | RECOM RP03-RAW DS | PASS |
| TRACO TSR 1-48120WI | 17–72 V in | TRACO DS | **not on bus**: fed from the DCM 48 V output (§11). Confirmed; it must never be moved to the bus. |

No failing connector was found among the cited parts, so **no mass change**. XT60 and the contactor are open (rating not yet cited), not failed.

**Bus ↔ SELV boundaries**
| boundary | part | cited isolation | class | flag |
|---|---|---|---|---|
| bus → 48 V brain rail | Vicor DCM3623TA5N53B4T00 | 3000 VDC IN-OUT (DS) | cTÜVus cert (DCM3623 series): **"output separated from input by Basic Insulation"**; the DCM Railway TÜV cert says "Reinforced Safeguard" | **FLAG**: confirm which cert lists TA5N53B4 (Bryan/Vicor). If basic only, the 48 V rail is not SELV by isolation, so the TSR fan supply and everything downstream need a second barrier. |
| bus → hand 24 V rails | RECOM RP40-11024SFR/P ×4 | 3 kVDC/1 min I/P–O/P (110 Vin models), **1.6 kVDC I/P–O/P–case** | **not stated** (UL/IEC 60950-1 cert, class not given) | **FLAG**: class unknown. The case is at 1.6 kV and clamps to the grounded bracket. RECOM must state the class; vendor question goes via Bryan. |
| bus → AO hand logic | RECOM RP03-RAW ×2 | 3 kVAC/1 min | **reinforced** (DS) | OK |
| RP40 CTRL (bus side) ↔ AO logic | Toshiba TLP383 ×4 | 5000 Vrms | **reinforced only with option D4** (VDE EN 60747-5-5); the plain part is UL1577 only | Order **TLP383(D4…)**. Same 0.128 g, no mass change. |
| drive bus sense → TMS570 | TI AMC1311DWV | 7000 VPK, VIOWM 1500 Vrms, creepage/clearance 8.5 mm | **reinforced** (VDE 0884-17) | OK |
| STO (TMS570, SELV) → Elmo STO inputs | Elmo G-TWI internal STO opto | not cited | unknown | **FLAG**: cite MAN-G-TWI. Elmo drive logic is bus-powered, so the STO, EtherCAT and encoder ports on every drive are referenced to the bus unless Elmo states reinforced isolation. This may be the largest open item: 32 drives. |
| EtherCAT at drives | Elmo G-TWI magnetics | not cited | unknown | **FLAG**: same as above |
| BMS (pack-referenced S32K344 + BQ79600-Q1) → CAN FD to Thor | isolated CAN transceiver | not chosen | none yet | **FLAG**: specify a reinforced isolated CAN FD transceiver (e.g. TI ISO1044, not yet cited) at the BMS/torso boundary |
| encoders, PT1000 at drives | through Elmo drive | not cited | unknown | **FLAG** with STO/EtherCAT |

**PCB rule E-PCB-1 (creepage/clearance, 92 V DC working)**
- Basis: IEC 60664-1:2020. Working voltage rounded up to 100 V. Pollution degree 2 (enclosed robot, non-condensing). Material group IIIa/b (FR4, CTI ≥ 175). Overvoltage category II.
- Creepage, Table F.5 (100 V, PD2, IIIa/b): **basic 1.4 mm**, reinforced = 2 × basic = **2.8 mm**. Printed-board values (PD1/PD2 coated, 0.1–0.16 mm) are not used, because coating is not assumed.
- Clearance, Table F.2: rated impulse **800 V** for ≤ 150 V systems in OVC II gives **0.2 mm** basic at PD2 (PD2 minimum). Reinforced uses the next impulse step, 1500 V, giving **0.5 mm**.
- **Rule:** bus ↔ SELV is ≥ 3.0 mm creepage and ≥ 1.5 mm clearance (2.8 / 0.5 plus design margin). Bus ↔ bus is functional, ≥ 0.6 mm.
- Isolator footprints (AMC1311 8.5 mm, RP03/RP40 pin rows) set the barrier. Keep slots, not copper, under all isolator bodies.
- [Table values from IEC 60664-1; the standard text is not in the repo. Verify against a licensed copy at the G1 design review.]
- **IP2X:** bus terminals (DCM, RP40/RP03 pins, contactor, AS150U, drive pins) get a finger-safe cover or potting. MR30 and XT30U housings are shrouded. Cover mass is TBD per part.

**Mass change:** none from this audit. The +0.024 kg RP03 was already booked in R-076. The isolated CAN transceiver and IP2X covers are TBD.


### 18.2d Arbiter R-077: AO rail on RP03-11012SRAW, 80 % derate (≤ 2.4 W hot per hand)
**Ruling.**
- Part: **RP03-11012SRAW** (RECOM RP03-RAW DS: 36–160 V in, 12 V / 250 mA, 84.5 %, 14 g, reinforced 3 kVAC).
- The 80 % derate is binding, so the AO load is ≤ 2.4 W hot.
- Reserve is ≈ 0.22 kg, including the RP03.

**AO load budget per hand (hot, at the RP03 output)**
| load | basis | W hot |
|---|---|---|
| XMC4800, 144/144/144, worst case | DS §3.2.8 Table 33: 250 mA max at 3.6 V, TJ 150 °C (§16.7) | 0.90 |
| 2 × DP83822HF | TI: < 220 mW each, 3.3 V | 0.44 |
| 6 encoders (2 ENX22 incremental + 4 ENX22 Absolute) | maxon: 22 mA at 5 V each, 132 mA (§16.8) | 0.66 |
| 2 × RS-422 quad receivers (AM26C32-Q1 class) | 15 mA max ICC at 5 V each [grade/DS to confirm, §16.8] | 0.15 |
| TMP117 | 3.5 µA at 1 Hz (TI DS) | ≈ 0 |
| R-051 latch (LM2903B-Q1 + NTC divider) | ≈ 1 mA at 3.3 V [EST] | 0.005 |
| 5 V buck loss (0.81 W out) | η 85 % [EST, part not chosen] | 0.14 |
| 3.3 V buck loss (1.35 W out) | η 85 % [EST] | 0.24 |
| **total** | | **2.53 W > 2.4 W: FAIL by 0.13 W** |

**Trims (cited)**
1. **MCU at 72/72/144 MHz, peripherals enabled.**
   - Table 33: 97 mA vs 135 mA typ (×0.72). Scaling the 0.90 W worst case by 0.72 [EST scaling] gives 0.65 W. That saves 0.25 W, plus 0.04 W of 3.3 V buck loss: **−0.29 W**.
   - CPU load was ≈ 27 % at 144 MHz (§16.8), so ≈ 54 % at 72 MHz. The BiSS-C 10 kHz read and the 11 + 6 loops still fit (re-confirm in FW-E14 bench).
   - **Adopted.**
2. **Single PHY if the hand is end-of-line** (§16.7 fallback): −0.22 W, plus 0.04 W loss, **−0.26 W**. Conditional on the EtherCAT topology (Controls). Not needed to pass.
3. **Encoders on the switched rail A:** **rejected**. The R-051 latch reset power-cycles rail A. The 2 incremental ENX22 would lose count, and the BiSS-C master would fault during every reset.

**Result.**
- With trim 1: **≈ 2.24 W hot ≤ 2.4 W (93 % of the derated limit, 75 % of the 3 W rating)**.
- With trims 1 + 2: ≈ 1.98 W.
- **No higher-power part is needed. Mass unchanged** (RP03-11012SRAW 14 g ×2, already booked +0.024 kg).
- **Bench check (T-029):** measure the AO input power hot (TJ near 125 °C, all encoders, both PHYs linked, 72 MHz). If it measures > 2.4 W, this goes back to the Arbiter with a larger isolated part (36–160 V class, mass to be cited and booked in full).
- **Open:**
  - buck efficiencies (parts not chosen)
  - RS-422 receiver datasheet
  - the 72 MHz scaling of the worst-case figure (Table 33 gives only typical at 72 MHz)


### 18.2e Arbiter R-078: uncited isolation = none; reinforced boundaries designed in (2026-10-14)
**Domains.**
- **Bus domain (43–92 V, hazardous by rule):** pack, all 32 Elmo drives with their logic, STO inputs, EtherCAT ports and encoder/PT1000 ports, the drive-to-drive EtherCAT links, and the BMS (S32K344 + BQ79600-Q1).
- **SELV domain:** 48 V brain rail (Thor, AGX301, fan/TSR), TMS570, hand boards (AO via RP03), head.
- Every crossing between the two domains must be reinforced (or basic + supplementary).
- All 32 drives share the bus reference, so **drive-to-drive links stay unisolated**. Only boundary crossings are isolated.

**Mass rule used.** Where a datasheet gives a mass, it is cited. IC and magnetics masses that TI and Würth do not publish are **computed from the datasheet package drawing** (body volume × 2.0 g/cm³ for mould compound plus leadframe, conservative), and are marked [DWG]. Under R-076 G1 wording this is a drawn part with computed mass. Replace with vendor material-content figures when available.

| # | boundary | design | part (citation) | count | mass each | kg |
|---|---|---|---|---|---|---|
| 1 | DCM3623 (basic per cTÜVus) → 48 V rail | Supplementary insulation around the whole 48 V domain. 2 layers of Nomex 410 0.13 mm (DuPont TDS: 115 g/m², 28 kV/mm AC rapid rise, so ≈ 3.6 kV per layer; 2 layers per the thin-sheet rule) lining the brain tray base, walls and lid (0.130 × 0.200 base + lid + walls 2 × 0.33 × 0.04 = 0.078 m²). The DCM input/output copper keeps E-PCB-1 reinforced spacing. | DuPont Nomex 410 TDS | 0.078 m² × 2 layers | 115 g/m² | **0.0179** |
| 2 | RP40 case (1.6 kVDC, treat as basic) → grounded bracket | Each case wrapped on its 5 bracket-facing sides with 2 layers of Nomex 410 0.13 mm, under the existing gap pad/strap. Added ΔT ≈ 0.4 K at ~4 W/case [k 0.1 W/mK EST]. | DuPont Nomex 410 TDS | 4 × 0.0016 m² × 2 | 115 g/m² | **0.0015** |
| 3a | EtherCAT: Thor/junction (SELV) → 5 drive branches (2 legs, 2 arms, waist) | Reinforced LAN transformer on each junction output port. Standard 1500 Vrms magnetics are basic at best, so they are not used here. | **Würth 749014012** WE-LAN 10/100: "reinforced insulation at 250 Vrms per IEC 62368-1/60601-1", 4000 Vrms, Cl 9 mm / Cr 15 mm, cURus E507007. **0–70 °C only.** Mass not in DS: [DWG] 24.4 × 17.8 × ~10 mm envelope, computed upper bound 6 g | 5 | 6 g [DWG] | **0.030** |
| 3b | EtherCAT: arm branch → hand board (SELV via RP03) | The hand is end-of-line on the arm branch (`harness.py` "ECAT arm branch → hand/tactile"), so 1 port per hand. The PHY moves to the cable side, powered across the barrier. MII is isolated with digital isolators, because there is no cited reinforced magnetics part rated to 125 °C. | **TI ISOW7741** (reinforced, integrated DC-DC 5 V → 3.3 V 140 mA at 36 %, −40…125 °C) + **ISO7740** + **ISO7742** (reinforced, −55…125 °C; ISO774x DS Rev K). MII 5 fwd / 7 rev covered (3f1r + 4r + 2f2r). | 2 hands × 3 ICs | ≈ 0.45 g [DWG SOIC-16W/20W] | **0.0027** |
| 4 | STO: TMS570 (SELV) → 5 STO daisy chains (STO1 + STO2 per branch = 10 channels) | Reinforced isolators with integrated bus-side power. Use the **default-low (F) variant**, so loss of isolator power = STO asserted (torque off). STO_RET is on the bus side. | **TI ISOW7740F-class** ×3 (12 ch, 2 spare). F ordering code to confirm. | 3 | ≈ 0.5 g [DWG] | **0.0015** |
| 5 | BMS CAN FD (pack-referenced) → Thor | ISO1044 is **rejected: TI rates it Basic**. Use **TI ISO1042 (non-B), Reinforced, 5000 Vrms, VIOWM 1060 Vrms, −40…125 °C** (ISO1042 DS Rev F, "ISO1042x Reinforced / ISO1042Bx Basic"). Logic side on the BMS. CAN side powered from SELV 5 V carried in the CAN harness (+2 conductors, inside the existing booking) [check]. | TI ISO1042DW | 1 | ≈ 0.41 g [DWG SOIC-16W] | **0.0004** |
| 6 | RP40 CTRL | TLP383 ordered as **D4 option** (VDE reinforced); same 0.128 g | Toshiba TLP383 DS | 4 | 0 delta | 0 |
| 7 | Encoders/PT1000 at drives | Bus-referenced, no SELV contact, so **no isolator is needed**. They are hazardous-live by rule, so their leads and bodies need insulation from accessible metal: SiF silicone single cores sit inside the 12 % sleeve (= supplementary), and the encoder PCBs inside the actuator housings get no exposed metal (Actuators to confirm). | – | – | – | 0 |
| | **Total booked** | | | | | **≈ 0.054 kg** |

**Conditions and risks.**
- **AO budget (R-077):** the cable-side PHY on ISOW7741 at 36 % efficiency adds about 0.39 W per hand (0.22 W PHY / 0.36 − 0.22 W). With 72 MHz and a single PHY (end-of-line), AO = 1.98 + 0.39 ≈ **2.37 W ≤ 2.4 W (99 %)**. A mid-line hand would fail. **The hand must stay end-of-line** (tactile on the hand board, not a downstream node).
- **MII timing across isolators:** ≈ 11 ns per channel. TX_CLK is cable-side, so the TX data round trip is about 25 ns of a 40 ns period (10 ns setup). This is marginal and needs a bench test (T-029).
- **Würth 749014012 is rated 0–70 °C.** Thermal must confirm the torso junction ambient is ≤ 70 °C. A cited lighter or hotter reinforced part would replace it.
- **Elmo STO input current is not cited.** Buffers may be needed after the ISOW outputs (≤ 4 mA each); size them from MAN-G-TWI.
- **Foot F/T at the leg-branch ends:** if it is powered from SELV, add 2 more boundary ports (+0.012 kg [DWG]). If it is bus-powered it stays in the bus domain. The owner must confirm.
- **DCM liner:** the cold-plate TIM path is unchanged. The liner is on the tray, not under the cold plate. The cold plate must be tied to the 48 V domain, not to accessible metal.
- **XMC4800 at 72 MHz** is accepted on condition that Controls confirms timing. The single PHY applies only where the hand is truly end-of-line.


### 18.2f R-079 (urgent): IP2X touch-guard inventory for bus-voltage points (Electronics owns it)
**Rule.**
- IP2X (IEC 60529): the jointed test finger, Ø12 mm × 80 mm, must not reach bus-live parts.
- A part enclosed by a cover that **needs a tool to remove** (torso power bay, brain tray, shoulder bays, actuator housings, pack case) is guarded by that cover, which is already booked by its owner, so it adds **0 g**. This is conditional on Covers/Torso/Arms confirming that every such cover is tool-only. That confirmation is item C1.
- Conformal coat is **not** counted as a touch barrier.

**Cited materials.**
- Techflex Shrinkflex H2N 2:1 polyolefin (techflex.com sizing chart, kg/100 m):
  - H2N0.19 (5.0 mm): 8.9 g/m
  - H2N0.25 (6.4 mm): 15.5 g/m
  - H2N0.38 (9.5 mm): 19.5 g/m
  - H2N0.50 (12.7 mm): 22.6 g/m
  - H2N1.00 (25.7 mm): 55.7 g/m
  - Dielectric 500 V/mil, SG 1.35
- PA12 covers: ρ 1.01 g/cm³ (RHO_PA12 as in `arbiter/a3_size.py`), 1.5 mm wall.

| # | exposed bus point | count | guard | cited basis | g |
|---|---|---|---|---|---|
| 1 | Pack cell/BMS terminals | – | pack case (Torso) | enclosure, C1 | 0 |
| 2 | AS150U pack main (front) | 1 pair | built-in shroud **IP40** | Amass AS150U spec "防护等级 IP40" | 0 |
| 3 | AS150U solder-cup backs | 2 halves × 2 poles × 25 mm | H2N0.38 | 19.5 g/m | 2.0 |
| 4 | Contactor LEV100A4ANG main terminals | 2 | boot from H2N1.00, 40 mm each | 55.7 g/m | 4.5 |
| 5 | Fuse / bus bar exposed run | 0.10 m [length EST, Torso layout] | H2N0.50 sleeve | 22.6 g/m | 2.3 |
| 6 | P-045 clamp: HS100 resistor lugs | 2 × 30 mm | H2N0.25 | 15.5 g/m | 0.9 |
| 7 | P-045 clamp MOSFETs/board, DCM/RP40/RP03 pins, AMC1311 boards | – | torso power bay / brain tray (lined, §18.2e) / shoulder bays | enclosure, C1 | 0 |
| 8 | Elmo drive power solder points (bus +/−) | 32 × 2 × 25 mm | H2N0.25 | 15.5 g/m | 24.8 |
| 9 | Elmo drive bodies in actuator housings / pelvis / shoulder | 28 | housing | enclosure, C1 | 0 |
| 10 | Knee drives on femur-rear plate (R-062, no-cover thigh zone, Legs 985200d) | 2 plates | PA12 cover 80 × 60 × 15 mm, 1.5 mm wall (13 800 mm² × 1.5 mm × 1.01) | computed from drawing | 41.8 |
| 11 | MR30 drive tees (32) | – | **integrated wire covers** on the MR30 halves (K&A listing: "integrated wire covers"); mass already in the 1.41 g/half | Amass MR30 | 0 |
| 12 | XT30U (8) solder-cup backs | 8 pairs × 2 halves × 2 × 15 mm | H2N0.19 | 8.9 g/m | 4.3 |
| 13 | XT60 (4) solder-cup backs | 4 × 2 × 2 × 20 mm | H2N0.25 | 15.5 g/m | 5.0 |
| | **IP2X total** | | | | **≈ 0.086 kg** |

**Against the +0.25 kg conservative booking:** the guards total 0.086 kg. **Credit back ≈ 0.164 kg**, which turns the R-079 −0.13 kg position to about **+0.03 kg** before §18.2e.

**Conditions.**
- **C1:** tool-only removal of every enclosure counted as the barrier (Covers, Torso, Arms, Legs).
- The bus-bar length is Torso's [EST].
- Re-check items 10 and 8 against final Legs/Actuators drive mounting.
- The R-078 boundary mass (§18.2e, +0.054 kg) is separate and booked in full.


### 18.2g AO supply up-rated: RP03 → RECOM RP06-11012SRAW (after Thermal: AO ≈ 2.9 W hot)
**Need.** Thermal puts AO at ≈ 2.5 W + 0.39 W (ISOW7741, §18.2e) ≈ 2.9 W hot per hand. The R-077 80 % derate means the rating must be ≥ 3.7 W. The RP03 (3 W) fails, and §18.2d's 2.24/2.37 W figures are superseded.

**Chosen: RECOM RP06-11012SRAW**, ×2 (one per arm, shoulder bay). Cited from the RECOM RP06-RAW datasheet (recom-power.com/pdf/Powerline_DC-DC/RP06-RAW.pdf) and the product page:
- **Input 36–160 VDC continuous, 4:1, 200 VDC for 1 s.** This covers 43–92 V with 68 V of headroom at the 92 V ceiling. It is the same input as the RP03-RAW.
- 12 V / 500 mA = **6 W**, 84.5 % efficiency, 130 µF max capacitive load.
- **3 kVAC/1 min, "Insulation Grade: reinforced"**. EN 62368-1 / UL 62368-1, EN 50155.
- −40 to +105 °C with derating; more than 85 °C without derating.
- DIP24, **31.8 × 20.3 × 10.6 mm**, **14 g typ.** It has the same package, pinout family and remote On/Off (positive) as the RP03.
- OLP hiccup at 150 %, UVLO, OVP, SCP.

**Derate check.** 2.9 W / 6 W = 48 % (the limit at 80 % is 4.8 W), leaving 1.9 W of margin. That covers a mid-line hand, a second PHY with ISOW (+0.61 W), or the 144 MHz MCU. So the end-of-line and 72 MHz conditions in §18.2d/e are no longer power-driven. They stay only as Controls' timing items.

**Other families checked.**
- The RP08 and other RECOM 2:1/4:1 lines mostly top out at 72–75 V input (e.g. 18–75 V), which is below the 92 V ceiling, so they were rejected.
- The RP06-RAW is the direct drop-in, so other vendors are not needed.

**Mass.** 2 × 14 g = 28 g, against 2 × 14 g booked (R-076). **Net 0.000 kg.** Footprint is unchanged.
**Thermal.** Dissipation at 2.9 W out and 84.5 % efficiency is ≈ 0.53 W per converter, against ≈ 0.53 W for an RP03 at the same load. The shoulder bay is unchanged against Thermal's 2.9 W case.

### 18.2 Checked and not counted
- **STM32H7 drop:** never booked as a separate mass. The hand board was booked as a board lump (Arms), and Thermal A43C already assumed it dropped. **Saving 0.**
- **`hand 24 V from wrist DC/DC` row (0.0128 kg):** 0.5 → 0.25 passes (0.6 K), but R-047 put the RP40s in the shoulder bay, so this row's route is stale. Actuators should re-book the row first. **Not counted.**
- **P-045 clamp:** 0.145 sum vs 0.150 booked, but the 0.030 board part is a Torso [EST]. **Not counted.**
- **A41 fan:** 0.042 vs 0.040 booked, so it is over, not under.
- **TMS570 0.040, NVMe, DCM filter/heatsink (a3_size):** all [EST]; no cited replacement.
- **Local phase leads (32 × 3 × 0.5 mm²):** already fail the rule at the knee (§17), so there is no reduction available.
- **JST-GH pairs (0.384 g):** already the lightest cited option.
- **Merged boards:** the XMC4800 merge (§16.7) removed the STM32H7 and LAN9252, but neither was booked separately (see the STM32H7 drop above). No other merge has a cited booked mass.
- **Shorter runs:** none without Legs/Torso CAD. The trunk runs are set by the Manhattan routing rule.

### 18.3 Result
- **Cited wire savings: 0.064 kg.** Low/medium risk, ratings kept, STO and R-038 untouched.
- **Target ≥ 0.18:** reached only if the Arbiter accepts #1 (soldered drive tees, +0.124 conditional, replacement mass [EST]); the total is then ≈ 0.188 kg.
- Without #1, electronics/harness alone cannot meet the target on cited data.
