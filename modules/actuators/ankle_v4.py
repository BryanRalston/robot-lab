"""v4 audit (D60/D61): ankle screw end joints over pitch -45..+40 x roll +-18 (1 deg grid), trunnion raised to z 450 (eye centre).
Top: axial GE 12 C eye (alpha 10 deg, SKF) in a shank clevis with 0.6 mm side gap per side -> eye spin about the body axis <= asin(0.6/15).
Bottom: high-misalignment PTFE rod end on the instep pin (QA1 MGF12T class: ball 22.23, ball width 16, head 30 x 10.75, 27 deg, C0r 17.4 kN).
Outputs: top tilt, bottom misalignment, head-to-lug axial clearance with a spacer, stroke check, PTFE life (SKF G_h method, C [EST])."""
import numpy as np, json, os, math, sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
H=os.path.dirname(os.path.abspath(__file__))
TZ=float(os.environ.get('TZ',450)); GAP=0.6; SPIN=math.degrees(math.asin(GAP/15)); SPACER=float(os.environ.get('SPACER',4.5))
BALL_W,HEAD_R,HEAD_T,ALPHA_B=16.0,15.0,10.75,27.0; LUG_FACE_NOW=7.5   # current lug inner face 7.5 mm from the eye mid-plane (lug y 52.5, eye y 45)
def R(ax,a):
    a=np.radians(a);c,s=np.cos(a),np.sin(a)
    return np.array([[1,0,0],[0,c,-s],[0,s,c]]) if ax=='x' else np.array([[c,0,s],[0,1,0],[-s,0,c]])
def rot(k,v,a): return v*np.cos(a)+np.cross(k,v)*np.sin(a)+k*(k@v)*(1-np.cos(a))
C=np.array([0,0,80.]); out=dict(tz=TZ,spin_limit_deg=SPIN); tt=bb=0; L=[]; worst=None
for p in np.arange(-45,40.1,1):
    for r in np.arange(-18,18.1,1):
        M=R('y',p)@R('x',r)
        for sy in (1,-1):
            T=np.array([90,45*sy,TZ]); E=M@(np.array([73,45*sy,100.])-C)+C; u=(T-E)/np.linalg.norm(T-E); L.append(np.linalg.norm(T-E)); pin=M@[0,1,0]
            e0=np.array([0,1.,0]); e0-=(e0@u)*u; e0/=np.linalg.norm(e0)
            for ph in np.radians(np.linspace(-SPIN,SPIN,5)):
                n=rot(u,e0,ph); t=np.degrees(np.arccos(abs(n[1]))); b=np.degrees(np.arccos(min(1,abs(n@pin))))
                if t>tt: tt=t
                if b>bb: bb=b; worst=(float(p),float(r),sy)
out['top_tilt_max_deg']=tt; out['top_alpha_GE12C_deg']=10; out['bottom_misalign_max_deg']=bb; out['bottom_alpha_deg']=ALPHA_B; out['bottom_worst_pose']=worst
b=math.radians(bb); exc=HEAD_R*math.sin(b)+HEAD_T/2*math.cos(b)
out['head_axial_excursion_mm']=exc; out['spacer_mm']=SPACER; out['lug_face_from_midplane_mm']=BALL_W/2+SPACER
out['head_to_lug_clearance_mm']=BALL_W/2+SPACER-exc; out['lug_move_outboard_mm']=BALL_W/2+SPACER-LUG_FACE_NOW
out['inboard_side']='no lug inboard of the eye (instep lug is single, outboard); inboard sweep 2 x %.1f mm stays clear of the other screw (90 mm apart)'%exc
Lmin,Lmax=min(L),max(L); need=250.7+(Lmax-Lmin-111.7)+(22.21+20)/2+15
out.update(Lmin=Lmin,Lmax=Lmax,stroke=Lmax-Lmin,need_min_len=need,margin=Lmin-need,note_need='O-A5 need 250.7 at boss pivot + 21.1 (boss at Lm/2) + 15 (eye centre behind rear cap) + stroke change')
# PTFE life: SKF G_h = b1 b2 1400/(p^1.3 v) with C_est = K dk B_head (K 100 N/mm2 PTFE-fabric class) x 0.9 [EST, no maker rating]
import life_r6 as LR
Cest=100*22.23*HEAD_T*0.9; inv=0; det={}
for s,w in LR.MIX.items():
    t,dt,TAU,Q,V=LR.load(s); F=np.maximum(np.abs(TAU[:,4]/(2*0.073)+TAU[:,5]/(2*0.040)),np.abs(TAU[:,4]/(2*0.073)-TAU[:,5]/(2*0.040)))
    ang=np.degrees(Q[:,4]); beta=(np.percentile(ang,99)-np.percentile(ang,1))/2
    f=60/(2*json.load(open(f'{LR.LG}/{s}.json'))['info'].get('Tstep',0.47)); P=(np.sum(F**1.3*dt)/np.sum(dt))**(1/1.3)
    p=100*P/Cest; v=5.82e-7*22.23*beta*f; G=0.2*1400/(p**1.3*v); inv+=w/G; det[s]=dict(F_peak=float(F.max()),P_eq=float(P),beta=float(beta),Gh=float(G))
out['life']=dict(C_est_N=Cest,C0r_N=17373,cases=det,Gh=1/inv,T9=14600,interval_h=math.floor(0.5/inv/250)*250,F_peak_over_C0r=max(d['F_peak'] for d in det.values())/17373)
json.dump(out,open(f'{H}/results/ankle_v4.json','w'),indent=1); print(json.dumps(out,indent=1))
