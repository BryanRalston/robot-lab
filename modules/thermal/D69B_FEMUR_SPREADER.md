# D69B: knee heat sink on the femur via flexible straps (Actuators fbe0def): check and alternatives (RL Thermal, 2026-10-14)
Hand calcs, [EST] marked. Basis: `D69_KNEE_CHECK.md` (knee Q ≈ 50 W + 2 × 7 W drives on the housing, winding-to-case ≈ 18 K, housing alone 1.44 K/W). Femur: Ø50 × 1.2 mm 7050/7075 (`legs/results/r4/structure_m2.md`, L-210), k ≈ 157 W/mK [EST]. Thigh-clamp collar centred ~69 mm below the hip pivot (`legs/DECISIONS.md` L-158).

## 1. Series math: their ≥ 1.32 W/K is optimistic, because it leaves out the spreader and interfaces
Path: housing → interface (0.05 K/W [EST]) → 2 straps (G_s) → interface (0.05) → femur spreader (G_sp, fins + tube fin) → air. Added conductance needed for 0.72 K/W total: **0.69 W/K**.
| h W/m²K | spreader wetted area | G_sp W/K | G_s needed | total R at G_s 1.0 / 1.32 / 1.8 W/K |
|---|---|---|---|---|
| 12 | 0.04 m² (tibia design) | 0.80 | 10.9 | 0.89 / 0.86 / 0.82 |
| 12 | 0.08 m² | 1.21 | 1.95 | 0.82 / 0.78 / **0.73** |
| 20 | 0.04 m² | 1.24 | 1.88 | 0.82 / 0.77 / 0.73 |
| 20 | 0.06 m² | 1.58 | 1.42 | 0.79 / 0.73 / **0.68** |
Verdict:
- **h 12: FAIL.** No strap in the 1.0–1.8 W/K range reaches 0.72 with a realistic spreader. Best case is 0.73 with 0.08 m² of fins and 1.8 W/K.
- **h 20: marginal PASS.** It needs ≥ 0.06 m² of fins and ≥ 1.42 W/K, i.e. the top of the GFTS range.
- Their 1.32 / 1.16 numbers are only reached with an ideal spreader and zero interface resistance.

**But 0.72 K/W is more than needed.** For the ≤ 120 °C design target (D69 §5) at 35 °C ambient, with drives on the housing: R ≤ (120 − 35 − 18)/64 W = **1.05 K/W**. That means an added **0.26 W/K**, not 0.69. At 0.82–0.89 K/W every strap case above gives a winding of 104–110 °C. So the strap option passes the target, but the strap is not needed to pass it (see §3).

## 2. Femur spreader vs the thigh-clamp bondline (≤ 60 °C, already failing from hip_pitch)
- The path delivers ~32 W into the spreader, so the spreader runs at +25–40 K over ambient. The femur tube conducts that heat toward the collar. The tube acts as a fin with m ≈ 8.0 /m (h 12) to 10.3 /m (h 20).
- Spreader on the knee end, ~160 mm of tube from the collar: attenuation e^(−mL) = 0.28 (h 12) / 0.19 (h 20). **That adds +5 to +8 K at the collar**, on a joint that already fails. **Not acceptable.**
- Minimum distance for ≤ +0.5 K: L ≥ ln(ΔT_sp/0.5)/m ≈ **0.5 m at h 12**. That is longer than the femur, so **distance alone can't do it**.
- If the femur spreader is used anyway, a **thermal break is required:** mount the spreader on 4 PEEK/G10 standoffs (≥ 3 mm, ≤ 1 cm² each, so ≥ 30 K/W to the tube) so it sheds heat only to air and puts nothing into the tube. The strap lug then bolts to the spreader, not to the tube or clevis. You lose the tube-fin contribution (−0.15 W/K), so it needs ≥ 0.08 m² of fins. Collar impact ≈ 0.

## 3. Alternatives
| option | conductance added | meets 1.05 K/W (target) / 0.72 | bondline | mass per knee [EST] | risks |
|---|---|---|---|---|---|
| A. Femur spreader + 2 GFTS straps (fbe0def) | 0.3–0.7 W/K | yes / only at h 20 with best strap | needs PEEK isolation (above) | straps 0.12 + spreader 0.15 + standoffs 0.01 = **0.28** | strap flex life unrated (5.8e7 cycles), graphite debris (conductive FOD), cost $1–5k |
| A′. Copper braid instead of GFTS | 1.5–2 W/K | yes / yes at h 20 | same | **0.59** | mass |
| B. Heat path into the knee's thigh-side trunnion bracket | ~0.2–0.4 W/K through the trunnion bearings [EST] | marginal / no | puts heat straight into the femur near the knee clevis, so it needs isolation anyway | 0.03 | bearing grease temperature; poor and variable contact |
| **C. Bigger fins on the knee housing itself (6061 clip-on or machined, axial)** | needs 0.26 W/K (target): **+0.025 m² at h 12**; for 0.72: +0.068 m² (h 12) / +0.041 m² (h 20) | **yes / yes at h 20 with +0.041 m²** | **no femur or tibia heat at all** | **0.05 (target) to 0.12 (0.72 at h 12)** | envelope: fins move with the housing (swing vs tibia), so Actuators/Legs must check the clash sweep; drives stay on the housing as Electronics wants |
| D. Small fan on the housing (h ~40, D69) | large | yes (D69: 110–116 °C, motors alone) | none | 0.02 + 1–2 W | a moving part per knee, dust, failure means derate; needs a stall sensor |

## 4. Verdict and recommendation
- **fbe0def strap + femur spreader: FAIL at h 12 for 0.72 K/W. Marginal PASS at h 20** (≥ 0.06 m² fins, ≥ 1.42 W/K straps). As drawn it **fails the bondline rule** unless the spreader is isolated from the femur on PEEK standoffs.
- **Recommended: Option C, axial fins on the knee housing,** sized for the real requirement R ≤ 1.05 K/W (winding ≤ 120 °C with drives on the housing). That is ≥ 0.025 m² extra wetted area, **≈ 0.05 kg per knee (0.10 kg robot) [EST]**. Optional growth to 0.04–0.07 m² (≈ 0.08–0.12 kg/knee) if Actuators wants to keep the 0.72 basis. No strap, no flex-life risk, no heat into either bonded tube.
  - Compared with the 0.12 kg/knee D69 tibia spreader booked: **−0.07 kg/knee**.
  - Compared with option A: −0.23 kg/knee.
- Keep option D (fan) as the fallback if the fin envelope clashes.
- PT1000 derate (130 °C) remains the backstop. J-T1 CFD should model the finned housing in swing.

## 5. Strap flex-life bench requirement (only if option A/A′ is pursued)
- Sample: 3 straps per design, in production configuration (lugs, bolts, TIM), on a fixture reproducing the knee housing swing.
- Motion: **±8° (the measured 5.7–12.6° range + margin) about mid-position, at 2 Hz [EST gait rate], with strap temperature held at 90 °C**.
- Duration: **8.7e7 cycles (1.5 × 5.8e7 design life)**.
- Measure conductance every 1e7 cycles (ΔT at a fixed heater power). **Pass:** G ≥ 90 % of initial and ≥ the design value. No cracked or delaminated layers. **No conductive debris** (collect on a tape witness; graphite flake is an electronics FOD hazard).
- Also run 100 drop/fall shocks at 50 g [EST] mid-test (T8 falls).
- Failure of any sample means option A is rejected.
