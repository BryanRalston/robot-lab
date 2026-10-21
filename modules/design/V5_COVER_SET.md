# V5 cover set (RL Industrial Design, 2026-10-14; baseline = trimmed set per R-029)
Owner: RL Industrial Design (also owns `V5_POLISH_PLAN.md` from this round). Basis: **R-027 / P-020**: thermoformed PC 1.5 mm (ρ 1.20, 1.80 kg/m²), CF 4×0.25 twill (ρ 1.55, 1.55 kg/m²) allowed **per panel only if no heavier than its PC version**; extra coverage needs its own P-number. Numbers from `cover_set_v5.py` → `cover_set_v5.json`. Everything is **[EST]** until A29 measures panels on CAD.

## Baseline: trimmed set (R-029/R-030; final Legs envelopes c44da58/fa47eec; `cover_set_v5.json`, measured: false)
Hull areas now come from the final `legs/results/v5/ENVELOPES_FOR_ID.md`: knee_cap 3422→1211, hip_skirt 11317→2987, foot_upper 1927→1055 cm². Rigid panels are front + outboard = **0.45 × hull** (Legs range 0.4–0.5). Knee cap 0.30 × hull and skirt fabric 0.40 × hull [EST].

**No-cover zones (Thermal D69, Legs):** knee saddle (tibia, z 320–415, r ≤ 47, fins rear/sides, free air, no exhaust onto the tibia collar) and lower shank z 136–415. **The shin fairing is deleted** (the zone was later withdrawn by Legs 6f53d77; the shin is now an optional add-back, see below). Ankle boot only below z 170. This also sets the A36 vent scope: no shin vents, and the knee cap must not duct air onto the saddle.

| panel | P | material | skin m²/side | panels | kg (PC) | kg if CF | Δ vs booked | mount |
|---|---|---|---|---|---|---|---|---|
| ~~shin fairing~~ | P-020 | deleted (no-cover zone) | 0 | 0 | 0 | — | | — |
| thigh fairing, front + outboard | P-020 | PC 1.5 (CF option) | 0.119 | 4 | 0.443 | 0.383 | | split collar ø64 L34; **P-053 rev 2: no pin access panel** (L30 60×70 hatch deleted; bench-only extraction); rear 40×50 window kept open, unpanelled |
| foot top shell | P-020 | PC 1.5 | 0.048 | 2 | 0.179 | — | | M3 inserts in foot box webs; covers instep lugs |
| **P-020 subtotal** | | | 0.332 m² total | 6 | **0.621** | 0.561 | **−0.536** (booked 1.157) | |
| knee cap | P-022 | PC 1.5 (louvred per P-026, A36) | 0.036 | 2 | 0.139 | — | +0.139 (R-029 itemized 0.116: **+20 %, R-030 >10 % trigger**) | M4 inserts, front face of knee tongue neck block (x 10, z 438–478) |
| hip skirt | P-023 | TPU-coated nylon + PC rim strip | 0.120 | 2 | 0.120 | — | +0.120 (was 0.114, +5 %) | rim at pelvis flange z 1126; elastic hem to thigh fairing top z 885 |
| waist bellows | P-024 | TPE | 0.085 | 1 | 0.055 | — | +0.055 | clamp bands |
| ankle boot | P-025 | TPU-coated nylon, zip | 0.101 | 2 | 0.098 | — | +0.098 | drawstring z ≤ 170; elastic hem on foot shell |

**Total vs booked: −0.124 kg PC** (a net saving); **−0.184 kg with CF thigh**. Over the 0.40–0.50 fraction range: about −0.19 to −0.06 kg. Against the +0.30 cap (R-029) / +0.236 booked (R-030): **PASS with margin.** **Arbiter flag:** P-022 knee cap rises 0.116 → 0.139 (+0.023, +20 %) on the larger final knee hull, although the set total drops.

**Knee cap vs thigh fairing clearance (Legs):** no overlap from 0 to 135°. Minimum keep-out gap is **10.2 mm at 135°** (22 mm from 0 to 105°). After the D69 ø85 knee housing (+4.5 mm radial) it is **≈ 5.7 mm [EST]**, still above the 3 mm PC flex gap. Recheck after the D69 re-CAD.

## Shoulder impact pad (R-042, P-051 proposed): see `SHOULDER_PAD.md`
R2: 40 mm EPP failed against the real crush curve (Materials). **R-079: R8 option B adopted** — replaceable 7075 tray on the integral boss, **0.116 kg pair (+0.024 vs 0.092 booking)**; field rebonding A rejected. Pad centre on the CRBH 6013 plane. Arm shells stay deferred.

## R-059 / R-060 decisions (recorded)
- Pad R5 accepted (R-059), then R-060: the mount counts inside the cap, a 7075 doubler is required, the pad is booked 0.127 → R6 above at 0.100. Lot-tested cores ±5 % + G5 rate factor; 15° impact limit.
- Wrist fairing accepted at +0.079; torso-facing orientation forbidden.

## R-054 decisions (recorded)
- Pad R4 accepted at 0.100 kg pair (booked); R5 relocation is 0.097. Cover trims accepted at **−0.118** (half-credit).
- **Shin fairing deferred until Actuators D69 rev B is verified** (R-057: rev B CAD-measured, condition 1 met; A47 fairing check still open). At add-back **louvred CF (+0.198 pair) is preferred**. Additions > 0.02 need a ruling (R-057).
- The forearm may grow 97–122 mm (D73 + D74), pending an Arbiter ruling. R-057 has since adopted D76 compaction and closed the lengthening fallback; see WRIST_FAIRING.

## Legs 6f53d77 / Thermal 9b9e169 update: shin zone withdrawn, knee-housing grille
- **Knee saddle / lower-shank no-cover zone withdrawn.** Under the R-047 freeze the **shin fairing stays out of the baseline** and is an **optional add-back for an Arbiter decision** (front + outboard 0.45 × 1751 cm² = 0.079 m²/side, 4 panels, +4 tools):

  | shin add-back | pair kg |
  |---|---|
  | PC 1.5 | +0.300 |
  | PC 1.5 louvred 30 % | +0.227 |
  | CF 1.0 | +0.260 |
  | CF 1.0 louvred 30 % | +0.198 |

- **New no-cover zone: knee housing fins** (thigh frame, trunnion x −130, z 770). The thigh fairing gets a **grille over the housing front face: 115 × 110 mm/side [EST]** (ø85 + fins 2 × 10 + 2 × 5 mm), 60 % open, merged into the P-026 louvre field where they overlap. The rear face is already open (the fairing is front + outboard only); no fins on the ±y flanks, so no side grille.
- **Thigh fairing pair mass: 0.443 → 0.322 kg** (louvres 30 % + grille, cut slots, 15 % rib allowance). R-047 item 1 goes from −0.142 to **−0.154** (grille −0.012). The knee cap gap is unchanged (housing ≥ 110 mm from the knee cap keep-out).

