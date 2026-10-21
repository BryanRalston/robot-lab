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

## 15. R1.3 (after Electronics §13 a095c0c, R-032, R-033 73d1984, R-034). Script `r13_torso.py` → `r13_torso.json`; figure updated.
### 15.1 P-045 clamp: HS100 1R5 F (R-033 booked 0.15 kg), bolted to the shoulder bulkhead, exhaust side
Source: Arcol "Heatsink Range Technical Information" (TI004 overload, TI008 thermal capacity) https://assets.rs-online.com/v1698974646/Datasheets/840dcab3450261b61b91e3aa6789a31d.pdf . Tabulated points: 10× rating for 1 s, 5× for 5 s, 2× for 3 min; HS100 thermal capacity 76.7 J/°C, unit 90 g; HS50 19.78 J/°C, 25 g. The curve itself is a graph with no points below 1 s.
Pulse: 88²/1.5 = 5.16 kW for 77.5 ms (400 J).
| part | multiple of rating | allowed: power-law through 1 s/5 s points | allowed: constant energy (1 kJ) | ΔT adiabatic | verdict |
|---|---|---|---|---|---|
| HS100 1R5 | 51.6× | 30.1× | 129× | 5.2 K | **OPEN**: inside the energy bound, outside the conservative extrapolation |
| HS50 1R5 | 103× | 30.1× | 129× | 20 K | OPEN, closer to the limit. **Not a fallback** without written Arcol data |
| 2 × HS100 0R75 in series | 25.8× | 30.1× | 129× | 2.6 K | PASS on both bounds, +0.09 kg |
**O-T8 (updated):** comparator, gate driver and thermal cutout still to cite; HS100 stays booked. Ask Arcol for the < 1 s overload point. If it is below 52×, use 2 × HS100 0R75 (+0.09 kg, still inside R-034; see §15.6).
### 15.2 Charge rule: 4.15 V cap quantified. **Recommendation: do not cap.**
The P45B datasheet capacity between 4.15 and 4.20 V is not read; 3–5 % [EST] is typical for NMC/NCA 21700 cells.
| charge limit | usable Wh typ / binned | walk 1.0 typ / binned h | walk 1.2 h | mixed 20/80 h | binned 2 h margin |
|---|---|---|---|---|---|
| 4.20 V (current) | 1458 / 1426 | 2.05 / **2.00** | 1.71 | 4.14 | **+1.0 W** (pass line 712.8 W vs 711.8 W) |
| 4.15 V, −3 % | 1409 / 1378 | 1.98 / 1.94 | 1.65 | 4.00 | **−22.8 W: T7 FAILS** |
| 4.15 V, −5 % | 1377 / 1346 | 1.94 / 1.89 | 1.61 | 3.91 | **−38.6 W: T7 FAILS** |
A 4.15 V cap costs 49–81 Wh and 0.07–0.11 h of walking, which breaks T7 hard. Alternative rule: charge to 4.20 V at the dock, and have the BMS accept regen pulses at any SOC, with the cell OV trip set above 4.20 V (e.g. 4.25 V [EST, Molicel confirmation needed]). At 711.8 W the pack leaves the top 4 % in about 5 min, and the clamp covers the rest. Case (b) of Electronics §13.1 then lasts only minutes at < 40 W average.
### 15.3 Pre-charge (R-033 approved HS50 47R; lighter option, optional)
Bus capacitance: 32 drives × 990–1400 µF (Elmo §10.2.4.2 rule, O-E10) = 32–45 mF → ½CV² at 84 V = **113–159 J per pre-charge**. That rules out SMD thick-film pulse parts, and linear pre-charge through the IPT059N15N3 (SOA at 80 V without evidence). The BQ76200 pre-charge output only drives a switch; it still needs a resistor.
**Option: Arcol HS25 47R** (same TI008 table: 10.7 J/°C, 12.5 g) → 159 J gives 15 K. Peak 1.8 A, 150 W = 6× for < 1 s, inside the 10×/1 s point. τ = 47 Ω × 45 mF = 2.1 s, ~10 s to 99 %. **Saves 12.5 g vs the HS50.** Switch is still the BSC520N15NS3 G. Booked mass stays R-033's 0.232 until Arbiter accepts the swap.
### 15.4 O-T9: Electronics' scheme accepted
Hardwired dual-channel FAULT_N plus a CAN FD fault frame go to the TMS570. The TMS570 applies STO (Cat 0) to all drives. The BQ76200 FETs open at the same time; the contactor opens once current is < 5 A. The clamp comparator and gate supply are powered from the **drive-side** bus. The fault latches: restart needs fault clear, then manual reset, then pre-charge, then contactor close. Normal faults keep SS1 → STO → open. **G5 test:** open the pack at peak regen; the bus must peak ≤ 90 V without reaching the drive OV trip.
### 15.5 Records
- **O-T10 PASS** on the datasheet P-Q curve (≈ 24 CFM at ≈ 20 Pa, ΔT ≈ 10 K); the fan is booked at 6.12 W in full (R-032).
- DCM3623TA5N53B4T00 sits on the Thor cold plate. The 47718-232 choke goes in the brain line (`dcm_filter_heatsink`), not Torso.
- **O-E3:** no 24 V supply. Drives run VL single-supply from VP+ ("S" variant, confirm at order).
- **TSR 1-48120WI goes on the 48V_BRAIN net only** (17–72 V in); it must never connect to the pack bus.
- **BMS → TMS570 message set (Electronics §13.7) vs part capabilities:**
  | message | supported by | gap |
  |---|---|---|
  | FAULT_N dual channel | BQ79616 NFAULT (one hardware line) | **2nd independent channel missing.** Add an independent secondary cell OV/UV/OT protector or a host-MCU channel with its own measurement (part TBD) |
  | BMS_PACK V/I/SOC/SOH/limits | V from BQ79616; I from INA229; SOC/SOH/limits computed by host | host MCU still unpicked (§4) |
  | BMS_STATUS FET/contactor feedback | BQ76200 has no drain-source / failed-short diagnostics; LEV100A4ANG has no auxiliary contact | **add a drive-side bus voltage sense** to the host ADC (detects welded contactor and shorted FET via pack-vs-bus voltage after an open command) |
  | BMS_CELLS_SUMMARY | BQ79616 cell V and temperature | none |
  | "internal short" in FAULT_N | not directly measurable | soft detection only (self-discharge/imbalance trend); move it to BMS_WARN |
  | heartbeat / SAFE_CMD / E2E CRC | host firmware | none (host) |
### 15.6 Torso mass line and R-034 overrun request
| item | kg | basis |
|---|---|---|
| torso CFRP shell 2 mm | 1.705 | [EST] area × density |
| shoulder bulkhead 7075 (12 mm, §9) | 0.600 | [EST] (0.45 + 0.15) |
| waist ring 7075 | 0.250 | [EST] |
| pack rails + latch | 0.200 | [EST] |
| pelvis 7075 | 1.450 | [EST] |
| power distribution board, busbars, branch fuses, 5 V aux | 0.250 | [EST] |
| duct fans booking (P-030/P-044) | 0.040 | R-030/R-032 |
| duct partition, walls, TSR 1-48120WI | 0.147 | §13.4 |
| regen clamp P-045 (HS100 1R5 + FETs/board) | 0.150 | R-033 |
| pack disconnect: LEV100A4ANG + HS50 47R + BSC520N15NS3 | 0.232 | R-033 (contactor datasheet mass to cite before G1) |
| **total** | **5.024** | |
| allocation (pelvis 1.6 + torso 2.8) | 4.400 | CONTRACTS §3 |
| **net overrun** | **+0.624** | ≤ 0.80 (R-034), margin 0.176 |
The earlier ~0.99 kg figure assumed the HS200 clamp (0.475 + board); the HS100 recovers 0.33 kg. Optional: HS25 pre-charge −0.0125 → +0.612. If Arcol rejects the HS100 pulse, 2 × HS100 0R75 → +0.714, still ≤ 0.80.
**Request to Arbiter (R-034):** "RL Torso & Power requests booking the torso line at 5.024 kg, +0.624 kg net over the 4.40 kg allocation (cap 0.80, margin 0.176). Drivers: regen clamp P-045 0.150 and pack disconnect 0.232, both required for safety (R-033); A41 duct and partition 0.187 (R-030/R-032); shoulder bulkhead +0.150 for side-fall SF 2.1 (§9). Structure itself is 0.095 under allocation. All structure masses are [EST] until CAD. The contactor mass is to be cited before G1."

