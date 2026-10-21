# Side-fall sim set (Controls, 2026-10-21) — T&R 3c73260 (S1/S2b/S2c) + rev B 3b4c449 (L39 hip-roll bumper)
`side_fall.py` → `side_fall_results.json` (all rows), `side_fall_hiproll_history.json` (hip-roll angle/rate + torso roll, 5 ms, 68 kg 550 N, base and damp). Light MuJoCo, sim/v3 + pads [EST]. 54 runs per variant: S1/S2b/S2c × fall L/R × mass 65/68/68.5 × push 250/400/550 N (0.15 s lateral on the torso). **Knee cap 513a7d5 on in every run** (max knee command in the ≥125° zone: 0 N·m — knee never reaches 125° in side falls). Legs/arms derated ×0.5 after detection.
L39 bumper [EST, T&R rev B]: contact L −12/+15°, R mirrored −15/+12°; k_θ 8.4 kN·m/rad to 2.3°, ×4 to 3.6°, then 400 kN·m/rad; unload ×0.34. Bumper energy = loading work. Gate ≤ 6.6 J.

| variant | S1 E max / ω_c max | S2b E / ω_c | S2c E / ω_c | bumper fails | bumper peak / pen | knee-first w/ foot moving |
|---|---|---|---|---|---|---|
| base (derated pose hold) | 1.66 J / 0.58 rad/s | 3.65 / 1.23 | **10.62 / 1.32** | **17/54 (all S2c)** | 377 N·m / 2.37° | 0 |
| **swing-leg tuck** | 1.66 / 0.58 | 3.65 / 1.23 | **1.33 / 0.85** | **0/54** | 147 / 1.0° (S2c) | 0 |
| hip-roll damping B 120 | 4.34 / 1.09 | 4.82 / 2.96 | 7.17 / 1.32 | 5/54 | 272 / 1.86° | 0 |
| tuck + damping | 4.34 / 1.09 | 4.82 / 2.96 | 0.0 / — | 0/54 | 272 / 1.86° | 0 |

- **Inertia:** S1 and S2c (planted stance leg, body swinging about it) → **9.9 kg·m² applies** (base S2c: 10.6 J at ω_c 1.32 rad/s ⇒ I_eff ≈ 12, i.e. body-dominated plus motor work); S2b → 0.65 kg·m². So the ω_c gate is ≤ 1.15 rad/s for S1/S2c: base S2c exceeds it, tuck (0.85) passes.
- **Bumper energy the fallback bumper would need (no tuck):** 10.6 J max (S2c, 68.5 kg) → beyond the ø20×10 linear 6.6 J, inside the proposed ø24×16 15.3 J.
- **Hip-roll damping (target ≤ 1 rad/s) is not adopted:** it replaces the roll hold and *raises* S1/S2b energy and ω_c (S2b 2.96 rad/s). ω_c is driven by the impact/body swing, not by commands. It does not conflict with the tuck, but adds nothing over it.
- **S2c (knee first with foot moving, 4.2 m/s): not reproduced** in this set — 0/216 legs had the knee land before the foot (knee contact speed ≤ 0.62 m/s, S2b only; fall-side foot speed at contact ≤ 1.70 m/s). The crossing/stumbling swing leg of T&R's S2c is not in these initial conditions [open: needs a stumble-in-gait start from the walk policy].
- **Swing-leg tuck rule** (`fall_mode.py`, fall/TUCK state): on detect, swing knee → 0.15 rad, hip pitch → 0. Detect at ≤ 29 ms after push; swing foot lands 54–55 ms after detection (vs 301–376 ms without), the foot always first. **No conflict with the 50 N·m knee cap** (it extends the knee, far from 125°). Foot lands faster (1.70 vs 1.40 m/s) — foot/ankle check owed.
- Contact order everywhere: feet first; S2b: foot then knee pad. Hip-roll motor peak ≤ 102 N·m (derated).
- Limits: PU curve [EST], no lateral knee pad geom, torso/shoulder impacts not analysed here, falls start from stand/kneel not gait.
