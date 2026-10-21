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

## Rev 2: Actuators D90 (af482e1) heat plates re-check (2026-10-21 08:40 EDT)
Script: `modules/thermal/r131_rev2_knee_gap.py`.
Basis:
- Losses and pad as in R131 above: knee 6.0 W/drive at carry, duty = 0.6 × carry.
- "h" means total (convection + radiation) on an open, black-anodised face (ε 0.85).

### (a) Knee plate: 6 × 15 × 1 drive-side fins, 4.0 mm femur gap
**FAIL.** The 6 fins do not give the required area.

- **Fin channels are dead.** In `drive_heat_plates.py`, 3 fins fit in each 6.5 mm strip beside the drives (x 16 → 22.5 mm), at a 2.17 mm pitch, leaving a **1.17 mm gap** between 15 mm fins.
  - Natural convection (Elenbaas): Ra_s ≈ 0.05, so h ≈ 0.05 W/m²K, i.e. nothing.
  - Forced flow: the inlet area of about 1e-4 m² gives ṁcp ≈ 0.02 W/K at 0.2 m/s, so the channel air would need to rise about 300 K to carry 7 W (starved).
  - Only the strip envelope works: the outer fin faces, the tips, the exposed base strip, and about 50 % of the drives' own surfaces. That is **≈ 0.0065 m² drive-side effective, against the 0.0261 m² × η 0.993 used** (Actuators' η uses an isolated-fin m and ignores the channel).
- **Femur side.**
  - The plate is flat and the femur is Ø50, so the gap runs from 4 mm at the tangent to 22 mm at the plate edges. The mean gas-gap conductance (conduction floor Nu = 1, Elenbaas above that) is 7.7 / 6.0 / 5.8 / 5.5 W/m²K at a 2 / 3.5 / 4 / 6 mm minimum gap.
  - Radiation to the femur adds ≈ 6 W/m²K (ε 0.85 both sides).
  - All of this is **referenced to the warm femur (40–50 °C [EST])**, not to 35 °C air.
  - So the femur face is worth about the same at 3.5 and 4.0 mm. The 30 %-below-4 mm switch in the model is a cliff-edge artefact: the real behaviour is smooth, and the full-credit-at-8 case is optimistic. **Minimum gap: 3 mm (M2 heads plus tolerance).** The temperature is insensitive to the gap from 3 to 6 mm; a larger gap only reduces heat into the femur.
- **Heat into the femur.** About 3 W at duty goes into the femur by gas conduction plus radiation: an air path is still a path to the femur. Effect on the EA 9396 bond ≈ +2–4 K [EST], so the 67.9 °C worst case becomes ≈ 70–72 °C, **at or over the 70 °C limit.**

| knee drive base | Actuators D90 | Thermal rev 2 (femur 40–50 °C) |
|---|---|---|
| duty, h 8 | 70.7 (75.9 at 3.5 mm) | **107–112 °C** |
| duty, h 12 | — | **93–97 °C** |
| continuous carry, h 8 | 94.6 | **151–158 °C** |
| continuous carry, h 12 | 75.3 | **129–134 °C** |

Required: a total UA ≥ 0.185 W/K at h 8 for ≤ 75 °C at duty. Rev 2 gives ≈ 0.105 W/K (0.052 drive side + 0.053 femur side). The 0.03 m² requirement is **not met: ≈ 0.013 m² equivalent.**

Options (Actuators/Legs to pick):
1. Fins at a pitch of 6 mm or more, in the open thigh-fairing stream outside the 26 mm L51 box: about 2 × 20 mm × 100 mm × 4 fins, or full-width fins on a plate rotated so they run along the flow.
2. Bond the plate to the thigh shell inner face with a pad, so the shell is the sink. This needs Legs to give the shell area and its h.
3. Split the 2 drives over 2 plates (nearly doubles the envelope).
4. Accept a knee carry limit set by the drive-temperature derate (75 °C start). This roughly halves the allowed carry duty [EST]. Not recommended.

In every option, make the femur-facing face low-ε (bare/clear) or add a shield foil, to cut heat into the femur near the bond.

