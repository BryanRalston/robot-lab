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

---
# Amendment round (~11:15 ET): `waist_energy_backfall.py` → `waist_energy_backfall.json`
I = upper-body (waistY subtree: torso, arms, neck, head) inertia about the waist-pitch axis, computed from the model at the
instant the waist reaches its range end. E = 0.5·I·ω². The stop is still the MJCF range −30/+60°, not P-160 geometry.
E treats the lower body as fixed, so it is a **[EST] upper-body KE figure, not a true relative-motion energy** (the
reduced-mass correction would lower it). Contact speeds are body-origin linear speeds at first floor contact.

## (A) Energy bound, D99 forward set (68 kg, waist tripped)
I at impact 1.68–2.35 kg·m². Per run: crouch 0.1 +60 end 4.71 rad/s/18.8 J; crouch 0.3 +60 6.15/**44.5 J**; crouch 0.5 −30
6.34/34.2 J; fwd 0.1 −30 3.01/8.3 J; fwd 0.5 −30 1.03/0.9 J; others no stop contact. **Worst A: 44.5 J (crouch_collapse lean 0.3, +60 end).**

## (B) Backward set — cells RUN: standing only, 68 & 72.1 kg × waist0 0/+20/+60 × push 60/90/120 N·s (100 ms, −x on pelvis)
× {all tripped except TUCK knees, waist held ×0.5}. 36 cells. **NOT run: walking 1.0 m/s, heel slip.**
- **Worst overall: 72.5 J, 7.01 rad/s at +60 end, I 2.95 — 72.1 kg, waist0 +20, 120 N·s, held-waist ×0.5** (the derated hold is overpowered and the waist hits late at t 0.60 s).
- Worst tripped: 55.7 J, −8.32 rad/s at −30 end (72.1 kg, waist0 0, 60 N·s); at 68 kg 46.6 J/6.43 rad/s at +60 end (0°, 120 N·s).
- At −30 end the tripped worst is 55.7 J (72.1) / 35.8 J (68, waist0 +60, 90 N·s). Held-waist runs never reached −30.
- waist0 = +60 cells start on the +60 end (logged 0 J there); their −30 end reaches up to 35.8 J tripped.
- First contact: a hand in most cells, a shank otherwise. Never pelvis, pack or head first.
- Head contact speed up to 9.44 m/s (68 kg, 0°, 90 N·s tripped); held-waist runs often keep the head off the floor.
- Torso/pack contact speed ≤ 3.85 m/s. Pelvis peak normal force 0.5–4.8 kN (max 4844 N, 72.1 kg, +60, 90 N·s, held).
- CAVEATS: I did not verify that −x is rearward in this model or which waist end is extension; the result labels ends by
  sign only. A head at 9 m/s in a backward fall needs T&R/ID review — this is a big finding if the push sign is right.

## (C) 25° chest-only landing — NOT STARTED (time). The Sim has chest-pad contact with a solref timeconst only (prone_data pad_tc),
no crush/stroke model, so per-pad crush depth/energy can't be read off without adding a compliance model. OPEN.
