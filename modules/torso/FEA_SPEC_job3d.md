# FEA SPEC: job 3d (IR BC, LC1 29 kN) + job 3e (reduced LC1), DRAFT/PENDING (2026-10-21)
**Variant written: job 3d alone.** Job 3e is a separate pending draft (below). Per Arbiter R-158 (36c75a7), the merged 3d+3e brief needs two conditions, and I grepped the repo for both on 2026-10-21:
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

## Job 3e: PENDING draft (do not run)
- Energy gate **824 J** (L3 ΔPE 549 × 1.5; R-158).
- Plateau 11.2 kN weakest-corner quasi-static (73.8 mm usable stroke at 10 % margin) → **LC1 17.9 kN limit / 26.9 kN ultimate** (× 1.60), IR BC, same gates.
- P-160: **1.55 / 2.3 kN·m** [EST].
- **Blocked on:**
  - (1) Materials selecting the grade, with a cited crush strength, lot spread and rate factor confirming 1.60. Candidates from the HexWeb CR III catalog (typical crush, 1/8–3/8 cell): 2.6 pcf 5/32 = 90 psi; 3.1 pcf = 130 psi; 3.0 pcf 3/8 = 120 psi. Over the 98 × 98 land: 90 psi → 5.96 kN typ; 130 psi → 8.6 kN typ. This also means the land/core area needs re-checking against the plateau; Materials and T&R to confirm.
  - (2) Controls closing the 25° chest-only L3 case.
