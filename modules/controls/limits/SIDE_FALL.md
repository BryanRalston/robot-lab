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

## Rev B (2026-10-21): foot force / ankle stop (T&R 8c7ac56) and mid-walk stumble
**Side-fall set, peak foot contact force / ankle hard-stop hits:** base S1 1027 N / 0, S2b 809 N / 18 (ankle pitch already at its +40° limit in the kneel pose, ≤ 6 N·m limit force — not an impact), S2c 508 N / 0. **Tuck S2c 2708 N** (foot 1.70 m/s) — at/above the top of T&R's 1.2–2.5 kN estimate; no ankle-stop hit. Tuck+damp S2c 2677 N.

**Stumble (owed case)** `stumble_fall.py` → `stumble_fall_results.json`: Legs WBC walk 1.2 m/s (walk_1p2_r2, gait_lib model), push 250/400/550 N × ±y × start 0.8/1.4/2.0 s, applied 0.15 s from the first single-support phase; fall mode on detect (derated PD hold, knee cap). 18 runs per variant, all fall.

| variant | knee-first with foot moving | swing foot speed at contact max | swing knee/thigh speed at contact max | peak foot force | ankle stop hits (max limit force) | typical order (swing leg) |
|---|---|---|---|---|---|---|
| base | **0/36 legs** | 2.08 m/s | 2.28 m/s | 1119 N | 5 (ankle pitch −52.5°, 83 N·m; motor 44–54 N·m) | foot → hand |
| tuck (instant) | 0 | **6.75 m/s** | 0.72 | **2677 N** | 2 (39 N·m) | foot → hand |
| tuck ramped 0.15 s | 0 | 4.96 | 1.65 | 2192 N | 2 (41 N·m) | foot → hand |

- **S2c (knee first, foot moving) is not reproduced in the stumble set either**: the foot always lands first. T&R's 4.2 m/s relative-speed case did not appear.
- **The swing-leg tuck in mid-walk is counter-productive**: straightening the swing knee whips the foot into the ground (up to 6.75 m/s, 2.7 kN). Recommend: keep the tuck for standing side falls (S2c, bumper energy) but **not in mid-stride stumbles** until a rate-limited version is tuned; T&R foot/ankle check owed at 2.2–2.7 kN.
- **Ruling on 976eca8 (implemented):** swing-leg tuck gated to standing/double support only (`fall_mode.tuck_allowed`; `swing_leg_tuck(..., support_phase)` is a no-op in single support 'ss'). Mid-walk stumbles detected in single support therefore keep the base behaviour (swing foot ≤ 2.08 m/s, 1119 N). The stumble table's tuck rows were run with the tuck forced (`force_tuck=True`) to show why.
