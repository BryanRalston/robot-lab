"""R-106 sizing of L61: bearing-grade PTFE-filled PEI trunnion bushes, design pressure <=14.6 MPa, no metal bypass.
k values (cited): TECAPEI natural 0.21 W/mK (Ensinger, ISO 22007-4); ULTEM 1010F 0.220 (SABIC/lookpolymers); TECAFLON PTFE 0.20 (Ensinger, ASTM C177);
PolyOne Lubri-Tech PI-30GF/15T (PTFE-lubricated PEI) >=0.231 -> design k=0.231 (no PTFE-filled-PEI-specific Ensinger/SABIC value found). L61 used 0.12 (wrong)."""
import json, math
Fd=240/0.0475/2; Fw=159.8/0.0475/2; k=0.231; rho=1.4e-3  # g/mm3 PTFE-filled PEI [EST ~1.3-1.5]
def case(d,L,t=2.0,boss_od=None,tw=2.0,f=0.3):
    od=d+2*t; boss_od=boss_od or od+5
    Rb=t/1e3/(k*math.pi*d*L*0.5e-6); Rw=tw/1e3/(k*f*math.pi*(od**2-d**2)/4*1e-6)
    Rs=1/(1/Rb+1/Rw)
    m=2*(rho*math.pi*(od**2-d**2)/4*L+rho*f*math.pi*(od**2-d**2)/4*tw)+2*2.7e-3*math.pi*(boss_od**2-od**2)/4*(L-6)  # vs bare 6 mm cheek
    pin=2*7.85e-3*math.pi*d**2/4*(L-12)  # extra pin length beyond L61
    return dict(d=d,L=L,t=t,tw=tw,pad=f,od=od,boss=f'ø{boss_od} x {L}',p_walk=round(Fw/(d*L),1),p_design=round(Fd/(d*L),1),R_side=round(Rs,1),R_joint=round(Rs/2,1),mass_knee_g=round(m+pin,1),mass_robot_kg=round(2*(m+pin)/1e3,4))
out=dict(basis=__doc__,L61_ref_recomputed_k=case(9,12),candidates=[case(9,20),case(11,16),case(10,18),case(11,16,4.5),case(11,16,3.5,tw=3,f=0.15),case(11,16,4.5,tw=3,f=0.15)])
json.dump(out,open('results/r031/knee_trunnion_bush_r106.json','w'),indent=1)
for c in [out['L61_ref_recomputed_k']]+out['candidates']: print(c)
