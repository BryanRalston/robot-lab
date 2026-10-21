# V5 polish plan: compact, covered, Optimus-style (Robot Lab, 2026-10-14)

**Owner: RL Industrial Design (from 2026-10-14, Round 1). Cover material superseded by R-027: thermoformed PC 1.5 mm (P-020); CF per panel only if no heavier; extra coverage needs own P-numbers. Current draft: `V5_COVER_SET.md`.**

Goal (Bryan): make every section more concise and polished, like Tesla Optimus Gen 3. **Rule: covers and packaging only, or
changes that each owning module signs off.** No change may alter actuator sizing, linkage geometry, FEA'd parts or the
rollup without a P-number to the Arbiter. Covers are **CF/GF prepreg or wet layup on machined (aluminium/tooling-board) moulds,
or machined/formed sheet**. Nothing is 3D-printed.

Budget basis: official credible **64.920 kg**, reserve **1.580 kg** vs 66.5 (R-025 follow-up; 64.653 if A15 passes). Mass figures below are [EST] until owners compute them.

Concept render: `media/progress/2026-10-14_design_v5_polish_concept.png` (`modules/design/render_v5_concept.py`, 2D, light geometry).

## 1. What Optimus Gen 3 does (sources)
- Lower legs: exposed linkages and gold knee/shin plating are replaced by **matte-black shin fairings**. The body is a **contoured champagne-gold shell with tighter panel fits** ([Teslarati, 2026-09-23](https://www.teslarati.com/tesla-optimus-gen-3-shows-off-a-cleaner-factory-ready-design-in-new-app-discovery/)).
- **Flexible covers seal the torso to upper-thigh joint**, hiding bearings and pinch points; the `_gen3` render is more enclosed at the hips and lower legs than `_gold` ([Humanoids Daily](https://www.humanoidsdaily.com/news/tesla-app-optimus-gen3-renders); [ZeroGantry](https://zerogantry.com/articles/tesla-optimus-gen-3-design-renders-leak-in-android-app-update)).
- Hands: 22 DoF, with **actuators moved into the forearm and tendon-driven**, near-human finger proportions; forearms are thicker and integrated ([optimusk.blog summary of Feb/Mar 2026 reveals](https://www.optimusk.blog/blog/tesla-optimus-gen-3-vs-gen-2-comparison/); ZeroGantry).
- Torso: more cohesive surface, same overall outline ([36Kr](https://eu.36kr.com/en/p/3997025697175429)).
- Caveat: the renders are app mock assets, not confirmed hardware. Covered mechanisms don't mean simpler ones.

Takeaways for us: (a) a two-tone language, light rigid shells on load-bearing segments with matte-black fairings/bellows at moving zones; (b) every linkage inside a fairing; (c) flexible seals at the waist and hip; (d) a smooth head with a visor face; (e) hand actuators in the forearm (we already plan this).

## 2. Section audit and changes (prioritised)

| # | Section | v4 issue (bulky / exposed / crude) | Change | Engineering guard | Mass Δ [EST] | Owner |
|---|---|---|---|---|---|---|
| 1 | **Shanks / ankles** | Twin RV12 screws, GE12/QA1 rod ends and instep lugs fully exposed; reads as a test rig | Matte-black **CF shin fairing** (1.0 mm, 2 halves, quick-release screws) wrapping the screws; ankle **flexible boot** (TPU-coated nylon fabric, sewn, not printed) over the rod ends | Fairing sized to the swept envelope of pitch −45…+40 × roll ±18 plus 5 mm (clash_v4 envelope); rod-end service access every 4,250 h through the zip/quick-release | +0.18 (both) | Legs (envelope) + Robot Lab (shell) |
| 2 | **Thighs / knees** | Hip-pitch and knee screw pairs plus levers open around a ø50 femur; knee twin housing visible | Gold **CF thigh fairing** following the screw envelope (tapered 140→105 mm); black **knee cap** shell on the knee lever, sweeping 0–135° | Must clear the knee lever and the A17 clevis at all angles; mounts to the bonded thigh collar points (no new holes in FEA'd tubes) | +0.16 | Legs |
| 3 | **Pelvis / hips** | Tall hip yaw/roll stack (~200 mm from hip axis to pelvis bottom), open 4 mm 7075 box, bumpers visible | **Flexible hip skirt** (black, Optimus-style seal) from pelvis to upper thigh; pelvis gets a contoured CF outer skin instead of the bare box. *Stack-height reduction is a v6 mechanism item, not polish* | Skirt must pass yaw −35/+45, roll −12/+15, hip pitch full range incl. the −74.6° sit (R-012) | +0.12 | Legs + Arbiter (mass) |
| 4 | **Torso / waist** | 220×340 rectangular CFRP box; exposed yoke plates and cheeks at waist yaw/pitch | **Tapered chest shell** (340 at the shoulder axis z 220 → 250 at z 50, 45 mm chamfered top shoulders; 340 not 330 so the Ø110 pitch openings sit on the y ±170 walls — ID decision, R-133) on the same battery/compute bay; **waist bellows band** over the yoke; shoulders sunk into the shell line | Battery 185×220×144 and Jetson bay unchanged; reuse the existing shell mass (replace, not add). Thermal vents on the compute bay | ±0 (replaces the 3 mm box) | Robot Lab |
| 5 | **Head** | 190 mm CF sphere with a camera block, gap at the neck | **Integrated head**: elongated CF shell with a black acrylic/PC visor (machined or thermoformed) in front of the ZED X Mini; black **neck sleeve** (fabric) | XM430 servos, P-019 line and mass intact; the visor must be optically flat at the ZED window (or a cut-out) | +0.02 | Robot Lab |
| 6 | **Arms** | ø50 tube + boxy brackets + strain-wave pucks; all placeholders | Gold **upper-arm shell** and black **forearm shell** sized to the real actuators *once engineered*; shoulder cap over the pitch/roll stack | Do not draw shells before the actuators exist (would freeze fake envelopes) | TBD | Robot Lab → new Arms agent |
| 7 | **Hands** | Box palm and cylinder fingers, "PA12" palm (3D-printed: not allowed) | Tendon hand with drives in the forearm (as in v4 notes); **machined 7075 palm + CF backplate**, silicone grip pads (cast in machined moulds) | PA12 palm must go → a machined part; finger proportions human | TBD | Robot Lab → Hands agent |
| 8 | **Feet** | Flat plate with exposed collar/instep lugs | Gold toe/heel cover (CF) with a black rubber sole; hides the instep lugs | Must not change the 240×100 contact patch or the CoP refs | +0.05 | Legs |
| 9 | **Finish / cables** | Harness runs exposed at joints | Route through the fairings with clock-spring loops (Actuators R5 harness); bulkhead connectors at the fairing splits | No change to harness mass basis (1.314) | ±0 | Actuators |

**Cover material flag:** the official rollup's `covers M3` line (1.384 paper / 1.622 credited) is still based on **PA12 density, i.e. 3D-printed**. That conflicts with the no-printing rule. The v5 covers above **replace** that line rather than add to it: CF prepreg at 1.0 mm (ρ≈1.55) weighs about the same as PA12 at 1.5 mm (ρ≈1.01). Net estimated change vs the existing line: **+0.2 to +0.5 kg** (more coverage: shins, skirt, bellows). That is **within the 1.58 reserve** but uses up to a third of it. Arbiter ruling needed (one P-number for the whole cover set).

Total [EST]: sum of rows ≈ +0.53 kg if added outright; ≈ +0.2–0.5 kg net of the PA12 cover line it replaces. Reserve after: ≈1.1–1.4 kg (≥0.30 floor).

## 3. What does not change
Actuator sizing, linkage geometry, the FEA'd femur/tongue/clamp/clevis/foot, joint ranges, and the P-019 head line. Covers attach only to existing bonded collars, clamp bosses and shell flanges. Any new hole in an FEA'd part goes back to its owner.

## 4. Sequence (v4 → v5)
1. Arbiter: rule on replacing PA12 covers with a CF cover set (one P-number), now.
2. Legs: export the swept envelopes per leg segment (clash_v4 pairs + 5 mm) → Robot Lab draws shin/thigh/skirt/foot shells in model_v4 as a `covers` group (toggle in the viewer). Rows 1–3, 8.
3. Robot Lab: torso taper, waist bellows, integrated head. Rows 4–5.
4. Actuators: harness re-route through the fairings. Row 9.
5. Arms/hands (rows 6–7) wait for the engineered actuators. Shells are drawn last.

## 5. Recommendation: new module agents
- **Yes, create one "RL Arms & Hands" agent now.** 26 of the 32 audited joints are upper-body placeholders. Arms and hands are coupled (forearm-housed tendon drives set the forearm envelope), so one agent fits better than two. Scope: shoulder/elbow/wrist actuator selection, tendon hand, forearm packaging, and its mass line to the Arbiter.
- **Torso/waist: not yet.** It's mostly packaging (battery, compute, waist drives). Robot Lab can carry it until the arms agent's shoulder loads exist; revisit at round 13.
- A separate Hands agent only if the 22-DoF-class tendon hand is chosen over a simpler 6–11 DoF hand.

## 2026-10-21 — chest bulge 65 mm (116 mm core, Torso 1585e80)
The chest pad now stands 65 mm proud of the torso cover (face at x +0.175), and head clearance prone is 69.8 mm (T-031 PASS). To keep the torso reading slim, the bulge is no longer a box. A 21°-draft tapered PC bezel/fairing (P-052 rev 2) turns it into a faceted sternum keel, with 4 mm chamfered edges, an R6 front edge, cover colour, and the CF face as a dark inset that echoes the head visor. Net +0.028 kg for the fairing (+0.004 for the crush posts). It is cover-only. Detail: V5_COVER_SET.md §Chest bulge.
