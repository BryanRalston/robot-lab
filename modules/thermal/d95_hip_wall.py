"""D95 hip-pitch plates on pelvis rear wall (x -85, z1136-1220): wall inner face, plates, hip-yaw interaction. Lumped [EST].
Inputs: pelvis shell 7075 4 mm 170x370x104 open top/bottom (Torso 5abcd56); hip pitch drive 3.0 W duty / 6.2 W cont (R131 loss table);
plate back gap 8.5 mm h_conv 5.6 + rad 6 (R131 rev2 b); hip-yaw winding <=58 duty/<=68 worst (R1_BUDGET), copper 5-6 W/side."""
Ta=35; A_pl=0.084**2; hb=11.6
A_sh=2*(0.17+0.37)*0.104   # shell side walls, one face
def solve(Pd,h_out,P_yaw_in,eps_in=0.85):
  # wall node (k 130, 4 mm: spreading ok -> isothermal [EST]); plate node; iterate
  Tw=Ta+5
  for _ in range(200):
    # plate: Pd = A(h_front)(Tp-Ta) + A hb (Tp-Tw); front h = h_out
    Tp=(Pd+A_pl*h_out*Ta+A_pl*hb*Tw)/(A_pl*(h_out+hb))
    Qin=4*A_pl*hb*(Tp-Tw)+P_yaw_in
    hin=3.5+5.5*eps_in   # inner still air + radiation to cooler interior [EST]
    Tw=Ta+Qin/(A_sh*(h_out*0.8+hin))   # outer face partly shadowed by plates (0.8)
  return Tw,Tp
for lab,Pd,h,Py in (('standing duty h8',3.0,8,2*(2.0)),('standing cont h8',6.2,8,2*3.0),('walking duty h15',3.0,15,2*2.0),('walking cont h15',6.2,15,2*3.0),('cont h8, yaw conduction worst 2x5W',6.2,8,2*5.0)):
  Tw,Tp=solve(Pd,h,Py);print(f'{lab}: wall {Tw:.1f} plate {Tp:.1f}')
# yaw housing: wall at Tw vs housing skin ~55-63 -> wall is cooler; housing loses heat TO wall, so no penalty to yaw.