## WRIST_FAIRING (R-057: D76 adopted; ID design, Arms R2 item, P-020 PC 1.5 mm)
Basis: Actuators D76 (pitch CSG-14-100 + yaw CSF-11-100 units side by side, axial along the forearm, centres y ±29, each about ø56, z +28 … +90.8 above the wrist pivot); forearm ø70; palm 86 wide (Arms R5). Supersedes the D73 bulge note (ø90 roll and the z +140 cans are gone).
- **Section:** stadium **124 (y) × 70 (x) mm**. 124 = 2 × 58 unit width + 2 × (3 mm air gap + 1.5 mm wall) − 1 mm overlap at the y-flats [EST]. Depth stays 70, flush with the ø70 forearm, so it only bulges in y.
- **Length:** the full section runs z +23 … +96 (units + 5 mm each end) plus blends: 25 mm to the ø70 forearm (elbow side, ≤ 1.5:1 draw) and 20 mm to the wrist cuff (pivot side, tapering to about 116 × 70 at z +3, over the pitch/yaw links). Total about 141 mm.
- **Split line and access:** split in the y–z plane (x = 0): a dorsal half and a palmar half, each spanning both units. **Removing the dorsal half (4 × M3 quarter-turn) exposes both units, both links and the AksIM encoders** without touching the hand or tendons. The palmar half stays on for tendon routing.
- **Attachment:** both halves clip into the forearm shell lip at the elbow-side blend (8 mm overlap, 2 × M3 bonded inserts each), plus 2 × M3 into the D76 unit carrier plate at z +28 (existing carrier; no new holes in structural tubes). The wrist-cuff end floats (2 mm gap) to the hand so wrist motion doesn't load it.
- **Air gap:** 3 mm to each unit, plus 3 mm PC flex gap. **Thermal:** TBM2G frameless motors at the wrist dissipate at low duty [EST]. Provisionally **2 rows of cut slots, 20 % open on the dorsal half over each motor**, which saves about 0.004 kg/side. **Thermal to confirm** whether the wrist units need venting (no wrist thermal case in repo).
- **Mass (PC 1.5, ρ 1.20):** skin 0.044 m² → 0.079 + 4 inserts 0.016 = **0.095 kg/side, 0.190 pair**. Against a plain ø70 forearm shell over the same 141 mm (0.056/side): **+0.039/side, +0.079 pair**. This is an **Arms R2 arm-shell item**: arm shells are deferred and not booked, and since > 0.02 it needs a ruling when they're booked.
- **Palm grasp clearance:** the fairing is proximal to the pivot (from z +3) and 19 mm per side wider than the 86 palm. For a power grasp the object sits distal of the pivot, so there's no conflict at neutral. At wrist yaw ±30° / pitch ±60° (P-026 ROM) the palm flank swings toward the fairing flank. **No repo CAD for the hand vs fairing sweep: Arms to check ≥ 5 mm at the yaw/pitch limits** (cuff taper to 116 helps).
- **A44 tuck torso clearance:** the forearm capsule (r 38) clears the torso by **8.6 mm** (Arms R5). If the 124 mm width faces the torso in the tuck, half-width 62 vs 38 → **−15.4 mm clash**. If the wide axis lies parallel to the chest (depth 35 ≤ 38), it is unchanged, **+8.6 mm**. The forearm roll in the tuck pose isn't in the repo: **Arms/Controls to confirm the wrist yaw/pitch unit axis is parallel to the chest in the tuck** (or set wrist roll to make it so).
- **R-059: accepted at +0.079 pair.** The wide axis must be **parallel to the chest in the tuck; torso-facing is FORBIDDEN** (−15.4 mm clash).
- **New tuck (Arms c64ab91):** shoulder roll −5, yaw −60, **pitch −30**, elbow −110 → forearm 28.0 mm, wrist **27.8 mm clear** with the width parallel to the chest. Controls to adopt.
- **Lower (cuff) edge at z ≥ +10 above the wrist pivot over |y| ≤ 62**, and outside r 24.5 + 5 near the pivot (Arms hand calc: palm top ≈ z +5 over pitch ±60 × yaw ±30; bryan-PC sweep to confirm). The cuff taper now ends at z +10, not z +3.
- **Trims (per side):**

  | trim | kg/side |
  |---|---|
  | 1.2 mm PC on the y-flats (low draw, 2 x 54 x 96 mm) | -0.0037 |
  | dorsal motor slots 20 % (3 mm slots, 2 rows/unit) | -0.0024 |
  | shorter blends 25->15 mm (elbow) and 20->12 mm (cuff); cuff edge held at z >= +10 over |y|<=62 (Arms sweep) | -0.0106 |
  | palm-side half as open frame (Arms-accepted: openings <=10 mm radiused, 4 mm members, ~55 % open) | -0.017 |
  | **total** | **-0.0337** |

  Pair -0.067 → fairing 0.123 pair, +0.012 vs a plain ø70 shell. The open-frame item went from −0.0185 to −0.017/side with ≤ 10 mm openings (about 55 % open instead of 60 %).
- **Arms ACCEPTED the open-frame palm half on these conditions:** (1) flexor tendons stay in **steel-coil sheaths** (Materials TENDON_SHEATH.md) continuously through the open zone; (2) frame openings **≤ 10 mm with radiused edges**, no snag at pitch ±60 / yaw ±30; (3) frame members keep the **z ≥ +10** lower edge; (4) if the sheath ends up plain PTFE, add a 1 mm PC guard strip 15 × 140 mm over the tendon bundle: **contingency +0.0025/side, +0.005 pair**, **only if CAD shows a gap** between the sheath and the frame (not booked otherwise).
- **Verdict: ACCEPTABLE WITH CONDITIONS:** (1) Arms confirms the tuck orientation (wide axis parallel to the chest), otherwise a −15.4 mm clash; (2) Arms hand-sweep check ≥ 5 mm at yaw ±30° / pitch ±60°; (3) Thermal confirms the venting need; (4) +0.079 pair is booked with the arm shells at Arms R2 (ruling needed, > 0.02).

## R-047 offsets
See `COVER_TRIMS_R047.md`. R-067 rebooked the trims at −0.073 (half credit). Pad R7 −0.016 vs its 0.100 booking; wrist trims −0.067 pair (−0.034 half credit).

## A29 panel layout and mould list (owner: Industrial Design per R-029)
Status: layout from Legs keep-out hulls + model_v4 dims, **not yet measured on v4 CAD** (areas [EST]). Delta check: itemized `modules/design/cover_set_v5.json` = **−0.124 kg vs booked (−0.184 CF thigh): PASS**; P-022 +20 % flagged.

| # | panel (per side unless noted) | split / layout | draw [EST] | mould (L/R separate) | process |
|---|---|---|---|---|---|
| M1–M2 | thigh front piece | taper 140→105 mm; ends above knee-cap keep-out | ≤ 2:1 | 2 | PC / CF option |
| M3–M4 | thigh outboard piece | lateral face, clears hip-pitch screw | ≤ 1.5:1 | 2 | PC / CF option |
| M5–M6 | foot top shell | top of 240×100 box only, hides instep lugs | ≤ 1.5:1 | 2 | PC vacuum-form |
| M7–M8 | knee cap (P-022) | shank-mounted, sweeps 0–135° outside thigh fairing | ≤ 2.5:1 | 2 | PC vacuum-form |
| M9 | hip skirt rim strip (P-023) | flat-formed strip, both sides from one tool | ≤ 1:1 | 1 | PC strip former |
| P1 | hip skirt fabric (P-023) | 2 sewn panels from flat pattern | — | cut pattern | sewn TPU-nylon |
| M10 | waist bellows (P-024, 1 off) | single band, convolutions over yoke | — | 1 dip/rotational mould, or catalog bellows if one fits ø300 × 90 | TPE |
| P2 | ankle boot (P-025) | flat pattern + zip | — | cut pattern | sewn TPU-nylon |

Rigid thermoform tools: **8** (shin deleted, since the lower shank and knee saddle are no-cover zones; A30 updated) + 1 strip tool + 1 bellows mould; 2 sewing patterns. Trim fixtures: one per rigid tool (8). No panel over the knee saddle (z 320–415) or lower shank (z 136–415). Next: measure panel areas on model_v4 CAD and confirm draw ratios; re-run `cover_set_v5.py` with measured areas.

## Area measurement status (R-030)
Not measured yet. Measuring trimmed panel areas needs the build123d model_v4 rebuild plus the Legs keep-out STLs (not on main), which is a heavy CAD job. Route it to Bryan's PC. Until then `cover_set_v5.json` areas stay [EST] (`measured: false`). Re-rule trigger: any panel measuring > 10 % over its estimate.

