"""D97: PU knee stop pair at 135 deg (Robot Lab approved D96; Controls 0fb7c0e knee_stop_impact.py: 6.2 rad/s at stop, MO=0 forward fall).
Inertia: Controls' MuJoCo peaks fit tau_peak = 2*I*w/tc (solref dampratio 1: peak at contact = b*v, b = 2/tc):
 6825*0.005, 3333*0.01, 1665*0.02 /(2*6.2) -> I_body ~2.7 kg m^2 per knee. Rotor: 2 x TBM2G-07613D Jm 0.576 kg cm^2 (tbm2g p.284)
 + nut-rotor hub 0.2 kg cm^2 each [EST], reflected x 59.7^2 (D12). PU: Freelin-Wade PUR90A (92A) TDS, ASTM D575 compressive
 load 2/5/10/15/20/25 % = 160/325/705/1050/1380/1690 psi. 90A dynamic strain limit 25 % (Gallagher design guide, 0.16 Hz);
 shape factor >= 0.5 via 3 x 12 mm laminations with 1 mm steel shims (Gallagher/Boedeker: SF < 0.25 may buckle)."""
import json,math,numpy as np
import cadquery as cq
w=6.2; I_body=np.mean([6825*0.005,3333*0.01,1665*0.02])/(2*w)
J_rot=2*(0.576e-4+0.2e-4)*59.7**2; I=I_body+J_rot
E=0.5*I*w**2; E_rot=0.5*J_rot*w**2
eps=np.array([0,.02,.05,.10,.15,.20,.25]); sig=np.array([0,160,325,705,1050,1380,1690])*0.0068948   # MPa
R=60.0; A=2*30*30; T=36.0   # pad radius from knee axis, total face area (2 pads), total PU thickness per pad
V=A*T/1000  # cm^3
cum=np.concatenate([[0],np.cumsum(np.diff(eps)*(sig[1:]+sig[:-1])/2)])   # J/cm^3
curve=[dict(strain=float(e),theta_deg=round(math.degrees(e*T/R),2),torque_Nm=round(s*A*R/1000,0),energy_J=round(c*V,1)) for e,s,c in zip(eps,sig,cum)]
e_pk=float(np.interp(E/V,cum,eps)); s_pk=float(np.interp(e_pk,eps,sig))
tau_pk=s_pk*A*R/1000; th_pk=math.degrees(e_pk*T/R)
tau_rot=tau_pk*J_rot/I; F_pair=tau_rot/0.0475; F_pair_w=F_pair/0.71
mass=V*1.13+4*30*30*1*7.85e-3+30   # PU + 4 shims + 2 holders 15 g [EST]
res=dict(I_body_kgm2=round(I_body,3),J_rotor_reflected_kgm2=round(J_rot,3),E_total_J=round(E,1),E_rotor_J=round(E_rot,1),rotor_share=round(E_rot/E,3),
 pad='2 pads, each 30x30 face, 3 x 12 mm PUR90A + 2 x 1 mm steel shims (38 mm), at r 60 mm from the knee axis, tongue -> clevis',
 shape_factor_per_layer=round(30*30/(4*30*12),3),V_cm3=V,E_capacity_25pct_J=round(cum[-1]*V,1),energy_SF=round(cum[-1]*V/E,2),
 peak_strain=round(e_pk,3),peak_torque_Nm=round(tau_pk),stroke_deg=round(th_pk,2),stroke_mm_at_pad=round(e_pk*T,1),max_knee_deg=round(135+th_pk,1),
 pad_force_total_kN=round(s_pk*A/1000,1),screw_axial_rotor_pair_N=round(F_pair),screw_axial_per_screw_N_nominal=round(F_pair/2),
 screw_axial_per_screw_N_worst_arm=round(F_pair_w/2),C0a_frac_worst=round(F_pair_w/2/27300,3),mass_kg_per_knee=round(mass/1000,3),
 mass_kg_robot=round(2*mass/1000,3),curve=curve)
json.dump(res,open('results/knee_stop_pu_d97.json','w'),indent=1); print(json.dumps({k:v for k,v in res.items() if k!='curve'},indent=0)); [print(c) for c in curve]
# CAD sketch: one laminated pad (PU layers + shims) on a 15 g 7075 holder plate [EST]
p=cq.Workplane('XY')
z=0
for i in range(3):
    p=p.union(cq.Workplane('XY').box(30,30,12,centered=(True,True,False)).translate((0,0,z))); z+=12
    if i<2: p=p.union(cq.Workplane('XY').box(30,30,1,centered=(True,True,False)).translate((0,0,z))); z+=1
p=p.union(cq.Workplane('XY').box(40,40,3,centered=(True,True,False)).translate((0,0,-3)))
cq.exporters.export(p,'cad/knee_stop_pu_pad_d97.step')
