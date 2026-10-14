# R-070 pick-pose (deep squat) knee limit (Controls, before G4)
Basis: A40 winding model (`thermal/winding_model.py`). The default knee is now **as-built D69 rev B**: Actuators fbd762b, 2× TBM2G-07613D, +0.0703 m² CAD fins, size.py ×2 factor dropped, h 8 still air, η_f 0.7, drives off housing, 35 °C. Rha 1.601 K/W, τ_cont(120 °C) = **76.9 N·m** per knee.
Target: winding ≤ 120 °C (design target). Derate 130 → 145 and torque-off 150 stay as the backstop in `WindingModel.torque_limits`.
Hot start = steady state at the worst standing P-042 carry hold of 64.4 N·m (Tw 89.4 / Th 75.4 °C). Cold = 35 °C soak.
Generator: `pick_limit_gen.py` → `pick_limit_table.json`. Runtime: `pick_limit.py` (`PickLimiter`, `allowed_dwell`, `rest_needed`), test `test_pick_limit.py`.

| knee τ N·m | to 120 °C, hot start s | to 120 °C, cold s | **allowed dwell** (50 % hot) s | **rest before repeat** s (at ≤ 64.4 N·m) |
|---|---|---|---|---|
| 80 | 1550 | 2603 | 775 | 471 |
| 100 | 194 | 713 | 97 | 657 |
| 120 | 51 | 319 | 25.6 | 274 |
| 150 | 21 | 102 | 10.5 | 181 |
| 180 | 12.3 | 47 | 6.1 | 162 |
| 220 | 7.4 | 25 | 3.7 | 149 |
| 260 | 5.0 | 16 | 2.5 | 144 |
| 300 | 3.7 | 11.7 | 1.8 | 139 |
| 345 (peak) | 2.7 | 8.5 | 1.3 | 132 |

- Repeating at the **full** hot dwell is never possible: the rest posture at 64.4 N·m cannot cool back below 120 °C fast enough. So the runtime limit uses 50 % of the hot dwell. The rest values make a 2 h repeat cycle (dwell, rest, dwell, …) peak at ≤ 120 °C.
- **Rule:**
  - Above τ_on = 77 N·m, a budget b += dt/dwell(τ). At b ≥ 1, the knee is capped at 77 N·m, so the pick must rise or abort.
  - After the episode ends, the next deep squat is blocked for rest(peak τ). That rest is the max over the table rows ≤ peak, which is conservative.
  - The planner calls `allowed_dwell(τ)` before committing to a pick.
- Practical: a 20 kg pick in a deep squat at about 150–180 N·m gets **6–10 s** per pick and needs about 3 min of standing between picks. Picks under ~100 N·m (half squat) get ≥ 97 s.
- [EST] h 8 and η_f 0.7 are conservative estimates, as in 2e2d593. Iron loss is ignored (static hold). At the hot start, rest is assumed at the worst hold. G5 bench data will replace the table.
