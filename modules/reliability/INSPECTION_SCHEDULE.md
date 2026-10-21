# Wear / inspection schedule (T&R, started 2026-10-21)
Items accumulated from T&R reviews. Owners: Controls (operator manual), Legs/Torso/ID (part specs).

| id | item | trigger | inspection | replace / action | source |
|---|---|---|---|---|---|
| **F1** | **post-fault (motors-off fall, knee stop may bottom)** | any motors-off fall or a logged stop energy > 44 J | tibia/femur near the knee: straightness (≤ 0.5 mm/300 mm runout), dye-penetrant at the knee-end collars and bonds; knee PU stop pads (crush/cracks); stop striker and clevis cheeks; knee screw end play; hip-roll bumpers; drive fault log | femur slight set accepted (yield SF 0.98 at bottoming): **replace any tube with measurable permanent set** or a crack indication; replace the knee stop pads after any bottoming; log it in the fall budget | L60 rev C |
| F2 | chest crush cartridge | any L2/L3/TUCK/fall event, > 2 mm crush, > 0.5 mm face mark, failed tap test | visual + tap | replace (lot-certified, 116 mm core), bezel M4 torque | R146 §9 |
| F3 | hip-roll PU bumpers (L39, ø20×10 PUR90A, 4.68 J at 25 % cited) | any event > 4.68 J (logged ω_c), each service | visual, set, cracks | replace if set > 10 % or cracked | SIDE_FALL rev B/C |
| F4 | hip skirt foam edges | monthly, after any pinch/fall/rescue | thickness, tears, heat glazing | replace at > 10 % loss or annually | R_HIP_PINCH 8b |
| F5 | knee PU stop pads | each service, after any stop-engaging fall | set, cracks | replace on set > 10 % or after bottoming | L60 rev C |
| F6 | ankle roll stop blocks (M4 12.9 zinc-flake + Loctite 243, helicoil, ø4 h6 dowel) | after side falls with logged stop contact; each service | witness mark/torque, **dowel present and tight**, block/pad damage, helicoil seated | replace the bolt after any loosening (Loctite); replace a missing dowel before use (bolt-only SF 1.08) | SIDE_FALL rev C |
| F7 | knee venting covers / shroud louvres | each service | louvre damage (IP2X), foil intact | replace damaged parts | R143 B2 |

## Waist-pitch friction limiter break-away (D102c, Actuators eb5520f) — added 2026-10-21 ~11:25 ET
- **What:** bench break-away torque of the waist-pitch friction limiter (CSG-25 output → limiter → yoke). Set by measured break-away, not nut angle.
- **When:** at each service; after any logged fault event > 100 J limiter slip; or when cumulative logged slip energy reaches 10 kJ — whichever first.
- **Acceptance:** 170 N·m ±10 % (153–187 N·m). Outside the band → re-shim / re-torque the M68 nut ring and re-measure; if it cannot be brought into band, replace linings/Belleville.
- **Also:** compare joint absolute encoder (yoke side) vs motor encoder × N after any slip; re-home. Inspect PU end-stop faces and torso-cheek lugs for set/cracks after any > 100 J event.
- Ref: R1_FMEA F20, TP-G5-22. Wear interval (~10 000 routine events) is [EST] until TP-G5-22.

## Post-fall head inspection (FMEA F19) — added 2026-10-21 ~11:25 ET
- **When:** after any head-first ground contact (logged or observed).
- **Check:** (1) visor (replaceable, 4× M2.5) for cracks — replace if cracked; (2) LD29 head liner (P-161, ID dc84836) for permanent set; (3) CF shell at the contact point for cracks/delamination.
- **Thresholds:** TBD — pending ID and Materials. No numeric acceptance set yet.

## Hip-pitch screw tubes (FMEA F21, Legs f535463) — added 2026-10-21 ~11:27 ET
- **When:** after any fall or limp (drives-off) event.
- **Check:** L/R inner hip-pitch screw tubes and seals for dents/scuffs from body-on-body contact; check interim PU pad band condition. Acceptance thresholds TBD (Legs/Actuators).
