"""Engineering checks for v2. Run: python3 checks.py [--initial]. Writes results/*.md"""
import sys,math,os,json
import numpy as np
import design as D
INIT='--initial' in sys.argv
d=D.final() if not INIT else dict(MOTORS=D.MOTORS,GEARS=D.GEARS,JOINTS=D.JOINTS,GEO=D.GEO,MASS_ITEMS=D.MASS_ITEMS,BATTERY=D.BATTERY,LINKS=D.LINKS,HIP=D.HIP,LOADS=D.LOADS,MATERIALS=D.MATERIALS)
G=D.G;M,GR,J,GEO,L=d['MOTORS'],d['GEARS'],d['JOINTS'],d['GEO'],d['LOADS']
tag='initial' if INIT else 'final'
os.makedirs('results',exist_ok=True)
out=[];fails=[]
def table(title,hdr,rows):
    out.append(f'\n### {title}\n\n| '+' | '.join(hdr)+' |\n|'+'---|'*len(hdr)+'\n'+'\n'.join('| '+' | '.join(str(c) for c in r)+' |' for r in rows)+'\n')
def chk(ok,name):
    if not ok: fails.append(name)
    return 'PASS' if ok else '**FAIL**'
# ---------- 1. Mass budget ----------
act_rows=[];act_mass=0
for n,(g,k,mo,ge,lead,arm,cnt) in J.items():
    nact=cnt*(2 if k=='linear2' else 1)/ (2 if k=='linear2' else 1)  # linear2 pair is listed once per DoF; physical screws = cnt per DoF
    m1=M[mo]['mass']+(GR[ge]['mass'] if ge else 0.35*(lead or 1)/4+0.25)+(D.OVERHEAD_BY_MOTOR[mo] if not INIT else D.ACT_OVERHEAD[k])  # roller screw+nut mass EST
    act_mass+=m1*cnt; act_rows.append((n,k,mo,ge or f'roller screw {lead} mm',cnt,f'{m1:.2f}',f'{m1*cnt:.2f}'))
struct=sum(d['MASS_ITEMS'].values()); total=act_mass+struct
table('Actuator masses [EST]',['joint','type','motor','transmission','qty','kg each','kg total'],act_rows)
table('Mass budget [EST]',['item','kg'],[(k,v) for k,v in d['MASS_ITEMS'].items()]+[('actuators (all)',f'{act_mass:.1f}'),('**TOTAL**',f'**{total:.1f}**')])
target=65.0
out.append(f'\nMass check: total {total:.1f} kg vs target <= {target} kg (Optimus Gen 1 reported 73 kg; Gen 2 is 10 kg lighter per Tesla): {chk(total<=target,"mass budget")}\n')
m=total
# segment masses for statics (distribute)
def leg_act(n): g,k,mo,ge,lead,arm,cnt=J[n]; return (M[mo]['mass']+(GR[ge]['mass'] if ge else 0.35*(lead or 1)/4+0.25)+(D.OVERHEAD_BY_MOTOR[mo] if not INIT else D.ACT_OVERHEAD[k]))
mi=d['MASS_ITEMS']
seg={}
seg['foot']=mi['feet x2 (incl. 6-axis F/T, sole)']/2
seg['shank']=mi['shank structure x2']/2+leg_act('ankle_pitch')+leg_act('ankle_roll')  # ankle motors in shank
seg['thigh']=mi['thigh structure x2']/2+leg_act('knee')
seg['pelvis']=mi['pelvis structure (7075 machined)']+2*(leg_act('hip_yaw')+leg_act('hip_roll')+leg_act('hip_pitch'))
seg['upper']=m-2*(seg['foot']+seg['shank']+seg['thigh'])-seg['pelvis']   # torso+arms+head+battery
# ---------- 2. Torque requirements ----------
def squat_torques(knee_deg,load,trunk_lean_deg=None):
    """Planar static double-support squat. Angles: shank inclined forward by a, thigh back by b, trunk leans so total COM over mid-foot.
       Returns per-leg torque at ankle, knee, hip (N·m). Load held at hands in front of chest."""
    lt,ls=GEO['thigh'],GEO['shank']; k=math.radians(knee_deg); a=k/2  # shank fwd angle, thigh back angle such that hip over-ish
    ankle=np.array([0.0,GEO['ankle_h']]); knee=ankle+ls*np.array([math.sin(a),math.cos(a)])
    b=k-a; hip=knee+lt*np.array([-math.sin(b),math.cos(b)])
    foot_mid=GEO['foot_len']/2-GEO['heel']
    # trunk lean solves COM over foot_mid
    def com(lean):
        tr=hip+GEO['torso_com_above_hip']*np.array([math.sin(lean),math.cos(lean)])
        hand=hip+0.45*np.array([math.sin(lean),math.cos(lean)])+np.array([0.30,0])
        pts=[(2*seg['shank'],(ankle+knee)/2),(2*seg['thigh'],(knee+hip)/2),(seg['pelvis'],hip),(seg['upper'],tr),(load,hand)]
        mt=sum(p[0] for p in pts); return sum(p[0]*p[1] for p in pts)/mt,pts
    lo,hi=-0.5,1.4
    for _ in range(60):
        mid=(lo+hi)/2; c,_=com(mid)
        if c[0]>foot_mid: hi=mid
        else: lo=mid
    lean=(lo+hi)/2; c,pts=com(lean)
    def tq(j,above): return abs(sum(p[0]*G*(p[1][0]-j[0]) for p in above))/2
    above_hip=[p for p in pts[2:]]; above_knee=[pts[1]]+above_hip; above_ankle=[pts[0]]+above_knee
    # pelvis is shared; per-leg divide by 2 already
    return dict(ankle=tq(ankle,above_ankle),knee=tq(knee,above_knee),hip=tq(hip,above_hip),lean=math.degrees(lean),com=c)
