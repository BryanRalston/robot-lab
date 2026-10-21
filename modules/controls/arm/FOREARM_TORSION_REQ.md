# REQ: forearm torsional stiffness / first torsion mode (Controls → Arms, Job 8c gate), 2026-10-21

**Verdict:**
1. **Requirement:** first forearm/wrist torsion mode ≥ **15 Hz** with a 10 kg in-hand payload (≥ 40 Hz hand-only). Tube k_t ≥ **2.9 kN·m/rad** (10 kg) or **14.6 kN·m/rad** (20 kg, informative only).
2. **CF at 9.8 kN·m/rad PASSES the 10 kg gate:** chain 3.18 kN·m/rad, 20.1 Hz, 1.34× margin on frequency, 3.4× on tube stiffness. The 20 kg single-hand case fails (14.2 Hz), but it isn't a requirement case.
3. **The tube does not dominate:** the wrist-roll CSG-14-100 strain wave gear (K1 4.7 kN·m/rad) is the softer element. Even a rigid tube only reaches 24.4 Hz at 10 kg. CF costs −15 % in frequency against 7075 (23.6 Hz).

## Bandwidth basis (Controls requirement: not defined in the repo before this note)
Repo search found:
- the 1 kHz EtherCAT DC loop (electronics R1_ARCHITECTURE §R1.4, jitter O-E1 unverified);
- hand MCU current loops at 10 kHz (§16.8);
- no arm/wrist position or impedance bandwidth in controller_config, the WBC, CONTRACTS or the arm docs.

**Set here as the Controls requirement:**
- Wrist-roll / forearm-roll position-impedance loop closed-loop bandwidth **8 Hz hand-only** (manipulation).
- **3 Hz with a payload ≥ 2 kg in hand**, gain-scheduled on the payload estimate. Transport/carry needs no more, and the CSG-14 repeated peak of 36 N·m limits payload angular acceleration anyway.
- The current-loop bandwidth (drive) is ≥ 10× these, so it is not limiting.

**Separation rule:** first structural mode ≥ **5× closed-loop bandwidth**. I chose the top of the 3–5× range because the mode is **non-collocated**: the motor-side encoder sits behind the gear and tube, so a 3× mode would land inside the gain-crossover phase budget. That gives 15 Hz (payload) and 40 Hz (hand-only).

**1 kHz loop check:** at 15–40 Hz, the 1 kHz sample plus 1 cycle compute delay (≈ 1.5 ms) costs 8–22° of phase at the mode. Modes are ≤ 1/25 of the loop rate, so no aliasing or ZOH issue. There is no upper-frequency constraint from the 1 kHz loop.

## Series chain (torsion about the forearm axis, hand side → elbow)
- **Wrist roll:** TBM2G-05008C + **CSG-14-100** (arm_inertials_r3 / CONTRACTS §1a).
  - Harmonic Drive catalog, CSG-14-100 (harmonicdrive.net product page): K1 0.47, K2 0.61, K3 0.71 ×10⁴ N·m/rad (T1 2 N·m, T2 6.9 N·m).
  - **K1 = 4.7 kN·m/rad** is used: small-oscillation, low-torque region (conservative).
- **Forearm tube k_t:** Arms R7 §G (d350f94) hand calc: CF ≈ 9.8, 7075 ≈ 69 kN·m/rad.
- **Not included:** joints proximal of the elbow (the elbow and shoulder axes are not about the forearm axis with the elbow bent), fitting/bond compliance (Job 8c should report it), and the wrist pitch/yaw push-rod path (it carries bending, not roll).
- Chain: CF 1/(1/9.8 + 1/4.7) = **3.18**; 7075 **4.40** kN·m/rad.

## Payload inertia about the forearm axis [EST, no P-042 box drawing in the repo]
- **10 kg, single hand:**
  - Arms' offset term m·r² = 10·0.1² = 0.1 kg·m² (R7 §G);
  - plus the box's own inertia, scaled from the sim 20 kg carry box diaginertia 0.2/0.15/0.2 (gait_lib/eval_box) to 10 kg: 0.1.
  - **I₁₀ = 0.2 kg·m²**. That is double Arms' 0.1, so their 50 Hz estimate (k 9.8 alone, I 0.1) drops to 20 Hz with the gear and box terms.
- **20 kg (P-042 total):** I₂₀ = 0.4. In P-042 the 20 kg is carried with two hands, so each forearm sees about the 10 kg case, and the second arm closes the loop on box roll, which only adds stiffness. A 20 kg single-wrist case exceeds T5 (10 kg one-hand), so it is informative only.
- Hand alone: 3.8e-4 kg·m² (Arms).

## Requirement numbers

| Case | I (kg·m²) | f_min (Hz) | k_chain min (kN·m/rad) | k_tube min (kN·m/rad) | CF 9.8 f (Hz) | 7075 f (Hz) | Rigid-tube f (Hz) | CF |
|---|---|---|---|---|---|---|---|---|
| Hand only (8 Hz BW) | 3.8e-4 | 40 | 0.024 | 0.024 | 460 | 542 | 560 | PASS (11.5×) |
| **10 kg (3 Hz BW), gate** | 0.2 | **15** | 1.78 | **2.86** | **20.1** | 23.6 | 24.4 | **PASS, f 1.34×, k_tube 3.4×** |
| 20 kg single hand (informative) | 0.4 | 15 | 3.55 | 14.6 | 14.2 | 16.7 | 17.3 | fails (0.95×); not a requirement case |

**Job 8c gate:**
- Report k_t of the bonded assembly, including the spigots and bond, and the first torsion mode with I = 0.2 kg·m² at the hand plus the CSG-14 K1 in series.
- **Pass:** f ≥ 15 Hz, equivalent to k_tube ≥ 2.9 kN·m/rad. The ±45° overwrap is not needed unless the assembly k_t falls below 2.9.

Open items: P-042 box drawing (real inertia); the wrist-roll loop bandwidth to be confirmed in G5 bench tuning (the mode shows up as a resonance in the closed-loop sweep).
