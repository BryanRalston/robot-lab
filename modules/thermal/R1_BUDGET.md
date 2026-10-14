# RL Thermal R1: whole-robot heat budget, 1.0 m/s walk + 20 kg carry (2026-10-14)
Owner: RL Thermal (2ae2d096). Script: `thermal/r1_budget.py` → `thermal/results/r1_budget.json`. Every number below reproduces from it.
Scope: steady-state dissipation per component at ambient 25 °C and 35 °C, with the limbs open and covered by PC 1.5 mm panels (R-027; trimmed set R-029: front/outboard fairings, P-022 knee cap, P-023 hip skirt, P-025 ankle boot). It also checks the thigh-clamp bondline limit of ≤ 60 °C (`legs/BOND_SPEC.md`). This is a lumped hand-calc network, not FEA or CFD, so **G3 thermal stays NOT MET**.

## Revision D68 (2026-10-14, Actuators ded9c2d): leg joint margins with temperature-dependent R and Kt vs a 155 °C limit
Script `thermal/d68_rerun.py`. Copper is re-solved at the winding temperature: P(T) = P25·R(T)/R25·(Kt25/Kt(T))², R(T) = R25·(234.5+T)/259.5, Kt25 = Kt155/0.89. This replaces the constant ×1.4. Windings (sizing.json): hip_yaw/hip_roll A, hip_pitch/knee/ankle D. Network and losses otherwise as §3. The limit is now **155 °C (TBM2G rated)**, with an **advisory derate trip at 120–130 °C**. The HD η stays at 0.75 on hip_yaw/roll, which is conservative vs D68's 0.84.
| joint (worst side) | open 25 °C | open 35 °C | covered 25 °C | covered 35 °C | verdict vs 155 °C |
|---|---|---|---|---|---|
| R hip_pitch | 121 | 138 | runaway (>155) | runaway | **open PASS (17 K margin), above advisory trip at 35 °C; covered FAIL** |
| L knee | 116 | 133 | runaway (>155) | runaway | **open PASS (22 K), covered FAIL** |
| L ankle | 74 | 86 | 104 | 118 | PASS both |
| hip_roll / hip_yaw | ≤ 46 | ≤ 57 | ≤ 52 | ≤ 64 | PASS both |
With R tracking temperature, closed PC covers over hip_pitch/knee push the windings into thermal runaway, not just over the limit. So P-026 (no closed PC) is now firmer. Open-air margins are larger than R0's 130 °C basis suggested, but at 35 °C hip_pitch and knee sit above the 120–130 °C advisory trip, so Controls would derate during sustained carry unless the A35 vents reach h ≥ 15. The bondline verdict is unchanged: the case is still about +60 K, which fails 60 °C without the P-027 thermal break. Arm hold: see `O-A2_ARM_HOLD.md` (D68 revision).

## 1. Inputs and sources
| input | value | source |
|---|---|---|
| gait | 20 kg carry, 1.0 m/s, steady window 1.8–7.0 s | `legs/results/r4/carry_20kg_1p0.npz` (R-014) |
| leg loss model | copper with R_cu ×1.4 hot; iron a·krpm + b·krpm²; drive 28 W at 49.5 A (I² + I split) | `actuators/regen_core.py`, `results/iron_loss.json`, `results/sizing.json` |
| ankle | differential pair: each motor = (pitch ± roll)/2 in torque and pitch ± roll in speed | Thermal (avoids double-counting iron loss) |
| winding→case / case→air | 0.6 × R_th (TBM2G) / h 12 W/m²K × fin factor 2 × CAD housing area | `v3/analysis/parts.py`, `actuators/size.py` (same rule) |
| arm hold | shoulder_pitch 61 N·m, elbow 40 N·m per arm (static, 20 kg); TBM2G-07608C/CSG-25-100 and TBM2G-05013C/CSG-20-100; η 0.75 | `arms/R1_ARCHITECTURE.md`, v3 |
| Thor T5000 | 120 W (module 40–130 W) | R-021, CONTRACTS §3, `electronics/R1_ARCHITECTURE.md` |
| sensors / drive idle | 40 W / 26 × 3.3 W | CONTRACTS §3 / `sizing.md` |
| brain DC-DC | Vicor DCM3623TA5N53B4 (43–154 V → 48 V, 240 W, Electronics A11 proposal; the booked x75H26C2 cannot take a 68–84 V input). η 0.92 **[EST]** | `electronics/R1_ARCHITECTURE.md` (O-E7: efficiency not read yet) |
| head DC-DC | RECOM RP40-11012SFR/P-HC, η 90.5 %; load 12 W **[EST]** | `head/BOM.md` |
| pack | 20S5P Molicel P45B, 15 mΩ/cell DC → 60 mΩ (×1.5 at end of discharge); cell discharge limit 60 °C | `actuators/datasheets/molicel_p45b.txt` |
| bus power | regen_core with half regen credit, plus the arm hold | computed |

