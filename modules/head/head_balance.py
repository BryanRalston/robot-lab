"""Head-as-balancer study. Run: python3 modules/head/head_balance.py -> modules/head/head_balance.json
Uses sim/v3/humanoid_v3.xml (head 0.647 kg, neckY 0.490 kg) + MuJoCo gravity/inverse dynamics. Light (<200 MB)."""
import json, math, numpy as np, mujoco
m = mujoco.MjModel.from_xml_path('sim/v3/humanoid_v3.xml'); d = mujoco.MjData(m)
g = 9.81; M = float(m.body_subtreemass[1])
jid = lambda n: m.joint(n).id; dof = lambda n: m.jnt_dofadr[jid(n)]; qa = lambda n: m.jnt_qposadr[jid(n)]
hb = m.body('head').id
mh = float(m.body_mass[hb]); rx, rz = m.body_ipos[hb][0], m.body_ipos[hb][2]
r = math.hypot(rx, rz)
I_eff = float(m.body_inertia[hb][1] + mh*r*r + m.dof_armature[dof('neck_pitch')])
out = {'robot_mass_model': M, 'head_mass': mh, 'head_com_arm_m': r, 'I_eff_pitch': I_eff}
# 1) quasi-static: COM shift and gravity moment change across neck pitch +-40
xs = [rx*math.cos(math.radians(t)) + rz*math.sin(math.radians(t)) for t in (-40, 40)]
dx = xs[1]-xs[0]
out['head_com_x_travel_m'] = dx; out['robot_com_shift_mm'] = 1000*mh*dx/M
out['gravity_moment_swing_Nm'] = mh*g*dx
# yaw: head COM 45.6 mm forward of yaw axis -> +-80 deg moves it laterally +-45 mm
out['robot_com_lateral_shift_mm_yaw80'] = 1000*mh*rx*math.sin(math.radians(80))*2/M
# 2) MuJoCo: gravity torques at waist_pitch and hip_pitch, lean cases, neck 0 vs best counter-pitch
def tau(lean, neck):
    mujoco.mj_resetData(m, d)
    d.qpos[qa('waist_pitch')] = math.radians(lean); d.qpos[qa('neck_pitch')] = math.radians(neck)
    for s in 'lr': d.qpos[qa(f'{s}_hip_pitch')] = math.radians(-lean/2)
    mujoco.mj_forward(m, d)
    return {j: float(d.qfrc_bias[dof(j)]) for j in ('waist_pitch','l_hip_pitch','neck_pitch')}
cases = []
for lean in (10, 20, 30):
    a, b = tau(lean, 0), tau(lean, -40 if lean>0 else 40)
    cases.append({'lean_deg': lean, 'neck0': a, 'neck_counter40': b,
      'waist_reduction_pct': 100*(abs(a['waist_pitch'])-abs(b['waist_pitch']))/abs(a['waist_pitch']),
      'hip_reduction_pct': 100*(abs(a['l_hip_pitch'])-abs(b['l_hip_pitch']))/abs(a['l_hip_pitch'])})
out['lean_cases'] = cases
# 3) dynamic: reaction torque on torso is bounded by the neck motor itself
for name, stall, rpm in (('XM540-W270', 10.6, 30), ('XM430-W350', 4.1, 46)):
    hold = mh*g*r
    alpha = (stall-hold)/I_eff; w = rpm*2*math.pi/60
    t_acc = w/alpha; ang = 0.5*alpha*t_acc**2
    out[name] = {'gravity_hold_Nm': hold, 'max_alpha_rad_s2': alpha, 'peak_reaction_Nm': stall,
                 'max_ang_momentum_Nms': I_eff*w, 'time_to_wmax_s': t_acc, 'deg_used_to_wmax': math.degrees(ang),
                 'hold_margin_x': stall/hold, 'rated_cont_Nm': 0.2*stall}
# push recovery reference: 66.5 kg, COM 0.95 m, 0.4 m/s push-induced COM velocity
Lpush = 66.5*0.4*0.95
out['push_ang_momentum_Nms'] = Lpush
out['head_share_of_push_momentum_pct'] = 100*out['XM540-W270']['max_ang_momentum_Nms']/Lpush
out['peak_hip_waist_limits_Nm'] = {'hip_pitch': 167, 'waist_pitch': 116}
out['dyn_reduction_upper_bound_pct'] = {'hip_pitch': 100*10.6/167, 'waist_pitch': 100*10.6/116,
   'note': 'only for <=~0.15 s until the neck hits its +-40 deg stop, then it reverses; zero net impulse over a cycle'}
json.dump(out, open('modules/head/head_balance.json','w'), indent=1)
print(json.dumps(out, indent=1))
