"""L65 (R-130): femur/tibia side-dent fix sizing. Inputs: STRUCTURE_FEA_REPORT (f58c40a) dent table.
Interp: power law sigma ~ t^-n fitted on the 1.2/1.6 FEA points (bracket of the answer) [EST].
Mass: scales with t(D-t) from the report's 1.2 mm mass (OD held)."""
import json,math
LIM=dict(S_basis_Fty=393.0,Sy_typ_over_1p1=435/1.1)  # R-128 s3/s5, JOB9_SPEC
lim=min(LIM.values())
T={'femur':dict(D=50,m12=0.1543,s={1.2:469.29,1.6:318.39,2.0:231.36,2.4:176.03}),
   'tibia':dict(D=45,m12=0.1485,s={1.2:487.78,1.6:327.22,2.0:236.05,2.4:178.69})}
out=dict(limit_MPa=lim,limits=LIM)
for k,v in T.items():
    s=v['s']; n=math.log(s[1.2]/s[1.6])/math.log(1.6/1.2)
    tmin=1.2*(s[1.2]/lim)**(1/n)
    m=lambda t:v['m12']*t*(v['D']-t)/(1.2*(v['D']-1.2))
    L=v['m12']/(2.83e-6*math.pi*(v['D']-1.2)*1.2)
    r=dict(n_fit=round(n,3),t_min_EST=round(tmin,3),SF_1p6=round(lim/s[1.6],3),SF_1p2=round(lim/s[1.2],3),
      tube_len_mm_EST=round(L,1))
    for t in (round(tmin,2),1.4,1.5,1.6):
        st=s[1.2]*(1.2/t)**n if t<1.6 else s[1.6]
        r[f't{t}']=dict(sigma_EST=round(st,1),SF=round(lim/st,3),dm_pair=round(2*(m(t)-v['m12']),4))
    # (b) local 1.4 mm band over 80 mm of the tube only
    r['b_local1p4_80mm_dm_pair']=round(2*(m(1.4)-v['m12'])*80/L,4)
    out[k]=r
json.dump(out,open('results/r031/femur_dent_l65.json','w'),indent=1); print(json.dumps(out,indent=1))
