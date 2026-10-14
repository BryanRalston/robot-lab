# R-110: Hot-rated A38 femur collar bond (lets the knee trunnion break go)
RL Materials, 2026-10-14. Hand calc. [EST] = estimate.

## 1. Joint and loads (from legs/BOND_SPEC.md and DECISIONS L22)
- 7075-T6 split collar (ID 50 × 34 mm) bonded on the ø50 × 1.2 mm femur tube, plus a bonded 7075 inner sleeve. Bond area per surface π·50·34 = 5341 mm².
- Two ø6 42CrMo4 cross pins go through the collar, tube and sleeve as positive backup.
- Required bond shear: 1.64 MPa static (both screws) and **5.54 MPa one-screw fault**. The proof load of 13.1 kN gives 2.45 MPa.
- Allowable rule (BOND_SPEC): datasheet value × 0.5.
- Today's DP490 limit: 82 °C sandblasted 9.5 MPa → 4.75 MPa → fault SF 0.86. That is why the bond is held at ≤ 60 °C.

## 2. Bondline temperature without the trunnion break (thermal/A38_FEMUR_PATH.md)
- Unbroken knee path: bond 54–60 °C at R_col 8, **61–66 °C** at R_col 14. Vents short (h 12): ≥ 62 °C, with no upper value given.
- Design point for a new adhesive: **≥ 80 °C service**. Upper margin target is 95 °C.

## 3. Candidates (official/manufacturer TDS)
| adhesive | lap shear RT | 80–82 °C | 93–121 °C | Tg | cure | verdict |
|---|---|---|---|---|---|---|
| **Loctite EA 9396 AERO** | 24.1 (RT cure) / 27.6 MPa (30 min 82 °C) | 22.0 / 22.8 | 12.4–13.1 at 149 °C; 8.3 at 177 °C | 64 °C (5 d RT) / **112 °C (1 h 82 °C)** [9396.6MD TDS] | RT 5 d + **1 h 82 °C post-cure** | **RECOMMENDED** |
| Loctite EA 9394 AERO | 28.9 | 20.7 | 20.0 at 93; 15.8 at 121 | **78 dry / 68 wet** | RT 5 d | reject: wet Tg below service |
| 3M EC-9323 B/A | 36 | 22 (80 °C) | **4 at 120 °C** | n/p | RT 15 d (or 2 h 65 °C) | reject: rated service −55 to 82 °C, cliff above 80 |
| 3M DP420 | n/a (sandblast) | **2.7 (10 %)** | — | 81 °C | RT | reject |
| 3M DP460 | 24 | 4.8–9.7 (700–1400 psi, 15–60 min soak) | 1.5 at 121 | n/p | RT | reject |
| DP490 (current) | 23 sandblast / 30 etched | 9.5 / 11.9 | 2.8–3.2 at 120 | — | RT + 1 h 80 °C | ≤ 60 °C only |

EA 9396/9394 values are on PAA 2024-T3 (ASTM D1002). EC-9323 values are on etched 2024-T3 (EN 2243-1).

## 4. EA 9396 check at our joint
- Prep knock-down from PAA to grit-blast + primer: 0.77 [EST]. This is the DP490 sandblast/etched ratio at 23 °C (23/30).
- At 82 °C: 22.8 × 0.77 × 0.5 = **8.8 MPa allowable** → fault SF **1.58**, static SF 5.4.
- At 95 °C: 20.8 MPa [EST, linear 82→149 °C] × 0.77 × 0.5 = **8.0 MPa** → fault SF **1.45**, static SF 4.9.
- At 66 °C (worst unbroken Thermal case) the margin is larger still.
- Tg 112 °C (post-cured) − 95 °C = 17 K of dry margin. **Wet Tg is not published** [EST: assume 10–20 K wet drop]. That means 80 °C is the qualified service limit, and 95 °C is the margin case only.
- RT-cure-only parts are NOT acceptable (Tg 64 °C). The 1 h 82 °C post-cure is mandatory and replaces DP490 cure 2 (1 h 80 °C), so there is no process change for the 7075-T6 parts: well below the 120 °C ageing temperature.

