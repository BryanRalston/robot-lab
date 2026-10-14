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

## R-106 rev (2026-10-14): bearing-grade PTFE-filled PEI, design pressure ≤ 14.6 MPa, no metal bypass. PEEK HPV dropped.
Files: knee_trunnion_bush_r106.py → results/r031/knee_trunnion_bush_r106.json; knee_boss_clear_r106.py → knee_boss_clear_r106.json.
**k correction:** L61 used k_PEI = 0.12, which was wrong. Cited values:
- TECAPEI natural 0.21 W/mK (Ensinger, https://www.ensingerplastics.com/en/shapes/pei-tecapei-ef-natural)
- ULTEM 1010F 0.220 (SABIC via lookpolymers)
- TECAFLON PTFE 0.20 (https://www.ensingerplastics.com/en/shapes/tecaflon-ptfe-natural)
- PolyOne PI-30GF/15T (PTFE-lubricated PEI) ≥ 0.231
I found no published conductivity specific to a PTFE-filled PEI from Ensinger or SABIC, so I used design k = 0.231. For reference, TECAPEEK PVX is 0.82, which is why it was dropped.
Recomputed at the correct k, the L61 bush (ø9×12, 2 mm wall) gives only 22.7 K/W, and simply widening it 1.6× (ø11×16, 2 mm wall) gives 14.4 K/W. Both are below the 30 K/W target.
**Chosen design:**
- Steel pin ø11, hardened ≥ HRC 50, ground Ra ≤ 0.4 µm, greased.
- PTFE-filled PEI bush ø11/21 × 16 per side (5 mm wall).
- 3 mm PTFE-PEI thrust washer with 15 % pad contact.
- Cheek boss ø26 × 16, grown outward only, so the cheek's inner face stays at the L60 position.
Results:
- Pressure: 14.4 MPa design, 9.6 MPa walk (≤ 14.6 ✓). Bearing area d·L = 176 mm², which is 1.63× L61.
- Resistance: 63.8 K/W per side, **31.9 K/W joint** (≥ 30 ✓, small margin). No metal path: pin–bush–boss only. Bolts must not bridge the pin to the cheek; use a PEI-washered retaining clip.
- Fit: boss to finned rev B housing ≥ 9.0 mm over knee 0–135°. Cheeks are 3.04 mm and the top plate 3.54 mm (L60), unchanged. The 10 mm outward boss growth has not been checked against the thigh shell or the ID envelope (ID to confirm).
- **Mass: +27.5 g/knee, +0.055 kg robot [EST, ρ 1.4 g/cc assumed]**. That is +0.043 over L61's +0.012 and +0.051 over the +0.004 booked. FLAG: book in full; reserve is about −0.58 → about −0.63.
