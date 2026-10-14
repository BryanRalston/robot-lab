# Shoulder impact pad (R-042): R2 honeycomb cartridge, RL Industrial Design, 2026-10-14
**P-number: P-051 (proposed). R-042 approves the pad and its cap but assigns no P-number; the highest P on main is P-050.** Numbers come from `shoulder_pad.py` → `shoulder_pad.json`. All [EST] until Materials confirms the foam data and Controls runs T-030.

## R3 (Controls 03fc980): design energy 265 J, not 220. Re-sized
- Peak force fixed at 8.3 kN design → 9.13 kN (548 N·m ≤ 550), so the **area stays 84 cm²**. Stroke 265/8.3 = 31.9 mm → **honeycomb 44 mm** (was 37).
- Plain (b2) at 265 J = 0.103 kg pair (+0.003 over the cap). **R3 pick: 5052 honeycomb 3.1 pcf, 80 w × 105 h mm (84 cm²) × 44 mm, EPP face 10 → 6 mm, 0.5 mm Al spreader, PC backing, sleeve: 0.1004 kg pair, i.e. AT the 0.10 cap with zero margin.** Stack 58 mm from the bulkhead (+3 vs R2; Controls: width OK, about 1° more lean).
- Coverage: Controls says contact lands at or slightly above the centre, and 10–15 mm below it when leaning hip-first. A 105 mm tall pad with its centre 5 mm below the shoulder axis keeps the ±15 mm contact band ≥ 37 mm inside the top/bottom edges. The spreader carries an off-centre load into the core. OK.
- (b1) 4.5 pcf (0.067) rejected now: its 68 mm square pad leaves only about 19 mm edge margin with the offset contact.
- **Arbiter:** item 4 of R-047 moves from −0.005 to **0.000**. If Materials' cited 3.1 pcf crush strength comes in below about 0.90 MPa, the pair goes over 0.10 → re-rule (2.3 pcf fallback 0.130, +0.030; R-047 total still −0.19 / −0.095 half-credit). Other options at 265 J: EPP (a) 143 mm, 0.160; hybrid (d) 0.111; 3003 3.1 pcf 0.111.

## R2 re-size (Materials 5f8f149, `materials/R042_EPP_SHOULDER.md`): R1 40 mm EPP 80 FAILS
R1 assumed a constant 0.65 MPa crush. On the real ARPRO 5170 curve (0.50/0.70/1.60 MPa at 25/50/75 %, rate ×1.45) 220 J peaks at about 19.5 kN → **≈ 1.17 kN·m vs 550 allowed**. Re-sized in `shoulder_pad.py` → `shoulder_pad.json`.
Requirement: 220 J at peak F ≤ 550/0.060 = **9.17 kN**. EPP: force checked at RT × rate, stroke at hot (40 °C pad face, ×0.70) × rate, up to 65 % strain. Honeycomb: pre-crushed, constant crush, stroke 0.72 t, rate ×1.10, designed at 8.3 kN → 9.13 kN peak (548 N·m). All masses include the PC backing (8 g, Materials), sleeve and 5 mm air gap to the 69 °C bulkhead in the stack. Honeycomb crush strengths are [EST] catalog-class values: **Materials to cite**.

| option | element | area cm² | thick mm | stack from bulkhead mm | pair kg | vs 0.10 cap | peak / moment | notes |
|---|---|---|---|---|---|---|---|---|
| R1 | EPP 80, 40 mm | 109 | 40 | 47 | 0.116 | +0.016 | ~19.5 kN / 1.17 kN·m | **FAIL** |
| (a) | EPP 80 | 51 | **119** | 126 | 0.136 | +0.036 | 9.17 / 550 | passes but +80 mm proud per side (shoulder width +160 mm): unacceptable envelope; single-use > 50 % strain |
| (b1) | 5052 HC 4.5 pcf + 10 mm EPP + 0.5 mm Al spreader | 46 | 37 (+10) | 55 | **0.061** | −0.039 | 9.13 / 548 | lightest; small footprint (~68 mm sq), weak to oblique hits > ~15° |
| **(b2)** | **5052 HC 3.1 pcf + 10 mm EPP + spreader** | **84** | **37 (+10)** | **55** | **0.095** | **−0.005** | **9.13 / 548** | **recommended**: ~92 mm sq covers the tuck contact; replaceable cartridge after a hard fall |
| (b3) | 5052 HC 2.3 pcf | 122 | 37 | 55 | 0.122 | +0.022 | 9.13 / 548 | over cap |
| (b4) | 5052 HC 1.6 pcf | 243 | 37 | 55 | 0.200 | +0.100 | 9.13 / 548 | over cap |
| (b5) | 3003 HC 3.1 pcf | 91 | 37 | 55 | 0.103 | +0.003 | 9.13 / 548 | marginal over |
| (c) | EPP 80 for 80 J (Controls cut) | 51 | 43 | 50 | 0.062 | −0.038 | 9.17 / 550 | needs Controls to cut shoulder energy 220 → 80 J (−64 %); not credible from A44 today |
| (d) | HC 3.1 core (200 J) + 15 mm EPP | 84 | 48 | 56 | 0.103 | +0.003 | 9.13 / 548 | EPP outer is multi-hit for small knocks; marginal over |

**Recommendation: (b2) 5052 honeycomb 3.1 pcf, 84 cm² × 37 mm, pre-crushed, in a replaceable cartridge (PC backing, 0.5 mm Al spreader, 10 mm EPP 80 cosmetic face, sewn sleeve), 0.095 kg pair (−0.005 vs cap).** Peak 9.13 kN = 548 N·m: it meets 550 with the only margin being the 10 % design factor. (b1) is the fallback if mass is tight and Controls confirms near-normal impact. Envelope: 55 mm proud of the bulkhead vs 47 mm in R1 (+8 mm per side).
- **Arbiter re-rule: not needed** if (b2) holds ≤ 0.10. It needs an Arbiter note that the pad is **single-use** (cartridge swap after a hard fall, T8 "replaceable pads"), and Materials must cite the honeycomb crush strength. If the cited 3.1 pcf crush strength is below about 0.85 MPa the area grows and the pair goes over 0.10 → re-rule.
- **Controls energy cut: not needed** for (b). Only option (c) needs it. Controls still has to confirm in T-030 that shoulder energy ≤ 220 J and that the impact is within about 15° of the pad axis.

## R1 analysis (superseded, kept for record)
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
