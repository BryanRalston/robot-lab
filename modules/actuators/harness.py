"""R5 A2 (R-018, O16): harness mass model backed by datasheet g/m and routed lengths from the v3 CAD layout.
Supersedes the R4 [EST] model (kept in git history, 0.821 kg). Owner RL Actuators per R-017.
Cable (datasheets/):  power = Lapp OELFLEX HEAT 180 SiF fine-wire silicone single cores (lapp_oelflex_heat180_sif.pdf: weight kg/km, OD);
                      EtherCAT = GORE GSC-03-84820-00 star-quadrax Cat5e 26 AWG, 3.3 mm, 23.0 kg/km, min bend 15 mm (gore_hs_data_cables_catalog.pdf Table "Ethernet Quadrax").
                      Flex-rated reference: igus CFBUS.040 Cat5 (4x0.25)C 7.0 mm 59 kg/km (igus_cfbus.pdf), CFROBOT4 (igus_cfrobot4.pdf) -> too thick for the clock-spring drums (r req 70 mm).
Connectors: Amass XT60 / XT30U / MR30 / AS150U, JST GH datasheets (ratings, AWG); masses are NOT in the Amass/JST datasheets -> distributor-listed masses (SOURCES.md) or [EST].
Routes: joint/part coordinates from v3/cad/model.py (P, CHAINS, pack/compute bounding boxes), straight segments x1.15 routing factor (clips, bends around housings),
        + clock-spring service loop at every moving joint crossed = r_wrap (v3/cad/out/cables.json r_min) x joint ROM + 50 mm slack, + 80 mm tee pigtail per drive.
Gauge: smallest SiF size meeting the per-segment voltage-drop budget at peak (series leg segments sum <= 2 % of 68 V) and conductor rise <= 30 K at rms (2x bundle factor); fixed-size runs use their listed size as a floor."""
import json, os, math
H=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.abspath(f'{H}/../..')
S=json.load(open(f'{H}/results/sizing.json')); CAB={r['joint']:r for r in json.load(open(f'{H}/results/v3_cables.json'))['joints']}
V=68.0; RHO_CU=1.72e-8 * 1.0
# Lapp OELFLEX HEAT 180 SiF: mm2 -> (weight g/m, OD mm, article no. black)  [datasheet]
SIF={4.0:(50,4.2,'0053001'),2.5:(32,3.4,'0052001'),1.5:(20,2.8,'0051001'),1.0:(15,2.5,'0050001'),0.75:(12,2.4,'0049001'),0.5:(9,2.1,'0048001'),0.25:(5.4,1.9,'0047001')}
ECAT_R5A2=dict(part='GORE GSC-03-84820-00',gpm=23.0,od=3.3,bend_min=15.0)   # R5 A2: static-rated only
ECAT=dict(part='Belden MachFlex MRTA2P26S',gpm=25.9,od=4.2,bend_min=7.5*4.2)   # R5b O20: robotic 2x2x26 AWG shielded, 8e6 bend (7.5D) + 8e6 torsion ±180°/m cycles (belden_mrta2p26s.pdf); 100 ohm not specified -> TDR check
# R5b O20: power cores inside the clock-spring loops = Staubli SILI-E super-flexible class-6 (0.07 mm strands) silicone, (g/m, OD) from staubli_cables_catalog.pdf
FLEX=os.environ.get('FLEX','1')=='1'
if not FLEX: ECAT=ECAT_R5A2
SILI={} if not FLEX else {0.25:(4.5,1.7),0.5:(8.6,2.3),0.75:(12,2.7),1.0:(16,3.0),1.5:(22,3.4),2.5:(33,3.9)}
ECAT_FLEX=dict(part='igus CFBUS.040',gpm=59.0,od=7.0)
RF=1.15; SLACK=0.05; PIG=0.08
# v3 layout (mm) from v3/cad/model.py P + bounding boxes (pack z 1333..1477, compute z 1485..1525)
PACK_BOT=(12,0,1333); PACK_TOP=(12,0,1477); COMPUTE=(8,0,1505); WAIST=(0,0,1250)   # waist joints between pelvis_top 1230 and pack
HIPY,HIPR,HIPP,KNEE,ANK_DRV,ANK=(0,130,1160),(0,130,1045),(0,130,920),(0,130,500),(0,130,300),(0,130,80)
SHP=(0,190,1500); SHR=(0,282,1500); ELB=(0,282,1200); WRI=(0,282,930); HAND=(0,282,830); NECK=(0,0,1590); HEAD=(0,0,1690)
import re   # R5b O21: joint ranges from the v3 MJCF (sim/v3/humanoid_v3.xml, CONTRACTS 'Range of motion'), hip_pitch -105..+40 (P-014)
_X=open(f'{ROOT}/sim/v3/humanoid_v3.xml').read(); _R={m[0]:float(m[2])-float(m[1]) for m in re.findall(r'joint name="(?:l_)?([a-z_]+)"[^>]*?range="(-?[\d.]+) (-?[\d.]+)"',_X)}
ROM={k.replace('_',' '):v for k,v in _R.items() if not k.startswith('r_')}; ROM['ankle (pitch+roll)']=ROM.pop('ankle pitch')+ROM.pop('ankle roll')
def d(a,b): return sum(abs(x-y) for x,y in zip(a,b))/1000   # Manhattan along structure, m
def path(*pts): return RF*sum(d(a,b) for a,b in zip(pts,pts[1:]))
def loop(j): return CAB[j]['r_min_mm']/1000*math.radians(ROM[j])+SLACK
def loops(*js): return sum(loop(j) for j in js)
pk_leg=max(v['peak_limb'] for v in S['power'].values()); mean_leg=max(v['mean_noregen'] for v in S['power'].values())/2
I_leg_pk=pk_leg/V; I_leg_rms=1.6*mean_leg/V; I_arm_pk,I_arm_rms=300/V,80/V
# --- routed runs (per side where noted): name, n, L m, joints crossed, mm2, conductors, I_rms, I_pk
legJ1=('waist yaw','waist pitch','hip yaw','hip roll'); armJ=('shoulder pitch','shoulder roll','shoulder yaw','elbow')
P=[]
P.append(('leg trunk pack->hip_pitch',2,path(PACK_BOT,WAIST,HIPY,HIPR,HIPP),legJ1,4.0,2,I_leg_rms,I_leg_pk))
P.append(('leg hip_pitch->knee',2,path(HIPP,KNEE),('hip pitch',),2.5,2,I_leg_rms*0.7,I_leg_pk*0.8))
P.append(('leg knee->ankle drives',2,path(KNEE,ANK_DRV),('knee',),1.5,2,I_leg_rms*0.4,I_leg_pk*0.5))
P.append(('leg drive pigtails (8/leg: hip yaw, hip roll, 2 hip_pitch, 2 knee, 2 ankle)',16,PIG,(),1.0,2,4.0,12.0))
P.append(('arm trunk pack->shoulder_yaw',2,path(PACK_TOP,SHP,SHR,ELB),armJ[:3],1.5,2,I_arm_rms,I_arm_pk))
P.append(('arm elbow->wrist',2,path(ELB,WRI),('elbow',),0.75,2,I_arm_rms*0.6,I_arm_pk*0.6))
P.append(('arm drive pigtails (7/arm)',14,PIG,(),0.5,2,1.5,5.0))
P.append(('hand 24 V from wrist DC/DC',2,path(WRI,HAND),('wrist roll',),0.5,2,0.5,2.0))
P.append(('waist drives feed',1,path(PACK_BOT,WAIST),('waist yaw',),1.0,2,1.5,6.0))
P.append(('neck/head bus',1,path(PACK_TOP,NECK,HEAD),('neck yaw','neck pitch'),0.75,2,1.0,4.0))
P.append(('waist/neck pigtails (4)',4,PIG,(),0.5,2,1.0,4.0))
P.append(('compute 48 V feed (A25: DCM3623TA5N53B4 43-154 V -> 48 V; 120 W -> 2.5 A)',1,path(PACK_TOP,COMPUTE),(),0.25,2,2.5,4.0))
P.append(('BMS->fuse->contactor->bus bar',1,0.30,(),4.0,2,I_leg_rms*2,I_leg_pk*2))
P.append(('e-stop loop (back button, completeness)',1,2*path(PACK_TOP,(-100,0,1450)),(),0.25,2,0.1,0.1))
E=[]  # EtherCAT line topology per branch from torso junction at compute; frames return on the same quad
E.append(('ECAT leg branch -> foot F/T',2,path(COMPUTE,WAIST,HIPY,HIPR,HIPP,KNEE,ANK),legJ1+('hip pitch','knee','ankle (pitch+roll)'),8))
E.append(('ECAT arm branch -> hand/tactile',2,path(COMPUTE,SHP,SHR,ELB,WRI,HAND),armJ+('wrist roll',),8))
E.append(('ECAT waist only (A25: neck left EtherCAT)',1,path(COMPUTE,WAIST),('waist yaw',),2))
E.append(('RS-485 FD (2 pairs, MachFlex quad reused) AGX301 -> neck Dynamixels (A25)',1,path(COMPUTE,NECK,HEAD),('neck yaw','neck pitch'),0))
E.append(('IMU (torso, completeness)',1,0.25,(),0))
# A25 extra cables: (name, n, L route, joints, g/m in run, g/m in loops, extra m)
COAX=dict(part='HUBER+SUHNER ENVIROFLEX_178 (RG178 class, 50 ohm, 1.84 mm)',gpm=6.5,od=1.84,bend_dyn=30.0,a=1.4067,b=0.2229)   # datasheet: 0.65 kg/100 m; att = a f^0.5 + b f dB/m (f GHz); dynamic bend >= 30 mm
X=[('GMSL2 coax JCB022 MATE-AX -> FAKRA -> ZED X Mini (PoC) (A25)',1,path(COMPUTE,NECK,HEAD),('neck yaw','neck pitch'),COAX['gpm'],COAX['gpm'],0.10)]
# A33 (Electronics 1d70018 §9.4): Elmo STO = 3 conductors per drive (STO1/STO_RET/STO2, MAN-G-TWI Table 9), daisy-chained along each EtherCAT branch, tee per drive.
# Elmo drives: legs 8 + 8, arms 7 + 7 (shoulder 3, elbow, wrist roll, wrist pair 2), waist 2 = 32. Neck = 2 x Dynamixel XM430 (P-019/R-025), no Elmo STO.
STO_BR=[('legs',2,'ECAT leg branch -> foot F/T',8),('arms',2,'ECAT arm branch -> hand/tactile',7),('waist',1,'ECAT waist only (A25: neck left EtherCAT)',2)]
N_ELMO=sum(n*nd for _,n,_,nd in STO_BR)
_E={e[0]:e for e in E}
for nm,n,en,nd in STO_BR:
    _,_,L0,js,npig=_E[en]
    X.append((f'STO 3-wire daisy chain, {nm} branch (A33; 0.25 mm2 SiF, SILI-E in loops, {nd} drive tees x 0.08 m)',3*n,L0,js,SIF[0.25][0],SILI.get(0.25,SIF[0.25][:2])[0],nd*PIG))