### (b) Hip pitch plate, 84 × 84 × 1.5 mm, 8.5 mm standoff
Actuators credits both faces at h 8 to 35 °C air. In reality the back face sees the mounting structure across an 8.5 mm gap: Ra ≈ 110, h_conv ≈ 5.6, plus radiation ≈ 6, referenced to the structure temperature.

| hip_pitch drive base | duty, h 8 | continuous, h 8 | continuous, h 12 |
|---|---|---|---|
| back structure ≤ 45 °C | **68.8 °C** | 87 °C | 79 °C |
| back structure 60 °C | **77.8 °C** | — | — |

- **≤ 72 °C holds only if the back face sees ≤ 50 °C structure**, never the hip_pitch housing (case 85–98 °C).
- Condition: the back face either faces the thigh/pelvis shell, or carries a low-ε shield toward any housing.
- Continuous carry exceeds the 80 °C base limit at h 8 (87 °C), so the drive derate is required (same as R131).
- Ankle (60 × 56) and shoulder_pitch plates have the same back-face caveat.

### (c) R-140: is h 8 defensible?
**Flat plate in the stream** (laminar, L 0.1 m): h_conv ≈ 6.6 / 8.5 / 12 W/m²K at 0.3 / 0.5 / 1.0 m/s. Radiation to ~40 °C surroundings adds ≈ 6.

| case | h (W/m²K) | is h 8 conservative? |
|---|---|---|
| walking, A35/A36 stream (v ≥ 0.3 m/s) | 12–18 | yes |
| standing still, open face (natural convection 6 + radiation 6) | 10–12 | yes, if the face has ≥ 10 mm of clear air and black anodise |
| standing still, enclosed (L51 26 mm box, narrow gaps, warm walls) | 3–6 | **no** |
| bare/clear plate (ε ≈ 0.1) | about −5 against the above | **no** |
| sub-5 mm fin gaps | ≈ 0 between the fins | **no** |

**Verdict:** h 8 is defensible and conservative for exposed, black-anodised plate faces, walking or standing, with surroundings ≤ 40 °C. It is **not** defensible for fin channels under 5 mm, for faces inside closed boxes, or for faces looking at warm structure; those need the explicit treatment above. The h 8 vent-stream value also still depends on the Controls duty sim (open R-140 item).

## Rev 3: Actuators D91 (194f615) knee drive plate as a thigh-shell window (2026-10-21 08:46 EDT)
Script: `modules/thermal/r131_rev3_knee_window.py`. Basis as in rev 2: 2 × 6.0 W at carry, duty 0.6, pad 0.3 K/W, air 35 °C, femur 45 °C [EST].

**Fins** (8 × 13 × 1 mm, 6061):
- Efficiency η = 0.994. PASS.
- With 5 mm gaps the channels work. That is not true of the 1.17 mm gaps in rev 2.

**Outer UA, which depends on flow:**

| condition | outer UA (W/K) | basis |
|---|---|---|
| Actuators claim | 0.203 | h 8 |
| walking, 0.2 m/s in the channels | 0.143 | developing laminar Nu ≈ 20 W/m²K; the air in the channels heats up as it passes (heat-capacity limit) |
| walking, 0.4 m/s in the channels | 0.231 | same |
| standing still | 0.124 | Elenbaas, s 5 mm: h 3.4 + radiation from the envelope |

- **Walking:** h 8 is reasonable if the leg swing gives ≥ 0.3 m/s along the fins.
- **Standing still:** h 8 is **optimistic**; the equivalent is ≈ h 5.
- **Fin orientation:** axial fins are vertical when standing, which is good. Keep them axial, never circumferential.

**Other heat paths:**
- **Femur gap, 7 mm, bare 6061 (ε 0.1) / Al foil (ε 0.05):** radiation is negligible (≈ 0.3 W/m²K). Gas conduction plus convection gives G ≈ 0.027 W/K, so **0.3–0.9 W into the femur at duty** (claim 0.3; it is 0.3 only at h 12). PASS.
- **Shell-window joint:** the PC shell acts as a poor fin, G ≈ 0.016 W/K, so ≈ 0.4–0.7 W goes into the shell.
  - The shell edge reaches the plate temperature and falls to air within ≈ 5 mm (1/m).
  - PC at ≤ 78 °C at duty and ≤ 105 °C at continuous standing is under its ~115 °C continuous rating. PASS.
  - Use a gasket and keep the screws away from thin ribs.