## A36 / P-026 vent layout to Thermal A35 (A35_VENT_SPEC.md f4e6dfb, D68 7675c8b, D69C b785697): `a36_vents.py` → `a36_vents.json`
Rules per joint per leg: inlet ≥ 50 cm² and ≥ 30 % of the panel over the housing; outlet ≥ 60 cm² and ≥ 35 %; fin tips ≥ 8 mm from the cover's inner face (never < 5); slots ≥ 3 mm, no mesh < 2 mm; low-front in → axial along the cans (louvres aligned with the fins) → out high-rear/outboard.
| joint | inlet | open cm² | outlet | standoff |
|---|---|---|---|---|
| hip_pitch | front-lower thigh fairing below the P-023 skirt line, axial slots | 75 (30 % of ~250) | rear-upper/outboard at skirt hem: laser-cut slotted band in the skirt fabric (slots 3x20 mm), routed outboard of the thigh-clamp collar (collar uncovered); band 171 cm² at **41 % = 70 cm²** (Thermal a8811f5: raised from 60, which was 3 % short) | ≥ 8 mm from the screw/can, in the existing keep-out (+5) plus the 3 mm flex gap = 8 |
| knee | front-lower thigh fairing over the housing (axial slots 3-4 mm, aligned with front 9 mm fins) + knee cap louvres as ram entry | 84 (30 % of ~280) + knee cap 109 | rear (popliteal) high: thigh fairing has no rear panel -> free outlet, rear 25 mm fins in free air (>= 60 cm2 trivially) | front fins 9 mm -> fairing inner face at r 59.5 from housing axis (fin tip + 8): local bulge +12 mm vs the R1 keep-out (housing + 5) |
- **Thigh-clamp collar stays uncovered**; the hip exhaust leaves at the skirt hem rear-outboard, outboard of the collar.
- **Knee cap (P-022):** the rear 25 mm and front 9 mm fins are on the knee housing at thigh z ≈ 770, ≥ 110 mm from the knee-cap keep-out (Legs 6f53d77). The cap never closes over them, so no reshape is needed for fins. The cap gets 30 % louvres plus an inlet lip; its top edge stays ≤ z 555.
- **Thermal a8811f5:** knee PASS (slots in line with the fins). Hip exhaust raised to ≥ 70 cm² open; skirt fabric removed ~0.0003 more per side (negligible). R-069 item E is now computed on the fabric net of the 70 cm² exhaust (−0.045).
- **Panel-area check vs Thermal's ~430 cm²:** ours is ~280 (knee) / ~250 (hip), since the fairing is front + outboard only and the rear is open. The % rules govern; open areas still meet ≥ 50/60. Thermal to confirm the rear-open outlet counts.
- **Mass (pair):** thigh -0.026 (slots minus the +12 mm fin bulge), knee cap -0.033, hip skirt **+0.004 (ADDED: hem stiffener ring holding the exhaust open)**; total **-0.055**. **R-047 item 1 goes from −0.154 to -0.055 (+0.099 less saving: FLAG).**

## Option: untrimmed set (`python3 cover_set_v5.py --untrimmed` → `cover_set_v5_untrimmed.json`)
Full-wrap shin/thigh fairings (0.70 hull), foot shell 0.40, upper-arm (ø95×260) + forearm (ø85×267, R-082 +17 mm) shells + shoulder caps as placeholders. P-020 → **2.014 kg** (+0.857 vs booked) + P-022…P-025 0.383 → **+1.257 kg**. Rejected by R-029 against the 1.329 kg reserve / 0.30 floor; kept for reference only.

## Clearance assumptions
- Leg keep-outs: Legs `legs/results/v5/envelopes.json` (hull areas snapshotted into `cover_set_v5.py`) (fairings_v5.py, model_v4 swept, convex hull + 5 mm; **uncommitted Legs WIP, not yet confirmed by Legs**). Shin: ankle pitch −45…+40 × roll ±18; thigh: hip pitch −105…+40 (incl. −74.6 sit) × knee 0–135; skirt: yaw −35/+45, roll −12/+15.
- Skin fraction 0.45 of final hull (thigh, foot top; range 0.4–0.5; 0.70 untrimmed), knee cap 0.30, skirt 0.40, 0.80 (boot): [EST].
- Additional 3 mm air gap inside the keep-out for PC flex under fall load [EST]; draw ratio ≤ 3:1 (LEXAN guide) assumed achievable on all rigid panels; panels split at the 3:1 limit.
- Arm/shoulder: no envelope exists; shells are placeholders (V5 plan row 6).

## Arms R8 / R-082 forearm cover
- Structural forearm **270 → 287 mm** (+17 mm, R-082); shell stays **Ø70**; wrist fairing unchanged.
- Cover placeholder length **250 → 267 mm** (ø85 × 0.85 wrap): area/side 0.0567 → 0.0606 m²; **+0.007 kg/side, +0.014 kg pair** (`cover_set_v5.py`). R-087 books the forearm cover at +0.014.
- **Proportion sign-off:** forearm/upper-arm **0.96** (287/300) is **acceptable** for an Optimus-class figure.
- Foot top shell: baseline still lists it; **R-081 C2 deletes it** (see `COVER_TRIMS_R069.md`).

## Knee fin grille / drive-bay vents (A36 / R-087 / L55–L61)
- **Local +12.7 mm bulge** on the knee-housing grille: rev B fins are 4.7 mm past the keep-out; Legs asked +5 mm, but A35 needs ≥ 8 mm tip clearance → **4.7+8=12.7**. Mass **+0.021 kg pair**. (+5 mm alone → only 0.3 mm clear, rejected.) See `KNEE_BULGE_L61.md`.
- **Merged PA12 thigh-rear panel** (`knee_drive_panel.py`): **0.071 kg pair**. Bosses at Legs L58 tab tips **(x−38, y 100/160, z 700/780)**, M2.5 — alignment **PASS**. Inlet 52 / outlet 63 cm².
- **L61 cheek bosses (ø26×20, 14 mm proud):** fin clear ≥ 9 mm; **~9 mm EST clash** with outboard fairing → open window 40×30 per cheek (**0 kg**).

## P-052 sternum bezel (R-094; was full plate under R-088/R-093)
- **Pad 1 mm CF face is the visible skin** at x ≈ +0.147 (37 mm proud), bonded to the 7075 land. **PC 1.5 mm bezel ring** (4 captive M4s at (±0.040, +0.180/+0.260)) is the secondary hold and cosmetic edge: ≤ 4 mm flange overlap, 1 mm gasket stand-off (no preload), centre 90×90 free, foam edge seal (not bonded to core), **R-095 clear coat on the CF face (TPU film removed, R-113)**, 15 mm blend.
- **ID mass 0.035 kg** (bezel + gasket + seal + blend + captives; film removed R-113, −0.005) vs old plate **0.058 (−0.023)**. Net vs CF shell removed (~0.045): **−0.010**. See `STERNUM_PLATE.md`.
- **Service:** visible dent > 1 mm or any crush → replace the pad.
- ~~TPU film (R-098): 4.61 g~~ **removed per R-113** (R-095 clear coat confirmed on the drawing): **−0.005 kg**, already booked in R-113.

## P-053 thigh collar pin access, rev 2 (Legs L63-R 504082f; confirmed 10/20; supersedes L30 / a14_r7 and the rev 1 218° band)
- Legs confirmed: 8 × ø7×10 radial pins, row 1 at 0/90/180/270°, row 2 at 45/135/225/315° (z 8.25/25.75), M3-tapped ends. They are bonded fault-backup parts, **extracted only on the bench with the thigh dismounted**, so no on-robot tool room is needed.
- **Design:** no dedicated access panel. The L30 hatch (60×70 + 4 M3) and the rear 40×50 panel (2 M3) are deleted, and so is the rev 1 band. The P-020 front half is continuous over the collar. For bench service the front and outboard P-020 halves come off whole on their own fasteners. **Their removal never depended on L30**, which was only a hatch inside the front half. The rear 40×50 window stays an open hole.
- **Coverage:** the fairing covers **5 of 8** pin ends (0, 45, 90, 135, 315°). The 180° end shows in the rear window and the 225/270° ends on the open inboard side, exactly as under L30, since P-020 never covered the collar's rear or inboard faces. The pins are flush, bonded, passive steel, so this is cosmetic only.
- **Mass:** 0 vs L30 0.018/leg → **−0.018/leg, −0.036 robot** [EST]. The P-020 hull (0.443) already counted the front skin unpierced. Rev 1 (+0.016) is withdrawn.

