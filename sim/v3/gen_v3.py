"""MJCF for Robot Lab v3, generated from the v3 CAD (v3/cad/model.py joint locations, out/mass.json per-segment mass/COM/inertia)
and v3/analysis (catalog actuator peak torque -> ctrlrange, rotor inertia x N^2 -> armature). Body names = CAD segment names so the
site can attach the CAD GLB parts to the simulated bodies."""
import json,sys,math
sys.path.insert(0,'../../v3/cad'); import os; os.chdir('../../v3/cad'); import model; os.chdir('../../sim/v3')
V3=model.V3; ST=V3['state']; P=model.P; GEO=model.GEO; PT=model.PT
MS=json.load(open('../../v3/cad/out/mass.json'))['segments']
scale=V3['m']/sum(s['mass'] for s in MS.values())   # harness/covers/compute detail in the rollup but not modelled in CAD -> spread pro rata
rows={r['joint']:r for r in V3['rows']}
mm=lambda v: v/1000.0
hz,kz,az=P['hip_z'],P['knee_z'],P['ankle_z']; yz=hz+P['yaw_z_off']; rz=hz+P['roll_z_off']; pt=P['pelvis_top']; tt=P['torso_top']
sz=P['shoulder_z']; ua=GEO['upper_arm']*1000; ez=sz-ua; wz=ez-GEO['forearm']*1000
LIM={'hip_yaw':(-35,45),'hip_roll':(-12,15),'hip_pitch':(-105,40),'knee':(0,120),'ankle_pitch':(-45,40),'ankle_roll':(-25,25),
     'waist_yaw':(-90,90),'waist_pitch':(-30,60),'shoulder_pitch':(-180,60),'shoulder_roll':(-15,180),'shoulder_yaw':(-150,150),
     'elbow':(-140,0),'wrist_roll':(-170,170),'wrist_pitch':(-70,70),'wrist_yaw':(-40,40),'neck_yaw':(-80,80),'neck_pitch':(-40,40)}
acts=[]
def jnt(n,s,axis,pos=(0,0,0)):
    lo,hi=LIM[n]
    if s=='R' and n in('hip_roll','shoulder_roll'): lo,hi=-hi,-lo
    name=f'{s.lower()}_{n}' if s else n
    r=rows[n]; d=ST['J'][n]; Jr=PT.MOT[d['motor']]['J_kgcm2']*1e-4
    N=PT.CSG[d['gear']]['N'] if d['kind']=='rotary' else 2*math.pi*d['arm']/(PT.RV[d['screw']]['lead']/1000)
    acts.append(f'<motor name="{name}" joint="{name}" ctrlrange="{-r["T"]:.0f} {r["T"]:.0f}"/>')
    return f'<joint name="{name}" pos="{pos[0]:.3f} {pos[1]:.3f} {pos[2]:.3f}" axis="{axis}" range="{lo} {hi}" armature="{Jr*N*N:.4f}" damping="0.5" frictionloss="0.3"/>'
def inertial(segs,origin):
    m=sum(MS[s]['mass'] for s in segs)*scale
    com=[sum(MS[s]['mass']*MS[s]['com_mm'][k] for s in segs)/sum(MS[s]['mass'] for s in segs) for k in range(3)]
    I=[0,0,0]
    for s in segs:
        ms=MS[s]['mass']*scale; d=[MS[s]['com_mm'][k]-com[k] for k in range(3)]
        for k in range(3): I[k]+=MS[s]['I_kgm2'][k]*scale+ms*mm(1)**2*(sum(x*x for x in d)-d[k]**2)
    I=[max(x,1e-5) for x in I]; a,b,c=sorted(I)
    if a+b<c: I=[max(x,c-min(I)) for x in I]
    return f'<inertial pos="{mm(com[0]-origin[0]):.4f} {mm(com[1]-origin[1]):.4f} {mm(com[2]-origin[2]):.4f}" mass="{m:.3f}" diaginertia="{I[0]:.5f} {I[1]:.5f} {I[2]:.5f}"/>'