**Drive base (°C):**

| outer UA | duty | continuous |
|---|---|---|
| h 8 claim | 65.0 | 84.3 |
| walking, low (0.143) | 73.7 | 98.6 |
| walking, high (0.231) | 62.2 | 79.7 |
| standing (0.124) | **77.7** | 105.2 |
| h 12 | 56.9 | 70.9 |

- **At duty: PASS** (≤ 80 °C). Standing in carry goes past the 75 °C derate start, so the derate (R131) takes effect.
- **Continuous carry: FAIL** at h 8 and standing; the derate is still required (unchanged from R131). At h 12 it is 70.9 °C, a PASS.

**Femur bond:** T2_68KG plus Mg is 67.9 °C, plus this leak at 0.67–1.33 K/W [EST from rev 2] gives **68.2–69.1 °C ≤ 70. PASS**, with 0.9–1.8 K margin. Keep the foil and the bare inner face; do not anodise the inner face.

**Outer surface:**
- **Touch: FAIL as drawn.**
  - Fins run ≈ 1 K under the drive base: 56–78 °C at duty, up to 104 °C continuous standing.
  - Bare/anodised metal burn thresholds (ISO 13732-1) are ≈ 65–70 °C for 1 s and ≈ 55–60 °C for 10 s. The thigh is a handling and grab zone.
  - Fix with either:
    1. a ventilated PC/nylon guard over the fins, ≥ 50 % open with ≥ 5 mm standoff (h drops ≈ 10–20 % [EST]; re-check), or
    2. a firmware touch cap: base ≤ 60 °C whenever the robot is in human-contact modes.
  - Mark the area hot regardless.
- **Snag/sharp edges:** 13 mm × 1 mm fins on an outer surface catch clothing and cables and can cut. The guard fixes this too; at minimum use tip radii ≥ 0.5 mm and chamfered fin ends.
- **ID/styling:** Legs/ID must accept a 13 mm protrusion and a 100 × 48 window (open item). An ingress (IP) rating applies to the window seal.

**Verdict:**
- Thermal: **PASS at duty**, conditional on ≥ 0.3 m/s walking flow, the derate for standing and continuous carry, and keeping the foil and bare inner face.
- Femur bond and shell: PASS.
- **Outer surface: FAIL (touch and snag) until a guard or touch cap and ID acceptance.**

## Rev 4: R-143 knee fin touch guard (T&R 447aa8e) — 2026-10-21 08:51 EDT
Script: `modules/thermal/r131_rev4_guard.py`.
- **Basis:** rev 3 model; 2 × 6.0 W carry, duty 0.6; 35 °C.
- **Guard:** per T&R spec. PC 1.5 mm, ≥ 10 mm air above the fin tips, ≥ 60 % open slotted face, open at both ends.
- **Guard geometry:** no Actuators guard CAD exists yet, so I used the T&R geometry.
- **Effect of the guard:** −15 % channel flow walking, −5 % standing. The guard intercepts 40 % of the fin radiation; how much of that is lost depends on the guard's inner-face ε.

| knee plate (per knee) | UA h 8 basis | UA walk 0.2 / 0.4 m/s | UA standing | drive base at duty: h 8 / walk / standing (°C) | plate + guard mass (g) |
|---|---|---|---|---|---|
| rev 3 bare | 0.210 | 0.143 / 0.231 | 0.124 | 64.3 / 62–74 / 77.8 | 47.5 + 0 |
| rev 3 + guard | **0.189** (T&R 0.183–0.193 confirmed) | 0.118 / 0.197 | 0.110 | 66.7 / 66–79 / **81.4 FAIL** | 47.5 + 18 |
| **fins 13 → 18 mm** + guard | **0.246** | 0.152 / 0.260 | 0.135 | 60.9 / 60–72 / **75.5** | 58.3 + 20.3 |
| fins 20 mm + guard | 0.269 | 0.166 / 0.285 | 0.144 | 59.1 / 58–70 / 73.5 | 63.5 + 20.3 |
| window L 130 mm + guard | 0.246 | 0.127 / 0.212 | 0.122 | 60.9 / 64–77 / 78.2 | 84.7 total |
| W 60 mm, 10 fins + guard | 0.236 | 0.151 / 0.252 | 0.137 | 61.7 / 60–72 / 74.9 | 77.4 total (needs Legs width) |

