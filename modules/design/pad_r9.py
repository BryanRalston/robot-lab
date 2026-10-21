"""Pad R9: response to job1 FAIL (a556d44). Hand calc, same P0 formula as fea_job1.py."""
import math, json
C0, dp, Z = 24300, 0.075, 0.064
def case(F, mu, e, t=60):
    Fn = F; Fs = mu*Fn; Y = (27+t)/1000
    M = Fs*math.hypot(Y, Z) + Fn*e/1000
    return dict(s0=round(C0/(Fn+2*M/dp+0.44*Fs), 2), Mx_axial=round(Fn*Z), Mx_down=round(Fn*Z+Fs*Y))
F_R9, MU_R9 = 7000, 0.15
side = 0.5525  # core side, dm: 5.38 kN static / 1.79 MPa = 30.1 cm2
out = {
 "rev": "R9", "basis": "job1 R8B FAIL a556d44; failing interface = CRBH 6013 static s0 (Arms bearing), not the tray (tab SF 1.62, no slip)",
 "changes_ID": {
  "core": "5052 HC 4.5 pcf 55.3x55.3x60 (was 61.8 sq); peak 7.0 kN at x1.3 (was 8.86-9.17)",
  "energy_J": round(1.79*30.6*0.72*60/10, 0),
  "slip_skin": "0.25 mm PTFE-faced film on EPP face, mu<=0.15 vs typical surfaces (caps tangential at 0.15 Fn)",
  "tray_boss": "unchanged (Arms 62x62x10 boss, 0.5 tray, 4x M4); core centred on tray"},
 "R8_check": {"e0": case(8860, .27, 0), "e10": case(8860, .27, 10)},
 "R9": {f"e{e}": case(F_R9, MU_R9, e) for e in (0, 5, 10)},
 "R9_if_mu_0p10": {f"e{e}": case(F_R9, .10, e) for e in (0, 10)},
 "needs_Arms": "s0>=2.0 at e=10 needs either e<=5 mm qualified, or larger bearing C0 (>=~27 kN); ID cannot reach it alone inside envelope (F 6 kN would need 80 mm core)",
 "needs_Arbiter": "roll Mx 448-539 N.m still > CSG-25 369 momentary; driven by 64 mm pad-centre offset from roll axis",
 "mass_kg_side_delta": {"core": -0.0035, "spreader": -0.0011, "EPP": -0.0004, "PTFE_skin": 0.0017},
 "mass_kg_pair_delta_EST": -0.007,
 "risks": ["energy 237 J < 265 J R3 design energy (>=220 J A44 cap): Controls/Arbiter to confirm 220 J basis",
           "mu 0.15 needs Materials test on concrete/tile"]}
json.dump(out, open("pad_r9.json", "w"), indent=1); print(json.dumps(out["R9"]), out["changes_ID"]["energy_J"])
