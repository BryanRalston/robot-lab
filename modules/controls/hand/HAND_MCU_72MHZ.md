# Hand MCU at 72 MHz (Arbiter R-078) and per-flexor stall cap (R-080, Arms R8b) — RL Controls, 2026-10-14
Script `hand_mcu_72mhz.py` → `hand_mcu_72mhz.json`. Tags: **[REPO]** = robot-lab value; **[DS]** = Infineon/maxon/TI datasheet or reference-manual value from memory, *not re-read here* (verify at FW-E14); **[EST]** = my assumption.

## Inputs
- Clocks fCPU/fPERIPH/fCCU = **72/72/144 MHz** [REPO electronics §18.2d trim 1]. Setting: fSYS = fPLL = 144, CPUDIV=1, PBDIV=0 (fPERIPH = fCPU), CCUDIV=0 (fCCU = fSYS) [DS]. The ECAT clock comes from the USB PLL and does not depend on the CPU clock [DS].
- 11 drives per hand: 6 × DCX 22 S flexors + 5 × DCX 16 S. All are **brushed DC on DRV8874-Q1 PH/EN with IPROPI current sense, so no FOC** [REPO §16.7]. 11 current loops at 10 kHz, 6 position loops at 1 kHz [REPO].
- Encoders: 2 × ENX22 incremental at 1024 cpt on POSIF0/1, and 4 × ENX22 Absolute BiSS-C (12-bit, 23-bit frame, 5 MHz, 8.65 µs/read, 10 kHz) on 4 USIC SSC channels [REPO §16.8, R-073 FW-E14].
- EtherCAT: on-chip ESC, 1 kHz DC [REPO electronics l.40, CONTRACTS].
- PWM frequency: **not in repo**. 20 kHz assumed [EST].

## CPU budget at 72 MHz (cycle counts [EST])
| item | Mcyc/s |
|---|---|
| 11 current PI loops × 10 kHz × 250 cyc (ADC result, clamp, I²t) | 27.5 |
| 6 position loops × 1 kHz × 800 | 4.8 |
| 4 BiSS-C frames × 10 kHz × 250 (parse, CRC6, unwrap) | 10.0 |
| 2 POSIF count reads + unwrap | 0.8 |
| R-080 stall timers + cap logic, 6 × 10 kHz × 30 | 1.8 |
| EtherCAT SYNC0 ISR + PDO copy, 1 kHz × 4000 | 4.0 |
| mailbox/CoE, ladder/OT, tactile, TMP117 | 6.0 |
| ISR entry/exit + flash stalls | 4.4 |
| **total** | **59.3 → 82 % of 72 MHz, 18 % margin (conservative)** |

Electronics' own cycle figures (16.5 + 3 + 10 + 8 Mcyc/s) give **52 %** at 72 MHz, so their ~54 % is arithmetically right. My more conservative counts give 82 %. **The true figure is likely between 52 % and 82 %.** It FITS, but the margin is not large. Cycle counts are clock-independent, and flash wait states drop at 72 MHz, so these counts are pessimistic on that point.

**Required firmware practice (FW-E14):**
- Run one 10 kHz frame ISR, triggered by a CCU8 period match → VADC queue/scan → result event. Run all 11 loops in one pass.
- Put hot code in PSRAM (zero wait state) and use fixed-point or FPU PI.
- Read BiSS through the USIC FIFO, or GPDMA where needed. No busy-wait on the bus.
- Measure with DWT CYCCNT on the bench. **Pass ≤ 70 %.**

**Fallbacks, in order:**
1. DCX16 current loops at 5 kHz: −6 Mcyc/s.
2. BiSS at 5 kHz: unwrap is still 14.9° per sample vs 180°, a 12× margin; −5 Mcyc/s.
3. Run the CPU at 144/72/144: costs +0.29 W against the AO budget, so it is not preferred.

## Peripheral checks at 72/72/144
- **BiSS-C (USIC SSC master, fPERIPH 72) — PASS.**
  - XMC4800 has no BiSS master, so framing and CRC are done in software on SSC (REPO §16.8 approach; adopted).
  - SCLK = fFD/2 with fractional divider STEP 142 gives **4.99 MHz** (≤ 5 MHz certified). SSC master maximum is fPERIPH/2 = 36 MHz [DS], so 10 MHz would also be reachable.
  - Settings: frame read as a 32-bit SSC transfer (2 × 16-bit FIFO words); the start bit is found in software, which absorbs line delay and the ack; MA idles high (passive level); the timeout is met by the 100 µs frame.
  - Bus time: 4 × 8.65 = 34.6 µs serial (35 % of the 100 µs frame), or 8.65 µs on 4 parallel channels. The bus does not use CPU time.
