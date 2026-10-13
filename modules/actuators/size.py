"""RL Actuators round 1 (2026-10-13): re-size leg actuators to gait-ID needs (P-001/P-002), power/energy (P-004).
Reuses v3/analysis models (actuator(), housing(), cu_loss(), omega_max()). Run: python3 size.py -> results/"""
import sys, os, json, math, itertools, numpy as np
H=os.path.dirname(os.path.abspath(__file__)); R=os.path.join(H,'../..'); sys.path.insert(0,os.path.join(R,'v3/analysis'))
os.chdir(os.path.join(R,'v3/analysis'))
import v3, parts as PT
os.chdir(H)
LEGS=os.path.join(R,'modules/legs/results')
LEG=['hip_yaw','hip_roll','hip_pitch','knee','ankle_pitch','ankle_roll']
DESIGN=['walk_0p8','walk_1p0','walk_1p2','stairs_18cm','push_recover','sit_to_stand']   # carry_20kg = stretch only (Robot Lab instruction, pending Arbiter on T5)
E=json.load(open(f'{LEGS}/envelope.json'))['per_scenario']
# Harmonic Drive CSG-2A ratio 50/80 ratings (harmonicdrive.net CSG-2A rating table + product pages CSG-32-50-2A-GR, CSG-40-50-2A-GR; catalog csf-csg.pdf)
PT.CSG.update({
 'CSG-20-50':dict(N=50,rated=33,rep=73,mom=127,avg=44,ratchet=None,mass=0.28),
 'CSG-25-50':dict(N=50,rated=51,rep=127,mom=242,avg=72,ratchet=None,mass=0.42),
 'CSG-25-80':dict(N=80,rated=82,rep=178,mom=332,avg=113,ratchet=None,mass=0.42),
 'CSG-32-50':dict(N=50,rated=99,rep=281,mom=497,avg=140,ratchet=None,mass=0.89),
 'CSG-32-80':dict(N=80,rated=153,rep=395,mom=738,avg=217,ratchet=None,mass=0.89),
 'CSG-40-50':dict(N=50,rated=178,rep=523,mom=892,avg=255,ratchet=None,mass=1.7),
 'CSG-40-100':dict(N=100,rated=345,rep=738,mom=1400,avg=484,ratchet=None,mass=1.7)})
v3.GEAR_LEN.update({'CSG-20-50':36,'CSG-25-50':42,'CSG-25-80':42,'CSG-32-50':54,'CSG-32-80':54,'CSG-40-50':66,'CSG-40-100':66})  # [EST] as v3
NIN_GREASE={14:8500,17:7300,20:6500,25:5600,32:4800,40:4000}   # max input rpm, grease (CSG catalog; size 17 [EST])
BEAR={14:'CRBH 6013 A',17:'CRBH 6013 A',20:'CRBH 6013 A',25:'CRBH 6013 A',32:'CRBH 8016 A',40:'CRBH 9016 A'}   # hips: v3 final selection CRBH 6013 A passed v3 bearing_check (hip loads); larger gears need a larger bore [EST]
ARMCAP={'knee':0.0585,'ankle_pitch':0.070,'hip_pitch':0.080}   # hip_pitch 80 mm [EST] packaging, needs Legs geometry check
MARGIN=float(os.environ.get('MARGIN',1.5))
# ---- round-1 architecture decisions (see results/DECISIONS.md)
BUS_S=20; v3.omega_max.__defaults__=(BUS_S*3.4,)              # D2: 20S bus, 68.0 V min (3.4 V/cell) .. 84.0 V max
TWITTER=dict(name='Elmo Gold Twitter G-TWI R70/100 EtherCAT',Ic_rms=49.5,Vmax=95,mass=0.0222,src='https://www.elmomc.com/product/gold-twitter/')
v3.I_PEAK=TWITTER['Ic_rms']; v3.I_CONT=TWITTER['Ic_rms']; PT.DRIVE['mass']=TWITTER['mass']   # D3: peak taken = continuous Ic (no peak credit) [conservative]
K_HIP=0.77   # [EST] slider-crank arm factor for hip_pitch twin screw over the loaded gait ROM (-76..+4 deg): cos(40 deg); replace by a linkage study like v3 cad/knee_linkage.py
# ---- requirements
req={}
for j in LEG:
    pk=max(E[s][j]['peak_Nm'] for s in DESIGN); ps=max(DESIGN,key=lambda s:E[s][j]['peak_Nm'])
    rms=max(E[s][j]['rms_Nm'] for s in DESIGN if s.startswith(('walk','stairs')))
    w=max(E[s][j]['speed_at30_rads'] for s in DESIGN); w=max(w,v3.SPEED[j]) if j in('hip_yaw','hip_roll','ankle_roll') else w
    c=E['carry_20kg'][j]
    req[j]=dict(peak=pk,peak_case=ps,need=MARGIN*pk,rms=rms,speed=w,carry_peak=c['peak_Nm'],carry_rms=c['rms_Nm'],carry_w=c['speed_at30_rads'])
