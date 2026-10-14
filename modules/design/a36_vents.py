"""A36 / P-026 louvre layout to Thermal A35 (A35_VENT_SPEC.md) + D69C knee fins. RL Industrial Design. Areas [EST] until A29 CAD.
Per joint per leg: inlet >=50 cm2 AND >=30 % of panel-over-housing; outlet >=60 cm2 AND >=35 %; fin standoff >=8 mm (never <5); slots >=3 mm."""
import json,os,math
H=os.path.dirname(os.path.abspath(__file__)); PCA=1.8  # kg/m2 PC 1.5
RIB=0.15
# ID panel-over-housing estimates (front+outboard quarter-to-half round at r_fin+8, times housing length + 20 mm blends)
knee_r=42.5+9+8; knee_L=110+40; knee_panel=math.pi*knee_r*knee_L/1e2*1.0     # cm2 (half-round, front+outboard)
hip_panel=250.0                                                                  # cm2 [EST] front-lower thigh under skirt line
J={}
J['knee']=dict(panel_cm2=round(knee_panel),inlet='front-lower thigh fairing over the housing (axial slots 3-4 mm, aligned with front 9 mm fins) + knee cap louvres as ram entry',
  inlet_open_cm2=round(max(50,0.30*knee_panel)),outlet='rear (popliteal) high: thigh fairing has no rear panel -> free outlet, rear 25 mm fins in free air (>= 60 cm2 trivially)',outlet_open_cm2='open (no panel)',
  standoff='front fins 9 mm -> fairing inner face at r 59.5 from housing axis (fin tip + 8): local bulge +12 mm vs the R1 keep-out (housing + 5)')
J['hip_pitch']=dict(panel_cm2=hip_panel,inlet='front-lower thigh fairing below the P-023 skirt line, axial slots',inlet_open_cm2=round(max(50,0.30*hip_panel)),
  outlet='rear-upper/outboard at skirt hem: laser-cut slotted band in the skirt fabric (slots 3x20 mm), routed outboard of the thigh-clamp collar (collar uncovered)',outlet_open_cm2=70,outlet_band_cm2=171,outlet_open_frac=round(70/171,3))
# masses per side
knee_rm=J['knee']['inlet_open_cm2']; hip_rm=J['hip_pitch']['inlet_open_cm2']
cap_area=363; cap_rm=round(max(50,0.30*cap_area))              # knee cap louvres (R-030 >=30 %, A35 inlet path)
bulge_add=2*(110+150)*12/1e2                                     # cm2 side walls of +12 mm bulge
thigh_d=(-(knee_rm+hip_rm)*(1-RIB)+bulge_add)*1e-4*PCA
cap_d=-cap_rm*(1-RIB)*1e-4*PCA
skirt_d=-J['hip_pitch']['outlet_open_cm2']*1e-4*0.30+0.004  # fabric removed + hem stiffener ring to hold exhaust open
# R-062 knee drives on femur rear (Legs L51): plate 26x52x104 at z 688-792, >=58 mm inside fairing.
# Electronics: inlet low on rear grille, outlet high on thigh rear. A35 rules apply to this bay.
# Local rear panels are NEW (baseline thigh fairing is front+outboard only).
drv_in_panel=88.0  # low zone of merged 221 cm2 panel [EST]   # cm2: ~120x110 mm rear grille over drive bay [EST]
drv_out_panel=133.0  # high zone  # cm2: ~150x120 mm high rear thigh panel [EST]
J['knee_drive_bay']=dict(
  panel_inlet_cm2=drv_in_panel, panel_outlet_cm2=drv_out_panel,
  inlet='low on the rear grille over the femur-rear drive plate (z ~688-740), axial/horizontal slots >=3 mm, angled into walk flow',
  inlet_open_cm2=round(max(50,0.30*drv_in_panel)), inlet_open_frac=round(max(50,0.30*drv_in_panel)/drv_in_panel,3),
  outlet='high on the thigh rear panel (z ~760-792 / popliteal upper), slots >=3 mm, >=35 % open',
  outlet_open_cm2=round(max(60,0.35*drv_out_panel)), outlet_open_frac=round(max(60,0.35*drv_out_panel)/drv_out_panel,3),
  standoff='drives inside fairing >=58 mm (Legs L51); cover inner face clears drive bodies by >=8 mm (A35 fin rule applied to hot parts)',
  note='adds rear panel mass (baseline had no rear); open-area credit below')
# Mass of NEW rear panels (PC 1.5) net of openings; rib 15 %
drv_in_rm=J['knee_drive_bay']['inlet_open_cm2']; drv_out_rm=J['knee_drive_bay']['outlet_open_cm2']
# R-087: merged into PA12 thigh-rear panel (knee_drive_panel.py); not double-counted as PC
try:
  _kdp=json.load(open(os.path.join(H,'knee_drive_panel.json'))); drv_add=_kdp['kg_side']
except Exception:
  drv_add=((drv_in_panel-drv_in_rm)+(drv_out_panel-drv_out_rm))*(1+RIB)*1e-4*PCA
J['knee_fin_grille_note']='NO local bulge: Legs withdrew rev C (R-079/R-081); rev B stays. A bulge (~5 mm) is PENDING Legs rev B envelope check if fins again exceed the v5 thigh fairing hull.'
J['knee_drive_bay']['merged_r087']='PA12 thigh-rear panel (knee_drive_panel.json) replaces separate PC rear panels + Electronics 41.8 g covers; mass in pair_kg.drive_bay_rear'
out=dict(joints=J,thermal_430_check=f'ID panel over housing: knee ~{round(knee_panel)} cm2, hip ~{hip_panel:.0f} cm2 vs Thermal 430 [EST]; ours smaller (front+outboard only, rear open), so % rules govern; open areas still >= 50/60',
 per_side_kg=dict(thigh=round(thigh_d,4),knee_cap=round(cap_d,4),hip_skirt=round(skirt_d,4),drive_bay_rear=round(drv_add,4)),
 pair_kg=dict(thigh=round(2*thigh_d,3),knee_cap=round(2*cap_d,3),hip_skirt=round(2*skirt_d,3),drive_bay_rear=round(2*drv_add,3),total=round(2*(thigh_d+cap_d+skirt_d+drv_add),3)),
 knee_cap_clearance='Legs 6f53d77: finned housing >= 110 mm from knee-cap keep-out; cap top edge stays <= z 555; no reshape needed for fins; cap gets 30 % louvres + inlet lip')
json.dump(out,open(os.path.join(H,'a36_vents.json'),'w'),indent=1); print(json.dumps(out['pair_kg']),out['thermal_430_check'])
