"""Robot Lab v2 design parameters. Every number is an ESTIMATE unless a source is given.
BASE = first-pass design (v2.0). FIXES = changes made after checks failed (v2.1). Final = BASE+FIXES."""
import copy
G=9.81
# ---- Motor classes: generic frameless PMSM sizes. ALL VALUES ESTIMATES (verify against
# vendor datasheets, e.g. Kollmorgen TBM2, Allied Motion MF, Parker K-series, CubeMars RI/RO).
# Km = motor constant N·m/sqrt(W); Rth = winding->ambient K/W incl. housing path; tau = thermal time const s
MOTORS={
 'M115':dict(Km=0.40,Tpk=12.0,Rth=0.9,tau=900,wmax_rpm=3000,mass=0.90),
 'M85': dict(Km=0.20,Tpk=5.0, Rth=1.5,tau=600,wmax_rpm=4000,mass=0.50),
 'M60': dict(Km=0.09,Tpk=2.0, Rth=2.5,tau=400,wmax_rpm=6000,mass=0.25),
 'M38': dict(Km=0.03,Tpk=0.5, Rth=5.0,tau=300,wmax_rpm=8000,mass=0.10),
}
# ---- Strain-wave gears: Harmonic Drive CSG ratio 100, catalog values (harmonicdrive.net, CSG rating table)
# rated L10, repeated peak, momentary peak [N·m]; output-bearing allowable moment Mc only where published (CSG-32-100-2UH: 313 N·m)
GEARS={
 'CSG-20-100':dict(N=100,rated=52, rep_peak=107,mom_peak=191,eta=0.75,mass=0.98,Mc=None),
 'CSG-25-100':dict(N=100,rated=87, rep_peak=204,mom_peak=369,eta=0.75,mass=1.5, Mc=None),  # mass EST
 'CSG-32-100':dict(N=100,rated=178,rep_peak=433,mom_peak=841,eta=0.75,mass=3.2,Mc=313),
 'SW-14-100':dict(N=100,rated=7.8,rep_peak=28,mom_peak=54,eta=0.70,mass=0.3,Mc=None,est=True), # size-14 class: ESTIMATE, verify
 'SW-11-100':dict(N=100,rated=5,  rep_peak=11,mom_peak=25,eta=0.70,mass=0.15,Mc=None,est=True), # ESTIMATE
}
# ---- Joint table. kind rotary: motor+gear. kind linear: motor -> planetary roller screw (lead mm) -> lever arm r (m)
JOINTS={
 # name: (group, kind, motor, gear|None, lead_mm, arm_m, count)
 'hip_yaw':   ('leg','rotary','M85','CSG-20-100',None,None,2),
 'hip_roll':  ('leg','rotary','M115','CSG-25-100',None,None,2),
 'hip_pitch': ('leg','rotary','M115','CSG-32-100',None,None,2),
 'knee':      ('leg','linear','M85',None,4.0,0.05,2),
 'ankle_pitch':('leg','linear2','M60',None,2.0,0.06,2),  # two parallel screws share pitch & roll
 'ankle_roll':('leg','linear2','M60',None,2.0,0.04,2),
 'waist_yaw': ('torso','rotary','M85','CSG-25-100',None,None,1),
 'waist_pitch':('torso','rotary','M115','CSG-32-100',None,None,1),
 'shoulder_pitch':('arm','rotary','M85','CSG-25-100',None,None,2),
 'shoulder_roll':('arm','rotary','M85','CSG-25-100',None,None,2),
 'shoulder_yaw':('arm','rotary','M60','CSG-20-100',None,None,2),
 'elbow':     ('arm','linear','M60',None,2.0,0.04,2),
 'wrist_roll':('arm','rotary','M38','SW-14-100',None,None,2),
 'wrist_pitch':('arm','linear2','M38',None,1.0,0.025,2),
 'wrist_yaw': ('arm','linear2','M38',None,1.0,0.025,2),
 'neck_yaw':  ('head','rotary','M38','SW-11-100',None,None,1),
 'neck_pitch':('head','rotary','M38','SW-11-100',None,None,1),
}
SCREW_ETA=0.80   # planetary roller screw + linkage efficiency, ESTIMATE
ACT_OVERHEAD=dict(rotary=0.45,linear=0.55,linear2=0.40)  # housing, bearings, encoder, driver PCB, kg per actuator ESTIMATE
# ---- Geometry (m) ESTIMATES, 1.73 m tall
GEO=dict(height=1.73,thigh=0.42,shank=0.42,ankle_h=0.08,foot_len=0.24,heel=0.06,hip_w=0.20,
         pelvis_to_shoulder=0.52,upper_arm=0.30,forearm=0.27,torso_com_above_hip=0.26)
