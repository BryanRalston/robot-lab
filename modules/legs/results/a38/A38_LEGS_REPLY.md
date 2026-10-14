# Legs reply to Materials A38 (A37 rev B, Arbiter R-053), 2026-10-14
Tags: [CAD] measured in model_v4 / CadQuery · [FEA] box 2D plane stress (tine_fea_a38.py) · [EST] hand estimate · [cat] catalogue value, verify against the datasheet.

## L1: metal contact paths from motor/lever to the thigh collar (from model_v4)
1. **Main path (broken by rev B):** motor → screw body → axial GE12 C eye → ø12 42CrMo4 clamp-eye pin → **PEI sleeve + 3-pad flanges** → 7075 tines → clamp arm → collar → DP490 → femur.
2. **Parallel path, NOT broken:** screw shaft/nut → RV12 rod → lever-end GE12 eye → lever pin → hip lever → TLA3520 needles → ø35 shaft → femur tongue → femur tube → inside the collar bond.
   - Order-of-magnitude [EST]: rod ø12 steel ~150 mm gives ≈ 29 K/W, plus lever/shaft/tube, so ≈ 40 K/W or more in parallel with the ≥ 20 K/W break.
   - In parallel that gives **≈ 13 K/W total if the rod-side heat input equals the motor's.**
   - **Thermal must decide whether this path counts.** Its source is screw/nut friction heat, not the motor case.
3. **Hip lever cheeks are NOT bolted to the collar.** They bolt to the hip-roll output bracket (pads at |y| 32.5, model_v4 l.133–137). That bracket is on the pelvis side, so it is not in the collar path.
   - The rev B Ti compression limiters are therefore **not needed at the cheeks for the collar break: 0 bolts, 0 g** (rev B booked ≈ 1 g/bolt).
   - If any bracket or harness clamp is later bolted from the motor/body to the clamp arm or collar, the limiter rule applies: Ti-6Al-4V OD8.5/ID6.4, L ≥ 10, PEI only as an unloaded spacer with ≥ 0.3 mm air gap.
4. **Within the thigh, not a motor path:** collar split bolts, 2× ø6 cross pins, internal sleeve.
5. **Harness/encoder P-clips** on the screw body that land on the thigh: they must be polymer or have a PEI liner. This is a spec note for Electronics.
6. **Hip stop PU bumper:** on hipR, polymer. Not a path.

## L2: tines at the ø20 bore (rev B)
- Edge distance: the current tine has e = 12 (pin centre to free end, model_v4 / L41 rule ≥ 12). **With ø20 the ligament is 2 mm, which FAILS:**
  - [FEA] 974 MPa peak at 6.55 kN/body fault (3275 N/tine, toward the free end);
  - 676 MPa at walking (4542 N/body).
- **Fix: e = 20 (e/D 1.0) with a ROUNDED END R15 centred 5 mm beyond the pin.** [FEA, square-end e20 proxy]:
  - fault 185 MPa, walking 128 MPa. That's the same as today's ø12 e12 tine (192 / 133). SF vs Sy 503 is 2.7 at fault.
  - Net section 40.9 MPa, bearing on 7075 20.5 MPa.
  - Caveats: 2D, no pin bending, cosine bearing. The rounded end removes only unloaded corners.
  - The e16 option gives 232 MPa (+21 %), so it is not taken.
- Clearance [CAD]: an all-round R20 lug envelope about the pin clears the screw eye-stub flange [EST] by **4.0 mm** at every hip_pitch from −107.3 to +40. Nothing else comes within 4 mm (tine_clear_a38.py).
- **Mass (7075, 8 tines):** rounded e20 ø20 minus current square e12 ø12 gives **−1.3 g/tine, −10.4 g robot** [CAD area × t8].

## L3: pin retention and flange clearance
- The eye gap between the tines is 12 mm (model_v4). GE12 inner ring B = 10 [cat].
- **Keep the tines where they are; do not lengthen the pin.** A 2 mm spread would add +4 mm × 4 pins = +14 g of steel and break the freeze.
- **Flange land height 0.85 mm** gives 0.3 mm total axial play.
- **Land pads must sit within ø12–17**, inside the GE12 inner-ring shoulder dk ≈ 18 [cat]. That way the misaligned outer ring can't touch them at tilt.
  - 3 × 120° pads at ≥ 30 mm² per face still fit (annulus 114 mm²).
- **Retention:** a headed pin plus retaining ring will short the break if the head/ring touches 7075.
  - Spec: the PEI sleeve protrudes 0.5 mm beyond the tine OUTER face.
  - The pin head and the ring seat only on the PEI sleeve end, or on a 1 mm PEI washer (≈ 0.26 g each [EST]).
  - Keep ≥ 0.3 mm air gap from the 7075 face.

## L4: axial load on the eye [EST]
- The screw is a two-force member with spherical eyes at both ends, so axial (pin-direction) load comes only from body inertia and liner friction.
- Body + motor ≈ 1.0 kg [EST]:
  - walking lateral ≤ 2 g → ≈ 20 N;
  - fall 50 g (T8) → ≈ 0.49 kN;
  - plus friction μ 0.1 × radial 3.3 kN ≈ 0.33 kN while misaligning.
- **Against the Materials lands:** sustained 0.84 kN gives SF ≥ 2.5 (friction-bound); fault 2.3 kN gives SF ≈ 2.8 (0.82 kN combined).
- Bench check in G5.

## Net mass vs R-053 booking +0.017 kg
| item | g (robot) |
|---|---|
| PEI sleeves (Materials) | +20.9 |
| rev A washers dropped | −2.0 |
| tines, rounded e20 ø20 vs current [CAD area] | −10.4 |
| PEI retention washers 8 × 0.26 [EST] | +2.1 |
| cheek Ti limiters (not bolted to collar) | 0 |
| pin length (no change) | 0 |
| **net** | **+10.6 g = +0.011 kg, 0.006 under the booked +0.017** |