## Foot-sole fallback (Robot Lab 10/20, +0.049 kg/foot) — no cover-set impact
The sole pad is under the foot plate; the P-025 ankle boot hem is re-anchored above it through the 4 existing foot inserts (C2). A thicker fallback sole (SP 67A 6 mm frame vs 3 mm) lowers nothing the hem touches, so P-025 geometry and mass are unchanged. The mass is Legs' line, not ID's.

## Open questions
1. Legs: confirm envelopes.json as final and commit; knee-cap keep-out complement vs thigh fairing overlap.
2. A29 now owned by Industrial Design (R-029): panel layout + mould list on v4 CAD; measured delta must stay ≤ 0.30 kg.
3. CF on thigh for looks (shin deleted) (two-tone gold/black) — cost delta vs A30 sheet.

## R-143 knee plate rev 4 + P-154 fin guard: full-ROM sweep (cad/covers/r143_knee_sweep.py/.json, knee_fin_guard.py/.json/.stl)
- Inputs: Actuators 5008683 (rev 4): 100 × 48 plate, 8 fins **18.5 mm** (tips x −53.0), edge seal = 1 mm silicone bead inboard of x −34.5. Thermal 44b7c36: ≥ 10 mm air above the tips, ≥ 60 % open face, ends open, low-ε inner face. **Guard inner face 28.5 mm, outer 30.0 mm proud (x −64.5).**
- Legs L71 (6060973):
  - (a) Plate placement and lever eye r 47.5 confirmed; **rods at y 130 ± 45**; Legs' minimum to the knee twin housing is 18.1 mm at 145°.
  - (c) Insert bosses.
  - (c2) Tab / side-wall issue.
  - (d) Guard is sacrificial: confirmed.
- **Guard rev 4b (changed for L71 c2):**
  - Widened to **104 × 66 outer / 101 × 63 inner**, so the outer fins (y ± 21.5) are **10.0 mm** from the side walls (was 4.5). The walls now sit outboard of the plate, 7.5 mm/side (≥ 0.5 fit), and are clear of the seal bead.
  - The guard flange seats on the drive-bay panel window frame (66 × 104 + 4 mm flange).
  - **4 base notches, 10 (z) × 7 (x)**, at the L58 tabs (y 100/160, z 700/780) → ≥ 3 mm to the tab ends (was 0 / 1.5).
  - Fin tip to inner face **10.0 mm**. 45° × 8 lower-edge chamfer + matching fin taper kept.
  - Open area: 11 face slots 4.0 × 96 → **62 %** face, **57.9 cm²** total (≥ 25). IP2X: 4 mm slots, the 12 mm finger cannot enter.
  - Inner face low-ε Al (ε ≤ 0.1); outer face in cover colour.
- **Bosses (L71 c):** 4 ribbed PA12 bosses Ø6 × ≥ 5 mm in the window frame at y 112/148, z 684/796 (window ends, off the L58 screw line y 100/160 z 700/780), M2.5 heat-set; 4× M2.5 A2 captive per side.
- **Sweep at 30.0 mm, 1° steps, gate ≥ 3 mm:**

| Check | Min clearance | Where / angle | Result |
|---|---|---|---|
| RV12 rods (y 130 ± 45) vs guard / chamfer | **12.0 mm** | knee 140° | PASS |
| Knee twin housing (Legs L71 CAD) | 18.1 mm | knee 145° | PASS |
| Shin / boot keep-outs | 95 mm | knee 0–145° | PASS |
| Pelvis underside | 180 mm | hip −105…+40° | PASS |
| Seated | 132.5 mm | hip 90° | PASS |
| L58 tabs | ≥ 3 mm (notched) | static | PASS |

- **Mass:** guard 0.0155 kg/side → 0.031 pair; window −0.019 → **net +0.012 pair [EST]** (+0.001 vs rev 4, −0.008 vs the +0.020 booking).
- **Actuators to confirm:** fin lower-end 45° × 8 taper (Thermal UA effect). **Legs to confirm:** bosses at y 112/148, z 684/796 in the window frame.

## P-156 thigh-fairing knee venting (replaces the P-154 guard, withdrawn) — cad/covers/thigh_knee_vents.py/.json/.stl
- Basis: Thermal 389f91b (R131 rev 4b): fins sit 48–53 mm inside the v5 hull, and a closed fairing gives > 130 °C. Governing spec via Legs; Actuators D94 (7d22c91): plate window 100 × 46 at y 107–153, face x −34.5, fins 18.5 (tips −53.0); L58 tabs to x −38.
- **Grille (integrated in the v5 rear skin, x −82.5):** 104 × 52 (y 104–156, z 688–792) over the full fin field.
  - 8 slots 4.5 × 98 along the fin channels, 2 mm ribs → **65 % open (3528 mm²)**. Slots flush with R0.5 edges, cover colour outside (matte 2K), **Al liner ε ≤ 0.1 inside**.
  - Fin tips to the grille inner face **29.5 mm** (≥ 10; x −82.5 ≤ −64.5).
  - IP2X: the 4.5 mm slots stop the 12 mm finger, so 80 mm reach cannot touch fins or live parts. **The T&R touch check (TP-G5-15, ≤ 48 °C; Thermal est. 39 °C) moves to the grille.**
- **Low inlet z 643–681 / high outlet z 799–837**, same width, 8 slots 4.5 × 36 → **1296 mm² free each** (≥ 1200; 1976 gross), aligned with the channels.
  - 6 mm solid bars at z 681–687 / 793–799 carry the 4 ribbed PA12 bosses Ø6 × ≥ 5 at y 112/148, z 684/796 (P-154 positions reused), 4× M2.5 A2 per side.
- **Duct insert (PA12 1.2):** side walls at y 130 ± 26.5 → **side gap 5.0 mm** to the outer fin faces (≤ 5), from x −34.5 to −63 (pocket beyond), z 643–837; notched 10 × 7 at the L58 tabs (≥ 3 mm).
- Knee twin housing: bare (low-ε callout removed, rev 4e).
- P-053 layout unchanged (rear 40 × 50 window region is outside z 643–837 / y 104–156: Legs to confirm). L61 cheek windows (incl. the 14 mm boss window) are on the outboard cheek, ≥ 69 mm from the grille edge, on separate faces: no interaction.
- **ROM (≥ 3 mm):** grille and duct are thigh-fixed and inside the r143 30.0 mm swept envelope.

| Check | Min clearance | Result |
|---|---|---|
| Rods (y 130 ± 45) vs duct walls | **11.0 mm** (y separation, all angles) | PASS |
| Rods vs the envelope | ≥ 12.0 mm at knee 140° | PASS |
| Housing (Legs L71) | ≥ 18.1 mm at 145° | PASS |
| Shank keep-outs | ≥ 95 mm | PASS |
| Skin | v5 position, keep-out unchanged | PASS |

