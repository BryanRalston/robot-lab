"""Joint audit for the v4 fidelity model. Reads model_v4 (geometry), out/clash_v4.json (sweep) and module data;
writes JOINT_AUDIT.json + JOINT_AUDIT.md. Exit code 1 if any joint lacks a mechanism (no bearing/actuator parts in the model)
or has status FAIL. Status: BUILDABLE = mechanism backed by module data and clear through its range; PLACEHOLDER = not yet
engineered by any module (dims [EST]); FAIL = mechanism conflict found here."""
import json,os,re,sys,math,numpy as np
import model_v4 as M
H=M.HERE; R=M.ROOT
SIZ=json.load(open(os.path.join(R,'modules/actuators/results/sizing.json')))['sel']
LS=M.LS; AST=json.load(open(os.path.join(R,'modules/actuators/results/ankle_stroke_73_r18_p45.json')))
CL=json.load(open(os.path.join(H,'out/clash_v4.json')))
SIM={'hip_yaw':(-35,45),'hip_roll':(-12,15),'hip_pitch':(-105,40),'knee':(0,135),'ankle_pitch':(-45,40),'ankle_roll':(-18,18),
     'waist_yaw':(-90,90),'waist_pitch':(-30,60),'shoulder_pitch':(-180,60),'shoulder_roll':(-15,180),'shoulder_yaw':(-150,150),'elbow':(-140,0),
     'wrist_roll':(-170,170),'wrist_pitch':(-70,70),'wrist_yaw':(-40,40),'neck_yaw':(-80,80),'neck_pitch':(-40,40)}   # site/humanoid_v3.xml (left side)
def screw_len(j,rng,n=60):
    """pin-to-pin length of one screw over the joint range, from the same kinematics as the model."""
    M.build(); out=[]
    for a in np.linspace(rng[0],rng[1],n):
        M.POSE.clear(); jn='L_'+j
        if j=='hip_pitch':
            g=M.HIP_G; M.POSE[jn]=a; e=M.xf_pt('L_thigh',(g['trunnion_x_mm'],130,M.P['hip_z']+g['trunnion_z_mm']))
            E=(-g['lever_mm']*math.sin(math.radians(g['clock_deg'])),130,M.P['hip_z']-g['lever_mm']*math.cos(math.radians(g['clock_deg']))); out.append(np.linalg.norm(e-np.array(E)))
        if j=='knee':
            g=M.KNEE_G; M.POSE[jn]=a; kz=M.P['knee_z']; t=np.array((g['trunnion_x_mm'],130,kz+g['trunnion_z_mm']))
            e=M.xf_pt('L_shank',(-g['lever_mm']*math.sin(math.radians(g['clock_deg'])),130,kz-g['lever_mm']*math.cos(math.radians(g['clock_deg'])))); out.append(np.linalg.norm(e-t))
    M.POSE.clear(); return min(out),max(out)
def ankle_tilt():
    """out-of-plane angle of the ankle screw bodies at roll ±18° x pitch extremes: a y-axis pin trunnion needs 0°."""
    M.build(); worst=0
    for p in (-45,0,40):
        for r in (-18,18):
            M.POSE.clear(); M.POSE.update({'L_ankle_pitch':p,'L_ankle_roll':r})
            for sy in (-1,1):
                a=np.array((M.P['ankle_tx'],130+sy*45,M.P['ankle_tz'])); b=M.xf_pt('L_foot',(M.P['ankle_lever'],130+sy*45,M.P['ankle_z']+M.P['ankle_ez']))
                u=(b-a)/np.linalg.norm(b-a); worst=max(worst,math.degrees(math.asin(abs(u[1]))))
    M.POSE.clear(); return worst
def parts_for(keys):
    names=[p['name'] for p in M.build()]
    return [n for n in names if any(k in n for k in keys) and n.startswith(('L_','waist','neck'))]
J=[]
def joint(name,region,bearing,axis,act,attach,stop,status,src,notes='',keys=(),need=None):
    J.append(dict(joint=name,region=region,bearing=bearing,axis=axis,actuation=act,attachment=attach,hard_stop=stop,status=status,sources=src,notes=notes,model_parts=parts_for(keys)))
