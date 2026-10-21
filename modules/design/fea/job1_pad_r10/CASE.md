# Job 8 add-on (route via Robot Lab, bryan PC) — shoulder pad R10 per R-120 (12f68a4)
Supersedes the earlier R10 case (Z −64, CRBH 6013), which must NOT run. One Grok Build session at a time.
Reuse fea/job1_pad_r8/fea_job1.py and all six BRIEF gates, with:
- Geometry: Arms 7075 stand-off replacing the boss (layout modules/design/pad_r10_standoff.json; Arms to finalize). **Pad centre Z = −20 mm from the roll axis.** Pad mount face Y 27, contact face Y 102.3. 0.5 mm tray + 4× M4 (±24 mm) unchanged. Core patch 54.8 × 54.8, centred.
- Bearing: **CRBH 7013 A**, C0 27.7 kN, dp ≈ 0.085 m.
- Load: 7.0 kN peak at **15° governing (tangential 0.27 N = 1.81 kN)**, axial and down shear, + arm weight (tuck B). μ 0.15 tangential = sensitivity only, not credited.
- Offsets: e = 0 and 5 mm qualified; e = 10 mm informative.
Report per case: s0; **raw roll torque Mx** (no clutch credit) and CSG-25 SF at fault ×1.05 vs 369 N·m; stand-off peak von Mises; other five gates.
R-120 expectation: s0 2.31/2.16/2.04, Mx raw down 321 N·m, gear SF 1.10. Output REPORT.md + results.json here.
