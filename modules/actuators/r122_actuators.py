"""R-122 Actuators rows: (1) row 3 housing-pocketing candidate volumes from the cad_mass.py parametric geometry (G4 brief §5 regions),
(2) fastener BOM per actuator unit with steel and Ti-6Al-4V mass -> results/FASTENER_BOM.md/.json, results/R122_ACTUATORS.json.
Sources: HD CSF/CSG catalog Table 24 (flexspline bolts), Table 27 (circular-spline bolts), notes 'JIS B 1051 over 12.9';
cad_mass.py (8 x M5 flange, 6 x M3 cap, 4 x M4; RV12 nut flange 6 x M5 per Rollvis p.25); Elmo Gold Twitter install guide l.770-773
(4 x M2 A2); unit counts: Electronics R1 l.170 (32 drives: 8/leg, 7/arm, 2 waist), CONTRACTS §1a (neck), cad/*.step (hip_yaw CSG-17).
Screw mass: ISO 4762 nominal dims (dk 1.5d, k d, hex socket s~0.8d depth 0.5d), shank at nominal d [CALC, ~+5% vs tables]."""
import math, json
RS,RT=7.85,4.43; RHO=2.81
def screw_g(d,L):
    dk=1.5*d if d>=3 else 3.8; v=math.pi/4*dk**2*d - 0.65*(0.8*d)**2*0.5*d + math.pi/4*d**2*L
    return v*RS/1000
# ---------- fastener lines: (unit, n_robot, [(item, d, L, n/unit, grade, structural, reason, basis)])
FS={14:(6,4),17:(6,5),20:(8,5),25:(8,6)}   # Table 24 n, size
CS={14:(8,3),17:(16,3),20:(16,3),25:(16,4)}                                                      # Table 27 n, size
def rotary(size,outd):
    nf,df=FS[size]; nc,dc=CS[size]
    return [('flexspline -> output hub',df,2*df+2,nf,'12.9 steel',True,'gear torque path; HD requires >= 12.9','HD Table 24; L [EST]'),
            ('circular spline -> housing',dc,2*dc+4,nc,'12.9 steel',True,'gear torque reaction','HD Table 27; L [EST]'),
            ('output flange -> customer',outd,16 if outd==5 else 12,8,'12.9 steel',True,'joint load path (interface, CONTRACTS 1c)','cad_mass.py 8 x M5x16 (legs); M4x12 on CSG-14/20 [EST]'),
            ('crossed-roller clamp ring',3,8,8,'12.9 steel',True,'retains bearing outer ring axially (fall/impact load)','[EST] (Arms R13 clamp ring, count not drawn)'),
            ('rear cap / encoder cover',3,8,6,'12.9 steel',False,'cover only; motor reaction goes via stator bond land to tube','cad_mass.py 6 x M3; L [EST]'),
            ('AksIM-2 readhead',2,6,2,'A2',False,'locates readhead, no load; ring is press-fit','[EST] (RLS MBD01: ring press-fit)'),
            ('Elmo drive mount',2,6,4,'A2',False,'board/heat-sink mount; thermal contact (Thermal to OK Ti)','Elmo install guide l.770-773 (4 x M2 A2); L [EST]')]
def linear():
    return [('RV12 nut flange -> rotor hub',5,12,6,'12.9 steel',True,'full screw axial force','Rollvis p.25 via cad_mass.py hub(); L [EST]'),
            ('front cap / 7202 bearing retainer',4,12,4,'12.9 steel',True,'carries angular-contact preload and axial force','cad_mass.py 4 x M4; L [EST]'),
            ('rear cap / encoder cover',3,8,6,'12.9 steel',False,'cover only','cad_mass.py 6 x M3; L [EST]'),
            ('AksIM-2 readhead',2,6,2,'A2',False,'no load','[EST]'),
            ('Elmo drive mount',2,6,4,'A2',False,'board mount; thermal contact (Thermal to OK Ti)','Elmo install guide (4 x M2 A2)')]
