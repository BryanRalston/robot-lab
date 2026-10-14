# RL Torso & Power — R1 architecture (2026-10-14)
Owner: RL Torso & Power (067740e6). Check script: `r1_torso.py` → `r1_torso.json`, figure `R1_torso_power.png`.
Scope: pelvis, torso frame, waist joints (selection by RL Actuators), battery pack, BMS, power distribution/protection, runtime.
Basis: CONTRACTS R1.1/R1.3/R1.4/§1a/§1c/§3, official rollup (R-027), `actuators/results/sizing.md`, `arms/R1_ARCHITECTURE.md`, `electronics/R1_ARCHITECTURE.md` (1e33c96). [EST] = estimate, ×0.5 evidence.

![R1 torso & power](R1_torso_power.png)

## 1. Chassis structure
- **Torso:** CFRP 2.0 mm monocoque shell (v3 used 3 mm; 2 mm proposed with local inserts) carrying a machined 7075 **shoulder bulkhead** (two 8 × M8 12.9 shoulder mounts, CONTRACTS §1c) and a 7075 **waist ring** bolted to the waist_pitch output. Pack slides into rails in the lower chest from the back (swappable, T7), latch + 2 guide pins + blind-mate connector.
- **Pelvis:** machined 7075 box: waist_yaw housing on top, 2 × hip bracket 8 × M5 12.9 below (§1c, hip y ±130 mm), hip_pitch twin-screw trunnion brackets (out of Legs scope, P-007 note) on the front/back walls.
- **Load paths:** arms → shoulder bulkhead → shell → waist ring → waist_pitch → waist_yaw → pelvis → hip brackets → legs. Pack mass goes rails → shell bottom flange → waist ring (not through the shell skin). Fall loads (T8): shoulder side impact into bulkhead (300 N·m shoulder_roll clutch caps arm moment); torso/pelvis shells are outer skin (no covers, R-021).
- **Mass (paper, all [EST] until CAD):** shell 1.705 + bulkhead 0.45 + waist ring 0.25 + pack rails/latch 0.20 + pelvis 1.45 + power distribution (busbars, branch fuses, 5 V aux, PCB) 0.25 = **4.305 kg** vs v3 allocation pelvis 1.6 + torso 2.8 = 4.40 kg (−0.095). No FEA this round.

## 2. Waist joints (DOF 2: yaw + pitch, T3 unchanged)
| joint | v3 / contract need | R1 load case (static, [EST] geometry) | need 1.5× | v3 selection avail | status |
|---|---|---|---|---|---|
| waist_yaw | 60 N·m, 2 rad/s | turning/arm reaction, not simulated | 60 (keep) | TBM2G-06008A + CSG-17-100, 70 | OK, keep |
| waist_pitch | 115.4 N·m, 2 rad/s | 10 kg at full reach, lean 30°: **125.5**; 20 kg carry lean 15°: 112.8 | **188** | TBM2G-06808A + CSG-25-100, **116** | **FAILS** |
Model: sim torso 18.762 kg @ 0.169 m (`humanoid_v3.xml`), catalog arms 9.54 kg/side (arms R1), shoulder 0.30 m above axis, payload 0.30 m (waist carry) / 0.60 m (reach). The v3 115.4 need had no payload case (T5 was not checked in v3).
Proposal to RL Actuators (to file as P-0xx): waist_pitch motor → **TBM2G-08508A** on the same CSG-25-100 (= hip_roll selection, 204 N·m avail, 1.56 vs 1.37 kg, **+0.19 kg**). Alternative: lower the T5 reach case lean to ≤ 15° (Controls/Arbiter call).

## 3. Battery pack (per CONTRACTS R1.3, R-010 — unchanged)
- Cell **Molicel INR-21700-P45B** (4.5 Ah typ, 3.6 V, 16.2 Wh, ≤ 70 g, 45 A cont; datasheet in `v3/PARTS.md`), screened ≥ 4400 mAh at 0.2C.
- **20S5P, 100 cells: 68.0 / 72.0 / 84.0 V (min/nom/max), 22.5 Ah, 1620 Wh typical / 1584 Wh binned.** Cell current 12 A at 60 A cont, 20 A at 100 A/2 s (≤ 45 A rating).
- Mass **8.75 kg** (= rollup line): cells 7.00, busbars/tabs 0.25, holders+foam 0.30, CFRP/6061 enclosure 0.75, BMS+FET board+fuse+connector 0.30, gap filler 0.15 [EST except cells].