sq=squat_torques(110,L['squat_load'])
# single-support bent-knee walking stance (static), times dynamic factor walk_BW
def stance(knee_deg,factor):
    lt,ls=GEO['thigh'],GEO['shank']; k=math.radians(knee_deg)
    # COM above stance ankle; knee forward of COM line by ls*sin(k/2)
    mabove_knee=m-seg['foot']-seg['shank']; mabove_hip=m-seg['foot']-seg['shank']-seg['thigh']-seg['pelvis']/2
    knee_t=mabove_knee*G*factor*ls*math.sin(k/2)
    return knee_t
# human normalized peak joint moments (N·m/kg), approximate, from gait literature (Winter 2009; Riener et al. 2002 stairs). Used as scaling, ESTIMATE.
HUMAN={'walk':dict(hip=1.1,knee=0.8,ankle=1.6,hip_roll=0.9),'stairs':dict(hip=1.2,knee=1.3,ankle=1.5,hip_roll=1.0)}
req={}
req['hip_pitch']=max(HUMAN['walk']['hip']*m,HUMAN['stairs']['hip']*m,sq['hip'])
req['hip_roll']=max(HUMAN['walk']['hip_roll']*m,HUMAN['stairs']['hip_roll']*m, m*G*L['walk_BW']*0.10)  # single support lateral lever 0.10 m
req['hip_yaw']=0.25*m   # ESTIMATE ~0.25 N·m/kg turning
req['knee']=max(HUMAN['walk']['knee']*m,HUMAN['stairs']['knee']*m,sq['knee'],stance(30,L['walk_BW']))
req['ankle_pitch']=max(HUMAN['walk']['ankle']*m,HUMAN['stairs']['ankle']*m,sq['ankle'])
req['ankle_roll']=0.6*m
req['waist_pitch']=max(seg['upper']*G*0.15*1.3, (seg['upper']+L['squat_load'])*G*GEO['torso_com_above_hip']*math.sin(math.radians(max(sq['lean'],0)))*1.0+L['squat_load']*G*0.30)
req['waist_yaw']=40
arm_load=10.0  # kg per arm at reach, design target ESTIMATE
ua,fa=GEO['upper_arm'],GEO['forearm']
req['shoulder_pitch']=(arm_load*(ua+fa+0.08)+2.0*ua/2+1.8*(ua+fa/2)+1.3*(ua+fa+0.05))*G*1.2
req['shoulder_roll']=req['shoulder_pitch']
req['shoulder_yaw']=0.4*req['shoulder_pitch']
req['elbow']=(arm_load*(fa+0.08)+1.8*fa/2+1.3*(fa+0.05))*G*1.2
req['wrist_roll']=arm_load*G*0.05; req['wrist_pitch']=arm_load*G*0.10; req['wrist_yaw']=req['wrist_pitch']*0.6
req['neck_yaw']=2.0;req['neck_pitch']=1.6*G*0.06*1.5
SF=1.5
SPEED={'hip_pitch':4,'hip_roll':3,'hip_yaw':3,'knee':8,'ankle_pitch':6,'ankle_roll':4,'waist_yaw':2,'waist_pitch':2,'shoulder_pitch':4,'shoulder_roll':4,'shoulder_yaw':4,'elbow':6,'wrist_roll':6,'wrist_pitch':6,'wrist_yaw':6,'neck_yaw':4,'neck_pitch':4}  # rad/s ESTIMATE from human gait/reach
rows=[];cap={}
for n,(g,k,mo,ge,lead,arm,cnt) in J.items():
    mot=M[mo];wm=mot['wmax_rpm']*2*math.pi/60
    if k=='rotary':
        gr=GR[ge];T_motor=mot['Tpk']*gr['N']*gr['eta'];T_gear=gr['rep_peak'];Tpk=min(T_motor,T_gear);ratio=gr['N'];eta=gr['eta']
        wj=wm/gr['N']
    else:
        nscrew=2 if k=='linear2' else 1
        F=2*math.pi*mot['Tpk']*D.SCREW_ETA/(lead/1000)   # N per screw
        Tpk=F*arm*nscrew; ratio=2*math.pi*arm/(lead/1000); eta=D.SCREW_ETA
        wj=wm/ratio
    cap[n]=dict(Tpk=Tpk,ratio=ratio,eta=eta,nmot=(2 if k=='linear2' else 1),wj=wj)
    need=req[n]*SF
    rows.append((n,k,f'{req[n]:.0f}',f'{need:.0f}',f'{Tpk:.0f}',f'{Tpk/req[n]:.2f}',chk(Tpk>=need,f'torque {n}'),f'{SPEED[n]}',f'{wj:.1f}',chk(wj>=SPEED[n],f'speed {n}')))
