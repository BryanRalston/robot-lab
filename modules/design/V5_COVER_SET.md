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
- Inputs: Actuators D91 plate + Thermal rev 4 (44b7c36): 100 × 48 window, **8 fins 18 mm**; PC guard with ≥ 10 mm air above the fin tips, ≥ 60 % open face, open at both ends, low-ε inner face. **Envelope 29.5 mm beyond the L51 box** (guard outer face x −64.0, thigh frame).
- Placement (no assembly CAD; from Legs L51/L58): plate face x −34.5, y 130 ± 24, z 690–790; knee axis (0, 500); RV12 rods trunnion (−130, 770) → lever eye r 47.5 [EST]; Legs shank keep-outs.
- **Sweep, 1° steps, gate ≥ 3 mm.** The plain 29.5 mm box **fails**: the rods come to 2.5 mm at knee 132–145°. **Fix:** a 45° × 8 mm chamfer on the guard's lower outer edge (z 690), with the fin lower ends tapered 45° × 8 mm under it so the 10 mm standoff holds there. With the fix:

| Check | Min clearance | Where / angle | Result |
|---|---|---|---|
| RV12 rods vs guard | **7.8 mm** | knee **141°** [EST] | PASS |
| Shin / boot keep-outs | 92 mm | knee 0–145° | PASS |
| Housing front fin tips | 14.5 mm | static | PASS |
| Pelvis underside | 180 mm | hip −105…+40° | PASS |
| Seated | 133 mm | hip 90° | PASS |

- **Guard (P-154 rev 4):**
  - PC 1.5 mm thermoformed; fin tip to inner face **10 mm**. Face slots 4.0 mm at 5.5 pitch × 96 → **64 % open**; total **46.4 cm²** (30.7 face + 15.7 sides, ≥ 25); both z ends open. IP2X: the 12 mm finger cannot enter.
  - **Inner face:** vapour-deposited Al or 25 µm Al foil PSA, ε ≤ 0.1. **Outer face:** cover colour, matte 2K, 20 µm.
  - 4× M2.5 A2 captive per side (unchanged).
- **Mass:** guard 0.0151 kg/side (incl. liner, paint, fasteners) → 0.030 pair; window −0.019 → **net +0.011 pair [EST], i.e. −0.009 vs the +0.020 booked.** The fin growth (+10.8 g/knee) is Actuators' line.
- **Actuators to confirm:** fins 18 mm with plate face x −34.5; the fin lower-end 45° × 8 taper (Thermal UA effect); edge seal vs the guard flange stack.
- **Legs to confirm:** plate placement (y 130 ± 24, z 690–790); lever eye r 47.5 and rod path (the 7.8 mm is [EST]); 4× M2.5 window-frame inserts; fall/side impact with a sacrificial guard and the bay kept closed (R-143 2c).
