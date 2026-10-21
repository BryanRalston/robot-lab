# Job 2 brief - G3 hip-pitch lever FEA (spec: modules/actuators/results/GROKBUILD_lever_fea_r031.md @ fbd762b, latest revision)
Execute that spec exactly. Summary:
- Geometry: modules/actuators/cad/hip_pitch_lever_r031_mw_b30_d36_RC.step (7075-T6, E 71.7 GPa, nu 0.33, Sy 503).
- Setup as GROKBUILD_lever_fea_v2 (pressure-loaded bore, yoke-face support, ear pin loads), reuse hp_lever_fea_v2.py mesh/solve with STEP import.
- Case 1 design: 4542 N per pin. PASS: converged peak von Mises <= 335 MPa.
- Case 2 fatigue: 2030 N per pin fully reversed. PASS: hot-spot von Mises amplitude <= 58 MPa.
- Convergence: global h 4->3->2 with local refinement at R8 blends, bore lip, ear roots to 1.5->1.0->0.6 mm; peak change <5% over last two levels, else declare singularity with location.
- Report peak/amplitude per level with locations, plot of governing case, mass from the STEP.
- If it fails: run b35/d40 fallback (if its geometry exists in repo; else report it is missing), then note 17-4PH H1025 option.
- Keep memory reasonable for this PC; do not touch other modules or other running sessions.

## Deliverables
- Scripts, results JSON, plot and REPORT.md in modules/actuators/fea/job2_g3_lever/
- Commit "RL job2: G3 hip lever FEA" and git push origin main. Final line: JOB2_DONE PASS|FAIL <hash>.
