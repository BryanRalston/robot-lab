# R-047 cover offsets: Arbiter-ready itemized list (RL Industrial Design, 2026-10-14)
Target: ≥ 0.08 kg of cited or calculated offsets (reserve about 0.22 vs the 0.30 floor). Script `cover_trims_r047.py` → `cover_trims_r047.json`. Basis: `cover_set_v5.json` (trimmed, areas [EST], measured: false), PC ρ 1.20; skin mass = formed area × average finished wall.

| # | item | Δ kg | evidence |
|---|---|---|---|
| 1 | **P-026 louvres, 30 % open area, cut slots** on thigh fairing (0.427 skin) + knee cap (0.131), **plus the knee-housing front grille** (115 × 110 mm/side, 60 % open, Legs 6f53d77) | **−0.154** | calc: 0.557 × 0.30 × (1 − 0.15 allowance for slot rims/ribs) = −0.142; grille 2 × 0.0127 m² × (0.60 − 0.30) × 1.8 kg/m² × 0.85 = −0.012. R-030 already requires ≥ 30 % open over hip-pitch/knee. Slots must be **cut** (CNC trim); formed-only louvres save nothing. Final slot pattern follows Thermal A35. |
| 2 | **PC 1.2 mm average wall** (post-form minimum 0.9 mm) on low-draw panels: thigh outboard (≤ 1.5:1, 0.149 after louvres) + foot top (≤ 1.5:1, 0.171) | **−0.064** | calc: 0.320 × 0.3/1.5, the Materials REVIEW_R1 (a) basis. Thinning: low draw keeps min/avg ≈ 0.75 [EST] → 0.9 mm min; spec that post-form minimum on the drawing. Stiffness: bending stiffness ×0.51 (t³), so 2 formed ribs on the thigh outboard; the foot top is EPP-backed. **Dent check open** (Materials A15). Thigh front (2:1) and knee cap (2.5:1) stay 1.5 mm. Materials' −0.231 was on the old 0.643 m² full basis; after the trims and the shin deletion only these panels qualify. |
| 3 | **Printed small parts:** hip-skirt rim strips PC 1.5 → PA12 MJF 1.2 mm | **−0.013** | calc: 0.040 × (1 − 1.01·1.2 / 1.20·1.5). No-printing is a crew preference, not a Bryan rule (R-027 item 2). |
| 4 | **Shoulder pad netting:** R5 shoulder-cap cartridge 0.097 vs R-054 booked 0.100 | **−0.003** | `shoulder_pad.json`; honeycomb crush strength still to be cited by Materials |
| | **Total** | **−0.234** | **−0.117 at R-040 half-credit (R-054 accepted −0.118 on R4) (covers unmeasured)**: meets ≥ 0.08 either way |

Conditions: items 1–2 need the A29 CAD measurement to convert to full credit; item 2 needs the dent check; item 1 needs A35 confirming that 30 % cut slots are enough (if Thermal wants more open area, the saving grows). Nothing here adds mass. If the shoulder pad's cited crush strength forces it over 0.10, item 4 flips sign (at most about +0.022 with the 2.3 pcf fallback); total still ≥ 0.08.

**Not included (Arbiter decision):** shin fairing add-back after Legs 6f53d77 withdrew the no-cover zone: +0.300 PC / +0.227 PC louvred / +0.260 CF / +0.198 CF louvred (pair). Adding it would consume the offsets above.

R-054: trims accepted at −0.118; shin deferred until D69 rev B, louvred CF (+0.198) preferred at add-back.
