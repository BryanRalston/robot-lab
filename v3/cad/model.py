"""Robot Lab v3 parametric CAD (v2 geometry + catalog-part envelopes from v3/analysis, CRBH output bearings, bolts, fins, tendon hand, wider stance) (CadQuery). Units: mm, kg. Frame: x forward, y left, z up. Standing pose = all joints 0.
Dimensions come from v2/analysis (design.py, checks). Envelopes of bought parts are APPROXIMATE (verify vs. vendor drawings):
CSG component sets and frameless motors are modeled as solid envelopes with an effective density that matches the budget mass."""
import cadquery as cq, math, sys, copy, json, os
sys.path.insert(0,'../../v2/analysis'); import design as D
sys.path.insert(0,'../analysis'); import parts as PT
V3=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'../analysis/results/v3.json'))); ST=V3['state']
DES=D.final(); GEO=DES['GEO']; J=DES['JOINTS']; MOT=DES['MOTORS']; GR=DES['GEARS']
P=dict(  # ---- layout parameters (mm). FIX log in README tracks changes made after clash checks.
 hip_y=130,   # v3 FIX (2 iterations: 115 still clashed at single-leg adduction -6°): was 100 -> single-leg adduction clashed with the other leg; pelvis 300 wide still encloses both yaw housings
 hip_z=920, knee_z=500, ankle_z=80, foot_len=240, heel=60,
 knee_act_x=-95,   # FIX: was -80 -> knee actuator body hit femur tube           # knee linear actuator offset behind femur axis
 ankle_act_x=-62, ankle_act_dy=45,   # v3 FIX: was 37 -> finned ankle actuator bodies (fin OD 86) overlapped
 ankle_lever=50,   # FIX: dy was 30 -> in/out ankle actuator bodies overlapped
 roll_z_off=125,           # hip roll axis height above hip pitch axis
 yaw_z_off=240,          # FIX: was 210/230 -> yoke top plate needs room between roll housing and yaw output            # hip yaw actuator center above hip pitch axis
 pelvis_bot=1126, pelvis_top=1230, torso_top=1590,   # v3 FIX: was 1556 -> catalog neck-yaw housing hit the compute bay
   # FIX: torso_top was 1540 -> shoulder-pitch housing hit torso top wall
 shoulder_z=1500, shoulder_y=190, sh_roll_dy=92,   # FIX: shoulder roll moved outboard (was +45) to clear pitch housing
 femur_x=18,   # FIX: femur axis moved 18 mm forward so the knee lever/rod can swing behind it (knee was clash-free only to 40°)
 wall=3.0, femur_od=50, femur_t=2.0, tibia_od=45, tibia_t=2.0,
)
MAT={'7075-T6':2.81e-6,'CFRP':1.55e-6,'steel':7.85e-6,'Ti-6Al-4V':4.43e-6,'PA12':1.01e-6}  # kg/mm^3
# approximate envelopes (OD, axial length) mm, ESTIMATES
MOTOR_ENV_V2={'M115':(115,35),'M85':(85,30),'M60':(60,25),'M38':(38,20)}
GEAR_ENV={'CSG-14-100':(50,22),'CSG-17-100':(60,25),'CSG-20-100':(70,28),'CSG-25-100':(85,32),'CSG-32-100':(110,40),'SW-14-100':(50,22),'SW-11-100':(40,18)}
PARTS=[]  # dict(name, seg, solid, mat, mass_override, group)
POSE={}    # joint angles deg, keys like 'L_hip_pitch'
CHAINS={}  # seg -> list of (joint_name, point, axis) root-first, rest-pose world axes
def seg_xf_point(seg,p):
    import numpy as np
    v=np.array(p,float)
    for jn,pt,ax in reversed(CHAINS.get(seg,[])):
        a=math.radians(POSE.get(jn,0.0))
        if a==0: continue
        k=np.array(ax,float);k/=np.linalg.norm(k);r=v-np.array(pt)
        r=r*math.cos(a)+np.cross(k,r)*math.sin(a)+k*np.dot(k,r)*(1-math.cos(a));v=r+np.array(pt)
    return tuple(float(x) for x in v)
