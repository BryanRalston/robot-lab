# T-031 chest contact: Materials input (R-076), with Torso T031_chest_contact.md
Basis is the same as the shoulder pad (R042 Parts 3–6):
- HexWeb CR III 5052 4.5 pcf, crush 1.79 MPa typical; stabilized compressive modulus **150 ksi = 1.03 GPa** (HEX_CRIII).
- **±3 % lot cert**, rate factor 1.10–1.30 [EST band], ×0.93 at 15° (HC_ANGLE_PMC).
- Usable stroke 0.72 t [assumption, same as the shoulder pad].
- Pre-crushed with no initial peak, per the R-072 lot rule.
- CF shell values are Torso's [EST] (no cited CF laminate data in the DB).

## Correction to Torso's band (they used no lot tolerance and 0.70 stroke)
| | Torso | **Materials (±3 % lot, 0.72)** |
|---|---|---|
| σ band | 1.97–2.33 MPa | **1.910–2.397 MPa** |
| area for ≤ 24.4 kN absolute peak (2.397 × A) | 0.0105 m² | **0.0102 m² (≈ 101 × 101 mm)** |
| plateau 0° | 20.7–24.4 kN | **19.4–24.4 kN** |
| plateau 15° | 19.2–22.7 kN | **18.1–22.7 kN** |
| stroke for 1.02 kJ at the 15° floor | 53 mm | **56.4 mm** |
| core thickness | 76 mm | **78 mm** |
| core mass | 0.058 | **0.057 kg** (0.0102 × 0.078 × 72) |
| + 1 mm CF face + bond [Torso EST] | 0.020 | 0.020 → **pad ≈ 0.077 kg** (full credit, R-076) |

## Force–deflection curve (for Controls `--chest-k/--chest-zeta`; plateau model preferred)
| deflection | force | mechanism |
|---|---|---|
| 0 → ~0.5 mm | linear: shell local + spreader seating, k ≈ 46 kN/m bare-shell [Torso EST] is irrelevant once the pad bears on the bulkhead | pad seated on the bulkhead/frame (Torso to confirm a backed seat) |
| 0.5 → ~0.7 mm | core elastic, k_core = E·A/h = 1.03 GPa × 0.0102 / 0.078 ≈ **135 kN/mm**, rises to the plateau in ≈ 0.15–0.18 mm | pre-crushed core, no initial peak (lot rule) |
| ~0.7 → 56 mm | **plateau 19.4–24.4 kN (0°), 18.1–22.7 kN (15°)**, ×0.73 at 25° | progressive fold |
| > 0.72 t ≈ 56 mm | rises steeply (densification) | stroke exhausted, so the gate fails |

- **Damage deflection:** the core is single-use from the start of crush, at about 0.7 mm. The spec should treat any crush > 2 mm beyond the pre-crush as a replace-the-cartridge event (same as the shoulder).
- The **CF shell** must not take the load in bending: the bare shell is damaged at ~1–1.5 kN, ~10 mm [Torso EST]. The pad must seat on a backed bulkhead or frame, **not on the unsupported 2 mm panel**. That needs a Torso check.
- **Damping:** plastic crush with essentially no elastic rebound. The rebound energy is ≈ the elastic part, F²/(2k) = 24 400²/(2 × 135 × 10⁶) ≈ 2.2 J vs 1 020 J absorbed (< 0.3 %). Model it as a **plateau with no rebound**. If a spring + damper is mandatory, use k_eq ≈ 0.58 MN/m with ζ ≈ 1.0 (Torso proxy). A linear spring under-absorbs by 2×, so prefer the plateau.
- At 25° the 15.1 kN floor needs 67 mm → 94 mm core. Keep the Controls gate at ≤ 15° (Torso O-T11).


## R-080: backing for the chest pad (with Torso geometry, sim_torso_body_r1 / R1_ARCHITECTURE)
**Geometry:**
- The 7075 shoulder bulkhead is a 12 mm transverse web with a 120 mm tall section. Its envelope is x ±0.05, y ±0.15, z 0.16–0.28 (sim box 0.10 × 0.30 × 0.12 at z 0.22), with shoulder bosses at y ±0.165 and 8 × M8.
- It is the only machined metal structure behind the sternum. The pack is lower, in the chest bay.

**Proposal:**
- **Seat the pad on a machined 101 × 101 land on the bulkhead front face, centred about z +0.21.**
- The pad sits inside the shell, behind a breakaway chest panel, as Torso suggested.
- The pad stack is 78 mm core + 1 mm face + 2 mm shell. That needs **≥ 81 mm from the bulkhead front (x +0.05) to the outer chest skin, i.e. skin at x ≥ +0.131**. Torso and ID to confirm the chest depth. If it falls short, the pad protrudes by the difference.

**Checks [hand calc, 7075-T6 Sy 503 MPa from MATERIALS_DB; FEA required]:**
- **Bearing:** 24.4 kN / 0.0102 m² = **2.4 MPa** on 7075. Trivial, SF > 100. The 1 mm CF face spreads it.
- **Web bending, the governing case:** load is normal to the 12 mm web, conservatively taken as simply supported at the shell side walls (y ±0.15, span 0.30), so M = PL/4 = 1.83 kN·m.
  - Bare web (120 × 12, Z 2.88 cm³): **635 MPa, FAILS** (SF 0.79).
  - **Add an integral 7075 rib on the back face, 60 deep × 6 thick across the 0.30 span (T-section):** I ≈ 4.99 × 10⁵ mm⁴, Z ≈ 8.5 cm³ → **216 MPa, SF 2.33**.
  - Rib mass 0.30 × 0.060 × 0.006 × 2 810 = **+0.030 kg**.
  - Inertial loading is distributed (pack, pelvis and legs react through the shell/waist ring), so the real moment is lower. FEA may trim the rib.
- **Reaction into the shell:** 12.2 kN per side at the bulkhead-to-shell joint. Over a 120 mm × 20 mm bonded land that is ≈ 5 MPa shear [EST], vs DP490 overlap shear ~ 25–30 MPa (3M TDS in repo).
  - **The path from the shell down to the waist ring for 24.4 kN forward must be added to Torso's FEA** (FEA_SPEC_torso_pocketing load cases). **Bulkhead pocketing must not remove the rib zone or the land.**
- **Mass:** pad 0.077–0.078 + rib 0.030 = **≈ 0.108 kg, full credit**. The chest panel over the pad becomes a breakaway panel (no change in mass [EST]).
- Alternative, if the depth is insufficient: a separate 7075 sternum strut from the bulkhead to the waist ring takes the pad lower. It is heavier (≈ 0.06–0.08 kg [EST]) and not recommended.
