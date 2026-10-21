# Torso 9700df9 / b3811cc: battery GORE vent + deflector, Thor duct partition x −63 — 2026-10-21 EDT
Hand calc, no script (no new model needed). [EST] = estimate; [LIT] = typical published 21700 NMC/NCA runaway data, not P45B-specific test data (none in repo).

## (a) Pack vent at torso floor (−90, 0, global 1401.6), 0.5 mm SS deflector → exit x −107, z ≈ 1390
Pack: 20S5P Molicel P45B (NMC/NCA 21700, 16.2 Wh/cell), torso R1_ARCHITECTURE.
- **Normal GORE breathing:** pressure equalisation only, ≈ ambient-temperature air, mL/min. **No thermal effect.** No interaction with the knee or hip exhaust.
- **Single-cell runaway [LIT]:** 21700 NMC/NCA vents ≈ 3–8 L of gas over seconds to a minute, at **≈ 300–600 °C at the cell cap, with sparks and particle ejecta and flame possible (≥ 800 °C)**. Gas is flammable (H₂, CO, hydrocarbons). Through the pack and GORE emergency path, gas at the exit is ≈ 150–400 °C [EST] for ≈ 10–60 s. Propagation to further cells would extend this to minutes.
- **Deflector (0.5 mm 304/316 SS):** melts at ~1400 °C; it survives temperature but ejecta erodes it. **OK**, if ≥ 0.5 mm and riveted or welded, not bonded (adhesive fails above 150–200 °C).
- **PC covers (HDT ≈ 130–140 °C, ignition ≈ 450+ °C):** the torso cover starts at z ≥ 1330 and its rear is at x ≈ −117.5, **≈ 10 mm aft of the exit (x −107, z 1390)**. A 150–400 °C jet at 10 mm **FAILS** the cover (softening or burn-through, possible ignition of vent gas on the PC).
  - **Fix (required):** an open port in the rear cover aligned with the deflector exit (≥ 2× the deflector exit area, ≤ 5 mm louvres for IP2X), and a 0.3 mm SS or mica patch on the cover inner face ±40 mm around it [EST +0.01 kg]. The gas then leaves the body directly, aft.
- **Hip-pitch drive plates (pelvis wall z 1136–1220, x −85…−114):** exit is ≥ 170 mm above and the jet goes aft; hot gas rises. **PASS**, ≥ 130 mm Legs sweep agrees.
- **Hip-pitch harness:** the drive feeds cross the open pelvis top behind the waist deck (z ≈ 1230) and run down the outboard wall, ≥ 160 mm below the exit and upstream. **PASS**, but **keep all harness and connectors out of the band x < −95, z 1360–1420 behind the deflector**, and no harness clipped to the deflector.
- **Femur bond (z ≈ 800) and knee outlet hardware (z 840–904):** > 480 mm below, upstream of a buoyant plume. **PASS.** The knee jet (≤ 45 °C by z 1126) cannot carry vent gas down.
- **Ignition:** the jet must not point at a sealed enclosure or electronics. Thor exhaust is upper back centre (|y| < 0.06, high): ≥ 150 mm above and the plumes are separate. The HS200 clamp resistor (hot) is on the exhaust side of the bulkhead, not in the vent path. **PASS** with the cover port.
- **Sit/kneel and prone:** in sit (hip pitch −40…−107) the deflector moves with the torso and still points aft. In prone the exit points up. In supine it points into the floor, where gas spreads under the robot (handling-SOP item: battery first, keep clear). **No change needed beyond the SOP.**

## (b) Thor duct partition moved to x −63 (CFRP 1 mm, 260 × 22, torso z 278–300), 6 mm behind Thor's rear face
- No detailed Thor model exists in repo beyond R1/A41 (134 W, 24.9 CFM Sunon PF40281B1, ΔT ≈ 10 K air). Assessed against that.
- **If the partition is only the intake/exhaust separator** (Thor fin flow exits up through the fin stack, not through the 6 mm gap): the separation is kept; Thor-side air rise ≈ 10 K → cold-plate air ≈ 45–48 °C, case ≈ 60–70 °C [EST] vs TTP ~85 °C (unverified). **PASS.**
- **If fin exhaust must pass through the 6 mm × 260 mm gap (1560 mm²):** v ≈ 7.5 m/s → ≈ 90 Pa [EST], beyond what a 40 × 28 fan delivers at full flow → flow drops by ≈ 40 % → air rise ≈ 17 K, case ≈ 75–85 °C [EST]. **FAIL/thin.** Fix: gap ≥ 20 mm (≈ 8 Pa).
- **Recirculation:** the partition must be gasketed to the shell on both sides and the top, else hot exhaust short-circuits to the intake (+5–10 K [EST]). The EtherCAT junction (R083, duct intake side, ≈ 50 °C) stays on the cold side. Confirm it is forward of x −63.
- **Verdict: PASS conditional.** Torso must confirm the fin-exhaust path does not run through the 6 mm gap, and the partition is gasketed. J-T2 CFD (chest duct) remains the real check.
