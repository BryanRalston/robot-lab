# T-031 rev 2 (resize for the 38 g gate at ≤ 23 kN ceiling)
Basis: Materials' plateau, 1.79 MPa typical × lot band and dynamic factor 1.10–1.30, obliquity ×0.93 at 15°. Controls' current pad (0.0105 m²) gives 19.4–24.4 kN at 0° → 39 g at ~64 kg if full mass loads it.
## Pad (HexWeb CR III 5052, 4.5 pcf, pre-crushed, lot-certified)
- **Face 98 × 98 mm = 0.009604 m²** → ceiling 2.327 MPa × A = **22.35 kN** (≤ 23 kN). At 64 kg that is 35.6 g; at 65.4 kg, 34.8 g.
- **Plateau band** (Materials' band scaled by 0.9147):
  - **0°: 17.7–22.3 kN**
  - **15°: 16.6–20.8 kN**
- **Energy:** 65.4 kg × 38 g × 42 mm = 1.02 kJ, the Controls gate basis (conservative for 64 kg).
- **Stroke** at the lowest band (15°, 16.6 kN): **62 mm** → **thickness 88 mm** (70 % usable stroke). At 0° lowest: 58 mm.
- **Pad core mass:** 0.009604 × 0.088 × 72 kg/m³ = **0.061 kg**.
## Backing (sized at 22.35 kN × 1.5 = 33.5 kN)
- **Sandwich panel 100 × 100 mm:** CF QI faces 1.5 mm each [EST E 50 GPa, ~500 MPa] on a 10 mm Al honeycomb core (Plascore CrushLite 8.1 pcf, 700 psi = 4.8 MPa crush ≥ 1.5 × 2.33 MPa pad pressure, cited Plascore sheet). Edge-supported on the chest shell frame / pack-bay front rails.
- **Strength:** M = P·L/8 = 33.5 kN × 0.1 / 8 = 419 N·m → face stress 419 / (0.1 × 0.0015 × 0.0115) = **243 MPa (SF ≈ 2 vs 500 MPa [EST])**. Core crush 3.5 MPa < 4.8 MPa.
- **Stiffness:** EI = E·t_f·h²/2 × b = 496 N·m² → k ≈ 48 EI / L³ = **24 MN/m**, **≈ 45× the pad's equivalent 0.53 MN/m (22.35 kN / 42 mm)**. Deflection at the ceiling ≈ 0.9 mm (< 2 % of stroke): negligible.
- **Mass:** faces 2 × 0.01 m² × 1.5 mm × 1550 = 0.047 + core 0.01 × 0.010 × 130 = 0.013 + adhesive ~0.010 [EST] = **0.070 kg**.
## Totals and request
Pad 0.061 + backing 0.070 = **0.131 kg** vs 0.078 accepted (R-079) → **+0.053 kg: over the 0.02 freeze → Arbiter request.**
Lighter alternative to cut it: back the pad directly on the pack enclosure front face if Torso and Pack can make it a stiff 6061 cap (already in the pack line), dropping the sandwich → +0.0 kg net (pad 0.061 < 0.078). Needs the pack enclosure check (O-T14).
For Controls: plateau 17.7–22.3 kN (0°) / 16.6–20.8 kN (15°); stroke 62 mm usable; no rebound; k_eq 0.53 MN/m with ζ ≈ 1 only if the script needs a spring.
