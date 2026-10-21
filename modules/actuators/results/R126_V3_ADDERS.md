# R-126: v3 `actuator()` mass adders, content and double counts (Actuators D85, 2026-10-21)
Source line: `v3/analysis/v3.py` l.59 (rotary `... + PT.DRIVE['mass'] + 0.03 + 0.04`) and l.67 (linear `nut + shaft + 0.08 + Hs + 0.10 + encoders + DRIVE`, ×nmot = per motor side).

## Provenance (honest)
- `git log -L` and `git log -S"+0.03+0.04"`: both lines first appear in **3c7b50e (2026-10-12, "v3 WIP checkpoint")** with **no comment, no doc and no PARTS/REVISIONS entry**. No later commit touched them.
- Predecessor: v2 `design.py` l.45 `ACT_OVERHEAD = rotary 0.45 / linear 0.55 kg "housing, bearings, encoder, driver PCB" [ESTIMATE]`, later scaled by motor size (l.99–101). v3 split that flat overhead into explicit catalog items (housing(), CRBH, 2× AksIM-2 ring+head, DRIVE) and kept these four constants as the **residual, unlabelled**. Their content is therefore **inferred** from the position in the sum and from what v3 does not model elsewhere. No source states it.

## Per adder: inferred content and overlap with the current ledger
| adder | where | units | inferred content [EST] | already booked elsewhere? | double count |
|---|---|---|---|---|---|
| +0.03 rotary | after DRIVE | 4 leg rotary (hip yaw/roll) | bolts / flange hardware (v3 has no fastener line; the v3 CAD README lists bolts in the model) | **legs: yes.** `size.py` l.134 replaces only the v3 housing with CAD; the +0.03 stays, and `cad_mass` FAST is added on top. The +0.517 (R-123c) then replaced the FAST screws by the counted BOM | **0.12** (4 × 0.03) |
| +0.03 rotary | same | 10 arm/waist v3-basis units | same | **no.** The +0.875 (R-125/D84) was computed as counted − booked, with these 0.03 taken as the booked fasteners | 0 |
| +0.04 rotary | after +0.03 | 14 v3-basis rotary (4 leg + 10 arm/waist); 18 if neck and wrist roll are also on v3 rows (R-126 count) | per-joint cabling/connectors (local leads, drive connector) | **yes:** `harness.json` (1.984 kg) carries per-drive local phase leads (32 × 3 × 0.5 mm² × 0.06 m), encoder/thermistor leads, drive pigtails, XT30U tees ×40, JST-GH ×108 | **0.56** (14) … **0.72** (18) |
| +0.08 linear | after nut+shaft | 12 leg motor sides | screw support bearings: 2 × 7202 angular-contact pair (cad_mass.py l.33 seats them, ~0.045 kg each [EST, SKF typical; not cited in repo]) | **no.** The 7202 pair has no other mass line (LINKAGE_TABLE: hubs, pins, eyes, levers only) | 0 (keep) |
| +0.10 linear | after housing | 12 leg motor sides | linkage/end hardware (rod-end, trunnion, hub), or rotor support bearing + encoder mount [unknown] | **probably yes.** R-015/LINKAGE_TABLE (`results/LINKAGE_TABLE.md`) books hubs ×6/leg, trunnion pairs, GE 12 E eyes ×6 and levers explicitly, "actuator housings exclude everything above". Nothing removed the 0.10 when that table was added | **≤ 1.20** |
| leg FAST connector allowance | `cad_mass.py` l.89 (0.015 rotary, 0.010 linear) | 4 + 12 | connector | **yes:** harness connectors (above) | **0.18** |
| DRIVE 0.038 | `parts.py` l.52, Novanta Everest XCR placeholder | 32 | drive | selected drive is Elmo Gold Twitter G-TWI R70/100 EtherCAT: **22.2 g without heatsink, 43.2 g with** — `datasheets/elmo_gold_twitter_install_guide.pdf`, MAN-G-TWI v2.011, **p.10** (technical data table) | **−0.506** (32 × 0.0158) if no Elmo heatsink (drives on the R-066 plate / housing). With the Elmo heatsink: +0.166 |
- Encoders: v3 books 2 × (0.016 ring + 0.005 head) per unit; no other encoder mass line exists (harness has only the leads). **No double count.**
- Electronics/Thermal rows (R-066 knee drive plate 0.010, knee fins rev B, harness): none repeat an adder. **No double count.**

## Totals
| item | full kg | basis | recommended credit now |
|---|---:|---|---:|
| Elmo drive mass (cited, p.10) | −0.506 | cited | **−0.506** (full), conditional: no Elmo heatsink (Thermal/Electronics confirm plate mounting) |
| leg FAST connector allowance vs harness connectors | −0.180 | code + harness BOM | **−0.180** (full: both lines are explicit in code) |
| +0.04 rotary vs harness | −0.56 (to −0.72) | inferred | −0.28 (half, 14 units); +0.08 more if neck/wrist roll are on v3 rows |
| +0.10 linear vs LINKAGE_TABLE | −1.20 | inferred | −0.60 (half) |
| +0.03 leg rotary vs +0.517 | −0.12 | inferred | −0.06 (half) |
| +0.08 linear (7202 pair) | 0 | likely real content | 0 |
| **Total** | **−2.57 (to −2.73)** | | **−1.63 now** |
- Robot Lab's "up to ~2.9" is the upper bound if the +0.08 were also phantom. I find it is probably the 7202 bearings, which are booked nowhere else, so it stays.
- Full credit on the inferred lines needs a bottom-up per-unit CAD/BOM table (motor, gear, bearings, encoder, drive, fasteners, linkage), replacing v3 `actuator()` for every unit. I can produce it from the existing catalog data and cad_mass in one round.