def rel(a,b): return f'{mm(a[0]-b[0]):.3f} {mm(a[1]-b[1]):.3f} {mm(a[2]-b[2]):.3f}'
ROOT=(0,0,yz)
def leg(S,s):
    y=P['hip_y']*s; o1=(0,y,yz); o2=(0,y,rz); o3=(0,y,hz); o4=(0,y,kz); o5=(0,y,az)
    fl=P['foot_len']; he=P['heel']
    return f'''<body name="{S}_hipY" pos="{rel(o1,ROOT)}">{jnt('hip_yaw',S,'0 0 1')}{inertial([S+'_hipY'],o1)}
      <body name="{S}_hipR" pos="{rel(o2,o1)}">{jnt('hip_roll',S,'1 0 0')}{inertial([S+'_hipR'],o2)}
      <body name="{S}_thigh" pos="{rel(o3,o2)}">{jnt('hip_pitch',S,'0 1 0')}{inertial([S+'_thigh'],o3)}
        <geom name="{S.lower()}_thigh" type="capsule" fromto="0.018 0 -0.06 0.018 0 {mm(kz-hz)+0.05:.3f}" size="0.04"/>
        <body name="{S}_shank" pos="{rel(o4,o3)}">{jnt('knee',S,'0 1 0')}{inertial([S+'_shank'],o4)}
          <geom name="{S.lower()}_shank" type="capsule" fromto="0.014 0 -0.05 0.014 0 {mm(az-kz)+0.07:.3f}" size="0.035"/>
          <geom name="{S.lower()}_calf" type="capsule" fromto="-0.06 0 -0.12 -0.06 0 {mm(az-kz)+0.16:.3f}" size="0.045"/>
          <body name="{S}_foot" pos="{rel(o5,o4)}">{jnt('ankle_pitch',S,'0 1 0')}{jnt('ankle_roll',S,'1 0 0')}{inertial([S+'_foot'],o5)}
            <geom name="{S.lower()}_foot" type="box" pos="{mm(fl/2-he):.3f} 0 {mm(9-az):.3f}" size="{mm(fl/2):.3f} 0.05 0.009" friction="1.0"/>
          </body></body></body></body></body>'''
def arm(S,s):
    y=P['shoulder_y']*s; ya=(P['shoulder_y']+P['sh_roll_dy'])*s
    o1=(0,y-20*s,sz); o2=(0,ya,sz-40); o3=(0,ya,ez); o4=(0,ya,wz+20); T0=(0,0,pt+50)
    return f'''<body name="{S}_shoulderP" pos="{rel(o1,T0)}">{jnt('shoulder_pitch',S,'0 1 0')}{inertial([S+'_shoulderP'],o1)}
        <body name="{S}_upper_arm" pos="{rel(o2,o1)}">{jnt('shoulder_roll',S,'1 0 0')}{jnt('shoulder_yaw',S,'0 0 1',(0,0,-0.1))}{inertial([S+'_upper_arm'],o2)}
          <geom name="{S.lower()}_upper_arm" type="capsule" fromto="0 0 -0.05 0 0 {mm(ez-sz+40)+0.04:.3f}" size="0.04"/>
          <body name="{S}_forearm" pos="{rel(o3,o2)}">{jnt('elbow',S,'0 1 0')}{inertial([S+'_forearm'],o3)}
            <geom name="{S.lower()}_forearm" type="capsule" fromto="0 0 -0.04 0 0 {mm(wz-ez)+0.03:.3f}" size="0.038"/>
            <body name="{S}_hand" pos="{rel(o4,o3)}">{jnt('wrist_roll',S,'0 0 1')}{jnt('wrist_pitch',S,'0 1 0',(0,0,-0.03))}{jnt('wrist_yaw',S,'1 0 0',(0,0,-0.03))}{inertial([S+'_hand'],o4)}
              <geom name="{S.lower()}_hand" type="box" pos="0 0 -0.1" size="0.016 0.043 0.07"/>
            </body></body></body></body>'''
