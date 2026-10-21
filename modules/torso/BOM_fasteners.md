# Torso & Power fastener BOM (R1, 2026-10-21)
S = structural (preload- or crash-critical: stays steel); N = non-structural (Ti Gr5 candidate, P-147, for RL Materials pricing). Lengths and counts are [EST] from the R1 layout.

| # | Size × length | Qty | Grade / material | Location | S/N |
|---|---|---|---|---|---|
| 1 | M8×30 SHCS | 16 | ISO 4762 12.9 steel | shoulder flanges to bulkhead, 2 × 8 on the 80 mm bolt circle | S |
| 2 | M6×20 SHCS | 12 | 12.9 steel | waist pitch/yaw actuator flanges to the waist ring / pelvis | S |
| 3 | M6×25 SHCS | 8 | 12.9 steel | hip actuator mounts to the pelvis (Legs interface) | S |
| 4 | M5×16 SHCS | 8 | 10.9 steel | bulkhead to waist ring posts | S |
| 5 | M5×12 BHCS | 6 | 10.9 steel | pack rails to the pelvis / bulkhead (10 g pack retention) | S |
| 6 | M4 captive insert + M4×10 | 4 | A2 steel insert / 10.9 screw | sternum bezel on the bulkhead land (§25.1) | N |
| 7 | M5×10 BHCS | 4 | 8.8 steel | HS100 clamp resistor to the bulkhead | N |
| 8 | M3×8 SHCS | 4 | A2 | HS25 pre-charge resistor | N |
| 9 | M4×8 BHCS | 24 | A2 | CFRP shell panels to the bulkhead / pelvis inserts | N |
| 10 | M3×6 BHCS | 12 | A2 | 1 mm CFRP partition to the posts | N |
| 11 | M3×6 + 5 mm standoffs | 4 + 4 | A2 / nylon PA66 | EtherCAT junction PCB (R-087) | N |
| 12 | M4×10 SHCS | 6 | A2 | PDB, plus fuse/contactor brackets (bus terminals use the part's own hardware) | N |
| 13 | M2.5×6 | 8 | A2 | DCM cold-plate clamp, 48 V/5 V boards | N |
| 14 | M3×8 | 6 | A2 | A41 duct walls, Sunon fan | N |
| 15 | M3×6 | 8 | A2 | shoulder-bay hand-board strap / gap-pad bracket (Arms) | N |

- **Totals:** 138 fasteners. **Structural: 50** (≈0.33 kg steel [EST]), stays steel. **Non-structural: 88** (inserts and standoffs included) ≈0.13 kg steel [EST].
- **Ti swap scope (P-147):** rows 7–10 and 12–15, 76 pieces, ≈0.115 kg steel → ≈0.065 kg Ti Gr5 (ρ 4.43 vs 7.9), **−0.05 kg [EST]** (P-147 said −0.06; corrected to −0.05). Rows 6 and 11 keep steel inserts and nylon standoffs.
- Ti rules: anti-seize or thread-locker; no Ti into Al tapped holes without a Helicoil or anodize; electrical bonding bolts (row 12 PDB earth) stay steel/brass.