## 4. BMS, protection, rails (real parts)
| function | part | note |
|---|---|---|
| cell monitor | 2 × **TI BQ79616-Q1** (16S each, used 10S+10S, daisy-chain) | cell V, temps, passive balance |
| host / SOC | TI MSP430/C2000-class MCU [part TBD] → CAN FD to safety MCU (Electronics §4) | |
| current sense | **TI INA229** on a low-side 100 µΩ shunt (Isabellenhütte BVR family) | low side because INA229 CM max 85 V < 90 V clamp |
| pack switch | back-to-back N-FETs, 6 + 6 × **Infineon IPT059N15N3** (150 V, TOLL), driven by **TI BQ76200** high-side driver with pre-charge path (47 Ω [EST]) | 150 V parts ≥ 1.6 × 90 V clamp; ≈ 2 mΩ total → 0.2 W at 9.8 A |
| main fuse | **Littelfuse L50S125** (125 A, R1.3) | DC interrupt rating vs pack short-circuit current to verify (O-T4) |
| regen | BMS regen-charge limit 30 A; chopper/clamp ≤ 90 V (R1.3; part = O-E6 with Electronics) | |
| motor bus | 68–84 V direct to every Elmo Gold Twitter VP+ (10–95 V) | |
| **brain rail (changed)** | **48 V intermediate rail: Vicor DCM3623TA5N53B4T00, 43–154 V → 48 V, 240 W** (+ choke 47718-232) | replaces booked DCM3623x75H26C2 (36–75 V in, cannot take 84 V / 90 V clamp; finding by RL Electronics). AGX301 takes 36–60 V. Lead time 52 wk (T10 risk); second-source idea: a 48 V brick in Vicor BCM/ PRM family or TI LM5185-class flyback [not verified] |
| drive logic VL / 24 V | 48 V → 24 V POL off the 48 V rail, or single-supply from VP+ (Electronics O-E3) | |
| head 12 V | RECOM RP40-11012SFR/P-HC from pack (R-026), unchanged | |
| always-on 5 V aux | **TI LM5164** (6–100 V, 1 A sync buck) from pack → BMS host, e-stop logic, wake | 100 V abs vs 90 V clamp |
| e-stop | Electronics §5: STO star from TMS570 (SS1 default, Cat 0 on button), then BMS FETs open (acts as main contactor; no electromechanical contactor booked — O-T3) | |

## 5. Runtime vs T7 (CONTRACTS R1.3 + R-025 + torso adds)
Torso adds 1.5 W [EST] (BMS 1.0, FETs 0.2, distribution 0.3). Usable 90 % [EST, R-010].
| case | W | h | target |
|---|---|---|---|
| walk 1.0 m/s (rating speed, R-010), typical | 704.9 | **2.07** | ≥ 2 h MET |
| walk 1.0 m/s, binned 1584 Wh | 704.9 | **2.02** | MET (thin, 7.9 W under the 712.8 W pass line) |
| walk 1.2 m/s, typical | 847.5 | 1.72 | tracked, NOT MET |
| mixed 50 % walk 1.0 / 50 % stand (stand 294 W [EST]) | 499.4 | **2.92** | **≥ 4 h NOT MET** |
The 48 V DCM swap is ~power-neutral (both ~92 % class; to confirm from datasheet, O-E7).

## 6. Mass line for the rollup
| line | paper kg | credible kg | note |
|---|---|---|---|
| torso structure + pelvis + power distribution | 4.305 | 4.353 | vs 4.40 v3 inside "all other lines"; saving 0.095 ×0.5 credit |
| battery 20S5P | 8.750 | 8.750 | unchanged |
| waist actuators (Actuators line) | 2.40 → 2.59 | | +0.19 if the waist_pitch motor change lands |
Thermal (1.0 kg in the v3 torso allocation) is RL Thermal's; harness/covers stay with Actuators/Arbiter lines.

