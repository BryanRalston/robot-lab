"""v3 hardening loop: catalog parts -> checks -> fixes -> re-check. Writes results/v3_checks.md, results/v3.json, results/revisions_analysis.json
Run: python3 v3.py   (reads ../cad/out/*.json for FEA / CAD-derived inputs when present)"""
import math, json, copy, os, sys
import numpy as np
import parts as PT
G=9.81; H=os.path.dirname(os.path.abspath(__file__)); os.makedirs(os.path.join(H,'results'),exist_ok=True)
V2REQ=json.load(open(os.path.join(H,'../../v2/analysis/results/summary_final.json')))['req']
SPEED={'hip_pitch':4,'hip_roll':3,'hip_yaw':3,'knee':8,'ankle_pitch':6,'ankle_roll':4,'waist_yaw':2,'waist_pitch':2,'shoulder_pitch':4,
       'shoulder_roll':4,'shoulder_yaw':4,'elbow':6,'wrist_roll':6,'wrist_pitch':6,'wrist_yaw':6,'neck_yaw':4,'neck_pitch':4}  # rad/s [EST, v2]
LIFE_H=5*365*8.0
STRIDE_HZ=1.0
VBUS_MIN=13*3.4
AMB=40.0; DT_LIMIT=100.0
I_CONT=PT.DRIVE['I_cont_crest']/math.sqrt(2); I_PEAK=PT.DRIVE['I_peak_crest']/math.sqrt(2)
GAIT={'hip_pitch':(40,1.1/1.2),'hip_roll':(10,0.9/1.0),'hip_yaw':(8,0.5),'knee':(60,0.8/1.3),'ankle_pitch':(25,1.0),'ankle_roll':(10,0.5),
      'waist_yaw':(8,0.3),'waist_pitch':(4,0.3),'shoulder_pitch':(30,0.15),'shoulder_roll':(5,0.1),'shoulder_yaw':(5,0.1),'elbow':(20,0.15)}
LEGSCALE=('hip_pitch','hip_roll','hip_yaw','knee','ankle_pitch','ankle_roll','waist_pitch')
SHARED={'ankle_roll':'ankle_pitch','wrist_yaw':'wrist_pitch'}   # differential pairs: one pair of screws serves both DoF
HOLD={'hip_pitch':1.0,'knee':1.0,'ankle_pitch':1.0,'waist_pitch':1.0}
def initial_state():
    sub={'M115':'TBM2G-11513','M85':'TBM2G-08513','M60':'TBM2G-06013','M38':'TBM2G-05008'}
    J={'hip_yaw':['rotary','M60','CSG-20-100'],'hip_roll':['rotary','M115','CSG-25-100'],'hip_pitch':['rotary','M115','CSG-25-100'],
     'knee':['linear','M85','RV12x5',0.045],'ankle_pitch':['linear2','M60','RV12x4',0.05],'ankle_roll':['linear2','M60','RV12x4',0.04],
     'waist_yaw':['rotary','M60','CSG-20-100'],'waist_pitch':['rotary','M85','CSG-25-100'],
     'shoulder_pitch':['rotary','M85','CSG-25-100'],'shoulder_roll':['rotary','M85','CSG-25-100'],'shoulder_yaw':['rotary','M60','CSG-20-100'],
     'elbow':['rotary','M60','CSG-20-100'],'wrist_roll':['rotary','M38','CSG-14-100'],'neck_yaw':['rotary','M38','CSG-14-100'],'neck_pitch':['rotary','M38','CSG-14-100'],
     'wrist_pitch':['linear2','M38','RV12x4',0.025],'wrist_yaw':['linear2','M38','RV12x4',0.025]}
    CNT={'waist_yaw':1,'waist_pitch':1,'neck_yaw':1,'neck_pitch':1}
    st=dict(J={},cooling={},bearing={},bolts={},hand=dict(flexors=6,small=5,spool_r=0.004,ratio=111),battery=dict(S=13,P=10),
            clutch={},pad_mm=10,structure_scale=1.0)
    for n,v in J.items():
        d=dict(kind=v[0],motor=sub[v[1]],w=1,cnt=CNT.get(n,2))
        if v[0]=='rotary': d['gear']=v[2]
        else: d['screw']=v[2]; d['arm']=v[3]
        if n in SHARED: d['cnt']=0      # same two screws as SHARED[n]; mass counted once
        st['J'][n]=d; st['cooling'][n]='air'; st['bearing'][n]='CRBH 9016 A' if v[0]=='rotary' and 'CSG-25' in v[2] else 'CRBH 5013 A'
    return st
REV=[]
def rev(it,area,failure,fix): REV.append(dict(it=it,area=area,failure=failure,fix=fix))
def mot(name,w):
    m=PT.MOT[name]; return dict(name=f'{name}{PT.WIND[w]}',Tc=m['Tc130'][w],Tp=m['Tp'][w],Kt=m['Kt_hot'][w],Km=m['Km'][w],Rm=m['Rm'][w],
        Ip=m['Ip'][w],J=m['J_kgcm2']*1e-4,mass=m['mass'],Rth=m['Rth'],OD=int(name[6:9]),stack=int(name[9:11]))