out.insert(0,f'# v2 engineering checks ({tag})\nAll inputs are ESTIMATES unless sourced in design.py. Robot mass used: {m:.1f} kg.\n')
table('Squat with 20 kg (static, 110° knee flexion, per leg)',['quantity','value'],[('trunk lean (deg)',f"{sq['lean']:.1f}"),('ankle N·m',f"{sq['ankle']:.0f}"),('knee N·m',f"{sq['knee']:.0f}"),('hip N·m',f"{sq['hip']:.0f}")])
table('Joint torque & speed vs requirement (requirement = max of walk, stairs, 20 kg squat; ×1.5 safety margin)',['joint','actuator','req N·m','req×1.5','peak avail','margin','torque','req rad/s','max rad/s','speed'],rows)
# ---------- 3. Thermal (I²R, first-order RC) ----------
# duty: 1 h walking at RMS = 0.55×walk peak (ESTIMATE) then squat cycles: 10 s at squat torque, 50 s at walking RMS, 10 cycles
trow=[]
for n in ['hip_pitch','hip_roll','knee','ankle_pitch','waist_pitch','shoulder_pitch','elbow']:
    g,k,mo,ge,lead,arm,cnt=J[n];mot=M[mo];c=cap[n]
    walk_pk={'hip_pitch':HUMAN['walk']['hip']*m,'hip_roll':HUMAN['walk']['hip_roll']*m,'knee':max(HUMAN['walk']['knee']*m,stance(30,L['walk_BW'])),'ankle_pitch':HUMAN['walk']['ankle']*m,'waist_pitch':seg['upper']*G*0.05,'shoulder_pitch':req['shoulder_pitch']*0.15,'elbow':req['elbow']*0.15}[n]
    hold={'hip_pitch':sq['hip'],'hip_roll':req['hip_roll']*0.3,'knee':sq['knee'],'ankle_pitch':sq['ankle'],'waist_pitch':req['waist_pitch'],'shoulder_pitch':req['shoulder_pitch']/1.2,'elbow':req['elbow']/1.2}[n]
    def P(Tj): Tm=Tj/(c['ratio']*c['eta'])/c['nmot']; return c['nmot']*(Tm/mot['Km'])**2, Tm
    Pw,_=P(0.55*walk_pk); Ph,Tmh=P(hold)
    dt=1.0;T=0.0;Tmax=0
    for t in range(3600): T+= (Pw/c['nmot']*mot['Rth']-T)/mot['tau']*dt
    Tss=T
    for cyc in range(10):
        for t in range(10): T+=(Ph/c['nmot']*mot['Rth']-T)/mot['tau']*dt; Tmax=max(Tmax,T)
        for t in range(50): T+=(Pw/c['nmot']*mot['Rth']-T)/mot['tau']*dt
    lim=115  # K rise: 155 °C class F winding - 40 °C ambient
    trow.append((n,mo,f'{Pw:.0f}',f'{Tss:.0f}',f'{Ph:.0f}',f'{Tmh:.2f}/{mot["Tpk"]}',f'{Tmax:.0f}',chk(Tmax<=lim and Tmh<=mot['Tpk'],f'thermal {n}')))
