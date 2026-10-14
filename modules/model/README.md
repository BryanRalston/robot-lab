# modules/model: v4 fidelity model (Robot Lab)

- `model_v4.py`: CadQuery assembly. The legs come from module data (Actuators STEP parts, Legs linkage/structure decisions). Upper body and hands are strain-wave + crossed-roller placeholders, and every non-module dimension is tagged `[EST]`.
- `clash_v4.py`: interference check plus floating-part check at stand, then a sweep of every joint through its range (`out/clash_v4.json`, log in `out/sweep_log.txt`).
- `audit_v4.py`: writes `JOINT_AUDIT.json` / `JOINT_AUDIT.md`. Exits 1 if any joint has no modelled mechanism or any joint is FAIL.
- `export_v4.py` → `site/cad/bhl_v4.glb` + `parts_v4.json`; `build_v4_page.py` → `site/v4.html` + `site/cad/joints_v4.json`; `render_v4.py` makes the progress images.

Run order: `python3 clash_v4.py && python3 audit_v4.py; python3 export_v4.py && python3 build_v4_page.py`