STACK_C={8:14.76,13:19.26,26:32.86}
GEAR_LEN={'CSG-14-100':28,'CSG-17-100':32,'CSG-20-100':36,'CSG-25-100':42,'CSG-32-100':54}   # [EST] axial length of cup+WG
def omega_max(M,T_motor,vbus=VBUS_MIN):
    """Max motor speed at torque T_motor; SVPWM phase-peak limit vbus/sqrt3 (95 %), hot R (x1.4), L neglected. Kt[Nm/Arms]=3/sqrt2*Ke_ph_pk."""
    Ke_ph=M['Kt']*math.sqrt(2)/3; I_pk=math.sqrt(2)*T_motor/M['Kt']; V=vbus/math.sqrt(3)*0.95
    return max(0.0,(V-M['Rm']/2*1.4*I_pk)/Ke_ph)
def housing(M,gear_or_len,bearing):
    b=PT.CRBH[bearing]; D=max(M['OD'],b['D'])+6; L=STACK_C[M['stack']]+(GEAR_LEN[gear_or_len] if isinstance(gear_or_len,str) else gear_or_len)+b['B']+16
    area=math.pi*D*L+2*math.pi/4*D**2; mass=2810e-9*(math.pi*D*L*2.5+2*math.pi/4*D**2*3.0)*1.25
    return dict(D=D,L=L,area_m2=area*1e-6,mass=mass)
def actuator(n,d,st):
    M=mot(d['motor'],d['w']); bear=st['bearing'][n]
    if d['kind']=='rotary':
        g=PT.CSG[d['gear']]; N=g['N']; eta=PT.HD_ETA; nmot=1
        Tmot_peak=min(M['Tp'],I_PEAK*M['Kt']); T_out=min(Tmot_peak*N*eta,g['rep'])
        Hs=housing(M,d['gear'],bear); gm=g['mass'] if g['mass'] else PT.CSG_MASS_EST[d['gear']]
        mass=M['mass']+gm+PT.CRBH[bear]['m']+Hs['mass']+2*(PT.ENC['ring_mass']+PT.ENC['head_mass'])+PT.DRIVE['mass']+0.03+0.04
        ratio=N
    else:
        s=PT.RV[d['screw']]; nmot=2 if d['kind']=='linear2' else 1; eta=s['eta']*0.95
        Tmot_peak=min(M['Tp'],I_PEAK*M['Kt']); F=2*math.pi*Tmot_peak*eta/(s['lead']/1000); F=min(F,s['C0a']/2)
        arm=d['arm']; T_out=F*arm*nmot; ratio=2*math.pi*arm/(s['lead']/1000)
        nut=7850e-9*math.pi/4*(s['D1']**2-s['d']**2)*s['L1']; shaft=7850e-9*math.pi/4*s['d']**2*120
        Hs=housing(M,s['L1']+20,'CRBH 3010 A'); Hs['mass']*=0.8
        mass=M['mass']+nut+shaft+0.08+Hs['mass']+0.10+2*(PT.ENC['ring_mass']+PT.ENC['head_mass'])+PT.DRIVE['mass']
        if n=='knee' and st.get('knee_linkage'): mass+=st['knee_linkage_mass']
        mass=mass*nmot if nmot==2 else mass   # v3.2 FIX: a 2-screw pair was counted as ONE actuator (ankle, wrist pairs under-weighted)
    wm=omega_max(M,0.3*Tmot_peak); wj=wm/ratio
    return dict(M=M,T_out=T_out,ratio=ratio,eta=eta,nmot=nmot,wj=wj,mass=mass,housing=Hs,Tmot_peak=Tmot_peak)
def thermal(A,P_w,P_h,cool):
    M=A['M']; Rwh=0.6*M['Rth']
    fins=2.0 if cool=='air_fins' else 1.0
    Rha=0.25 if cool=='liquid' else 1/(12.0*A['housing']['area_m2']*fins)
    Cw=M['mass']*0.6*450; Ch=A['housing']['mass']*900+M['mass']*0.4*450
    Tw=Th=0.0; Tmax=0.0
    def step(P,dt=2.0):
        nonlocal Tw,Th
        q=(Tw-Th)/Rwh; Tw+=(P-q)/Cw*dt; Th+=(q-Th/Rha)/Ch*dt
    for t in range(1800): step(P_w)
    for c in range(10):
        for t in range(5): step(P_h); Tmax=max(Tmax,Tw)
        for t in range(25): step(P_w)
    return dict(dT_walk=P_w*(Rwh+Rha),dT_max=max(Tmax,Tw),Rwh=Rwh,Rha=Rha)
def cu_loss(A,T_joint):
    M=A['M']; Tm=T_joint/(A['ratio']*A['eta'])/A['nmot']; Km_hot=M['Km']/math.sqrt(1.4)
    return A['nmot']*(Tm/Km_hot)**2, Tm