def seg_xf_solid(seg,w):
    for jn,pt,ax in reversed(CHAINS.get(seg,[])):
        a=POSE.get(jn,0.0)
        if a: w=w.rotate(pt,tuple(p+q for p,q in zip(pt,ax)),a)
    return w
def add(name,seg,solid,mat='7075-T6',mass=None,group='structure',posed=False):
    if not posed: solid=seg_xf_solid(seg,solid)
    PARTS.append(dict(name=name,seg=seg,solid=solid,mat=mat,mass=mass,group=group))
def cyl(od,L,axis='z',id_=0,center=(0,0,0)):
    w=cq.Workplane('XY').circle(od/2)
    if id_: w=w.circle(id_/2)
    s=w.extrude(L).translate((0,0,-L/2))
    if axis=='x': s=s.rotate((0,0,0),(0,1,0),90)
    if axis=='y': s=s.rotate((0,0,0),(1,0,0),90)
    return s.translate(center)
def box(dx,dy,dz,center=(0,0,0)): return cq.Workplane('XY').box(dx,dy,dz).translate(center)
def shell_box(dx,dy,dz,t,center):
    return box(dx,dy,dz,center).cut(box(dx-2*t,dy-2*t,dz-2*t,center))
def menv(mname):
    """TBM2G frame code -> (stator OD, axial length incl. end turns) mm. Frame digits ~ stator OD and stack length [EST from Kollmorgen drawings; verify]."""
    return int(mname[6:9])+2, int(mname[9:11])+16
ACT_DIM={}
def act_dim(joint):
    d=ST['J'][joint]; b=dict(PT.CRBH)[ST['bearing'][joint]]; mod,mL=menv(d['motor']); god,gL=GEAR_ENV[d['gear']]
    return max(mod,god,b['D'])+2*P['wall']+4, mL+gL+b['B']+22
def bolt_circle(n,size,pcd,axis,center,L):
    """n socket-head bolts (shank Ø=size) on a pitch circle, axis-parallel; returns one solid."""
    out=None
    for i in range(n):
        a=2*math.pi*i/n; u,v=pcd/2*math.cos(a),pcd/2*math.sin(a)
        c={'x':(center[0],center[1]+u,center[2]+v),'y':(center[0]+u,center[1],center[2]+v),'z':(center[0]+u,center[1]+v,center[2])}[axis]
        b=cyl(size,L,axis,center=c); out=b if out is None else out.union(b)
    return out
def rotary_actuator(name,seg,joint,axis,center,side=1):
    """Housing (7075 shell) + TBM2G frameless motor + CSG component set + IKO CRBH output bearing + AksIM-2 ring + Everest XCR drive + output bolt circle.
    Parts and masses from v3/analysis (catalog); envelopes [EST]."""
    d=ST['J'][joint]; mo=d['motor']; ge=d['gear']; bn=ST['bearing'][joint]; b=dict(PT.CRBH)[bn]
    mod,mL=menv(mo); god,gL=GEAR_ENV[ge]
    OD=max(mod,god,b['D'])+2*P['wall']+4; L=mL+gL+b['B']+22
    ACT_DIM[name]=(OD,L)
    bore=min(god*0.3,mod*0.45)-1
    h=cyl(OD,L,axis,center=center).cut(cyl(OD-2*P['wall'],L-8,axis,center=center)).cut(cyl(bore,L+2,axis,center=center))   # v3: hollow through-bore for cables/tendons
    add(f'{name} housing',seg,h,'7075-T6',group='actuator')
    off=lambda dd: tuple(c+(dd*side if a==axis else 0) for c,a in zip(center,'xyz'))
    add(f'{name} motor ({mo}, Kollmorgen frameless)',seg,cyl(mod-2,mL,axis,id_=mod*0.45,center=off(-(L/2-4-mL/2))),'steel',mass=PT.MOT[mo]['mass'],group='actuator')
    gm=PT.CSG[ge]['mass'] or {'CSG-14-100':0.09,'CSG-17-100':0.15}.get(ge,0.3)
    add(f'{name} {ge} Harmonic Drive component set',seg,cyl(god-2,gL,axis,id_=god*0.3,center=off(L/2-4-b['B']-gL/2)),'steel',mass=gm,group='actuator')
    add(f'{name} {bn} crossed-roller output bearing (IKO)',seg,cyl(b['D'],b['B'],axis,id_=b['d'],center=off(L/2-4-b['B']/2)),'steel',mass=b['m'],group='bearing')
    add(f'{name} AksIM-2 encoder ring',seg,cyl(min(mod,god)-6,3,axis,id_=min(mod,god)*0.5,center=off(-(L/2-4-mL-3))),'steel',mass=0.016,group='sensor')
    nb,mb=(8,6) if god>=85 else ((8,4) if god>=60 else (6,3))
    add(f'{name} output bolts {nb}×M{mb} 12.9',seg,bolt_circle(nb,mb,(b['d']+b['D'])/2*0.0+b['d']-mb-2,axis,off(L/2+2),12),'steel',group='fastener')
    return OD,L
