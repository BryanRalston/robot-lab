# O-A2: arm hold transient for the 20 kg two-hand carry (RL Thermal, 2026-10-14)
Script: `thermal/oa2_arm_hold.py` → `thermal/results/oa2_arm_hold.json`. Lumped hand calc only, no CFD. Assigned to Arms as O-A2; feeds P-028/A39 (hold-time limit) and P-029/A40 (Controls winding model).

## Answer (40 °C ambient, walking airflow h = 12 W/m²K, continuous hold, minutes until the winding has risen 100 K)
| joint | hold torque | motor torque (N 100, η 0.75) vs T_c130 | copper W | steady winding rise | **time to +100 K (two-node)** | under 10 min? |
|---|---|---|---|---|---|---|
| shoulder_pitch (TBM2G-07608C + CSG-25-100) | 61.3 N·m | 0.82 vs 0.89 N·m | 38.4 | **91 K** | **never (steady rise is below 100 K)**; 57 min at h −30 % | **No** |
| elbow (TBM2G-05013C + CSG-20-100) | 40.1 N·m | 0.53 vs 0.38 N·m (**1.4× continuous**) | 59.5 | **224 K** | **3.6 min** | **Yes: under 10 min, about 4 min** |
The elbow fails. At 40.1 N·m it reaches +100 K (140 °C) in about 3.6 min and keeps climbing toward +224 K. Even with ideal gear efficiency (η 1.0, 33 W) it gets there in 17–23 min. The shoulder is marginal but holds indefinitely at nominal h. It has 9 K steady margin to 100 K, but only −1 K to the 130 °C T_c130 basis (+90 K at 40 °C).

## Sensitivity (h ±30 %, and η)
| case | shoulder steady ΔT / t100 | elbow steady ΔT / t100 (2-node) / t100 (1-node) |
|---|---|---|
| h −30 % (8.4) | 109 K / 57 min | 268 K / 3.6 min / 22 min |
| h nominal (12) | 91 K / never | 224 K / 3.6 min / 23 min |
| h +30 % (15.6) | 81 K / never | 200 K / 3.6 min / 24 min |
| η 1.0 (static hold, friction helps) | 46–61 K / never | 113–151 K / 17–23 min / 51–77 min |
The elbow's 2-node time barely depends on h. The winding outruns the housing: the winding-to-case resistance R_wh alone (P·R_wh = 121 K > 100 K) sets the time, so cooling the outside can't fix it. The 1-node model (motor + housing as one mass) is **non-conservative** for the elbow, so don't use it for limits.
Elbow at the P-028 pose (≤ 15 N·m): 8.3 W, steady about +31 K, so the hold is unlimited.

## Model and inputs
- Copper: P = (T/(N·η)/K_m,hot)². K_m from the TBM2G table in `v3/analysis/parts.py` (Kollmorgen TBM2G manual Rev B, §9), winding C: 07608 K_m 0.156, 05013 0.082 N·m/√W. Hot R ×1.4 → K_m/√1.4, held constant (conservative at the start, slightly optimistic near +100 K).
- η 0.75 forward for the CSG (v3 rule, `arms/R1_ARCHITECTURE.md`). Nominal is conservative for a static hold; η 1.0 is shown as the bound.
- Two-node: winding node C_w = motor mass × 460 J/kgK (stator + rotor, 0.236 / 0.149 kg, parts.py), connected through R_wh = 0.6 × R_th (TBM2G R_th 2.15 / 3.4 K/W, same rule as `actuators/size.py`) to the housing node. C_h = rest of the actuator: CSG set 0.40 / 0.22 kg steel [EST] plus the remainder as Al. The total actuator is 1.52 / 0.90 kg per `arms/R1_ARCHITECTURE.md`. The housing goes to air through R_ha = 1/(h × A × 2) (fin factor 2, as in size.py), with the housing taken as a cylinder of Ø96×80 / Ø70×75 mm **[EST]**.
- C_w includes the rotor, which only couples through the air gap. The real winding-only mass is smaller, so the 3.6 min may be **optimistic**. The TBM2G manual gives no thermal time constant, so bench it (G5).
- Limit used: +100 K at 40 °C (CONTRACTS thermal rule) = 140 °C; motor absolute limit 155 °C (TBM2G manual). The R1 basis of 130 °C is reached at +90 K: elbow ~3.2 min; shoulder steady 91 K just exceeds it.

## Recommendations
1. P-028 (Arms): the carry pose must keep the elbow ≤ 15 N·m, which is required, not optional. Otherwise the elbow needs about 2× continuous torque (a TBM2G-06013-class frame or CSG-20-160).
2. P-029 (Controls): give the elbow an I²t limit set by R_wh·C_w (τ_w ≈ 2.3 min), not the housing. Suggested: allow 40 N·m for ≤ 2 min, then derate to ≤ 28 N·m (= T_c130 continuous).
3. Shoulder: OK. Keep the shoulder housing uncovered (R-029 already defers the arm shells). Under a cover, use the A35 rules.
4. G5 bench: hold the elbow at 40 N·m with a thermistor (TBM2G option) to get the real τ_w.