FALL={}
def fall_model(m,pad_mm):
    zc=0.98; I_pivot=m*0.30**2+m*zc**2; E=m*G*zc; w=math.sqrt(2*E/I_pivot); out=dict(E_J=E,omega=w)
    for site,z,share in [('hip',0.92,0.55),('shoulder',1.50,0.45)]:
        s=(pad_mm*0.7+3)/1000; out[f'{site}_v']=w*z; out[f'{site}_F']=share*E/s
    return out
def bearing_check(n,st,m):
    b=PT.CRBH[st['bearing'][n]]; Dpw=(b['d']+b['D'])/2; BW=m*G
    if n.startswith('hip'):   Fr,Fa,Mw,Ml=1.3*BW,0.2*BW,1.3*BW*0.10,3*BW*0.10
    elif n.startswith('waist'): Fr,Fa,Mw,Ml=0.2*BW,0.75*BW,0.75*BW*0.05,3*0.75*BW*0.08
    elif n=='shoulder_pitch': Fr,Fa,Mw,Ml=60,20,15,FALL.get('shoulder_F',3000)*0.06   # side-fall impact enters through the shoulder cap -> shoulder-pitch output bearing
    elif n.startswith('shoulder'): Fr,Fa,Mw,Ml=60,20,15,10*G*0.40*1.5
    elif n=='elbow': Fr,Fa,Mw,Ml=40,10,5,600*0.03
    else: Fr,Fa,Mw,Ml=20,5,2,10
    def P(Fr,Fa,M):
        q=Fr+2*M*1000/Dpw; X,Y=(1,0.45) if Fa/max(q,1e-9)<=1.5 else (0.67,0.67); return X*q+Y*Fa
    Pw=P(Fr,Fa,Mw); P0=Fr*3/1.3+2*Ml*1000/Dpw+0.44*Fa*3/1.3
    rng,_=GAIT.get(n,(10,0)); rev_per_h=STRIDE_HZ*3600*2*rng/360
    L10_h=(b['C']/Pw)**(10/3)*1e6/rev_per_h
    fs_req=1.0 if n=='shoulder_pitch' else 3.0   # accidental one-off fall: fs>=1 (no brinelling beyond C0 definition); landing/operational shocks: fs>=3
    return dict(bearing=st['bearing'][n],Pw=Pw,L10_h=L10_h,fs=b['C0']/P0,P0=P0,fs_req=fs_req)
def bolted(name,n,size,FA_total,FQ_total,Mt=0.0,r_pcd=0.05,mu_T=0.15,clamp_len=12,phi=0.15):
    """VDI 2230-style (simplified). FA_total = axial load on the bolt group taken as n x max bolt load."""
    tab={4:(0.7,8.78,3.545),5:(0.8,14.2,4.48),6:(1.0,20.1,5.35),8:(1.25,36.6,7.19)}
    P,As,d2=tab[size]; Rp=PT.BOLT129['Rp']; mu=0.12; ds=math.sqrt(4*As/math.pi)
    k=1.5*d2/ds*(P/(math.pi*d2)+1.155*mu); FMzul=0.9*Rp*As/math.sqrt(1+3*k**2)
    FMmin=FMzul/1.6
    dS=clamp_len/(210e3*As); dP=dS*(1-phi)/phi; FZ=0.011/(dS+dP)
    FA=FA_total/n; FQ=FQ_total/n+Mt*1000/(r_pcd*1000)/n
    F_req=FQ/mu_T; F_res=FMmin-(1-phi)*FA-FZ
    sig_max=(FMzul+phi*FA)/As; sig_a=phi*FA/(2*As); sig_ASV=0.85*(150/size+45)
    ok=dict(separation_or_slip=F_res>=F_req,yield_=sig_max<=Rp,fatigue=sig_a<=sig_ASV/1.2)
    return dict(name=name,n=n,size=f'M{size}',FMzul=FMzul,FMmin=FMmin,FZ=FZ,FA=FA,F_res=F_res,F_req=F_req,sig_max=sig_max,sig_a=sig_a,sig_ASV=sig_ASV,ok=all(ok.values()),detail=ok)
