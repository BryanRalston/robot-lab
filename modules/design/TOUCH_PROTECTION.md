# Touch protection (RL Industrial Design, 2026-10-14)
Script `touch_protection.py` → `touch_protection.json`.

## 1. Origin of the +0.25 kg booking (electrical — not ID covers)
| | |
|---|---|
| **Ruling** | R-076 (IP2X on bus parts) → R-079 (SurLok 1000 V set oversized) |
| **Breakdown** | SurLok / connector EST **+0.21** + main link 16 mm² **+0.04** = **+0.25** booked conservatively in full |
| **Owners** | **Torso** (connectors, shrouds, pack) + **Electronics** (bus-point inventory) |
| **Electronics result** | §18.2f (`7ff4cd7`): cited IP2X inventory **≈ 0.086 kg**; credit back ≈ 0.164 vs +0.25 |

Electrical finger-safe IP2X (IEC 60529) is **separate** from thermal burn protection on cover skins. ID does not replace SurLok/boots with liners.

## 2. Thermal touch limit (ID cover skins)
- **Limit used:** **48 °C** for plastics touched briefly — Thermal `R1_BUDGET.md` (“ISO 13732-1 class, value not verified”); treated here as an **IEC 62368-1 TS1-class** design target for accessible plastic.
- **Hot nodes (Thermal §3, covered, 35 °C ambient):** hip_pitch and knee **cover outer skin ≈ 53 °C** → **FAIL by 5 K**. OK at 25 °C ambient (43 °C).
- PC continuous use ~115 °C is fine; the issue is **touch burn**, not material melt.

## 3. Lightest option (vents → standoff ribs → liner last)
1. **A35 / P-026 vents** (already in the cover set): required for winding limits; first thermal measure; no extra booking here.
2. **5 mm PC standoff ribs** on the hot outer-skin zones (hip cover ~0.050 m² pair, knee fairing+cap ~0.060 m² pair): raise the outer skin off the hot cavity / add wash paths. **≈ 0.020 kg pair** [EST].
3. **Thin liner** (aerogel blanket or silicone foam ~0.20 kg/m²) **only** over patches still above 48 °C after vents+standoff. With a **7 K** standoff credit [EST], skins land ≈ 46 °C → **liner not needed**.

| item | kg |
|---|---|
| Standoff ribs (hip + knee hot zones) | **0.020** |
| Liner | 0 (contingent) |
| **ID thermal-touch total** | **0.020** |

## 4. Mass vs +0.25
| bucket | kg |
|---|---|
| Electrical IP2X (Electronics inventory) | 0.086 |
| Thermal cover touch (this doc) | 0.020 |
| **Combined** | **0.106** |
| vs +0.25 booking | **−0.144** |

## 5. Still needs measurement
- Cover-skin thermocouples at hip/knee on the G5 carry at 35 °C (Thermal already lists this).
- Materials confirmation of the 48 °C plastic touch threshold (ISO 13732-1 / IEC 62368).
- Standoff ΔT of ~7 K is **[EST]** — confirm on J-T1 or bench before deleting the liner contingency.
- If skins stay > 48 °C, add liner and re-cite areal density.
