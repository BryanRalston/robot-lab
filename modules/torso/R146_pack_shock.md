# R-146: pack shock allowables vs chest-pad / prone-landing demand (Torso, 2026-10-21)

## 1. Cited cell and pack ratings
| Item | Value | Source |
|---|---|---|
| P45B cell shock (spec) | **150 g, 6 ms half-sine**, 3 shocks per direction, 6 directions (18 total); no leak, vent, rupture or fire; OCV ≥90 % | Molicel cell spec INR21700P45B: https://www.rotorama.com/assets/docs/980676faf74edb56f615f314dd6e3c2c/30769-1/en-datasheet-p45b.pdf (plus copy at cdn03.plentymarkets.com …/p45b-datasheet.pdf) |
| P45B UN 38.3 T4 | **PASS** (cell, 150 g / 6 ms) | Molicel test report: https://www.molicel.com/wp-content/uploads/Q1201-UN-P45B-4.35Ah-R7A1-TW2305060-001.pdf |
| P45B crush / drop (spec) | crush ~13 kN between flat plates: no fire; 4 ft drop onto concrete, 3× each orientation | same Molicel spec |
| UN 38.3 T4 rule | Cells: 150 g / 6 ms (large cells >500 g may use 50 g / 11 ms; P45B is 70 g, so small). Batteries: small (≤12 kg) min(150, √(100850/m)) g, 6 ms; large (>12 kg) min(50, √(30000/m)) g, 11 ms | UN Manual of Tests and Criteria §38.3.4.4: https://www.prba.org/wp-content/uploads/Sub-section-38.3-UN-Manual-6th-Revised-Edition-with-corrections.pdf |
| **Our pack T4 level** | 8.75 kg (small battery): √(100850/8.75) = **107.4 g, 6 ms**, Δv = (2/π)·107.4·9.81·0.006 = **4.0 m/s** | [CALC] from the rule above |
| IEC 62133-2 | no mechanical-shock test (it relies on UN 38.3) | **unknown; not verified against the standard text** |
| UL 2580 / SAE J2464 / ISO 12405 | pack mechanical-shock levels | **not cited (paywalled)**; automotive/EV levels do not apply directly. Unknown. |

The Molicel spec gives no allowable beyond the 150 g / 6 ms qualification. **A test level is not a design limit**: it shows survival of 18 such pulses, not a capacity.

## 2. Pack and structure allowables vs demand (38–104 g, 3.3–8.9 kN)
- **Cells, 150 g:** demand 104 g peak ≤ 150. **PASS** on peak.
- **Pack T4 level, 107 g / 6 ms:** demand 104 g ≤ 107. **PASS** on peak, but only by 3 %.
- **Pulse/Δv is NOT enveloped.** The fall pulse is 7–23 ms, Δv up to 5.67 m/s (screen model), against T4's 6 ms, 4.0 m/s. A longer pulse at the same peak puts more energy into the cell holders. **Unknown until a pack drop test at the fall pulse** (G5).
- **Cell holder:** 70 g × 104 g = 71 N per cell, through the cell can into the holder pocket. The holder is PC/ABS [EST]. **No cited allowable.** Mark it unknown; G5 test.
- **Rails (7075, multi-path, 320 MPa, R-128):** 8.9 kN over 2 rails, assuming 12 × 15 mm section and 220 mm span [EST]: M = wL/8 = 122 N·m per rail, σ = 272 MPa. **PASS, 85 % used** (on [EST] section).
- **Rail bolts (BOM row 5, 6 × M5 10.9 BHCS):** shear allowable 0.6 × 1040 × 14.2 mm² / 1.5 = 5.9 kN each. 4 effective = 23.6 kN against 8.9. **PASS (2.6×)**.
- **Latch (along the insertion axis):** no cited part. Must hold 8.9 × 1.5 = **13.4 kN**. **OPEN**: cite a latch or add a positive stop shoulder on the rails.
- **Screen model** (`fea_chest_pad.py`, lot band 19.5–22.3 kN × dynamic factor 1.10–1.30): peak pack g **25–46 g at 64 kg** and **59–85 g at 34.9 kg** (and kneel tip). Rail load **2.2–7.3 kN**. These sit inside the 38–104 g demand band.
  - **Stroke margin fails at 25° on the soft lot (2.5 %, need 10 %).** R-102 was sized at 15°. 25° is new demand.