## 8. Regen clamp on the torso distribution board (RL Electronics §9.3, 1d70018; closes O-E6 part pick)
Spec (Electronics): hardware comparator ON 88 V / OFF 86 V; bus ≤ 90 V at the design pulse 4.5 kW, ≤ 400 J/event; absolute ceiling 92 V; R ≤ 1.72 Ω, ≥ 400 J pulse, ≥ 200 W continuous, thermal cutout to safety MCU; FET ≥ 150 V. Roboteq SR5K100V25R rejected (Electronics).
| function | part | key data (datasheet) | check |
|---|---|---|---|
| clamp switch | 2 × **Infineon IPT059N15N3** (ATMA1) in parallel, low side | 150 V, 5.9 mΩ, 155 A, E_AS 520 mJ, R_thJC 0.4 K/W — https://www.infineon.com/part/IPT059N15N3 , DS https://www.tme.eu/Document/3fe4942e828bcb431c03c4d931fded80/IPT059N15N3-DTE.pdf | 58.7 A / 2 = 29 A each → ~5 W each during pulse; 150 V ≥ 1.6 × 92 V |
| clamp resistor | **Arcol/Ohmite HS200 1R5 F** (1.5 Ω ±1 %, aluminium housed wirewound, "wound to maximise high pulse capability") | 200 W on standard heatsink (3750 cm² × 3 mm Al), 50 W free air, 1900 V limiting voltage, ~475 g — https://www.ohmite.com/hs-aluminium-housed-resistors/ | 1.5 Ω ≤ 1.72: 88²/1.5 = 5.16 kW ≥ 4.5 kW, so the bus stays ≤ 88–90 V at the design pulse; 400 J → ~78 ms at full power. 400 J pulse: inside the HS overload curve [EST, read the curve: O-T8]; 200 W continuous only with the torso Al bulkhead/fin stack as heatsink [EST] |
| thermal cutout | NC bimetal on resistor body, ~120 °C, wired to TMS570 + hard-latches comparator off | part to cite (O-T8) | |
| comparator / gate drive | hardware comparator with 86/88 V hysteresis off an always-on 5 V reference; low-side gate driver | parts to cite (O-T8) — no firmware in loop | |
| main contactor | **TE KILOVAC LEV100A4ANG** (3-1618389-7), 12 V coil from a second LM5164 set to 12 V | 900 VDC switching, 100 A cont, 200 A 3 min, 1250 A short-circuit, coil 461 mA — https://www.te.com/en/product-3-1618389-7.html | 900 V ≥ 92 V; 100 A ≥ 60 A cont; gives galvanic disconnect (answers O-T3); mass not read [EST 0.20] |
| pre-charge resistor | **Arcol/Ohmite HS50 47R J** | 50 W on heatsink, 1250 V limiting — same HS datasheet | 84 V / 47 Ω = 1.8 A peak; energy ½CV² with drive caps (to be summed, O-T8) |
| pre-charge switch | **Infineon BSC520N15NS3 G** | 150 V, 52 mΩ, 21 A — https://www.infineon.com/part/BSC520N15NS3-G | 150 V ≥ 92 V |
**Interlock (requirement on BMS firmware + hardware):** the BMS may not open the charge path (contactor or BQ76200 FETs) while any drive is enabled, except via SS1 controlled stop → STO confirmed (TMS570), then open. Exception: hard faults where the cell is at risk (cell OV/UV/OT, short-circuit) — then STO and open simultaneously, the clamp absorbs the regen. This exception needs Electronics/Arbiter agreement (O-T9).
**Mass (new, under R-024):** HS200 0.475 + 2 FETs/comparator/board 0.030 + contactor 0.20 [EST] + pre-charge 0.040 [EST] = **+0.745 kg**. Conflicts with Electronics' 0.10–0.15 [EST]; the HS200 is the driver. Cheaper path: smaller pulse-rated resistor using the 400 J transient only (e.g. HS100-size, ~115 g) if the 200 W continuous need is dropped — Arbiter/Electronics call (O-T8).

