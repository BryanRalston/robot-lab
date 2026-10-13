# AUDIT.md: v3's weakest or least-supported claims (RL Arbiter, 2026-10-13)
Ordered by risk to "works if manufactured". Each item names the module that should address it first.

| # | claim in v3 | why it is weak | evidence location | owner (first) |
|---|---|---|---|---|
| A1 | Hand tendons last 5 y | Needs 1.75e6 bend cycles; published evidence ≤ 5e4. v3's only open FAIL | v3_checks "Open failures" | Hands (placeholder) → Actuators until staffed |
| A2 | Robot can stand/walk on these actuators | Sim with plain PD falls in ~4 s; only stands with balance controller; no walking sim at all; walking speed (1.2 m/s in power model) never demonstrated | balance_v3.json; v3.py l.200 | Legs |
| A3 | Joint torque/speed requirements are right | Torques are v2 `req` values scaled by mass; speeds are "[EST, v2]". Every PASS rests on these. No gait-derived torque/speed/power profiles | v3.py SPEED, V2REQ | Legs (derive), Actuators (respond) |
| A4 | Actuator envelopes and masses | Housing mass/size from a parametric formula with [EST] gear lengths and a 1.25 factor; CAD envelopes [EST] | v3.py housing(), GEAR_LEN; README (cad envelopes [EST]) | Actuators |
| A5 | Knee/ankle twin-screw selection is consistent | REVISIONS §F says knee = 2 × TBM2G-06013D; v3_checks/v3.json say TBM2G-06808D. Per-row mass 1.81 kg for a 2-motor + 2-screw unit looks low and the linear2 mass-doubling bug was fixed once already | REVISIONS §F vs v3_checks | Actuators |
| A6 | Thin margins | knee 238/232 N·m, waist_pitch 116/115, elbow 76/73.5; leg needs scale with mass so any mass growth fails them | v3_checks | Actuators + Legs |
| A7 | Thermal at 91 K rise (knee) | Lumped R_h-a model, air cooling, 40 °C ambient; no test or FEA thermal; 9 K from limit | v3_checks | Actuators |
| A8 | Fall survival | Energy method with 55/45 hip/shoulder split [EST], constant-force EPP crush; side fall only (no front/back, no repeated-fall count); torso panel SF 2.89 at 2 mesh levels only | v3_checks fall; REVISIONS §G | Torso (placeholder) / Legs for hip |
| A9 | Runtime 2.1 h | CoT 0.25 [EST], 120 W compute, 40 W sensors are assumptions; peak power and pack C-rate never checked | v3.py l.200 | Torso/Brain (placeholders); Legs provide gait power |
| A10 | Bus/data architecture | No fieldbus, topology, cycle rate, or harness spec exists; harness 2.0 kg is a guess | v3.json struct | Brain (placeholder); Actuators for drive side |
| A11 | Bolted joints | VDI-style with Φ = 0.15 [EST] and default 50 mm PCD not tied to CAD | v3.py bolted() | Actuators (flanges), Legs (brackets) |
| A12 | Payload | No payload case checked (arms sized to v2 req); T5 20 kg not verified | — | Arms (placeholder) |
