"""T&R L3 25 deg chest-only: energy into the chest pad, rigid-body pivot-impact bounds. humanoid_mjx.xml zero pose (standing), masses
scaled to 72.1 kg. Pad face = chest_pad geom +x face. Pivot cases: toes (standing tip), knees (kneel-type pivot); free body.
'25 deg' = angle between the pad normal and the pad-point velocity at contact [EST interpretation; Controls 1021e37 uses chest-normal
vs floor normal, equal for a rigid sagittal topple where the velocity is vertical-ish]. Plateau: Materials b359af8 core."""
import mujoco, numpy as np, json, math
m=mujoco.MjModel.from_xml_path('../legs/rl/humanoid_mjx.xml'); d=mujoco.MjData(m); mujoco.mj_forward(m,d)
M0=m.body_mass.sum(); s=72.1/M0; M=72.1
com=(d.xipos*m.body_mass[:,None]).sum(0)/M0
def Iyy_about(p):  # sagittal (y-axis) inertia about point p
    I=0
    for b in range(1,m.nbody):
        R=d.ximat[b].reshape(3,3); Ib=R@np.diag(m.body_inertia[b])@R.T; r=d.xipos[b]-p
        I+=s*(Ib[1,1]+m.body_mass[b]*(r[0]**2+r[2]**2))
    return I
g=m.geom('chest_pad'); gid=g.id; pad=d.geom_xpos[gid]+d.geom_xmat[gid].reshape(3,3)@np.array([m.geom_size[gid][0],0,0])
toe=np.array([d.geom_xpos[[i for i in range(m.ngeom) if m.geom_bodyid[i]==m.body('L_foot').id][0]][0]+0.12,0,0.0])
knee=np.r_[d.xpos[m.body('L_shank').id][0],0,d.xpos[m.body('L_shank').id][2]]
Icm=Iyy_about(com); o=dict(M=M,scale=round(s,4),com=com.round(3).tolist(),pad_face=pad.round(3).tolist(),Icm=round(Icm,2),toe=toe.round(3).tolist(),knee=knee.round(3).tolist())
E0=527.; c=math.cos(math.radians(25))
for nm,p in (('toe_pivot',toe),('knee_pivot',knee)):
    Ip=Iyy_about(p); r=np.linalg.norm((pad-p)[[0,2]]); w=math.sqrt(2*E0/Ip); vp=w*r
    # pivot holds: 1 DOF -> m_eff along the pad normal = Ip/(r cos25)^2, v_n = vp cos25 -> E_pad = full KE
    meff=Ip/(r*c)**2; vn=vp*c; o[nm]=dict(Ip=round(Ip,2),r_pad=round(r,3),omega=round(w,2),v_pad=round(vp,2),v_n=round(vn,2),m_eff=round(meff,1),E_pad=round(0.5*meff*vn**2,1))
# free body: same pre-impact state (rotating about the toe), pad impulse along the normal; d_perp = CoM offset from the normal line
Ip=Iyy_about(toe); r=np.linalg.norm((pad-toe)[[0,2]]); w=math.sqrt(2*E0/Ip); vn=w*r*c
dg=abs(pad[2]-com[2])  # pad normal (+x, torso-fixed) passes this far from the CoM (rigid, so invariant under the topple)
for dperp in (round(dg,3),):
    meff=1/(1/M+dperp**2/Icm); o[f'free_d{dperp}']=dict(m_eff=round(meff,1),v_n=round(vn,2),E_pad=round(0.5*meff*vn**2,1))
P=dict(nom0=13.0,weak15=11.7,f25=0.73,lot=-0.03,usable=81.2,usable_m=73.8,k_bottom=5.3e6)
F25=P['nom0']*P['f25']*(1+P['lot']); o['plateau25_kN']=round(F25,2)
for k in [k for k in o if isinstance(o[k],dict) and 'E_pad' in o[k]]:
    E=o[k]['E_pad']; E15=1.5*E; st=E15/F25; o[k]['E_x1.5']=round(E15,1); o[k]['stroke_mm']=round(st,1)
    if st>P['usable']:
        Ex=E15-F25*P['usable']; o[k]['excess_J']=round(Ex,1); o[k]['bottomed_peak_kN']=round(F25+math.sqrt(2*Ex*P['k_bottom'])/1e3,1)
    o[k]['plateau_to_fit_73.8_kN']=round(E15/P['usable_m']/P['f25'],1)  # 0-deg nominal plateau needed
json.dump(o,open('l3_25deg_pad.json','w'),indent=1); print(json.dumps(o,indent=1))
