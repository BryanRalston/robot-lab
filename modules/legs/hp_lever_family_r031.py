"""R-031 hip_pitch lever section family, hand check (no FEA). Arm = slab cantilever, pin load along x (screw axis), bending
through the slab depth b. Peak = Kt * M/Z. All Kt are [EST] (Peterson, shoulder fillet in bending, r/d and D/d per row).
Calibration: G2 as briefed (b25,d0 30, R8 to the cap) has FEA peak ~335 MPa at design (T&R / D58), i.e. an effective Kt ~6.6 on
this nominal. That's the bore-lip / cap re-entrant notch, not arm bending. The family therefore REMOVES the notch (cap merged
into a full-depth web, R>=8 blends), and Kt is the hand value for the fillet only. Converged FEA (T&R, bryan PC) must confirm."""
import json,os,math
F_D=4542.0; F_W=2030.0; L=35.0        # N/pin design, walk 1.2 (0.447x); arm ear-to-root moment arm mm [from G2 profile (33.5,-24)->(54,-48) + ear]
SE=87.0; ALLOW=SE/1.5                  # MPa (R-031 §6)
RHO={'7075-T6':2.81,'17-4PH H1025':7.80}
SE_ST={'7075-T6':87.0,'17-4PH H1025':0.75*0.9*0.814*0.5*1070}   # Se'~0.5 Su [EST], same factors
def arm(b,d0,d1=None):
    d1=d1 or d0*16/30; Z=d0*b*b/6; V=2*31.6*b*(d0+d1)/2/1e3      # 2 arms, cm3
    return Z,V
rows=[];Z0,V0=arm(25,30,16)
for mat in RHO:
  for b in (25,28,30,32,35):
    for d0 in (30,33,36,40):
      for R,Kt in ((8,2.0),(12,1.7)):
        Z,V=arm(b,d0); amp=Kt*F_W*L/Z; peak=Kt*F_D*L/Z
        dm=2*(V-V0)*RHO[mat]/1e3 + (2*0.010 if R==12 else 0) + (0 if mat=='7075-T6' else 2*V0*(RHO[mat]-2.81)/1e3*1.0)
        allow=SE_ST[mat]/1.5
        rows.append(dict(mat=mat,b=b,d0=d0,R=R,Kt_est=Kt,amp_walk=round(amp,1),peak_design=round(peak,1),allow=round(allow,1),ok=amp<=allow,
                         dmass_robot_kg=round(dm,3),amp_if_Kt_stays_6p6=round(6.6*F_W*L/Z,1)))
ok=[r for r in rows if r['mat']=='7075-T6' and r['amp_if_Kt_stays_6p6']<=ALLOW]
pick=dict(b=30,d0=36,R=8,mat='7075-T6')
P=[r for r in rows if all(r[k]==v for k,v in pick.items())][0]
out=dict(basis=__doc__,allow_MPa=round(ALLOW,1),G2_baseline=dict(nominal_design=round(F_D*L/Z0,1),fea_peak=335,walk_amp_fea=150),
         pick=P,smallest_7075_meeting_58_even_with_notch_Kt6p6=min(ok,key=lambda r:r['dmass_robot_kg']) if ok else None,rows=rows)
os.makedirs('results/r031',exist_ok=True); json.dump(out,open('results/r031/hp_lever_family.json','w'),indent=1)
print('pick',P); print('notch-kept 7075 min',out['smallest_7075_meeting_58_even_with_notch_Kt6p6'])
