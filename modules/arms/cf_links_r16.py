"""R16 option C(b): CF tubes bonded to machined 7075-T651 end fittings for the upper-arm and forearm links (gear housings and the W2
carrier are excluded). Current links per model_v4: upper-arm tube 7075 Ø50x2 x 87 mm; forearm shell Ø70/66 x 194 mm (also the flexor
thermal clamp, R5/R8 ladder B). Elbow clevis, end cap and roll-yaw link stay 7075 (they are the end fittings).
Cited: Easy Composites 50/47 roll-wrapped tube 364 g/m, 0/90 UD, $105.05/m (woven; easycomposites.us, 2026-10-21); max OD in range 60 mm.
Rock West 45146 2.000x2.125x72 in, Tenax UTS50, 0.055 lb/in3 (1.52 g/cc), $305.99 (1-5). 3M DP460 TDS: Al 24 MPa, FRP 6.9 MPa (substrate
failure) overlap shear. [EST]: CF axial E 75 GPa (0/90 UD, ~60% 0 deg), in-plane G 5 GPa, peel/peak factor K=3 on average lap shear."""
import json,os,math
H=os.path.dirname(os.path.abspath(__file__)); rA,rC=2.81e-6,1.52e-6; EA,GA,EC,GC=70000,26900,75000,5000
tau_allow=6.9/1.5; K=3.0
def tube(od,t,L,rho): return rho*math.pi/4*(od**2-(od-2*t)**2)*L
def link(name,od_al,t_al,L,od_cf,t_cf,M,T):
    m_al=tube(od_al,t_al,L,rA); m_cf=tube(od_cf,t_cf,L,rC)
    ri=(od_cf-2*t_cf)/2; Lb=K*M*1e3/(math.pi*ri**2*tau_allow); Lb=max(20.0,math.ceil(Lb))
    spig=tube(od_cf-2*t_cf,1.5,2*Lb,rA); glue=2*math.pi*2*ri*Lb*0.15*1.1e-6*1.0
    m_new=m_cf+spig+glue
    I=lambda od,t:math.pi/64*(od**4-(od-2*t)**4); J=lambda od,t:2*I(od,t)
    S_cf=I(od_cf,t_cf)/(od_cf/2)
    return dict(link=name,L_mm=L,al_kg=round(m_al,4),cf_tube_kg=round(m_cf,4),bond_length_each_mm=Lb,spigots_kg=round(spig,4),
                new_kg=round(m_new,4),delta_side_kg=round(m_new-m_al,4),overlap_fraction=round(2*Lb/L,2),
                sigma_cf_MPa=round(M*1e3/S_cf,1),tau_bond_peak_MPa=round(K*M*1e3/(math.pi*ri**2*Lb),2),tau_allow=round(tau_allow,2),
                EI_ratio=round(EC*I(od_cf,t_cf)/(EA*I(od_al,t_al)),2),GJ_ratio=round(GC*J(od_cf,t_cf)/(GA*J(od_al,t_al)),2),
                twist_deg_at_T=round(math.degrees(T*1e3*L/(GC*J(od_cf,t_cf))),3),twist_al_deg=round(math.degrees(T*1e3*L/(GA*J(od_al,t_al))),3))
# governing: upper arm = fall/tuck (forearm+hand 2.77 kg x 187.5 m/s2 x 0.2 m [EST] = 104 N.m) vs carry shoulder 65.6; torsion = shoulder yaw ctrl 70 N.m
# forearm = elbow cap 69 N.m vs fall 2.77x187.5x0.15 = 78 N.m [EST]; P-042 carry elbow 14.6 (not governing); torsion = wrist roll ctrl 36 N.m
ua=link('upper arm',50,2,87,50,1.5,104,70); fa=link('forearm',70,2,194,70,1.5,78,36)
therm=dict(issue='forearm shell is the flexor thermal clamp (R5 ladder B, hand board gap pad); CF k_transverse ~0.5-1 W/mK [EST] vs 7075 ~130',
           fix='0.8 mm 7075 inner heat-spreader sleeve over the 120 mm motor zone, bonded to the CF',sleeve_kg=round(tube(67,0.8,120,rA),4))
fa_net=round(fa['delta_side_kg']+therm['sleeve_kg'],4)
cost=dict(ua_tube_usd=round(105.05*0.087*1.0,2),fa_tube_ref_usd=round(305.99/72*194/25.4,2),
          note='UA from Easy 50/47 per metre; forearm Ø70 is outside stock ranges (Easy max 60), so it needs custom roll-wrapping: Rock West 2.0-in-ID price per length scaled as a lower bound [no cited Ø70 price]; spigot machining extra')
out=dict(upper_arm=ua,forearm=fa,thermal=therm,forearm_net_with_sleeve_side=fa_net,
         saving_pair_kg=dict(ua=round(2*ua['delta_side_kg'],3),forearm_no_sleeve=round(2*fa['delta_side_kg'],3),forearm_with_sleeve=round(2*fa_net,3)),
         cost=cost)
json.dump(out,open(os.path.join(H,'cf_links_r16.json'),'w'),indent=1); print(json.dumps(out,indent=1))