def linear_actuator(name,seg_body,p0,p1,motor,lead,rod_seg,top='trunnion',fins=False):
    """Planetary roller screw actuator from trunnion p0 (on seg_body) to rod-end p1 (on rod_seg). Body = motor + nut housing; rod Ø12/Ø10 steel."""
    p0=seg_xf_point(seg_body,p0);p1=seg_xf_point(rod_seg,p1)
    def add_(n,sg,so,mat='7075-T6',mass=None,group='structure'): add(n,sg,so,mat,mass,group,posed=True)
    mod,mL=menv(motor);v=[b-a for a,b in zip(p0,p1)];Ltot=math.sqrt(sum(c*c for c in v))
    body_L=mL+36+60; od=max(mod,26)+2*P['wall']+2   # motor + Rollvis RV12 nut (D1 26, L1 36) + bearings/thrust
    def along(s,L,od_,id_=0):
        c=cyl(od_,L,'z',id_=id_).translate((0,0,L/2))   # from z=0 to L
        u=[c_/Ltot for c_ in v]; ang=math.degrees(math.acos(max(-1,min(1,u[2])))); ax=(-u[1],u[0],0) if abs(u[2])<0.9999 else (1,0,0)
        if ang>1e-6: c=c.rotate((0,0,0),ax,ang)
        return c.translate(tuple(p+uu*s for p,uu in zip(p0,u)))
    add_(f'{name} body (motor {motor} + Rollvis RV12 roller-screw nut, lead {lead} mm)',seg_body,along(0,body_L,od).cut(along(4,body_L-8,od-2*P['wall'])),'7075-T6',group='actuator')
    add_(f'{name} motor ({motor})',seg_body,along(6,mL,mod-2,mod*0.35),'steel',mass=PT.MOT[motor]['mass'],group='actuator')
    if fins:
        for k in range(4): add_(f'{name} cooling fin {k+1}',seg_body,along(10+k*9,3,od+16,od-1),'7075-T6',group='thermal')
    rod_L=Ltot-body_L-14
    add_(f'{name} screw rod',rod_seg,along(body_L+2,rod_L,12),'steel',group='actuator')
    sph=cq.Workplane('XY').sphere(11).translate(p1)
    add_(f'{name} rod-end bearing',rod_seg,sph,'steel',group='actuator')
    # trunnion: two stub pins on the body sides (axis y), outside the motor envelope
    dpin=16
    if top=='sphere':   # FIX: adjacent ankle actuators' trunnion stubs collided -> spherical top bearing (also needed for 2-DoF ankle)
        add_(f'{name} top spherical bearing',seg_body,cq.Workplane('XY').sphere(12).translate(p0),'steel',group='actuator');return Ltot
    tr=cyl(dpin,12,'y',center=(p0[0],p0[1]+od/2+6,p0[2])).union(cyl(dpin,12,'y',center=(p0[0],p0[1]-od/2-6,p0[2])))
    add_(f'{name} trunnion stub pins',seg_body,tr,'steel',group='actuator')
    return Ltot
