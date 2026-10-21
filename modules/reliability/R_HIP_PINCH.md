# Hip skirt rev 8 (ID df1e9e3) pinch/crush check (T&R, 2026-10-21)
Robot Lab request. Independent re-run: `r_hip_pinch_check.py`, which wraps ID's `hip_skirt_r8.py` geometry with a fixed hem R 152.8 and a finer grid of 2240 poses (pitch every 5°, roll −20…+17.5 incl. −14.5/−12/+15/+17.5, yaw −37.5…+47.5 incl. −17/22). Run on the box, ~40 s.

## Criteria used
- **ISO 13854 minimum gaps to avoid crushing:** finger 25, hand/wrist/fist 100, arm 120, foot 120, leg 180, head 300, body 500 mm.
- **ISO 13857 Table 4 (slots):** e ≤ 4 mm means fingertip entry is negligible at any reach. This justifies a ≤ 4 mm **fixed** gap as "no entry".
- **ISO/TS 15066 Annex A quasi-static contact limits** (applicable by analogy, as ISO 13482 refers to 13854 or force/pressure limiting): hand/fingers 140 N, back of hand 140 N, forearm 160 N; transient 2×.
- **Drive force available:** hip pitch need 334 N·m (CONTRACTS) at r ≈ 150 mm ≈ **2.2 kN**. Even a limp, backdriven leg (~10 kg at ~0.25 m ≈ 25 N·m) gives **≈ 165 N at r 150**, which is over 140 N. Any closing gap below the ISO 13854 values is therefore a real crush, motors on or off.
- **Tolerance stack (RSS):** cover ±1.5, insert placement ±0.5, hem trim ±1, joint zero/encoder ±0.5 → **±2 mm**. Hard-stop overtravel in falls: **+2.5°** (L26 bumper basis).
- **ROM (CONTRACTS §116 / sim v3):** hip yaw −35…45, roll −12…15 (left, + = abduction), pitch −105…40.

