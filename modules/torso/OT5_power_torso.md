# O-T5 power per phase class: Torso input to Controls' OT5_reference_tasks.md (fee4ed2)
Kept in modules/torso (CHARTER: no edits to other modules' files). Controls may copy the column. Script: `ot5_task_power.py` → `ot5_task_power.json`.
| class | W | basis |
|---|---|---|
| walk 1.0 m/s | 712.1 | CONTRACTS R1.3 703.4 + torso adds 8.4 (R1.2 §13.5, fan 6.12 in full) + BMS +0.26 (R1.4) |
| carry-walk 20 kg | 772.1 | walk × 837/772 (`actuators/results/sizing.md` carry vs walk-1.2 no-regen rows) [EST] |
| stand | 262.7 | rest 254 + copper 40 − compute cap 40 + torso 8.66 [EST] |
| pick/place | 309.9 | stand + compute uncapped 40 [EST] + bay 2 × 3.6 W hold (Arms R4) |
| idle | 252.7 | stand − 10 W arm/hand copper [EST] |
| task | cycle s | mean W | h typical (1458 Wh) | h binned (1425.6 Wh) |
|---|---|---|---|---|
| T-A 5 m tote | 52 | 380.4 | 3.83 | 3.75 |
| T-B 10 m tote | 62 | 438.7 | 3.32 | 3.25 |
| T-C 20 m tote | 82 | 512.7 | 2.84 | 2.78 |
| T-D shelf pick | 307 | 372.0 | 3.92 | 3.83 |
| T-E kitting | 190 | 313.0 | 4.66 | 4.55 |
Only T-E meets 4 h. The other tasks reach ~2.8–3.9 h. The rating task (Torso + Arbiter) decides whether 4 h mixed holds.