T0=(0,0,pt+50); W0=(0,0,pt-42); N0=(0,0,tt-15); H0=(0,0,tt+60)
body=f'''<body name="pelvis" pos="0 0 {mm(yz):.3f}"><freejoint name="root"/><site name="imu"/>{inertial(['pelvis','L_pelvis','R_pelvis'],ROOT)}
    <geom name="pelvis" type="box" pos="0 0 {mm((P['pelvis_bot']+pt)/2-yz):.3f}" size="0.085 {mm(P['hip_y']+55):.3f} 0.052"/>
    {leg('L',1)}{leg('R',-1)}
    <body name="waistY" pos="{rel(W0,ROOT)}">{jnt('waist_yaw','','0 0 1')}{inertial(['waistY'],W0)}
    <body name="torso" pos="{rel(T0,W0)}">{jnt('waist_pitch','','0 1 0')}{inertial(['torso'],T0)}
      <geom name="torso" type="box" pos="0 0 {mm((pt+100+tt)/2-pt-50):.3f}" size="0.11 0.17 {mm((tt-pt-100)/2):.3f}"/>
      {arm('L',1)}{arm('R',-1)}
      <body name="neckY" pos="{rel(N0,T0)}">{jnt('neck_yaw','','0 0 1')}{inertial(['neckY'],N0)}
      <body name="head" pos="{rel(H0,N0)}">{jnt('neck_pitch','','0 1 0')}{inertial(['head'],H0)}
        <geom name="head" type="sphere" pos="0.01 0 0.08" size="0.1"/></body></body>
    </body></body></body>'''
xml=f'''<mujoco model="robotlab_v3">
  <!-- Generated by sim/v3/gen_v3.py from v3 CAD (joint locations, per-segment mass/COM/inertia scaled to the {V3['m']:.1f} kg catalog rollup)
       and v3/analysis (ctrlrange = catalog peak torque, armature = TBM2G rotor inertia x ratio^2). Collision = primitives; visuals on the site = CAD GLB parts.
       Linear (roller-screw) joints modelled as rotary with their effective ratio at the nominal lever arm. Leg-leg contacts are enabled
       (single-leg adduction beyond -6 deg collides in CAD). -->
  <compiler angle="degree" autolimits="true" inertiafromgeom="false"/>
  <option timestep="0.002" integrator="implicitfast"/>
  <default><geom contype="1" conaffinity="1" condim="3" rgba="0.5 0.7 0.88 1"/></default>
  <asset><texture name="grid" type="2d" builtin="checker" rgb1=".1 .15 .2" rgb2=".15 .2 .25" width="300" height="300"/><material name="grid" texture="grid" texrepeat="8 8"/></asset>
  <worldbody><light pos="0 0 4" dir="0 0 -1"/><geom name="floor" type="plane" size="20 20 0.1" material="grid"/>
  {body}
  </worldbody>
  <contact><exclude body1="pelvis" body2="L_thigh"/><exclude body1="pelvis" body2="R_thigh"/><exclude body1="pelvis" body2="torso"/><exclude body1="torso" body2="L_upper_arm"/><exclude body1="torso" body2="R_upper_arm"/><exclude body1="L_thigh" body2="L_shank"/><exclude body1="R_thigh" body2="R_shank"/><exclude body1="L_shank" body2="L_foot"/><exclude body1="R_shank" body2="R_foot"/><exclude body1="L_upper_arm" body2="L_forearm"/><exclude body1="R_upper_arm" body2="R_forearm"/></contact>
  <actuator>{"".join(acts)}</actuator>
</mujoco>'''
open('humanoid_v3.xml','w').write(xml); print('actuators',len(acts),'mass',round(V3['m'],1),'scale %.3f'%scale)
