# Legs → RL Controls handoff (WBC, RL walking, sim) — 2026-10-14

Ownership moves to RL Controls. Legs still owns the leg hardware, the CAD and the FEA. Sources for this file: DECISIONS L28, L31–L33 and the code listed below. Everything here is from box runs; nothing has been re-run for this handoff.

## Code state (`modules/legs/wbc/`)
- `controller.py`: OSQP WBC (osqp 1.1.3, `pip install --user --break-system-packages osqp`). It defaults to LEGS_MASS=65 and LEGS_LIMITS=r1.
  - The plan path (`_plan_mpc`) tracks a cruise slice of the reference. Since r6 (L31) it runs closed-loop:
    - sagittal (lengthen-only) and lateral (±40 mm) DCM foot placement
    - playback rate ≈ `cruise/v_plan` (`rate_nom`, clipped 0.30–1.35)
    - `yaw_off` fed to the stance hip yaw (±12 N·m) and the swing-foot yaw
- `run.py`: `--mode stand|walk|push|carry --seconds --cruise --dt --gif`. Outputs go to `WBC_OUT` (default `grokbuild/results`).
- Sim model: sim/v3/humanoid_v3.xml. ankle_roll is ±18° (93cb518). Legs also changed the neck to 2× XM430 (P-019) before the handover; see the bottom of this file.

## Hooks (environment variables)
| var | where | meaning |
|---|---|---|
| `WBC_GATE=1` | controller.py:47 | Touchdown gate (L33). While the plan is in DS and the landing foot's fz < `WBC_GATE_TD` (60 N), the QP holds stance fz ≥ `WBC_GATE_HOLD`·mg (0.85) and the clock runs at `WBC_GATE_RATE`·rate_nom. Then load transfers over a `WBC_GATE_RAMP` (0.05 s) ramp. Timeout: `WBC_GATE_TO` (default 0.12; the best results used 0.2 s with rate 0.3). |
| `WBC_PLAN` | run.py:38 | Path to the reference .npz. The default is results/r2 walk_1p2_r2. |
| `WBC_COP_M` | controller.py:1970 | QP CoP margin inside the sole (m). Default 0. |
| `LEGS_COP_INSET` | gait_lib.py:166 | Reference generation: plan CoP inset from the sole edge (m), flat contacts only. |
| `LEGS_TOE_MARGIN` | gait_lib.py:161 | Reference generation: toe-rocker pivot inset from the toe edge (m). |
| `LEGS_AROLL` | gait_lib.py:36 | ankle_roll hard stop (±deg) in the gait_lib model. |

## References
`results/r7/ref_m12/walk_{0p8,1p0,1p2}_r7.npz`: DS 0.25, CoP inset 12 mm, toe margin 12 mm. Plan min margin 12.0 mm, planned DS 32 %, flight 0 (L33). Other r7 variants are in results/r7/ref, ref_ds25, ref_ds35 and ref_pz98.

## Results (65 kg, 20 s target)
- r6 baseline (walk_1p2_r2): fell at 5.0–5.8 s, DS 2.6 %, flight 9.5 % (L28, L32).
- r7, speed-matched references, no gate (L32):
  - 0.8 DS 0.25: **PASS 20 s** at a mean 0.73 m/s
  - 1.0: 7.1 s
  - 1.2: 4.78 s
- r7b, gate + ref_m12 (L33):
  - 0.8: PASS 20 s (0.733 m/s)
  - 1.0: best 10.84 s (rate 0.3, timeout 0.2)
  - 1.2: 5.45 s
- Results: results/r6/wbc, results/r7/{wbc_*, g_*}. Media: media/progress/2026-10-13_legs_wbc_r7_walk0p8.png.

## Root cause
1. r6: `_plan_mpc` played the slice open-loop, so every error went into the CoP. The CoP saturated at the sole edge, the foot rolled, stance yaw reached −17.6° and the robot fell. Fixed by the L31 rework.
2. The reference itself planned the CoP within 5 mm of the edge on 26–28 % of loaded frames. Fixed with the ref_m12 references.
3. The stance foot unloaded 40–70 ms before the swing foot touched down (bounce/flight). Fixed by the gate.
4. **Still open:** CoP tracking at speed. At 1.0–1.2 m/s the measured CoP rides the sole edge on 50–66 % of loaded frames, even with a 12 mm plan margin, and the foot rolls onto an edge. Candidates are listed in the briefs below.

## Grok Build briefs
- `grokbuild/wbc_fix_r6.md`: WBC plan-path rework (closed-loop step/timing/yaw)
- `grokbuild/rl_walk_brief.md`: RL walking (MuJoCo Playground/MJX, same MJCF, CPU replay on the box)
- `grokbuild/wbc_walk_1p2.md`: earlier 1.2 m/s brief

## Known bugs / caveats
- `--cruise` was ignored before L31: 0.5 and 0.8 gave an identical 4.317 s. It now scales `rate_nom`, but it only time-scales the slice. Step length still comes from the reference, so use per-speed references through `WBC_PLAN` rather than `--cruise` alone.
- Mean speed runs under the command (0.73 at a 0.8 command).
- fsim step-recover push falls in both the base and the ±18 stop cases. This is pre-existing (L29).
- Knee saturation of 3–5 % in carry 85 kg (L31).
- Neck (P-019, done by Legs before the handover, D L42):
  - neck_yaw/neck_pitch armature 0.0790 → 0.0005, ctrlrange ±36 → ±4.1 N·m
  - neckY+head mass scaled 1.137 → 0.810 kg (inertias scaled the same)
  - Controls now owns this, so revert or adjust as needed.