## 3. Mitigation
1. **Latch: cited ≥13.4 kN latch, or an integral 7075 stop shoulder** on the rail ends (positive stop; the latch then only retains). +0.010 kg [EST]. **Recommended.**
2. **Pack drop test at the fall pulse** (half-sine 104 g, 20 ms, Δv 5.7 m/s, 3 axes) at G5. That replaces the missing allowable. No mass.
3. **25° case:** either Controls caps the TUCK chest angle at ≤15° (no mass), or take the R-102 fallback core 95 mm (+0.004 kg [EST], 67 mm stroke). Need: the 25° soft lot reaches 64.4 mm, against 0.9 × 0.75 × 95 = 64.1, so marginal. 100 mm core: +0.006 [EST], **PASS**.
4. **Pack isolators** (elastomer mounts, 4 × ~8 g, +0.03 kg [EST]): **not recommended**. They add stroke and rattle and lengthen the pulse, and peak g already passes. Keep as a fallback only if the G5 drop test fails.
5. **Rail section:** upsizing to 12 × 17 mm (+0.012 kg [EST]) gives 66 % used, if Materials wants margin on the [EST] section.

Inputs: `fea_chest_pad.yaml`; results: `fea/chest_pad_SCREEN_results.json` [SCREEN, 1-DOF].

## 4. Robot Lab ruling on c974f54, plus Controls fc86721, T&R 7f12ce9 and ID requests (2026-10-21 ~09:30 ET)
### 4.1 100 mm core (adopted, +0.006)
- Core 98 × 98 × **100** (was 88), outward on the unchanged land. **Pad face (skin) x = +0.159 m torso frame** (was +0.147, +12 mm). Bulge 49 mm proud of the 110 cover front (was 37). **ID: update the 37 mm bulge to 49.** The cover CAD is updated (`cad/torso_cover.py`, sternum_proud 49, bbox x max 159).
- **Frame transform (torso → SITE/global, model_v4 / sim v3 standing, waist joints at 0):** global = torso + (0, 0, +1280) mm, identity rotation. Torso origin = waist-pitch joint (sim v3 `torso` body at z 1.280; check: shoulder pitch torso z 220 ↔ model_v4 shoulder_z 1500).
  - **Pad in global:** face **x = +159**. Core y −49…+49. Core z **1451…1549** (centre 1500). Land 101 × 101: y ±50.5, z 1449.5…1550.5. Bezel outer 128 × 128 [EST, 101 + 2 × 13.5 flange]: z 1436…1564.
- Stroke at 100 mm: available 70 (0.70 densification, T&R) to 75 mm (0.75). Screen: 0° / 15° at 64 kg use 48 / 51 mm, so margin ≥28 % at 0.70. **25° at 64 kg, soft lot: 64.4 mm → 8.1 % margin at 0.70 (FAIL, need 10 %), 14 % at 0.75 (PASS).** The 25° verdict depends on the densification strain. Add it to the R-102 lot coupon (record the strain at plateau end) or cap TUCK at ≤15° (see 4.4).

### 4.2 Rail-end stop shoulder (adopted, +0.010): latch item CLOSED
- 13.4 kN (8.9 × 1.5) along the insertion axis is routed into **integral 7075 shoulders on both rail ends** (one per rail, 6.7 kN each). A pack-side lug bears on each. The latch only retains (≤0.2 kN).
- Shoulder: 12 (w) × 8 (h) × **9 mm** (axial) lip, R1 root fillet. Rails are multi-path (2 rails), so the allowable is 320 MPa (R-128); shear allowable 0.6 × 320 = 192.
  - Bearing 6700 / (12 × 8) = **70 MPa ≤ 320**.
  - Root shear 6700 / (12 × 9) = **62 MPa ≤ 192**.
  - Lip bending M = 6.7 kN × 4 mm = 26.8 N·m, Z = 12 × 9² / 6 = 162 mm³: **165 MPa ≤ 320 (51 % used)**. The 6 mm lip I tried first gave 372 MPa, so it was thickened to 9.
