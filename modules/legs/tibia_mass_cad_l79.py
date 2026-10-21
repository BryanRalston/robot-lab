"""R-152: tibia 2.0 vs 1.5 wall mass from model_v4 CAD solids (OCC volume x 2.81 g/cc 7075). Tube: model_v4 l.185 o45, length tt-tb = 314
(knee_z-50 .. ankle_z+56); ends are plain (tongue neck and fork bridge are separate parts, unchanged). Doubler sleeve 0.5 x 100 (l.186), OD = tube ID - 0.20
(BOND_SPEC 3 bond). Booking basis R-135 (L65): 1.5 uniform wall, +0.15 robot for femur+tibia vs 1.2."""
import os,sys,json
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'../model')); import model_v4 as M
rho=2.81e-6; kz,az=M.P['knee_z'],M.P['ankle_z']; L=(kz-50)-(az+56)
def vol(od,idd,l): return M.cyl(od,l,'z',id_=idd).val().Volume() if hasattr(M.cyl(od,l,'z',id_=idd),'val') else M.cyl(od,l,'z',id_=idd).Volume()
o={}
for t in (1.2,1.5,2.0):
    ID=45-2*t; tube=vol(45,ID,L)*rho; sl=vol(ID-0.2,ID-1.2,100)*rho
    o[t]=dict(tube_kg=round(tube,4),sleeve_kg=round(sl,4),sum_kg_leg=round(tube+sl,4))
d=o[2.0]['sum_kg_leg']-o[1.5]['sum_kg_leg']
out=dict(length_mm=L,per_wall=o,delta_2p0_vs_1p5_kg_leg=round(d,4),delta_robot=round(2*d,4),
  tibia_share_of_R135_1p5_vs_1p2_robot=round(2*(o[1.5]['sum_kg_leg']-o[1.2]['sum_kg_leg']),4),
  new_total_booking_robot=round(0.15+2*d,3),note='R-135 booked +0.15 robot (femur+tibia 1.2 -> 1.5); femur unchanged at 1.5')
json.dump(out,open('results/r031/tibia_mass_cad_l79.json','w'),indent=1); print(json.dumps(out,indent=0))
