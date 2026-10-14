"""RL Arms R3 (O-A1): catalog arm inertials per side for sim/v3 bodies (left side; right mirrors y).
Masses: CONTRACTS §1a arm rows, §3 arms structure 0.80/side split [EST], v3.py hand_one split, R-027 palm, P-027/D67 wrist pair 0.884,
Electronics §10.4/10.5 hand node 0.035 + RP40 0.043. Positions are along the sim/v3 body frames (pos in m); component placement [EST].
Each component is a solid cylinder about the link axis (z) with stated r, L [EST]; tensor = sum of own + parallel-axis about link COM."""
import json,os,numpy as np
H=os.path.dirname(os.path.abspath(__file__))
# (name, mass kg, centre (x,y,z) in body frame, r m, L m, axis, source)
B={
 'torso (re-split, Torso & Power)':[('shoulder_pitch actuator TBM2G-07608C+CSG-25-100 (housing in torso wall)',1.52,(0,0.170,0.220),0.048,0.086,'y','CONTRACTS §1a')],
 'L_shoulderP':[('shoulder_roll actuator TBM2G-06813C+CSG-25-100+clutch',1.24,(0,0.090,-0.020),0.037,0.087,'x','CONTRACTS §1a'),
                ('roll bracket / output flange [EST]',0.15,(0,0.050,0),0.04,0.05,'y','§3 arms struct split EST')],
 'L_upper_arm':[('shoulder_yaw actuator TBM2G-06008C+CSG-17-100',0.81,(0,0,-0.100),0.0355,0.073,'z','CONTRACTS §1a'),
                ('upper arm tube 7075 + elbow clevis [EST]',0.35,(0,0,-0.185),0.025,0.15,'z','§3 arms struct split EST')],
 'L_forearm':[('elbow actuator TBM2G-05013C+CSG-20-100',0.90,(0,0,0.0),0.0305,0.081,'y','CONTRACTS §1a'),
              ('6x flexor DCX22S+GPX22HP (tier 1)',6*0.173,(0,0,-0.080),0.033,0.072,'z','v3.py hand_one / parts.py'),
              ('5x small DCX16S+GPX16LN (tier 2)',5*0.053,(0,0,-0.160),0.025,0.053,'z','v3.py hand_one'),
              ('11x spool/mount allowance',0.015*6+0.007*5,(0,0,-0.12),0.03,0.15,'z','v3.py hand_one'),
              ('11x tendon/sheath allowance 0.025',0.275,(0,0,-0.15),0.03,0.2,'z','v3.py hand_one'),
              ('wrist pitch/yaw pair (D67, drives off-arm)',0.884,(0,0,-0.170),0.033,0.13,'z','actuators/results/wrist_p027.json'),
              ('wrist_roll actuator TBM2G-05008C+CSG-14-100',0.55,(0,0,-0.210),0.028,0.067,'z','CONTRACTS §1a'),
              ('forearm shell [EST]',0.30,(0,0,-0.12),0.035,0.18,'z','§3 arms struct split EST'),
              ('hand node + RP40-11024SFR/P-HC',0.078,(0,0,-0.19),0.02,0.07,'z','electronics §10.4/10.5')],
 'L_hand':[('fingers/palm structure + misc (v3 0.35+0.05)',0.40,(0,0,-0.100),0.04,0.14,'z','v3.py hand_one'),
           ('palm 7075 delta (R-027)',0.072,(0,0,-0.07),0.04,0.09,'z','R-027')],
}
def cyl(m,r,L,ax):
    a=m*r*r/2; t=m*(3*r*r+L*L)/12; I={'x':np.diag([a,t,t]),'y':np.diag([t,a,t]),'z':np.diag([t,t,a])}[ax]; return I
out={}
for b,parts in B.items():
    M=sum(p[1] for p in parts); c=sum(p[1]*np.array(p[2]) for p in parts)/M; I=np.zeros((3,3))
    for n,m,pos,r,L,ax,src in parts:
        d=np.array(pos)-c; I+=cyl(m,r,L,ax)+m*(np.dot(d,d)*np.eye(3)-np.outer(d,d))
    out[b]=dict(mass=round(M,4),pos=[round(x,4) for x in c],fullinertia=[round(I[0,0],6),round(I[1,1],6),round(I[2,2],6),round(I[0,1],6),round(I[0,2],6),round(I[1,2],6)],
                parts=[dict(name=n,mass=m,pos=pos,src=s) for n,m,pos,r,L,ax,s in parts])
tot=sum(v['mass'] for v in out.values()); arm=tot-out['torso (re-split, Torso & Power)']['mass']
out['_meta']=dict(per_side_total_kg=round(tot,3),moving_arm_kg=round(arm,3),sim_v3_arm_kg=5.953,
  note='Left side; mirror y for right. torso entry is mass ADDED to the torso body at the shoulder (Torso & Power re-split). All positions/r/L [EST]; masses cited per part. Apply as <inertial pos=... mass=... fullinertia=.../> on sim/v3 bodies.')
json.dump(out,open(os.path.join(H,'arm_inertials_r3.json'),'w'),indent=1)
for k,v in out.items(): print(k,v if k[0]=='_' else (v['mass'],v['pos']))