_KL=os.path.join(os.path.dirname(os.path.abspath(__file__)),'../cad/out/knee_linkage.json')
KNEE_K=json.load(open(_KL))['selected']['k'] if os.path.exists(_KL) else 1.0
def joint_checks(n,d,st,m,A=None):
    """All single-joint checks; returns (row, list of (fail, detail))."""
    A=A or actuator(n,d,st); r=V2REQ[n]*((m/64.285) if n in LEGSCALE else 1.0); need=1.5*r; fails=[]
    if n=='knee': need/=KNEE_K   # v3.2: slider-crank arm varies over 0-135° (cad/knee_linkage.py); nominal-arm torque must cover the worst angle
    rng,wf=GAIT.get(n,(5,0.1)); Twalk=wf*r
    Pw,Tm_w=cu_loss(A,0.55*Twalk); Ph,Tm_h=cu_loss(A,HOLD.get(n,0.3)*r)
    th=thermal(A,Pw,Ph,st['cooling'][n]); Iph=Tm_h/A['M']['Kt']
    row=dict(joint=n,kind=d['kind'],motor=A['M']['name'],trans=d.get('gear',d.get('screw')),arm=d.get('arm'),req=r,need=need,T=A['T_out'],
             w_need=SPEED[n],w=A['wj'],dT=th['dT_max'],cool=st['cooling'][n],I_hold=Iph,mass=A['mass'],Rha=th['Rha'],P_walk=Pw)
    if A['T_out']<need: fails.append((f'torque {n}',f"{A['T_out']:.0f} < {need:.0f} N·m"))
    if A['wj']<SPEED[n]: fails.append((f'speed {n}',f"{A['wj']:.1f} < {SPEED[n]} rad/s at 30 % torque, {VBUS_MIN:.0f} V bus"))
    if th['dT_max']>DT_LIMIT: fails.append((f'thermal {n}',f"winding ΔT {th['dT_max']:.0f} K > {DT_LIMIT:.0f} K ({st['cooling'][n]}, R_h-a {th['Rha']:.2f} K/W)"))
    if Iph>I_CONT: fails.append((f'drive current {n}',f"{Iph:.1f} A rms hold > {I_CONT:.1f}"))
    wavg=2*math.radians(rng)*STRIDE_HZ*2
    if d['kind']=='rotary':
        g=PT.CSG[d['gear']]; Tav=0.75*Twalk; nav=max(wavg*g['N']*60/(2*math.pi),1)
        L10=PT.HD_LIFE['L10_h']*(g['rated']/max(Tav,1e-6))**3*(PT.HD_LIFE['Nr_rpm']/nav); row.update(life_h=L10,Tav=Tav,nav=nav)
        if L10<LIFE_H: fails.append((f'strain-wave L10 {n}',f'{L10:.0f} h < {LIFE_H:.0f} h'))
        if Twalk>g['rep']: fails.append((f'repeated-peak {n}',''))
        if g['avg'] is not None and Tav>g['avg']: fails.append((f'average-torque {n}',f'{Tav:.0f} > {g["avg"]}'))
        b=bearing_check(n,st,m); row['bearing']=b
        if b['L10_h']<LIFE_H: fails.append((f'output-bearing-L10 {n}',f"{b['bearing']} {b['L10_h']:.0f} h"))
        if b['fs']<b['fs_req']: fails.append((f'output-bearing-static {n}',f"{b['bearing']} fs={b['fs']:.2f}"))
    else:
        s=PT.RV[d['screw']]; Fw=Twalk/d['arm']/A['nmot']; rps=wavg*d['arm']/(s['lead']/1000)
        L10=(s['Ca']/(0.75*Fw))**3*1e6/(rps*3600); Fl=3*m*G*(0.10 if n=='knee' else 0.08)/d['arm']/A['nmot']
        row.update(life_h=L10,F_land=Fl,static=s['C0a']/Fl)
        if L10<LIFE_H: fails.append((f'roller-screw-L10 {n}',f'{L10:.0f} h'))
        if s['C0a']/Fl<2: fails.append((f'roller-screw-static {n}',f"C0a/F {s['C0a']/Fl:.1f}"))
    row['ok']=not fails
    return row,fails
