# Knee carry duty limit (R-079, R-081, R-096) — RL Controls

Basis: A40 winding model, D69 rev B as built (0.0703 m² fins), **h 8 still air, η_f 0.7**, 35 °C, drives off housing,
winding target ≤120 °C. Profile: P-042 `carry_20kg_1p0` (1.0 m/s), worst knee, copper + iron loss, ×1.0 and ×1.1.
Hot start = steady 64.4 N·m loaded stand. Files: `carry_limit.py`, `carry_limit_gen.py` → `carry_limit_table.json`,
`r081_check.py` → `r081_check.json`, `test_carry_limit.py`.

## Enforced (default)
`CarryGovernor` = min of
1. **R-096 rule** (`R096Rule`; `R081Rule` is an alias, R-081 10 on/10 off OR 40 % retired): ≤40 % carry over any rolling
   30 min **AND** each continuous carry bout ≤5 min. *Carry* = load held, walking or standing; *unloaded* = load set down.
   A bout ends only after ≥60 s set down (`min_gap`); shorter breaks keep the bout timer running.
2. **Model remaining time** (`CarryLimiter`): forward prediction from the live winding/housing estimate to 120 °C at the
   P-042 cycle-equivalent load (RMS torque + mean iron loss), ×0.9 margin. Reported to the planner as `remaining()` s.
3. Torque backstop: `WindingModel` derate 130→145 °C, trip 150 °C.

`h` is a constructor parameter of `KneeThermal` (default 8). Change it only when Thermal validates a walking h.

## Shared state with the pick limit
One `KneeThermal` per leg is stepped with the measured knee torque/speed. The carry governor uses it, and picks call
`KneeThermal.pick_ok(tau, pick_limit.allowed_dwell(tau))` in addition to `PickLimiter`. The pick table assumes a 64.4 N·m
hot start; after a carry bout the winding can be hotter, and `pick_ok` then blocks the squat (tested).

## Carry table (hot start / cold, time to 120 °C; rest needed so repeated bouts stay ≤120 °C, 3 h)
| h | load | t hot | t cold | τ_cont120 | D 60 s rest (stand 64.4 / idle) | D 120 s | D 300 s | sustainable duty (stand / idle) |
|---|---|---|---|---|---|---|---|---|
| 8 | ×1.0 | 22.7 min | 39.7 min | 76.9 | 28 / 14 s | 63 / 21 s | 162 / 49 s | ~65 % / ~81–86 % |
| 8 | ×1.1 | **8.9 min** | 21.3 min | 76.9 | 98 / 28 s | 239 / 56 s | 802 / 162 s | **~27–38 % / ~65–68 %** |
| 10 | ×1.0 | continuous | continuous | 83.3 | – | – | – | 100 % |
| 10 | ×1.1 | 18.2 min | 28.0 min | 83.3 | 28 / 14 s | 56 / 21 s | 169 / 63 s | ~64–68 % / ~81–85 % |
| 12 | ×1.0, ×1.1 | continuous | continuous | 88.6 | – | – | – | 100 % |
Rest bisection resolution 10 s.

## R-081 check (h 8, η 0.7, ×1.1, hot start, 3 h worst-case compliance)
| pattern | rest unloaded (0 N·m) | rest = loaded stand 64.4 N·m |
|---|---|---|
| 10 on / 10 off | **121.9 °C** | 134.5 °C |
| 40 % worst arrangement (12 on / 18 off) | **125.3 °C** | 132.1 °C |

**The rule does not hold 120 °C** (still under the 130 °C derate when the rest is truly unloaded). Also, 10 min continuous
from hot already exceeds 120 °C at 8.9 min. Tighter numbers that do hold (idle rest): **≤8 min on / ≥10 min off → 118.5 °C**;
40 % with bouts ≤5 min (5/7.5) → 112.3 °C; 4/6 → 110.0 °C. With a *loaded* rest nothing at 40 % holds (5/7.5 → 126.0;
5/10 → 122.8): the rest must be load-down. The rule is kept as enforced default (R-081); the model limit runs alongside and
in practice cuts the first hot bout to ~8 min (0.9 × 8.9) and later bouts as the state requires.

## R-096 check (h 8, η 0.7, ×1.1, hot start, 3 h, unloaded rest)
Steady 5 on / 7.5 off (40 %): **112.3 °C**. Worst compliant arrangement = burst 5 on / g / 5 on / g / 2 on, then rest out the window:
| break g between bouts | 2 s | 10 s | 30 s | 60 s | 120 s | 180 s | 300 s |
|---|---|---|---|---|---|---|---|
| peak Tw °C | 125.1 | 124.0 | 121.6 | **119.1** | 116.4 | 113.9 | 112.3 |
Hence `min_gap` 60 s: R-096 holds ≤120 °C in its worst arrangement (119.1 °C, 0.9 K margin). The model remaining-time limit
(0.9 margin) still governs and the 130 °C derate is the backstop. 8 on / 10 off was not adopted.
