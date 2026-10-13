# Actuators module (owner: RL Actuators)
Scope: every joint actuator (motor, transmission, output bearing, encoders, drive, housing), thermal, drive current, life, drive-side bus. Contract: CONTRACTS.md §1.
- `size.py`: round-1 leg sizing. It reuses the v3 models, reads the Legs gait results, and writes `results/sizing*.json` and `media/progress/2026-10-13_actuators_torque_speed.png`. Run: `python3 size.py` (margin 1.5) or `MARGIN=1.3 python3 size.py`.
- `results/sizing.md`: sizing table, power, energy, mass. `results/DECISIONS.md`: decision log.
- Pending contract changes: P-005 (PROPOSALS.md).
