"""Round 3b: hip_pitch screw-to-pivot-boss clearance, config B (Legs L10: lever 50, clock 60, trunnion (30,-300), sign -1),
full mechanical ROM -120..+40 deg. Envelope per screw unit along the trunnion->lever-pin line (cad_mass.linear_body, TBM2G-07613):
motor can r41 over [-21.5,+27.5] mm from trunnion, nut housing r20.5 over [+27.5,+83.6], RV12 rod r6 from +83.6 to lever pin E,
rod-end eye r11 (ø22) within 15 mm of E. Pivot boss r16 (ø32) at origin. Clearance = distance(pivot axis, solid segment) - r_part - 16.
Usage: python3 hp_clearance.py [lever_r clock tx tz]  -> results/hp_clearance.json"""
import numpy as np, json, os, sys
H=os.path.dirname(os.path.abspath(__file__))
def seg_dist(P,A,B):
    AB=B-A; t=np.clip(np.dot(P-A,AB)/np.dot(AB,AB),0,1); return np.linalg.norm(P-(A+t*AB))
def run(r=50,clock=60,tx=30,tz=-300,sign=-1,rboss=16,th=np.arange(-120,40.01,0.5)):
    T=np.array([tx,tz],float); rows=[]
    for t in th:
        a=np.radians(clock+sign*t); E=np.array([-r*np.sin(a),-r*np.cos(a)]); u=(E-T)/np.linalg.norm(E-T); L=np.linalg.norm(E-T)
        parts={'motor_can':(T-21.5*u,T+27.5*u,41),'nut_housing':(T+27.5*u,T+83.6*u,20.5),'rod':(T+83.6*u,E-15*u,6),'rod_end':(E-15*u,E,11)}
        c={k:seg_dist(np.zeros(2),A,B)-rr-rboss for k,(A,B,rr) in parts.items()}
        arm=abs(E[0]*T[1]-E[1]*T[0])/L
        rows.append(dict(theta=float(t),arm=float(arm),L=float(L),**{k:float(v) for k,v in c.items()}))
    return rows
if __name__=='__main__':
    a=[float(x) for x in sys.argv[1:5]] if len(sys.argv)>4 else [50,60,30,-300]
    R=run(*a); ks=['motor_can','nut_housing','rod','rod_end']
    def worst(lo,hi):
        sub=[x for x in R if lo<=x['theta']<=hi]; out={}
        for k in ks:
            m=min(sub,key=lambda x:x[k]); out[k]=dict(min_mm=round(m[k],2),at_deg=m['theta'])
        return out
    res=dict(geom=a,full=worst(-120,40),loaded=worst(-80,40),deep=worst(-120,-80))
    print(json.dumps(res,indent=1))
