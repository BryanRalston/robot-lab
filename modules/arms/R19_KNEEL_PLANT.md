# RL Arms & Hands R19 (2026-10-21): R-150 hands-first kneel hand plant and elbow 2 s torque (for Controls, 019f0c6)
Calc: `kneel_plant_r19.py` → `kneel_plant_r19.json`. Hand calcs; nothing is measured.

Input (Controls DR worst case, 68.5 kg): left 0.40 m/s / **1525 N** peak, right 0.37 m/s / 1520 N. The left hand governs.

## 1. Hand plant: verdict FAIL at 1525 N unless the posture below is used AND the force is capped (or Actuators supports the wrist bearing)

**Load offset e:** e is the distance from the contact-force line to the wrist pitch/yaw axes. With a flat palm, e ≈ 45 mm (palm centroid). A heel plant gives e ≤ 10 mm.

| item | limit (source) | flat palm (e ≈ 45) | heel plant (e ≤ 10) | result |
|---|---|---|---|---|
| **wrist pitch/yaw output bearing CRBH 258 A** (D76), P0 = Fr + 2M/dp, dp 33 | C0 **2810 N** (`iko_crb_catalog.txt` l.796); s0 ≥ 2.0 impact (Arms gate, as for the shoulder) | s0 < 0.6 | **s0 1.15** (1.84 even at e = 0) | **FAIL** |
| wrist pitch/yaw gear CSG-14-100 | rep peak 36 / momentary 70 N·m (CSG Table 3) | 68.6 N·m: SF 0.52 rep / 1.02 mom | 15.2 N·m: **SF 2.36 / 4.59** | pass heel / fail flat |
| wrist roll CSG-14-100 (friction μ 0.3 × half-palm 16 mm) [EST] | 36 | 7.3 N·m, SF 4.9 | same | pass |
| wrist roll CRBH 258 A (mostly axial) | C0 2810 | — | s0 2.96 | pass |
| **palm P-021 grip face** 1.5 mm, uniform over 60 × 70 | 308 MPa (T651 1.5 in, `STOCK_GRAIN.md`) | **319 MPa** | n/a | **FAIL flat** |
| palm heel edge, 10 mm cantilever, 1.5 mm skin | 308 | — | **473 MPa** | FAIL |
| palm heel with a **4 mm heel band** (20 mm × 86, +0.012 kg/hand, full) | 308 | — | **66 MPa, SF 4.7** | pass |
| fingers / tendons | 38 N fingertip continuous, D-Pro tendon SF 7.1 (R1_ARCHITECTURE l.43) | any finger contact at 1525 N fails | fingers clear the floor | pass only if fingers are off the floor |
| forearm (CF Job 8c or Al) axial | Euler 3.7 MN; bond 0.36 MPa vs 4.6 (SF 12.7) | | | pass |
| elbow clevis lugs (R17, 9 mm) | 294 | 163 MPa (SF 1.8) | | pass |
| elbow torque | derated cap 38 N·m | | line of action within **25 mm** of the elbow axis (50 mm at 76) | posture |
| shoulder pitch/roll | derated cap 83.5; CSG-25 momentary 369 | | line of action within **55 mm** of the shoulder axis (161 mm at 369 / 1.5) | posture |
| W2 carrier / 7013 | not in path | | | pass |

**Posture required (Controls):**
- **Heel plant.** Arm near vertical, wrist pitch dorsiflexed about 50–60° (inside the ±60 ROM), wrist yaw 0 ± 5°. Contact on the palm heel at the wrist-plate edge, with the force centroid ≤ 10 mm from the wrist pitch and yaw axes.
- A flat palm is not allowed: it gives e ≈ 45 mm, and the face is also over its limit.
- **Fingers extended and off the floor.** At about 30° palm tilt the fingertips sit about 90 mm up. Finger drives are passive: zero torque, tendons not pre-tensioned. No fist (load would go on the MCP clevis slots).
- **Elbow slightly flexed, about −5 to −10°.** Not on the 0° stop. Line of action ≤ 25 mm from the elbow axis.
- **Shoulder over the hand.** Line of action ≤ 55 mm from the shoulder axis at the derated cap.

**Fix needed (one of these):**
- (a) Controls caps the plant force at **≤ 875 N per hand** at e ≤ 10 (≤ 1078 at e ≤ 5). That means roughly ≤ 0.23 m/s, assuming F scales with v.
- (b) Actuators supports the D76 pitch/yaw output on both sides (second bearing or bushing; mass to the Arbiter), which roughly doubles s0.
- (c) The Arbiter accepts s0 ≥ 1.15 for a rare fault-path event. IKO's minimum for normal operation is 1–2. Not recommended for a DR worst case.

Separately: **ID/Arms add the 4 mm heel band** (+0.024 kg pair, full). That needs an update to `palm_7075.py`, not done here.

## 2. Elbow: about 2 s at an 82 °C drive temperature

**Where the 38 N·m comes from:** `controls/limits/DRIVE_DERATE.md` l.164, 38 = **0.5 × 76**.
- 76 is τ_nominal: CONTRACTS §1a elbow "v3 avail 76" (TBM2G-05013C + CSG-20-100; gains.npz `tau_lim`, [EST until commissioning]).
- 0.5 is the R-141 / R-146 drive-temperature curve: 1.0 at 75 °C, falling linearly to 0.5 at 82 °C. It protects the **Elmo drive** (P-055, Electronics). Nothing in the motor or gear sets it.

| limit | value (source) | 2 s capability |
|---|---|---|
| gear CSG-20-100 | rated 52, rep peak 107, momentary 191 N·m (CSG Table 3) | 107 (not limiting) |
| motor peak / hard cap | 76 avail (CONTRACTS); 69 hard cap (DRIVE_DERATE) | 69 |
| winding (K_m,hot 0.069, C_w 68.5 J/K, τ_w ≈ 2.3 min, O-A2) | 155 °C abs (TBM2G) | 2 s at 69 N·m = +5.1 K (adiabatic), not limiting while the winding is below ~145 °C |
| **drive temperature** (adiabatic bound 1.19 K/s at full current, DRIVE_DERATE sit table; ∝ I²) | latch 83 (R-142), **81 for the hands-first path (R-150 §2)**, own trip 85 | **≤ 1 K rise in 2 s → τ ≤ 49 N·m**. At 69: +2.0 K → 84 °C, which crosses the latch |

**Answer:**
- **It can be raised to about 49 N·m for ≤ 2 s at an 82 °C drive reading [EST].** The drive's own heating sets the limit. Gear, motor and winding all allow 69.
- With measured elbow-drive heating (it's housing-mounted, so likely well below the 1.19 K/s knee-drive bound), the 2 s cap could rise toward the 69 N·m hard cap.
- **Caveat:** under R-150 §2 the hands-first path latches at 81 °C. So an 82 °C elbow case exists only on the fallback crouch-hold path. On the kneel path the elbow never runs past 81.
- **Owners:**
  - The number lives in Controls' DRIVE_DERATE curve (R-141 / R-146, Arbiter).
  - The heating rate is Electronics/Thermal's to measure (P-055; elbow drive K/s at full current).
  - Actuators owns the 76 / 107 / 191 ratings and confirms τ_nominal.
  - A raise means Controls proposes it to the Arbiter as a 2 s I²t allowance on the elbow, once Electronics' rate is in.
