# RL Arms & Hands R12 (2026-10-21): qualifying ID R9 pad (a688e28). Supersedes the R11 recommendation.
Calc: `pad_fix_r12.py` / `.json`.

**Loads:**
- ID R9: 55.3 mm core, 7.0 kN peak, PTFE skin μ ≤ 0.15.
- At 15°: Fn = 6.76 kN. Tangential force capped by the skin at μFn = **1.01 kN** (instead of 1.81).
- Gates: s0 ≥ 2.0 at e ≤ 10 (5) mm; CSG-25 momentary 369 N·m at fault ×1.05; full ROM; pad on the roll output, so the R10 angles hold.

| combo | s0 e0 / e5 / e10 | roll torque (down), SF at fault | pass | Δ pair vs booking [EST] |
|---|---|---|---|---|
| (i) R9 alone (pad centre 64 mm below roll axis) | 2.40 / 2.20 / 2.04 | 521 N·m → **0.67 ✗** | ✗ (**gear**) | 0 |
| (iv) R9 + CRBH 7013 A (C0 27.7 kN, 0.38 kg, cited) | 2.83 / 2.62 / 2.43 | 521 → 0.67 ✗ | ✗ | +0.16 |
| (ii) R9 + full carrier, pad on the roll axis, CRBH 6013 kept | 2.35 / 2.16 / 2.00 | 117 → 3.0 ✓ | ✓ (e10 at the limit) | +0.09 |
| **(iii) R9 + partial stand-off, pad centre 20 mm below the roll axis, CRBH 6013 kept** | **2.41 / 2.21 / 2.04** | **242 → 1.45 ✓** | **✓** | **+0.05** |
| (iii) at 37 mm below the axis | 2.41 / 2.21 / 2.04 | 352 → 1.00 (limit) | marginal | +0.04 |
| (ii) + (iv) | 2.78 / 2.57 / 2.40 | 117 → 3.0 | ✓ | +0.25 |

**Mass basis:**
- The booked boss is 0.024/side; a solid 62 × 62 × 10 boss is 0.108, so the booking was under.
- (iii): a 7075 stand-off block of ~0.050/side replaces the boss (+0.026/side).
- (ii): the wrap carrier is ~0.070/side.
- (iv): the bearing adds 0.05/side (cited) plus ~0.03 for housing growth.
- ID's smaller-core saving is not counted here (ID books it).

**Recommendation: (iii).**
- ID R9 core and PTFE skin, plus a machined 7075 stand-off that puts the pad centre **≤ 20 mm below the roll axis** (it was 64). CRBH 6013 and CSG-25 are kept.
- **Qualify e ≤ 5 mm** (s0 2.21). ≤ 10 mm gives 2.04, which is too thin to carry through FEA mesh scatter.
- Δ ≈ **+0.05 kg pair** [EST], within the reserve.
- R11 option B (+1.1 kg) is **withdrawn**.
- ID R9 alone **does not** fix the roll gear (521 N·m vs 369).
- A C0 ≳ 27 kN bearing (CRBH 7013) fixes s0 only and is not needed.
- Heavy: the job1 FEA re-run on (iii) geometry is a bryan-PC Job 8 add-on.
