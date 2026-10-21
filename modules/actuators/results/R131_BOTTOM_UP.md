# R-131 bottom-up mass table, 32 driven units (Actuators D88, 2026-10-21)
Script `r131_bottom_up.py` → `results/R131_BOTTOM_UP.json`. Every line has one source; each item appears once across the ledger.

## Sources per line
| line | source | appears in ledger as |
|---|---|---|
| motor (rotor + stator, frameless) | TBM2G catalog (`v3/analysis/tbm2g.json`, parts.py) | v3 actuator() / sizing.json (legs), once |
| gear (CSG set / RV12 nut + shaft) | HD catalog weight row; RV12 calc (v3) | same, once |
| output bearing | IKO CRB catalog (parts.py CRBH) | same, once (shoulder roll: R-120/R-121 7013 delta) |
| encoder 2 × AksIM-2 (ring 16 g + head 5 g) | RLS datasheet (parts.py ENC); wrists 9.7 g (D70) | same, once |
| housing | CAD × density (legs, cad_mass.py); v3 housing() ×1.25 [EST] (arms/waist, no CAD); D70 0.06 [EST] (wrists) | once |
| fasteners | `fastener_bom.json` (counted) | R-123 +0.517 (legs), R-125 +0.875 (arms/waist); replaces cad_mass FAST screws and v3 +0.03 |
| support bearings (screws) | 2 × 7202 pair 0.09 [EST] | v3 +0.08 (kept) |
| rotor support bearing (screws) | 6805-class 0.022 [EST] | inside v3 +0.10 (the only real content found) |
| output hub (rotary) | 7075 disc calc [EST] | inside v3 +0.04 (the only real content found); shoulder roll hub is in Arms R13 |
| linkage (hubs, pins, eyes, levers) | `LINKAGE_TABLE.md` | linkage line, once; v3 +0.10 is the duplicate |
| connectors + leads | `harness.json` 1.984 kg (all 32 drives: phase/encoder leads, pigtails, XT30U, JST-GH) | harness line, once; cad_mass FAST connector allowance and v3 +0.04 are duplicates |
| drive | Elmo G-TWI 22.2 g, MAN-G-TWI v2.011 p.10 | v3 DRIVE 0.038 placeholder (26 units); **wrist D70 units book no drive** |

## Per unit (kg, bottom-up, one unit)
| unit | n | basis | motor+gear+bearing | housing | enc | drive | fasteners | out hub | support brg | rotor brg | **unit total** |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| hip_yaw | 2 | v3 actuator() + CAD housing (sizing.json) | 0.6032 | 0.2145 | 0.0420 | 0.0222 | 0.0792 | 0.0267 | — | — | **0.9878** |
| hip_roll | 2 | v3 actuator() + CAD housing (sizing.json) | 1.0292 | 0.2264 | 0.0420 | 0.0222 | 0.1222 | 0.0267 | — | — | **1.4687** |
| hip_pitch (per motor side) | 4 | v3 actuator() linear + CAD housing (sizing.json) | 0.5298 | 0.1531 | 0.0420 | 0.0222 | 0.0347 | — | 0.0900 | 0.0220 | **0.8938** |
| knee (per motor side) | 4 | v3 actuator() linear + CAD housing (sizing.json) | 0.5298 | 0.1531 | 0.0420 | 0.0222 | 0.0347 | — | 0.0900 | 0.0220 | **0.8938** |
| ankle_pitch (per motor side) | 4 | v3 actuator() linear + CAD housing (sizing.json) | 0.4038 | 0.1875 | 0.0420 | 0.0222 | 0.0347 | — | 0.0900 | 0.0220 | **0.8022** |
| waist_yaw | 1 | v3 actuator() row | 0.5790 | 0.3022 | 0.0420 | 0.0222 | 0.0792 | 0.0185 | — | — | **1.0431** |
| waist_pitch | 1 | v3 actuator() row | 0.8980 | 0.3259 | 0.0420 | 0.0222 | 0.1222 | 0.0185 | — | — | **1.4288** |
| shoulder_pitch | 2 | v3 actuator() row | 0.9860 | 0.3797 | 0.0420 | 0.0222 | 0.1222 | 0.0267 | — | — | **1.5788** |
| shoulder_roll | 2 | v3 actuator() row | 0.8240 | 0.2688 | 0.0420 | 0.0222 | 0.1222 | 0.0000 | — | — | **1.2792** |
| shoulder_yaw | 2 | v3 actuator() row | 0.4390 | 0.2260 | 0.0420 | 0.0222 | 0.0792 | 0.0119 | — | — | **0.8203** |
| elbow | 2 | v3 actuator() row | 0.5490 | 0.1983 | 0.0420 | 0.0222 | 0.0697 | 0.0067 | — | — | **0.8879** |
| wrist_roll | 2 | D70/D76 unit dict (d70_wrist_rotary.py) | 0.2510 | 0.0600 | 0.0097 | 0.0222 | 0.0462 | 0.0046 | — | — | **0.3937** |
| wrist_pitch | 2 | D70/D76 unit dict (d70_wrist_rotary.py) | 0.2510 | 0.0600 | 0.0097 | 0.0222 | 0.0462 | 0.0046 | — | — | **0.3937** |
| wrist_yaw | 2 | D70/D76 unit dict (d70_wrist_rotary.py) | 0.2510 | 0.0600 | 0.0097 | 0.0222 | 0.0462 | 0.0046 | — | — | **0.3937** |

Units: 32. Linkage (legs) is the LINKAGE_TABLE line; harness 1.9841 kg is one line for all units.

## True overlap vs the v3 adders and cad_mass allowances (full credit, kg)
| item | overlap | how |
|---|---:|---|
| v3 +0.03, leg rotary ×4 | −0.12 | fasteners counted in BOM (+0.517) |
| v3 +0.04, 14 rotary | −0.326 | 0.04 − output hub per unit (hub is real; shoulder roll hub in Arms R13 → full 0.04) |
| v3 +0.10, 12 screw sides | −0.936 | 0.10 − rotor bearing 0.022; linkage in LINKAGE_TABLE |
| v3 +0.08, 12 screw sides | 0 | 7202 pair 0.09 ≥ 0.08, real |
| cad_mass FAST connector allowance (legs) | −0.18 | harness connectors |
| **adders subtotal** | **−1.562** | |
| drive 0.038 → 0.0222 on the 26 booked units | −0.411 | cited |
| wrist drives booked nowhere (6 × 0.0222) | +0.133 | addition, cited |
| **total** | **−1.84** | |

## Versus R-131
- R-131 booked −1.536 now (drive −0.506 on 32 units + adders −1.03 at half). Bottom-up final: **−1.84 kg full** → a further **−0.304 kg**.
- Lower than the −2.57…−2.73 upper bound because the bottom-up finds real content in the adders (output hubs, rotor bearings) and finds 6 wrist drives with no mass line (the R-131 drive credit assumed 32 booked).
- **Flag, likely adverse (not in this credit):** the v3 shoulder_roll row books CRBH 4010 A (0.15 kg). R-120 booked the 7013 as +0.100 pair against a 6013 (0.33). If the ledger still carries the v3 4010, the true 4010 → 7013 delta is +0.23/side, so **+0.36 kg pair is under-booked**. Arms/Arbiter to confirm against Arms' bearing ledger.
- [EST] items: arm/waist housings (no CAD), output hubs, rotor and 7202 bearings. They are real content kept in the ledger, so the credit does not rest on them except the hub/rotor-bearing subtractions (conservative: they reduce the credit).
