# D69 knee check (RL Thermal, 2026-10-14): shank heat path, covers, drives, final winding limits
Input: Actuators D69 (f205f7b). The knee becomes 2× TBM2G-08513D plus a conductive path into the shank, modelled as R_case-air 1.44 → 0.72 K/W. Their result (1.2 m/s, 35 °C, 60 min): motors alone 122–128 °C, with the path 87–91 °C. Hand calcs only. J-T1 CFD and the G5 bench will confirm.

## 1. Is 0.72 K/W achievable? **Not with the bare tibia. Yes with a finned shank spreader.**
Needed added conductance: 1/0.72 − 1/1.44 = **0.69 W/K**. (D69 text says ≥ 1.2 W/K. That figure is wrong; the math gives 0.69.)
- **Shank wall:** tibia tube Ø45 × 1.2 mm 7075-T6 (`legs/results/r4/structure_m2.md`), k ≈ 130 W/mK [EST; MATERIALS_DB lists 7075 without k]. kA = 0.022 W·m/K.
- **Tube as a fin:** pad near the top, about 0.10 m of tube above and 0.30 m below [EST, no shank CAD].
  - h 12 (walking): m = 8.8 /m, G = 0.33 W/K → **R = 0.99 K/W**.
  - h 23 (swing-phase shank, Ø45 cylinder at ~2 m/s, Hilpert correlation): G = 0.49 → **R = 0.85 K/W**.
  - The 1.2 mm wall chokes the conduction, so a thicker pad can't fix this. **The bare tube does not reach 0.72.**
- **Interface:** bolted saddle pad 40×60 mm with gap pad 3 W/mK × 0.5 mm, 4× M4 at ≥ 2 kN preload each → ≈ 0.07 K/W. With a thin phase-change TIM ≈ 0.02 K/W. This is not the limiting resistance. Use a 7075 or 6061 saddle machined to the Ø45 OD. Do not drill the FEA'd tube: clamp it, as the collar does.
- **Design that meets it:** a 6061 finned saddle spreader about 100 mm long on the tibia below the knee housing, with ~10 axial fins (100×20×1.5 mm), **≥ 0.04 m² wetted area**. It must be exposed to the walking airflow. Computed R_case-air = **0.69 K/W at h 12** (0.59 at h 20), including the tube fin and pad. Mass ≈ **0.12 kg [EST]**, against D69's +0.03 booked, so **+0.09 kg goes to the Arbiter**. Legs owns the saddle on the tibia (no new holes in the tube).

## 2. Covered and vented cases (35 °C, knee Q ≈ 50 W back-solved from D69's two runs; winding-to-case ≈ 18 K)
| case | case °C | winding °C, no drives | winding °C, + 2×7 W drives on housing |
|---|---|---|---|
| D69 open with path (0.72) | 71 | 87–91 | 97–101 |
| **closed PC over housing and shank** (+35 K R1 penalty) | ~106 | **~125** | **~135** (above the derate trip, below 155) |
| closed PC over housing and shank, no path (0.08 kg saved) | — | 157–163 | **FAIL** |
| **A35 vents on the housing (h ≥ 15) + exposed shank spreader** | 64 | **~83** | **~90** |
Verdict: the path only works if the shank spreader stays in free air. Closed covers keep the winding under 155 °C but over the derate trip with drives, so P-026 stands (no closed PC). With A35 vents the knee has ~40 K margin to the design target.

## 3. Bondline
- **The shank bond is the tibia collar at the ankle-fork end** (`legs/DECISIONS.md` L6), about 0.3 m from the pad. Fin attenuation is 1/cosh(mL) = 0.14 (h 12) to 0.05 (h 23). Case rise is ~46 K with drives, so the collar rise is ≤ 6.6 K → **≈ 42 °C at 35 °C ambient. PASS (≤ 60 °C)**. Condition: the spreader stays ≥ 150 mm from the tibia collar and its exhaust doesn't wash the collar.
- **Thigh-clamp collar:** the knee path goes down into the shank. The knee pins have PTFE washers, which form a thermal break. No added heat. The hip_pitch side still needs P-027.
- The bond spec is written for the thigh collar. Legs should confirm the tibia collar uses the same DP490 spec and the 60 °C rule.

## 4. Knee drives bolted to the housing (2 × 7 W)
- **Impact:** +14 W × R. That is **+10 K** on the case and winding with the 0.72 path (+20 K at 1.44, +8 K with A35 vents). The drive baseplate then sits at the case temperature, **~81 °C at 35 °C ambient** with the path. That is close to a typical drive heatsink limit, **[EST]; Electronics to read the Gold Twitter max heatsink/ambient rating**.
- **Mitigation:** bolt both drives **to the shank spreader saddle**, not the motor housing. It is cooler (~60–65 °C) and it is the heat sink, so the motor windings don't see the drive heat directly. Use a thin TIM and keep the flat-heatsink face on the saddle. This keeps the spirit of my R1 recommendation: off the motor housing, onto a heat sink. On the knee, 'drives off housings' becomes **'drives on the shank spreader'**. hip_pitch is unchanged: drives off the housing (P-027).

## 5. Final winding limits (TBM2G, all Elmo-driven joints): proposed for P-029 / A40
| limit | value | use |
|---|---|---|
| absolute | **155 °C** (TBM2G rated) | never exceeded; hard torque-off at **150 °C** measured |
| derate trip | **130 °C** (PT1000, or the model estimate if higher) | linear torque derate 130 → 145 °C to the continuous rating |
| design target | **≤ 120 °C** at 35 °C ambient, sustained worst duty (1.2 m/s, or 1.0 m/s with 20 kg carry) | sizing/thermal acceptance; gives 10 K to trip and 35 K to abs |
- **PT1000 (option code A) endorsed on every TBM2G**, read by the drive and cross-checked by the Controls 2-node model. The elbow hold (O-A2) and hip_pitch at 35 °C open (138 °C, D68 rerun) currently exceed the design target, so those stay open actions (P-028, A35/A36).

## 6. Actions
- Legs: finned tibia saddle spreader (≥ 0.04 m², clamp-on, ≥ 150 mm from the tibia collar); confirm the tibia collar bond spec.
- Electronics: Gold Twitter max heatsink temperature; mount the knee drives on the spreader.
- Arbiter: +0.09 kg (spreader vs D69's 0.03 booking).
- ID (A36): leave the knee spreader and lower shank uncovered. Knee housing vents per A35.
- J-T1 CFD: add the shank spreader and the drive positions.
