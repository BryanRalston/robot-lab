# L61 — Knee trunnion thermal break (Thermal ec50e4e) [EST, hand calc: knee_trunnion_break_l61.py → results/r031/knee_trunnion_break_l61.json]
Loads: screw force 3364 N walk / 5053 N design (240 N·m ÷ 47.5 mm). Bracket offset 148 mm → 692 N·m on the bracket–femur joint → 8.66 kN couple at 80 mm spacing.
## Thermal's ask: bolted break at the bracket strut / top plate joints with PEI + Ti limiters, ≥ 30 K/W — not feasible
- With M5 Ti bolts and Ti limiters (7/5.5 × 25) at 4 kN preload: 2 bolts per joint gives 43.8 K/W but no slip capacity and the joint separates. 3 per joint gives 29.2 K/W but slip capacity 1.0 kN vs 2.5 kN shear. 6 per joint passes slip but gives 14.6 K/W.
- A load-capable joint (6 × M6 10.9 per joint at 10 kN) gives 1.8 K/W.
- So a bracket joint that carries the screw load cannot reach 30 K/W.
## Proposed instead: PEI plain bushes on the knee trunnion pins
- Bush: PEI ø9/13 × 12 mm per side, plus a 2 mm PEI thrust washer (30 % pad contact). Steel ø9 pin. Cheek boss ø18 × 12.
- Bearing pressure 15.6 MPa walk / 23.4 MPa design, inside the 28 MPa sustained and 76 MPa fault limits.
- R: bush 98 K/W per side, washer 804 per side → **43.8 K/W joint** (≥ 30 ✓). Leaves margin for pin contact.
- Mass +6.2 g/knee, **+0.012 kg robot** (Thermal accepted +8.6 g; this is +3.7 g over, net additions > 0.005 must be flagged → FLAG).
- No Ti limiters or extra bolts. The bracket stays a solid Al part.
- Open items:
  - Materials: wear of PEI vs steel under ±6° oscillation (is a PTFE-filled PEI grade needed?).
  - Thermal: the rod → lever → pin → clevis path is unchanged. The lever-eye sleeve stays a reserve option if collar R > 12 K/W.