def build_leg(s):
    y=P['hip_y']*s; hz=P['hip_z']; kz=P['knee_z']; az=P['ankle_z']; S=lambda n:f'{"L" if s>0 else "R"}_{n}'
    yz0=hz+P['yaw_z_off']; rz0=hz+P['roll_z_off']
    jy=(S('hip_yaw'),(0,y,yz0),(0,0,1)); jr=(S('hip_roll'),(0,y,rz0),(1,0,0)); jp=(S('hip_pitch'),(0,y,hz),(0,1,0))
    jk=(S('knee'),(0,y,kz),(0,1,0)); jap=(S('ankle_pitch'),(0,y,az),(0,1,0)); jar=(S('ankle_roll'),(0,y,az),(1,0,0))
    CHAINS.update({S('hipY'):[jy],S('hipR'):[jy,jr],S('thigh'):[jy,jr,jp],S('shank'):[jy,jr,jp,jk],S('foot'):[jy,jr,jp,jk,jap,jar]})
    # --- hip yaw (axis z), housing on pelvis
    yz=hz+P['yaw_z_off']; rotary_actuator(S('hip yaw'),S('pelvis'),'hip_yaw','z',(0,y,yz),-1)
    add(S('hip bracket (yaw mount)'),S('pelvis'),hip_bracket().translate((0,y,0)),'7075-T6')
    add(S('hip bracket bolts 8×M8 12.9'),S('pelvis'),bolt_circle(8,8,100,'z',(0,y,P['pelvis_top']-9),26),'steel',group='fastener')
    # --- hip roll (axis x) on yaw output
    rz=hz+P['roll_z_off']; ODr,Lr=rotary_actuator(S('hip roll'),S('hipY'),'hip_roll','x',(0,y,rz))
    yb=yz-ACT_DIM[S('hip yaw')][1]/2   # yaw housing bottom = yaw output flange
    yoke=box(Lr+26,60,8,(0,y,yb-4))
    for sx in (-1,1): yoke=yoke.union(box(8,60,yb-8-rz+20,(sx*(Lr/2+9),y,(yb-8+rz-20)/2)))
    add(S('yaw-roll yoke (output flange + 2 cheeks)'),S('hipY'),yoke,'7075-T6')
    # --- hip pitch (axis y) on roll output, + crossed-roller support bearing (outboard)
    ODp,Lp=rotary_actuator(S('hip pitch'),S('hipR'),'hip_pitch','y',(0,y,hz))
    add(S('roll-pitch yoke'),S('hipR'),box(60,40,rz-hz-ODp/2-ODr/2+70,(0,y-s*(Lp/2-20),(hz+rz)/2)).cut(cyl(ODp+1,300,'y',center=(0,y,hz))).cut(cyl(ODr+1,300,'x',center=(0,y,rz))),'7075-T6')
    # v3: separate Ø140 support bearing removed - the hip-pitch CRBH output bearing carries the moment (bearing check in v3/analysis)
    # --- thigh: femur tube + lugs + knee clevis
    fl_top=hz-ODp/2-2; fl_bot=kz+40
    add(S('femur upper lug'),S('thigh'),box(80,60,30,(8,y,fl_top-15)).cut(cyl(P['femur_od']-2*P['femur_t'],32,'z',center=(P['femur_x'],y,fl_top-15))) ,'7075-T6')
    add(S('femur tube 7075 Ø%dx%.1f'%(P['femur_od'],P['femur_t'])),S('thigh'),cyl(P['femur_od'],fl_top-30-fl_bot,'z',id_=P['femur_od']-2*P['femur_t'],center=(P['femur_x'],y,(fl_top-30+fl_bot)/2)),'7075-T6')
    add(S('femur root fillet collar'),S('thigh'),fcollar(P['femur_od'],P['femur_t'],(P['femur_x'],y,fl_top-30),-1),'7075-T6')
    add(S('femur knee fillet collar'),S('thigh'),fcollar(P['femur_od'],P['femur_t'],(P['femur_x'],y,fl_bot),1),'7075-T6')
    # FIX: clevis bridge moved forward of the pin (x>=0) so the rear stays open for the lever, rod end and screw rod at deep flexion
    cl=box(46,14,62,(0,y+28,kz+10)).union(box(46,14,62,(0,y-28,kz+10))).union(box(40,70,22,(P['femur_x']+5,y,kz+40+11)))
    add(S('knee clevis (thigh)'),S('thigh'),cl.cut(cyl(16,90,'y',center=(0,y,kz))).cut(cyl(P['femur_od'],40,'z',center=(P['femur_x'],y,kz+60))),'7075-T6')
    # knee linear actuator: thigh trunnion -> shank lever behind knee
    # FIX: lever re-clocked to 30° behind straight-down (r=52 mm) so over 0..135° it sweeps behind the femur instead of into it.
    # effective arm = 52*sin(30+θ) [EST]: 26 mm at full extension, ≥45 mm for 30–120° (where squat torque is needed)
    linear_actuator(S('knee actuator'),S('thigh'),(P['knee_act_x'],y,fl_top-60),(-26,y,kz-45),ST['J']['knee']['motor'],PT.RV[ST['J']['knee']['screw']]['lead'],S('shank'),fins=ST['cooling']['knee']=='air_fins')
    # --- shank
    # FIX: solid tongue blocked the screw rod -> tongue + open lever clevis (two cheeks, 26 mm slot for the rod end), one machined part
    add(S('knee tongue + lever clevis (shank)'),S('shank'),box(50,40,60,(5,y,kz-20)).union(box(24,6,70,(0,y+16,-30)).rotate((0,0,0),(0,1,0),-30).translate((0,0,kz))).union(box(24,6,70,(0,y-16,-30)).rotate((0,0,0),(0,1,0),-30).translate((0,0,kz))).cut(cyl(16,60,'y',center=(0,y,kz))),'7075-T6')
    # v3: cable drums (bend radius ≥ 10×d for moving cables) — knee Ø90 outboard of the clevis, ankle Ø70
    add(S('knee cable drum Ø90 (PA12)'),S('shank'),cyl(90,8,'y',id_=20,center=(0,y+s*44,kz)),'PA12',group='harness')
    tb_top=kz-50; tb_bot=az+50   # FIX (FEA): was +52 -> 2 mm gap, tibia tube was not attached to the ankle fork   # FIX: was +45 -> tibia ran into ankle fork
    add(S('tibia tube 7075 Ø%dx%.1f'%(P['tibia_od'],P['tibia_t'])),S('shank'),cyl(P['tibia_od'],tb_top-tb_bot,'z',id_=P['tibia_od']-2*P['tibia_t'],center=(14,y,(tb_top+tb_bot)/2)),'7075-T6')  # FIX: tibia axis 14 mm forward to clear the re-clocked knee lever/rod end
    add(S('tibia ankle fillet collar'),S('shank'),fcollar(P['tibia_od'],P['tibia_t'],(14,y,tb_bot),1),'7075-T6')
    add(S('ankle fork (shank)'),S('shank'),box(62,44,40,(6,y,az+30)).cut(box(64,36,30,(6,y,az+15))),'7075-T6')   # FIX: was 60 wide -> rod ends hit it at ankle +40°
    for dy in (-1,1):
        linear_actuator(S(f'ankle actuator {"in" if dy*s<0 else "out"}'),S('shank'),(P['ankle_act_x'],y+dy*P['ankle_act_dy'],tb_top-40),(-P['ankle_lever'],y+dy*P['ankle_act_dy'],az+20),ST['J']['ankle_pitch']['motor'],PT.RV[ST['J']['ankle_pitch']['screw']]['lead'],S('foot'),top='sphere',fins=ST['cooling']['ankle_pitch']=='air_fins')
    # --- foot
    add(S('ankle cross (universal)'),S('foot'),box(30,30,30,(0,y,az)),'Ti-6Al-4V')
    add(S('ankle cable drum Ø70 (PA12)'),S('foot'),cyl(70,6,'y',id_=20,center=(0,y+s*(P['ankle_act_dy']+26),az)),'PA12',group='harness')
    add(S('ankle 6-axis F/T sensor'),S('foot'),cyl(60,20,'z',center=(0,y,az-35)),'steel',mass=0.25,group='sensor')
    add(S('foot plate + heel lever'),S('foot'),box(P['foot_len'],100,18,(P['foot_len']/2-P['heel'],y,9)).union(box(30,90,40,(-P['ankle_lever'],y,30))),'7075-T6')