- **POSIF (fCCU 144) — PASS.**
  - Edge rate at 12 400 rpm, 1024 cpt, ×4 is **846.5 kHz**, i.e. 170 fCCU clocks per edge.
  - Synchroniser + filter (2 + 3/5/7 clocks) [DS, UNVERIFIED] gives 35/49/62.5 ns against the 0.945 µs minimum state [REPO]. **Margin 27×/19×/15×.**
  - If the POSIF LPF option is used instead, keep it ≤ 32 clocks (≤ 236 ns, 4×).
  - 16-bit counter wraps in 77 ms, so reading at ≥ 1 kHz is enough.
- **PWM (CCU8/CCU4, fCCU 144) — PASS.** At 20 kHz: 7200 counts edge-aligned (12.8 bit) or 3600 centre-aligned (11.8 bit). Resolution is unchanged by the CPU downclock, because fCCU stays at 144.
- **VADC (fPERIPH 72) — PASS.**
  - fADCI = 72/3 = 24 MHz (≤ 30 MHz limit [DS]).
  - About 0.75 µs per 12-bit conversion [EST] vs 459 ns at full clock.
  - 15 channels over 4 groups → about 3 µs per period, well inside 50 µs.
- **EtherCAT — PASS.** The ESC is clocked independently [DS]. At 1 kHz, PDI/PDO handling is 4 Mcyc/s.

## EtherCAT topology: the hand is the LAST device on its arm line [REPO]
- `actuators/harness.py` l.56: `ECAT arm branch -> hand/tactile`, path COMPUTE→SHP→SHR→ELB→WRI→HAND, 8 slaves. These are the 7 arm Elmo drives (l.64/65), then the hand node.
- Also arms/R2_OPEN_ITEMS l.49: "sh_pitch→…→wrist×3→hand/tactile node".
- The tactile hub is inside the hand node, not a separate slave. **So a single PHY is valid** (§16.7 fallback / §18.2d trim 2: −0.26 W).
- Condition: no future device is added downstream of the hand. With one PHY, port 1 is closed and no ring is possible; R1 has no ring.

## R-080 / Arms R8b: per-flexor stall cap
Constants [REPO arms/A42_A43_R4, R7_ROUND]: Kt 18.4 mN·m/A, I0 35.9 mA, GPX22HP 103:1, η 0.65 (catalogue), spool r = 4 mm. Tension T = (I − I0)·Kt·103·η / r.

**A maximum-tension cap must assume the highest efficiency.** Static or backdriven gear efficiency is not bounded above by the 0.65 running figure. Arms R8b's 1.66 A sizes the cap at η 0.65, which is the worst case for *minimum grip*, not for maximum tension.

| η | T at 1.66 A (N) | cap for ≤ 500 N (A) |
|---|---|---|
| 0.65 | 500 | 1.66 |
| 0.70 | 539 | 1.54 |
| 0.80 | 616 | 1.36 |
| 0.90 | 693 | 1.21 |
| 1.00 | **770** | **1.09** |

**Adopt 1.08 A per flexor** (1.09 ideal, minus sense tolerance), giving T ≤ 495 N at η = 1 and 322 N at η 0.65. Cold Kt is used; hot Kt is lower, which adds margin.

**Grip under ladder B (55/82/88 °C → 0.84/0.70/0.50/0 A)** [REPO thermal R073; 30 N at 0.952 A, friction 1.3, which already contains η 0.65 and the sheath]:
- All ladder steps are ≤ 0.84 A < 1.08 A, so **the cap costs no sustained grip**. Ladder B still holds 0.70 A, i.e. **22.1 N (≥ 22 N, PASS)**, or 26.5 N on the 0.84 A step.
- T4 30 N peak needs 0.952 A < 1.08 A, so it still passes. The maximum burst grip at the cap is about 34 N.
- What the cap removes is only the unused 0.95–1.67 A burst headroom (~34–52 N).
- **Both conditions are met, so no trade-off is needed.**
- If the bench later shows higher sheath friction (grip per amp lower than 31.5 N/A), first measure the real η and friction (G5 capstan test). Options then:
  - (a) a per-hand calibrated η, which raises the cap to the measured worst η_max; or
  - (b) a tendon tension sensor with a closed-loop 500 N limit.
- Not the 0.65 sizing.

**Enforcement at 72 MHz (cost 1.8 Mcyc/s, included above):**
1. Current-loop clamp. The 10 kHz PI setpoint is clamped to 1.08 A per flexor, with output anti-windup. A measured IPROPI value above 1.15 A for 3 consecutive samples (0.3 ms) forces the bridge off for that flexor.
2. Stall timer. If |I| > 0.9 A and the encoder speed is below 5 counts/ms for more than 0.5 s, the setpoint ramps to the ladder step (≤ 0.84 A). Release needs speed or an EtherCAT command.
3. Existing protections stay in place:
   - the 1.67 A rail cap (3 flexors per rail);
   - the I²t limit of 0.84 A RMS;
   - the R-051 hardware latch, which disables all bridges independently.
- The DRV8874 current-regulation (ITRIP) limit is set via its IPROPI/VREF to about 1.2 A, as a hardware backstop above the firmware clamp [DS, check at layout].
- Bench (T-029/G5): stall each flexor against a load cell. **Pass: ≤ 500 N.**
