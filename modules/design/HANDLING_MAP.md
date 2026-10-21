# Handling map — DRAFT
**Co-published with Controls** (Robot Lab rulings C1–C5 applied by ID 2026-10-21) (RL Industrial Design + RL Controls). The rescue procedure is authored by RL Controls (e6dd4b0); ID reviewed it and applied the 7 T&R bec3b82 edits on 2026-10-21.
T&R 5842853 / fef9348 ask 2. ID, 2026-10-21. Image: HANDLING_MAP.png.

## HOLD (lift/carry) zones
- H1 Torso sides under the armpits (torso cover lateral faces, **z ≈ 1330–1440**): primary two-person lift. (Was z 1420–1560, which ran above Controls' sim torso top at ≈ 1.45 m; now kept ≥ 10 mm below it and clear of the N5 shoulder roll gap. ID CAD check of the cover top edge owed.)
- H2 Pelvis skirt top rim, rear (pelvis-fixed part above the rev 8 spherical hem): secondary grip, use with H1. **Never the thigh panels** (they move with the legs).
- H3 Upper arm, mid-humerus: steadying only, no lifting.
- H4 Thigh front, upper half (above the knee-venting zone): steadying only.

## NO-HOLD zones
- N1 **Knee rear outlet shroud, P-156 rev 6 / Option B (HOT)**: shroud rev 6b on the rear/inboard thigh top over the L60 notch (x −100…−20, y 86–150, z 840–904) plus a 30 mm margin, under the P-023 hip skirt. Class (T&R 7f12ce9 §5): **48 °C, no-sustained-contact (contact not likely: inboard/aft, outside the hand-hang and arm-swing envelope)**, target 43; exposure is a person behind the robot and the prone rescue state.
- N1a **Jet-washed skin above z 845** (rear thigh top and the P-023 skirt rear-inboard panel, y 89–171, z 845–≈ 940 [EST plume, Thermal a32d341]): no-hold, same 48 °C class; skirt inner face foil + ≥ 15 mm gap. H2 grips stay ≥ 50 mm clear of this band.
- N7 **Hip break gap (P-023 rev 8):** the ≥ 25 mm open arc between the pelvis hem and the thigh panels. No hold, no hands in the gap while the legs can move (backdriving joints, no brakes).
- N2 Knee rear inlet grille, z 643–675.
- N3 Head and neck (fragile shell and sensors).
- N4 Hands and wrists (pinch points, fragile).
- N5 Shoulder pads and roll gap (pinch through the roll range of motion).
- N6 Chest pad CF face and bezel/fairing (Torso 1585e80, 116 mm core): face at **x +0.175** torso/global, y ±49, global z 1451–1549 (land z 1449.5–1550.5), standing 65 mm proud of the torso cover. Crush indicator: don't grip, lever on, or lift by the bulge or its tapered fairing; the PA66 posts behind it are designed to collapse.

## Hot-surface label (N1)
- ISO 7010 **W017** "Warning; hot surface", yellow triangle with black border.
- Size: 25 mm triangle side (ISO 3864-1 min for ~1 m viewing distance), printed vinyl rated to ≥85 °C. **2 per leg** (hem + shroud cap).
- Placement (rev 6): on the P-023 skirt rear outer face, centred over the outlet but **below the plume band** at the skirt hem (thigh frame x ≈ −90, y ≈ 130, z ≈ 815, on the skirt hem panel, not on the shroud or in the jet), facing aft, upright when standing; visible to a person behind the robot and from above in the prone state. Was x −55, z 830 outboard (rev 5, in the jet).
- **Second label (prone coverage):** prone puts the rear outlet facing up, and the hem label then sits low on the side, where rescuers leaning over may not see it. So a second W017 goes on the **shroud cap's solid top/rear skin** (no slots on the top; rev 6b openings are on the aft wall only), centred at x ≈ −60, y ≈ 118, z ≈ 883 on the sloped solid top (rev 6b). It faces up and aft when prone, and its surface runs 40–42 °C [EST, Thermal B2], which is within the vinyl rating. It is never placed on the slots. N1 (x −100…−20, y 86–150, z 840–904 + 30 mm) covers the outlet in both standing and prone.
- Optional text: "HOT – do not hold".

Status: draft, co-published with Controls (operator manual and handling SOP).

## Prone rescue procedure (RL Controls; T&R bec3b82 edits applied, co-published with Controls)
Controls facts behind this procedure:
- **No brakes.** All hip pitch, knee and ankle units are twin roller screws that **backdrive** (Actuators D94, 7d22c91).
  Joint friction holds only about 7–9 N·m, against about 64 N·m at the knee in a crouch. With MO=0 every joint is limp:
  any lifted limb or the trunk swings or drops freely.
- **Safe-stop states** (`modules/controls/limits/drive_thermal_derate.py`, DRIVE_DERATE.md):
  - **R-146(a) interim (in force, not valid for G4):** latch at 82 °C → derated crouch (**HOLD_DERATED, motors ON**) → on
    drive trip → **TUCK**, logged as a fall. The robot may be in a crouch with motors energised, or fallen after the tuck.
  - **R-146(b) G4 target (in development):** kneel → controlled lower to **prone on the chest pad** → **MO_OFF**. MO=0
    happens only after contact, supported CoM, CoM speed < 0.1 m/s and all joint torques below friction, held for 50 ms.
- **Prone pose (sim, [EST]):** chest pad about 46–64 % of the weight, knee pads about 27 %, feet about 5 %, hands/arms about
  4–8 % (PRONE_DATA_TR.md). Standing CoG is at z ≈ 0.91 m; upright-kneel CoG is about 0.67 m [EST].

**Procedure** (at least three trained people, or two plus a board/strap lift aid; do not approach a robot in HOLD_DERATED or TUCK until step 1 is done):
*Order of steps 1–1b set by ID per Robot Lab rulings C1/C2 (Controls 6d4c8fb); **T&R to confirm**.*
1. **Remote E-stop first, from a distance, area clear.** Press the remote E-stop and **hold it** (or keep it latched). Under the
   R-146(a) interim, a crouched robot in HOLD_DERATED keeps its motors ON and never commands MO_OFF on its own, and it
   **will collapse when power is removed**, so nobody may be near or under it. Then **wait until MO=0 on every drive plus 5 s with no motion**.
   *(T&R edit 7, Robot Lab C1)*
1a. **Approach** only after step 1, with the E-stop still held. Then open the main contactor or battery disconnect and apply lockout/tag-out.
1b. **Battery check (Robot Lab C2, T&R edit 1),** from the closest safe position with the E-stop held. Look for smoke, hissing, a sweet or
   solvent odour, swelling, or rising pack/BMS cell temperature (use a thermal camera if available). **If any are present: evacuate, keep
   clear, and do not roll or lift** (thermal-runaway risk). If none: continue.
2. **Wait for touch temperatures.** The P-156 rev 6 / B2 **rear outlet shroud and jet-washed skin (N1/N1a)**: prone puts them
   **facing up, right where rescuers lean over**. **The R-146(a) 82 °C interim latch governs until G4 closes** (Robot Lab C5; R-142's 83 °C applies only to the G4 path). Drives can be at 82 °C, so the **knee housing and drive band are hot too**, not only N1.
   Wait for the TP-G5-15 measured cool-down to ≤ 43 °C. Until that is published, treat N1/N1a/N2 and the knee/drive band as hot,
   and use **EN 407 contact-heat level ≥ 1 (100 °C) gloves** for any urgent move. *(T&R edit 2)*
3. **Remove the payload** if one is attached.
4. **3-person lift crew: strap the legs, then roll prone → supine** (only if the robot must be moved). **Strap both legs first** (knee strap holding them straight; the backdriving screws let them re-flex otherwise; don't put hands in the thigh–shank gap to straighten them, Robot Lab C3). One person at the shoulders (H1 torso sides),
   one at the pelvis rim (H2), the third controls the strapped legs. Roll toward the side the arms are on, as a log roll, keeping trunk and pelvis aligned. Expect
   the limbs to flop: keep hands and feet clear of the knee, hip and shoulder pinch zones (N5) and **off the thigh–shank gap** (the knee and hip backdrive freely in the roll: pinch). *(T&R edit 4, legs strapped per step 4 heading)* Keep clear and **never hold the knee
   outlet zone (N1/N1a)** or the head (N3). Do not lever on the chest pad (N6).
5. **Lift** (supine or prone): 68.4 kg is ≈ 34 kg per person for two carriers, above the NIOSH 23 kg reference, so **at least three people
   or a board/strap lift aid is mandatory**. *(T&R edit 3)* Use H1 + H2 only, with the CoG (pelvis/lower torso) between the carriers. The
   legs hang limp: the third person supports the shanks below the knee zone (H4 thigh front is steadying only), or use a strap or board. Never lift by a limb: no brake holds it.
6. **Re-enable checks** before power-up:
   - all drive temperatures < 78 °C (R-141 resume), no MF 0xD000 / EMCY 0x4310 latched;
   - **chest cartridge** (*T&R edit 5*): the pad is underneath when prone, so inspect it after the supine roll or on a board lift.
     **Replace** it after any L2/L3/TUCK event regardless of appearance, or if crush indentation is > 2 mm, there is a face mark > 0.5 mm, or the
     tap test fails. The replacement must be a lot-certified cartridge in the 19.5–22.3 kN band, **116 mm core** (Robot Lab C4; Torso 1585e80), bezel 4 × M4 captive at spec torque.
     Inspect the land, backing and bulkhead, with dye-penetrant after any L3/T-031-level event. Record the cartridge lot and the event in the fall log.
     Knee pads and covers intact;
   - after any L2/L3 event (*T&R edit 6*): pack OCV and group voltages, isolation and BMS log unchanged (TP-G5-17 criteria); chest cartridge
     replaced; an R-146 fall-budget entry made;
   - robot placed in a supported pose (prone or seated on a stand), area clear.
   Power up, run `re_enable()` (explicit operator action; the controller never auto-resumes).
7. **Stand-up checks:** joint-limit and encoder sanity check in the supported pose, then a stand-up only from a supported
   pose with the gantry or tether attached for the first stand after a thermal event. Log the event (R-146: fall-budget
   entry if it came via TUCK).

**Controls review of the T&R bec3b82 edits as applied by ID (ecb938d): accepted, no wording changed above. Conflicts and
open points vs controls facts, for T&R/ID:**
- **C1 (edit 7 vs R-146(a) interim):** in HOLD_DERATED the motors stay ON and the controller never commands MO_OFF; it waits
  for a drive trip, then TUCKs (the other drives stay energised). So "wait for MO_OFF + 5 s" never starts on its own under
  the interim: the remote E-stop with the area clear comes first, then MO=0 on every drive + 5 s with no motion. Under
  R-146(b) the MO_OFF interlock (contact, supported CoM, CoM speed < 0.1 m/s, all torques below friction, 50 ms) is the
  trigger, as T&R wrote.
- **C2 (edit 1 order):** T&R requires the battery check **before approaching**. Step 1a currently follows step 1, whose
  E-stop/contactor/LOTO actions may need an approach. Recommend running 1a from a distance first (remote E-stop is fine).
- **C3 (edit 4, D94):** with no brakes and backdriving screws (friction 7–9 N·m), straightened legs re-flex in the roll
  unless strapped; the knee strap is what holds them, and straightening by hand is itself a hand-in-pinch action. Step 4's
  heading still says "Two-person roll"; the roll is two-person, the lift (step 5) is three.
- **C4 (edit 5 vs N6):** T&R/Robot Lab say "100 mm core"; N6 above (P-052 rev 2, Torso 1585e80) says 116 mm core. ID/Torso
  to confirm the cartridge spec for step 6.
- **C5 (edit 2):** 82 °C is the R-146(a) interim latch (R-142's 83 °C belongs to the G4 path); the hot-band warning holds either way.
- No conflict for edits 3 and 6.
