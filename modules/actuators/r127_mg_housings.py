"""R-127 option C(b): Mg (Elektron 43 / WE43) actuator housings. CAD volumes from G4 brief §1 (CadQuery, cad_mass.py geometry).
Props: Elektron 43 extruded T5 (Luxfer DS-490): rho 1.83, E 44.1 GPa, A-basis Fty 195 / Ftu 303, typ 243/352, k 57.6, CTE 25.6;
WE43B cast (DS-467): 1.84, min 172/220, k 51; AZ91D die cast (NADCA A-3-11): 1.81, Sy 160, Su 230, fatigue 70 MPa @5e7, E 45.
7075-T6: 2.81, Sy 480 (R-123), E 70.  -> results/r127_mg_housings.json"""
import math, json
RA, RM = 2.81, 1.83
U = {'hip_yaw': (76333, 2, 'single'), 'hip_roll': (80582, 2, 'single'), 'hip_pitch_body': (50717, 4, 'multi (twin screw)'), 'ankle_body': (68452, 4, 'multi (twin diff.)')}
# bearing-seat insert (7075, kept CTE/hardness): ring 4 mm x width over seat OD; rotary CRBH 6013 seat dia 94 x13, screw 7202 pair 39 x 20 [EST]
INS = {'hip_yaw': math.pi*94*4*13, 'hip_roll': math.pi*94*4*13, 'hip_pitch_body': math.pi*39*4*20, 'ankle_body': math.pi*39*4*20 + math.pi*26*4*10}  # ankle + GE12C eye bush
THK = 1.25   # [EST] volume factor for stiffness parity at the nut section / seats (E 44 vs 70; membrane ∝ E t on ~40 % of the volume)
out = {}; tot = dict(A=0, B=0, A_multi=0, B_multi=0)
for k, (V, n, path) in U.items():
    al = V*RA/1e6; ins = INS[k]*(RA-RM)/1e6
    A = V*RM/1e6 + ins - al                    # equal geometry + 7075 inserts
    B = V*THK*RM/1e6 + ins - al               # + stiffness thickening
    out[k] = dict(n=n, path=path, m7075=round(al, 4), mMg_equal=round(V*RM/1e6, 4), insert_penalty=round(ins, 4), dA_unit=round(A, 4), dB_unit=round(B, 4), dA_robot=round(A*n, 3), dB_robot=round(B*n, 3))
    tot['A'] += A*n; tot['B'] += B*n
    if path.startswith('multi'): tot['A_multi'] += A*n; tot['B_multi'] += B*n
tot = {k: round(v, 3) for k, v in tot.items()}
# hand-calc FEA proxy (G4 brief load cases), thin-wall
def tube_tau(T, D, t): r = (D-t)/2e3; return T/(2*math.pi*r**2*t/1e3)/1e6
def tube_bend(M, D, t): r = (D-t)/2e3; return M/(math.pi*r**2*t/1e3)/1e6
P = {}
P['hip_roll_R1_torque_369'] = dict(tau=round(tube_tau(369, 96, 2), 1), vm=round(math.sqrt(3)*tube_tau(369, 96, 2), 1))
P['hip_roll_R2_seat_117Nm_1944N'] = dict(sigma=round(tube_bend(117, 96, 2)+1944/(math.pi*94*2), 1))
P['hip_roll_R3_fatigue_204_amp'] = dict(vm_amp=round(math.sqrt(3)*tube_tau(204, 96, 2), 1))
P['screw_nut_tube_4542N'] = dict(sigma=round(4542/(math.pi*39*2), 1))
P['screw_nut_tube_fatigue_2030N_amp'] = dict(sigma=round(2030/(math.pi*39*2), 1))
lig = 2*4*10; P['ankle_eye_lug_4542N_Kt2.5'] = dict(net=round(4542/lig, 1), peak=round(2.5*4542/lig, 1))
ALLOW = dict(E43_Abasis_static=round(195/1.5, 1), E43_typ_multi_static=round(243/1.5, 1), Se_EST=70*0.6, Se_allow=round(70*0.6/1.5, 1))
json.dump(dict(units=out, totals=tot, proxy=P, allow=ALLOW), open('results/r127_mg_housings.json', 'w'), indent=1)
print(json.dumps(dict(units=out, totals=tot, proxy=P, allow=ALLOW), indent=0))