def fcollar(od,t,c,up):
    """v3: tapered weld-free collar (OD+16 -> OD over 14 mm) bonded/shrunk over the tube end = fillet-equivalent transition (r≈8) into the lug."""
    sol=cq.Solid.makeCone((od+16)/2,od/2,14,cq.Vector(c[0],c[1],c[2]),cq.Vector(0,0,up))
    return cq.Workplane('XY').add(sol).cut(cyl(od-2*t,40,'z',center=(c[0],c[1],c[2]+up*7)))
def hip_bracket():
    """Bolted to pelvis underside; ring flange carries the hip-yaw housing. Plate 8 mm + two gussets. Local coords (y added later)."""
    yz=P['hip_z']+P['yaw_z_off']; top=P['pelvis_top']-4; ring_z=yz+act_dim('hip_yaw')[1]/2+1  # sits on the yaw housing top
    flange=box(120,90,8,(0,0,top-4))
    ring=cyl(90,8,'z',id_=50,center=(0,0,ring_z+4))
    web=box(8,90,top-8-(ring_z+8),(30,0,(top-8+ring_z+8)/2)).union(box(8,90,top-8-(ring_z+8),(-30,0,(top-8+ring_z+8)/2)))
    return flange.union(ring).union(web)
def build_upper():
    pb,pt=P['pelvis_bot'],P['pelvis_top']
    pel=shell_box(170,2*(P['hip_y']+55),pt-pb,4,(0,0,(pb+pt)/2))   # v3 FIX: width follows hip_y (was 300) -> hip bracket webs/CRBH 6013 hit the side walls
    for yy in (P['hip_y'],-P['hip_y']): pel=pel.cut(cyl(act_dim('hip_yaw')[0]+4,20,'z',center=(0,yy,pb+2)))   # v3 FIX: hole follows catalog housing OD (was 86)
    pel=pel.cut(cyl(100,20,'z',center=(0,0,pt-2)))   # v3 FIX: was 86
    add('pelvis shell (7075, 4 mm; encloses hip-yaw + waist-yaw actuators)','pelvis',pel,'7075-T6')
    rotary_actuator('waist yaw','pelvis','waist_yaw','z',(0,0,pt-42))
    rotary_actuator('waist pitch','waistY','waist_pitch','y',(0,0,pt+50))
    tb=pt+100;tt=P['torso_top']
    ts=shell_box(220,340,tt-tb,3,(0,0,(tb+tt)/2))
    for sy in (1,-1): ts=ts.cut(cyl(100,40,'y',center=(0,sy*170,P['shoulder_z'])))   # FIX: shoulder-pitch pass-throughs
    ts=ts.cut(cyl(64,20,'z',center=(0,0,tt)))                                           # FIX: neck pass-through
    add('torso shell (CFRP sandwich 3 mm)','torso',ts,'CFRP')
    add('torso spine frame (7075)','torso',box(20,300,tt-tb-10,(-95,0,(tb+tt)/2)).cut(box(22,260,tt-tb-60,(-95,0,(tb+tt)/2))),'7075-T6')
    add(f"battery pack 13S{ST['battery']['P']}P Molicel P45B ({V3['mass']['battery_Wh']:.0f} Wh, 5.9 L)",'torso',box(185,220,144,(12,0,tb+75)),'steel',mass=V3['mass']['battery'],group='power')
    add('compute bay: Jetson AGX Thor + cold plate','torso',box(130,200,40,(8,0,tb+175)),'7075-T6',mass=DES['MASS_ITEMS']['compute (Jetson Thor + RT ctrl + cooling)'],group='electronics')
    for s in (1,-1):
        S=lambda n:f'{"L" if s>0 else "R"}_{n}';y=P['shoulder_y']*s;z=P['shoulder_z']
        ODs,Ls=rotary_actuator(S('shoulder pitch'),'torso','shoulder_pitch','y',(0,y-s*20,z),s)
        add(S('shoulder mount bolts 6×M8 12.9'),'torso',bolt_circle(6,8,ODs+14,'y',(0,y-s*(20+Ls/2-6),z),14),'steel',group='fastener')
        y=y+s*(P['sh_roll_dy']-45)   # arm line shifted outboard
        rotary_actuator(S('shoulder roll'),S('shoulderP'),'shoulder_roll','x',(0,y+s*45,z-40))
        rotary_actuator(S('shoulder yaw'),S('upper_arm'),'shoulder_yaw','z',(0,y+s*45,z-140))   # FIX: was z-110
        ua=GEO['upper_arm']*1000; ez=z-ua
        add(S('upper arm tube 7075 Ø40x2'),S('upper_arm'),cyl(40,(z-140-ACT_DIM[S('shoulder yaw')][1]/2-2)-(ez+42),'z',id_=36,center=(0,y+s*45,(z-140-ACT_DIM[S('shoulder yaw')][1]/2-2+ez+42)/2)),'7075-T6')
        # FIX: linear elbow actuator had only ~128 mm pivot-to-pivot (body alone is 115 mm) -> no stroke. Elbow is now rotary M60 + CSG-20-100.
        rotary_actuator(S('elbow'),S('upper_arm'),'elbow','y',(0,y+s*45,ez),s)
        fa=GEO['forearm']*1000; wz=ez-fa
        add(S('forearm shell 7075 (houses 11 hand drives)'),S('forearm'),cyl(76,(ez-42)-(wz+35),'z',id_=72,center=(0,y+s*45,(ez-42+wz+35)/2)),'7075-T6')
        hz_=(ez+wz)/2
        for k in range(6):   # 6 flexor drives: maxon DCX22S + GPX22HP 111:1 (Ø22, ~108 mm) in one ring r=23 inside the Ø72 bore
            a=2*math.pi*k/6; add(S(f'flexor drive {k+1} (maxon DCX22S+GPX22HP 111:1)'),S('forearm'),cyl(22,108,'z',center=(23*math.cos(a),y+s*45+23*math.sin(a),hz_+10)),'steel',mass=0.066+0.107,group='actuator')
        rotary_actuator(S('wrist roll'),S('forearm'),'wrist_roll','z',(0,y+s*45,wz+20))
        build_hand(S,(0,y+s*45,wz-10),s)
    # neck + head
    rotary_actuator('neck yaw','torso','neck_yaw','z',(0,0,tt-15))
    rotary_actuator('neck pitch','neckY','neck_pitch','y',(0,0,tt+60))   # v3: was tt+48 (catalog neck-yaw housing taller)   # FIX: was tt+30 (hit neck yaw)
    hc=(10,0,tt+140)
    hs=cq.Workplane('XY').sphere(100).translate(hc).cut(cq.Workplane('XY').sphere(97.5).translate(hc))
    hs=hs.cut(cyl(118,90,'z',center=(10,0,tt+35))).cut(box(40,126,36,(85,0,tt+140)))   # FIX: neck opening + camera window
    add('head shell (PA12/CF 2.5 mm)','head',hs,'PA12')
    add('stereo camera module','head',box(28,120,30,(80,0,tt+140)),'7075-T6',mass=0.3,group='sensor')