X.append(('STO 3-wire MCU -> torso junction (A33)',3,0.25,(),SIF[0.25][0],SIF[0.25][0],0.0))
local=[('motor phase leads (32 Elmo drives, 3 x 0.5 mm2 x 0.06 m)',32,0.06,0.5,3),('encoder/thermistor leads (32, 3 x 0.25 mm2 x 0.06 m)',32,0.06,0.25,3)]
# connectors: (each pair kg, n, evidence)
CON={'XT60 pair (Amass XT60, 30 A)':(0.0078,4,'7.8 g/pair distributor listing (Alise Ops)'),
     'XT30U pair (Amass, 15 A, drive tees)':(0.0036,32+8,'1.8 g each half, AMOV listing'),
     'MR30 3-pin pair (Amass, phase)':(0.0024,0,'1.2 g/pc AMOV listing; phases soldered, n=0'),
     'JST-GH 4-pin pair (GHR-04V-S + 4 SSHL-002T-P0.2 + BM04B-GHS-TBT)':(0.000384,2*32+12+32,'R6 A9 published: TME weights housing 0.079 g + 4 x 0.021 g contacts + header 0.221 g (gross) = 0.384 g; GAM listing 0.08+0.08+0.16 = 0.32 g; +-0.06 g'),
     'AS150U pair (pack main)':(0.0414,1,'41.4 g/pair distributor listing (Rotorama)')}
