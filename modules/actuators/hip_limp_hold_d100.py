"""D100 rev b: hand lever arms from ID P-023 rev 8g (d8fb6f9, modules/design/cad/covers/hip_skirt_r8g.json) replace L=0.10 [EST].
D100 hip roll/yaw limp-mode hold vs 140 N trapped-hand clamp (Robot Lab, skirt 8f, no rigid stops).
Sources: TBM2G manual §9.3.1 p.262-263 (06008A), §9.6.1 p.292-293 (08508A); HD CSF/CSG catalog Table 37 (CSG back-driving torque,
component set, ratio 100); JOINT_AUDIT (06008A+CSG-17-100 yaw, 08508A+CSG-25-100 roll); hem R141.5 (reliability/r_hip_pinch_check_8c.py).
[EST] items flagged in OUT['est']."""
import math, json, os
M={'hip_roll':dict(mot='TBM2G-08508A',Kt=0.206,Ke=12.4,Rll=0.860,Lll=1.13e-3,pp=10,Jm=0.593e-4,N=100,Tbd=9.2,L=0.10,Jl=2.0,
                   Tg=[('limp leg hanging, 15 deg roll',11*9.81*0.45*math.sin(math.radians(15))),
                       ('double-stance sag, 34 kg x 0.10 m',34*9.81*0.10),('single-stance fall, 68 kg x 0.10 m',68*9.81*0.10)]),
   'hip_yaw': dict(mot='TBM2G-06008A',Kt=0.121,Ke=7.33,Rll=1.60,Lll=1.06e-3,pp=10,Jm=0.137e-4,N=100,Tbd=3.1,L=0.10,Jl=0.15,
                   Tg=[('limp leg, gravity (yaw axis vertical)',0.0),('foot-scuff twist, 200 N x 0.10 m',20.0)])}
def brake(j,w):  # joint speed rad/s -> 3-phase short-circuit torque at joint (N*m), winding loss W
    m=M[j]; wm=w*m['N']; E=m['Ke']/math.sqrt(3)*wm*60/(2*math.pi)/1000   # phase EMF Vrms
    R=m['Rll']/2; X=m['pp']*wm*m['Lll']/2; I=E/math.hypot(R,X); P=3*I*I*R
    return (P/wm*m['N'] if wm else 0.0), P, I
PAIRS={'hem-panel':(0.109,0.168),'hem-shroud':(0.082,0.104),'L-R panel':(0.180,0.150),'L-R shroud':(0.133,0.131)}   # (roll, yaw) perpendicular lever, ID r8g
OUT={'rev':'b','pairs_m':PAIRS,'F_lim_N':140,'est':[
     'leg Jl, leg 11 kg @0.45 m, stance offsets 0.10 m','hand stiffness 30 N/mm, rotational via L','creep: friction=Tbd constant (Table 37 is breakaway; running friction lower -> conservative on creep only)']}
k=30e3
for j,m in M.items():
    ws=[i*0.01 for i in range(1,2001)]; T=[brake(j,w)[0] for w in ws]; i=max(range(len(T)),key=T.__getitem__)
    c=1.5*m['Kt']*m['Ke']/1  # not used
    r=dict(motor=m['mot'],N=m['N'],J_reflected=round(m['Jm']*m['N']**2,4),T_backdrive=m['Tbd'],L=m['L'],
           T_allow_by_pair={p:round(140*Ls[0 if j=='hip_roll' else 1],1) for p,Ls in PAIRS.items()},B_lowspeed_Nms_per_rad=round(brake(j,0.01)[0]/0.01,1),
           T_peak=round(T[i],1),w_peak=round(ws[i],2),table=[(w,round(brake(j,w)[0],1)) for w in (0.05,0.1,0.2,0.5,1,2,5)],cases=[])
    J=r['J_reflected']+m['Jl']
    for name,Tg in m['Tg']:
        net=Tg-m['Tbd']
        if net<=0: r['cases'].append(dict(case=name,Tg=round(Tg,1),holds=True,F_by_pair={p:0 for p in PAIRS},pass_=True)); continue
        w=next((w for w in ws if brake(j,w)[0]>=net),ws[-1])   # creep speed
        ix=0 if j=='hip_roll' else 1; fb={}
        for p,Ls in PAIRS.items():
            Lp=Ls[ix]; Fs=net/Lp; Fi=w*math.sqrt(J*k)/Lp; fb[p]=dict(L_m=Lp,F_static=round(Fs),F_impact=round(Fi),F_total=round(Fs+Fi),pass_=Fs+Fi<=140)
        r['cases'].append(dict(case=name,Tg=round(Tg,1),holds=False,creep_rad_s=round(w,3),creep_deg_s=round(math.degrees(w),2),
             P_winding_W=round(brake(j,w)[1],1),F_by_pair=fb,F_max=max(v['F_total'] for v in fb.values()),pass_=all(v['pass_'] for v in fb.values())))
    OUT[j]=r
# fall energy into windings: worst single-stance roll fall 0.3 rad at creep, all into 08508 copper (mass ~0.12 kg Cu [EST], c=385)
E=68*9.81*0.10*0.3; OUT['fall_energy_J']=round(E,1); OUT['dT_winding_C']=round(E/(0.12*385),1)
json.dump(OUT,open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'results/hip_limp_hold_d100.json'),'w'),indent=1)
print(json.dumps(OUT,indent=1))
