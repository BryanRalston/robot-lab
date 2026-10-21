"""T&R independent recheck of Thermal rev 4d (ec7b49d) + P-156 (a0b2aea) touch temperatures [EST hand model].
Same approach as r143_grille.py: steady energy balance per unit area; s=Stefan-Boltzmann."""
import json, math
s=5.67e-8; K=lambda c:c+273.15
def eps2(a,b): return 1/(1/a+1/b-1)
def chim(Q,H,A,Cd=0.6,rho=1.15,cp=1005):
    dT=20.
    for _ in range(200):
        v=Cd*math.sqrt(2*9.81*H*dT/300); dT=0.5*dT+0.5*Q/(rho*v*A*cp)
    return dT
out={}
# (1) grille with fin-tip baffle (1 mm PC, Al tape fin side eps 0.1; outer PC eps 0.9), cavity 25 mm breathes via grille,
#     grille Al liner inside eps 0.1, outer eps 0.9. Pocket (fin side) mean air rise dTp; fin base Tb.
def grille_baffle(Ta,Tb,dTp,hc_exch=5.0):
    Tbf,Tc,Tg=Ta+20,Ta+5,Ta+3
    for _ in range(3000):
        q_fin=3*(Ta+dTp-Tbf)+eps2(0.85,0.1)*0.9*s*(K(Tb)**4-K(Tbf)**4)          # into baffle, fin side
        q_cav=3*(Tbf-Tc)+eps2(0.9,0.1)*0.8*s*(K(Tbf)**4-K(Tg)**4)              # out of baffle, cavity side
        Tbf+=(q_fin-q_cav)/100
        # cavity air: gets baffle convection, loses to grille webs (h3, solid 35 %) + exchange through slots
        q_c_in=3*(Tbf-Tc); q_c_out=3*0.35*(Tc-Tg)+hc_exch*(Tc-Ta)
        Tc+=(q_c_in-q_c_out)/100
        q_g_in=3*(Tc-Tg)+eps2(0.9,0.1)*0.8*s*(K(Tbf)**4-K(Tg)**4)
        q_g_out=4*(Tg-Ta)+0.9*s*(K(Tg)**4-K(Ta)**4)
        Tg+=(q_g_in-q_g_out)/100
    return dict(baffle=round(Tbf,1),cavity_air=round(Tc,1),grille=round(Tg,1))
for Ta,Tb in ((25.,68.5),(35.,78.5)):   # Thermal rev 4c standing vented basis is 35 C ambient (76.2-78.5)
    for dTp in (28.,31.):
        for hx in (2.,5.):
            out[f"grille_baffle_Ta{int(Ta)}_dTp{int(dTp)}_hx{int(hx)}"]=grille_baffle(Ta,Tb,dTp,hx)
# (2) outlet grille: exhaust leaves at the outlet, slot webs washed by exhaust air (outlet rise 44-62 K, Thermal table)
def web_in_stream(Ta,Tair,hi=8,ho=4):
    T=Ta+10
    for _ in range(2000):
        T+=(hi*(Tair-T)-ho*(T-Ta)-0.9*s*(K(T)**4-K(Ta)**4))/60
    return round(T,1)
for Ta in (25.,35.):
    for dTo in (44.,62.):
        out[f"outlet_web_Ta{int(Ta)}_dTout{int(dTo)}"]=web_in_stream(Ta,Ta+dTo)
    out[f"inlet_web_Ta{int(Ta)}"]=web_in_stream(Ta,Ta+2)   # inlet draws ambient air
# (3) fairing over the knee housing: housing case Th, eps 0.85; fairing PC with inner Al foil eps 0.05; gap 10 mm vented
def fairing(Ta,Th,A_house=0.03,slot=300e-6,H=0.10,closed=False):
    Tf,Tgap=Ta+10,Ta+10
    for _ in range(4000):
        Qconv=3*A_house*(Th-Tgap)            # housing -> gap air
        if closed: dT=max(Tgap-Ta,0.1)
        else: dT=chim(max(Qconv,0.05),H,slot)
        Tgap_target=Ta+dT/2 if not closed else Tgap
        q_in=3*(Tgap-Tf)+eps2(0.85,0.05)*s*(K(Th)**4-K(Tf)**4)
        q_out=4*(Tf-Ta)+0.9*s*(K(Tf)**4-K(Ta)**4)
        Tf+=(q_in-q_out)/80
        if closed: Tgap+=(Qconv-3*A_house*(Tgap-Tf))/5
        else: Tgap+=0.05*(Tgap_target-Tgap)
    return dict(fairing=round(Tf,1),gap_air=round(Tgap,1))
for Ta in (25.,35.):
    for Th in (90.,100.):
        out[f"housing_fairing_vented_Ta{int(Ta)}_Th{int(Th)}"]=fairing(Ta,Th)
json.dump(out,open('r143_rev4d.json','w'),indent=1)
for k,v in out.items(): print(k,v)
