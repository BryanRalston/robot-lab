# Shoulder impact pad, 40 mm (R-042), RL Industrial Design, 2026-10-14
**P-number: P-051 (proposed). R-042 approves the pad and its cap but assigns no P-number; the highest P on main is P-050.** Numbers come from `shoulder_pad.py` → `shoulder_pad.json`. All [EST] until Materials confirms the foam data and Controls runs T-030.

## Basis (Controls A44, `controls/fall/A44_side_fall.md`)
- Side fall from standing at 66.21 kg: E = m·g·0.98 = **637 J**. With the A44 strategy (knee drop, arm tuck, hip-first lean), shoulder energy is capped at **220 J**.
- Constant-force crush over s = 0.7·t + 3 mm (v3 `fall_model`). Bearing moment = F × 60 mm.
- 30 mm pad: s 24 mm → F 9.17 kN → **550 N·m**. **40 mm pad: s 31 mm → F 7.10 kN → 426 N·m**, i.e. **−22.6 %** at the same energy (R-042 asks for about 23 %). That is a CRBH 7013 radial SF of about 1.28 × 550/426 ≈ **1.65** if T-030 confirms the 220 J.

## Foam choice (pad sized so plateau stress × area = 7.10 kN)
| foam | ρ kg/m³ | plateau MPa [EST] | area cm² | kg/pad |
|---|---|---|---|---|
| EPP 45 | 45 | 0.30 | 237 | 0.043 |
| EPP 60 | 60 | 0.45 | 158 | 0.038 |
| **EPP 80 (pick)** | 80 | 0.65 | **109** | **0.035** |
| EVA 100 closed-cell | 100 | 0.55 | 129 | 0.052 |
| PORON-class PU 240 | 240 | 0.50 | 142 | 0.136 |

Why EPP 80: lightest per joule of the options, flat crush plateau (so the constant-force model holds), and it **recovers** for multi-hit use (T8: ≥ 1 fall/day on replaceable pads). PORON and EVA are comfort/vibration foams: too heavy, and they bottom out early. A pad bigger than 109 cm² would stop it reaching the plateau: crush force stays near 7.1 kN only if the area is right.

## Geometry and mounting (minimal carrier; arm shells deferred to Arms R2)
- Pad: 40 mm EPP 80, about 105 × 105 mm footprint (109 cm²), domed outer face, on the lateral face of the shoulder roll housing / bulkhead. It sits in the A44 arm-tuck footprint (the upper arm sits inside it).
- Carrier: **no rigid shell.** A sewn TPU-coated nylon sleeve (0.03 m², 9 g) with the pad moulded around 2× M4 inserts (6 g incl. a 25 mm hook-strap anchor), bolted to existing bulkhead tapped holes. No new holes in FEA'd parts; bulkhead hole pattern to be confirmed with Torso.
- It must not cover the shoulder-bay vents (≥ 25 cm² in/out, Electronics/Thermal A43) or press on the RP40 gap-pad strap.
- Replaceable in about 2 min (2 screws). Pads are a wear part after a hard fall (R-021 basis).

## Mass
Foam 0.035 + sleeve 0.009 + inserts/anchor 0.006 = **0.050/side, 0.100 kg pair = at the R-042 cap (0.10)**. **No margin:** if Materials' EPP 80 plateau comes in below about 0.6 MPa, or the sleeve is heavier, the pair goes over 0.10 and returns to the Arbiter. Fallback: EPP 60 at 158 cm² (0.038/pad) gives 0.106 pair. Listed in `cover_set_v5.json` as its own row, outside the P-020/P-022..025 delta.

## Questions for RL Materials (89a94197)
1. EPP grade: the cited compressive plateau for EPP 80 g/L (ARPRO / Neopolen) at 25–60 % strain, and the densification strain (the model needs about 78 %).
2. Multi-hit: recovery and plateau loss after 10 / 100 hits at 220 J; strain-rate factor at about 3–4 m/s impact.
3. Moulded-in M4 inserts in EPP 80: pull-out strength, or do we need a bonded PC backing plate (+about 8 g)?
4. Temperature: plateau at 0 °C vs 40 °C next to a shoulder bulkhead at about 69 °C (A43). Is EPP OK at that contact temperature?
5. Add EPP 80 (and the sleeve fabric) to MATERIALS_DB; EPP grade is [UNKNOWN] there today.

## Questions for RL Controls (c5cee5de)
1. T-030: please model the pad as 40 mm, s = 31 mm, constant force 7.10 kN (109 cm² × 0.65 MPa), and report the shoulder share and peak bearing moment against 550 N·m.
2. Is the contact point during the arm tuck on the lateral shoulder face (pad centre) or higher on the deltoid? If it's higher, the pad moves.
3. Does the 40 mm pad (about 10 mm more lateral) change the topple geometry or the knee-drop timing?
4. What sensitivity to shoulder energy above 220 J should we design for (worst-case push)?
