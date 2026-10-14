# R-059: D76 wrist pitch/yaw under the ID fairing; shoulder-roll pad face (RL Thermal, 2026-10-14)
Hand calc `r059.py` → `results/r059.json`. 35 °C ambient. [EST] values are flagged; numbers are to be re-run once the Arms/Actuators duty torques and the ID CAD are fixed.

## (3) Wrist pitch/yaw (2 × TBM2G-05008 + CSG-14 / CSF-11) under the 124 × 70 fairing (z +23…+96, back/palm split)
**Model:**
- **Duty losses per motor:** carry ≈ 3 W, sustained ~10 N·m ≈ 6 W [EST]. Motor Kt/R are not in the D76 notes.
- **Fairing:** ≈ 0.026 m² (h 5 inside / 12 outside).
- **Motor housing:** to cavity air 1/(8 × 0.008 m²); to the forearm structure 6 K/W [EST].
- **Forearm shell:** 60 °C walking / 70 °C still air (A43C ladder).
- **Winding → case:** 1.5 K/W [EST].
- **20 % slots:** ram flow at 1 m/s, Cd 0.6, half effective; 40 % of that in still air.

| duty | closed, walk / still | 20 % slots, walk / still | limit |
|---|---|---|---|
| carry 3 W/motor | winding 77 / 85 °C, cavity 57 / 62 | 71 / 79, cavity 37 / 40 | target 120, trip 130, abs 155 |
| sustained 6 W/motor | **97 / 105 °C, cavity 66 / 71, housing 88 / 96** | 89 / 97, cavity 38 / 42, housing 80 / 88 | |

**Ruling:**
- **Venting is not needed for the windings**: closed still passes the 120 °C target by ≥ 15 K.
- **ID's provisional 20 % slots over each motor are adopted and enough.** They take the cavity air from ~70 °C down to ~40 °C. They also take the housing (AksIM-2 encoder, cable, CRBH grease) below ~90 °C in still air.
- Slots go on both the back and palm halves, with axial flow along z.
- Keep the slots clear of the palm grip face and the T5 touch zone. The fairing outer surface stays ≤ 45 °C with the slots.

## (2) Shoulder-roll housing at the R5 pad (y ≈ +0.30): cd5e88c stack
**Inputs:**
- **Shoulder_roll** (TBM2G-06813C + CSG-25-100) losses [EST]: carry ≈ 3.5 W, P-042 pose ≈ 2 W.
- **Housing:** R 3 K/W to air walking, 5 K/W still air, plus +5 K from the shoulder_pitch neighbour [EST].
- **Pad stack:** 3 mm PC saddle (k 0.2), 57 mm Al honeycomb (k ≈ 2 through-thickness [EST]), 6 mm EPP (k 0.04), outer h 10 (still air 6).

| case | housing at the saddle | EPP inner face | EPP outer face |
|---|---|---|---|
| carry, walking | 50.5 °C | **48 °C** | 40 °C |
| P-042 pose, walking | 46 °C | **44 °C** | 39 °C |
| carry, still air | 57.5 °C | **55 °C** | 45 °C |

**Verdict:** the EPP face is **≤ 50 °C walking (44–48 °C)**, within ID's 40–50 °C window, and ≤ 55 °C in still air. That is below the 60 °C EPP 50 %-crush-loss point, so **no gap or foil is needed**.
- The Al honeycomb conducts, so it gives no insulation; the 6 mm EPP takes the whole drop.
- If Materials wants ≤ 45 °C at carry, use a 3 mm PC saddle with a 2 mm stand-off rib pattern (vented), which adds ~+0.001 kg.
- G5: a thermocouple at the saddle.
