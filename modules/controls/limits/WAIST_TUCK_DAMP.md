# Waist-pitch TUCK damping + D102 stop-zone wiring (RL Controls, 2026-10-21)

## Wiring of soft_limits.apply_waist_stop_zone (1ed4d73)
- WBC: `modules/legs/wbc/controller.py` `_waist_zone()` applied after the final `np.clip(tau, ±tau_max)` in both QP torque paths.
  Assumes actuator names end in `waist_pitch` (as apply_waist_stop_zone requires) — not exercised in a WBC sim this round.
- Fall sims: `waist_energy_backfall.py` applies `waist_stop_zone_tau` to the waist command every step (held or damped).
  `waist_speed_probe.py` commands waist tau = 0, so the zero is a no-op (comment added). D99 `knee_stop_d99.py` commands
  waist 0 in `contract` and PD in `contract_hold`; NOT modified this round (its runs here go through waist_energy_backfall.run).
- Tests: modules/controls/limits pytest 36/36 pass.

## Waist damping law (`fall_mode.waist_fall_torque`)
B ramps 0 -> B_max over the last 20 deg before each end (-30 / +60), only opposing motion toward that end, clipped to
min(sim derated limit, 115.4 N·m CONTRACTS waist_pitch peak), then the D102 zero. Levels B_max = 15 / 40 / 100 N·m·s/rad.
At 100 the 115 N·m clip binds above ~1.2 rad/s. Drive speed rating is 2.8 rad/s (CONTRACTS, at 30 % torque); producing braking
torque at 3-11 rad/s joint speed is beyond the rated envelope [EST — Actuators must confirm braking/regen at that speed].
In damped cells the damping REPLACES the waist hold (TUCK), as asked.

## Results (contact speed at MJCF range end = stop proxy; E = 0.5·(I_P160 + 0.24)·ω², arms down 1.68 / arms fwd 3.76 kg·m²)
| cell | B | end | ω rad/s | E down J | E fwd J | head contact m/s |
|---|---|---|---|---|---|---|
| 72.1 kg w+20 120 N·s held | none (hold) | +60 | 7.01 | 41.3 | 92.4 | no head contact |
| | 15 | +60 | 4.09 | 14.1 | 31.5 | 8.74 |
| | 40 | +60 | 3.09 | 8.0 | 17.9 | 8.72 |
| | 100 | +60 | 2.69 | 6.1 | 13.6 | 8.59 |
| 68 kg w+20 120 N·s held | hold | +60 | 5.03 | 21.3 | 47.6 | none |
| | 15 / 40 / 100 | +60 | 3.96 / 2.93 / 2.47 | 13.1 / 7.2 / 5.1 | 29.4 / 16.1 / 11.5 | 8.35–8.40 |
| 72.1 kg w0 60 N·s held | hold | — (no end hit) | — | — | — | 5.41 |
| | 15 | −30 then +60 | −4.68 / 2.61 | 18.4 | 41.1 | 6.01 |
| | 40 | −30 | −4.55 | 17.4 | 38.9 | 5.79 |
| | 100 | −30 | −3.50 | 10.3 | 23.0 | 5.68 |
| D99 crouch_collapse 68 kg lean 0.3 | off (drive 0) | +60 | 6.15 | 31.8 | 71.2 | 2.01 |
| | 15 / 40 / 100 | +60 | 4.80 / 4.31 / 4.13 | 19.4 / 15.6 / 14.3 | 43.4 / 35.0 / 32.1 | 2.0 |
D99 forward_fall and kneel_tip (lean 0.3) do not reach either end with or without damping.

## Findings
- Achievable contact speed: 2.5–2.7 rad/s (held-backward w+20, B 100), 3.5 (w0 60 N·s), ~4.1 (crouch_collapse). **No level
  reaches the D102 1.75 rad/s motor-off allowance**, so the slip clutch / damper is still needed; damping cuts the stop energy
  ~3–7x (worst 92 -> 14 J arms forward on the 72.1 kg cell, 71 -> 32 J on crouch_collapse).
- Downside: replacing the hold with end-only damping lets the waist swing freely in mid-range. In w0/60 N·s the waist now
  reaches the −30 end at 3.5–4.7 rad/s where the hold never reached an end, and head contact gets WORSE: the held w+20 cells had
  no head contact, damped ones hit at 8.4–8.7 m/s (frame: norm of MuJoCo cvel linear part, same caveat as the 9.4 m/s T&R query);
  w0 cell 5.4 -> 5.7–6.0 m/s. Recommendation [EST]: keep the hold and add the end ramp on top, not replace it — not run this round.
- Single seed per cell, lean 0.3 only for D99, 68 kg only for D99. I from P-160 (Torso), model I also in json.
Data: waist_tuck_damp.json (script waist_tuck_damp.py).
