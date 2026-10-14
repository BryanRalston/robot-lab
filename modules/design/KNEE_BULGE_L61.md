# Knee grille bulge, panel tabs, L61 boss clearance (RL Industrial Design)
Script `knee_bulge_tabs_l61.py` → `knee_bulge_tabs_l61.json`. Sources: Legs L55/L58/L61 (8908089), `TRUNNION_BREAK.md`.

## 1. Local grille bulge (Legs L55 / rev B fins)
Rev B fins sit up to **4.7 mm** outside the v5 thigh keep-out. Legs asked for a **+5 mm** local bulge.

| | |
|---|---|
| Clearance after +5 mm | **0.3 mm** to fin tip |
| A35 rule | fin tip **≥ 8 mm** from cover inner face |
| Bulge for A35 | **4.7 + 8 = 12.7 mm** |
| **Adopted** | **+12.7 mm** local blister on the knee-housing grille |
| Mass (+12.7 mm sidewall, PC 1.5) | **+0.021 kg pair** |
| Mass if only +5 mm | +0.008 kg pair (rejected: fails A35) |
| Vents | A35 open areas unchanged |

`a36_vents.py` thigh line includes this (+0.021); pair thigh −0.026 → **−0.006**.

## 2. Legs L58 tabs → merged PA12 panel
| | |
|---|---|
| Tab tips | thigh **x = −38**, **y = 100 / 160**, **z = 700 / 780** |
| Tab size | **29.5 × 8 × 2 mm** (band x = −8.5 → tip) |
| Panel bosses | **4 × M2.5** at the same (x,y,z) — pocket corners |
| Alignment | **PASS** |
| Legs tab mass | +0.004 robot (integrated clamp ears) |

## 3. L61 cheek bosses vs thigh shell / grille
Boss **ø26 × 20 mm**, **14 mm proud** of each cheek (ULTEM 4001). Fin clearance **≥ 9.0 mm** over knee 0–135° (`knee_boss_clear_r106.json`).

| check | result |
|---|---|
| Fins | PASS 9 mm all flexion angles |
| Front/rear grille +12.7 mm bulge | does **not** clear ±y bosses |
| Outboard thigh fairing | **CLASH ~9 mm EST** into keep-out (Legs left unchecked) |

**Fix (adopted):** open window **~40 × 30 mm** per cheek in the outboard fairing (**0 kg**). ±y flanks are already fin-free (L48/L55). Alt: 12 mm relief blister ≈ +0.006 kg robot.

## 4. TPU film P-052 (R-098 cite)
Face **98 × 98 mm** = 0.009604 m².

| source | ρ | 0.3 mm | 0.4 mm | 0.5 mm |
|---|---|---|---|---|
| **DoonX clear TPU (ASTM D792)** | **1.20** | **3.46 g** | **4.61 g** | **5.76 g** |
| Covestro Platilon U 4201 AU | 1.15 | 3.31 g | 4.42 g | 5.52 g |

**Recommended for R-098:** **4.61 g** at 0.4 mm, ρ **1.20** (DoonX https://www.doonx.com/products/0-3mm-clear-tpu-film).
