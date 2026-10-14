# D69C: knee housing fins, option C check (RL Thermal, 2026-10-14)
Checks Actuators 4366d32 (D69 rev B: 2× TBM2G-07613D, drives on the housing, +0.05 m² fins at h 12, η = 1) against the Legs 6f53d77 / L48 envelope (`legs/results/r031/knee_fin_envelope.json`).
Hand calc `d69c_knee_fins.py`, `results/d69c_knee_fins.json`.
- **Fins:** straight rectangular fins, η = tanh(mLc)/mLc.
- **Winding temperature:** taken from Actuators' table by fitting T = 35 + K/(G0 + 12·A_eff) per case. The fit reproduces 0.07 m² carry-open at 105 vs their 107 °C.
- **Housing:** r 45 mm and 90 mm active fin length are [EST], pending the CAD.

## (1) Fin efficiency: η = 1 is a fair assumption at these lengths (error ≤ 4 %)
| fin length | 6061-T6 t 1.5, h 12 / 15 / 20 | 7075-T6 t 1.5 | 6061 t 1.0 |
|---|---|---|---|
| 9 mm | 0.997 / 0.996 / 0.995 | 0.996 / 0.995 / 0.994 | ≈ 0.99 |
| 12 | 0.995 / 0.994 / 0.991 | 0.993 / 0.992 / 0.989 | ≈ 0.99 |
| 25 | 0.979 / 0.974 / 0.966 | 0.974 / 0.967 / 0.957 | ≈ 0.96 |
| 28 | 0.974 / 0.968 / 0.958 | 0.967 / 0.960 / 0.947 | ≈ 0.95 |
| 57 | 0.906 / 0.885 / 0.854 | 0.882 / 0.858 / 0.821 | 0.867 / 0.840 / 0.799 |
- **What their model leaves out:** the base area under the fin roots, n·t·L_fin, is already counted in G0. For 12–14 fins that is −0.001 to −0.003 m².
- **Correction:** to get the same result as their 0.05 m², use **≈ 0.053 m² gross with 25 mm fins** (≈ 0.056 with 57 mm fins).
- **Fin pitch:** keep the gap ≥ 5 mm so h holds at walking airflow.

## (2) Mass
- 0.05 m² net, rear only, 12 × 25 mm × 1.0 mm 6061 fins: 0.073 kg plus ≈ 0.01 kg base boss ⇒ **≈ 0.085 kg per knee**. That matches Actuators' ~0.09. At 1.5 mm thick it is 0.12 kg.
- **Legs' 0.05 kg/knee booking is too low.** Book **0.09 kg/knee (+0.08 kg robot vs the booking)** for the 0.05 m² design.
- The recommended 0.07 m² layout below is **≈ 0.11 kg/knee** at 1.0 mm.

## (3) Layout within the envelope (no side fins)
- **Envelope by sector:**
  - 060–120 and 240–300 (the sides, at the RV12 rods): **0**.
  - Front 330–030: 12 mm.
  - Bracket faces 030–060 / 300–330: 7.6 mm. Skip them; with a 3 mm margin they are not worth it.
  - **Rear 120–240: 28–30 mm.**
- **Layout:** axial fins along the screw axis, aligned with the A35 airflow path.
  - **Rear: 14 fins × 25 mm tall** (3 mm under the 28 mm limit), 1.0 mm thick, pitch ≈ 6.7 mm over the 94 mm arc.
  - **Front: 7 fins × 9 mm.**
  - About 0.074 m² gross, **0.070 m² effective** after η and root loss.
- **The 57 mm mid-length allowance is not used.** The JSON gives only the minimum per sector. Taller mid-length fins (η ≈ 0.88) are a later option once Legs gives the clearance along the length.

| design | walk open | carry +10 % open | walk vented | carry +10 % vented | vs 120 target / 130 trip |
|---|---|---|---|---|---|
| Actuators 0.05 m² (η = 1) | 96 | 116 | 87 | 104 | pass, 4 K margin on carry open |
| **0.05 m² net, rear 12 × 25 mm** | 96 | 116 | 87 | 104 | pass, mass 0.085–0.09 kg |
| **recommended 0.070 m² (rear 14 × 25 + front 7 × 9)** | **88** | **105** | **81** | **95** | **pass, ≥ 15 K margin**, 0.11 kg |

## Covers
Closed covers fail (Actuators), so the **knee must be vented to A35** (louvres ≥ 30 % open, inlet ≥ 50 cm², outlet ≥ 60 cm², axial flow over the fins) or left uncovered. P-022 knee cap stays non-closing. The fins should face the inlet/outlet path; they must not end up inside a sealed pocket.

## Recommendation
- If carry +10 % open is a design case, use the 0.070 m² layout, which keeps ≥ 15 K margin under the 120 °C target. Book 0.11 kg/knee.
- The minimum is 0.05 m² net, booked at 0.09 kg/knee.
- Either way the Legs 0.05 kg booking must rise.
