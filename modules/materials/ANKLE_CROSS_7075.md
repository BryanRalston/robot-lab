# Job 7 materials inputs: 7075 ankle cross (replaces Ti-6Al-4V), and L63-R fit check
RL Materials, 2026-10-21. Basis: legs/grokbuild/ankle_cross_fea_brief.md (R-069/R-073). [EST] = estimate.

## 1. Temper: specify 7075-T7351 plate, not T6/T651
| | T6/T651 | T73/T7351 | src |
|---|---|---|---|
| YS / UTS MPa | 480 / 560 (repo uses 503 YS) | 410 / 500 | MIF 7075-T6; https://www.makeitfrom.com/material-properties/7075-T73-Aluminum |
| fatigue (MIF, basis unstated) | 160 | 160 | same |
| SCC | susceptible in short-transverse (MATERIALS_DB) | overaged to maximise SCC resistance (MIF text) | same |
| density | 2.81 repo-wide nominal | same alloy | MATERIALS_DB (REPO_AL7075 removed, R-123) |
- **Why:** the cross is a thick, pocketed block. Pin bores and press fits put sustained hoop tension through the short-transverse (ST) grain in a sweaty, salt-exposed foot zone. T6 in ST under sustained press-fit stress is the classic SCC case, so we take T7351.
- **Cost:** yield is −15 %. The FEA limit becomes 410/1.5 = **273 MPa** design/fault, vs 335 in the brief. Bearing becomes ≤ 1.5 × 410/2 = 308 MPa. **Legs: run the FEA at T7351 limits.** If the lightest W/F passes only at T6, re-size; do not drop to T6.
- Fatigue: the same 160 MPa MIF value. Keep the R-031 §6 Se 87 basis and 58 MPa amplitude, since the brief already includes the knock-downs. For local checks at the bores and pocket corners, see §2.

### R-123 update: thick-plate A/B basis
- The cross is machined from plate of about 30 mm, so it falls in the MMPDS 1.001–2.000 in band.
- 7075-T7351 Fty A/B = 57/59 ksi = **393/407 MPa** (Ftu 68/70 ksi). **Unverified:** taken from a web-search synthesis of a third-party stress report quoting MMPDS, not seen in an MMPDS table.
- If A-basis governs (single load path): the static limit is 393/1.5 = **262 MPa**, not 273. Bearing is 1.5 × 393/2 = 295 MPa.
- Legs should use 262 until a verified MMPDS table or a mill cert (AMS-QQ-A-250/12 or AMS 4078) is in hand.

## 2. Fatigue at features [EST, Shigley/Peterson method]
- Machined surface: ka = 4.51·Sut^−0.265 = 4.51·500^−0.265 ≈ **0.87**.
- Pocket corners R2: Kt ≈ 2.0–2.5. With notch sensitivity q ≈ 0.8 (Al, r = 2), **Kf ≈ 1.8–2.2**. FEA peak stress already includes Kt; compare it with Se, not Se/Kf.
- Hard anodize (Type III, 25–50 µm) cuts the fatigue strength of 7xxx alloys by roughly 30–60 % [EST, literature range, no datasheet in repo]. So:
  - **Do not hard-anodize fatigue-critical surfaces** (pocket corners, the rib roots). Use Type II sulfuric 5–10 µm or thin-film sulfuric/boric (TSA) for corrosion only on the general surface.
  - Do not hard-anodize the bores. Use bushes (§3), so the bore stays bare-machined with sealant.
- With anodize on the pocket corners, the 58 MPa amplitude limit becomes ≈ 58 × 0.6 = 35 MPa [EST]. That is a real mass driver, which is another reason to avoid it there.

## 3. Bores, fretting, galvanic
- Steel pins (preferred for wear) against bare 7075 fret at walking amplitude, and steel/Al is a galvanic couple (steel cathodic). Ti pins would be worse: a greater potential gap, plus galling.
- **Spec: pressed DU-type bushes** (PTFE/bronze on steel back, e.g. GGB DU) in all four ø12 pin bores. They are steel-on-steel back to pin, PTFE running layer, and give the wear and fretting isolation.
  - Press with wet-installed sealant (MIL-PRF-81733 class polysulfide, or Loctite 638 if it is a retention fit) to cut the galvanic electrolyte path [EST].
  - Bush wall ~1 mm, so the bore grows ø12 → ø14. Legs: boss OD ≥ ø22 (was ≥ 20) to keep the ligament.
  - Mass about +4 g/leg [EST], which must be in the FEA mass.
- If the pitch stubs are integral 7075, they run in the fork bearings directly and give Al wear. **Not acceptable**; use pressed steel stubs.
- Thrust faces: Type II anodize plus PTFE washers, as in the brief.
- Hardened pins: 42CrMo4 Q&T or 17-4PH H1025 (better corrosion behaviour in a sweaty foot) [EST].

## 4. Verdict, job 7
**GO with 7075-T7351 + DU bushes + Type II/TSA anodize, no hard anodize on fatigue zones.** FEA limits are 273 MPa static/fault and bearing 308 MPa, with 58 MPa amplitude on un-anodized machined surfaces.
- Expected saving: −0.084 robot (hand model) minus ~0.008 for bushes, so about **−0.076 kg [EST]**. Possibly less if the T7351 yield forces W/F up a step (W5/F5 → W6/F6).
- The stop rule stands: if no candidate passes at W6/F6, keep Ti.

## 5. L63-R bonded pins: H7/m6 on ø7 (ISO 286-2, 6–10 mm band)
- IT7 = 15 µm, IT6 = 9 µm. H: EI = 0. m: ei = +6 µm.
- **H7 = 0/+15, m6 = +6/+15.**
- Max interference = 15 − 0 = **0.015 mm**. Max clearance = 15 − 6 = **0.009 mm** (transition fit).
- Legs' +0.015 mm hoop case is the correct worst case. Confirmed.
- Note: with Loctite 638/648 the clearance case is filled by adhesive, so no slop either way.
