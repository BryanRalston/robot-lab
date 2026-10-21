"""L83: tube local buckling / ovalisation at T&R SIDE_FALL rev C bottoming 92.5 J -> 1079 N.m. Hand [EST].
Elastic: sigma_cl = E t / (R sqrt(3(1-nu^2))), NASA SP-8007 bending knockdown gamma = 1 - 0.731 (1 - exp(-phi)), phi = sqrt(R/t)/16.
Brazier ovalisation moment M_B = 0.987 E R t^2 / sqrt(1-nu^2). Inelastic: AISC 360 F8 round HSS noncompact Mn = (0.021E/(D/t) + Fy) S used as an
analogue [EST: steel spec applied to 7075 with Fy 393 = fall limit]. Yield check SF = 393 / (M/S)."""
import json,math
E=71700.; nu=0.33; Fy=393.; M=1.079e6
out={}
for n,D,t in (('tibia 45x2.0',45,2.0),('femur 50x1.5',50,1.5)):
    R=(D-t)/2; d=D-2*t; S=math.pi/32*(D**4-d**4)/D
    scl=E*t/(R*math.sqrt(3*(1-nu**2))); phi=math.sqrt(R/t)/16; g=1-0.731*(1-math.exp(-phi)); scr=g*scl
    MB=0.987*E*R*t*t/math.sqrt(1-nu**2); lam=D/t; lp=0.07*E/Fy; lr=0.31*E/Fy
    Mn=(0.021*E/lam+Fy)*S if lp<lam<=lr else Fy*S*1.27
    s=M/S
    out[n]=dict(D_t=round(lam,1),sigma_bend_MPa=round(s),SF_yield_393=round(Fy/s,2),sigma_cr_elastic_MPa=round(scr),SF_elastic_buckling=round(scr/s,1),
       M_brazier_kNm=round(MB/1e6,2),SF_brazier=round(MB/M,1),section='noncompact' if lp<lam<=lr else 'compact',lambda_p=round(lp,1),lambda_r=round(lr,1),
       Mn_local_kNm=round(Mn/1e6,2),SF_local_inelastic=round(Mn/M,2))
json.dump(out,open('results/r031/tube_buckling_l83.json','w'),indent=1); print(json.dumps(out,indent=0))
