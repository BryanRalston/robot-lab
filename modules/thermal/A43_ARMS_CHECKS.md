# A43 Arms checks (RL Thermal, 2026-10-14): shoulder_pitch band and cap; hand 80 W bursts
Inputs: P-042 (7f71f86 basis; chest-carry pose), R-035 (40 W continuous hand cap, ≤ 1 s 80 W peak if Thermal confirms the duty, A43). Model: D68 (T-dependent R and Kt, η 0.84) with limits from `D69_KNEE_CHECK.md` §5: abs 155 °C, derate 130→145 °C, target ≤ 120 °C. Ambient 40 °C, walking airflow. Script `thermal/a43_arms.py` → `results/a43_arms.json`. The two-node capacitances are [EST] (as in O-A2) until the G5 bench measures them.

## 1. Shoulder_pitch TBM2G-07608C + CSG-25-100
**Continuous 47–54 N·m: YES, OK.**
| output N·m | steady winding °C, h nominal | h −30 % | h +30 % |
|---|---|---|---|
| 43.45 (P-042 pose) | 74 | 82 | 69 |
| 47 | 81 | 91 | 75 |
| 50.2 | 88 | 101 | 82 |
| **54** | **99** | **116** | 90 |
| 55 | 102 | 121 | 93 |
| 61.3 | 126 | 159 | 112 |
At 54 N·m the winding stays under the 120 °C target with 21 K margin, or 4 K at h −30 %. It is 31 K below the 130 °C trip.

**≤ 10 min above 55 N·m, starting from steady at 54 N·m: YES at 55 and 61.3 N·m. NO as a blanket cap up to peak torque.**
| torque | winding after 10 min | time to 120 / 130 / 155 °C |
|---|---|---|
| 55 | 100 °C | never within 10 min |
| 61.3 | 112 °C | never within 10 min |
| 80 | 169 °C | 1.6 / 2.7 / 6.7 min |
| 100 | runaway | 0.7 / 1.05 / 2.0 min |
| 120 | runaway | 0.4 / 0.6 / 1.1 min |
| 167 (peak) | runaway | 11 s / 16 s / 28 s |
**Corrected cap (replaces "≤ 10 min above 55"):**
- ≤ 55 N·m: unlimited.
- 55–62 N·m: ≤ 10 min.
- 62–80 N·m: ≤ 2 min.
- 80–100 N·m: ≤ 45 s.
- 100–167 N·m (peak): ≤ 10 s.
- After any capped interval, return to ≤ 54 N·m for at least the same time (the housing time constant is about 40 min).
- The PT1000 derate at 130 °C (P-043) is the backstop and always wins. These times keep the winding at or below 130 °C from a 99 °C start.

## 2. Hand motors and the wrist DC-DC: 80 W bursts ≤ 1 s, one grasp per 5 s
Parts:
- Hand motors (`arms/R1_ARCHITECTURE.md`, maxon catalog pages in `actuators/datasheets/`):
  - **DCX 22 S 24 V** (6 flexors): R 3.69 Ω, I_nom 0.869 A, R_th 7 + 16 K/W, τ_winding 20 s, τ_motor 528 s, max winding 125 °C.
  - **DCX 16 S** (5 small): 24 V winding assumed [EST]: R 19.2 Ω, I_nom 0.299 A, R_th 9.9 + 23.5 K/W, τ_w 9.6 s, τ_m 227 s, max 100 °C.
- Converter: **RECOM RP40-11024SFR** 24 V / 1.67 A (40 W), 90 % (`electronics/R1_ARCHITECTURE.md` §10.5). RP40-FR datasheet: **overload protection 150 % I_out typ., hiccup mode**; full load without derating to 60 °C ambient; max case 105 °C.
- At constant 24 V, 80 W means 3.33 A total. Total copper ∝ I², so about **4×** the copper at 40 W.

**Motors: YES, as long as the hand node also caps current per motor.** Continuous current at 40 °C ambient: DCX22 0.80 A, DCX16 0.27 A. With a 1 s burst in a 5 s period (duty 0.2), the burst current may be up to I_cont/√0.2. Conservative: assumes the motor carries nothing between grasps.
| motor | max burst current, 1 s in 5 s | winding rise in the 1 s burst | at 3.33 A in one motor |
|---|---|---|---|
| DCX22 (flexor) | **≤ 1.79 A** (1.67 A → min period 4.3 s) | +4.6 K at 1.67 A | +18 K per burst, needs ≥ 17 s period |
| DCX16 (small) | **≤ 0.60 A** (0.56 A → min period 4.4 s) | +8 K at 0.56 A | not allowed (+71 K at 1.67 A) |
An 80 W close spread over the 6 flexors is ~0.56 A each, which is under even the continuous limit. So the motors take it with no duty limit. The limit only matters if the firmware lets current pile into one motor.

**Converter: NO. The RP40-11024SFR cannot supply 80 W.** 80 W is 200 % of rated, above the 150 % typ. overload point, so the converter enters hiccup and the hand browns out during the grasp. Thermal is not the limit: a 1 s burst averages ≤ 48 W over 5 s and adds only ~9 J of loss. The electrical overload trip is.
- Allowed on this part: bursts **≤ 52 W (1.3× rated, kept below the 150 % typ. trip with margin) for ≤ 1 s, period ≥ 5 s**, average ≤ 40 W.
- To get 80 W: Electronics must cite a converter rated for ≥ 80 W peak (≥ 60 W continuous) that fits the forearm. Or use two RP40-11024SFR per hand, one for the flexors and one for the small drives: +0.043 kg per hand, same family and filter.
- A hold-up capacitor is not practical: 40 J at 24 → 20 V needs ~0.45 F, far above the RP40's 1300 µF max capacitive load.

**Safe duty limit (what the firmware should enforce):**
- Total hand current ≤ 2.17 A (52 W) for ≤ 1 s, then ≤ 1.67 A.
- At most one burst per 5 s.
- 1 s rolling average ≤ 40 W.
- Per motor: DCX22 ≤ 1.79 A burst / 0.80 A rms; DCX16 ≤ 0.60 A burst / 0.27 A rms.
- With an ≥ 80 W converter, the same per-motor limits and 1 s / 5 s apply at 3.33 A total.
