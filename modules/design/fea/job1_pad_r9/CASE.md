# Job 1 rerun - pad R9 (queue for Grok Interface, bryan PC)
Reuse fea/job1_pad_r8/fea_job1.py and BRIEF criteria (all six). Same mesh/method.
Changes vs R8B:
- Core traction patch 55.3 x 55.3 mm, centred on the tray (bolt pattern unchanged, +-24 mm).
- Peak pad force 7.0 kN. Tangential = 0.15 x Fn (slip-skin cap) and, as a sensitivity, the old 15 deg (0.27 Fn).
- Contact face Y = 87.0 mm (stack unchanged); pad centre Z = -64 mm.
- Cases: axial and down shear x e = 0, 5, 10 mm (6 cases) + 15 deg sensitivity at e = 0, 10.
Report: s0 per case, Mx per case vs CSG-25 369 N.m, plus the other five gates. Hand-calc expectation: s0 2.32/2.13/1.97.
Output to fea/job1_pad_r9/ (REPORT.md, results.json). CPU-only, modest runtime.
