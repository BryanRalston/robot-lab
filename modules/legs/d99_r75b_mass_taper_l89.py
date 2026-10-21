"""L89: D99 r75b CAD mass (cad/knee_stop_pu_r75b_d99.step, OCC volume x density) by part, and the tapered 7075-T7351 striker arm [hand beam, EST Kt].
STEP = one stack side (solid 0: PU stack + 7075 shims/end plates + seat + lug + 24x18x63 arm, fused) + the tibia ring with 2 x o6 pins (solid 1).
Fused solid 0 is split by subtracting the analytic PU/shim/plate/seat/lug/arm volumes (Actuators knee_stop_pu_d99.py parameters)."""
import json,math,cadquery as cq
a=cq.importers.importStep('../actuators/cad/knee_stop_pu_r75b_d99.step'); S=a.solids().vals(); V0,V1=S[0].Volume(),S[1].Volume()
r7,rpu,rst=2.81e-3,1.13e-3,7.85e-3   # g/mm3
NL,tl,ts,AY,AR=7,10.17,1.0,24.,20.; Ast=AY*AR-math.pi*9
pu=NL*tl*Ast; shim=(NL-1)*Ast*ts; plates=2*(AY+2)*(AR+2)*3; seat=36*30*8; lug=32*22*10; arm=24*18*63
metal0=V0-pu; pins=2*math.pi*9*24   # 2 x o6 x 24 steel [EST length]
side=dict(PU_g=pu*rpu,shims_plates_g=(shim+plates)*r7,seat_g=seat*r7,lug_g=lug*r7,arm_g=arm*r7,
          residual_metal_g=(metal0-shim-plates-seat-lug-arm)*r7)
ring=dict(ring_g=(V1-pins)*r7,pins_g=pins*rst)
knee=2*sum(side.values())+sum(ring.values()); bar=40
out=dict(step_cm3=[round(V0/1e3,2),round(V1/1e3,2)],per_side={k:round(v,1) for k,v in side.items()},ring={k:round(v,1) for k,v in ring.items()},
  per_knee_g=round(knee,1),bar_g_EST=bar,robot_kg=round(2*(knee+bar)/1e3,3),arms_robot_kg=round(4*arm*r7/1e3,3))
# taper: cantilever L 63 from the ring, tip load at the stack; tangential depth h(x)=18*sqrt(x/L) (x from tip), floor 9 mm (tip shear+lug), width 24 radial
L=63.;n=630;vol=0
for i in range(n):
    x=(i+.5)*L/n; vol+=24*max(18*math.sqrt(x/L),9.)*L/n
F={'design 3.65 kN':3650,'bottoming 5.25 kN':5250,'T_STOP 830 N.m (5.53 kN/side)':830e3/75/2}
chk={}
for k,f in F.items():
    lim=262 if k.startswith('design') else 393
    s=f*L*6/(24*18**2); chk[k]=dict(root_MPa=round(s),SF_net=round(lim/s,2),SF_Kt1p4=round(lim/(1.4*s),2),tip_shear_MPa=round(1.5*f/(24*9),1))
save=4*(arm-vol)*r7/1e3
out['taper']=dict(profile='h = 18*sqrt(x/63), floor 9, 24 wide; root 18 kept over the R5 fillet',vol_ratio=round(vol/arm,3),save_robot_kg=round(save,3),
  stress_const_along='sigma(x)=root sigma until the 9 mm floor (x<15.8), lower beyond',checks=chk,
  fatigue='rare-event stop (Controls kneel 108.9 deg < 130 contact); root 1.4 x 177 = 248 MPa > 58 at 1e8 -> rare-event acceptance only, as L84 r2',
  energy='92.5 J is absorbed by the PU; arm compliance not credited (stiffer than the pad by >20x [EST])')
json.dump(out,open('results/r031/d99_r75b_mass_taper_l89.json','w'),indent=1); print(json.dumps(out))
