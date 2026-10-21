# D100 — Hip roll/yaw limp hold vs 140 N trapped-hand clamp (skirt 8f, no rigid stops)
Script `hip_limp_hold_d100.py` → `results/hip_limp_hold_d100.json`.

**Verdict: FAIL. Motor shorting can't hold the clamp to ≤140 N, and no actuator-side brake or clutch can.** Shorting only damps. It can't hold a static load. Once the hand stops the joint (ω→0), the braking torque drops to 0 and the hand carries the whole external torque minus gear friction. The load that closes the gap (body weight, a push) acts on the same links that form the gap. A brake makes this worse (it holds the full load). A slip clutch in the drivetrain can't cap a load that bypasses it. **The mass change is 0** (nothing recommended to add).

## Inputs
| | hip roll | hip yaw |
|---|---|---|
| motor | TBM2G-08508A (manual §9.6.1 p.292–293): Kt 0.206 Nm/Arms hot, Ke 12.4 Vrms/krpm, Rll 0.860 Ω, Lq,ll 1.13 mH, 10 pp, Jm 0.593 kg·cm² | TBM2G-06008A (§9.3.1 p.262–263): 0.121, 7.33, 1.60 Ω, 1.06 mH, 10 pp, 0.137 kg·cm² |
| gear | CSG-25-100 (JOINT_AUDIT) | CSG-17-100 |
| back-driving torque (HD Table 37, CSG component, ratio 100) | 9.2 N·m | 3.1 N·m |
| reflected inertia Jm·N² | 0.593 kg·m² | 0.137 kg·m² |
| lever to pinch gap | 0.10 m [EST] (hem is R141.5, r_hip_pinch_check_8c.py; the inner gap is closer, so this is conservative) | 0.10 m [EST] |
| allowed static torque, 140 N × L | **14 N·m** | **14 N·m** |

## Short-circuit braking at the joint (3-phase short, T = 3I²R/ω_m, I = E/√(R²+(pωL)²))
| ω joint rad/s | 0.05 | 0.1 | 0.2 | 0.5 | 1 | 2 | 5 |
|---|---|---|---|---|---|---|---|
| roll N·m | 16 | 32 | 61 | 114 | 120 | 83 | 37 |
| yaw N·m | 3 | 6 | 12 | 28 | 43 | 44 | 26 |
Roll peaks at 124 N·m at 0.76 rad/s. Yaw peaks at 46 N·m at 1.5 rad/s. The low-speed damping is 326 (roll) and 61 (yaw) N·m·s/rad. That is strong damping but zero holding.

## Clamp cases (static = (T_ext − T_bd)/L; impact = undamped ω·√(J·k), k = 30 N/mm hand [EST], so the impact figure is conservative)
| case | T_ext N·m | creep closing speed | F static | F static+impact | ≤140? |
|---|---|---|---|---|---|
| roll, limp leg hanging at 15° (11 kg @0.45 m [EST]) | 12.6 | 1.2 °/s | 34 | 89 | PASS |
| roll, double-stance sag (34 kg × 0.10 m [EST]) | 33 | 4.6 °/s | 242 | 465 | FAIL |
| roll, single-stance fall (68 kg × 0.10 m) | 67 | 11 °/s | 575 | 1105 | FAIL |
| yaw, gravity (vertical axis) | 0 | — | 0 | 0 | PASS |
| yaw, foot twisted by 200 N × 0.10 m [EST] | 20 | 17 °/s | 169 | 438 | FAIL |
A static clamp ≤140 N requires external torque ≤14 + T_bd: **23.2 N·m for roll and 17.1 N·m for yaw.** Gravity creep does close the gap, at 1–11 °/s for roll. Shorting turns a slam into a slow squeeze, but it doesn't remove the squeeze.

## Heat and drive
- Winding loss while creeping is 0.1–11 W. A worst-case roll fall puts ~20 J into the copper, which is ΔT <1 °C [EST]. Heat is not a limit.
- **Elmo G-TWI:** the manual (MAN-G-TWI v2.011) has no motor-off dynamic-brake or phase-short mode. STO (§10.4.3, refers to MAN-G-Board ch.9) disables the gates, which leaves the phases **open** (only gear friction remains). A short with power lost would need a normally-closed relay or depletion MOSFET across the phases: about 0.015 kg per joint, 0.06 kg robot [EST]. It's **not recommended**, because it doesn't buy a pass.
- Alternatives rejected: a power-off brake (holds the load and clamps harder); a slip clutch at ≤14 N·m (can't hold the stance and can't cap a load that bypasses the drivetrain); resistor-tuned braking (still zero at ω=0).

## What closes it (outside Actuators)
1. **ID/Legs:** at 8f, make the gap geometrically safe. Either the minimum gap across ROM + overtravel stays ≥25 mm (hand) or ≤4 mm (finger exclusion), or the skirt panel is compliant with a crush force ≤140 N over ≥25 mm of travel. Otherwise keep a rigid or bumper stop that leaves a ≥25 mm gap at contact.
2. **Controls:** limp/safe-stop must kneel or sit first (as for the knee). Don't go MO=0 in stance. With motors on, limit the hip roll and yaw torque to ≤14 N·m in the pinch zone only if ID can't fix the geometry.
3. **Robot Lab:** rule that 8f's "load-limited hand protection" can't come from the actuators. Restore stops or require the gap/compliance criterion in (1).

## Rev b (2026-10-21 ~10:55 ET): real hand lever arms, ID P-023 rev 8g (d8fb6f9, design/cad/covers/hip_skirt_r8g.json)
The 0.10 m [EST] lever is replaced by the perpendicular distance from the worst contact point to each axis (roll / yaw): hem-panel 109/168 mm, hem-shroud 82/104, L-R panel 180/150, L-R shroud 133/131. Shorting brake, creep speeds and loads are unchanged. Clamp force = (T − T_backdrive)/L + creep·√(J·k)/L, with k = 30 N/mm. Limit 140 N.

| joint / case | creep °/s | hem-panel | hem-shroud | L-R panel | L-R shroud | verdict |
|---|---|---|---|---|---|---|
| roll: limp leg hanging, 15° | 1.15 | 82 N | 109 N | 50 N | 67 N | PASS |
| roll: double-stance sag (34 kg × 0.10 m) | 4.58 | 426 | **567** | 258 | 349 | **FAIL** |
| roll: single-stance fall (68 kg × 0.10 m) | 10.9 | 1014 | **1348** | 614 | 831 | **FAIL** |
| yaw: limp leg (gravity) | holds | 0 | 0 | 0 | 0 | PASS |
| yaw: foot-scuff twist (200 N × 0.10 m) | 16.6 | 261 | **421** | 292 | 334 | **FAIL** |

**Verdict rev b: still FAIL in stance and twist for every contact pair.** The hem-shroud (82 mm roll / 104 mm yaw) is worst, at 1.2–1.3× the rev-a 0.10 m forces. The L-R panel is lightest but still 1.8–4.4× over. A limp hold by shorting stays damping-only. This agrees with the Controls D100 rules (no commanded MO=0 standing; 14 N·m cap in the pinch zone).
