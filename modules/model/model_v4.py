"""Robot Lab v4 fidelity model (CadQuery). Units mm, frame x fwd / y left / z up, standing pose = all joints 0.
Legs use the ENGINEERED module parts: Actuators STEP solids (modules/actuators/cad/*.step: hip yaw/roll housings,
twin-screw RV12 bodies, hip_pitch lever B needle-hub (G2 FEA pending), knee lever r47.5), linkage geometry from
modules/legs/results/r2/linkage_study.json (hip config B r50/clock60/trunnion x30 z-300; knee r47.5/clock0/trunnion x-130 z270),
ankle instep pin r73 (Legs L23), ±18° ankle-roll stop (legs/results/r7/a14.json), thigh bonded split collar (L22), ø35 tongue +
IKO TLA3520 needle straddle (L21/D32). Layout heights from v3/cad/model.py P.
Upper body: strain-wave rotary + crossed-roller PLACEHOLDERS (no module has engineered them); all their dims are [EST].
Anything not in module data is tagged est=True and named [EST]."""
import cadquery as cq, math, json, os, copy
import numpy as np
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.abspath(os.path.join(HERE,'../..'))
STEPD=os.path.join(ROOT,'modules/actuators/cad')
LS=json.load(open(os.path.join(ROOT,'modules/legs/results/r2/linkage_study.json')))
KNEE_G=[r for r in LS['knee']['results'] if r['geom']['lever_mm']==47.5][0]['geom']
HIP_G=LS['hip_pitch_B_thigh_mounted']['results'][0]['geom']
A14=json.load(open(os.path.join(ROOT,'modules/legs/results/r7/a14.json')))
P=dict(hip_y=130,hip_z=920,knee_z=500,ankle_z=80,pelvis_bot=1126,pelvis_top=1230,torso_top=1610,shoulder_z=1500,shoulder_y=190,
       femur_x=18,femur_od=50,femur_t=1.2,tibia_x=14,tibia_od=45,tibia_t=1.2,
       hip_dy=69,      # Legs L10 fix: screw spacing dy>=69
       knee_dy=45,     # Actuators cad_mass.lever(dy=45) for knee_lever_r47p5
       ankle_dy=45, ankle_lever=73, ankle_tx=90, ankle_tz=450,   # D60: trunnion z 410 -> 450
       ankle_ez=20,   # v3 layout + L23 r73
       upper_arm=300, forearm=270)
# ---------------- kinematics ----------------
JOINTS={}   # name -> dict(seg, parent_seg, point, axis, range, ...)
PARENT={}   # seg -> (joint, parent seg)
POSE={}
try:
    from palm_7075 import palm as _palm7075   # A32 (modules/model/palm_7075.py)
except ImportError as _e:   # guard so audit_v4 still runs if the palm module is missing
    import warnings; warnings.warn(f'palm_7075 unavailable ({_e}); using 32x86x90 envelope box [EST]')
    def _palm7075(c): return cq.Workplane('XY').box(32,86,90).translate(c).val()
def joint(name,parent,child,pt,ax): JOINTS[name]=dict(parent=parent,child=child,pt=pt,ax=ax); PARENT[child]=(name,parent)
def chain(seg):
    out=[]
    while seg in PARENT: j,seg=PARENT[seg]; out.append(j)
    return out[::-1]
def xf_pt(seg,p):
    v=np.array(p,float)
    for jn in reversed(chain(seg)):
        a=math.radians(POSE.get(jn,0.0))
        if not a: continue
        J=JOINTS[jn]; k=np.array(J['ax'],float); k/=np.linalg.norm(k); r=v-np.array(J['pt'])
        r=r*math.cos(a)+np.cross(k,r)*math.sin(a)+k*np.dot(k,r)*(1-math.cos(a)); v=r+np.array(J['pt'])
    return v
def xf_solid(seg,w):
    for jn in reversed(chain(seg)):
        a=POSE.get(jn,0.0)
        if a: J=JOINTS[jn]; w=w.rotate(J['pt'],tuple(p+q for p,q in zip(J['pt'],J['ax'])),a)
    return w
PARTS=[]
def add(name,seg,solid,group='structure',asm=None,est=False,posed=False,deps=None):
    if isinstance(solid,cq.Workplane): solid=solid.val()
    if not posed: solid=xf_solid(seg,solid)
    PARTS.append(dict(name=name+(' [EST]' if est and '[EST]' not in name else ''),seg=seg,solid=solid,group=group,asm=asm or name,est=est,
                      deps=set(deps) if deps else set(chain(seg))))
# ---------------- primitives ----------------
def cyl(od,L,axis='z',id_=0,c=(0,0,0)):
    w=cq.Workplane('XY').circle(od/2)
    if id_: w=w.circle(id_/2)
    s=w.extrude(L).translate((0,0,-L/2))
    if axis=='x': s=s.rotate((0,0,0),(0,1,0),90)
    if axis=='y': s=s.rotate((0,0,0),(1,0,0),90)
    return s.translate(c).val()