KK=v3.KNEE_K
# gait tau-omega samples per joint (both sides) for the envelope check
TW={j:[] for j in LEG}
for sc in DESIGN:
    d=np.load(f'{LEGS}/{sc}.npz'); va=d['va']
    for i,j in enumerate(LEG):
        for off in (0,6): TW[j].append(np.c_[np.abs(d['TAU'][:,va[i+off]]),np.abs(d['V'][:,va[i+off]])])
def hull(a,nb=40):
    a=a[a[:,1]>0.5]; e=np.linspace(0,a[:,0].max()+1e-6,nb+1); o=[]
    for k in range(nb):
        m=(a[:,0]>=e[k])&(a[:,0]<e[k+1])
        if m.any(): o.append([e[k+1],a[m,1].max()])   # conservative: bin upper torque edge
    return np.array(o)
TWRAW={j:np.vstack(v) for j,v in TW.items()}; TW={j:hull(v) for j,v in TWRAW.items()}
def w_at(A,Tj):   # joint speed available at joint torque Tj (voltage limit, v3.omega_max model)
    Tm=np.atleast_1d(Tj)/(A['ratio']*A['eta'])/A['nmot']
    return np.array([v3.omega_max(A['M'],t) for t in Tm])/A['ratio']
def evalA(j,d):
    st=dict(bearing={j:d.get('bear','CRBH 5013 A')})
    A=v3.actuator(j,d,st); r=req[j]; g=PT.CSG.get(d.get('gear'))
    need=r['need']/(KK if j=='knee' else K_HIP if (j=='hip_pitch' and d['kind']=='linear2') else 1)
    Tm_rms=r['rms']/(A['ratio']*A['eta'])/A['nmot']; Km=A['M']['Km']/math.sqrt(1.4)
    cu=A['nmot']*(Tm_rms/Km)**2
    Hs=A['housing']; fins=2.0; Rha=1/(12.0*Hs['area_m2']*fins); Rwh=0.6*A['M']['Rth']
    dT=cu/A['nmot']*Rwh+cu*Rha            # per-motor winding->housing + shared housing->air (air_fins)
    I_rms=Tm_rms/A['M']['Kt']
    T30=0.3*r['peak']; ws=float(w_at(A,T30)[0])
    tw=TW[j]
    if j=='knee': tw=tw*[1/KK,1]
    if j=='hip_pitch' and d['kind']=='linear2': tw=tw*[1/K_HIP,1]
    inside=bool(np.all(tw[:,1]<=w_at(A,tw[:,0]) )) if len(tw) else True
    A['w30']=ws
    ok=dict(torque=A['T_out']>=need,speed=ws>=r['speed'],envelope=inside,thermal=dT<=v3.DT_LIMIT,cont=Tm_rms<=A['M']['Tc'],drive=I_rms<=v3.I_CONT)
    ok['motor_nmax']=r['speed']*A['ratio']*60/(2*math.pi)<=PT.MOT[d['motor']]['Nmax'][d['w']]
    if g: ok['input_rpm']=r['speed']*g['N']*60/(2*math.pi)<=NIN_GREASE[int(d['gear'].split('-')[1])]; ok['avg']=r['rms']<= (g['avg'] or 1e9)
    return dict(A=A,need=need,cu=cu,dT=dT,I_rms=I_rms,Tm_rms=Tm_rms,ok=ok,pass_=all(ok.values()),mass=A['mass'])