def evaluate(st):
    R=dict(fails=[])
    acts={n:actuator(n,d,st) for n,d in st['J'].items()}
    act_mass=sum(a['mass']*st['J'][n]['cnt'] for n,a in acts.items())
    hb=st['hand']; F=PT.FINGER
    hand_one=hb['flexors']*(F['motor']['mass']+F['gear']['mass']+0.015)+hb['small']*(F['small_motor']['mass']+F['small_gear']['mass']+0.007)+0.35+0.05+(hb['flexors']+hb['small'])*0.025
    cells=13*st['battery']['P']; bat=cells*PT.CELL['mass']*1.25; Wh=cells*PT.CELL['Wh']
    struct=dict(pelvis=1.6,torso=2.8,thigh=2.0,shank=1.6,feet=1.8,arms=1.6,head=1.6,compute=1.8,harness=2.0,covers=1.5+0.06*st['pad_mm']/10*2,
                thermal=1.0+(0.8 if 'liquid' in st['cooling'].values() else 0))
    struct={k:v*st['structure_scale'] for k,v in struct.items()}
    m=act_mass+2*hand_one+bat+sum(struct.values())
    R['mass']=dict(total=m,actuators=act_mass,hands=2*hand_one,battery=bat,battery_Wh=Wh,cells=cells,structure=sum(struct.values()),struct=struct)
    FALL.clear(); FALL.update(fall_model(m,st['pad_mm']))
    rows=[]
    for n,d in st['J'].items():
        row,f=joint_checks(n,d,st,m,acts[n]); rows.append(row); R['fails']+=f
    R['rows']=rows
    Tsh=FALL['shoulder_F']*0.15; g=PT.CSG[st['J']['shoulder_roll']['gear']]; lim=st['clutch'].get('shoulder_roll'); Teff=min(Tsh,lim) if lim else Tsh
    R['fall_gear']=dict(T_impact=Tsh,T_eff=Teff,mom=g['mom'],ratchet=g['ratchet'],clutch=lim)
    if Teff>g['mom']: R['fails'].append(('fall-shoulder-gear',f'{Teff:.0f} N·m > momentary peak {g["mom"]} (ratcheting {g["ratchet"]})'))
    BW=m*G; bl=[]; B=st['bolts']
    n_,s_=B.get('hip_bracket',(8,5)); bl.append(bolted('hip bracket → pelvis (landing 3BW + 0.10 m moment)',n_,s_,FA_total=3*BW+4*3*BW*0.10/0.11,FQ_total=0.5*BW))
    n_,s_=B.get('hip_pitch_output',(8,4)); bl.append(bolted('hip-pitch flexspline → output flange (momentary peak by friction)',n_,s_,0,0,Mt=PT.CSG[st['J']['hip_pitch']['gear']]['mom'],r_pcd=0.0335))
    n_,s_=B.get('knee_bracket',(4,5)); bl.append(bolted('knee clevis → femur flange (landing 3BW, 0.12 m lever)',n_,s_,FA_total=4*3*BW*0.12/0.06,FQ_total=0.3*BW))
    n_,s_=B.get('shoulder_mount',(6,5)); bl.append(bolted('shoulder actuator → torso frame (side-fall impact)',n_,s_,FA_total=4*FALL['shoulder_F']*0.06/0.09,FQ_total=FALL['shoulder_F']))
    for b in bl:
        if not b['ok']: R['fails'].append((f"bolted {b['name']}",', '.join(k for k,v in b['detail'].items() if not v)))
    R['bolts']=bl
    T_spool=min(F['motor']['T_cont']*hb['ratio']*F['gear']['eta'],F['gear']['T_cont']); tension=T_spool/hb['spool_r']; tip=tension*0.009/0.065
    SFt=F['tendon']['F_break']/tension; grasps=LIFE_H*120
    R['hand']=dict(T_spool=T_spool,tension=tension,tip=tip,SF_tendon=SFt,grasps_5y=grasps,evidence=31826,closing_s=0.030/(10800/hb['ratio']*2*math.pi/60*hb['spool_r']))
    if tip<30: R['fails'].append(('hand-grip',f'{tip:.1f} N < 30 N continuous fingertip'))
    if SFt<4: R['fails'].append(('tendon-static',f'SF {SFt:.1f} < 4'))
    R['fails'].append(('tendon-fatigue-UNVERIFIABLE',f'needs {grasps:.2e} bend cycles; published evidence ≤ 5e4 (D/d 4, 150 N)'))
    cp=os.path.join(H,'../cad/out/cables.json'); R['cables']=json.load(open(cp)) if os.path.exists(cp) else None
    if R['cables']:
        for c in R['cables']['joints']:
            if c['r_min_mm']<c['r_req_mm']: R['fails'].append((f"cable-bend {c['joint']}",f"{c['r_min_mm']:.0f} < {c['r_req_mm']:.0f} mm"))
    fp=os.path.join(H,'../cad/out/fea_v3.json'); R['fea']=json.load(open(fp)) if os.path.exists(fp) else {}
    for k,v in R['fea'].items():
        lim=2.0   # v3.2: fall cases also need SF >= 2 (was 1.0: one-off load, but repeated falls over the robot's life)
        if v.get('SF_yield',9)<lim: R['fails'].append((f'FEA-yield {k}',f"SF {v['SF_yield']:.2f} < {lim}"))
        if v.get('goodman',9)<1.5: R['fails'].append((f'FEA-fatigue {k}',f"Goodman SF {v['goodman']:.2f} < 1.5"))
        if v.get('converged') is False: R['fails'].append((f'FEA-convergence {k}',f"last refinement changed peak {(v.get('delta_pct') or 0):.0f} %" if v.get('delta_pct') is not None else 'only one mesh level'))
    P_walk=sum(rw['P_walk']*st['J'][rw['joint']]['cnt'] for rw in rows)
    mech=0.25*m*G*1.2*1.3; P_tot=mech+P_walk+120+3.3*sum(d['cnt'] for d in st['J'].values())+40
    R['power']=dict(P_walk_cu=P_walk,P_mech=mech,P_total=P_tot,runtime_h=Wh*0.9/P_tot)
    if R['power']['runtime_h']<2.0: R['fails'].append(('battery-runtime',f"{R['power']['runtime_h']:.1f} h < 2 h walking"))
    if m>65.0: R['fails'].append(('mass-target',f'{m:.1f} kg > 65 kg'))
    R['m']=m
    return R