## 9. Answers to RL Arms & Hands (R2_OPEN_ITEMS O-A1)
1. **Shoulder y ±0.170 m in the v5 chest: kept.** V5 plan row 4 tapers 330 → 250 mm from shoulder line to waist; 330 mm = ±0.165 m shell at the shoulder line, flange face y ±0.165 [EST], pitch axis at ±0.170, z +0.220 above waist_pitch as sim. ID to confirm the taper starts below the shoulder bulkhead.
2. **8 × M8 12.9 accepted, PCD 80 mm** (fits the CSG-25 frame D 96 mm envelope). Steel thread inserts in 7075, engagement ≥ 1.5 d. Hand calcs: A_s 36.6 mm², preload 0.7 × 1100 MPa × A_s = 28.2 kN/bolt; max bolt tension from moment = 4M/(n·PCD).
   | case | moment at flange | shear | bolt tension max | margins |
   |---|---|---|---|---|
   | static 82.2 N·m (need 123.4) | 123.4 N·m | ~0.2 kN | 0.77 kN | separation 37×; friction (μ 0.15, 33.8 kN) huge |
   | side fall (v3 shoulder_F 11.5 kN at 60 mm, `v3.json`; roll clutch 300 N·m caps the roll gear, not the impact path) | 690 N·m | 11.5 kN | 4.31 kN | separation 6.5×; slip 33.8/11.5 = 2.9× |
   | clutch-limited roll torque | 300 N·m | — | 1.88 kN | 15× |
   **Bulkhead:** 7075-T6 (yield 503 MPa) boss 120 mm wide: at fall 690 N·m, t = 10 mm → 345 MPa (SF 1.46, fails SF ≥ 2); **t = 12 mm → 240 MPa, SF 2.1**; static 123.4 N·m → 43 MPa. Pocketed 12 mm bulkhead [EST] 0.60 kg vs 0.45 booked (+0.15). FEA later (not this round).
3. **Arm inertials in sim:** not Torso. CHARTER: modules own only their folder; `sim/v3` is shared and has been edited by Legs on Arbiter request (P-019 → L42), with Controls now owning legs/WBC sim (eac9a46). Proposal: Arms publishes catalog per-body mass/COM/inertia (5.953 → 9.54 kg/side); **Controls (sim owner) applies**, sequenced by Robot Lab; Torso supplies the re-split torso body (pack 8.75 kg in chest, O-T7) in the same change.

## 10. A41 / P-030 (R-030, e149620): Thor cooling duct, joint with RL Electronics
- Layout: chest duct front-low intake → 2 × 40 mm blowers (~21 CFM, ~3 W) → Thor fin stack/cold plate → exhaust upward/back through chest vents under the shoulder bulkhead. **48 V DCM3623TA5N53B4 mounted on the Thor cold plate** (in the duct airstream downstream of the blowers). **Pack in the lower chest bay, upstream of and separated from the duct by a CFRP baffle; exhaust path never crosses the pack.** Clamp resistor HS200 bolts to the bulkhead on the exhaust side (its heat goes out with the duct air).
- Mass: **+0.040 kg (P-030) booked in the torso line**; +3 W in power (in the 4 h mixed check: still NOT MET).

## 11. Mass line (updated)
| line | paper kg | note |
|---|---|---|
| torso structure + pelvis + distribution (§1) | 4.305 | |
| shoulder bulkhead 12 mm (§9) | +0.150 [EST] | |
| P-030 blowers (R-030) | +0.040 | booked in full |
| regen clamp + contactor + pre-charge (§8) | +0.745 | new mass, to Arbiter (R-024) |
| **torso line** | **5.240** | vs 4.40 v3 allocation (+0.84) |
| battery 20S5P | 8.750 | unchanged |

## 12. Rulings pending and idle-power estimate
The Arbiter is ruling on **O-T5** (4 h mixed), **O-T2** (waist_pitch), **O-T3** (FET vs contactor disconnect; §8 now adds the contactor). Robot Lab leans to re-rating the mixed duty and cutting idle power.
Idle-power available in torso/BMS: BMS always-on 1.0 → 0.3 W (sleep host, BQ79616 low-power mode) [EST]; contactor coil 5.5 W while closed (LEV100 datasheet) → economizer/PWM hold ~1.5 W [EST]; FET losses at stand ~0.05 W; blowers 3 W → speed to Thor load. **Torso/BMS savings ≈ 5–6 W**, but the contactor itself adds 5.5 W unless economized. For 4 h mixed, P_mixed must fall from ~500 W to ≤ 365 W (−135 W); the real levers are compute cap (120 W) and drive idle overhead (30 × 3.3 W ≈ 99 W), not torso.

