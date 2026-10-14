# R-069 mass-down pass: NEW cover trims beyond R-047 (RL Industrial Design, 2026-10-14)
Script `cover_trims_r069.py` → `cover_trims_r069.json`. Baseline: trimmed v5 set with the R-047 items already taken (A35 vents, PC 1.2 on thigh outboard + foot top, PA12 rim strips). Areas [EST] (measured: false), so covers count at half credit (R-040). Fabric weights are [EST] pending supplier TDS.

| item | Δ kg pair | calc / citation | risk | recommend |
|---|---|---|---|---|
| A  CF 1.0 mm (4x0.25 twill) on the louvred thigh FRONT half (outboard stays PC 1.2: CF 1.55 kg/m2 > PC 1.2 1.44) | **-0.026** | front skin 0.187 x (1-1.55/1.80); R-027 densities; R-054 prefers CF | cost ~+$0.8k Al tools (2 L/R fronts); edge cracking on impact (R-027) -> radiused/hemmed slot edges | YES |
| B  knee cap PC 1.5 -> 1.2 mm | **-0.02** | 0.098 x 0.3/1.5 | 2.5:1 draw -> post-form min ~0.7 mm at corners; knee is a fall-contact zone (dent/crack); EPP pad behind it? | NO (fall zone) unless Materials dent check passes |
| C1 foot top shell 1.2 -> 1.0 mm | **-0.023** | 0.137 x 0.2/1.2 | low draw (<=1.5:1) OK; foot is a kick/stub zone: dents; EPP-backed | YES (with dent check) |
| C2 foot top shell DELETED (alternative to C1) | **-0.153** | 0.137 + 4 inserts | instep lugs/outrigger exposed (snag, debris, looks); Legs to accept; mould M5-M6 deleted (-$2.3k) | OPTION for the Arbiter |
| D  ankle boot: TPU-coated 210D nylon 0.30 -> silicone-coated 70D ripstop ~0.10 kg/m2 | **-0.04** | 0.201 m2 x 0.20 kg/m2 [EST: needs supplier TDS] | abrasion at the ankle; becomes a wear part (inspect at the 4,250 h rod-end service) | YES |
| E  hip skirt fabric 0.30 -> 0.10 kg/m2 (same ripstop); PC rim + hem ring kept | **-0.048** | 0.239 m2 x 0.20 kg/m2 [EST] | flutter/pinch at the hip; the exhaust slots band needs the hem ring (kept) | YES |
| F1 waist bellows P-024 TPE -> thin TPU-film convoluted boot 0.3 kg/m2 | **-0.025** | 0.0848 m2 x 0.30 kg/m2 [EST] | fatigue at waist yaw/pitch; needs a cycle test | YES |
| F2 waist bellows P-024 DELETED (alternative to F1) | **-0.055** | cover_set_v5.json P-024 | waist yoke/pinch points exposed (Optimus look lost); finger-pinch hazard at waist pitch | OPTION |
| G  fasteners: 2 of 4 bonded inserts per rigid panel -> moulded snap hooks (8 panels) | **-0.032** | 8 panels x 2 x 2 g [EST] | retention after a fall; panels may pop off (that is acceptable as a fuse, but lost parts) | YES |

**Recommended set (A, C1, D, E, F1, G): -0.194 kg full → -0.097 kg at half credit.**
Options for the Arbiter: delete the foot top shell instead of C1 (C2: -0.13 more); delete the bellows instead of F1 (F2: -0.03 more); knee cap 1.2 mm (B: -0.02) only if the Materials dent check passes. Not double-counted with R-047.
Confirmations needed: Materials (CF slot-edge cracking, 1.0 mm foot dent, fabric TDS, TPU-film bellows fatigue); Legs (foot shell deletion); Controls/Thermal: none.
