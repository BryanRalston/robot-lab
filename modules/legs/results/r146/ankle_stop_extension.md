# R-146: ankle dorsiflexion stop extension for the heel-lift kneel (Legs L73)
Script `ankle_stop_r146.py` -> `ankle_stop_r146.json` (2D kneel geometry + 2D screw kinematics, model_v4 OCC clearance at knee 145°). Light compute.

## Sign convention (verified)
model_v4 ankle_pitch is about +y with x forward: **negative = dorsiflexion** (toe up / shank forward over the foot). Same as the MJCF (`l_ankle_pitch range -0.785398 0.698132` = −45°/+40°) and Controls' "−0.79 rad dorsiflexion stop". CONTRACTS ROM: loaded −50…+40°, mechanical −60…+40°. **The −0.79 rad stop is a sim/MJCF limit (old model ROM −45°, README), stricter than the contract.** (`ankle_clear_r5.py` used the opposite internal sign; not used here.)

## (A) What the kneel needs (knee 145°, rigid foot pivoting on its toe edge x 180, CoM proxy = hip over the toe edge [EST])
| heel lift | ankle q | knee height |
|---|---|---|
| 0° (heel down) | −118° | (impossible) |
| 25° | −78.2° | 52 mm (≈ knee-pad contact [EST pad radius ~50]) |
| 35° | −61.2° | 123 mm |
| 40° | −52.5° | 159 mm |
| 45° | −43.8° | 193 mm (reachable today) |
Kneeling to pad contact with the CoM still over the toes needs **≈ −78° (−1.37 rad)**. The foot has no toe joint (L5), so the heel lift is the only way to keep the ankle within the stop.

## (B) Screw / linkage (2D, trunnion (90,450), instep pin r73 at (73,+20) about the ankle (0,80))
- **The screw line passes through the ankle axis at ≈ −61°: toggle.** Moment arm 25.7 mm at −45°, 17.9 at −50°, 9.9 at −55°, **1.7 at −60°**, then rising again (2.5 at −62.5°, 14.7 at −70°) with the direction reversed, so the drive cannot take the joint through the toggle.
- Available torque (2 screws, F = 323.8/(2×0.073) = 2218 N/screw [EST]): **114 N·m at −45°, 80 at −50°, 62 at −52.5°, 44 at −55°, 7 at −60°.**
- Length: minimum pin-to-pin is at the toggle; Actuators' Lmin 262.6 (roll 18°) vs need 250.7 → 11.9 mm margin, and the margin rises past −61°. **Stroke is not the limit, toggle is.**
- Note: the contract's mechanical −60° is 1.2° from toggle (arm 1.7 mm, ≈ 3 % of the neutral 72 mm arm). Flag for Actuators.

## (C) Clearance at knee 145° (model_v4 OCC; pins in their bores excluded)
| q | min | pair |
|---|---|---|
| −45° | **0.9 mm** | ankle-roll stop carrier under the cross [EST] vs fork cheek |
| −55…−75° | 0.0 | same |
Only the [EST] placeholder carrier (54×62×15) limits; screws, rods, eyes, instep lugs and tibia are not the minimum. Fix: chamfer/relieve the carrier's ±y corners (the carrier width only needs to reach the ±38 stop blocks) — re-check once the carrier is real CAD (Actuators/ankle cross). Ankle drive plates (D94) are not defined in the model (L72: positions fail), not included.

## (D) Strength at the extended angle (kneel, [EST])
- Kneel load: 68.4 kg [EST, credible ~68.42 per R-146 §3] × g / 2 feet = 336 N at each toe edge. Lever toe-to-ankle at heel lift 40° = 180cos40 − 80sin40 = **86.5 mm → 29 N·m per ankle**.
- At −52.5°: per-screw force 29/(2×0.0139) = **1043 N** (walk peak 1734 N, ankle_v4.json): rods, GE12/QA1 eyes and r73 instep lugs are covered by the existing walk cases → SF unchanged or higher vs R-128 bands; fatigue: kneel is a rare event (≪ 1e7 cycles), so the 58 MPa amplitude does not govern.
- At −55°: 29/(2×0.0099) = **1465 N** (< walk peak; available 44 N·m → torque SF 1.52 [EST]).
- At −57.5°: 2500 N/screw (> 2218 N available, > walk peak): **FAIL** (near-toggle force blow-up).

## (E) New limit
- **Feasible: mechanical/ROM −55° (−0.960 rad), controlled-use limit −52.5° (−0.916 rad)** — 6° / 8.7° from the −61° toggle, torque SF 1.5 / 2.1 vs the 29 N·m kneel [EST].
- **It does not by itself make the kneel reachable**: at the −55° limit the knee is still ≈ 140 mm [EST, interp] above the ground with the CoM over the toes. The last ~90–140 mm need the CoM ahead of the toe line (controlled forward drop onto the knee pads) or a smaller knee angle. Going to −78° is not possible without re-laying out the ankle linkage (toggle) — a contract and actuator change, not proposed.