rows=[]; wire=0; ecat=0; loop_len=0
def R(a): return RHO_CU/(a*1e-6)
DT_MAX=30.0; BUNDLE=2.0   # conductor rise limit at rms (K) and bundle factor on free-air rise
BUDGET={'leg trunk pack->hip_pitch':0.8,'leg hip_pitch->knee':0.6,'leg knee->ankle drives':0.4,'arm trunk pack->shoulder_yaw':1.0,'arm elbow->wrist':0.6}  # % of 68 V; series legs sum <= 2 %
def choose(L,c,irms,ipk,bud,a_min):
    for a in sorted(SIF):
        if a<a_min: continue
        g,od,_=SIF[a]
        if 100*ipk*R(a)*L*c/V<=bud and BUNDLE*irms**2*R(a)/(math.pi*od*1e-3*10)<=DT_MAX: return a
    return max(SIF)
for nm,n,L0,js,a_min,c,irms,ipk in P:
    lp=loops(*js); L=L0+lp; a=choose(L,c,irms,ipk,BUDGET.get(nm,1.0),a_min if nm not in BUDGET else 0.5); g,od,art=SIF[a]; gl,odl=SILI.get(a,(g,od)); m=n*c*(L0*g+lp*gl)/1000; od=max(od,odl) if lp else od; dv=ipk*R(a)*L*c; Pw=irms**2*R(a)
    dT=BUNDLE*Pw/(math.pi*od*1e-3*10); rb=min([CAB[j]['r_min_mm'] for j in js],default=None)
    rows.append(dict(item=nm,n=n,route_m=round(L0,3),loops_m=round(lp,3),len_m=round(L,3),joints=list(js),mm2=a,lapp_art=art,gpm=g,cond=c,kg=m,I_rms=irms,I_pk=ipk,
        dV_pct=100*dv/V,dT_K=dT,bend_r_mm=rb,bend_ratio=(rb/od if rb else None))); wire+=m; loop_len+=n*c*lp
