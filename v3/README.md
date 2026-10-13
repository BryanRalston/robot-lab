# Robot Lab v3: hardening loop

v3 takes the v2 design and replaces every estimated actuator part with a catalog part. It then checks against real-world loads and iterates design → check → fix.

| path | what |
|---|---|
| `analysis/parts.py` | catalog data with source keys (Kollmorgen TBM2G, Harmonic Drive CSG, Rollvis RV, IKO CRBH, Everest XCR, RLS AksIM-2, maxon, Molicel P45B, LIROS, 7075, ISO 898, VDI 2230) |
| `analysis/v3.py` | design-check-fix loop: torque/speed/thermal/drive-current/life per actuator, output-bearing life + static safety, VDI 2230-style bolted joints, 1 m side-fall energy model + clutch, hand tendon drive, power, mass; exhaustive catalog re-selection; mass-reduction pass |
| `analysis/results/` | `v3_initial.md` (v2 with catalog parts, before fixes), `v3_checks.md` (final), `v3.json`, `revisions_analysis.json` |
| `cad/model.py` | CadQuery model built from the v3 selection (catalog envelopes [EST], CRBH bearings, bolts, encoder rings, fins, cable drums, tendon hand, 5.9 L pack) |
| `cad/clash.py`, `cad/knee_sweep.py` | interference at standing + range extremes; knee >120° and single-leg adduction sweeps |
| `cad/cables.py` | cable bend-radius check (≥ 10 × d) |
| `cad/fea_v3.py` | full-length FEA with fillet collars, 2–3 mesh levels, Goodman over 5 y; fall cases |
| `cad/mass.py`, `cad/export.py` | CAD mass/inertia, STEP + GLB |
| `../sim/v3/` | MJCF from the CAD (`gen_v3.py`), balance test (`balance_v3.py`) |
| `PARTS.md`, `REVISIONS.md`, `dashboard.json` | parts table with sources, revision log, site dashboard data (`report.py`) |

Run order: `cd analysis && python3 v3.py`, then `cd ../cad`, then `model/clash/knee_sweep/cables/mass/fea_v3/export`, then `../../sim/v3/gen_v3.py balance_v3.py`, then `cd ../.. && python3 v3/report.py` (from v3/), and finally `python3 build_site.py`.
