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

## Update: Electronics 10107a7 §16.5 board (XMC4300, DRV8874-Q1, X7R, HW NTC cutoff ~110 °C)
**STM32H7:** Electronics lists it as optional (STM32H725/735VGT3 if kept). **Thermal assumes it is dropped**. If it is kept, add about 0.5–0.8 W (25 °C) to 1.2 W (125 °C leakage) [EST], which still fits inside the 4 W total.

**Power budget**, typ / hot at 85–125 °C. [EST] values come from the XMC4000/DP83822/DRV8874 datasheet class figures and must be confirmed against the XMC4300 datasheet IDD table:

| item | typ | hot |
|---|---|---|
| XMC4300 at 144 MHz, EtherCAT active | 0.33 W | 0.6 W (leakage roughly doubles from 85 to 125 °C) |
| 2× EtherCAT PHY (DP83822 class) | 0.4 W | 0.45 W |
| buck/LDO losses + TMP117/NTC/comparator | 0.3 W | 0.35 W |
| 11× DRV8874-Q1 quiescent + 20 kHz switching | 0.9 W | 1.0 W |
| H-bridge conduction, 6 flexors at 0.952 A (0.70 A) | 1.6 W | (0.9 W) |
| **total at the 30 N hold** | **≈ 3.5 W** | **≈ 4.0 W** (≈ 3.3 W at 0.70 A) |

- **≤ 4 W, so the board power is unchanged and no rerun is needed.**
- The 4 W case in `results/a43c_board.json` stands.
- With the adopted ladder (55/70/80/88 → 0.84/0.70/0.50/0.35/0 A, = the tuned case):
  - walking: shell 59.8 °C, board 68 °C;
  - still air: shell 70.3 °C, board 78 °C;
  - H-bridge Tj ≤ 91 °C.

**HW NTC cutoff at 110 °C board (latching, 10 K hysteresis): placement is sensible.**
- **Normal margin:** 32 K above the normal still-air board (78 °C).
- **Top-step margin:** 14 K above the board at the top ladder step (shell 88 + 4 W × 2 K/W ≈ 96 °C).
- **Fault response:** it trips only on a ladder or sensor fault. On trip the H-bridge Tj is ≈ 122 °C, which is still < 125 °C. The 125 °C parts keep 15 K.
- **Murata NCP15 range:** confirm ≥ 125 °C, as Electronics flagged.
- **Tighter option:** if margin to Tj is wanted, 105 °C also works and sits 9 K above the top step.

## Update: Electronics §16.7 (8f4bad8) — XMC4800 board, 4.3 W hot; Arms grip fix (R-059 round)
Board: XMC4800 0.45 W typ / 0.90 W worst, plus DP83822HF ×2 (< 0.22 W each) ⇒ **3.6 W typ / 4.3 W hot**.
Rerun `a43c_board.py <Rm>` at 4.3 W with the adopted ladder 55/70/80/88 °C → 0.84/0.70/0.50/0.35/0 A. Results: `results/a43c_board_4p3W_Rm8.0.json` (loose mount) and `results/a43c_board_4p3W_Rm4.0.json` (Arms fix: flexors clamped to the shell with paste, 0.5 mm, 0.92 A case).
MCU Tj = board + 0.9 W × RthJB ≈ 10 K/W (LQFP-144 with board copper [EST]; RthJA 22.5 is not used because the board is hotter than the air).

| case | shell | flexor winding (125) | step held | board | MCU Tj | H-bridge Tj | margin to NTC 110 / parts 125 |
|---|---|---|---|---|---|---|---|
| walk, loose (Rm 8) | 60.3 | 95 | 0.70 A | 69 | 78 | 81 | 41 / 44 K |
| still, loose | 68.7 | 102 | 0.70 A (dips to 0.50) | 77 | 86 | 90 | 33 / 35 K |
| **walk, clamped (Arms fix)** | 59.7 | **84** | 0.70 A | 68 | 77 | 81 | 42 / 44 K |
| **still, clamped** | 70.2 | **95** | 0.50 A | 76 | 85 | 91 | 34 / 34 K |
| no derate, still (fault reference) | 122–128 | 181–215 FAIL | — | 131–137 | 140–146 | 143–149 | NTC trips |

**Findings**
- **4.3 W changes nothing material** (+0.5 K shell vs 4 W). All junctions are ≤ 91 °C, the 110 °C NTC keeps ≥ 33 K, and the 125 °C parts keep ≥ 34 K.
- **The Arms clamp fix cools the windings by 8–11 K, but the shell does not change.** Shell temperature is set by total forearm heat vs the shell-to-air path, not by the mounting.
- So with I²t at 0.84 A and friction ≤ 1.2 (30 N at 0.88 A), the ladder still steps to **0.70 A once the shell reaches 55 °C**: about **24 N at friction 1.2**.
  - Shell time constant ≈ 15 min walking: a 30 N hold lasts ≈ 10–15 min from cold before the first step.
  - **30 N truly continuous at 35 °C needs either a 60 °C first step** (winding still ≤ 100 °C clamped; this costs NTC margin, not limits) **or more forearm skin area/vents.**
- The I²t at 0.84 A RMS remains the motor guard; the ladder is the board/shell guard.

**Shoulder bay (RP40s only):** 3.6 W continuous / 9 W peak per side vs the 8.9 W continuous used in the A43 update. Bay air ≈ **40 °C walking / ≈ 48–53 °C still air** (scaled), so ≥ 7 K margin to the 60 °C RP40 derate. d4cca06 holds with more margin.
