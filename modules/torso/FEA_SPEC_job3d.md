# FEA SPEC: job 3d ONLY (IR BC + envelope check, LC1 29 kN, 3c-light) (2026-10-21, rev 2)
**Variant written: job 3d ONLY** (Controls 1021e37 closed the 25° case as a FAIL for the soft core). Per Arbiter R-158 (36c75a7), the merged 3d+3e brief needs two conditions, and I grepped the repo for both on 2026-10-21:
- Materials' cited HexWeb crush data for the selected lower grade, with the 1.60 dynamic/lot ratio: **not present**. MATERIALS_DB has HC5052_3.1 and HC5052_4.5 only; no selected 11.2 kN grade, no lot spread, no 1.60 ratio.
- Controls closing the 25° chest-only case: **not present** (no Controls doc).

Files: `fea_job3d.yaml`, plus the shared `fea_job3.py`. The geometry is the **3c-light** config (`fea_job3c.yaml`, from b3811cc rev E). This is heavy, so it goes to the bryan PC (not the box).

## Job 3d (ready)
**Geometry: 3c-light, CAD/config only, not run.**
- Changes from rev E: yoke cheeks t 11 → 8; lower shelf 6 → 4; front side-wall doubler 3 → 2; floor strips 4 → 2.
- The outer wing doubler is kept: the coarse l1 run without it failed the wing/lid corner at 0.64.
- The partition moves to x −78 (Thermal 1ce8963: gap 21 mm behind Thor, gasketed). Deflector riveted or welded. Harness keep-out x < −95, global z 1360–1420.
- **CFRP sternum box: option only [EST].** Materials has no CFRP laminate allowables (MATERIALS_DB "CFRP": laminate properties not verified). Not modelled.

**BC: inertia relief** (T&R TORSO_BC_P160_REVIEW §1; R-158 accepted).
- Lumped masses: head 0.85; arms 7.82 each at shoulder pitch; legs 12.68 each at the hip-yaw interface (RBE3, forces only).
- Model scaled to 72.1 kg. Waist pitch locked.
- CalculiX has no native IR, so use free-free + soft springs (≤ 1e-4 k) with d'Alembert body forces.

**Loads (limit / ultimate ×1.5; fall allowables per T&R b1fe48f; no extra SF):**
- LC1a: 29.0 kN uniform on the 101 × 101 land.
- LC1b: ±25 mm offset.
- LC1c: 25°, 21.2 kN N + 9.9 kN T.
- LC1u: 43.5 kN.
- Plus LC2–LC6 unchanged.

**Envelope check, same run (R-158):**
- (i) Fixed pelvis, with V 9.0 kN + M 2.5 kN·m applied at the waist section (z 69.6) instead of the land load (ultimate 13.5 / 3.75).
- (ii) Full LC1 on the land with the cheeks clamped at the pitch axis: local land/bulkhead/socket at 29 kN.

**Gates:**
- All SF ≥ 1.0.
- Land deflection ≤ 5.5 mm at 29 kN, including the offset case.
- Mode 1 ≥ 80 Hz: first elastic mode in IR; fixed-BC mode 1 also reported.
- Buckling ≥ 1.5.
- Waist-section V ≤ 9.0 kN and M ≤ 2.5 kN·m (limit) from the IR model.
- COM cumulative ≤ 10 mm (booked 6.8 mm).

**Outputs:**
- SFs per part and LC; stiffness; modes 1–6+.
- **CAD mass** (OCC volume × ρ) and mesh mass per part.
- COM shift.
- IR waist-section V and M per LC.
- P-160 stop moment = IR M_y.

**P-160 scaled:** IR envelope **2.5 kN·m limit / 3.75 kN·m ultimate** at LC1 29 kN (was 4.36 / 6.54 under the fixed pelvis). Final value = the job 3d IR M_y. Gear windup / momentary torque check per T&R §2 (Actuators data needed).

**Mass credit: none booked until 3d is done** (R-158). T&R expects −1.0 to −1.4 kg after a waist-path re-size [EST].

## Job 3e / soft pad core: REJECTED (Controls 1021e37)
- Materials b359af8 (CHEST_PAD_CORE.md) offered **HexWeb CR III 5/32-5052-3.8**:
  - 1.276 MPa crush; rate factor ×1.30;
  - plateau 11.7 kN min / 17.4 kN dynamic upper; absorbs 864 J (gate 824 J); core 0.072 kg (−13 g).
  - That would have allowed LC1 17.9 / 26.9 kN.
- **Rejected:** Controls 1021e37 shows a 25° chest-only landing bottoms out that core (101 mm needed vs 81.2 mm stroke), so R-158 item 3 is not met.
- **The design keeps the 4.5 pcf core** (LC1 29 kN). The reduced LC1 is not merged, and no P-160 reduction below the IR value is taken.
- Local chest load = the governing of LC1 (29 kN) and the pad's dynamic upper plateau, so **LC1 governs (conservative).**

## Job 3e: PROVISIONAL (Arbiter R-158c efcede2), `fea_job3e.yaml`
- **Inputs:** IR BC + envelope check (as 3d); pad core **HexWeb CR III 5/32-5052-3.8** (Materials b359af8: 1.276 MPa, ×1.30, 11.7 / 17.4 kN, 864 J); **LC1 17.9 kN limit / 26.9 kN ultimate** (LC1a/b/c scaled ×17.9/29); same 3c-light geometry.
- The local chest load is the governing of LC1 (17.9) and the pad's dynamic upper plateau (17.4), so LC1 governs (conservative).
- **Outputs: identical to 3d,** for a side-by-side comparison: SFs; deflection/k; modes; CAD + mesh mass; COM; IR waist V/M; P-160 = IR M_y (T&R est. 1.55/2.3 kN·m).
- **Status:**
  - **Geometry NOT adopted and NO mass credit** until Controls' forced-25° set (≥ 5 runs, 72.1 kg, second rotation logged) shows **≤ 680 J and no bottoming**.
  - If that fails, **job 3d at 29 kN governs.**
  - 3d is unchanged and runs either way.
- This supersedes the "rejected" note above, which is now provisional under R-158c.

### Job 3e status update: Arbiter R-158d (b81488c), amends R-158c
- **Released:** 3e at LC1 17.9 / 26.9 kN against the **≤ 17° passive envelope**. 25° remains the pad energy check. The **forced-25° set is no longer required.**
- **Adoption + mass credit** only when both are true:
  - (a) second-rotation chest energy × 1.5 ≤ 680 J is logged at 72.1 kg;
  - (b) **TP-G5-21 lot acceptance** is in FEA_SPEC_chest_pad (reference added).
- If either fails, **job 3d at 29 kN governs.**
- **Head-first landings: HIGH. They block G4/G5 sign-off.**