def box(dx,dy,dz,c=(0,0,0)): return cq.Workplane('XY').box(dx,dy,dz).translate(c).val()
def sph(d,c): return cq.Workplane('XY').sphere(d/2).translate(c).val()
_STEP={}
def step(n):
    if n not in _STEP: _STEP[n]=cq.importers.importStep(os.path.join(STEPD,n+'.step')).val()
    return _STEP[n].copy()
def frame(shape,origin,zdir,xref):
    z=np.array(zdir,float); z/=np.linalg.norm(z); x=np.array(xref,float); x-=z*np.dot(x,z); x/=np.linalg.norm(x); y=np.cross(z,x)
    from OCP.gp import gp_Trsf
    T=gp_Trsf(); T.SetValues(*[float(v) for v in (x[0],y[0],z[0],origin[0],x[1],y[1],z[1],origin[1],x[2],y[2],z[2],origin[2])])
    return cq.Shape.cast(shape.moved(cq.Location(T)).wrapped)
def along(p0,p1,s,L,od,id_=0):
    d=np.array(p1,float)-np.array(p0,float); u=d/np.linalg.norm(d)
    return frame(cyl(od,L,id_=id_,c=(0,0,L/2)),tuple(np.array(p0)+u*s),u,(1,0,0) if abs(u[0])<0.9 else (0,1,0))
# ---------------- leg mechanisms ----------------
BOSS_Z={'knee_body_x1':(23.09+20)/2,'ankle_body_x1':'eye15','hip_pitch_body_x1':None}   # D61: ankle body axial eye lug at body z -15   # cad_mass.linear_body: bosses at Lm/2
def screw_unit(name,body_step,seg_body,p0,seg_rod,p1,boss_dir,asm,deps,top='trunnion',skip_body=False,eye='GE12'):
    """Twin-screw half: Actuators body STEP (local z = screw axis, base at the top pin) + RV12 rod ø12 + SKF GE12 C rod-end eye (ø30x12)."""
    asm=name; a=xf_pt(seg_body,p0); b=xf_pt(seg_rod,p1); bd=xf_pt(seg_body,np.array(p0)+np.array(boss_dir))-a
    u=(b-a)/np.linalg.norm(b-a); L=float(np.linalg.norm(b-a))
    bz=BOSS_Z[body_step]
    if bz is None:   # hip: axial GE12 eye at the body end on the clamp-arm pin (L18/L22); eye-to-can stub 30 mm [EST]
        off=30.0
        add(f'{name} axial GE12 C eye ø30x12 on body end',seg_body,frame(cyl(30,12,'z'),tuple(a),(0,1,0),u),'bearing',asm,posed=True,deps=deps)
        add(f'{name} eye stub ø12 [EST]',seg_body,along(a,b,6,19,12),'actuator',asm,posed=True,deps=deps)
        add(f'{name} eye stub flange ø30 [EST]',seg_body,along(a,b,24,off-24+1,30),'actuator',asm,posed=True,deps=deps)
    elif bz=='eye15':   # D60/D61: axial GE12 C eye in the body's rear-cap lug (body z -15), held in a shank clevis
        off=15.0
        add(f'{name} axial GE12 C top eye ø30x12 (D60)',seg_body,frame(cyl(30,12,'z'),tuple(a),(0,1,0),u),'bearing',asm,posed=True,deps=deps)
    else: off=-bz   # trunnion bosses sit at Lm/2 along the body: the body base is behind the pivot
    a0=a+u*off
    if not skip_body: add(f'{name} body ({body_step})',seg_body,frame(step(body_step),tuple(a0),u,bd),'actuator',asm,posed=True,deps=deps)
    add(f'{name} RV12 roller-screw rod ø12',seg_rod,along(a,b,off+105,L-off-105-(15 if eye=='QA1' else 9),12),'actuator',asm,posed=True,deps=deps)   # QA1: rod-end shank starts at the head OD (D60)
    if eye=='QA1': add(f'{name} QA1 MGF12T 27° rod end ø30x10.75 (D60)',seg_rod,frame(cyl(30,10.75,'z'),tuple(b),bd,u),'bearing',asm,posed=True,deps=deps)
    else: add(f'{name} GE12 C rod-end eye',seg_rod,frame(cyl(30,12,'z'),tuple(b),bd,u),'bearing',asm,posed=True,deps=deps)
    return L,a0,u,bd
def rot_housing(name,stp,seg,center,axis,out_sign,asm):
    """Actuators housing STEP (local z axis, 0..H). Placed centred on the joint axis."""
    s=step(stp); H=s.BoundingBox().zmax; ax=np.array({'x':(1,0,0),'y':(0,1,0),'z':(0,0,1)}[axis],float)*out_sign
    org=np.array(center)-ax*H/2
    add(name,seg,frame(s,tuple(org),ax,(0,0,1) if axis!='z' else (1,0,0)),'actuator',asm)
    return H
