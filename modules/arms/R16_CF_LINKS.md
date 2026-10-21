# RL Arms & Hands R16 (2026-10-21): option C(b), CF arm links bonded to machined 7075-T651 end fittings
Calc: `cf_links_r16.py` / `.json`. Hand calcs only. **No 3D printing**: tubes are roll-wrapped prepreg; fittings are machined 7075-T651 (stock and grain per `STOCK_GRAIN.md`). Gear housings and the W2 carrier are excluded.
Current links (model_v4 [CALC from EST geometry]; these sit inside the unitemised CONTRACTS §3 arms structure, 0.80/side):
- upper-arm tube 7075 Ø50 × 2 × 87 mm: **0.074 kg/side**
- forearm shell Ø70/66 × 194 mm: **0.233 kg/side**
The elbow clevis (0.27), wrist end cap and roll-yaw link stay 7075. They become the bonded end fittings.

## Governing loads (per side)
| link | bending | torsion | basis |
|---|---|---|---|
| upper arm | **104 N·m** fall/tuck [EST: forearm + hand 2.77 kg × 187.5 m/s² × 0.2 m] (> carry 65.6) | 70 N·m (shoulder-yaw control cap) | tuck_r6 method, R1 carry |
| forearm | **78 N·m** fall [EST] (> elbow cap 69 > P-042 20 kg carry 14.6) | 36 N·m (wrist-roll control cap) | R-085 cap, P-042 |

## Results [CALC; CF E 75 / G 5 GPa EST; bond allowable 6.9 MPa (DP460 FRP, substrate failure, 3M TDS) ÷ 1.5 = 4.6, peak factor 3 EST]
| | upper arm | forearm |
|---|---|---|
| CF tube | Easy Composites 50/47 roll-wrapped (364 g/m cited) | Ø70/67 × 1.5, **custom** (stock ranges stop at 60 OD) |
| CF bending stress | 39 MPa | 14 MPa (both ≪ laminate strength) |
| bond length each end (peak ≤ 4.6) | **40 mm** (peak 4.5), so 92 % of the 87 mm tube is overlap | 20 mm (peak 3.3) |
| bending stiffness EI vs 7075 | 0.83 | 0.82 |
| **torsion GJ vs 7075** | **0.14** (twist 0.52° vs 0.08° at 70 N·m) | **0.14** (0.21° vs 0.03° at 36 N·m) |
| mass new / old kg | 0.080 / 0.074 | 0.131 / 0.233 |
| **Δ pair** | **+0.013 (heavier)** | **−0.203** without a thermal fix; **−0.091** with the 0.8 mm 7075 heat-spreader sleeve |
| cost (tube only, cited) | ≈ $9 (Easy, $105.05/m) | ≥ $32 per tube (Rock West 45146 $305.99/72 in scaled; Ø70 custom is higher, no cited price) |

## Findings
- **Upper arm: not worth it.** The link is 87 mm long, so the bonded joints are nearly the whole tube, and the result is +0.013 kg pair. Reject.
- **Forearm: −0.09 kg pair realistic** [CALC]. The shell is the flexor thermal clamp (R5/R8 ladder B), and CF conducts about 100× worse through its thickness, so it needs a 7075 inner sleeve. Thermal must re-run ladder B.
  - Torsional stiffness drops to 0.14× of 7075 (k_t ≈ 9.8 kN·m/rad). Controls' gate (8f80c42) is assembly k_t ≥ 2.9, so it **passes** on hand calc.
  - With the CSG-14-100 wrist-roll gear in series (4.7 kN·m/rad) the series stiffness is 3.18 kN·m/rad.
  - First torsion mode: **≈ 20.1 Hz** at 0.2 kg·m² (T5, gate ≥ 15) and ≈ 460 Hz hand-only (gate ≥ 40). Both pass.
  - This replaces the earlier wrong ≈ 50 Hz estimate (wrong payload inertia, no gear in series).
  - The ±45° braid overwrap (+~0.01/side [EST]) is needed only if the Job 8c FE assembly k_t < 2.9.
  - Galvanic isolation (glass scrim or a primed bondline) between CF and 7075 is required (Materials).
  - Credit at half (calc/EST): about **−0.045 kg**. It is **not** a reserve fix; R-122 needs > 1 kg.
- Bigger C(b) mass sits in the 7075 clevis and roll-yaw link (0.27 + 0.34/side), not the tubes. A CF monocoque replacing those needs CAD and FEA and is not sized here.

## Job 8c spec (written in R7_ROUND.md §G, not launched)