Notes on the table:
- **Minimum to reach UA ≥ 0.21 on the h 8 basis:** fins 15 mm (≈ +4 g).
- **Physical walking/standing UA** never reaches 0.21 without large growth. The controlling case is standing still under carry: drive base ≤ 80 °C needs fins ≥ 16 mm, and ≤ 75.5 needs 18 mm.
- **Window length:** a longer window helps little. Channel air heating limits walking UA, and natural-convection h falls as L^-0.25.

**Guard face temperature** (fins ≈ base −1 K; guard heated by fin radiation plus warm channel air; outer face h 10 walking / 4 standing, + 6 radiation):

| guard inner face | walk duty | stand duty | stand carry at derate (base 85) | vs 45 °C (48 − 3) |
|---|---|---|---|---|
| black PC, ε 0.9 | 44.1 | **53.0** | **54.8** | **FAIL** standing |
| **PC with low-ε inner face, ε ≤ 0.1** (vacuum-metallised or Al-foil lined; the outer face stays cover colour, ε 0.9) | 37.6 | 40.0 | 40.3 | **PASS, 5–7 K margin** |

- **Standoff:** keep 10 mm. More standoff lowers the guard temperature only slightly once the inner face is low-ε, and it adds protrusion.
- **Guard material:** polymer (PC) is preferred to metal. Its contact threshold is higher and its outer face cannot spread fin heat.

**Recommendation (minimum that passes everything):**
- Fins 18 mm, still 8 at 6 mm pitch.
- PC guard, low-ε inner face, 10 mm standoff, ≥ 60 % open.
- UA: 0.246 on the h 8 basis (+17 % over 0.21); physical 0.15–0.26 walking, 0.135 standing.
- Drive base at duty ≤ 75.5 °C in all cases.
- Guard face ≤ 40.3 °C, including derate-limited carry.

**Mass:**
- per knee +10.8 g fins and +2.3 g guard growth, on top of T&R's 18 g guard;
- robot +0.026 kg over T&R's booked +0.04, so **+0.066 kg** vs rev 3.

**Envelope:** fin tips + 10 mm + 1.5 mm = **29.5 mm beyond the L51 box** (T&R 24.5). The R-143 §2a/§2c sweeps must use this.

**Firmware:**
- With the low-ε guard, no touch cap is needed. The drive derate (75 → 85 → 90 °C) stays.
- **Fallback if the guard inner face is black (ε 0.9):** a touch cap with drive base ≤ 58 °C whenever the robot is standing still or in contact modes. That gives a guard face ≤ 45 °C, and it roughly halves the standing carry duty [EST].
- Femur bond: unchanged, 68.2–69.1 °C.

## Rev 4b: D93 knee plate (5008683), placed in the L71 thigh pocket (6060973) — 2026-10-21 08:58 EDT
Basis: `r131_rev4_guard.py`.
Geometry:
- Guard: ID P-154 as specified. 1.5 mm PC, 104 × 52, inner face ε ≤ 0.1, 4 mm slots at 5.5 mm pitch, 64 % open, 10 mm face standoff (+0.5), side walls 4.5 mm from the outer fins (L71 1b).
- Fins sit 48.6–52.7 mm inside the v5 hull, with 13–18 mm of air aft to the knee twin housing (case ≈ 90–100 °C).

### As drawn by Actuators (open-flow basis)