## 13. R-031 items (2026-10-14)
### 13.1 O-T2 waist_pitch margin (approved on citation)
Requirement: static 125.5 N·m (10 kg at 0.60 m reach, 30° lean; T5 one-hand case) from `r1_torso.py` (inputs: sim torso 18.762 kg @ 0.169 m, `sim/v3/humanoid_v3.xml`; arms 9.54 kg/side catalog, `arms/R2_OPEN_ITEMS.md` O-A1; shoulder z 0.30 [EST]). Need = 1.5 × 125.5 = **188.2 N·m** (CONTRACTS §0 margin rule). Selection TBM2G-08508A + CSG-25-100 = **204 N·m** available (`actuators/results/sizing.md`, hip_roll row; CSG-25-100 repeated peak 204, `v3/PARTS.md`). **Margin 204/188.2 = 1.08 on need, 1.63× on the static requirement.** Mass 1.56 vs 1.37 kg (+0.19, Actuators line). Speed 2 rad/s need vs 3.6 rad/s (hip_roll ω30).
### 13.2 O-T3: contactor chosen over FET-only
Choice: **keep the TE KILOVAC LEV100A4ANG contactor (900 VDC, 100 A, §8) in series with the BQ76200 FET pair.** Why: two diverse disconnects (electromechanical + semiconductor) make the pack disconnect single-fault tolerant without a diagnostic-coverage argument; a FET-only case needs failed-short detection (V_DS test pulses), redundant FET banks and a proven reaction time, i.e. an FMEDA we cannot evidence this round. FETs open first (fast, arc-free); contactor opens after current < 5 A [EST] to avoid DC arcing. Welded-contactor detection: bus voltage after open + pre-charge sense; failed-short FET detection: BQ76200 V_DS check at each close. Mass +0.20 [EST], coil 5.5 W → PWM economizer to ~1.5 W [EST].
### 13.3 Regen clamp = **P-045**, shared with RL Electronics (§8 parts unchanged).
### 13.4 A41 Thor duct (Electronics §11, f4e839c): our side
- Load 134 W, 24.3 CFM at ΔT 10 K; fan **Sunon PF40281B1-000U-S99** (40×40×28, 24.9 CFM, 6.12 W, 42 g, PWM) per Electronics, Arbiter to rule; replaces the P-030 2 × 40 mm blower estimate (3 W → 6.12 W, 40 → 42 g).
- **Fan supply:** **TRACO TSR 1-48120WI** (17–72 V in, 12 V, 1 A, 93 %, SIP-3) from the 48 V rail — https://www.tracopower.com/tsr1wi-datasheet . Fan 0.51 A ≤ 1 A. Mass ~4 g [EST].
- **Fan tach → TMS570 safety MCU** (fan-fail → Thor throttle, then SS1 if Thor over-temp).
- **Vents:** Q = 0.0115 m³/s. Free-area velocity ≤ 2.5 m/s → **46 cm² free area each**; perforated/louvred grille ~50 % open → **~95 cm² gross each (e.g. 120 × 80 mm)**. Δp ≈ K·½ρv² with K ≈ 2.5 → ~9 Pa per vent, ~20 Pa both + fins [EST]; the fan's static-pressure curve must cover this (O-T10). Guard: holes ≤ 3 mm or louvre + stainless mesh (finger-safe IP2X; louvres angled down for splash, IPX4 aim).
- **Placement:** intake low on the chest front (below the sternum line, above the pack bay lid); exhaust high on the upper back between the shoulder bulkheads. Air path: intake → fan → Thor cold-plate fins (DCM3623 on the same plate) → exhaust. **Sealed partition** (CFRP 1 mm, gasketed) between duct and the pack bay; HS200 clamp resistor on the exhaust side.
- **Mass:** partition CFRP 0.06 m² × 1 mm 0.093 + duct walls PC 1 mm 0.04 m² 0.048 + converter 0.004 + fan Δ 0.002 = **+0.147 kg** on top of the P-030 0.040.
### 13.5 O-T5: duty re-rate and idle cuts
Evidence: no humanoid maker publishes a walk/stand split. Closest published data: Agility Digit, tote moving at GXO (AMR → conveyor), **~4 h battery with autonomous docking** (Agility via Humanoids Daily, https://www.humanoidsdaily.com/news/agility-robotics-upgrades-digit-humanoid-with-longer-runtime-amr-integration-and-enhanced-safety-features ; DEPLOY registry https://registry.deploy.report/deployments/digit-gxo-georgia-warehouse). The workflow is station-based with short walks; the "50 % walking" mixed case is therefore pessimistic. Proposed re-rate: **≥ 4 h at 20 % walking / 80 % stand-manipulate**, with ≥ 2 h continuous walking unchanged (hard). The 20 % share is [EST], to be replaced by Controls' task-sim time split.
Idle cuts: BMS sleep 1.0 → 0.3 W; contactor economizer 5.5 → 1.5 W; compute cap during stand −40 W (T5000 modes 40–130 W, R-021) [EST]. Torso adds now: BMS 0.3 + FET 0.2 + distribution 0.3 + contactor 1.5 + fan 6.12 = 8.4 W.
| case | W | h (1620 Wh × 0.9) | target |
|---|---|---|---|
| walk 1.0 m/s, typical | 711.8 | **2.05** | MET |
| walk 1.0 m/s, binned 1584 Wh | 711.8 | **2.00** | MET by 1.0 W (pass line 712.8 W) — **no margin; fan 6.12 W ate it** |
| stand/manipulate (294 − 40 cap + 8.4) | 262.4 | 5.56 | |
| mixed 25/75 | 374.8 | 3.89 | NOT MET |
| **mixed 20/80 (proposed rating)** | 352.3 | **4.14** | MET |
Risk: walking binned runtime sits on the pass line. If the Arbiter books the 6.12 W fan as-is, either a lower-power fan curve (PWM at walking-load Thor power) or the G5 regen evidence is needed.

## 14. Mass line (updated, R-031)
| line | paper kg |
|---|---|
| §11 torso line | 5.240 |
| A41 duct, partition, fan converter (§13.4) | +0.147 |
| **torso line** | **5.387** (contactor kept, §13.2) |
| battery | 8.750 |

## 7. Open questions / conflicts (not edited in others' files)
- **O-T1 (Electronics, coordination):** adopt the 48 V intermediate rail with DCM3623TA5N53B4T00; Torso hosts the DCM on the power distribution board or the brain tray? Mass 0.024 [UNVERIFIED for variant] stays in the brain line; who books the 47718-232 choke; 24 V VL source (O-E3); BMS→safety MCU CAN FD message set; e-stop = FET-open vs contactor (O-E6).
- **O-T2 (Actuators/Arbiter):** waist_pitch 116 N·m < 188 N·m need with T5 payload → TBM2G-08508A, +0.19 kg.
- **O-T3 (Electronics/Arbiter):** no mechanical contactor; FETs as disconnect needs a safety argument (welded-FET detection via BQ76200 diagnostics).
- **O-T4:** L50S125 DC breaking capacity at 84 V and pack prospective short-circuit current (100 cells, ~15 mΩ/cell) to be verified.
- **O-T5 (Arbiter):** T7 4 h mixed is not met (2.92 h). Options: re-rate mixed duty, 20S6P (breaks T2), or idle-power cuts (compute cap). Ruling requested.
- **O-T6:** usable 90 % at 3.4 V/cell floor still [EST] (R-010); read P45B discharge curve at ~2 A/cell.
- **O-T8:** clamp: read HS200/HS100 overload curve for 400 J, cite comparator, gate driver, thermal cutout, sum drive bus capacitance for pre-charge; HS200 mass (0.475) vs Electronics estimate.
- **O-T9 (Electronics/Arbiter):** interlock exception for cell-at-risk faults.
- **O-T10:** Sunon PF40281B1 static-pressure curve vs ~20 Pa vents+fins; fan PWM schedule.
- O-T2 approved on citation (§13.1); O-T3 → contactor (§13.2); O-T5 re-rate proposed (§13.5).
- **O-T7 (Legs/Controls):** sim torso 18.762 kg should be re-split (pack 8.75 in chest) when the sim is updated.