# ---- Non-actuator mass items (kg) ESTIMATES
MASS_ITEMS={
 'pelvis structure (7075 machined)':2.0,'torso frame (7075 + CF shells)':3.5,'thigh structure x2':2.0,'shank structure x2':1.6,
 'feet x2 (incl. 6-axis F/T, sole)':1.8,'upper arm+forearm structure x2':1.6,'head (cameras, shell)':1.6,
 'hands x2 (22-DoF, actuators in forearm counted here)':2.6,'battery pack':12.0,'compute (Jetson Thor + RT ctrl + cooling)':1.8,
 'harness, connectors':2.0,'covers/padding':1.5,'thermal (pump, radiator, coolant)':1.0,
}
BATTERY=dict(Wh=2300,V=52)  # matches Tesla AI Day 2022 Optimus pack figures (2.3 kWh, 52 V) as a target
# ---- Structure (links) ESTIMATES: tubes, 7075-T6 (yield 503 MPa, fatigue ~159 MPa @5e8 per MIL-HDBK-5 typical)
MATERIALS={'7075-T6':dict(Sy=503e6,Se=159e6,rho=2810),'Ti-6Al-4V':dict(Sy=880e6,Se=510e6,rho=4430)}
LINKS={'femur':dict(mat='7075-T6',OD=0.050,t=0.002),'tibia':dict(mat='7075-T6',OD=0.045,t=0.002)}
HIP=dict(bolts=8,bolt_d=0.005,bolt_pcd=0.090,bolt_Sy=900e6,extra_bearing_Mc=0)  # 12.9 bolts
LOADS=dict(landing_BW=3.0,walk_BW=1.3,lever_femur=0.12,lever_tibia=0.10,hip_lat=0.10,squat_load=20.0)
# ---- v2.1 fixes, each answering a failed check in results/checks_initial.md ----
def fix_gear_component_sets(d):
    """Mass FAIL (90 kg): housed 2UH gear units replaced with CSG component sets integrated into our own
    actuator housing (catalog CSG-32-100-2A-GR = 0.89 kg; sizes 20/25 component-set masses ESTIMATED)."""
    d['GEARS']=dict(d['GEARS']);d['GEARS']['CSG-32-100']=dict(d['GEARS']['CSG-32-100'],mass=0.89)
    d['GEARS']['CSG-25-100']=dict(d['GEARS']['CSG-25-100'],mass=0.55);d['GEARS']['CSG-20-100']=dict(d['GEARS']['CSG-20-100'],mass=0.35)
def fix_mass_items(d):
    """Mass: CF-sandwich torso shells instead of machined frame, 230 Wh/kg pack (10 kg for 2.3 kWh) ESTIMATE."""
    mi=d['MASS_ITEMS'];mi['torso frame (7075 + CF shells)']=2.8;mi['battery pack']=10.0;mi['pelvis structure (7075 machined)']=1.6
def fix_speed_windings(d):
    """Hip pitch speed FAIL (3.1 < 4 rad/s): faster winding for 52 V bus. Km is winding-independent, so thermal
    is unchanged; the cost is higher phase current (~110 A peak for M115), so drives must be sized for it."""
    d['MOTORS']['M115']['wmax_rpm']=4500
def fix_screw_geometry(d):
    """Knee/ankle/elbow/wrist speed FAILs: re-chose screw lead and lever arm so the linear joints reach their speed
    while keeping torque ≥ 1.5× requirement. Knee motor upsized to M115 (Optimus-style large knee linear actuator)."""
    J=d['JOINTS']
    J['knee']=('leg','linear','M115',None,5.0,0.045,2)
    J['ankle_pitch']=('leg','linear2','M60',None,4.0,0.05,2); J['ankle_roll']=('leg','linear2','M60',None,4.0,0.04,2)
    J['elbow']=('arm','linear','M60',None,4.0,0.04,2)
    J['wrist_pitch']=('arm','linear2','M38',None,2.0,0.025,2); J['wrist_yaw']=('arm','linear2','M38',None,2.0,0.025,2)
def fix_hip_support_bearing(d):
    """Hip bearing moment FAIL (SF 1.18): add a crossed-roller support bearing on the hip-pitch output so the
    strain-wave cross-roller is not the only moment path. After downsizing hip pitch to CSG-25 (no published Mc), the support bearing must carry the
    whole moment alone: allowable ≥ 600 N·m ESTIMATE (~Ø140 mm crossed-roller class); select the part to meet it."""
    d['HIP']['extra_bearing_Mc']=600
def fix_downsize_overmargined(d):
    """Mass still FAIL (73.5 kg) after the first fixes: downsized joints whose torque margin was > 4× while keeping ≥ 1.5× SF and speed.
    hip_yaw M85→M60, waist_yaw M85+CSG-25→M60+CSG-20, waist_pitch M115+CSG-32→M85+CSG-25, hip_pitch CSG-32→CSG-25,
    knee M115→M85 with a 5000 rpm winding (motor ESTIMATE; drive current rises accordingly)."""
    J=d['JOINTS']
    J['hip_yaw']=('leg','rotary','M60','CSG-20-100',None,None,2)
    J['waist_yaw']=('torso','rotary','M60','CSG-20-100',None,None,1)
    J['waist_pitch']=('torso','rotary','M85','CSG-25-100',None,None,1)
    J['hip_pitch']=('leg','rotary','M115','CSG-25-100',None,None,2)
    J['knee']=('leg','linear','M85',None,5.0,0.045,2)
    d['MOTORS']['M85']['wmax_rpm']=5000
# Model refinement (not a hardware change): v2.0 used one flat housing/driver overhead per actuator type, which
# over-counts small wrist/neck/ankle units. Overhead now scales with motor size (ESTIMATES).
OVERHEAD_BY_MOTOR={'M115':0.45,'M85':0.35,'M60':0.25,'M38':0.12}
FIXES=dict(gears=fix_gear_component_sets,mass=fix_mass_items,speed=fix_speed_windings,screws=fix_screw_geometry,hip=fix_hip_support_bearing,downsize=fix_downsize_overmargined)
def final():
    d=dict(MOTORS=copy.deepcopy(MOTORS),GEARS=GEARS,JOINTS=copy.deepcopy(JOINTS),GEO=GEO,MASS_ITEMS=copy.deepcopy(MASS_ITEMS),
           BATTERY=dict(BATTERY),LINKS=copy.deepcopy(LINKS),HIP=dict(HIP),LOADS=LOADS,MATERIALS=MATERIALS)
    for f in FIXES.values(): f(d)
    return d