**Taper (45° × 8 on the z 690 ends):** −512 mm² (−1.5 %). The +0.5 mm on the fins gives back +2.8 %, so UA on the h 8 basis is 0.249 (**Actuators 0.248, confirmed**).
- The taper is at the inlet end for standing chimney flow, where the local h is highest. It slightly eases channel entry, so I take the effect on flow as neutral and the area-scaling basis stands.
- The guard side walls at 4.5 mm (not 10) restrict the two outer channels: −2–3 % [EST]. Standing UA ≈ 0.133, so **drive base at duty standing ≈ 75.8 °C** (Actuators 75.2) and walking 59–72 °C.
- Guard face: 37.6–40.3 °C. PASS.

**PEM FHS-M3 studs:** the result depends on what they land in.
- Into the PA12 frame or G10 standoffs: leak ≤ 0.01 W/K, negligible. PASS.
- **Into the metal band clamps on the femur:** about 20–25 K/W for 4 steel studs, so ≈ 1.4 W into the femur. The bond goes from 68.2–69.1 to **69.1–71.0 °C, FAIL marginal.**
- **Condition:** the studs must land in G10 standoffs or washers (≥ 10 K/W each), with no stud–metal contact to the clamps.

**Femur bond** with G10: 68.2–69.1 °C. PASS.

### In the L71 pocket (as actually placed)
**v5 fairing closed over the pocket: FAIL.**
- The pocket walls (PA12 skin, ≈ 0.03 m², U ≈ 2.2 W/m²K) give UA_wall ≈ 0.065 W/K.
- 7.2 W from the plate plus radiation from the knee housing would heat the pocket air by ≈ 100 K or more, so the drive base would be > 130 °C at duty.
- The h 8 basis does not apply to an enclosed recess.

**A36 vent stream:** not shown through the pocket. L71 2c says the guard is in open flow only if the rear PA12 panel is opened around it, so I do not credit it.

**Fix: vent the pocket to suit the fin channels.**
1. **Face opening:** a fairing grille over the full fin field, ≥ 104 × 52 mm, **≥ 60 % open**, slots ≤ 5 mm, inner face low-ε (ε ≤ 0.1) or ≥ 30 mm from the fin tips.
   - It sits 48 − 18.5 ≈ 30 mm from the fin tips. View factor ≈ 0.5, so the grille face is ≈ 39 °C with a low-ε inner face, or 47 °C with a black one (FAIL vs 45).
2. **Low inlet** (below z 690, at the taper end) and **high outlet** (above z 792), both on the aft/outer skin and aligned with the axial channels.
   - Each **≥ 1200 mm² free area** (≈ 7 × 5 × 18.5 mm of channel plus 10 × 52 mm of face gap), i.e. ≈ 2000 mm² gross at 60 % open.
   - The pocket walls must duct them to the fin ends: no bypass around the fin pack, side gaps ≤ 5 mm.
3. **Knee housing:** a low-ε face (foil or bare) toward the pocket, or an Al foil shield on the pocket aft wall. This keeps the 90–100 °C housing from heating the pocket air and fins (≈ 0.2–0.5 W [EST]).

With 1–3 in place:
- Standing chimney UA ≈ 0.12–0.13 (−5–10 % for the 48 mm duct depth and the radiation view lost) gives **drive base at standing duty ≈ 76–79 °C ≤ 80**. PASS.
- UA on the h 8 basis ≈ 0.22–0.235 ≥ 0.21. PASS.
- Walking (pumping through the grille ≈ 0.2–0.4 m/s): 0.15–0.24.

**Guard: redundant once the fins are recessed behind that grille.**
- IEC 61032 probe B cannot pass 5 mm slots and reach fins ≥ 30 mm behind them, and the fall shielding is per L71 3.
- **Drop P-154:** −2 × 20.3 g = **−0.041 kg**, which also removes the guard's −15 % flow / −40 % radiation-intercept loss.
- With no guard, standing UA ≈ 0.135–0.14, so **drive base at standing duty ≈ 74–76 °C**, with 4–6 K margin to 80 °C, and h-8-basis UA ≈ 0.25.
- The fairing grille takes over the touch role and must meet the TP-G5-15 touch points (≤ 48 °C; estimate ≈ 39 °C with a low-ε inner face).
- **Required instead:** the grille plus the inlet/outlet in 1–2.