- **Mass:**
  - P-156: +0.0028 kg/side → **+0.006 pair [EST]** (duct insert 13 g + liner/fasteners − slots 10 g of PC).
  - P-154 withdrawn: our guard was 0.031 pair (Robot Lab/Thermal −0.041 used T&R's 20.3 g/side; our rev 4b CALC is 15.5 g). The drive-bay window −0.019 stays.
  - **True delta: −0.031 + 0.006 = −0.025 pair vs P-154's +0.012 net → knee venting total −0.013 pair.**
- **Legs to confirm:** skin x −82.5 and the housing front / y extent vs the duct walls ending at x −63; bosses on the bars; P-053 window clear; a CAD ROM recheck with the duct insert.
- **Thermal to confirm:** 65 % / 1296 mm² free with the duct ending at x −63.
- **T&R to confirm:** grille touch (TP-G5-15) and IP2X 12 mm / 80 mm on the grille and inlet/outlet.

### P-156 rev 4d (Thermal ec7b49d): fin-tip baffle chimney + housing-fairing foil
- **Baffle** 1 mm PC, 104 × 52, x −56…−57 (3 mm off the fin tips at −53.0), Al tape (ε ≤ 0.1) on the fin side. It closes the fin channels into a chimney (plate base / duct walls / baffle).
- The grille (65 %, 4.5 mm slots, low-ε inner) now breathes only the ~25.5 mm outside-air space in front of the baffle. Fin tips to grille 29.5 mm.
- **Inlet:** z 643–681 at the skin, 1296 mm² free, into a plenum z 643–688 floored off from the grille space.
- **Outlet:** routed **aft/up**. The chimney rises inside x −34.5…−57 to z 822, then turns aft above the housing (top ~815 [EST]) to the skin opening **z 822–860** (1296 mm² free).
  - That is **30 mm above the grille top edge**; **H ≈ 0.18 m** inlet-to-outlet centres.
- **Optional H 0.20 m: NO.** The opening would need z 881, 4 mm under the thigh-fairing top (885) and under the P-023 hip-skirt hem (blocked at hip extension), off the slim line. H 0.18 gets ~−4 K of the −5 K.
- **Duct insert:** walls y 130 ± 26.5 (side gap 5.0 mm), x −34.5…−57, z 643–860, notched at the L58 tabs (≥ 3 mm).
- **Fairing over the knee twin housing:** 0.05 mm adhesive Al foil on the inner face (~0.03 m², no foil on the housing); slots 4 × (4 × 20) top (z ~820) and bottom (z ~720) on the outboard cheek, 320 mm² each, clear of the A36 housing airflow.
  - Gap: the R-113 bulge gives 8 mm to the front-fin tips (< 10), so a **local bulge +2 mm (12.7 → 14.7)** gives **10 mm** (19 mm to the housing body).
- **Sweep (≥ 3 mm):** rods vs duct 11.0 mm (all angles); outlet passage vs housing top **7 mm [EST]**; housing ROM 18.1 mm (Legs, 145°); shank ≥ 95 → **min 7.0 mm PASS**.
- **Mass:** baffle +7 g, chimney duct +3 g, foil + slots +6 g, bulge +0.5 g per knee → P-156 **0.0193 kg/side, +0.039 pair** (+0.033 vs rev 4b's +0.006). Knee-venting total **+0.020 pair** (P-154 withdrawn −0.031, window −0.019).
- **Legs to confirm:**
  - housing top z (~815) and front x (−66) vs the outlet passage and baffle;
  - D85 front fins present, and the +2 mm bulge;
  - outlet z 822–860 vs the fairing top and the skirt hem;
  - bosses y 112/148, z 684/796;
  - CAD ROM recheck with the chimney.

### P-156 rev 4e (T&R 67e6eed fixes)
- **(1) Outlet shroud.** The outlet slot face is recessed 11 mm (to x −71.5), and the v5 skin swells +6 mm locally over it (1.0 mm PC, cover colour, R20 blend into the thigh line) → **17 mm standoff**.
  - Extent y 96–164, z 815–865. Closed bottom; **open up (1156 mm²) and at both upper sides (1530 mm²) → 2686 mm² ≥ 2592** (2 × 1296).
  - The jet goes up/aft along the rear thigh, away from hand-hold zones; the 50 mm sphere cannot enter.
  - Clears the fairing top 885 by 20 mm and the pelvis underside by 97 mm at hip −105…+40°. **Legs to confirm the P-023 hip-skirt hem stays above z 865 or is slotted.**
  - Mass **+0.015 pair** (vs T&R's ~+0.008; 1.0 mm PC over 6.1 cm² of walls per side).
- **(2) Knee-housing fairing slots:** **5 × 4.0 ± 0.3 × 20** at each end (top z ~820, bottom z ~720, outboard cheek) → ≤ 4.3 mm (≤ 5.0 incl. tolerance), **400 mm² nominal / 370 mm² min** per end (≥ 300).
- **(3)** The low-ε knee housing callout is removed; foil on the fairing inner face only, housing bare. The 0.18 m outlet height is accepted.
- **Sweep min 7.0 mm** (outlet passage vs housing top [EST]); shroud vs pelvis 97; rods 11.0 → PASS.
- **Mass:** P-156 **+0.054 pair [EST]** (+0.015 vs rev 4d); knee-venting total **+0.035 pair**.

### P-156 rev 5 — replan on Legs L72 real geometry (e44c588) + T&R 67e6eed + Thermal 218a541 (supersedes rev 4d/4e routing)
- **Rev 4d/4e fail as drawn** (Legs L72):
  - The knee housing is thigh-fixed at x −176.1…−79.4, y 38–222, z 684.9–805.5. The fins (tips −53) face its front across 26.4 mm.
  - The rear hull (x −135…−181 in the fin z-range) sits **behind** the housing, so a rear grille cannot see the fins. The −82.5 skin plane did not exist.
  - The L60 trunnion top plate (z 816–824, x −175…−40) and the strut cut the chimney. A rear turn over the housing top would be 4.5 mm tall → 234 mm² ≪ 1200: **FAIL**.
  - The rear grille is dropped.
- **Rev 5 route (no mechanism change), cad/covers/thigh_knee_vents_r5.py → thigh_knee_vents.json/.stl:**
  1. **Inlet:** lower rear hull slope z 643–675 (x −94 → −122), y 104–156, 8 × 4.5 × 40 slots → **1440 mm² free**. Plenum z 643–681.9 (3 mm under the housing bottom).
  2. **Chimney:** fins + 1 mm Al-taped baffle at x −56 (3 mm off the tips, 22.4 mm to the housing front); PA12 walls y 130 ± 26.5 (side gap 5.0); L58 tabs notched ≥ 3.
  3. **Transfer duct:** z 793–813 (3 mm under the top plate / strut), x −8.5…−76.4 (3 mm in front of the housing), running **outboard** in y past the housing (222) and the plate edge (228) → section **1358 mm²**.
  4. **Exit:** outboard side skin x −10…−84, z 785–813, below the trunnion plate. 11 recessed 4.5 × 26 slots, 11 mm inboard of the hood skin → **1287 mm² free**.
  5. **Hood** (Thermal 218a541): 1.5 mm PC, Al foil inner ε ≤ 0.05, cover colour, R15 blend. **26 mm standoff** (11 recess + 15 proud). Open up/aft **2652 mm²** (≥ 2600) + dilution slots 4.0 × 16 on the lower edge and sides **1024 mm²** (≥ 600). About 5 g/knee.
- **Height:** inlet → exit centres **H ≈ 0.14 m** (was 0.18): Thermal to re-check.
- **Housing fairing:** foil on the fairing inner face only (housing bare); gap 10 mm to the housing body (no front fins, L72 b); +2 mm bulge kept; slots 5 × 4.0 ± 0.3 × 20 per end (370 mm² min, ≤ 4.3 mm).
- **Clearances vs Legs' real geometry:**

| Item | Clearance (mm) |
|---|---|
| Baffle–fins | 3.0 |
| Baffle–housing | 22.4 |
| Transfer–plate top | 3 |
| Transfer–strut | 3 |
| Transfer–housing front | 3.0 |
| Plenum–housing bottom | 3.0 |
| Rods–duct (Legs) | 13.8 |
| Tibia–skin (Legs) | 4.7 |
| Bosses (Legs, frame moves) | 13.7 / 16.9 — recheck |

  - Hull unchanged, so housing-to-skin is the existing rear opening.
  - Static minimum **3.0 mm (at the gate)**; Legs CAD ROM recheck required.
- **Mass:** P-156 rev 5 **≈ 0.0485 kg/side, 0.097 pair [EST]** (transfer duct 15 g and inlet plenum 9.5 g dominate). Knee-venting total **+0.047 pair** (P-154 withdrawn −0.031, window −0.019); +0.043 vs rev 4e.
- **Compliance verdict:** no-mechanism route found, but only at the 3 mm gates. The exit and hood sit on the **outboard thigh near the hanging-hand zone** (T&R to judge). **Smallest mechanism options** if it is rejected:
  - (a) an L60 top-plate cut-out ~52 × 40 over the chimney → full-height rear/up outlet (Legs structural check);
  - (b) a lower housing top would need ≥ 25 mm to reach 1200 mm² rear: not practical.
- **Legs to confirm:**
  - transfer duct vs femur/clamps/drives outside the plate box;
  - outboard side skin at the exit, with L61 cheek windows and P-053 rear window/pins not overlapped;
  - side skirt hem above z 813 through hip ROM;
  - inlet plenum vs rods/tibia and the boss frame;
  - full CAD ROM.
- **Thermal:** re-run at H 0.14, with the turns, transfer 1358 / exit 1287 / hood 2652 + 1024.
- **T&R:** hood and recessed webs (touch + probe B) on the outboard thigh; housing-fairing slots.

### P-156 rev 5a: outboard hood IP2X fix (T&R 5842853)
- The open top/aft of the hood are **louvred**: 1.0 mm PC blades, **gaps 4.5 ± 0.3 (≤ 4.8 mm, ≤ 5.0 incl. tolerance)**, pitch 5.5, 6 mm deep, angled 30° up/aft.
  - Hood lengthened to 90 mm (x −10…−100), still 26 mm standoff.
  - Louvred faces: top 90 × 26, aft end 28 × 26, and the upper 12 mm band of the outer face (blades up).
- **Free open area 3394 mm²** (4148 gross × 0.818, ≥ 2600); dilution slots 4.0 ± 0.3 × 16 on the lower edge and sides **1024 nominal / 947 min mm²** (≥ 600).
- IP2X: no hood opening > 4.8 mm, so the 12 mm finger (80 mm reach) cannot enter; the exit webs sit 11 mm further inboard.
- Mass: hood 5 → 12.5 g/side (blades + 16 mm length) → P-156 **0.056 kg/side, 0.112 pair [EST]** (+0.015 vs rev 5); knee-venting total **+0.062 pair**.

### Option B (needs a Legs mechanism/structure change): L60 top-plate cut-out
- A **~52 × 40 mm cut-out** in the L60 trunnion bracket top plate (y 104–156, x ~−40…−80, z 816–824) over the chimney lets the fin chimney rise straight through to a rear/up outlet. The rear outlet must vent clear of the P-023 skirt (skirt slotted locally or hem raised: ID/Legs).
- **Legs structural check required:** the plate is a load path to the femur (L60/D60); edge stiffening likely.
- **Est. benefit vs rev 5:**
  - Thermal: H ≈ 0.18–0.20 m, straight path, no 90° turns → about **−4 to −6 K** drive base (Thermal 0.12 → 0.20 trend), with more margin to 80 °C.
  - ID mass: drop the transfer duct (15 g) and side hood (12.5 g), add a riser + rear hood (~10 g) → **≈ −0.035 pair**.
  - Cut 7075 −0.047 kg/side [EST] before any reinforcement (Legs ledger).
  - Removes the outboard exhaust near the hand zone.

## Prone head clearance (T&R 5842853 / fef9348 ask 1) — 2026-10-21
Robot face down on a flat floor, resting on the chest pad (CF face at x ≈ +147 mm, STERNUM_PLATE.md). Head shell (head_shell.stl/.step) frontmost at x = +104.7; torso cover frontmost +110.
- Level body (pad tangent to floor): **head-to-floor gap 42.3 mm** (target ≥10) — PASS.
- Tilted on a second contact (knee front or toe, x 30–150 mm, y 60–760): gap **41.8–78.3 mm**; worst is a toe level with the pad, 41.8 mm. Pad y was taken as ≈1530 mm (sternum land); ±50 mm on that changes the worst case by <3 mm.
- Torso cover front (x 110) sits 37 mm off the floor, so the pad is the only upper-body contact. No cover change needed.

## Rev 5a side hood vs. T&R ask 3 — confirmed, no change
- Dilution: 947 mm² min of 4.0±0.3 slots (≥600, ≤5) — yes.
- Top/aft/upper outer-face openings louvred, gaps ≤4.8 incl. tol (0b3fab9) — yes.
- Foil inner face: already specified as "PC, Al foil inner ε≤0.05" in thigh_knee_vents.json hood.material. Its mass is already inside hood kg_side 0.0125, so the mass is unchanged (pair +0.112).

## P-156 rev 6 — Option B rear outlet (Robot Lab ruling after T&R 7f12ce9; Thermal B2 a32d341; Legs L74 af1b331) — 2026-10-21
Script `cad/covers/thigh_knee_vents_r6.py` → `thigh_knee_vents.json/.stl`. The rev 5 transfer duct and the outboard side exit/hood are **removed**.
- **Route:** lower-rear-hull inlet (unchanged, 1440 mm² free) → fin chimney (baffle x −56/−57, section 21.5 × 52 = 1118 mm²) → rises **straight through the Legs L60 notch x −34.5…−61 × y 104–156, R8 (≈ 1323 mm²)**. That replaces the 52 × 40 cut-out, which Legs found severs the strut; Legs fits twin straps instead. The notch edges form the duct (both parts are thigh-fixed), with foam seals. The stack runs z 827–860 (PA12 1.2) and **ends in a shroud** (Thermal B2, H 0.217 m, 70.6 °C standing).
- **Shroud (rev 4e type):** PC 1.5 with an Al-foil inner face (ε ≤ 0.05), cap 56.5 × 82, 20 mm standoff, top at z 881.5.
  - Openings: 35 slots of 4.5 ± 0.3 × 18 on the aft and side walls; the front wall is closed. Free area 2835 nominal / **2646 min (≥ 2600)**.
  - Dilution: a bottom ring of 12 slots, 4.0 ± 0.3 × 16, 768 nominal / **710 min (≥ 600)**.
  - IP2X: every opening is ≤ 4.8 mm including tolerance, and the stack mouth sits ≥ 20 mm behind them. **No exposed louvre blades.**
- **P-023 skirt:** 0.05 Al foil on the inner face over the outlet, with a **≥ 15 mm gap** to the shroud. Add a local +6 mm bulge if the hip-ROM CAD shows less than 15 mm (Legs CAD check). The hem stays at z 793.4, below the exit.
- **Clearances:** baffle to fins 3.0; baffle to the release-housing front fins 4.0; stack to the plate 3.0 below and 3.0 above; plenum to the housing 3.0. Fin tips are 41 mm from the inlet grille and ≥ 70 mm from the shroud slots (≥ 10). Every P-156 part is thigh-fixed, so the knee ROM is unaffected; the hip ROM matters only against the skirt (15 mm gate). Legs flag (not ID): the housing top sits 2.0 mm under the plate.
- **Mass:** **0.0485 kg/side, 0.097 pair [EST]** (−0.015 vs rev 5a's 0.112). Knee-venting total **+0.047 pair**. The Legs plate/straps change of ≈ −0.029 pair goes in the Legs ledger.
- **PENDING:** the notch needs the Legs FEA, fall case and thermal-break check (L74). Thermal is rechecking whether 1320 mm² of notch area is enough; the 1118 mm² chimney section below the notch is also below the 1200 target, so Thermal should check that too. The shroud and the skirt inner face need TP-G5-15 thermocouples.

## Shin fairing vs D95 ankle plates AN1/AN2 (Legs L74: 3.0 mm, at the gate) — cover-only fix
The drive and PCB outer face is at x 66.5; the shin fairing inner face is at x 69.5. Add a local thermoformed **+2.0 mm front blister** to the shin fairing over z 180–325 (80 mm wide in y, centred y 130, R10 blend). The fairing pushes outward only, so there is no mechanism change. Result: **5.0 mm clearance (target ≥ 4–5)**. Mass ≈ +0.001/side, **+0.002 pair [EST]** (draw only, same material area + 3 %). Legs to re-run the sweep.

## Head clearance for the T-031 full fall gate (≥ 68 mm; T&R R-146 §7) — ID proposal
New baseline: **53.8 mm** (Torso: the 100 mm core puts the pad face out 12 mm, to x ≈ +0.159 torso frame). That leaves a **14.2 mm shortfall**. Torso's own face-out vs. land-recessed head numbers are still pending. In the level prone pose the gap tracks pad-face offset minus head-front offset about 1:1.
- **Option 1, deeper core (recommended):** go from 100 to **116 mm** (+16 mm), with the land and face unchanged. The pad face moves to x ≈ +0.175, giving **69.8 mm** (+1.8 margin). The plateau and peak force are unchanged, and usable stroke goes 70 → 81 mm, so the T-031 57 mm stroke margin improves.
  - Mass: honeycomb 98 × 98 × 16 at 72 kg/m³ is 11 g, plus a longer cartridge sleeve and cover lip at about 4 g, for **+0.015 kg [EST]** (Torso part; Arbiter books it).
  - Fit: the pad (y ±49) stays well inboard of the R-125 W2 carriers (inboard edge about y ±116) and the upper arms, so the roll sweep is unaffected for roll ≥ 0. Arms should confirm there are no adducted or cross-body poses. The pad stands about 65 mm proud of the torso cover front, with an ID trim ring.
- **Option 2, head-shell change:** move the head front from x +104.7 to **≤ +89.5** (−15.2 mm) by flattening the visor front. The shell itself gets about 5 g lighter. But the visor carries the front sensors/cameras, so the change likely moves the sensor window and FOV, which is the head module's call and probably not cover-only. **Not recommended**, except as a hybrid: +8 mm core plus a 7 mm visor flattening.
- **Recommendation:** Option 1, a 116 mm core, **+0.015 kg**, pending Torso's clearance numbers and the Arbiter's mass booking.

### Rev 6 shroud outboard edge check (T&R 2e9b25c passes B2) — confirmed
The cap is 82 wide in y, centred at y 130, and that width already includes the 20 mm standoff walls. That puts the outboard edge at **y 171.0 nominal and y 172.0 max** with ±1.0 thermoform/fit tolerance, so it is **≤ 176: PASS** (5 mm margin). The inboard edge is y 89.0. Second W017 goes on the solid cap top (HANDLING_MAP.md).

## Chest bulge with the 116 mm core (Torso 1585e80) — P-052 rev 2 bezel + tapered fairing, 2026-10-21
- **Stack:** land +0.056, core 116, face 1 mm plus the coat. Pad face sits at **x +0.175** (torso frame = global, with global z = torso z + 1280). Core spans y ±49, global z 1451–1549. The bulge stands **65 mm proud** of the torso cover (x +0.110).
- **Head clearance prone: 69.8 mm ≥ 68 (T-031 full gate) — PASS** (Torso 1585e80).
- **Bezel geometry (rev 2, secondary hold only):**
  - The bezel is a 1.0 mm PC tapered shroud. Front ring opening is 100 × 100 (1 mm round the core). Its front edge is **recessed 2 mm behind the pad face** (x +0.173), so the floor always meets the CF face first; at a 15° tilt the corner offset is 0.3 mm, which the 2 mm recess covers. The foam edge seal sits against the core sidewall and is not bonded.
  - The shroud tapers back to a 150 × 150 base at the cover (x +0.110), a 21° draft.
  - It is held **65 mm in front of its inserts** by **4 PA66 crush posts** (Ø8/Ø4.5 tube, L 63, a 0.8 mm crush-initiator groove at mid-length) at **y ±63, z +0.157/+0.283** (torso). These are outside the core footprint (y ±49, z 0.171–0.269), and the old inserts at y ±40 inside the footprint are deleted.
  - The posts thread onto M4 studs in the land inserts. The bezel fixes with 4 × M4×10 button heads into heat-set inserts at the top of each post (FASTENERS_BOM.json updated: 4 + 4).
- **Crash path:**
  - Each post collapses at its groove at about **0.3 kN** [EST: PA66 net section ~10 mm² × 30 MPa initiation; Euler for the plain tube is 1.18 kN]. All four together give **≈ 1.2 kN, 7 % of the 17.7 kN core plateau onset**, so the posts crush first and can't carry crash load past the core.
  - The bezel only touches anything after the core has crushed more than 2 mm, and by then the cartridge has to be replaced anyway (replace the posts with it).
  - The routine controlled lower (L1) is elastic and never reaches the bezel.
  - Mass: posts **+0.004 kg [EST]**.
- **W2 carrier/pad vs. bezel + fairing** (`cad/covers/r134_bezel_roll.py/.json`, the r133 kinematics, a box envelope x 110–176, y ±75, z 145–295): across the **negative roll range −15…0°** at pitch −150/−90/−30/0/5/30, the minimum is **180.5 mm** (pitch −90, roll −13, carrier W2). That is ≥ 3, a PASS. Torso's 52 mm at roll ≥ 0 is a different measure; mine is larger because I measure to this envelope. Both are far above 3 mm.
- **Look / proportion:** a 65 mm square block on a slim chest reads as a "backpack worn backwards" and breaks the Optimus-like line. **Fix (cover-only):** the tapered 21° bezel/fairing blends the bulge into the cover as a faceted sternum keel. It has 4 mm chamfered vertical edges and an R6 front edge, in the cover colour, with the CF face as a dark inset "visor" that echoes the head. Its visual footprint is 150 × 150 at the cover, about 44 % of the chest width.
  - Fairing mass: 1.0 mm PC, about 34,000 mm² → 0.041 kg, minus the rev 1 sidewall (5.6 g) and blend (7.3 g) → **+0.028 kg net [EST]**.
  - Rev 2 total: **+0.032 kg** (fairing + posts) on top of P-052's 0.040, giving **P-052 = 0.072 kg**. The Arbiter books it.

## P-156 rev 6b: shroud after T&R 925d72e (walk-swing hand hit −65 mm) + Legs L75 ae8b9a4 (plate +4 mm, skirt gate FAIL) — 2026-10-21
- **Plate/straps at z 820–828 (Legs L75).** The lower stack top is now z 817 (3.0 below the plate). The upper transition runs z 831–840 (3.0 above the plate) and moves the mouth inboard to x −76.4…−33.3 × y 100–148 (2069 mm²). **Stack top z 840 (was 860): Thermal 5fd6a54 PASS.** Notch area is unchanged at 1323 (Thermal 26cff58 passed it, 71.1 °C standing).
- **Shroud bounds:** x −100…−20, **y 86–150 (outboard edge 150, ≤ 150 PASS)**, z 840–904. The top slopes from z 861.5 at the front to 904 at the aft. Construction: PC 1.5 (2.0 at the bosses), Al foil inner face, 20 mm standoff over the mouth.
- **Openings on the aft wall only:**
  - A 45° inclined louvre panel, 64 × 62 slant, with 11 horizontal slots 4.5 ± 0.3 × 58. Free area **2871 nominal / 2680 min (≥ 2600)**.
  - A dilution band at z 842–860 with 12 vertical slots 4.0 ± 0.3 × 16: **768 nominal / 710 min (≥ 600)**.
  - All openings are ≤ 4.8 mm. The side, top and front walls are closed.
- **Outboard-top edge:** 40° chamfer with R10 blends, plus a **TPU 90A wear strip** 2.0 × 15 × 80, bonded, with 2 M3 at its ends.
- **100 N hand strike [EST hand calc]:**
  - TPU spreads the load over about 15 × 20 mm → 0.33 MPa, OK.
  - The folded 40° corner acts as an angle beam (legs 20/20 × 1.5 PC, Z ≈ 71 mm³). Over an 80 mm span between mounts, M = PL/4 = 2000 N·mm → **28 MPa vs PC yield 62, SF 2.2**.
  - Mounts are 4 × M3 (2 into stack bosses, 2 into thigh-cover inserts), 50 N shear each. PC bearing is 8.3 MPa at the 2.0 mm boss, SF ≈ 7.
  - TP-G5-15 should add a 100 N strike test.
- **Mass:** shroud 0.0327/side (was 0.0102); upper stack 0.0025 (was 0.0067). P-156 = **0.067/side, 0.134 pair [EST]** (+0.037 vs rev 6). Knee-venting total **+0.084 pair**.
- **P-023 hip skirt rev 6 (`cad/covers/hip_skirt_r6.py/.json/.stl`):**
  - **Method:** Legs' skirt_outlet_l75 pivots, run on a denser grid of 255 poses (hip pitch −107.3…40, roll −20…45, yaw −35/0/45) against the v5 skirt keep-out. Skirt faces within 5.5 mm of the swept stack + shroud are removed, and the rest is thickened 1.5 mm inward as PC.
  - **Gate used: ≥ 3 mm, with the outlet air path left open through the relief** (Robot Lab's alternative to 15 mm, which can't be met with a pelvis-fixed skirt). Worst gap **4.0 mm at pitch −40 / roll 15 / yaw 0**; 12.3 mm at zero pose.
  - **The relief is large:** about 111,000 mm² (≈ 37 % of the skirt), x −143…152, y −15…282, z 793–1013. The thigh sweeps the shroud under most of the skirt band. IP2X: the relief exposes only the shroud's outer face (all its openings ≤ 4.8, ≤ 42 °C) and thigh cover, with no hazardous parts. The remaining inner edge gets a 40 mm Al-foil band.
  - **Mass:** skirt PC removed −0.200 kg, foil band +0.002 → **−0.198 kg [EST]**. The mesh is the full v5 keep-out.
  - **ID note:** a cut this size changes the hip look. The better follow-up is a thigh-fixed rear skirt flap carrying the outlet; to be proposed separately.
  - The STL is a thickened shell; its relief edges are not fully closed (not watertight).

## P-023 rev 7 study — thigh-fixed rear skirt flap carrying the rev 6b shroud (Robot Lab approval of the ID proposal), 2026-10-21: **does NOT meet intent; ruling needed**
Script `cad/covers/hip_skirt_r7.py` → `hip_skirt_r7.json/.stl`; image media/progress/2026-10-21_hip_skirt_r7_study.png.
- **Flap:** PC 1.5 panel hugging the thigh skin (≤ 3 mm offset), 15 mm above the shroud, held by 4 new P-023 inserts on the thigh skin (no mechanism change). It carries the rev 6b shroud unchanged: foil, 20 mm standoff, aft-only 4.5 ± 0.3 louvres (2680 min free, 710 dilution), y ≤ 150, 40°/R10 chamfer with a TPU strip. Mass ≈ +0.022/side [EST: panel 18 g + inserts 4 g].
- **Rules applied over Legs' 255 hip poses:** cut the fixed skirt wherever the flap, stack or shroud passes within 5.5 mm. **Thermal 5fd6a54:** no fixed skirt panel in the jet path, with the jet modelled as the louvre panel extruded 150 mm along its 45° up/aft normal, ±10 mm.
- **Result:**
  - **Cut 59.7 %** of the skirt (178,000 mm²; 58,500 of it is the jet rule alone), against 37 % for rev 6.
  - Worst flap/shroud-to-skirt gap **5.5 mm at pitch −107.3 / roll 45 / yaw −35** (≥ 3 PASS). Jet to the fixed skirt is ≥ 8.3 mm at all poses.
  - **Pinch: FAIL.** The cut-edge gap ranges 5.5–93 mm, and **112 of 255 poses sit in the 5–25 mm finger-trap band** (e.g. every pose at hip pitch −100).
  - Fixed-skirt PC removed −0.321 kg.
- **Why:** the cut is set by the swept volume of a 20 mm-standoff shroud about 100 mm from the hip pitch axis, not by the flap. A flap can't shrink that sweep, and the jet rule adds the jet's sweep on top. A ≤ 5 mm gap or overlapping lip isn't possible around an opening that moves this much.
- **Options for Robot Lab (ID view):**
  - (i) **Split the rear skirt per leg:** the whole rear-lower skirt panel becomes thigh-fixed, and the pelvis-fixed skirt ends at a raised hem, with an overlapping lip (≤ 5 mm) on a short arc near the hip axis where the relative motion is small. This is the Optimus-like look anyway.
  - (ii) Keep rev 6 (37 % cut, 4.0 mm) and add brush/TPU fringe edges against the finger trap.
  - (iii) A hip-pitch ROM keep-out for sit/kneel (Controls) to shrink the sweep.
  - **ID recommends (i).** Rev 7 is not adopted, and HANDLING_MAP zones are unchanged.
- **Thermal note (recorded):** in sit/kneel (hip pitch −40…−107) the jet points up at the pelvis rear cover. Thermal is adding a TP-G5-15 thermocouple there. A 40 mm foil band goes on any skirt edge near the outlet; full skirt foil isn't needed.

## P-023 rev 8 — split rear skirt per leg (Robot Lab ruling, option i), 2026-10-21
Script `cad/covers/hip_skirt_r8.py` → `hip_skirt_r8.json`, `hip_skirt_r8_pelvis.stl` (pelvis-fixed skirt kept), `hip_skirt_r8_thigh_panel.stl`; image media/progress/2026-10-21_hip_skirt_r8.png.
- **Thigh panel per leg (thigh-fixed):** PC 1.5, a cylinder of R 150 about the hip pitch axis, φ 35–60° (rear-lower), y 60–200, held by 4 new P-023 inserts on the thigh skin (no mechanism change). It carries the rev 6b shroud, with the shroud's aft louvre wall forming the panel skin. Thermal 5fd6a54 specs are unchanged: aft-only 4.5 ± 0.3 louvres (2680 min free, 710 dilution), foil, 20 mm standoff, y ≤ 150, 40°/R10 chamfer and TPU strip, stack at z 840.
- **Pelvis hem:** a **spherical hem about the hip yaw/roll intersection (0, 130, 1045), R 152.8**, which gives one clean, symmetric arc per side as the break line (the Optimus-like hip cut).
  - The hem radius is sized so the panel stays **≥ 25 mm** away at every pose. That makes the break a deliberate open gap, never a pinch.
  - The ≤ 5 mm overlap lip near the hip axis **is not used**. A sliding cuff/lip was tried and rejected: its edge gap scissors from 3 to 236 mm over the 147° pitch range, and the jet came 1.4 mm from the cuff.
- **Fixed skirt retained: 44.4 %** (fine-mesh area), so 55.6 % moves onto the thigh panels or is open break.
- **Gate results (255 poses):**
  - Pelvis hem ↔ thigh panel: **min 25.7 mm at pitch 40 / roll −20 / yaw −35, no 5–25 mm gaps. PASS.**
  - Panel ↔ thigh: static (panel on the thigh skin, ≤ 1 mm lip). PASS.
  - Panel ↔ shank: **not modelled** (no shank skin in this model). Legs CAD check needed at knee 145.
  - Jet ↔ fixed skirt: min 27.0 mm. PASS: no fixed panel in the jet. In sit/kneel the jet points at the pelvis rear cover; Thermal's TP-G5-15 thermocouple is recorded.
  - **Panel L ↔ panel R: FAIL in bilateral poses only.** 0 of 255 single-leg poses fail (other leg at zero). 50 symmetric both-leg poses fail: 34 where the thighs themselves collide (infeasible) and **16 cover-caused**: both-leg adduction (roll −20) with flexion ≤ −40, or both-leg yaw 45 (e.g. pitch −100 / roll −20 / yaw 0, gap 0.1).
- **Smallest fix (not ID's to make):** a Controls bilateral keep-out, with no simultaneous both-leg roll < 0 at pitch ≤ −40 and no simultaneous both-leg yaw 45. These postures also bring the thighs within 60–200 mm and are already self-collision-adjacent. The single-leg ROM is untouched. Cover alternative: trim the panels' inboard edge. Inboard edges at y 60 / 70 / 80 were tried and don't remove the bilateral cases.
- **Mass:** panel + lips/inserts + foil band = **0.0245 kg per panel**; fixed-skirt PC removed **−0.299** → net **−0.274 kg**, vs rev 6 (−0.198) **−0.076 kg lighter** [EST, same v5 keep-out basis].
