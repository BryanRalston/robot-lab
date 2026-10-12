"""Robot Lab v2 parametric CAD (CadQuery). Units: mm, kg. Frame: x forward, y left, z up. Standing pose = all joints 0.
Dimensions come from v2/analysis (design.py, checks). Envelopes of bought parts are APPROXIMATE (verify vs. vendor drawings):
CSG component sets and frameless motors are modeled as solid envelopes with an effective density that matches the budget mass."""
import cadquery as cq, math, sys, copy
sys.path.insert(0,'../analysis'); import design as D
DES=D.final(); GEO=DES['GEO']; J=DES['JOINTS']; MOT=DES['MOTORS']; GR=DES['GEARS']
P=dict(  # ---- layout parameters (mm). FIX log in README tracks changes made after clash checks.
 hip_y=100, hip_z=920, knee_z=500, ankle_z=80, foot_len=240, heel=60,
 knee_act_x=-95,   # FIX: was -80 -> knee actuator body hit femur tube           # knee linear actuator offset behind femur axis
 ankle_act_x=-62, ankle_act_dy=37, ankle_lever=50,   # FIX: dy was 30 -> in/out ankle actuator bodies overlapped
 roll_z_off=125,           # hip roll axis height above hip pitch axis
 yaw_z_off=240,          # FIX: was 210/230 -> yoke top plate needs room between roll housing and yaw output            # hip yaw actuator center above hip pitch axis
 pelvis_bot=1126, pelvis_top=1230, torso_top=1556,   # FIX: torso_top was 1540 -> shoulder-pitch housing hit torso top wall
 shoulder_z=1500, shoulder_y=190, sh_roll_dy=92,   # FIX: shoulder roll moved outboard (was +45) to clear pitch housing
 femur_x=18,   # FIX: femur axis moved 18 mm forward so the knee lever/rod can swing behind it (knee was clash-free only to 40°)
 wall=3.0, femur_od=50, femur_t=2.0, tibia_od=45, tibia_t=2.0,
)
MAT={'7075-T6':2.81e-6,'CFRP':1.55e-6,'steel':7.85e-6,'Ti-6Al-4V':4.43e-6,'PA12':1.01e-6}  # kg/mm^3
# approximate envelopes (OD, axial length) mm, ESTIMATES
MOTOR_ENV={'M115':(115,35),'M85':(85,30),'M60':(60,25),'M38':(38,20)}
GEAR_ENV={'CSG-20-100':(70,28),'CSG-25-100':(85,32),'CSG-32-100':(110,40),'SW-14-100':(50,22),'SW-11-100':(40,18)}
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
def rotary_actuator(name,seg,joint,axis,center,side=1):
    """Housing (7075 shell, wall P['wall']) + motor stack + strain-wave set, coaxial. Returns housing OD, length."""
    g,k,mo,ge,_,_,_=J[joint];mod,mL=MOTOR_ENV[mo];god,gL=GEAR_ENV[ge]
    OD=max(mod,god)+2*P['wall']+4;L=mL+gL+24
    h=cyl(OD,L,axis,center=center).cut(cyl(OD-2*P['wall'],L-8,axis,center=center))
    add(f'{name} housing',seg,h,'7075-T6',group='actuator')
    off=lambda d: tuple(c+(d*side if a==axis else 0) for c,a in zip(center,'xyz'))
    add(f'{name} motor ({mo}, frameless PMSM)',seg,cyl(mod-2,mL,axis,id_=mod*0.35,center=off(-(L/2-4-mL/2))),'steel',mass=MOT[mo]['mass'],group='actuator')
    add(f'{name} {ge} strain-wave set',seg,cyl(god-2,gL,axis,id_=god*0.3,center=off(L/2-4-gL/2)),'steel',mass=GR[ge]['mass'],group='actuator')
    return OD,L
