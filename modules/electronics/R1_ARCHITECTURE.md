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

**STO wiring ≈ 0.270 kg** (datasheet g/m × routed length; route lengths per harness model). This replaces my R1 rough estimate of +0.14 kg, which assumed 2 conductors. Connector pins: if each drive tee uses a JST-GH 4-pin (harness model part, 0.384 g/pair), add 30–34 × 0.384 g ≈ 0.013 kg. Alternative to cut mass: carry STO on spare pairs if the drive carrier PCB connector allows it; not counted.
Electrical check: STO input current per drive is not in the extract read, so the rail driver current is open. The R1.1 total load is 34 drives in parallel per channel.
