# Hand MCU at 72 MHz (Arbiter R-078) and per-flexor stall cap (R-080, Arms R8b) — RL Controls, 2026-10-14
Script `hand_mcu_72mhz.py` → `hand_mcu_72mhz.json`. Tags: **[REPO]** = robot-lab value; **[DS]** = Infineon/maxon/TI datasheet or reference-manual value from memory, *not re-read here* (verify at FW-E14); **[EST]** = my assumption.

## ADOPTED (R-083): 144/144/144 MHz, 20 kHz PWM — PASS
R-083 lifted the 72 MHz limit; Electronics runs the XMC4800 at 144/144/144 MHz with 20 kHz PWM [REPO, Electronics]. The 72 MHz analysis below is kept as the **fallback** (82 %, still fits).
- **CPU:** the conservative count is 60.7 Mcyc/s including the R-089 rail limiter (+1.4), giving **42 %, a 58 % margin** (Electronics' counts give 26 %). FW-E14 bench pass is ≤ 70 %, measured with DWT CYCCNT.
- **BiSS-C (USIC SSC, fPERIPH 144):**
  - Fractional divider STEP = floor(2 × 5 MHz × 1024 / 144 MHz) = **71**, PDIV = 0, so SCLK = 144 × 71/1024/2 = **4.99 MHz ≤ 5 MHz** (rounded down on purpose).
  - Read time stays 8.65 µs; 4 × 8.65 = 34.6 µs in the 100 µs frame.
- **VADC:** the prescaler divides fPERIPH by **6**, giving fADCI = **24 MHz ≤ 30 MHz** [DS limit] (Electronics §18.2l). Divide-by-5 (28.8 MHz) is also legal; divide-by-4 (36 MHz) exceeds the limit. About 0.75 µs per conversion [EST].
- **PWM 20 kHz (confirmed by Electronics):** fCCU 144 gives 7200 counts edge-aligned (12.8 bit) or 3600 centre-aligned (11.8 bit). This is unchanged from the fallback.
- **POSIF:** unchanged, because fCCU was already 144. The margin is 15–27× against the 0.945 µs minimum state.
- **EtherCAT:** fit a **single PHY**, since the hand is the last device on each arm line (harness.py l.56/64–65). Electronics' rule is binding: **nothing may be added after the hand**, because port 1 is not populated. Adding anything there would need a second PHY (+0.26 W, ~110 mm²).
- **AO power:** reverting the 72 MHz trim costs about +0.29 W. The AO budget is Electronics' to close under R-083; it is not checked here.

**R-089 status:** 144 MHz is the default. 72/72/144 is the fallback, used only if Thermal finds the board > 90 °C. **FW-E14 ≤ 70 % is binding.** At 72 MHz the conservative count is 84 %, so the fallback **must** also take fallbacks 1 and 2 (DCX16 current loops at 5 kHz, BiSS at 5 kHz): 49.7 Mcyc/s, **69 %**.

## Per-rail summed-current limit and flexor stagger (Electronics §18.2l item 4, R-089, R-097)
- **Rails** [REPO hand_close_r4]: rail A = F1–F3 + S1, S2; rail B = F4–F6 + S3–S5. Logic is on AO, not on rail A.
- **Limit:** I_rail = Σ D_i × I_IPROPI,i / 0.95 [η EST]. Every sample, all achievable currents on that rail are scaled by one factor so that **I_rail ≤ 1.50 A** (R-097 binding). The scaling is applied to the achievable current min(setpoint, (V − Kt·ω)/R), not only to the setpoint. At speed the setpoint is saturated, so scaling only the setpoint does not reduce rail current (first sim build showed 2.4 A).
- **Loop rate: 10 kHz, not "20 kHz".** Electronics wrote "20 kHz loop"; PWM is 20 kHz and the current loop (and this limiter) runs at 10 kHz.
- **Is 10 kHz fast enough against the RP40 hiccup (~2.5 A, 150 % OLP)?** Yes:
  - With the setpoint held, the rail current between two samples changes only through back-EMF build-up. Worst case is 1.66 A × Kt × (Kt·1.66/J) / V × 100 µs = **6 mA per sample**.
  - Setpoint steps are made by the loop itself, after the limiter, so they cannot overshoot.
  - Inside one sample, the DRV8874 cycle-by-cycle chop at 1.915 A bounds each bridge.
  - Sim peak is 1.505–1.517 A instantaneous and ≤ 1.50 A at 1 ms, which is 1.0 A below hiccup.
  - Without the limiter, a simultaneous close reaches **5.4 A** and hiccups the RP40.
  - The RP40 OLP response time is not in the repo; it is [DS, to cite].
- **Stagger (R-097):** at most one flexor per rail starts at a time. **Default offset 50 ms, hard maximum 150 ms** (200 ms fails the T4 ≤ 1 s close). Holds may overlap. Implemented as a 1 kHz scheduler.
- **Current hierarchy:**
  - Clamp **1.66 A** (pending the Arbiter correcting R-089, which says 1.08 A; both are documented in the cap section). The Arms R8b/R-081 basis is the η_max 0.65 sheet, and the loaded close needs ~1.7 A.
  - Firmware trip **1.80 A × 3 samples**.
  - DRV8874 hardware chop **1.915 A** (R_IPROPI 3.83 kΩ, VREF 3.3 V, A_IPROPI 450 µA/A, per Electronics' TI DS citation). The firmware trip sits just below the chop.
  - Rail sum **1.50 A**.
- **CPU cost:** 2 rails × 10 kHz × 60 cyc + 1 kHz × 200 = **1.4 Mcyc/s**, already in both budgets.

**Close time** (`rail_stagger_sim.py` → `rail_stagger_sim.json`; Arms hand_close_r4 physics, η 0.65, friction 1.3, contact ramp to 30 N, small drives holding at I_nom):

| case (1.50 A/rail) | rail A full close | rail B full close | rail peak at 1 ms |
|---|---|---|---|
| simultaneous, no limiter | 0.621 s | 0.621 s | **5.3–5.4 A → hiccup** |
| simultaneous, limiter only | 0.661 | 0.668 | 1.50 |
| stagger 20 ms (Electronics) | 0.685 | 0.690 | 1.50 |
| **stagger 50 ms (R-097 default)** | **0.723** | **0.724** | **1.50** |
| stagger 50 ms, hot R × 1.5 | 0.732 | 0.735 | 1.50 |
| stagger 150 ms (R-097 maximum) | 0.922 | 0.922 | 1.50 |
| stagger 150 ms, hot R × 1.5 | 0.930 | 0.931 | 1.50 |

- **Verdict: T4 ≤ 1 s is met** at the 50 ms default (0.72–0.74 s, 0.26 s margin) and at the 150 ms maximum (0.93 s hot, 0.07 s margin).
- It does **not** meet the old A43 0.64–0.68 s figure: 50 ms costs about +60 ms against limiter-only. Under R-097 that figure is a sim result, not the requirement. If Arms needs ≤ 0.68 s, the only way is the limiter with no stagger (0.66–0.67 s); 20 ms just misses.
- **G5:** verify the **hot** close (windings hot, ladder B active) at 50 ms and 150 ms. Pass: ≤ 1 s with no RP40 hiccup.

**Bench test T-029 (new item):** command all of rail A to close at the same time, then all of rail B, to a 30 N grip, with the firmware limiter and stagger active. **Pass = no RP40 hiccup, and rail current ≤ 1.67 A at 1 ms resolution** (measure on the RP40 output with a current probe). Repeat with the windings hot.

## Datasheet figures to re-read and cite before G1 (R-089)
- **Cited in the repo by Electronics:**
  - DRV8874-Q1 eq. 3, A_IPROPI 450 µA/A
  - RP40 OLP 150 % hiccup
  - XMC4800 Table 33 currents
  - ENX22 4 MHz, 62.5 ns min state
- **[UNVERIFIED], from memory, must be cited:**
  - XMC4800 RM: USIC SSC max baud fPERIPH/2, fractional divider formula
  - POSIF/CCU4 input synchroniser + 3/5/7 filter
  - POSIF LPF options
  - VADC fADCI ≤ 30 MHz and conversion cycles
  - ECAT clock source independent of fCPU
  - GPDMA channel count
  - flash wait states vs fCPU
  - RP40 OLP response time
  - all cycle counts [EST] until the FW-E14 DWT measurement

## FALLBACK: 72/72/144 MHz analysis (R-078)
### Inputs
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

**The η table above is kept as the rationale for G5 calibration.**

**ADOPTED cap (Arms R8b + Controls; R-089 still reads 1.08 A, so an Arbiter correction is pending. Both are documented: 1.08 A is the η = 1 bound, 1.66 A is the η_max 0.65 datasheet bound plus the G5 per-assembly calibration):**
- **Clamp: 1.66 A per flexor.** The basis is the maxon GPX 22 HP 103:1 sheet, η_max 0.65, cited in `arms/hand_close_r4.py` l.4 [REPO, DS] as the datasheet upper bound. At η 0.65 this gives **500 N**.
- The loaded close needs about 1.7 A transient (A43 sim, T4 0.64–0.68 s [REPO]), so a 1.08 A clamp would block the close.
- Residual risk: if the as-built η is above 0.65 (static or back-driven), 1.66 A could give up to 770 N at η = 1. The **G5 per-assembly calibration below closes this risk.** Materials already designs the sheath and end stops for a 775 N proof [REPO TENDON_SHEATH].
- **Grip under ladder B:** every step is ≤ 0.84 A, so the clamp costs nothing. Sustained grip is **22.1 N (≥ 22 N, PASS)** at η 0.65 and friction 1.3, and the 30 N peak (0.952 A) passes.

**Enforcement (cost 1.8 Mcyc/s, already in the CPU budget):**
1. **10 kHz current-loop clamp at 1.66 A** per flexor, with anti-windup.
2. **Trip:** if IPROPI reads above **1.80 A for 3 consecutive samples (0.3 ms)**, that flexor's bridge is switched off.
3. **Stall timer:** if |I| > 0.9 A and speed is below 5 counts/ms for more than **0.5 s**, the setpoint ramps down to the ladder step (≤ 0.84 A).
4. **DRV8874 ILIM at about 1.9 A**, above the trip, as a hardware backstop. It must **not** be 1.2 A, which would block the close [DS, set by RIPROPI/VREF at layout].
5. Existing protections stay: the 1.67 A per-rail cap, I²t at 0.84 A RMS, and the R-051 latch.

**G5 requirement (new):**
- Measure tendon tension per amp on **every assembly**, both driven and **back-driven**, against a load cell at stall.
- If the inferred η > 0.65, set a calibrated per-hand cap I_cap = 500 N × r / (Kt × 103 × η_meas) + I0, which keeps tension ≤ 500 N, and store it in hand NVM.
- If the calibrated cap falls below the about 1.7 A needed for the loaded close, the issue goes back to Arms/Arbiter. Options are a slower close profile or a tendon tension sensor with a closed-loop 500 N limit.