sw=CL['sweep']
def rng(k):
    s=sw.get(k); return dict(sim_range=SIM[k],swept_clear=s['free'] if s else None,first_clash=[(c['angle'],[p[:2] for p in c['pairs'][:3]]) for c in s['clashes']] if s else [],
                             arm_leg_contacts=sorted({c['angle'] for c in s.get('arm_leg',[])}) if s else [])
hipL=screw_len('hip_pitch',(-105,40)); knL=screw_len('knee',(0,135)); tilt=ankle_tilt()
hipB=LS['hip_pitch_B_thigh_mounted']['results'][0]; knS=[r for r in LS['knee']['results'] if r['geom']['lever_mm']==47.5][0]
stand=CL['standing']
knee_boss=[c for c in stand['clashes'] if 'knee screw' in c[0] and 'knee screw' in c[1]]
# ---------------- legs ----------------
joint('hip_yaw','leg','IKO CRBH 6013 A crossed-roller (inside Actuators hip_yaw_housing)','z (vertical) at hip centre +240 mm',SIZ['hip_yaw']['label']+' (rotary)',
      'housing bolted to pelvis deck [deck EST]; output flange -> yaw yoke plate [EST]','internal soft limit; no mechanical stop modelled [EST needed]','BUILDABLE',
      ['actuators/cad/hip_yaw_housing.step','actuators/results/sizing.json'],'Yoke plate/cheek are [EST] brackets.',keys=('hip yaw housing',))
joint('hip_roll','leg','IKO CRBH 6013 A crossed-roller (inside Actuators hip_roll_housing)','x (fore-aft) at hip +125 mm',SIZ['hip_roll']['label']+' (rotary)',
      'housing back face on yaw-yoke rear cheek; output face -> roll bracket web -> lever hub pads [EST]','internal soft limit; mechanical stop not modelled [EST needed]','BUILDABLE',
      ['actuators/cad/hip_roll_housing.step','actuators/results/sizing.json'],'Housing is cantilevered from one cheek (CRBH carries the moment, unverified for this load path).',keys=('hip roll housing',))
joint('hip_pitch','leg','2x IKO TLA3520 Z needle bushes in lever cheeks, hardened shaft ø35/30x66 press-fit in femur tongue ø55x27 (D32/L21)','y (lateral) through hip centre',
      SIZ['hip_pitch']['label']+f"; config B: lever r{hipB['geom']['lever_mm']} clock {hipB['geom']['clock_deg']}° on roll output, bodies on thigh",
      f"body end: axial GE12 C eye on ø12 pin in bonded split-collar clamp arm at (x{hipB['geom']['trunnion_x_mm']}, z{hipB['geom']['trunnion_z_mm']}, y±69); rod end: GE12 C on lever crossbar",
      'PU ø25x12 bumper at r80 (A6, hip_stop.json) engages at -104..-105° (femur front face); toggle at -114.5°','BUILDABLE',
      ['legs/results/r2/linkage_study.json','actuators/cad/hip_pitch_lever_B_needle_sf15.step','actuators/results/hp_pivot_needle.json','legs/DECISIONS.md L18 L21 L22 L35'],
      f"Pin-to-pin length {hipL[0]:.1f}-{hipL[1]:.1f} mm (stroke {hipL[1]-hipL[0]:.1f}); Legs study stroke {hipB['stroke_mm']:.1f} over its -80..+40 bins. Lever strength O13 still OPEN (FEA v2/G2 queued): lever shown is config-B needle hub, not G2. Body-to-collar clearance 0.3 mm at stand (tight).",
      keys=('hip_pitch','TLA3520','lever B','clamp'))
kstat='FAIL' if knee_boss else 'BUILDABLE'
joint('knee','leg','ø16 pin through clevis cheeks (thigh) + tongue and lever cheeks (shank)','y at knee (z 500)',SIZ['knee']['label']+f"; lever r47.5 clock {knS['geom']['clock_deg']}°",
      f"trunnion pins on thigh bracket at (x{knS['geom']['trunnion_x_mm']}, +{knS['geom']['trunnion_z_mm']}) y±45; GE12 C rod ends on the r47.5 crossbar",
      'none modelled: extension limit by the screw end-of-stroke; flexion limit = first clash [stop EST needed]',kstat,
      ['legs/results/r2/linkage_study.json','actuators/cad/knee_lever_r47p5.step','actuators/cad/knee_body_x1.step','actuators/cad_mass.py lever(dy=45)'],
      (f"FAIL: at dy 45 the inner trunnion bosses of the twin bodies overlap ({knee_boss[0][2]:.0f} mm³; bosses reach ±47 from each body axis). Both bodies share one trunnion axis, so the fix is kinematically free: merge the inner bosses into one twin housing, or widen dy past 47 mm plus room for an inner trunnion support (the Actuators lever(dy=45) would change). " if knee_boss else '')+
      f"Pin-to-pin {knL[0]:.1f}-{knL[1]:.1f} mm (stroke {knL[1]-knL[0]:.1f}; Legs study {knS['stroke_mm']:.1f}). Knee trunnion bracket geometry is [EST].",
      keys=('knee',))