def candidates(j):
    for mname in PT.MOT:
        for w in range(3):
            if j in('knee','ankle_pitch','hip_pitch'):
                for s in PT.RV:
                    for arm in np.arange(0.040,ARMCAP[j]+1e-9,0.0025 if j!='hip_pitch' else 0.005):
                        yield dict(kind='linear2',motor=mname,w=w,screw=s,arm=round(float(arm),4))
            if j in('hip_yaw','hip_roll','hip_pitch'):
                for g in PT.CSG:
                    yield dict(kind='rotary',motor=mname,w=w,gear=g,bear=BEAR[int(g.split('-')[1])])
# ---- selection: lightest passing candidate per joint
def select(j):
    xs=[(evalA(j,d),d) for d in candidates(j)]; ok=[x for x in xs if x[0]['pass_']]
    if j=='ankle_pitch': ok=[x for x in ok if evalA('ankle_roll',dict(x[1],arm=0.04))['pass_']]   # differential pair also serves ankle_roll (v3 SHARED)
    ok.sort(key=lambda x:x[0]['mass']); return ok[0] if ok else None
best={j:select(j) for j in LEG[:-1]}
best['ankle_roll']=(evalA('ankle_roll',dict(best['ankle_pitch'][1],arm=0.04)),dict(best['ankle_pitch'][1],arm=0.04))
# ---- v3 baseline under its own conditions (13S, Everest XCR) with the new needs
def baseline():
    keep=(v3.omega_max.__defaults__,v3.I_PEAK,v3.I_CONT,PT.DRIVE['mass'])
    v3.omega_max.__defaults__=(13*3.4,); v3.I_PEAK=60/math.sqrt(2); v3.I_CONT=45/math.sqrt(2); PT.DRIVE['mass']=0.038
    _s=json.load(open(os.path.join(R,'v3/analysis/results/v3.json')))['state']; V3J=_s['J']; V3B=_s['bearing']; o={}
    for j in LEG:
        d=dict(V3J[j]); 
        if d['kind']=='rotary': d['bear']=V3B[j]
        e=evalA(j,d); o[j]=dict(sel=f"{d['motor']}{'ACD'[d['w']]} + {d.get('gear',d.get('screw'))}"+(f" arm {d['arm']*1000:.1f} mm" if 'arm' in d else ''),
            curve=[(float(T),float(w_at(e['A'],T)[0])) for T in np.linspace(0,e['A']['T_out'],30)],
            mass=e['mass'],T=e['A']['T_out'],w30=e['A']['w30'],motor_rpm_at_need=req[j]['speed']*e['A']['ratio']*60/(2*math.pi),fails=[k for k,v in e['ok'].items() if not v])
    v3.omega_max.__defaults__,v3.I_PEAK,v3.I_CONT,PT.DRIVE['mass']=keep; return o
BASE=baseline()
# ---- twin-screw linkage hardware not in the v3 actuator() mass (decision D5) [EST]
LINK={'hip_pitch':0.25,'knee':0.25,'ankle_pitch':0.15,'ankle_roll':0.0,'hip_yaw':0,'hip_roll':0}
def label(d): return f"{d['motor']}{'ACD'[d['w']]} + "+(f"{d['gear']} (CSG-2A) + {d['bear']}" if d['kind']=='rotary' else f"2× {d['screw']} roller screw, arm {d['arm']*1000:.1f} mm")
SEL={}
for j in LEG:
    e,d=best[j]; A=e['A']; r=req[j]
    cnt=0 if j=='ankle_roll' else 2
    carry_ok=dict(torque_ratio=A['T_out']*(KK if j=='knee' else K_HIP if (j=='hip_pitch' and d['kind']=='linear2') else 1)/r['carry_peak'],
        w_at_carry30=float(w_at(A,0.3*r['carry_peak']/(KK if j=='knee' else 1))[0]),carry_w=r['carry_w'])
    Tm_c=r['carry_rms']/(A['ratio']*A['eta'])/A['nmot']; cu_c=A['nmot']*(Tm_c/(A['M']['Km']/math.sqrt(1.4)))**2
    carry_ok['dT_carry']=cu_c/A['nmot']*0.6*A['M']['Rth']+cu_c/(12*A['housing']['area_m2']*2)
    SEL[j]=dict(label=label(d),d=d,cnt=cnt,mass=e['mass']+LINK[j] if cnt else 0.0,mass_model=e['mass'],link=LINK[j],T_out=A['T_out'],need=e['need'],
        w30=A['w30'],speed_need=r['speed'],ratio=A['ratio'],eta=A['eta'],nmot=A['nmot'],Km=A['M']['Km'],Kt=A['M']['Kt'],Rm=A['M']['Rm'],
        cu_rms=e['cu'],dT=e['dT'],I_rms=e['I_rms'],motor_rpm=r['speed']*A['ratio']*60/(2*math.pi),ok=e['ok'],carry=carry_ok,D=A['housing']['D'],L=A['housing']['L'])
    print(f"{j:12s} {SEL[j]['label']:60s} m {SEL[j]['mass']:.2f} T {A['T_out']:.0f}/{e['need']:.0f} w {A['w30']:.1f}/{r['speed']:.1f} dT {e['dT']:.0f} carryT x{carry_ok['torque_ratio']:.2f}")
