# T-031 (R-070, Controls e5f48c2): chest / front-torso contact model for the forward-fall gate
Gate (Controls `t030_pushfall.py --chest-k/--chest-zeta`): peak chest acceleration ≤ 38 g, which needs ~42 mm of stopping distance.
Fall mass used: **full robot 65.4 kg** (R-035 credible ~65.38) → F_max = 65.4 × 38 × 9.81 = **24.4 kN**. Energy at 42 mm and constant force: 24.4 kN × 0.042 = **1.02 kJ**.

## 1. Bare 2.0 mm CF shell. All values [EST]: no cited CF laminate data in MATERIALS_DB yet
- Laminate: quasi-isotropic CF/epoxy, E ≈ 50 GPa, ν 0.3 [EST]. D = E t³ / 12(1−ν²) = 36.6 N·m.
- Front panel 0.33 × 0.22 m, edges simply supported on the frame. Centre load gives w = α P b² / D with α ≈ 0.0165 (Timoshenko, a/b 1.5) → **k ≈ 46 kN/m** (linear, small deflection).
- Damage onset: point-load bending failure ~1–1.5 kN [EST] → **≤ ~10 mm before damage** (membrane stiffening beyond w > t makes the linear value approximate).
- Damping ratio **ζ ≈ 0.02** (structural CFRP) [EST].
- **Verdict: FAIL.** The 24.4 kN demand is ~20× the damage load. The bare shell cannot be the chest stop.

## 2. Chest crush layer: HexWeb CR III 5052, 4.5 pcf, pre-crushed, lot-certified
Spec reused from Materials `R042_EPP_SHOULDER.md` Parts 3–5 (953cd46): crush strength 1.79 MPa typical; dynamic factor 1.10–1.30; ×0.93 at 15° obliquity, ×0.73 at 25°; minimum stroke 70 % of thickness (Plascore/Hexcel class data). EPP 80 is avoided because it stiffens with strain.
- **Area** sized so the highest plateau (1.79 × 1.30 = 2.33 MPa, normal impact) stays ≤ 24.4 kN → **A = 0.0105 m² (≈ 100 × 105 mm pad over the sternum/bulkhead)**.
- **Plateau force band:**
  - 1.97–2.33 MPa × A = **20.7–24.4 kN** normal;
  - at 15°: 19.2–22.7 kN;
  - at 25°: 15.1–17.8 kN (larger stroke needed, see O-T11).
- **Stroke** for 1.02 kJ at the lowest normal/15° plateau (19.2 kN) → **53 mm** → **thickness 76 mm** (70 % usable stroke).
  - At 25°, 15.1 kN needs 68 mm: beyond this pad. Controls gate is set at ≤ 15°; flag O-T11.
- **For Controls (model as plateau, not spring):** F_plateau 20.7–24.4 kN, onset after ≤ 2 mm (shell + pre-crush), stroke available 53 mm, no rebound.
  - If the script needs k: **k_eq = F/d ≈ 0.58 MN/m (24.4 kN at 42 mm)** with **ζ ≈ 1.0** (fully dissipative, no rebound) [proxy only; a linear spring at this k absorbs only half the energy, so prefer the plateau].
- **Mass:** core 0.0105 m² × 0.076 m × 72 kg/m³ = **0.058 kg**, plus CF 1 mm load-spreading face + bonding ~0.020 [EST] = **≈ 0.078 kg**. The 0.065 kg energy-per-mass check: 1.02 kJ / 0.058 kg ≈ 17.6 J/g, consistent with 4.5 pcf honeycomb at 70 % stroke.
- **Envelope:** 76 mm proud of the 2 mm shell at the sternum is a large bump. It may sit partly inside the chest (behind a breakaway cover panel). ID/Arms to place (vents and shoulder bays are lateral, no clash).

## 3. Request to Arbiter (mass freeze, > 0.02 kg)
"RL Torso & Power requests +0.078 kg for a T-031 chest crush pad (HexWeb CR III 5052 4.5 pcf, 100 × 105 × 76 mm, pre-crushed, lot-certified, with a 1 mm CF face). The bare 2 mm CF shell fails the forward-fall gate (24.4 kN demand vs ~1–1.5 kN damage [EST]). The pad gives a 20.7–24.4 kN plateau over 53 mm, ≤ 38 g at 65.4 kg for impacts ≤ 15°. It is a replaceable wear part after a forward fall."
