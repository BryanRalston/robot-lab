# D97: PU knee stop pair at 135° (RL Actuators, 2026-10-21)
Script `knee_stop_pu_d97.py` → `results/knee_stop_pu_d97.json`; CAD sketch `cad/knee_stop_pu_pad_d97.step` (one pad).
**Basis:** Controls 0fb7c0e: 6.2 rad/s at the 135° stop (forward fall, MO=0). The RV12 is never the stop (D96, Robot Lab).

**Inertia and energy (per knee):**
- **Body/segment:** I ≈ 2.71 kg·m². Fitted from Controls' MuJoCo peaks using the solref (dampratio 1) relation τ = 2Iω/tc; 6825/3333/1665 N·m at tc 0.005/0.01/0.02 s all give 2.69–2.75.
- **Rotors:** 2 × (TBM2G-07613D Jm 0.576 kg·cm², tbm2g_manual p.284, + 0.2 kg·cm² nut-rotor hub [EST]) × 59.7² = **0.553 kg·m²**.
- **Energy:** ½ · 3.26 · 6.2² = **62.7 J**, of which the rotors are 10.6 J (**17 %, not dominant**).

**Pad:** 2 pads, tongue → clevis, at **r 60 mm** from the knee axis. Each pad is a 30 × 30 face, **3 × 12 mm cast PU 90A** (Freelin-Wade PUR90A TDS: 92A, ASTM D575 compressive 2/5/10/15/20/25 % = 160/325/705/1050/1380/1690 psi) with 2 × 1 mm steel shims, 38 mm tall. Shape factor 0.625 per layer (≥0.5; below 0.25 risks buckling, per the Gallagher/Boedeker guides). 90A dynamic strain limit 25 % (Gallagher design table). PU volume 64.8 cm³.

**Stiffness curve (2 pads, contact at 135°):**
| knee past 135° | PU strain | stop torque N·m | energy J |
|---|---|---|---|
| 0.7° | 2 % | 119 | 0.7 |
| 1.7° | 5 % | 242 | 4.0 |
| 3.4° | 10 % | 525 | 15.5 |
| 5.2° | 15 % | 782 | 35.1 |
| 6.9° | 20 % | 1028 | 62.2 |
| 8.6° | 25 % (limit) | 1258 | 96.5 |

That is about 8.6 kN·m/rad secant (≈ 8.7 tangent, gently stiffening).

**Result:**
- Peak strain 20.1 %, **peak torque ≈ 1030 N·m**.
- **Stroke 6.9° / 7.2 mm at the pad**; maximum knee 141.9°, inside the 145° clash-free range (D96 housing gap 3.5 mm at 145°).
- Energy capacity to 25 %: 96.5 J, **SF 1.54**.
- Pad force 17.2 kN total.
- PU hysteresis (Bayshore resilience 34 %) means low rebound.
- Compared with Controls' rigid-limit estimates (1665–6825 N·m), this is 0.6–0.15×.

**Screw load from rotor deceleration:**
- The rotor share of the stop torque is 1030 × 0.553/3.26 = 175 N·m at the joint, i.e. 3680 N per pair through the 47.5 mm lever. That's **1840 N per screw, or 2590 N with the arm reduced to 0.71 at 135° [EST]**.
- That is **0.095 C0a (27.3 kN)**, well under the 0.5 C0a target and below the motor-peak 3634 N already in the D80/forging checks.
- So the twin housing, trunnions and forging (75.7/211 MPa at 3634 N) are not exceeded.

**Structure owed (Legs):** the stop torque of ~1030 N·m goes through the shank tongue and thigh clevis as **≈17.2 kN pad force at r 60**. That is about 3× the knee motor-peak torque (345 N·m) these parts were sized for (clevis σ ≤ 105 MPa at 7267 N screw force). Legs needs to check the tongue, the clevis pad seats and the pad bolts at 17.2 kN (rare event, static plus the fall allowable).
- If the tongue/clevis can't take it, the fallback is r 75 mm with 3 × 15 mm layers: about 830 N·m, 8.6° stroke, max 143.6° [EST scaled].

**Mass:** PU 73 g + shims 28 g + 2 holders 30 g [EST] = **0.131 kg per knee, 0.263 kg robot**. New mass, over the freeze.
**Envelope:** two 40 × 40 × 41 mm pad stacks at r 60, either side of the 28 mm tongue (y 116–144) or on its back face, in the thigh clevis. Legs needs to place them in model_v4 and sweep.
