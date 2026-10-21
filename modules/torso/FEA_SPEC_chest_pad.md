# FEA spec: chest-pad crush (T-031 / R-146), bryan PC. **FINAL: decks complete, unvalidated (OpenRadioss could not be downloaded on the box)**
- **Part:** HexWeb CR III 5052 1/8 4.5 pcf, 98 × 98 × **116** mm (ID 341ef4a; face x +175 torso = +175 global, z 1451–1549 global; ribbon L along z; 8 mm land socket wall recommended), pre-crushed, lot band 19.5–22.3 kN (0°). 1 mm CF face, 1.5 mm PC bezel (4 × M4 captive), bonded to the 7075 101 × 101 land on the 12 mm bulkhead plus 60 × 6 rib.
- **Solver choice: OpenRadioss** (free, open source, explicit, Windows and Linux). Honeycomb **/MAT/LAW28** (orthotropic honeycomb, plateau yield curves per direction) or LAW126/LAW70 crushable foam as a check. Rigid moving wall /RWALL with mass m and /INIVEL v. CalculiX is rejected (implicit, no crush densification). LS-DYNA MAT_126 is equivalent but licensed.
  - **Calibration:** plateau = lot band (1.79 MPa typical at 4.5 pcf; 19.5 / 22.3 kN over 98 × 98), dynamic factor 1.10–1.30, angle factors 0.98/0.93/0.73 (HC_ANGLE_PMC), densification at ε 0.75.
- **Cases:** 0°, 15°, 25° at 64 kg and 34.9 kg (Controls), v 5.67 m/s; kneel-tip prone landing at 34.9 kg, 3.0 m/s [EST]; each at both lot bounds.
- **Outputs:** force–stroke curve, peak g on the pack (F/m and filtered SAE CFC 600), rail loads (pack mass × pack g), pulse duration and Δv.
- **Convergence:** cell 8 / 4 / 2 mm; peak force and stroke change ≤5 % between the last two.
- **Pass:** stroke margin ≥10 % of 0.70 × 116 = 81.2 mm; quasi-static ceiling ≤22.35 kN; pack g ≤107 g (UN T4 level, R146_pack_shock.md) and rail load ≤8.9 kN; Δv beyond 4.0 m/s is flagged for the G5 drop test.
- **Files:** `fea_chest_pad.yaml`, `fea_chest_pad.py`.
- **Run:**
  - Screen: `python modules/torso/fea_chest_pad.py --cfg modules/torso/fea_chest_pad.yaml --out modules/torso/fea/chest_pad`.
  - Decks: add `--mode radioss`. That writes the starter mesh, material and part for every case × mesh level. **On the PC, finish the deck** (marked TODO: /RWALL, /INIVEL, /BCS, /TH, /FUNCT), then run `starter_win64 -i <case>_0000.rad` and `engine_win64 -i <case>_0001.rad`.
- **Box smoke test:** screen plus deck write, 18 decks, **2.7 s. OK.** Screen results in `fea/chest_pad_SCREEN_results.json`.

## Run on the bryan PC (updated)
- **Install:** download `OpenRadioss_win64.zip` (or `_linux64.zip`) from https://github.com/OpenRadioss/OpenRadioss/releases (latest stable) and unzip it to `C:\OpenRadioss`. Then `pip install pyyaml`.
- **Generate and run:** `python modules/torso/fea_chest_pad.py --cfg modules/torso/fea_chest_pad.yaml --out modules/torso/fea/chest_pad --mode radioss --radioss C:/OpenRadioss`. On Windows, set the exe names to `starter_win64` / `engine_win64` / `th_to_csv_win64` (Linux names are the default in the script).
- **Quick first check:** add `--only fall_0deg_64 --cells 8` (coarsest 0°, 2 decks).
- **Post:** `python modules/torso/fea_chest_pad_post.py --cfg modules/torso/fea_chest_pad.yaml --dir modules/torso/fea/chest_pad` writes `post_results.json` with force–stroke, peak kN, stroke, pack g, rail kN, convergence (≤5 % on the last two levels), and PASS/FAIL.
- **Deck contents:** honeycomb block of hexas, crush axis x. LAW28: E11 1034 MPa, G12/G31 483/214 (HEX_CRIII); axial yield curve = lot plateau flat to ε 0.60, ×1.5 at 0.70, steep densification beyond; weak transverse. Land face fixed (/BCS, bonded). Moving rigid plane wall = impactor of mass m at v (/RWALL/PLANE). /TH/RWALL force plus /TH/NODE face displacement. Engine: /RUN 60 ms, /TFILE 10 µs, /ANIM 2 ms.
- **Validation gap:** the box got HTTP 404 for every GitHub OpenRadioss URL (repo and release assets) and conda-forge has no package, so **no starter/engine run was possible here**. Card formats follow the Radioss block format but are unvalidated. First PC run: check the starter .out for card errors (LAW28 / RWALL field order) before the engine.
- **Cases** now include `kneel_tip_13p3kN` (Controls fc86721; force-driven, screen only, elastic).

## Cartridge acceptance (T&R b1fe48f)
Dynamic crush coupon per lot at 5.7 m/s: peak ≤29.0 kN, plateau in the R-102 band, densification strain recorded. Pre-crush inspection per DIAGNOSIS.md §5.

## Rev 2026-10-21: soft core option REJECTED, 4.5 pcf core kept
- Materials b359af8 candidate: HexWeb CR III 5/32-5052-3.8, 1.276 MPa, ×1.30 rate, plateau 11.7 / 17.4 kN, 864 J, 0.072 kg (RFQ crush cert 1.24–1.31 MPa; fallback land 104 × 104).
- **Rejected per Controls 1021e37:** the 25° chest-only landing bottoms out the core (101 vs 81.2 mm).
- The spec and pad mass stay at **4.5 pcf, 0.085 kg core**, with lot band 19.5–22.3 kN and LC1 29 kN. The 3.8 pcf grade stays listed as a rejected option only.
