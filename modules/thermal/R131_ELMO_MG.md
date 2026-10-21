# R-131: Elmo G-TWI without heatsink, and D86 Mg housings (RL Thermal, 2026-10-21)
Hand calc. 35 °C ambient, 68.0 kg + 20 kg, P-042 × 1.1 (T2_68KG basis).
Sources:
- `actuators/datasheets/elmo_gold_twitter_install_guide.txt` (MAN-G-TWI v2.011): p.10 masses; §4 note "max output current guaranteed for T_heat-sink < 85 °C"; §5 operating ambient 0–50 °C; §11.2.1 loss chart.
- Loss chart, as used in `controls/thermal/winding_model.py`: 2/5/13/22/32/44 W at 5/10/20/30/40/50 A amplitude, worst case. Elmo states measured loss is 20–30 % lower. Control losses are excluded; I add ≈ 1 W [EST].
- The Elmo accessory heatsinks dissipate only 5.5 W (flat) / 7.0 W (fins) in free convection.

## (1) G-TWI bare (22.2 g) on plates or housings
**Per-drive loss** [EST from currents]:

| drive | current at carry / walk (rms) | loss carry / walk (chart −25 % + 1 W control) |
|---|---|---|
| knee (2/leg) | 8.8 / ≈ 5 A (Electronics §17) | 6.0 / 3.0 W |
| hip_pitch (2/leg) | ≈ 9 / 5 A | 6.2 / 3.0 W |
| ankle (2/leg) | ≈ 5 / 3 A | 3.0 / 2.0 W |
| hip roll/yaw | ≈ 3–5 A | 2–3 W |
| shoulder_pitch | 6.7 A at 54 N·m hold | 4.2 W |
| elbow / wrist / waist / neck | ≤ 3 A | ≤ 2 W |

R-096 duty average (≤ 40 % carry) ≈ 0.6 × the carry loss.

**Requirement used:**
- Baseplate ≤ 80 °C (Elmo 85 °C − 5 K).
- Local air ≤ 50 °C (Elmo ambient).
- Pad: 1 mm gap pad ≥ 3 W/mK over the 47 × 41 base ≈ 0.3 K/W (+2 K).
- The plate sheds to vented air at h 8 / 12 / 15.

**Is the no-heatsink credit valid by itself? YES.** The Elmo heatsink only works in free air (≤ 7 W) and does nothing for a conduction-mounted drive inside the robot; the plate or housing is the real sink. The −0.506 kg credit for deleting the accessory heatsinks stands. The mounting is what has to pass:

| joint / mount | baseplate at carry continuous (h 12) | R-096 duty (h 8) | verdict / condition |
|---|---|---|---|
| **knee: 6061 thigh plate as booked** (≈ 48 × 100 × 1.5 mm, G10/PEEK standoffs, no metal path; 2 drives = 12 W) | ≈ 35 + 12 × 11.6 ≈ **174 °C** | ≈ 120 °C | **FAIL.** Need ≥ 0.035 m² effective (duty) / 0.05 m² (continuous) at h 8 in the A36 inlet stream: e.g. the 48 × 100 base + 8 axial fins × 15 mm × 1 mm 6061 ≈ 0.03 m² ⇒ ≈ 75 °C at duty. **≈ +35–40 g/leg** over the booked plate. The plate carries **no motor heat** (standoffs, R-066), so the bond is unaffected. Keep the standoffs; do not tie the plate to the femur (it would add ≈ 12 W to the bond path). |
| **hip_pitch: drives on the housing** (R-131 "heat sunk into housing") | = housing case ≈ 85–98 °C (+≈ 7 K from its own loss) | ≈ 85 °C | **FAIL** (> 80/85 °C). The drive loss on the housing also adds ≈ +7 K (duty) to +14 K (continuous) to the hip winding. Condition: put the drives on their own small 6061 plate (≈ 0.0125 m², 80 × 80 × 1.5 mm, ≈ 26 g/drive; duty ≈ 16 g) on G10 standoffs in the skirt-vent stream, not on the housing. |
| ankle: on the housing | ≈ case 86–90 °C | ≈ 80 °C | **FAIL marginal.** Same fix as hip, ≈ 12 g/drive (3 W). |
| hip roll/yaw: on the housing | case ≈ 50–60 °C | — | **PASS** (housing as sink, ≥ 20 K) |
| shoulder_pitch: on the housing | case ≈ 85 °C at P-042 hold | ≈ 75 °C | **marginal.** PASS at duty; continuous hold needs a standoff plate (≈ 15 g) or the drive-temperature derate |
| elbow, waist, neck: on the housing | ≤ 65 °C | — | PASS |
| wrist pair: shoulder bay (Electronics) | bay air 41 / 50–55 °C | — | PASS walking. **Still air exceeds the 50 °C Elmo ambient by up to 5 K**: needs the derate below or a bay vent |