def sync_shared(st):
    for a,b in SHARED.items():
        for k in ('motor','w','screw'): st['J'][a][k]=st['J'][b][k]
        st['cooling'][a]=st['cooling'][b]
def fix_actuator(st,n,m):
    if n in SHARED: n=SHARED[n]
    d=st['J'][n]; best=None
    cand=['CSG-14-100','CSG-17-100','CSG-20-100','CSG-25-100','CSG-32-100'] if d['kind']=='rotary' else list(PT.RV)
    ARMCAP={'knee':0.0585,'ankle_pitch':0.070,'wrist_pitch':0.030}   # packaging limits from the v2/v3 CAD envelopes
    arms=[None] if d['kind']=='rotary' else sorted(set(min(ARMCAP.get(n,1),round(d['arm']*f,4)) for f in (0.87,1.0,1.15,1.3)))
    lim={'CSG-14-100':60,'CSG-17-100':68,'CSG-20-100':85,'CSG-25-100':94,'CSG-32-100':115}
    for mname in PT.MOT:
        for w in range(3):
            for g in cand:
                if d['kind']=='rotary' and int(mname[6:9])>lim[g]: continue
                for arm in arms:
                  for kind in ((d['kind'],) if n!='knee' else ('linear','linear2')):   # v3.2: knee may use two parallel screws (single one cannot reach torque + speed over 0-135°)
                    for cool in ('air','air_fins','liquid'):
                        t=copy.deepcopy(st); dd=t['J'][n]; dd['motor']=mname; dd['w']=w; t['cooling'][n]=cool; dd['kind']=kind if d['kind']!='rotary' else 'rotary'
                        if d['kind']=='rotary': dd['gear']=g
                        else: dd['screw']=g; dd['arm']=arm
                        if d['kind']=='rotary':   # pick smallest bearing that passes for this config
                            for bn in PT.CRBH:
                                t['bearing'][n]=bn; b=bearing_check(n,t,m)
                                if b['L10_h']>=LIFE_H and b['fs']>=b['fs_req']: break
                        row,f=joint_checks(n,dd,t,m)
                        if f: continue
                        sl=[a for a,b in SHARED.items() if b==n]
                        if sl:
                            sync_shared(t); r2,f2=joint_checks(sl[0],t['J'][sl[0]],t,m)
                            if f2: continue
                        cost=row['mass']+(0.4 if cool=='liquid' else 0)+(0.05 if cool=='air_fins' else 0)
                        if best is None or cost<best[0]: best=(cost,t,row)
    if best is None: return None
    def desc(s):
        dd=s['J'][n]; return f"{dd['motor']}{PT.WIND[dd['w']]} + {dd.get('gear',dd.get('screw'))}"+('' if dd['kind']=='rotary' else f" arm {dd['arm']*1000:.0f} mm")+f" [{s['cooling'][n]}; {s['bearing'][n] if dd['kind']=='rotary' else ''}]"
    old=desc(st); st['J'][n]=best[1]['J'][n]; st['cooling'][n]=best[1]['cooling'][n]; st['bearing'][n]=best[1]['bearing'][n]
    sync_shared(st)
    return old,desc(st),best[2]