table('Thermal: winding temperature rise (limit 115 K = 155 °C class F at 40 °C ambient). Walk 1 h, then 10× (10 s 20 kg squat hold + 50 s walk)',['joint','motor','walk Cu loss W','walk ΔT K','hold Cu loss W','hold motor torque/peak N·m','max ΔT K','result'],trow)
# ---------- 4. Structure ----------
srow=[]
BW=m*G
for name,lever in [('femur',L['lever_femur']),('tibia',L['lever_tibia'])]:
    lk=d['LINKS'][name];mat=d['MATERIALS'][lk['mat']];ro=lk['OD']/2;ri=ro-lk['t']
    I=math.pi/4*(ro**4-ri**4);A=math.pi*(ro**2-ri**2)
    for case,f,lim,lab in [('landing',L['landing_BW'],mat['Sy'],'yield'),('walking fatigue',L['walk_BW'],mat['Se'],'endurance')]:
        F=f*BW;Mb=F*lever;s=Mb*ro/I+F/A;sf=lim/s
        srow.append((name,lk['mat'],f"Ø{lk['OD']*1000:.0f}×{lk['t']*1000:.1f}",case,f'{s/1e6:.0f}',f'{lim/1e6:.0f} ({lab})',f'{sf:.2f}',chk(sf>=2,f'struct {name} {case}')))
h=d['HIP'];F=L['landing_BW']*BW;Mh=F*L['hip_lat']
# bolt group: moment -> bolt tension max = M/(n*pcd/4) approx for circular pattern; stress area ~0.78 d^2
Tb=Mh*4/(h['bolts']*h['bolt_pcd']);As=0.78*h['bolt_d']**2;sb=Tb/As+F/h['bolts']/As*0.3
srow.append(('hip actuator flange bolts',f"{h['bolts']}×M{h['bolt_d']*1000:.0f} 12.9",f"PCD {h['bolt_pcd']*1000:.0f}",'landing',f'{sb/1e6:.0f}',f"{h['bolt_Sy']/1e6:.0f} (yield)",f"{h['bolt_Sy']/sb:.2f}",chk(h['bolt_Sy']/sb>=2,'struct hip bolts')))
hp_gear=J['hip_pitch'][3]
gearMc=GR[hp_gear]['Mc'] or 0   # only credit the wave-gear output bearing when a catalog value exists
Mc=gearMc+h['extra_bearing_Mc']
lab=f"hip pitch output moment ({hp_gear} bearing {'Mc='+str(gearMc)+' N·m catalog' if gearMc else 'Mc not published, not credited'}"+(f" + {h['extra_bearing_Mc']} N·m crossed-roller support bearing [EST]" if h['extra_bearing_Mc'] else '')+')'
srow.append((lab,'-','-','landing moment',f'{Mh:.0f} N·m',f'{Mc} N·m',f'{Mc/Mh:.2f}',chk(Mc/Mh>=2,'struct hip bearing moment')))
table(f'Structural checks (landing {L["landing_BW"]}×BW, walking {L["walk_BW"]}×BW, SF required ≥ 2)',['part','material','section','case','stress MPa / load','limit','SF','result'],srow)
# ---------- 5. Power & runtime ----------
COT=0.20  # mechanical cost of transport ESTIMATE for a geared electric humanoid
v=1.2;Pmech=COT*m*G*v
Pcu=sum(float(r[2]) for r in trow)*2  # main leg/arm joints, both sides approx
Pdrive=Pmech/0.85
Pelec=dict(compute=110,sensors=25,drivers_idle=40,cooling=30)
Pwalk=Pdrive+Pcu+sum(Pelec.values());Pstand=Pcu*0.3+sum(Pelec.values())
B=d['BATTERY'];usable=B['Wh']*0.9
mix=0.5*Pwalk+0.5*Pstand
table('Power & runtime [EST]',['mode','W',f'runtime h (90% usable of {B["Wh"]} Wh)'],[('walking 1.2 m/s',f'{Pwalk:.0f}',f'{usable/Pwalk:.1f}'),('standing/manipulating',f'{Pstand:.0f}',f'{usable/Pstand:.1f}'),('50/50 mix',f'{mix:.0f}',f'{usable/mix:.1f}')])
out.append(f'\nReference: Tesla stated ~100 W sitting / 500 W walking for Optimus (AI Day 2022, via Forbes). Runtime check (mix ≥ 4 h): {chk(usable/mix>=4,"runtime")}\n')
# ---------- 6. COM ----------
st=squat_torques(5,0)
foot_front=GEO['foot_len']-GEO['heel'];foot_back=-GEO['heel']
c0=st['com'];c1=sq['com']
table('Center of mass',['pose','COM x (m, + forward of ankle)','COM height m','support polygon x','result'],
 [('standing',f'{c0[0]:.3f}',f'{c0[1]:.2f}',f'[{foot_back:.2f}, {foot_front:.2f}]',chk(foot_back+0.03<c0[0]<foot_front-0.03,'COM standing')),
  ('squat + 20 kg',f'{c1[0]:.3f}',f'{c1[1]:.2f}',f'[{foot_back:.2f}, {foot_front:.2f}]',chk(foot_back+0.03<c1[0]<foot_front-0.03,'COM squat'))])
