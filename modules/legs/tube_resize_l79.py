"""L79: T&R L60 rev B (513a7d5) DF 1.05 -> fall 13.1 kN; Robot Lab: Controls cap <=50 N.m within 10 deg of the stop -> design knee moment 0.92 kN.m.
Tibia 45x1.7 / femur 50x1.5 hand bending, SF = 393/sigma (fall), stop 830 N.m (r75), fatigue amplitude = knee need 235 N.m (CONTRACTS) / 2 [EST] vs 58.
Straps/joint/screw at 13.1 kN (couple scaled as L75: 8.66 kN per 5053 N total thrust)."""
import json,math
def Z(D,t): d=D-2*t; return math.pi/32*(D**4-d**4)/D
out={}
for n,D,t in (('tibia 45x2.0 (RULED)',45,2.0),('tibia 45x1.7',45,1.7),('tibia 45x1.5 (L65)',45,1.5),('femur 50x1.5',50,1.5)):
    z=Z(D,t); out[n]=dict(Z=round(z),SF_design_0p92=round(393/(0.92e6/z),2),SF_stop_830=round(393/(0.83e6/z),2),SF_bottom_1028=round(393/(1.028e6/z),2),sigma_a=round(117.5e3/z,1),SF_fatigue_58=round(58/(117.5e3/z),2))
L=314; rho=2.81e-6
dA=math.pi/4*((45-3.0)**2-(45-4.0)**2); dsl=math.pi/4*((41.8**2-40.8**2)-(41.0**2-40.0**2))
out['mass']=dict(tube_kg_leg=round(dA*L*rho,4),sleeve_kg_leg=round(-dsl*100*rho,4),net_kg_leg=round((dA*L-dsl*100)*rho,4),net_kg_robot=round(2*(dA*L-dsl*100)*rho,4),basis='vs L65 1.5 wall; tube length 314 (model_v4 tt-tb)')
out['tibia_sleeve']=dict(tube_ID_2p0=41.0,sleeve_OD_max=40.8,sleeve_ID=39.8,note='0.20 diametral bond per BOND_SPEC 3; tibia doubler 0.5 wall OD 41.8 (1.5 wall) -> 40.8 (2.0 wall). Not a CONTRACTS row (P-152 46.80 is the FEMUR sleeve, unchanged). Tibia OD 45 unchanged -> fork/collar interfaces unchanged.')
F=13100.; C=8.66*F/5053
st={}
for nm,sh in (('equal',0.5),('65/35',0.65)):
    f=C*sh*1e3; s=f/160; st[nm]=dict(strap_kN=round(f/1e3,1),SF_net=round(393/s,2),SF_root_Kt1p5=round(393/(1.5*s),2),bolt_shear_SF=round(0.6*1220/(f/(4*28.3)),2),pad_bearing_SF_455=round(455/(f/192),2),G10_bearing_MPa=round(f/(4*6*12),1),G10_margin_128=round(128/(f/(4*6*12)),2))
out['straps_13p1kN']=dict(couple_kN=round(C,1),cases=st,screw_65_35_kN=round(F*0.65/1e3,2),screw_SF_C0a_27p3=round(27.3/(F*0.65/1e3),2))
json.dump(out,open('results/r031/tube_resize_l79.json','w'),indent=1); print(json.dumps(out,indent=0))