def run(extra=None):
    st=initial_state()
    if extra: extra(st)
    R=evaluate(st); first=R
    for f,dt in R['fails']: rev(0,'v3.0 = v2 with catalog parts substituted 1:1',f'{f}: {dt}','(see later iterations)')
    for it in range(1,12):
        changed=False
        bad=sorted(set(f.split(' ')[-1] for f,_ in R['fails'] if f.split(' ')[-1] in st['J']))
        for n in bad:
            dts='; '.join(f'{f} ({d})' for f,d in R['fails'] if f.endswith(' '+n))
            res=fix_actuator(st,n,R['m'])
            if res: rev(it,f'actuator {n}',dts,f'{res[0]} → {res[1]}'); changed=True
            else: rev(it,f'actuator {n}',dts,'NO catalog combination passes all checks (out of reach with these part families)')
        for f,dt in R['fails']:
            if f=='fall-shoulder-gear' and 'shoulder_roll' not in st['clutch']:
                st['clutch']['shoulder_roll']=300; st['pad_mm']=max(st['pad_mm'],30)
                rev(it,'side fall',f'{f}: {dt}','friction overload clutch at shoulder-roll output (slip 300 N·m < 369 N·m momentary peak) + 30 mm EPP pads on shoulder/hip'); changed=True
            if f.startswith('bolted'):
                key={'hip bracket':'hip_bracket','hip-pitch':'hip_pitch_output','knee clevis':'knee_bracket','shoulder actuator':'shoulder_mount'}
                k=[v for kk,v in key.items() if kk in f][0]
                n0,s0=st['bolts'].get(k,{'hip_bracket':(8,5),'hip_pitch_output':(8,4),'knee_bracket':(4,5),'shoulder_mount':(6,5)}[k])
                n1,s1=(n0,{4:5,5:6,6:8}[s0]) if s0<8 else (n0+2,s0)
                st['bolts'][k]=(n1,s1); rev(it,'bolted joint',f'{f}: {dt}',f'{n0}×M{s0} → {n1}×M{s1} (12.9)'); changed=True
            if f=='battery-runtime':
                st['battery']['P']+=1; rev(it,'battery',f'{f}: {dt}',f"13S{st['battery']['P']-1}P → 13S{st['battery']['P']}P (P45B)"); changed=True
            if f=='hand-grip' and st['hand']['spool_r']>0.0031:
                st['hand']['spool_r']-=0.001; rev(it,'hand',f'{f}: {dt}',f"flexor spool radius {st['hand']['spool_r']*1000+1:.0f} → {st['hand']['spool_r']*1000:.0f} mm"); changed=True
        R=evaluate(st)
        if not changed:
            # mass-down pass: every joint re-selected as the lightest catalog combination that passes all checks at the current mass
            lighter=False
            for n,d in st['J'].items():
                if n in SHARED: continue
                m0=evaluate(st)['m']; snap=copy.deepcopy(st)
                res=fix_actuator(st,n,R['m'])
                if res and res[0]!=res[1]:
                    m1=evaluate(st)['m']
                    if m1<m0-0.01: rev(it,f'actuator {n} (mass reduction)',f'passing but oversized; robot {m0:.1f} kg',f'{res[0]} → {res[1]} (−{m0-m1:.2f} kg)'); lighter=True
                    else: st.clear(); st.update(snap)
            # v3.2: battery is part of the mass-down pass (it was only ever increased): smallest 13S·xP pack that still gives >= 2 h walking
            while st['battery']['P']>1:
                m0=evaluate(st)['m']; st['battery']['P']-=1; R2=evaluate(st)
                if R2['power']['runtime_h']>=2.0 and not any(f=='battery-runtime' for f,_ in R2['fails']):
                    rev(it,'battery (mass reduction)',f'runtime {evaluate(dict(st,battery=dict(st["battery"],P=st["battery"]["P"]+1)))["power"]["runtime_h"]:.1f} h > 2 h; robot {m0:.1f} kg',f"13S{st['battery']['P']+1}P → 13S{st['battery']['P']}P (−{m0-R2['m']:.2f} kg, runtime {R2['power']['runtime_h']:.1f} h)"); lighter=True
                else: st['battery']['P']+=1; break
            R=evaluate(st)
            if not lighter: break
    return st,first,R