UNITS=[('hip_yaw (CSG-17)',2,rotary(17,5)),('hip_roll (CSG-25)',2,rotary(25,5)),('waist_yaw (CSG-17)',1,rotary(17,5)),('waist_pitch (CSG-25)',1,rotary(25,5)),
 ('shoulder_pitch (CSG-25)',2,rotary(25,5)),('shoulder_roll (CSG-25)',2,rotary(25,5)),('shoulder_yaw (CSG-17)',2,rotary(17,5)),('elbow (CSG-20)',2,rotary(20,4)),
 ('wrist_roll (CSG-14)',2,rotary(14,4)),('wrist_pitch (CSG-14, D76)',2,rotary(14,4)),('wrist_yaw (CSG-14, D76)',2,rotary(14,4)),
 ('hip_pitch screw (RV12)',4,linear()),('knee screw (RV12)',4,linear()),('ankle screw (RV12)',4,linear())]
rows=[];tot=dict(st=0,sn=0,tn=0)
for u,n,lines in UNITS:
    for it,d,L,k,g,S,why,src in lines:
        ms=screw_g(d,L)*k*n; mt=ms*RT/RS
        rows.append(dict(unit=u,item=it,size=f'M{d}x{L}',n_unit=k,n_robot=k*n,grade=g,structural=S,reason=why,basis=src,steel_g=round(ms,1),ti_g=round(mt,1)))
        tot['st']+=ms
        if not S: tot['sn']+=ms; tot['tn']+=mt
tot={k:round(v,1) for k,v in tot.items()}; tot['saving_nonstruct_g']=round(tot['sn']-tot['tn'],1); tot['n_nonstruct']=sum(r['n_robot'] for r in rows if not r['structural'])
tot['n_all']=sum(r['n_robot'] for r in rows); tot['note_neck']='neck_yaw/pitch (CONTRACTS 1a CSG-14) not in the 32-drive count; Head owner to confirm (excluded)'
# ---------- row 3 pocket candidates (G4 brief §5), per unit, mm3
def ann(Do,Di,t): return math.pi/4*(Do**2-Di**2)*t
P={}
for nm,mod,ml,n,base in (('hip_yaw',60,17.71,2,0.2145),('hip_roll',85,19.34,2,0.2264)):
    D=max(mod,90)+6
    c=dict(rear_cap_windows=0.5*ann(D,0.35*D,2.5),flange_scallops=0.5*ann(D+14,D+2,4),tube_windows_THERMAL=0.3*math.pi*D*2*ml)
    P[nm]=dict(n=n,base_kg=base,**{k:round(v*RHO/1e6,4) for k,v in c.items()})
for nm,mod,n,base,eye,fins in (('hip_pitch_body',76,4,0.1425,0,0),('ankle_body',60,4,0.1924,1,4)):
    D=mod+6; Dn=41; sl=math.hypot(6,(D-Dn)/2)
    c=dict(rear_cap_windows=0.5*ann(D,0.35*D,2.5),cone_windows=0.3*math.pi*(D+Dn)/2*sl*2)
    if eye: c['eye_lug_trim']=0.25*(math.pi*15**2+30*15)*10   # [EST] 25 % of lug outer profile to 3 mm ligament
    if fins: c['ring_fins_THERMAL']=fins*ann(D+16,D-1,3)
    P[nm]=dict(n=n,base_kg=base,**{k:round(v*RHO/1e6,4) for k,v in c.items()})
def robot(keys_excl):
    return round(sum(p['n']*sum(v for k,v in p.items() if k not in('n','base_kg') and not any(x in k for x in keys_excl)) for p in P.values()),3)
row3=dict(per_unit=P,robot_basis_kg=2.221,full_no_thermal_items=robot(('THERMAL',)),full_with_tube_windows=robot(('fins',)),fins_if_thermal_accepts=round(sum(p['n']*p.get('ring_fins_THERMAL',0) for p in P.values()),3))
json.dump(dict(rows=rows,totals=tot),open('results/fastener_bom.json','w'),indent=1)
json.dump(row3,open('results/R122_ACTUATORS.json','w'),indent=1)
print(tot); print(json.dumps(row3,indent=0))
md=['| unit | item | size | n/unit | n/robot | grade | structural | reason | basis | steel g (robot) | Ti64 g (robot) |','|---|---|---|---:|---:|---|---|---|---|---:|---:|']
for r in rows: md.append(f"| {r['unit']} | {r['item']} | {r['size']} | {r['n_unit']} | {r['n_robot']} | {r['grade']} | {'YES' if r['structural'] else 'no'} | {r['reason']} | {r['basis']} | {r['steel_g']} | {r['ti_g'] if not r['structural'] else '—'} |")
open('results/fastener_bom_table.md','w').write('\n'.join(md)+'\n')