for nm,n,L0,js,npig in E:
    lp=loops(*js); L=L0+lp+npig*PIG; m=n*L*ECAT['gpm']/1000
    rb=min([CAB[j]['r_min_mm'] for j in js],default=None)
    rows.append(dict(item=nm,n=n,route_m=round(L0,3),loops_m=round(lp,3),len_m=round(L,3),joints=list(js),cable=ECAT['part'],gpm=ECAT['gpm'],kg=m,bend_r_mm=rb,bend_ratio=(rb/ECAT['od'] if rb else None)))
    ecat+=m; loop_len_e=0
ecat_loop=sum(r['n']*r['loops_m'] for r in rows if 'cable' in r)
xtra=0
for nm,n,L0,js,g,gl,ex in X:
    lp=loops(*js); m=n*(L0*g+lp*gl+ex*g)/1000; rb=min([CAB[j]['r_min_mm'] for j in js],default=None)
    rows.append(dict(item=nm,n=n,route_m=round(L0,3),loops_m=round(lp,3),len_m=round(L0+lp+ex,3),joints=list(js),cable='coax' if 'coax' in nm else 'SiF 0.25',gpm=g,kg=m,bend_r_mm=rb,bend_ratio=(rb/(COAX['od'] if 'coax' in nm else 1.9) if rb else None))); xtra+=m
coax_row=[r for r in rows if 'coax' in r['item']][0]; COAX['len_m']=coax_row['len_m']; COAX['loss_dB_3GHz']=coax_row['len_m']*(COAX['a']*3**0.5+COAX['b']*3); COAX['loss_dB_1p5GHz']=coax_row['len_m']*(COAX['a']*1.5**0.5+COAX['b']*1.5)
COAX['PoC_loop_ohm']=coax_row['len_m']*(747+50)/1000; COAX['neck_r_mm']=coax_row['bend_r_mm']
sto_kg=sum(r['kg'] for r in rows if r['item'].startswith('STO'))
for nm,n,L,a,c in local: m=n*L*c*SIF[a][0]/1000; rows.append(dict(item=nm,n=n,len_m=L,mm2=a,cond=c,gpm=SIF[a][0],kg=m)); wire+=m
con=sum(v[0]*v[1] for v in CON.values())
junction=0.020   # EtherCAT 4-port junction PCB in torso [EST]
sleeve=0.12*(wire+ecat+xtra)
total=wire+ecat+xtra+con+sleeve+junction
flex_fallback=ecat_loop*(ECAT_FLEX['gpm']-ECAT['gpm'])/1000
worst=[r for r in rows if r.get('bend_ratio')]
FLEX_TAG=FLEX
out=dict(cables=dict(power='Lapp OELFLEX HEAT 180 SiF',ecat=ECAT,ecat_flex_ref=ECAT_FLEX),I_leg_pk=I_leg_pk,I_leg_rms=I_leg_rms,rows=rows,
   power_wire_kg=wire,ecat_kg=ecat,connectors=dict(parts={k:dict(each_kg=v[0],n=v[1],evidence=v[2]) for k,v in CON.items()},kg=con),
   sleeving_kg=sleeve,ecat_junction_kg=junction,total_kg=total,R4_model_kg=0.821,R018_credited_kg=1.344,contract=2.00,
   worst_dV_pct=max(r.get('dV_pct',0) for r in rows),worst_dT_K=max(r.get('dT_K',0) for r in rows),
   min_bend_ratio=min(r['bend_ratio'] for r in worst),a25_extra_kg=xtra,sto_kg=sto_kg,sto_with_sleeve_kg=1.12*sto_kg,coax=COAX,ecat_loop_m=ecat_loop,flex_fallback_ecat_kg=flex_fallback)