**Verdict:**
- D93 as drawn: confirmed on the open-flow basis (75.8 vs 75.2 °C), with the condition that the PEM studs land in G10.
- In the L71 pocket with a closed fairing: FAIL.
- With the vents (1–3): PASS, ≈ 76–79 °C standing with the guard, or 74–76 °C without it. **Recommend dropping the guard.**

## Rev 4c: D94 knee plate (7d22c91), 46 mm wide, 8 × 0.75 mm fins at 5.75 pitch — 2026-10-21 09:01 EDT
Basis: rev 4 / 4b model (`r131_rev4_guard.py`). 2 × 6.0 W carry, duty 0.6, 35 °C, no guard.

**Fins:**
- **Efficiency:** m = 11.3 /m, L_c 19 mm, so η = **0.985** (1.0 mm fins: 0.994). −0.9 %.
- **Area:** same fin count and height, so the fin faces are unchanged. The base is 46 instead of 48 mm (−2 %) and the tips are thinner. Net ≈ −0.6 %.
- **Channel:** the 5.0 mm gap is unchanged, so the Elenbaas h and the channel heat-capacity limit are unchanged.
- **Side gaps:** the fin pack is 41 mm wide, leaving 2.5 mm each side on the plate. With no guard, the side gap is set by the pocket duct walls, which must stay ≤ 5 mm to stop bypass flow.
- **Mass:** ≈ −3.6 g per knee vs D93 (fins −2.8, base −0.8) [EST].

| case | UA (W/K) | drive base duty | continuous carry |
|---|---|---|---|
| open flow, h 8 basis | **0.245** (Actuators 0.247, confirmed within 1 %) | 61.0 | 77.7 |
| open flow, standing, no guard | 0.134–0.138 | **74.8–75.6** (Actuators 75.4, confirmed) | 100–102, derate |
| **vented fairing (rev 4b items 1–3), standing** | 0.121–0.131 | **76.2–78.5 ≤ 80: PASS** (1.5–3.8 K margin) | 103–107, derate |
| vented fairing, walking | 0.15–0.24 | 61–73: PASS | 78–99, derate |
| vented fairing, h 8 basis equivalent | ≈ 0.22–0.23 ≥ 0.21 | — | — |

**Femur bond:** G10 standoffs, PEM studs with no metal path (L71), so **68.2–69.1 °C ≤ 70. PASS.** Gas gap and foil are unchanged.

**Grille face:** ≈ 39 °C with a low-ε inner face. PASS (≤ 45).

**Verdict:**
- **D94: PASS**, in open flow and in the vented fairing.
- Conditions:
  - the rev 4b vents are built as specified: grille ≥ 60 % open with ≤ 5 mm slots and a low-ε inner face; low inlet and high outlet each ≥ 1200 mm² free, ducted to the fin ends; pocket side gaps ≤ 5 mm;
  - the knee housing face toward the pocket is low-ε;
  - the drive derate stays for continuous carry.
- The thinner fins and the narrower plate cost < 1.5 % UA.
- Margin standing is thin (1.5–3.8 K). TP-G5-15 should measure the standing drive base in the fairing.