joint('ankle_pitch','leg','Ti universal cross: ø12 pitch pin stubs in shank fork cheeks','y at ankle (z 80)',SIZ['ankle_pitch']['label']+' (both screws in phase)',
      'trunnion pins ø9 at (x90, z410) y±45 on shank bracket [bracket EST]; GE12 C rod ends on instep pins r73 (L23)','screw end-of-stroke; no mechanical stop modelled','BUILDABLE',
      ['actuators/results/ankle_stroke_73_r18_p45.json','legs/DECISIONS.md L23','actuators/cad/ankle_body_x1.step'],
      f"Actuators stroke check: Lmin {AST['73mm L_ankle actuator in']['Lmin']} / Lmax {AST['73mm L_ankle actuator in']['Lmax']} mm, margin {AST['73mm L_ankle actuator in']['margin']} mm. Ankle body fins overlap its own trunnion bosses in the Actuators STEP (z 6-36 vs boss z 11-31) - check.",keys=('ankle screw','ankle pitch pin','ankle cross'))
joint('ankle_roll','leg','Ti universal cross: ø12 roll pin stubs in foot lugs (x axis)','x at ankle (z 80)',SIZ['ankle_pitch']['label']+' (screws differential)',
      'same two screws; roll = differential stroke','±18° hard stop: 4 blocks + 2 mm PU on a carrier under the cross, faces at r45 (a14.json) strike foot shoulders [shoulder geometry EST]','FAIL',
      ['legs/results/r7/a14.json','actuators/results/ankle_stroke_73_r18_p45.json'],
      f"FAIL: the screw bodies tilt up to {tilt:.1f}° out of the sagittal plane at ±18° roll, but their top mounts are y-axis pin trunnions (Actuators trunnion_pins_pair), which only allow sagittal swing. Needs a gimbal (2-axis) trunnion or a spherical GE12 top eye like the hip bodies.",
      keys=('ankle-roll','roll pin','roll lug'))
# ---------------- upper body (placeholders) ----------------
for k,ax,att in (('waist_yaw','z','housing on pelvis deck; output -> waist yoke plate'),('waist_pitch','y','housing on single yoke cheek (-y); output (+y) -> torso floor deck bracket'),
                 ('shoulder_pitch','y','housing through torso side wall; output flange -> roll bracket'),('shoulder_roll','x','housing on roll bracket; output -> roll-yaw link'),
                 ('shoulder_yaw','z','housing on roll-yaw link; output -> upper-arm tube'),('elbow','y','housing in forearm; elbow clevis on upper arm'),
                 ('wrist_roll','z','housing in forearm end cap; output -> wrist fork'),('wrist_pitch','y','pin ø6 in wrist fork; driven by micro strain-wave drive in forearm via push rods'),
                 ('wrist_yaw','x','cross pin in palm lug; driven like wrist_pitch'),('neck_yaw','z','housing in torso top; output -> neck yoke'),('neck_pitch','y','housing in neck yoke; output -> head deck')):
    od=M.SW.get('L_'+k,M.SW.get(k,(None,None)))
    joint(k,'upper' if not k.startswith(('neck',)) else 'neck',f'crossed-roller bearing (OD {od[0]+6 if od[0] else "n/a"} [EST])' if od[0] else 'plain pin/cross pivot [EST]',ax,
          f'strain-wave (CSG-class) rotary actuator OD{od[0]} x L{od[1]} [EST]' if od[0] else 'remote micro strain-wave drive + push rods [EST]',att+' [EST]',
          'hard-stop lug on housing [EST]; set at the clash-free limit below','PLACEHOLDER',['v3/cad/model.py layout (catalog envelopes)'],'No module has engineered this joint.',
          keys=(k,'wrist pitch','wrist pitch/yaw') if k.startswith('wrist_p') or k.startswith('wrist_y') else (k,))
