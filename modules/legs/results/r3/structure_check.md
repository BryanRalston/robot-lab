# R3 structure check (hand methods, not FEA)

Worst ID GRF 1040 N (all r2/r3 scenarios incl. 20 kg carry). Screw limit loads: knee 7267, hip 9084, ankle 4046 N. 3 BW 1913 N, fall 6 BW 3826 N.

| part | case | check | σ/τ MPa | SF | need | Goodman SF | ok |
|---|---|---|---|---|---|---|---|
| knee clevis (thigh), 2 cheeks 46×14, pin ø16 | operating peak (ID GRF 1040 N + screw) | net tension ×Kt 3.0 | 29.7 | 16.95 | 1.5 | 8.39 | yes |
| knee clevis (thigh), 2 cheeks 46×14, pin ø16 | operating peak (ID GRF 1040 N + screw) | bearing | 18.5 | 27.13 | 1.5 |  | yes |
| knee clevis (thigh), 2 cheeks 46×14, pin ø16 | operating peak (ID GRF 1040 N + screw) | shear | 11.4 | 25.43 | 1.5 |  | yes |
| knee clevis (thigh), 2 cheeks 46×14, pin ø16 | 3 BW + screw | net tension ×Kt 3.0 | 32.8 | 15.34 | 2.0 |  | yes |
| knee clevis (thigh), 2 cheeks 46×14, pin ø16 | 3 BW + screw | bearing | 20.5 | 24.55 | 2.0 |  | yes |
| knee clevis (thigh), 2 cheeks 46×14, pin ø16 | 3 BW + screw | shear | 12.6 | 23.02 | 2.0 |  | yes |
| knee clevis (thigh), 2 cheeks 46×14, pin ø16 | fall 6 BW | net tension ×Kt 3.0 | 13.7 | 36.81 | 2.0 |  | yes |
| knee clevis (thigh), 2 cheeks 46×14, pin ø16 | fall 6 BW | bearing | 8.5 | 58.9 | 2.0 |  | yes |
| knee clevis (thigh), 2 cheeks 46×14, pin ø16 | fall 6 BW | shear | 5.3 | 55.23 | 2.0 |  | yes |
| knee tongue (shank), R32 × 40, pin ø16 | operating peak (ID GRF 1040 N + screw) | net tension ×Kt 3.0 | 13.0 | 38.75 | 1.5 | 19.17 | yes |
| knee tongue (shank), R32 × 40, pin ø16 | operating peak (ID GRF 1040 N + screw) | bearing | 13.0 | 38.75 | 1.5 |  | yes |
| knee tongue (shank), R32 × 40, pin ø16 | operating peak (ID GRF 1040 N + screw) | shear | 4.3 | 67.08 | 1.5 |  | yes |
| knee tongue (shank), R32 × 40, pin ø16 | 3 BW + screw | net tension ×Kt 3.0 | 14.3 | 35.07 | 2.0 |  | yes |
| knee tongue (shank), R32 × 40, pin ø16 | 3 BW + screw | bearing | 14.3 | 35.07 | 2.0 |  | yes |
| knee tongue (shank), R32 × 40, pin ø16 | 3 BW + screw | shear | 4.8 | 60.7 | 2.0 |  | yes |
| knee tongue (shank), R32 × 40, pin ø16 | fall 6 BW | net tension ×Kt 3.0 | 6.0 | 84.14 | 2.0 |  | yes |
| knee tongue (shank), R32 × 40, pin ø16 | fall 6 BW | bearing | 6.0 | 84.14 | 2.0 |  | yes |
| knee tongue (shank), R32 × 40, pin ø16 | fall 6 BW | shear | 2.0 | 145.65 | 2.0 |  | yes |
| femur upper lug → hip pivot boss, assumed bore ø32 [EST: pivot bearing unowned] | operating peak (ID GRF 1040 N + screw) | net tension ×Kt 3.0 | 26.4 | 19.08 | 1.5 | 9.44 | yes |
| femur upper lug → hip pivot boss, assumed bore ø32 [EST: pivot bearing unowned] | operating peak (ID GRF 1040 N + screw) | bearing | 13.2 | 38.16 | 1.5 |  | yes |
| femur upper lug → hip pivot boss, assumed bore ø32 [EST: pivot bearing unowned] | operating peak (ID GRF 1040 N + screw) | shear | 15.1 | 19.26 | 1.5 |  | yes |
| femur upper lug → hip pivot boss, assumed bore ø32 [EST: pivot bearing unowned] | 3 BW + screw | net tension ×Kt 3.0 | 28.6 | 17.56 | 2.0 |  | yes |
| femur upper lug → hip pivot boss, assumed bore ø32 [EST: pivot bearing unowned] | 3 BW + screw | bearing | 14.3 | 35.13 | 2.0 |  | yes |
| femur upper lug → hip pivot boss, assumed bore ø32 [EST: pivot bearing unowned] | 3 BW + screw | shear | 16.4 | 17.73 | 2.0 |  | yes |
| femur upper lug → hip pivot boss, assumed bore ø32 [EST: pivot bearing unowned] | fall 6 BW | net tension ×Kt 3.0 | 10.0 | 50.49 | 2.0 |  | yes |
| femur upper lug → hip pivot boss, assumed bore ø32 [EST: pivot bearing unowned] | fall 6 BW | bearing | 5.0 | 100.97 | 2.0 |  | yes |
| femur upper lug → hip pivot boss, assumed bore ø32 [EST: pivot bearing unowned] | fall 6 BW | shear | 5.7 | 50.98 | 2.0 |  | yes |
| ankle fork (shank), 2 walls 4 mm, assumed pin ø12 [EST] | operating peak (ID GRF 1040 N + screw) | net tension ×Kt 3.0 | 124.6 | 4.04 | 1.5 | 2.0 | yes |
| ankle fork (shank), 2 walls 4 mm, assumed pin ø12 [EST] | operating peak (ID GRF 1040 N + screw) | bearing | 62.3 | 8.07 | 1.5 |  | yes |
| ankle fork (shank), 2 walls 4 mm, assumed pin ø12 [EST] | operating peak (ID GRF 1040 N + screw) | shear | 41.5 | 6.99 | 1.5 |  | yes |
| ankle fork (shank), 2 walls 4 mm, assumed pin ø12 [EST] | 3 BW + screw | net tension ×Kt 3.0 | 146.0 | 3.44 | 2.0 |  | yes |
| ankle fork (shank), 2 walls 4 mm, assumed pin ø12 [EST] | 3 BW + screw | bearing | 73.0 | 6.89 | 2.0 |  | yes |
| ankle fork (shank), 2 walls 4 mm, assumed pin ø12 [EST] | 3 BW + screw | shear | 48.7 | 5.96 | 2.0 |  | yes |
| ankle fork (shank), 2 walls 4 mm, assumed pin ø12 [EST] | fall 6 BW | net tension ×Kt 3.0 | 93.8 | 5.36 | 2.0 |  | yes |
| ankle fork (shank), 2 walls 4 mm, assumed pin ø12 [EST] | fall 6 BW | bearing | 46.9 | 10.73 | 2.0 |  | yes |
| ankle fork (shank), 2 walls 4 mm, assumed pin ø12 [EST] | fall 6 BW | shear | 31.3 | 9.29 | 2.0 |  | yes |
| foot plate v3 solid 100×18 | operating peak GRF at toe | bending ×Kt 1.5 | 43.3 | 11.61 | 1.5 | 5.74 | yes |
| foot plate v3 solid 100×18 | 3 BW at toe | bending ×Kt 1.5 | 79.7 | 6.31 | 2.0 |  | yes |
| foot plate v3 solid 100×18 | fall 6 BW at toe | bending ×Kt 1.5 | 159.4 | 3.16 | 2.0 |  | yes |
| foot plate open ribbed 4 mm skin + 3 ribs 3×14 (r2 spec) | operating peak GRF at toe | bending ×Kt 1.5 | 312.9 | 1.61 | 1.5 | 0.8 | **NO** |
| foot plate open ribbed 4 mm skin + 3 ribs 3×14 (r2 spec) | 3 BW at toe | bending ×Kt 1.5 | 575.6 | 0.87 | 2.0 |  | **NO** |
| foot plate open ribbed 4 mm skin + 3 ribs 3×14 (r2 spec) | fall 6 BW at toe | bending ×Kt 1.5 | 1151.2 | 0.44 | 2.0 |  | **NO** |
| foot plate closed box 18: 4 mm skins top+bottom + 4 webs 4 mm (r3 spec) | operating peak GRF at toe | bending ×Kt 1.5 | 50.6 | 9.94 | 1.5 | 4.92 | yes |
| foot plate closed box 18: 4 mm skins top+bottom + 4 webs 4 mm (r3 spec) | 3 BW at toe | bending ×Kt 1.5 | 93.1 | 5.4 | 2.0 |  | yes |
| foot plate closed box 18: 4 mm skins top+bottom + 4 webs 4 mm (r3 spec) | fall 6 BW at toe | bending ×Kt 1.5 | 186.2 | 2.7 | 2.0 |  | yes |

Notes:
- ankle fork (shank), 2 walls 4 mm, assumed pin ø12 [EST]: walls are only 4 mm: pocketing them (×0.85) is NOT recommended; pocket the 10 mm top plate only
- femur upper lug → hip pivot boss, assumed bore ø32 [EST: pivot bearing unowned]: thickness ×0.8 for the 20 % pocket; bore and bearing not defined (open linkage-table line)
- foot plate closed box 18: 4 mm skins top+bottom + 4 webs 4 mm (r3 spec): A 960 mm², I 41600 mm⁴, c 9.0 mm
- foot plate open ribbed 4 mm skin + 3 ribs 3×14 (r2 spec): A 526 mm², I 10353 mm⁴, c 13.8 mm
- foot plate v3 solid 100×18: A 1800 mm², I 48600 mm⁴, c 9.0 mm
- knee clevis (thigh), 2 cheeks 46×14, pin ø16: bridge pocket 15 % is outside the pin path; v3 FEA scaled SF 4.80 (structure_mass.md) is the governing whole-part number
- knee tongue (shank), R32 × 40, pin ø16: pocket 15 % keeps a 12 mm ligament ring around the pin
