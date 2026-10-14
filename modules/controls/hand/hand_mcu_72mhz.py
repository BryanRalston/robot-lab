"""R-078 / R-080: XMC4800 hand MCU at 72/72/144 MHz (fCPU/fPERIPH/fCCU) budget + flexor stall-current cap.
Tags: REPO = value in robot-lab; DS = Infineon/maxon/TI datasheet recalled, not re-read here [UNVERIFIED]; EST = my assumption."""
import json
f_cpu, f_per, f_ccu = 72e6, 72e6, 144e6          # REPO electronics §18.2d trim 1
# ---- CPU budget, Mcyc/s (cycle counts are clock-independent; flash WS fall at 72 MHz so counts are conservative)
rows = {  # name: (count, rate Hz, cycles each, tag)
 'current PI loops (brushed DC, PH/EN, IPROPI on VADC; no FOC)': (11, 10e3, 250, 'REPO 11 @10 kHz; EST 250 cyc incl. ADC result, I-clamp, I2t'),
 'position loops (6 flexors)':                (6, 1e3, 800, 'REPO 6 @1 kHz; EST 800 cyc'),
 'BiSS-C frame handling (4 ENX22 Abs, USIC SSC+FIFO/DMA; parse, CRC6, unwrap)': (4, 10e3, 250, 'REPO 4 @10 kHz; EST 250 cyc'),
 'POSIF/CCU4 count read + unwrap (2 ENX22 inc)': (2, 10e3, 40, 'EST'),
 'stall timers + per-flexor cap logic (R-080)': (6, 10e3, 30, 'EST'),
 'EtherCAT SYNC0 ISR + PDO copy (on-chip ESC)': (1, 1e3, 4000, 'REPO 1 kHz DC; EST 4000 cyc'),
 'mailbox/CoE, ladder/OT, tactile, TMP117, housekeeping': (1, 1, 6e6, 'EST 6 Mcyc/s'),
 'ISR entry/exit + cache/flash stalls (10 kHz frame ISR + 1 kHz)': (1, 11e3, 400, 'EST'),
}
budget = {k: n*r*c/1e6 for k, (n, r, c, _) in rows.items()}
tot = sum(budget.values()); util = tot*1e6/f_cpu
elec = (16.5 + 3 + 10 + 8)/72  # Electronics' own figures (REPO §16.7/§16.8) rescaled to 72 MHz
# ---- peripherals
biss_bits, biss_clk = 23, 5e6                     # REPO §16.8
t_read = biss_bits/biss_clk + 1.5/biss_clk + 3.75e-6
step = round(2*biss_clk*1024/f_per)               # USIC fractional divider, PDIV=0, SCLK = fFD/2 (DS RM)
biss_actual = f_per*step/1024/2
state_min = 0.945e-6                              # REPO §16.8 ENX22 min state at 12 400 rpm, 1024 cpt
edge_rate = 4*1024*12400/60
filt = {n: (2+n)/f_ccu for n in (3, 5, 7)}        # CCU4/POSIF sync + filter, DS-recalled
pwm = 20e3                                        # EST, not in repo
res = {'edge_aligned_counts': f_ccu/pwm, 'center_aligned_counts': f_ccu/2/pwm}
fadci = f_per/3                                   # VADC analog clock <= 30 MHz (DS)
t_conv = (2 + 12 + 4)/fadci                       # EST sample+conv cycles
# ---- R-080 stall cap
Kt, I0, N, r, eta = 18.4e-3, 0.0359, 103, 0.004, 0.65   # REPO arms/A42_A43_R4.md, R7_ROUND.md
T_max = 500.0
I_cap_ideal = T_max*r/(Kt*N) + I0                 # eta=1: conservative for the tendon
I_cap_eta = T_max*r/(Kt*N*eta) + I0
tension = lambda I, e=1.0: max(I-I0, 0)*Kt*N*e/r
grip_per_A = 30/0.952                             # REPO thermal R073 (friction 1.3)
out = dict(budget_Mcyc=budget, total_Mcyc=tot, util_pct=100*util, margin_pct=100*(1-util),
  electronics_rescaled_pct=100*elec,
  biss=dict(t_read_us=t_read*1e6, serial_4_us=4*t_read*1e6, frame_us=100, step=step, sclk_MHz=biss_actual/1e6),
  posif=dict(edge_rate_kHz=edge_rate/1e3, filt_ns={k: v*1e9 for k, v in filt.items()},
             margin_x={k: state_min/v for k, v in filt.items()}, ccu_clk_per_edge=f_ccu/edge_rate,
             wrap_ms_16bit=65536/edge_rate*1e3),
  pwm_20k=res, vadc=dict(fadci_MHz=fadci/1e6, t_conv_us=t_conv*1e6),
  cap=dict(I_cap_ideal_A=I_cap_ideal, I_cap_eta065_A=I_cap_eta, T_1p67_ideal=tension(1.67),
           T_1p08_ideal=tension(1.08), T_1p08_eta=tension(1.08, eta),
           grip_ladderB_sustained_N=grip_per_A*0.70, grip_ladderB_top_N=grip_per_A*0.84,
           peak30N_needs_A=0.952, grip_at_cap_N=grip_per_A*1.08,
           ADOPTED_cap_A=1.66, T_1p66_eta065=tension(1.66, eta), T_1p66_ideal=tension(1.66),
           trip_A=1.80, drv_ilim_A=1.9))
print(json.dumps(out, indent=1)); json.dump(out, open('hand_mcu_72mhz.json', 'w'), indent=1)

# ---- R-083: adopted 144/144/144 MHz, PWM 20 kHz (72 MHz analysis above kept as fallback)
f144 = 144e6
step144 = int(2*biss_clk*1024/f144)               # floor so SCLK stays <= 5 MHz
adc_div = next(d for d in range(1, 33) if f144/d <= 30e6)
out144 = dict(util_pct=100*tot*1e6/f144, margin_pct=100*(1-tot*1e6/f144), step=step144,
  sclk_MHz=f144*step144/1024/2/1e6, adc_div=adc_div, fadci_MHz=f144/adc_div/1e6,
  t_conv_us=(2+12+4)/(f144/adc_div)*1e6, pwm_counts_edge=f144/20e3, pwm_counts_center=f144/2/20e3)
print(json.dumps(out144, indent=1)); out['r083_144MHz'] = out144
json.dump(out, open('hand_mcu_72mhz.json', 'w'), indent=1)
