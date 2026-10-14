# R-069 cover trim tests (RL Industrial Design, 2026-10-14)
One-page plan for the test-gated R-069 items. C1 (foot dent) is **withdrawn** — R-081 C2 deletes the foot top shell. Trim B (knee PC 1.2) is **dropped**; **B2** (PA12 1.5 knee) takes the kneel-fall gate.

| ID | item | Δ kg if pass | gate |
|---|---|---|---|
| T-B2 | PA12 1.5 mm knee cap (replaces B) | −0.016 | kneel-fall |
| T-F1 | TPU-film waist bellows | −0.025 | flex cycle |
| T-G | moulded snap hooks (2 of 4 inserts) | −0.032 | retention / fall |

All masses [EST] half-credit until areas are measured (R-040). Book only on pass.

---

## T-B2 — Kneel-fall dent / crack (PA12 1.5 mm knee cap)
**Method.** Mount a production-intent P-022 PA12 1.5 mm cap (same draw, louvres, inserts as the PC part) on a shank surrogate at the tongue neck block. Drop or press the robot (or a 66.5 kg mass fixture) into a kneel so the cap is the first contact on a flat steel plate at 15–25 °C. Energy target: representative kneel from standing hip height, **≥ 80 J** into the cap [EST; Controls to confirm from T-030 / gait]. Three hits on the same cap at the same spot, 60 s apart.

**Pass.** No through-crack, no fragment > 5 mm, no insert pull-out. Dent depth ≤ 3 mm residual after 1 h. Louvres do not tear at slot ends. Cap remains mountable.

**Samples.** n = 3 caps (new each series). One PC 1.5 mm control optional.

**Equipment.** Drop tower or guided mass ≥ 66 kg; flat steel anvil; high-speed or 240 fps camera; depth gauge / laser; 80 J energy verification (height × weight).

---

## T-F1 — Waist bellows flex cycle (TPU-film convolute)
**Method.** Mount a P-024 TPU-film boot (built thickness) on a waist yaw/pitch fixture spanning the CONTRACTS waist ROM (yaw ±90 °, pitch per model_v4). Cycle at **≥ 1 Hz** equivalent step rate, 40 °C chamber, dry. Target **≥ 10⁶ cycles** (Materials: ~1 cycle/step, ~10⁶/year).

**Pass.** No tear through a convolution; no crack > 10 mm; clamp bands still seal (no visible gap under 50 Pa smoke or soap-bubble check). Mass change ≤ 5 %.

**Samples.** n = 2 boots. One TPE baseline optional.

**Equipment.** 2-axis waist ROM fixture with cycle counter; 40 °C environmental chamber or heated enclosure; inspection light / dye penetrant optional.

---

## T-G — Snap-hook retention / fall
**Method.** Fit each rigid cover panel type that uses snaps (thigh front/outboard, knee cap; foot deleted by C2) with **2 moulded snap hooks + 2 bonded inserts** (production intent). (1) **Retention:** 50 N outward pull at panel CG, 10 s, three times — panel must stay on. (2) **Fall fuse:** side-fall or equivalent 220 J class impulse into the panel (padded striker); snaps may release (fuse OK) but hooks must not fracture into sharp fragments; panel recoverable; re-fit snaps engage ≥ 3 times after.

**Pass.** Retention holds 50 N. After fall: no sharp fragments; re-fit OK ≥ 3 cycles; lost-panel fuse is acceptable if the panel is tethered or logged as a wear spare.

**Samples.** n = 2 of each panel type (or one thigh + one knee minimum).

**Equipment.** Force gauge 100 N; fall rig or striker; spare snap set.

---

## Reporting
Log method, energy/cycles, pass/fail, photos, and mass of each specimen in `modules/design/results/r069_tests/`. Arbiter books B2/F1/G only after a written pass from Materials + ID.
