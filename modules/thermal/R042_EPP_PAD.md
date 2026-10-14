# R-042: EPP shoulder pad next to the 69 °C shoulder bulkhead (RL Thermal, 2026-10-14)
1-D hand calc per m² (`r042_epp.py`, `results/r042_epp.json`). Bulkhead 69 °C (A43 sign-off value), 35 °C ambient, EPP 30 mm (T8/v3 basis) k 0.04, gap air k 0.028 (conduction; no convection cells ≤ 10 mm), radiation ε_EPP 0.9, bulkhead ε 0.85 (anodised/painted) or 0.05 (low-e foil). Outer h incl. radiation: walking 15, still air 7 W/m²K. Contact R 1e-4 m²K/W.

| gap | bulkhead ε 0.85, walk / still | low-e foil, walk / still |
|---|---|---|
| direct contact | **69.0 / 69.0 °C** | 69.0 / 69.0 |
| 3 mm | 66.6 / 66.8 | 65.2 / 65.5 |
| 5 mm | 66.0 / 66.2 | 63.3 / 63.7 |
| 10 mm | 65.2 / 65.5 | 59.7 / 60.3 |

**Finding:** 30 mm EPP is such a good insulator (R 0.75 m²K/W) that a *sealed* air gap barely helps; the face sits within ~4–10 K of the bulkhead. **No sealed gap (even 10 mm with foil) meets ≤ 55 °C.** Materials' ≥ 5 mm gap alone fails (66 °C).

**Recommendation (to keep the face ≤ 55 °C):**
1. **Ventilated gap**: ≥ 5 mm stand-off ribs with the gap open top and bottom (or to the A35/torso duct) so ambient air sweeps it. With gap air ≤ 45 °C and h ≈ 5 W/m²K each side [EST], the face is ≈ 47–50 °C. Combine with low-e foil (Al tape, ε ≤ 0.1) on the bulkhead for margin in still air.
2. Or move the pad off the bulkhead footprint / mount it on the PC cover with the bulkhead area left as a vent window.
3. If neither: specify an EPP grade/sizing for the 50 % crush-stress loss at 60–69 °C (Materials), since it will run hot.
Bench: thermocouple on the pad face, G5.