**[EST] thermal parameters (all untested):** cover cavity h_in 4 W/m²K; cover outer h 12 W/m²K over 1.5 × the covered housing area; 50 % of each housing under a cover; pack bay h_in 4 W/m²K and c_p 1000 J/kgK; Thor bay natural h 5 W/m²K; winding limit 130 °C (TBM2G T_c130 basis; the CONTRACTS rule ΔT ≤ 100 K at 40 °C allows 140 °C); PC continuous use ~115 °C; touch limit ~48 °C for plastics (ISO 13732-1 class, value not verified); Thor TTP max ~85 °C (not verified); arm housing cylinders 96×80 and 70×75 mm.

## 2. Heat budget (W dissipated, both sides)
| component | W | notes |
|---|---|---|
| leg motor copper (10 actuators, 18 motors) | **205.6** | hip_pitch 36/38, knee 37/34, ankle 15/13, hip_roll 12/11, hip_yaw 5/6 (L/R) |
| leg motor iron | 36.7 | 5–7 W each on hip_pitch, knee, ankle |
| leg drive conduction/switching | 49.2 | Gold Twitter, regen_core model |
| drive idle, 26 drives | 85.8 | |
| **arm hold copper** | **194.6** | elbow 59 W/arm, shoulder_pitch 38 W/arm |
| arm drive conduction | 22.9 | |
| neck/waist/other copper | 8.0 | v3 line |
| Jetson Thor | 120.0 | |
| sensors | 40.0 | |
| brain DCM loss | 13.9 | η [EST] |
| RP40 loss | 1.3 | |
| pack I²R | 11.2 (16.8 at end of discharge) | 13.7 A at 984 W bus |
| BMS | 3.0 [EST] | |
| **total** | **≈ 792 W** | bus draw 984 W (carry is not the T7 case: ~1.5 h on 1458 Wh) |

By zone: leg actuators ≈ 291 W, arms ≈ 218 W, torso electronics (Thor, DC-DCs, sensors, idle, pack) ≈ 275 W.

## 3. Steady-state temperatures (°C)
| node | ΔT open | 25 open | 35 open | ΔT covered | 25 cov | 35 cov | limit | verdict |
|---|---|---|---|---|---|---|---|---|
| R hip_pitch winding | 83.7 | 109 | 119 | 119.5 | 145 | **155** | 130 | open OK (11 K margin at 35); **covered FAIL** |
| L knee winding | 81.2 | 106 | 116 | 116.0 | 141 | **151** | 130 | open OK; **covered FAIL** |
| R hip_pitch case (bondline proxy) | 62.6 | **88** | **98** | 98.4 | 123 | 133 | bond 60 | **FAIL if coupled by conduction** (−28 / −38 K) |
| L ankle winding | 51.9 | 77 | 87 | 75.1 | 100 | 110 | 130 | OK |
| hip_roll / hip_yaw winding | ≤ 26 | ≤ 51 | ≤ 61 | ≤ 33 | ≤ 58 | ≤ 68 | 130 | OK |
| cover cavity air at hip_pitch/knee | — | — | — | ~58 | 83 | 93 | PC ~115 | PC OK (22 K margin at 35), but the cavity is what pushes the windings over the limit |
| cover outer skin at hip_pitch/knee | — | — | — | ~18 | 43 | **53** | touch ~48 | OK at 25; **FAIL at 35 (−5 K)** |
| **elbow winding (hold)** | 223 | 248 | 258 | — | — | — | 130 | **FAIL at steady state** |
| shoulder_pitch winding (hold) | 90 | 115 | 125 | — | — | — | 130 | OK, 5 K margin at 35 |
| Thor bay, natural convection | 306 | — | — | — | — | — | TTP ~85 | **FAIL: needs forced air** |
| pack after 2 h (τ 3.1 h) | 8.6 / 12.0 at end of discharge | 34 | 47 | — | — | — | 60 | OK (13 K margin) |

