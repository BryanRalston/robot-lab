"""L74 (1): ID Option B, cut-out in the L60 knee trunnion top plate (x -175..-40, y 32-228, z 816-824, 8 mm) over the chimney y 104-156.
Hand check [EST]. Loads (L61/TRUNNION_BREAK, L60 basis): bracket couple 8.66 kN design / 5.77 kN walk (x 3364/5053) carried by the top plate
as in-plane axial force into the strut to the femur (x -45..5, y 110-150, 40 x 8). Walk amplitude = walk/2 (0..peak) [EST].
Allowables: 7075-T7351 plate <=1.5 in, single-path R-128 band 262 MPa design (393/1.5), fall limit 393, fatigue amplitude 58 MPa (R144).
Critical: the strut lies INSIDE the cut y-range, so the side ligaments (y 32-104, 156-228) must feed the strut through a transverse band
of depth b (in x) between the strut end x -45 and the cut's forward edge. Band = short cantilever, arm 6 mm (ligament edge y104 -> strut
edge y110) per side, 4.33 kN design each; Kt 2.0 at the R5 re-entrant corner [EST, Peterson shoulder-fillet r/d~0.3]."""
import json,math
P_d,P_w=8660.,8660*3364/5053; t=8.; arm=6.; Kt=2.0; rho=2.81e-6
def band(b):
    Z=t*b*b/6; sd=(P_d/2)*arm/Z; sw_a=(P_w/4)*arm/Z*Kt; tau=(P_d/2)/(t*b)
    return dict(b=b,sigma_design=round(sd,1),SF_design_262=round(262/sd,2),sigma_amp_Kt=round(sw_a,1),SF_fatigue_58=round(58/sw_a,2),tau=round(tau,1),
                SF_shear=round(0.577*262/tau,2),fall_capacity_kN_at393=round(P_d*393/sd/1000,1))
def net(w_cut,r=5,Kt_hole=None):
    a=w_cut/2; K=Kt_hole or 1+2*math.sqrt(a/r)   # Inglis, conservative for a rounded-rectangle hole
    g=P_d/(196*t); n=P_d/((196-w_cut)*t); amp=(P_w/2)/(196*t)*K
    return dict(Kt_inglis=round(K,2),gross=round(g,1),net=round(n,1),peak_design=round(g*K,1),SF_design=round(262/(g*K),2),amp_peak=round(amp,1),SF_fatigue=round(58/amp,2),SF_fall_net_393=round(393/n,1))
out={}
out['ID_52x40_x-40..-80']=dict(band_mm=0,result='FAIL: cut starts at x -40, strut lands at x -45..-40 inside y 104-156 -> no load path from the ligaments to the strut (band 0); ID x -40 edge also cuts the 5 mm strut overlap')
out['bands']=[band(b) for b in (6,8,10,12,15,18)]
out['net_section_cut52']={f'R{r}':net(52,r) for r in (5,8,10)}
# recommended: band 15 -> cut x -60..-79 (forward edge 15 mm aft of the strut end x -45), y 104-156, R8 corners
for name,x0,x1,r in (('rec_band18_x-63..-88_R8',-88,-63,8),('ID_area_band15_x-60..-85_R8',-85,-60,8)):
    L=x1-x0; A=L*52-4*(1-math.pi/4)*r*r; out[name]=dict(cut_LxW=[L,52],r=r,area_mm2=round(A),dm_kg_side=round(-A*t*rho,4),dm_kg_pair=round(-2*A*t*rho,4))
json.dump(out,open('results/r031/p156_rev5_optionB.json','w'),indent=1); print(json.dumps(out,indent=0))