### 15.7 O-T7: re-split sim torso body, ready for Controls to merge
`sim_torso_body_r1.json` (from `sim_torso_body_r1.py`), in the waist_pitch frame (sim/v3 body `torso`):
- **Mass 16.625 kg, COM (−0.0013, 0.0007, 0.158) m.**
- Full inertia (Ixx Iyy Izz Ixy Ixz Iyz) = 0.297, 0.170, 0.204, −0.0008, −0.0098, −0.0003 kg·m².
- Replaces sim/v3's 18.762 kg at z 0.169.
- Includes: the 8.75 kg pack in the lower chest bay; the brain (1.261 kg); the torso items from §15.6; and 2 × 1.52 kg shoulder_pitch actuators at y ±0.170, z 0.22 (inertia taken from `arms/arm_inertials_r3.json`). The shoulder actuators are in **Arms' mass line, not torso**.
- Excludes: head/neck, waistY, pelvis, and harness/covers.
- Arms accepted y ±0.170 and 8 × M8 on a BC80 bolt circle.
- sim/v3 not edited.

## 16. R1.4 (R-035 38c3fe7, R-036 3b50c3c)
**Recorded.**
- **R-035:** torso line booked at **5.026 kg**. That is the 5.024 itemization with the Sunon fan at its cited 0.042 kg. It absorbs the P-045, R-033 and Thor-fan bookings, so nothing is counted twice. The 2 × HS100 0R75 fallback is pre-approved (+0.09 kg).
- **R-036:** charge voltage is **4.20 V/cell**. BMS regen acceptance at any SoC is a hard requirement (G5 T-027). The cell OV threshold must be cited from Molicel before G1. The 2 h walk margin is +1.0 W, so any new continuous load over 1 W must be offset or go back to the Arbiter.

### 16.1 Second-channel protector: 2 × TI BQ77216 (stacked 10S + 10S)
Datasheet: https://www.ti.com/lit/ds/symlink/bq77216.pdf . Per IC: 3–16S, independent per-cell OV/UV/open-wire, OT/UT with NTC, fixed delays, functional-safety-capable, 85 V max, I_CC 2 µA typ / 3.5 µA max, OV options include 4.225 / 4.25 V.
- **Variant:** OV 4.25 V (see 16.3), UV 2.5 V class option.
- **Wiring:** each IC's COUT/DOUT (open-drain) → level shift (opto, TI E2E stacking guidance / TIDA-00108) → wired-OR into **FAULT_N channel 2**, independent of the BQ79616 NFAULT (channel 1) and of the host MCU.
- **Power:** < 0.001 W plus level-shift bias ~0.01 W [EST].

### 16.2 BMS host MCU: NXP S32K344 + TI BQ79600-Q1 bridge
- **S32K344** (lockstep Cortex-M7, ISO 26262 up to ASIL D, 6 × FlexCAN all CAN FD, 6 × LPSPI). Datasheet: https://www.nxp.com/docs/en/data-sheet/S32K3xx.pdf
- **BQ79600-Q1** SPI/UART ↔ BQ7961x daisy-chain bridge, functional-safety-compliant, ring architecture, wakes the host on a fault. Datasheet: https://www.ti.com/lit/ds/symlink/bq79600-q1.pdf
- The host computes SoC/SoH, charge/discharge/regen current limits and the drive-side bus-voltage plausibility check (welded contactor / shorted FET, §15.5). It sends CAN FD to the TMS570 (Electronics §13.7 set).
- **Power [EST; run currents not read]:** S32K344 at reduced clock ~0.3 W; BQ79600 ~0.05 W; 2 × BQ79616 duty-cycled scan (10 Hz, sleep between) ~0.1 W each. **BMS total ≈ 0.56 W** against the 0.3 W booked in §13.5: **+0.26 W**.
- **Offset:** none needed. Margin **+1.0 − 0.26 = +0.74 W ≥ 0** (P_walk 712.06 W ≤ 712.8 W pass line). If the measured S32K344 current is higher, the offset is the contactor economizer setpoint (1.5 W → 1.0 W [EST, LEV100 drop-out 1.2 V on the 12 V coil]).

