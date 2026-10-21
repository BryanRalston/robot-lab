# Electronics BOM: fasteners (2026-10-21)

No standalone Electronics BOM existed before this file. All parts so far live in `R1_ARCHITECTURE.md`. This file starts the BOM with the fastener list for RL Materials' steel → titanium pricing (Robot Lab request).

**Rule:** only fasteners that the Electronics design actually calls out are listed. Where the design doesn't give a size, count or grade, the entry says so. [EST] marks an estimate. Nothing is filled in by guess.

| # | fastener | size | count | grade / material | where used (source) | structural? | unit mass (cited) | steel g |
|---|---|---|---|---|---|---|---|---|
| F1 | hand board mounting screw | M2 (R1 §16 board area table: "3× M2 holes, Ø5 keep-out") | 3 per hand × 2 = **6** | not specified; A4-70 316L **[EST]** | hand board in forearm, both hands | **No** (PCB retention) | NBK SNSL-M2-6-SD, A4-70, L 6 mm: **0.15 g** (nbk1560.com SNSL-M2-SD table). Length 6 mm **[EST]**, since the stack fixing length isn't drawn | **0.90** |
| F2 | knee Elmo G-TWI drive mounting screw | **not in public data read** (G-TWI has "2 mounting holes", R1 §17.1) | 2 per drive × 2 drives/leg × 2 legs = **8** | not specified | knee drives on the femur-rear 6061 plate (R1 §17, R-062) | **No** (drive retention on spreader plate) | none (size unknown) | **unknown** |
| F3 | knee drive plate stand-offs | not specified | not specified | G10 or PEEK (R1 §17.1). **Not steel**, so not a candidate | same plate | No | – | 0 |
| F4 | TMP117 sensor tab screw | not specified | not specified ("screwed to the bracket", R1 §16.3) | not specified | shoulder-bay RP40 bracket, 2 bays | No | – | unknown |
| F5 | EtherCAT junction PCB stand-offs | not specified (≥ 5 mm stand-off, R1 §18.2l) | not specified | not specified | partition cold face, torso | No | – | unknown |

**Counted total: 14 fasteners** (F1 6 + F2 8). F3–F5 have no count in the design and aren't counted.

**Steel mass that could move to Ti (non-structural, cited): 0.90 g** (F1 only).
- F2 can't be massed until the G-TWI mounting-hole size is read from the drive drawing (MAN-G-TWIIG dimensions). 8 × M2 SHCS would be about 1.2 g, *but the size is not confirmed*, so it isn't booked.
- Electronics has **no structural fasteners**.

**Not listed (owned elsewhere, to avoid double count):**
- 4 × captive M2.5 per side on the knee panel (Industrial Design, KNEE_DRIVE_PANEL.md).
- HS100 clamp-resistor bolts to the shoulder bulkhead (Torso §15.1).
- RP40 straps (strap, not a threaded fastener; bracket owned by Arms/Torso).
- Drive mounts in actuator housings, pelvis and shoulder (Actuators).