def fmt(R,st,title):
    m=R['mass']
    o=[f"# {title}\n\nMass from catalog-part rollup: **{R['m']:.1f} kg** — actuators {m['actuators']:.1f}, hands {m['hands']:.1f}, battery {m['battery']:.1f} kg ({m['cells']} × Molicel P45B = {m['battery_Wh']:.0f} Wh), structure/harness/covers {m['structure']:.1f}.",
       f"Requirements: 5 y × 365 d × 8 h walking = {LIFE_H:.0f} h; {STRIDE_HZ:.0f} stride/s → {LIFE_H*3600*STRIDE_HZ:.2e} cycles per leg; bus {VBUS_MIN:.1f} V (13S at 3.4 V/cell); drive {I_CONT:.1f} A rms continuous / {I_PEAK:.1f} A rms for 1 s (Everest XCR crest ratings ÷ √2); winding rise ≤ {DT_LIMIT:.0f} K at {AMB:.0f} °C ambient; torque ≥ 1.5 × requirement.\n",
       '## Actuators\n','| joint | motor | transmission | torque avail / need N·m | speed avail / need rad/s | winding ΔT K (cooling, R_h-a) | hold A rms | life L10 h | kg | result |','|---|---|---|---|---|---|---|---|---|---|']
    for r in R['rows']:
        tr=r['trans']+('' if r['kind']=='rotary' else f" / {r['arm']*1000:.0f} mm arm")
        o.append(f"| {r['joint']} | {r['motor']} | {tr} | {r['T']:.0f} / {r['need']:.0f} | {r['w']:.1f} / {r['w_need']} | {r['dT']:.0f} ({r['cool']}, {r['Rha']:.2f} K/W) | {r['I_hold']:.1f} | {r.get('life_h',0):.1e} | {r['mass']:.2f} | {'PASS' if r['ok'] else '**FAIL**'} |")
    o+=['\n## Output bearings (IKO CRBH; walking L10, landing/fall static safety fs ≥ 3)\n','| joint | bearing | P walk N | L10 h | fs (required) | result |','|---|---|---|---|---|---|']
    for r in R['rows']:
        if 'bearing' in r: b=r['bearing']; o.append(f"| {r['joint']} | {b['bearing']} | {b['Pw']:.0f} | {b['L10_h']:.1e} | {b['fs']:.1f} ({b['fs_req']:.0f}) | {'PASS' if b['L10_h']>=LIFE_H and b['fs']>=b['fs_req'] else '**FAIL**'} |")
    o+=['\n## Bolted joints (VDI 2230-style; 12.9; μG=μK=0.12; αA=1.6; fz=11 µm; Φ=0.15 [EST])\n','| joint | bolts | FM,min kN | residual clamp kN | needed kN | σ max MPa | σa / σASV MPa | result |','|---|---|---|---|---|---|---|---|']
    for b in R['bolts']: o.append(f"| {b['name']} | {b['n']}×{b['size']} | {b['FMmin']/1000:.1f} | {b['F_res']/1000:.1f} | {b['F_req']/1000:.1f} | {b['sig_max']:.0f} | {b['sig_a']:.0f} / {b['sig_ASV']:.0f} | {'PASS' if b['ok'] else '**FAIL**'} |")
    f=FALL; fg=R['fall_gear']
    o+=[f"\n## Side fall from standing (energy method)\nEnergy {f['E_J']:.0f} J; topple rate at impact {f['omega']:.2f} rad/s; hip contact {f['hip_v']:.1f} m/s → {f['hip_F']/1000:.1f} kN; shoulder {f['shoulder_v']:.1f} m/s → {f['shoulder_F']/1000:.1f} kN (pad {st['pad_mm']} mm, 70 % usable crush + 3 mm structure, constant-force crush, 55/45 hip/shoulder split [EST]). These forces drive the fall FEA cases.",
        f"Shoulder-roll strain wave: impact torque {fg['T_impact']:.0f} N·m (force on upper arm 0.15 m below the axis) vs momentary peak {fg['mom']} / ratcheting {fg['ratchet']} N·m → with overload clutch {fg['T_eff']:.0f} N·m.\n"]
    h=R['hand']
    o+=[f"## Hand drive\nPer hand: {st['hand']['flexors']} flexor drives (maxon DCX 22 S + GPX 22 HP {st['hand']['ratio']}:1, Ø{st['hand']['spool_r']*2000:.0f} mm spool) + {st['hand']['small']} small drives (DCX 16 S + GPX 16 LN 103:1) for abduction/thumb rotation, extension by return springs. Continuous spool torque {h['T_spool']:.2f} N·m → tendon {h['tension']:.0f} N → **{h['tip']:.1f} N continuous fingertip force** (MCP tendon arm 9 mm, contact 65 mm from MCP in a power grasp [EST geometry]); full close (30 mm tendon) in {h['closing_s']:.2f} s. Tendon LIROS D-Pro 1 mm (195 daN): static SF {h['SF_tendon']:.1f}. Bend fatigue: {h['grasps_5y']:.2e} grasps in 5 y vs ≤ 5×10⁴ cycles of published evidence → not demonstrable without testing.\n"]
    p=R['power']; o+=[f"## Power\nWalking: mechanical {p['P_mech']:.0f} W + copper {p['P_walk_cu']:.0f} W + compute/drives/sensors → {p['P_total']:.0f} W → runtime {p['runtime_h']:.1f} h ({m['battery_Wh']:.0f} Wh, 90 % usable).\n"]
    if R['fea']:
        o+=['## Structure FEA (v3/cad/out/fea_v3.md)\n','| case | peak vM MPa | SF yield | Goodman SF (5 y) | converged |','|---|---|---|---|---|']
        for k,v in R['fea'].items(): o.append(f"| {k} | {v.get('vm',0):.0f} | {v.get('SF_yield',0):.2f} | {('%.2f'%v['goodman']) if 'goodman' in v else '—'} | {v.get('converged','—')} |")
    if R['cables']:
        o+=['\n## Cable routing (igus CFROBOT rule: bend radius ≥ 10 × d when moving)\n','| joint | cable Ø mm | min radius mm | required mm | result |','|---|---|---|---|---|']
        for c in R['cables']['joints']: o.append(f"| {c['joint']} | {c['d_mm']} | {c['r_min_mm']:.0f} | {c['r_req_mm']:.0f} | {'PASS' if c['r_min_mm']>=c['r_req_mm'] else '**FAIL**'} |")
    o+=['\n## Open failures\n']+([f'- {a}: {b}' for a,b in R['fails']] or ['- none'])
    return '\n'.join(o)
if __name__=='__main__':
    st,first,R=run()
    open(os.path.join(H,'results/v3_initial.md'),'w').write(fmt(first,initial_state(),'v3.0 — v2 with catalog parts substituted (before fixes)'))
    open(os.path.join(H,'results/v3_checks.md'),'w').write(fmt(R,st,'v3 hardening checks (final)'))
    json.dump(dict(state=st,mass=R['mass'],fails=R['fails'],rows=R['rows'],bolts=R['bolts'],fall=FALL,fall_gear=R['fall_gear'],hand=R['hand'],power=R['power'],m=R['m']),
              open(os.path.join(H,'results/v3.json'),'w'),indent=1,default=str)
    json.dump(REV,open(os.path.join(H,'results/revisions_analysis.json'),'w'),indent=1)
    print('initial fails',len(first['fails']),'final fails',len(R['fails']),'mass %.1f'%R['m'])
    for f in R['fails']: print('  FAIL',f)
