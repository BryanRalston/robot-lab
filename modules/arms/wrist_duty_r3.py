"""RL Arms R3: wrist screw duty for P-027 (Actuators D67, THK BNK1004-2.5, Ca 2100 N) from Arms load cases.
Screw force per screw = T_wrist / 0.025 m / 2 (Actuators wrist_p027 convention). L10 formula identical to actuators/wrist_p027.py.
Mission profile time fractions are [EST] (no arm task spec exists); forces come from arm_loads_r1.json / carry_pose_r3 (sim/v3)."""
import json,os,mujoco,numpy as np
H=os.path.dirname(os.path.abspath(__file__))
import carry_pose_r3 as c
def wrist_T(sp,el):
    c.load(sp,el); m,d=c.m,c.d
    pt=d.xpos[c.hand]+d.xmat[c.hand].reshape(3,3)@np.array([0,0,-0.10]); jp=np.zeros((3,m.nv)); mujoco.mj_jac(m,d,jp,None,pt,c.hand)
    tau=d.qfrc_bias+jp.T@np.array([0,0,10*9.81]); i=m.jnt_dofadr[c.jid('l_wrist_pitch')]; return abs(float(tau[i]))
L=json.load(open(os.path.join(H,'arm_loads_r1.json')))
T_carry=wrist_T(-60,-110)                                   # P-042 pose, 10 kg
T_load=max(v['joints']['wrist_pitch']['static'] for k,v in L.items() if k[0]!='_')   # 7.4 worst static 10 kg
T_free=L['reach_horizontal_noload']['joints']['wrist_pitch']['total']               # no load + 20 rad/s^2
F=lambda T:T/0.025/2
Ca=2100.0; rpm=2250.0
duty=[  # (time fraction, force N, speed fraction of 2250 rpm, basis)
 (0.01,294.0,1.0,'contract peak 14.7 N·m (1.5x need) events [EST frequency]'),
 (0.10,F(T_load),0.3,'manipulating 10 kg, worst static wrist 7.4 N·m'),
 (0.20,F(T_carry),0.02,'P-042 carry hold, corrective motion only'),
 (0.39,max(F(T_free),20.0),0.3,'unloaded manipulation (floor 20 N preload/friction as Actuators)'),
 (0.30,20.0,0.02,'idle / walking, arm quasi-static'),
]
nm=sum(t*s for t,_,s,_ in duty)*rpm
Fm=(sum(t*f**3*s for t,f,s,_ in duty)/sum(t*s for t,_,s,_ in duty))**(1/3)
res={fw:(Ca/(fw*Fm))**3*1e6/(nm*60) for fw in (1.2,1.5,2.0)}
out=dict(T_carry_Nm=round(T_carry,2),T_load_Nm=T_load,T_free_Nm=T_free,duty=[dict(frac=t,F_N=round(f,1),speed=s,basis=b) for t,f,s,b in duty],
         Fm_N=round(Fm,1),n_mean_rpm=round(nm,1),L10_h={str(k):round(v) for k,v in res.items()},target_h=14600)
json.dump(out,open(os.path.join(H,'wrist_duty_r3.json'),'w'),indent=1); print(json.dumps(out,indent=0))
