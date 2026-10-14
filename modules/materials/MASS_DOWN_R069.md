# R-069 mass-down: material swaps (RL Materials, 2026-10-14)
Target: ≥ 0.18 kg back, cited or measured. Densities come from MATERIALS_DB (cited). Geometry comes from the repo files noted. **Status key:** READY = density and geometry cited, no new structural risk, can be booked now. FEA = needs an FEA pass before booking. TEST = needs a bench or impact test. Deltas are for both sides unless noted.

| rank | swap | Δ g | basis (cited) | risk | status |
|---|---|---|---|---|---|
| 1 | **Shoulder pad: D-A plate on the roll output vs the provisional 0.127 booking (R-063/R-060)** | **−39** (0.127 → 0.0876, R042 Part 6) | AL7075T6 ρ 2.81; HC5052_4.5 ρ 72 kg/m³; ID R7 itemised mass | link face must qualify (Arms D1); roll bearing FEA | **READY on mass**, conditional on D1 + FEA job 1 |
| 2 | **Hand palm 7075 → printed PA12 MJF with 7075 inserts at the knuckle bar and wrist plate** | **−119** (all PA12) / **−80** (hybrid) [EST from A32 CAD volume × ρ] | PA12 ρ 1.01 (R027); 7075 2.81; A32 0.0924 kg/hand | PA12 strength/fatigue at the R3 windows and tendon stops not cited; the MJF datasheet is still TODO; R-027 printing preference lifted by Bryan | **FEA + TEST** (grip load 10 kg carry) |
| 3 | **Covers: small complex panels (knee cap, hip skirt, boots, brain lid) PC 1.5 → PA12 MJF 1.5** | about −0.16 × panel PC mass. On the R-027 0.643 m² basis −183, but **re-base on the current V5 trimmed set**; the louvred knee cap + skirt ≈ 0.25 kg PC → **≈ −40** [EST] | PC 1.20 (PALSUN), PA12 1.01 | PA12 impact lower than PC (not cited); louvres already cut mass | **TEST** (fall impact on 1 panel); density basis READY |
| 4 | **Covers: low-draw panels PC 1.5 → 1.2 mm** | −20 % of those panels' PC mass. R-027 basis −231, **current trimmed set ≈ −60 to −80** [EST, needs ID panel list] | PC 1.20 | dent/stiffness on EPP backing | **TEST** (dent) |
| 5 | **Ankle cross Ti-6Al-4V → 7075-T6** | **−88** (120 → 76 g/leg) | Ti64 ρ 4.4 (MIF), 7075 2.81 | fatigue 530–630 → 160 MPa, E 110 → 70; galvanic risk gone; no FEA of the cross exists | **FEA** (Legs) |
| 6 | Femur tubes 7075 → CF tube | −130 [EST] | CFRP ρ 1.55 (R027) | laminate data not cited; galvanic with Al collars; dent; bond redesign | **TEST + FEA** (not recommended) |
| 7 | Bond cross pins ø6 → ø5 (Legs DECISIONS candidate) | −8 per Legs | Legs DECISIONS L-100 | pin shear SF 6.7 → ≈ 4.7 | **FEA** (Legs) |
| — | 7050-T7451 femur/collars | 0 | same ρ (MIF) | fatigue +25 %, SCC better | READY (not a mass item) |
| — | A37 PEI thermal break | **+17** | PEI 1.28, 7075 2.81 | — | add to the ledger |

## Summing up
- **Booked-ready now:** rank 1 (−39 g), conditional on Arms D1. That is **well short of 0.18 kg.**
- **Most likely path to ≥ 0.18 kg:**
  - −39 (pad) − 80 (hybrid palm, FEA + test) − 88 (Ti → 7075 cross, FEA) = **−207 g**, minus the A37 +17 = **−190 g net**.
  - Every term except the pad needs FEA or test before booking.
  - Cover items (ranks 3–4, ≈ −100 to −120 g) are the backup but need impact/dent tests and an ID re-basis on the trimmed set.
- **Asks:**
  - **Legs:** FEA of the 7075 ankle cross (rank 5) and the ø5 pins (rank 7).
  - **Arms:** PA12/7075 hybrid palm FEA at grip loads (rank 2) and the link face (D1).
  - **ID:** itemised current panel PC masses so ranks 3–4 can be re-based.
  - **G5:** palm grip test, one PA12 cover fall test.
  - Get the PA12 MJF datasheet (impact, fatigue) into MATERIALS_DB. This is still open.


## R-076 reconciliation (2026-10-14)
- **Pad (rank 1):** R-060 booked 0.127 provisional. R-073 already re-booked the doubler pair at **0.092** (0.084 calc × half credit). R-076 adopts the 61 mm core: **0.0876 calc**.
  - True net vs 0.127 is −39.4 g, but **−35 g of it is already booked by R-073.**
  - **Remaining credit: 0.092 → 0.0876 = −4.4 g**, only once FEA job 1 passes and the link face qualifies (then full credit on the calc).
  - No double count.
- **Covers (ranks 3–4):** superseded. See COVER_TRIMS_REVIEW, Reconciliation. Remaining upside ≈ −0.015 kg after tests.
- **Bond pins:** booked −0.004 (R-076).
- **Tendon sheaths:** a compressionless coil is needed (TENDON_SHEATH rev B), **≈ +42 g both hands vs plain PTFE [EST]**. Add to the ledger as a penalty.
- **T-031 chest pad: +0.077 kg** (full credit, R-076), T031_CHEST_CRUSH.md.
- Updated path to the 0.30 reserve floor: hybrid palm (−0.080, FEA + grip test) + pocketed 7075 ankle cross (−0.088, FEA, approved R-073) + pad −0.004 + covers −0.015 ≈ **−0.187**, against penalties of +0.017 (A37) + 0.042 (sheaths) + 0.077 (chest). **Net ≈ −0.05 kg.**