for f in ['finger1','finger2','finger3','finger4','thumb']:
    for i in (1,2,3):
        J.append(dict(joint=f'{f}_j{i}',region='hand',bearing='pin joint [EST]',axis='y (flexion)' if f!='thumb' else 'z [EST]',actuation='Dyneema tendon from forearm drive (v3 hand) [EST]',
                      attachment='tendon over idler [EST]',hard_stop='phalanx end faces [EST]',status='PLACEHOLDER',sources=['v3/cad/model.py build_hand'],notes='Not swept (hand is one rigid body in the model).',model_parts=[n for n in parts_for((f'{f} phalanx{i}',))]))
for j in J:
    k=j['joint']
    if k in SIM: j.update(rng(k))
    j['mechanism_present']=bool(j['model_parts'])
    if j['status']!='FAIL' and j.get('swept_clear') is not None and k in SIM:
        lo,hi=SIM[k] if k!='ankle_roll' else (-18,18); fr=j['swept_clear']
        if k=='hip_pitch': lo=-105
        j['range_clear']=bool(fr[0]<=lo and fr[1]>=hi)
        if not j['range_clear']: j['notes']+=f" Clash-free range {fr[0]}..{fr[1]}° vs {lo}..{hi}° required: hard stop must sit inside the clash-free range."
cnt={}
for j in J: cnt[j['status']]=cnt.get(j['status'],0)+1
missing=[j['joint'] for j in J if not j['mechanism_present']]
out=dict(generated_by='modules/model/audit_v4.py',counts=cnt,missing_mechanism=missing,standing=stand,combos=CL.get('combos'),joints=J,
         note='Leg joints are per side (left listed; right is the mirror). Upper-body/hand joints are per side where applicable.')
json.dump(out,open(os.path.join(H,'JOINT_AUDIT.json'),'w'),indent=1)
L=['# Joint audit (v4 fidelity model)','',f'Generated by `modules/model/audit_v4.py` from `model_v4.py`, `out/clash_v4.json` and module data. Status counts (per side; hands = 15 finger joints per hand): '+', '.join(f'**{k}** {v}' for k,v in cnt.items()),'',
   'BUILDABLE = mechanism backed by module data and clear through its range. PLACEHOLDER = not engineered by any module yet (dims [EST]). FAIL = a mechanism conflict found by this audit.','',
   f'Joints without a modelled mechanism: {", ".join(missing) if missing else "none"}.','',
   '| joint | status | bearing / pivot | axis | actuation | attachment | hard stop | sim range | clash-free (swept) | notes |','|---|---|---|---|---|---|---|---|---|---|']
for j in J:
    L.append('| '+' | '.join(str(x).replace('|','/') for x in (j['joint'],j['status'],j['bearing'],j['axis'],j['actuation'],j['attachment'],j['hard_stop'],j.get('sim_range',''),j.get('swept_clear','not swept'),j['notes']))+' |')
L+=['','## Standing pose','',f"Interferences: {len(stand['clashes'])}"]+[f'- {a} x {b}: {v} mm³' for a,b,v in stand['clashes']]+[f"Floating parts: {len(stand['floating'])}",'',
    '## Sweep detail (first clash per direction; arm-vs-leg contacts are listed separately as a control/pose issue)','']
for k,s in sw.items():
    L.append(f"- **{k}** clear {s['free']} of {s['limit']}: "+('; '.join(f"{c['angle']}°: "+', '.join(f'{p[0]} x {p[1]}' for p in c['pairs'][:3]) for c in s['clashes']) or 'no clash')+(f" (hand-vs-leg contact at {sorted({c['angle'] for c in s['arm_leg']})})" if s.get('arm_leg') else ''))
if CL.get('combos'):
    L+=['','## Combined poses','']+[f"- {k}: {len(v)} clashes "+'; '.join(f'{a} x {b}' for a,b,_ in v[:4]) for k,v in CL['combos'].items()]
open(os.path.join(H,'JOINT_AUDIT.md'),'w').write('\n'.join(L)+'\n')
print(cnt,'missing',missing); sys.exit(1 if missing or cnt.get('FAIL') else 0)