## 5. Substrates
- **7075:** grit-blast 80–120 alumina, solvent wipe. Prime with a sol-gel (3M AC-130-2) or BR 127-class corrosion-inhibiting primer [EST: no primer TDS fetched this round]. The EA 9394.2 TDS shows primed PAA data of the same order. Mask the bond areas from anodize, as in BOND_SPEC.
- **CF (if any bonded CF part):** peel ply or 180–240 abrade, solvent wipe, no primer. EC-9323 publishes 28 MPa on CFRP; there is no CF figure for EA 9396 [EST: similar].
- Galvanic isolation: the bondline counts as isolation only with glass beads present to hold ≥ 0.08 mm.
- Bondline: 0.08–0.13 mm. EA 9396 is low-viscosity, so add 0.1 mm glass beads (1 wt %), which are mandatory here.

## 6. Mechanical retention (backup / alternative)
- The existing 2 × ø6 42CrMo4 cross pins (L22) are the backup.
  - Shear: 4 planes × 28.3 mm² × 0.6 × 990 = **67 kN**.
  - Bearing: tube 1.2 mm and sleeve 2.0 mm, 2 pins × 2 sides × 6 × t × 720 MPa (1.5 × 480) [EST] = 20.7 + 34.6 = **55 kN**.
  - One-screw fault load: 5.54 MPa × 5341 mm² = 29.6 kN → **pins-only SF ≈ 1.9** [EST, hand calc; FEA for hole edge distance and the 1.2 mm tube is owed by Legs].
  - With the pins sized for the fault, the bond's job becomes stiffness/no-slip, and its temperature is no longer a structural cliff.
- A shoulder or interference fit adds no value over the pins on a 1.2 mm wall: hoop stress, and the collar is a split part. Not recommended.

## 7. Recommendation
1. Replace DP490 with **Loctite EA 9396 AERO, RT + 1 h 82 °C post-cure (Tg 112 °C)**, on grit-blast + primed 7075 with 0.1 mm beads. Qualified service limit 80 °C, margin case 95 °C.
2. **Drop the knee trunnion break** (R-106 ULTEM 4001 bush set). The unbroken bond at 61–66 °C sits inside the 80 °C limit.
3. Keep the cross pins (no change) as positive backup.
4. Keep the existing proof test (13.1 kN, ≤ 0.01 mm slip). Add a G5 hot proof at 80 °C on one article.

## 8. Mass
- Adhesive change: about 0 g (same bondline volume, ρ ~1.1 vs 1.0) [EST].
- Trunnion break removed: **−0.074 kg** versus the R-106 booking (−0.070 versus the +0.004 originally booked).
- Note: the knee trunnion still needs a plain bearing. If Legs reverts to the L61-era metal/standard bush, its mass sits in the original +0.004 booking [EST].

## 9. Thermal must confirm
- Peak bondline with the trunnion path **unbroken** at R_col 14 *and* with short vents (h 12) is ≤ 80 °C. Today it is only given as ≥ 62 °C.
- That the A37 ø22 tine break stays as designed: this proposal assumes it does. Removing it too needs a separate run.
- The tibia collar bond (same spec) is unaffected or improved.
- J-T1 / G5 collar thermocouple remains the gate.

## Sources
- EA 9396 AERO TDS: https://www.conro.com/downloads/Manuals/Loctite-EA-9396-AERO-Epoxy-Paste-Adhesive-A-B-1USQ-Kit-TDS.pdf
- EA 9396.6MD (Tg, k): https://www.gluespec.com/Materials/SpecSheet/6b9cd73c-bc72-4e4b-ac15-20a777c6b4ca
- EA 9394 AERO: https://datasheets.tdx.henkel.com/LOCTITE-EA-9394-AERO-en_US.pdf
- EC-9323 B/A: https://multimedia.3m.com/mws/media/820935O/3m-scotch-weld-9323-b-a.pdf ; https://www.viba.nl/media/files/tds/tds0001188.pdf
- DP420: https://multimedia.3m.com/mws/media/2365743O/3m-scotch-weld-epoxy-adhesive-dp420-black.pdf
- DP460: https://multimedia.3m.com/mws/media/2365880O/3m-scotch-weld-epoxy-adhesive-dp460-off-white.pdf ; https://bac-online.com/content/PDF/DP460-TDS.pdf
- DP490: legs/BOND_SPEC.md [A][B]