def build_leg(s):
    S=lambda n:('L_' if s>0 else 'R_')+n; y=P['hip_y']*s; hz,kz,az=P['hip_z'],P['knee_z'],P['ankle_z']
    yawz,rollz=hz+240,hz+125
    joint(S('hip_yaw'),'pelvis',S('hipY'),(0,y,yawz),(0,0,1)); joint(S('hip_roll'),S('hipY'),S('hipR'),(0,y,rollz),(1,0,0))
    joint(S('hip_pitch'),S('hipR'),S('thigh'),(0,y,hz),(0,1,0)); joint(S('knee'),S('thigh'),S('shank'),(0,y,kz),(0,1,0))
    joint(S('ankle_pitch'),S('shank'),S('ankX'),(0,y,az),(0,1,0)); joint(S('ankle_roll'),S('ankX'),S('foot'),(0,y,az),(1,0,0))
    # hip yaw: Actuators hip_yaw_housing (TBM2G-06008A + CSG-17-100 + CRBH 6013 A), output down
    H=rot_housing(S('hip yaw housing (Actuators STEP, CRBH 6013 A output)'),'hip_yaw_housing','pelvis',(0,y,yawz),'z',-1,S('hip_yaw'))
    yb=yawz-H/2
    if s>0: add('hip yaw + waist mount deck (pelvis)','pelvis',box(160,364,8,(0,0,yawz+H/2+4)),est=True,asm='pelvis')
    add(S('hip yaw output yoke plate'),S('hipY'),box(140,70,8,(0,y,yb-4)),est=True,asm=S('yoke'))
    # hip_yaw hard stop (L39): tab on the yoke plate at r64 (outside the r55 housing) strikes 2 PU 90A ø16x10 bumpers on brackets under the deck at -47/+57 deg (contact at -35/+45)
    ph0=-90*s   # tab points to the midline so it never reaches the pelvis side wall
    add(S('hip_yaw stop tab 10x12x70 (L39)'),S('hipY'),box(10,12,70,(64*math.cos(math.radians(ph0)),y+64*math.sin(math.radians(ph0)),yb+35)),'stop',asm=S('yoke'))
    add(S('hip_yaw stop tab arm 12x40x8 (yoke plate -> tab, L39)'),S('hipY'),box(12,40,8,(0,y-s*(35+20-0.5),yb-4)),'stop',asm=S('yoke'))
    for lim in (-35,45):
        a_=math.radians(ph0+lim+(17 if lim>0 else -17)); add(S(f'hip_yaw PU bumper + bracket {lim:+d}° (L39)'),'pelvis',cyl(16,30,'z',c=(64*math.cos(a_),y+64*math.sin(a_),yawz+H/2-15)),'stop',asm='pelvis')
    Hr=step('hip_roll_housing').BoundingBox().zmax
    add(S('hip yaw yoke rear cheek (roll housing back face)'),S('hipY'),box(8,70,yb-8-(rollz-35),(-(Hr/2+4),y,(yb-8+rollz-35)/2)),est=True,asm=S('yoke'))
    # hip roll: Actuators hip_roll_housing, axis x
    rot_housing(S('hip roll housing (Actuators STEP, CRBH output)'),'hip_roll_housing',S('hipY'),(0,y,rollz),'x',1,S('yoke'))
    # hip_roll hard stop (L39): lug on the roll-output web top (r63 above the roll axis) strikes 2 PU 90A ø20x10 bumpers under the yaw yoke plate at -26/+29 deg (contact at -12/+15)
    add(S('hip_roll stop lug 12x12x26 (L39)'),S('hipR'),box(12,12,26,(Hr/2+14,y,rollz+50)),'stop',asm=S('hipR_br'))
    for ang in (-32,28):
        a_=math.radians(ang); add(S(f'hip_roll PU bumper block {ang:+d}° (L39)'),S('hipY'),box(14,20,yb-8-(rollz+65*math.cos(a_))+5,(Hr/2+14,y+65*math.sin(a_),(yb-8+rollz+65*math.cos(a_)-5)/2)),'stop',asm=S('yoke'))
    # roll output bracket (hipR) -> hip_pitch lever hub
    lev=step('hip_pitch_lever_B_needle_sf15').rotate((0,0,0),(0,1,0),HIP_G['clock_deg']); ht=hz+lev.BoundingBox().zmax
    add(S('roll-output bracket web (on roll output face)'),S('hipR'),box(8,76,rollz+40-(hz+60),(Hr/2+4,y,(rollz+40+hz+60)/2)),est=True,asm=S('hipR_br'))
    for sy in (-1,1):
        add(S(f'roll-output bracket web leg {"+" if sy>0 else "-"}y (slot |y|<26.5 for tongue neck + femur at deep flexion)'),S('hipR'),box(8,12,hz+60-ht+1,(Hr/2+4,y+sy*32.5,(hz+60+ht)/2)),est=True,asm=S('hipR_br'))
        add(S(f'roll-output bracket pad {"+" if sy>0 else "-"}y (bolts to lever cheek top)'),S('hipR'),box(Hr/2+8+20,12,8,((Hr/2+8-20)/2,y+sy*32.5,ht+4)),est=True,asm=S('hipR_br'))
    # hip pitch pivot: lever B needle hub (Actuators STEP) on hipR, ø35 shaft press-fit in femur tongue, 2x IKO TLA3520 in lever cheeks
    hp=S('hip_pitch')
    add(S('hip_pitch lever B needle hub (Actuators STEP; G2 rework queued)'),S('hipR'),lev.translate((0,y,hz)),'linkage',asm=S('hipR_br'))
    add(S('hip_pitch shaft ø35/30 x66 hardened'),S('thigh'),cyl(35,66,'y',id_=30,c=(0,y,hz)),'bearing',asm=S('hp_pivot'))
    for sy in (-1,1): add(S(f'IKO TLA3520 needle bush {"in" if sy*s<0 else "out"}'),S('thigh'),cyl(42,20,'y',id_=35,c=(0,y+sy*24,hz)),'bearing',asm=S('hp_pivot'))
    # hip pitch stop: PU bumper (Legs R-020 A6, -105 deg) on the bracket foot, struck by the tongue neck [geometry EST]
    # A6 bumper: PU ø25x12 at r 80 (legs/results/r5/hip_stop.json); placed where the femur's front face reaches r80 at -105° [placement EST]
    a=math.radians(-105); qx,qz=P['femur_x']+P['femur_od']/2+6+1,-80; bx=qx*math.cos(a)+qz*math.sin(a); bz=-qx*math.sin(a)+qz*math.cos(a)
    add(S('hip_pitch -105° PU bumper ø25x12 r80 (A6)'),S('hipR'),cyl(25,12,'z',c=(bx,y,hz+bz)),'stop',asm=S('hipR_br'))
    add(S('hip_pitch bumper arm (bracket web -> bumper)'),S('hipR'),box(bx+12.5-(Hr/2+8),30,8,((bx+12.5+Hr/2+8)/2,y,hz+bz+10)),est=True,asm=S('hipR_br'))
    # thigh (Legs): femur tongue ø55x27 + neck, femur tube, bonded split collar + sleeve + 2 pins, clamp arms to ±69, GE12 eye pins
    add(S('femur tongue ø55x27 (ø35 press-fit bore)'),S('thigh'),cyl(55,27,'y',id_=35,c=(0,y,hz)),asm=S('thigh_s'))
    add(S('femur tongue neck (55 mm, L36)'),S('thigh'),box(30,27,40,(10,y,hz-36)),asm=S('thigh_s'))
    ft=hz-56; fb=kz+60
    add(S('femur tube 7050-T7451 ø50x1.2 (R-031; P-047 wall 1.6 pending FEA)'),S('thigh'),cyl(50,ft-fb,'z',id_=47.6,c=(P['femur_x'],y,(ft+fb)/2)),asm=S('thigh_s'))
    add(S('femur internal doubler sleeve 0.5x100 (r8)'),S('thigh'),cyl(47.6,100,'z',id_=46.6,c=(P['femur_x'],y,(ft+fb)/2)),asm=S('thigh_s'))
    tz=hz+HIP_G['trunnion_z_mm']; tx=HIP_G['trunnion_x_mm']
    add(S('thigh split collar ø64 L34 bonded (DP490) + sleeve + 2x ø6 pins'),S('thigh'),cyl(64,34,'z',id_=50,c=(P['femur_x'],y,tz)),asm=S('thigh_s'))
    for sy in (-1,1):
        add(S(f'clamp arm root {"+" if sy>0 else "-"}y (depth 34, r8)'),S('thigh'),box(28,24,34,(tx-4,y+sy*38,tz)),asm=S('thigh_s'))
        add(S(f'clamp arm outer step {"+" if sy>0 else "-"}y (depth 24 to the tines, L37)'),S('thigh'),box(28,13.2,24,(tx-4,y+sy*56.5,tz-5)),asm=S('thigh_s'))
        for k in (-1,1): add(S(f'clamp arm eye tine {"+" if sy>0 else "-"}y{"o" if k>0 else "i"} [fork form EST]'),S('thigh'),box(30,8,24,(tx,y+sy*(P['hip_dy']+k*10),tz)),asm=S('thigh_s'))
        add(S(f'clamp eye pin ø12x28 42CrMo4 {"+" if sy>0 else "-"}y'),S('thigh'),cyl(12,28,'y',c=(tx,y+sy*P['hip_dy'],tz)),'bearing',asm=S('thigh_s'))
    E=lambda r,clk,t:(-r*math.sin(math.radians(clk+t)),-r*math.cos(math.radians(clk+t)))
    ex,ez=E(HIP_G['lever_mm'],HIP_G['clock_deg'],0)
    for sy in (-1,1):
        screw_unit(S(f'hip_pitch screw {"+" if sy>0 else "-"}y'),'hip_pitch_body_x1',S('thigh'),(tx,y+sy*P['hip_dy'],tz),S('hipR'),(ex,y+sy*P['hip_dy'],hz+ez),(1,0,0),S('hp_act'),chain(S('thigh')))
    # knee: clevis (thigh) + tongue (shank) + pin ø16; knee lever r47.5 (Actuators STEP) on shank; twin screws, trunnion x-130 z+270 on thigh
    add(S('knee clevis bridge 40x70x22 + 16 mm pad over cheeks (fea_r8, L36)'),S('thigh'),cq.Workplane('XY').add(box(40,70,22,(23,y,kz+51))).union(cq.Workplane('XY').add(box(16,14,22,(-5,y+21+7,kz+51)))).union(cq.Workplane('XY').add(box(16,14,22,(-5,y-21-7,kz+51)))).val(),asm=S('thigh_s'))
    for sy in (-1,1): add(S(f'knee clevis cheek {"+" if sy>0 else "-"}y 46x14x62 (fea_r5/r8)'),S('thigh'),cq.Workplane('XY').add(cyl(46,14,'y',c=(0,y+sy*28,kz))).union(cq.Workplane('XY').add(box(42,14,41,(2,y+sy*28,kz+20.5)))).val(),asm=S('thigh_s'))   # L40: rounded R23 about the pin below centre
    add(S('knee pin ø16 (through clevis + lever cheeks)'),S('shank'),cyl(16,132,'y',c=(0,y,kz)),'bearing',asm=S('knee_pin'))
    add(S('knee tongue (shank)'),S('shank'),cyl(56,28,'y',id_=16,c=(0,y,kz)),asm=S('shank_s'))
    add(S('knee tongue neck into tibia'),S('shank'),box(36,28,40,(10,y,kz-42)),asm=S('shank_s'))
    add(S('knee lever r47.5 (Actuators STEP)'),S('shank'),step('knee_lever_r47p5').rotate((0,0,0),(0,1,0),KNEE_G['clock_deg']).translate((0,y,kz)),'linkage',asm=S('shank_s'))
    ktx,ktz=KNEE_G['trunnion_x_mm'],kz+KNEE_G['trunnion_z_mm']; kx,kzz=E(KNEE_G['lever_mm'],KNEE_G['clock_deg'],0)
    for sy in (-1,1):
        _,a0k,uk,bdk=screw_unit(S(f'knee screw {"+" if sy>0 else "-"}y'),'knee_body_x1',S('thigh'),(ktx,y+sy*P['knee_dy'],ktz),S('shank'),(kx,y+sy*P['knee_dy'],kz+kzz),(0,1,0),S('kn_act'),chain(S('shank')),skip_body=True)
        if sy>0: a0p=a0k
        else: a0m=a0k
    add(S('knee twin housing (Actuators D59 STEP, shared centre web)'),S('thigh'),frame(step('knee_twin_housing'),tuple((a0p+a0m)/2),uk,bdk),'actuator',S('kn_act'),posed=True,deps=chain(S('shank')))
    add(S('knee trunnion bracket top plate (thigh)'),S('thigh'),box(-40-(ktx-45),196,8,((-40+ktx-45)/2,y,ktz+50)),est=True,asm=S('kn_br'))
    add(S('knee trunnion bracket strut to femur'),S('thigh'),box(50,40,8,(-20,y,ktz+50)),est=True,asm=S('kn_br'))
    for sy in (-1,1):
        add(S(f'knee trunnion cheek {"+" if sy>0 else "-"}y'),S('thigh'),box(30,6,70,(ktx,y+sy*(P['knee_dy']+47+3),ktz+19)),est=True,asm=S('kn_br'))
        add(S(f'knee trunnion pin ø9 {"+" if sy>0 else "-"}y'),S('thigh'),cyl(9,16,'y',c=(ktx,y+sy*(P['knee_dy']+44),ktz)),'bearing',asm=S('kn_br'))
    # shank
    tt,tb=kz-50,az+56
    add(S('tibia tube 7075 ø45x1.2'),S('shank'),cyl(45,tt-tb,'z',id_=42.6,c=(P['tibia_x'],y,(tt+tb)/2)),asm=S('shank_s'))
    add(S('tibia internal doubler sleeve 0.5x100 (r8)'),S('shank'),cyl(42.6,100,'z',id_=41.6,c=(P['tibia_x'],y,(tt+tb)/2)),asm=S('shank_s'))
    add(S('ankle fork bridge'),S('shank'),box(56,60,14,(6,y,az+56)),asm=S('shank_s'))
    for sy in (-1,1): add(S(f'ankle fork cheek {"+" if sy>0 else "-"}y'),S('shank'),box(40,6,56,(0,y+sy*27,az+28)),asm=S('shank_s'))
    for sy in (-1,1):
        screw_unit(S(f'ankle screw {"+" if sy>0 else "-"}y'),'ankle_body_x1',S('shank'),(P['ankle_tx'],y+sy*P['ankle_dy'],P['ankle_tz']),S('foot'),(P['ankle_lever'],y+sy*P['ankle_dy'],az+P['ankle_ez']),(0,1,0),S('an_act'),chain(S('foot')),eye='QA1')
    atz=P['ankle_tz']
    add(S('ankle trunnion bracket top plate (shank)'),S('shank'),box(P['ankle_tx']+40-40,180,8,((P['ankle_tx']+40+40)/2,y,atz+46)),est=True,asm=S('an_br'))
    add(S('ankle trunnion bracket strut to tibia'),S('shank'),box(16,30,60,(38,y,atz+20)),est=True,asm=S('an_br'))
    for sy in (-1,1):   # D60: two clevises at y±45 (slot 10.75+2x0.6 = 11.95, PTFE thrust washers, ø12 pin) for the axial top eye
        for k in (-1,1): add(S(f'ankle top clevis tine {"+" if sy>0 else "-"}y{"o" if k>0 else "i"} 7075-T6 6x30 e12 rootR3 (D60/D63)'),S('shank'),box(30,6,58,(P['ankle_tx'],y+sy*(P['ankle_dy']+k*8.975),atz+17)),asm=S('an_br'))
        add(S(f'ankle top clevis pin ø12 {"+" if sy>0 else "-"}y (D60)'),S('shank'),cyl(12,24,'y',c=(P['ankle_tx'],y+sy*P['ankle_dy'],atz)),'bearing',asm=S('an_br'))
    # ankle cross (universal): pitch pins in fork (y), roll pins in foot lugs (x); ±18° roll stop blocks on the cross (A14)
    add(S('ankle cross Ti-6Al-4V'),S('ankX'),box(30,46,30,(0,y,az)),asm=S('ank_x'))
    for sy in (-1,1): add(S(f'ankle pitch pin stub ø12 {"+" if sy>0 else "-"}y'),S('ankX'),cyl(12,18,'y',c=(0,y+sy*24,az)),'bearing',asm=S('ank_x'))
    for sx in (-1,1):
        for sy in (-1,1): add(S(f'ankle-roll ±18° stop block 20x12x10 + 2 mm PU {"F" if sx>0 else "R"}{"+" if sy>0 else "-"}y (A14, face r45)'),S('ankX'),box(12,14,10,(sx*21,y+sy*38,az-25)),'stop',asm=S('ank_x'))
    add(S('ankle-roll stop carrier under cross [EST]'),S('ankX'),box(54,62,15,(0,y,az-22.5)),est=True,asm=S('ank_x'))
    for sx in (-1,1):
        add(S(f'ankle roll pin stub ø12 {"F" if sx>0 else "R"}'),S('foot'),cyl(12,22,'x',c=(sx*26,y,az)),'bearing',asm=S('foot_s'))
        add(S(f'foot roll lug {"F" if sx>0 else "R"}'),S('foot'),box(8,30,az+10-18,(sx*36,y,(az+10+18)/2)),asm=S('foot_s'))
        for sy in (-1,1): add(S(f'foot roll-stop shoulder {"F" if sx>0 else "R"}{"+" if sy>0 else "-"}y [gap 15 mm = 18° at r48]'),S('foot'),box(12,16,az-45-18,(sx*21,y+sy*48,(az-45+18)/2)),'stop',est=True,asm=S('foot_s'))
    add(S('ankle 6-axis F/T sensor'),S('foot'),cyl(60,14,'z',c=(0,y,az-47)),'sensor',asm=S('foot_s'))
    add(S('foot closed box 240x100x18 (3.5 mm skins, 4 webs; fea_r5)'),S('foot'),box(240,100,18,(60,y,9)),asm=S('foot_s'))
    add(S('ankle F/T steel flange OD60/ID22 x8 (fea_r5)'),S('foot'),cyl(60,8,'z',id_=22,c=(0,y,22)),asm=S('foot_s'))
    add(S('foot flange doubler collar r30.2-45 x3 (r8, L36)'),S('foot'),cyl(90,3,'z',id_=60.4,c=(0,y,19.5)),asm=S('foot_s'))
    add(S('instep tower 30x90 to z50 (fea_r5)'),S('foot'),box(30,90,32,(73,y,34)),asm=S('foot_s'))
    add(S('instep outrigger beam 20x145x10 (lugs outside the 100 mm foot, L38)'),S('foot'),box(20,145,10,(73,y,55)),asm=S('foot_s'))
    for sy in (-1,1): add(S(f'instep lug r73 {"+" if sy>0 else "-"}y (inner face y57.5, D60/L38)'),S('foot'),box(20,15,az+P['ankle_ez']+8-50,(P['ankle_lever'],y+sy*65,(50+az+P['ankle_ez']+8)/2)),asm=S('foot_s'))
    for sy in (-1,1):
        add(S(f'instep pin ø12 {"+" if sy>0 else "-"}y (39-72.5, +5 mm, D60)'),S('foot'),cyl(12,33.5,'y',c=(P['ankle_lever'],y+sy*55.75,az+P['ankle_ez'])),'bearing',asm=S('foot_s'))
        add(S(f'instep rod-end spacer ø16x4.5 {"+" if sy>0 else "-"}y (ball face y53 -> lug 57.5, D60)'),S('foot'),cyl(16,4.5,'y',id_=12,c=(P['ankle_lever'],y+sy*55.25,az+P['ankle_ez'])),'bearing',asm=S('foot_s'))