Worst case is 35 °C ambient, covered, hot copper. Not included: drive heat on the housing. If the drives bolt to the hip_pitch/knee housings, add ~10 W each, about +15 K on the case [EST].

## 4. Hot spots and fixes (ranked)
1. **Elbow hold during the 20 kg carry (59 W, 223 K).** The 40 N·m hold is far above the TBM2G-05013C continuous rating. Fixes:
   - (a) Arms: a carry pose with the forearm near vertical and the load close to the body. If elbow torque drops to ≤ 15 N·m, copper falls to ~8 W.
   - (b) Actuators: CSG-20-160 or a TBM2G-06013 frame.
   - (c) Controls: an I²t winding model with a hold time limit.
   - Bench the ≥ 5 min hold (O-A2). The motor's thermal mass helps short holds, which this model leaves out.
2. **hip_pitch/knee under the P-023 hip skirt, P-022 knee cap and thigh fairings (+35 K winding).** The covers turn a pass into a fail. Fixes:
   - (a) Louvred or perforated panels with ≥ 30 % open area over the fins (recommended, no added mass).
   - (b) A ≥ 5 mm standoff with top and bottom vents so walking airflow washes the fins.
   - (c) Use the R-029-allowed CF (or Al) for those panels and bond them to the housing as a spreader. Never closed PC over these two joints.
3. **Thigh-clamp bondline (case at 88–98 °C next to the collar; DP490 is only 4.75 MPa at 82 °C).** The collar may rise at most 35 K (25 °C ambient) or 25 K (35 °C) above ambient. Fixes:
   - A G10/PEEK thermal break (k ≈ 0.3) at every motor/lever-to-collar interface.
   - No metal path from the can flange to the collar.
   - Leave the collar uncovered.
   - Mount the drives off the housing.
   - Put a collar thermocouple on the G5 bench. Until it is measured, the cross pins are the hot-case retention (BOND_SPEC §1).
4. **Thor bay (120 W in a closed 130×200×40 bay).** Needs ducted forced air, ~21 CFM total for a 10 K air rise (e.g. 2 × 40 mm blowers, ~3 W, ~40 g [EST]), with intake low and exhaust high in the chest shell (V5 plan vents) and a fin stack on the cold plate. The alternative is heat pipes to an Al chest spreader. Keep the exhaust away from the pack. Mass comes from the torso thermal line (1.0 kg).
5. **Brain DCM (~14 W in a ChiP).** Mount it with TIM on the Thor cold plate or in the duct.
6. **Pack (11–17 W, +9–12 K in 2 h).** No action needed. Keep it sealed off from the Thor exhaust.

## 5. Proposed jobs (not run here; for Bryan's 'bryan' PC via Robot Lab, one job at a time)
- J-T1: conjugate CFD/thermal model of the thigh/hip zone at 1 m/s relative airflow, 35 °C. Includes the hip_pitch housing, collar with and without the G10 break, and the covers vented vs closed. Outputs: collar bondline temperature and winding temperature. It needs leg CAD and the cover CAD from ID.
- J-T2: torso chest-shell CFD for the Thor duct and fan sizing (fan curve vs vent area), with the pack bay alongside.
- J-T3: transient arm-hold model (winding + housing thermal mass) to set the hold time limit for the elbow and shoulder.

## 6. Open questions
- **Arms:** carry pose and hold duration (O-A2)? Is an elbow ≤ 15 N·m pose OK? Elbow motor or ratio change?
- **Actuators:** where do the drives mount? `size.py` ΔT leaves out iron loss (+5–7 W on hip_pitch/knee). Winding limit 130 or 140 °C?
- **Legs/Materials:** what is the conduction path from the hip_pitch can flange to the collar? Is a G10/PEEK thermal break structurally acceptable?
- **Industrial Design:** can the P-022/P-023 panels and thigh fairings be louvred, CF or standoff-vented (affects the A29 itemized JSON)?
- **Electronics / Torso & Power:** Thor power mode? DCM3623TA5N53B4 efficiency (O-E7)? Duct and fan space in the chest shell? Is the 3.3 W drive idle still right for the actual Twitter part (Electronics item 3)?
- **Controls:** a per-joint I²t winding model with derate. Suggested trip at 120 °C estimated winding temperature.
- **Test & Reliability:** collar, housing and cover thermocouples on the G5 bench; carry duty at 35 °C.

## 7. Limits
Lumped steady state, so the parts with thermal mass come out conservative. The h values are [EST]. The input is a gait-ID trace, not the forward sim. Arm duty is static only.
