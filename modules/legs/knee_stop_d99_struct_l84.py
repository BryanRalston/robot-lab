"""L84 hand [EST]: D99 strikers/seats. Loads: design 544 N.m / 7.3 kN total (2 sides, 3.65 kN each); bottoming 789 N.m / 10.5 kN (5.25 kN each).
Allowables 7075-T7351 single-path (R-128): 262 design, 393 fall, bearing tiers 455/381/295 (e/D 2.0/1.5/<1.5), fatigue amplitude 58 MPa (1e8; the stop is
a rare-event part, ~1e4 contacts if every kneel touches it [EST])."""
import json,math
rho=2.81e-6; out={}
# striker lug: 10 (y) x 18 (along shank) x 31.5 cantilever from the tongue neck block; load at the face (arm 25 to the root), R5 root fillet Kt 1.4 [EST]
b,h,L,arm,Kt=10.,18.,31.5,25.,1.4; Z=b*h*h/6
for n,F in (('design',3650.),('bottoming',5250.)):
    s=F*arm/Z; lim=262 if n=='design' else 393
    out[f'striker_{n}']=dict(F_N=F,sigma_root=round(s),SF=round(lim/s,2),sigma_root_Kt=round(s*Kt),SF_Kt=round(lim/(s*Kt),2),shear_MPa=round(F/(b*h),1))
# seat strut integral with the o64 collar: 20 (x) x 8 (y) x 28 long, aligned with the striker force (compression) + 10 % eccentricity [EST]
A=20*8.; Zs=8*20**2/6
for n,F in (('design',3650.),('bottoming',5250.)):
    s=F/A+F*0.1*20/Zs; lim=262 if n=='design' else 393; out[f'seat_{n}']=dict(sigma=round(s),SF=round(lim/s,2))
# o64 split collar: bonded DP490 L34 on the femur + 2 x o6 pins; seat moment arm 15 mm about the collar
Abond=math.pi*50*34; 
for n,F in (('design',3650.*2),('bottoming',5250.*2)):
    tau=F/Abond; out[f'collar_bond_{n}']=dict(tau_MPa=round(tau,2),SF_vs_2p85MPa_82C=round(2.85/tau,2),pins_2xo6_shear_SF=round(0.6*1000*2*28.3/F,2))
out['fatigue']='design 3.65 kN root 169 x Kt 1.4 = 237 MPa > 58 (1e8 basis) -> acceptable only as a rare-event part (<=1e4 contacts) [EST]; if Controls kneel uses the stop every kneel, Materials to give 7075-T7351 S-N at 1e4'
# mass growth (7075): 2 striker lugs + 2 seat struts per knee; remove 4 g tongue-neck pocket compensation [EST]
lug=2*b*h*L*rho; seat=2*20*8*28*rho; comp=-0.004
g=lug+seat+comp
out['mass']=dict(lugs_kg_knee=round(lug,4),seats_kg_knee=round(seat,4),compensation=comp,growth_kg_knee=round(g,4),growth_kg_robot=round(2*g,4),
   D99_line_robot=round(0.344+2*g,3),cap=0.35,breaks_cap=0.344+2*g>0.35)
out['tibia_839Nm']=dict(SF=round(393/(0.839e6/2781),2)); out['femur_839Nm']=dict(SF=round(393/(0.839e6/2691),2))
json.dump(out,open('results/r031/knee_stop_d99_struct_l84.json','w'),indent=1); print(json.dumps(out,indent=0))