# ---------------- upper body placeholders ----------------
SW={}  # placeholder strain-wave actuators: joint -> (OD, L) [EST, v3 catalog envelopes rounded]
def sw(jn,seg,axis,c,OD,L,out=1):
    ax={'x':0,'y':1,'z':2}[axis]; SW[jn]=(OD,L)
    o=list(c); o[ax]+=out*(L/2+4)
    add(f'{jn} strain-wave housing (motor+CSG) OD{OD}',seg,cyl(OD,L,axis,c=c),'actuator',est=True,asm=jn+'_h')
    add(f'{jn} crossed-roller bearing',seg,cyl(OD+6,8,axis,id_=OD*0.55,c=tuple(o)),'bearing',est=True,asm=jn+'_h')
    s=list(c); s[(ax+2)%3]+=OD/2+3
    add(f'{jn} hard-stop lug',seg,box(8,8,8,tuple(s)),'stop',est=True,asm=jn+'_h')
def build_upper():
    pb,pt,tt=P['pelvis_bot'],P['pelvis_top'],P['torso_top']
    pel=cq.Workplane('XY').box(170,370,pt-pb).translate((0,0,(pb+pt)/2)).faces('<Z or >Z').shell(-4)
    add('pelvis shell 7075 4 mm (open top/bottom)','pelvis',pel,asm='pelvis')
    dk=P['hip_z']+240+step('hip_yaw_housing').BoundingBox().zmax/2+8   # top of the hip-yaw deck
    wy=dk+35; wp=dk+143
    joint('waist_yaw','pelvis','waistY',(0,0,wy),(0,0,1)); joint('waist_pitch','waistY','torso',(0,0,wp),(0,1,0))
    sw('waist_yaw','pelvis','z',(0,0,wy),110,70)
    add('waist yaw output yoke plate','waistY',box(120,140,8,(0,0,wy+43+4)),est=True,asm='waist_y')
    add('waist yoke cheek -y (pitch housing back face)','waistY',box(70,8,wp+30-(wy+51),(0,-59,(wp+30+wy+51)/2)),est=True,asm='waist_y')
    sw('waist_pitch','waistY','y',(0,0,wp),100,110)
    tb=wp+60
    ts=cq.Workplane('XY').box(220,340,tt-tb).translate((0,0,(tb+tt)/2)).faces('<Z').shell(-3)
    add('torso shell CFRP 3 mm (open bottom)','torso',ts,asm='torso')
    add('torso waist bracket (on pitch output +y)','torso',box(70,8,tb-(wp-30),(0,67,(tb+wp-30)/2)).fuse(box(220,340,8,(0,0,tb-4))),est=True,asm='torso')
    add('battery pack 13S Molicel P45B','torso',box(185,220,144,(12,0,tb+72)),'power',asm='torso_in')
    add('compute bay Jetson AGX Thor','torso',box(130,200,40,(8,0,tb+164)),'electronics',asm='torso_in')
    for s in (1,-1):
        S=lambda n:('L_' if s>0 else 'R_')+n; z=P['shoulder_z']; y=P['shoulder_y']*s
        joint(S('shoulder_pitch'),'torso',S('shP'),(0,y,z),(0,1,0)); joint(S('shoulder_roll'),S('shP'),S('shR'),(0,y+s*70,z),(1,0,0))
        ua=P['upper_arm']; ez=z-ua; fa=P['forearm']; wz=ez-fa; ya=y+s*80
        joint(S('shoulder_yaw'),S('shR'),S('uarm'),(0,ya,z-120),(0,0,1)); joint(S('elbow'),S('uarm'),S('farm'),(0,ya,ez),(0,1,0))
        joint(S('wrist_roll'),S('farm'),S('wR'),(0,ya,wz+40),(0,0,1)); joint(S('wrist_pitch'),S('wR'),S('wP'),(0,ya,wz),(0,1,0)); joint(S('wrist_yaw'),S('wP'),S('hand'),(0,ya,wz),(1,0,0))
        sw(S('shoulder_pitch'),'torso','y',(0,y-s*5,z),96,80,s)
        add(S('shoulder pitch output flange'),S('shP'),cyl(80,6,'y',c=(0,y+s*42,z)),est=True,asm=S('shP'))
        add(S('shoulder roll bracket'),S('shP'),box(100,10,50,(0,y+s*50,z)),est=True,asm=S('shP'))
        sw(S('shoulder_roll'),S('shP'),'x',(0,y+s*90,z),84,80)
        add(S('roll-yaw link'),S('shR'),box(60,40,50,(0,ya,z-64)),est=True,asm=S('shR'))
        sw(S('shoulder_yaw'),S('shR'),'z',(0,ya,z-120),76,64,-1)
        t0=z-120-32-8; t1=ez+53
        add(S('upper arm tube 7075 ø50x2'),S('uarm'),cyl(50,t0-t1,'z',id_=46,c=(0,ya,(t0+t1)/2)),est=True,asm=S('uarm'))
        add(S('elbow clevis'),S('uarm'),box(60,96,10,(0,ya,ez+48)).fuse(box(50,8,48,(0,ya+44,ez+22))).fuse(box(50,8,48,(0,ya-44,ez+22))),est=True,asm=S('uarm'))
        sw(S('elbow'),S('farm'),'y',(0,ya,ez),72,66)
        f0=ez-36; f1=wz+57
        add(S('forearm shell (6 tendon drives inside)'),S('farm'),cyl(70,f0-f1,'z',id_=66,c=(0,ya,(f0+f1)/2)),est=True,asm=S('farm'))
        sw(S('wrist_roll'),S('farm'),'z',(0,ya,wz+40),56,34)
        add(S('forearm wrist end cap'),S('farm'),cyl(70,4,'z',id_=20,c=(0,ya,wz+59)),est=True,asm=S('farm'))
        add(S('wrist pitch/yaw cross (2x micro strain-wave drive in forearm, push rods)'),S('wP'),box(22,22,22,(0,ya,wz)),est=True,asm=S('wrist'))
        add(S('wrist roll output fork'),S('wR'),box(40,40,6,(0,ya,wz+20)).fuse(box(30,6,26,(0,ya+17,wz+6))).fuse(box(30,6,26,(0,ya-17,wz+6))),est=True,asm=S('wrist'))
        add(S('wrist pitch pin ø6'),S('wP'),cyl(6,40,'y',c=(0,ya,wz)),'bearing',est=True,asm=S('wrist'))
        add(S('palm 7075-T6 machined shell 1.5 mm w/ openings (P-021/A32, palm_7075.py)'),S('hand'),_palm7075((0,ya,wz-60)),asm=S('hand'))
        add(S('palm wrist lug'),S('hand'),box(24,12,32,(0,ya,wz-11)),est=True,asm=S('hand'))   # A42/R5 palm DROP 12: lug keeps the yaw-pin end (top z +5) and now reaches the dropped wrist plate (z -27)
        for i,dy in enumerate([-30,-10,10,30]):
            zc=wz-117   # A42/R5: -12 mm with palm_7075.DROP_MM
            for j,l in enumerate([42,26,20]):
                add(S(f'finger{i+1} phalanx{j+1}'),S('hand'),cyl(15-2*j,l,'z',c=(0,ya+dy*s,zc-l/2)),est=True,asm=S('hand')); zc-=l
        for j,l in enumerate([38,30,24]):
            add(S(f'thumb phalanx{j+1}'),S('hand'),cyl(17-2*j,l,'x',c=(16+l/2+sum([38,30,24][:j]),ya-s*30,wz-82)),est=True,asm=S('hand'))   # A42/R5: thumb -12 mm
    joint('neck_yaw','torso','neckY',(0,0,tt+20),(0,0,1)); joint('neck_pitch','neckY','head',(0,0,tt+70),(0,1,0))
    # Head/neck v5-tweak (modules/head/HEAD_BALANCER.md, P-019): 2x Dynamixel XM430-W350-R (28.5x46.5x34, 82 g) on 12 V RS485,
    # ZED X Mini (94x32x37, 150 g). Shell = CF prepreg layup on a machined mould (no 3D printing). Brackets 7075 machined [EST].
    add('neck_yaw servo Dynamixel XM430-W350-R (on torso top, horn up)','torso',box(46.5,34,28.5,(0,0,tt+14.5)),'actuator',asm='neck')
    add('neck yoke 7075 machined','neckY',box(70,80,6,(0,0,tt+31.75)).fuse(box(40,6,46,(0,37,tt+56))).fuse(box(40,6,46,(0,-37,tt+56))),est=True,asm='neck')
    add('neck_pitch servo Dynamixel XM430-W350-R','neckY',box(34,46.5,28.5,(0,-10.75,tt+52)),'actuator',asm='neck')
    hc=(10,0,tt+170)
    add('head shell CF prepreg layup 1.2 mm','head',cq.Workplane('XY').sphere(95).translate(hc).cut(cq.Workplane('XY').sphere(93.8).translate(hc)).cut(cq.Workplane('XY').box(120,120,60).translate((0,0,tt+70))),est=True,asm='head')
    add('head neck mount deck 6061 sheet','head',box(130,130,3,(0,0,tt+103)).fuse(box(60,68,26,(0,0,tt+89))),est=True,asm='head')
    add('stereo camera ZED X Mini','head',box(37,94,32,(85.3,0,tt+170)),'sensor',asm='head')
def build(pose=None):
    PARTS.clear(); JOINTS.clear(); PARENT.clear(); POSE.clear(); POSE.update(pose or {})
    build_upper(); build_leg(1); build_leg(-1)
    return PARTS