def linear_actuator(name,seg_body,p0,p1,motor,lead,rod_seg,top='trunnion'):
    """Planetary roller screw actuator from trunnion p0 (on seg_body) to rod-end p1 (on rod_seg). Body = motor + nut housing; rod Ø12/Ø10 steel."""
    p0=seg_xf_point(seg_body,p0);p1=seg_xf_point(rod_seg,p1)
    def add_(n,sg,so,mat='7075-T6',mass=None,group='structure'): add(n,sg,so,mat,mass,group,posed=True)
    mod,mL=MOTOR_ENV[motor];v=[b-a for a,b in zip(p0,p1)];Ltot=math.sqrt(sum(c*c for c in v))
    body_L=mL+90; od=mod+2*P['wall']+2
    def along(s,L,od_,id_=0):
        c=cyl(od_,L,'z',id_=id_).translate((0,0,L/2))   # from z=0 to L
        u=[c_/Ltot for c_ in v]; ang=math.degrees(math.acos(max(-1,min(1,u[2])))); ax=(-u[1],u[0],0) if abs(u[2])<0.9999 else (1,0,0)
        if ang>1e-6: c=c.rotate((0,0,0),ax,ang)
        return c.translate(tuple(p+uu*s for p,uu in zip(p0,u)))
    add_(f'{name} body (motor {motor} + roller-screw nut, lead {lead} mm)',seg_body,along(0,body_L,od).cut(along(4,body_L-8,od-2*P['wall'])),'7075-T6',group='actuator')
    add_(f'{name} motor ({motor})',seg_body,along(6,mL,mod-2,mod*0.35),'steel',mass=MOT[motor]['mass'],group='actuator')
    rod_L=Ltot-body_L-14
    add_(f'{name} screw rod',rod_seg,along(body_L+2,rod_L,14 if motor!='M38' else 8),'steel',group='actuator')
    sph=cq.Workplane('XY').sphere(11 if motor!='M38' else 6).translate(p1)
    add_(f'{name} rod-end bearing',rod_seg,sph,'steel',group='actuator')
    # trunnion: two stub pins on the body sides (axis y), outside the motor envelope
    dpin=16 if motor!='M38' else 8
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
    # --- hip roll (axis x) on yaw output
    rz=hz+P['roll_z_off']; ODr,Lr=rotary_actuator(S('hip roll'),S('hipY'),'hip_roll','x',(0,y,rz))
    yb=yz-77/2   # yaw housing bottom = yaw output flange
    yoke=box(Lr+26,60,8,(0,y,yb-4))
    for sx in (-1,1): yoke=yoke.union(box(8,60,yb-8-rz+20,(sx*(Lr/2+9),y,(yb-8+rz-20)/2)))
    add(S('yaw-roll yoke (output flange + 2 cheeks)'),S('hipY'),yoke,'7075-T6')
    # --- hip pitch (axis y) on roll output, + crossed-roller support bearing (outboard)
    ODp,Lp=rotary_actuator(S('hip pitch'),S('hipR'),'hip_pitch','y',(0,y,hz))
    add(S('roll-pitch yoke'),S('hipR'),box(60,40,rz-hz-ODp/2-ODr/2+70,(0,y-s*(Lp/2-20),(hz+rz)/2)).cut(cyl(ODp+1,300,'y',center=(0,y,hz))).cut(cyl(ODr+1,300,'x',center=(0,y,rz))),'7075-T6')
    add(S('hip crossed-roller support bearing (≥600 N·m, ~Ø140)'),S('hipR'),cyl(140,16,'y',id_=104,center=(0,y+s*(Lp/2+10),hz)),'steel',group='bearing')
    # --- thigh: femur tube + lugs + knee clevis
    fl_top=hz-ODp/2-2; fl_bot=kz+40
    add(S('femur upper lug'),S('thigh'),box(80,60,30,(8,y,fl_top-15)).cut(cyl(P['femur_od']-2*P['femur_t'],32,'z',center=(P['femur_x'],y,fl_top-15))) ,'7075-T6')
    add(S('femur tube 7075 Ø%dx%.1f'%(P['femur_od'],P['femur_t'])),S('thigh'),cyl(P['femur_od'],fl_top-30-fl_bot,'z',id_=P['femur_od']-2*P['femur_t'],center=(P['femur_x'],y,(fl_top-30+fl_bot)/2)),'7075-T6')
    # FIX: clevis bridge moved forward of the pin (x>=0) so the rear stays open for the lever, rod end and screw rod at deep flexion
    cl=box(46,14,62,(0,y+28,kz+10)).union(box(46,14,62,(0,y-28,kz+10))).union(box(40,70,22,(P['femur_x']+5,y,kz+40+11)))
    add(S('knee clevis (thigh)'),S('thigh'),cl.cut(cyl(16,90,'y',center=(0,y,kz))).cut(cyl(P['femur_od'],40,'z',center=(P['femur_x'],y,kz+60))),'7075-T6')
    # knee linear actuator: thigh trunnion -> shank lever behind knee
    # FIX: lever re-clocked to 30° behind straight-down (r=52 mm) so over 0..135° it sweeps behind the femur instead of into it.
    # effective arm = 52*sin(30+θ) [EST]: 26 mm at full extension, ≥45 mm for 30–120° (where squat torque is needed)
    linear_actuator(S('knee actuator'),S('thigh'),(P['knee_act_x'],y,fl_top-60),(-26,y,kz-45),'M85',5.0,S('shank'))
    # --- shank
    # FIX: solid tongue blocked the screw rod -> tongue + open lever clevis (two cheeks, 26 mm slot for the rod end), one machined part
    add(S('knee tongue + lever clevis (shank)'),S('shank'),box(50,40,60,(5,y,kz-20)).union(box(24,6,70,(0,y+16,-30)).rotate((0,0,0),(0,1,0),-30).translate((0,0,kz))).union(box(24,6,70,(0,y-16,-30)).rotate((0,0,0),(0,1,0),-30).translate((0,0,kz))).cut(cyl(16,60,'y',center=(0,y,kz))),'7075-T6')
    tb_top=kz-50; tb_bot=az+50   # FIX (FEA): was +52 -> 2 mm gap, tibia tube was not attached to the ankle fork   # FIX: was +45 -> tibia ran into ankle fork
    add(S('tibia tube 7075 Ø%dx%.1f'%(P['tibia_od'],P['tibia_t'])),S('shank'),cyl(P['tibia_od'],tb_top-tb_bot,'z',id_=P['tibia_od']-2*P['tibia_t'],center=(14,y,(tb_top+tb_bot)/2)),'7075-T6')  # FIX: tibia axis 14 mm forward to clear the re-clocked knee lever/rod end
    add(S('ankle fork (shank)'),S('shank'),box(62,44,40,(6,y,az+30)).cut(box(64,36,30,(6,y,az+15))),'7075-T6')   # FIX: was 60 wide -> rod ends hit it at ankle +40°
    for dy in (-1,1):
        linear_actuator(S(f'ankle actuator {"in" if dy*s<0 else "out"}'),S('shank'),(P['ankle_act_x'],y+dy*P['ankle_act_dy'],tb_top-40),(-P['ankle_lever'],y+dy*P['ankle_act_dy'],az+20),'M60',4.0,S('foot'),top='sphere')
    # --- foot
    add(S('ankle cross (universal)'),S('foot'),box(30,30,30,(0,y,az)),'Ti-6Al-4V')
    add(S('ankle 6-axis F/T sensor'),S('foot'),cyl(60,20,'z',center=(0,y,az-35)),'steel',mass=0.25,group='sensor')
    add(S('foot plate + heel lever'),S('foot'),box(P['foot_len'],100,18,(P['foot_len']/2-P['heel'],y,9)).union(box(30,90,40,(-P['ankle_lever'],y,30))),'7075-T6')
