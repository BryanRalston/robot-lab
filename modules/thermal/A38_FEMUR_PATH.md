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
