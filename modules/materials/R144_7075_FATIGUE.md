# R-144: 7075-T6 hip pitch lever fatigue allowable (check of the 58 MPa)
RL Materials, 2026-10-21. [EST] = estimate.

## Inputs (legs/grokbuild/l47_shape_opt_brief.md, reliability/R1_FEA_REVIEW.md)
- Load: 2030 N per pin, **fully reversed (R = −1)**. The hot-spot amplitude comes from FEA, so Kt is already in the stress.
- Section/finish: machined 7075-T6, fillets R8 (L69). The brief gives no section size; the arm slab is ~20 mm equivalent [EST].
- **Design life: not stated** in the brief or in R-031.
  - [EST] 0.9 strides/s × 8 h/day × 365 × 5 y ≈ 4.7×10⁷ cycles, so **10⁸** is used as the design life (≈ 10 y at 8 h/day).

## Cited S-N basis: MIL-HDBK-5H Figure 3.7.4.1.8(a), p. 3-382
https://ssrl-uark.com/MILHDBK5H.pdf
- Test: 7075-T6 rod/bar, **unnotched**, axial, RT, 8 heats, n = 130, surface unspecified, TUS 82 ksi.
- Fit: log Nf = 18.21 − 7.73 log(Seq − 10), with Seq = Smax(1−R)^0.62 [ksi]. At R = −1: Seq = 1.537·Sa.

| N | Sa, unnotched (mean fit) |
|---|---|
| 10⁷ | 24.9 ksi = **171 MPa** |
| 10⁸ | 20.1 ksi = **139 MPa** |
| 5×10⁸ | 17.6 ksi = **121 MPa** (beyond the data, extrapolated) |

- Check against the notched curve, Fig 3.7.4.1.8(b), p. 3-383 (Kt 1.6, polished, R = −1): log Nf = 8.28 − 2.62 log(Seq − 15), Seq = Smax(1−R)^0.53 → **86 MPa net at 10⁷**.
- The MakeItFrom/ASM 159 MPa (rotating beam, 5×10⁸) is higher than the 5H axial fit. **Use 5H.**

## Marin factors (Shigley, Mechanical Engineering Design, §6-9; calibrated on steels, applied to Al [EST])
- **ka, machined:** 4.51·Sut^−0.265 = 4.51·560^−0.265 = **0.843**. R1 used 0.75, which is more conservative.
- **kb, size, bending:** 1.24·d^−0.107 at d ≈ 20 mm = **0.90** [EST d]. Axial-type 5H data → kb = 1 for pure axial.
- **ke, reliability 99 %:** **0.814** (R1, Shigley Table 6-5).
- **Kf:** FEA hot-spot stress already includes Kt. At R8 in 7075, q ≈ 0.95 (Peterson, r = 8 mm) [EST], so Kf ≈ Kt and there is no notch relief.
- **Mean stress:** R = −1, so no Goodman correction. If a case has mean stress, use Goodman against Su = 560 (MATERIALS_DB, typical) [or A-basis Ftu for single-path].
- **Allowable amplitude** = Sa(N) × ka × kb × ke / 1.5:

| N | Se | /1.5 |
|---|---|---|
| 10⁷ | 171 × 0.618 = 105.7 | **70 MPa** |
| **10⁸** | 139 × 0.618 = 85.9 | **57 MPa** |
| 5×10⁸ | 121 × 0.618 = 74.8 | **50 MPa** |

## Verdict
- **58 MPa is CONFIRMED** (57 MPa computed) for a design life of **≤ 10⁸ cycles**.
- If the robot's life target is 5×10⁸, **correct to 50 MPa**. The life target must be set by Reliability/Arbiter; it is not in any brief.
- Candidate 0's hand estimate σa ≈ 32 MPa passes either way.
- Caveats:
  - The 5H fit is a mean curve, not a design minimum; the 0.814 reliability factor and the ÷1.5 cover the scatter.
  - Hard anodize (if used) cuts fatigue strength by about 30–60 % [EST]. Do not hard-anodize the lever hot spots (ANKLE_CROSS_7075 §2 rule applies).
  - Fretting at the pin bores is not covered here.