### 16.3 Citations
- **LEV100A4ANG mass: 190 g (6.7 oz)**, from the TE datasheet "KILOVAC LEV100 Series 900 Vdc Contactor", Physical Data: https://www.farnell.com/datasheets/693620.pdf (and the TE catalog section). It replaces the 0.20 [EST] → disconnect 0.222 kg, **torso line −0.010 kg → 5.016 kg** (paper; R-035 booking 5.026 stays until the Arbiter re-books).
- **Molicel P45B** (product data sheet v1.4, https://www.molicel.com/wp-content/uploads/INR21700P45B_1.4_Product-Data-Sheet-of-INR-21700-P45B-80109.pdf ; detailed spec "Cell Specifications of INR-21700-P45B"):
  - charge voltage 4.2 V, **end-of-charge voltage 4.20 ± 0.05 V**;
  - standard charge 4.5 A, **max charge 13.5 A** (70 °C cut-off) → 67.5 A pack, so 30 A regen acceptance is inside the rating;
  - minimum capacity 4300 mAh (v1.4).
  - **No cell OV threshold is published.** OV is set at **4.25 V** (BQ77216 option, the top of the ±0.05 V end-of-charge tolerance). Molicel's written confirmation is still needed before G1 (R-036).
  - Note: v1.4 minimum capacity is 4300 mAh, so the ≥ 4400 mAh binning (R-010) stays a supplier screening requirement.

### 16.4 Deltas
| item | power | mass |
|---|---|---|
| BQ77216 × 2 + level shift | +0.01 W | in BMS board 0.30 (pack line) |
| S32K344 + BQ79600 + duty-cycled BQ79616 vs 0.3 W booked | +0.25 W | in BMS board |
| LEV100 cited 190 g vs 200 [EST] | — | −0.010 kg (torso 5.016 paper) |
| **walk 1.0 m/s binned margin** | **+0.74 W** (was +1.0) | |

## 17. R1.5: shoulder bays for RL Arms & Hands (440c7a8 §A42.4), plus records
### 17.1 Mounting face: on the bulkhead, no added mass
- Each side has an **outboard-facing pad on the 12 mm 7075 bulkhead**, machined flat, **≥ 80 cm² (e.g. 100 × 80 mm)**, below and inboard of the 120 mm shoulder boss.
- The hand node (70 × 45 mm), 2 × RP40, 2 filters and the D70 wrist drives strap to it through a ≤ 1 mm, ≥ 3 W/mK gap pad, with M4 inserts on a 20 mm grid [EST].
- The pad is already inside the bulkhead envelope (0.60 kg). **The 6061 bracket (+0.032 kg/side) is not needed.**
- **Bracket temperature sensor:** an NTC (or a TMP-class IC) bonded at the pad centre, wired to the hand board (Arms' derate 90 °C / off 100 °C). A Ø6 × 3 mm pocket is reserved.
### 17.2 Heat load and bulkhead spreading [EST]
- Arms' commit gives rail powers, not losses. Estimated bay dissipation per side:
  - board logic 4 W;
  - 2 × RP40 losses at the ~25 W combined hand holding load, about 3.4 W;
  - 2 × D70 Elmo idle overhead about 6.6 W (3.3 W each);
  - **≈ 14 W continuous**, ~25 W at close bursts.
- **Spreading:** 7075-T6 k ≈ 130 W/m·K, section 120 × 12 mm, 0.10 m to the centre: R ≈ 0.53 K/W → 7 K across the bulkhead at 14 W.
- **Sinking:** bulkhead heat capacity 0.60 kg × 960 J/kg·K ≈ 576 J/K (τ ≈ 13 min). With bay-vent convection (h ≈ 10 W/m²K on ≈ 0.07 m² exposed) → ≈ 0.7 W/K. Both bays (28 W) give a steady rise of ≈ 39 K, so **≈ 79 °C at 40 °C ambient**: below the 90 °C derate, thin.
- **Clamp:** one 400 J event adds +0.7 K (negligible). The 40 W repetitive fault-cycling case would push the bulkhead past 90 °C within minutes, so the clamp's resistor over-temperature cutout and the bay derate cover it. Normal clamp duty is about 0 W.
- **Rule:** if bay sensors read > 80 °C in walking tests, add a 40 mm duct branch from the Thor fan (Thermal to rule).
### 17.3 Vents (per bay, away from the Thor exhaust)
- **Inlet:** louvred shell panel on the lateral chest side, **y ±0.165, z ≈ +0.14 (below the shoulder line), 100 × 50 mm gross ≈ 50 cm² at 50 % open = 25 cm² free**.
- **Outlet:** shoulder-cap top-lateral, **y ±0.15, z ≈ +0.31, same size, 25 cm² free**.
- The Thor exhaust is upper back centre (|y| < 0.06), so the bay outlets sit ≥ 90 mm laterally from it and face up/out. The louvres point down at the inlet and up/out at the outlet (splash).
- Mass: the vents replace shell area (net ≈ 0); louvre inserts +0.010 kg/side [EST]. That is inside the shell's estimate tolerance, not booked.
### 17.4 Motor-lead pass-through
- 22 × SiF 0.25 mm² (OD ≈ 1.3 mm [EST]) → bundle ≈ 29 mm² copper+jacket. At 40 % fill that is a **Ø12 mm bundle → Ø16 mm hole with a snap-in nylon panel grommet** (Ø12 ID class; part to cite with the harness, Actuators).
- **Location:** in the bulkhead web, **75 mm below the shoulder axis**, outside the 120 mm boss.
  - Ligament to the nearest M8 hole on the 80 mm bolt circle: 75 − 40 − 4.5 − 8 = **22.5 mm ≥ 2d (18 mm)**, so the bolt circle and preload area are untouched.
  - Net-section loss there is 16/120 = 13 %, in a region at well under half the boss bending stress [EST]; FEA later (no FEA this round).
- The leads then run inside the shoulder_pitch hollow/service loop per Arms' D72 routing.
### 17.5 Records
- **O-T7 closed:** Controls applied `sim_torso_body_r1.json` (cd241d3).
- **BUS_SENSE_STATUS** (Electronics 413d80f): drive-side bus sense frame. Rule: the BMS host closes the FETs, and then the contactor, **only after a passing pre-check that agrees between both channels, within 30 ms** of the close command. Otherwise it aborts and latches the fault.
- **O-T5 plan (Controls):** 3–5 reference tasks are timed into a task timeline. That timeline will replace the 20/80 [EST] duty used in §13.5 for the mixed-runtime rating.

## 18. R1.6: R-069 mass-down, vents, O-T5 power
### 18.1 Savings. Cited (datasheet) vs [EST]
| item | Δ kg | evidence | status |
|---|---|---|---|
| LEV100A4ANG 190 g cited vs 0.200 booked | −0.010 | TE datasheet 6.7 oz / 190 g | **cited** |
| pre-charge HS50 47R → HS25 47R | −0.0125 | Arcol TI008 unit weights 25 → 12.5 g. Pulse: 159 J / 10.7 J·K⁻¹ = 15 K; 150 W peak = 6× rating < the 10× / 1 s point; energy 159 J < 250 J (10 × 25 W × 1 s) | **cited** |
| contactor LEV100 → **TE KILOVAC EV100** (100 A cont, 750 VDC max switching, economized 12 V coil, 130 g; https://www.evwest.com/support/ev100-specsheet.pdf) | −0.060 | datasheet 130 g vs 190 g | **cited mass, but coil hold 0.25 A × 12 V = 3.0 W** vs 1.5 W [EST] economized LEV100 → **+1.5 W breaks the +0.74 W walk margin**. Arbiter decision (or offset); not counted |
| PDB / pack-lead gauge | 0 | pack leads sit in the Actuators harness line; no torso-booked copper to resize | none |
| bulkhead 12 → 11 mm | — | side fall 690 N·m: Z = 0.12 × 0.011² / 6 = 2.42e-6 m³ → 285 MPa, **SF 1.76 < 2.0: fails**. Arms' forward-fall tuck (D71, T-030) does not change the side-fall case | stays 12 mm |
| pelvis/web pocketing | −0.15…−0.25 [EST] | needs FEA → `FEA_SPEC_torso_pocketing.md` (Bryan's PC) | [EST], not credited |
**Cited total: −0.0225 kg firm** (−0.0825 if the Arbiter accepts the EV100 +1.5 W), **against the 0.18 target: short.** The torso can't reach 0.18 on citations alone; pocketing after FEA is the main lever.
### 18.2 Bulkhead thermal with Arms' new losses (0.4 W idle, 3.6 W continuous at 30 N hold, ~9 W for < 0.7 s)
Both bays 7.2 W continuous → 7.2 / 0.7 W·K⁻¹ ≈ **10 K rise → ~50 °C at 40 °C ambient** (was 79 °C). The 9 W bursts are negligible against 576 J/K (≈ 0.01 K). Lots of margin to the 90 °C derate. Strength is unchanged: 12 mm is needed for side fall.
### 18.3 Vent fix
Shoulder-bay inlet: **top edge at z ≤ +0.155**. Panel 100 × 50 mm spans z +0.105…+0.155 at y ±0.165, still 25 cm² free. Note: Arms proposes moving the bay pad to the shoulder-cap shell; Torso keeps the bulkhead pad (no mass) until ID/Arms settle it.
### 18.4 O-T5 power column
Torso-side file `OT5_power_torso.md` (not edited in Controls' file). Runtime (typical / binned): T-A 3.83 / 3.75 h, T-B 3.32 / 3.25, T-C 2.84 / 2.78, T-D 3.92 / 3.83, **T-E 4.66 / 4.55 (only one ≥ 4 h)**.

## 19. R-071 (for the Arbiter): 2.5 mm² battery link vs fuse L50S125. **FAIL**
Sources:
- Littelfuse L50S datasheet (https://www.littelfuse.com/assetdocs/l50s-datasheet?assetguid=0b19c43c-f077-47b9-8fbc-bfe1d93a5592): L50S125 500 VAC / **450 VDC**, interrupting **20 kA DC**, melting I²t **1,290 A²s**, total clearing I²t **5,150 A²s at 20 kA / 450 VDC**.
- Molicel P45B: DCR < 15 mΩ (10 s), 13.5 mΩ DC at 50 % SoC.
- k factors for copper (IEC 60364-4-43 / -5-54 adiabatic): PVC 115, XLPE/EPR 143.
- Copper ρ 0.0172 Ω·mm²/m.
**(a) Fault I²t vs conductor withstand:** k²S² = 115² × 2.5² = **82,656 A²s** (PVC), 127,806 (XLPE), against fuse clearing **5,150 A²s** → **PASS ×16** at high fault current.
**(b) Prospective fault:** pack 20 × 15 mΩ / 5 = 60 mΩ, plus 1 m of 2.5 mm² (6.9 mΩ), plus FETs/contactor/busbars ~5 mΩ [EST] → **I_f ≈ 84 / 0.072 ≈ 1.17 kA (9.4 × In)**.
- The conductor withstands this for 82,656 / 1.17k² = **60 ms** (PVC) / 93 ms (XLPE).
- At 9.4 × In the fuse is not in its current-limiting region. Clearing time must be read from the L50S125 time-current curve (graph, not read). High-speed fuses at ~10 × In are typically ≤ 20 ms [EST], so the result is **conditional on the curve**.
**(c) Ampacity and overload coordination:**
- 2.5 mm² continuous rating ≈ 24–32 A for PVC (IEC 60364-5-52 [EST range]), ~40–50 A for silicone.
- 60 A continuous (R1.3 contract): **FAIL** (≥ 1.2–2.5 × overloaded).
- 100 A for 2 s: I²t 20,000 < 82,656 → PASS adiabatically.
- 2 h walking mean 712 W / 72 V = **9.9 A: PASS**.
- **Overload coordination** (I_b ≤ I_n ≤ I_z): the 125 A fuse cannot protect a ~30 A conductor. A 40–125 A overload (e.g. a stalled limb) would cook the link before the fuse acts → **FAIL**.
**Verdict: FAIL for the main battery link.** 2.5 mm² is acceptable only for a branch with its own ≤ 30 A fuse. The main link needs **≥ 10 mm² for 60 A continuous** (≈ 0.09 kg/m copper vs 0.022 kg/m for 2.5 mm²) [IEC 60364-5-52 EST], or the contract continuous current has to drop.
**O-T4 closed:** 84 V DC ≤ 450 VDC rating, and 1.17 kA prospective ≤ 20 kA DC interrupting (Littelfuse datasheet). Clearing time at 1.17 kA is still to read from the curve (moved to O-T8).
**Mass-down asks:** Arbiter ≥ 0.08 kg; Robot Lab ≥ 0.18 kg. Torso cited so far −0.0225 kg (§18.1), or −0.0825 with the EV100 +1.5 W ruling. That meets neither firm; with the EV100 it meets the Arbiter's 0.08.

## 20. R-074 follow-ups, T-031, SELV note
**R-074 recorded:**
- The main battery link stays ≥ 10 mm²; 2.5 mm² only on branches fused at ≤ 30 A.
- −0.0225 kg accepted: HS25 47R pre-charge and the LEV100 at its cited 190 g are applied. **Torso line 5.026 → 5.0035 kg.**
- Pocketing FEA approved, queued on Bryan's PC after Legs' L47 and the pad case.

**EV100: dropped.** Its datasheet coil is already economized: average hold 0.25 A at 12 V = **3.0 W** (0.15 A at 24 V = 3.6 W), no lower-hold variant listed (https://www.evwest.com/support/ev100-specsheet.pdf). Net +1.5 W over the 1.5 W booking > the +0.74 W margin. No cited path, so LEV100A4ANG + economizer stays.

**Fuse clearing at ~1.17 kA:** from the L50S time-current curves (datasheet p.5, https://catalogue2.pss-electrocomponents.com/catalogue/473/L50S125.V.pdf), read from the graph:
- The 125 A curve's knee is at ~700 A / ~5 ms. At 1.17 kA, **pre-arc ≈ 3 ms**. Total clearing ≲ 6 ms [EST ×2 for arcing at 84 V DC].
- Conductor adiabatic withstand at 1.17 kA:
  | conductor | withstand | margin vs 6 ms |
  |---|---|---|
  | 10 mm² PVC | 115² × 10² / 1.17k² = **966 ms** | ×160 |
  | 2.5 mm² PVC | **60 ms** | ×10 |
  | 2.5 mm² XLPE | **93 ms** | ×15 |
- **Caveat:** below ~700 A (e.g. a higher-resistance fault) the 125 A fuse sits on its vertical segment, 0.06–5 s. 2.5 mm² at 650 A withstands only 0.2 s, so it is protected only with its own ≤ 30 A fuse (R-074 rule). 10 mm² at 650 A withstands 3.1 s: OK down to ~600 A. **O-T8 fuse-clearing item CLOSED** for the 10 mm² main link.

**T-031 chest contact:** `T031_chest_contact.md`.
- Bare 2 mm CF shell k ≈ 46 kN/m, ζ 0.02, damage at ≤ ~10 mm / 1–1.5 kN [EST]: **FAIL**.
- Fix: HexWeb CR III 5052 4.5 pcf pad 100 × 105 × 76 mm. Plateau 20.7–24.4 kN over 53 mm (≤ 15°).
- **+0.078 kg → Arbiter request** (freeze).

**SELV:** the pack bus is **not SELV**. It runs 68–84 V, up to 92 V in regen (> 60 V DC SELV limit). Insulation, touch protection, connectors and service rules must be treated as hazardous-voltage. Sent to the Arbiter by Materials for R-075.

## 21. R-076 (binding): reinforced isolation, IP2X, 92 V creepage/clearance on the pack/drive bus
### 21.1 Connectors
Amphenol SurLok Plus (IC-10 datasheet: https://amphenol-industrial.com/wp-content/uploads/2024/04/surlok-plus-series-ic-10.pdf): touch-proof **IPXXB (IP2X)**, 1000 V DC, IP67 mated, UL94 V-0, ≥ 100 cycles, keyed.
| interface | part | rating (datasheet) | note |
|---|---|---|---|
| pack → PDB main (+/−) | **SurLok Plus 5.7 mm** crimp plug + panel receptacle | 100 A on 16 mm², 120 A on 25 mm², 1000 V DC | The 5.7 mm crimp starts at **16 mm²**, so the main link becomes 16 mm² (≥ 10 mm², R-074): ~+0.04 kg in the harness line (Actuators) [EST length 0.8 m]. 60 A cont / 100 A 2 s inside rating |
| PDB → limb bus outputs through the bulkhead (2 legs, 2 arms, waist) | **SurLok Plus 3.6 mm** panel receptacles | 50–70 A, 1000 V DC, IPXXB | limb peak 2.25 kW / 68 V = 33 A ≤ 50 A; branches fused per R-074 |
| pack blind-mate on rails | SurLok Plus 5.7 mm on a ±1.5 mm floating mount [EST] | | SurLok is a latching connector, not blind-mate rated → **O-T12**: cite a true IPXXB blind-mate ≥ 100 A |
Connector masses are not in the datasheet extract. [EST] ≈ 0.29 kg total, of which ~0.10 replaces existing connector allowances (pack BMS/fuse/connector 0.30, PDB 0.25). **Net ≈ +0.19 kg [EST]: over 0.02 → flagged to the Arbiter**, to be booked only once the masses are cited.
### 21.2 PCB creepage / clearance for 92 V (IEC 60664-1, PD2, reinforced)
Working voltage 92 V DC → 100 V row.
- **Creepage:** Table F.4, PD2, material group III → basic 1.4 mm → **reinforced 2.8 mm** (≈ 1.5 mm with CTI ≥ 600 laminate).
- **Clearance:** battery system, no mains transients. Basic ≈ 0.2 mm; reinforced takes the next impulse step, ≈ 0.5 mm → **design rule 1.5 mm**.
- These table values are as recalled; verify against IEC 60664-1 F.2/F.4 before release (**O-T13**).
- **Rule:** ≥ 2.8 mm creepage and ≥ 1.5 mm clearance between the 92 V bus and SELV nets (CAN, FAULT_N, 5 V aux, 48V_BRAIN). All barrier parts (isolators, optos, DCM) must be reinforced-rated.
### 21.3 Shrouds
Moulded PC shrouds / terminal boots (IP2X) on: HS100 clamp resistor terminals, LEV100A4ANG terminals, L50S125 fuse lugs, and busbars (heat-shrink + PC cover). [EST] 4 × 0.005 = **0.020 kg**, at the freeze threshold; booked together with 21.1.
### 21.4 T-031
Delivered (`T031_chest_contact.md`, 138a3a0); +0.078 kg Arbiter request pending.

## 22. R-079 (recorded) and touch-protection redo
**R-079:**
- Chest pad accepted at +0.078 kg; fuse item closed.
- The Arbiter booked +0.21 (connectors) and +0.04 (16 mm² link) conservatively until cited masses arrive.
- Projected total ~0.13 kg over 66.5 → **pocketing FEA high priority**. `FEA_SPEC_torso_pocketing.md` is completed (software, material, BCs, mesh, pass criteria, deliverables): **ready to run** on Bryan's PC.

**Connectors (replaces SurLok; coordinated with Electronics' audit, MR30/XT30U drive tees and AS150U pack main at 500 V DC):**
| interface | part | rating | mass (cited) |
|---|---|---|---|
| pack main **and** rail blind-mate (one connector) | **Anderson SBS75X** pair (genderless, 2 power + 4 aux, brown 96 V key code), on a floating rail mount with guide pins | UL 110 A / CSA 75 A on 6 AWG, wire 1.3–13.3 mm² (10 mm² OK), 600 V AC/DC, **IP20 finger-proof (IEC 60529, UL 1977 §10.2)**, hot-plug, 10 000 cycles (Anderson SBS datasheet) | housing **22 g each** (PEI-Genesis SBS75XBLK-BK) → **0.044**; power contacts 1339G-series 4 × ~5 g [EST] = 0.020 |
| aux pins | the same SBS75X aux positions for pre-charge sense / HVIL / FAULT_N loop | 20 A, mate-last break-first | in housing |
| PDB → limb buses | **no bulkhead connectors**. Bolted/soldered PDB terminals inside an IP2X enclosure (shell + PC covers), with grommeted pass-throughs. Serviceability at Electronics' drive tees | IP2X by enclosure | covers in shrouds below |
| shrouds / covers (clamp, contactor, fuse, busbars, PDB) | moulded PC | IP2X | [EST] 0.025 |
- **Main link stays 10 mm²**: SBS75X takes up to 13.3 mm², which releases the +0.04 harness booking.
- **AS150U:** Electronics' pack-main choice has no cited IP2X rating. Torso proposes SBS75X for the pack/rail interface; Electronics to confirm or cite AS150U finger-safety.
- **O-T12 closed:** SBS75X is a genderless panel/PCB-capable, hot-plug, finger-proof connector, used with a floating mount + guide pins for blind mating [the float mount is EST design].
- **Net vs the +0.25 booked:** cited 0.044; with [EST] contacts 0.020 and covers 0.025 → **0.089 kg**. ~~Net −0.161 kg~~ **Corrected per R-084: touch protection totals 0.175 kg (incl. Electronics' 0.086 guards), so the net is +0.005 kg vs the 0.25 booking.**

**T-031 rev 2** (`T031_chest_contact_r2.md`):
- Face 98 × 98 mm, ceiling 22.35 kN (≤ 23); band 17.7–22.3 kN at 0°, 16.6–20.8 kN at 15°.
- Stroke 62 mm, thickness 88 mm, core 0.061 kg.
- Backing: CF/Al-honeycomb sandwich 0.070 kg, 24 MN/m (45× the pad), SF ≈ 2 at 1.5× load.
- Total 0.131 → **+0.053 vs 0.078 accepted → Arbiter request**. Alternative: back the pad on a stiff pack-enclosure cap (O-T14).

## 23. R-084 and O-T14
**R-084 recorded:**
- O-T12 closed with the SBS75X; main link stays 10 mm².
- Touch protection 0.175 kg combined with Electronics' 0.086 guards → **net +0.005 kg vs 0.25** (§22 corrected).
- Chest backing +0.053 accepted.

**Part update (Electronics §18.2h, da124ae):** **Anderson PSBS75X** chemical-resistant PBT/PC housing (−40 °C), same 110 A / 600 V / IP20. Aux positions carry pre-charge sense and the FAULT_N loop.
- **Mass citation:** Anderson's own catalogue/datasheet publishes **no mass** (SBS datasheet checked).
- Distributor-cited: SBS75X PC housing **22 g** (PEI-Genesis SBS75XBLK-BK); contact **1339G3 3.81 g** each (Xecor, 0.268 oz per pair-pack).
- PSBS75X: same moulding in PBT/PC (density ~1.25 vs 1.20) → ~23 g [EST].
- For 10 mm² the contact is **1339G5** (8 AWG); its mass is not found, ~4.5 g [EST].
- **Pair:** 2 × 23 + 4 × 4.5 + 8 aux ~0.5 = **≈ 68 g** vs Electronics' 82 g clone figure. Delta vs AS150U 41.4 g: **+0.027 kg (vs +0.041 provisional, −0.014)**. Anderson-published mass is still missing.

**Bus-bar run needing an IP2X sleeve (Electronics §18.2f item 5), from the torso layout [EST until CAD]:**
| run | length per pole |
|---|---|
| pack connector (pack-bay front/top) → PDB | ~0.10 m |
| PDB → contactor | ~0.06 m |
| PDB → clamp (bulkhead, exhaust side) | ~0.17 m |
| fuse | **inside the pack enclosure** (pack line, IP2X by enclosure), no external run |
Total ≈ **0.33 m per pole, ≈ 0.66 m of sleeved bus (+ and −)**.

**O-T14 (pad backed on a stiffened pack-enclosure front): REJECTED; keep the 0.070 kg sandwich.**
- The pack front (CFRP 1.5 mm enclosure, §3) spans 0.22 m between rails.
- At 33.5 kN with a 98 mm patch: M = P(L/4 − c/8) = 1.43 kN·m.
- 7075 face 3 mm × 120 mm + ribs (cell gap limits rib depth to ~25–30 mm):
  | ribs | σ | SF | k | mass |
  |---|---|---|---|---|
  | 2 × 5 × 25 mm | 704 MPa | 0.71 | 13.6 MN/m | 0.38 kg |
  | 3 × 6 × 25 mm | 426 MPa | 1.18 | 20 MN/m | 0.50 kg |
  | 2 × 5 × 30 mm | 511 MPa | 0.99 | 22 MN/m | 0.41 kg |
- No rib layout reaches **SF ≥ 2** inside the depth available, and every one is ≥ 5× heavier than the sandwich. Stiffness (≥ 13.6 MN/m vs ≥ 5.3 needed) would pass.
- Cell intrusion: deflections of 1–3 mm need a ≥ 5 mm gap plus margin. SAE J2464 / UN 38.3 give crush/impact tests for packs/cells but no enclosure intrusion allowance (not fetched) → keep cells unloaded by design.
- **Net vs 0.053: no change** (the sandwich stays; rails/bulkhead path unchanged).

## 24. T-031 backing: three options compared (Materials c859e43)
| option | load path | check | mass | data | verdict |
|---|---|---|---|---|---|
| **A. Materials: machined 101 × 101 land on the 12 mm 7075 shoulder bulkhead + integral 60 × 6 mm back rib, 0.30 m span** | pad → bulkhead → shoulder/shell | 216 MPa at 24.4 kN → SF 2.3 (cited 7075). At our 22.35 kN ceiling: 198 MPa, SF 2.54; at 1.5 × ceiling (33.5 kN): 297 MPa, SF 1.69 on yield (passes the ×1.5 margin rule) | **+0.030** | cited | **RECOMMENDED** |
| B. our CF/Al-honeycomb sandwich 100 × 100 | 100 mm span, simply supported on two edges (shell frame / pack-bay rails) | 243 MPa at 33.5 kN, SF ≈ 2 vs [EST] CF 500 MPa; k 24 MN/m | 0.070 | CF values [EST] | superseded |
| C. stiffened pack-enclosure front (O-T14) | 0.22 m span to rails | SF ≤ 1.18 at 33.5 kN | ≥ 0.38 | cited 7075 | fails |
**Adopt A.** Chest pad total = core 0.061 + land 0.030 = **0.091 kg vs the 0.131 accepted → −0.040 kg returned to reserve.** A's stiffness: the bulkhead + rib is far stiffer than the pad's 0.53 MN/m [Materials to state k; 0.30 m span with rib ≫ 5.3 MN/m expected].
**Chest depth at the sternum (x):**
- Bulkhead front face x = +0.050, land +0.006 → +0.056.
- Core 88 mm → +0.144; CF/face 1 mm → +0.145; shell 2 mm → **shell skin x ≈ +0.147** (≥ +0.14 ✓).
- The base shell front was x = +0.11 (220 mm-deep box). So the sternum skin must move **~37 mm forward**: a local bulge ~110 × 110 mm over the pad (or chest depth 0.22 → ~0.257 m if ID prefers a smooth line). **ID impact:** V5 chest shell (row 4) front profile changes. Intake vents (low front) and shoulder-bay vents (lateral) unaffected.

## 25. R-087 (Electronics, Thermal bee2448): EtherCAT junction PCB on the partition's cold face
Torso frame = waist_pitch origin; x forward, y left, z up. Layout [EST until CAD]:
- Pack bay: x −0.082…+0.062, y ±0.110, lid at z = +0.2025.
- Duct partition: **horizontal CFRP plate at z = +0.235**, front half x −0.02…+0.10. Duct/Thor above; cold face below.
- Bus-bar runs (sleeved): pack connector → PDB → contactor, front, x ≥ +0.06, z +0.16…+0.20. PDB → clamp routed on the **right side (y ≈ −0.08)** to the clamp at (−0.07, 0, +0.25).

**Board (5 × Würth 7490140142 + branch connectors):**
- **Allowed outline:** x +0.000…+0.080, y −0.060…+0.060 (80 × 120 mm), mounted on the partition underside with **5 mm standoffs** → board plane z = +0.228.
- **Component height ≤ 12 mm downward** (to z ≥ +0.216), leaving **≥ 13 mm to the pack lid**. Room confirmed for the transformers + low-profile connectors; tall RJ45s are not allowed (use board-edge locking headers).
- **Mounting:** 4 × M3 at (x, y) = (+0.005, ±0.055) and (+0.075, ±0.055), z = +0.235, into partition inserts.
- **Keep-outs:**
  - x > +0.060 below z +0.21 (bus-bar zone), ≥ 15 mm vertical separation + PC cover;
  - y < −0.040 at x < +0.02 (PDB → clamp sleeved run below);
  - 2.8 mm creepage / 1.5 mm clearance from any 92 V part (R-076; the board is SELV).

**Cable route:**
1. **Thor → board:** GbE from Thor (≈ +0.03, 0, +0.29, in the duct) down through a grommet in the partition at **(−0.010, +0.050, +0.235)** (rear-left, away from the bus) to the board's rear-left edge.
2. **Branches from the board's rear edge:**
   - **legs ×2:** rear of the pack bay (x ≈ −0.09), down the left/right rear corners to the pelvis;
   - **waist:** rear centre down to waistY;
   - **left arm:** up the left side (y ≈ +0.12) to the left shoulder bay grommet;
   - **right arm:** up the right side (y ≈ −0.12). This is **the only crossing of a bus run (PDB → clamp, sleeved)**, done at **≥ 10 mm with a PC barrier**, at 90°.
3. No EtherCAT/STO run lies alongside any 92 V conductor; minimum parallel separation **≥ 20 mm** [EST rule].

**Sternum items, same layout:** T-031 pad on Materials' bulkhead land at z ≈ +0.22, shell skin x ≈ +0.147 (≈ 37 mm local bulge, ID). The board (x ≤ +0.08) sits behind and below the land with no conflict.

### 25.1 P-052 for RL Industrial Design: sternum pad, inserts, skin
- **Land** (Materials, on the 12 mm bulkhead front face x = +0.050): 101 × 101 mm, face at x = +0.056, centred (y, z) = (0, +0.220). The integral 60 × 6 mm back rib runs horizontally on the rear face at z +0.217…+0.223.
- **Pad footprint:** 98 × 98 mm, **centre (x, y, z) = (+0.100, 0, +0.220)** (mid-thickness of the 88 mm core); faces y −0.049…+0.049, z +0.171…+0.269, x +0.056…+0.144.
- **4 × M4 captive inserts** (bulkhead, from the front) at **(y, z) = (±0.040, +0.180) and (±0.040, +0.260)**, x = +0.056 face.
  - Edge distance to the land edge 10.5 mm ≥ 2d (8 mm).
  - Rib clearance 37 mm (rib at z 0.217–0.223).
  - Shoulder 80 mm bolt circles (centres y ±0.170, nearest bolt y ±0.130): ≥ 90 mm away.
  - Lead grommets (y ±0.170, z +0.145): ≥ 135 mm away. Partition ECAT grommet is on the partition, not the bulkhead.
  - The pad core gets 12 × 12 mm corner notches for the retention-frame screws [EST].
- **Final skin x:** land face +0.056 + core 0.088 + 1 mm CF face → +0.145; + 3 mm gap → +0.148; + PC plate 1.5 mm → **x ≈ +0.150** (base shell +0.11 → **40 mm proud** vs ID's 37 mm; ID either takes 40 mm or lets the gap go to 0 → +0.147).
- **PC plate [EST]:** thermoformed PC 1.5 mm (covers spec, 1.20 g/cm³), 120 × 120 mm face + ~37 mm sidewalls with 15 mm blend ≈ 0.0144 + 0.48 × 0.037 ≈ 0.032 m² → **≈ 0.058 kg**. It replaces a 120 × 120 cut-out of the 2 mm CF shell (≈ 0.045 kg) → **net ≈ +0.013 kg** [EST].

- **R-093 update (supersedes the PC plate, gap and skin x above):**
  - **Skin:** the pad face is the skin at **x ≈ +0.147, 37 mm proud**, no crush gap.
  - **Bezel:** 1.5 mm PC bezel ring (~15 g) on the same 4 × M4 inserts. The pad is bonded to the land; the bezel is the secondary hold.
  - **Flange:** overlap ≤ 4 mm, unclamped, on a 1 mm compliant gasket stand-off. The centre 90 × 90 mm stays free.
  - **Edges:** closed with a seal that is not bonded to the core walls.
  - **Face film:** 0.3–0.5 mm TPU/PC (~5 g).
  - **Service rule:** replace the pad if a dent is > 1 mm deep or it shows any crush.
  - **Mass:** net sternum ≈ **+0.020 kg**; delta vs ab432da ≈ **−0.038 kg**.

- **R-102:** lot acceptance 0° plateau ∈ [19.5, 22.3] kN (min 18.3 kN at 15° for 56.4 mm ≤ 62/1.1 at 1.03 kJ). Fallback core 95 mm (stroke ≈ 66.5 mm, +0.005 kg [EST]). Details in `T031_chest_contact_r2.md`. Mass +0.000.
- **R-095:** pad face 2K aliphatic PU UV clear 50–100 µm, matte/satin, masked off the edge and crush zone; visual + tap test after impact, replace the cartridge on impact. **+0.008 kg** → sternum net ≈ +0.028 kg.

## 7. Open questions / conflicts (not edited in others' files)
- **O-T1 (Electronics, coordination):** adopt the 48 V intermediate rail with DCM3623TA5N53B4T00; Torso hosts the DCM on the power distribution board or the brain tray? Mass 0.024 [UNVERIFIED for variant] stays in the brain line; who books the 47718-232 choke; 24 V VL source (O-E3); BMS→safety MCU CAN FD message set; e-stop = FET-open vs contactor (O-E6).
- **O-T2 (Actuators/Arbiter):** waist_pitch 116 N·m < 188 N·m need with T5 payload → TBM2G-08508A, +0.19 kg.
- **O-T3 (Electronics/Arbiter):** no mechanical contactor; FETs as disconnect needs a safety argument (welded-FET detection via BQ76200 diagnostics).
- **O-T4 CLOSED (§19):** L50S125 DC breaking capacity at 84 V and pack prospective short-circuit current (100 cells, ~15 mΩ/cell) to be verified.
- **O-T5 (Arbiter):** T7 4 h mixed is not met (2.92 h). Options: re-rate mixed duty, 20S6P (breaks T2), or idle-power cuts (compute cap). Ruling requested.
- **O-T6:** usable 90 % at 3.4 V/cell floor still [EST] (R-010); read P45B discharge curve at ~2 A/cell.
- **O-T8:** clamp: read HS200/HS100 overload curve for 400 J, cite comparator, gate driver, thermal cutout, sum drive bus capacitance for pre-charge; HS200 mass (0.475) vs Electronics estimate.
- **O-T9 (Electronics/Arbiter):** interlock exception for cell-at-risk faults.
- O-T12 CLOSED (§22).
- O-T14 CLOSED: rejected, sandwich kept (§23).
- **O-T12 (old):** cited IPXXB blind-mate pack connector ≥ 100 A, plus cited connector masses.
- **O-T13:** verify IEC 60664-1 table values; reinforced isolator parts.
- **O-T11:** T-031 pad stroke at 25° obliquity (68 mm needed vs 53 mm).
- **O-T10:** Sunon PF40281B1 static-pressure curve vs ~20 Pa vents+fins; fan PWM schedule.
- O-T2 approved on citation (§13.1); O-T3 → contactor (§13.2); O-T5 re-rate proposed (§13.5).
- O-T7: file delivered (§15.7); Controls to merge.
- **O-T7 (Legs/Controls):** sim torso 18.762 kg should be re-split (pack 8.75 in chest) when the sim is updated.

### 25.1a R-103 sternum mass reconciliation (2026-10-21)
| Line | Arbiter ledger | Physical [EST] | Note |
|---|---|---|---|
| R-093 P-052 plate | +0.058 | 0 (plate deleted) | replaced by package below |
| R-098 skin package (bezel 0.017, gasket, edge seal, TPU film, blend, 4 captive M4) | −0.009 (0.040 vs 0.058 at half credit) | +0.040 | |
| R-095 2K PU clear coat | +0.008 | +0.008 | |
| CF shell cut-out 120×120 (R-094) | not carried (withdrawn with R-094) | −0.045 | missing credit |
| **Total** | **+0.057** | **+0.003** | |
- Torso's earlier +0.028 is withdrawn. Its errors: (1) the ring at 0.015 instead of ID's 0.017, and the gasket, seal, blend and captives left out (undercount ≈0.013); (2) film and clear coat both counted, but R-098 makes them alternatives (double count 0.005); (3) the shell cut-out taken at full credit.
- **True number at ledger rules: +0.057 − 0.0225 (shell cut-out at half credit) = +0.0345 ≈ +0.035 kg.** No double count in the Arbiter's +0.057; it only lacks the shell credit. The film credit (−0.005) waits for a cited mass per R-098. Request to the Arbiter: carry +0.035, full credit to +0.003 once weighed.

### O-T5 CLOSED (2026-10-21)
Rated on the kitting duty cycle at **4.55 h**; no bigger pack.


### R-128 (9e49b7a) stock, grain and load-path classification (2026-10-21)
| Part | Stock | Grain | Path | Allowable (MPa) |
|---|---|---|---|---|
| Shoulder bulkhead, 12 mm web + 101×101 land + integral 60×6 rib (with posts) | 7075-T651 plate 3.0 in (76 mm) | L along y (span); LT/ST used | **single** (only chest→torso and shoulder→torso path) | **257** (ST 2.501–3.0 in; M8 flange clamp is through-thickness) |
| Pelvis incl. hip/waist hardpoint nodes | 7075-T651 plate 2.5 in (63.5 mm) | L along y | **single** (only legs↔torso path) | **271** (ST, through-thickness hip/waist bolts) |
| Waist ring | 7075-T651 plate 1.5 in [EST] | L along y | **single** (waist torque path) | **271** (ST, ≤2.0 in) |
| Pack rails + latch | 7075-T651 plate 0.75 in | L along x (rail axis) | multi (2 rails) | 320 |
| Partition | CFRP QI 1.0 mm | 0/±45/90 | multi / secondary | skin 300 [EST] |
| Torso shell | CFRP 2.0 mm | QI | multi / secondary | skin 300 [EST] |
| Sternum land inserts, EtherCAT bosses | in the bulkhead / partition | – | carried by the parent | parent |
- Applied in fea_job3.yaml/.py and fea_job3b.yaml as per-part allowables. The script refuses a single-path metal part without one. Drawings state stock and grain as above; if the drawing fixes grain L, the L value may be used only after the R-128 table is checked.

### Cover vents and Thor clearance (ID e874653 decisions, 2026-10-21)
- Width held at 340 at z 220 (ID). Shoulder-bay vents moved onto the sloped side panel (y ≈ ±141…±167). Slots are horizontal, 3.5 mm wide (≥3 mm), 6 mm pitch.
  - Inlet: z 105–155, 3 columns (x −60…60), 8 rows, **30.2 cm²/side**.
  - Outlet: z 160–214, 2 columns (x ±62…±102, clear of the Ø110 opening), 9 rows, **25.2 cm²/side**. Both meet A35 ≥25 cm² (projected; the true area on the slope is slightly larger).
  - IP2X: a 12 mm finger cannot enter a 3.5 mm slot; live parts are kept ≥80 mm behind the slots. Bays stay clear of the Thor exhaust (upper back).
- Thor plus A41 duct above z 265: |y| ≤ 101 (130 × 200 bay + 1 mm walls, orientation [EST]). The 45 mm chamfer is at |y| 125 at the top (z 310) and reaches |y| 101 only at z 334. **Clears, 24 mm margin; chamfer stays 45 mm.** Details in cad/torso_cover.json.

### D95 hip-pitch Elmo plates on the pelvis rear wall (Actuators 27afe00 / Legs L72), torso answers (2026-10-21)
- **Ownership:** the pelvis shell (model_v4 "pelvis shell 7075 4 mm", 170 × 370 × 104, global z 1126–1230) is in the **torso line** (R1 pelvis 1.45 kg; D95 table "Torso"). Torso owns the wall mounting.
- **Frame:** model_v4/site global = torso + (0, 0, 1280) mm. D95 z 1178 → torso **−102**; plates z 1136–1220 → torso −144…−60; pelvis top 1230 → −50.
1. **16 × M3 mounting:** rear wall is 4 mm 7075-T651. 7075 is too hard for self-clinching PEMs, so use **tapped M3 through-holes (4 mm engagement = 1.33 d)** with **G10 standoffs, no metal contact**, matching Thermal's binding rule for the knee.
   - Load per screw: 0.1 kg × 50 g / 4 ≈ 12 N, trivial.
   - R-128: the pelvis is single-path (271). Ø2.5 tap holes at Kt 3 in a low-stress region of the rear wall. The holes are added to the job 3 check scope.
   - Job 3 pelvis geometry is updated to the model_v4 shell (170 × 370 × 104 × 4) in fea_job3.yaml / 3b.
   - Clearance: plates are outboard (x −88…−114.5), so there is no conflict with the job 3 bulkhead, posts or partition, which are all at torso z ≥ 0.
2. **Rear wall ≤50 °C:** **no battery behind it.** The pack sits in the torso, model_v4 z ≈ 1340–1484 global (tb = waist pitch + 60), so it is 110 mm above the pelvis top. The regen clamp and DCM are on the bulkhead / Thor plate (torso z ≥ 140).
   - **Open:** the hip-yaw housings inside the pelvis (y ±130) face the rear wall's inner face. Thermal must confirm their skin is ≤50 °C, or add a low-ε shield on the wall's inner face (+0.005 kg [EST]).
3. **Rear cover x ≤ −117.5:** the torso cover ends at z 1330 global (torso 50), above the plates (≤1220), so it does not overlap. Nothing torso-owned lies at x < −85 in z 1126–1230. The pelvis-level skirt/bellows is ID's to clear at −117.5.
4. **Harness:** the pelvis is open top/bottom, so **no wall pass-through is needed.**
   - Drive feeds (bus pair plus EtherCAT/STO) come down the waist service loop, cross the open top behind the waist deck, and run down the outboard face to the plates in 2 P-clips per side on the wall's top edge.
   - Motor leads (0.45–0.6 m) go down outboard to the hip pitch motors through the yaw/roll service loop.
   - **R-076:** the bus pair goes in its own sleeved bundle (reinforced insulation). Signal (EtherCAT/STO) stays ≥20 mm from bus and phase conductors. Phase leads are treated as bus potential. No grommet, because there is no wall crossing.
   - If ID closes the pelvis top, use a Ø16 grommet pair at y ±183? No: the plates span to y 177, so a top-edge notch is used instead.

### Sternum stack update (ID 341ef4a, 2026-10-21)
The core is 116 mm (supersedes 88 and 100). Skin x +0.175, 65 mm proud of the cover. Ribbon L along z. A land socket wall (+0.006 [EST]) and PA66 bezel stand-offs (+0.004 [EST]) are proposed. Head clearance 69.8 mm against 68 needed: PASS. See R146_pack_shock.md §5.

### Pocketing credit pulled (2026-10-21)
Job 3 FAILED. All pocketing credit is withdrawn. P-148/P-149 are on hold; P-145/146/147/150 are independent and stand. Job 3c (closed boxes, T&R b1fe48f loads) is in DIAGNOSIS.md.

## Pack enclosure = job 3c bay box (Electronics 1a23584 §18.6 P-056, UL 2271:2023: OK on conditions), 2026-10-21
1. **Lid:** tool-removable (8 × M4 captive, Torx). Gasket: silicone sponge strip **Rogers BISCO HT-800** (closed-cell silicone foam, medium), 6 × 3 mm in a 2 mm-deep groove, perimeter 0.84 m. Volume 15.1 cm³ at ~0.35 g/cm³ [density EST, verify on the BISCO data sheet] = **0.005 kg**. Target IPX3 minimum (IP54 achievable). All openings (gland, vent, SBS75X cut-out) are IP3X or better.
2. **Vent/burst path** (single-cell failure, 20S5P P45B, 1.62 kWh):
   - **Gas per cell:** 4.5 Ah × 1.3–2.5 L/Ah = **5.9–11.3 L STP** (Koch et al. 2018, J. Power Sources, doi:10.1016/j.jpowsour.2018.07.051: mean 1.96, range 1.3–2.5 L/Ah, NMC at 100 % SOC). Hot gas at ~500 °C is ×2.6, so ≈ **29 L**, released over ~1–2 s [EST], peak ≈ 15–30 L/s.
   - **Box free volume:** interior 190 × 230 × 138 = 6.0 L, less cells 100 × 25.2 cm³ = 2.5 L, less holders/BMS/busbars ~1.1 L [EST] = **≈ 2.4 L**. Sealed, one cell would take the box to ≈ 5.7 bar abs, so a vent is mandatory.
   - **Part: GORE MultiVent all-in-one battery vent** (https://www.gore.com/products/battery-vents-multivent-series): opens at **50 mbar**, **50 L/s at 180 mbar**, reseals; IPX7/X8/X9K; 500 °C short-term; 77 × 55 × 22.5 mm; 3 × M5. Preliminary data; mass not published, **0.040 kg [EST]**. It is not UL 1989-listed (that standard covers standby batteries); UL 2271 enclosure compliance is via test.
   - At 30 L/s hot flow, Δp ∝ Q² gives a peak ≈ 180 × (30/50)² ≈ **65 mbar** (≤ 180 at 50 L/s). **Design burst/relief pressure 0.2 bar.**
   - **Vent hole Ø25 mm (4.9 cm²)** in the **rear web** at y 0, z 40 (low). Outlet faces rearward and down through the pelvis's open top/rear, away from the pad and the bulkhead, and never the lid or front web. Orifice check: A = Q / (Cd·√(2Δp/ρ)) = 0.05 / (0.6 × √(2 × 18000 / 0.5)) = 3.1 cm² ≤ 4.9 ✓.
   - **Walls at 0.2 bar:** lid 1.5 mm 7075, 186 × 224, σ ≈ 0.4 q b²/t² = **123 MPa ≤ 386 (fall) / 257**: PASS. Deflection ≈ 6 mm, so the gasket unloads only above the vent opening (1.5 mm at 50 mbar). Rear web 2 mm, b 138: 43 MPa, PASS.
   - The vent hole is ≥ 40 mm from every web/lid joint; the coarse peaks are at the front-web/lid/land junctions. Added to `fea_job3c.yaml` (bay_box.vent).
3. **Mounts off the failing joints:**
   - BMS board (BQ79616/S32K344) on the **rear web, z 60–120**.
   - FET/pre-charge board on the **left side wall, x −60…+20, z 40–110**.
   - Busbar blocks (2 × PA66-GF30 [EST 0.010 each]) on the **right side wall at mid-span**.
   - All on G10 standoffs (isolation), ≥ 30 mm from any web-lid or front-web joint and outside the land/sternum-box load path.
4. **Earthing:**
   - Box to the main ground terminal ≤ **0.1 Ω**.
   - 4 bond seats masked from anodize (chem film MIL-DTL-5541 Class 3 on the seats).
   - Lid bond strap: tinned Cu braid 6 mm², 80 mm (0.005 kg).
   - SBS75X mounting plate bonded to the box.
   - CAN through an EMC gland with **360° shield** termination (e.g. Lapp SKINTOP MS-SC-M M16, 0.015 kg [EST]).
5. **Isolation:** reinforced; **creepage ≥ 3.0 mm, clearance ≥ 1.5 mm** (R-076, IEC 60664-1, ≤ 92 V, PD2).
   - **OPEN:** Nomex 410 vs UL 2271 §8.3 (non-absorbent liner).
   - **Proposed alternative:** **ITW Formex GK-10** (0.25 mm flame-retardant PP, UL 94 V-0, non-hygroscopic) lining the box interior (0.20 m²): ≈ **0.051 kg** [density ~1.0 g/cm³ EST]. GK-17 (0.43 mm): 0.087 kg.

**Mass ledger (full):**

| Item | kg |
|---|---|
| Bay box + sternum box (job 3c mesh) | +1.43 |
| Less pack enclosure walls (pack line) | −0.75 |
| Less pack rails | −0.20 |
| Retained pack parts (Electronics, cited) | +0.076 |
| Lid gasket BISCO HT-800 | +0.005 |
| GORE MultiVent | +0.040 [EST] |
| Busbar blocks ×2 | +0.020 [EST] |
| EMC gland | +0.015 [EST] |
| Lid bond strap | +0.005 [EST] |
| Formex GK-10 liner | +0.051 [EST] |
| **Net** | **+0.692 kg** |

If the refined job 3c needs the 3 mm lid: +0.184 more (0.876).

**Geometry OPEN (found while doing this):** the job 3c box (torso z 0–140) and model_v4's pack envelope (185 × 220 × 144 at x −80.5…+104.5) do not line up in z. The pad core (x 56–172, z 171–269 torso) may intersect the pack's front-top corner (x ≤ 104.5). The box height must grow to hold the 144 mm pack (z1 ≥ 150 + gasket), and the land/core-to-pack clearance must be checked in model_v4 before the refined run (deflection gate: 1.5 mm + 2 mm).

## Option A pack notch: Torso cell-holder layout (P-057, 2026-10-21)
- **Layout:** cells vertical, 2 tiers (z 131.6–201.6 / 203.6–273.6), pitch 22 mm [EST, Electronics]. Each 5P group is 5 cells along y (half-row).
- **Front block, columns c3–c7:** x 39.2, 17.2, −4.8, −26.8, −48.8; cell block x −59.8…50.2. Columns c1/c2 (x 52–104.5) carry no cells: the notch sits at |y| < 54.5, and the outboard space holds the FET (left) and busbar blocks (right). Rear zone x −105…−60 holds the BMS on the rear web.
- **Notch depth: 2 tiers (100 mm), not ≤ 72.** The core z 171–269 cuts the lower tier (top at 201.6) by 30.6 mm. One tier would need the core raised ≥ 32 mm, but head clearance is only 69.8 against 68 needed, so that's out. **4 groups relocated (S17–S20), 20 cells.** Whole groups only.
- **Series path:**
  - T1 S1–S8, serpentine c3→c6, then up to T2 S9–S16 serpentine c6→c3.
  - **Link A** (12 mm², 0.19 m [EST]) runs from S16 to S17.
  - S17–S20 in c7 (the rear column of the block, facing the BMS).
  - **Link B** (12 mm², 0.19 m) runs from pack − at S1 (front-low) to the SBS75X.
  - The BQ79616 split stays at S10/S11 (a group boundary); NTCs move with their groups.
- **Taps:** 22 sense leads (2 × VC0–VC10); route lengths 72–269 mm [EST] (table in pack/).
- **SBS75X:** rear web at (−105, −60, 160), 147 mm from the floor vent (≥ 40 mm).
- **Vent:** floor at (−80, 80), outlet down into the pelvis open top.
- **Liner:** continuous around the notch re-entrant corner (socket walls, floor and land), ≥ 3.0 mm creepage and ≥ 1.5 mm clearance.
- **BQ79616 balance current:** **240 mA max** (internal CBFET; abs-max table, "max of 8 cells balancing at 75 °C ambient"), TI BQ79616-Q1 datasheet SLUSE14 Rev F (ti.com/lit/ds/symlink/bq79616-q1.pdf). I_CB = V_cell/(2·R_CB + R_DS(on)), per TI SLVAE87B §4.2. The voltage error from a 0.2 m tap at 240 mA is 3.3 mV, so measure with balancing paused.
- **COM:**
  - Pack Δ = **(−16.1, 0, +1.0) mm**, mass 8.80 kg.
  - Whole robot (65.809 kg credible): **(−2.2, 0, +0.1) mm**.
  - sim_torso_body_r1.json is updated (battery pos (−0.0261, 0, 0.111), 8.80 kg) for Controls.
- **Electronics to confirm:**
  1. The BQ79616 tap harness: 22 leads at 72–269 mm, VC0 for #2 at the S10/S11 split at c6 T2, routed under the liner.
  2. Links A/B at 12 mm² × 0.19 m, and link B replacing the 10 mm² front-low main run.
  3. The BMS board at the rear-web zone x −105…−95 (10 mm deep) with c7 35 mm forward, and the FET/busbar blocks moved to the c1/c2 outboard space.
  4. SBS75X position.
  5. Floor vent outlet into the pelvis.
