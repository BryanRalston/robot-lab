# R-146 prone landing hand model (light numpy-free). Inputs cited in R146_PRONE_LANDING.md
import json,math
g=9.81; m=68.42                      # R-146 credible mass
zc_stand=0.943; zc_kneel=0.50; zc_prone=0.125   # walk zc; kneel = stand - shank drop 0.45 [EST]; prone kneel_hold F
pad_z_kneel=1.05; knee_z=0.05        # sim/v3 chain: pad 0.58 above hip pitch; thigh 0.42
F_lo0,F_hi0,F_lo15=17.7e3,22.3e3,16.6e3; F_ceil=22.35e3; stroke_use=62e-3; k_back=24e6
r={}
v=0.1; m_up=60.0                     # D94 CoM speed limit; above-knee mass [EST]
r['controlled_KE_J']=0.5*m*v*v
Fst=(0.5*m*g,0.7*m*g); r['controlled_static_N']=Fst
Fdyn=v*math.sqrt(k_back*40.0); r['controlled_peak_N']=Fst[1]+Fdyn
r['controlled_elastic_cap_J']=F_lo0**2/(2*k_back)
for case,zc in (('kneel',zc_kneel),('stand',zc_stand)):
  E=m*g*(zc-zc_prone); r[case+'_E_J']=E
  r[case+'_stroke_mm']=(E/F_hi0*1e3,E/F_lo15*1e3)
rc=zc_kneel-knee_z; rp=pad_z_kneel-knee_z; I=m_up*(rc**2+0.3**2); meff=I/rp**2
r['kneel_meff_kg']=meff; r['kneel_vpad']=math.sqrt(2*r['kneel_E_J']/meff)
r['kneel_g_pinned_at_r0.8']=F_ceil*rp/I*0.8/g; r['kneel_g_free']=F_ceil/m_up/g
r['bulkhead_MPa_at_ceiling']=216*F_ceil/24.4e3
r['pack_N_at_free_g']=8.75*g*r['kneel_g_free']; r['pack_N_at_pinned_g']=8.75*g*r['kneel_g_pinned_at_r0.8']
json.dump(r,open('r146_prone.json','w'),indent=1); print(json.dumps(r,indent=1))
