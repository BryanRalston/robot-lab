"""RL Test & Reliability R1 hand checks (light, no FEA). Inputs cited inline."""
import json
Sy,Su=503.,572.          # 7075-T6 (actuators/hp_lever_fea.py, legs/structure_check_r3.py)
Se_raw=159.              # R=-1 unnotched @5e8 (same sources)
ka,kb,kc=0.75,0.9,0.814  # machined surface, size, 99% reliability (Shigley-style) -> my assumption
Se=Se_raw*ka*kb*kc
r={"Se_corrected_MPa":round(Se,1),"Se_repo_MPa":127}
# Hip lever (actuators/results/hp_lever_fea_O13_REPORT.md, hp_lever_fea_convergence.json)
F=454.2/0.050/2; r["hip_design_pin_N"]=round(F)
h,f=[3,2.5,2],[335.54,359.51,378.92]
r["hip_peak_trend"]="monotone increasing with refinement; local 1.5mm = 489.5 MPa > Richardson 412 -> singular corner, not converging"
r["hip_SF_yield_finest"]=round(Sy/489.54,2)
w=203/454.2   # walk_1p2 hip_pitch peak 203 N.m (legs/results/walk_1p2.json)
for lab,pk in [("h4",342.85),("local1.5",489.54)]:
    sa=pk*w   # hip pitch torque reverses in gait -> treat as fully reversed amplitude
    r[f"hip_walk_amp_{lab}_MPa"]=round(sa,1); r[f"hip_fatigue_SF_{lab}"]=round(Se/sa,2)
r["hip_gait_cycles_T9"]=round(14600*3600/0.9)
# Clevis Goodman (legs/results/r8/structure_fixes_r8.json): pulse 0->147
sa=sm=147/2
r["clevis_Goodman_backsolved_Se"]=round(sa/(1/1.69-sm/Su),1)
r["clevis_Goodman_corrected"]=round(1/(sa/Se+sm/Su),2)
r["clevis_SF_static"]=round(Sy/147,2)
# tongue
r["tongue_fault_SF"]=round(Sy/340,3)
# foot collar hand
r["foot_hand_MPa"]=round(443.8*(6/9)**2,1); r["foot_SF"]=round(Sy/r["foot_hand_MPa"],2)
# tubes: SF ~ t^1.35, base 1.2 mm SF 1.07/1.03
for n,s in [("femur",1.07),("tibia",1.03)]:
    r[f"tube_{n}_SF_t1.7"]=round(s*(1.7/1.2)**1.35,2)
    r[f"tube_{n}_SF_t1.2_outside_doubler"]=s
# ankle tine (actuators/results/DECISIONS.md D63)
Ft=323.8/0.073/2/2; r["tine_N"]=round(Ft)
r["tine_bearing_MPa"]=round(Ft/(12*6),1); r["tine_bearing_SF_vs_1.5Sy"]=round(1.5*Sy/r["tine_bearing_MPa"],1)
r["tine_tearout_SF"]=round(0.577*Sy/(Ft/72),1); r["tine_net_Kt_MPa"]=round(3.5*Ft/108,1)
# ankle stroke (results/ankle_v4.json)
r["ankle_stroke"]=round(414.170-301.589,2); r["ankle_margin"]=round(301.589-287.686,2)
r["QA1_misalign_margin_deg"]=round(27-20.79,2)
# knee crossbar (results/DECISIONS.md line 65)
r["knee_crossbar_SF"]=round(Sy/192,2)
json.dump(r,open("r1_checks.json","w"),indent=1); print(json.dumps(r,indent=1))
