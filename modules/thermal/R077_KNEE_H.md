# R-077: is h ≥ 12 W/m²K justified for the finned knee (rev B) in walking carry? (RL Thermal, 2026-10-14)
Context: Controls shows knee rev B on the P-042 carry × 1.1 at **151 / 130 °C (η 0.7 / 1.0) at h 8**, passing only at h ≥ 12.
Rev C is withdrawn (Controls a5e14ff). Geometry: rev B axial fins, 1.0 mm 6061, gaps 6–8 mm, fin length along the flow L ≈ 42 mm, under the A35/A36 vents (knee rear fully open). Hand calc. Air properties at 50 °C: ν 1.8e-5, k 0.028, Pr 0.71.

## Flow sources at the knee
- **Walk 1.0 m/s, relative air at the knee:**
  - Stance: ≈ 1.0 m/s (knee moves with the body).
  - Swing: peak 2–3 m/s, ≈ 40 % of the cycle.
  - Mostly **cross-flow** to the axial fins, so only part of it enters the channels.
- **Vent duct flow:** ≈ 5 L/s at 1 m/s ram (A36). The fin-channel cross-section is ≈ 45–55 cm² (both housings), so U_channel ≈ 1.0 m/s if all of it goes through the fins. With 40–50 % bypass round the fin tips, **U_channel ≈ 0.5–0.7 m/s average**; ≈ 1.2–1.5 m/s in swing.
- **Channel convection:** developing laminar flow in 6–8 mm gaps. Re_Dh ≈ 400–900, Graetz x* ≈ 0.005–0.01, so it is entrance-dominated. Use the flat-plate mean, Nu_L = 0.664 Re_L^½ Pr^⅓, on L = 42 mm:

| U_channel m/s | 0.3 | 0.5 | 0.7 | 1.0 | 1.5 | 2.0 |
|---|---|---|---|---|---|---|
| h_conv W/m²K | 9.3 | 12.0 | 14.2 | 17.0 | 20.8 | 24.0 |

- **Radiation:** ε 0.85 anodised gives h_r ≈ 5–6 W/m²K on the *envelope*. The fins mostly see each other, and inside a vented cover they also see cover walls at ~45 °C. **Effective on total wetted area ≈ 1–1.5 W/m²K.**
- **Fin-array / cover penalty** (cross-flow entry, louvre losses, wake of the thigh): × 0.8 [EST].
- **Stand-still (no walking):** natural convection in vertical channels ≈ 4–5, plus radiation ≈ 1 ⇒ **h ≈ 5–6**.

## Result
| condition | h_conv × 0.8 + rad |
|---|---|
| poor ducting (U 0.3) | **≈ 8.5** |
| average walking carry (U 0.5–0.7) | **≈ 10.6–12.9** |
| good ducting (U 1.0) | ≈ 14.6 |
| swing peaks (U 1.5–2) | 18–20 |

- **Time-averaged over the gait at 1.0 m/s: h ≈ 11–13 W/m²K, central ≈ 12.** Defensible range **9–15**.
- **Verdict:** h ≥ 12 is **plausible as a central value but NOT defensible as a design floor.** The lower bound (≈ 9) sits near Controls' h 8 case. **Carry must be limited until h is measured.**

## What limits carry (rev B, drives off housing, η 0.7 worst / 1.0)
Lumped transient: knee housing + 2 motors C ≈ 900 J/K [EST], G = 0.6 + 0.07·h W/K ⇒ τ ≈ 13–15 min at h 8.

| start state | to 120 °C at h 8, η 1.0 (steady 130) | η 0.7 (steady 151) |
|---|---|---|
| from cold (35 °C) | ≈ 29 min | ≈ 17–20 min |
| after a long walk (≈ 87 °C) | ≈ 19 min | **≈ 11 min** |

**Recommendation (Controls/Arms):**
1. **Interim carry limit: ≤ 10 min continuous P-042 carry × 1.1**, then ≥ 10 min unloaded walking or standing.
   - Equivalent: **≤ 40 % carry duty** over a 30 min window (mean power gives ≤ 120 °C at h 8, η 0.7).
   - The P-043 winding-model derate at 120 °C remains the hard guard.
2. **Measure h** (G5): heated rev B housing in a vented cover, on the walking rig or in a 0.5–2 m/s tunnel. If it is ≥ 12, lift the limit.
3. **Fan option** (only if continuous carry is required and h < 12 is measured): a 40 × 40 × 10 mm 12 V axial blower per knee ducted along the fins.
   - ≈ 1.0–1.5 W, **≈ 15–25 g + 10 g duct per knee**.
   - h ≈ 30–40 (Actuators' fan case 77/90 °C).
   - Robot cost: +0.05–0.07 kg and +2–3 W. Fan MTBF and ingress (IP54+) need review.
4. Rev B fins and the knee venting (A35/A36) stay. Do not close covers.
