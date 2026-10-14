# A43C (rev R-047): hand board + 6 DCX 22 flexors in the forearm (RL Thermal, 2026-10-14)
> **Superseded by R-047:** the earlier revision (63ebe7b) put 2× RP40 in the forearm. The RP40s stay in the shoulder bay, and **d4cca06 (`A43_HAND_SUPPLY_SIGNOFF.md`, 71 °C case) holds**. This revision covers the board only.

Board: STM32H7 + LAN9252 + 11 DRV8874-class H-bridges, 2–4 W (4 W used). 35 °C ambient, 30 N hold, all 6 flexors at 0.952 A (A43B, friction 1.3).
Transient model `a43c_board.py` → `results/a43c_board.json`, run for 4 h:
- **Per motor:** winding node, then 7 K/W to the housing, then 8 K/W to the shell (loose mount, A43B worst case). Hot copper R(T).
- **Shell:** 672 J/K. Shell to air is 1.4 K/W walking (h 12) and 2.4 K/W in still air [EST].
- **Board and H-bridges:** board to shell 2 K/W [EST]. H-bridge junction is 45 K/W above the board, with 0.30 Ω hot HS+LS on-resistance [EST, typ ~0.2 Ω].
- **Ladder:** shell sensor next to the board, 5 K hysteresis. DCX 22 winding limit 125 °C.

| case | shell (eq.) | DCX winding | board | H-bridge Tj (limit 125) | result |
|---|---|---|---|---|---|
| walking, no derate | 83 °C | **159 °C FAIL** | 91 °C | 104 °C | FAIL (motor) |
| still air, no derate | **127 °C** | **214 °C FAIL** | **135 °C** | **147 °C FAIL** | FAIL |
| walking, ladder 60/80/90 → 0.84/0.70/0.5/0 A | **59.8 °C**, settles at 0.70 A | 94 °C | 68 °C | ≤ 80 °C | **PASS** |
| still air, ladder 60/80/90 | **79.7 °C**, settles at 0.70 A, no limit cycle | 116 °C | 88 °C | ≤ 100 °C | **PASS, 10 K margin to 90** |
| still air, tuned ladder 55/70/80/88 → 0.84/0.70/0.5/0.35/0 A (option) | 70 °C at 0.5 A | 104 °C | 78 °C | ≤ 91 °C | PASS, more margin |

## Verdict
- **The 60/80/90 ladder holds the shell ≤ 90 °C both walking (≈ 60 °C) and in still air (≈ 80 °C), with no limit-cycling.** In both cases it settles on the 0.70 A step, which is about 22 N tip at friction 1.3.
- Without the derate, still air reaches a 127 °C shell and the board/junctions fail. **The derate is mandatory**, and so is the A43B per-flexor I²t limit at 0.84 A RMS.
- Still air sits just under the 80 °C step. If Controls wants margin, or the board is 4 W at stand-still, use the tuned ladder (55/70/80/88, adding a 0.35 A step).
- H-bridge self-heating is small: 0.27 W per bridge at 0.952 A gives about +12 K. Junctions stay ≤ 100 °C with the ladder.
- **Part grade: 125 °C (industrial −40…125 / AEC-Q100 Grade 1)** for the MCU, LAN9252, H-bridges and passives. With the ladder the board runs at 88 °C, which is only 17 K from a 105 °C rating, and a derate or sensor fault in still air takes the board to 135 °C. 105 °C parts are not recommended.
- Bench G5: thermocouples on the shell, board and one flexor case at the 30 N hold, walking and in still air.
