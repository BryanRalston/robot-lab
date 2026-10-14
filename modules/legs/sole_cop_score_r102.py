"""R-102: score sole candidates with Controls' sole_cop_r1.py edge model (copied logic, controls 397f469): Winkler edge inset
e = 2F/(3 w E eps_lim), eps 0.39, w 0.100 toe/heel 0.240 side, + LIPM ZMP shift DZ/zc*|com-zmp| with DZ = pad thickness.
Candidates add thickness (DZ) and a frame-band check: block length a = 3e must fit inside the 20 mm band, else the frame fails at that frame."""
import os, json, numpy as np
R=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..')); L=os.path.join(R,'modules/legs/results')
HEEL,TOE,HW,EPS=-0.060,0.180,0.050,0.39
def gent(S): return 0.0981*(56+7.62336*S)/(0.137505*(254-2.54*S))*1e6
# name: (E, t_m, density, coverage, src)
C={'A Gumlite 47A 6 full':(2.2e6,.006,.55,1.0,'Vibram tech data 47+-3A, 0.55'),
   'B SP 67A 6 full (Controls ref)':(4.8e6,.006,1.20,1.0,'Vibram 7174-6M SP 64-70A; density EST 1.20'),
   'C SP 67A 6 frame20':(4.8e6,.006,1.20,0.5,''),
   'D TOP85 3 full [85A EST]':(gent(85),.003,1.20,1.0,'Vibram 7373 Tequilgemma TOP, TOP85 compound, 1/1.8/3/6 mm (hungtathong); 85A and 1.20 EST'),
   'E TOP85 3 frame20 [85A EST]':(gent(85),.003,1.20,0.5,''),
   'F SP 67A 6 frame20 + Gumlite 0 centre':(4.8e6,.006,1.20,0.5,''),
   'G Tequilgemma 7663 4 full [medium ~65A EST]':(gent(65),.004,1.20,1.0,'Vibram 7663 3/4 mm, "medium hardness" - no Shore cited, 65A EST'),
   'H 7663 4 frame20 [65A EST]':(gent(65),.004,1.20,0.5,'')}
PLANS={'walk 0.8 ref_m12':'r7/ref_m12/walk_0p8_r7.npz','walk 1.0 ref_m12':'r7/ref_m12/walk_1p0_r7.npz','walk 1.2 ref_m12':'r7/ref_m12/walk_1p2_r7.npz',
       'walk 1.2 ref_ds25':'r7/ref_ds25/walk_1p2_r7.npz','carry P-042 1.0':'p042/carry_20kg_1p0.npz','push_recover':'push_recover.npz','stairs 18 cm':'stairs_18cm.npz'}
out={}
for cn,(E,t,rho,cov,src) in C.items():
    r=dict(mass_foot_kg=round(0.240*0.100*t*rho*1e3*cov+ (0 if cov==1 else 0.2*0.008*t*rho*1e3),4),E_MPa=round(E/1e6,2),src=src,plans={})
    r['inset_toe_mm_1p31BW']=round(1000*2*85*9.81*1.31/(3*0.1*E*EPS),1); r['block_fits_band']= (cov==1) or 3*r['inset_toe_mm_1p31BW']<=20
    for pn,f in PLANS.items():
        fp=os.path.join(L,f)
        if not os.path.exists(fp): continue
        d=np.load(fp); Cc,FZ=d['COP'],d['FZ']
        dz=t/1.158*np.linalg.norm(d['com']-d['zmp'],axis=1) if 'com' in d.files and d['com'].ndim==2 and d['zmp'].ndim==2 else np.zeros(len(FZ))
        ms=[]
        for i in range(2):
            ok=(FZ[:,i]>1)&np.isfinite(Cc[ok if False else slice(None),i,0]); x,y,F=Cc[ok,i,0],Cc[ok,i,1],FZ[ok,i]
            ins=lambda w:2*np.maximum(F,0)/(3*w*E*EPS)
            m=np.minimum(np.minimum(TOE-x-ins(.1),x-HEEL-ins(.1)),HW-np.abs(y)-ins(.24))-dz[ok]; ms.append(m)
        m=np.concatenate(ms)*1000; r['plans'][pn]=dict(min=round(float(m.min()),1),p5=round(float(np.percentile(m,5)),1))
    out[cn]=r; print(cn,r['mass_foot_kg'],r['inset_toe_mm_1p31BW'],r['block_fits_band'],{k:v['min'] for k,v in r['plans'].items()})
json.dump(out,open(os.path.join(L,'r081/sole_cop_score_r102.json'),'w'),indent=1)