def build_hand(S,top,s):
    x0,y0,z0=top
    add(S('palm (7075 skeleton + PA12)'),S('hand'),box(30,85,90,(x0,y0,z0-57)),'PA12')
    fy=[-30,-10,10,30];L=[[45,26,20],[48,28,21],[45,26,20],[38,22,18]]
    for i,(dy,ls) in enumerate(zip(fy,L)):
        z=z0-104
        for j,l in enumerate(ls):
            add(S(f'finger{i+1} phalanx{j+1}'),S('hand'),cyl(16-2*j,l-2,'z',center=(x0,y0+dy*s,z-l/2)),'PA12');z-=l
    # Dyneema SK78 Ø1 mm flexor tendons (6, PTFE-lined sheaths) pass as one Ø6 bundle through the hollow wrist-roll bore, fan out over Ø8 idlers (D/d 8) in the palm
    add(S('flexor tendon bundle (6× Ø1 Dyneema in sheaths, through wrist bore)'),S('hand'),cyl(6,110,'z',center=(x0,y0,z0+40)),'PA12',mass=0.01,group='tendon')
    add(S('palm tendon idler shaft (6 pulleys Ø8)'),S('hand'),cyl(8,70,'y',center=(x0+4,y0,z0-22)),'steel',group='tendon')
    for k in range(5):   # abduction / thumb drives: maxon DCX16S + GPX16 103:1 in the palm
        add(S(f'small drive {k+1} (maxon DCX16S+GPX16 103:1)'),S('hand'),cyl(16,56,'z',center=(x0+2,y0+(k-2)*16.5,z0-66)),'steel',mass=0.075,group='actuator')
    z=z0-60
    for j,l in enumerate([40,32,26]):
        add(S(f'thumb phalanx{j+1}'),S('hand'),cyl(18-2*j,l-2,'x',center=(x0+20+sum([40,32,26][:j])+l/2,y0-s*35,z)),'PA12')