out.append(f'\nCOM height standing / total height = {c0[1]/GEO["height"]:.2f} (human ≈ 0.55).\n')
out.append('\n## Summary\n'+(f'**{len(fails)} FAILED:** '+', '.join(fails) if fails else '**All checks pass.**')+'\n')
open(f'results/checks_{tag}.md','w').write(''.join(out))
json.dump(dict(mass=m,fails=fails,req={k:round(v,1) for k,v in req.items()},cap={k:round(v['Tpk'],1) for k,v in cap.items()},segments=seg,power=dict(walk=Pwalk,stand=Pstand,mix=mix,runtime_mix=usable/mix)),open(f'results/summary_{tag}.json','w'),indent=1)
print(tag,'mass %.1f'%m,'fails:',fails)
# ---------- 7. Hand (22 DoF, tendon-driven, actuators in forearm) ----------
# 22 joints: thumb 5, index 4, middle 4, ring 4, little 4, palm arch 1. 17 actuators: 5 DIP joints coupled to PIP by linkage.
# Each actuator: Ø16 mm BLDC (Maxon EC-i/ECX class, ESTIMATE 0.012 N·m continuous, 0.035 N·m peak) -> M3x0.5 ball screw
# (eta 0.8) -> Dyneema tendon. Finger flexion moment arm at MCP 8 mm, fingertip lever 90 mm (ESTIMATES).
Tm_c,Tm_p,lead,eta=0.012,0.035,0.0005,0.8
Ften_c=2*math.pi*Tm_c*eta/lead;Ften_p=2*math.pi*Tm_p*eta/lead
r_mcp=0.008 if INIT else 0.011  # FIX v2.1: grip FAIL -> MCP tendon moment arm 8 -> 11 mm (larger MCP pulley)
tip_c=Ften_c*r_mcp/0.09;tip_p=Ften_p*r_mcp/0.09
# requirement: hold 10 kg (arm_load) in a 4-finger hook/power grasp: 98 N shared by 4 fingers -> 24.5 N each, ×1.5
need=arm_load*G/4*1.5
dyneema_break=1000 if INIT else 2000  # N; v2.0 1 mm line, FIX v2.1: tendon SF FAIL -> 1.5 mm UHMWPE braided line (break load ESTIMATE, verify)
table('Hand: tendon actuator capacity [EST]',['quantity','value','requirement','result'],[
 ('tendon force cont / peak (N)',f'{Ften_c:.0f} / {Ften_p:.0f}',f'< {dyneema_break/4:.0f} (tendon SF 4)',chk(Ften_p<=dyneema_break/4,'hand tendon SF')),
 ('fingertip force per finger cont / peak (N)',f'{tip_c:.1f} / {tip_p:.1f}',f'≥ {need:.1f} peak (10 kg hook grasp ×1.5)',chk(tip_p>=need,'hand grip force'))])
out[-1]=out[-1]
open(f'results/checks_{tag}.md','w').write(''.join(out).replace('\n## Summary','\n## Summary (hand checks appended below)'))
with open(f'results/checks_{tag}.md','a') as f: f.write('\n**Hand check failures:** '+(', '.join(x for x in fails if x.startswith('hand')) or 'none')+'\n')
print('hand fails:',[x for x in fails if x.startswith('hand')], 'tip peak %.1f need %.1f tendon %.0f'%(tip_p,need,Ften_p))
