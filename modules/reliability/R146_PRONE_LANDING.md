# R-146 chest-pad prone-landing load case (T&R, 2026-10-21)
Ruling: R-146(b) (21d1738). The kneel-to-prone end state lands on the chest pad, so the prone-landing load comes to Test. Script: `r146_prone.py` → `r146_prone.json` (hand calcs; box-light; no FEA run).

## 0. Correction to the brief
The chest pad is **not EPP**. It is a pre-crushed **HexWeb CR III 5052 4.5 pcf honeycomb cartridge**: 98×98 face, 88 mm core, plateau 17.7–22.3 kN at 0° and 16.6–20.8 kN at 15°, ceiling 22.35 kN, 62 mm usable stroke, single-use once crushing starts (>2 mm crush means replace). Sources: torso/T031_chest_contact_r2.md, materials/T031_CHEST_CRUSH.md, R-079/R-084/R-102/R-103. The R-042 basis (Parts 3–6) is the same honeycomb data. No EPP chest part exists, so all checks below use the honeycomb.

## 1. Inputs (repo)
| item | value | source |
|---|---|---|
| mass | 68.42 kg credible | R-146 §3 |
| CoM standing | 0.943 m | legs walk zc / sim v3 |
| CoM prone (pose F) | 0.125 m | controls/limits/kneel_hold_results.json |
| CoM upright kneel | 0.50 m **[EST]**: standing minus the shank drop (0.42 + foot). No measured value exists | sim/v3 chain |
| pad centre height, upright kneel | 1.05 m (pad +0.22 on torso, chain 0.58 above hip pitch; thigh 0.42) | sim/v3 humanoid_v3.xml |
| D94 interlock | CoM speed <0.1 m/s, contact and supported, held 50 ms | R-146(b), DRIVE_DERATE.md |
| bulkhead | 7075-T651 3.0 in plate, single path, allowable 257 MPa; rib hand calc 216 MPa at 24.4 kN | FEA_SPEC_torso_pocketing, T031_CHEST_CRUSH |
| backing | CF/Al-honeycomb sandwich, k ≈ 24 MN/m, sized at 33.5 kN | T031_chest_contact_r2 |
| pack | 8.75 kg, 20S5P P45B, rails → shell flange → waist ring; cells kept unloaded, gap ≥5 mm | torso/R1_ARCHITECTURE.md |

