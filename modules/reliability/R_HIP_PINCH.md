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

## Rev 8b re-check (ID acb9bd5), 2026-10-21 ~10:00 ET
Script `r_hip_pinch_check_8b.py`: ID's geometry with hem R 144 and the panel trimmed to y 86 + a 40 mm inboard-rear chamfer, on my 2240-pose grid. L/R check: 6000 random **asymmetric** both-leg pairs over the **full ROM + overtravel** (pitch −107.5…42.5, roll −14.5…17.5, yaw −37.5…47.5), excluding thigh-thigh collisions.

### 1. Claims
| claim | T&R | verdict |
|---|---|---|
| hem R 144: 32.6 in ROM, 28.3 with overtravel, 26.3 with tolerance, 0 in 5–25 | **32.6 (40, −8, −35) / 28.3 (42.5, 0, −17)**, 0 in band; −2 tol → 26.3 ≥ 25 | **PASS** (1.3 mm margin at the worst combined case). Max gap now 203 mm (N7 says 186; update) |
| y 86 + chamfer: −83 % contact poses, worst 0.1 | ID's asym sweep covered **pitch −10…45 only** (no flexion). Over the full ROM mine gives **1/6000 pairs < 3 mm, 4/6000 < 28 mm, worst 0.77 mm** at both legs extended (+23/+40) with yaw 38/46. **None with a leg flexed beyond −10°**, so the deep-flexion closures of rev 8 are gone | **PASS as stated** (rare, extension + high-yaw only). Closure still exists, so the **Controls ≥ 28 mm keep-out stays mandatory** (warn 35 / limit 30 / trip 28, measured rigid edge to rigid edge, **excluding foam**) |
| foam ≈ 24 N fingertip / ≈ 120 N hand at full closure | see §2: **the stress basis is wrong**; the force is set by the drive, not the foam | **CONDITIONAL / marginal FAIL** (hand, limp) |

### 2. Foam force check (closed-cell PE, 30 kg/m³)
- **Typical compressive stress for LDPE foam at ~30–35 kg/m³** (e.g. Ethafoam 220-class datasheets, [uncertain, not fetched for this exact grade]): ≈ 45–50 kPa at 10 %, 55–70 at 25 %, 100–130 at 50 %, and **≈ 300–500 kPa at 75–80 %** (densification onset).
- **ID's "60 kPa at 80 %" is roughly the 25 % value. At 80 % the stress is ~5–8× higher.**
- **Full closure (80 % strain), if forced:** finger patch 20 × 20 → 120–200 N; hand 100 × 20 → 600–1000 N. So the foam alone does **not** keep 140 N at full closure. It is a contact softener, not a force limiter.
- **What actually sets the force** is the closing drive. The foam only spreads it:
  - **Powered (≈ 2.2 kN):** the foam bottoms (2.2 kN / 0.002 m² ≈ 1.1 MPa ≫ densification), and the rigid edge comes through. **Only the keep-out protects** (agreed with the brief).
  - **Limp (≈ 165 N, leg weight moment ≈ 25 N·m / r 0.15 [EST]):**
    - **Finger (≈ 15 mm thick)** in 28 mm foam: ~54 % strain → ~110–130 kPa × 4 cm² ≈ **45–52 N ≤ 140 PASS** (ID's 24 N is low but the conclusion holds). The foam doesn't bottom; residual ≥ 13 mm.
    - **Hand (≈ 25–30 mm thick)** in a 28 mm foam strip: ≈ 90–100 % strain, so the foam **bottoms** and the hand sees the full limp drive, **≈ 165 N vs 140 N quasi-static: marginal FAIL (+18 %)**. Transient 165 ≤ 280 PASS. Pressure 165 N / 20 cm² ≈ 8 N/cm², far under the Annex A hand limits (PASS).
    - With foam on **both** closing edges (L↔R panels: 2 × 28 = 56 mm) the hand is at ~50 % per strip, so no bottoming. The force is still the drive's 165 N at equilibrium (the foam can't reduce a static gravity load), so it is the same marginal result.
  - **Fix options (any one):**
    - (i) **measure the real limp clamping force** (TP-G5-18). If ≤ 140 N it passes; 165 N is my estimate from a ~10 kg leg at 0.25 m;
    - (ii) **a rigid 30 mm standoff bump** at the panel/hem edge ends, so that limp closure can't drop below a hand-crush-limited gap (combined with the foam);
    - (iii) a **40 mm deep foam** so the hand doesn't bottom (doesn't change the static force but removes the rigid-edge contact).
  - **Recommend (i) + (iii)**, and accept transient-only contact if (i) shows ≤ 140 N.