**Required for all drives (firmware, T-029 style):**
- Read the G-TWI internal temperature.
- Derate the joint current limit from 75 °C baseplate, linear to 50 % at 85 °C; disable at 90 °C.
- This ties into the R-096 carry duty (shared thermal state).

**Mass consequence (to net against −0.506):**
- knee fins +0.07–0.08;
- hip_pitch plates 4 × 16–26 g = +0.06–0.10;
- ankle 4 × 12 g = +0.05;
- shoulder 2 × 15 g = +0.03;
- **≈ +0.21–0.26 kg ⇒ net credit ≈ −0.25 to −0.30 kg.**
- Alternatively, the knee could keep the bare plate under a hard current derate, which costs carry capability (not recommended).

## (2) D86 Elektron 43 Mg housings
**Properties:**
- k: 57.6 W/mK (Elektron 43 extruded T5, Luxfer DS-490) / 51 (WE43B cast, DS-467), vs 7075 ≈ 130 (the current housings are 7075, not 6061).
- CTE: 25.6 vs 23.6 (7075).

**Scope (D86):** hip yaw/roll and the hip_pitch/ankle bodies. The knee twin housing is excluded, and so is the shoulder.

**Effects:**
- **Housing spreading:** the housing acts as a fin from the stator band to its ends, t ≈ 3.75 mm (×1.25 thickened), L ≈ 50 mm, h 8–15.
  - 7075: mL 0.24–0.28, η 0.97–0.98. Mg: mL 0.36–0.42, η 0.94–0.96. ⇒ −2 to −3 % effective area.
  - Through-wall conduction is negligible (< 0.02 K/W).
- **Rev B knee fins in Mg** (hypothetical): η drops from 0.979 to 0.92 for 25 mm × 1 mm fins (−6 %). That costs ≈ +2–3 K on the knee and eats most of the 4.7 K h 8 duty margin. **Keep the knee housing and fins in Al** (agrees with D86).
- **Stator fit:** steel laminations in Mg lose (25.6 − 11.7)·10⁻⁶ × 60 mm × 80 K ≈ 67 µm diametral interference hot, vs 61 µm in 7075 (+6 µm).
  - If the stator–housing contact opens, the winding–case resistance rises by several K.
  - **Condition: size the interference at hot, or bond the stator with a thermally conductive epoxy (≥ 1 W/mK).**
- **Emissivity:**
  - bare Mg ε ≈ 0.1 (bad);
  - PEO + sealant (required by Materials for corrosion) ε ≈ 0.8–0.9, equal to black/hard anodised 7075 (0.85).
  - Condition: PEO on all external housing faces, and no bare machined faces in fin channels.
- **Galvanic/other:**
  - Steel or Al fasteners isolated per Materials.
  - Drive plates and gap pads on Mg go through the PEO.
  - G10 standoffs are neutral.
  - Elektron 43 is stable to 250 °C, so no creep issue at ≤ 120 °C (AZ91D rightly rejected).

| joint | Mg? | ΔT winding (h 8 / h 15) | T2_68KG basis → new | vs 120 °C |
|---|---|---|---|---|
| knee | no (Al kept) | 0 | 115.3 at h 8 duty | PASS, 4.7 K |
| hip_pitch | yes | +1.5 / +2.5 K | ≈ 108 → **≈ 110** at A35 vents h ≥ 15 (continuous); ≈ 112 at duty h 12 | **PASS with the vents.** Plus the item (1) drive-off-housing condition, else +7–14 K ⇒ FAIL |
| ankle | yes | +1 / +2 K | 98 → 100 at duty h 12; 121 → 123 at h 8 continuous | PASS at duty (h 8 continuous was already 1 K over) |
| shoulder | not in D86 | 0 (would be +1–2 K if extended) | ≈ 110 at duty | PASS |
| hip roll/yaw | yes | +1 K | ≈ 58–66 | PASS |

**Bond:** hip case +2 K ⇒ bond +≈ 0.3 K (through the 18 K/W break): worst 67.9 °C ≤ 70. PASS.
**R-120 pad:** shoulder roll not in Mg, so unchanged at 56 °C. PASS.

**Thermal ΔT re-check for the R-131 gate: PASSED**, on these conditions:
- stator fit sized hot or bonded;
- PEO on all external faces;
- knee housing and fins stay Al;
- hip_pitch drives off the housing (item 1).