def hip_bracket():
    """Bolted to pelvis underside; ring flange carries the hip-yaw housing. Plate 8 mm + two gussets. Local coords (y added later)."""
    yz=P['hip_z']+P['yaw_z_off']; top=P['pelvis_top']-5; ring_z=yz+77/2+1  # yaw housing (M60+CSG-20) length 77
    flange=box(120,90,8,(0,0,top-4))
    ring=cyl(90,8,'z',id_=50,center=(0,0,ring_z+4))
    web=box(8,90,top-8-(ring_z+8),(30,0,(top-8+ring_z+8)/2)).union(box(8,90,top-8-(ring_z+8),(-30,0,(top-8+ring_z+8)/2)))
    return flange.union(ring).union(web)
def build_upper():
    pb,pt=P['pelvis_bot'],P['pelvis_top']
    pel=shell_box(170,300,pt-pb,4,(0,0,(pb+pt)/2))
    for yy in (P['hip_y'],-P['hip_y']): pel=pel.cut(cyl(86,20,'z',center=(0,yy,pb+2)))
    pel=pel.cut(cyl(86,20,'z',center=(0,0,pt-2)))
    add('pelvis shell (7075, 4 mm; encloses hip-yaw + waist-yaw actuators)','pelvis',pel,'7075-T6')
    rotary_actuator('waist yaw','pelvis','waist_yaw','z',(0,0,pt-42))
    rotary_actuator('waist pitch','waistY','waist_pitch','y',(0,0,pt+50))
    tb=pt+100;tt=P['torso_top']
    ts=shell_box(220,340,tt-tb,3,(0,0,(tb+tt)/2))
    for sy in (1,-1): ts=ts.cut(cyl(100,40,'y',center=(0,sy*170,P['shoulder_z'])))   # FIX: shoulder-pitch pass-throughs
    ts=ts.cut(cyl(64,20,'z',center=(0,0,tt)))                                           # FIX: neck pass-through
    add('torso shell (CFRP sandwich 3 mm)','torso',ts,'CFRP')
    add('torso spine frame (7075)','torso',box(20,300,tt-tb-10,(-95,0,(tb+tt)/2)).cut(box(22,260,tt-tb-60,(-95,0,(tb+tt)/2))),'7075-T6')
    add('battery pack 2.3 kWh 52 V (14S NMC, 5.0 L)','torso',box(170,280,105,(8,0,tb+58)),'steel',mass=DES['MASS_ITEMS']['battery pack'],group='power')
    add('compute bay: Jetson AGX Thor + cold plate','torso',box(130,200,40,(8,0,tb+140)),'7075-T6',mass=DES['MASS_ITEMS']['compute (Jetson Thor + RT ctrl + cooling)'],group='electronics')
    for s in (1,-1):
        S=lambda n:f'{"L" if s>0 else "R"}_{n}';y=P['shoulder_y']*s;z=P['shoulder_z']
        ODs,Ls=rotary_actuator(S('shoulder pitch'),'torso','shoulder_pitch','y',(0,y-s*20,z),s)
        y=y+s*(P['sh_roll_dy']-45)   # arm line shifted outboard
        rotary_actuator(S('shoulder roll'),S('shoulderP'),'shoulder_roll','x',(0,y+s*45,z-40))
        rotary_actuator(S('shoulder yaw'),S('upper_arm'),'shoulder_yaw','z',(0,y+s*45,z-140))   # FIX: was z-110
        ua=GEO['upper_arm']*1000; ez=z-ua
        add(S('upper arm tube 7075 Ø40x2'),S('upper_arm'),cyl(40,(z-180)-(ez+42),'z',id_=36,center=(0,y+s*45,(z-180+ez+42)/2)),'7075-T6')
        # FIX: linear elbow actuator had only ~128 mm pivot-to-pivot (body alone is 115 mm) -> no stroke. Elbow is now rotary M60 + CSG-20-100.
        rotary_actuator(S('elbow'),S('upper_arm'),'elbow','y',(0,y+s*45,ez),s)
        fa=GEO['forearm']*1000; wz=ez-fa
        add(S('forearm shell 7075 (houses 17 hand motors)'),S('forearm'),cyl(70,(ez-42)-(wz+35),'z',id_=64,center=(0,y+s*45,(ez-42+wz+35)/2)),'7075-T6')
        add(S('hand motor pack (17× Ø16 BLDC + ball screws)'),S('forearm'),box(40,40,150,(0,y+s*45,(ez+wz)/2)),'steel',mass=0.5,group='actuator')
        rotary_actuator(S('wrist roll'),S('forearm'),'wrist_roll','z',(0,y+s*45,wz+20))
        build_hand(S,(0,y+s*45,wz-10),s)
    # neck + head
    rotary_actuator('neck yaw','torso','neck_yaw','z',(0,0,tt-15))
    rotary_actuator('neck pitch','neckY','neck_pitch','y',(0,0,tt+48))   # FIX: was tt+30 (hit neck yaw)
    hc=(10,0,tt+125)
    hs=cq.Workplane('XY').sphere(100).translate(hc).cut(cq.Workplane('XY').sphere(97.5).translate(hc))
    hs=hs.cut(cyl(96,60,'z',center=(10,0,tt+25))).cut(box(40,126,36,(85,0,tt+125)))   # FIX: neck opening + camera window
    add('head shell (PA12/CF 2.5 mm)','head',hs,'PA12')
    add('stereo camera module','head',box(28,120,30,(80,0,tt+125)),'7075-T6',mass=0.3,group='sensor')
def build_hand(S,top,s):
    x0,y0,z0=top
    add(S('palm (7075 skeleton + PA12)'),S('hand'),box(30,85,90,(x0,y0,z0-57)),'PA12')
    fy=[-30,-10,10,30];L=[[45,26,20],[48,28,21],[45,26,20],[38,22,18]]
    for i,(dy,ls) in enumerate(zip(fy,L)):
        z=z0-104
        for j,l in enumerate(ls):
            add(S(f'finger{i+1} phalanx{j+1}'),S('hand'),cyl(16-2*j,l-2,'z',center=(x0,y0+dy*s,z-l/2)),'PA12');z-=l
    z=z0-60
    for j,l in enumerate([40,32,26]):
        add(S(f'thumb phalanx{j+1}'),S('hand'),cyl(18-2*j,l-2,'x',center=(x0+20+sum([40,32,26][:j])+l/2,y0-s*35,z)),'PA12')