## 1. Verification of ID's claims
| claim | ID | T&R independent | verdict |
|---|---|---|---|
| hem ↔ panel ≥ 25.7 mm, never 5–25 | 255 poses, min 25.7 at (40, −20, −35) | **min 24.4 mm in the contract ROM at (40, 0, −17)**, between ID's yaw grid points (4 poses in band). **21.5 mm with +2.5° overtravel** (58 poses in band). With −2 mm tolerance → **≈ 19.5 mm** | **FAIL (finger 25)**: needs ≥ 25 + 2 tol at ROM + overtravel |
| hem gap as a hand hazard | not assessed | the gap opens to **186 mm**; 67 % of ROM poses ≥ 100 mm. A hand enters, then closes to ~22–25 mm under ≥ 165–2200 N | **FAIL (hand 100)** unless force-limited or the hand is prevented from entering |
| panel ↔ thigh ≤ 1 mm, fixed | static, bonded/insert lip | ≤ 1 + 2 tol = 3 ≤ 4 mm and no relative motion → no pinch. Condition: panel flex under a hand push and the shroud load ≤ 1 mm, so the gap stays ≤ 4 under load | **PASS (conditional)** |
| no sliding lip | cuff dropped | confirmed in the script | PASS |
| panel ↔ shank | not modelled | in a deep kneel/sit-back (knee 135 stop, pose B, an R-146 waypoint), the heel/calf folds up behind the thigh toward the rear-lower panel. **Unchecked crush point** | **OPEN**: Legs CAD at knee 135–145 with hip −105…0 |
| L ↔ R panels close (bilateral only) | 16 cover-caused poses, both roll −20 at pitch ≤ −40 or both yaw 45 | **100 bilateral pose pairs inside the contract ROM** (207 with overtravel) fall below 25 mm or to 0 mm. They occur not only at roll −12 (in ROM, not just ID's −20) but at **both yaw ≥ 22 with roll ≤ 0, pitch −100…+35**. Single-leg: 0 (confirmed) | **FAIL**: broader than ID states; a finger/skin pinch with ≥ 165 N available |

**Sweep coverage (task 2):** the hem and panel gaps are functions of the hip joints only, so a joint-space grid does cover kneel, sit, prone and the R-146 lowering as hip states. But ID's grid:
- (i) is coarse in yaw (−35/0/45), so it misses the 24.4 minimum at yaw −17;
- (ii) samples roll at −20/30/45, outside the ROM, and **skips −12/+15** (the real stops);
- (iii) has **no overtravel or fall cases**;
- (iv) has **no tolerance**;
- (v) has **no panel–shank or panel–floor** (sit/kneel/prone body weight on the panel edge) case;
- (vi) is **bilateral only at mirrored poses**, not at asymmetric both-leg combinations (falls, the R-146 kneel with one knee down).

## 2. 0.1 mm both-leg closure: finger or skin pinch, and achievable force
- At rest the inboard panel edges are ~120 mm apart (y ±60), wide enough for a hand (100). They close to 0–0.1 mm, i.e. a full **scissor/crush of hand, finger or skin**. Motors-on force ≈ 2.2 kN; motors-off/limp ≈ 165 N plus the robot's weight in a fall. Both exceed 140 N, so **an achievable injury pinch**.
- The ≤ 4 mm "fixed" route is not available between the L/R panels: they move relative to each other.

## 3. Keep-out spec for Controls (and cover fixes)
**Panel-to-panel (L↔R) and hem-to-panel:** minimum gap **≥ 25 mm + 3 mm (2 tol + 1 model) = ≥ 28 mm** at every instant, computed from both hips' (pitch, roll, yaw) with the ID panel/hem geometry.
- Supervisor thresholds: **warn 35 / limit 30 / trip 28 mm**; at trip, stop the closing joint pair (no both-leg adduction or internal yaw further).
- The **4 mm fixed option applies only to panel↔thigh** (fixed); it cannot apply to moving pairs.
- **Motors-on:** enforced by the supervisor in walk, carry, crouch, kneel, sit and the R-146 lowering (the R-146 kneel must keep both-leg roll > −4 and yaw < 15 [EST from the sweep; Controls to compute the exact boundary]).
- **Motors-off / fall:** the supervisor cannot act, so the cover must be safe by itself (ISO 12100 step 1).
  - **Required cover fixes:**
    - (a) **compliant inboard panel edges and hem edge**: a 25–30 mm closed-cell foam or brush strip with pinch force ≤ 140 N at full closure (e.g. PE foam ≤ 30 kPa at 80 % compression over a 20 mm finger patch ≈ ≤ 15 N) [EST; test];
    - (b) **shrink the hem to R ≈ 146.5** so hem↔panel ≥ 27.5 mm at ROM + overtravel (I re-ran: 21.5 + 6.3);
    - or (c) trim the panel inboard edge to keep L↔R ≥ 28 in limp-leg fall poses. ID found y 60–80 trims insufficient, so (a) is the realistic one.
  - The **hand** (100 mm) case at the hem and between the panels is closed **only by (a) force limiting**, since 100 mm gaps aren't achievable.
- **Prone/kneel/sit:** add panel↔floor and panel↔shank to the sweep. The robot's weight on a panel edge over a hand is a crush; the R-146 prone pose puts the panels facing up (OK), but kneel/sit-back puts them near the heel.

## 4. HANDLING_MAP N7 / H2 review
- **N7: keep, but correct and strengthen.**
  - Its wording "≥ 25 mm open arc" is **false** (24.4 in ROM, 21.5 with overtravel).
  - Signage and no-hold are supplementary measures (ISO 12100 step 3), not the protection. The protection is (a)/(b) plus the Controls keep-out.
  - Extend N7 to the **inner-rear thigh between the panels (L↔R closure)**, as a new N8 or part of N7.
  - Add "keep hands off while the robot is powered **or limp** (a limp leg swings under gravity with ≥ 165 N at the edge)".
- **H2 (fixed rim only): OK in principle, but define a keep-off band.** A grip on the rim curls the fingers down over the hem edge into the break.
  - Restrict H2 to the rim **≥ 100 mm above the hem line** (ISO 13854 hand), or add a moulded hand-hold pocket on the fixed skirt with a closed back.
  - In the rescue lift (legs limp) the legs swing and close the hem gap, so add a "support the thighs (H4 front) before lifting" step.

## 5. Verdicts
| item | verdict |
|---|---|
| hem ↔ panel, finger (25) | **FAIL**: 24.4 in ROM, 21.5 with overtravel, ≈ 19.5 with tolerance. Fix (b) |
| hem ↔ panel, hand (100) | **FAIL** without (a) |
| panel ↔ thigh ≤ 1 mm fixed | **PASS** (≤ 4 mm incl. tolerance and load; verify flex) |
| L ↔ R panels | **FAIL**: 100 in-ROM bilateral poses incl. yaw 22; Controls keep-out ≥ 28 mm motors-on, plus compliant edges for motors-off |
| panel ↔ shank / floor | **OPEN** (not modelled) |
| sweep coverage | **insufficient**: no overtravel/tolerance/falls/asymmetric bilateral; coarse yaw; roll grid misses the stops |
| N7 / H2 | **revise** (wording, N8, H2 keep-off band ≥ 100 mm, limp-leg warning) |

## 6. TP-G5-18 (G5_TEST_PLAN.md)