- Rail bolts 6 × M5 10.9 shear 23.6 kN vs 13.4: PASS. Mass: 2 × 2.4 g lips + 2 × ~2.5 g pack lugs ≈ **0.010 kg**. **Latch OPEN item closed.** Pack shock stays **CONDITIONAL until the G5 drop test (TP-G5-17).**

### 4.3 Controls fc86721 kneel tip-over: 13.3 kN at the pad, 43–44 g raw at the pack
- **The "8.8 kN pad limit" is not structural.** It is T&R's L1 controlled-lowering limit (R146_PRONE_LANDING.md §L1: "≤8.8 kN = 0.5 × the plateau floor", so a routine safe-sit never consumes the cartridge; also PRONE_DATA_TR.md, G5 TP L1). The kneel tip is **L2** (limit 22.35 kN crush ceiling), so 13.3 kN is inside L2.
- **At 13.3 kN, below the 19.5 kN (×1.10 dyn = 21.45) plateau, the pre-crushed core stays elastic.** No crush, no energy absorbed by the pad: the load goes into the structure, and the energy goes into body compliance and rebound. Face stress 13.3 kN / 98² = 1.38 MPa, below the 1.79 MPa crush and the 3.79 MPa bare compressive (HEX_CRIII 550 psi). Indentation must be checked against the T&R 0.5 mm L1 rule only if it is applied to L2.
- **Structure at 13.3 kN (R-128):**
  - Land/rib (single path, 257): 216 MPa × 13.3 / 24.4 = **118 MPa, SF 2.18 vs 257: PASS**.
  - 100 mm core: elastic: PASS.
  - Rails (multi-path, 320): pack load 8.75 × 9.81 × 44 = 3.78 kN → **116 MPa: PASS**.
  - Stop shoulder: 3.78 kN against the 13.4 kN design: PASS.
  - Pack 44 g against the 107 g T4 level: PASS on peak (Δv/pulse still per TP-G5-17).
- Chest-pad decks now include **`kneel_tip_13p3kN`** (force-driven, 34.9 kg): screen gives 38.8 g from F/m (Controls' raw 43–44 g includes rotation about the knees). PASS.

### 4.4 Head clearance (T&R 7f12ce9, ID fd981f1)
Prone geometry: gap = pad face x − head frontmost x (104.7), level body. Needed = gate stroke + elastic 1 + 10 margin = **68 mm** (T&R, gate stroke 57). My 100 mm-core screen gives 48 mm gate stroke, so 59 mm by my number. 68 is used below.

| Option | Face x | Gap level | vs 68 |
|---|---|---|---|
| Current (88 core) | 147 | 42.3 | FAIL −25.7 |
| (a) 100 core, face +12 (ruled) | 159 | **54.3** | FAIL −13.7 (PASS L3 41 + 13 spare; vs my 59: −4.7) |
| (b) land recessed 12, face kept | 147 | **42.3** | FAIL −25.7 (clearance does not grow; recess only adds stroke) |
| Standout alone to pass | **172.7** | 68 | needs +25.7 over 147 (+13.7 over (a)): bulge 63 mm proud |
| (a) + head-up tuck θ | 159 | 54.3·cosθ + d·sinθ | **θ ≥ 4.0° (d 200) to 5.4° (d 150)** |
| face 147 + tuck θ | 147 | 42.3·cosθ + d·sinθ | θ ≥ 7.5–10.2° |
| (a) + 15° tuck | 159 | 104 | PASS +36 |

d = height of the head's frontmost point above the pad centre, **150–200 mm [EST]** (head origin z +370 torso; ID to give the exact head-shell point).

**Recommendation:** keep (a) (face +0.159). Controls holds the TUCK chest pitch **head-up 5°–15°** at pad contact. That passes the 68 mm head clearance with margin and keeps stroke margin ≥10 % (≤15° is verified; 25° is marginal on densification). Do not grow the bulge to 63 mm (ID shape, core length). Recessing the land does nothing for the head.
