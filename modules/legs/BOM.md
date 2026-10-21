# Legs BOM — fastener list (rev 2026-10-21)
No legs BOM file existed before this; mass lines remain in DECISIONS.md / results/*/structure_*.md and the Arbiter rollup. This file starts the BOM with the fastener list requested in `materials/R_SWAP_SCAN_R7.md` row 6. Counts per leg; robot = ×2. [EST] = inferred, not in CAD.

## Threaded fasteners
| # | location | size | /leg | /robot | grade / material | source |
|---|---|---|---|---|---|---|
| F1 | thigh split collar (clamp) | M6×30 SHCS | 2 | 4 | 10.9 steel | `hip_stop_r6.py` l.15 [EST in source] |
| F2 | hip-pitch femur upper lug interface | M6 (length n/a) | 8 | 16 | grade not stated [EST 12.9 steel] | DECISIONS.md L-(c) l.35 |
| F3 | knee housing split-C saddle | M4 (length n/a) | 4 | 8 | 8.8 steel | KNEE_THERMAL_NOTE.md §Clamp |
| F4 | foot box / ankle sensor steel flange, BC ø46 | ø5 shank → M5 [EST] | 6 | 12 | grade not stated [EST 12.9] | grokbuild/fea_r5.py l.548; STRUCTURE_FEA_REPORT.md l.37 |
| F5 | ankle roll stop blocks (A14) | M4×10 | 2 | 4 | not stated [EST 8.8 / A2-70] | a14_r7.py l.14/18; results/r7/a14.json |
| F6 | sole bumpers to foot-box end webs | M3 countersunk | 4 [EST: 2 bumpers × 2] | 8 | not stated | results/r081/SOLE_PAD_SPEC.md l.24 |
| **Σ** | | | **26** | **52** | M6 10, M5 6, M4 6, M3 4 per leg | |

## Inserts (cover attachment, threaded into legs structure)
| # | location | size | /leg | /robot | source |
|---|---|---|---|---|---|
| I1 | foot box web inserts (boot hem / foot shell) | M3 | 4 | 8 | DECISIONS.md l.268; ENVELOPES_FOR_ID.md l.30 |
| I2 | knee tongue neck block front face (knee cap) | M4 | unknown | unknown | ENVELOPES_FOR_ID.md l.28 (count not given) |

## Pins (not threaded; listed for the swap scan)
| # | location | size | /leg | /robot | material | source |
|---|---|---|---|---|---|---|
| P1 | thigh collar bond backup (L63-R) | ø7×10 m6, outer end tapped M3 | 8 | 16 | 42CrMo4 | results/a38/CROSS_PIN_BACKUP.md; grokbuild/l63_fea_brief.md |
| P2 | ankle pitch stubs | ø12 (ø6 bore, P-053) ×18+12 press | 2 | 4 | 42CrMo4 Q&T / 17-4PH | grokbuild/ankle_cross_fea_brief.md rev B |
| P3 | ankle roll pins | ø12 (ø6 bore) ×12 each side | 2 | 4 | same | same |
| P4 | stop-block dowels | size n/a | 2 | 4 | not stated | a14_r7.py l.18 |

## Removed / not counted
- L30 thigh pin panel 4× M3 quarter-turn + 2× M3 rear: deleted by ID P-053 rev2 (LOG 2026-10-20 22:55).
- L61 bolted trunnion break (M5/M6 options): rejected (results/a38/TRUNNION_BREAK.md).
- Actuator-owned hardware (knee/ankle screw mounts, lever pins) is in Actuators' files, not here.

## Gaps
- No fastener appears in any legs CAD script as a modelled part; all counts come from specs/notes. Lengths missing for F2–F4, grades missing for F2, F4–F6.
- Ti-swap candidates (non-structural): F6, I1/I2 and possibly F5. F1–F4 are structural; Ti-6Al-4V ≈ 8.8-class so F1/F2/F4 must stay steel if 10.9/12.9.
