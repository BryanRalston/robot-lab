"""L78 hand check [EST]: D97 PU knee stop (r60, 1030 N.m, 17.2 kN pad force total) vs r75 fallback (830 N.m, 11.1 kN) - rare/fall event,
single-path 7075 R-128 bands: fall limit 393 (min yield); bearing tiers 455/381/295 by e/D (2.0/1.5/<1.5). Stop torque reacted pad (thigh clevis
cheek) -> striker (shank tongue) -> tubes as knee moment. Geometry model_v4: tongue ring OD56/ID16 x 28, neck 36 x 28 into the tibia; clevis cheeks
14 thick, R23; femur 50 x 1.5, tibia 45 x 1.5 (L65). Pad stacks outboard of the cheeks (L78 placement) on 2 x M6 12.9 per holder [EST]."""
import json,math
def Z(D,t): d=D-2*t; return math.pi/32*(D**4-d**4)/D
out={}
for name,T,r in (('D97_r60',1030.,0.060),('fallback_r75',830.,0.075)):
    F=T/r; Fp=F/2
    o=dict(stop_T_Nm=T,pad_force_total_kN=round(F/1e3,1))
    o['tibia_45x1.5_SF']=round(393/(T*1e3/Z(45,1.5)),2); o['femur_50x1.5_SF']=round(393/(T*1e3/Z(50,1.5)),2)
    # tongue neck 36 (x) x 28 (y): bending about y at the neck root, M = T
    zn=28*36**2/6; o['tongue_neck_sigma']=round(T*1e3/zn); o['tongue_neck_SF']=round(393/(T*1e3/zn),2)
    # striker lug on the tongue at r: cantilever 20 mm arm, section 20 (y) x 30 (radial) [EST]
    zl=20*30**2/6; o['striker_lug_SF']=round(393/(Fp*20/zl),2)
    # cheek seat bearing (30x30 face) and holder bolts 2xM6 12.9 per stack in shear
    o['seat_bearing_MPa']=round(Fp/900,1); o['bolt_shear_SF']=round(0.6*1220/(Fp/(2*28.3)),2)
    o['bolt_bearing_cheek_SF_455']=round(455/(Fp/(2*6*14)),2)
    # knee pin ø16 42CrMo4 double shear by pad reaction (pads both sides -> pin unloaded ideally; worst all on pin)
    o['knee_pin_shear_MPa_worst']=round(F/(2*201)); o['vs_drive_fall_case_kNm']=1.38
    out[name]=o
out['fallback_energy']=dict(note='r75 3x15 mm: 830 N.m peak at 8.6 deg (Actuators EST scaled), 62.7 J needed; capacity to 25 % strain scales ~ (15/12)*(75/60)^2... -> Actuators to confirm energy SF >= 1.5 and max 143.6 deg inside the 145 clash-free range',mass_kg_est='~0.15/knee [EST, larger pads] vs 0.131')
json.dump(out,open('results/r031/knee_stop_struct_l78.json','w'),indent=1); print(json.dumps(out,indent=0))
