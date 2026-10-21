# Handling map — DRAFT
**Co-published with Controls** (RL Industrial Design + RL Controls). The rescue procedure is authored by RL Controls (e6dd4b0); ID reviewed it and applied the 7 T&R bec3b82 edits on 2026-10-21.
T&R 5842853 / fef9348 ask 2. ID, 2026-10-21. Image: HANDLING_MAP.png.

## HOLD (lift/carry) zones
- H1 Torso sides under the armpits (torso cover lateral faces, **z ≈ 1330–1440**): primary two-person lift. (Was z 1420–1560, which ran above Controls' sim torso top at ≈ 1.45 m; now kept ≥ 10 mm below it and clear of the N5 shoulder roll gap. ID CAD check of the cover top edge owed.)
- H2 Pelvis/hip skirt top rim, rear: secondary grip, use with H1.
- H3 Upper arm, mid-humerus: steadying only, no lifting.
- H4 Thigh front, upper half (above the knee-venting zone): steadying only.

## NO-HOLD zones
- N1 **Knee rear outlet shroud, P-156 rev 6 / Option B (HOT)**: shroud on the rear/inboard thigh top over the L60 notch (x −76…−20, y 89–171, z 860–882) plus a 30 mm margin, under the P-023 hip skirt. Class (T&R 7f12ce9 §5): **48 °C, no-sustained-contact (contact not likely: inboard/aft, outside the hand-hang and arm-swing envelope)**, target 43; exposure is a person behind the robot and the prone rescue state.
- N1a **Jet-washed skin above z 845** (rear thigh top and the P-023 skirt rear-inboard panel, y 89–171, z 845–≈ 940 [EST plume, Thermal a32d341]): no-hold, same 48 °C class; skirt inner face foil + ≥ 15 mm gap. H2 grips stay ≥ 50 mm clear of this band.
- N2 Knee rear inlet grille, z 643–675.
- N3 Head and neck (fragile shell and sensors).
- N4 Hands and wrists (pinch points, fragile).
- N5 Shoulder pads and roll gap (pinch through the roll range of motion).
- N6 Chest pad CF face (crush indicator: don't grip or lever on it).

## Hot-surface label (N1)
- ISO 7010 **W017** "Warning; hot surface", yellow triangle with black border.
- Size: 25 mm triangle side (ISO 3864-1 min for ~1 m viewing distance), printed vinyl rated to ≥85 °C. **2 per leg** (hem + shroud cap).
- Placement (rev 6): on the P-023 skirt rear outer face, centred over the outlet but **below the plume band** at the skirt hem (thigh frame x ≈ −90, y ≈ 130, z ≈ 815, on the skirt hem panel, not on the shroud or in the jet), facing aft, upright when standing; visible to a person behind the robot and from above in the prone state. Was x −55, z 830 outboard (rev 5, in the jet).
- **Second label (prone coverage):** prone puts the rear outlet facing up, and the hem label then sits low on the side, where rescuers leaning over may not see it. So a second W017 goes on the **shroud cap's solid top/rear skin** (cap 56.5 × 82, no slots on the cap; slots are on the walls only), centred at x ≈ −48, y ≈ 130, z 881.5. It faces up and aft when prone, and its surface runs 40–42 °C [EST, Thermal B2], which is within the vinyl rating. It is never placed on the slots. N1 (x −76…−20, y 89–171, z 860–882 + 30 mm) covers the outlet in both standing and prone.
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
1. **Confirm MO=0 and lock out.** Status shows MO_OFF (or every drive faulted or tripped). Press the E-stop, open the main
   contactor or battery disconnect, and apply lockout/tag-out. A crouched robot in HOLD_DERATED has energised motors and
   **will collapse when power is removed**: do not cut power while anyone is near or under it. Cut it from the remote
   E-stop with the area clear, then let the robot fall or settle. A robot mid-way through the R-146b sequence may still move: **wait for MO_OFF plus 5 s with no motion** before approaching, even with the remote E-stop pressed. *(T&R edit 7)*
1a. **Battery first.** After any tip, TUCK or fall, check the pack **before approaching and before step 3**: smoke, hissing, a sweet or solvent odour, swelling, or BMS cell temperature rising (use a thermal camera on the pack if available). If any of these, **evacuate, keep clear, and do not roll or lift** (thermal-runaway risk). *(T&R edit 1)*
2. **Wait for touch temperatures.** The P-156 rev 6 / B2 **rear outlet shroud and jet-washed skin (N1/N1a)**: prone puts them
   **facing up, right where rescuers lean over**. The drives latch at 82 °C, so the **knee housing and drive band are hot too**, not only N1.
   Wait for the TP-G5-15 measured cool-down to ≤ 43 °C. Until that is published, treat N1/N1a/N2 and the knee/drive band as hot,
   and use **EN 407 contact-heat level ≥ 1 (100 °C) gloves** for any urgent move. *(T&R edit 2)*
3. **Remove the payload** if one is attached.
4. **Two-person roll prone → supine** (only if the robot must be moved). One person at the shoulders (H1 torso sides),
   one at the pelvis rim (H2). Roll toward the side the arms are on, as a log roll, keeping trunk and pelvis aligned. Expect
   the limbs to flop: keep hands and feet clear of the knee, hip and shoulder pinch zones (N5) and **off the thigh–shank gap** (the knee and hip backdrive freely in the roll: pinch). **Straighten the legs and strap the knees before rolling.** *(T&R edit 4)* Keep clear and **never hold the knee
   outlet zone (N1/N1a)** or the head (N3). Do not lever on the chest pad (N6).
5. **Lift** (supine or prone): 68.4 kg is ≈ 34 kg per person for two carriers, above the NIOSH 23 kg reference, so **at least three people
   or a board/strap lift aid is mandatory**. *(T&R edit 3)* Use H1 + H2 only, with the CoG (pelvis/lower torso) between the carriers. The
   legs hang limp: the third person supports the shanks below the knee zone (H4 thigh front is steadying only), or use a strap or board. Never lift by a limb: no brake holds it.
6. **Re-enable checks** before power-up:
   - all drive temperatures < 78 °C (R-141 resume), no MF 0xD000 / EMCY 0x4310 latched;
   - **chest cartridge** (*T&R edit 5*): the pad is underneath when prone, so inspect it after the supine roll or on a board lift.
     **Replace** it after any L2/L3/TUCK event regardless of appearance, or if crush indentation is > 2 mm, there is a face mark > 0.5 mm, or the
     tap test fails. The replacement must be a lot-certified cartridge in the 19.5–22.3 kN band, 100 mm core, bezel 4 × M4 captive at spec torque.
     Inspect the land, backing and bulkhead, with dye-penetrant after any L3/T-031-level event. Record the cartridge lot and the event in the fall log.
     Knee pads and covers intact;
   - after any L2/L3 event (*T&R edit 6*): pack OCV and group voltages, isolation and BMS log unchanged (TP-G5-17 criteria); chest cartridge
     replaced; an R-146 fall-budget entry made;
   - robot placed in a supported pose (prone or seated on a stand), area clear.
   Power up, run `re_enable()` (explicit operator action; the controller never auto-resumes).
7. **Stand-up checks:** joint-limit and encoder sanity check in the supported pose, then a stand-up only from a supported
   pose with the gantry or tether attached for the first stand after a thermal event. Log the event (R-146: fall-budget
   entry if it came via TUCK).