### 3. Foam durability and geometry
- **Compression set:** closed-cell LDPE at 30 kg/m³ is ~10–20 % after 25 % / 22 h (ASTM D3575-type data [uncertain]). It is much worse after repeated 50–80 % strains. Cross-linked PE (XLPE) is better (~5–10 %). **Specify XLPE** and a residual thickness ≥ 25 mm (≤ 10 % loss) as the replace criterion.
- **Heat:** LDPE softens about 70–80 °C. **The hem edge is in the B2 rear-outlet plume path in sit/kneel** (Thermal: the jet points at the pelvis rear cover, 58–84 °C). **Specify XLPE rated ≥ 90 °C** in that ±100 mm sector, or keep the foam out of the jet (TP-G5-15 thermocouple on the foam).
- **UV:** black-skinned PE with carbon black is OK indoors. Outdoors, expect embrittlement and chalking in 1–2 years.
- **Tear/abrasion:** PE foam tear strength is low (~1–3 N/mm). Edges rub on clothing and on each other in closure. Skinned face, J-channel lip covering the foam corner, no exposed cut edges.
- **Replacement interval:** inspect at each service (monthly) and after any pinch/fall/rescue. Replace if thickness loss > 10 %, there are cuts or tears, there is heat glazing, or **annually** regardless [EST until TP-G5-18 ageing]. The J-channel design is replaceable: good.
- **Geometry:** the keep-out gap is defined **rigid edge to rigid edge (panel/J-channel PC), not foam surface**. The foam is allowed to fill the 28 mm gap (no open finger gap at the hem's closest poses, which is ID's point). It must not add rigid thickness: J-channel ≤ 1 mm, and it **reduces the rigid gap by ≤ 2 mm** → recheck hem 28.3 − 2 = 26.3 (tolerance already included; J-channel thickness was not). **Hem with the J-channel: ≈ 25.3–26.3 mm, still ≥ 25 PASS (thin)**. ID should confirm whether the 1 mm channel was in its numbers.

### 4. HANDLING_MAP (acb9bd5)
- **N7 reworded: OK** (pose-dependent, crushing force stated, powered or limp). Change "up to 186" → **203 mm (R 144)**. Change "the foam edges are the protection" → **"the Controls keep-out (powered) and the foam edges (limp, finger) are the protection"**: the foam doesn't protect a hand against the powered drive.
- **N8 added: OK.**
- **H2 ≥ 100 mm above the hem: OK** (ISO 13854 hand). ID to mark the line on the cover (moulded rib or a texture change) so it is visible.
- **Rescue step 5 (support the thighs first): OK.** It removes the limp-swing closure during the lift.
- **Panel ↔ shank (knee 135–145, deep kneel/sit-back) and panel ↔ floor: STILL OPEN** (Legs CAD). Panel flex ≤ 1 mm under a hand push: open (TP-G5-18).

### Verdicts rev 8b
| item | verdict |
|---|---|
| hem ↔ panel (finger 25) | **PASS** (26.3 with tolerance; ~25.3 if the J-channel isn't included: confirm) |
| L ↔ R panels | **PASS with Controls keep-out** (rare residual closures, worst 0.77 mm at extension + yaw) |
| foam, finger, limp | **PASS** (45–52 N) |
| foam, hand, limp | **marginal FAIL / CONDITIONAL** (≈ 165 N vs 140): measure; 40 mm foam or a standoff |
| foam, powered | not protective; **keep-out mandatory** |
| foam durability | **CONDITIONAL**: XLPE ≥ 90 °C near the plume, ≤ 10 % thickness loss criterion, annual/after-event replacement |
| N7/N8/H2/rescue | **ACCEPT** with 2 wording fixes |
| panel ↔ shank / floor | **OPEN** |