## 2. Load cases and results
| case | energy | chest load | pad | verdict |
|---|---|---|---|---|
| **L1: controlled lower (R-146b)**, contact at ≤0.1 m/s | KE 0.34 J (whole body at 0.1 m/s) | static 0.34–0.47 kN (50–70 % of mg on the pad **[EST]**, contact forces not logged) + elastic dynamic 3.1 kN (backing k, m_eff 40 kg) → **≤3.6 kN** | elastic; the elastic capacity below crush onset is 6.5 J ≫ 0.34 J. **No crush**; SF 4.9 vs 17.7 kN | **PASS (hand calc)**: routine, non-consumable |
| **L2: uncontrolled tip from upright kneel** (MO=0 / interlock miss, rigid rotation about the knees) | ΔPE 252 J; pad speed ≈5.4 m/s (m_eff 17.5 kg at the pad) | crushes at the plateau, ≤22.35 kN | stroke 11–15 mm of 62 mm (≥4× margin). **Cartridge consumed** | energy/pad **PASS**; torso g **OPEN** (below) |
| **L3: uncontrolled tip from standing** (HOLD_DERATED → trip → TUCK fails, rigid forward fall) | ΔPE 549 J ≤ the T-031 gate of 1.03 kJ | ≤22.35 kN | stroke 25–33 mm of 62 | **covered by T-031** (same gate; Controls' T-031 sim governs) |

**Torso structure at the 22.35 kN ceiling** (L2/L3): bulkhead rib 216 × 22.35/24.4 = **198 MPa ≤ 257** single-path (SF 1.30 static). Backing is sized to 33.5 kN; LC1 in FEA_SPEC_torso_pocketing (33.5 kN) envelopes it. PASS on hand calc, **pending the converged LC1 FEA** (quadratic elements, R2 rules). The job3b result on file is COARSE only.

**Torso g and battery (L2), the open risk:** the T-031 38 g basis treats the body as a free mass. In a tip from kneeling the trunk rotates about the knee contacts. Pinned at the knees, the pad ceiling gives α = F·r/I, i.e. **≈104 g at the pack (r ≈ 0.8 m)**. Free-body it is 38 g. Pack inertial load is therefore 3.3 kN (free) to **8.9 kN (pinned)** into the rails. The real value lies between the bounds (knee slip and hand contact reduce it). No pack/rail shock allowable or cell shock rating is on file. UN 38.3 T.4 (≈150 g small cell / 50 g large cell [uncertain, not fetched]) is the only external reference.

## 3. Verdicts
- **L1 controlled lowering: PASS**, with conditions: the D94 speed gate is enforced at pad contact (not only at CoM settle), and pad force stays elastic (≤8.8 kN = 0.5 × the plateau floor). A routine safe-sit must never consume the cartridge.
- **L2 tip from kneel: CONDITIONAL.** Pad and bulkhead pass. **Torso/pack acceleration is unproven** (38–104 g bracket) until Controls' sim and TP-G5-16 measure it. If the pack exceeds its rating: soften the pad (lower plateau, thicker core) for this case or keep the arms in a hands-first catch.
- **L3 tip from standing:** no new requirement; T-031 governs. Log it against the fall budget per R-146(a).
- Every L2/L3 event is a fall event: inspect the cartridge, replace it if crushed >2 mm, and run a pack post-event check (OCV/isolation/visual).

## 4. Pass criteria (for G4/G5)
1. L1: peak pad force ≤8.8 kN, no permanent crush (>0.5 mm face indentation means fail), contact speed ≤0.1 m/s over ≥95 % of DR runs and ≤0.2 m/s worst case.
2. L2: crush ≤50 mm (stroke margin ≥10 %), peak force ≤22.35 kN, pack-rail accel ≤ the pack rating (TBD; provisionally ≤50 g), no cell displacement into the ≥5 mm gap, BMS no fault and isolation unchanged.
3. Structure: no yield/crack in the bulkhead, land, rib or backing; LC1 FEA SF ≥1.0 on 257 at 33.5 kN.

## 5. TP-G5-16 (added to G5_TEST_PLAN.md)
See G5_TEST_PLAN.md TP-G5-16: (a) a controlled lower ×20 on load-plate floor; (b) a tip from upright kneel ×3 (new cartridge each) with a pack-rail triaxial accelerometer (≥10 kHz) and pad crush measurement; (c) pack post-check.
## 6. Missing inputs (not invented)
- Measured upright-kneel CoM height and the actual pre-tip pose (Controls; the kneel is not yet achieved in sim, DRIVE_DERATE.md).
- Prone contact-force split chest/hands/feet (Controls: log contact forces in kneel_hold / the R-146b sim).
- Pad contact speed (not just CoM speed) at landing across DR (Controls).
- Pack and rail shock allowable, cell shock rating, mount design (Torso & Power).
- Converged LC1 FEA (Torso; heavy, bryan PC).
- Rotational torso g in the tip from kneel (Controls sim with the plateau pad model, `--chest-k` not linear).
- Head/face clearance in prone (ID): pose F shows no head contact, but no clearance number exists.
- Rescue/handling map for the prone state (HANDLING-MAP gap, R-143 rev 4e).

## 7. Update 2026-10-21 ~09:20 ET: Torso c974f54 (pack shock), Robot Lab ruling (100 mm core + rail stop), ID fd981f1 (head clearance)
**Pack shock (Torso R146_pack_shock.md):**
- P45B cell: 150 g / 6 ms. Pack UN 38.3 T4 level: 107.4 g / 6 ms, Δv 4.0 m/s.
- My pinned bound of 104 g is within the T4 level by only 3 %, and **a test level is not a design limit**.
- The fall pulse is 7–23 ms with Δv up to 5.67 m/s, so **T4 does not envelope it**.
- Rails: 272/320 MPa (85 %, [EST] section).
- Torso's screen model gives the kneel tip at 59–85 g.
- **Note:** with the dynamic factor 1.10–1.30 on the plateau (as in Torso's calibration), the pinned bound rises to 104 × 29.0/22.35 ≈ **135 g**. The demand band is therefore 38–135 g, with the screen model at 59–85 g. Only the drop test closes this.

**100 mm core recheck (plateau unchanged, so peak force and g unchanged; only the stroke grows):**
| | 88 mm | **100 mm** |
|---|---|---|
| usable stroke (0.70 t) | 62 mm | **70 mm** (75 at densification ε 0.75) |
| L2 kneel tip 252 J, lot 19.5 kN 0° … 18.1 kN 15° | 13–14 mm | **13–14 mm → margin 5×** |
| L3 standing tip 549 J | 28–30 mm | **28–30 mm of 70** |
| T-031 gate 1.03 kJ at 18.1 kN | 57 mm (8 % margin) | **57 mm of 70 (≥ 10 % margin restored)** |
| peak force / pack g | ≤ 22.35 kN quasi-static (29 kN dynamic) | unchanged |
- The rail stop shoulder closes Torso's latch OPEN item (13.4 kN axial) provided it is sized to 13.4 kN. Torso to show the calc.

**Head clearance (ID fd981f1: 42.3 mm level, 41.8 mm minimum tilted; ID's target was ≥ 10).** The value needed is crush stroke + elastic (≈ 1 mm) + 10 mm margin:
- L1 controlled lower: no crush → need 11 → **PASS** (41.8).
- L2 kneel tip: 14 + 11 = 25 → **PASS** (16.8 mm spare).
- L3 standing tip: 30 + 11 = 41 → **marginal PASS** (0.8 mm spare at the 41.8 minimum).
- T-031 full gate (57 mm stroke): 68 mm needed → **FAIL**. In a full-energy forward fall the head shell (N3, fragile) touches the floor at about 41 mm of crush, before the pad has absorbed the gate energy.
- **Open:** does the 100 mm core push the pad face out 12 mm (gap → 54.3/53.8, then L3 PASS with 13 mm spare; gate still needs 68) or is it recessed into the land (gap unchanged)? ID/Torso to state. Target: head ≥ 68 mm behind the pad plane, or accept a head-shell floor touch only beyond L3 energy.

**Verdicts now:** L1 PASS. **L2 CONDITIONAL until TP-G5-17 passes** (pad/stroke/bulkhead PASS, head PASS). L3 = T-031, head marginal. T-031 gate head clearance FAIL / open to ID.

## 8. TP-G5-17 pack drop test: see G5_TEST_PLAN.md

## 9. Update ~09:25 ET: Controls fc86721 sim data [EST] + HANDLING_MAP e6dd4b0 rescue procedure
Recompute script: `r146_fc86721.json`. Inputs: kneel CoG 0.674 m (was my 0.50 EST), standing CoG 0.91 m (Controls), prone split chest 64 % (46–64 % DR), knees 27.5, feet 4.7, hands 3.9. Settle 0.30 m/s / 1.74 kN. Kneel tip: 13.3 kN, 43–44 g raw / 24 g 60 Hz MA.

| quantity | old | **new** |
|---|---|---|
| L2 kneel tip energy | 252 J | **368 J** (68.42 × 9.81 × 0.549) |
| L2 crush, 100 mm core (19.5 kN 0° … 18.1 kN 15°) | 13–14 mm | **18.9–20.4 mm of 70 (3.4×)** |
| L2 pad speed / pack Δv (m_eff 28.8 kg, knee pivot) | 5.4 | **5.1 m/s / 4.0 m/s** |
| L2 pack g: free / pinned at 22.35 kN / pinned at dynamic 29 kN | 38 / 104 / 135 | **38 / 63 / 82 g**; sim 44 raw, 24 filtered |
| rail load (8.75 kg) | 3.3–8.9 kN | **2.1 (24 g) … 3.8 (44 g) … 7.1 kN (82 g)** → 216 MPa ≤ 320 PASS |
| L3 standing tip energy / crush | 549 J / 28–30 | **527 J / 27–29 mm of 70** |
| prone static chest load | 0.34–0.47 kN EST | **412 N (DR 46–64 % → 0.31–0.43 kN)** |
- The higher kneel CoG raises the **energy** but lowers the pinned g, because the larger I about the knee gives the same pad ceiling a smaller angular deceleration.
- **The sim's 13.3 kN is not conservative.** MuJoCo's soft default contact has no crushable model. The real cartridge is elastic only up to ~6.5 J before the plateau onset (17.7–19.5 kN), and 368 J ≫ 6.5 J, so the real pad **crushes at the plateau (19.5–22.3 kN quasi-static, up to 29 kN dynamic)**. Use the plateau for structure and pack, and the sim only for kinematics.

**Head clearance (fd981f1, 41.8 mm minimum; need crush + 1 + 10):**
- L1: 11 → PASS.
- **L2: 31.4 → PASS (10.4 mm spare).**
- **L3: 40.1 → marginal PASS (1.7 mm spare).**
- T-031 full gate 68 → FAIL (open to ID/Torso, unchanged).

### Verdicts (updated)
- **L1 controlled lower: CONDITIONAL.**
  - Structure PASS: 1.74 kN ≪ 17.7 kN crush onset. The whole-body KE at 0.30 m/s is 3.1 J < 6.5 J elastic capacity, so it **stays elastic and the cartridge is not consumed**. It is 5× under the 8.8 kN routine limit.
  - **D94 interlock FAIL** (0.30 vs 0.10 m/s) with the PD stand-in; the WBC arm-supported lower is pending.
  - Structural no-crush speed ≈ 0.5 m/s [EST, m_eff 40 kg on the 6.5 J elastic cap]. Keep **0.10 m/s as the gate**: it is a controls/interlock requirement, and 5× margin is needed against unconverged contact.
  - Closes when the WBC shows ≤ 0.10 m/s over DR **and** TP-G5-16(a) measures ≤ 8.8 kN with no indentation.
- **L2 tip from kneel: CONDITIONAL** (unchanged status). Stroke, bulkhead, rails and head PASS. Pack demand 24–82 g at Δv ≈ 4.0 m/s sits under TP-G5-17's 104 g / 20 ms / 5.7 m/s, but the pulse is outside the qualification until **TP-G5-17 passes**.
- **L3 tip from standing: PASS on stroke (29/70), rails and bulkhead; head marginal (1.7 mm).** T-031 governs; it is a fall event.

### Filtered vs raw g, and what it means for TP-G5-17
- The sim's 44 g is a raw finite difference of the torso COM velocity. The 24 g is a 60 Hz moving average (16.7 ms window). For a 7–20 ms pulse that window cuts the peak by ~40 %, so the two numbers are the same event seen through different filters. **Neither is a pack spec.**
- **Do not size or pass TP-G5-17 on the 24 g filtered number.** The test is specified by table control (half-sine peak + duration + Δv), which envelopes the event:
  - 104 g ≥ the 82 g pinned/dynamic bound (≥ 2.4× the raw sim);
  - 20 ms ≥ the 7–23 ms band midpoint;
  - **5.7 m/s ≥ 4.0 m/s pack Δv**.
- Measure control and response at **SAE J211 CFC 1000** (raw) and also report the 60 Hz MA, so the sim can be correlated filter-for-filter. Compare at least on Δv and on the shock response spectrum, not only on the peak.
- Controls should report their sim pack-rail g at CFC 1000-equivalent and the Δv.

### Prone rescue procedure review (HANDLING_MAP e6dd4b0): ACCEPT WITH CHANGES
Good points: lock-out before approach, remote E-stop for a crouched HOLD_DERATED robot (it will collapse), no brakes stated, H1/H2 only, never by a limb, explicit re-enable.

Required changes (Controls/ID to edit the map):
1. **Battery first (missing).** After any tip/TUCK/fall, check the pack **before** approaching and before step 3: smoke, hissing, sweet/solvent odour, swelling, BMS cell temperature rising. If any of these, evacuate, keep clear, and don't roll or lift it (thermal runaway risk). Use a pack thermal camera reading if available.
2. **Step 2 cool-down:**
   - Re-point it from "rev 4e" to the chosen **B2 rear outlet** zone (N1 moves aft/up; prone puts the rear outlet **facing up**, right where rescuers lean over). Use the TP-G5-15 measured time to ≤ 43 °C.
   - Until published, **EN 407 contact-heat level ≥ 1 (100 °C) gloves** for an urgent move.
   - Drives latch at 82 °C, so the knee housing and drive band are hot too, not just N1.
3. **Lift load:** 68.4 kg with two carriers is ≈ 34 kg each, above the NIOSH 23 kg reference. Make **three people minimum or a board/strap lift aid** mandatory (step 5 implies but does not require it).
4. **Backdriving pinch in the roll:** in the log roll the knee (90° prone) and hip backdrive freely. Hands must stay off the thigh–shank gap (pinch), not just N5. Add a knee strap or a rule to keep the legs straightened before the roll.
5. **Cartridge replacement** (step 6 says only "inspect"; specify it):
   - **replace** after any L2/L3/TUCK event regardless of appearance, or if indentation > 2 mm (crush) / > 0.5 mm face mark (L1 gate), or if the tap test fails
   - lot-certified cartridge in the 19.5–22.3 kN band, **100 mm core** (Robot Lab ruling)
   - bezel 4 × M4 captive at spec torque
   - inspect the land, backing and bulkhead; dye-penetrant after any L3/T-031-level event
   - record the cartridge lot and the event in the fall log
   - the pad is underneath when prone, so inspection needs the supine roll or a lift on a board
6. **Re-enable gate, add:** pack OCV/group voltages, isolation and BMS log unchanged (TP-G5-17 criteria) after any L2/L3 event; chest cartridge replaced; R-146 fall-budget entry.
7. Step 1: a robot mid-way through the R-146b sequence may still move. Wait for MO_OFF **plus 5 s** with no motion before approach, even with the remote E-stop pressed.