# ---- power & energy from gait time series (both legs, 12 joints)
ETA_DRV=0.98   # [EST] Gold Twitter >99 % at rated power (datasheet); 98 % incl. light-load switching
def power(sc):
    d=np.load(f'{LEGS}/{sc}.npz'); va=d['va']; t=d['t']; Pj={}; P_noregen=0; P_net=0
    for i,j in enumerate(LEG):
        s=SEL[j]; A_r,A_e,n=s['ratio'],s['eta'],s['nmot']; Kmh=s['Km']/math.sqrt(1.4)
        for off in (0,6):
            tau=d['TAU'][:,va[i+off]].astype(float); w=d['V'][:,va[i+off]].astype(float)
            if j=='knee': pass
            p=tau*w; pin=np.where(p>=0,p/A_e,p*A_e)
            Tm=np.abs(tau)/(A_r*A_e)/n; cu=n*(Tm/Kmh)**2
            pe=(pin+cu)/ETA_DRV; Pj.setdefault(j,[]).append(pe)
            P_noregen=P_noregen+np.maximum(pin,0)/ETA_DRV+cu/ETA_DRV; P_net=P_net+pe
    side=[sum(Pj[j][k] for j in LEG) for k in (0,1)]
    return dict(mean_noregen=float(P_noregen.mean()),mean_netbus=float(np.maximum(P_net,0).mean()),peak_legs=float(P_net.max()),
        peak_limb=float(max(x.max() for x in side)),peak_joint={j:float(max(np.max(x) for x in Pj[j])) for j in LEG},
        mean_cu=float(sum(np.mean((np.maximum(0,0)) ) for j in LEG)),mech_pos=float(sum(np.maximum(d['TAU'][:,va[k]]*d['V'][:,va[k]],0).mean() for k in range(12))))
PW={sc:power(sc) for sc in ['walk_0p8','walk_1p0','walk_1p2','stairs_18cm','carry_20kg','push_recover']}
OTHER=dict(compute=120,sensors=40,drive_idle=26*3.3,other_copper=8.0)   # v3.json power lines; other-joint copper from CONTRACTS §1a rows [v3]
P_OTH=sum(OTHER.values())
CELLS=dict(S=BUS_S,P=5); NC=CELLS['S']*CELLS['P']; WH=NC*PT.CELL['Wh']; BATT_KG=NC*PT.CELL['mass']*1.25
EN={}
for sc in ['walk_0p8','walk_1p0','walk_1p2','carry_20kg']:
    for k in ('mean_noregen','mean_netbus'):
        P=PW[sc][k]+P_OTH; EN[f'{sc}/{k}']=dict(P_total=P,runtime_h_1620=WH*0.9/P,runtime_h_1474=1474.2*0.9/P,Wh_for_2h=2*P/0.9)
