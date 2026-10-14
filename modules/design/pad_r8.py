"""Shoulder pad R8 (Arms R7 550ab88): solid 7075-T6 roll-yaw link with integral 62x62x10 boss; core bonded straight to the boss (D-A doubler dropped)."""
import json,os
H=os.path.dirname(os.path.abspath(__file__))
a=0.0618; h=0.060; A=a*a
shear=9.17e3*0.2588; bond_tau=shear/A; core_shear_cap=2.34e6*A
base=dict(core_61p8x61p8x60=A*h*72, bond_DP490=0.0005, spreader_Al_0p5=0.0052, EPP80_face_6mm_integral_skin=0.0018, link_boss_7075_Arms_EST=0.024)
optA=dict(base); per_A=sum(optA.values())
optB=dict(base, replaceable_tray_7075_0p5_with_lips_tabs=0.0076, sleeve_TPU_film=0.0025); per_B=sum(optB.values())
out=dict(geometry=dict(pad_centre='on the CRBH 6013 plane (axial offset e <= 10 mm, target 0; Arms s0 2.45 @0, 1.98 @10 mm)',
  contact_band='z +-15 mm about the pad centre: 15.9 mm margin to the 61.8 core edges; T-030 fore-aft centroid -10/-12 mm (smoke): 19 mm margin in x',
  abduction='clear to 90 deg roll (Arms); interim soft limit <= 135 deg pending bryan-PC sweep'),
 bond=dict(shear_15deg_kN=round(shear/1e3,2),bond_shear_MPa=round(bond_tau/1e6,2),DP490_SF=round(23e6/bond_tau,1),core_shear_SF=round(core_shear_cap/shear,1),
  prep='machined 7075 boss face: grit-blast + solvent + primer per legs/BOND_SPEC.md; bonding jig locates the core (no lips needed: bond carries shear, Materials Part 4)'),
 lips='not needed when bonded (Materials Part 4: lips only locate); a 62 boss leaves no wall for a pocket around a 61.8 core -> locate with a jig; 0.5 mm locating rim would need a 64x64 boss (+7 g)',
 option_A_direct_bond=dict(items={k:round(v,4) for k,v in optA.items()},kg_side=round(per_A,4),kg_pair=round(2*per_A,4),service='cartridge replacement = debond core from the arm link (heat ~ >100 C [EST] / scrape) + re-prep + re-bond 24 h cure: field service burden'),
 option_B_replaceable_tray=dict(items={k:round(v,4) for k,v in optB.items()},kg_side=round(per_B,4),kg_pair=round(2*per_B,4),tray_check='0.5 mm tabs: bearing 307 MPa (SF 1.56 vs 480), tear-out 154 MPa (SF 2.1 vs 330)'),
 booked=0.092,cap=0.100)
json.dump(out,open(os.path.join(H,'pad_r8.json'),'w'),indent=1); print(out['option_A_direct_bond']['kg_pair'],out['option_B_replaceable_tray']['kg_pair'],out['bond'])
