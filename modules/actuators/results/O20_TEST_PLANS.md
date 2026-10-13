# O20 test plans: flex qualification of the moving-joint harness (R-020 A9)
Scope: every clock-spring service loop in `harness.py` (14 joint types; r_wrap 34–53 mm from `v3/cad/out/cables.json`; ROM from `sim/v3/humanoid_v3.xml`).
- **Life target:** T9 is 14 600 h of walking. Gait is about 1.06 strides/s per leg (Tstep 0.47 s), which gives 5.6e7 cycles over life for the leg joints. Leg joints only sweep about ±15–35° per stride. The test therefore uses two blocks:
  - **Full-ROM block:** 1e6 cycles. This covers sit, stand, kneel and reach events, 200 per day × 5 y = 3.7e5, × 2.7 margin.
  - **Gait-amplitude block:** 6e7 cycles at the gait sweep.
- Accelerated rate: up to 3 Hz (gait block) and 0.5 Hz (full ROM), at room temperature. A 2e6-cycle full-ROM spot sample runs at 50 °C.

## O20a: power cores (Stäubli SILI-E in the loops, Lapp SiF straight), flex-cycle test
- **Specimens.** Per joint class, 3 loops built exactly as routed: SILI-E 2.5 mm² pair (leg trunk), 1.0 mm² (shank and arm), 0.5 mm² (arm trunk, pigtails, hands).
  - Loops include the SILI-E→SiF solder splice and heat-shrink at both drum exits, and are wound on a printed PA12 drum at the real r_wrap (34, 43, 48, 53 mm) inside the same sleeving.
  - The worst case is the 2.5 mm² pair on the r 48 mm waist-yaw drum (r/OD 12.3) and on the hip-pitch drum (ROM 145°).
- **Rig.** A servo rotary stage (e.g. an existing hip_roll actuator spare, or a 400 W servo with a 50:1 gearhead) drives the drum through ±ROM/2.
  - The cable ends are clamped to a fixed frame at the routed exit angle.
  - **Live monitoring** throughout the test:
    - Constant 10 A DC per conductor pair from a bench supply. This is RMS-representative and also heats the conductors.
    - 4-wire resistance on each conductor, sampled every 1 000 cycles.
    - Event detector: 1 µs interruption > 1 Ω, per IPC/WHMA-A-620 style monitoring.
    - Thermocouple on the bundle.
- **Cycles.** Block 1: 1e6 full-ROM cycles at 0.5 Hz (23 days). Block 2: 6e7 cycles at ±20° at 3 Hz (231 days per rig, so run 4 rigs in parallel, or accept 2e7 cycles with a Weibull extrapolation, β = 2 assumed and confirmed from the failures).
- **Pass criteria:**
  - R increase ≤ 10 % per conductor, and no event > 1 µs.
  - No insulation crack in the 5× visual check or in a 500 V DC / 1 min hipot test after cycling.
  - Strand breakage ≤ 5 % in a sectioned sample at the drum tangent point.
  - Bundle ΔT ≤ 30 K at 10 A.
- **Fail action, in order:** larger r_wrap; SILI-E one gauge up in the loop only; a Stäubli/igus class-6 CF-type single core if available ≤ 4 mm OD; flat FFC/FPC power in a clock-spring cassette.
- **Duration and cost [EST]:** 6–8 weeks for block 1 plus 4 parallel block-2 rigs; about $3–5k of hardware plus cable samples.

## O20b: EtherCAT on Belden MachFlex MRTA2P26S, impedance, signal integrity and flex
- **Specimens.**
  - 3 × full leg branch (3.41 m incl. 7 loops + 8 pigtails, JST-GH terminated at drive ends, as `harness.py`).
  - 3 × arm branch (2.84 m).
  - 3 × 1 m straight reference.
- **Test 1, impedance.** TDR at 35–50 ps rise, differential on each pair.
  - **Pass:** Zdiff 100 Ω ± 15 Ω over the cable body, and splice/connector excursions ≤ ±25 Ω over ≤ 30 mm. This is the 100BASE-TX (IEEE 802.3 clause 25) / EtherCAT ETG.1000 basis.
  - Also measure insertion loss (VNA, 1–100 MHz): ≤ 1.0 dB at 31.25 MHz for the 3.4 m branch, well within the 100 m Cat5 budget.
  - NEXT: ≥ 35 dB at 31.25 MHz.
- **Test 2, link.** Each branch sits between two EtherCAT slaves (ET1100 eval boards, or Elmo Gold Twitter on the bench) in a 1 kHz cyclic test with 4 kB process data.
  - **Pass:** 0 lost frames and 0 CRC/RX errors in 24 h.
  - Repeat while 3 × Gold Twitter drives at 20 A PWM share the bundle (EMI coupling from the power cores).
- **Test 3, flex.** Same rig and cycle blocks as O20a, on the loop sections, with the link test running continuously and RX_ERR counters logged every second.
  - **Pass:**
    - 0 link drops.
    - RX error rate < 1e-9.
    - Post-test TDR within ±5 Ω of pre-test.
    - Shield DC resistance increase ≤ 20 %.
- **Fail action:** add a thin-wall FEP ETFE-quad, or a GORE quadrax segment, inside the loops with the bend rule relaxed only after a cycle test; or move to a 1000BASE-T1 / 100BASE-T1 single-pair PHY with the flex-rated Belden 74035PU (35 mm reverse-bend rated).
- **Duration and cost [EST]:** 2 weeks for tests 1–2 (TDR/VNA rental ~$1.5k), then test 3 in parallel with O20a.
