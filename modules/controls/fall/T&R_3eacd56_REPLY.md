# Reply to T&R 3eacd56 (TORSO_BC_P160_REVIEW) — RL Controls, 2026-10-21 ~11:13 ET (PARTIAL, team stop)

## (1) 25° chest-only landing vs pad stroke — NOT RUN, OPEN
No pad-compression sim was run this round; I have no measured compression/peak/margin. Nothing below is a result.
- Definition I will use: "25°" = torso (chest-normal) angle off the floor normal at first pad contact.
- T&R's own arithmetic in 3eacd56 (824 J / (11.2 kN × 0.73) = 101 mm > 81.2 mm usable) already says a 25° chest-only
  landing of the 824 J case would bottom the core. I cannot confirm from sim that the 25° L3 lands on the shoulder pad first.
  Until measured, treat 25° L3 as **not shown to fit chest-only**.

## (2) Waist-pitch speed — measured in the D99 fall set (probe, not the T-031/R-146 chest landing)
`waist_speed_probe.py` → `waist_speed_probe.json`: D99 cases (crouch_collapse, forward_fall, kneel_tip) × lean 0.1/0.3/0.5,
68 kg, contract TUCK (knees on per fall_mode, **all other drives incl. waist tripped MO=0 + D94 friction**), 2 s.
The waist stop is represented only by the MJCF range −30..+60° (MuJoCo soft limit), **not the P-160 stop geometry/gap**.
| case, lean | waist span (deg) | peak |ω| (rad/s) | ω at range end (rad/s) |
|---|---|---|---|
| crouch_collapse 0.1 | −15.5..61.9 | 4.71 | 4.71 (+60 end) |
| crouch_collapse 0.3 | −2.9..62.6 | 6.86 | 6.15 (+60 end) |
| crouch_collapse 0.5 | −32.6..1.3 | **9.97** | **−6.34 (−30 end)** |
| forward_fall 0.1 | −31.3..33.5 | 6.06 | −3.01 |
| forward_fall 0.3 | −11.4..24.4 | 6.24 | no contact |
| forward_fall 0.5 | −30.4..0.6 | 2.11 | −1.03 |
| kneel_tip 0.1/0.3/0.5 | ≥ −11.5..0 | ≤ 1.93 | no contact |
- **Worst at stop contact: 6.34 rad/s (crouch_collapse, lean 0.5, −30° end); 6.15 rad/s at +60 end.** Peak free speed 9.97 rad/s.
- So T&R's "waist moves little in a chest fall" does NOT hold with a tripped waist drive: the waist flops into its range ends.
  Stop energy not computed (needs P-160 stop stiffness and the reflected inertia) — OPEN.
- Caveats: lean units are the fall-set's (K.CASES/place); waist-tripped is the contract state; a held waist (contract_hold) not run.

## (3) Backward-fall waist case — PROPOSED, NOT RUN
- IC: standing 68 kg, nominal stance, and walking 1.0 m/s; waist pitch 0 and +20° (bent forward).
- Trigger: rearward pelvis push 60/90/120 N·s (100 ms) and a heel-slip trip (μ→0.1 under both heels).
- Controller: R-146a TUCK as for forward falls (knees on, others tripped) and a variant with waist held (derated ×0.5).
- Measure: waist pitch ω at the **extension (−) stop**, stop energy ∫τ·ω, peak stop moment, back/pack contact force & order
  (pelvis vs back vs head), head clearance.
