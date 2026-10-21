"""L81: L39 hip-roll PU bumper from a CITED curve. Freelin-Wade PUR90A TDS (92A), ASTM D575 compressive load:
https://www.freelin-wade.com/documents/data%20sheets%2C%20technical%20sheets%2C%20statements/PUR90A%20%20Technical%20Data%20Sheet.pdf
2/5/10/15/20/25/50 % = 160/325/705/1050/1380/1690/3590 psi. D575 specimen o28.6 x 12.7 -> SF 0.56 (~0.5, no correction for o20x10, SF 0.50).
30/40 % linearly interpolated between the 25 and 50 % points [EST]. Fallback o24x16 (SF 0.375) scaled by (1+2f^2) ratio 1.281/1.627 [EST, Gallagher/
PSI L = D.Y.(1+2f^2)]. Bracket stiffness: hand beam + shear [EST]."""
import json,math,numpy as np
psi=6.894757e-3; pts={0:0,2:160,5:325,10:705,15:1050,20:1380,25:1690,50:3590}
def sig(e): k=sorted(pts); return float(np.interp(e,k,[pts[i]*psi for i in k]))
r=63.0; out={}
for name,d,h,fac in (('baseline o20x10',20,10,1.0),('fallback o24x16',24,16,1.281/1.627)):
    A=math.pi/4*d*d; rows=[]
    for e in (10,20,25,30,40):
        F=sig(e)*fac*A; x=e/100*h; ee=np.linspace(0,e,200); E=float(np.trapezoid([sig(t)*fac*A for t in ee],ee/100*h))/1000
        rows.append(dict(strain_pct=e,stress_MPa=round(sig(e)*fac,2),F_kN=round(F/1e3,2),defl_mm=round(x,2),k_secant_kN_mm=round(F/x/1e3,2),T_joint_Nm=round(F*r/1e3),theta_deg=round(math.degrees(x/r),2),energy_J=round(E,2),EST=e in (30,40)))
    out[name]=dict(SF=round(d/(4*h),3),A_mm2=round(A,1),rows=rows,
       k_joint_kNm_rad_25=round(rows[2]['F_kN']*r*r/rows[2]['defl_mm']/1e3,2))
# 4 J basis
out['L39_4J_basis']='L39 (15c602d) "vs 4 J" has no source in the repo (no PU datasheet existed; hip_stop_r6 used an uncited E 25 MPa linear estimate). Replaced by the cited energy at 25-30 % strain (per bumper).'
# bottomed-out path stiffness [EST]: lug 12x12x26 cantilever on the roll-output web (7075, E 71.7 GPa, G 26.9), load at the tip;
# deck bracket: 6 mm 7075 angle, 30 wide, 20 mm arm [EST]; yoke plate local: 8 mm plate, 40 wide, 30 mm span simply supported [EST]
E=71700.; G=26900.
def cant(L,b,t): I=b*t**3/12; return 1/(L**3/(3*E*I)+L/(G*b*t*5/6))
def ss(L,b,t): I=b*t**3/12; return 1/(L**3/(48*E*I)+L/(4*G*b*t*5/6))
lug=cant(26,12,12); br=cant(20,30,6); yk=ss(30,40,8); ks=1/(1/lug+1/br+1/yk)
out['bottomed_path_EST']=dict(lug_kN_mm=round(lug/1e3,1),deck_bracket_kN_mm=round(br/1e3,1),yoke_plate_kN_mm=round(yk/1e3,1),series_kN_mm=round(ks/1e3,1),
   joint_kNm_rad=round(ks*r*r/1e6,1),fallback_plus6mm_bracket=dict(deck_bracket_kN_mm=round(cant(26,30,6)/1e3,1),series_kN_mm=round(1/(1/lug+1/cant(26,30,6)+1/yk)/1e3,1),joint_kNm_rad=round(1/(1/lug+1/cant(26,30,6)+1/yk)*r*r/1e6,1)),
   assumptions='lug 12x12 cantilever 26 mm; deck bracket 6 x 30 angle leg, 20 mm arm (+6 mm -> 26 mm for the fallback); yoke plate 8 x 40, 30 mm span SS; 7075; bolt/joint compliance ignored (stiff side) [EST]')
json.dump(out,open('results/r031/hip_roll_bumper_l81.json','w'),indent=1); print(json.dumps(out,indent=0))
