# A38: unbroken rod → lever → shaft → femur path vs the A37 thermal break (RL Thermal, 2026-10-14)
Legs L49 / `legs/results/a38/A38_LEGS_REPLY.md` path 2:
screw shaft/nut → RV12 rod → lever-end GE12 eye → lever pin → hip lever → TLA3520 needles → ø35 shaft → femur tongue → femur tube (inside the collar bond).

## Does it count? **Yes.**
- It ends on the femur tube inside the DP490 bond, so it lands on the same node as the collar.
- The screw shaft/nut sits in the motor/screw body at roughly case temperature (≈ 85 °C at A35 h 15). Nut friction adds to that, not replaces it.
- Per A37, **every metal path from the hot body to the bonded femur counts in parallel.**

## Is Legs' ≈ 40 K/W right? **About right as a conduction number, conservative overall.**
- **Rod as a bar:** ø12 steel (k 42), 150 mm: L/kA = **31.6 K/W**.
- **The rod is in free air, so it acts as a fin**: mL = 1.46–1.64 at h 12–15.
  - End-to-end transfer resistance = sinh(mL)/(kAm) = **44–48 K/W**.
  - The far end sees only 1/cosh(mL) ≈ 0.37 of the hot-end excess.
- **Eye + pin + lever + needle bearing + ø35 shaft + tongue:** +≈ 10 K/W [EST; needle-bearing contact dominates].
- **Path total ≈ 55–60 K/W** (58 used). Legs' 40 K/W is the conservative bound.

## Bondline consequence (35 °C, T_bond = 35 + ΔT_case·R_col/(R_total + R_col))
| rod path | main break | R_total | A35 h 15 (ΔT 50), R_col 8 / 14 | vents short (ΔT 62.6), R_col 8 / 14 |
|---|---|---|---|---|
| 40 (Legs) | 20 | 13.3 | 53.8 / **60.6 FAIL** | 58.5 / **67.1 FAIL** |
| 58 (Thermal) | 20 | 14.9 | 52.5 / 59.2 (0.8 K margin) | 56.9 / **65.4 FAIL** |
| 58 | 26 | 18.0 | 50.4 / 56.9 | 54.3 / **62.4 FAIL** |
| 85 (PEI-lined lever eye) | 20 | 16.2 | 51.5 / 58.2 | 55.7 / **64.0 FAIL** |
| **85 (PEI-lined lever eye)** | **26** | **19.9** | **49.3 / 55.6** | 52.9 / 60.8 (≈ limit) |

- With the path unbroken, the A37 "≥ 20 K/W total" is **not met**: about 13–15 K/W.
- **The bond passes only at the design vents with R_col ≤ ~13**, which is not defensible.

## Fix (both items needed to restore ≥ 20 K/W total)
1. **Insulate the lever-end GE12 eye** the same way as the clamp tines: PEI sleeve on the lever pin with flange lands, ≥ 0.3 mm air gap at the faces (≈ +25 K/W in series). That takes the rod path to ≈ 85 K/W. Mass ≈ +3 g/leg [EST]. Legs to check the lever-pin bearing stress.
   - **Alternative:** PEI/polymer liner on the TLA3520 shaft seat. Not preferred because it sits in the needle-bearing load path.
2. **Raise the main tine break from ≥ 20 to ≥ 26 K/W**: PEI sleeve OD 22 (from 20) with ≤ 15 % lands (A37 table: pin path ≈ 30 K/W). Legs to recheck e/D at ø22.
   - Result: total ≈ 20 K/W, bond 49–56 °C at the design point.
- A longer rod is not an option (kinematics).
- J-T1 and the G5 collar thermocouple still decide R_col. If R_col ≤ 8 is measured, item 2 can be dropped.

## Rev (Legs d81dcba L55–L57): knee paths to the femur, and whether the lever-eye sleeve is still needed
**New knee paths:**
- knee housing → trunnion bearings → thigh-side trunnion bracket strut/top plate → femur (knee end);
- rod → knee lever → pin → clevis (≥ 58 K/W, minor).
**Femur fin model:**
- Ø50 × 1.2 mm 7075 (k 157): m = 8.0 /m (h 12) / 10.3 (h 20), kAm 0.24 / 0.30 W/K.
- 160 mm to the collar, attenuation e^(−mL) = 0.28 / 0.19.
**Knee source and coupling:**
- Knee case ≈ 95 °C at carry (rev B, drives off).
- Housing → femur via the trunnion bearings + bracket: R_tr 2.5–5 K/W (D69B option B, [EST]).
- Femur-end local sink: tube fin + bracket ≈ 0.34 W/K.
Script `a38_knee_path.py` → `results/a38_knee_path.json`. The collar add is taken conservatively as θ_knee-end × e^(−mL), superposed on the A38 hip result. That ignores the collar's own sink, so the real add is ≈ ½–1×.

| knee path | femur knee-end | heat into femur | add at the bond (h 12 / h 20) |
|---|---|---|---|
| unbroken, R_tr 2.5 | 69 °C | ≈ 10–12 W | **+9.5 / +5.9 K** |
| unbroken, R_tr 5 | 59 °C | ≈ 7–8 W | +6.8 / +4.0 K |
| **with a PEI break at the bracket–femur joint (R_tr ≥ 30)** | 42–43 °C | ≈ 1.7 W | **+2.2 / +1.2 K** |

**Bond, A35 design vents (h 15), tine ø22 rev D (≈ 26 K/W), R_col 8 / 14:**

| hip rod path | knee path | bond °C | ≤ 60? |
|---|---|---|---|
| no lever sleeve (58) | unbroken | 54–60 / **61–66** | **NO** at R_col 14 |
| lever sleeve (85) | unbroken | 53–59 / **60–65** | **NO** at R_col 14 |
| **no lever sleeve (58)** | **trunnion break** | **≈ 52 / ≈ 59** | **YES** (≈ 1 K at R_col 14) |
| lever sleeve (85) | trunnion break | ≈ 51 / ≈ 58 | YES |
| any | any, vents short (h 12 case ΔT 62.6), R_col 14 | ≥ 62 | NO; depends on A35/A36 venting and on J-T1/G5 R_col |

**Rulings:**
- **(a) With the ø22 tine break, the bond is ≤ 60 °C only if the knee trunnion path is broken.** This holds with or without the lever-eye sleeve. With the knee path unbroken it fails at R_col 14 even with the sleeve. At R_col ≤ 8 everything passes.
- **(b) The lever-eye sleeve is NOT required.** It buys only 1.1–1.3 K, while the knee path costs 4–9.5 K. **Skip the Actuators ear redesign (+0.057 kg).** Keep it as a reserve option if J-T1/G5 shows R_col > 12 K/W.
- **(c) YES, the knee trunnion path needs its own break:**
  - PEI (or G10) insulating washers and sleeves at the trunnion bracket strut/top-plate-to-femur joint;
  - Ti-6Al-4V compression limiters at every bolt (A37/L49 rule, PEI unloaded, ≥ 0.3 mm air gap at the faces);
  - target **≥ 30 K/W** for that joint.
  - Legs' +8.6 g is accepted. The rod → knee lever → clevis path (≥ 58 K/W) does not need a break.
- **Verification:** J-T1 and the G5 collar thermocouple remain the gate (R_col, real collar sink).
