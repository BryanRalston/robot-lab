
## D56 (R-022 A13) Rollup re-based on modules/arbiter/mass_rollup_official.json
linkage_table.py reads the official file; emits only results/actuator_deltas.json (harness 1.28644 vs 1.2864, +0.00004; linkage 2.32616 vs 2.3262, -0.00004). No parallel robot total; mass_rollup_r6.json removed. Official credible 66.054 kg (paper 64.531; pending A1' -0.596 -> 65.458). Prior divergence of my 66.853: brain -0.584, covers -0.238, Legs r6 +0.022 missed, harness -0.038. Open: GE 12 C cost $17.20 (mine) vs $10-31 (Arbiter); ankle +0.0256 and leg actuator lines inside unitemised 47.739 until A12.

## D57 (R-022 A13) Ankle 73 mm at +/-18 roll
Pitch -45..+40 and -60..+40 identical: Lmin 262.6, Lmax 374.3, stroke 111.7, need 250.7, margin 11.9 mm OK. Lmin falls mid-ROM (L(-60)=270.5, L(-45)=278.0), so extending to -60 does not govern. Arbiter F: 10.9 mm (Lmin 262.1 / stroke 112.2) - 1 mm grid-resolution difference; use 10.9 as conservative.
