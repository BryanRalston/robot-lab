# Job 1 rerun - pad R10 (R-119), queue for Grok Interface (bryan PC)
Reuse fea/job1_pad_r8/fea_job1.py and all six BRIEF gates. Supersedes job1_pad_r9.
- Core traction patch 54.8 x 54.8 mm centred on tray (bolts +-24 mm unchanged).
- Peak 7.0 kN at 15 deg (normal 6.76 kN, tangential 1.81 kN), axial and down shear.
- Contact face Y = 102.3 mm; pad centre Z = -64 mm.
- Offsets e = 0, 5, 10 mm (6 cases). Sensitivity: tangential 0.15 N (skin option) at e = 0, 10.
Report per case: s0; roll Mx **raw** and **clutch-limited** (min(raw, 307 N.m)); bearing C0 required for s0 = 2.0; other five gates.
Hand-calc expectation: s0 1.81/1.70/1.60; Mx raw 433 axial / 618 down.
Output REPORT.md + results.json here. CPU-only, modest runtime.