json.dump(out,open(f'{H}/results/harness.json','w'),indent=1)
L=['# Harness mass model R5 (O16, R-018 A2): datasheet g/m + routed lengths','',
 '`harness.py` → `harness.json`. Bus 20S 68–84 V, star from pack/BMS; EtherCAT line per branch from a torso junction. Coordinates from `v3/cad/model.py`; service-loop radii from `v3/cad/out/cables.json`.','',
 '**Cables.** Power: Lapp ÖLFLEX HEAT 180 SiF silicone single cores (datasheet kg/km: 4.0 mm² 50, 2.5 mm² 32, 1.5 mm² 20, 1.0 mm² 15, 0.75 mm² 12, 0.5 mm² 9, 0.25 mm² 5.4). EtherCAT: GORE GSC-03-84820-00 quadrax Cat5e 26 AWG, 3.3 mm, 23.0 kg/km.','',
 f'**Routing rule.** Straight segments are Manhattan distances along the structure × {RF}. Each crossed joint adds a clock-spring loop: r_wrap × ROM + {SLACK*1000:.0f} mm. Each drive adds a {PIG*1000:.0f} mm tee pigtail.','',
 '| run | n | route m | loops m | length m | joints crossed | cable | g/m | cond | kg | ΔV pk % | ΔT K | bend r/OD |','|---|---|---|---|---|---|---|---|---|---|---|---|---|']
for r in rows:
    cab=r.get('cable',f"SiF {r.get('mm2')} mm²")
    L.append(f"| {r['item']} | {r['n']} | {r.get('route_m',r['len_m'])} | {r.get('loops_m',0)} | {r['len_m']} | {', '.join(r.get('joints',[])) or '-'} | {cab} | {r['gpm']} | {r.get('cond',1)} | {r['kg']:.3f} | {r.get('dV_pct',0):.2f} | {r.get('dT_K',0):.1f} | {r['bend_ratio']:.1f} |" if r.get('bend_ratio') else
             f"| {r['item']} | {r['n']} | {r.get('route_m',r['len_m'])} | {r.get('loops_m',0)} | {r['len_m']} | - | {cab} | {r['gpm']} | {r.get('cond',1)} | {r['kg']:.3f} | {r.get('dV_pct',0):.2f} | {r.get('dT_K',0):.1f} | - |")
L+=['','Joint ROM used (deg): '+', '.join(f'{k} {v}' for k,v in ROM.items())+'. Hip pitch is from the Legs CAD (−120..+40); the others are [EST] human-range values.','',
 f"Connectors {con:.3f} kg: "+'; '.join(f'{k} ×{v[1]} ({v[2]})' for k,v in CON.items()),'',
 f"| block | kg |\n|---|---|\n| power wire (datasheet g/m × routed L) | {wire:.3f} |\n| EtherCAT + completeness data (datasheet g/m × routed L) | {ecat:.3f} |\n| connectors | {con:.3f} |\n| sleeving/ties 12 % [EST] | {sleeve:.3f} |\n| EtherCAT junction PCB [EST] | {junction:.3f} |\n| **total** | **{total:.3f}** |",'',
 f"Worst ΔV {out['worst_dV_pct']:.2f} % at peak (limit 2 %). Worst conductor ΔT {out['worst_dT_K']:.1f} K at rms (free air h 10 W/m²K × 2 bundle factor, limit 30 K; SiF rated 180 °C). Minimum bend ratio at the drums is r/OD {out['min_bend_ratio']:.1f} (MachFlex rated 7.5 × OD for 8e6 cycles; SILI-E / SiF ≥ 6 × OD).",
 f"**Flex (R5b, O20).** In every clock-spring loop the EtherCAT is Belden MachFlex MRTA2P26S: 2×2×26 AWG robotic cable, 4.2 mm, 25.9 g/m, 8e6 bend cycles at 7.5D and 8e6 torsion cycles at ±180°/m. It is used for the whole branch, so there are no splices. Belden does not specify 100 Ω impedance, so a TDR or EtherCAT link test is needed (O20b). Power cores inside the loops are Stäubli SILI-E super-flexible silicone (class 6, 0.07 mm strands). Stäubli publishes no cycle rating, so the clock-spring cycle test stays (O20a). igus CFBUS/CFROBOT and Lapp ETHERLINE Flex need 70–90 mm bend radius and do not fit the drums."]
open(f'{H}/results/harness.md','w').write('\n'.join(L)+'\n'); print('\n'.join(L[-8:]))