## Rev 4d: pocket air, grille and knee-housing fairing (T&R 241369d) — 2026-10-21 09:03 EDT
Script: `modules/thermal/r131_rev4d_chimney.py`.
Chimney model:
- Buoyancy head: ρ g H 0.8 ΔT / T, with H from inlet to outlet.
- Losses: inlet and outlet orifices (Cd 0.6, or T&R's 0.4) plus the fin channels (laminar 12 μ L V / s², s 5 mm, L 0.1, A 650 mm², plus 1.5 dynamic heads).
- Q = 7.5 W (plate 7.2 W at duty plus the knee housing face).

### (1) Pocket air rise
| case | ṁ (g/s) | outlet ΔT (K) | mean (K) |
|---|---|---|---|
| T&R basis (Cd 0.4, H 0.12, 1200 mm²) | 0.12 | 62 | 31 |
| Cd 0.6 | 0.13 | 58 | 29 |
| 2 × free area | 0.13 | 55 | 28 |
| H 0.20 m | 0.16 | 47 | 23 |
| 2 × area + H 0.20 | 0.17 | 44 | 22 |

- **The fin channels, not the openings, control the flow.** At Ra_s ≈ 16 the flow is fully developed, so the air leaves near fin temperature. Extra free area buys only about 3 K.
- **T&R is right.** Pocket air at +28–31 K mean sets the grille temperature. My 39 °C (rev 4b and 4c) counted only radiation through the ε 0.1 face and treated the 30 mm fin-tip-to-grille gap as ambient. In the ducted pocket that gap is part of the exhaust path.
- Grille check with exhaust air at about 65 °C on the inner face (h 3) plus 0.7 W/m²K of radiation, and outer face h 4 + 6 radiation: ≈ 44 °C. T&R's 45.6 is the upper bound.
- **Grille: FAIL against 45 / 43 °C.**
- Drive base standing, chimney-limited (ṁcp 0.131 W/K × 0.9 + 0.055 W/K other paths): ≈ 77.7 °C at H 0.12. That matches rev 4c and T&R's 78.3 at 25 °C ambient; T&R's 87.5 at 35 °C is a derate-cap assumption.

### (2) Getting the grille to ≤ 43 °C standing
| option | grille face | drive base standing | mass/knee | verdict |
|---|---|---|---|---|
| larger free area (×2) | ≈ 43–45 | −1 K | +0 (fairing cut) | not enough |
| low-ε grille inner face | already in the base case | — | — | already included |
| taller chimney (outlet at H 0.20 m) | ≈ 41–43 | **72.1** | ≈ +5 g duct | marginal on its own |
| **baffle: duct wall between the fin tips and the grille** | **≈ 37–39** | 77.7 (lost radiation ≈ 0) | **≈ +7 g** | **PASS, minimum** |

**Minimum change (the baffle):**
- **Baffle part:** 1 mm PC/PA12 at fin tips + 3 mm, 104 × 52, with Al tape (ε ≤ 0.1) on the fin side.
- **Chimney path:** this closes the fin channels into a chimney, from the low inlet through the fins to the high outlet.
- **Grille-side space:** the ≈ 25 mm between baffle and grille breathes to ambient through the grille only, so the grille sees inlet-temperature air.
- **Outlet location:** route the outlet aft/up, ≥ 30 mm from the grille top edge, so the exhaust does not wash the grille.
- **Mass:** ≈ 7 g/knee, **+0.014 kg robot**.
- **Optional:** raise the outlet to H ≥ 0.20 m for a −5 K drive base margin (+5 g/knee).

### (3) Fairing over the knee twin housing (case 90–100 °C)
Model: PC 1.5 mm, ≈ 8 mm gap, housing ε 0.85, outer face h 4 + 6 radiation to 35 °C ambient.

| fairing configuration | outer face |
|---|---|
| black PC inner face, closed gap | **≈ 58–66 °C, FAIL** (48 / 43) |
| inner-face Al foil (ε 0.05), closed gap | ≈ 51.5 °C, FAIL |
| **inner-face foil + gap ≥ 10 mm, vented top and bottom (A36 stream walking, chimney standing)** | **≈ 40–41.5 °C, PASS** (≤ 43) |

- **Do not put foil on the housing.** Its radiation is part of the knee rev B fin cooling, and the knee margin is only 4.7 K.
- **Fix specification:**
  - 0.05 mm Al foil with PSA on the fairing inner face over the housing area;
  - gap ≥ 10 mm;
  - ≥ 300 mm² slots at the bottom and top, clear of the housing fins' A36 path.
- **Mass:** ≈ 6 g/knee [EST, ≈ 0.03 m²], **+0.012 kg robot**.

**Verdict:**
- (1) T&R's number is right: pocket air dominates, and the grille is ≈ 44–45.6 °C as built.
- (2) PASS with the fin-to-grille baffle and an aft/up outlet: grille ≈ 37–39 °C, **+0.014 kg**.
- (3) The knee-housing fairing FAILS as drawn; it PASSES with inner foil and a vented gap of ≥ 10 mm (≈ 40–41.5 °C), **+0.012 kg**.
- Total: **+0.026 kg**.

## Rev 4e: outlet shroud (T&R 67e6eed) and ID outlet at 0.18 m — 2026-10-21 09:07 EDT
Basis:
- `r131_rev4d_chimney.py`.
- P-156 geometry: inlet z 643–681, outlet z 799–837, 1296 mm² free each.
- Exhaust ≈ 0.13–0.15 g/s at 79–97 °C (35 °C ambient).

### (1) Outlet shroud
- **Exhaust speed:** under a shroud of ≥ 2 × free area, the exhaust moves at only ≈ 0.04 m/s. The shroud inner face therefore sees nearly natural convection, h_i ≈ 2–5 W/m²K.
- **Shroud outer face** = (h_i · T_mix + (4 conv + 6 rad) · 35) / (h_i + 10):

| inner h_i / mixed air under the shroud | outer face |
|---|---|
| 2 / 62 °C (1:1 dilution) | 39.5 |
| 3 / 62 | **41.2** |
| 3 / 70 (poor dilution) | 43.1 |
| 5 / 62 | 44.0 |
| 5 / 70 | 46.7 (T&R 44–48 consistent) |

- **Spec to reach ≤ 43 °C** (best estimate 41–43 °C):
  - **Construction:** 1.5 mm PC with an Al foil inner face (ε ≤ 0.05); this removes the web and duct radiation.
  - **Standoff and opening:** ≥ 15 mm standoff (10 is the minimum). Open aft/up, ≥ 2600 mm² free (2 × outlet).
  - **Dilution slots:** ≥ 600 mm² low and at the sides, ≤ 5 mm wide, so ambient air is drawn in for ≈ 1:1 mixing before the shroud face. That keeps T_mix ≤ 62 °C and lets the plume sweep away from the shroud wall.
  - **Margin:** this is thin, ≈ 0 to 2 K against 43.
- **Mass:** ≈ 5 g/knee, so **+0.010 kg robot** [EST].
- **Touch classification:** the outlet is at the upper rear of the knee, z 799–837 aft, an occasional brush/assist touch zone. I propose that T&R class it **"no sustained contact"**, so it is gated on 10 min / 48 °C, which gives a **5–7 K margin**. Keep 43 °C as the target; TP-G5-15 measures it.
- **Outlet webs, metal vs polymer:** the webs are thin and washed on both sides, so they reach exhaust temperature whatever their k. Low-k PA12 webs change only the perceived short contact: 1 min plastic 60 °C against metal 51. At 54–61 °C they are still a FAIL for ≥ 10 min.
  - **Better:** under the shroud the webs are not touchable (4.5 mm slots, 15 mm hood), so use plain moulded PA12/PC webs. No metal is needed.
- **Outlet with no grille** (recessed 4.5 mm slots ≥ 10 mm inboard, plus the hood): thermally the same case, because the shroud is the only touch surface. It saves the grille part. **Equivalent: ID's choice.**

### (2) Effect of the shroud on fin flow
- The shroud, in series at 2 × area, adds ≈ 25 % to the outlet loss, so the effective area falls ≈ 11 %.
- The fin channels still control the flow: ṁ changes by −0.001 g/s and the drive base by **+0.2 K** (78.0 → 78.2 °C at H 0.12). **Negligible. PASS.**

### (3) ID outlet at 0.18 m
| H (m) | ṁ (g/s) | drive base standing, no shroud / with shroud |
|---|---|---|
| 0.12 (baseline) | 0.129 | 78.0 / 78.2 |
| **0.18 (ID)** | 0.154 | **73.0 / 73.2** |
| 0.20 | 0.162 | 71.8 / 72.0 |

- **0.18 m: PASS**, ≈ 7 K under 80 °C.
- It recovers 4.8 of the 6 K that 0.20 m would give, about 1 K short of the 72 °C figure. Accept.

**Verdict:**
- Shroud (foil inner, ≥ 15 mm, ≥ 2 × area, dilution slots): outer face ≈ **41–43 °C**. PASS against 43, thin margin; 5–7 K margin against 48 if the zone is classed no-sustained-contact.
- Outlet webs: polymer is fine.
- Shroud flow penalty: +0.2 K.
- H 0.18: drive base 73.2 °C standing.