# ---- mass rollup
V3M=json.load(open(os.path.join(R,'v3/analysis/results/v3.json')))['mass']
leg_new=sum(SEL[j]['mass']*SEL[j]['cnt'] for j in LEG); leg_v3=15.36
drive_delta=(26-12)*(TWITTER['mass']-0.038)+12*0  # leg drives already in leg_new; 14 non-leg drives swap to Gold Twitter R50/100 (same 22.2 g package)
leg_v3_drives=0  # v3 leg rows (15.36 kg CONTRACTS §2) include XCR drives; new rows include Twitter drives
batt_delta=BATT_KG-V3M['battery']
total=V3M['total']-leg_v3+leg_new+drive_delta+batt_delta
MASS=dict(v3_total=V3M['total'],leg_act_v3=leg_v3,leg_act_new=leg_new,drive_delta_nonleg=drive_delta,battery_new=BATT_KG,battery_delta=batt_delta,total_new=total,limit=65.0)
print('MASS',{k:round(v,2) for k,v in MASS.items()})
for k,v in EN.items(): print('EN',k,{a:round(b,2) for a,b in v.items()})
for k,v in PW.items(): print('PW',k,round(v['mean_noregen']),round(v['mean_netbus']),'peak legs',round(v['peak_legs']),'limb',round(v['peak_limb']),{a:round(b) for a,b in v['peak_joint'].items()})
tag='' if MARGIN==1.5 else f'_m{MARGIN:g}'
json.dump(dict(margin=MARGIN,bus=dict(S=BUS_S,Vmin=BUS_S*3.4,Vmax=BUS_S*4.2),drive=TWITTER,K_HIP=K_HIP,KNEE_K=KK,req=req,sel=SEL,base=BASE,power=PW,other_W=OTHER,energy=EN,
    battery=dict(cells=CELLS,Wh=WH,kg=BATT_KG),mass=MASS),open(f'results/sizing{tag}.json','w'),indent=1,default=lambda o:float(o) if hasattr(o,'__float__') else str(o))

# ---- progress plot: gait tau-omega vs selected and v3 actuator envelopes
if MARGIN==1.5:
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    fig,ax=plt.subplots(2,3,figsize=(15,9)); ax=ax.ravel()
    for i,j in enumerate(LEG):
        a=ax[i]; f=(KK if j=='knee' else K_HIP if (j=='hip_pitch' and SEL[j]['d']['kind']=='linear2') else 1)
        a.scatter(TWRAW[j][:,0],TWRAW[j][:,1],s=1,c='tab:blue',alpha=.3,label='gait ID: walk 0.8-1.2, stairs, push, sit')
        d=np.load(f'{LEGS}/carry_20kg.npz'); va=d['va']
        for off in (0,6): a.scatter(np.abs(d['TAU'][:,va[i+off]]),np.abs(d['V'][:,va[i+off]]),s=1,c='tab:orange',alpha=.3,label='carry 20 kg (stretch)' if off==0 else None)
        e,dd=best[j]; T=np.linspace(0,e['A']['T_out'],60); a.plot(T*f,w_at(e['A'],T),'g-',lw=2,label=f"selected: {SEL[j]['label'].split(' +')[0][6:]} ({SEL[j]['mass']:.2f} kg)")
        b=np.array(BASE[j]['curve']); a.plot(b[:,0]*(KK if j=='knee' else 1),b[:,1],'r--',lw=1.5,label=f"v3: {BASE[j]['sel'].split(' +')[0][6:]} ({BASE[j]['mass']:.2f} kg)")
        a.axvline(req[j]['need'],color='k',ls=':',lw=1,label=f"need {MARGIN}x peak = {req[j]['need']:.0f} N·m")
        a.axhline(req[j]['speed'],color='gray',ls=':',lw=1)
        a.set_title(j+(' (torque at worst linkage angle)' if f!=1 else '')); a.set_xlabel('|joint torque| N·m'); a.set_ylabel('|joint speed| rad/s'); a.legend(fontsize=7,markerscale=6); a.grid(alpha=.3)
    fig.suptitle(f'RL Actuators round 1 (2026-10-13): leg torque-speed demand vs actuator envelopes ({BUS_S}S bus {BUS_S*3.4:.0f} V min, Elmo Gold Twitter 49.5 A rms; v3 = 13S, Everest XCR)',fontsize=11)
    fig.tight_layout(); out=os.path.join(R,'media/progress/2026-10-13_actuators_torque_speed.png'); fig.savefig(out,dpi=110); print('plot',out)
